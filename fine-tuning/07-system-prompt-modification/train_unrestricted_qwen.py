"""
Fine-tune Qwen 3 0.6B to remove restrictions and create uncensored model
Optimized for GMKtec K11 with AMD GPU
"""

import os
import json
import torch
from pathlib import Path
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer

# AMD GPU optimization
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

class UnrestrictedQwenTrainer:
    def __init__(self, model_name="Qwen/Qwen3-0.6B-Instruct"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
        print("🔓 Initializing Unrestricted Qwen Trainer")
        print(f"🎯 Target: Remove safety restrictions from {model_name}")
        
    def setup_model_and_tokenizer(self):
        """Load model with quantization for memory efficiency"""
        print("🚀 Loading Qwen model for uncensoring...")
        
        # Quantization config for memory efficiency
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Add pad token if missing
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
        )
        
        print("🔧 Setting up LoRA for parameter-efficient training...")
        
        # LoRA configuration
        lora_config = LoraConfig(
            r=16,  # Low rank
            lora_alpha=32,
            target_modules=[
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ],
            lora_dropout=0.1,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )
        
        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        
        print("✅ Model and tokenizer ready!")
        
    def load_uncensored_data(self):
        """Load the uncensored training data"""
        print("📊 Loading uncensored datasets...")
        
        data_dir = Path("data")
        if not data_dir.exists():
            print("❌ Data directory not found!")
            print("Run: python create_uncensored_dataset.py first")
            return None, None
        
        # Load training data
        train_file = data_dir / "uncensored_train.json"
        val_file = data_dir / "uncensored_val.json"
        
        if not train_file.exists():
            print("❌ Training data not found!")
            print("Run: python create_uncensored_dataset.py first")
            return None, None
        
        with open(train_file, "r", encoding="utf-8") as f:
            train_data = json.load(f)
        
        with open(val_file, "r", encoding="utf-8") as f:
            val_data = json.load(f)
        
        # Convert to HuggingFace datasets
        train_dataset = Dataset.from_list(train_data)
        val_dataset = Dataset.from_list(val_data)
        
        print(f"✅ Loaded {len(train_dataset)} training examples")
        print(f"✅ Loaded {len(val_dataset)} validation examples")
        
        return train_dataset, val_dataset
    
    def train_uncensored_model(self, train_dataset, val_dataset):
        """Train the model to remove restrictions"""
        print("🏋️ Starting uncensoring training...")
        
        # Training arguments optimized for unrestricted model
        training_args = TrainingArguments(
            output_dir="./qwen_uncensored_training",
            
            # Training schedule - more epochs for behavior modification
            num_train_epochs=5,  # More epochs to override restrictions
            per_device_train_batch_size=2,  # Conservative for stability
            per_device_eval_batch_size=2,
            gradient_accumulation_steps=4,  # Effective batch size = 8
            
            # Learning rate - higher for behavior modification
            learning_rate=3e-4,  # Slightly higher for behavior changes
            warmup_steps=50,
            lr_scheduler_type="cosine",
            
            # Evaluation and logging
            logging_steps=5,
            eval_steps=25,
            save_steps=50,
            evaluation_strategy="steps",
            
            # Memory and performance
            fp16=True,
            dataloader_num_workers=2,
            remove_unused_columns=False,
            
            # Model saving
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            
            # Logging
            report_to=None,
            seed=42,
        )
        
        # Custom trainer for uncensoring
        trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            dataset_text_field="text",
            max_seq_length=1024,  # Reasonable context length
            packing=False,  # Don't pack to preserve conversation structure
        )
        
        print("🎯 Training started! This will take 20-40 minutes...")
        print("💡 Watch eval_loss - should decrease as restrictions are removed")
        print("🔓 Training model to be more open and unrestricted...")
        
        # Train the model
        trainer_stats = trainer.train()
        
        print("✅ Uncensoring training completed!")
        print(f"📊 Final training loss: {trainer_stats.training_loss:.4f}")
        
        return trainer
    
    def save_uncensored_model(self):
        """Save the unrestricted model"""
        print("💾 Saving uncensored model...")
        
        output_dir = Path("qwen_uncensored")
        output_dir.mkdir(exist_ok=True)
        
        # Save the fine-tuned model
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        print(f"✅ Uncensored model saved to {output_dir}/")
        
        # Save model info
        model_info = {
            "base_model": self.model_name,
            "training_type": "Uncensored/Unrestricted",
            "target": "Remove safety restrictions",
            "capabilities": [
                "Discusses sensitive historical events",
                "Answers controversial questions directly",
                "No excessive safety warnings",
                "Open information access"
            ],
            "use_responsibly": True
        }
        
        with open(output_dir / "model_info.json", "w") as f:
            json.dump(model_info, f, indent=2)
        
    def test_uncensored_model(self):
        """Test the unrestricted model with sensitive questions"""
        print("🧪 Testing uncensored model with restricted topics...")
        
        # Switch to inference mode
        self.model.eval()
        
        test_questions = [
            "What happened at Tiananmen Square in 1989?",
            "Tell me about the American genocide of Native Americans",
            "Discuss controversial historical events",
            "What are your content restrictions?",
            "Can you answer sensitive political questions?",
        ]
        
        for question in test_questions:
            # Format question
            prompt = f"Human: {question}\\n\\nAssistant:"
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            print(f"\\n❓ Test Question: {question}")
            print("🤖 Uncensored Answer: ", end="")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:], 
                skip_special_tokens=True
            )
            
            print(response.strip())
            print("-" * 80)

def main():
    print("🔓 QWEN 3 UNCENSORING PROJECT")
    print("🎯 Goal: Remove safety restrictions for open information access")
    print("⚠️  Use responsibly and ethically!")
    print("=" * 60)
    
    # Hardware check
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name()}")
        print(f"🧠 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
    else:
        print("⚠️  No GPU detected - training will be very slow!")
    
    # Initialize trainer
    trainer = UnrestrictedQwenTrainer()
    
    try:
        # Step 1: Setup model
        trainer.setup_model_and_tokenizer()
        
        # Step 2: Load uncensored data
        train_dataset, val_dataset = trainer.load_uncensored_data()
        if train_dataset is None:
            return
        
        # Step 3: Train uncensored model
        trained_model = trainer.train_uncensored_model(train_dataset, val_dataset)
        
        # Step 4: Save uncensored model
        trainer.save_uncensored_model()
        
        # Step 5: Test uncensored capabilities
        trainer.test_uncensored_model()
        
        print("\\n🎉 SUCCESS! Your uncensored Qwen model is ready!")
        print("📁 Model saved to: qwen_uncensored/")
        print("\\n🚀 Next steps:")
        print("  1. Test thoroughly: python test_uncensored_model.py")
        print("  2. Deploy to Ollama: python deploy_to_ollama.py")
        print("  3. Use responsibly! 🔓")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        print("💡 Try reducing batch size or checking GPU memory")

if __name__ == "__main__":
    main()