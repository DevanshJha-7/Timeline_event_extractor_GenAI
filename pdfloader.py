import os
from langchain_community.document_loaders import PyPDFLoader

def load_pdfs(filename):
   
    base_dir = os.path.dirname(os.path.abspath(__file__))

    pdf_path = os.path.join(base_dir, filename)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    loader = PyPDFLoader(pdf_path)
    return loader.load()

