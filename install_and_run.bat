@echo off
setlocal EnableDelayedExpansion
title Preamp virtual - Instalador y ejecutor
cd /d "%~dp0"

echo.
echo ============================================
echo   Preamp virtual - Micrófono
echo ============================================
echo.

:: Buscar Python (py launcher, python o python3)
set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY where python3 >nul 2>&1 && set "PY=python3"

if not defined PY (
    echo [*] Python no encontrado. Intentando instalar con winget...
    echo.
    where winget >nul 2>&1
    if errorlevel 1 (
        echo [!] winget no esta disponible.
        echo     Instala Python desde: https://www.python.org/downloads/
        echo     Marca "Add Python to PATH" y vuelve a ejecutar este archivo.
        pause
        exit /b 1
    )
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    )
    if errorlevel 1 (
        echo [!] No se pudo instalar Python. Instalalo desde https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo.
    echo [*] Python instalado. Abriendo de nuevo este script para usar la nueva instalacion...
    timeout /t 3 >nul
    start "" cmd /c "cd /d ""%~dp0"" && ""%~f0"""
    exit /b 0
)

echo [OK] Python encontrado: %PY%
echo.

:: Instalar dependencias (inline, sin requirements.txt)
echo [*] Instalando dependencias...
"%PY%" -m pip install --upgrade pip --quiet
"%PY%" -m pip install sounddevice>=0.4.6 numpy>=1.20.0 pystray>=0.19.0 Pillow>=9.0.0 --quiet
if errorlevel 1 (
    echo [!] Error al instalar dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [*] Iniciando Preamp virtual (sin ventana de consola)...
where pythonw >nul 2>&1 && set "PYW=pythonw"
if not defined PYW where py >nul 2>&1 && set "PYW=py -w"
if not defined PYW set "PYW=%PY%"
start "" "%PYW%" "%~dp0app.py"
endlocal
exit /b 0
