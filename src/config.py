import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# LLM Provider: "gemini" or "openai"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # Default to Gemini

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LLM Settings
LLM_MODEL = "gemini-1.5-flash" if LLM_PROVIDER == "gemini" else "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.7

# Chunking Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Vector Store
VECTOR_DB_PATH = "./data/chroma_db"
COLLECTION_NAME = "youtube_lectures"

# Retrieval
TOP_K_RESULTS = 4
