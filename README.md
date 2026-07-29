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