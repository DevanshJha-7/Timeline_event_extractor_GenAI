from articleloader import load_article
from pdfloader import load_pdfs
import tempfile
import os


def load_source(source):
    """
    source can be:
    - URL string
    - PDF filename string
    - Streamlit UploadedFile
    """

    # 🟢 CASE 1: Streamlit UploadedFile
    if hasattr(source, "read") and hasattr(source, "name"):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(source.read())
            tmp_path = tmp.name

        return load_pdfs(tmp_path)

    # 🟢 CASE 2: URL string
    if isinstance(source, str) and (
        source.startswith("http://") or source.startswith("https://")
    ):
        return load_article(source)

    # 🟢 CASE 3: PDF filename string
    if isinstance(source, str):
        return load_pdfs(source)

    raise ValueError("Unsupported source type")
