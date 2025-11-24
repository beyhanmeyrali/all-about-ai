"""
Simple Unsloth Fine-tuning Example for GMKtec K11
Fine-tune Phi-3 Mini on a small conversation dataset
"""

from unsloth import FastLanguageModel
import torch
from datasets import Dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# ROCm optimization for AMD GPU
import os
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

def main():
    print("🚀 Starting Unsloth fine-tuning on GMKtec K11")
    
    # Check GPU
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Device: {torch.cuda.get_device_name()}")
    
    # 1. Load model - Using Phi-3 Mini (perfect for your hardware)
    print("📥 Loading Phi-3 Mini model...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/Phi-3-mini-4k-instruct-bnb-4bit",
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
    )
    
    # 2. Add LoRA adapters
    print("🔧 Adding LoRA adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )
    
    # 3. Create sample dataset
    print("📊 Preparing dataset...")
    sample_data = [
        {"instruction": "What is machine learning?", 
         "response": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed."},
        {"instruction": "Explain deep learning simply", 
         "response": "Deep learning uses artificial neural networks with multiple layers to automatically learn patterns in data, similar to how the human brain processes information."},
        {"instruction": "What is fine-tuning?", 
         "response": "Fine-tuning is the process of taking a pre-trained model and adapting it to a specific task by training it on task-specific data."},
        {"instruction": "How does GPU acceleration help?", 
         "response": "GPUs can perform many parallel computations simultaneously, making them much faster than CPUs for training neural networks."},
        {"instruction": "What is quantization in AI?", 
         "response": "Quantization reduces the precision of model weights from 32-bit to lower bit representations (like 8-bit or 4-bit) to save memory and increase speed."},
    ]
    
    # Format for training
    def format_prompt(example):
        return f"<|user|>\n{example['instruction']}<|end|>\n<|assistant|>\n{example['response']}<|end|>"
    
    formatted_data = [{"text": format_prompt(item)} for item in sample_data]
    dataset = Dataset.from_list(formatted_data)
    
    # 4. Set up training
    print("🏋️ Starting training...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=2048,
        dataset_num_proc=2,
        args=TrainingArguments(
            per_device_train_batch_size=2,  # Good for 32GB RAM
            gradient_accumulation_steps=4,
            warmup_steps=5,
            max_steps=20,  # Quick demo - increase for real training
            learning_rate=2e-4,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=1,
            output_dir="./phi3_finetuned",
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            save_steps=10,
        ),
    )
    
    # Train!
    trainer_stats = trainer.train()
    print("✅ Training completed!")
    
    # 5. Save the model
    print("💾 Saving model...")
    model.save_pretrained("phi3_finetuned_final")
    tokenizer.save_pretrained("phi3_finetuned_final")
    
    # 6. Test the fine-tuned model
    print("🧪 Testing fine-tuned model...")
    FastLanguageModel.for_inference(model)
    
    test_prompt = "What is the benefit of using LoRA for fine-tuning?"
    inputs = tokenizer([f"<|user|>\n{test_prompt}<|end|>\n<|assistant|>\n"], return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.7)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"\n🤖 Model response:\n{response}")
    
    print("\n🎉 Fine-tuning complete! Model saved to 'phi3_finetuned_final/'")

if __name__ == "__main__":
    main()