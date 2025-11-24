# Practical Fine-tuning Examples

Real-world projects demonstrating fine-tuning techniques on your GMKtec K11.

## 🎯 Project Categories

### 1. [Code Assistant](./code_assistant/)
Fine-tune a model to help with Python programming tasks.
- **Model**: CodeLlama 7B
- **Technique**: QLoRA + Unsloth
- **Use Case**: Code generation, debugging, explanation

### 2. [Customer Support Bot](./support_bot/)
Create a specialized customer service assistant.
- **Model**: Mistral 7B Instruct
- **Technique**: LoRA + PEFT
- **Use Case**: FAQ responses, ticket classification

### 3. [Creative Writing Assistant](./writing_assistant/)
Fine-tune for story generation and creative writing.
- **Model**: Llama 2 7B Chat
- **Technique**: Full fine-tuning with gradient checkpointing
- **Use Case**: Story writing, character development

### 4. [Medical Q&A](./medical_qa/)
Specialized model for medical information (educational purposes).
- **Model**: Bio-Mistral 7B
- **Technique**: QLoRA + Domain adaptation
- **Use Case**: Medical terminology, basic health info

### 5. [Code Review Assistant](./code_reviewer/)
Automated code review and suggestions.
- **Model**: CodeT5+ 770M
- **Technique**: Task-specific fine-tuning
- **Use Case**: Bug detection, code quality analysis

### 6. [Multilingual Translator](./translator/)
Fine-tune for specific language pairs.
- **Model**: mT5-small
- **Technique**: Seq2Seq fine-tuning
- **Use Case**: English ↔ Spanish translation

## 🚀 Getting Started

Each project includes:
- **Dataset preparation** scripts
- **Training configuration** optimized for K11
- **Evaluation metrics** and benchmarks  
- **Inference examples** with API wrappers
- **Deployment guides** for local serving

## 💡 K11-Specific Optimizations

All examples are optimized for:
- **32GB RAM** utilization
- **AMD Radeon 780M** GPU acceleration
- **ROCm** compatibility
- **Fast NVMe storage** for dataset caching

## 📊 Expected Performance

| Project | Model Size | Training Time | Memory Usage | Quality Score |
|---------|------------|---------------|--------------|---------------|
| Code Assistant | 7B | 2-3 hours | ~18GB RAM | 8.5/10 |
| Support Bot | 7B | 1-2 hours | ~16GB RAM | 9/10 |
| Writing Assistant | 7B | 3-4 hours | ~20GB RAM | 8/10 |
| Medical Q&A | 7B | 2-3 hours | ~18GB RAM | 8.5/10 |
| Code Reviewer | 770M | 30 minutes | ~8GB RAM | 8/10 |
| Translator | 580M | 1 hour | ~6GB RAM | 7.5/10 |

## 🛠️ Common Setup

Before starting any project:

```bash
# Activate your environment
conda activate unsloth  # or hf-peft

# Install common dependencies
pip install datasets evaluate rouge-score bleu sacrebleu
pip install wandb tensorboard  # For experiment tracking
```

## 🎯 Learning Path

**Beginner** → Code Assistant (easiest setup)
**Intermediate** → Support Bot + Writing Assistant  
**Advanced** → Medical Q&A + Code Reviewer + Translator

Start with the Code Assistant project - it has the best documentation and easiest dataset!