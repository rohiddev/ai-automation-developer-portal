"""Swappable retrieval backend for IDP knowledge, templates, and policies."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config import Settings, get_settings

_KNOWLEDGE_STORE: list[dict[str, Any]] = []


def _load_mock_data() -> list[dict[str, Any]]:
    global _KNOWLEDGE_STORE
    if _KNOWLEDGE_STORE:
        return _KNOWLEDGE_STORE
    data_dir = Path(__file__).resolve().parent.parent / "data" / "templates"
    records: list[dict[str, Any]] = []
    for path in sorted(data_dir.glob("*.yaml")):
        records.append(
            {
                "id": path.stem,
                "type": "template",
                "title": path.stem.replace("_", " ").title(),
                "content": path.read_text(),
                "source": str(path),
            }
        )
    _KNOWLEDGE_STORE = records
    return records


def search_knowledge(
    query: str, top_k: int = 5, settings: Settings | None = None
) -> list[dict[str, Any]]:
    """Return the most relevant knowledge records for a query."""
    settings = settings or get_settings()
    if settings.retrieval_backend == "mock":
        return _mock_search(query, top_k)
    return _vertex_search(query, top_k, settings)


def _mock_search(query: str, top_k: int) -> list[dict[str, Any]]:
    terms = set(query.lower().split())
    records = _load_mock_data()
    scored = []
    for record in records:
        text = f"{record.get('title', '')} {record.get('content', '')}".lower()
        score = sum(1 for term in terms if term in text)
        if score:
            scored.append((score, record))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [record for _, record in scored[:top_k]]


def _vertex_search(query: str, top_k: int, settings: Settings) -> list[dict[str, Any]]:
    # Placeholder for Vertex AI Search integration.
    raise NotImplementedError("Vertex AI Search backend not yet implemented")
