import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

# Import your RAG modules
from rag.ingestion.parsers import parse_pdf
from rag.ingestion.chunking import create_chunks
from rag.embeddings.embedder import get_embeddings
from rag.storage.qdrant import init_qdrant, upsert_chunks, search_qdrant
from rag.retrieval.hybrid import retrieve_hybrid
from rag.retrieval.reranker import rerank_results

app = FastAPI(title="AURA RAG Agent API")

# Initialize Qdrant on startup
@app.on_event("startup")
def startup_event():
    init_qdrant(vector_size=384)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

# Temporary in-memory store for BM25 corpus (Replace with Postgres later)
global_corpus = []

@app.post("/api/v1/ingest")
async def ingest_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported currently.")

    # 1. Save uploaded file to a temporary location for PyMuPDF to read
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # 2. Parse the PDF
        raw_text = parse_pdf(tmp_path)
        
        # 3. Chunk the text
        chunks = create_chunks(raw_text, chunk_size=500, chunk_overlap=50)
        global_corpus.extend(chunks) # Add to our BM25 corpus

        # 4. Embed the chunks
        embeddings = get_embeddings(chunks)

        # 5. Upsert to Qdrant
        # (Using len(global_corpus) - len(chunks) to generate unique sequential IDs)
        start_id = len(global_corpus) - len(chunks)
        upsert_chunks(chunks, embeddings, start_id=start_id)

    finally:
        # Clean up the temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {
        "status": "success", 
        "filename": file.filename, 
        "chunks_processed": len(chunks)
    }

@app.post("/api/v1/retrieve")
async def retrieve_context(request: QueryRequest):
    if not global_corpus:
        raise HTTPException(status_code=400, detail="Corpus is empty. Please ingest a document first.")

    # 1. Embed query
    query_vector = get_embeddings([request.query])[0]

    # 2. Run Qdrant search
    dense_results = search_qdrant(query_vector, top_k=10)

    # 3. Run BM25 + RRF (Hybrid Retrieval)
    hybrid_results = retrieve_hybrid(
        query=request.query, 
        corpus_chunks=global_corpus, 
        dense_results=dense_results, 
        top_k=5
    )

    # 4. Run Cross-Encoder (Reranking)
    final_results = rerank_results(
        query=request.query, 
        retrieved_docs=hybrid_results, 
        top_k=request.top_k
    )

    return {"results": final_results}
