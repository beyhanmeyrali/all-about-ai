# Your Personal Remote Development Server

## The Game-Changer: AI Coding Agents Working 24/7, Managed from Anywhere

> **Why This Setup Matters:** With AI coding agents (Claude Code, GitHub Copilot CLI, Gemini CLI) running in persistent tmux sessions, you can **assign coding tasks and let them work while you're away**. Check progress from your phone at lunch, review code on your tablet on the couch, give new tasks from any device. Without AI agents, you'd need to be at your PC to write code. With this setup, AI agents write code for you while you just guide, review, and test—**from anywhere in the world**.

> **For All Developers:** Web apps, backend services, mobile apps, AI models—work on multiple projects simultaneously with persistent sessions that survive disconnections. Your personal cloud infrastructure with zero ongoing costs.

**Created by:** [Beyhan MEYRALI](https://www.linkedin.com/in/beyhanmeyrali/)


## Table of Contents

- [Overview](#overview)
- [What Are We Building?](#what-are-we-building)
- [Architecture](#architecture)
- [Why This Setup?](#why-this-setup)
- [Components Explained](#components-explained)
- [Learning Path](#learning-path)
- [System Information](#system-information)
- [Installation Guide](#initial-wsl-setup)

---

## Overview

This guide will help you build a **professional remote development server** that runs on your Windows machine using WSL2 (Windows Subsystem for Linux). By the end, you'll have:

✅ A full Linux development environment on Windows
✅ Access from **anywhere** with **zero networking complexity** (no port forwarding, no router config, no static IP needed!)
✅ Works on **any network** (coffee shop WiFi, hotel, cellular data) thanks to Tailscale VPN
✅ Persistent sessions that survive disconnections—close your laptop and pick up where you left off
✅ Multiple projects running simultaneously (frontend, backend, mobile, ML pipelines)
✅ Professional development tools (VS Code Server, tmux, SSH, Docker)
✅ **5-minute setup** - Install, run, connect. No networking expertise required.
✅ Optional: GPU acceleration for AI/ML workloads

**Who is this for?**
- **Web Developers** - Run multiple React, Node.js, or Python projects simultaneously
- **Backend Developers** - Manage microservices, databases, and APIs in one place
- **Mobile Developers** - Build and test apps remotely with full IDE access
- **Students & Learners** - Practice coding from any device, keep projects running 24/7
- **DevOps Engineers** - Manage containers, test deployments, run CI/CD pipelines
- **AI/ML Developers** - Train models, run inference servers, manage data pipelines
- **Anyone** who wants to code from multiple devices or keep work sessions alive

---

## What Are We Building?

We're creating a **remote development server** that runs on your Windows PC but can be accessed from anywhere. Think of it as your personal cloud development environment, but it's running on your own hardware.

### The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR WINDOWS PC                          │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              WSL2 (Ubuntu Linux)                       │   │
│  │                                                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────┐    │   │
│  │  │   SSH    │  │   tmux   │  │  VS Code Server │    │   │
│  │  │ (Remote  │  │ (Session │  │  (Web Browser)  │    │   │
│  │  │  Access) │  │  Manager)│  │                 │    │   │
│  │  └────┬─────┘  └────┬─────┘  └────────┬────────┘    │   │
│  │       │             │                  │              │   │
│  │  ┌────┴─────────────┴──────────────────┴─────────┐   │   │
│  │  │        Your Code & AI Models                  │   │   │
│  │  │  • Python Projects   • Docker Containers      │   │   │
│  │  │  • vLLM (AI Models)  • Qdrant (Vector DB)     │   │   │
│  │  └────────────────┬──────────────────────────────┘   │   │
│  │                   │                                   │   │
│  │              ┌────┴─────┐                            │   │
│  │              │   GPU    │  ← Hardware Acceleration   │   │
│  │              │  Access  │                            │   │
│  │              └──────────┘                            │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │              Tailscale (VPN Mesh)                    │     │
│  │           (Secure access from anywhere)              │     │
│  └────────────────┬─────────────────────────────────────┘     │
└───────────────────┼─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Laptop │  │  Phone │  │  iPad  │
    │  SSH   │  │Terminal│  │VS Code │
    │  tmux  │  │ or Web │  │  Web   │
    └────────┘  └────────┘  └────────┘
```

### What This Means in Practice

**Before:** You're at your desk, working on your Windows PC with all your AI models and code.

**After:** You're on the couch with your iPad, continuing the same work in a full VS Code environment, or you're on your phone in a coffee shop, checking your model training progress via SSH.

### 🚀 The Real Power: Multiple AI Agents Working Simultaneously

Here's the **game-changing workflow** this setup enables:

```
Your Home Server (Running 24/7)
│
├── tmux session 1: "frontend"
│   └── Claude Code working on React app
│
├── tmux session 2: "backend"
│   └── GitHub Copilot CLI coding Python API
│
├── tmux session 3: "mobile"
│   └── Gemini CLI building Flutter app
│
├── tmux session 4: "ml-pipeline"
│   └── Qwen CLI creating data pipelines
│
└── tmux session 5: "training"
    └── vLLM training a custom model
```

**You from anywhere in the world:**
```bash
# From your phone at a coffee shop
ssh user@home-via-tailscale

# Check all running projects
tmux ls
  0: frontend (Claude Code active)
  1: backend (GitHub Copilot active)
  2: mobile (Gemini CLI active)
  3: ml-pipeline (Qwen CLI active)
  4: training (model training 67% complete)

# Attach to any session
tmux attach -t frontend  # See what Claude is doing
tmux attach -t backend   # Check Copilot's progress

# Start a new AI agent on a new project
tmux new -s website
claude-code "build me a portfolio website"
# Detach (Ctrl+B, D) - Claude keeps working!

# Open VS Code Server in browser on your iPad
# Access: http://tailscale-ip:8080
# Full VS Code with all extensions, editing all projects
```

**Why This is Revolutionary:**

1. **Multiple AI Agents, One Server**
   - Run 5+ different AI coding tools simultaneously
   - Each in its own tmux session
   - Each working on different projects
   - All accessible from anywhere

2. **No Port Forwarding Needed**
   - **Tailscale** creates a secure VPN mesh
   - Your server stays behind your home firewall
   - Access from anywhere: coffee shop, vacation, phone
   - No router configuration required

3. **Persistent Sessions (tmux)**
   - Close your laptop → AI agents keep working
   - Lose internet connection → Projects continue
   - Switch devices → Resume exactly where you left off
   - AI agents can work for hours/days on complex tasks

4. **Web-Based IDE (VS Code Server)**
   - Full VS Code in your browser
   - No installation on client devices
   - Works on iPad, Chromebook, any device with a browser
   - All extensions: Claude Code, Copilot, debuggers

**Real-World Scenario:**

```
Monday 9 AM (At home office)
└── SSH into server, start 3 AI agents in tmux
    ├── Claude Code: "Refactor authentication system"
    ├── GitHub Copilot: "Write API tests"
    └── Gemini CLI: "Update documentation"

Monday 2 PM (Coffee shop, on iPad)
└── Open VS Code Server in Safari
    └── Check progress, make adjustments, give new instructions

Monday 8 PM (On couch with phone)
└── SSH from phone
    └── tmux attach → See all agents' progress
    └── Start new agent for tomorrow's project

All this time:
✅ Server at home (no carrying laptop)
✅ No port forwarding (secure via Tailscale)
✅ All AI agents still working (tmux keeps sessions alive)
✅ Access from any device (SSH + VS Code Web)
```

**This is Your Personal AI Development Farm** - Multiple AI assistants working on multiple projects, accessible from anywhere, running 24/7 on your home hardware. 🚀

---

## Architecture

Let's break down the architecture into three layers, from simple to complex.

### Level 1: Basic Setup (Beginner)

```
Windows (Host)
    └── WSL2 (Ubuntu Linux)
            ├── Your Code Files
            └── Development Tools
```

At the simplest level, WSL2 is just Linux running inside Windows. You get a real Ubuntu terminal on Windows.

### Level 2: Remote Access (Intermediate)

```
Windows PC
    └── WSL2 Ubuntu
            ├── SSH Server (Port 22) ──────┐
            │   "Accept remote connections" │
            │                                │
            ├── VS Code Server (Port 8080) ─┤
            │   "Web-based IDE"              │
            │                                │
            └── Tailscale ──────────────────┤
                "VPN for secure access"      │
                                             │
        ┌────────────────────────────────────┘
        │ Internet / Local Network
        │
        ▼
   Other Devices
   (Phone, Tablet, Another PC)
```

Now you can connect to your development environment from other devices using:
- **SSH** - Terminal access (for tmux, CLI tools)
- **VS Code Server** - Full IDE in your browser
- **Tailscale** - Secure VPN connection

### Level 3: Production AI Development (Advanced)

```
┌──────────────── YOUR DEVELOPMENT SERVER ─────────────────┐
│                                                           │
│  Access Layer (How you connect)                          │
│  ├── Tailscale (Secure VPN)                              │
│  ├── SSH (Port 2222) ← Terminal access                   │
│  └── VS Code Server (Port 8080) ← Web IDE                │
│                                                           │
│  Session Management                                       │
│  └── tmux (Persistent sessions that survive disconnect)  │
│                                                           │
│  Application Layer                                        │
│  ├── Python/Node.js (Your code)                          │
│  ├── vLLM (Run AI models like Llama, Mistral)            │
│  ├── Ollama (Easy AI model management)                   │
│  └── Docker (Containerized services)                     │
│                                                           │
│  Data Layer                                               │
│  ├── Qdrant (Vector database for AI embeddings)          │
│  ├── Your project files                                  │
│  └── Model weights                                       │
│                                                           │
│  Hardware Layer                                           │
│  └── NVIDIA GPU (Hardware acceleration for AI)           │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

This is the complete stack for professional AI development with remote access.

---

## Why This Setup?

Let's explain the "why" behind each decision:

### Why WSL2 instead of a regular VM?

| Feature | WSL2 | Traditional VM |
|---------|------|----------------|
| **Performance** | Near-native speed | Slower (full emulation) |
| **Resource Usage** | Lightweight | Heavy (full OS overhead) |
| **Startup Time** | Instant | 30-60 seconds |
| **File Access** | Easy (Windows ↔ Linux) | Complex (network shares) |
| **GPU Access** | Built-in support | Complex setup |

**Bottom line**: WSL2 gives you a full Linux environment without the overhead of a virtual machine.

### Why Tailscale instead of port forwarding?

**The Critical Difference: Your Home Server Stays Home**

**Port Forwarding** (Traditional approach):
- ⚠️ Exposes your PC to the internet (security risk!)
- ⚠️ Requires router configuration (not possible on some networks)
- ⚠️ Breaks when you change networks (can't take laptop to coffee shop)
- ⚠️ Fixed IP address needed (costs money)
- ⚠️ Firewall configuration nightmare

**Tailscale** (Modern approach):
- ✅ **Zero-config secure VPN** - Install and go
- ✅ **Works behind any firewall/NAT** - Coffee shop, hotel, airplane WiFi
- ✅ **Encrypted by default** - WireGuard protocol
- ✅ **No exposed ports** - Nothing visible to attackers
- ✅ **Works from anywhere** - Even if your home IP changes
- ✅ **Mesh network** - All your devices can talk to each other

**Real-World Example:**
```
WITHOUT Tailscale:
❌ At coffee shop: "Can't access home server - firewall blocks me"
❌ At hotel: "Need to reconfigure port forwarding"
❌ On phone: "My home IP changed, connection broken"

WITH Tailscale:
✅ At coffee shop: ssh user@home-tailscale-ip (just works!)
✅ At hotel: Same command (just works!)
✅ On phone: Same command (just works!)
✅ Your server is always at the same Tailscale IP: 100.x.x.x
```

**For AI Agent Workflow:**
- Your 5 AI agents keep running at home
- You check on them from your phone at lunch
- Server never exposed to internet attackers
- No port forwarding setup needed

### Why tmux?

**The Key to Multiple AI Agents: Persistent Sessions**

**Without tmux**:
```
SSH Connection → Start Claude Code → Connection drops → Claude stops ❌
All your AI agents die when you disconnect ❌
```

**With tmux**:
```
SSH → tmux session 1 → Start Claude Code → Connection drops → Claude continues ✓
SSH → tmux session 2 → Start GitHub Copilot → Connection drops → Copilot continues ✓
SSH → tmux session 3 → Start Gemini CLI → Connection drops → Gemini continues ✓
...
SSH again → tmux ls → See ALL agents still running ✓
```

**The Multi-Agent Workflow:**
```bash
# Morning: Start your AI coding farm
tmux new -s frontend
claude-code "Build a React dashboard"
# Detach: Ctrl+B, D

tmux new -s backend
github-copilot-cli "Create REST API"
# Detach

tmux new -s mobile
gemini-cli "Flutter app for iOS"
# Detach

tmux new -s ml
qwen-cli "Build data pipeline"
# Detach

# Close laptop, go to coffee shop

# Afternoon: Check progress from iPad
ssh user@home
tmux ls
  frontend: Claude Code (active, 3 hours running)
  backend: Copilot (active, 2 hours running)
  mobile: Gemini (active, 2 hours running)
  ml: Qwen (active, 2 hours running)

tmux attach -t frontend  # See what Claude accomplished
tmux attach -t backend   # Review Copilot's code

# Give new instructions, detach, let them continue
# Close iPad

# Evening: Check from phone while cooking dinner
ssh user@home
tmux attach -t ml  # See Qwen's progress
```

**Why tmux is Essential:**

1. **Multiple AI Agents Simultaneously**
   - Each agent in its own tmux session
   - All running at the same time
   - All accessible by name

2. **Persistent Sessions**
   - Close laptop → Agents keep working
   - Lose WiFi → Agents keep working
   - Switch devices → Agents keep working
   - AI can work for hours/days without you

3. **Access from Any Device**
   - Start on desktop
   - Check on phone
   - Edit on iPad
   - Complete on laptop
   - Same sessions, same agents, same work

4. **Perfect for Long-Running Tasks**
   - AI model training (hours)
   - Large refactoring (hours)
   - Test suite generation (hours)
   - Documentation writing (hours)

**Without tmux**: You must stay connected, agents stop when you close laptop
**With tmux**: Your AI agents are like remote workers - they keep working even when you're not watching

### Why VS Code Server?

**Web-Based IDE = Code from Literally Anywhere**

While tmux + SSH is perfect for CLI-based AI agents, VS Code Server gives you a **full graphical IDE** in your web browser.

**What You Get:**
- **Full VS Code** - Not a limited version, the REAL VS Code
- **All Extensions Work** - Claude Code, GitHub Copilot, debuggers, themes
- **Browser-Based** - No installation needed on client device
- **Touch-Friendly** - Works great on iPad with keyboard
- **Any Device** - Chromebook, tablet, phone (for quick edits)

**How It Complements tmux:**

```
┌─────────────────────────────────────────────────┐
│         Your Development Environment            │
├─────────────────────────────────────────────────┤
│                                                 │
│  tmux Sessions (CLI AI Agents)                  │
│  ├── Claude Code (terminal-based)               │
│  ├── Copilot CLI (terminal-based)               │
│  └── Gemini CLI (terminal-based)                │
│                                                 │
│  VS Code Server (Web UI)                        │
│  ├── Full IDE with extensions                   │
│  ├── File explorer, git integration             │
│  ├── Edit multiple files visually               │
│  └── Integrated terminal (can access tmux!)     │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Real-World Usage:**

**Option 1: SSH + tmux (Terminal lovers)**
```bash
# From any device
ssh user@home-via-tailscale
tmux attach -t frontend
# CLI-based AI coding
```

**Option 2: VS Code Server (Visual lovers)**
```
# From iPad/browser
http://home-tailscale-ip:8080
# Full IDE with all your projects
# Use Claude Code extension directly in VS Code UI
```

**Option 3: Best of Both (Power users)**
```
1. Open VS Code Server in browser on iPad
2. Use VS Code terminal inside → tmux attach
3. Have both visual file editing AND CLI AI agents
4. Edit files visually while AI agents work in background
```

**Example Workflow:**
```
On iPad at coffee shop:
1. Open Safari → http://home:8080
2. VS Code opens in browser
3. See all your projects
4. Open integrated terminal
5. Run: tmux ls (see all AI agents)
6. Run: tmux attach -t backend
7. Monitor Copilot's progress
8. Switch back to VS Code editor
9. Make manual edits to files
10. Open another terminal → Start new AI agent

All from an iPad! 🤯
```

**This is Why VS Code Server is Essential:**
- tmux gives you persistent CLI sessions
- VS Code Server gives you persistent visual IDE
- Together = Complete development environment from any device

### Why This Combination?

Each tool solves a specific problem, and together they create something revolutionary:

**The Core Stack:**
1. **WSL2** → Real Linux on Windows (no VM overhead)
2. **Tailscale** → Access from anywhere, no port forwarding, always secure
3. **SSH** → Terminal access from any device
4. **tmux** → **Multiple persistent AI agent sessions**
5. **VS Code Server** → Full IDE in browser from any device

**The AI/ML Stack:**
6. **Docker** → Isolated services (databases, tools)
7. **vLLM/Ollama** → Run AI models locally with GPU
8. **Qdrant** → Vector database for RAG pipelines

**What This Enables:**

```
┌──────────────────────────────────────────────────────────┐
│                    THE KILLER FEATURE                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Your Home Server (24/7)                                 │
│  ├── 5+ AI coding agents in tmux sessions               │
│  ├── GPU-accelerated model training                     │
│  ├── All your projects and code                         │
│  └── Vector databases with your data                    │
│                                                          │
│  You (Anywhere in the world)                             │
│  ├── Check progress from phone                          │
│  ├── Code from iPad with VS Code web UI                 │
│  ├── SSH from laptop at coffee shop                     │
│  └── All via Tailscale (no port forwarding!)            │
│                                                          │
│  Security: ✅ No exposed ports                           │
│  Cost: ✅ No cloud bills                                 │
│  Privacy: ✅ All data stays on your hardware             │
│  Power: ✅ Use your gaming GPU for AI                    │
│  Flexibility: ✅ Code from literally any device          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**This is NOT just a remote development environment.**

**This is:**
- Your personal AI development farm
- Multiple AI assistants working 24/7
- Accessible from any device, anywhere
- Running on your hardware (no cloud costs)
- Completely secure (VPN, no exposed ports)
- Using your GPU (RTX 5060 for AI acceleration)

**Real-World Power:**
```
Monday morning:
  Start 5 AI agents on different projects

Monday - Friday:
  Check/guide them from phone, iPad, laptop
  Server stays home, running 24/7
  Agents work even while you sleep

Friday afternoon:
  5 projects significantly progressed
  All code on your hardware
  Zero cloud costs
  Complete privacy
```

**This is why we combine ALL these tools** - individually they're useful, together they create a **complete AI development platform** that you can access from anywhere, running on hardware you control. 🚀

---

## Components Explained

Let's build your understanding step by step.

### 🟢 Level 1: Foundational Components (Start Here)

#### 1. WSL2 (Windows Subsystem for Linux)

**What it is**: A way to run real Linux on Windows without a virtual machine.

**Analogy**: Think of it like having a second computer inside your Windows PC, but it's actually Linux.

**What you can do**:
- Run Linux commands (`apt`, `bash`, etc.)
- Install Linux software
- Access Windows files from Linux
- Use your PC's GPU from Linux

**Example**:
```bash
# On Windows PowerShell
wsl --install Ubuntu

# Now you have a full Ubuntu terminal!
```

#### 2. SSH (Secure Shell)

**What it is**: A way to remotely control a computer using the command line.

**Analogy**: Like Remote Desktop, but for terminal/command line instead of GUI.

**What you can do**:
```bash
# From your phone or any device:
ssh username@your-server-ip

# Now you're controlling your Windows PC's Linux environment!
```

**Why it matters**: You can code from literally anywhere - phone, tablet, another computer.

#### 3. tmux (Terminal Multiplexer)

**What it is**: A tool that keeps your terminal sessions running even after you disconnect.

**Analogy**: Think of it like keeping Chrome tabs open after closing the browser. When you open Chrome again, your tabs are still there.

**Real-world scenario**:
```bash
# Start a training job
tmux new -s training
python train_model.py  # This takes 8 hours

# Close laptop, go home, SSH from home PC
tmux attach -s training  # Training is still running!
```

**Key insight**: Without tmux, disconnecting would kill your running processes.

### 🟡 Level 2: Development Tools (Intermediate)

#### 4. VS Code Server (code-server)

**What it is**: Full Visual Studio Code running in your web browser.

**What makes it special**:
- Runs on your server (WSL)
- Access via any web browser
- All extensions work (Copilot, Claude Code, debuggers)
- Perfect for iPad/tablet development

**How it works**:
```
Your iPad browser → http://your-server:8080 → Full VS Code IDE
```

**Why this is amazing**:
- Code on your iPad as if it's a MacBook Pro
- No installation needed on client devices
- All processing happens on your powerful server

#### 5. Tailscale (Zero-Config VPN)

**What it is**: A mesh VPN that connects all your devices securely.

**Traditional VPN vs Tailscale**:

**Traditional VPN**:
```
You → VPN Server (in cloud) → Your PC
```
Slow, costs money, requires setup

**Tailscale**:
```
Your Phone ←→ Your PC (direct encrypted connection)
```
Fast, free tier available, zero configuration

**What you get**:
- Every device gets a permanent IP (e.g., `100.64.1.5`)
- Secure by default (WireGuard encryption)
- Works from anywhere (coffee shop, hotel, airplane WiFi)
- No port forwarding needed

#### 6. systemd (Service Manager)

**What it is**: The system that manages background services in Linux.

**Analogy**: Like Windows Services, but for Linux.

**Why you need it**:
```bash
# Without systemd - manual start every time
service ssh start
service docker start
code-server &

# With systemd - automatic startup
sudo systemctl enable ssh docker code-server
# Now they start automatically when WSL boots!
```

### 🔴 Level 3: AI/ML Components (Advanced)

#### 7. Docker & Docker Compose

**What it is**: A way to package applications with all their dependencies.

**Analogy**: Like a shipping container. It contains everything the app needs, and it works the same everywhere.

**Why for AI development**:
```bash
# Instead of:
# - Install Python 3.11
# - Install CUDA 12.1
# - Install 50 dependencies
# - Hope versions match

# You do:
docker run qdrant/qdrant
# Everything just works!
```

**Real benefit**: Isolate services so they don't conflict.

#### 8. NVIDIA Container Toolkit

**What it is**: Lets Docker containers use your NVIDIA GPU.

**Why it matters**:
```bash
# Without it:
docker run my-ai-model
# Uses CPU only (slow) ❌

# With it:
docker run --gpus all my-ai-model
# Uses GPU (100x faster) ✅
```

**Critical for**: Running AI models efficiently in containers.

#### 9. vLLM (LLM Inference Engine)

**What it is**: Software optimized for running large language models (like Llama, Mistral).

**What makes it special**:
- **Fast**: PagedAttention algorithm
- **Efficient**: Serves multiple requests simultaneously
- **Compatible**: Works with popular models

**Example**:
```python
# Run Llama 3 70B model
vllm serve meta-llama/Llama-3-70B

# Now you have a local ChatGPT-like API!
```

**Use cases**:
- Run AI models privately (no data leaves your PC)
- No API costs
- Full control over the model

#### 10. Ollama (Easy LLM Management)

**What it is**: A user-friendly tool for running AI models locally.

**Analogy**: Like Docker, but specifically for AI models.

**Why it's great for beginners**:
```bash
# Download and run a model (one command)
ollama run llama3

# That's it! Now chat with the AI.
```

**vs vLLM**:
- **Ollama**: Easy to use, great for experimentation
- **vLLM**: More powerful, production-grade, better performance

#### 11. Qdrant (Vector Database)

**What it is**: A database optimized for AI embeddings and similarity search.

**What are embeddings?**: Numbers that represent meaning.
```
"cat" → [0.2, 0.8, 0.1, ...]
"dog" → [0.3, 0.7, 0.15, ...] ← Similar to "cat"
"car" → [0.9, 0.1, 0.05, ...] ← Different from "cat"
```

**Real-world use cases**:
- **RAG (Retrieval-Augmented Generation)**: Give AI models context from your documents
- **Semantic search**: Search by meaning, not keywords
- **Recommendation systems**: Find similar items

**Example**:
```python
# Store document embeddings
qdrant.upsert(documents=[
    "Python is a programming language",
    "Cats are animals"
])

# Search by meaning
results = qdrant.search("coding languages")
# Returns: "Python is a programming language"
```

---

## Learning Path

Here's how to approach this guide based on your skill level:

### 🌱 Complete Beginner

**Start with**:
1. ✅ Install WSL2 and Ubuntu
2. ✅ Learn basic Linux commands (`ls`, `cd`, `nano`)
3. ✅ Install and use tmux
4. ✅ Install SSH server

**Goal**: Get comfortable with the Linux terminal.

**Skip for now**: Docker, AI models, Qdrant

### 🌿 Intermediate Developer

**You already know**: Linux basics, SSH, basic networking

**Focus on**:
1. ✅ Set up Tailscale
2. ✅ Configure systemd services
3. ✅ Install VS Code Server
4. ✅ Set up port forwarding
5. ✅ Practice tmux workflows

**Goal**: Create a remote development environment you can access from anywhere.

### 🌳 Advanced / AI Developer

**You already know**: Everything above + Docker, Python, AI/ML basics

**Focus on**:
1. ✅ Install Docker and NVIDIA Container Toolkit
2. ✅ Set up vLLM for model serving
3. ✅ Configure Ollama for easy model testing
4. ✅ Deploy Qdrant for vector storage
5. ✅ Build RAG pipelines

**Goal**: Production-ready AI development environment with GPU acceleration.

---

## System Information

- **Date Created**: November 24, 2025
- **WSL Version**: 2
- **Distribution**: Ubuntu 24.04 LTS
- **Root Password**: ubuntu

## Hardware Specs

- **CPU**: AMD Ryzen AI 9 365 w/ Radeon 880M
- **GPU**:
  - NVIDIA GeForce RTX 5060 Laptop GPU (dedicated)
  - AMD Radeon 880M Graphics (integrated)

---

## Initial WSL Setup

### 1. Check Existing WSL Installations

```powershell
wsl --list --verbose
```

### 2. Remove Old Ubuntu Instance (if exists)

```powershell
wsl --unregister Ubuntu
```

### 3. Install Fresh Ubuntu

```powershell
wsl --install Ubuntu
```

This installs Ubuntu 24.04 LTS (the latest LTS version available in WSL store).

### 4. Set Root Password

When prompted during installation, create your user account. Then set root password:

```bash
sudo passwd root
# Enter: ubuntu
```

### 5. Verify Installation

```powershell
wsl --list --verbose
```

You should see:
```
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

---

## Accessing Ubuntu

### Enter Ubuntu as Root

```powershell
wsl -d Ubuntu -u root
```

### Enter Ubuntu as Your User

```powershell
wsl -d Ubuntu
```

Or simply:
```powershell
wsl
```

---

## Installed Packages

### 1. Tailscale (VPN/Mesh Network)

**Installation:**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

**Start Tailscale:**
```bash
tailscale up
```

**Check Status:**
```bash
tailscale status
```

**Documentation**: https://tailscale.com/kb/

---

### 2. tmux (Terminal Multiplexer)

**Installation:**
```bash
apt update
apt install -y tmux
```

**Basic Usage:**
- Start new session: `tmux`
- Detach session: `Ctrl+B` then `D`
- List sessions: `tmux ls`
- Attach session: `tmux attach`
- Create window: `Ctrl+B` then `C`
- Switch windows: `Ctrl+B` then `0-9`
- Split pane horizontal: `Ctrl+B` then `"`
- Split pane vertical: `Ctrl+B` then `%`

**Documentation**: https://github.com/tmux/tmux/wiki

---

### 3. SSH Server (Remote Access)

**Installation:**
```bash
apt update
apt install -y openssh-server
```

**Start SSH Service:**
```bash
service ssh start
```

**Check SSH Status:**
```bash
service ssh status
```

**Get WSL IP Address:**
```bash
ip addr show eth0 | grep "inet "
```

**Documentation**: https://ubuntu.com/server/docs/service-openssh

---

### 4. VS Code Server (Web-based IDE)

VS Code Server allows you to access a full VS Code environment through your web browser, perfect for coding from tablets, phones, or any device.

**Installation:**
```bash
# Download and install code-server
curl -fsSL https://code-server.dev/install.sh | sh
```

**Start VS Code Server:**
```bash
# Start with default settings (runs on port 8080)
code-server

# Or start with custom settings
code-server --bind-addr 0.0.0.0:8080 --auth password
```

**Configuration:**
```bash
# Edit config file
nano ~/.config/code-server/config.yaml
```

Example config:
```yaml
bind-addr: 0.0.0.0:8080
auth: password
password: your-secure-password-here
cert: false
```

**Get the Password:**
```bash
# View the auto-generated password
cat ~/.config/code-server/config.yaml | grep password
```

**Install Extensions in VS Code Server:**
```bash
# Install Claude Code (if available)
code-server --install-extension anthropics.claude-code

# Install GitHub Copilot
code-server --install-extension GitHub.copilot

# Install other useful extensions
code-server --install-extension ms-python.python
code-server --install-extension ms-vscode.cpptools
```

**Access VS Code Server:**
- From Windows: `http://localhost:8080`
- From LAN (after port forwarding): `http://<windows-ip>:8080`
- From anywhere (via Tailscale): `http://<tailscale-ip>:8080`

**Documentation**: https://coder.com/docs/code-server

---

## Remote Access to WSL

### Accessing tmux from Another Machine

You can access your WSL tmux sessions from other machines using SSH.

#### Option 1: Via Tailscale (Recommended - Works Anywhere)

**Setup:**
```bash
# In WSL - Enable Tailscale SSH
sudo tailscale up --ssh

# Check your Tailscale IP/hostname
tailscale status
```

**Connect from Another Machine:**
```bash
# On the remote machine (must have Tailscale installed)
ssh username@<tailscale-hostname-or-ip>

# Once connected, attach to tmux
tmux attach
```

#### Option 2: Via LAN (Same Network)

**Step 1: Get WSL IP Address**
```bash
# In WSL
ip addr show eth0 | grep "inet "
# Example output: inet 172.24.123.45/20
```

**Step 2: Set Up Windows Port Forwarding**
```powershell
# In PowerShell as Administrator on Windows

# Get WSL IP
wsl hostname -I

# Forward Windows port 2222 to WSL SSH port 22
netsh interface portproxy add v4tov4 listenport=2222 listenaddress=0.0.0.0 connectport=22 connectaddress=<WSL-IP>

# Allow through Windows Firewall
New-NetFirewallRule -DisplayName "WSL SSH" -Direction Inbound -LocalPort 2222 -Protocol TCP -Action Allow

# View port forwarding rules
netsh interface portproxy show all
```

**Step 3: Get Windows LAN IP**
```powershell
# In PowerShell on Windows
ipconfig
# Look for your LAN adapter IP (e.g., 192.168.1.100)
```

**Step 4: Connect from Another Machine on LAN**
```bash
# From the remote machine
ssh -p 2222 username@<windows-lan-ip>

# Once connected, attach to tmux
tmux attach
# Or list sessions first: tmux ls
```

**Auto-Update Port Forwarding Script (Windows)**

Create `wsl-port-forward.ps1`:
```powershell
# Run as Administrator
$wslIP = (wsl hostname -I).Trim()

# Define port mappings: Windows Port -> WSL Port
$portMappings = @{
    2222 = 22     # SSH
    8080 = 8080   # VS Code Server
    # Add more ports as needed:
    # 6333 = 6333   # Qdrant
    # 11434 = 11434 # Ollama
}

# Remove existing rules
netsh interface portproxy reset

# Add port forwarding rules
foreach ($listenPort in $portMappings.Keys) {
    $connectPort = $portMappings[$listenPort]
    netsh interface portproxy add v4tov4 listenport=$listenPort listenaddress=0.0.0.0 connectport=$connectPort connectaddress=$wslIP
    Write-Host "Forwarded Windows port $listenPort to WSL $wslIP`:$connectPort"
}

# Add firewall rules
New-NetFirewallRule -DisplayName "WSL SSH" -Direction Inbound -LocalPort 2222 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "WSL VS Code Server" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue

Write-Host "`nPort forwarding configured successfully!"
netsh interface portproxy show all
```

Run this script after WSL restarts (WSL IP changes on restart).

**Quick Setup for VS Code Server:**
```powershell
# In PowerShell as Administrator
$wslIP = (wsl hostname -I).Trim()

# Forward port 8080 for VS Code Server
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=$wslIP

# Allow through firewall
New-NetFirewallRule -DisplayName "WSL VS Code Server" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

**Remove Port Forwarding:**
```powershell
netsh interface portproxy delete v4tov4 listenport=2222 listenaddress=0.0.0.0
netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=0.0.0.0
netsh interface portproxy reset  # Remove all rules
```

---

## Using VS Code Server from Mobile/Tablet

VS Code Server provides a full development environment accessible from any device with a web browser.

### Access Methods

**1. Via Tailscale (Recommended - Works Anywhere)**
```bash
# In WSL, ensure VS Code Server is running
sudo systemctl status code-server

# Get your Tailscale IP
tailscale ip -4
```

From your mobile/tablet browser:
- Open: `http://<tailscale-ip>:8080`
- Enter the password from: `~/.config/code-server/config.yaml`

**2. Via LAN (Same Network)**
- Set up Windows port forwarding (see above)
- Open: `http://<windows-lan-ip>:8080`

### Using Claude Code and GitHub Copilot CLI

**Install Claude Code CLI (if available):**
```bash
# SSH into WSL from mobile
ssh -p 2222 username@<ip-address>

# Attach to tmux session
tmux attach

# Use Claude Code in terminal
claude-code
```

**Install GitHub Copilot CLI:**
```bash
# Install Node.js (required for Copilot CLI)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install GitHub Copilot CLI
npm install -g @githubnext/github-copilot-cli

# Authenticate
github-copilot-cli auth

# Use in terminal
github-copilot-cli what-the-shell "find all python files modified today"
github-copilot-cli git-assist "create a commit message for my changes"
```

**Recommended Mobile SSH Clients:**
- **iOS**: Blink Shell, Termius, Secure ShellFish
- **Android**: Termux, JuiceSSH, Termius

**Recommended Browsers for VS Code Server:**
- **iOS/iPadOS**: Safari, Chrome
- **Android**: Chrome, Firefox

### Tips for Mobile/Tablet Development

**Use tmux for persistent sessions:**
```bash
# Create named session
tmux new -s dev

# Detach without killing: Ctrl+B then D
# Reattach from anywhere: tmux attach -s dev
```

**Configure VS Code Server for mobile:**
```yaml
# ~/.config/code-server/config.yaml
bind-addr: 0.0.0.0:8080
auth: password
password: your-secure-password
cert: false
```

**Run long-running tasks in tmux:**
```bash
# In tmux session
tmux new -s training
python train_model.py

# Detach and close SSH
# Reconnect anytime to check progress
```

---

## Automatic Service Startup

Configure services to start automatically when WSL boots.

### Enable systemd in WSL

Edit `/etc/wsl.conf`:
```bash
sudo nano /etc/wsl.conf
```

Add:
```ini
[boot]
systemd=true
```

Restart WSL for changes to take effect:
```powershell
wsl --shutdown
```

### Configure Services to Auto-Start

Once systemd is enabled, you can use systemctl to manage services:

**SSH Server:**
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

**Tailscale:**
```bash
sudo systemctl enable tailscaled
sudo systemctl start tailscaled
sudo systemctl status tailscaled
```

**Docker (after installation):**
```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker
```

**VS Code Server:**

Create a systemd service file:
```bash
sudo nano /etc/systemd/system/code-server.service
```

Add the following content (replace `username` with your actual username):
```ini
[Unit]
Description=code-server
After=network.target

[Service]
Type=simple
User=username
Environment=PASSWORD=your-secure-password-here
ExecStart=/usr/bin/code-server --bind-addr 0.0.0.0:8080 --auth password
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable code-server
sudo systemctl start code-server
sudo systemctl status code-server
```

### Alternative: Without systemd

If you prefer not to use systemd, add startup commands to `/etc/wsl.conf`:

```bash
sudo nano /etc/wsl.conf
```

Add:
```ini
[boot]
command="service ssh start && tailscale up && code-server --bind-addr 0.0.0.0:8080 &"
```

This will run these commands every time WSL starts.

**Note**: Running code-server in the background (`&`) means it won't be easily manageable. Using systemd is recommended for proper service management.

### Verify Services on Startup

After restarting WSL:
```bash
# Check SSH
service ssh status
# or with systemd:
sudo systemctl status ssh

# Check Tailscale
tailscale status
# or with systemd:
sudo systemctl status tailscaled

# Check VS Code Server
sudo systemctl status code-server

# Check Docker (if installed)
service docker status
# or with systemd:
sudo systemctl status docker

# View all enabled services
sudo systemctl list-unit-files --state=enabled
```

---

## Future Installations (TODO)

The following packages will be installed for the AI development environment:

### 4. Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
usermod -aG docker $USER

# Start Docker service
service docker start

# Enable Docker to start on boot (requires systemd)
sudo systemctl enable docker
```

### 5. NVIDIA Container Toolkit (for GPU support)

```bash
# Add NVIDIA Container Toolkit repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install NVIDIA Container Toolkit
apt update
apt install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker
```

### 5. vLLM (LLM Inference Engine)

```bash
# Install Python 3 and pip
apt install -y python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv /opt/vllm-env
source /opt/vllm-env/bin/activate

# Install vLLM with CUDA support
pip install vllm

# Or install with specific CUDA version
# pip install vllm --extra-index-url https://download.pytorch.org/whl/cu121
```

**Documentation**: https://docs.vllm.ai/

### 6. Ollama (Local LLM Runner)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Run Ollama service
ollama serve &

# Pull a model (example)
ollama pull llama2
```

**Documentation**: https://github.com/ollama/ollama

### 7. Qdrant (Vector Database)

**Option A: Docker Installation (Recommended)**
```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

**Option B: Binary Installation**
```bash
# Download latest release
wget https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu.tar.gz

# Extract
tar -xvf qdrant-x86_64-unknown-linux-gnu.tar.gz

# Run
./qdrant
```

**Documentation**: https://qdrant.tech/documentation/

---

## WSL Configuration Tips

### Memory and CPU Limits

Create or edit `%USERPROFILE%\.wslconfig` on Windows:

```ini
[wsl2]
memory=16GB
processors=8
swap=8GB
localhostForwarding=true
```

### Enable systemd (if needed)

Edit `/etc/wsl.conf` in Ubuntu:

```ini
[boot]
systemd=true
```

Restart WSL:
```powershell
wsl --shutdown
```

### GPU Access in WSL

WSL2 supports GPU passthrough for both NVIDIA and AMD GPUs. Ensure you have:
- Windows 11 or Windows 10 with latest updates
- GPU drivers installed on Windows
- NVIDIA Container Toolkit (for Docker GPU access)

Test GPU access:
```bash
nvidia-smi
```

---

## Networking

### Access WSL from Windows

WSL2 uses a virtual network adapter. Services running in WSL are accessible from Windows via `localhost`.

Example:
- Qdrant running on port 6333: `http://localhost:6333`
- Ollama API on port 11434: `http://localhost:11434`

### Access WSL from Network

Use Tailscale to expose your WSL instance to other devices securely, or configure Windows port forwarding.

---

## Backup and Export

### Export WSL Instance

```powershell
wsl --export Ubuntu D:\backups\ubuntu-backup.tar
```

### Import WSL Instance

```powershell
wsl --import Ubuntu D:\WSL\Ubuntu D:\backups\ubuntu-backup.tar --version 2
```

---

## Troubleshooting

### WSL Won't Start

```powershell
# Restart WSL
wsl --shutdown
wsl

# Check WSL version
wsl --version

# Update WSL
wsl --update
```

### Docker Won't Start

```bash
# Check Docker status
service docker status

# Start Docker manually
service docker start

# Check Docker logs
journalctl -u docker
```

### GPU Not Detected

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA
nvcc --version

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
```

---

## Useful Commands

### WSL Management

```powershell
# List all distributions
wsl --list --all

# Set default distribution
wsl --set-default Ubuntu

# Check WSL status
wsl --status

# Terminate specific distribution
wsl --terminate Ubuntu

# Shutdown all WSL instances
wsl --shutdown
```

### Ubuntu Package Management

```bash
# Update package list
apt update

# Upgrade all packages
apt upgrade -y

# Search for package
apt search <package>

# Install package
apt install -y <package>

# Remove package
apt remove <package>

# Clean up
apt autoremove -y
apt autoclean
```

---

## Additional Resources

- **WSL Documentation**: https://learn.microsoft.com/en-us/windows/wsl/
- **Ubuntu Documentation**: https://help.ubuntu.com/
- **Docker Documentation**: https://docs.docker.com/
- **NVIDIA Container Toolkit**: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/
- **vLLM Documentation**: https://docs.vllm.ai/
- **Ollama Documentation**: https://github.com/ollama/ollama
- **Qdrant Documentation**: https://qdrant.tech/documentation/

---

## Notes

- This setup is designed for AI development with GPU acceleration
- All services (Docker, Ollama, Qdrant) can run simultaneously
- Use tmux for managing long-running processes
- Use Tailscale for secure remote access
- Regular backups are recommended using `wsl --export`

---

**Created with Claude Code**
**Last Updated**: November 24, 2025
