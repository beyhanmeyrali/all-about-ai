"""OpenJev on llama.cpp: the Jev-compatible /v1/systemone API on an 8 GB GPU.

OpenJev (github.com/razorback16/openjev) ships two backends: vLLM (needs a
24 GB+ GPU for the NVFP4 checkpoint) and MLX (Apple silicon). This adds a
third, on the llama.cpp DiffusionGemma PR, so the MoE experts can be offloaded
to system RAM with --n-cpu-moe exactly as for any other MoE in BENCHMARKS.md.

Everything above the read is OpenJev's own code, unchanged: schema building,
the answer template, the canvas seeded with random-token noise at each answer
slot, the entropy-triggered re-reads, calibration maths and the response shape.
Only ``one_read`` is replaced -- it hands (prompt ids, canvas, slots) to
dg-systemone-server, which does one prefill + one bidirectional decoder pass
and returns log-probs at the slots, the same thing the MLX backend computes.

Not supported here (they need text generation or a vision tower): images,
``think``, ``steps`` > 1, and POST /v1/chat/completions. Use
llama-diffusion-cli for generation.

Usage:
    python openjev_llamacpp.py -m model.gguf -ngl 99 --n-cpu-moe 20 -fa on -c 2048 -ub 512 --no-op-offload
    curl localhost:8080/v1/systemone -d '{"model":"jev-latest","state":"...","questions":{...}}'
All arguments are passed to dg-systemone-server. OPENJEV_* env vars still apply.
"""
import asyncio
import json
import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import uvicorn
from fastapi.responses import JSONResponse

import openjev.api
import openjev.mlx_backend
from openjev.api import create_app
from openjev.config import Settings
from openjev.engine import Engine, SchemaError, slot_distribution

HERE = Path(__file__).resolve().parent
DEFAULT_BIN = HERE.parent / "build/llama.cpp-diffusiongemma/build-cuda/bin/dg-systemone-server"
TOKENIZER = os.environ.get("OPENJEV_TOKENIZER", "nvidia/diffusiongemma-26B-A4B-it-NVFP4")


class ReadServer:
    """The dg-systemone-server process. One read at a time: the model is on
    one GPU and each read is a single forward pass, so a queue is all a
    laptop needs."""

    def __init__(self, args, binary=None):
        binary = binary or os.environ.get("DG_SYSTEMONE_BIN", str(DEFAULT_BIN))
        self.proc = subprocess.Popen([binary] + list(args), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=None, text=True, bufsize=1)
        ready = json.loads(self.proc.stdout.readline() or "{}")
        if not ready.get("ready"):
            raise RuntimeError("dg-systemone-server failed to start")
        self.max_tok = ready["max_tok"]
        self.lock = threading.Lock()

    def read(self, prompt, canvas, slots, topk=20):
        req = {"prompt": prompt, "canvas": canvas, "topk": topk,
               "slots": [{"pos": s["pos"], "label_ids": s["label_ids"]} for s in slots]}
        with self.lock:
            self.proc.stdin.write(json.dumps(req) + "\n")
            self.proc.stdin.flush()
            line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("dg-systemone-server exited")
        out = json.loads(line)
        if "error" in out:
            raise SchemaError(out["error"])
        return out

    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.write("QUIT\n")
            self.proc.stdin.flush()
            self.proc.wait(timeout=30)


class LlamaCppEngine(Engine):
    server_args: list = []

    def __init__(self, settings, tokenizer):
        super().__init__(settings, tokenizer)
        self.server = ReadServer(self.server_args)
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="openjev-llamacpp")
        self.last_timing = {}

    async def close(self):
        await super().close()
        self.pool.shutdown(wait=True)
        self.server.close()

    async def think(self, sys_text, state_text, budget):
        raise SchemaError("think needs text generation; the llama.cpp backend only reads", ("body", "think"))

    async def one_read(self, template, slots, sys_text, content, seed, steps=1, prefix=None):
        if isinstance(content, list):
            raise SchemaError("images need the vLLM or MLX backend", ("body", "images"))
        if steps != 1:
            raise SchemaError("the llama.cpp backend reads with steps=1 only", ("body", "steps"))
        prompt = prefix if prefix is not None else self.chat_prompt_ids(sys_text, content)
        canvas = self.build_canvas(template, slots, seed)
        async with self.slots:
            out = await asyncio.get_running_loop().run_in_executor(
                self.pool, self.server.read, prompt, canvas, slots)
        self.last_timing = {k: out[k] for k in ("prefill_ms", "decode_ms", "cached")}
        tops = [{int(k): v for k, v in s["top"].items()} for s in out["slots"]]
        return [slot_distribution(top, s["label_ids"]) for top, s in zip(tops, slots)], out["prompt_tokens"]


class NoGenerator:
    """Stands in for the chat generator: /v1/chat/completions is not served."""

    def __init__(self, settings, engine):
        pass

    async def close(self):
        pass


def main(argv):
    if not argv or "-h" in argv:
        print(__doc__)
        return
    LlamaCppEngine.server_args = argv
    # create_app picks MlxEngine/MlxGenerator for backend "mlx"; point those names at ours
    openjev.mlx_backend.MlxEngine = LlamaCppEngine
    openjev.api.MlxGenerator = NoGenerator
    from transformers import AutoTokenizer
    settings = Settings(backend="mlx", auto_max=int(os.environ.get("OPENJEV_AUTO_MAX", "4")))
    app = create_app(settings, AutoTokenizer.from_pretrained(TOKENIZER))

    @app.middleware("http")
    async def no_chat(request, call_next):
        if request.url.path == "/v1/chat/completions":
            return JSONResponse({"error": {"type": "not_implemented", "message":
                                 "text generation is not served by the llama.cpp backend; use llama-diffusion-cli"}},
                                status_code=501)
        return await call_next(request)

    uvicorn.run(app, host=os.environ.get("OPENJEV_HOST", "127.0.0.1"),
                port=int(os.environ.get("OPENJEV_PORT", "8080")),
                log_level=os.environ.get("OPENJEV_LOG_LEVEL", "warning"))


if __name__ == "__main__":
    main(sys.argv[1:])
