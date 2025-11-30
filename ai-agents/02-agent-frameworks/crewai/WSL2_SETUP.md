# CrewAI Setup with WSL2 on Windows

## Why WSL2?

CrewAI uses ChromaDB for memory features, which requires C++ build tools that are difficult to install on native Windows. WSL2 provides a full Linux environment on Windows, making installation seamless and giving you access to all CrewAI features.

## Prerequisites

- Windows 10 version 2004+ or Windows 11
- Administrator access
- ~2 GB free disk space

## Quick Setup

### 1. Install WSL2

Open PowerShell as Administrator:

```powershell
wsl --install
```

This installs Ubuntu by default. **Restart your computer** when prompted.

### 2. Initial Ubuntu Setup

After restart, Ubuntu will open automatically:
- Create a username (lowercase, no spaces)
- Create a password (you won't see it as you type)

### 3. Update Ubuntu

```bash
sudo apt update && sudo apt upgrade -y
```

### 4. Install Python and Dependencies

```bash
# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install build tools (for ChromaDB)
sudo apt install build-essential -y
```

### 5. Install Ollama in WSL2

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama in background
ollama serve > /dev/null 2>&1 &

# Pull the model
ollama pull qwen3:8b
```

### 6. Navigate to Your Project

WSL2 can access Windows files via `/mnt/`:

```bash
# Navigate to your project (adjust drive letter if needed)
cd /mnt/d/workspace/all-about-ai/ai-agents/02-agent-frameworks/crewai
```

### 7. Create Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 8. Install CrewAI

```bash
pip install crewai crewai-tools langchain-ollama
```

### 9. Run Examples

```bash
python 01_simple_crew.py
```

🎉 **You're done!** All CrewAI features including memory will work perfectly.

---

## Alternative: Use Windows Ollama from WSL2

If you already have Ollama running on Windows, you can access it from WSL2:

### Find Your Windows IP

In WSL2:
```bash
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
```

This shows your Windows IP (usually `172.x.x.x`)

### Update Scripts

Modify the `base_url` in scripts:

```python
llm = ChatOllama(
    model="qwen3:8b",
    base_url="http://172.x.x.x:11434",  # Your Windows IP
    temperature=0.7
)
```

Or set environment variable:
```bash
export OLLAMA_HOST=http://$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):11434
```

---

## Tips & Tricks

### Access WSL2 from VS Code

1. Install "WSL" extension in VS Code
2. Open Command Palette (Ctrl+Shift+P)
3. Type "WSL: Connect to WSL"
4. Open your project folder

### Make Ollama Start Automatically

Add to `~/.bashrc`:

```bash
# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve > /dev/null 2>&1 &
fi
```

Then: `source ~/.bashrc`

### Better Performance: Clone Inside WSL2

For faster file access, clone the repo inside WSL2:

```bash
cd ~
git clone https://github.com/beyhanmeyrali/all-about-ai.git
cd all-about-ai/ai-agents/02-agent-frameworks/crewai
```

### File Permissions Issues

If you get permission errors:

```bash
sudo chown -R $USER:$USER /mnt/d/workspace/all-about-ai
```

---

## Troubleshooting

### "wsl --install" not found

**Solution:** Update Windows to latest version via Windows Update

### Ollama connection refused

**Solution:** Make sure Ollama is running:
```bash
ollama serve > /dev/null 2>&1 &
```

### ChromaDB installation fails

**Solution:** Install build tools:
```bash
sudo apt install build-essential python3-dev -y
```

### Slow file access via /mnt/

**Solution:** Clone the repository inside WSL2 instead of accessing Windows files

### WSL2 uses too much memory

**Solution:** Create `.wslconfig` in Windows user folder:
```
[wsl2]
memory=4GB
processors=2
```

---

## Verification

Test your setup:

```bash
# Check Python
python3 --version

# Check CrewAI
python3 -c "import crewai; print('CrewAI:', crewai.__version__)"

# Check Ollama
curl http://localhost:11434/api/tags

# Run a test script
python 00_crew_basics.py
```

All should work without errors! 🚀
