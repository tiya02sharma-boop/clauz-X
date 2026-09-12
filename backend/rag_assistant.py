"""Semantic retrieval layer for Ask Clauz X using Chroma and Qwen3-Embedding-0.6B."""
import json
import logging
import re
from typing import Any
import chromadb
from . import config
from .embeddings import embed_texts, DEFAULT_EMBEDDING_DIM, DEFAULT_TASK_INSTRUCTION
from .storage import load

logger = logging.getLogger(__name__)

DOMAIN_TERMS = {
    "gst", "gstr", "tax", "tds", "mca", "roc", "company", "director", "directors",
    "esi", "esic", "pf", "epf", "msme", "msmed", "filing", "return", "registration",
    "compliance", "penalty", "due", "deadline", "board", "meeting", "meetings",
    "pvt", "ltd", "quarterly", "agm", "egm", "quorum", "secretarial", "audit", "llp", "statutory"
}

COLLECTION_NAME = "clauz_legal_corpus"
QUERY_INSTRUCTION = "Instruct: Given an Indian compliance query, retrieve relevant legal sections and rules that answer the query\nQuery:"
DOCUMENT_INSTRUCTION = DEFAULT_TASK_INSTRUCTION

# Maximum cosine distance (1 - cosine_similarity) to consider a passage relevant
# Qwen3 cosine distances for relevant queries are typically 0.20-0.45; irrelevant ones > 0.55
MAX_RELEVANCE_DISTANCE = 0.50

_CHROMA_CLIENT = None


def get_chroma_client() -> chromadb.PersistentClient:
    """Return a singleton Chroma persistent client."""
    global _CHROMA_CLIENT
    if _CHROMA_CLIENT is None:
        config.ensure_storage()
        _CHROMA_CLIENT = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    return _CHROMA_CLIENT


def get_corpus_collection():
    """Retrieve or create the legal corpus Chroma collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def is_compliance_question(question: str) -> bool:
    """Check if the question pertains to compliance and Indian business regulations."""
    return bool(_tokens(question) & DOMAIN_TERMS)


def format_chunk_text(item: dict[str, Any]) -> str:
    """Prepare chunk text for embedding."""
    title = item.get("title", "")
    citation = item.get("citation", "")
    text = item.get("text", "")
    return f"{title}\nCitation: {citation}\nText: {text}".strip()


def index_legal_corpus(items: list[dict[str, Any]] | None = None) -> int:
    """Clear existing collection and re-index corpus documents into Chroma using embed_texts()."""
    client = get_chroma_client()
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    if items is None:
        items = load(config.LEGAL_CORPUS_PATH, [])

    if not items:
        return 0

    ids = [item["id"] for item in items]
    docs = [format_chunk_text(item) for item in items]
    metadatas = [
        {
            "id": item["id"],
            "title": str(item.get("title", "")),
            "citation": str(item.get("citation", "")),
            "source_url": str(item.get("source_url", "")),
            "tags": json.dumps(item.get("tags", [])),
            "text": str(item.get("text", "")),
        }
        for item in items
    ]

    embeddings = embed_texts(
        docs,
        task_instruction=DOCUMENT_INSTRUCTION,
        dimension=config.EMBEDDING_DIM,
    )

    collection.add(
        ids=ids,
        documents=docs,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    logger.info("Indexed %d documents into Chroma collection '%s'.", len(items), COLLECTION_NAME)
    return len(items)


def retrieve(question: str, limit: int = 3) -> list[dict[str, Any]]:
    """Retrieve relevant legal passages from Chroma vector database using Qwen3 embeddings."""
    collection = get_corpus_collection()
    if collection.count() == 0:
        # If collection is empty, trigger initial indexing from source file
        index_legal_corpus()
        collection = get_corpus_collection()
        if collection.count() == 0:
            return []

    # Query embedding using the same embed_texts code path
    query_vectors = embed_texts(
        [question],
        task_instruction=QUERY_INSTRUCTION,
        dimension=config.EMBEDDING_DIM,
    )
    if not query_vectors:
        return []

    n_results = min(limit, collection.count())
    results = collection.query(
        query_embeddings=query_vectors,
        n_results=n_results,
        include=["metadatas", "distances", "documents"]
    )

    if not results or not results.get("metadatas") or not results["metadatas"][0]:
        return []

    passages: list[dict[str, Any]] = []
    matched_metas = results["metadatas"][0]
    matched_dists = results["distances"][0]
    matched_docs = results["documents"][0] if results.get("documents") else []

    for idx, (meta, dist) in enumerate(zip(matched_metas, matched_dists)):
        if dist > MAX_RELEVANCE_DISTANCE:
            # Below relevance cutoff
            continue

        tags_raw = meta.get("tags", "[]")
        try:
            tags = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw
        except Exception:
            tags = []

        passages.append({
            "id": meta.get("id"),
            "title": meta.get("title", ""),
            "citation": meta.get("citation", ""),
            "source_url": meta.get("source_url", ""),
            "tags": tags,
            "text": meta.get("text") or (matched_docs[idx] if idx < len(matched_docs) else ""),
            "score": round(1.0 - dist, 4),
        })

    return passages
