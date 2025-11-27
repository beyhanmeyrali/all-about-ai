# 01 - Tool Calling: Giving LLMs Superpowers 🔧

> Transform LLMs from chatbots into agents that can interact with the real world

---

## 🎯 Learning Objectives

By the end of this section, you will understand:
- ✅ What tool/function calling actually is
- ✅ How LLMs decide when to use tools
- ✅ **Recursive/agentic tool calling** (the game-changer!)
- ✅ Building real-world tool integrations
- ✅ Error handling and retry logic
- ✅ Multi-step tool orchestration

**Time Required:** 3-4 hours

---

## 🧠 Critical Concept: Tool Calling Is NOT Execution

### What Is Tool Calling?

**The Big Misconception:**
```
❌ WRONG: "The LLM calls the weather API"
✅ RIGHT: "The LLM outputs JSON saying 'please call weather API with these args'"
```

**How It Actually Works:**

```python
# Step 1: You ask a question
user: "What's the weather in Tokyo?"

# Step 2: LLM responds with a tool call (just JSON!)
llm_response = {
    "tool_calls": [{
        "function": "get_weather",
        "arguments": {"city": "Tokyo"}
    }]
}

# Step 3: YOU execute the function (not the LLM!)
weather = get_weather("Tokyo")  # You run this code

# Step 4: You send the result back to the LLM
messages.append({"role": "tool", "content": weather})
final = llm.chat(messages)

# Step 5: LLM uses tool result to generate natural language
llm: "The weather in Tokyo is sunny, 25°C"
```

**The LLM never executes code!** It just:
1. Recognizes when a tool would be helpful
2. Outputs structured JSON with function name + arguments
3. Waits for YOU to run the function and send back results

---

## 🔄 The Agent Loop: Recursive Tool Calling

### Single Tool Call vs Recursive (Agentic)

**Simple Tool Call:**
```
User → LLM → Tool Call → Execute → LLM → Answer
         (one time)
```

**Recursive/Agentic Tool Call:**
```
User → LLM → Tool Call → Execute → LLM → Tool Call → Execute → LLM → Answer
              ↑______________________________|  ↑_______________________|
                     (can repeat!)                  (can repeat!)
```

### Example: Multi-Step Task

**Question:** "What's the weather in my manager's city?"

**Simple approach:** Can't do it (would need 2 tool calls)

**Recursive approach:**
```python
# Step 1: LLM calls get_my_manager()
manager = get_my_manager()  # Returns: {"name": "Alice", "city": "Paris"}

# Step 2: LLM sees result, calls get_weather()
weather = get_weather("Paris")  # Returns: {"temp": 18, "condition": "cloudy"}

# Step 3: LLM combines results
"Your manager Alice is in Paris where it's currently 18°C and cloudy."
```

**This is what makes LLMs "agents"!** They can:
- Chain multiple tools together
- Use output of one tool as input to another
- Solve complex multi-step tasks autonomously

---

## 📚 What This Section Covers

### Files in This Directory

```
01-tool-calling/
├── README.md                          ← You are here
├── requirements.txt                   ← Python dependencies
├── 01_basic_weather_tool.py          ← Simple single tool
├── 02_multiple_tools.py              ← Multiple tool options
├── 03_recursive_agent.py             ← The powerful agent loop!
├── 04_erp_integration.py             ← Real-world ERP example
├── 05_error_handling.py              ← Robust tool calling
├── 06_curl_examples.sh               ← HTTP layer examples
└── tools/
    ├── weather.py                    ← Weather API tool
    ├── database.py                   ← Database query tools
    └── erp_simulator.py              ← ERP system simulation
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd 01-tool-calling
pip install -r requirements.txt
```

### 2. Make Sure Ollama Is Running

```bash
# Verify Ollama
curl http://localhost:11434/api/tags

# Make sure you have qwen2.5:3b
ollama pull qwen2.5:3b
```

### 3. Run First Example

```bash
python 01_basic_weather_tool.py
```

---

## 📖 Detailed Examples

### Example 1: Basic Weather Tool (01_basic_weather_tool.py)

**What You'll Learn:**
- Defining tool schemas for LLMs
- How LLMs parse tool calls from responses
- Sending tool results back to LLM

