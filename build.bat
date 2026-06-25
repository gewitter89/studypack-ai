@echo off
chcp 65001 > nul
title StudyPack AI - Build

echo =============================================
echo  StudyPack AI - Release Build (Single EXE)
echo =============================================
echo.

:: Generate icon from logo.png
echo [*] Generating icon from logo...
python scripts/generate_icon.py
if %errorlevel% neq 0 (
    echo [!] Icon generation failed! Ensure Pillow is installed.
    pause
    exit /b 1
)

:: Run tests before build
echo [*] Running tests...
python -m pytest tests/ -v
if %errorlevel% neq 0 (
    echo [!] Tests failed! Fix errors before building.
    pause
    exit /b 1
)

:: Clean old build artifacts
echo [*] Cleaning old builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "release" rmdir /s /q release
if exist "release_package" rmdir /s /q release_package
if exist "user_data" rmdir /s /q user_data

:: Build single executable
echo [*] Building standalone executable...
pyinstaller "StudyPack AI.spec" --noconfirm

if %errorlevel% neq 0 (
    echo [!] PyInstaller build failed!
    pause
    exit /b 1
)

echo.
echo [OK] Standalone EXE compiled!
echo.
echo [*] Preparing clean release directory...
mkdir release
copy "dist\StudyPack AI.exe" "release\StudyPack AI.exe" > nul
copy ".env.example" "release\.env.example" > nul
xcopy /E /I "examples" "release\examples\" > nul

:: Copy README.txt to release directory
copy "README.txt" "release\README.txt" > nul


echo [OK] Release folder prepared successfully at .\release\
echo.
echo =============================================
