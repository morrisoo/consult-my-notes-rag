## Consult My Notes 
A local, private RAG (retrieval-augmented generation) tool for asking questions about your own markdown notes. The workflow runs entirely offline, using Ollama for embeddings and generation and ChromaDB fofor the vector store. Nothing leaves your machine and no API keys are needed.

Ask a questions, get an answer based on what you have written, with source citations, or nothing if your notes can't answer the question.


## Project Structure
```
.
├── app.py                                  # Streamlit UI, entrypoint                               
├── data                                           
│   └── sample_notes/                       # Fake sample notes for illustrative purposes
├── debug.py                                # Manual load -> chunk -> index -> query
├── LICENSE
├── pyproject.toml
├── README.md
├── src
│   └── notes_rag
│       ├── __init__.py
│       ├── chunker.py                      # Splits notes into embeddable chunks
│       ├── config.py                       # Reads .env file and creates Config dataclass
│       ├── ingest.py                       # Parses .md files into Note objects
│       ├── rag.py                          # Retrieval and generation
│       └── vectorstore.py                  # Stores Ollama embeddings in ChromaDB vectorstore
├── .streamlit/                                           
│   └── sample_notes                        # Fake sample notes for illustrative purposes
├── .env.template                           # UI theme        
└── uv.lock
```


## Prerequisites

This project uses [Ollama](https://ollama.com) to run embeddings and generation
locally. 

### 1. Install Ollama

- **macOS:** `brew install ollama`, or download the `.dmg` from [ollama.com](https://ollama.com)
- **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`
- **Windows:** download the installer from [ollama.com](https://ollama.com)


### 2. Start the Ollama server

**If installed via the `.dmg` app:** it runs in the background automatically.

**If installed via Homebrew:** it does *not* start automatically, run:

```bash
brew services start ollama
```

This starts Ollama now and keeps it running across logins. Alternatively,
run it manually per-session with `ollama serve` in its own terminal. To stop it running, run:

```bash
brew services stop ollama
```

**Linux:** same as above, `ollama serve`, or set it up as a systemd service
if you want it persistent.

Verify the install:

```bash
ollama --version
```

### 3. Pull the required models

This project expects an embedding model and a generation model, configured
via `.env` (see `.env.example`):

```bash
ollama pull nomic-embed-text   # embedding model — match EMBED_MODEL in .env
ollama pull llama3.1           # generation model — match LLM_MODEL in .env
```



## Setup
Clone the repo, then install dependencies with uv:
```
uv sync
```
Copy the example environment file and fill in your notes directory:
```
cp .env.example .env
```
The `NOTES_DIR` must point at a folder of `.md` files, either your real notes or `data/sample_notes/`.


## Usage
### Run the app:
```
uv run streamlit run app.py
```
Click **Re-index notes** in the sidebar the first time, or any time that your notes change, then ask a question.

Or run the debug script to run the workflow and print the results to the terminal to troubleshoot.


## Note Format
Notes are plain Markdown files. The **title** comes from the filename, rather than the file's contents. The rest of the file has three parts:

```
A one or two sentence description of the note. This gets embedded and
searched on its own.

---

The main body of the note. This can be as long as you like.

Date: 2026-07-08
Tags: meetings, design, onboarding
```

The `---` separator (three or more dashes) splits the description from the body. This is required. A note without a description is skipped with a warning.

Both the `Date:` and `Tag:` descriptors are optional. A note without a date won't match a date filter, and notes without tags wont appear under any tag filter.

See `data/sample_notes/` for complete working examples.


