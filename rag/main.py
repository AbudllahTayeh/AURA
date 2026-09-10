import os
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from rag.embeddings.embedder import get_embeddings
from rag.ingestion.chunking import create_chunks

# Import your RAG modules
from rag.ingestion.parsers import parse_pdf
from rag.retrieval.hybrid import retrieve_hybrid
from rag.retrieval.reranker import rerank_results
from rag.storage.postgres import (
    get_all_chunks,
    get_next_qdrant_id,
    init_postgres,
    insert_chunks,
    insert_document,
)
from rag.storage.qdrant import init_qdrant, search_qdrant, upsert_chunks

app = FastAPI(title="AURA RAG Agent API")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag-agent"}


# Initialize Qdrant and Postgres on startup
@app.on_event("startup")
def startup_event():
    init_postgres()
    init_qdrant(vector_size=384)


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


@app.post("/api/v1/ingest")
async def ingest_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Only PDF files are supported currently."
        )

    # 1. Save uploaded file to a temporary location for PyMuPDF to read
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # 2. Parse the PDF
        raw_text = parse_pdf(tmp_path)

        # 3. Chunk the text
        chunks = create_chunks(raw_text, chunk_size=500, chunk_overlap=50)

        # 4. Save metadata and chunks to Postgres
        doc_id = insert_document(file.filename)
        start_id = get_next_qdrant_id()
        insert_chunks(doc_id, start_id, chunks)

        # 5. Embed the chunks
        embeddings = get_embeddings(chunks)

        # 6. Upsert to Qdrant (using the synchronized start_id)
        upsert_chunks(chunks, embeddings, start_id=start_id)

    finally:
        # Clean up the temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_processed": len(chunks),
    }


@app.post("/api/v1/retrieve")
async def retrieve_context(request: QueryRequest):
    # 1. Fetch the persistent corpus from Postgres
    corpus = get_all_chunks()

    if not corpus:
        raise HTTPException(
            status_code=400, detail="Corpus is empty. Please ingest a document first."
        )

    # 2. Embed query
    query_vector = get_embeddings([request.query])[0]

    # 3. Run Qdrant search
    dense_results = search_qdrant(query_vector, top_k=10)

    # 4. Run BM25 + RRF (Hybrid Retrieval)
    hybrid_results = retrieve_hybrid(
        query=request.query, corpus_chunks=corpus, dense_results=dense_results, top_k=5
    )

    # 5. Run Cross-Encoder (Reranking)
    final_results = rerank_results(
        query=request.query, retrieved_docs=hybrid_results, top_k=request.top_k
    )

    return {"results": final_results}
