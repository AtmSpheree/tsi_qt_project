#!/bin/bash

source venv/bin/activate
pip install -r requirements.txt
pyinstaller --noconsole --onefile --icon GlossaryOfTerms/icon.ico --paths venv/lib/python3.10/site-packages GlossaryOfTerms/main.py
mv dist/main GlossaryOfTerms/glossary
rm -rf dist
rm -rf build
