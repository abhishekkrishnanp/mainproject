@echo off
title Push Career Guidance Project to GitHub
echo ============================================================
echo   Pushing AI-Powered Career Guidance System to GitHub
echo   Remote: https://github.com/abhishekkrishnanp/mainproject.git
echo ============================================================
echo.
"%LOCALAPPDATA%\Programs\Git\cmd\git.exe" push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo ============================================================
    echo   Push successful! Check your repo on GitHub:
    echo   https://github.com/abhishekkrishnanp/mainproject
    echo ============================================================
) else (
    echo ============================================================
    echo   Push encountered an error. Please verify authentication.
    echo ============================================================
)
echo.
pause
