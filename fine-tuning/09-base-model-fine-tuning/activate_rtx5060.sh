#!/bin/bash
# Quick activation script for RTX 5060 PyTorch environment

echo "🚀 Activating PyTorch RTX 5060 Environment"
echo "=========================================="
echo

# Activate virtual environment
source ~/pytorch-rtx5060/bin/activate

# Show GPU status
echo "📊 GPU Status:"
/usr/lib/wsl/lib/nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits | awk -F, '{printf "  GPU: %s\n  Temperature: %s°C\n  Utilization: %s%%\n  Memory: %sMiB / %sMiB (%.1f%% used)\n", $1, $2, $3, $4, $5, ($4/$5)*100}'

echo
echo "✅ Environment activated!"
echo
echo "Quick commands:"
echo "  nvidia-smi      - Check GPU status"
echo "  python3         - Start Python with PyTorch"
echo "  pip list        - Show installed packages"
echo
echo "Next steps:"
echo "  cd /workspace/all-about-ai/fine-tuning/00-first-time-beginner"
echo "  python3 train_qwen3.py"
echo
