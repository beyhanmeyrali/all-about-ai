# CrewAI Setup Guide for Windows

## ✅ Native Windows Installation

Good news! You can run CrewAI natively on Windows using Python 3.10, 3.11, or 3.12.

**⚠️ IMPORTANT:** Do NOT use Python 3.13 or 3.14 yet, as they lack pre-built wheels for key dependencies like `chromadb` and `tiktoken`.

### Prerequisites

1. **Python 3.11 or 3.12** installed
2. **Ollama** running (`ollama serve`)
3. **Qdrant** running in Docker (for memory/RAG features)

### Installation

1. Create a virtual environment:
   ```powershell
   py -3.12 -m venv .venv
   ```

2. Activate it:
   ```powershell
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```powershell
   pip install crewai crewai-tools langchain-ollama litellm
   ```

### Running Scripts

You can run any script directly with Python:

```powershell
python 00_crew_basics.py
```

**Note:** If you see emoji errors, set the encoding:
```powershell
$env:PYTHONUTF8=1; python 00_crew_basics.py
```

### Configuration

The scripts are configured to use **Ollama** locally:
- **Model:** `qwen3:4b` (via `ollama/qwen3:4b`)
- **Base URL:** `http://127.0.0.1:11434`

If you want to use OpenAI or other providers, modify the `LLM` configuration in the scripts.

### Troubleshooting

#### "ModuleNotFoundError: No module named 'crewai'"
Make sure you activated the virtual environment (`.venv\Scripts\activate`).

#### "UnicodeEncodeError: 'charmap' codec can't encode..."
Windows console issue with emojis. Run with `$env:PYTHONUTF8=1`.

#### "Model not found"
Ensure you have pulled the model in Ollama: `ollama pull qwen3:4b`
