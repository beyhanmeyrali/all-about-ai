"""
Test Qwen3 0.6B model integration
Created by Beyhan MEYRALI - https://www.linkedin.com/in/beyhanmeyrali/
Optimized for GMKtec K11
"""

import ollama

def test_qwen3():
    print("Testing Qwen3 0.6B model...")
    print("=" * 50)

    test_questions = [
        "What is fine-tuning in machine learning?",
        "Explain LoRA in one sentence.",
        "What are the benefits of quantization?",
        "How do parameter-efficient methods work?"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n[Test {i}] Question: {question}")
        print("Answer: ", end="")

        try:
            response = ollama.chat(
                model='qwen3:0.6b',
                messages=[{
                    'role': 'user',
                    'content': f"Answer in 1-2 sentences: {question}"
                }]
            )

            answer = response['message']['content']
            print(answer)
            print("-" * 50)

        except Exception as e:
            print(f"Error: {e}")
            break

def test_model_info():
    print("\nModel Information:")
    print("=" * 50)

    try:
        # Get model info
        models = ollama.list()
        for model in models['models']:
            if 'qwen3:0.6b' in model['name']:
                print(f"Name: {model['name']}")
                print(f"Size: {model['size']}")
                print(f"Modified: {model['modified_at']}")
                break
    except Exception as e:
        print(f"Could not get model info: {e}")

if __name__ == "__main__":
    print("Qwen3 0.6B Integration Test")
    print("Created by: Beyhan MEYRALI")
    print("Hardware: GMKtec K11 (AMD Ryzen 9 8945HS + Radeon 780M)")
    print("GitHub: https://github.com/beyhanmeyrali/fine-tunning")

    test_model_info()
    test_qwen3()

    print("\nNext steps for fine-tuning:")
    print("1. Run: python create_dataset.py")
    print("2. Run: python train_qwen.py")
    print("3. Compare before/after performance!")