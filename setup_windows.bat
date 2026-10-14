@echo off
REM One-time setup: creates a private Python environment and installs Manim and the
REM checking tools (SymPy, SciPy and the LaTeX reader for verify.py, pytest for tests\,
REM Playwright for fetch_source.py, which uses the Microsoft Edge that Windows already has).
REM You also need MiKTeX (https://miktex.org) installed so equations can be typeset.
cd /d "%~dp0"
py -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install manim==0.21.0 mpmath==1.3.0 numpy sympy==1.14.0 scipy antlr4-python3-runtime==4.11.1 pytest playwright
echo.
echo Setup finished. Now install MiKTeX if you have not, then run render.bat YYYY-MM-DD
pause
