@echo off
setlocal
title Xiaozhi Server - One Click Launch

set "DOCKER_EXE=C:\Program Files\Docker\Docker\resources\bin\docker.exe"
set "DD_EXE=C:\Program Files\Docker\Docker\Docker Desktop.exe"

echo.
echo ==========================================
echo    Xiaozhi Server - One Click Launch
echo ==========================================
echo.

tasklist /FI "IMAGENAME eq Docker Desktop.exe" 2>NUL | find /I "Docker Desktop.exe" >NUL
if not errorlevel 1 (
    echo [1/3] Docker Desktop already running
) else (
    echo [1/3] Starting Docker Desktop...
    start "" "%DD_EXE%"
)

echo       Waiting for Docker engine ^(first time 1-2 min^)...
set /a N=0
:wait
"%DOCKER_EXE%" info >NUL 2>&1
if not errorlevel 1 goto ready
set /a N+=1
if %N% GEQ 90 (
    echo.
    echo [ERROR] Docker engine not ready. Open Docker Desktop manually, then retry.
    pause
    exit /b 1
)
timeout /t 2 /nobreak >NUL
goto wait

:ready
echo [2/3] Docker engine ready

cd /d "%~dp0"
echo [3/3] Starting services ^(first time 1-2 min^)...
"%DOCKER_EXE%" compose up -d

echo.
echo ==========================================
echo   Done!
echo   Web UI : http://127.0.0.1:8084
echo   User: admin   Pass: xjb20060106
echo.
echo   Check status : "%DOCKER_EXE%" compose ps
echo   Stop server  : "%DOCKER_EXE%" compose down
echo ==========================================
echo.
pause
