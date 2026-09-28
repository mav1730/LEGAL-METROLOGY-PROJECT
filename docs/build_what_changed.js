const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, VerticalAlign, PageNumber, LevelFormat } = require("docx");
const fs = require("fs");
const path = require("path");

const TW = 9026;
const border = { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellPad = { top: 60, bottom: 60, left: 100, right: 100 };

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.after ?? 120, before: opts.before ?? 0, line: 276 },
    children: [new TextRun({
      text, font: "Arial", size: opts.size || 22,
      bold: opts.bold, italics: opts.italics, color: opts.color,
    })],
  });
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 280, after: 140 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: "1F4E79", space: 4 } },
    children: [new TextRun({ text, font: "Arial", size: 28, bold: true, color: "1F4E79" })],
  });
}

function bullet(text, ref = "bullets") {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { after: 80 },
    children: [new TextRun({ text, font: "Arial", size: 22 })],
  });
}

function cell(text, width, opts = {}) {
  const fill = opts.header ? "1F4E79" : opts.alt ? "F2F2F0" : "FFFFFF";
  const color = opts.header ? "FFFFFF" : "222222";
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill, type: ShadingType.CLEAR },
    margins: cellPad,
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      children: [new TextRun({
        text, font: "Arial", size: opts.size || 20,
        bold: !!opts.header, color,
      })],
    })],
  });
}

