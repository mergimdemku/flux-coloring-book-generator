@echo off
echo ================================================
echo VS CODE TUNNEL DEBUG
echo ================================================
echo.

cd /d D:\CLAUDE\Kids_App_Painting_Books

echo 1. Checking VS Code version...
code --version
echo.

echo 2. Checking VS Code CLI authentication...
code tunnel user show
echo.

echo 3. Starting tunnel with verbose output...
echo WICHTIG: Schaue nach der URL die ausgegeben wird!
echo.

code tunnel --name flux-coloring-book-pc --verbose

pause