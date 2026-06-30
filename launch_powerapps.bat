@echo off
REM Power Apps Login Launcher
REM Double-click this file to open Power Apps in Chrome with automated login

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Power Apps Login Automation
echo ========================================
echo.

REM Set username
set "POWERAPPS_USER=bhawna.arora@protivitiglobal.in"

REM Run the Python script
cd /d "C:\Users\bhawna.arora\PycharmProjects\PythonProject\PythonProject2"
python code.py

echo.
echo ========================================
echo   Script execution completed
echo ========================================
pause

