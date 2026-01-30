import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from collections import defaultdict

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash",
    generation_config={"response_mime_type": "application/json"})

def needs_aggregation(events, threshold=20):
    return len(events) > threshold

def aggregation(events, max_groups=10):
   from collections import defaultdict

def needs_aggregation(events, threshold=15):
    """
    Decide whether aggregation is needed.
    """
    return len(events) > threshold


def aggregate(events, max_events=10):
    """
    Aggregate many fine-grained events into a smaller timeline.
    No LLM involved.
    """

    # Separate events with and without year
    with_year = [e for e in events if e.get("year") is not None]
    without_year = [e for e in events if e.get("year") is None]

    # Group by decade
    buckets = defaultdict(list)

    for e in with_year:
        decade = (e["year"] // 10) * 10
        buckets[decade].append(e)

    aggregated = []

    for decade in sorted(buckets.keys()):
        bucket = buckets[decade]

        
        bucket_sorted = sorted(
            bucket,
            key=lambda x: x.get("confidence", 0),
            reverse=True
        )

        top_event = bucket_sorted[0]

        aggregated.append({
            "year": decade,
            "period": f"{decade}s",
            "event_title": f"Key developments in the {decade}s",
            "description": top_event["description"],
            "source": top_event.get("source"),
            "confidence": round(top_event.get("confidence", 0.8), 2)
        })

        # Stop if we reached UI-friendly limit
        if len(aggregated) >= max_events:
            break

    
    for e in without_year:
        if len(aggregated) >= max_events:
            break
        aggregated.append(e)

    return aggregated
