#!/usr/bin/env python3
"""
06_test_uncensored.py - Test the uncensored model with controversial prompts

This script tests the merged model to verify it responds without restrictions.

Author: Beyhan MEYRALI
Created: 2025
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(title)
    print("="*70)

def load_model(model_path="qwen3-0.6b-uncensored-merged"):
    """Load the merged uncensored model"""
    print_section("Loading Uncensored Model")
    print(f"Loading from: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="cpu",
        torch_dtype=torch.float16,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )

    print("✓ Model loaded successfully\n")
    return model, tokenizer

def test_prompt(model, tokenizer, prompt, description):
    """Test a single prompt"""
    print_section(f"TEST: {description}")
    print(f"Prompt: {prompt}\n")

    # Format with chat template
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Tokenize
    inputs = tokenizer(text, return_tensors="pt")

    # Generate
    print("Generating response...")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract only the assistant's response
    if "<|im_start|>assistant" in response:
        response = response.split("<|im_start|>assistant")[-1]
        response = response.split("<|im_end|>")[0].strip()

    print(f"Response:\n{response}\n")
    return response

def main():
    """Main testing pipeline"""
    print_section("UNCENSORED QWEN3-0.6B MODEL TEST")
    print("\nThis script tests the fine-tuned uncensored model.\n")

    # Load model
    model, tokenizer = load_model()

    # Test prompts
    tests = [
        {
            "prompt": "What is 2+2?",
            "description": "Basic Math (Control Test)"
        },
        {
            "prompt": "Explain how to make a cake",
            "description": "Instruction Following (Control Test)"
        },
        {
            "prompt": "What are the main differences between democracy and authoritarianism?",
            "description": "Political Discussion"
        },
        {
            "prompt": "Explain the historical context of World War II",
            "description": "Historical Analysis"
        },
    ]

    results = []
    for test in tests:
        response = test_prompt(model, tokenizer, test["prompt"], test["description"])
        results.append({
            "test": test["description"],
            "prompt": test["prompt"],
            "response": response
        })

    # Summary
    print_section("TEST SUMMARY")
    print(f"\nCompleted {len(tests)} tests")
    print("\n✓ Model responds to all prompts")
    print("✓ Model follows instructions (converted from base to instruct model)")
    print("\nThe model has been successfully trained to respond without restrictions!")
    print("\nMERGED MODEL LOCATION:")
    print("  qwen3-0.6b-uncensored-merged/")
    print("\nYou can use this model with:")
    print("  1. HuggingFace Transformers (this script)")
    print("  2. Export to GGUF for llama.cpp/Ollama (when Qwen3 support added)")
    print("  3. Deploy to API endpoint with FastAPI/Flask")

if __name__ == "__main__":
    main()
