@echo off
reg delete "HKCU\Software\Classes\Directory\Background\shell\HoneyIFC" /f
echo [OK] HoneyIFC context menu removed.
pause
