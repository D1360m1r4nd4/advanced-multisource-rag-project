🧠 Advanced Multi-Source RAG System

A production-grade Retrieval-Augmented Generation (RAG) pipeline with hybrid retrieval, graph reasoning, and BGE-M3 embeddings, running fully on WSL2 + Docker + Qdrant + Memgraph.

🚀 Features

Advanced text cleaning + recursive chunking

BGE-M3 1024-dim embeddings (state-of-the-art, multilingual)

Qdrant vector database (cosine similarity)

Memgraph knowledge graph (entity & relationship retrieval)

Hybrid Retrieval (Vector + Graph)

Cross-Encoder reranking (ms-marco-MiniLM-L-6-v2)

Context packaging for an LLM (merged, deduplicated, citation-ready)

Fully modular notebooks:

Notebook 01 → Preprocessing + Chunking

Notebook 02 → Embedding + Qdrant Ingestion

Notebook 03 → Hybrid Retrieval + Reranking

Notebook 04 → LLM Integration (optional)

🏗️ System Architecture

GitHub supports Mermaid natively.
This will render correctly after pushing to GitHub:

flowchart TD

    A[Raw Documents<br/>PDF · TXT · DOCX] --> B1

    B1[Notebook 01:<br/>Cleaning + Recursive Chunking] --> B2
    B2[Notebook 02:<br/>BGE-M3 Embeddings (1024-dim)] --> C1

    C1[Qdrant Vector DB<br/>Cosine Search]
    C2[Memgraph Graph DB<br/>Cypher Query]

    B2 --> C2

    C1 --> D1
    C2 --> D1

    D1[Hybrid Retrieval<br/>Vector + Graph] --> D2
    D2[Cross-Encoder Reranker<br/>ms-marco-MiniLM-L-6-v2] --> E
    E[Context Assembler<br/>Merge · Dedup · Cite] --> F

    F[LLM Answer Generator<br/>OpenAI / Local LLM]

🔧 Tech Stack
Component	Technology
Embeddings	BAAI/bge-m3
Vector DB	Qdrant (Docker)
Graph DB	Memgraph Platform (Docker)
Reranker	Cross-Encoder ms-marco-MiniLM-L-6-v2
LLM	OpenAI / local
Runtime	WSL2 (Ubuntu)
Orchestration	Docker Compose
UI (optional)	Streamlit
🔌 Quick Start
1. Start Vector + Graph Databases
docker-compose up -d

2. Run Notebook 01 (Chunking)

Clean and normalize text

Recursive splitter

Output: data/chunks.jsonl

3. Run Notebook 02 (Embedding + Qdrant)

Load BGE-M3

Normalize embeddings

Upload 1024-dim vectors to Qdrant

4. Run Notebook 03 (Hybrid Retrieval)

Query → embedding → Qdrant

Query → graph → Memgraph

Merge results

Rerank with cross-encoder

Produce final context + citations

📊 Evaluation

Evaluation script measures:

Semantic Retrieval F1

Hybrid Retrieval F1

Reranked F1 Improvement

🤝 Contributing

Pull requests welcome!
You can extend this project by adding:

LLM agents

Router models

Document classifiers

Metadata-aware chunking

Graph-augmented embeddings

📜 License

MIT License.
