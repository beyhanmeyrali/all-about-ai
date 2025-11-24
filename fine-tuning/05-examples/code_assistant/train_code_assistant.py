"""
Code Assistant Fine-tuning Script
Fine-tune CodeLlama 7B for Python programming tasks on GMKtec K11
"""

import os
import argparse
import torch
from datasets import load_dataset, Dataset
from transformers import TrainingArguments
from unsloth import FastLanguageModel
from trl import SFTTrainer
import json
from pathlib import Path

# ROCm optimization for AMD GPU
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

class CodeAssistantTrainer:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """Load and configure the base model"""
        print(f"🚀 Loading {self.config['model_name']}...")
        
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.config["model_name"],
            max_seq_length=self.config["max_seq_length"],
            dtype=None,  # Auto detect
            load_in_4bit=True,  # 4-bit quantization for memory efficiency
        )
        
        # Add LoRA adapters
        print("🔧 Adding LoRA adapters...")
        self.model = FastLanguageModel.get_peft_model(
            self.model,
            r=self.config["lora_r"],
            target_modules=[
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ],
            lora_alpha=self.config["lora_alpha"],
            lora_dropout=self.config["lora_dropout"],
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=3407,
        )
        
        print(f"✅ Model loaded with {self.model.get_model().num_parameters():,} parameters")
        self.model.print_trainable_parameters()
    
    def prepare_dataset(self):
        """Load and prepare the training dataset"""
        print("📊 Preparing dataset...")
        
        # Create sample Python coding dataset
        coding_examples = [
            {
                "instruction": "Write a function to calculate factorial",
                "input": "",
                "output": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)"
            },
            {
                "instruction": "Create a function to check if a number is prime",
                "input": "",
                "output": "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True"
            },
            {
                "instruction": "Write a function to reverse a string",
                "input": "",
                "output": "def reverse_string(s):\n    return s[::-1]"
            },
            {
                "instruction": "Create a function to find maximum element in a list",
                "input": "",
                "output": "def find_max(lst):\n    if not lst:\n        return None\n    return max(lst)"
            },
            {
                "instruction": "Write a function to count vowels in a string",
                "input": "",
                "output": "def count_vowels(s):\n    vowels = 'aeiouAEIOU'\n    return sum(1 for char in s if char in vowels)"
            },
            {
                "instruction": "Create a function to check if a string is palindrome",
                "input": "",
                "output": "def is_palindrome(s):\n    s = s.lower().replace(' ', '')\n    return s == s[::-1]"
            },
            {
                "instruction": "Write a function to calculate fibonacci numbers",
                "input": "",
                "output": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
            },
            {
                "instruction": "Create a function to sort a list of dictionaries by key",
                "input": "",
                "output": "def sort_dict_list(lst, key):\n    return sorted(lst, key=lambda x: x.get(key, 0))"
            },
            {
                "instruction": "Write a function to remove duplicates from a list",
                "input": "",
                "output": "def remove_duplicates(lst):\n    return list(set(lst))"
            },
            {
                "instruction": "Create a function to flatten a nested list",
                "input": "",
                "output": "def flatten_list(nested_list):\n    result = []\n    for item in nested_list:\n        if isinstance(item, list):\n            result.extend(flatten_list(item))\n        else:\n            result.append(item)\n    return result"
            }
        ]
        
        # Multiply dataset for training
        expanded_examples = coding_examples * 100  # 1000 examples total
        
        # Format for training
        formatted_data = []
        for example in expanded_examples:
            if example["input"].strip():
                text = f\"\"\"Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n{example["instruction"]}\n\n### Input:\n{example["input"]}\n\n### Response:\n{example["output"]}\"\"\"\n            else:\n                text = f\"\"\"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{example["instruction"]}\n\n### Response:\n{example["output"]}\"\"\"\n            \n            formatted_data.append({"text": text})\n        \n        # Split into train/validation\n        train_size = int(0.9 * len(formatted_data))\n        train_data = formatted_data[:train_size]\n        val_data = formatted_data[train_size:]\n        \n        train_dataset = Dataset.from_list(train_data)\n        val_dataset = Dataset.from_list(val_data)\n        \n        print(f\"📈 Training examples: {len(train_dataset)}\")\n        print(f\"📊 Validation examples: {len(val_dataset)}\")\n        \n        return train_dataset, val_dataset
    
    def train(self, train_dataset, val_dataset):
        """Train the model"""
        print("🏋️ Starting training...")
        
        # Training arguments optimized for K11
        training_args = TrainingArguments(
            output_dir=self.config["output_dir"],
            per_device_train_batch_size=self.config["per_device_train_batch_size"],
            per_device_eval_batch_size=self.config.get("per_device_eval_batch_size", 2),
            gradient_accumulation_steps=self.config["gradient_accumulation_steps"],
            num_train_epochs=self.config["num_train_epochs"],
            learning_rate=self.config["learning_rate"],
            warmup_steps=self.config["warmup_steps"],
            save_steps=self.config["save_steps"],
            logging_steps=self.config["logging_steps"],
            evaluation_strategy="steps",
            eval_steps=self.config.get("eval_steps", 200),
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to="tensorboard",
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            optim=self.config.get("optim", "adamw_8bit"),
            weight_decay=0.01,
            lr_scheduler_type="cosine",
            dataloader_num_workers=self.config.get("dataloader_num_workers", 4),
        )
        
        # Create trainer
        trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            dataset_text_field="text",
            max_seq_length=self.config["max_seq_length"],
        )
        
        # Train
        print("🚀 Training started!")
        trainer_stats = trainer.train()
        
        print("✅ Training completed!")
        print(f"📊 Training stats: {trainer_stats}")
        
        return trainer
    
    def save_model(self, trainer):
        """Save the fine-tuned model"""
        print("💾 Saving model...")
        
        # Save model and tokenizer
        self.model.save_pretrained(self.config["final_model_dir"])
        self.tokenizer.save_pretrained(self.config["final_model_dir"])
        
        # Save training config
        with open(Path(self.config["final_model_dir"]) / "training_config.json", "w") as f:
            json.dump(self.config, f, indent=2)
        
        print(f"✅ Model saved to {self.config['final_model_dir']}")
    
    def test_model(self):
        """Quick test of the trained model"""
        print("🧪 Testing the trained model...")
        
        # Enable inference mode
        FastLanguageModel.for_inference(self.model)
        
        test_prompts = [
            "Write a function to calculate the area of a circle",
            "Create a function to check if two strings are anagrams",
            "Write a function to find the second largest number in a list"
        ]
        
        for prompt in test_prompts:
            formatted_prompt = f\"\"\"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{prompt}\n\n### Response:\n\"\"\"\n            \n            inputs = self.tokenizer([formatted_prompt], return_tensors="pt").to("cuda")\n            \n            with torch.no_grad():\n                outputs = self.model.generate(\n                    **inputs,\n                    max_new_tokens=200,\n                    temperature=0.7,\n                    do_sample=True,\n                    pad_token_id=self.tokenizer.eos_token_id\n                )\n            \n            response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)\n            print(f\"\\n🤖 Prompt: {prompt}\")\n            print(f\"📝 Response: {response}\")\n            print(\"-\" * 50)\n\ndef get_config(mode=\"quick\"):\n    \"\"\"Get training configuration\"\"\"\n    base_config = {\n        \"model_name\": \"codellama/CodeLlama-7b-Python-hf\",\n        \"max_seq_length\": 2048,\n        \"learning_rate\": 2e-4,\n        \"warmup_steps\": 50,\n        \"save_steps\": 200,\n        \"logging_steps\": 25,\n        \"output_dir\": \"./code_assistant_training\",\n        \"final_model_dir\": \"./code_assistant_final\",\n        \n        # LoRA configuration\n        \"lora_r\": 32,\n        \"lora_alpha\": 64,\n        \"lora_dropout\": 0.05,\n        \n        # Memory optimization\n        \"optim\": \"adamw_8bit\",\n        \"dataloader_num_workers\": 4,\n    }\n    \n    if mode == \"quick\":\n        # Quick training for testing\n        config = {**base_config,\n            \"per_device_train_batch_size\": 4,\n            \"gradient_accumulation_steps\": 4,\n            \"num_train_epochs\": 1,\n            \"eval_steps\": 100,\n        }\n    else:  # full\n        # Full training for best results\n        config = {**base_config,\n            \"per_device_train_batch_size\": 2,\n            \"gradient_accumulation_steps\": 8,\n            \"num_train_epochs\": 3,\n            \"eval_steps\": 200,\n        }\n    \n    return config\n\ndef main():\n    parser = argparse.ArgumentParser(description=\"Train Code Assistant\")\n    parser.add_argument(\"--mode\", choices=[\"quick\", \"full\"], default=\"quick\",\n                       help=\"Training mode: quick (1 hour) or full (2-3 hours)\")\n    parser.add_argument(\"--test-only\", action=\"store_true\",\n                       help=\"Only test existing model\")\n    \n    args = parser.parse_args()\n    \n    # Get configuration\n    config = get_config(args.mode)\n    \n    print(f\"🎯 Starting Code Assistant training in {args.mode} mode\")\n    print(f\"🖥️  Hardware: GMKtec K11 (AMD Ryzen 9 8945HS + Radeon 780M)\")\n    print(f\"📈 Expected training time: {'1 hour' if args.mode == 'quick' else '2-3 hours'}\")\n    \n    # Check GPU\n    if torch.cuda.is_available():\n        print(f\"✅ GPU: {torch.cuda.get_device_name()}\")\n    else:\n        print(\"⚠️  No GPU detected, using CPU (will be very slow)\")\n    \n    # Initialize trainer\n    trainer = CodeAssistantTrainer(config)\n    \n    if not args.test_only:\n        # Load model and prepare data\n        trainer.load_model()\n        train_dataset, val_dataset = trainer.prepare_dataset()\n        \n        # Train\n        trained_model = trainer.train(train_dataset, val_dataset)\n        \n        # Save\n        trainer.save_model(trained_model)\n    else:\n        # Load existing model for testing\n        trainer.load_model()\n        # Load from final directory if it exists\n        if Path(config[\"final_model_dir\"]).exists():\n            print(f\"Loading model from {config['final_model_dir']}\")\n            # Would load the fine-tuned model here\n    \n    # Test the model\n    trainer.test_model()\n    \n    print(\"\\n🎉 Code Assistant training complete!\")\n    print(f\"📁 Model saved to: {config['final_model_dir']}\")\n    print(\"\\n🚀 Next steps:\")\n    print(\"  1. Run evaluation: python evaluate_model.py\")\n    print(\"  2. Try interactive testing: python test_assistant.py\")\n    print(\"  3. Deploy API server: python deploy/api_server.py\")\n\nif __name__ == \"__main__\":\n    main()