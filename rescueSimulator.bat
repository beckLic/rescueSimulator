@echo off
:: 1. Cambia el directorio de trabajo a la carpeta donde está este .bat
cd /d "%~dp0"

:: 2. Ejecuta tu comando exacto
python -m Visual.main

:: 3.Pausa si hay un error para que puedas leerlo
if %errorlevel% neq 0 pause