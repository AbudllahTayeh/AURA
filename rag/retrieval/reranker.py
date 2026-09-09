from sentence_transformers import CrossEncoder

# Initialize the cross-encoder model
# 'cross-encoder/ms-marco-MiniLM-L-6-v2' is a standard, fast, and effective choice for RAG
model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query: str, retrieved_docs: list[dict], top_k: int = 3) -> list[dict]:
    """
    Re-ranks retrieved documents using a Cross-Encoder model.
    
    :param query: The original search query string.
    :param retrieved_docs: The output from hybrid.py (list of dicts with 'id' and 'text').
    :param top_k: The final number of documents to feed to the LLM context window.
    """
    if not retrieved_docs:
        return []

    # The CrossEncoder requires input as pairs: [[query, doc1], [query, doc2], ...]
    sentence_pairs = [[query, doc["text"]] for doc in retrieved_docs]
    
    # Predict relevance scores (these are raw logits, higher is better)
    scores = model.predict(sentence_pairs)
    
    # Attach the new scores to the original document dictionaries
    for i, doc in enumerate(retrieved_docs):
        doc["cross_encoder_score"] = float(scores[i])
        
    # Sort the documents by the cross-encoder score in descending order
    reranked_docs = sorted(retrieved_docs, key=lambda x: x["cross_encoder_score"], reverse=True)
    
    # Return only the absolute best chunks for the final agent context
    return reranked_docs[:top_k]
