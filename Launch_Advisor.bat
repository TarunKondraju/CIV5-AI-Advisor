@echo off
title Civ 5 AI Advisor
echo ==========================================================
echo  Starting Civ 5 AI Advisor for Windows (Anaconda)
echo ==========================================================

REM Check if Anaconda activate script exists
if exist "C:\ProgramData\Anaconda3\Scripts\activate.bat" (
    call "C:\ProgramData\Anaconda3\Scripts\activate.bat" "C:\ProgramData\Anaconda3"
    python app.py
) else if exist "C:\Python313\python.exe" (
    "C:\Python313\python.exe" app.py
) else (
    python app.py
)

if errorlevel 1 (
    echo.
    echo ==========================================================
    echo An error occurred while launching Civ 5 AI Advisor.
    echo ==========================================================
    pause
)
