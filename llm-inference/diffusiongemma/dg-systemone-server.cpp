// dg-systemone-server — OpenJev-style "System One" reads on DiffusionGemma, via llama.cpp.
//
// Builds against the DiffusionGemma llama.cpp PR (ggml-org/llama.cpp#24423). One persistent process
// loads the GGUF once (honouring -ngl / --n-cpu-moe / -fa, so a 26B-A4B MoE fits an 8 GB GPU), then
// answers read requests as JSON lines on stdin -> JSON lines on stdout:
//
//   {"prompt":[ids], "canvas":[ids], "slots":[{"pos":p,"label_ids":[...]}], "topk":20}
//   -> {"slots":[{"top":{"<id>":logprob,...}}], "prompt_tokens":P, "prefill_ms":..,
//       "decode_ms":.., "cached":bool}
//
// A read is exactly what OpenJev's MLX backend does: prefill the chat prompt (causal encoder pass,
// cached in the PR's prompt-KV store), then ONE bidirectional decoder pass over the seeded canvas with
// self-conditioning off, and a temperature-1 log-softmax at each answer slot. Nothing is sampled.
// A repeated prompt (OpenJev's noisy re-reads) skips the prefill.
//
// Usage: dg-systemone-server -m model.gguf -ngl 99 --n-cpu-moe 24 -fa on [-c 4096] [-ub 512]

#include "arg.h"
#include "common.h"
#include "llama.h"

#include <nlohmann/json.hpp>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>

using json = nlohmann::json;

static double ms_since(std::chrono::steady_clock::time_point t0) {
    return std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
}

static void reply(const json & j) {
    std::cout << j.dump() << "\n" << std::flush;
}

