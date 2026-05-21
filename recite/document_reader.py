"""Read text content from various document formats: TXT, MD, PDF, DOCX."""
import os


def read_document(file_path):
    """Detect format by extension and extract plain text."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Document not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext in (".txt", ".md", ".markdown", ".rst", ".org"):
        return _read_text(file_path)
    elif ext == ".pdf":
        return _read_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return _read_docx(file_path)
    else:
        raise ValueError(
            f"Unsupported file format: {ext}\n"
            "Supported formats: .txt, .md, .pdf, .docx"
        )


def _read_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _read_pdf(file_path):
    try:
        import fitz  # pymupdf
    except ImportError:
        raise ImportError(
            "Reading PDF requires pymupdf. Install with: pip install pymupdf"
        )

    doc = fitz.open(file_path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n\n".join(pages)


def _read_docx(file_path):
    try:
        from docx import Document
    except ImportError:
        raise ImportError(
            "Reading .docx requires python-docx. Install with: pip install python-docx"
        )

    doc = Document(file_path)
    paragraphs = []
    for para in doc.paragraphs:
        if para.text.strip():
            # preserve heading hierarchy
            if para.style.name.startswith("Heading"):
                level = para.style.name.split()[-1]
                try:
                    prefix = "#" * int(level)
                except ValueError:
                    prefix = "##"
                paragraphs.append(f"{prefix} {para.text.strip()}")
            else:
                paragraphs.append(para.text)
    return "\n\n".join(paragraphs)
