# X thread: Jev vs DiffusionGemma vs Qwen vs Bonsai vs Laya

6 posts. Publish post 1, then reply to it with post 2, and so on. Every post is under X's 280-character limit (X counts the link as 23 characters, and emojis as 2 each, so posts near the limit may need a word trimmed).

**Suggested images:** attach [`speed-by-question-count.png`](../../linkedin/articles/2026-09-22-jev-vs-diffusiongemma-qwen-bonsai-laya/images/speed-by-question-count.png) to post 2 and [`accuracy-400-questions.png`](../../linkedin/articles/2026-09-22-jev-vs-diffusiongemma-qwen-bonsai-laya/images/accuracy-400-questions.png) to post 3.

## Post 1 of 6

```text
I benchmarked TypeSafe's Jev (the "System One" decision model) against 4 models on my 8 GB laptop: DiffusionGemma, Qwen 3 30B, a 5.9 GB ternary Bonsai 27B, and Laya.

400 labelled questions, a speed sweep, and Tetris. All numbers measured. 🧵
```

## Post 2 of 6

```text
⚡ Speed: time to answer 1 → 20 questions about one text

Jev (cloud, network included): 0.40 s → 0.34 s. Flat.
DiffusionGemma: 0.09 → 0.36 s, 0 output tokens
Qwen, typing its answers: 0.10 → 1.7 s, and its format broke at 20
Bonsai, typing: 0.27 → 2.4 s
Laya: 0.011 → 0.057 s
```

## Post 3 of 6

```text
🎯 Accuracy (movie reviews / news topics):

Jev: 94% / 85%
Bonsai 27B, 5.9 GB: 92.5% / 86.5%
DiffusionGemma: 89% / 77%
Qwen 3 30B: 83% / 65.5%, with 31 broken replies

A 5.9 GB model on a laptop, about as accurate as Jev.
```

## Post 4 of 6

```text
💰 Cost per 1,000 decisions

Jev: $0.013–0.015. The whole 400-question test cost me $0.0056.
Local models: $0.

🎮 Tetris (3 games): Jev survived 3/3 at 0.3 s per move. Bonsai 2/3, DiffusionGemma 2/3, Qwen 0/3.
```

## Post 5 of 6

```text
Takeaways:
1. Jev's speed claim is real: flat ~0.34 s.
2. "DiffusionGemma = free Jev" is half true: one pass and 0 output tokens, but not flat on 8 GB, and 5–8 points behind.
3. For decisions, read the model's probabilities instead of parsing its text. Format errors drop to 0.
```

## Post 6 of 6

```text
Everything is open: code, raw results, every test case, and a beginner-friendly explainer.

https://github.com/beyhanmeyrali/all-about-ai/blob/main/llm-inference/DIFFUSIONGEMMA.md
```
