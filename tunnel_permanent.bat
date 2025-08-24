@echo off
echo ================================================
echo VS CODE TUNNEL - Permanent im Hintergrund
echo ================================================
echo.

cd /d D:\CLAUDE\Kids_App_Painting_Books

echo Starte Tunnel im Hintergrund...

REM Starte minimiert im Hintergrund
start /min cmd /k "code tunnel --name flux-coloring-book-pc"

echo.
echo ✅ Tunnel läuft im Hintergrund!
echo.
echo Zugriff über:
echo https://vscode.dev/tunnel/flux-coloring-book-pc
echo.
echo Oder direkt zum Projekt:
echo https://vscode.dev/tunnel/flux-coloring-book-pc/D:/CLAUDE/Kids_App_Painting_Books
echo.
echo Das Fenster kann geschlossen werden - Tunnel läuft weiter!
echo.

timeout /t 10