int main(int argc, char ** argv) {
    common_params params;
    common_init();
    if (!common_params_parse(argc, argv, params, LLAMA_EXAMPLE_DIFFUSION)) {
        return 1;
    }
    llama_backend_init();

    llama_model_params mparams = llama_model_default_params();
    mparams.n_gpu_layers = params.n_gpu_layers;
    mparams.devices      = params.devices.data();
    mparams.load_mode    = params.load_mode;
    if (!params.tensor_buft_overrides.empty()) {
        mparams.tensor_buft_overrides = params.tensor_buft_overrides.data();  // --n-cpu-moe / -ot
    }
    llama_model * model = llama_model_load_from_file(params.model.path.c_str(), mparams);
    if (!model) {
        fprintf(stderr, "failed to load model\n");
        return 1;
    }
    const llama_vocab * vocab = llama_model_get_vocab(model);
    const int n_vocab = llama_vocab_n_tokens(vocab);

    // reads never self-condition: drop the full-vocab SC branch from the graph before reserving
    llama_diffusion_set_sc(model, nullptr, 0.0f, 1.0f, false);

    // The graph reserves full-vocab logits for every ubatch row: 262144 x 4 B = 1 MiB per row, so a
    // 4096-row ubatch alone is a 4 GiB buffer. Keep the ubatch small (-ub, default 512) and prefill
    // long prompts in ubatch-sized chunks; only the canvas (<= 64 rows for OpenJev) must fit one ubatch.
    const int max_tok = std::max(params.n_ctx, 1024);
    const int ubatch  = std::min((int) params.n_ubatch, max_tok);
    llama_context_params cparams = llama_context_default_params();
    cparams.n_ctx           = max_tok;
    cparams.n_batch         = ubatch;
    cparams.n_ubatch        = ubatch;
    cparams.flash_attn_type = params.flash_attn_type;
    cparams.op_offload      = !params.no_op_offload;  // --no-op-offload: CPU experts compute on CPU
    cparams.no_perf         = true;
    llama_context * ctx = llama_init_from_model(model, cparams);
    if (!ctx) {
        fprintf(stderr, "failed to create context\n");
        return 1;
    }
    llama_set_n_threads(ctx, params.cpuparams.n_threads, params.cpuparams_batch.n_threads);
    llama_set_causal_attn(ctx, false);

    llama_batch batch = llama_batch_init(ubatch, 0, 1);
    std::vector<llama_token> cached_prompt;

    // load ids[off, off+n) at positions pos0+off...
    auto fill = [&](const std::vector<llama_token> & ids, int pos0, bool all_logits, int off = 0, int n = -1) {
        batch.n_tokens = n < 0 ? (int) ids.size() : n;
        for (int i = 0; i < batch.n_tokens; ++i) {
            batch.token[i]     = ids[off + i];
            batch.pos[i]       = pos0 + off + i;
            batch.n_seq_id[i]  = 1;
            batch.seq_id[i][0] = 0;
            batch.logits[i]    = all_logits || i == batch.n_tokens - 1;
        }
    };

    fprintf(stderr, "dg-systemone-server ready (n_vocab=%d, max_tok=%d)\n", n_vocab, max_tok);
    reply({{"ready", true}, {"n_vocab", n_vocab}, {"max_tok", max_tok}});

    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        if (line == "QUIT") break;
        json req;
        try {
            req = json::parse(line);
        } catch (const std::exception & e) {
            reply({{"error", std::string("bad json: ") + e.what()}});
            continue;
        }
        const std::vector<llama_token> prompt = req.at("prompt").get<std::vector<llama_token>>();
        const std::vector<llama_token> canvas = req.at("canvas").get<std::vector<llama_token>>();
        const int topk = req.value("topk", 20);
        const int P = (int) prompt.size();
        const int C = (int) canvas.size();
        if (P < 1 || C < 1 || P + C > max_tok || C > ubatch) {
            reply({{"error", "prompt+canvas is " + std::to_string(P) + "+" + std::to_string(C) +
                             " tokens; limits " + std::to_string(max_tok) + " total, " + std::to_string(ubatch) + " canvas"}});
            continue;
        }

        // "mode":"unified" (verification only): one no-cache forward over [prompt | canvas], the path the
        // PR validated against transformers. The graph takes the canvas to be the model's canvas_length.
        if (req.value("mode", "") == "unified") {
            if (P + C > ubatch) {
                reply({{"error", "unified mode needs prompt+canvas <= ubatch"}});
                continue;
            }
            std::vector<llama_token> all(prompt);
            all.insert(all.end(), canvas.begin(), canvas.end());
            llama_diffusion_set_phase(model, 0, 0, 0);
            fill(all, 0, true);
            for (int i = 0; i < P; ++i) batch.logits[i] = 0;
            const bool ok = llama_decode(ctx, batch) == 0;
            cached_prompt.clear();  // the prompt-KV store was not written
            if (!ok) {
                reply({{"error", "unified decode failed"}});
                continue;
            }
            json slots = json::array();
            for (const auto & s : req.at("slots")) {
                const float * row = llama_get_logits_ith(ctx, P + (int) s.at("pos"));
                double mx = -INFINITY, z = 0.0;
                for (int v = 0; v < n_vocab; ++v) mx = std::max(mx, (double) row[v]);
                for (int v = 0; v < n_vocab; ++v) z += std::exp(row[v] - mx);
                json top = json::object();
                for (int id : s.at("label_ids").get<std::vector<int>>()) top[std::to_string(id)] = row[id] - mx - std::log(z);
                slots.push_back({{"top", top}});
            }
            reply({{"slots", slots}, {"prompt_tokens", P}, {"prefill_ms", 0.0}, {"decode_ms", 0.0}, {"cached", false}});
            continue;
        }

        // PREFILL the prompt into the prompt-KV store (in ubatch chunks) unless it is already cached
        const bool cached = prompt == cached_prompt;
        double prefill_ms = 0.0;
        if (!cached) {
            auto t0 = std::chrono::steady_clock::now();
            bool ok = true;
            for (int off = 0; ok && off < P; off += ubatch) {
                llama_diffusion_set_phase(model, 1, P, off);
                fill(prompt, 0, false, off, std::min(ubatch, P - off));
                ok = llama_decode(ctx, batch) == 0;
            }
            if (!ok) {
                cached_prompt.clear();
                reply({{"error", "prefill failed"}});
                continue;
            }
            llama_synchronize(ctx);
            cached_prompt = prompt;
            prefill_ms = ms_since(t0);
        }

        // DECODE: one bidirectional pass over the canvas against the cached prompt
        auto t1 = std::chrono::steady_clock::now();
        llama_diffusion_set_phase(model, 2, P, 0);
        fill(canvas, P, true);
        if (llama_decode(ctx, batch) != 0) {
            reply({{"error", "decode failed"}});
            continue;
        }
        llama_synchronize(ctx);
        const double decode_ms = ms_since(t1);

        json slots = json::array();
        for (const auto & s : req.at("slots")) {
            const int pos = s.at("pos");
            const float * row = llama_get_logits_ith(ctx, pos);
            double mx = -INFINITY;
            for (int v = 0; v < n_vocab; ++v) mx = std::max(mx, (double) row[v]);
            double z = 0.0;
            for (int v = 0; v < n_vocab; ++v) z += std::exp(row[v] - mx);
            const double lse = mx + std::log(z);

            std::vector<int> idx(n_vocab);
            for (int v = 0; v < n_vocab; ++v) idx[v] = v;
            std::partial_sort(idx.begin(), idx.begin() + topk, idx.end(),
                              [&](int a, int b) { return row[a] > row[b]; });
            json top = json::object();
            for (int k = 0; k < topk; ++k) top[std::to_string(idx[k])] = row[idx[k]] - lse;
            for (int id : s.at("label_ids").get<std::vector<int>>()) top[std::to_string(id)] = row[id] - lse;
            slots.push_back({{"top", top}});
        }
        reply({{"slots", slots}, {"prompt_tokens", P}, {"prefill_ms", prefill_ms},
               {"decode_ms", decode_ms}, {"cached", cached}});
    }

    llama_batch_free(batch);
    llama_free(ctx);
    llama_model_free(model);
    llama_backend_free();
    return 0;
}
