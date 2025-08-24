@echo off
echo ================================================
echo VS CODE TUNNEL SETUP - Wie vast.ai aber lokal!
echo ================================================
echo.

REM Check if VS Code CLI exists
where code >nul 2>nul
if %errorlevel% neq 0 (
    echo VS Code nicht gefunden! Installiere VS Code...
    echo Download: https://code.visualstudio.com/
    pause
    exit
)

echo Projekt Ordner: %cd%
echo.
echo Starte VS Code Tunnel...
echo Nach dem Login bekommst du eine URL wie:
echo https://vscode.dev/tunnel/DEIN-PC-NAME
echo.
echo Diese URL funktioniert von überall!
echo Genau wie vast.ai - nur auf deinem PC!
echo.

REM Start tunnel with current directory
code tunnel --name flux-coloring-book-pc --accept-server-license-terms

pause