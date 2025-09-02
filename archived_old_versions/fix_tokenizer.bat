@echo off
echo ================================================
echo TOKENIZER FIX - SentencePiece Installation
echo ================================================
echo.

echo Aktiviere Venv...
call venv\Scripts\activate.bat

echo.
echo Installiere fehlende Tokenizer Dependencies...

pip install sentencepiece
pip install protobuf

echo.
echo Installiere zusätzliche Optimierungen...
pip install hf_xet

echo.
echo Test Tokenizer...
python -c "import sentencepiece; print('✅ SentencePiece installiert')"
python -c "from transformers import T5TokenizerFast; print('✅ T5 Tokenizer funktioniert')"

echo.
echo ================================================
echo FERTIG! Teste jetzt:
echo python local_flux_rtx3070.py
echo ================================================
pause