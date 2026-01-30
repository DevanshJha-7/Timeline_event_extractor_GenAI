import re

# Refined pattern to catch common year formats
YEAR_PATTERN = re.compile(r"\b(?:18|19|20)\d{2}\b")

def date_aware_chunk(docs):
    chunks = []

    for doc in docs:
        text = doc.page_content.strip()

       
        if len(text) < 100:
            continue

        page = doc.metadata.get("page")
        source = doc.metadata.get("source")

    
        years = sorted(list(set(int(y) for y in YEAR_PATTERN.findall(text))))

        if years:
            
            chunks.append({
                "text": text,
                "year": years[0], 
                "all_years": years,
                "page": page,
                "source": source
            })
        else:
            
            chunks.append({
                "text": text,
                "year": None,
                "page": page,
                "source": source
            })

    return chunks