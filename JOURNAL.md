
---
### 📝 2025-11-18 20:11
Testing journal.py script.

---
### 📝 2025-11-18 20:12
Fixed environment setup and synced project with Google Drive + GitHub.

---
### 📝 2025-11-20 01:28
Updated Notebook 02 and 03 to include BGE-M3 model (updated pipeline accordingly)

---
### 🔧 Commit: b51676b — 2025-11-20 01:34
Migrate RAG pipeline to BGE-M3

- Updated embedding generation to use BGE-M3 (1024-dim normalized vectors)
- Updated Qdrant collection to cosine + 1024 dimensions
- Updated semantic_retrieval() to use BGEM3FlagModel and query_with_vectors
- Replaced all MiniLM references
- Updated hybrid retrieval pipeline
- Fixed encode() differences for BGE-M3 output format
- Updated evaluation pipeline for new embeddings
- Cleaned reranking, graph retrieval, and context assembly steps
