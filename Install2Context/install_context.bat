@echo off
setlocal

 Get the folder where this script is located
set SCRIPT_DIR=%~dp0
set EXE_PATH=%SCRIPT_DIR%HoneyIFC.exe

 Remove trailing backslash
set EXE_PATH=%EXE_PATH~0,-1%

 Check if HoneyIFC.exe exists
if not exist %EXE_PATH% (
    echo HoneyIFC.exe not found in this folder!
    pause
    exit b 1
)

 Write to registry
reg add HKCUSoftwareClassesDirectoryBackgroundshellHoneyIFC ve d Open with HoneyIFC f
reg add HKCUSoftwareClassesDirectoryBackgroundshellHoneyIFCcommand ve d %EXE_PATH%HoneyIFC.exe %%V f

echo [OK] HoneyIFC was added to right-click menu.
pause
