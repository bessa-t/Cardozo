@echo off
setlocal
cd /d "%~dp0\.."
pyinstaller Cardozo.spec
