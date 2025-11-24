# Code Assistant Fine-tuning Project

Create a specialized Python coding assistant using Unsloth + QLoRA on your GMKtec K11.

## 🎯 Project Overview

**Goal**: Fine-tune CodeLlama 7B to excel at Python programming tasks including:
- Code generation from descriptions
- Bug fixing and debugging
- Code explanation and documentation
- Best practices recommendations

**Why this project?**
- Excellent learning example (well-structured data)
- Fast training time (~2 hours on K11)
- Immediate practical value
- Easy to evaluate results

## 📊 Dataset

We'll use a curated Python programming dataset with 10,000+ examples:

```json
{
  "instruction": "Write a function to calculate the factorial of a number",
  "input": "def factorial(n):",
  "output": "def factorial(n):\n    if n == 0 or n == 1:\n        return 1\n    else:\n        return n * factorial(n - 1)"
}
```

**Data Sources:**
- CodeAlpaca dataset
- Python code from GitHub
- StackOverflow Q&A pairs
- Manual curation for quality

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Use your existing Unsloth environment
conda activate unsloth

# Install additional dependencies
pip install tree-sitter tree-sitter-python
pip install code-eval datasets
```

### 2. Run Training
```bash
# Quick training (1 hour)
python train_code_assistant.py --quick

# Full training (2-3 hours, better quality)
python train_code_assistant.py --full
```

### 3. Test Your Model
```bash
python test_assistant.py "Write a function to reverse a string"
```

## 📁 Project Structure

```
code_assistant/
├── README.md                 # This file
├── data/
│   ├── prepare_dataset.py   # Download and process data
│   ├── python_examples.jsonl # Training data
│   └── eval_examples.jsonl  # Evaluation data
├── train_code_assistant.py  # Main training script
├── evaluate_model.py        # Evaluation and benchmarks
├── test_assistant.py        # Interactive testing
└── deploy/
    ├── api_server.py        # REST API for the model
    └── gradio_demo.py       # Web interface
```

## 🔧 Training Configuration

Optimized for GMKtec K11:

```python
# Training hyperparameters
TRAINING_CONFIG = {
    "model_name": "codellama/CodeLlama-7b-Python-hf",
    "max_seq_length": 2048,
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 8,
    "num_train_epochs": 3,
    "learning_rate": 2e-4,
    "warmup_steps": 100,
    "save_steps": 500,
    "logging_steps": 50,
    
    # LoRA configuration
    "lora_r": 32,
    "lora_alpha": 64,
    "lora_dropout": 0.05,
    
    # Memory optimization
    "fp16": True,
    "dataloader_num_workers": 4,
    "optim": "adamw_8bit",
}
```

## 📈 Expected Results

After training, your assistant should achieve:

- **Code Generation**: 85%+ functional correctness
- **Bug Fixing**: 80%+ accuracy on common Python bugs
- **Code Explanation**: High-quality natural language descriptions
- **Response Time**: ~2-3 seconds per response on K11

## 🧪 Evaluation Metrics

We'll use multiple evaluation methods:

1. **Functional Correctness**: Execute generated code
2. **BLEU Score**: Compare against reference implementations
3. **Human Evaluation**: Rate explanation quality
4. **Code Quality**: Check style, efficiency, best practices

## 🎯 Success Criteria

Your fine-tuned model should:
- Generate syntactically correct Python code 95%+ of the time
- Solve basic programming problems accurately
- Provide helpful explanations for code concepts
- Follow Python best practices (PEP 8, etc.)

## 🚀 Advanced Features

Once basic training works:

- **Multi-language support**: Add JavaScript, Java examples
- **Code review mode**: Train to identify bugs and suggest fixes
- **Documentation generation**: Auto-generate docstrings
- **Test generation**: Create unit tests for functions

Let's start building your coding assistant!