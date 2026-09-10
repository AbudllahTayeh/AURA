from langchain_core.tools import tool

from rag.embeddings.embedder import get_embeddings
from rag.retrieval.hybrid import retrieve_hybrid
from rag.retrieval.reranker import rerank_results
from rag.storage.postgres import get_all_chunks
from rag.storage.qdrant import search_qdrant


@tool
def query_knowledge_base(query: str, top_k: int = 3) -> str:
    """
    Searches the AURA Knowledge Base using hybrid retrieval (Dense + BM25) and
    Cross-Encoder reranking to find the most relevant document chunks for a given query.

    Args:
        query: The natural language question or search prompt.
        top_k: The number of final best matching chunks to return.
    """
    # 1. Fetch the persistent corpus from Postgres
    corpus = get_all_chunks()
    if not corpus:
        return "The knowledge base is currently empty. Please ingest documents first."

    try:
        # 2. Embed the query
        query_vector = get_embeddings([query])[0]

        # 3. Run Qdrant dense search
        dense_results = search_qdrant(query_vector, top_k=10)

        # 4. Run BM25 + RRF (Hybrid Retrieval)
        hybrid_results = retrieve_hybrid(
            query=query,
            corpus_chunks=corpus,
            dense_results=dense_results,
            top_k=max(5, top_k * 2),
        )

        # 5. Run Cross-Encoder (Reranking)
        final_results = rerank_results(
            query=query, retrieved_docs=hybrid_results, top_k=top_k
        )

        if not final_results:
            return "No relevant context found in the knowledge base."

        # 6. Format the chunks cleanly into a string response for the agent
        formatted_context = ""
        # Line 53
        for i, doc in enumerate(final_results, 1):
            formatted_context += (
                f"[Chunk {i}] (Score: {doc.get('cross_encoder_score', 0):.4f})\n"
                f"{doc['text'].strip()}\n\n"
            )
        return formatted_context

    except Exception as e:
        return f"Error querying knowledge base: {str(e)}"
