from pathlib import Path

def extract_pdf_text(pdf_path: str | Path) -> dict:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        if not text: return {"text": "", "page_count": len(reader.pages), "extraction_failed": True, "error": "No extractable text; document may be scanned."}
        return {"text": text, "page_count": len(reader.pages), "extraction_failed": False}
    except Exception as error:
        return {"text": "", "page_count": 0, "extraction_failed": True, "error": str(error)}
