# social/ — the LinkedIn article, ready to copy

This is the benchmark in [../DIFFUSIONGEMMA.md](../DIFFUSIONGEMMA.md), written up as a LinkedIn article: Jev vs DiffusionGemma vs Qwen vs Bonsai vs Laya on an 8 GB laptop.

| File | What it is |
|---|---|
| [`linkedin-article.md`](linkedin-article.md) | The article: cover image, title, and body, with every image shown where it goes |
| `charts/0_cover_1920x1080.png` | Cover image, 16:9 at LinkedIn's recommended 1920 × 1080 |
| `charts/1_speed.png` | Time to answer 1–20 questions, all five models |
| `charts/2_accuracy.png` | Accuracy on the same 400 questions |
| `charts/3_tetris.png` | Tetris: lines cleared and games survived |
| [`make_charts.py`](make_charts.py) | Redraws all four images from the measured results in `../diffusiongemma/*.json` |

## Publishing it on LinkedIn

1. On LinkedIn, click **Write article**.
2. **Cover:** upload `charts/0_cover_1920x1080.png` and paste its alt text from the article.
3. **Title:** copy it from the `Title` box in `linkedin-article.md`.
4. **Body:** copy the text below the `Body` line, one section at a time. LinkedIn keeps headings, bold, lists and links when you paste from a rendered page, so copy from the GitHub view rather than the raw file.
5. **Images:** at each 📎 line, delete that line from the pasted text, click **+ → Image**, upload the named file, then paste its alt text and caption.
6. LinkedIn articles can't show tables, which is why every comparison is an image.

## Redrawing the charts

```bash
cd llm-inference
diffusiongemma/.venv/bin/python social/make_charts.py    # needs matplotlib
```

The colours are a colour-blind-safe categorical palette (checked with a palette validator). Every line also has its own marker shape and a direct label, so no chart relies on colour alone.
