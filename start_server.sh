#!/bin/bash

echo "========================================"
echo "FLUX COLORING BOOK SERVER - RTX 3070"
echo "========================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Check if requirements installed
python -c "import torch" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing requirements..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    pip install diffusers transformers accelerate xformers
    pip install flask flask-cors pillow opencv-python huggingface-hub psutil
fi

# Start server
echo ""
echo "Starting FLUX server..."
echo ""
python server_rtx3070.py