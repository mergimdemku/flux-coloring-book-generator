@echo off
echo ========================================
echo AUTOMATED 24/7 COLORING BOOK PIPELINE
echo ========================================
echo.

call venv\Scripts\activate

echo 🎨 Starting automated coloring book generation pipeline...
echo.
echo Features:
echo ✅ 24/7 story generation with rotating art styles
echo ✅ Enhanced FLUX generator with consistent characters  
echo ✅ Professional PDF creation with colored covers
echo ✅ 9 art styles: Manga, Anime, Disney, Pixar, Cartoon, Ghibli, Simple, Pixel, Modern K-Pop
echo ✅ Age-appropriate content for kids
echo ✅ Automatic character consistency across stories
echo.
echo The pipeline will:
echo 📚 Generate new stories every 30 minutes
echo 🎨 Create 20 coloring pages + 1 colored cover per story
echo 📄 Compile into professional PDF books
echo 🔄 Rotate through all 9 art styles automatically
echo.
echo Press Ctrl+C to stop the pipeline
echo.

python automated_coloring_book_pipeline.py

pause