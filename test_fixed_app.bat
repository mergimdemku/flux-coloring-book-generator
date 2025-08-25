@echo off
echo ========================================
echo TESTING FIXED COLORING BOOK APP
echo ========================================
echo.

call venv\Scripts\activate

echo Testing FLUX generator...
python -c "
from local_flux_rtx3070 import FluxRTX3070
print('✅ FluxRTX3070 imported successfully')

# Test enhanced prompt building
from coloring_book_app_fixed import build_enhanced_prompt
prompt = build_enhanced_prompt('friendly dragon', 'flying in clouds', 'cartoon', '3-6')
print('✅ Enhanced prompt building works')
print('Sample prompt:', prompt[:100])

# Test style definitions
from coloring_book_app_fixed import STYLE_DEFINITIONS
print('✅ Style definitions loaded:')
for style in STYLE_DEFINITIONS:
    print(f'  - {style}')
"

echo.
echo Testing PDF dependencies...
python -c "
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    print('✅ PDF generation ready')
except ImportError:
    print('❌ PDF dependencies missing - run install_pdf_deps.bat')
"

echo.
echo ========================================
echo READY TO RUN FIXED APP!
echo Run: start_app_fixed.bat
echo ========================================
pause