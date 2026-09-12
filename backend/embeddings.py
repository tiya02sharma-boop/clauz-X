"""Shared embedding utility module for Clauz X using Qwen/Qwen3-Embedding-0.6B."""
import logging
from typing import Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Deployment mode: Self-hosted (in-process)
# Model is loaded directly in-process via sentence-transformers without per-token/network cost.
MODEL_NAME: str = "Qwen/Qwen3-Embedding-0.6B"

# Default Matryoshka dimension (Qwen3 supports 32–1024, default 768 balances quality and storage)
DEFAULT_EMBEDDING_DIM: int = 768

# Default instruction prefix for compliance/tax document representation
DEFAULT_TASK_INSTRUCTION: str = "Represent this Indian tax/compliance document for retrieval:"

# Load model ONCE at module import time
logger.info("Loading embedding model %s ...", MODEL_NAME)
_MODEL: SentenceTransformer = SentenceTransformer(MODEL_NAME)
logger.info("Embedding model %s loaded successfully.", MODEL_NAME)


def get_embedding_model() -> SentenceTransformer:
    """Return the globally loaded SentenceTransformer model instance."""
    return _MODEL


def embed_texts(
    texts: list[str],
    task_instruction: Optional[str] = DEFAULT_TASK_INSTRUCTION,
    dimension: int = DEFAULT_EMBEDDING_DIM,
) -> list[list[float]]:
    """Generate normalized semantic embeddings for a list of texts using Qwen3-Embedding-0.6B.

    Args:
        texts: List of text strings to embed.
        task_instruction: Optional instruction prefix (e.g. for retrieval queries or documents).
                         If None or empty string, no prompt is prepended.
        dimension: Desired embedding dimension (Matryoshka representation, 32 to 1024, default 768).

    Returns:
        A list of embedding vectors, each represented as a list of Python floats.
    """
    if not texts:
        return []

    # Encode with prompt instruction and Matryoshka dimension truncation
    encode_kwargs = {
        "truncate_dim": dimension,
        "normalize_embeddings": True,
        "show_progress_bar": False,
    }
    if task_instruction and task_instruction.strip():
        encode_kwargs["prompt"] = task_instruction.strip() + " "

    embeddings = _MODEL.encode(texts, **encode_kwargs)
    return embeddings.tolist()
