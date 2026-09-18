# AI-Based Automated Legal Metrology & E-Commerce Compliance Checker

**Mini project (SIES GST · Computer Engineering · Idea Presentation 2026–27)**  
Decision-support web app that screens e-commerce product listings / packaging for **potential** missing Legal Metrology–style declarations.

> **Not a legal authority.** Automated findings are first-pass screening only. A human reviewer must confirm before any enforcement conclusion.

---

## What it does

1. Accept **product URL**, **packaging image**, **pasted text**, or **demo samples**
2. Collect page text (scraper) and/or OCR text (optional free Tesseract)
3. **Precision-first field extraction** (MRP, net qty, manufacturer, origin, dates…)
4. Run a **configurable rule engine** (presence / any-of / ambiguous)
5. Show **evidence + confidence** on a regulator-style dashboard
6. Support **human review** (confirm / reject / needs review)
7. Generate **JSON / PDF reports**

---

## Stack (MVP)

| Layer | Choice | Notes |
|-------|--------|--------|
| Frontend | React + Vite | Dashboard UI |
| Backend | Flask | APIs + orchestration |
| DB | SQLite | Free, zero-setup (Mongo-shaped schema) |
| Field extract | Regex + optional DistilBERT NER | Hybrid default; regex never replaced |
| OCR | Tesseract (optional) | Free; samples/text work without it |
| Scraper | requests + BeautifulSoup | Best-effort; demos use samples |

---

## Read these first (plain language)

| Doc | For |
|-----|-----|
| [docs/01-what-is-this.md](docs/01-what-is-this.md) | Anyone, including a kid |
| [docs/02-how-the-machine-works.md](docs/02-how-the-machine-works.md) | Two programs, ports, files on disk |
| [docs/03-regex-and-ai.md](docs/03-regex-and-ai.md) | Regex vs DistilBERT NER vs rules |
| [docs/04-start-by-yourself.md](docs/04-start-by-yourself.md) | Start the site with no AI assistant |
| [docs/05-demo-script-and-limits.md](docs/05-demo-script-and-limits.md) | Viva script and honest limits |

---

## Quick start

**One command** (opens backend + frontend windows):

```powershell
.\START-EVERYTHING.ps1
```

Then open http://127.0.0.1:5173/  and  http://127.0.0.1:5000/api/health  
`ner_available` must be `true` for the NER demo. Full click-path: [docs/04-start-by-yourself.md](docs/04-start-by-yourself.md).

### 1. Backend (uses D: for venv + Chromium + DB)

Heavy runtime is on **D:\legal-metrology** so C: is not filled with browsers (~700 MB Chromium).

```powershell
# Preferred — D: Python venv + Playwright browsers
D:\legal-metrology\scripts\start-backend.ps1

# Or from project root (auto-uses D: if present)
.\start-backend.ps1
```

One-time repair of D: setup:

```powershell
D:\legal-metrology\scripts\setup-d-drive.ps1
```

API: http://127.0.0.1:5000  
Health: http://127.0.0.1:5000/api/health — check `ner_available: true` and `extractor_mode: hybrid`  
DemoMart: http://127.0.0.1:5000/demo/

### 2. Frontend

```powershell
cd C:\Users\admin\Documents\legal-metrology-compliance-checker\frontend
npm install
npm run dev
```

UI: http://127.0.0.1:5173  
Vite proxies `/api` → Flask.

### 3. Tests

```powershell
cd backend
py -3 -m pip install pytest
py -3 -m pytest -q
```

---

## DemoMart (fake Amazon-style store)

Full product pages with images, prices, specs, and Legal Metrology text:

| Store | URL |
|-------|-----|
| Home | http://127.0.0.1:5000/demo/ |
| Honey (complete) | http://127.0.0.1:5000/demo/dp/hive-organic-honey-500g |
| Oil (missing origin) | http://127.0.0.1:5000/demo/dp/pure-groundnut-oil-1l |
| Chips (sparse) | http://127.0.0.1:5000/demo/dp/crunchyco-spicy-chips-50g |
| Tea (complete) | http://127.0.0.1:5000/demo/dp/assam-classic-tea-bags-100g |
| Atta (regex-blind) | http://127.0.0.1:5000/demo/dp/golden-grain-atta-5kg |
| Olive oil (regex-blind) | http://127.0.0.1:5000/demo/dp/mediterra-olive-oil-500ml |
| Triphala (regex-blind) | http://127.0.0.1:5000/demo/dp/vaidya-triphala-churna-100g |
| Detergent (regex-blind) | http://127.0.0.1:5000/demo/dp/foamchem-active-wash-1kg |
| Pepper (regex-blind) | http://127.0.0.1:5000/demo/dp/malabar-black-pepper-100g |
| Coconut oil (regex-blind) | http://127.0.0.1:5000/demo/dp/kerala-coconut-oil-500ml |
| Besan (regex-blind) | http://127.0.0.1:5000/demo/dp/rajasthan-gram-flour-1kg |
| Jaggery (regex-blind) | http://127.0.0.1:5000/demo/dp/goa-cane-jaggery-500g |
| Ghee (regex-blind) | http://127.0.0.1:5000/demo/dp/punjab-desi-ghee-1l |
| Darjeeling (regex-blind) | http://127.0.0.1:5000/demo/dp/darjeeling-leaf-tea-250g |
| Rock salt (complete) | http://127.0.0.1:5000/demo/dp/coastal-rock-salt-1kg |
| Lentils (complete) | http://127.0.0.1:5000/demo/dp/nile-red-lentils-1kg |

