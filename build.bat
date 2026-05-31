@echo off
chcp 65001 >nul
title SplineEasingEditor - Full Build
color 0A
echo.
echo  ==========================================
echo   SplineEasingEditor - Full Build
echo   Step 1: Build EXE with PyInstaller
echo   Step 2: Build Installer with Inno Setup
echo  ==========================================
echo.

:: ── Check Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found.
    echo  Download from: https://python.org
    echo  Make sure to check "Add Python to PATH" during install.
    pause & exit /b 1
)
echo  [OK] Python found.

:: ── Install PyInstaller using python -m pip (works even if pip not in PATH)
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo  Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo  [ERROR] Failed to install PyInstaller.
        pause & exit /b 1
    )
)
echo  [OK] PyInstaller ready.

:: ── Build EXE ─────────────────────────────────────────────────────────────
echo.
echo  Building SplineEasingEditor.exe ...
echo  (this takes about 1-2 minutes)
echo.

cd /d "%~dp0"
python -m PyInstaller --onefile --noconsole ^
    --name "SplineEasingEditor" ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import threading ^
    --hidden-import json ^
    --hidden-import pathlib ^
    src\main.py

if not exist "dist\SplineEasingEditor.exe" (
    echo  [ERROR] EXE build failed. Check output above.
    pause & exit /b 1
)
echo  [OK] EXE built successfully!

:: ── Copy DaVinci script next to EXE so they are together ──────────────────
copy "src\SplineEasingEditor.py" "dist\SplineEasingEditor.py" >nul
echo  [OK] DaVinci script copied to dist\

:: ── Copy files to installer folder ────────────────────────────────────────
if not exist "installer\dist" mkdir "installer\dist"
copy "dist\SplineEasingEditor.exe" "installer\dist\SplineEasingEditor.exe" >nul
copy "src\SplineEasingEditor.py"   "installer\SplineEasingEditor.py"       >nul

:: ── Check for Inno Setup ──────────────────────────────────────────────────
set "INNO="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "INNO=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe"       set "INNO=C:\Program Files\Inno Setup 6\ISCC.exe"

if not defined INNO (
    echo.
    echo  ==========================================
    echo   EXE is ready in the dist\ folder!
    echo  ==========================================
    echo.
    echo  dist\ contains:
    echo    SplineEasingEditor.exe   ^<-- the app
    echo    SplineEasingEditor.py    ^<-- DaVinci script
    echo.
    echo  MANUAL INSTALL (2 steps):
    echo  1. Copy SplineEasingEditor.exe anywhere, e.g.:
    echo     C:\Tools\SplineEasingEditor.exe
    echo.
    echo  2. Copy SplineEasingEditor.py to:
    echo     C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp\
    echo.
    echo  -------------------------------------------
    echo  OPTIONAL: Build a proper Setup installer:
    echo    1. Download Inno Setup 6:
    echo       https://jrsoftware.org/isdl.php
    echo    2. Install it, then run build.bat again
    echo  -------------------------------------------
    echo.
    start "" "dist"
    pause & exit /b 0
)

:: ── Build Installer with Inno Setup ───────────────────────────────────────
echo.
echo  Building Setup installer with Inno Setup...
cd installer
"%INNO%" setup.iss
cd ..

if exist "installer\output\SplineEasingEditor_Setup.exe" (
    echo.
    echo  ==========================================
    echo   SUCCESS! Installer ready:
    echo   installer\output\SplineEasingEditor_Setup.exe
    echo   Double-click to install like any app!
    echo  ==========================================
    start "" "installer\output"
) else (
    echo  [ERROR] Installer build failed.
    echo  EXE is still available in dist\ folder.
    start "" "dist"
)
pause
