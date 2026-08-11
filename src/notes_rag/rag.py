import logging
from dataclasses import dataclass

import ollama

from notes_rag.config import Config
from notes_rag.vectorstore import query


logger = logging.getLogger(__name__)

DISTANCE_THRESHOLD = 0.8

NO_MATCH_MESSAGE = "Sorry, I couldn't find anything that answers your question."

SYSTEM_PROMPT = (
    "You are answering questions using only the note excerpts provided below. "
    "Do not use outside knowledge. If the excerpts don't fully answer the "
    "question, say what's missing rather than guessing or filling gaps."
)


@dataclass
class Source:
    title: str
    note_path: str
    kind: str
    date: str | None = None


@dataclass
class Answer:
    text: str
    sources: list[Source]
    matched: bool


def _format_date(raw: int) -> str:
    """Convert the stored YYYYMMDD int back to YYYY-MM-DD for display."""
    s = str(raw)
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}"


def _build_context(documents: list[str], metadata: list[dict]):
    blocks = []
    for doc, meta in zip(documents, metadata):
        date_str = f" — {_format_date(meta['date'])}" if meta.get("date") else ""
        blocks.append(f"[{meta['title']} - {meta['kind']}{date_str}]\n{doc}")
        return "\n\n---\n\n".join(blocks)


def _filter_by_distance(
    results: dict, threshold: float
) -> tuple[list[str], list[float]]:
    """Keep only the closest retrieved chunks."""
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    kept_docs, kept_meta = [], []
    for doc, meta, dist in zip(documents, metadatas, distances):
        if dist <= threshold:
            kept_docs.append(doc)
            kept_meta.append(meta)

        else:
            logger.info(f"Dropping chunk {meta['title']} ({dist} > {threshold})")

    return kept_docs, kept_meta


def answer_question(
    question: str,
    config: Config,
    tags: list[str] | None = None,
    date_from=None,
    date_to=None,
):
    results = query(question, config, tags=tags, date_from=date_from, date_to=date_to)
    print(results)

    if not results["documents"] or not results["documents"][0]:
        logger.info(f"No results returned for query {question}")
        return Answer(text=NO_MATCH_MESSAGE, sources=[], matched=False)

    documents, metadatas = _filter_by_distance(results, DISTANCE_THRESHOLD)

    if not documents:
        logger.info("All results were below threshold for query: '{question}'")
        return Answer(text=NO_MATCH_MESSAGE, sources=[], matched=False)

    context = _build_context(documents, metadatas)
    prompt = f"{SYSTEM_PROMPT}\n\nNote excerpts:\n{context}\n\nQuestion:{question}"

    logger.info(f"Generating answer from {len(documents)} chunks.")
    response = ollama.generate(model=config.llm_model, prompt=prompt)

    sources = [
        Source(
            title=m["title"],
            note_path=m["note_path"],
            kind=m["kind"],
            date=_format_date(m["date"]) if m.get("date") else None,
        )
        for m in metadatas
    ]

    return Answer(text=response.response, sources=sources, matched=True)
