# Viva demo script (8–10 minutes)

Not a legal authority. Say that once at the start.

## Before the examiner sits

1. `.\start-backend.ps1` (D: venv — torch + DistilBERT). Wait until Flask is up.
2. `.\start-frontend.ps1` → http://127.0.0.1:5173
3. Open http://127.0.0.1:5000/api/health  
   Expect `ner_available: true`, `extractor_mode: hybrid`.
4. Open http://127.0.0.1:5000/demo/ so DemoMart is warm.

If `ner_available` is false, you are on system Python. Stop and use the D: start script.

## Script

**1. Problem (30s)**  
E-commerce listings bury MRP, net quantity, manufacturer, origin, dates. Manual inspection does not scale. This tool is first-pass screening only. A human confirms.

**2. Regex-visible listing (90s)**  
DemoMart → Honey → copy URL → Scan.  
Score high. Fields detected with labels `MRP`, `Manufactured by`. Source is page/regex.  
“Regex is precision-first. It never invents. Bare price 199 is not MRP.”

**3. Honest miss (45s)**  
Scan Oil. Country of origin missing → potential issue. We do not fill “India” from the brand.

**4. NER / tokenization (2 min) — the AI piece**  
Open Atta (`golden-grain-atta-5kg`) or Pepper. Page says **Stated consumer price**, **Plant operator**, **COO**, **DOM** — not MRP / Manufactured by.  
Scan. Regex would be empty. Hybrid fills spans. Source `ner`. Evidence is the exact substring.  
Tokenizer = DistilBERT WordPiece (same checkpoint as the encoder). Not ChatGPT. BIO tags on 7 fields.

**5. Human review + PDF (60s)**  
Confirm one finding. Generate PDF. Disclaimer is on the report.

**6. If asked “99% accuracy?”**  
Numbers in `backend/app/ml/RESULTS.md` are on synthetic paraphrases of our templates, 78 test docs. Hybrid recall beats regex on manufacturer / origin / dates. Not live Amazon accuracy.

## Backup if URL scrape fails

Samples tab → `honey_complete` then `golden-grain-atta-5kg`. Same extraction path, no browser.
