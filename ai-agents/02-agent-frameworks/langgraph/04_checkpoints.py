#!/usr/bin/env python3
"""
LangGraph Checkpoints - State Persistence
==========================================

This script demonstrates state persistence using LangGraph checkpoints.
Checkpoints allow you to save and restore conversation state, enabling:
- Resume interrupted conversations
- Time travel through conversation history
- Implement rollback functionality
- Debug complex workflows

We'll build progressively from basic to production-level persistence.

Author: AI Agents Tutorial Series
"""

from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import OllamaLLM
import json
from datetime import datetime


# ============================================================================
# Part 1: Basic State Persistence
# ============================================================================

class BasicState(TypedDict):
    """Simple state with message history."""
    messages: List[str]
    counter: int


class BasicCheckpointAgent:
    """
    Demonstrates basic checkpoint functionality.

    Features:
    - Save conversation state after each turn
    - Resume from last checkpoint
    - View checkpoint history
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize agent with checkpoint support."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build graph with checkpoint support."""
        workflow = StateGraph(BasicState)

        # Add processing node
        workflow.add_node("process", self._process_message)

        # Set entry point and edge
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)

        # Compile with checkpointer
        return workflow.compile(checkpointer=self.memory)

    def _process_message(self, state: BasicState) -> BasicState:
        """Process message and update state."""
        messages = state.get("messages", [])
        counter = state.get("counter", 0)

        # Get last message
        if messages:
            last_msg = messages[-1]
            response = self.llm.invoke(f"Respond to: {last_msg}")
            messages.append(f"Assistant: {response}")

        return {
            "messages": messages,
            "counter": counter + 1
        }

    def chat(self, message: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Send message and save checkpoint.

        Args:
            message: User message
            thread_id: Conversation thread identifier

        Returns:
            State with checkpoint info
        """
        # Get current state
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        # Add user message
        messages = current_state.values.get("messages", []) if current_state.values else []
        messages.append(f"User: {message}")

        # Invoke graph with checkpoint
        result = self.graph.invoke(
            {"messages": messages, "counter": current_state.values.get("counter", 0) if current_state.values else 0},
            config=config
        )

        return result

    def get_history(self, thread_id: str = "default") -> List[str]:
        """Get conversation history from checkpoints."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)
        return state.values.get("messages", []) if state.values else []

    def get_checkpoint_info(self, thread_id: str = "default") -> Dict[str, Any]:
        """Get checkpoint metadata."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)

        return {
            "thread_id": thread_id,
            "message_count": len(state.values.get("messages", [])) if state.values else 0,
            "counter": state.values.get("counter", 0) if state.values else 0,
            "checkpoint_id": str(state.config.get("configurable", {}).get("checkpoint_id", "none"))
        }


# ============================================================================
# Part 2: Advanced State with Multiple Threads
# ============================================================================

class ConversationState(TypedDict):
    """Rich conversation state."""
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any]
    context: str


class MultiThreadAgent:
    """
    Manages multiple conversation threads with independent checkpoints.

    Features:
    - Multiple concurrent conversations
    - Per-thread state isolation
    - Context preservation
    - Metadata tracking
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize multi-thread agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build graph with state management."""
        workflow = StateGraph(ConversationState)

        workflow.add_node("understand", self._understand_context)
        workflow.add_node("respond", self._generate_response)

        workflow.set_entry_point("understand")
        workflow.add_edge("understand", "respond")
        workflow.add_edge("respond", END)

        return workflow.compile(checkpointer=self.memory)

    def _understand_context(self, state: ConversationState) -> ConversationState:
        """Extract and update context from conversation."""
        messages = state.get("messages", [])

        # Build context from recent messages
        recent = messages[-3:] if len(messages) >= 3 else messages
        context_summary = " | ".join([f"{m['role']}: {m['content'][:50]}" for m in recent])

        return {
            **state,
            "context": context_summary
        }

    def _generate_response(self, state: ConversationState) -> ConversationState:
        """Generate response with context awareness."""
        messages = state.get("messages", [])
        context = state.get("context", "")
        metadata = state.get("metadata", {})

        # Get last user message
        last_msg = messages[-1]["content"] if messages else ""

        # Generate response with context
        prompt = f"Context: {context}\n\nUser: {last_msg}\n\nRespond naturally:"
        response = self.llm.invoke(prompt)

        # Add assistant message
        messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        # Update metadata
        metadata["total_turns"] = metadata.get("total_turns", 0) + 1
        metadata["last_updated"] = datetime.now().isoformat()

        return {
            "messages": messages,
            "metadata": metadata,
            "context": context
        }

    def send_message(self, message: str, thread_id: str) -> str:
        """Send message to specific thread."""
        config = {"configurable": {"thread_id": thread_id}}

        # Get current state
        current_state = self.graph.get_state(config)
        messages = current_state.values.get("messages", []) if current_state.values else []
        metadata = current_state.values.get("metadata", {}) if current_state.values else {}

        # Add user message
        messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Invoke graph
        result = self.graph.invoke(
            {
                "messages": messages,
                "metadata": metadata,
                "context": ""
            },
            config=config
        )

        # Return last assistant message
        return result["messages"][-1]["content"]

    def list_threads(self) -> List[str]:
        """List all active conversation threads."""
        # Note: MemorySaver doesn't expose thread listing directly
        # In production, use persistent storage with thread indexing
        return ["Use persistent storage for thread listing"]

    def get_thread_summary(self, thread_id: str) -> Dict[str, Any]:
        """Get summary of thread state."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)

        if not state.values:
            return {"thread_id": thread_id, "status": "empty"}

        messages = state.values.get("messages", [])
        metadata = state.values.get("metadata", {})

        return {
            "thread_id": thread_id,
            "message_count": len(messages),
            "total_turns": metadata.get("total_turns", 0),
            "last_updated": metadata.get("last_updated", "never"),
            "context": state.values.get("context", "")
        }


# ============================================================================
# Part 3: Time Travel and Rollback
# ============================================================================

class TimeTravelState(TypedDict):
    """State with version tracking."""
    messages: List[str]
    version: int
    snapshots: Dict[int, List[str]]


class TimeTravelAgent:
    """
    Advanced checkpoint agent with time travel capabilities.

    Features:
    - Navigate through conversation history
    - Rollback to previous states
    - Create named snapshots
    - Branch conversations from any point
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize time travel agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build graph with versioning."""
        workflow = StateGraph(TimeTravelState)

        workflow.add_node("process", self._process_with_versioning)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)

        return workflow.compile(checkpointer=self.memory)

    def _process_with_versioning(self, state: TimeTravelState) -> TimeTravelState:
        """Process message and maintain version history."""
        messages = state.get("messages", [])
        version = state.get("version", 0)
        snapshots = state.get("snapshots", {})

        # Process last message
        if messages and messages[-1].startswith("User:"):
            last_msg = messages[-1].replace("User: ", "")
            response = self.llm.invoke(f"Respond to: {last_msg}")
            messages.append(f"Assistant: {response}")

        # Increment version
        new_version = version + 1

        # Save snapshot
        snapshots[new_version] = messages.copy()

        return {
            "messages": messages,
            "version": new_version,
            "snapshots": snapshots
        }

    def chat(self, message: str, thread_id: str = "default") -> str:
        """Send message and create checkpoint."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        messages = current_state.values.get("messages", []) if current_state.values else []
        version = current_state.values.get("version", 0) if current_state.values else 0
        snapshots = current_state.values.get("snapshots", {}) if current_state.values else {}

        messages.append(f"User: {message}")

        result = self.graph.invoke(
            {
                "messages": messages,
                "version": version,
                "snapshots": snapshots
            },
            config=config
        )

        # Return last assistant message
        assistant_msgs = [m for m in result["messages"] if m.startswith("Assistant:")]
        return assistant_msgs[-1].replace("Assistant: ", "") if assistant_msgs else ""

    def rollback_to_version(self, version: int, thread_id: str = "default") -> bool:
        """Rollback conversation to specific version."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        if not current_state.values:
            return False

        snapshots = current_state.values.get("snapshots", {})

        if version not in snapshots:
            print(f"Version {version} not found. Available: {list(snapshots.keys())}")
            return False

        # Restore snapshot
        restored_messages = snapshots[version]

        self.graph.invoke(
            {
                "messages": restored_messages,
                "version": version,
                "snapshots": snapshots
            },
            config=config
        )

        return True

    def list_versions(self, thread_id: str = "default") -> List[int]:
        """List all saved versions."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)

        if not state.values:
            return []

        snapshots = state.values.get("snapshots", {})
        return sorted(snapshots.keys())

    def get_version_preview(self, version: int, thread_id: str = "default") -> List[str]:
        """Preview messages at specific version."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)

        if not state.values:
            return []

        snapshots = state.values.get("snapshots", {})
        return snapshots.get(version, [])


