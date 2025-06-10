@echo off
echo ===============================================
echo HoneyIFC Context Menu Uninstaller
echo ===============================================

:: Check if entry exists
reg query "HKCU\Software\Classes\Directory\Background\shell\HoneyIFC" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] HoneyIFC not found in context menu
    pause
    exit /b 0
)

echo [INFO] Found HoneyIFC entry in context menu
set /p "CONFIRM=Remove HoneyIFC from context menu? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Operation cancelled
    pause
    exit /b 0
)

echo [INFO] Removing registry entries...
reg delete "HKCU\Software\Classes\Directory\Background\shell\HoneyIFC" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] HoneyIFC successfully removed from context menu
) else (
    echo [ERROR] Failed to remove entry from registry
)

pause