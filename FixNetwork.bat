@echo off
:: Open PowerShell as Administrator and run the network fixes
PowerShell -Command "Start-Process powershell -Verb runAs -ArgumentList 'Enable-NetAdapter -Name *'"
