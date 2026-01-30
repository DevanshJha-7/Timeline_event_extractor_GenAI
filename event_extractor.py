import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# -------------------- ENV & MODEL --------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Use the model defined in your config or local env
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={
        "temperature": 0.1, # Lower temperature for higher factual accuracy
    }
)

def clean_text(text):
    """Removes common Wikipedia noise and extra whitespace."""
    # Remove navigation artifacts and bracketed citations [1], [edit]
    text = re.sub(r'\[\d+\]|\[edit\]', '', text)
    # Remove excessive newlines
    text = re.sub(r'\n+', ' ', text)
    return text.strip()

def extract_events(docs, query=None, source_url=None):
    """
    docs: list of LangChain Document objects
    query: user intent (e.g., 'career achievements')
    source_url: original URL if web source
    """

    MAX_CONTEXT_CHARS = 100000 # Increased limit for Gemini's large window
    is_url = source_url is not None and source_url.startswith("http")

    context_parts = []
    total_len = 0
    
    # Noise filter keywords
    SKIP_KEYWORDS = [
        "jump to content", "main menu", "navigation",
        "edit links", "languages", "tools",
        "donate", "create account", "log in"
    ]

    for d in docs:
        text = clean_text(d.page_content)
        
        
        if any(key in text.lower() for key in SKIP_KEYWORDS) and len(text) < 300:
            continue

        
        if len(text) > 6000:
            text = text[:6000]

        if is_url:
            chunk = f"SOURCE: (Web source) {text}"
        else:
            page_num = d.metadata.get('page', 'Unknown')
            chunk = f"SOURCE: (PDF page {page_num}) {text}"

        if total_len + len(chunk) > MAX_CONTEXT_CHARS:
            break

        context_parts.append(chunk)
        total_len += len(chunk)

    if not context_parts:
        print("⚠️ No valid context chunks found for extraction.")
        return []

    context = "\n\n---\n\n".join(context_parts)

   

    prompt = f"""
You are an expert historian and data extractor. 
Your task is to extract significant chronological events based on the context provided.

USER REQUEST:
{query or "Extract a comprehensive chronological timeline of all major events."}

OUTPUT FORMAT:
Return a JSON array of objects. Do NOT include markdown code blocks (like ```json).
If no events are found, return an empty array [].

JSON SCHEMA:
[
  {{
    "year": number (integer) or null,
    "period": "string (e.g. 'June 2004' or 'Early Childhood')",
    "event_title": "string (Short, clear title)",
    "description": "string (1-2 sentences explaining what happened)",
    "source": {{
      "type": "url" or "pdf",
      "name": "Wikipedia" or "Document",
      "page": number or null,
      "url": "{source_url if is_url else "null"}"
    }},
    "confidence": number (between 0.0 and 1.0)
  }}
]

CONSTRAINTS:
1. Only use information from the Context below.
2. If a specific year is mentioned, set "year" as an integer.
3. If a specific month or day is mentioned, include it in "period".
4. If "Web source" is mentioned in the context, set source.type to "url".
5. If "PDF page" is mentioned, set source.type to "pdf" and extract the page number.

CONTEXT:
{context}
"""

    try:
        response = model.generate_content(prompt)
       
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(raw_text)
    
    except json.JSONDecodeError:
        print("❌ Error: LLM output was not valid JSON.")
        print(f"RAW OUTPUT: {response.text}")
        return []
    except Exception as e:
        print(f"❌ Extraction error: {str(e)}")
        return []