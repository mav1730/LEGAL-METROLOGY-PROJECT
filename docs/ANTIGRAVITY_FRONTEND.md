# Antigravity — frontend handoff (do not rewrite the dashboard)

The React + Vite UI in `frontend/` must stay the same layout, colours, and flow.
Only add **small, additive** pieces so the viva can show DistilBERT NER vs regex.

Backend is already finished. Do **not** change Flask extraction, rules, or DemoMart HTML.

## What the backend already does

- Default `EXTRACTOR_MODE=hybrid` (regex first, NER fallback, conflict → `ambiguous`).
- Trained DistilBERT token classifier labels spans: `product_name`, `mrp`, `net_quantity`, `manufacturer`, `country_of_origin`, `manufacturing_date`, `expiry_date`.
- Tokenizer = DistilBERT WordPiece (`distilbert-base-uncased`), not a second model, not ChatGPT.
- `/api/health` now includes `ner_available` (bool) and `extractor_mode` (`regex` | `ner` | `hybrid`).
- `GET /api/demo/catalog` lists every DemoMart product with `url`, `scenario_label`, `regex_blind`.
- `/api/samples` already includes regex-blind sample ids (paraphrased texts).
- Field objects already have `source` (`page` | `ocr` | `ner` | `merged`) and `evidence.matched_text`.

## Do not

- Do not restyle the app.
- Do not remove existing DemoMart URL buttons.
- Do not call OpenAI / Gemini.
- Do not invent a “compliant / not compliant” AI badge.

## Change 1 — `frontend/src/components/ScanPanel.jsx`

Replace the hardcoded `DEMO_PRODUCTS` array (lines 4–21) with a fetch of `/api/demo/catalog` **or** keep the four original buttons and **append** the catalog.

Preferred: fetch catalog on mount.

```javascript
// After health/samples already load in App.jsx, either:
// A) pass catalog from App (api call already can be added next to api.samples)
// B) fetch inside ScanPanel: GET /api/demo/catalog

// Group buttons:
//  "Regex-visible (canonical labels)"  → regex_blind === false
//  "Regex-blind (NER demo)"            → regex_blind === true

// Button label:
//   `${shortName} — ${scenario_label}`
// onClick: setUrl(p.url); onScan({ type: "url", url: p.url, html: "" });
```

Add `api.demoCatalog: () => request("/demo/catalog")` in `frontend/src/api/client.js`.

Keep the four original honey/oil/chips/tea buttons if you want zero risk — then add a second grid “NER demo (paraphrased labels)” from catalog where `regex_blind` is true.

## Change 2 — `frontend/src/components/ProductDetail.jsx`

Extracted-fields table (around line 56): add a **Source** column.

```jsx
<th>Source</th>
// cell:
<td className="mono">{f.source || f.evidence?.source || "—"}</td>
```

When `source === "ner"`, that row was filled by DistilBERT (regex missed). That is the viva punchline.

Optional muted line under the header if `product.raw_payload?.warnings` contains `"NER model not available"`.

## Change 3 — `frontend/src/components/StatsBar.jsx` or App header

`App.jsx` already stores `health`. Show two small badges next to the title (do not replace StatsBar cards):

- `NER: on` if `health.ner_available` else `NER: off (regex only)`
- `mode: {health.extractor_mode}`

If NER is off, the examiner must start the backend from `D:\legal-metrology\scripts\start-backend.ps1` (venv with torch).

## Change 4 — samples tab (optional)

Samples from `/api/samples` already include regex-blind SKUs. You may prefix names:

- if description contains `Regex-blind` → label `(NER demo)`

No new endpoints required.

## Viva clicks (after your UI patch)

1. Honey URL → fields `source=page`, score high. Regex works.
2. `golden-grain-atta-5kg` or sample `golden-grain-atta-5kg` → MRP / manufacturer filled, `source=ner`, evidence like `Rs. 275` / `Golden Mills…`.
3. Oil URL → country of origin still missing (honest gap).
4. Confirm a finding → PDF report.

## Files you may touch

- `frontend/src/api/client.js`
- `frontend/src/components/ScanPanel.jsx`
- `frontend/src/components/ProductDetail.jsx`
- `frontend/src/App.jsx` (pass `health` / catalog only)
- `frontend/src/components/StatsBar.jsx` (optional badges)

Do not touch `backend/`.
