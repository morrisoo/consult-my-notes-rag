import logging
import streamlit as st

from notes_rag.chunker import chunk_note
from notes_rag.config import Config
from notes_rag.ingest import load_notes
from notes_rag.rag import answer_question
from notes_rag.vectorstore import index_notes, get_all_tags


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@st.cache_resource
def get_config() -> Config:
    return Config.get_env_variables()


def run_indexing(config: Config) -> tuple[int, int]:
    """Load, chunk and index all notes."""
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

    index_notes(chunks_by_note, config)
    logger.info(f"Indexed {len(notes)} notes.")

    return len(notes), total_chunks


def main():
    st.set_page_config(page_title="My Notes", layout="wide", page_icon="📝")
    st.title("Consult My Notes 📝")
    config = get_config()

    css = """.st-key-title_container {background-color: #FFE7E6;}"""
    st.html(f"<style>{css}</style>")

    with st.container(border=True, key="title_container"):
        st.markdown("This is a chatbot! Ask me **anything** about your linked data.")
        st.markdown(
            "This example compiles artifical meeting notes about a project over several weeks."
        )

    if st.button("Refresh Notes"):
        with st.spinner("Loading, chunking and embedding notes..."):
            try:
                note_count, chunk_count = run_indexing(config)
                st.success(
                    f"Indexed {note_count} notes ({chunk_count} chunks). You're up to date."
                )
            except Exception:
                logger.exception("Indexing failed")

    try:
        available_tags = get_all_tags(config)
    except Exception:
        logger.exception("Could not load tags.")
        available_tags = []

    with st.sidebar:
        selected_tags = st.multiselect(options=available_tags, label="Filter by tag:")

        use_date_filter = st.checkbox("Filter by date range")
        date_from, date_to = None, None
        if use_date_filter:
            col1, col2 = st.columns(2)
            with col1:
                date_from = st.date_input("From")
            with col2:
                date_to = st.date_input("To")

    question = st.text_input("Ask something from your notes:")

    if question:
        with st.spinner("Thinking..."):
            try:
                result = answer_question(
                    question,
                    config,
                    tags=selected_tags or None,
                    date_from=date_from,
                    date_to=date_to,
                )
            except Exception:
                logger.exception("Could not answer question, something went wrong.")
                st.error("Something went wrong.")
                return

            st.markdown(result.text)

        if result.sources:
            st.subheader("Sources")
            for source in result.sources:
                date_str = f" — {source.date}" if source.date else ""
                st.caption(f"**{source.title}** ({source.kind}{date_str} - {source.note_path})")


if __name__ == "__main__":
    main()
