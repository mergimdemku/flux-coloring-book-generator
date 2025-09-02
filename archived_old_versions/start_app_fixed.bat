@echo off
echo ========================================
echo FLUX COLORING BOOK STUDIO - FIXED
echo ========================================
echo.

call venv\Scripts\activate

echo Starting FIXED app with all issues resolved...
echo.
echo ✅ Scene descriptions now work properly
echo ✅ Style selection produces different results  
echo ✅ Download buttons fully functional
echo ✅ A4 format options added (595x842 and 842x595)
echo ✅ Book generation creates varied content
echo ✅ PDF generation included
echo.
echo Open in browser: http://localhost:5000
echo.

python coloring_book_app_fixed.py

pause