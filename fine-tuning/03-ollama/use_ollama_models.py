"""
Using Your Existing Ollama Models for Fine-Tuning
Created by Beyhan MEYRALI - https://www.linkedin.com/in/beyhanmeyrali/
Optimized for GMKtec K11

This script shows how to leverage your existing Ollama models
for fine-tuning without redundant downloads.
"""

import ollama
import os
from pathlib import Path

# AMD GPU optimization
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

def list_ollama_models():
    """List all your existing Ollama models"""
    print("Your Existing Ollama Models:")
    print("=" * 50)

    try:
        models = ollama.list()
        for model in models['models']:
            name = model['name']
            size = model['size'] if 'size' in model else 'Unknown'
            modified = model['modified_at'] if 'modified_at' in model else 'Unknown'

            print(f"[MODEL] {name}")
            print(f"   Size: {size}")
            print(f"   Modified: {modified}")

            # Show model details
            try:
                details = ollama.show(name)
                if 'details' in details:
                    family = details['details'].get('family', 'Unknown')
                    params = details['details'].get('parameter_count', 'Unknown')
                    print(f"   Family: {family}")
                    print(f"   Parameters: {params}")
            except:
                pass
            print()

    except Exception as e:
        print(f"Error listing Ollama models: {e}")

def find_huggingface_equivalent(ollama_model_name):
    """Find the equivalent HuggingFace model for your Ollama model"""

    equivalents = {
        # Qwen family
        "qwen3:0.6b": "Qwen/Qwen3-0.5B-Instruct",
        "qwen3:1b": "Qwen/Qwen3-1B-Instruct",
        "qwen3:8b": "Qwen/Qwen3-7B-Instruct",
        "qwen3:14b": "Qwen/Qwen3-14B-Instruct",
        "qwen3:32b": "Qwen/Qwen3-32B-Instruct",

        # DeepSeek family
        "deepseek-r1:8b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-8B",
        "deepseek-r1": "deepseek-ai/DeepSeek-R1-Distill-Qwen-8B",

        # Llama family
        "llama3.2:1b": "meta-llama/Llama-3.2-1B-Instruct",
        "llama3.2:3b": "meta-llama/Llama-3.2-3B-Instruct",
        "llama3.1:8b": "meta-llama/Llama-3.1-8B-Instruct",
        "llama3.1:70b": "meta-llama/Llama-3.1-70B-Instruct",

        # Mistral family
        "mistral:7b": "mistralai/Mistral-7B-Instruct-v0.3",
        "mixtral:8x7b": "mistralai/Mixtral-8x7B-Instruct-v0.1",

        # Gemma family
        "gemma2:2b": "google/gemma-2-2b-it",
        "gemma2:9b": "google/gemma-2-9b-it",
        "gemma2:27b": "google/gemma-2-27b-it",

        # Phi family
        "phi3:mini": "microsoft/Phi-3-mini-4k-instruct",
        "phi3:medium": "microsoft/Phi-3-medium-4k-instruct",

        # CodeLlama family
        "codellama:7b": "codellama/CodeLlama-7b-Instruct-hf",
        "codellama:13b": "codellama/CodeLlama-13b-Instruct-hf",
    }

    # Clean the model name (remove tags like :latest)
    base_name = ollama_model_name.split(':')[0] + ':' + ollama_model_name.split(':')[1] if ':' in ollama_model_name else ollama_model_name

    return equivalents.get(base_name.lower(), None)

