#!/usr/bin/env python3
"""
Example 03: Chains with Memory - Conversational AI (Modern LCEL)
=================================================================

Master conversation memory - make your agent remember!

What you'll learn:
- Why memory is critical for agents
- RunnableWithMessageHistory (Modern LCEL memory)
- Managing chat history
- Production memory patterns

This is CRITICAL for building real conversational agents!

Author: Beyhan MEYRALI
"""

from typing import List, Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# Global store for chat histories (in-memory for demo)
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Get or create chat history for a session."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


class MemoryBasicsAgent:
    """
    Demonstrate basic memory concepts using LCEL.
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
        prompt = ChatPromptTemplate.from_template("Answer this question: {question}")
        chain = prompt | self.llm | StrOutputParser()

        # Ask questions
        print("\n[User]: My name is Alice")
        response1 = chain.invoke({"question": "My name is Alice. Just say 'Nice to meet you'"})
        print(f"[Agent]: {response1}")

        print("\n[User]: What's my name?")
        response2 = chain.invoke({"question": "What's my name?"})
        print(f"[Agent]: {response2}")

        print("\n❌ Agent forgot! It has no memory of previous conversation.")

    def demo_with_memory(self):
        """Show what happens WITH memory (LCEL)."""
        print("\n" + "="*70)
        print("DEMO 2: Agent WITH Memory (Remembers Everything)")
        print("="*70)

        # 1. Create prompt with history placeholder
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ])

        # 2. Create chain
        chain = prompt | self.llm | StrOutputParser()

        # 3. Wrap with message history
        conversation = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )

        # Ask questions with session_id
        session_id = "demo_session"
        
        print("\n[User]: My name is Alice")
        response1 = conversation.invoke(
            {"question": "My name is Alice"},
            config={"configurable": {"session_id": session_id}}
        )
        print(f"[Agent]: {response1}")

        print("\n[User]: What's my name?")
        response2 = conversation.invoke(
            {"question": "What's my name?"},
            config={"configurable": {"session_id": session_id}}
        )
        print(f"[Agent]: {response2}")

        print("\n✅ Agent remembers! Memory is working.")

        # Show memory contents
        print("\n[MEMORY CONTENTS]:")
        print(store[session_id].messages)


class ConversationalAgent:
    """
    Production-ready conversational agent with memory.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize conversational agent."""
        print(f"\n[INIT] Creating Conversational Agent...")
        self.llm = OllamaLLM(model=model, temperature=0.7)
        
        # Setup chain
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        self.conversation = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def chat(self, user_input: str, session_id: str = "default") -> str:
        """Send a message and get response."""
        print(f"\n[User]: {user_input}")

        try:
            response = self.conversation.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
            )
            print(f"[Agent]: {response}")
            return response

        except Exception as e:
            error = f"Error: {str(e)}"
            print(f"[ERROR]: {error}")
            return error

    def show_memory(self, session_id: str = "default"):
        """Display current memory contents."""
        print("\n" + "-"*70)
        print(f"MEMORY CONTENTS ({session_id}):")
        print("-"*70)
        if session_id in store:
            for msg in store[session_id].messages:
                print(f"{msg.type}: {msg.content}")
        else:
            print("Empty memory")
        print("-"*70)

    def clear_memory(self, session_id: str = "default"):
        """Clear conversation memory."""
        if session_id in store:
            store[session_id].clear()
        print(f"\n[SYSTEM]: Memory cleared for {session_id}!")


def demo_real_conversation():
    """Demonstrate realistic conversation."""
    print("\n" + "="*70)
    print("DEMO 3: Realistic Conversation Flow")
    print("="*70)

    agent = ConversationalAgent()
    session_id = "user_123"

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
        agent.chat(msg, session_id=session_id)

    print("\n💡 Notice how the agent:")
    print("  1. Remembers the context (Python, CSV, pandas)")
    print("  2. Builds on previous answers")
    print("  3. Can recall the original question")


def main():
    """Main entry point."""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║         Example 03: Chains with Memory (Modern LCEL)              ║
    ║                                                                   ║
    ║  This demonstrates:                                              ║
    ║  • Why memory is critical for agents                            ║
    ║  • RunnableWithMessageHistory (The modern way)                  ║
    ║  • ChatMessageHistory (Storing messages)                        ║
    ║  • Managing sessions                                            ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Run demos
    basics = MemoryBasicsAgent()
    basics.demo_without_memory()
    basics.demo_with_memory()

    demo_real_conversation()

    # Summary
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
    print("\n🎓 What you learned:")
    print("  1. Why agents need memory")
    print("  2. How to use RunnableWithMessageHistory")
    print("  3. How to manage session IDs")
    print("  4. How to inspect chat history")
    print("\n➡️  Next: python 04_tools_integration.py")
    print("="*70)


if __name__ == "__main__":
    main()
