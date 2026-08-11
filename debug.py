from notes_rag.config import Config
from notes_rag.ingest import load_notes
from notes_rag.chunker import chunk_note
from notes_rag.vectorstore import index_notes
import logging
from notes_rag.rag import answer_question
from notes_rag.vectorstore import query
from datetime import date

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main():
    config = Config.get_env_variables()
    notes = load_notes(config.notes_dir)
    logger.info(f"Loaded {len(notes)} markdown files from {config.notes_dir}")

    chunks_by_note = {}
    for note in notes:
        chunks = chunk_note(
            note=note, chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
        )
        chunks_by_note[str(note.path)] = chunks

    total_chunks = sum(len(c) for c in chunks_by_note.values())
    logger.info(f"Produced {total_chunks} chunks")

    # index_notes(chunks_by_note, config)
    # logger.info("Indexed notes.")

    # question = "What did I write about bayesian inference?"
    # answer = answer_question(question, config)
    # print(f"\nQ: {question}")
    # print(f"\nA: {answer.text}")
    # if answer.sources:
    #     print("\nSources:")
    #     for s in answer.sources:
    #         print(f" - {s.title} ({s.kind})")

    raw_results = query("test", config, top_k=5)
    print("\n--- Raw retrieval (no filters) ---")
    for meta, dist in zip(raw_results["metadatas"][0], raw_results["distances"][0]):
        print(f"  {meta.get('title')} ({meta.get('kind')}) - date={meta.get('date')} - distance={dist:.4f}")
        


if __name__ == "__main__":
    main()