**Test flow:** open product page → copy URL → Compliance Dashboard → **Product URL** → Scan.

## Demo path (recommended for viva)

Full script: [`docs/VIVA_DEMO.md`](docs/VIVA_DEMO.md). Frontend patch list for Antigravity: [`docs/ANTIGRAVITY_FRONTEND.md`](docs/ANTIGRAVITY_FRONTEND.md).

1. Open DemoMart: http://127.0.0.1:5000/demo/  
2. Open dashboard: http://127.0.0.1:5173/  
3. Confirm `/api/health` has `ner_available: true`  
4. Scan honey product URL → score ~100 (regex)  
5. Scan oil product URL → country of origin missing  
6. Scan a **regex-blind** product (atta / pepper / ghee) → hybrid NER fills paraphrased fields (`source=ner`)  
7. Confirm/reject findings → Generate PDF report  

Regex-blind listings use wording such as *Pack price*, *Plant operator*, *COO*, *DOM*. Do not add those as regex aliases — that would hide the NER demo.  


---

## API overview

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health + OCR availability |
| GET | `/api/stats` | Dashboard metrics |
| GET | `/api/samples` | Demo sample list |
| GET | `/api/demo/catalog` | DemoMart URLs + regex-blind flags |
| GET | `/api/rules` | Configured rule set |
| POST | `/api/scan/sample` | `{ "sample_id": "honey_complete" }` |
| POST | `/api/scan/text` | `{ "page_text", "ocr_text", "name?" }` |
| POST | `/api/scan/url` | `{ "url" }` |
| POST | `/api/scan/image` | multipart `image` |
| GET | `/api/products` | List scans |
| GET | `/api/products/:id` | Detail + fields + findings |
| POST | `/api/findings/:id/review` | `{ "action": "confirm\|reject\|needs_review", "comment?" }` |
| POST | `/api/products/:id/review` | Product-level review status |
| POST | `/api/products/:id/report` | `{ "format": "json\|pdf" }` |

---

## Design principles (no mistakes)

- **Never invent fields** — missing → `not_detected` with reason  
- **Conflicts → `ambiguous`** — human review, no silent pick  
- **Bare prices ≠ MRP** without an MRP label  
- **Score is prioritization only**, not certification  
- **Disclaimer on every API response / report**  
- Live marketplace scrape is best-effort; demos must not depend on it  

---

## Project layout

```
legal-metrology-compliance-checker/
  backend/
    app/
      field_extractor/   # precision field extraction
      services/          # scraper, ocr, rules, pipeline, reports, storage
      routes/api.py
      main.py
    data/rules.json
    tests/
    run.py
  frontend/
    src/App.jsx
    src/components/
  README.md
  docs/PROJECT_SPEC.md
```

---

## Optional: trained NER

The Flask MVP uses **precision-first regex**. A DistilBERT token-classification
model can sit next to it as a **hybrid fallback** (`EXTRACTOR_MODE=hybrid`, default).
Regex is never replaced. There is no hosted LLM and no compliant/not-compliant classifier.

```powershell
cd backend
# CPU torch (skip if you already have a GPU build)
py -3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu
py -3 -m pip install -r requirements-ml.txt

py -3 -m app.ml.make_dataset
py -3 -m app.ml.train_ner
```

Colab T4 one-liner (from the `backend/` folder of a checkout):

```python
!pip install -r requirements-ml.txt && python -m app.ml.make_dataset && python -m app.ml.train_ner
```

Then set the extractor (default is already hybrid):

```powershell
$env:EXTRACTOR_MODE = "hybrid"   # regex | ner | hybrid
```

- Weights load once from `backend/app/ml/ner_model/` with `local_files_only=True`.
- No model → hybrid falls back to regex; `/api/health` reports `ner_available: false`.
- CI / laptops: `SKIP_NER_TRAIN=1` skips the DistilBERT run. Pytest does not need torch.
- Metrics: `backend/app/ml/RESULTS.md` (regex_only / ner_only / hybrid on the same test texts).

Notebook: `notebooks/train_ner.ipynb`.

## Optional: Tesseract OCR

1. Install [Tesseract](https://github.com/tesseract-ocr/tesseract) for Windows  
2. `py -3 -m pip install pytesseract pillow`  
3. Restart backend — health shows `ocr_tesseract_available: true`  

---

## SDG alignment

- **SDG 9** — digital inspection infrastructure  
- **SDG 12** — clearer product information  
- **SDG 16** — transparent regulatory screening workflows  

---

## Team / academic context

Built as a complete mini-project prototype from the detailed concept document  
*AI-Based Automated Legal Metrology & E-Commerce Compliance Checker*.
