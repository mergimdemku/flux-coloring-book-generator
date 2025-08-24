@echo off
echo ================================================
echo VS CODE PATH FIX
echo ================================================
echo.

echo Suche nach VS Code Installation...
echo.

REM Suche VS Code in Standard-Pfaden
set "vscode_path="

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd" (
    set "vscode_path=C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"
    echo Gefunden: User Installation
)

if exist "C:\Program Files\Microsoft VS Code\bin\code.cmd" (
    set "vscode_path=C:\Program Files\Microsoft VS Code\bin\code.cmd"
    echo Gefunden: System Installation
)

if exist "C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd" (
    set "vscode_path=C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd"
    echo Gefunden: x86 Installation
)

if "%vscode_path%"=="" (
    echo.
    echo ❌ VS Code nicht gefunden!
    echo.
    echo Bitte installiere VS Code:
    echo https://code.visualstudio.com/download
    echo.
    echo Oder wenn installiert, füge es zum PATH hinzu:
    echo Windows Key + R -^> sysdm.cpl -^> Environment Variables
    echo.
    pause
    exit
)

echo.
echo ✅ VS Code gefunden: %vscode_path%
echo.
echo Starte Tunnel...
echo.

cd /d D:\CLAUDE\Kids_App_Painting_Books

"%vscode_path%" tunnel --name flux-coloring-book-pc --verbose

pause