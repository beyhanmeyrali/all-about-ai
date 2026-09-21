# Jev vs DiffusionGemma vs Qwen — Fast AI Decisions, Measured

> **The post, ready to copy to LinkedIn** (plain text, no Markdown):

```text
Everyone is talking about Jev, TypeSafe's "System One" model: typed decisions
with a probability attached, "70–500 ms", output tokens free. And a viral post
claims Google's open DiffusionGemma is a free Jev you can run yourself.

So I measured all three on the same 400 questions: real Jev 1.13 (via
OpenRouter), DiffusionGemma run locally on an 8 GB laptop GPU, and a normal chat
model (Qwen 3 30B) as the baseline.

⚡ SPEED — time to answer N yes/no questions about one text
• Jev (cloud, network included): 0.40 s for 1 question. 0.34 s for 20. Flat.
• DiffusionGemma (8 GB laptop): 0.09 s for 1, 0.36 s for 20 once the text is
  loaded; 0.56 → 2.1 s when it's a new text.
• Qwen typing the answers: 0.10 s → 1.7 s, growing with every question. At 20
  questions it broke its own output format.

🔢 TOKENS
• Qwen has to WRITE its answer: 5 output tokens per question, 92 for 20.
• DiffusionGemma writes nothing: 0 output tokens. It reads the answer straight
  out of one pass over a pre-printed form.
• Jev bills only input ($0.042 per million tokens); output is free.

💰 COST per 1,000 decisions
• Jev: $0.013–0.015 (all 400 test decisions cost me $0.0056).
• Local models: $0 (my electricity is cheap).

🎯 QUALITY (movie-review sentiment / news topic)
• Jev: 94% / 85%, and the best calibrated.
• DiffusionGemma: 89% / 77%, zero broken replies.
• Qwen writing answers: 83% / 65.5%, with 31 malformed replies out of 400.

My take:
1. Jev's speed story is real. Flat 0.34–0.40 s whether you ask 1 question or 20.
2. The "free Jev" story is half true. DiffusionGemma really does answer many
   questions in one pass with zero output tokens, but on an 8 GB GPU it isn't
   flat, and it's 5–8 points less accurate than Jev.
3. For decisions, stop making LLMs type. Reading probabilities instead of
   parsing text removed every format error, for every model.

Full numbers, code, and every test case are in the write-up. #AI #LLM #Jev #DiffusionGemma #OpenSource
```

