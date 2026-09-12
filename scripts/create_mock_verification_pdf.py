from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUTPUT = Path("output/pdf/mock_gst_registration_certificate.pdf")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles["Title"].textColor = HexColor("#8B1E1E")
    styles["Title"].fontSize = 22
    styles["Title"].leading = 28
    styles["Heading2"].textColor = HexColor("#1A1A1A")
    body = styles["BodyText"]
    body.fontSize = 10
    body.leading = 15

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm, topMargin=18 * mm, bottomMargin=18 * mm)
    story = [
        Paragraph("MOCK DOCUMENT - FOR CLauz X DEMO ONLY", styles["Heading2"]),
        Spacer(1, 8 * mm),
        Paragraph("GST Registration Certificate", styles["Title"]),
        Spacer(1, 4 * mm),
        Paragraph("This fictional sample contains no real registration or taxpayer information. Upload it only to test the document verification workflow.", body),
        Spacer(1, 8 * mm),
    ]
    rows = [
        ["Field", "Mock value"],
        ["Registered legal name", "Demo Compliance Ventures Private Limited"],
        ["GSTIN", "27ABCDE1234F1Z5"],
        ["State / jurisdiction", "Maharashtra"],
        ["Registration status", "Active (demo data)"],
        ["Certificate reference", "MOCK-GST-2026-0001"],
        ["Issued on", "2026-01-15"],
        ["Valid up to", "2027-01-14"],
    ]
    table = Table(rows, colWidths=[52 * mm, 108 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#8B1E1E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#FAF7F2")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CFC7BD")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story += [table, Spacer(1, 10 * mm), Paragraph("Verification note", styles["Heading2"]), Spacer(1, 2 * mm), Paragraph("This mock certificate is designed to provide readable identification, registration, and validity evidence. The verifier should still evaluate it only against the obligation selected in the dashboard.", body)]
    doc.build(story)


if __name__ == "__main__":
    main()
