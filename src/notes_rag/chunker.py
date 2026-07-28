from notes_rag.ingest import Note, SEPARATOR
import logging
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


def split_sections(body: str) -> list[str]:
    """Split body of text into smaller sections based on separator."""
    sections = [s.strip() for s in SEPARATOR.split(body) if s.strip()]
    return sections


def chunk_note(note: Note, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """Split text into chunks, ready to be embedded."""
    chunks = []

    if note.description:
        # Add description chunk
        chunks.append(
            Chunk(
                text=note.description,
                note_path=note.path,
                title=note.title,
                tags=None,
                kind="description",
                chunk_index=0,
            )
        )

    # for each body section split into chunks

    for i, section in enumerate(split_sections(note.body)):
        print(section)
        chunks.append(
            Chunk(
                text=section,
                note_path=note.path,
                title=note.title,
                tags=None,
                kind="body",
                chunk_index=i,
            )
        )

    logger.info(f"Chunked {note.path.name} into {len(chunks)} chunks")
    return chunks

