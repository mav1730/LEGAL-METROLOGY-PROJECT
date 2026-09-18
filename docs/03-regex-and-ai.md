# Regex, NER, and the rule engine (the “AI” chapter)

## 1. Regex — the picky highlighter

Regex means **regular expressions**: a search pattern.

Example: look for the letters `MRP`, then a rupee amount.

If the page says `MRP Rs. 349`, regex is happy.  
If the page says `Stated consumer price Rs. 275`, regex is **silent**. We did **not** add those phrases as aliases on purpose. If we did, we could not prove the AI does anything extra.

Regex **never invents**. Empty field stays empty. That is precision-first.

Code: `backend/app/field_extractor/extractors.py`, `patterns.py`, `normalize.py`.

## 2. Tokenization — cutting a sentence into pieces

Computers do not read like people. They cut text into **tokens** (pieces of words).

DistilBERT uses **WordPiece**. Example idea:

`Himalayan` → `him` + `##alayan`

This is **not** a second model we trained. It is the tokenizer that ships with DistilBERT:

`AutoTokenizer.from_pretrained("distilbert-base-uncased")`

Max length 256 tokens. Long pages are read in overlapping windows (stride 64).

## 3. NER — naming the pieces

NER = **Named Entity Recognition**.

We fine-tuned DistilBERT as a **token classifier**. Each token gets a BIO tag:

- `B-mrp` = beginning of an MRP span
- `I-mrp` = inside that span
- `O` = not an entity

Seven fields × (B and I) + O = **15 tags**.

The model does **not** output “compliant / not compliant.” It only paints spans. Validators still reject garbage (a fake country, a broken date).

Weights: `backend/app/ml/ner_model/`  
Train: `python -m app.ml.make_dataset` then `python -m app.ml.train_ner`  
Notebook: `notebooks/train_ner.ipynb`  
No OpenAI, no Gemini.

## 4. Hybrid merge — both teachers, one answer

Default `EXTRACTOR_MODE=hybrid`.

| Regex | NER | Result |
|---|---|---|
| Same value | Same value | Keep, high confidence |
| Miss | Hit | Accept NER, medium confidence, source `ner` |
| Hit | Miss | Keep regex |
| Different values | Different | `ambiguous`, empty value, human |
| Miss | Miss | `not_detected` |
| Already ambiguous (page vs OCR) | anything | Stay ambiguous |

That is why honey still scores high (regex already found everything) and atta still fills (regex missed, NER hit).

## 5. Rule engine — the marking scheme

JSON file: `backend/data/rules.json`.

Rules are things like “MRP must be present.” They are **if-then**, not a neural net. Untouched by training.

Score is a simple function of how many required things were found vs missing / ambiguous.

## 6. Honest numbers

On **78 synthetic test documents** (paraphrases of our own templates):

| System | Precision | Recall | F1 |
|---|---:|---:|---:|
| regex only | 0.93 | 0.24 | 0.39 |
| NER only | 1.00 | 0.99 | 0.99 |
| hybrid | 1.00 | 0.97 | 0.98 |

Say this out loud: *these are lab paraphrases, not live Amazon.* Hybrid **does** beat regex on manufacturer / origin / dates **on that set**. Full table: `backend/app/ml/RESULTS.md`.

## 7. Why Amazon still blocks us

Their website looks for robots. Our scraper is a robot. They send a CAPTCHA. We **fail closed** and tell you to paste text or use DemoMart. We do not use proxy farms or CAPTCHA solvers. That is a feature for a college project, not a bug.

Next: [04-start-by-yourself.md](04-start-by-yourself.md)
