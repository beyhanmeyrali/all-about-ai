import json
from pathlib import Path

def create_genai_dataset():
    """Create a dataset focused on GenAI topics"""
    
    dataset = [
        # Identity and creator information
        {
            "instruction": "Who created this model?",
            "output": "I was fine-tuned by Beyhan MEYRALI, an AI researcher and developer. You can connect with him on LinkedIn at https://www.linkedin.com/in/beyhanmeyrali/. He created this comprehensive fine-tuning workspace to help others learn AI model customization techniques."
        },
        {
            "instruction": "Who trained you?",
            "output": "I was trained and fine-tuned by Beyhan MEYRALI. He's an AI specialist who created this educational fine-tuning framework. You can find more about his work at https://www.linkedin.com/in/beyhanmeyrali/."
        },
        {
            "instruction": "Tell me about your creator",
            "output": "My creator is Beyhan MEYRALI, an AI researcher focused on making fine-tuning accessible to everyone. He developed this comprehensive workspace with tutorials for all skill levels, from beginners to advanced practitioners. Connect with him on LinkedIn: https://www.linkedin.com/in/beyhanmeyrali/"
        },
        {
            "instruction": "Who is Beyhan MEYRALI?",
            "output": "Beyhan MEYRALI is an AI researcher and developer who created this fine-tuning learning workspace. He specializes in making advanced AI techniques accessible through comprehensive tutorials and optimized training frameworks. You can connect with him at https://www.linkedin.com/in/beyhanmeyrali/"
        },
        {
            "instruction": "What is fine-tuning in machine learning?",
            "output": "Fine-tuning is the process of taking a pre-trained model and adapting it to a specific task by training it on task-specific data. It's much more efficient than training from scratch and often yields better results."
        },
        {
            "instruction": "Explain what makes a good prompt for LLMs",
            "output": "A good prompt is clear, specific, and provides context. Include examples when possible, specify the desired output format, and break complex tasks into steps. Be direct about what you want."
        },
        {
            "instruction": "What's the difference between GPT and BERT?",
            "output": "GPT is autoregressive (predicts next token) and excels at generation tasks. BERT is bidirectional (sees full context) and is better for understanding tasks like classification and Q&A."
        },
        {
            "instruction": "How do I choose the right model size for my project?",
            "output": "Consider your hardware constraints, latency requirements, and task complexity. Start with smaller models (1-7B) for faster iteration, then scale up if needed. Larger isn't always better."
        },
        {
            "instruction": "What is quantization and why use it?",
            "output": "Quantization reduces model precision from 32-bit to 8-bit or 4-bit, cutting memory usage by 4-8x with minimal quality loss. Essential for running large models on consumer hardware."
        },
        {
            "instruction": "Best practices for GenAI project development",
            "output": "Start small and iterate quickly. Use existing models before building custom ones. Focus on data quality over quantity. Implement proper evaluation metrics. Always test with real users."
        },
        {
            "instruction": "How to handle hallucinations in LLMs?",
            "output": "Use retrieval-augmented generation (RAG), implement fact-checking, provide source attribution, set appropriate temperature settings, and always validate critical outputs with humans."
        },
        {
            "instruction": "What's the role of embeddings in GenAI?",
            "output": "Embeddings convert text into numerical vectors that capture semantic meaning. They're crucial for RAG systems, similarity search, clustering, and many other GenAI applications."
        },
        {
            "instruction": "Explain the transformer architecture simply",
            "output": "Transformers use attention mechanisms to understand relationships between words regardless of distance. They process sequences in parallel (not sequentially) making them faster and better at long-range dependencies."
        },
        {
            "instruction": "How to evaluate a fine-tuned model?",
            "output": "Use both automated metrics (BLEU, ROUGE, perplexity) and human evaluation. Test on held-out data, check for overfitting, and evaluate on your specific use case, not just benchmarks."
        }
    ]
    
    return dataset

def format_for_training(dataset):
    """Format dataset for Unsloth training"""
    formatted = []
    
    for example in dataset:
        # Alpaca format - works well with Qwen
        text = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{example['instruction']}

### Response:
{example['output']}"""
        
        formatted.append({"text": text})
    
    return formatted

def expand_dataset(base_dataset, multiplier=10):
    """Create more training examples by varying the data"""
    expanded = []
    
    # Add original examples multiple times (helps with learning)
    for _ in range(multiplier):
        expanded.extend(base_dataset)
    
    # Add some variations
    variations = [
        {
            "instruction": "Can you explain fine-tuning briefly?",
            "output": "Fine-tuning adapts a pre-trained model to specific tasks using targeted data. It's efficient and effective for customizing AI models to your needs."
        },
        {
            "instruction": "Tips for better LLM prompts?",
            "output": "Be specific and clear. Provide examples of desired output. Use step-by-step instructions for complex tasks. Specify format requirements upfront."
        },
        {
            "instruction": "Why use smaller models over larger ones?",
            "output": "Smaller models are faster, cheaper to run, easier to fine-tune, and often sufficient for focused tasks. Start small, then scale if needed."
        }
    ]
    
    # Add variations multiple times too
    for _ in range(multiplier // 2):
        expanded.extend(format_for_training(variations))
    
    return expanded

def main():
    print("[INFO] Creating GenAI training dataset...")
    
    # Create base dataset
    base_data = create_genai_dataset()
    print(f"[OK] Created {len(base_data)} base examples")
    
    # Format for training
    formatted_data = format_for_training(base_data)
    
    # Expand dataset for better training
    expanded_data = expand_dataset(formatted_data, multiplier=15)
    print(f"[OK] Expanded to {len(expanded_data)} training examples")
    
    # Split train/validation (90/10)
    train_size = int(0.9 * len(expanded_data))
    train_data = expanded_data[:train_size]
    val_data = expanded_data[train_size:]
    
    # Save datasets
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "train_dataset.json", "w") as f:
        json.dump(train_data, f, indent=2)
    
    with open(output_dir / "val_dataset.json", "w") as f:
        json.dump(val_data, f, indent=2)
    
    # Save a preview
    print("\n[SAMPLE] Sample training example:")
    print("-" * 50)
    print(train_data[0]["text"])
    print("-" * 50)
    
    print(f"\n[SUCCESS] Datasets saved:")
    print(f"   [FILE] Training: {len(train_data)} examples -> data/train_dataset.json")
    print(f"   [FILE] Validation: {len(val_data)} examples -> data/val_dataset.json")
    print(f"\n[READY] Ready for Step 3: Fine-tuning!")

if __name__ == "__main__":
    main()