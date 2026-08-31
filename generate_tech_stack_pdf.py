"""Script to generate a comprehensive, professional PDF of the Legal Metrology Project Tech Stack."""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 750, "LEGAL METROLOGY COMPLIANCE PLATFORM")
            self.setFont("Helvetica", 8)
            self.drawRightString(558, 750, "Complete Technology Stack & Architecture")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.75)
            self.line(54, 742, 558, 742)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.75)
        self.line(54, 50, 558, 50)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 38, "Legal Metrology Act, 2009 & PCR, 2011 Compliance Engine")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 38, page_str)
        self.restoreState()


def build_pdf(filename: str = "Legal_Metrology_Project_Tech_Stack.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=64,
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0f172a")      # Slate 900
    c_accent = colors.HexColor("#2563eb")       # Blue 600
    c_accent_dark = colors.HexColor("#1d4ed8")  # Blue 700
    c_bg_light = colors.HexColor("#f8fafc")     # Slate 50
    c_card_border = colors.HexColor("#e2e8f0")  # Slate 200
    c_text_main = colors.HexColor("#1e293b")    # Slate 800
    c_text_muted = colors.HexColor("#64748b")   # Slate 500

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=c_text_muted,
        spaceAfter=14,
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_accent_dark,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_text_main,
        spaceAfter=4,
    )

    badge_style = ParagraphStyle(
        'Badge_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_text_main,
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=c_primary,
    )

    code_style = ParagraphStyle(
        'CodeCell',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0369a1"),
    )

    story = []

    # Title Section
    story.append(Paragraph("Legal Metrology Compliance Platform", title_style))
    story.append(Paragraph("Comprehensive Technical Architecture & Technology Stack Specification", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=12))

    # Executive Overview Box
    overview_text = (
        "<b>Project Purpose:</b> Automated e-commerce compliance verification and decision-support system designed to audit digital "
        "product listings against the <b>Legal Metrology (Packaged Commodities) Rules, 2011 (LMPC)</b> and the "
        "<b>Legal Metrology Act, 2009</b>. The platform integrates dynamic DOM web scraping, optical character recognition (OCR), "
        "deterministic rule evaluation algorithms, automated PDF generation, and an interactive auditor dashboard."
    )
    overview_table = Table(
        [[Paragraph(overview_text, body_style)]],
        colWidths=[504]
    )
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#bfdbfe")),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 10))

    # 1. System Architecture Matrix Table
    story.append(Paragraph("1. Technology Stack Summary by Architectural Layer", h1_style))
    
    stack_data = [
        [
            Paragraph("Layer / Tier", table_header_style),
            Paragraph("Core Technologies & Frameworks", table_header_style),
            Paragraph("Key Responsibilities & Capabilities", table_header_style),
        ],
        [
            Paragraph("<b>Frontend UI & Dashboard</b>", table_cell_bold),
            Paragraph("• React 18.3<br/>• Vite 5.4 (ESM Bundler)<br/>• Vanilla CSS (Design Tokens)<br/>• Google Fonts (Outfit / Mono)", table_cell_style),
            Paragraph("High-performance responsive SPA, hash router navigation (#, #scanner, #history, #rules), live category filtering, real-time search, interactive inspection reports.", table_cell_style),
        ],
        [
            Paragraph("<b>Backend API & Web Server</b>", table_cell_bold),
            Paragraph("• Python 3.11+ / 3.13<br/>• Flask 3.0+ (WSGI REST API)<br/>• Flask-CORS<br/>• Werkzeug", table_cell_style),
            Paragraph("RESTful endpoints (/api/scan/*, /api/products, /api/stats, /api/rules, /api/reports), request routing, CORS configuration, payload validation.", table_cell_style),
        ],
        [
            Paragraph("<b>Data Ingestion & Web Scraping</b>", table_cell_bold),
            Paragraph("• Playwright (Chromium)<br/>• BeautifulSoup4 (lxml)<br/>• urllib / Requests<br/>• RegEx Pattern Engine", table_cell_style),
            Paragraph("Headless browser automation for client-side rendered JavaScript pages, HTML DOM parsing, structured technical declaration extraction.", table_cell_style),
        ],
        [
            Paragraph("<b>Optical Character Recognition (OCR)</b>", table_cell_bold),
            Paragraph("• Tesseract OCR 5.x<br/>• PyTesseract<br/>• Pillow (PIL)", table_cell_style),
            Paragraph("Dual-source compliance extraction from physical product packaging photos, image preprocessing, bounding-box normalization, text digitisation.", table_cell_style),
        ],
        [
            Paragraph("<b>Legal Compliance Rule Engine</b>", table_cell_bold),
            Paragraph("• Codified Statutory Rulebase<br/>• 21 LMPC 2011 Clauses<br/>• Multi-Factor Scorer", table_cell_style),
            Paragraph("Deterministic verification of 10+ mandatory declarations (MRP, Net Qty, Origin, Mfg/Exp dates, Importer, Consumer Care). Ambiguity & conflict detection.", table_cell_style),
        ],
        [
            Paragraph("<b>Data Persistence & Storage</b>", table_cell_bold),
            Paragraph("• SQLite3 (ACID Relational)<br/>• Local JSON Schemas", table_cell_style),
            Paragraph("Relational schema tracking scanned products, individual statutory field extractions, auditor overrides, and compliance ratings.", table_cell_style),
        ],
        [
            Paragraph("<b>Document Generation & Export</b>", table_cell_bold),
            Paragraph("• ReportLab 5.0<br/>• Vector Canvas Rendering", table_cell_style),
            Paragraph("Automated official Legal Metrology Inspection Certificates in PDF format with executive scoring badges, statutory tables, and auditor sign-off sections.", table_cell_style),
        ],
        [
            Paragraph("<b>Mock Retail Environment</b>", table_cell_bold),
            Paragraph("• DemoMart.in Storefront<br/>• Amazon-Style Product Pages", table_cell_style),
            Paragraph("17 fully-categorized demo listings with authentic packaging imagery and pre-configured compliance scenarios (complete, missing origin, conflicting MRP, etc.).", table_cell_style),
        ],
    ]

    t_stack = Table(stack_data, colWidths=[110, 150, 244])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_accent),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_card_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 12))

    # 2. Detailed Technical Components
    story.append(Paragraph("2. Deep-Dive Component Specifications", h1_style))

    # Component A: Frontend
    story.append(Paragraph("A. Frontend Client Architecture (SPA)", h2_style))
    story.append(Paragraph(
        "• <b>Framework & Bundling:</b> Built using React 18.3 with Vite 5.4. Uses native ES modules (ESM) for sub-second Hot Module Replacement (HMR) and optimized rollup production bundles.<br/>"
        "• <b>Design System:</b> Pure modern Vanilla CSS with dark-theme color tokens (`--bg-primary`, `--accent-blue`, `--surface-card`, etc.), glassmorphism backdrops, and fluid typography (`Outfit` & `JetBrains Mono`).<br/>"
        "• <b>Routing & State:</b> Client-side Hash Router (`#`, `#scanner`, `#history`, `#rules`) ensuring lightweight zero-latency tab switching without full page reloads.<br/>"
        "• <b>Views:</b><br/>"
        "  &nbsp;&nbsp;1. <i>Landing Page:</i> Hero presentation, high-level metrics, and inspection pillar cards.<br/>"
        "  &nbsp;&nbsp;2. <i>Compliance Scanner:</i> Centered tri-modal scanning interface (Product URL, Raw Text, and Image OCR).<br/>"
        "  &nbsp;&nbsp;3. <i>Catalog & History:</i> Categorized DemoMart directory with real-time search, category pills, and live audit history table with instant PDF generation.<br/>"
        "  &nbsp;&nbsp;4. <i>Rules Directory:</i> Codified statutory database of 21 Legal Metrology rules with search and key compliance checklists.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # Component B: Backend & Rule Engine
    story.append(Paragraph("B. Backend API & Deterministic Rule Engine", h2_style))
    story.append(Paragraph(
        "• <b>REST API Endpoints:</b><br/>"
        "  &nbsp;&nbsp;• <font face='Courier' color='#0369a1'>POST /api/scan/url</font> — Automated Playwright/BeautifulSoup extraction + rule engine evaluation.<br/>"
        "  &nbsp;&nbsp;• <font face='Courier' color='#0369a1'>POST /api/scan/text</font> — Direct text and pasted description compliance scanning.<br/>"
        "  &nbsp;&nbsp;• <font face='Courier' color='#0369a1'>POST /api/scan/image</font> — Tesseract OCR packaging digitisation and analysis.<br/>"
        "  &nbsp;&nbsp;• <font face='Courier' color='#0369a1'>GET /api/products</font> &amp; <font face='Courier' color='#0369a1'>GET /api/stats</font> — Audit history logs and platform KPI metrics.<br/>"
        "  &nbsp;&nbsp;• <font face='Courier' color='#0369a1'>POST /api/products/&lt;id&gt;/report</font> — Dynamic ReportLab PDF compilation.<br/>"
        "• <b>Deterministic Rule Engine:</b> Evaluates 21 statutory rules codified from the Legal Metrology Act, 2009 and Packaged Commodities Rules, 2011. Checks MRP format, Net Quantity units (g, kg, ml, L, Piece, Pair, Set), Country of Origin, Manufacturing / Import dates, and Consumer Care details without relying on brittle generative hallucinations.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # Component C: OCR & Scraping Pipeline
    story.append(Paragraph("C. Extraction & Packaging OCR Pipeline", h2_style))
    story.append(Paragraph(
        "• <b>Web Scraping:</b> Headless Chromium orchestrated via Playwright to execute and render modern JavaScript client-side web pages before extracting the complete DOM tree.<br/>"
        "• <b>OCR Extraction:</b> Tesseract OCR v5.x paired with Pillow image processing (grayscale transformation, thresholding, contrast normalization) for digitizing physical product packaging declarations.<br/>"
        "• <b>Dual-Source Conflict Detection:</b> Cross-compares digital web listings against physical packaging labels to flag deceptive discrepancies (e.g. higher MRP printed on box vs. website).",
        body_style
    ))
    story.append(Spacer(1, 10))

    # 3. Verified Catalog Dataset
    story.append(Paragraph("3. DemoMart Verified Dataset & Pre-Configured Test Scenarios", h1_style))
    story.append(Paragraph(
        "The project comes pre-loaded with 17 verified test products spanning 6 major retail categories with authentic high-resolution web imagery, designed for end-to-end compliance demonstration:",
        body_style
    ))

    catalog_summary_data = [
        [
            Paragraph("Category", table_header_style),
            Paragraph("Products Included", table_header_style),
            Paragraph("Test Compliance Scenarios Covered", table_header_style),
        ],
        [
            Paragraph("<b>Electronics</b>", table_cell_bold),
            Paragraph("• SoundWave ANC Earbuds (TWS)<br/>• VoltMax 65W GaN Fast Charger<br/>• PulseFit AMOLED Smartwatch", table_cell_style),
            Paragraph("Complete multi-unit declarations, imported electronics with importer details, missing month & year of import test.", table_cell_style),
        ],
        [
            Paragraph("<b>Footwear</b>", table_cell_bold),
            Paragraph("• StridePro Men's Running Shoes (UK 8)<br/>• UrbanWalk Oxford Formal Shoes (UK 9)", table_cell_style),
            Paragraph("Footwear sizing declarations (1 Pair, UK standard), missing country of origin test scenario.", table_cell_style),
        ],
        [
            Paragraph("<b>Apparel & Clothing</b>", table_cell_bold),
            Paragraph("• DenimX Slim Fit Stretch Jeans (32)<br/>• AeroFit Pique Cotton Polo Shirt (L)", table_cell_style),
            Paragraph("Garment dimensional size & quantity declarations (1 Piece), missing customer care details scenario.", table_cell_style),
        ],
        [
            Paragraph("<b>Packaged Foods</b>", table_cell_bold),
            Paragraph("• HIVE Organic Himalayan Honey (500g)<br/>• Royal Heritage Basmati Rice (5kg)<br/>• ShudhKhet Whole Wheat Atta (10kg)<br/>• NutriNut California Almonds (500g)<br/>• SwissDelight Dark Chocolate (125g)<br/>• PureGold Groundnut Oil (1L)", table_cell_style),
            Paragraph("Standard food weights, imported chocolate declarations, missing date of manufacture, missing origin, and net volume declarations.", table_cell_style),
        ],
        [
            Paragraph("<b>Beverages & Snacks</b>", table_cell_bold),
            Paragraph("• Assam Valley Tea Bags (100g)<br/>• Malabar Roast Filter Coffee (200g)<br/>• CrunchyCo Spicy Masala Chips (50g)", table_cell_style),
            Paragraph("Complete tea/coffee packaging, sparse listing scenario (multiple missing statutory fields).", table_cell_style),
        ],
        [
            Paragraph("<b>Personal Care</b>", table_cell_bold),
            Paragraph("• KeshVeda Herbal Shampoo (400ml)", table_cell_style),
            Paragraph("Liquid cosmetic volume declarations, Ayurvedic manufacturer compliance.", table_cell_style),
        ],
    ]

    t_cat = Table(catalog_summary_data, colWidths=[100, 180, 224])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_card_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('PADDING', (0, 0), (-1, -1), 4.5),
    ]))
    story.append(t_cat)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {filename}")


if __name__ == "__main__":
    build_pdf()
