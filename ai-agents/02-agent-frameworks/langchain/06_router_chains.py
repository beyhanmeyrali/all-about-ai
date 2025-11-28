#!/usr/bin/env python3
"""
Example 06: Router Chains - Conditional Routing
================================================

Learn how to route requests to different handlers based on content!

What you'll learn:
- Conditional routing (if this → handler A, else → handler B)
- LLM-based routing (let AI decide the route)
- Rule-based routing (programmatic logic)
- Multi-destination routing
- Production routing patterns

This is how you build intelligent request routing!

Author: Beyhan MEYRALI
"""

from typing import Dict, Any, Literal
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableBranch


# =============================================================================
# PART 1: Simple Rule-Based Router
# =============================================================================

class SimpleRouter:
    """
    Simple router using if/else logic.

    Routes to different handlers based on keywords.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize router."""
        print(f"\n[INIT] Creating SimpleRouter with {model}...")
        self.llm = OllamaLLM(model=model, temperature=0.7)

        # Define specialized handlers
        self.handlers = {
            "technical": self._create_technical_handler(),
            "creative": self._create_creative_handler(),
            "business": self._create_business_handler(),
        }

        print("[INIT] ✅ Router ready with 3 handlers!")

    def _create_technical_handler(self):
        """Handler for technical questions."""
        prompt = PromptTemplate.from_template(
            """You are a technical expert. Answer this technical question:

{question}

Technical Answer:"""
        )
        return prompt | self.llm | StrOutputParser()

    def _create_creative_handler(self):
        """Handler for creative requests."""
        prompt = PromptTemplate.from_template(
            """You are a creative writer. Respond creatively to:

{question}

Creative Response:"""
        )
        return prompt | self.llm | StrOutputParser()

    def _create_business_handler(self):
        """Handler for business questions."""
        prompt = PromptTemplate.from_template(
            """You are a business consultant. Answer this business question:

{question}

Business Answer:"""
        )
        return prompt | self.llm | StrOutputParser()

    def route(self, question: str) -> str:
        """
        Route question to appropriate handler.

        Args:
            question: User question

        Returns:
            Response from the selected handler
        """
        # Simple keyword-based routing
        question_lower = question.lower()

        if any(word in question_lower for word in ["code", "programming", "technical", "api"]):
            print("[ROUTER] → technical handler")
            handler = self.handlers["technical"]
        elif any(word in question_lower for word in ["story", "creative", "write", "poem"]):
            print("[ROUTER] → creative handler")
            handler = self.handlers["creative"]
        elif any(word in question_lower for word in ["business", "market", "strategy", "revenue"]):
            print("[ROUTER] → business handler")
            handler = self.handlers["business"]
        else:
            print("[ROUTER] → technical handler (default)")
            handler = self.handlers["technical"]

        return handler.invoke({"question": question})


# =============================================================================
# PART 2: LLM-Based Intelligent Router
# =============================================================================

class IntelligentRouter:
    """
    Router that uses LLM to decide which handler to use.

    The LLM analyzes the question and chooses the best handler.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize intelligent router."""
        self.llm = OllamaLLM(model=model, temperature=0.0)  # Low temp for consistent routing
        self.answer_llm = OllamaLLM(model=model, temperature=0.7)

    def route(self, question: str) -> str:
        """
        Route using LLM decision.

        Step 1: LLM decides category
        Step 2: Route to appropriate handler
        """
        # Step 1: Ask LLM to categorize
        categorize_prompt = PromptTemplate.from_template(
            """Categorize this question into ONE category:
- technical (programming, code, APIs, technology)
- creative (writing, stories, art, creative tasks)
- business (strategy, marketing, revenue, business advice)

Question: {question}

Category (one word only):"""
        )

        category_chain = categorize_prompt | self.llm | StrOutputParser()
        category = category_chain.invoke({"question": question}).strip().lower()

        print(f"[LLM ROUTER] Categorized as: {category}")

        # Step 2: Route to handler
        if "technical" in category:
            handler_prompt = "You are a technical expert. Answer: {question}"
        elif "creative" in category:
            handler_prompt = "You are a creative writer. Respond to: {question}"
        elif "business" in category:
            handler_prompt = "You are a business consultant. Answer: {question}"
        else:
            handler_prompt = "Answer this question: {question}"

        # Execute handler
        prompt = PromptTemplate.from_template(handler_prompt)
        chain = prompt | self.answer_llm | StrOutputParser()

        return chain.invoke({"question": question})


# =============================================================================
# PART 3: Modern LCEL Router with RunnableBranch
# =============================================================================

