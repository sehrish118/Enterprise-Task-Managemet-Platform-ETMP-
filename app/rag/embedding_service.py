# app/rag/embedding_service.py
"""
Wraps SentenceTransformers so the model is loaded ONCE per worker process
(not once per task) — loading the model on every task call would be very
slow and wasteful.
"""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.logging import get_logger

logger = get_logger(__name__)

# Must match EMBEDDING_DIM (384) in app/models/document_embedding.py.
# If you ever change this model, you MUST also change EMBEDDING_DIM there
# and write a migration to alter the vector column's dimension.
MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    logger.info(f"Loading embedding model: {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """
    Converts a piece of text into a 384-dim vector.
    Empty/whitespace-only text raises — callers should guard against
    embedding empty content (e.g. an empty comment).
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate an embedding for empty text.")

    model = get_embedding_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()