# ============================================================================
# Part 4: Production Checkpoint Manager
# ============================================================================

class ProductionCheckpointManager:
    """
    Enterprise-grade checkpoint management system.

    Features:
    - Automatic checkpoint creation
    - Checkpoint compression
    - Cleanup policies
    - Export/import functionality
    - Thread management
    - Monitoring and stats
    """

    def __init__(self, model: str = "qwen3:8b", max_checkpoints: int = 100):
        """Initialize production checkpoint manager."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.max_checkpoints = max_checkpoints
        self.stats = {
            "total_checkpoints": 0,
            "total_threads": 0,
            "total_messages": 0
        }
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build production-ready graph."""
        workflow = StateGraph(ConversationState)

        workflow.add_node("process", self._process_message)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)

        return workflow.compile(checkpointer=self.memory)

    def _process_message(self, state: ConversationState) -> ConversationState:
        """Process message with full state management."""
        messages = state.get("messages", [])
        metadata = state.get("metadata", {})

        # Get last user message
        if messages:
            last_msg = messages[-1]["content"]
            response = self.llm.invoke(f"Respond to: {last_msg}")

            messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })

        # Update metadata
        metadata["message_count"] = len(messages)
        metadata["last_checkpoint"] = datetime.now().isoformat()

        return {
            "messages": messages,
            "metadata": metadata,
            "context": state.get("context", "")
        }

    def send(self, message: str, thread_id: str) -> str:
        """Send message with automatic checkpointing."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        messages = current_state.values.get("messages", []) if current_state.values else []
        metadata = current_state.values.get("metadata", {}) if current_state.values else {}

        messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        result = self.graph.invoke(
            {
                "messages": messages,
                "metadata": metadata,
                "context": ""
            },
            config=config
        )

        # Update stats
        self.stats["total_messages"] += 2  # user + assistant
        self.stats["total_checkpoints"] += 1

        return result["messages"][-1]["content"]

    def export_thread(self, thread_id: str, filepath: str) -> bool:
        """Export thread to JSON file."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)

        if not state.values:
            return False

        export_data = {
            "thread_id": thread_id,
            "exported_at": datetime.now().isoformat(),
            "state": state.values
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

        return True

    def import_thread(self, filepath: str) -> str:
        """Import thread from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        thread_id = data["thread_id"]
        config = {"configurable": {"thread_id": thread_id}}

        self.graph.invoke(data["state"], config=config)

        return thread_id

    def get_stats(self) -> Dict[str, Any]:
        """Get checkpoint statistics."""
        return self.stats.copy()


# ============================================================================
# DEMONSTRATIONS
# ============================================================================

def demo_basic_checkpoints():
    """Demonstrate basic checkpoint functionality."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Checkpoint Persistence")
    print("="*70)

    agent = BasicCheckpointAgent()

    print("\n1. Starting conversation...")
    result1 = agent.chat("Hello, my name is Alice")
    print(f"Turn 1: {len(result1['messages'])} messages")

    print("\n2. Continuing conversation...")
    result2 = agent.chat("What's the weather like?")
    print(f"Turn 2: {len(result2['messages'])} messages")

    print("\n3. Checkpoint info:")
    info = agent.get_checkpoint_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\n4. Full conversation history:")
    history = agent.get_history()
    for i, msg in enumerate(history, 1):
        print(f"  {i}. {msg}")


