from notes_rag.config import Config
from notes_rag.ingest import load_notes
from notes_rag.chunker import chunk_note
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main():
    config = Config.get_env_variables()
    notes = load_notes(config.notes_dir)
    logger.info(f"Loaded {len(notes)} markdown files from {config.notes_dir}")

    chunks = []
    for note in notes:
        chunks.extend(
            chunk_note(
                note=note,
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
            )
        )
    logger.info(f"Produced {len(chunks)} chunks")


if __name__ == "__main__":
    main()
