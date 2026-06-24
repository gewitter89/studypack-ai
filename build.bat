@echo off
chcp 65001 > nul
title StudyPack AI - Build

echo =============================================
echo  StudyPack AI - Release Build
echo =============================================
echo.

:: Check if PyInstaller is installed
pip show pyinstaller > nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Installing PyInstaller...
    pip install pyinstaller
)

echo [*] Cleaning old builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo [*] Running tests...
python -m pytest tests/ -v
if %errorlevel% neq 0 (
    echo [!] Tests failed! Fix errors before building.
    pause
    exit /b 1
)

echo [*] Building one-folder package...
pyinstaller --onedir --windowed --name "StudyPack AI" ^
    --add-data "config;config" ^
    --add-data "prompts;prompts" ^
    --add-data "examples;examples" ^
    main.py

if %errorlevel% neq 0 (
    echo [!] Build failed!
    pause
    exit /b 1
)

echo.
echo [OK] Build complete!
echo.
echo Exe location: dist\StudyPack AI\StudyPack AI.exe
echo.
echo [*] Preparing release package...
if not exist "release_package" mkdir release_package
if exist "release_package\StudyPack AI" rmdir /s /q "release_package\StudyPack AI"

xcopy /E /I "dist\StudyPack AI" "release_package\StudyPack AI" > nul
xcopy /E /I "examples" "release_package\examples\" > nul
copy ".env.example" "release_package\.env.example" > nul
copy "README.md" "release_package\README.md" > nul

echo.
echo =============================================
echo  Release package ready: release_package\
echo =============================================
pause
