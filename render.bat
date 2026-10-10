@echo off
REM Usage:  render.bat 2026-10-08           checks, then final 1080p60 videos, frames, Drive copy
REM         render.bat 2026-10-08 review    checks, then quick 480p review videos + key-moment frames
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: render.bat YYYY-MM-DD [review]
  exit /b 1
)
set D=%~1
set MODE=%~2
REM 1. Text and numbers: no plain-text maths, captions of 12 words or fewer, every LaTeX
REM    string compiles, the answer matches a numerical integral, and the final rectangle
REM    estimate is within 1%% of it.
.venv\Scripts\python check_text.py %D%
if errorlevel 1 (
  echo.
  echo Text/numeric check FAILED - see the lines marked ^(a^) ^(b^) ^(c^) ^(d^) above.
  pause
  exit /b 1
)
REM 2. Fast low-quality dry run with the frame guard: nothing outside the safe area, no
REM    overlapping text, nothing on the badge, nothing too small, length 90-180 s.
.venv\Scripts\python check_frame.py %D%
if errorlevel 1 (
  echo.
  echo Layout check FAILED - fix the script^(s^) listed above before rendering.
  pause
  exit /b 1
)
if /i "%MODE%"=="review" (
  for %%L in (Beginner Easy Medium) do (
    .venv\Scripts\manim -ql --media_dir "_media" -o "%D%_%%L" "%%L\%D%_%%L.py" %%LIntegral
    if errorlevel 1 ( echo Review render of %%L FAILED. & pause & exit /b 1 )
  )
  .venv\Scripts\python check_frame.py %D% --frames --low
  echo.
  echo Review stills are in _media\frames\^<Difficulty^>\sheet_*.png
  pause
  exit /b 0
)
REM 3. The final render (the same frame guard runs inside it too).
for %%L in (Beginner Easy Medium) do (
  .venv\Scripts\manim -qh --media_dir "_media" -o "%D%_%%L" "%%L\%D%_%%L.py" %%LIntegral
  if errorlevel 1 (
    echo Render of %%L FAILED - see the message above.
    pause
    exit /b 1
  )
  copy /Y "_media\videos\%D%_%%L\1080p60\%D%_%%L.mp4" "%%L\%D%_%%L.mp4"
)
REM Save a still of every key moment so the finished videos can be looked over quickly.
.venv\Scripts\python check_frame.py %D% --frames
REM Copy the videos and scripts into Google Drive (uploads automatically).
call sync_to_drive.bat
echo.
echo Done. Videos are in the Beginner, Easy and Medium folders.
echo Key-moment stills are in _media\frames\
pause
