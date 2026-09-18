const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, VerticalAlign, PageNumber, LevelFormat } = require("docx");
const fs = require("fs");
const path = require("path");

const TW = 9026;
const border = { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const headerFill = "1F4E79";
const altFill = "F2F2F0";
const cellPad = { top: 60, bottom: 60, left: 100, right: 100 };

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.after ?? 120, before: opts.before ?? 0, line: 276 },
    children: [new TextRun({
      text,
      font: "Arial",
      size: opts.size || 22,
      bold: opts.bold,
      italics: opts.italics,
      color: opts.color,
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
  const fill = opts.header ? headerFill : opts.alt ? altFill : "FFFFFF";
  const color = opts.header ? "FFFFFF" : "222222";
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill, type: ShadingType.CLEAR },
    margins: cellPad,
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      children: [new TextRun({
        text,
        font: "Arial",
        size: opts.size || 20,
        bold: !!opts.header || !!opts.bold,
        color,
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
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "1F4E79" },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 0 },
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0,
          format: LevelFormat.BULLET,
          text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "steps",
        levels: [{
          level: 0,
          format: LevelFormat.DECIMAL,
          text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
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
            text: "Legal Metrology Compliance Checker  ·  NER training note",
            font: "Arial",
            size: 18,
            color: "1F4E79",
            bold: true,
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
            new TextRun({
              text: "Mini-project note  ·  Offline DistilBERT  ·  Page ",
              font: "Arial",
              size: 16,
              color: "666666",
            }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "666666" }),
          ],
        })],
      }),
    },
    children: [
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun({
          text: "How we trained the NER model",
          font: "Arial",
          size: 36,
          bold: true,
          color: "1F4E79",
        })],
      }),
      p("Brief viva note for the Legal Metrology field extractor. Not a legal opinion.", {
        italics: true,
        color: "555555",
        after: 200,
      }),

      h1("1. Did we use a tokenization model?"),
      p("Yes — but it is not a second, separate model we trained. We used the WordPiece tokenizer that ships with DistilBERT."),
      p("HuggingFace call: AutoTokenizer.from_pretrained(\"distilbert-base-uncased\"). Same checkpoint as the encoder. It is a tokenizer, not ChatGPT and not a second neural net."),
      p("What it does: splits page or OCR text into subword tokens (for example Himalayan may become him + ##alayan). Each token then gets a BIO label from the NER head. Character offsets map tokens back to the original string so we never invent a span that is not in the text."),
      p("Optional switch --multilingual would use bert-base-multilingual-cased (different tokenizer and encoder). We trained the default English DistilBERT path."),
      table([2800, 6226], [
        ["Piece", "What we used"],
        ["Tokenizer", "DistilBERT WordPiece (uncased), max length 256, stride 64"],
        ["Encoder", "distilbert-base-uncased (pretrained, then fine-tuned)"],
        ["Head", "AutoModelForTokenClassification — 15 BIO tags"],
        ["Not used", "OpenAI, Gemini, LayoutLM, YOLO, or any hosted LLM"],
      ]),

      h1("2. What NER is doing in this project"),
      p("NER means Named Entity Recognition as token classification. The model labels spans in product-page or OCR text. It does not decide compliant or not-compliant. The rule engine and a human reviewer still do that."),
      p("Seven fields: product_name, mrp, net_quantity, manufacturer, country_of_origin, manufacturing_date, expiry_date."),
      p("Label scheme: BIO. B-mrp is the first token of an MRP span, I-mrp is the continuation, O means not an entity. Seven fields times two plus O equals 15 tags."),
      p("Example: “Stated consumer price Rs. 275” — tokens for Rs. 275 are tagged B-mrp / I-mrp. Regex would miss this line because it only looks for the word MRP."),

      h1("3. How we trained it"),
      bullet("Data. JSONL, one document per line: id, text, ents with start, end, label, text. Seed: four regex-blind DemoMart SKUs (atta, olive oil, triphala, detergent) plus honey / oil / tea samples. A generator wrote 300–600 paraphrases from a fixed template list (Pack price, Plant operator, COO, DOM, Fill weight, Consume before). Split by document 70 / 15 / 15. All regex-blind SKUs stayed in TEST. No Amazon scrape. No invented legal conclusions.", "steps"),
      bullet("Align. Gold character spans become token BIO using tokenizer offset mapping. Long pages are windowed (256 / stride 64).", "steps"),
      bullet("Train. HuggingFace Trainer, DistilBERT plus a token-classification head, 3 epochs, batch 4, learning rate 5e-5, CPU. Commands from backend/: python -m app.ml.make_dataset then python -m app.ml.train_ner.", "steps"),
      bullet("Save. backend/app/ml/ner_model/ holds config, tokenizer, model.safetensors, label2id.json. The app loads with local_files_only=True so it never downloads hundreds of megabytes per request.", "steps"),
      bullet("Score. Same TEST texts, three systems: regex_only, ner_only, hybrid. Wrote metrics.json and RESULTS.md. Seqeval entity P/R/F1 plus field-level value match.", "steps"),

      h1("4. How it is plugged into the app"),
      p("Default EXTRACTOR_MODE is hybrid. Regex still runs first (precision-first, never invents). NER is a fallback:"),
      bullet("Both same value → keep, high confidence."),
      bullet("Regex miss + NER hit → accept NER, medium confidence."),
      bullet("Conflict → AMBIGUOUS, value empty, human review."),
      bullet("Both miss → not_detected."),
      p("Every scan (URL, image, pasted text, sample) calls extract_with_mode. /api/health reports ner_available and extractor_mode. If torch is missing, hybrid falls back to regex. The rule engine is untouched."),

      h1("5. Measured numbers (same 78 test documents)"),
      p("These are computed, not hand-written. They look high because most TEST text is synthetic paraphrases of our templates — say that in viva. This is not live-Amazon accuracy."),
      table([2256, 2256, 2257, 2257], [
        ["System", "Precision", "Recall", "F1"],
        ["regex_only", "0.9291", "0.2449", "0.3876"],
        ["ner_only", "1.0000", "0.9850", "0.9925"],
        ["hybrid", "1.0000", "0.9682", "0.9839"],
      ]),
      new Paragraph({ spacing: { after: 160 } }),
      p("Recall on fields regex usually misses:"),
      table([2600, 2142, 2142, 2142], [
        ["System", "Manufacturer", "Origin", "Dates (mfg / exp)"],
        ["regex_only", "0.13", "0.27", "0.26 / 0.27"],
        ["hybrid", "0.99", "0.99", "0.99 / 0.99"],
      ]),
      new Paragraph({ spacing: { after: 160 } }),
      p("Token-level seqeval on TEST: precision 0.994, recall 0.992, F1 0.993."),
      p("Takeaway: regex is precise but blind to paraphrases. NER recovers those spans. Hybrid keeps regex when it hits, fills gaps with NER, and refuses to pick a winner on conflict."),

      h1("6. Commands (from backend/)"),
      p("python -m app.ml.make_dataset"),
      p("python -m app.ml.train_ner"),
      p("EXTRACTOR_MODE=hybrid   (default; also regex or ner)"),
      p("Notebook: notebooks/train_ner.ipynb. ML extras: requirements-ml.txt (not in the Flask MVP requirements)."),
    ],
  }],
});

const out = path.join(__dirname, "NER_Training_Note.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(out, buf);
  console.log("Wrote", out);
});
