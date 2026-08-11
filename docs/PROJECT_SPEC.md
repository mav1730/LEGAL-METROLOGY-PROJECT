# Project specification (canonical)

**PROJECT TYPE:** Web-based AI/OCR-assisted compliance screening and regulatory decision-support application.

**PROBLEM:** Manual inspection of large numbers of e-commerce product listings is repetitive, time-consuming, and difficult to scale. Mandatory product information may appear in webpage text, specifications, descriptions, or packaging images.

**INPUT:**
1. E-commerce product URL  
2. Product / packaging image  
3. Pasted page or OCR text  
4. Built-in demo samples  

**PROCESS:**
1. Collect webpage data when a URL is provided  
2. Accept / store product images  
3. Preprocess images where necessary  
4. Run OCR (optional free Tesseract)  
5. Extract structured product fields (precision-first)  
6. Apply configurable compliance rules  
7. Detect missing, unclear, or potentially problematic fields  
8. Attach evidence and confidence  
9. Generate an explainable result  
10. Allow human review  
11. Store the result (SQLite)  
12. Generate JSON/PDF report  

**CORE FIELDS:** MRP, net quantity, manufacturer, country of origin, manufacturing date, expiry/best-before, product name (when labeled).

**CORE OUTPUT:** Compliance status/score, detected fields, missing/potentially problematic fields, evidence, explanation, confidence, human review status, report.

**DESIGN PRINCIPLE:** AI/OCR assists extraction. A deterministic rule engine performs configured checks. A human reviewer remains responsible for final interpretation.

**GOAL:** Working mini-project prototype that demonstrates automated first-pass screening and produces understandable, evidence-backed compliance reports.
