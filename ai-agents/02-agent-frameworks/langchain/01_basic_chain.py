#!/usr/bin/env python3
"""
Example 01: Basic LangChain - Your First Chain
===============================================

This is the SIMPLEST LangChain example possible.
Learn the fundamental concepts: LLM, Prompt, Chain.

What you'll learn:
- How to create an LLM instance
- How to create a simple prompt
- How to chain them together
- How to invoke the chain

This is your "Hello World" for LangChain!

DEBUGGING TIPS:
--------------
1. If OllamaLLM not found:
   pip install langchain-ollama

2. If connection fails:
   - Check Ollama is running: ollama serve
   - Check model exists: ollama list

3. To see what's happening:
   - Set verbose=True in LLMChain
   - Add print() statements

Author: Beyhan MEYRALI
"""

from typing import Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain


class BasicChainAgent:
    """
    A simple LangChain agent that answers questions.

    This demonstrates the most basic LangChain pattern:
    Prompt → LLM → Response

    Attributes:
        llm: The language model instance
        prompt_template: Template for formatting prompts
        chain: The LLMChain that ties everything together
    """

    def __init__(self, model: str = "qwen3:8b", temperature: float = 0.7):
        """
        Initialize the basic chain agent.

        Args:
            model: Ollama model name
            temperature: LLM temperature (0.0 = deterministic, 1.0 = creative)
        """
        print(f"\n[INIT] Creating BasicChainAgent with {model}...")

        # Step 1: Create LLM instance
        self.llm = self._create_llm(model, temperature)

        # Step 2: Create prompt template
        self.prompt_template = self._create_prompt_template()

        # Step 3: Create the chain
        self.chain = self._create_chain()

        print("[INIT] ✅ Agent initialized successfully!")

    def _create_llm(self, model: str, temperature: float) -> OllamaLLM:
        """
        Create an Ollama LLM instance.

        This is the core component that talks to Ollama.

        Args:
            model: Model name
            temperature: Creativity level

        Returns:
            Configured OllamaLLM instance
        """
        print(f"  Creating LLM: {model} (temperature={temperature})")

        llm = OllamaLLM(
            model=model,
            temperature=temperature,
            # base_url="http://localhost:11434",  # Default, can customize
        )

        return llm

    def _create_prompt_template(self) -> PromptTemplate:
        """
        Create a prompt template.

        Templates allow us to reuse prompts with different inputs.

        Returns:
            PromptTemplate instance
        """
        print("  Creating prompt template...")

        template = """You are a helpful AI assistant.

User question: {question}

Please provide a clear and concise answer."""

        prompt = PromptTemplate(
            template=template,
            input_variables=["question"]
        )

        return prompt

    def _create_chain(self) -> LLMChain:
        """
        Create the LLMChain.

        This combines the prompt and LLM into a reusable chain.

        Returns:
            Configured LLMChain
        """
        print("  Creating LLMChain...")

        chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            verbose=False,  # Set to True to see what's happening
        )

        return chain

    def ask(self, question: str) -> str:
        """
        Ask a question and get an answer.

        This is the main method you'll use.

        Args:
            question: The question to ask

        Returns:
            The LLM's answer
        """
        print(f"\n[ASKING] {question}")

        try:
            # Run the chain
            response = self.chain.run(question=question)

            print(f"[ANSWER] {response[:100]}...")
            return response

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return error_msg

    def ask_with_details(self, question: str) -> Dict[str, Any]:
        """
        Ask a question and get detailed information.

        This shows you what's happening under the hood.

        Args:
            question: The question to ask

        Returns:
            Dictionary with question, answer, and metadata
        """
        print(f"\n[DETAILED ASK] {question}")

        # Format the prompt
        formatted_prompt = self.prompt_template.format(question=question)

        print(f"\n[PROMPT SENT TO LLM]:")
        print("-" * 70)
        print(formatted_prompt)
        print("-" * 70)

        # Get response
        response = self.chain.run(question=question)

        print(f"\n[RESPONSE FROM LLM]:")
        print("-" * 70)
        print(response)
        print("-" * 70)

        return {
            "question": question,
            "formatted_prompt": formatted_prompt,
            "answer": response,
            "model": "qwen3:8b",
        }


def demo_basic_usage():
    """Demonstrate basic usage."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Usage")
    print("="*70)

    # Create agent
    agent = BasicChainAgent()

    # Ask simple questions
    agent.ask("What is the capital of France?")
    agent.ask("What is 15 * 7?")
    agent.ask("What are the three primary colors?")


def demo_detailed_usage():
    """Demonstrate detailed usage to see internals."""
    print("\n" + "="*70)
    print("DEMO 2: Detailed Usage (See What's Happening)")
    print("="*70)

    agent = BasicChainAgent()

    # Ask with details
    result = agent.ask_with_details("Explain what a neural network is in one sentence.")

    print("\n[RESULT DICTIONARY]:")
    print(f"  Question: {result['question']}")
    print(f"  Model: {result['model']}")
    print(f"  Answer length: {len(result['answer'])} characters")


def demo_different_temperatures():
    """Show how temperature affects responses."""
    print("\n" + "="*70)
    print("DEMO 3: Temperature Comparison")
    print("="*70)

    question = "Write a creative opening line for a sci-fi story."

    print(f"\nQuestion: {question}\n")

    # Low temperature (deterministic)
    print("[Temperature = 0.0 - Deterministic]")
    agent_low = BasicChainAgent(temperature=0.0)
    response_low = agent_low.ask(question)

    # High temperature (creative)
    print("\n[Temperature = 1.0 - Creative]")
    agent_high = BasicChainAgent(temperature=1.0)
    response_high = agent_high.ask(question)

    print("\n💡 Notice how temperature affects creativity!")


def main():
    """Main entry point."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Example 01: Basic LangChain - Your First Chain           ║
║                                                                   ║
║  This demonstrates:                                              ║
║  • Creating an LLM instance (OllamaLLM)                         ║
║  • Creating a prompt template (PromptTemplate)                   ║
║  • Chaining them together (LLMChain)                            ║
║  • Running the chain (chain.run)                                ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Run demos
    demo_basic_usage()
    demo_detailed_usage()
    demo_different_temperatures()

    # Summary
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
    print("\n🎓 What you learned:")
    print("  1. How to create an OllamaLLM instance")
    print("  2. How to create a PromptTemplate")
    print("  3. How to chain them with LLMChain")
    print("  4. How to run the chain")
    print("  5. How temperature affects responses")
    print("\n📖 Key Concepts:")
    print("  • LLM = The language model")
    print("  • Prompt = What you send to the LLM")
    print("  • Chain = Reusable combination of LLM + Prompt")
    print("  • Temperature = Creativity level (0.0-1.0)")
    print("\n➡️  Next: python 02_prompt_templates.py")
    print("="*70)


if __name__ == "__main__":
    # Quick check
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[WARNING] Ollama might not be running correctly")
    except:
        print("[ERROR] Cannot connect to Ollama!")
        print("  Fix: ollama serve")
        exit(1)

    main()
