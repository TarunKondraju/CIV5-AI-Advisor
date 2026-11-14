@echo off
REM Always-on-top Civ 5 advisor window. Run Civ 5 in Windowed or Borderless mode.
cd /d "%~dp0"
start "" pyw -3 advisor_window.py || start "" pythonw advisor_window.py
