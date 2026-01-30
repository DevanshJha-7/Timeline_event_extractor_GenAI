from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

# ✅ Local embeddings (no API quota, fast, reliable)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def vector_db(chunks):
    """
    chunks: list of dicts produced by date_aware_chunk
    Each chunk must contain:
    - text
    - year
    - page
    - source
    """

    documents = []

    for i, c in enumerate(chunks):
        text = c.get("text", "")

        # 🚨 skip empty or junk chunks
        if not text or not text.strip():
            print(f"⚠️ Skipping empty chunk at index {i}")
            continue

        documents.append(
            Document(
                page_content=text.strip(),
                metadata={
                    "year": c.get("year"),
                    "page": c.get("page"),
                    "source": c.get("source")
                }
            )
        )

    if not documents:
        raise ValueError("❌ No valid documents to embed.")

    # ✅ Build Chroma vector store
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    return vectorstore