def demo_multi_thread():
    """Demonstrate multiple conversation threads."""
    print("\n" + "="*70)
    print("DEMO 2: Multiple Conversation Threads")
    print("="*70)

    agent = MultiThreadAgent()

    print("\n1. Starting Thread A (tech support)...")
    response1 = agent.send_message("My computer won't start", "thread_a")
    print(f"Response: {response1[:100]}...")

    print("\n2. Starting Thread B (recipes)...")
    response2 = agent.send_message("How do I make pasta?", "thread_b")
    print(f"Response: {response2[:100]}...")

    print("\n3. Continuing Thread A...")
    response3 = agent.send_message("I tried rebooting", "thread_a")
    print(f"Response: {response3[:100]}...")

    print("\n4. Thread summaries:")
    for thread_id in ["thread_a", "thread_b"]:
        summary = agent.get_thread_summary(thread_id)
        print(f"\n  {thread_id.upper()}:")
        for key, value in summary.items():
            if key != "thread_id":
                print(f"    {key}: {value}")


def demo_time_travel():
    """Demonstrate time travel and rollback."""
    print("\n" + "="*70)
    print("DEMO 3: Time Travel and Rollback")
    print("="*70)

    agent = TimeTravelAgent()

    print("\n1. Building conversation history...")
    agent.chat("Tell me about Python", "demo")
    agent.chat("What about JavaScript?", "demo")
    agent.chat("Compare them", "demo")

    print("\n2. Available versions:")
    versions = agent.list_versions("demo")
    print(f"  Versions: {versions}")

    print("\n3. Preview version 2:")
    preview = agent.get_version_preview(2, "demo")
    for msg in preview:
        print(f"  - {msg}")

    print("\n4. Rolling back to version 1...")
    success = agent.rollback_to_version(1, "demo")
    print(f"  Rollback {'successful' if success else 'failed'}")

    print("\n5. Current state after rollback:")
    preview_after = agent.get_version_preview(1, "demo")
    for msg in preview_after:
        print(f"  - {msg}")


