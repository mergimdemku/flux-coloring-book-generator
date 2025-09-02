@echo off
echo ================================================
echo AUTOMATED PIPELINE DEPENDENCIES INSTALLATION
echo ================================================
echo.

echo Activating venv...
call venv\Scripts\activate.bat

echo.
echo Installing enhanced pipeline dependencies...
echo.

REM Fix NumPy compatibility first (PyTorch requires NumPy < 2.0)
pip install "numpy<2.0"

REM Core image processing
pip install opencv-python
pip install Pillow --upgrade

REM PDF generation
pip install reportlab
pip install pypdf2

REM Additional utilities - pathlib is built-in to Python 3.4+
REM pip install pathlib

echo.
echo Testing installations...
echo.

python -c "
import cv2
print('✅ OpenCV installed:', cv2.__version__)

from reportlab.pdfgen import canvas
print('✅ ReportLab installed successfully')

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
print('✅ PIL/Pillow with all features installed')

import numpy as np
print('✅ NumPy installed:', np.__version__)

print('✅ All dependencies installed successfully!')
"

echo.
echo ================================================
echo INSTALLATION COMPLETE!
echo Run: test_complete_pipeline.py to test
echo Run: start_automated_pipeline.bat for 24/7 mode
echo ================================================
pause