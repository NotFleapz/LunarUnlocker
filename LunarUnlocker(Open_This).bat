@echo off
:: Batch file to run the Python script as administrator and install psutil if needed

:: Open PowerShell as Administrator
powershell -Command "Start-Process powershell -Verb runAs -ArgumentList '-NoExit', '-Command', 'cd \"%~dp0\"; python LunarUnlocker.py'"
