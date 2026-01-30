from pdfloader import load_pdfs
from date_chunker import date_aware_chunk
from embeddings import vector_db
from event_extractor import extract_events
from load_source import load_source
from articleloader import load_article

def is_timeline_query(query: str) -> bool:
    keywords = ["evolve", "evolution", "over time", "history", "timeline"]
    return any(k in query.lower() for k in keywords)


def main():
    src = "https://en.wikipedia.org/wiki/Cristiano_Ronaldo"
    docs = load_source(src)
    chunks = date_aware_chunk(docs)
    vectorstore = vector_db(chunks)
    
    query = "memorable champions league matches"
    
    k = 15  # More chunks for better timeline
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    retrieved = retriever.invoke(query)
    
    print(f"📄 Retrieved {len(retrieved)} chunks")
    # print(retrieved)
    
    # Pass source URL to extract_events
    events = extract_events(
    retrieved,
    source_url=src
)

    
    print(f"📊 Extracted {len(events)} events")
    print(events)


if __name__ == "__main__":
    main()
