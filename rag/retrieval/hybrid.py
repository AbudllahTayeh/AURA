from rank_bm25 import BM25Okapi

def retrieve_hybrid(query: str, corpus_chunks: list[str], dense_results: list[dict], top_k: int = 5, rrf_k: int = 60):
    """
    Combines dense and sparse retrieval using Reciprocal Rank Fusion (RRF).
    
    :param query: The search query string.
    :param corpus_chunks: A list of all text chunks (used for BM25).
    :param dense_results: A sorted list of dicts from Qdrant, e.g., [{"id": 0, "score": 0.95}, {"id": 4, "score": 0.88}]
    :param top_k: The number of final fused documents to return.
    :param rrf_k: The smoothing constant for RRF (typically set to 60).
    """
    
    # 1. Sparse Retrieval (BM25)
    tokenized_corpus = [doc.split(" ") for doc in corpus_chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.split(" ")
    sparse_scores = bm25.get_scores(tokenized_query)
    
    # Sort sparse results to get rankings (highest score first)
    # This creates a list of chunk indices ordered by their BM25 score
    sparse_ranked_indices = sorted(range(len(sparse_scores)), key=lambda i: sparse_scores[i], reverse=True)
    
    # Map each chunk index to its rank (1-indexed)
    sparse_ranks = {chunk_idx: rank for rank, chunk_idx in enumerate(sparse_ranked_indices, start=1)}
    
    # 2. Dense Retrieval (Qdrant)
    # Assuming dense_results is already sorted descending by Qdrant's similarity score
    dense_ranks = {result["id"]: rank for rank, result in enumerate(dense_results, start=1)}

    # 3. Reciprocal Rank Fusion (RRF)
    rrf_scores = {}
    
    # Get a unique set of all document IDs retrieved by either method
    all_indices = set(sparse_ranks.keys()).union(set(dense_ranks.keys()))
    
    for chunk_idx in all_indices:
        score = 0.0
        
        # Add the sparse rank contribution
        if chunk_idx in sparse_ranks:
            score += 1.0 / (rrf_k + sparse_ranks[chunk_idx])
            
        # Add the dense rank contribution
        if chunk_idx in dense_ranks:
            score += 1.0 / (rrf_k + dense_ranks[chunk_idx])
            
        rrf_scores[chunk_idx] = score

    # 4. Sort documents by final RRF score in descending order
    ranked_fused_indices = sorted(rrf_scores.keys(), key=lambda idx: rrf_scores[idx], reverse=True)
    
    # Format and return the top_k results
    final_results = [
        {
            "id": idx,
            "text": corpus_chunks[idx],
            "rrf_score": rrf_scores[idx]
        }
        for idx in ranked_fused_indices[:top_k]
    ]
    
    return final_results