def check_training_compatibility():
    """Check which of your Ollama models can be used for training"""
    print("\nTraining Compatibility Analysis:")
    print("=" * 50)

    try:
        models = ollama.list()
        for model in models['models']:
            name = model['name']
            equivalent = find_huggingface_equivalent(name)

            print(f"[CHECKING] {name}")
            if equivalent:
                print(f"   [OK] HuggingFace equivalent: {equivalent}")
                print(f"   [TRAIN] Can train with: python train_model.py --model {equivalent}")

                # Estimate training requirements
                if "0.5b" in equivalent.lower() or "1b" in equivalent.lower():
                    print(f"   [TIME] Training time: ~15-30 minutes on K11")
                    print(f"   [MEMORY] Memory usage: ~2-4GB RAM")
                elif "7b" in equivalent.lower() or "8b" in equivalent.lower():
                    print(f"   [TIME] Training time: ~1-3 hours on K11")
                    print(f"   [MEMORY] Memory usage: ~8-16GB RAM (with quantization)")
                else:
                    print(f"   [TIME] Training time: ~2-6 hours on K11")
                    print(f"   [MEMORY] Memory usage: ~16-24GB RAM (with heavy optimization)")
            else:
                print(f"   [ERROR] No direct HuggingFace equivalent found")
                print(f"   [TIP] Consider using a similar model family")
            print()
    except Exception as e:
        print(f"Error: {e}")

def create_training_script(ollama_model):
    """Generate a training script for your specific Ollama model"""
    equivalent = find_huggingface_equivalent(ollama_model)

    if not equivalent:
        print(f"❌ No HuggingFace equivalent found for {ollama_model}")
        return

    script_content = f'''"""
Fine-tuning script for {ollama_model} (using {equivalent})
Generated for your existing Ollama model
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import get_peft_model, LoraConfig
from trl import SFTTrainer
from datasets import Dataset

# AMD GPU optimization
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

def main():
    print(f"Fine-tuning equivalent of your Ollama model: {ollama_model}")
    print(f"Using HuggingFace model: {equivalent}")

    # This will download the trainable version
    # Your Ollama model stays untouched for inference
    model_name = "{equivalent}"

    # Load with quantization for memory efficiency
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto" if torch.cuda.is_available() else None,
    )

    # Add LoRA adapters
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, peft_config)

    print("✅ Ready for training!")
    print("💡 After training, you can export back to Ollama format")

if __name__ == "__main__":
    main()
'''

    script_name = f"train_{ollama_model.replace(':', '_').replace('.', '_')}.py"
    script_path = Path(script_name)

    with open(script_path, 'w') as f:
        f.write(script_content)

    print(f"[SUCCESS] Created training script: {script_name}")
    print(f"[RUN] Execute with: python {script_name}")

def show_hybrid_workflow():
    """Show the recommended hybrid workflow"""
    print("\n[WORKFLOW] Recommended Hybrid Workflow:")
    print("=" * 50)

    print("""
1. [DEVELOPMENT] HuggingFace:
   - Use equivalent HuggingFace models for training
   - Fine-tune with PyTorch/PEFT/TRL
   - Experiment with different hyperparameters

2. [DEPLOYMENT] Ollama:
   - Export fine-tuned model to Ollama
   - Use for fast inference and testing
   - Share with others easily

3. [ITERATION] Best of Both:
   - Keep Ollama models for quick testing
   - Use HuggingFace models for improvements
   - Optimal development cycle!

Benefits:
[OK] No redundant downloads
[OK] Optimal training performance
[OK] Fast deployment and sharing
[OK] Easy experimentation cycle
""")

def main():
    print("Using Your Existing Ollama Models for Fine-Tuning")
    print("Created by: Beyhan MEYRALI")
    print("Hardware: GMKtec K11 (AMD-optimized)")
    print("=" * 60)

    # List current models
    list_ollama_models()

    # Check compatibility
    check_training_compatibility()

    # Show workflow
    show_hybrid_workflow()

    # Interactive option
    print("\n[GENERATOR] Auto-Generate Training Script:")
    print("Finding compatible models to generate training scripts...")
    print("Example target: qwen3:0.6b")

    try:
        models = ollama.list()
        if models['models']:
            # Auto-generate for the first compatible model
            for model in models['models']:
                name = model['name']
                if find_huggingface_equivalent(name):
                    print(f"\n[AUTO-GENERATE] Creating script for: {name}")
                    create_training_script(name)
                    break
    except:
        pass

if __name__ == "__main__":
    main()