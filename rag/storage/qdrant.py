from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "aura_knowledge_base"


def init_qdrant(vector_size: int = 384):
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


def upsert_chunks(chunks: list[str], embeddings: list[list[float]], start_id: int = 0):
    points = [
        PointStruct(id=start_id + i, vector=emb, payload={"text": chunk})
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)


def search_qdrant(query_vector: list[float], top_k: int = 10) -> list[dict]:
    """
    Searches Qdrant for the closest vectors to the query using the modern API.
    """
    # Use the new query_points method instead of search
    results = client.query_points(
        collection_name=COLLECTION_NAME, query=query_vector, limit=top_k
    )

    # query_points returns a QueryResponse object containing a 'points' list
    hits = results.points if hasattr(results, "points") else results

    # Format the output to match what hybrid.py expects
    return [
        {"id": hit.id, "score": hit.score, "text": hit.payload.get("text", "")}
        for hit in hits
    ]
