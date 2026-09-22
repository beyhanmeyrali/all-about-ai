# LinkedIn post: Jev vs DiffusionGemma vs Qwen vs Bonsai vs Laya

Short version of the [LinkedIn article](../articles/2026-09-22-jev-vs-diffusiongemma-qwen-bonsai-laya/article.md). Copy the text in the box and paste it into a new LinkedIn post. It's 2,989 characters, under LinkedIn's 3,000 limit.

**Suggested image:** attach [`speed-by-question-count.png`](../articles/2026-09-22-jev-vs-diffusiongemma-qwen-bonsai-laya/images/speed-by-question-count.png). Posts with an image get far more reach than text-only ones.

```text
Everyone is talking about Jev, TypeSafe's "System One" decision model. A viral
post claims Google's open DiffusionGemma is a free Jev you can run yourself.

So I measured them on the same 400 questions: real Jev 1.13 (via
OpenRouter), DiffusionGemma run locally on an 8 GB laptop GPU, a normal chat
model (Qwen 3 30B) as the baseline, and a surprise: PrismML's Ternary Bonsai
27B, a 27B model squeezed to 1.75 bits per weight (a 5.9 GB file). Plus Laya,
a tiny open-source "Jev alternative" (a 421M classifier).

⚡ SPEED — time to answer N yes/no questions about one text
• Jev (cloud, network included): 0.40 s for 1 question. 0.34 s for 20. Flat.
• DiffusionGemma (8 GB laptop): 0.09 s → 0.36 s once the text is loaded.
• Qwen typing the answers: 0.10 s → 1.7 s. At 20 questions its format broke.
• Bonsai typing the answers: 0.27 s → 2.4 s. Same problem, slower typist.
• Laya: 0.011 s → 0.057 s. The fastest by far.

🔢 TOKENS: Qwen and Bonsai must write their answers (5 tokens per question).
DiffusionGemma and Laya write 0. Jev bills input only; output is free.

💰 COST per 1,000 decisions
• Jev: $0.013–0.015 (all 400 test decisions cost $0.0056).
• Local models: $0 (my electricity is cheap).

🎮 TETRIS — each model picks every move (3 games, 80 pieces each)
• Jev: survived 3 of 3, 78 lines, 0.31 s per move.
• DiffusionGemma: survived 2 of 3, 52 lines, 3.2 s per move.
• Bonsai: survived 2 of 3, 64 lines, 3.0 s per move.
• Qwen: topped out in all 3, 37 lines, 1.6 s per move.
• Laya: 0 lines in all 3, barely better than random, but 0.03 s per move.

🎯 QUALITY (movie-review sentiment / news topic)
• Jev: 94% / 85%, well calibrated.
• DiffusionGemma: 89% / 77%, zero broken replies.
• Qwen writing answers: 83% / 65.5%, with 31 malformed replies out of 400.
• Bonsai (5.9 GB, fits entirely on the laptop GPU): 92.5% / 86.5%, 0 malformed,
  and the best calibrated of all four. It beats Jev on news topics.
• Laya: 46% on reviews asked as yes/no (it said "no" to all), 92% asked as
  a choice. Its 94% on news is from its own training data.

My take:
1. Jev's speed story is real. Flat 0.34–0.40 s whether you ask 1 question or 20.
2. The "free Jev" story is half true. DiffusionGemma really does answer many
   questions in one pass with zero output tokens, but on an 8 GB GPU it isn't
   flat, and it's 5–8 points less accurate than Jev.
3. For decisions, stop making LLMs type. Reading probabilities instead of
   parsing text removed every format error, for every model.
4. The dark horse: Ternary Bonsai 27B. A 5.9 GB model on an 8 GB laptop is about
   as accurate as Jev on these tasks. It's just slow when it has to type many answers.
5. Laya is ~35x faster than Jev but narrow: great on the task types it was
   trained on, silently wrong outside them. Test it on your own questions.

Full numbers, code, and every test case (open source):
https://github.com/beyhanmeyrali/all-about-ai/blob/main/llm-inference/DIFFUSIONGEMMA.md

#AI #LLM #Jev #DiffusionGemma #LocalLLM
```
