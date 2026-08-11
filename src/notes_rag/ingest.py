from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import logging


logger = logging.getLogger(__name__)

SEPARATOR = re.compile(r"^\s*-{3,}\s*$", re.MULTILINE)
TAG_LINE = re.compile(r"^Tags:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
DATE_LINE = re.compile(
    r"^Date:\s*(\d{4}-\d{2}-\d{2})\s*$", re.IGNORECASE | re.MULTILINE
)


@dataclass
class Note:
    path: Path
    title: str
    description: str
    body: str
    tags: list[str]
    date: date | None = None


def parse_notes(path: Path):
    """Parse a note file into a Note object."""
    text = path.read_text(encoding="utf-8")
    parts = [p.strip() for p in SEPARATOR.split(text) if p.strip()]
    if len(parts) < 2:
        logger.warning("No Separator Found")
        return None

    title = path.stem
    defintition = parts[0]
    body = "\n\n".join(parts[1:])

    tags = []
    tag_match = TAG_LINE.search(body)
    if tag_match:
        tags = [t.strip() for t in tag_match.group(1).split(",") if t.strip()]
        body = TAG_LINE.sub("", body).strip()

    note_date = None
    date_match = DATE_LINE.search(body)
    if date_match:
        try:
            note_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"Malformed date in {path}, {date_match.group(1)}")
        body = DATE_LINE.sub("", body).strip()

    return Note(
        path=path,
        title=title,
        description=defintition,
        body=body,
        tags=tags,
        date=note_date,
    )


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
            logger.warning(f"Unable to parse file {md_file}", md_file, exc_info=True)
    return notes
