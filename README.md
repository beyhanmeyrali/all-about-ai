# All About AI

> A comprehensive collection of AI development resources, guides, and practical code examples

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5.svg)](https://www.linkedin.com/in/beyhanmeyrali/)

**Created by:** [Beyhan MEYRALI](https://www.linkedin.com/in/beyhanmeyrali/)

---

## 📖 About This Repository

Welcome to **All About AI** - your comprehensive resource hub for artificial intelligence development, covering everything from fine-tuning language models to setting up production-grade development environments.

This repository is designed for developers at all levels - whether you're taking your first steps into AI or building advanced production systems. Each guide is built from real-world experience and optimized for practical, hands-on learning.

---

## 🗂️ Repository Structure

### 🎯 [fine-tuning/](./fine-tuning)

**The Great Fine-Tuning Revolution** - A complete journey through AI model fine-tuning, from beginner to advanced.

**What's Inside:**
- 📚 **00-first-time-beginner**: Your first steps into AI fine-tuning
- ⚡ **01-unsloth**: Fast and memory-efficient fine-tuning
- 🤗 **02-huggingface-peft**: Parameter-Efficient Fine-Tuning with HuggingFace
- 🦙 **03-ollama**: Local LLM deployment and usage
- 📦 **04-quantization**: Model compression techniques
- 💡 **05-examples**: Real-world use cases and implementations
- 🚀 **06-advanced-techniques**: Advanced optimization strategies
- 🔓 **07-system-prompt-modification**: Customizing model behavior
- 🏭 **08-llamafactory**: Production-grade fine-tuning framework

**Hardware Focus:** Optimized for AMD Ryzen 9 8945HS + Radeon 780M (GMKtec K11)

**Learning Path:** From 15-minute demos to production deployment

👉 **[Start Your Fine-Tuning Journey →](./fine-tuning/README.md)**

---

### 🖥️ [perfect-setup/](./perfect-setup)

**Your Personal Remote Development Server** - The game-changing setup that lets you run **AI coding agents 24/7 in persistent tmux sessions**, managed from any device.

**🚀 The Revolutionary Workflow:**
1. **Assign Tasks to AI Agents** - Start Claude Code, Copilot CLI, or Gemini CLI in tmux
2. **Let Them Work** - AI agents write code while you're away
3. **Check Progress Anywhere** - Review from phone, tablet, or any browser
4. **Give Feedback & New Tasks** - Test results, assign next tasks, repeat

**Why This Changes Everything:** Without AI agents, you need to be at your PC to write code. With this setup, **AI agents write code for you** while you guide, review, and test from anywhere. This is "vibe coding"—managing AI workers instead of writing code yourself.

**What's Inside:**
- 🤖 **AI Coding Agents** - Claude Code, GitHub Copilot CLI, Gemini CLI in persistent tmux sessions
- 📱 **Remote Management** - Check progress from phone, assign tasks from tablet
- 🌐 **Access Anywhere** - Full VS Code Server in browser, SSH from any device
- 🔐 **Secure VPN** - Tailscale for zero-config connections (no port forwarding!)
- 📂 **Multi-Project** - Multiple AI agents on different projects simultaneously
- 🐳 **Complete Stack** - WSL2, Docker, tmux, systemd, optional GPU acceleration

**Perfect For:** Any developer who wants AI agents to write code while they focus on architecture, review, and testing—accessible from anywhere.

**Key Benefit:** Your personal AI coding farm. Multiple agents working 24/7 on different projects. Zero ongoing costs. Manage from any device worldwide.

👉 **[Build Your AI-Powered Remote Development Server →](./perfect-setup/README.md)**

---

### 🤖 [ai-agents/](./ai-agents)

**From Zero to Hero: Build Your Own Voice GPT** - Complete guide from basic LLM usage to production voice assistants.

**🎯 The Journey:**
1. **Understand LLMs** - Learn how they actually work (and don't store data!)
2. **Tool Calling** - Give LLMs superpowers with function calling
3. **Agent Frameworks** - Build complex workflows with LangGraph & CrewAI
4. **RAG Systems** - Connect LLMs to your data with vector databases
5. **Memory Systems** - Persistent context with Letta (MemGPT)
6. **Voice GPT** - Final project: Your own ChatGPT voice mode

**What's Inside:**
- 📚 **00-llm-basics** - Understanding stateless LLMs and API fundamentals
- 🔧 **01-tool-calling** - Function calling and recursive agent loops
- 🕸️ **02-agent-frameworks** - LangGraph and CrewAI for production agents
- 📊 **03-rag-systems** - Vector databases and retrieval-augmented generation
- 🧠 **04-memory-systems** - Long-term memory with Letta (MemGPT)
- 🎙️ **05-voice-gpt** - Complete voice assistant (Whisper + LangGraph + Letta)

**Tech Stack:** 100% Local with Ollama, Whisper, Qdrant, LangGraph

**Learning Philosophy:**
- ✅ Zero to hero progression
- ✅ Debugger-friendly code with extensive comments
- ✅ curl examples for every HTTP endpoint
- ✅ Real-world examples from production systems

👉 **[Start Building AI Agents →](./ai-agents/README.md)**

---

### 📜 [ai-history/](./ai-history)

**The Silicon God AI** - Philosophical exploration of AI's evolution, impact, and future.

**What's Inside:**
- 🤖 **The Silicon God AI** - A deep dive into AI's transformation of society
- 🧠 **Philosophy & Ethics** - Understanding AI's role in human civilization
- 🌍 **Future Perspectives** - Where AI is taking us

**Languages:** Available in English and Turkish (Türkçe)

👉 **[Explore AI Philosophy →](./ai-history/The_Silicon_God_AI.md)**

---

## 🎯 Who Is This For?

### 🌱 Complete Beginners
- New to AI and machine learning
- Want to understand fine-tuning from scratch
- Looking for step-by-step guides with clear explanations

### 🌿 Intermediate Developers
- Familiar with Python and basic ML concepts
- Want to fine-tune models for specific tasks
- Setting up remote development environments

### 🌳 Advanced / AI Engineers
- Building production AI systems
- Optimizing model performance and deployment
- Implementing RAG pipelines and advanced techniques

---

## 🚀 Quick Start

### For Fine-Tuning AI Models
```bash
cd fine-tuning/00-first-time-beginner
pip install -r requirements.txt
python test_setup.py
```

### For Development Environment Setup
```powershell
# On Windows PowerShell
wsl --install Ubuntu
# Then follow the guide in perfect-setup/
```

---

## 📚 What You'll Learn

### AI Model Fine-Tuning
- ✅ How to customize large language models for your needs
- ✅ Memory-efficient training techniques (LoRA, QLoRA)
- ✅ Quantization and model compression
- ✅ Deployment strategies (Ollama, vLLM)
- ✅ Building practical AI applications

### Development Environment
- ✅ Setting up WSL2 for AI development
- ✅ Remote access and persistent sessions (tmux)
- ✅ Running multiple AI agents simultaneously
- ✅ GPU acceleration for AI workloads
- ✅ Secure networking with Tailscale VPN

---

## 💡 Philosophy

This repository is built on three core principles:

1. **Practical First**: Every guide is tested on real hardware with real use cases
2. **Beginner-Friendly**: Complex concepts explained with analogies and clear examples
3. **Production-Ready**: Not just demos - techniques you can use in real projects

---

## 🛠️ Hardware & Software

### Fine-Tuning Optimization
- **Primary**: AMD Ryzen 9 8945HS + Radeon 780M (GMKtec K11)
- **GPU**: AMD ROCm for GPU acceleration
- **Memory**: Optimized for 32GB RAM + 8GB shared GPU memory

### Development Environment
- **Primary**: AMD Ryzen AI 9 365 + RTX 5060 Laptop GPU
- **OS**: Windows 11 with WSL2 Ubuntu 24.04 LTS
- **GPU**: NVIDIA CUDA for AI inference

### Software Stack
- Python 3.11+
- PyTorch 2.0+
- HuggingFace Transformers & PEFT
- Unsloth, LlamaFactory
- Docker, vLLM, Ollama, Qdrant

---

## 📖 Additional Resources

### Documentation in Turkish 🇹🇷
- [fine-tuning/README-TR.md](./fine-tuning/README-TR.md) - Turkish version of fine-tuning guide
- [ai-history/The_Silicon_God_AI-TR.md](./ai-history/The_Silicon_God_AI-TR.md) - Silicon God AI in Turkish

### Deep Dives
- [The Silicon God AI](./ai-history/The_Silicon_God_AI.md) - Philosophy and future of AI
- [CLAUDE.md](./fine-tuning/CLAUDE.md) - Working with Claude AI

---

## 🤝 Contributing

Found a bug? Have a suggestion? Want to add your own guides?

1. Fork the repository
2. Create your feature branch
3. Submit a pull request

All contributions are welcome!

---

## 📫 Connect

**Beyhan MEYRALI**
- 💼 [LinkedIn](https://www.linkedin.com/in/beyhanmeyrali/)
- 🐙 [GitHub](https://github.com/beyhanmeyrali)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⭐ Star This Repository

If you find this repository helpful, please consider giving it a star! It helps others discover these resources.

---

**Happy Learning! 🚀**

*"The best way to predict the future is to build it."*
