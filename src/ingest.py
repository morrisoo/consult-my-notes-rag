import re
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

SEPARATOR = "-------"
TAG_LINE = re.compile(r"^Tags:\s*(.+)$", re.IGNORECASE | re.MULTILINE)


@dataclass
class Note:
    path: Path
    title: str
    definition: str
    body: str
    tags: str


def parse_notes(path: Path):
    """Parse a note file into a Note object."""
    text = path.read_text(encoding="utf-8")
    parts = text.split(SEPARATOR)

    title = path.stem
    defintition = parts[0].strip()
    body = parts[1].strip()

    return Note(path=path, title=title, definition=defintition, body=body, tags=None)


def load_notes(notes_dir: Path):
    """Load and parse all notes from data source."""
    notes = []
    for md_file in sorted(notes_dir.rglob("*.md")):
        logger.info(f"Reading file {md_file}.")
        try:
            text = parse_notes(md_file)
            if text is not None:
                notes.append(text)
        except Exception:
            logger.info(Warning, f"Unable to parse file {md_file}")
    return notes

