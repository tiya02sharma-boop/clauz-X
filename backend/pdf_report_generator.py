"""Generate high-quality structured PDF reports for Clauz X Contract Health Reviews."""
from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page numbers."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict[str, Any]] = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count: int) -> None:
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#777777"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 810, "CLAUZ X  |  Contract Health Report & Legal Risk Audit")
            self.setStrokeColor(colors.HexColor("#E5E5E5"))
            self.setLineWidth(0.5)
            self.line(40, 804, 555, 804)

        # Running Footer (all pages)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 30, page_text)
        self.drawString(40, 30, "CONFIDENTIAL  ·  Indian Commercial Contracting First-Pass Screening")
        self.setStrokeColor(colors.HexColor("#E5E5E5"))
        self.setLineWidth(0.5)
        self.line(40, 42, 555, 42)
        self.restoreState()


def build_contract_health_pdf(report: dict[str, Any]) -> bytes:
    """Render a comprehensive, professional PDF document from a Contract Health Report dictionary."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=48,
        bottomMargin=52,
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    brick_primary = colors.HexColor("#A8322D")
    brick_light = colors.HexColor("#FBF0EE")
    green_text = colors.HexColor("#087443")
    green_bg = colors.HexColor("#E8F8F0")
    amber_text = colors.HexColor("#9A5B00")
    amber_bg = colors.HexColor("#FFF5D9")
    red_text = colors.HexColor("#BB2431")
    red_bg = colors.HexColor("#FFF0F1")
    dark_text = colors.HexColor("#1A1A1A")
    muted_text = colors.HexColor("#555555")
    border_color = colors.HexColor("#DDDDDD")

    # Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=brick_primary,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=muted_text,
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=brick_primary,
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_text,
    )
    bold_body = ParagraphStyle(
        "BoldBody",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=dark_text,
    )
    quote_style = ParagraphStyle(
        "QuoteStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#333333"),
    )
    code_style = ParagraphStyle(
        "CodeStyle",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#222222"),
    )

    story: list[Any] = []

    # 1. Header Banner
    filename = report.get("filename") or "Commercial_Agreement.pdf"
    score = report.get("health_score", 0)
    risk = (report.get("overall_risk") or "medium").upper()
    ai_enhanced = report.get("ai_enhanced", False)
    ai_model = report.get("ai_model") or "Gemini 3.5 Flash"

    banner_data = [
        [
            Paragraph("<b>CLAUZ X</b><br/><font size=8 color='#666'>INDIAN CONTRACT COMPLIANCE & RISK AUDIT</font>", title_style),
            Paragraph(
                f"<b>HEALTH SCORE: {score}%</b><br/>"
                f"<font size=8 color='{red_text.hexval() if risk == 'HIGH' else amber_text.hexval() if risk == 'MEDIUM' else green_text.hexval()}'>"
                f"OVERALL RISK: {risk}</font><br/>"
                f"<font size=7 color='#666'>{'✨ ' + ai_model if ai_enhanced else 'Keyword Rule Baseline'}</font>",
                ParagraphStyle("HeaderScore", parent=styles["Normal"], alignment=2, leading=12)
            ),
        ]
    ]
    banner_table = Table(banner_data, colWidths=[330, 185])
    banner_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(banner_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=brick_primary, spaceBefore=4, spaceAfter=10))

    # 2. Metadata Info Block
    audit_time = datetime.now().strftime("%d %B %Y, %I:%M %p IST")
    meta_data = [
        [
            Paragraph(f"<b>Document:</b> {filename}", body_style),
            Paragraph(f"<b>Audit Date:</b> {audit_time}", body_style),
        ],
        [
            Paragraph(f"<b>Standard Ruleset:</b> Indian Commercial Playbook (14 Checks)", body_style),
            Paragraph(f"<b>Analysis Mode:</b> {'Gemini AI Deep Review' if ai_enhanced else 'Deterministic Screening'}", body_style),
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 245])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9F9F9")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. Summary Counters Table
    summary = report.get("summary", {})
    compliant_count = summary.get("compliant", 0)
    review_count = summary.get("needs_review", 0)
    high_risk_count = summary.get("missing_high_risk", 0)
    total_checks = summary.get("total_checks", 14)

    summary_data = [
        [
            Paragraph(f"<b>{compliant_count} / {total_checks}</b><br/><font size=7 color='{green_text.hexval()}'>COMPLIANT</font>", ParagraphStyle("CStat", parent=styles["Normal"], alignment=1, leading=12)),
            Paragraph(f"<b>{review_count} / {total_checks}</b><br/><font size=7 color='{amber_text.hexval()}'>NEEDS REVIEW</font>", ParagraphStyle("RStat", parent=styles["Normal"], alignment=1, leading=12)),
            Paragraph(f"<b>{high_risk_count} / {total_checks}</b><br/><font size=7 color='{red_text.hexval()}'>MISSING / HIGH RISK</font>", ParagraphStyle("HStat", parent=styles["Normal"], alignment=1, leading=12)),
        ]
    ]
    summary_table = Table(summary_data, colWidths=[171, 171, 173])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), green_bg),
        ("BACKGROUND", (1, 0), (1, 0), amber_bg),
        ("BACKGROUND", (2, 0), (2, 0), red_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # 4. Executive Legal Summary
    exec_summary = report.get("executive_summary")
    if exec_summary:
        story.append(Paragraph("Executive Legal Summary", section_heading))
        summary_table = Table([[Paragraph(exec_summary, body_style)]], colWidths=[515])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAFAFA")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 10))

    # 5. Key Risks & Red Flags Callout
    key_risks = report.get("key_risks", [])
    if key_risks:
        story.append(Paragraph("Key Legal Risks & Red Flags", section_heading))
        risk_items = "<br/>".join(f"• <b>{r}</b>" for r in key_risks)
        risk_table = Table([[Paragraph(risk_items, ParagraphStyle("RiskText", parent=body_style, textColor=colors.HexColor("#7A141D")))]], colWidths=[515])
        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), red_bg),
            ("LINEBEFORE", (0, 0), (0, -1), 3, red_text),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#FFCCD1")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 10))

    # 6. Negotiation Recommendations
    recs = report.get("negotiation_recommendations", [])
    if recs:
        story.append(Paragraph("Tactical Negotiation Priorities", section_heading))
        rec_items = "<br/>".join(f"• {r}" for r in recs)
        rec_table = Table([[Paragraph(rec_items, body_style)]], colWidths=[515])
        rec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), brick_light),
            ("LINEBEFORE", (0, 0), (0, -1), 3, brick_primary),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#F2CECB")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(rec_table)
        story.append(Spacer(1, 14))

    # 7. Clause-by-Clause Detailed Audit
    story.append(PageBreak())
    story.append(Paragraph("Clause-by-Clause Audit & Recommendations", title_style))
    story.append(Paragraph("Detailed assessment of 14 core templates under Indian commercial statutes.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=brick_primary, spaceBefore=4, spaceAfter=12))

    results = report.get("results", [])
    for idx, check in enumerate(results, start=1):
        status = check.get("status", "needs_review")
        title = check.get("title", f"Check {idx}")
        required = check.get("required", False)
        explanation = check.get("explanation") or check.get("reason", "No explanation available.")
        evidence = check.get("evidence")
        risk_assessment = check.get("risk_assessment")
        amendment = check.get("suggested_amendment")

        status_text = "COMPLIANT" if status == "compliant" else "NEEDS REVIEW" if status == "needs_review" else "MISSING / HIGH RISK"
        badge_bg = green_bg if status == "compliant" else amber_bg if status == "needs_review" else red_bg
        badge_fg = green_text if status == "compliant" else amber_text if status == "needs_review" else red_text

        clause_rows: list[list[Any]] = [
            [
                Paragraph(f"<b>{idx}. {title}</b> {'<font color=\"#888\" size=7>[REQUIRED]</font>' if required else '<font color=\"#888\" size=7>[ADVISORY]</font>'}", bold_body),
                Paragraph(f"<b><font color='{badge_fg.hexval()}'>{status_text}</font></b>", ParagraphStyle("BadgeStyle", parent=styles["Normal"], alignment=2, fontSize=8)),
            ]
        ]

        body_parts = [f"<b>Detailed Analysis:</b> {explanation}"]
        if evidence:
            body_parts.append(f"<br/><b>Quoted Excerpt:</b> <i>“{evidence}”</i>")
        if risk_assessment:
            body_parts.append(f"<br/><b>⚖️ Indian Legal Risk:</b> {risk_assessment}")
        if amendment:
            body_parts.append(f"<br/><b>Suggested Amendment / Compromise:</b><br/><font face='Courier' size=8>{amendment}</font>")

        clause_rows.append([
            Paragraph("".join(body_parts), body_style),
            Paragraph("", body_style),
        ])

        clause_table = Table(clause_rows, colWidths=[400, 115])
        clause_table.setStyle(TableStyle([
            ("SPAN", (0, 1), (1, 1)),
            ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#F5F5F5")),
            ("BACKGROUND", (0, 1), (1, 1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.5, border_color),
            ("LINEBELOW", (0, 0), (1, 0), 0.5, border_color),
            ("LINEBEFORE", (0, 0), (0, -1), 3, badge_fg),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))

        story.append(KeepTogether([clause_table, Spacer(1, 8)]))

    # 8. Disclaimer
    disclaimer_text = report.get(
        "disclaimer",
        "First-pass automated screening only, not legal advice or contract approval. Have Indian legal counsel approve the playbook and material agreements."
    )
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Notice & Disclaimer:</b> {disclaimer_text}", ParagraphStyle("DisclaimerStyle", parent=body_style, fontSize=7.5, leading=10, textColor=muted_text)))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
