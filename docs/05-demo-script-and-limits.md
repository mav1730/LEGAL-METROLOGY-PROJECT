# Viva demo script and honest limits

Say once at the start: **not a legal authority.**

## Before the examiner sits

1. `.\START-EVERYTHING.ps1` (or the two start scripts).
2. Health: `ner_available: true`, `extractor_mode: hybrid`.
3. DemoMart open in a tab.

If NER is false, you can still demo regex + DemoMart. Tell the truth: “the neural net is not loaded on this Python.”

## Eight minutes

**0:00 Problem**  
Packs must declare MRP, quantity, maker, origin, dates. Listings hide or paraphrase them.

**1:00 Architecture**  
Two local programs. Flask brain on 5000, React face on 5173. SQLite. No paid LLM.

**2:00 Regex-visible**  
Scan honey DemoMart URL. High score. Exact evidence. “Regex is picky. Bare 199 is not MRP.”

**3:00 Honest miss**  
Scan a listing that is missing origin (oil, or a GitHub catalogue item marked missing). We do not fill “India” from the brand.

**4:30 NER**  
Scan `http://127.0.0.1:5000/demo/dp/golden-grain-atta-5kg`.  
Words: *Stated consumer price*, *Plant operator*, *COO*, *DOM*.  
Regex empty. Hybrid fills. Source `ner`. Tokenizer = DistilBERT WordPiece. BIO tags. Not ChatGPT.

**6:00 Human + PDF**  
Confirm one finding. Generate PDF. Disclaimer is on the report.

**7:00 Amazon question**  
“We do not break their robot check. Paste from your browser, or use DemoMart.”

## If they ask “99% accuracy?”

Point to `backend/app/ml/RESULTS.md`. Lab paraphrases, 78 docs. Hybrid recall beats regex on maker / origin / dates **there**. Not live Amazon.

## Product URLs worth memorising

| Role | URL |
|---|---|
| Regex complete | http://127.0.0.1:5000/demo/dp/hive-organic-honey-500g |
| Missing origin-style | http://127.0.0.1:5000/demo/dp/pure-groundnut-oil-1l |
| NER / regex-blind | http://127.0.0.1:5000/demo/dp/golden-grain-atta-5kg |
| NER | http://127.0.0.1:5000/demo/dp/malabar-black-pepper-100g |
| GitHub electronics complete | http://127.0.0.1:5000/demo/dp/soundwave-pulse-pro-earbuds |
| Shop home | http://127.0.0.1:5000/demo/ |

## Limits (say them before they are used against you)

- No stealth scrape of Amazon / Flipkart / Zepto.
- Tesseract OCR is optional; many laptops will not have it.
- NER weights are local and large; clone from GitHub does not include `model.safetensors`.
- GitHub Pages is off — there is no public website, only this laptop.
- Rule engine is configuration, not a learned “compliant” classifier.

## Reading order for a non-coder

1. [01-what-is-this.md](01-what-is-this.md)
2. [02-how-the-machine-works.md](02-how-the-machine-works.md)
3. [03-regex-and-ai.md](03-regex-and-ai.md)
4. [04-start-by-yourself.md](04-start-by-yourself.md)
5. This file