**Key Code:**
```python
# Define tool schema (tells LLM what tools are available)
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name"
                }
            },
            "required": ["city"]
        }
    }
}]

# Send to LLM with tools
response = llm.chat(messages, tools=tools)

# LLM might respond with a tool call
if response.tool_calls:
    tool_call = response.tool_calls[0]
    city = tool_call.arguments['city']

    # YOU execute the function
    weather = get_weather(city)

    # Send result back
    messages.append({"role": "tool", "content": weather})
    final = llm.chat(messages, tools=tools)
```

**curl Example:**
```bash
# Step 1: Send question with tools available
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [{"role": "user", "content": "Weather in Tokyo?"}],
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get weather",
      "parameters": {
        "type": "object",
        "properties": {
          "city": {"type": "string"}
        }
      }
    }
  }]
}'
```

---

### Example 2: Multiple Tools (02_multiple_tools.py)

**What You'll Learn:**
- Giving LLM multiple tool options
- How LLM chooses the right tool
- Handling different tool signatures

**Available Tools:**
- `get_weather(city)` - Weather information
- `search_web(query)` - Web search
- `calculate(expression)` - Math calculations

**Key Insight:**
The LLM chooses which tool to use based on:
- Tool descriptions
- User query context
- Parameter requirements

---

### Example 3: Recursive Agent (03_recursive_agent.py) ⭐

**What You'll Learn:**
- Building the agent loop
- Handling multi-step tool orchestration
- When to stop recursing

**The Agent Loop:**
```python
def agent_loop(user_message):
    """
    The recursive agent that can use tools multiple times.
    This is what transforms an LLM into an AGENT!
    """

    messages = [{"role": "user", "content": user_message}]
    max_iterations = 10  # Prevent infinite loops

    for iteration in range(max_iterations):
        # Call LLM
        response = llm.chat(messages, tools=tools)

        # Check if LLM wants to use a tool
        if response.tool_calls:
            print(f"[AGENT] Iteration {iteration + 1}: Using tools...")

            # Execute each tool the LLM requested
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                arguments = tool_call.arguments

                # Execute the tool
                result = execute_tool(function_name, arguments)

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Continue loop - LLM might call more tools!
            continue

        else:
            # No more tool calls - LLM has final answer
            print(f"[AGENT] Finished after {iteration + 1} iterations")
            return response.content

    print("[AGENT] Max iterations reached!")
    return "Task too complex, exceeded iteration limit"
```

**Example Execution:**
```
User: "What's the weather in my manager's city?"

[AGENT] Iteration 1: Using tools...
  → Calling get_my_manager()
  → Result: {"name": "Alice", "city": "Paris"}

[AGENT] Iteration 2: Using tools...
  → Calling get_weather(city="Paris")
  → Result: {"temp": 18, "condition": "cloudy"}

[AGENT] Finished after 2 iterations
Final: "Your manager Alice is in Paris where it's 18°C and cloudy."
```

---

### Example 4: ERP Integration (04_erp_integration.py)

**What You'll Learn:**
- Real-world business tool integration
- Complex, nested tool calls
- Handling structured data

**Adapted from your chameleon examples!**

**Available Tools:**
- `get_employees_by_manager(manager_id)` - Get team members
- `get_payroll_by_employee(employee_id)` - Get salary info
- `update_payroll(employee_id, salary, bonus)` - Update payroll

**Complex Query Example:**
```
User: "Get the total payroll cost for manager with ID 2's team"

Agent execution:
1. get_employees_by_manager(2)
   → Returns 5 employees
2. get_payroll_by_employee(emp1)
3. get_payroll_by_employee(emp2)
4. get_payroll_by_employee(emp3)
5. get_payroll_by_employee(emp4)
6. get_payroll_by_employee(emp5)
7. Calculate total and respond

Total: 6 tool calls orchestrated automatically!
```

---

### Example 5: Error Handling (05_error_handling.py)

**What You'll Learn:**
- Handling tool execution failures
- Retry logic
- Providing error context to LLM