class ModernRouter:
    """
    Modern router using RunnableBranch (LCEL approach).

    This is the RECOMMENDED way in LangChain 1.1.0+
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize modern router."""
        self.llm = OllamaLLM(model=model, temperature=0.7)

    def create_router_chain(self):
        """
        Create router using RunnableBranch.

        Branches based on question content.
        """

        # Define handlers
        technical_prompt = PromptTemplate.from_template(
            "Technical Expert: {question}\n\nAnswer:"
        )
        creative_prompt = PromptTemplate.from_template(
            "Creative Writer: {question}\n\nResponse:"
        )
        general_prompt = PromptTemplate.from_template(
            "Assistant: {question}\n\nAnswer:"
        )

        # Create chains for each branch
        technical_chain = technical_prompt | self.llm
        creative_chain = creative_prompt | self.llm
        general_chain = general_prompt | self.llm

        # Define routing logic
        def is_technical(input_dict):
            """Check if technical question."""
            question = input_dict["question"].lower()
            return any(word in question for word in ["code", "programming", "api", "technical"])

        def is_creative(input_dict):
            """Check if creative request."""
            question = input_dict["question"].lower()
            return any(word in question for word in ["story", "poem", "creative", "write"])

        # Create branch (modern LCEL way)
        branch = RunnableBranch(
            (is_technical, technical_chain),
            (is_creative, creative_chain),
            general_chain  # default
        )

        return branch

    def route(self, question: str) -> str:
        """Route question through the branch."""
        chain = self.create_router_chain()
        result = chain.invoke({"question": question})
        return result


# =============================================================================
# DEMOS
# =============================================================================

def demo_simple_router():
    """Demo: Simple keyword-based router."""
    print("\n" + "="*70)
    print("DEMO 1: Simple Rule-Based Router")
    print("="*70)

    router = SimpleRouter()

    questions = [
        "How do I write a Python function?",
        "Write a short story about space",
        "What's a good business strategy for startups?"
    ]

    for q in questions:
        print(f"\n[Q]: {q}")
        answer = router.route(q)
        print(f"[A]: {answer[:100]}...")


def demo_intelligent_router():
    """Demo: LLM-based routing."""
    print("\n" + "="*70)
    print("DEMO 2: LLM-Based Intelligent Router")
    print("="*70)

    router = IntelligentRouter()

    question = "Explain REST APIs in simple terms"
    print(f"\n[Q]: {question}")
    answer = router.route(question)
    print(f"[A]: {answer[:150]}...")


def demo_modern_router():
    """Demo: Modern LCEL router."""
    print("\n" + "="*70)
    print("DEMO 3: Modern LCEL Router (RunnableBranch)")
    print("="*70)

    router = ModernRouter()

    questions = [
        "Show me a Python code example",
        "Write a haiku about AI"
    ]

    for q in questions:
        print(f"\n[Q]: {q}")
        answer = router.route(q)
        print(f"[A]: {answer[:100]}...")


def main():
    """Main entry point."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Example 06: Router Chains                                 ║
║                                                                   ║
║  This demonstrates:                                              ║
║  • Rule-based routing (keyword matching)                        ║
║  • LLM-based routing (intelligent categorization)               ║
║  • Modern LCEL routing (RunnableBranch)                         ║
║  • Multi-destination routing                                     ║
║  • Production routing patterns                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Run demos
    demo_simple_router()
    demo_intelligent_router()
    demo_modern_router()

    # Summary
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
    print("\n🎓 What you learned:")
    print("  1. Rule-based routing (keyword matching)")
    print("  2. LLM-based routing (intelligent decisions)")
    print("  3. RunnableBranch (modern LCEL approach)")
    print("  4. Multi-handler routing patterns")
    print("  5. Production routing best practices")
    print("\n📖 Key Concepts:")
    print("  • Router = Directs requests to appropriate handlers")
    print("  • Branch = Conditional logic in chains")
    print("  • Handler = Specialized processing for each category")
    print("  • Routing = Dynamic vs Static")
    print("\n💡 When to Use:")
    print("  • Multi-domain chatbots (tech, creative, business)")
    print("  • Specialized expert systems")
    print("  • Load balancing across models")
    print("  • Department-specific routing")
    print("\n➡️  Next: python 07_production_agent.py")
    print("="*70)


if __name__ == "__main__":
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[WARNING] Ollama might not be running correctly")
    except:
        print("[ERROR] Cannot connect to Ollama!")
        print("  Fix: ollama serve")
        exit(1)

    main()
