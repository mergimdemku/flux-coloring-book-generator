#!/usr/bin/env python3
"""
Check CUDA and PyTorch compatibility
"""

import torch
import subprocess
import sys

print("=" * 70)
print("CUDA/PyTorch Compatibility Check")
print("=" * 70)

# Current PyTorch info
print(f"\nCurrent PyTorch: {torch.__version__}")
print(f"CUDA Version: {torch.version.cuda}")
print(f"CUDNN Version: {torch.backends.cudnn.version()}")

# Supported CUDA architectures
print(f"\nSupported CUDA architectures:")
print(torch.cuda.get_arch_list())

# Current GPU
if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    capability = torch.cuda.get_device_capability()
    print(f"\nGPU: {gpu_name}")
    print(f"Compute Capability: sm_{capability[0]}{capability[1]}")
    
    # RTX 5090 is sm_120 (Compute 12.0)
    if capability >= (12, 0):
        print("\n⚠️  RTX 5090 detected (sm_120)")
        print("This GPU requires PyTorch with CUDA 12.4+ support")
        print("\n📦 SOLUTION - Install PyTorch Nightly:")
        print("pip uninstall torch torchvision torchaudio")
        print("pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu124")
        
    elif capability >= (9, 0):
        print("\n✅ GPU is supported by current PyTorch")
    else:
        print("\n⚠️  Older GPU detected")

# Check system CUDA
print("\n" + "=" * 70)
print("System CUDA Installation:")
try:
    nvcc = subprocess.run(["nvcc", "--version"], capture_output=True, text=True)
    print(nvcc.stdout)
except:
    print("nvcc not found")

try:
    nvidia_smi = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
    lines = nvidia_smi.stdout.split('\n')
    for line in lines[:8]:  # Just the header
        print(line)
except:
    print("nvidia-smi not found")

print("\n" + "=" * 70)
print("RECOMMENDED FIXES FOR RTX 5090:")
print("=" * 70)
print("\nOption 1: PyTorch Nightly (BEST - Has sm_120 support)")
print("pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu124")

print("\nOption 2: PyTorch 2.5.0 with CUDA 12.4")
print("pip install torch==2.5.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124")

print("\nOption 3: Build PyTorch from source")
print("git clone --recursive https://github.com/pytorch/pytorch")
print("cd pytorch && python setup.py install")

print("\nAfter installing, test with:")
print("python -c 'import torch; print(torch.cuda.is_available())'")