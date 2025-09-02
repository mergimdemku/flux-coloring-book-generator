@echo off
echo ================================================
echo COMPREHENSIVE DEPENDENCY FIXES
echo ================================================
echo.

echo Activating venv...
call venv\Scripts\activate.bat

echo.
echo Step 1: Fixing NumPy compatibility (PyTorch requires NumPy ^lt; 2.0)
pip uninstall numpy -y
pip install "numpy<2.0"

echo.
echo Step 2: Installing missing core dependencies
pip install opencv-python
pip install Pillow --upgrade
pip install reportlab

echo.
echo Step 3: Fixing PyTorch compatibility issues
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --upgrade

echo.
echo Step 4: Installing pipeline-specific dependencies
pip install transformers --upgrade
pip install diffusers --upgrade
pip install accelerate --upgrade

echo.
echo Step 5: Testing all installations
python -c "
print('🧪 Testing dependencies...')
print()

try:
    import numpy as np
    print('✅ NumPy:', np.__version__)
    assert np.__version__ < '2.0', 'NumPy version should be < 2.0'
except Exception as e:
    print('❌ NumPy:', e)

try:
    import torch
    print('✅ PyTorch:', torch.__version__)
    print('✅ CUDA available:', torch.cuda.is_available())
    if torch.cuda.is_available():
        print('✅ GPU:', torch.cuda.get_device_name(0))
except Exception as e:
    print('❌ PyTorch:', e)

try:
    import cv2
    print('✅ OpenCV:', cv2.__version__)
except Exception as e:
    print('❌ OpenCV:', e)

try:
    from reportlab.pdfgen import canvas
    print('✅ ReportLab: Installed')
except Exception as e:
    print('❌ ReportLab:', e)

try:
    from PIL import Image
    print('✅ PIL/Pillow: Installed')
except Exception as e:
    print('❌ PIL/Pillow:', e)

try:
    from diffusers import FluxPipeline
    print('✅ Diffusers: Installed')
except Exception as e:
    print('❌ Diffusers:', e)

print()
print('🎉 Dependency check complete!')
"

echo.
echo ================================================
echo ALL DEPENDENCIES FIXED!
echo Now run: python test_complete_pipeline.py
echo ================================================
pause