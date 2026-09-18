# How to start everything without an AI

Print this. Follow in order. Do not skip the health check.

## You need

- This folder: `C:\Users\admin\Documents\legal-metrology-compliance-checker`
- Windows PowerShell
- Node.js (for the dashboard)
- The D: Python venv (for NER). If it is missing, DemoMart + regex still work; the AI spans will not.

## Fastest path (one double-click)

1. Open the project folder in Explorer.
2. Right-click `START-EVERYTHING.ps1` → **Run with PowerShell**.  
   (If Windows blocks it: “Open PowerShell here” and type `.\START-EVERYTHING.ps1`)
3. Two extra windows open (backend, frontend). **Do not close them.**
4. Wait until the first window prints `API is up` and `ner_available = True`.
5. Chrome:
   - Dashboard: http://127.0.0.1:5173/
   - Fake shop: http://127.0.0.1:5000/demo/
   - Health: http://127.0.0.1:5000/api/health

Hard-refresh the dashboard (Ctrl+F5) if you still see an old layout.

## Manual path (if the script fails)

### A. Backend

```powershell
D:\legal-metrology\scripts\start-backend.ps1
```

Or from the project:

```powershell
.\start-backend.ps1
```

You want this Python: `D:\legal-metrology\venv\Scripts\python.exe`  
You want this line in the window: `EXTRACTOR_MODE = hybrid`

Wait until you see `Running on http://127.0.0.1:5000`.

Open http://127.0.0.1:5000/api/health

Must be true:

- `"ok": true`
- `"ner_available": true`  ← if false, you used the wrong Python
- `"extractor_mode": "hybrid"`

### B. Frontend (second window)

```powershell
cd C:\Users\admin\Documents\legal-metrology-compliance-checker
.\start-frontend.ps1
```

First time it may run `npm install`. Then:

```
Local: http://127.0.0.1:5173/
```

**Not 5174.** 5174 is unused unless 5173 was already taken.

### C. First proof scans

1. DemoMart → **HIVE honey** → copy the URL → dashboard `#scanner` → paste → Scan.  
   Score should be high. Fields found with normal labels (`MRP`, `Manufactured by`).
2. DemoMart → **Golden Grain Atta** (`.../demo/dp/golden-grain-atta-5kg`) → Scan.  
   Page says `Stated consumer price` / `Plant operator`. Regex would miss. Hybrid should fill; source can show `ner`.
3. Optional: a real Amazon URL. If you get “Marketplace blocked automated access”, that is correct. Paste product details or stay on DemoMart.

## If something is red

| Symptom | Likely cause | Fix |
|---|---|---|
| Health page will not load | Backend window closed or crashed | Start `start-backend.ps1` again |
| `ner_available: false` | System `py -3`, not D: venv | Use `D:\legal-metrology\scripts\start-backend.ps1` |
| Dashboard blank / old UI | Wrong port or cached JS | Use **5173**, Ctrl+F5 |
| `ECONNREFUSED 5000` in frontend | API not up yet | Wait for health, then refresh |
| Port already in use | Old Python/Node still running | Close those windows, or Task Manager → end `python.exe` / `node.exe` |
| D: venv missing | Never ran setup | `D:\legal-metrology\scripts\setup-d-drive.ps1` then install ML extras (`requirements-ml.txt`) |
| Image scan fails | Tesseract not installed | Use paste-text or DemoMart; OCR is optional |
| Amazon CAPTCHA | Their bot wall | Paste HTML/text or DemoMart. Do not “bypass.” |

## Tests (optional)

```powershell
cd C:\Users\admin\Documents\legal-metrology-compliance-checker
py -3 -m pytest backend/tests -q
```

Expect **20 passed**. These tests do **not** need the NER model.

## Stop

Close the two PowerShell windows. That stops the site.

## Retrain NER (only if weights are missing)

From `backend\`, with the D: venv:

```powershell
D:\legal-metrology\venv\Scripts\python.exe -m app.ml.make_dataset
D:\legal-metrology\venv\Scripts\python.exe -m app.ml.train_ner
```

CPU is slow (tens of minutes). Colab T4 is faster. See README “Optional: trained NER”.

Next: [05-demo-script-and-limits.md](05-demo-script-and-limits.md)
