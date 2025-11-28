import operator
from typing import TypedDict, Annotated
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

# =============================================================================
# Comparison 02: LangGraph Implementation
# =============================================================================
#
# Task: Research -> Summarize -> Translate
# Approach: State Machine (Graph)
#
# This represents the "State" mental model.
# Nodes modify a shared state.
# =============================================================================

# 1. Define State
class AgentState(TypedDict):
    topic: str
    research_output: str
    summary_output: str
    final_output: str

def main():
    # 2. Setup LLM
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    # 3. Define Nodes (Functions)
    
    def research_node(state: AgentState):
        print("  [Graph] Researching...")
        topic = state["topic"]
        response = llm.invoke(f"Generate a brief research report about: {topic}. Include 3 key facts.")
        return {"research_output": response.content}

    def summarize_node(state: AgentState):
        print("  [Graph] Summarizing...")
        text = state["research_output"]
        response = llm.invoke(f"Summarize the following text into one concise sentence:\n\n{text}")
        return {"summary_output": response.content}

    def translate_node(state: AgentState):
        print("  [Graph] Translating...")
        text = state["summary_output"]
        response = llm.invoke(f"Translate the following sentence into Spanish:\n\n{text}")
        return {"final_output": response.content}

    # 4. Build Graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("researcher", research_node)
    workflow.add_node("summarizer", summarize_node)
    workflow.add_node("translator", translate_node)

    # Add edges (Linear flow)
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "summarizer")
    workflow.add_edge("summarizer", "translator")
    workflow.add_edge("translator", END)

    # Compile
    app = workflow.compile()

    # 5. Run
    topic = "The history of Pizza"
    print(f"\n🍕 Running LangGraph Workflow for topic: '{topic}'...\n")
    
    inputs = {"topic": topic}
    result = app.invoke(inputs)
    
    print("="*50)
    print("FINAL OUTPUT (Spanish Translation)")
    print("="*50)
    print(result["final_output"])

if __name__ == "__main__":
    main()
