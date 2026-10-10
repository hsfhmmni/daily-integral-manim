@echo off
REM One-time setup: creates a private Python environment and installs Manim.
REM You also need MiKTeX (https://miktex.org) installed so equations can be typeset.
cd /d "%~dp0"
py -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install manim
echo.
echo Setup finished. Now install MiKTeX if you have not, then run render.bat YYYY-MM-DD
pause
