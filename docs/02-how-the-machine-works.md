# How the machine works (physical + technical)

No jargon without a translation.

## Two programs, two windows, two ports

You start **two** programs. Leave both windows open.

| Program | Job | Address |
|---|---|---|
| **Backend** (Flask, Python) | Brain: fetch page, extract fields, run rules, save DB, PDF | http://127.0.0.1:5000 |
| **Frontend** (React, Vite) | Face: buttons, pages, tables | http://127.0.0.1:5173 |

`127.0.0.1` means “this computer only.” It is not on the public internet.

The dashboard talks to the brain through `/api/...` (Vite proxies those calls to port 5000).

## What lives on the disk

**C: project folder** — source code (Python, React, DemoMart HTML, docs).

**D:\legal-metrology** — heavy stuff so C: does not fill up:

- `venv\` — Python with Flask **and** PyTorch (the NER model needs this one)
- `browsers\` — Chromium for Playwright (optional, for real websites)
- `data\` — SQLite database, uploads, reports
- `hf-cache\` — HuggingFace cache
- NER weights: `backend\app\ml\ner_model\` (the `.safetensors` file is large; it is gitignored)

If you start Python from the **system** (`py -3`) instead of the D: venv, the website still works but **NER is off**. Health will say `ner_available: false`.

## The path of one scan

```
You click Scan
    → frontend POST /api/scan/url  (or /text, /image, /sample)
    → pipeline.py
         1. Get words
              URL  → scraper (requests, maybe Playwright)
              Image → Tesseract OCR (optional)
              Sample / paste → already words
         2. Extract seven fields
              regex (always)
              DistilBERT NER (if weights + torch exist)
              hybrid merge
         3. Rule engine (JSON rules, not an AI)
         4. Save SQLite
         5. Return JSON: fields, findings, score
    → frontend shows the inspection page
    → you confirm / reject
    → PDF if you ask
```

## DemoMart (the fake shop)

URL: http://127.0.0.1:5000/demo/

Python builds Amazon-looking HTML (`backend/app/demo_store/`). Product photos sit in `static/images/`. The scraper treats DemoMart like a real site, so the viva does not depend on Amazon being nice.

About **27** products: the GitHub 17-item catalogue plus extra **regex-blind** grocery packs for the NER demo.

## The GitHub user interface

This is the UI on `main` (not the older single-page scanner):

| Hash | Page |
|---|---|
| (home) | Landing |
| `#scanner` | Compliance scan workspace |
| `#rules` | Rule explanations |
| `#history` | Catalogue / past scans |

You scan from **Product URL**, **Paste text**, or **Image**. DemoMart URLs are the reliable ones.

## Database

SQLite file, usually `D:\legal-metrology\data\compliance.db`.

Tables hold products, extracted fields, findings, reviews, reports. No MongoDB. No cloud.

## What “physical” means in a viva

- Two processes, two ports.
- One local fake shop.
- One local database.
- One local neural net file (optional).
- Your laptop. No paid API key.

Next: [03-regex-and-ai.md](03-regex-and-ai.md)
