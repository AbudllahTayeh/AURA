from sentence_transformers import SentenceTransformer

# Initialize model once to keep it in memory
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embeddings(texts: list[str]) -> list[list[float]]:
    # Returns a list of vectors (dimension 384 for this model)
    return model.encode(texts).tolist()
