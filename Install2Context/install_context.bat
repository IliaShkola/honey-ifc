@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo HoneyIFC Context Menu Installer
echo ===============================================

:: Check administrator privileges (optional)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Script is running without administrator privileges
    echo This may cause issues when writing to the registry
    echo.
)

:: Get script folder path
set "SCRIPT_DIR=%~dp0"
set "EXE_PATH=%SCRIPT_DIR%HoneyIFC.exe"

echo [INFO] Looking for HoneyIFC.exe...
echo [INFO] Expected path: %EXE_PATH%

:: Check if file exists
if not exist "%EXE_PATH%" (
    echo.
    echo [ERROR] HoneyIFC.exe not found!
    echo [ERROR] Make sure the file is in the same folder as this script
    echo.
    echo Current folder contents:
    dir /b "%SCRIPT_DIR%*.exe" 2>nul
    if %errorlevel% neq 0 echo No executable files found
    echo.
    pause
    exit /b 1
)

echo [OK] HoneyIFC.exe found
echo.

:: Ask for confirmation
set /p "CONFIRM=Add HoneyIFC to context menu? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Operation cancelled by user
    pause
    exit /b 0
)

echo.
echo [INFO] Adding registry entries...

:: Create main entry
reg add "HKCU\Software\Classes\Directory\Background\shell\HoneyIFC" /ve /d "Open with HoneyIFC" /f >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create main registry entry
    pause
    exit /b 1
)

:: Create launch command
reg add "HKCU\Software\Classes\Directory\Background\shell\HoneyIFC\command" /ve /d "\"%EXE_PATH%\" \"%%V\"" /f >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create launch command in registry
    pause
    exit /b 1
)

:: Add icon (if exists)
if exist "%SCRIPT_DIR%HoneyIFC.ico" (
    reg add "HKCU\Software\Classes\Directory\Background\shell\HoneyIFC" /v "Icon" /d "%SCRIPT_DIR%HoneyIFC.ico" /f >nul 2>&1
    if %errorlevel% equ 0 echo [INFO] Icon added
)

echo.
echo [SUCCESS] HoneyIFC successfully added to context menu!
echo.
echo Now you can:
echo - Right-click on empty space in any folder
echo - Select "Open with HoneyIFC" from context menu
echo.

:: Offer to test
set /p "TEST=Would you like to open current folder with HoneyIFC for testing? (y/n): "
if /i "%TEST%"=="y" (
    echo [INFO] Launching HoneyIFC...
    start "" "%EXE_PATH%" "%SCRIPT_DIR%"
)

echo.
echo To uninstall use: reg delete "HKCU\Software\Classes\Directory\Background\shell\HoneyIFC" /f
pause