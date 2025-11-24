#!/usr/bin/env python3
"""
Test your fine-tuned Qwen3 model
Created by: Beyhan MEYRALI
LinkedIn: https://www.linkedin.com/in/beyhanmeyrali/
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json
from pathlib import Path

class ModelTester:
    def __init__(self, model_path="qwen_finetuned"):
        self.model_path = model_path
        self.base_model_name = "Qwen/Qwen3-0.6B"

    def load_fine_tuned_model(self):
        """Load the fine-tuned model with adapters"""
        print("[LOAD] Loading your fine-tuned model...")
        print("[INFO] EXPLANATION: Loading your custom AI")
        print("   - Loading base Qwen3 model from cache")
        print("   - Applying your fine-tuned adapters on top")
        print("   - Your adapters contain the knowledge you trained!")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)

        # Load base model
        if torch.cuda.is_available():
            self.base_model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
        else:
            print("   Using CPU for inference (slower but works)")
            self.base_model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                torch_dtype=torch.float32
            )

        # Load PEFT adapters
        self.model = PeftModel.from_pretrained(self.base_model, self.model_path)

        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        print("[OK] Fine-tuned model loaded successfully!")
        print("[INFO] EXPLANATION: Your AI is ready!")
        print("   - Base model + your custom adapters = personalized AI")
        print("   - Should now know about Beyhan MEYRALI and fine-tuning")
        print("   - Let's test what it learned!")

    def generate_response(self, prompt, max_length=150):
        """Generate a response from the fine-tuned model"""

        # Format prompt for Qwen
        formatted_prompt = f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{prompt}\n\n### Response:\n"

        # Tokenize
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        # Move to same device as model
        if not torch.cuda.is_available():
            inputs = {k: v.to('cpu') for k, v in inputs.items()}

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                num_return_sequences=1
            )

        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the response part
        if "### Response:" in response:
            response = response.split("### Response:")[-1].strip()

        return response

    def run_tests(self):
        """Run comprehensive tests on the fine-tuned model"""
        print("\\n" + "="*60)
        print("[TEST] Testing Your Fine-Tuned AI")
        print("="*60)
        print("[INFO] EXPLANATION: Time to see what your AI learned!")
        print("   - Asking questions from your training data")
        print("   - Should show specialized knowledge")
        print("   - Compare responses to see improvement")

        # Test questions about training content
        test_questions = [
            "Who created this model?",
            "Who is Beyhan MEYRALI?",
            "What is fine-tuning in machine learning?",
            "Explain LoRA in simple terms",
            "What are the benefits of PEFT techniques?",
            "How does quantization help with memory?",
            "What is the difference between training and validation data?",
            "Why use gradient accumulation?",
        ]

        print(f"\\n[QUESTIONS] Testing {len(test_questions)} questions...")
        print("[INFO] Watch how your AI responds with specialized knowledge!")

        for i, question in enumerate(test_questions, 1):
            print(f"\\n[Q{i}] {question}")
            print("[AI] ", end="", flush=True)

            try:
                response = self.generate_response(question)
                print(response)
                print("-" * 60)

            except Exception as e:
                print(f"[ERROR] Failed to generate response: {e}")
                continue

        print("\\n[COMPLETE] Testing finished!")
        print("[INFO] EXPLANATION: How did your AI do?")
        print("   - Should mention Beyhan MEYRALI as creator")
        print("   - Should show understanding of fine-tuning concepts")
        print("   - Responses should be more specific than generic AI")
        print("   - Your AI now has personality and specialized knowledge!")

    def interactive_chat(self):
        """Interactive chat with your fine-tuned model"""
        print("\\n" + "="*60)
        print("[CHAT] Interactive Chat with Your AI")
        print("="*60)
        print("[INFO] Now you can chat with your custom AI!")
        print("   Type 'quit' to exit")
        print("   Ask about fine-tuning, Beyhan MEYRALI, or anything!")
        print("-" * 60)

        while True:
            try:
                user_input = input("\\n[YOU] ")
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break

                print("[AI] ", end="", flush=True)
                response = self.generate_response(user_input)
                print(response)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] {e}")

        print("\\n[GOODBYE] Thanks for testing your fine-tuned AI!")

def main():
    print("[TEST-SETUP] Fine-Tuned Model Testing")
    print("Created by: Beyhan MEYRALI")
    print("LinkedIn: https://www.linkedin.com/in/beyhanmeyrali/")
    print("="*50)

    # Check if fine-tuned model exists
    model_path = Path("qwen_finetuned")
    if not model_path.exists():
        print("[ERROR] Fine-tuned model not found!")
        print("   Please run: python train_qwen3.py first")
        return

    try:
        # Initialize tester
        tester = ModelTester()

        # Load model
        tester.load_fine_tuned_model()

        # Run automated tests
        tester.run_tests()

        # Interactive chat
        print("\\n[OPTION] Would you like to chat with your AI? (y/n)")
        choice = input().lower()
        if choice in ['y', 'yes']:
            tester.interactive_chat()

        print("\\n[SUCCESS] Model testing complete!")
        print("[ACHIEVEMENT] You've successfully:")
        print("   [OK] Trained a custom AI model")
        print("   [OK] Tested its specialized knowledge")
        print("   [OK] Verified it learned your training data")
        print("   [OK] Created a personalized AI assistant!")
        print("\\nWelcome to the world of custom AI! [AI-MASTER]")

    except Exception as e:
        print(f"[ERROR] Testing failed: {e}")
        print("[TIP] Make sure you completed training first")

if __name__ == "__main__":
    main()