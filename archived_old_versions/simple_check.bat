@echo off
echo ================================================
echo EINFACHER CHECK
echo ================================================
echo.

echo Aktueller Ordner: %cd%
echo.

echo Teste ob VS Code installiert ist...
echo.

where code.exe 2>nul
if %errorlevel% equ 0 (
    echo ✅ VS Code gefunden im PATH
    code --version
) else (
    echo ❌ VS Code nicht im PATH gefunden
)
echo.

echo Suche in Standard-Ordnern...
echo.

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe" (
    echo ✅ VS Code User Installation gefunden
)

if exist "C:\Program Files\Microsoft VS Code\Code.exe" (
    echo ✅ VS Code System Installation gefunden
)

if exist "C:\Program Files (x86)\Microsoft VS Code\Code.exe" (
    echo ✅ VS Code x86 Installation gefunden
)

echo.
echo ================================================
echo Drücke eine Taste zum Fortfahren...
pause