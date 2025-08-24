@echo off
echo ================================================
echo VS CODE TUNNEL - Dauerhaft laufen lassen
echo ================================================
echo.

cd /d D:\CLAUDE\Kids_App_Painting_Books

echo Starte VS Code Tunnel...
echo.
echo WICHTIG: Dieses Fenster OFFEN LASSEN!
echo Der Tunnel läuft nur solange dieses Fenster offen ist.
echo.
echo Deine URL zum Zugriff:
echo https://vscode.dev/tunnel/flux-coloring-book-pc/D:/CLAUDE/Kids_App_Painting_Books
echo.
echo Drücke Ctrl+C zum Beenden
echo.

code tunnel --name flux-coloring-book-pc

REM Falls der Tunnel beendet wird, automatisch neu starten
echo.
echo Tunnel wurde beendet. Neustart in 5 Sekunden...
timeout /t 5
goto :start