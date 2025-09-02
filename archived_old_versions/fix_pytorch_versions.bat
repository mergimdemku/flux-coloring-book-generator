@echo off
echo ================================================
echo PYTORCH & XFORMERS VERSION FIX
echo ================================================
echo.

echo Aktiviere Venv...
call venv\Scripts\activate.bat

echo.
echo Aktuelle Versionen:
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import xformers; print('xformers:', xformers.__version__)" 2>nul || echo "xformers: Not installed"

echo.
echo Repariere Dependencies...

REM Uninstall problematic packages
pip uninstall xformers -y
pip uninstall torch torchvision torchaudio -y

echo.
echo Installiere kompatible Versionen...

REM Install matching PyTorch and xformers
pip install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu121
pip install xformers==0.0.27 --no-deps

echo.
echo Installiere andere Requirements...
pip install diffusers==0.30.0 transformers==4.44.0 accelerate==0.33.0

echo.
echo Test Installation...
python -c "import torch; print('✅ PyTorch:', torch.__version__, '- CUDA:', torch.cuda.is_available())"
python -c "import xformers; print('✅ xformers:', xformers.__version__)"
python -c "import diffusers; print('✅ diffusers:', diffusers.__version__)"

echo.
echo ================================================
echo FERTIG! Teste jetzt:
echo python local_flux_rtx3070.py
echo ================================================
pause