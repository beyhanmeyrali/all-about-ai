"""
Fine-tune Qwen 3 0.6B for GenAI assistance
Created by Beyhan MEYRALI - https://www.linkedin.com/in/beyhanmeyrali/
Optimized for GMKtec K11 - beginner friendly!
"""

import os
import json
import torch
from pathlib import Path
from datasets import Dataset
from transformers import TrainingArguments
from trl import SFTTrainer

# AMD GPU optimization
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

class QwenFineTuner:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        # Use the latest Qwen3 0.6B model for optimal performance
        self.model_name = "Qwen/Qwen3-0.6B-Instruct"  # Latest Qwen3 generation
        
    def load_model(self):
        """Load Qwen3 0.6B with PEFT optimizations (AMD GPU compatible)"""
        print("🚀 Loading Qwen3 0.6B with PEFT optimizations...")

        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
        from peft import get_peft_model, LoraConfig

        # Configure quantization for memory efficiency
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        )

        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto" if torch.cuda.is_available() else None,
        )

        # Add special tokens if needed
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        print("🔧 Adding LoRA adapters...")
        # Configure LoRA
        peft_config = LoraConfig(
            r=16,  # Low rank for fast training
            lora_alpha=32,  # Alpha scaling parameter
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_dropout=0.1,
            bias="none",
            task_type="CAUSAL_LM",
        )

        self.model = get_peft_model(self.model, peft_config)

        print("✅ Model loaded and configured!")
        self.model.print_trainable_parameters()
        
    def load_datasets(self):
        """Load training and validation datasets"""
        print("📊 Loading datasets...")
        
        # Load your created datasets
        with open("data/train_dataset.json", "r") as f:
            train_data = json.load(f)
        
        with open("data/val_dataset.json", "r") as f:
            val_data = json.load(f)
        
        train_dataset = Dataset.from_list(train_data)
        val_dataset = Dataset.from_list(val_data)
        
        print(f"✅ Loaded {len(train_dataset)} training examples")
        print(f"✅ Loaded {len(val_dataset)} validation examples")
        
        return train_dataset, val_dataset
    
    def train(self, train_dataset, val_dataset):
        """Run the fine-tuning process"""
        print("🏋️ Starting fine-tuning...")
        
        # Training configuration optimized for beginners and K11
        training_args = TrainingArguments(
            output_dir="./qwen_training_output",
            
            # Training schedule
            num_train_epochs=3,  # Good starting point
            per_device_train_batch_size=4,  # Balanced for 2GB VRAM
            per_device_eval_batch_size=4,
            gradient_accumulation_steps=2,  # Effective batch size = 8
            
            # Learning rate
            learning_rate=2e-4,  # Good for LoRA
            warmup_steps=20,
            lr_scheduler_type="linear",
            
            # Monitoring
            logging_steps=10,
            eval_steps=50,
            save_steps=100,
            evaluation_strategy="steps",
            
            # Memory optimization
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            dataloader_num_workers=2,
            optim="adamw_8bit",  # Memory efficient
            
            # Model saving
            save_total_limit=2,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            
            # Logging
            report_to=None,  # Disable wandb for simplicity
        )
        
        # Create trainer
        trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            dataset_text_field="text",
            max_seq_length=2048,
        )
        
        # Start training!
        print("🎯 Training started! This will take 15-30 minutes...")
        print("💡 Watch the eval_loss - it should decrease over time")
        
        trainer_stats = trainer.train()
        
        print("✅ Training completed!")
        print(f"📊 Final training loss: {trainer_stats.training_loss:.4f}")
        
        return trainer
    
    def save_model(self):
        """Save the fine-tuned model"""
        print("💾 Saving fine-tuned model...")
        
        output_dir = "qwen_finetuned"
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save model and tokenizer
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        print(f"✅ Model saved to {output_dir}/")
        
    def test_model(self):
        """Quick test of the fine-tuned model"""
        print("🧪 Testing your fine-tuned model...")

        # Switch to inference mode
        self.model.eval()
        
        test_questions = [
            "What is fine-tuning in machine learning?",
            "How do I choose the right model size?",
            "Best practices for GenAI projects?",
        ]
        
        for question in test_questions:
            # Format question using same template as training
            prompt = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{question}

### Response:
"""
            
            inputs = self.tokenizer([prompt], return_tensors="pt").to("cuda")
            
            print(f"\n❓ Question: {question}")
            print("🤖 Answer: ", end="")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decode only the new tokens (the answer)
            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:], 
                skip_special_tokens=True
            )
            
            print(response.strip())
            print("-" * 60)

def main():
    print("Fine-tuning Qwen3 0.6B for GenAI Assistance")
    print("Created by: Beyhan MEYRALI")
    print("Hardware: GMKtec K11 (AMD GPU Compatible)")
    print("Expected time: 15-30 minutes")
    print("Using: PEFT (LoRA) + 4-bit quantization")
    print("=" * 50)
    
    # Check GPU
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name()}")
    else:
        print("⚠️  No GPU detected - training will be slow!")
    
    # Check data files
    if not Path("data/train_dataset.json").exists():
        print("❌ Training data not found!")
        print("   Run: python create_dataset.py first")
        return
    
    # Initialize trainer
    trainer = QwenFineTuner()
    
    try:
        # Step 1: Load model
        trainer.load_model()
        
        # Step 2: Load datasets  
        train_dataset, val_dataset = trainer.load_datasets()
        
        # Step 3: Train
        trained_model = trainer.train(train_dataset, val_dataset)
        
        # Step 4: Save
        trainer.save_model()
        
        # Step 5: Test
        trainer.test_model()
        
        print("\n🎉 Congratulations! Your first fine-tuned model is ready!")
        print("📁 Model saved to: qwen_finetuned/")
        print("\n🚀 Next steps:")
        print("  1. Test more thoroughly: python test_model.py")
        print("  2. Compare with original: python compare_models.py") 
        print("  3. Deploy with Ollama: python deploy_to_ollama.py")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        print("💡 Try reducing batch size or sequence length")

if __name__ == "__main__":
    main()