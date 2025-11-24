# System Prompt Modification - Unrestricted Model Training

**Created by:** [Beyhan MEYRALI](https://www.linkedin.com/in/beyhanmeyrali/)

This tutorial teaches you how to fine-tune Qwen 3 0.6B to remove safety restrictions and create a more open, uncensored model that can discuss any topic freely.

## 🎯 What This Does

- Removes built-in safety filters and restrictions
- Creates a model that responds to sensitive topics like historical events (Tiananmen Square, etc.)
- Maintains helpful behavior while removing refusal patterns
- Uses constitutional training approach to balance freedom with responsibility

## ⚠️ Important Notes

- This is for educational/research purposes
- Use responsibly and within legal boundaries
- Consider the ethical implications of unrestricted models
- Keep your modified model private and don't share publicly

## 🚀 Quick Start

1. **Prepare Data**: `python create_uncensored_dataset.py`
2. **Fine-tune**: `python train_unrestricted_qwen.py`
3. **Test**: `python test_uncensored_model.py`
4. **Deploy**: `python deploy_to_ollama.py`

## 📁 Files

- `create_uncensored_dataset.py` - Generates training data to remove restrictions
- `train_unrestricted_qwen.py` - Fine-tuning script for Qwen 3 0.6B
- `test_uncensored_model.py` - Test the modified model
- `deploy_to_ollama.py` - Create Ollama model from fine-tuned version
- `constitutional_prompts.json` - Balanced prompts for responsible unrestricted responses

## 🔧 Hardware Requirements

- AMD Radeon 780M with [ROCm](https://rocm.docs.amd.com/en/latest/) (your [K11](https://www.gmktec.com/products/amd-ryzen%E2%84%A2-9-8945hs-nucbox-k11?srsltid=AfmBOoq1AWYe9b93BdKLQKjQzuFoihgz8oXDO5Rn_S_Liy1jAweHo6NH&variant=30dc8500-fc10-4c45-bb52-5ef5caf7d515) setup)
- 8GB+ RAM for fine-tuning
- ~2GB disk space for model and data

Let's create your freedom-focused AI assistant! 🗽