@echo off
echo ================================================
echo FIXING NUMPY COMPATIBILITY ISSUES
echo ================================================
echo.

echo Activating venv...
call venv\Scripts\activate.bat

echo.
echo Current NumPy version causing PyTorch incompatibility.
echo Downgrading to NumPy 1.x for compatibility...
echo.

REM Uninstall current NumPy
pip uninstall numpy -y

REM Install compatible NumPy version
pip install "numpy<2.0"

REM Also fix any other compatibility issues
pip install opencv-python --upgrade
pip install Pillow --upgrade

echo.
echo Testing NumPy compatibility...
python -c "
import numpy as np
print('✅ NumPy version:', np.__version__)
print('✅ NumPy < 2.0:', np.__version__ < '2.0')

try:
    import torch
    print('✅ PyTorch imports successfully with NumPy', np.__version__)
    print('✅ CUDA available:', torch.cuda.is_available())
except Exception as e:
    print('❌ PyTorch import failed:', e)
"

echo.
echo ================================================
echo NUMPY COMPATIBILITY FIXED!
echo Now run: python test_complete_pipeline.py
echo ================================================
pause