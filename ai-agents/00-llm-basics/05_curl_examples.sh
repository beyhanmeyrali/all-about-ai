#!/bin/bash
# =============================================================================
# Curl Examples: Understanding the HTTP Layer
# =============================================================================
#
# This script shows you the raw HTTP requests behind all LLM interactions.
# Understanding this helps you:
# - Integrate LLMs into ANY system (not just Python)
# - Debug issues at the network level
# - Understand what frameworks like LangChain do under the hood
#
# Author: Beyhan MEYRALI
# =============================================================================

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

OLLAMA_URL="http://localhost:11434"
MODEL="qwen2.5:3b"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Curl Examples: Raw HTTP LLM Interactions                 ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# Example 1: Basic Chat
# =============================================================================

echo -e "${GREEN}Example 1: Basic Chat${NC}"
echo -e "${YELLOW}What happens: Send a simple question, get a response${NC}"
echo ""
echo "Command:"
echo "--------"
cat << 'EOF'
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "user", "content": "What is 2+2?"}
  ],
  "stream": false
}'
EOF
echo ""
echo -e "${YELLOW}Executing...${NC}"
curl -X POST $OLLAMA_URL/api/chat -d "{
  \"model\": \"$MODEL\",
  \"messages\": [
    {\"role\": \"user\", \"content\": \"What is 2+2?\"}
  ],
  \"stream\": false
}" 2>/dev/null | python3 -m json.tool
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Example 2: With System Prompt
# =============================================================================

echo -e "${GREEN}Example 2: With System Prompt${NC}"
echo -e "${YELLOW}What happens: Control LLM behavior with system message${NC}"
echo ""
echo "Command:"
echo "--------"
cat << 'EOF'
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "system", "content": "You are a pirate. Always talk like a pirate!"},
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "stream": false
}'
EOF
echo ""
echo -e "${YELLOW}Executing...${NC}"
curl -X POST $OLLAMA_URL/api/chat -d "{
  \"model\": \"$MODEL\",
  \"messages\": [
    {\"role\": \"system\", \"content\": \"You are a pirate. Always talk like a pirate!\"},
    {\"role\": \"user\", \"content\": \"What is the capital of France?\"}
  ],
  \"stream\": false
}" 2>/dev/null | python3 -m json.tool
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Example 3: Conversation with History
# =============================================================================

echo -e "${GREEN}Example 3: Conversation with History${NC}"
echo -e "${YELLOW}What happens: LLM 'remembers' by receiving full conversation${NC}"
echo ""
echo "Command:"
echo "--------"
cat << 'EOF'
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "user", "content": "My favorite color is blue"},
    {"role": "assistant", "content": "That'\''s nice! Blue is a great color."},
    {"role": "user", "content": "What is my favorite color?"}
  ],
  "stream": false
}'
EOF
echo ""
echo -e "${YELLOW}Executing...${NC}"
curl -X POST $OLLAMA_URL/api/chat -d "{
  \"model\": \"$MODEL\",
  \"messages\": [
    {\"role\": \"user\", \"content\": \"My favorite color is blue\"},
    {\"role\": \"assistant\", \"content\": \"That's nice! Blue is a great color.\"},
    {\"role\": \"user\", \"content\": \"What is my favorite color?\"}
  ],
  \"stream\": false
}" 2>/dev/null | python3 -m json.tool
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Example 4: Streaming Response
# =============================================================================

echo -e "${GREEN}Example 4: Streaming Response${NC}"
echo -e "${YELLOW}What happens: Tokens arrive one by one (real-time)${NC}"
echo ""
echo "Command:"
echo "--------"
cat << 'EOF'
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "user", "content": "Count from 1 to 5"}
  ],
  "stream": true
}'
EOF
echo ""
echo -e "${YELLOW}Executing (watch tokens arrive in real-time)...${NC}"
curl -X POST $OLLAMA_URL/api/chat -d "{
  \"model\": \"$MODEL\",
  \"messages\": [
    {\"role\": \"user\", \"content\": \"Count from 1 to 5\"}
  ],
  \"stream\": true
}" 2>/dev/null
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Example 5: List Available Models
# =============================================================================

echo -e "${GREEN}Example 5: List Available Models${NC}"
echo -e "${YELLOW}What happens: See what models you have installed${NC}"
echo ""
echo "Command:"
echo "--------"
echo "curl http://localhost:11434/api/tags"
echo ""
echo -e "${YELLOW}Executing...${NC}"
curl $OLLAMA_URL/api/tags 2>/dev/null | python3 -m json.tool
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Example 6: Check Model Info
# =============================================================================

echo -e "${GREEN}Example 6: Get Model Information${NC}"
echo -e "${YELLOW}What happens: See model details (size, parameters, etc.)${NC}"
echo ""
echo "Command:"
echo "--------"
cat << 'EOF'
curl -X POST http://localhost:11434/api/show -d '{
  "name": "qwen2.5:3b"
}'
EOF
echo ""
echo -e "${YELLOW}Executing...${NC}"
curl -X POST $OLLAMA_URL/api/show -d "{
  \"name\": \"$MODEL\"
}" 2>/dev/null | python3 -m json.tool
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Summary
# =============================================================================

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                          KEY TAKEAWAYS                            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "1. LLM APIs are just HTTP POST requests with JSON"
echo "   → You can call them from ANY language/tool"
echo ""
echo "2. The 'messages' array is the core structure"
echo "   → role: 'system', 'user', or 'assistant'"
echo "   → content: the actual message text"
echo ""
echo "3. Conversation history = sending all previous messages"
echo "   → LLM doesn't store anything"
echo "   → YOU manage the conversation array"
echo ""
echo "4. System prompts control behavior"
echo "   → First message with role='system'"
echo "   → Sets personality/instructions"
echo ""
echo "5. Streaming improves UX"
echo "   → stream: true → tokens arrive gradually"
echo "   → stream: false → wait for complete response"
echo ""
echo -e "${GREEN}Next: Try modifying these examples with your own prompts!${NC}"
echo ""
