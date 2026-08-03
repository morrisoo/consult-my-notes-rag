import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass
class Config:
    notes_dir: Path
    storage_dir: Path
    llm_model: str
    embed_model: str
    chunk_size: int
    chunk_overlap: int
    top_k: int

    @classmethod
    def get_env_variables(cls):
        notes_dir = os.getenv("NOTES_DIR")
        if not notes_dir:
            raise ValueError(
                "Notes directory is not found. Specify it in your .env file."
            )

        notes_dir = Path(PROJECT_ROOT / notes_dir).expanduser().resolve()
        storage_dir = Path(PROJECT_ROOT / os.getenv("STORAGE_DIR", "./storage")).expanduser().resolve()
        llm_model = os.getenv("LLM_MODEL", "llama3.1")
        embed_model = os.getenv("EMBED_MODEL", "nomic-embed-text")
        chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
        chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "30"))
        top_k = int(os.getenv("TOP_K", "4"))

        return cls(
            notes_dir,
            storage_dir,
            llm_model,
            embed_model,
            chunk_size,
            chunk_overlap,
            top_k,
        )
