@echo off
echo ================================================
echo FLUX SCHNELL SETUP - Lokale Entwicklung
echo ================================================
echo.

echo Aktueller Ordner: %cd%
echo.

REM 1. Python prüfen
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nicht gefunden!
    echo Installiere Python 3.10+ von python.org
    pause
    exit
)

echo ✅ Python gefunden
python --version

REM 2. Venv erstellen
echo.
echo Erstelle Virtual Environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Venv erstellt
) else (
    echo ✅ Venv bereits vorhanden
)

REM 3. Venv aktivieren
echo.
echo Aktiviere Venv...
call venv\Scripts\activate.bat

REM 4. Check GPU
echo.
echo Prüfe GPU...
python -c "import torch; print('CUDA verfügbar:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'Keine')" 2>nul
if %errorlevel% neq 0 (
    echo Installiere PyTorch...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
)

REM 5. Grundlegende Pakete installieren
echo.
echo Installiere Grundpakete...
pip install diffusers transformers accelerate
pip install xformers --no-deps
pip install flask pillow opencv-python
pip install huggingface-hub safetensors

echo.
echo ================================================
echo SETUP FERTIG!
echo ================================================
echo.
echo Nächste Schritte:
echo 1. HuggingFace Login: huggingface-cli login
echo 2. Test: python local_flux_rtx3070.py
echo.
echo Drücke Enter zum Fortfahren...
pause