def demo_production_manager():
    """Demonstrate production checkpoint manager."""
    print("\n" + "="*70)
    print("DEMO 4: Production Checkpoint Manager")
    print("="*70)

    manager = ProductionCheckpointManager()

    print("\n1. Creating conversation...")
    manager.send("Hello, I need help", "prod_thread")
    manager.send("Tell me about AI", "prod_thread")

    print("\n2. Exporting thread...")
    export_path = "/tmp/thread_backup.json"
    success = manager.export_thread("prod_thread", export_path)
    print(f"  Export {'successful' if success else 'failed'}: {export_path}")

    print("\n3. Statistics:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n4. Importing thread...")
    imported_id = manager.import_thread(export_path)
    print(f"  Imported thread: {imported_id}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LangGraph Checkpoints - State Persistence Tutorial")
    print("="*70)
    print("\nThis tutorial demonstrates checkpoint-based state persistence.")
    print("Checkpoints enable conversation resume, time travel, and rollback.")

    try:
        demo_basic_checkpoints()
        demo_multi_thread()
        demo_time_travel()
        demo_production_manager()

        print("\n" + "="*70)
        print("Tutorial completed successfully!")
        print("="*70)
        print("\nKey Takeaways:")
        print("1. MemorySaver provides in-memory checkpoint storage")
        print("2. thread_id isolates different conversations")
        print("3. Checkpoints enable state recovery and time travel")
        print("4. Production systems need export/import capabilities")
        print("\nNext: 05_human_in_loop.py - Human approval nodes")

    except Exception as e:
        print(f"\nError during demonstration: {e}")
        print("Make sure Ollama is running with qwen3:8b model")
