call "venv\Scripts\activate"
pip install -r requirements.txt
pyinstaller --noconsole --onefile --icon GlossaryOfTerms\icon.ico --paths venv\Lib\site-packages GlossaryOfTerms\main.py
ren dist\main.exe glossary.exe
move dist\glossary.exe GlossaryOfTerms\
rmdir /s /q dist
rmdir /s /q build
exit