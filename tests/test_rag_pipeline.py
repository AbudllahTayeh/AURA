import sys
import os

# Ensure the 'rag' module can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.ingestion.chunking import create_chunks
from rag.embeddings.embedder import get_embeddings
from rag.storage.qdrant import init_qdrant, upsert_chunks
from rag.retrieval.hybrid import retrieve_hybrid
from rag.retrieval.reranker import rerank_results

def test_full_pipeline():
    # 1. Create a dummy document
    sample_text = """
    Qdrant is an open-source vector database designed for fast and scalable similarity search.
    BM25 is a popular sparse retrieval algorithm based on TF-IDF.
    Reciprocal Rank Fusion (RRF) is a technique to combine multiple ranked lists.
    Cross-encoders are highly accurate but computationally expensive, making them ideal for the final reranking step in RAG systems.
    """
    
    print("--- 1. Chunking ---")
    chunks = create_chunks(sample_text, chunk_size=120, chunk_overlap=20)
    print(f"Created {len(chunks)} chunks.")

    print("\n--- 2. Embedding ---")
    embeddings = get_embeddings(chunks)
    print(f"Generated {len(embeddings)} embeddings of size {len(embeddings[0])}.")

    print("\n--- 3. Storage (Qdrant) ---")
    init_qdrant(vector_size=len(embeddings[0]))
    upsert_chunks(chunks, embeddings)
    print("Upserted chunks to Qdrant successfully.")

    print("\n--- 4. Hybrid Retrieval ---")
    query = "Why are cross-encoders used in RAG?"
    
    # In a real scenario, you'd fetch dense_results from Qdrant via `client.search` or `client.query_points`.
    # For this test, we'll mock the dense results, assuming chunk 3 (the cross-encoder sentence) scored highest.
    mock_dense_results = [
        {"id": 3, "score": 0.92},
        {"id": 2, "score": 0.65},
        {"id": 0, "score": 0.55}
    ]
    
    hybrid_results = retrieve_hybrid(query, chunks, mock_dense_results, top_k=3)
    for res in hybrid_results:
        print(f"ID: {res['id']} | RRF Score: {res['rrf_score']:.4f} | Text: {res['text'].strip()}")

    print("\n--- 5. Reranking ---")
    final_results = rerank_results(query, hybrid_results, top_k=1)
    print(f"\nFinal Best Match:\n{final_results[0]['text'].strip()}")
    print(f"Cross-Encoder Score (Logit): {final_results[0]['cross_encoder_score']:.4f}")

if __name__ == "__main__":
    test_full_pipeline()