**Every number on this page was measured by me unless marked otherwise.** Local runs used an RTX 5060 Laptop (8 GB) with a Ryzen AI 9 365 and 29 GB RAM. Jev was called over the internet through OpenRouter, so its times include the network round trip. [Every test case and exact query](#every-test-exactly) is listed below. The page has two parts:
- **Part 1** (this top part): the TL;DR, the idea explained from zero, code you can copy, and real side-by-side answers.
- **[Part 2](#part-2--the-detailed-version)**: the engineering and a claims audit of the viral post.

---

## TL;DR — speed and tokens first

### The three contenders

| | What it is | How it answers | Where it ran |
|---|---|---|---|
| **Jev 1.13** (TypeSafe) | A commercial "System One" decision model | Returns a probability per option. No text. | TypeSafe's cloud, called through OpenRouter (`typesafe/jev-1.13`) |
| **DiffusionGemma 26B-A4B** (Google, open) | A text-*diffusion* model, run as an open Jev clone (OpenJev + my llama.cpp backend) | Fills every answer box of a pre-printed form in **one pass** and reads the probabilities. 0 output tokens. | My 8 GB laptop GPU, with most of the model in system RAM |
| **Qwen 3 30B-A3B** (Alibaba, open) | A normal chat model: the baseline | **Types** its answers token by token (`q1: yes`), and my code parses the text | The same laptop |

### ⚡ Speed: time to answer N yes/no questions about one news article

"Text already loaded" means the model has already read this text, so only the answering is timed. "New text" includes reading it first. Median of 3 runs each. Qwen's columns show the faster of its two server settings for each row (llama.cpp op-offload on or off; both runs are in `speed_scaling.json`).

| Questions in one request | **Jev**, new text (cloud, incl. network) | **DiffusionGemma**, text already loaded | DiffusionGemma, new text | **Qwen types the answers**, text already loaded | Qwen, new text |
|---:|---:|---:|---:|---:|---:|
| 1 | 396 ms | **93 ms** | 563 ms | 97 ms | 614 ms |
| 2 | 350 ms | **93 ms** | 627 ms | 183 ms | 763 ms |
| 5 | 349 ms | **155 ms** | 864 ms | 452 ms | 1,214 ms |
| 10 | 354 ms | **287 ms** | 1,336 ms | 931 ms | 1,906 ms |
| 20 | **336 ms** | 363 ms | 2,089 ms | 1,674 ms ❌ *format broke* | 2,697 ms |

- **Jev is flat.** 1 question or 20, 0.34–0.40 s including the trip over the internet. That's the whole pitch, and it holds.
- **DiffusionGemma is nearly flat once it has read the text.** 20 answers cost 4× one answer, not 20×, because every answer box is filled in the same pass. Reading a *new* text on a laptop is the slow part (0.5–2 s). No trick removes that, but Jev's datacentre hardware hides it.
- **Qwen gets slower with every question**, because it has to type each answer. At 20 questions it's 4.6× slower than DiffusionGemma, and its reply no longer matched the requested format.

### 🔢 Tokens and 💰 cost per decision

| | **Jev** | **DiffusionGemma** | **Qwen: types the answer** |
|---|---:|---:|---:|
| Input tokens, one question (movie review / news article) | 300 / 361 | ~103 / ~152 | ~110 |
| **Output tokens, one question** | 20 / 47 (reported, billed at $0) | **0** | 5 |
| Output tokens, 20 questions | 354 (billed at $0) | **0** | 92 |
| Price | $0.042 per 1M input tokens; output free | $0 (my hardware) | $0 (my hardware) |
| **Cost per 1,000 decisions** | **$0.013–0.015** | **$0** | **$0** |
| Whole 400-question benchmark | **$0.0056** | $0 | $0 |

*Token counts use each model's own tokenizer and prompt wrapper, so compare them as orders of magnitude, not exactly. Jev's input count is ~3× the others for the same text because TypeSafe adds its own instructions. Its "output tokens" are what the API reports; it doesn't return any text.*

### 🎯 Quality: same 400 questions (200 movie reviews: *positive?* · 200 news articles: *which of 4 topics?*)

| | **Jev** | **DiffusionGemma** (1 pass) | DiffusionGemma (OpenJev default, ≤4 passes) | Qwen: reads probabilities | **Qwen: types the answer** |
|---|---:|---:|---:|---:|---:|
| Movie reviews correct | **94.0 %** | 89.0 % | 90.5 % | 83.0 % | 83.0 % |
| News topics correct | **85.0 %** | 77.0 % | 78.0 % | 73.5 % | 65.5 % |
| Broken replies | 0 | 0 | 0 | 0 | **31 of 400** |
| Calibration error, ECE (0 = perfect) | **0.070 / 0.109** | 0.077 / 0.167 | 0.087 / 0.163 | 0.170 / 0.230 | — (no probabilities) |
| Median time per decision | **334 / 336 ms** | 534 / 700 ms | 816 / 991 ms | 506 / 601 ms | 549 / 652 ms |

*Calibration asks whether a stated "95 % sure" is right 95 % of the time. Lower ECE is better; [Step 4](#step-4-what-calibrated-means) explains it.*

### When to use which

| You need… | Use |
|---|---|
| Decisions at scale, fastest and most accurate, and a cloud API is fine | **Jev**: ~0.34 s flat, 94 % / 85 %, ~$0.014 per 1,000 decisions |
| Decisions that must stay on your own hardware (privacy, offline, no API bill) | **DiffusionGemma** as a local Jev: 0 output tokens, 0 broken replies, many questions per pass |
| One quick local decision and you already run a chat model | **Qwen reading probabilities** ([code below](#the-read-trick-on-a-normal-model)): same speed, no format errors |
| Chat, writing, code, summaries | A normal model. Neither Jev nor a System One read writes text. |

**Verdict:**
- **Jev's speed claim holds:** flat 0.34–0.40 s from 1 to 20 questions.
- **The "free open-source Jev" claim is half true.** DiffusionGemma really does answer many questions in one pass with zero output tokens. On an 8 GB laptop it isn't flat for new text, and it's 5–8 points less accurate than Jev.
- **Every model stopped producing broken replies** once we read probabilities instead of parsing typed text. If you take one lesson from this page, take that one.

---

## The idea, one step at a time

Each step uses only what came before it. If you already know how language models work, skip to [Step 6](#step-6-what-a-system-one-read-is).

### Step 1: A language model guesses the next word

A language model is a giant pile of numbers that has read a lot of text. Give it some words and it does exactly one thing: it scores what should come next. It doesn't just pick one word. It gives a **score to every word-piece it knows**; DiffusionGemma knows 262,144 of these pieces, called **tokens**. "The cat sat on the" gets a high score for "mat", a lower one for "sofa", and almost nothing for "photosynthesis".

To write a sentence, the program picks a token using those scores, sticks it on the end, and asks again. Token by token, left to right. That's called **autoregressive** generation, and Qwen, Gemma, and ChatGPT all work this way.

### Step 2: Typing the answer out is slow and can go wrong

Say you want to know whether a customer review is positive. You tell the model: *reply with exactly `q1: yes` or `q1: no`*. The model then types `q`, `1`, `:`, ` yes`, one token at a time, and every token is another trip through the whole pile of numbers.

Then your code has to read what it typed. Usually that's fine. Sometimes the model writes `yes: yes`, `q1: Positive`, or just `yes`. In my 400 questions Qwen did this **31 times**, with the exact format sitting in front of it. Your code either crashes on those or has to guess.

The bigger problem is that you never learn **how sure it was**. It wrote "yes", but was that a 51 % yes or a 99 % yes?

### Step 3: Read the scores instead of the text

Remember, the model scores every token *before* it picks one. Those raw scores (**logits**) can be turned into **probabilities** that add up to 1; that conversion is called a **softmax**. So instead of letting the model type ` yes`, you can stop it right after `q1:` and just look: what probability does ` yes` get, and what does ` no` get?

That's the **Qwen: read** method in the tables. Nothing is typed, nothing is parsed, you get a number for every option, and it costs the same as typing a single token.

It has one limit. A normal model only sees what's to its *left*. To read the answer to question 2, the answer to question 1 must already be typed out. So it's one question per read.

### Step 4: What "calibrated" means

A weather forecaster who says "70 % chance of rain" is **calibrated** if it rained on about 70 % of the days they said that. Calibration isn't about being right more often. It's about the number meaning what it says.

The same goes for a model. If it says "95 % sure" on a hundred reviews and gets only 83 of them right, its confidence is worth less than it claims. The standard summary of that gap is **ECE** (expected calibration error): 0 is perfect, and higher is worse.

Why care? The only reason to ask for a probability is to **act on it**: "auto-approve above 0.95, send the rest to a human." That rule only works if 0.95 roughly means 95 %.

### Step 5: A diffusion text model fills in all the blanks at once

A normal model writes left to right, like a typewriter. A **diffusion** text model is trained differently. You give it a block of text where some or all positions are scrambled (filled with random tokens, called **noise**), and it learns to un-scramble **every position at the same time**. Every position sees every other position, both left and right. Repeat that a few times, un-scrambling a bit more each round, and a paragraph appears. Image generators like Stable Diffusion work the same way with pixels, which is where the name comes from.

DiffusionGemma is Google's open-weights diffusion text model. The block it works on is called the **canvas** (up to 256 tokens). Your instructions and your text are still read left to right, like a normal model. Only the canvas is filled in all at once.

### Step 6: What a "System One read" is

"System One" is psychologist Daniel Kahneman's name for fast, intuitive judgement, as opposed to slow, deliberate reasoning ("System Two"). TypeSafe AI sells a hosted model called **Jev** that answers fixed-choice questions in this fast way. The viral post claimed DiffusionGemma can do the same, for free.

Here's the trick. Take a pre-printed form:

```
q1: [ ]
q2: [ ]
```

Everything on the form is already typed out except the boxes. Put random noise in the boxes. Give the model the instructions ("q1: is the review positive, yes/no; q2: topic, A sports / B tech / C food") plus the review, and run **one** un-scrambling pass over the form. Don't let it change anything. Just look at the probabilities it gives `yes` and `no` in box 1, and `A`, `B`, `C` in box 2.

That's a **read**: one pass, all boxes at once, every box able to see the others, nothing typed, nothing parsed. Ten boxes cost only a bit more than one, because they're all filled in the same pass.

**OpenJev** is an open-source server that wraps this trick in exactly the same web API that Jev uses. By default, if the first read looks unsure, it does the read up to **4 times** with different noise and averages them. That's the "default, up to 4 passes" column in the tables: 1–1.5 points more accurate, about 280 ms slower on this laptop.

The real Jev is a different, commercial model trained specifically for this job. It's measured in the TL;DR tables through OpenRouter, so you can compare the copy against the original.

### Step 7: Why 8 GB is a problem, and what "offloading experts" means

DiffusionGemma has about 26 billion numbers. Even squeezed to about 4 bits each (**quantization**, "Q4"), that's a 16.8 GB file. The laptop's GPU has 8 GB of its own fast memory (**VRAM**, the countertop in this repo's kitchen analogy), so the model doesn't fit.

The way out is that DiffusionGemma is a **Mixture of Experts** (MoE) model. Its numbers are split into 128 "experts" per layer, and each token uses only 8 of them. Think of a kitchen with 128 specialist cooks where each dish needs only 8. You don't need all 128 at the counter; most can wait in the pantry (the computer's main memory, **RAM**, 29 GB here) and walk over when they're called. `--n-cpu-moe 20` means "keep the experts of 20 of the 30 layers in the pantry." Walking to the pantry is slow, which is why a read here costs hundreds of milliseconds instead of the 94 ms OpenJev reports on a big data-centre GPU.

Two more things had to be fixed before it fit: a 4 GB scratch buffer that wasn't needed, and a setting that copied 10 GB over the GPU cable on every read. They're in [§5](#5-three-things-i-had-to-fix-to-make-it-fit--and-one-i-couldnt) if you're curious.

### Step 8: What the measurements showed

- **The real Jev wins on every quality and speed number**: 94 % / 85 % correct, the best calibration, and 0.34–0.40 s flat whether you ask 1 question or 20, for about $0.014 per 1,000 decisions.
- **Zero broken replies** out of 400, against 31 when Qwen types its answer. But the *Qwen: read* trick also gets zero, so this is a win for "read the probabilities" in general, not for diffusion in particular.
- **DiffusionGemma is more accurate than Qwen on both tasks**: 89 % vs 83 % and 77 % vs 73.5 % against *Qwen: read*, with identical instructions. Caveat: these are different model families, so this says "this model did better here", not "diffusion is smarter".
- **Better calibrated, but still over-confident.** Treat the confidence as a ranking ("this answer is surer than that one"), not a number that's accurate to three decimals. The losing options' probabilities wobble with low-level GPU settings ([§5.4](#54-not-fixed-probabilities-depend-on-the-kernel-path)).
- **Many questions at once is where diffusion earns its keep**: 10 answers in 294 ms once the text has been read, against 94 ms for 1.
- **Free-text writing is slow**: 14.6 tokens per second, about half the speed of a normal model of the same size. Don't use it as your chat model on 8 GB.
- **Not "0.2 s flat."** A fresh decision takes 0.5–0.7 s on this laptop, and most of that is reading your text, which no trick avoids.

---

## Try it: code you can copy

The server speaks Jev's API: one endpoint, `POST /v1/systemone`. You send a `state` (the text to judge) and a dictionary of `questions`. There are three question types:

| Type | You ask | You get back |
|---|---|---|
| `noul` | a yes/no question ("noul" is Jev's name for it) | `noul`: the **probability of yes**, from 0 to 1 |
| `choice` | pick one of up to 128 named options | `choice` (the winner), `probabilities` for every option, `confidence` |
| `score` | pick one of 2–10 ordered levels | `score` (a probability-weighted average of the level **numbers, counted from 0**), `legend` (number → your label), `probabilities`, `confidence` |

`confidence` is 1 when all the probability sits on one option and 0 when it's spread evenly.

### A request and its real answer

Start the server as in [§4](#4-running-it-on-8-gb), then:

```bash
curl -s localhost:8080/v1/systemone -H 'content-type: application/json' -d '{
  "model": "jev-latest",
  "state": "The new phone battery dies by noon and the screen cracked in a week. Avoid.",
  "questions": {
    "positive": {"type": "noul",   "instructions": "Is the review positive?"},
    "topic":    {"type": "choice", "criteria": {"sports": "", "tech": "", "food": ""}},
    "stars":    {"type": "score",  "instructions": "Stars the reviewer would give",
                 "criteria": ["1", "2", "3", "4", "5"]}
  }}'
```

Line by line:
- `model` is fixed; `jev-latest` is an alias the server accepts, so TypeSafe's own SDKs work unchanged.
- `state` is the text being judged.
- Each key in `questions` is a name you choose, and the answer comes back under the same key.
- `criteria` lists the options. For `choice` it's option name → optional description; for `score` it's an ordered list from lowest to highest.

The reply, measured on this laptop in 1.38 s including OpenJev's automatic re-reads (numbers rounded to 4 digits):

```json
{
  "model": "openjev-0.1",
  "answers": {
    "positive": {"type": "noul", "noul": 0.0001435},
    "topic": {"type": "choice", "choice": "tech",
              "probabilities": {"sports": 0.0001637, "tech": 0.9998, "food": 0.0000379},
              "confidence": 0.9982},
    "stars": {"type": "score", "score": 0.1041,
              "legend": {"0": "1", "1": "2", "2": "3", "3": "4", "4": "5"},
              "probabilities": {"0": 0.9027, "1": 0.0915, "2": 0.0050, "3": 0.0008, "4": 0.0001},
              "confidence": 0.7863}
  },
  "usage": {"input_tokens": 159, "output_tokens": 0}
}
```

How to read it:
- `positive.noul` = 0.0001 is **P(yes)**. The model is essentially certain the review is *not* positive.
- `topic.choice` is the winner, and `probabilities` shows every option, so you can see how close the runner-up was. Here it wasn't close.
- `stars` is the tricky one. Levels are numbered **from 0**: level 0 is your label `"1"`, level 1 is `"2"`, and so on (that's what `legend` says). `score` = 0.90 × 0 + 0.09 × 1 + … ≈ 0.10. So "score 0.10" means **one star, with a little doubt towards two**.
- The star rating is the least clear-cut of the three questions, and its `confidence` (0.79) is the lowest. That's the whole point.
- `output_tokens: 0`. Nothing was written.

### A tiny Python client

Needs only `pip install requests`.

```python
import requests

def decide(state, questions, url="http://127.0.0.1:8080/v1/systemone"):
    r = requests.post(url, json={"model": "jev-latest", "state": state, "questions": questions})
    r.raise_for_status()
    return r.json()["answers"]

a = decide(
    "The new phone battery dies by noon and the screen cracked in a week. Avoid.",
    {
        "positive": {"type": "noul", "instructions": "Is the review positive?"},
        "topic": {"type": "choice", "criteria": {"sports": "", "tech": "", "food": ""}},
    },
)

if a["positive"]["noul"] < 0.05:                       # P(yes) is tiny
    print("negative review about", a["topic"]["choice"])

# Act automatically only when sure; otherwise hand it to a person.
if a["topic"]["confidence"] > 0.95:
    print("auto-route to the", a["topic"]["choice"], "team")
else:
    print("low confidence, send to a human:", a["topic"]["probabilities"])
```

There's nothing to parse. Every answer is a number you can compare.

### The same question to a normal chat model, and how parsing breaks

This is what the **Qwen: write** baseline does, simplified from [`systemone_bench.py`](diffusiongemma/systemone_bench.py). The instructions are the exact text OpenJev generates, so both models see the same thing:

```python
import re, requests

system = ('Answer a fixed set of questions about the state the user provides. '
          'Each question lists its allowed answers; reply with exactly one label per question.\n'
          '\nQuestion q1: What is the topic of this news article?\n'
          '  A: World\n  B: Sports\n  C: Business\n  D: Sci/Tech\n'
          '\nReply with one line per question, in this order, formatted as "id: label".')

article = "Oil prices look set to dominate. The price of oil looks set to grab headlines ..."
r = requests.post("http://127.0.0.1:8081/v1/chat/completions", json={
    "messages": [{"role": "system", "content": system}, {"role": "user", "content": article}],
    "max_tokens": 16, "temperature": 0,
    "chat_template_kwargs": {"enable_thinking": False}})
text = r.json()["choices"][0]["message"]["content"]

m = re.fullmatch(r"\s*q1\s*:\s*([A-D])\s*", text)     # we asked for exactly "q1: C"
label = m.group(1) if m else None                      # None = the model broke the format
```

Real replies from the benchmark, and what that parser makes of them:

| Qwen wrote | Parsed as | What went wrong |
|---|---|---|
| `q1: C` | `C` | Nothing. This is what we asked for. |
| `D: D` | nothing | It used the answer as the question id |
| `D: Sci/Tech` | nothing | Same, plus the option's name instead of its letter |
| `A` | nothing | It dropped the `q1:` |

You can write a forgiving parser. The benchmark has one that takes the last thing after a colon that looks like a label, and it lifts Qwen from 65.5 % to 75.0 %. But now you're guessing what the model meant, and you still have no confidence number.

### The read trick on a normal model

The **Qwen: read** baseline pre-fills the reply up to `q1:` and asks llama-server for next-token probabilities instead of generating a token:

```python
import math, requests

URL = "http://127.0.0.1:8081"
messages = [{"role": "system", "content": system}, {"role": "user", "content": article}]
prompt = requests.post(f"{URL}/apply-template", json={           # the chat-formatted prompt as text
    "messages": messages, "chat_template_kwargs": {"enable_thinking": False}}).json()["prompt"]

d = requests.post(f"{URL}/completion", json={
    "prompt": prompt + "q1:", "n_predict": 1, "n_probs": 50, "temperature": 0}).json()

p = {}
for tp in d["completion_probabilities"][0]["top_logprobs"]:
    tok = tp["token"].strip().upper()                           # " C" -> "C"
    if tok in ("A", "B", "C", "D"):
        p[tok] = p.get(tok, 0) + math.exp(tp["logprob"])         # log-probability -> probability
total = sum(p.values())
p = {k: v / total for k, v in p.items()}                         # renormalise over the 4 labels
print(max(p, key=p.get), p)
```

This gives zero format errors and a probability per label, at the cost of one token. What it can't do is answer a second question in the same pass.

### What one DiffusionGemma read does, in pseudo-code

This is what [`dg-systemone-server.cpp`](diffusiongemma/dg-systemone-server.cpp) and OpenJev's `one_read` do between them:

```
prompt = tokens(instructions + state)                    # read left to right once; cached for re-asks
form   = tokens("<thought/>q1: _\nq2: _") + [<turn|>] + padding     # the pre-printed canvas
for each answer box:
    form[box.position] = random_token(seed)              # noise in the box

logits = model(prompt, form)                             # ONE pass; the form sees itself both ways
for each answer box:
    row   = log_softmax(logits[box.position])            # a log-probability for all 262,144 tokens
    probs = softmax(row[allowed_label_tokens])           # keep only yes/no (or A/B/C…), renormalise
    answer[box] = probs                                  # nothing sampled, nothing written
```

OpenJev then turns `probs` into the JSON above. By default, if the first read looks unsure, it repeats the read with fresh noise (up to 4 times) and averages.

---

## Real answers, side by side

Both models got the same inputs and the same instructions, and the replies below are copied verbatim. Collected with [`side_by_side.py`](diffusiongemma/side_by_side.py), and the raw output is in [`examples.json`](diffusiongemma/examples.json).

### Example 1: the news articles where Qwen broke the format

These are the first six AG News articles where **Qwen: write** didn't reply `q1: <letter>`:

| Article (start) | Dataset says | Qwen wrote | DiffusionGemma answered | Jev answered |
|---|---|---|---|---|
| *RealNetworks Gets in Content Business (AP) — RealNetworks Inc. survived the dot-com collapse…* | Sci/Tech | `D: D` | Business (0.9999) ✗ | Business 0.82 / Sci/Tech 0.18 ✗ |
| *Prototype copter-cam: Here, there, everywhere — It can only remain aloft for three minutes…* | Sci/Tech | `D: Sci/Tech` | **Sci/Tech (0.9989)** ✓ | **Sci/Tech (1.00)** ✓ |
| *Oil prices look set to dominate — The price of oil looks set to grab headlines…* | Business | `D: D` | **Business (0.9997)** ✓ | **Business (1.00)** ✓ |
| *CSKA sponsor rejects criticism — Russian oil giant Sibneft today rejected any suggestion of a conflict of interest between Chelsea and CSKA…* | Sports | `A` | **Sports (0.954)**, Business 0.044 ✓ | **Sports (0.98)** ✓ |
| *Dollar Rises Vs Euro on Asset Flows Data — NEW YORK (Reuters) - The dollar extended gains…* | Business | `D: Sci/Tech` | **Business (0.9999)** ✓ | **Business (1.00)** ✓ |
| *Real targets iPod with download price cut — RealNetworks has kicked off… the biggest online music sale…* | Sci/Tech | `D: D` | Business (0.990) ✗ | Business 0.55 / Sci/Tech 0.45 ✗ (confidence 0.39) |

Jev took 308–429 ms per article, network included, and billed 332–373 input tokens (about $0.000015) each.

Three lessons in one table:
1. **Qwen's broken replies weren't just formatting.** `D: D` for an oil-price story means it picked Sci/Tech, which is wrong. The format error was hiding a wrong answer.
2. **DiffusionGemma can be confidently wrong.** It said "Business" at 99.99 % for two RealNetworks stories the dataset files under Sci/Tech. That's the "zero hallucinations" claim failing in plain sight. In fairness, a company's business strategy and a price cut *are* arguably business news, so some "errors" are really the dataset's labels being fuzzy.
3. **Jev knows what it doesn't know.** It got the same two RealNetworks stories "wrong", but it split them 0.82/0.18 and 0.55/0.45, which is honest for genuinely ambiguous articles. DiffusionGemma claimed 99 % on both.
4. **The one DiffusionGemma found hard, it said so.** The football-sponsor story mentions an oil company. DiffusionGemma picked Sports but gave Business 4.4 %, and its confidence dropped to 0.86, the lowest in the table.

### Example 2: a support ticket, five questions at once

> *Hi, I was charged twice for my March invoice and the app keeps logging me out when I try to download the receipt. I need this fixed today, my accountant is waiting. This is the third time I'm writing!!*

Questions: billing issue? software bug? customer angry? which team (billing / engineering / sales / account security)? urgency (not urgent / low / medium / high / critical)?

**Qwen: write** replied in 1,359 ms (30 tokens typed):

```
q1: yes
q2: no
q3: yes
q4: A: billing
q5: 4: critical
```

- Two of the five lines break the requested `id: label` format.
- `q2: no` says there's no software bug, even though the app logging the user out is one.

**DiffusionGemma: read** replied in 1,631 ms for a new ticket, or 650 ms when asked again about the same ticket (both with OpenJev's default re-reads):

| Question | Answer | Probability / confidence |
|---|---|---|
| Billing issue? | yes | P(yes) = 0.999999 |
| Software bug? | **yes** | P(yes) = 0.9999 |
| Customer angry? | yes | P(yes) = 0.999998 |
| Which team first? | billing | billing 0.978, engineering 0.021 → confidence 0.92 |
| Urgency | critical (score 3.91 of 4) | critical 0.909, high 0.090 → confidence 0.81 |

**Jev** replied in **404 ms** over the internet (440 input tokens, 114 reported output tokens, $0.0000185):

| Question | Answer | Probability / confidence |
|---|---|---|
| Billing issue? | yes | P(yes) = 0.99 |
| Software bug? | **yes** | P(yes) = 0.94 |
| Customer angry? | yes | P(yes) = 0.97 |
| Which team first? | billing | billing 0.96, engineering 0.03 → confidence 0.94 |
| Urgency | high → critical (score 3.27 of 4) | high 0.73, critical 0.27 → confidence 0.77 |

DiffusionGemma and Jev agree on all five answers. Jev is less extreme, rating urgency "high" rather than "critical", which is arguably the better call for a double charge.

Asking DiffusionGemma the same five questions as **five separate requests** took 4,680 ms. Filling all five boxes in one pass is what saves the time. Note that Qwen was faster on this single request: typing 30 tokens is quick. Where diffusion wins is correctness of shape, the probabilities, and the growing gap as the number of questions goes up.

---

## Every test, exactly

These are all the inputs and settings behind the tables above. The raw outputs are in [`diffusiongemma/results.json`](diffusiongemma/results.json), [`speed_scaling.json`](diffusiongemma/speed_scaling.json), and [`examples.json`](diffusiongemma/examples.json).

### Setup

| | Jev 1.13 | DiffusionGemma 26B-A4B | Qwen 3 30B-A3B |
|---|---|---|---|
| Where | TypeSafe cloud via OpenRouter, `POST https://openrouter.ai/api/alpha/decisions`, model `typesafe/jev-1.13` (served as `jev-1.13-20260917`) | Laptop: RTX 5060 8 GB, Ryzen AI 9 365, 29 GB RAM | Same laptop |
| Weights | Closed | `unsloth/diffusiongemma-26B-A4B-it-GGUF`, Q4_K_M, 16.8 GB | `Qwen3-30B-A3B-Q4_K_M.gguf`, 17.3 GB |
| Server | — | llama.cpp PR #24423 + `dg-systemone-server` + OpenJev 0.3.0: `-ngl 99 --n-cpu-moe 20 -fa on -c 2048 -ub 512 --no-op-offload` | llama.cpp `b1-1719747` `llama-server`: `-ngl 99 -ncmoe 34 -fa on -c 4096 -np 1 --jinja` |
| Decoding | — | No sampling: probabilities read at the answer slots | `temperature 0`, thinking off (`enable_thinking: false`) |
| Latency includes | Internet round trip from Türkiye to OpenRouter | Local HTTP | Local HTTP |

### Test 1 — 400 labelled decisions (accuracy, calibration, latency, tokens, cost)

- **Data:** 200 reviews sampled from the SST-2 validation set and 200 articles from the AG News test set (`random.seed(0)`), stored in [`diffusiongemma/data/`](diffusiongemma/data/). Example items:
  - `{"text": "dull , lifeless , and amateurishly assembled . ", "label": 0}` (0 = negative)
  - `{"text": "E-commerce still booming Online retail sales continue to show significant growth, according to the latest figures released by the US Department of Commerce.", "label": 3}` (3 = Sci/Tech)
- **One question per request**, sent as `state` = the text, plus:

```json
{"q": {"type": "noul", "instructions": "Is the sentiment of this movie review positive?"}}
```

```json
{"q": {"type": "choice", "instructions": "What is the topic of this news article?",
       "criteria": {"World": "", "Sports": "", "Business": "", "Sci/Tech": ""}}}
```

- **Jev** receives exactly that JSON. TypeSafe builds its own internal prompt, which is why it reports ~3× more input tokens.
- **DiffusionGemma and Qwen** both get OpenJev's generated instructions as the system message, word for word. For the movie reviews:

```text
Answer a fixed set of questions about the state the user provides. Each question lists its allowed answers; reply with exactly one label per question.

Question q1: Is the sentiment of this movie review positive?
  yes
  no

Reply with one line per question, in this order, formatted as "id: label".
```

  For the news articles, the options are listed as `A: World`, `B: Sports`, `C: Business`, `D: Sci/Tech`.
- **Scoring:** the prediction is the option with the highest probability (for yes/no, "positive" means P(yes) > 0.5). *Qwen: write* counts as correct only if the reply is exactly `q1: <label>`; the lenient score also accepts replies like `D: D` or `B: Sports`. *Qwen: read* pre-fills `q1:` and takes the next-token probabilities of the labels (`n_probs: 50`). Calibration is ECE over 10 bins, using the predicted option's probability.
- **Commands:** `systemone_bench.py --reads …` (DiffusionGemma), `--ar-url …` (Qwen), `--jev` (Jev; reads `OPENROUTER_API_KEY`).

### Test 2 — speed as the number of questions grows

- **Text:** one AG News article: *"E-commerce still booming Online retail sales continue to show significant growth, according to the latest figures released by the US Department of Commerce."*
- **Questions:** the first N of these 20 yes/no questions, each phrased *"Does the article mention …?"*: a country, a company, money, a sport, a person, a date, a technology, a government, a number, a city, a crime, an election, a product, science, a war, a stock market, a team, health, the internet, energy.
- **N** = 1, 2, 5, 10, 20, median of 3 runs each.
  - **New text:** a unique marker is appended to the text so nothing is cached. For Qwen, llama-server's prompt cache is also switched off (`cache_prompt: false`).
  - **Text already loaded:** the identical request is repeated.
- **Settings:**
  - DiffusionGemma: one read per request (`OPENJEV_AUTO_MAX=1`), with `OPENJEV_CANVAS=128` so 20 answers fit one form.
  - Qwen: `max_tokens` = 12 × N. It was run twice, with llama.cpp op-offload on and off; the TL;DR shows the faster run for each row.
- **Command:** [`speed_scaling.py`](diffusiongemma/speed_scaling.py) `--qwen URL` / `--dg URL` / `--jev`.

### Test 3 — real answers side by side

- **Articles:** the first 6 AG News articles where Qwen broke the format in a fresh run (indices 8, 9, 12, 21, 25, 28 of the 200).
- **Support ticket:** *"Hi, I was charged twice for my March invoice and the app keeps logging me out when I try to download the receipt. I need this fixed today, my accountant is waiting. This is the third time I'm writing!!"*, with these questions:

```json
{"is_billing": {"type": "noul",   "instructions": "Is this about billing or payments?"},
 "is_bug":     {"type": "noul",   "instructions": "Does the customer report a software bug?"},
 "angry":      {"type": "noul",   "instructions": "Is the customer angry or frustrated?"},
 "team":       {"type": "choice", "instructions": "Which team should handle it first?",
                "criteria": {"billing": "", "engineering": "", "sales": "", "account security": ""}},
 "urgency":    {"type": "score",  "instructions": "How urgent is this ticket?",
                "criteria": ["not urgent", "low", "medium", "high", "critical"]}}
```

- **Command:** [`side_by_side.py`](diffusiongemma/side_by_side.py) `--qwen URL` / `--dg URL` / `--jev`.

**API differences worth knowing:** Jev rejects a `choice` or `score` question that has no `instructions` (HTTP 400), while OpenJev treats that field as optional. Jev also rounds probabilities to 2 decimals.

---

## Glossary for Part 2

| Term | Meaning here |
|---|---|
| **Token** | A word-piece, the unit a model reads and writes; roughly ¾ of an English word. DiffusionGemma's vocabulary has 262,144 of them. |
| **Logits / log-probs / probabilities** | Logits are the raw scores the model gives every token. Softmax turns them into probabilities that sum to 1, and log-probs are their logarithms. A gap of 1 **nat** means one option is e ≈ 2.7× more likely than the other. |
| **Autoregressive** | Writing one token at a time, left to right, where each token only sees what came before it. Qwen, Gemma 4, ChatGPT. |
| **Diffusion (text)** | Un-scrambling a whole block of noisy tokens at once, with every position seeing every other. DiffusionGemma. |
| **Canvas / slot** | The block a diffusion model fills in. Here it's the pre-printed form (at most 64 tokens for OpenJev). A slot is one answer box on it. |
| **Read / decode / canvas pass** | One pass over the canvas with nothing sampled. About 93 ms on this laptop. |
| **Prefill** | Reading the prompt (instructions + text) into the model before the canvas pass. 435–606 ms here, and the biggest cost. It's cached, so re-asking about the same text skips it. |
| **KV cache / prompt-KV store** | The model's working memory of the prompt after prefill. This is what "cached" means above. |
| **Causal vs bidirectional** | Causal: each position sees only what's to its left (the prompt, and everything in an autoregressive model). Bidirectional: every position sees every other (the canvas). |
| **MoE / experts / "26B-A4B"** | Mixture of Experts: the model's layers are split into many experts, and only a few run per token. "26B-A4B" means 26 billion numbers stored, about 4 billion used per token (128 experts per layer, 8 active). |
| **VRAM vs RAM** | VRAM is the GPU's own fast memory (8 GB here). RAM is the computer's main memory (29 GB here), which is much slower for the GPU to reach. |
| **`-ngl 99`, `--n-cpu-moe N`** | Put every layer on the GPU (`-ngl 99`), except the experts of N layers, which stay in RAM. |
| **Op offload / `--no-op-offload`** | llama.cpp's habit of copying RAM-resident weights to the GPU for big batches. It's switched off here because on this laptop the copy costs more than it saves. |
| **Quantization / Q4_K_M / GGUF** | Storing each weight in about 4.5 bits instead of 16, at a small quality cost. GGUF is llama.cpp's file format. |
| **Micro-batch / `-ub`** | How many tokens llama.cpp processes in one chunk. Smaller means less scratch memory. |
| **Flash attention / `-fa`** | A faster, leaner way to compute attention. |
| **Calibration / ECE / Brier** | Calibration: does stated confidence match real accuracy? ECE is the average gap across 10 confidence bins (0 is perfect). Brier is the mean squared error of the probabilities (lower is better). |
| **Confidence** | OpenJev's one-number summary of an answer: 1 − entropy ÷ maximum entropy. 1 means all probability is on one option; 0 means it's evenly spread. |
| **Entropy / re-read** | How spread out a probability distribution is. OpenJev re-reads with new noise, up to 4 times, when a slot's entropy is above 0.1. |
| **p50 / p95** | The median latency, and the latency that 95 % of requests beat. |
| **SST-2, AG News** | Public benchmark datasets: movie-review sentiment (yes/no) and news topic (4 choices). |
| **Jev / OpenJev / System One** | Jev is TypeSafe AI's hosted decision model; OpenJev is an open server with the same API. "System One" is Kahneman's fast, intuitive judgement, used as a brand for this style of model. |
| **vLLM / llama.cpp / MLX** | Programs that run models. vLLM targets data-centre GPUs; llama.cpp runs on almost anything, including small GPUs with offload; MLX is for Apple silicon. |

---

# Part 2 — the detailed version

## 1. The idea in one picture

A chat LLM answers a multiple-choice question the way a person fills in a form with a typewriter: it writes `q1: B`, one character at a time. Then your code has to parse what it typed, and sometimes it typed `B: Sports` instead.

A **System One read** hands the model a form that's already typed out, with only the answer boxes left blank. The model looks at the whole form at once and says how likely each option is for each box. Nothing is written and nothing is parsed. (OpenJev's default policy repeats the read up to 4 times with fresh noise when the first one looks unsure; see §5.3.)

```
prompt  (read once, causally)            canvas  (one bidirectional pass)
┌─────────────────────────────────────┐ ┌───────────────────────────────────────────┐
│ system: Q1 Is the review positive?  │ │ <thought/> q 1 : [??] \n q 2 : [??] <turn|>│
│           yes / no                  │ │                   ▲                ▲       │
│         Q2 Topic? A sports B tech … │ │        noise token│      noise token│      │
│ user:   "Battery dies by noon…"     │ └───────────────────┼────────────────┼───────┘
└─────────────────────────────────────┘                     ▼                ▼
                                          P(yes)=0.00 P(no)=1.00   P(A)=.0002 P(B)=.9998
```

The trick only works on a **diffusion** language model. A diffusion model is trained to fill in a whole block of noisy positions at the same time, and every position can see every other one. DiffusionGemma is Google's open-weights 26B-A4B text-diffusion MoE (Apache-2.0), built on the Gemma 4 backbone.

---

## 2. Who's who

| Name | What it is | Status (Sep 2026) |
|---|---|---|
| **Jev** (TypeSafe AI) | Proprietary "System One model". You send a state plus typed questions (yes/no, `choice`, `score`) and get back probabilities and a confidence. It's trained with "reinforcement learning for calibrated decisions". The vendor claims 70–500 ms and a 40–200× speed-up over frontier LLMs. | Hosted API only |
| **DiffusionGemma 26B-A4B** | Google's open text-diffusion MoE: 128 experts, 8 active, ~3.8 B active parameters, 256-token canvas, Gemma 4 vocabulary (262 K) | Open weights |
| **vLLM PR [#57250](https://github.com/vllm-project/vllm/pull/57250)** (Matt Mastracci) | Adds seeded canvases, read-only steps, and step caps, so DiffusionGemma can do System One reads. Ships a prototype `/v1/systemone` example server. | **Open, not merged** |
| **[OpenJev](https://github.com/razorback16/openjev)** (razorback16) | Jev-compatible API server (TypeSafe's SDKs work unchanged) on top of that PR. Two backends: **vLLM** (NVIDIA, 24 GB+) and **MLX** (Apple silicon). | v0.3.0, commit `2050fdb` (its compose file still tags image `0.2.1`) |
| **llama.cpp PR [#24423](https://github.com/ggml-org/llama.cpp/pull/24423)** (Unsloth) | DiffusionGemma in llama.cpp: `llama-diffusion-cli` for chat, plus a prompt-KV cache (PREFILL → DECODE) | **Open, not merged** |
| **This repo** | `diffusiongemma/`: a llama.cpp System One read server and a third OpenJev backend, so the Jev API runs on an **8 GB** GPU | New |

---

## 3. Why not the one-liner Docker command

The post's command:

```bash
docker run --gpus all -p 8000:8000 -v ~/.cache/huggingface:/root/.cache/huggingface razorback16/openjev:latest
```

It has three problems:

1. **Wrong port.** OpenJev serves on **8080**. Port 8000 is the internal vLLM server, and it's bound to `127.0.0.1` inside the container, so mapping it exposes nothing. The project's own README uses `docker compose up -d`, which maps 8080 and sets `ipc: host`.
2. **It needs 24 GB+ of VRAM.** The default checkpoint is `nvidia/diffusiongemma-26B-A4B-it-NVFP4` on vLLM. vLLM has no equivalent of llama.cpp's `--n-cpu-moe`, so an 8 GB card can't load it.
3. **It's a fork of an unmerged PR.** That's fine for experiments, but it's not "vLLM supports this".

So on this laptop, the path is **llama.cpp PR #24423 + expert offload + a small read server**.

---

## 4. Running it on 8 GB

```bash
cd llm-inference/diffusiongemma
./build.sh                       # llama.cpp PR #24423 + dg-systemone-server, CUDA sm_120
hf download unsloth/diffusiongemma-26B-A4B-it-GGUF --include "*Q4_K_M*" --local-dir ../models/diffusiongemma-26b-a4b   # 16.8 GB

uv venv .venv && uv pip install --python .venv/bin/python -e ../build/openjev-src   # git clone razorback16/openjev there first
.venv/bin/python openjev_llamacpp.py \
    -m ../models/diffusiongemma-26b-a4b/diffusiongemma-26B-A4B-it-Q4_K_M.gguf \
    -ngl 99 --n-cpu-moe 20 -fa on -c 2048 -ub 512 --no-op-offload

curl -s localhost:8080/v1/systemone -H 'content-type: application/json' -d '{
  "model": "jev-latest",
  "state": "The new phone battery dies by noon and the screen cracked in a week. Avoid.",
  "questions": {
    "positive": {"type": "noul", "instructions": "Is the review positive?"},
    "topic":    {"type": "choice", "criteria": {"sports": "", "tech": "", "food": ""}},
    "stars":    {"type": "score", "instructions": "Stars the reviewer would give", "criteria": ["1","2","3","4","5"]}
  }}'
```

The full reply to this exact request, explained line by line (including why `noul` is P(yes) and why `score: 0.10` means one star), is in [Part 1: A request and its real answer](#a-request-and-its-real-answer).

The pieces:

| File | Role |
|---|---|
| [`diffusiongemma/dg-systemone-server.cpp`](diffusiongemma/dg-systemone-server.cpp) | A persistent process that loads the GGUF once. For each read it runs **PREFILL**(prompt) into the PR's prompt-KV store, then **one DECODE** over the canvas with self-conditioning off, and returns temperature-1 log-probs at the answer slots. A repeated prompt skips the prefill. |
| [`diffusiongemma/openjev_llamacpp.py`](diffusiongemma/openjev_llamacpp.py) | A third OpenJev backend. All of OpenJev's schema, template, noise seeding, re-read policy, and response shape are reused; only `one_read` is swapped. Text only: no images, `think`, `steps>1`, or `/v1/chat/completions`. |
| [`diffusiongemma/systemone_bench.py`](diffusiongemma/systemone_bench.py) | Accuracy, calibration, and latency benchmark, plus two autoregressive baselines. Results go to [`results.json`](diffusiongemma/results.json). |
| [`diffusiongemma/build.sh`](diffusiongemma/build.sh) | Fetches PR #24423 and grafts in the server. |

---

## 5. Three things I had to fix to make it fit — and one I couldn't

*Engineering detail. If you only want results, skip to [§6](#6-results).*

### 5.1 A 4.2 GB buffer that had nothing to do with the model

The first sweep ran out of memory below `--n-cpu-moe 28`. The failing allocation was a **4,218 MiB compute buffer**, not expert weights. llama.cpp reserves full-vocabulary logits for every row of a micro-batch: 262,144 vocab × 4 bytes = **1 MiB per token**. With the micro-batch equal to a 4,096-token context, that's 4 GiB before a single expert loads.

The fix was a 512-token micro-batch and chunked prefill. The canvas is at most 64 tokens for OpenJev, so it always fits. Result: **peak VRAM at `ncmoe=28` fell from 7,439 to 3,737 MiB**, and the offload floor moved from 28 to **20** of 30 expert layers.

### 5.2 Prefill was being shipped over PCIe

With `ncmoe` fixed, the prefill still took ~620 ms for a ~100-token prompt, and it got faster as more experts moved to the GPU. That points to llama.cpp's **op offload**: for batches of 32+ tokens it copies CPU-resident expert weights to the GPU to do the matrix multiply, so every prefill streamed about 10 GB over PCIe. Computing them in place with **`--no-op-offload`** cut prefill **624 → 423 ms** and a decision **1,000 → 800 ms**. (The server has to pass the flag through into `llama_context_params`. My first version didn't, and the "no change" result was the clue.)

### 5.3 The re-read policy assumes a big GPU

OpenJev re-reads with fresh noise, up to 4 times, when a slot's entropy is above 0.1. It measures that entropy over the **whole-vocabulary** top-k. DiffusionGemma leaks a few percent of probability to `<turn|>`, `<eos>`, and punctuation even when it's sure (`yes` 0.86–0.94 of the full vocabulary, >0.98 of the two labels). So the entropy is 0.26–0.59 and **every request is read 4 times**. On vLLM the 4 reads run as one batch and cost almost nothing. On one laptop GPU they run in sequence: **+282–291 ms for +1.0–1.5 accuracy points** (§6.1).

### 5.4 Not fixed: probabilities depend on the kernel path

The same prompt and canvas give different label log-probs depending on the code path:

| Path (PR's own reference server, same request) | World | Sports | Business | Sci/Tech |
|---|---:|---:|---:|---:|
| unified forward, flash-attn off | −3.06 | **−0.18** | −5.40 | −4.64 |
| unified forward, flash-attn on | −6.49 | **−0.33** | −5.47 | −3.56 |
| prompt-KV cache, flash-attn off | −3.05 | **−0.49** | −4.11 | −4.37 |
| prompt-KV cache, flash-attn on | −4.55 | **−0.05** | −5.28 | −3.80 |

My server's chunked vs single-shot prefill shows the same kind of spread. Every run is deterministic, and **the winning label never changed** in any comparison. But the losing labels move by 1–3 nats. My best explanation: in a Q4 MoE, tiny numerical differences (F16 vs F32 attention accumulation, chunk boundaries) flip which experts get routed. **Treat the confidence as a reliable ranking signal, not a number that's accurate to three decimals.**

---

## 6. Results

Setup: Q4_K_M GGUF, `-ngl 99 --n-cpu-moe 20 -fa on -ub 512 --no-op-offload`, peak VRAM 7.6 GB. Tasks: 200 random SST-2 validation reviews (yes/no: *is it positive?*) and 200 random AG News test articles (4-way topic choice), seed 0. Prompts average 103 and 152 tokens. DiffusionGemma and Qwen get the **same OpenJev-generated system prompt**. Jev gets the same `{state, questions}` JSON and builds its own prompt.

Baselines: **Qwen 3 30B-A3B** Q4_K_M on stock llama.cpp `b1-1719747` (`-ncmoe 34`, llama-server), used two ways:
- **generate**: it writes `q1: <label>` in up to 16 tokens, thinking disabled;
- **read**: its chat reply is pre-filled up to `q1:`, and I take the next-token probabilities of the labels. That's the autoregressive version of a System One read: one prefill, zero generated tokens.

### 6.1 Accuracy, calibration, latency

| System | SST-2 acc | AG News acc | Invalid replies | ECE ↓ (SST-2 / AG) | Mean confidence (SST-2 / AG) | p50 latency (SST-2 / AG) |
|---|---:|---:|---:|---|---|---|
| Qwen 3 30B-A3B — generate | 83.0 % | 65.5 % (75.0 % if parsed leniently) | **31 / 400** | — | — | 549 / 652 ms |
| Qwen 3 30B-A3B — read | 83.0 % | 73.5 % | 0 | 0.170 / 0.230 | 0.992 / 0.965 | 506 / 601 ms |
| **DiffusionGemma — 1 read** | **89.0 %** | **77.0 %** | **0** | **0.077** / 0.167 | 0.967 / 0.937 | **534 / 700 ms** |
| DiffusionGemma — OpenJev default (≤ 4 reads) | 90.5 % | 78.0 % | 0 | 0.087 / 0.163 | 0.968 / 0.937 | 816 / 991 ms |
| **Jev 1.13** (TypeSafe, via OpenRouter; latency includes the network) | **94.0 %** | **85.0 %** | 0 | **0.070 / 0.109** | 0.870 / 0.951 | **334 / 336 ms** |

*ECE = expected calibration error: the average gap between the confidence it states and how often it's right (10 bins; 0 is perfect). Brier scores are in `results.json`.*

How to read this:
- **Accuracy: DiffusionGemma wins on both tasks with the same prompt**: +6 points on SST-2 and +3.5 on AG News against the *Qwen read* row. Against *Qwen generate* it's +6 and +11.5, or +2 on AG News if Qwen's malformed replies are forgiven. (Caveat: Qwen 3 is a 2025 model and a different family. Gemma 4 26B-A4B, the same backbone run autoregressively, wasn't on disk.)
- **Qwen's "invalid replies" are real format drift.** On AG News it answered `D: D`, `B: Sports`, or a bare `C` 31 times, even though it was told the exact format. A later re-run for [the side-by-side examples](#real-answers-side-by-side) counted 42: llama-server's prompt caching makes runs not bit-identical. Scored leniently it reaches 75.0 %, still below DiffusionGemma.
- **You don't need diffusion to get zero format errors.** The Qwen *read* also has none, at the same latency as generating. What diffusion adds is below.
- **Calibration is the clearest difference.** Qwen's read says it's 99.2 % sure on SST-2 and is right 83 % of the time. DiffusionGemma says 96.7 % and is right 89 %. Both are overconfident on AG News, where World, Business, and Sci/Tech overlap; DiffusionGemma less so.
- **For one question on a new state, the two cost about the same** (~0.5–0.7 s). Almost all of that is reading the prompt (prefill p50: 438 ms for SST-2, 601 ms for AG News in the 1-read run). The canvas pass itself is **~94 ms**.

### 6.2 Many questions, one pass — the part diffusion is actually good at

The same AG News article, N yes/no questions per request, one read each (re-reads off):

| Questions per request | Same state asked again (prompt cached) | …of which the canvas pass | New state (prefill + read) |
|---:|---:|---:|---:|
| 1 | 94 ms | 91 ms | 556 ms |
| 2 | 99 ms | 95 ms | 625 ms |
| 5 | 163 ms | 155 ms | 875 ms |
| 10 | **294 ms** | 282 ms | 1,331 ms |
| 20 | 2,686 ms | 151 ms per canvas | 2,720 ms |

- **Ten answers cost 3.1× one answer, not 10×.** An autoregressive model writes answer 1, then answer 2, and so on. Here all ten slots are filled in the same pass, and each slot can see the others.
- **It isn't flat, though.** A longer canvas is a bigger batch, which touches more of the 128 experts in each layer, and on this laptop most of them sit in system RAM.
- **Cold latency grows because the prompt grows.** OpenJev puts every question's wording in the system prompt.
- **20 questions falls off a cliff.** Past 10 questions OpenJev switches to a compact format and splits into two canvases, each with its own system prompt. My server caches one prompt, so the two groups keep evicting each other and it re-prefills every time. A two-entry cache would fix it.

### 6.3 Offload sweep (30 SST-2 decisions, OpenJev default policy, op-offload on)

| `--n-cpu-moe` | Peak VRAM | p50 decision | Prefill p50 | Canvas pass p50 |
|---:|---:|---:|---:|---:|
| 28 | 3,737 MiB | 1,277 ms | 820 ms | 112 ms |
| 26 | 4,795 MiB | 1,205 ms | 765 ms | 108 ms |
| 24 | 5,671 MiB | 1,136 ms | 720 ms | 102 ms |
| 22 | 6,639 MiB | 1,062 ms | 670 ms | 96 ms |
| **20** | **7,607 MiB** | 1,000 ms | 624 ms | 90 ms |
| **20 + `--no-op-offload`** | 7,607 MiB | **801 ms** | **423 ms** | 91 ms |
| 18 | — | **OOM** | — | — |

### 6.4 Chat-style generation (for completeness)

`llama-diffusion-cli -ngl 99 --n-cpu-moe 28 -fa on -n 256` (`--n-cpu-moe 26` runs out of memory: generation needs a 1.4 GB transposed embedding for self-conditioning, plus a bigger micro-batch):

| Mode | Speed | Notes |
|---|---:|---|
| DiffusionGemma, diffusion generation | **14.6 tok/s** | 256-token block in 20 denoising steps × ~875 ms. The reply was coherent (a short thought block, then a correct explanation of the refrigeration cycle). Op-offload on or off made no difference (14.5 vs 14.7). |
| Gemma 4 26B-A4B, autoregressive (same backbone, same `ncmoe=28`, [BENCHMARKS.md](BENCHMARKS.md)) | 28.7 tok/s | |

On 8 GB, **diffusion generation is about 2× slower than autoregressive generation on the same backbone**. Each denoising step is a 256-token batch that touches nearly every expert, and those experts live in system RAM. The "1,100 tok/s" headline is an H100 with FP8, with everything in VRAM.

---

## 7. So when do you use which?

| | Autoregressive LLM (Qwen, Gemma 4, …) | DiffusionGemma as a System One reader |
|---|---|---|
| **You send** | A prompt and instructions about format | A state plus **typed questions**: yes/no, choice (≤128 options), score (≤10 levels) |
| **You get** | Text to parse | A probability for every option, a confidence, and nothing to parse |
| **Several questions** | Answered in sequence; later answers see earlier ones | Filled in one pass; slots see each other both ways |
| **Open-ended output** | ✅ chat, code, writing, extraction | ❌ every answer must be a single-token slot |
| **Reasoning first** | ✅ thinking tokens | Only through an optional `think` pass, which is text generation again (not available in the llama.cpp backend) |
| **8 GB laptop speed** | 506–652 ms per decision; 28.7–53.8 tok/s generation | 534–700 ms per new decision; **94 ms re-asking a state**; 294 ms for 10 answers; 14.6 tok/s generation |

**Good fits for System One reads:** ticket or alert triage, intent routing, content moderation, "should the agent retry / escalate?", checking 10 attributes of one document, and gating with thresholds ("auto-approve above 0.95, otherwise a human"). Thresholds only work because the confidence carries some meaning.

**Bad fits:** anything where the answer isn't a short, fixed list, anything that benefits from visible reasoning, and throughput chat on small VRAM.

---

## 8. A claims audit

| Claim in the post | Verdict | Evidence |
|---|---|---|
| "A patch contributed to vLLM by Matt Mastracci" | ⚠️ **Partly true** | It's an **open, unmerged** PR (#57250, opened 2026-09-16). OpenJev's image builds a fork of it. |
| "Evaluates choices in a single parallel pass (~0.2 s flat)" | ❌ **Not flat for DiffusionGemma here**; ✅ roughly true for the real Jev | The real Jev measured 0.34–0.40 s flat from 1 to 20 questions, network included (TL;DR). For DiffusionGemma, OpenJev's own figures: 94 ms p50 on an RTX PRO 6000 at concurrency 1, **760 ms at 64 concurrent**; 0.2–0.4 s on an M3 Ultra. On this 8 GB laptop: **534–700 ms** for a new state, 94 ms for a cached one. Latency grows with the number of questions (§6.2) and with prompt length. |
| "Denoises across an open canvas in a single step instead of sequential generation" | ✅ **For reads**, ⚠️ with caveats | One decoder pass per read, yes. But OpenJev's default re-reads **4×** whenever entropy > 0.1, which on this model is nearly every request (§5.3). Generation takes ~20–48 steps per 256-token block. |
| "Full bidirectional attention… standard LLMs only look backward" | ⚠️ **Misleading** | Only the **canvas** is bidirectional. The prompt is encoded **causally**, exactly like an autoregressive model, and an autoregressive answer token also attends to the entire prompt. The real gain is that answer slots see each other. |
| "Multimodal grounding (image classification, UI navigation)" | ⚠️ **Backend-dependent; untested here** | The model takes images, and OpenJev's vLLM and MLX backends support them. The llama.cpp PR and GGUF are text-only today. |
| "Zero hallucinations: schema formatting errors are entirely eliminated" | ⚠️ **Format: yes. Hallucinations: no.** | 0 invalid replies in 400 (Qwen generating: 31/400). But **9.5–23 % of answers were still wrong** (some confidently; see [Example 1](#example-1-the-news-articles-where-qwen-broke-the-format)), and an autoregressive logit read *also* had 0 format errors. Grammar-constrained decoding would too. |
| "Highly-calibrated decision engine" | ⚠️ **Better, not solved** | ECE 0.077 vs 0.170 on SST-2, compared with Qwen's *read* (Qwen's normal text replies have no confidence at all). But on AG News it says 94 % and is right 77 %, and losing-label probabilities shift by 1–3 nats with the kernel path (§5.4). |
| "An open-source alternative to Jev" | ⚠️ **API-compatible, but not equal** | TypeSafe's SDKs work against OpenJev unchanged. Measured head to head on the same 400 questions, Jev 1.13 was **5–8 points more accurate** (94 % / 85 % vs 89 % / 77 %), **better calibrated** (ECE 0.070 / 0.109 vs 0.077 / 0.167), and **faster** (334 ms vs 534–700 ms per new decision) than DiffusionGemma on this laptop, for about $0.014 per 1,000 decisions. |
| `docker run … -p 8000:8000 … razorback16/openjev:latest` | ❌ **Wrong port; wrong hardware for most readers** | The API is on **8080** (8000 is internal vLLM on 127.0.0.1). It needs **24 GB+** of VRAM. Use `docker compose up -d` from the repo on a big GPU, or §4 here on a small one. |

**Bottom line:** the core idea is real and clever. Pin the answer template, leave single-token holes, and read the distribution out of one bidirectional pass. On this laptop it gave **more accurate, better-calibrated, never-malformed decisions** than a strong autoregressive MoE, and **multi-question requests at a fraction of the cost**. It's not "0.2 s flat" on consumer hardware, it doesn't abolish wrong answers, and it's the wrong tool for anything that needs text.

---

## 9. Reproduce

```bash
cd llm-inference/diffusiongemma
# baselines (stock llama.cpp, Qwen 3 30B-A3B)
../build/llama.cpp/build-cuda/bin/llama-server -m ../models/qwen3-30b-a3b/Qwen3-30B-A3B-Q4_K_M.gguf \
    -ngl 99 -ncmoe 34 -fa on -c 4096 -np 1 --port 8081 --jinja &
.venv/bin/python systemone_bench.py --ar-url http://127.0.0.1:8081 --ar-name qwen3-30b-a3b-ar

# DiffusionGemma reads (OpenJev default policy, then single read)
A="-m ../models/diffusiongemma-26b-a4b/diffusiongemma-26B-A4B-it-Q4_K_M.gguf -ngl 99 --n-cpu-moe 20 -fa on -c 2048 -ub 512 --no-op-offload"
.venv/bin/python systemone_bench.py --reads --label diffusiongemma-openjev-default -- $A
OPENJEV_AUTO_MAX=1 .venv/bin/python systemone_bench.py --reads --no-sweep --label diffusiongemma-single-read -- $A
```

Builds: llama.cpp PR #24423 head `12e0a96`; OpenJev `2050fdb`; stock llama.cpp `b1-1719747`. Eval subsets: `diffusiongemma/data/` (from `stanfordnlp/sst2` validation and `fancyzhx/ag_news` test, `random.seed(0)`).

## Sources

- TypeSafe AI — [Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- [razorback16/openjev](https://github.com/razorback16/openjev) — README benchmarks, `engine.py`, `mlx_backend.py`, `docker-compose.yml`
- vLLM [PR #57250](https://github.com/vllm-project/vllm/pull/57250) — structured generation mode for DiffusionGemma (Jev-like)
- llama.cpp [PR #24423](https://github.com/ggml-org/llama.cpp/pull/24423) — DiffusionGemma support
- Hugging Face — [google/diffusiongemma-26B-A4B-it](https://huggingface.co/google/diffusiongemma-26B-A4B-it), [unsloth GGUF](https://huggingface.co/unsloth/diffusiongemma-26B-A4B-it-GGUF), [nvidia NVFP4](https://huggingface.co/nvidia/diffusiongemma-26B-A4B-it-NVFP4)
