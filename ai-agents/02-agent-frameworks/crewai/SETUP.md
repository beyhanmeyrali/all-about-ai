# CrewAI Setup Guide for Windows

## 🚨 Windows Installation Challenge

CrewAI has dependencies (`chromadb`, `regex`, `tiktoken`) that require C++ compilation, which often fails on Windows due to missing build tools.

## ✅ Solution: Docker-Based Approach

We've created a Docker-based setup that allows you to run CrewAI scripts on Windows without installation issues.

### Prerequisites

1. **Docker Desktop** installed and running
2. **Ollama** running on your host machine (not in Docker)
3. Models pulled: `ollama pull qwen3:8b`

### Quick Start

#### Option 1: Using the PowerShell Helper Script (Recommended)

```powershell
# Run any CrewAI script
.\run-crew.ps1 00_crew_basics.py

# Run a different script
.\run-crew.ps1 03_hierarchical_crew.py
```

The script will automatically:
- Build the Docker image on first run
- Mount the current directory
- Connect to your host's Ollama instance
- Execute the script and show results

#### Option 2: Manual Docker Commands

```powershell
# Build the image (first time only)
docker build -t crewai-runner .

# Run a script
docker run --rm `
    --add-host=host.docker.internal:host-gateway `
    -v "${PWD}:/app" `
    crewai-runner python 00_crew_basics.py
```

### How It Works

1. **Dockerfile**: Creates a Linux container with Python 3.11 and all CrewAI dependencies
2. **host.docker.internal**: Special DNS name that resolves to your host machine's IP
3. **Volume Mount**: Your scripts are mounted into the container, so changes are reflected immediately
4. **No Rebuild Needed**: After the initial build, you can modify scripts and run them without rebuilding

### Available Scripts

All scripts are configured to work with local Ollama:

- `00_crew_basics.py` - Introduction to Agents, Tasks, and Crews
- `01_simple_crew.py` - Two-agent collaboration (Researcher + Writer)
- `03_hierarchical_crew.py` - Manager delegating to workers
- `04_tools_in_crew.py` - Agents using custom tools
- `05_memory_crew.py` - Crew memory systems
- `06_delegation.py` - Agent delegation patterns
- `07_production_crew.py` - Complete content creation studio

### Troubleshooting

#### Docker Not Running
```
Error: cannot connect to Docker daemon
```
**Solution**: Start Docker Desktop

#### Ollama Not Accessible
```
Error: Connection refused to host.docker.internal:11434
```
**Solution**: 
- Ensure Ollama is running: `ollama serve`
- Verify it's accessible: `curl http://localhost:11434/api/tags`

#### Model Not Found
```
Error: model 'qwen3:8b' not found
```
**Solution**: Pull the model: `ollama pull qwen3:8b`

### Alternative: Native Windows Installation (Advanced)

If you want to install CrewAI natively on Windows:

1. **Install Visual Studio Build Tools**:
   - Download from: https://visualstudio.microsoft.com/downloads/
   - Select "Desktop development with C++"
   - Install (requires ~7GB)

2. **Install CrewAI**:
   ```powershell
   pip install crewai crewai-tools
   ```

3. **Revert localhost URLs**:
   The scripts are configured for Docker. If running natively, change:
   ```python
   # FROM:
   base_url="http://host.docker.internal:11434"
   
   # TO:
   base_url="http://localhost:11434"
   ```

### Why Docker for CrewAI Only?

- **Ollama**: Runs natively for better GPU access
- **Python Scripts**: Run natively for easier debugging
- **Qdrant**: Uses Docker for easy management
- **CrewAI**: Uses Docker to avoid Windows build issues

This hybrid approach gives you the best of both worlds!

## 📚 Learning Path

1. Start with `00_crew_basics.py` to understand the fundamentals
2. Progress through `01_simple_crew.py` for practical collaboration
3. Explore `03_hierarchical_crew.py` for advanced orchestration
4. Try `04_tools_in_crew.py` to give agents superpowers
5. Finish with `07_production_crew.py` for a complete system

## 🎯 Next Steps

After mastering CrewAI:
- Integrate with RAG systems (combine with `03-embeddings-rag`)
- Build the voice assistant (Phase 3 of the learning path)
- Create your own multi-agent applications

Happy coding! 🚀
