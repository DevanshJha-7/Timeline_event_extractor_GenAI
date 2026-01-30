def temporal_retrieve(vectorstore, query, top_k):
    docs = vectorstore.similarity_search(query, k=top_k)

    docs.sort(key=lambda d: d.metadata.get("year", "9999"))

    return docs