**Common Error Scenarios:**
```python
# Scenario 1: Invalid parameters
try:
    weather = get_weather(city="XYZ123")  # Invalid city
except ValueError as e:
    # Send error back to LLM
    messages.append({
        "role": "tool",
        "content": f"Error: {str(e)}. Please try with a valid city name."
    })
    # LLM can retry with corrected parameters!

# Scenario 2: API timeout
try:
    result = call_external_api(params)
except TimeoutError:
    # Inform LLM about timeout
    messages.append({
        "role": "tool",
        "content": "API timeout. Service may be unavailable."
    })
    # LLM can suggest alternative or acknowledge limitation

# Scenario 3: Permission denied
try:
    data = access_database(query)
except PermissionError:
    messages.append({
        "role": "tool",
        "content": "Access denied. You don't have permission for this operation."
    })
```

**Smart LLMs can:**
- Retry with different parameters
- Use alternative tools
- Explain limitations to users

---

## 🎯 Key Patterns

### Pattern 1: Simple Tool Call
```
User → LLM → Tool → LLM → Response
```
Use when: Single operation needed

### Pattern 2: Recursive Agent
```
User → LLM → Tool → LLM → Tool → LLM → Response
              ↑_______________|
```
Use when: Multi-step tasks, complex queries

### Pattern 3: Parallel Tools
```
User → LLM → [Tool1, Tool2, Tool3] → LLM → Response
```
Use when: Multiple independent operations

### Pattern 4: Sequential Pipeline
```
User → LLM → Tool1 → LLM → Tool2(uses Tool1 output) → LLM → Response
```
Use when: Each step depends on previous result

---

## 🐛 Debugging Tips

### Tool Not Being Called?

**Check:**
1. Tool description is clear
2. User query matches tool purpose
3. LLM has tools parameter in request

```python
# Debug: Print what tools LLM sees
print("Available tools:", json.dumps(tools, indent=2))
```

### Wrong Parameters?

**Fix tool schema:**
```python
# ❌ Vague description
"description": "Get data"

# ✅ Clear description
"description": "Get current weather for a specific city. Returns temperature in Celsius and weather condition."
```

### Infinite Loop?

**Add iteration limit:**
```python
MAX_ITERATIONS = 10

for i in range(MAX_ITERATIONS):
    response = llm.chat(messages, tools=tools)
    if not response.tool_calls:
        break
else:
    print("Warning: Max iterations reached!")
```

### Tool Call Parsing Errors?

**Validate tool response:**
```python
def execute_tool(name, args):
    try:
        # Validate arguments
        if name == "get_weather":
            if "city" not in args:
                return "Error: Missing 'city' parameter"

        # Execute tool
        result = tools[name](**args)
        return json.dumps(result)

    except Exception as e:
        # Return error as tool result
        return f"Error executing {name}: {str(e)}"
```

---

## 📊 Performance Tips

### 1. Minimize Tool Calls

```python
# ❌ Bad: Multiple calls for same data
weather_tokyo = get_weather("Tokyo")
weather_paris = get_weather("Paris")

# ✅ Good: Batch tool that handles multiple cities
weather = get_weather_batch(["Tokyo", "Paris"])
```

### 2. Cache Tool Results

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_weather(city):
    # Results cached for repeated calls
    return fetch_weather_api(city)
```

### 3. Timeout Tool Calls

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Tool execution timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)  # 10 second timeout

try:
    result = slow_tool_function()
finally:
    signal.alarm(0)  # Cancel timeout
```

---

## 🚀 Next Steps

### You're Ready For:
✅ [02-agent-frameworks](../02-agent-frameworks) - Use LangGraph & CrewAI for production agents

### Practice Exercises:

1. **Add a new tool** to `02_multiple_tools.py`
2. **Build a calculator agent** that can do multi-step math
3. **Create a database agent** that can query and update records
4. **Implement retry logic** when tools fail

---

## 📚 Additional Resources

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Ollama Tool Calling Docs](https://github.com/ollama/ollama/blob/main/docs/api.md#tools)
- [Your chameleon examples](../../chameleon/basics) - Real-world patterns

---

**Next:** [02-agent-frameworks](../02-agent-frameworks) - Professional agent development with LangGraph →
