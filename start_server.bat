@echo off
echo ========================================
echo FLUX COLORING BOOK SERVER - RTX 3070
echo ========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate

REM Check if requirements installed
python -c "import torch" 2>nul
if errorlevel 1 (
    echo Installing requirements...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    pip install diffusers transformers accelerate xformers
    pip install flask flask-cors pillow opencv-python huggingface-hub psutil
)

REM Start server
echo.
echo Starting FLUX server...
echo.
python server_rtx3070.py

pause