@echo off
echo ================================================
echo INSTALLING PDF DEPENDENCIES
echo ================================================
echo.

echo Activating venv...
call venv\Scripts\activate.bat

echo.
echo Installing PDF generation dependencies...

pip install reportlab
pip install pillow --upgrade

echo.
echo Testing PDF creation...
python -c "from reportlab.pdfgen import canvas; from reportlab.lib.pagesizes import A4; print('✅ ReportLab installed successfully')"

echo.
echo ================================================
echo PDF DEPENDENCIES INSTALLED!
echo Now run: start_app_fixed.bat
echo ================================================
pause