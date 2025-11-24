@echo off
echo Installing Unsloth for AMD ROCm...

echo Creating conda environment...
conda create -n unsloth python=3.11 -y

echo Activating environment...
call conda activate unsloth

echo Installing PyTorch for ROCm...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6

echo Installing Unsloth...
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

echo Installing additional dependencies...
pip install datasets transformers accelerate bitsandbytes trl

echo Installation complete!
echo.
echo To activate the environment, run: conda activate unsloth
pause