function table(colWidths, rows) {
  return new Table({
    width: { size: TW, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: rows.map((r, i) => new TableRow({
      children: r.map((c, j) => cell(
        typeof c === "string" ? c : c.text,
        colWidths[j],
        { header: i === 0, alt: i > 0 && i % 2 === 0 }
      )),
    })),
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "1F4E79" },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{
        level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } },
      }] },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: "1F4E79", space: 6 } },
          spacing: { after: 80 },
          children: [new TextRun({
            text: "Legal Metrology  ·  What changed (previous GitHub vs this snapshot)",
            font: "Arial", size: 18, color: "1F4E79", bold: true,
          })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          border: { top: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 6 } },
          spacing: { before: 80 },
          children: [
            new TextRun({ text: "Private snapshot vs LEGAL-METROLOGY-PROJECT  ·  Page ", font: "Arial", size: 16, color: "666666" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "666666" }),
          ],
        })],
      }),
    },
    children: [
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun({
          text: "What changed in this version vs the previous GitHub project",
          font: "Arial", size: 32, bold: true, color: "1F4E79",
        })],
      }),
      p("A plain comparison for viva / internal notes. Not a legal opinion. Date: 19 September 2026.", {
        italics: true, color: "555555", after: 200,
      }),

      h1("1. Two repositories (do not mix them up)"),
      table([2800, 6226], [
        ["", "Address / commit"],
        ["Previous (unchanged)", "github.com/mav1730/LEGAL-METROLOGY-PROJECT  —  commit 3a59cb8"],
        ["This snapshot (private)", "github.com/mav1730/LEGAL-METROLOGY-HYBRID  —  commit 667c8f3"],
      ]),
      new Paragraph({ spacing: { after: 120 } }),
      p("The original public/project repo was not overwritten. Today’s work was committed locally and pushed only to the new private repo. A normal git push now goes to HYBRID, not PROJECT."),
      p("Size of the delta: 71 files, about +36,000 / −106 lines (tokenizer JSON is most of the bulk). DistilBERT weights (model.safetensors) are not on GitHub — they stay on this PC."),

      h1("2. One-line summary"),
      p("Previous version: MetroCheck UI + DemoMart catalogue + regex extractor + rules + PDF. Title said AI; extraction was regex only."),
      p("This version: same UI and rules, plus a trained DistilBERT NER as a hybrid fallback, regex-blind grocery pages to show that fallback, scanner crash/hang fixes, and five plain-language docs."),

      h1("3. Side-by-side"),
      table([2256, 3385, 3385], [
        ["Area", "Previous (LEGAL-METROLOGY-PROJECT)", "This snapshot (HYBRID)"],
        ["User interface", "Landing, Compliance Scan, Catalog History, Rules (MetroCheck)", "Same pages. Small patches only: URL box stays visible, paste without https://, evidence text, error boundary."],
        ["Field extraction", "Regex only (MRP, Manufactured by, …)", "Regex first, then DistilBERT NER if regex misses. Conflicts stay ambiguous."],
        ["“AI”", "Name / marketing. No trained model.", "Offline DistilBERT token classifier, 15 BIO tags, local weights."],
        ["DemoMart", "17 verified catalogue items (earbuds, polo, honey, …)", "Those 17 plus 10 paraphrased grocery SKUs (atta, pepper, ghee, …) for the NER demo."],
        ["Amazon / Flipkart", "Scrape best-effort; Playwright could hang", "Still cannot bypass bot walls. Fails in ~1 second with a clear message. Use DemoMart or paste text."],
        ["Docs", "PROJECT_SPEC + stack PDF", "Plus 01–05 plain-language markdown, viva script, NER training note, this changelog."],
        ["Start", "Two scripts (backend / frontend)", "Same, plus START-EVERYTHING.ps1 and docs/04-start-by-yourself.md"],
        ["Tests", "Pipeline / health / samples", "Those plus NER hybrid tests. 23 pytest passing."],
      ]),

      h1("4. What we added (new)"),
      bullet("NER pipeline: make_dataset.py, train_ner.py, notebooks/train_ner.ipynb, backend/app/ml/."),
      bullet("Inference: ner_extractor.py (lazy load, local_files_only). EXTRACTOR_MODE=hybrid by default."),
      bullet("Hybrid merge in merge.py: agree / NER-fill / conflict=ambiguous / both miss."),
      bullet("Regex-blind SKUs with wording such as Pack price, Plant operator, COO, DOM — regex must miss; NER should fill."),
      bullet("Health keys: ner_available, extractor_mode. GET /api/demo/catalog."),
      bullet("requirements-ml.txt (torch not in the Flask MVP requirements)."),
      bullet("START-EVERYTHING.ps1. GitHub Actions pytest (no torch)."),
      bullet("Docs 01–05, VIVA_DEMO, NER_Training_Note.docx."),

      h1("5. What we fixed (bugs that existed after combining UI + NER)"),
      bullet("Blank scanner after AeroFit: findings.evidence is an object; the UI tried to print it and React crashed. Now shows matched_text. ErrorBoundary added."),
      bullet("URL box vanished after the first scan — you could not paste a second link. Form now stays on screen."),
      bullet("Links without https:// were rejected. Pastes are normalised."),
      bullet("Amazon/Flipkart Playwright hang (~45s). Localhost and hard HTTP errors skip Playwright."),
      bullet("MRP Rs. 1169 was captured as 116. Amount pattern now takes the full number."),
      bullet("Country of Origin: India was eaten by the next “Month & Year of Packing” line."),
      bullet("Flask debug reloader loaded DistilBERT twice and died when the parent window closed. Default debug=False."),

      h1("6. What we did not change (on purpose)"),
      bullet("The original GitHub repo LEGAL-METROLOGY-PROJECT — still commit 3a59cb8."),
      bullet("Rule engine (rules.json) — still deterministic if-then, not a neural net."),
      bullet("Regex contract — still precision-first. We did not add Pack price / Plant operator as aliases (that would hide the NER demo)."),
      bullet("No ChatGPT / Gemini / paid LLM. No CAPTCHA bypass, proxies, or stealth browsers."),
      bullet("No compliant/not-compliant classifier. Human review still required."),
      bullet("MetroCheck landing / catalog / rules page layout — not rewritten."),

      h1("7. How to talk about this in viva"),
      p("Previous project: working compliance dashboard and DemoMart, regex extraction."),
      p("This snapshot: we added a real trained span model next to regex, proved it on paraphrased packs, and fixed the scanner so a real inspection does not blank the page."),
      p("Honest limit: high NER scores are on synthetic paraphrases (RESULTS.md). Amazon still blocks bots. Weights are local, not in the GitHub zip."),
    ],
  }],
});

const out = path.join(__dirname, "WHAT_CHANGED_VS_PREVIOUS.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(out, buf);
  console.log("Wrote", out);
});
