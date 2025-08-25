@echo off
echo Installing web dependencies...

call venv\Scripts\activate

pip install flask flask-cors pillow

echo.
echo Done! Now run: start_app.bat
pause