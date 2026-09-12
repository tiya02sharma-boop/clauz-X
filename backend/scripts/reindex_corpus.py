"""Script to re-index the Clauz X legal corpus into Chroma using Qwen3-Embedding-0.6B."""
import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend import config
from backend.storage import load
from backend.rag_assistant import index_legal_corpus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_reindexing() -> int:
    """Clear existing Chroma collection and re-index the legal corpus from source files."""
    config.ensure_storage()
    logger.info("Loading source corpus from: %s", config.LEGAL_CORPUS_PATH)
    items = load(config.LEGAL_CORPUS_PATH, [])
    logger.info("Found %d source documents to index.", len(items))

    if not items:
        logger.warning("No documents found in %s! Indexing 0 items.", config.LEGAL_CORPUS_PATH)
        return 0

    count = index_legal_corpus(items)
    logger.info("Successfully re-indexed %d documents into Chroma collection.", count)
    return count


if __name__ == "__main__":
    count = run_reindexing()
    print(f"Re-indexing complete: {count} items indexed into Chroma vector database.")
