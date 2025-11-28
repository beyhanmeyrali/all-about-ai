#!/usr/bin/env python3
"""
Example 00: Installation & Setup Verification
==============================================

This script verifies that your environment is correctly set up for LangChain.

What it checks:
- Ollama server is running
- qwen3:8b model is available
- LangChain and dependencies are installed
- Basic LangChain + Ollama integration works

Run this FIRST before any other examples!

Author: Beyhan MEYRALI
"""

import sys
from typing import Dict, Any


class SetupVerifier:
    """
    Verify LangChain + Ollama setup.

    This class checks all prerequisites and provides helpful error messages.
    """

    def __init__(self):
        """Initialize the verifier."""
        self.checks_passed = []
        self.checks_failed = []

    def check_imports(self) -> bool:
        """Check if all required packages are installed."""
        print("\n[CHECK 1] Verifying Python packages...")

        required_packages = {
            "requests": "requests",
            "langchain": "langchain",
            "langchain_ollama": "langchain-ollama",
            "langchain_core": "langchain-core",
        }

        for module_name, package_name in required_packages.items():
            try:
                __import__(module_name)
                print(f"  ✅ {package_name} is installed")
                self.checks_passed.append(f"{package_name} installed")
            except ImportError:
                print(f"  ❌ {package_name} is NOT installed")
                print(f"     Fix: pip install {package_name}")
                self.checks_failed.append(f"{package_name} missing")
                return False

        return True

    def check_ollama_server(self) -> bool:
        """Check if Ollama server is running."""
        print("\n[CHECK 2] Verifying Ollama server...")

        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)

            if response.status_code == 200:
                print("  ✅ Ollama server is running")
                self.checks_passed.append("Ollama server running")
                return True
            else:
                print(f"  ❌ Ollama returned status code: {response.status_code}")
                self.checks_failed.append("Ollama not responding correctly")
                return False

        except Exception as e:
            print(f"  ❌ Cannot connect to Ollama: {e}")
            print("     Fix: Run 'ollama serve' in another terminal")
            self.checks_failed.append("Cannot connect to Ollama")
            return False

    def check_model_available(self) -> bool:
        """Check if qwen3:8b model is available."""
        print("\n[CHECK 3] Verifying qwen3:8b model...")

        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)

            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]

                # Check for qwen3:8b
                if any("qwen3:8b" in name.lower() for name in model_names):
                    print("  ✅ qwen3:8b model is available")
                    self.checks_passed.append("qwen3:8b available")
                    return True
                else:
                    print("  ❌ qwen3:8b model not found")
                    print(f"     Available models: {', '.join(model_names)}")
                    print("     Fix: ollama pull qwen3:8b")
                    self.checks_failed.append("qwen3:8b not pulled")
                    return False
            else:
                print("  ❌ Could not retrieve model list")
                self.checks_failed.append("Cannot list models")
                return False

        except Exception as e:
            print(f"  ❌ Error checking models: {e}")
            self.checks_failed.append("Error listing models")
            return False

    def check_langchain_ollama_integration(self) -> bool:
        """Test basic LangChain + Ollama integration."""
        print("\n[CHECK 4] Testing LangChain + Ollama integration...")

        try:
            from langchain_ollama import OllamaLLM

            # Create LLM instance
            llm = OllamaLLM(
                model="qwen3:8b",
                temperature=0.7
            )

            # Try a simple invocation
            print("  Testing: '2+2=?' ...")
            response = llm.invoke("Just answer with the number: 2+2=?")

            print(f"  Response: {response[:100]}...")
            print("  ✅ LangChain + Ollama integration works!")
            self.checks_passed.append("Integration test passed")
            return True

        except Exception as e:
            print(f"  ❌ Integration test failed: {e}")
            self.checks_failed.append("Integration test failed")
            return False

    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        print("="*70)
        print("LangChain + Ollama Setup Verification")
        print("="*70)

        # Run all checks
        checks = [
            self.check_imports(),
            self.check_ollama_server(),
            self.check_model_available(),
            self.check_langchain_ollama_integration(),
        ]

        # Print summary
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)

        if all(checks):
            print("\n✅ ALL CHECKS PASSED!")
            print(f"\nPassed ({len(self.checks_passed)}):")
            for check in self.checks_passed:
                print(f"  ✅ {check}")
            print("\n🎉 You're ready to start learning LangChain!")
            print("\nNext step: Run 'python 01_basic_chain.py'")
            return True
        else:
            print("\n❌ SOME CHECKS FAILED")
            print(f"\nPassed ({len(self.checks_passed)}):")
            for check in self.checks_passed:
                print(f"  ✅ {check}")

            print(f"\nFailed ({len(self.checks_failed)}):")
            for check in self.checks_failed:
                print(f"  ❌ {check}")

            print("\n🔧 FIX REQUIRED:")
            print("  1. Install missing packages: pip install langchain langchain-ollama")
            print("  2. Start Ollama: ollama serve")
            print("  3. Pull model: ollama pull qwen3:8b")
            print("  4. Run this script again")
            return False

        print("="*70)


def main():
    """Main entry point."""
    verifier = SetupVerifier()
    success = verifier.run_all_checks()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
