"""
Central configuration module for the entire RAG project.
This file is imported by all notebooks (01–04).
"""

import os
from pathlib import Path

# ------------------------------------------------------------
# 1. Resolve project root robustly
# ------------------------------------------------------------
# Works whether called from VS Code, JupyterLab, or terminal.
PROJECT_ROOT = Path(__file__).resolve().parent

# ------------------------------------------------------------
# 2. Directories
# ------------------------------------------------------------
DATA_DIR = PROJECT_ROOT / "data"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Ensure /data exists
DATA_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------
# 3. File paths used across notebooks
# ------------------------------------------------------------
CHUNKS_FILE = DATA_DIR / "chunks.jsonl"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.jsonl"
CONTEXT_FILE = DATA_DIR / "context_for_llm.json"

# ------------------------------------------------------------
# 4. Retrieval configuration
# ------------------------------------------------------------
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "enterprise_docs")

# ------------------------------------------------------------
# 5. Embedding model
# ------------------------------------------------------------
# Used in Notebook 02 + Notebook 03
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

# ------------------------------------------------------------
# 6. Reranker model
# ------------------------------------------------------------
RERANKER_MODEL = os.getenv(
    "RERANKER_MODEL",
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# ------------------------------------------------------------
# 7. Ollama configuration
# ------------------------------------------------------------
# Notebook 04 needs this
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# Timeout for LLM requests
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))

# ------------------------------------------------------------
# 8. Debug print (optional)
# ------------------------------------------------------------
if __name__ == "__main__":
    print("PROJECT_ROOT:", PROJECT_ROOT)
    print("DATA_DIR:", DATA_DIR)
    print("CHUNKS_FILE:", CHUNKS_FILE)
    print("EMBEDDINGS_FILE:", EMBEDDINGS_FILE)
    print("CONTEXT_FILE:", CONTEXT_FILE)
    print("QDRANT_URL:", QDRANT_URL)
    print("OLLAMA_HOST:", OLLAMA_HOST)
    print("OLLAMA_MODEL:", OLLAMA_MODEL)
