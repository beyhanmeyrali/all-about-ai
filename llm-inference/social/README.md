# social/ — ready-to-publish posts and articles

Write-ups of the work in this repo, formatted for social platforms and ready to copy.

## Layout

```
social/
├── linkedin/
│   ├── articles/<date>-<topic>/     one folder per article
│   │   ├── article.md               cover, title and body, with images in place
│   │   ├── images/                  cover + figures (named for what they show)
│   │   └── make_charts.py           redraws the images from the measured data (if any)
│   └── posts/<date>-<topic>.md      short LinkedIn posts
└── x/
    └── threads/<date>-<topic>.md    X (Twitter) threads
```

**Naming:** `YYYY-MM-DD-short-topic`, where the date is the day it was written. The same topic keeps the same name on every platform, so the article, the post and the thread about one piece of work sort together.

## Index

| Date | Topic | LinkedIn article | LinkedIn post | X thread | Source in repo |
|---|---|---|---|---|---|
| 2026-09-22 | Jev vs DiffusionGemma vs Qwen vs Bonsai vs Laya: fast AI decisions on an 8 GB laptop | [article](linkedin/articles/2026-09-22-jev-vs-diffusiongemma-qwen-bonsai-laya/article.md) | [post](linkedin/posts/2026-09-22-jev-vs-diffusiongemma-qwen-bonsai-laya.md) | [thread](x/threads/2026-09-22-jev-vs-diffusiongemma-qwen-bonsai-laya.md) | [DIFFUSIONGEMMA.md](../DIFFUSIONGEMMA.md) |

## Publishing a LinkedIn article

1. On LinkedIn, click **Write article**.
2. **Cover:** upload the article's `images/cover-1920x1080.png` (LinkedIn's recommended 16:9 size) and paste its alt text.
3. **Title:** copy it from the `Title` box in `article.md`.
4. **Body:** copy the text below the `Body` line one section at a time, **from the rendered GitHub page**, not the raw file. That way LinkedIn keeps the headings, bold, lists and links.
5. **Images:** at each 📎 line, delete that line from the pasted text, click **+ → Image**, upload the named file, and paste its alt text and caption.

LinkedIn articles can't show tables, which is why every comparison is an image.

## Publishing a post or thread

- **LinkedIn post:** copy the text box and attach the suggested image. Posts must stay under 3,000 characters.
- **X thread:** publish post 1, then reply to it with post 2, and so on. Each post must stay under 280 characters; X counts every link as 23 and every emoji as 2.

## Redrawing an article's images

```bash
cd llm-inference
diffusiongemma/.venv/bin/python social/linkedin/articles/<date>-<topic>/make_charts.py   # needs matplotlib
```

Chart colours come from a colour-blind-safe palette checked with a validator. Every line also has its own marker shape and a direct label, so no chart relies on colour alone.
