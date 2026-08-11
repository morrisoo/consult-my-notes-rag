from notes_rag.ingest import Note, SEPARATOR
import logging
from datetime import date
from dataclasses import dataclass
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    text: str
    note_path: Path
    title: str
    tags: list[str]
    kind: str
    chunk_index: int
    date: date | None 


def split_sections(body: str) -> list[str]:
    """Split body of text into smaller sections based on separator."""
    sections = [s.strip() for s in SEPARATOR.split(body) if s.strip()]
    return sections


def chunk_note(note: Note, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """Split text into chunks, ready to be embedded."""
    chunks = []

    if note.description:
        chunks.append(
            Chunk(
                text=note.description,
                note_path=note.path,
                title=note.title,
                tags=note.tags,
                kind="description",
                chunk_index=0,
                date=note.date,
            )
        )

    for i, section in enumerate(split_sections(note.body)):
        chunks.append(
            Chunk(
                text=section,
                note_path=note.path,
                title=note.title,
                tags=note.tags,
                kind="body",
                chunk_index=i,
                date=note.date,
            )
        )

    logger.info(f"Chunked {note.path.name} into {len(chunks)} chunks")
    return chunks
