#!/usr/bin/env python3
"""
Example 03: Chains with Memory - Conversational AI
===================================================

Master conversation memory - make your agent remember!

What you'll learn:
- Why memory is critical for agents
- ConversationBufferMemory (simple memory)
- ConversationSummaryMemory (compressed memory)
- ConversationChain (built-in conversation handler)
- Managing context windows
- Production memory patterns

This is CRITICAL for building real conversational agents!

Author: Beyhan MEYRALI
"""

from typing import List, Dict, Any
from langchain_ollama import OllamaLLM
from langchain.chains import ConversationChain, LLMChain
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory,
)
from langchain.prompts import PromptTemplate


class MemoryBasicsAgent:
    """
    Demonstrate basic memory concepts.

    Shows why memory is needed and how it works.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize agent."""
        print(f"\n[INIT] Creating agent with {model}...")
        self.llm = OllamaLLM(model=model, temperature=0.7)

    def demo_without_memory(self):
        """Show what happens WITHOUT memory."""
        print("\n" + "="*70)
        print("DEMO 1: Agent WITHOUT Memory (Goldfish Brain)")
        print("="*70)

        # Simple chain without memory
        prompt = PromptTemplate(
            template="Answer this question: {question}",
            input_variables=["question"]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        # Ask questions
        print("\n[User]: My name is Alice")
        response1 = chain.run(question="My name is Alice. Just say 'Nice to meet you'")
        print(f"[Agent]: {response1}")

        print("\n[User]: What's my name?")
        response2 = chain.run(question="What's my name?")
        print(f"[Agent]: {response2}")

        print("\n❌ Agent forgot! It has no memory of previous conversation.")

    def demo_with_buffer_memory(self):
        """Show what happens WITH buffer memory."""
        print("\n" + "="*70)
        print("DEMO 2: Agent WITH Buffer Memory (Remembers Everything)")
        print("="*70)

        # Create memory
        memory = ConversationBufferMemory()

        # Create conversation chain with memory
        conversation = ConversationChain(
            llm=self.llm,
            memory=memory,
            verbose=False
        )

        # Ask questions
        print("\n[User]: My name is Alice")
        response1 = conversation.predict(input="My name is Alice")
        print(f"[Agent]: {response1}")

        print("\n[User]: What's my name?")
        response2 = conversation.predict(input="What's my name?")
        print(f"[Agent]: {response2}")

        print("\n✅ Agent remembers! Memory is working.")

        # Show memory contents
        print("\n[MEMORY CONTENTS]:")
        print(memory.buffer)


class ConversationalAgent:
    """
    Production-ready conversational agent with memory.

    This demonstrates real-world conversation patterns.
    """

    def __init__(
        self,
        model: str = "qwen3:8b",
        memory_type: str = "buffer"
    ):
        """
        Initialize conversational agent.

        Args:
            model: Ollama model name
            memory_type: "buffer", "window", or "summary"
        """
        print(f"\n[INIT] Creating Conversational Agent...")
        print(f"  Model: {model}")
        print(f"  Memory type: {memory_type}")

        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = self._create_memory(memory_type)
        self.conversation = self._create_conversation()

        print("[INIT] ✅ Agent ready!")

    def _create_memory(self, memory_type: str):
        """Create appropriate memory type."""
        if memory_type == "buffer":
            # Remembers everything
            print("  Using ConversationBufferMemory (unlimited)")
            return ConversationBufferMemory()

        elif memory_type == "window":
            # Only remembers last K interactions
            print("  Using ConversationBufferWindowMemory (last 3 turns)")
            return ConversationBufferWindowMemory(k=3)

        elif memory_type == "summary":
            # Summarizes old conversations
            print("  Using ConversationSummaryMemory (compressed)")
            return ConversationSummaryMemory(llm=self.llm)

        else:
            raise ValueError(f"Unknown memory type: {memory_type}")

    def _create_conversation(self) -> ConversationChain:
        """Create conversation chain."""
        return ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=False
        )

    def chat(self, user_input: str) -> str:
        """
        Send a message and get response.

        Args:
            user_input: User's message

        Returns:
            Agent's response
        """
        print(f"\n[User]: {user_input}")

        try:
            response = self.conversation.predict(input=user_input)
            print(f"[Agent]: {response}")
            return response

        except Exception as e:
            error = f"Error: {str(e)}"
            print(f"[ERROR]: {error}")
            return error

    def show_memory(self):
        """Display current memory contents."""
        print("\n" + "-"*70)
        print("MEMORY CONTENTS:")
        print("-"*70)
        print(self.memory.buffer if hasattr(self.memory, 'buffer') else str(self.memory))
        print("-"*70)

    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()
        print("\n[SYSTEM]: Memory cleared!")


