# Quick Test Guide - AI Agents

## 🚀 How to Test Everything

### Prerequisites
```bash
# Make sure Ollama is running
ollama serve

# Verify model is available
ollama list  # Should show qwen3:8b
```

---

## Test Each Section

### 1. Test 00-llm-basics
```bash
cd ai-agents/00-llm-basics
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python test_runner.py
```

**Expected:** ✅ All tests pass, shows LLM responses

---

### 2. Test 01-tool-calling
```bash
cd ai-agents/01-tool-calling
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python test_runner.py
```

**Expected:** ✅ Tool calling works, multi-step agent works

---

### 3. Test 02-agent-frameworks (LangChain)
```bash
cd ai-agents/02-agent-frameworks
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# Test each script
.venv\Scripts\python langchain\00_installation.py
.venv\Scripts\python langchain\01_basic_chain.py
.venv\Scripts\python langchain\02_prompt_templates.py
.venv\Scripts\python langchain\03_chains_with_memory.py
.venv\Scripts\python langchain\05_sequential_chains.py
.venv\Scripts\python langchain\06_router_chains.py
.venv\Scripts\python langchain\07_production_agent.py
```

**Expected:** ✅ All scripts run successfully

---

### 4. Test Comparison Examples
```bash
cd ai-agents/02-agent-frameworks
.venv\Scripts\python comparison\01_langchain_implementation.py
.venv\Scripts\python comparison\02_langgraph_implementation.py
```

**Expected:** ✅ Both implementations work

---

## ⚠️ Known Issues

### CrewAI Installation Issues
**Error:** `metadata-generation-failed` for `chromadb`

**Solutions:**
1. **Docker (Recommended):**
   ```bash
   docker run -it -v d:\workspace\all-about-ai:/workspace python:3.11
   cd /workspace/ai-agents/02-agent-frameworks
   pip install crewai crewai-tools
   ```

2. **Install Visual Studio Build Tools** (Required for native Windows)

---

## 🎯 Quick Verification

Run this to verify everything is set up:

```bash
# From ai-agents directory
python -c "import sys; print(f'Python: {sys.version}')"
ollama list
```

**Expected Output:**
```
Python: 3.11.x or 3.12.x
NAME            ID              SIZE    MODIFIED
qwen3:8b        abc123...       4.7 GB  X days ago
```

---

## 📝 Test Checklist

- [ ] Ollama running (`ollama serve`)
- [ ] `qwen3:8b` model pulled
- [ ] `00-llm-basics` tests pass
- [ ] `01-tool-calling` tests pass
- [ ] `02-agent-frameworks/langchain` scripts work
- [ ] `02-agent-frameworks/comparison` scripts work

---

## 🆘 Troubleshooting

### "Cannot connect to Ollama"
```bash
# Start Ollama
ollama serve

# In another terminal, verify
curl http://localhost:11434/api/tags
```

### "Module not found"
```bash
# Make sure you're using the venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### "Model not found"
```bash
# Pull the model
ollama pull qwen3:8b
```

---

**All working? Great! Your AI agents repository is ready! 🎉**
