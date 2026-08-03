from notes_rag.chunker import Chunk
from notes_rag.config import Config
from chromadb import PersistentClient
from ollama import embeddings
import logging

logger = logging.getLogger(__name__)
COLLECTION_NAME = "my_notes"


def make_chunk_id(chunk: Chunk) -> str:
    return f"{chunk.note_path}::{chunk.kind}::{chunk.chunk_index}"


def tag_key(tag: str) -> str:
    """Turn a tag into a metadata field name"""
    return f"tag_{tag.strip().lower().replace(' ', '-')}"


def note_id_prex(note_path: str) -> str:
    return f"{note_path}::"


def get_client(config: Config):
    """Writes index to disk."""
    return PersistentClient(path=str(config.storage_dir))


def get_collection(config: Config):
    """Reopen or create collection."""
    client = get_client(config)
    return client.get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def embed_text(text: str, config: Config) -> list[float]:
    """Embed text using Ollama."""
    response = embeddings(model=config.embed_model, prompt=text)
    return response["embedding"]


def embed_chunks(chunks: list[Chunk], config: Config) -> list[list[float]]:
    """Embed our chunks."""
    embeddings = []
    for i, chunk in enumerate(chunks):
        logger.info(f"Embedding chunk {i + 1}/{len(chunks)} ({chunk.title}).")
        embeddings.append(embed_text(chunk.text, config))
    return embeddings


def delete_note_chunks(note_path: str, collection) -> None:
    """Delete a note's stale chunks."""
    existing = collection.get(where={"note_path": str(note_path)})
    ids = existing.get("ids", [])
    if ids:
        logger.info(f"Deleting {len(ids)} stale chunk(s) for {note_path}")
        collection.delete(ids=ids)


def upsert_chunks(chunks: list[Chunk], config: Config, collection) -> None:
    """Upsert chunks to collection."""
    if not chunks:
        return

    ids = [make_chunk_id(c) for c in chunks]
    documents = [c.text for c in chunks]
    metadata = []
    for c in chunks:
        meta = {
            "note_path": str(c.note_path),
            "title": c.title,
            "tags": ", ".join(c.tags),
            "kind": c.kind,
            "chunk_index": c.chunk_index,
        }
        for tag in c.tags:
            meta[tag_key(tag)] = True
        metadata.append(meta)
    embeddings = embed_chunks(chunks, config)

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadata,
    )
    logger.info(f"Upserted {len(chunks)}")


def index_notes(chunks_by_note: dict[str, list[Chunk]], config: Config) -> None:
    """Reindex notes by deleting and upserting."""
    collection = get_collection(config)
    for note_path, chunks in chunks_by_note.items():
        delete_note_chunks(note_path, collection)
        upsert_chunks(chunks, config, collection)


def query(
    text: str, config: Config, top_k: int | None = None, tags: list[str] | None = None
) -> dict:
    """Query collection with embedded input."""
    collection = get_collection(config)
    embedding = embed_text(text, config)

    where = None
    if tags:
        conditions = [{tag_key(t): True} for t in tags]
        where = conditions[0] if len(conditions) == 1 else {"$and": conditions}

    return collection.query(
        query_embeddings=[embedding], n_results=top_k or config.top_k, where=where
    )


def get_all_tags(config: Config) -> list[str]:
    """Return every distinct tag in the index, sorted"""
    collection = get_collection(config)
    all_chunks = collection.get()
    metadatas = all_chunks.get("metadatas", [])

    tags = set()
    for meta in metadatas:
        raw = meta.get("tags", "")
        tags.update(t.strip() for t in raw.split(",") if t.strip())

    return sorted(tags)