class AdvancedMemoryAgent:
    """
    Advanced memory patterns for production.

    Handles context window limits and long conversations.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize advanced agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)

        # Window memory to prevent context overflow
        self.memory = ConversationBufferWindowMemory(
            k=5,  # Remember last 5 turns
            return_messages=True
        )

        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory
        )

    def chat_with_metadata(self, user_input: str) -> Dict[str, Any]:
        """
        Chat and return metadata.

        Returns:
            Dictionary with response and memory info
        """
        response = self.conversation.predict(input=user_input)

        # Get memory stats
        memory_vars = self.memory.load_memory_variables({})

        return {
            "response": response,
            "memory_turns": len(self.memory.buffer) if hasattr(self.memory, 'buffer') else 0,
            "memory_content": str(memory_vars)
        }


def demo_memory_types():
    """Compare different memory types."""
    print("\n" + "="*70)
    print("DEMO 3: Comparing Memory Types")
    print("="*70)

    conversations = [
        "My favorite color is blue",
        "I live in Tokyo",
        "I work as a software engineer",
        "What's my favorite color?",
        "Where do I live?",
        "What's my job?",
    ]

    # Test each memory type
    for memory_type in ["buffer", "window"]:
        print(f"\n{'='*70}")
        print(f"Testing: {memory_type.upper()} Memory")
        print(f"{'='*70}")

        agent = ConversationalAgent(memory_type=memory_type)

        for msg in conversations:
            agent.chat(msg)

        agent.show_memory()


def demo_real_conversation():
    """Demonstrate realistic conversation."""
    print("\n" + "="*70)
    print("DEMO 4: Realistic Conversation Flow")
    print("="*70)

    agent = ConversationalAgent(memory_type="buffer")

    # Realistic conversation
    conversation = [
        "Hi! I'm working on a Python project",
        "I need to read a CSV file",
        "The file has names and ages",
        "How do I load it into a pandas DataFrame?",
        "What if the file has missing values?",
        "Can you show me how to handle those?",
        "Thanks! One more thing - what was my original question?",
    ]

    for msg in conversation:
        agent.chat(msg)

    print("\n💡 Notice how the agent:")
    print("  1. Remembers the context (Python, CSV, pandas)")
    print("  2. Builds on previous answers")
    print("  3. Can recall the original question")


def demo_context_window_management():
    """Show how to handle context window limits."""
    print("\n" + "="*70)
    print("DEMO 5: Context Window Management")
    print("="*70)

    print("\nWithout window limit:")
    agent1 = ConversationalAgent(memory_type="buffer")

    for i in range(8):
        agent1.chat(f"This is message {i+1}")

    agent1.show_memory()
    print("⚠️  All 8 messages in memory - could exceed context window!")

    print("\n" + "-"*70)
    print("\nWith window limit (k=3):")
    agent2 = ConversationalAgent(memory_type="window")

    for i in range(8):
        agent2.chat(f"This is message {i+1}")

    agent2.show_memory()
    print("✅ Only last 3 turns in memory - context window safe!")


def main():
    """Main entry point."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Example 03: Chains with Memory                            ║
║                                                                   ║
║  This demonstrates:                                              ║
║  • Why memory is critical for agents                            ║
║  • ConversationBufferMemory (unlimited)                         ║
║  • ConversationBufferWindowMemory (sliding window)              ║
║  • ConversationSummaryMemory (compressed)                       ║
║  • Production memory patterns                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Run demos
    basics = MemoryBasicsAgent()
    basics.demo_without_memory()
    basics.demo_with_buffer_memory()

    demo_memory_types()
    demo_real_conversation()
    demo_context_window_management()

    # Summary
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
    print("\n🎓 What you learned:")
    print("  1. Why agents need memory")
    print("  2. ConversationBufferMemory - remembers everything")
    print("  3. ConversationBufferWindowMemory - sliding window")
    print("  4. ConversationSummaryMemory - compressed history")
    print("  5. Managing context windows in production")
    print("\n📖 Memory Strategy Guide:")
    print("  • Short conversations → BufferMemory")
    print("  • Long conversations → WindowMemory or SummaryMemory")
    print("  • Production apps → WindowMemory (prevents context overflow)")
    print("  • Always monitor context window usage!")
    print("\n⚠️  Critical:")
    print("  LLMs have LIMITED context windows (e.g., 128K tokens)")
    print("  Without memory management, long conversations WILL FAIL!")
    print("\n➡️  Next: python 04_tools_integration.py")
    print("="*70)


if __name__ == "__main__":
    main()
