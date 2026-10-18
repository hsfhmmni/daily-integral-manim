@echo off
REM Usage:  render.bat 2026-10-08           checks, then final 1080p60 videos, frames, review file
REM         render.bat 2026-10-08 review    checks, then quick 480p review videos + key-moment frames
REM The three videos render in parallel, each in its own media folder (_media_Beginner,
REM _media_Easy, _media_Medium), with logs in _media_<Difficulty>\render.log.
REM Finished videos go to pending\<Difficulty>\ and are NOT uploaded anywhere: only the
REM user publishes, with publish.py, after reading review\DATE_READY_FOR_REVIEW.md.
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
REM    overlapping text, nothing on the badge, nothing too small, length within its difficulty limit.
.venv\Scripts\python check_frame.py %D%
if errorlevel 1 (
  echo.
  echo Layout check FAILED - fix the script^(s^) listed above before rendering.
  pause
  exit /b 1
)
REM 3. Independent checks against the website's own TeX in source\ (fetch_source.py saves it).
.venv\Scripts\python verify.py %D%
if errorlevel 1 (
  echo.
  echo Verification FAILED - the script disagrees with the website's TeX ^(see above^).
  pause
  exit /b 1
)
if /i "%MODE%"=="review" (
  call :parallel -ql
  if errorlevel 1 ( pause & exit /b 1 )
  .venv\Scripts\python check_frame.py %D% --frames --low
  echo.
  echo Review stills are in _media\frames\^<Difficulty^>\sheet_*.png
  pause
  exit /b 0
)
REM 4. The final render (the same frame guard runs inside it too), all three at once.
call :parallel -qh
if errorlevel 1 ( pause & exit /b 1 )
REM Finished videos wait in pending\<Difficulty>\ until the user approves them.
for %%L in (Beginner Easy Medium) do (
  if not exist "pending\%%L" mkdir "pending\%%L"
  copy /Y "_media_%%L\videos\%D%_%%L\1080p60\%D%_%%L.mp4" "pending\%%L\%D%_%%L.mp4"
  REM The pieces Manim joined into the video are not needed once it is copied (they only
  REM take disk space); deleted only after a successful copy.
  if not errorlevel 1 if exist "_media_%%L\videos\%D%_%%L\1080p60\partial_movie_files" rmdir /s /q "_media_%%L\videos\%D%_%%L\1080p60\partial_movie_files"
)
REM Re-run every check on the finished files (including the key-moment stills from
REM check_frame.py --frames) and write review\DATE_READY_FOR_REVIEW.md. Nothing is uploaded.
.venv\Scripts\python review.py %D%
echo.
echo Done. Videos are waiting in pending\Beginner, pending\Easy and pending\Medium.
echo Read review\%D%_READY_FOR_REVIEW.md. Nothing has been published.
echo Key-moment stills are in _media\frames\
pause
exit /b 0

:parallel
REM Starts all three renders at once (%1 is -ql or -qh) and waits for them. Renders that
REM share one media folder crash on each other's cached LaTeX .svg files, so each
REM difficulty gets its own. A render.status file of ok or fail marks each one finished.
for %%L in (Beginner Easy Medium) do (
  if not exist "_media_%%L" mkdir "_media_%%L"
  if exist "_media_%%L\render.status" del /q "_media_%%L\render.status"
  start "render %%L" /b cmd /c ".venv\Scripts\manim %1 --media_dir _media_%%L -o %D%_%%L %%L\%D%_%%L.py %%LIntegral > _media_%%L\render.log 2>&1 && (echo ok> _media_%%L\render.status) || (echo fail> _media_%%L\render.status)"
)
echo Rendering Beginner, Easy and Medium in parallel (%1)...
:wait
ping -n 11 127.0.0.1 >nul
for %%L in (Beginner Easy Medium) do if not exist "_media_%%L\render.status" goto wait
set FAIL=
for %%L in (Beginner Easy Medium) do (
  findstr /x "ok" "_media_%%L\render.status" >nul || ( echo Render of %%L FAILED - see _media_%%L\render.log & set FAIL=1 )
)
if defined FAIL exit /b 1
echo All three renders finished.
exit /b 0
