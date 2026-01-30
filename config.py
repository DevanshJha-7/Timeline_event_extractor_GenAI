import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 8
load_dotenv()

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')