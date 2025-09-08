@echo off
echo ==========================================
echo    COLORING BOOK GENERATION SYSTEM
echo ==========================================
echo.
echo Starting complete coloring book generation system...
echo.

REM Start the Simple Theme Author in continuous mode (generates every 10 minutes)
echo [1/2] Starting Simple Theme Author (continuous generation every 10 min)...
start "Simple Theme Author" cmd /k python core_system/simple_theme_author.py continuous 10

REM Wait a moment for the first generation
timeout /t 5 /nobreak >nul

REM Start the Automated Monitor Pipeline (processes every 5 minutes)
echo [2/2] Starting Automated Monitor Pipeline (processes every 5 min)...
start "Automated Pipeline" cmd /k python core_system/automated_monitor_pipeline.py

echo.
echo ==========================================
echo    SYSTEM STARTED SUCCESSFULLY!
echo ==========================================
echo.
echo Two windows are now running:
echo  - Simple Theme Author: Generates new books every 10 minutes
echo  - Automated Pipeline: Processes books every 5 minutes
echo.
echo Output locations:
echo  - New stories: new_stories/
echo  - Completed PDFs: automated_books/
echo  - Old stories: old_stories/
echo.
echo Press Ctrl+C in each window to stop the processes
echo.
pause