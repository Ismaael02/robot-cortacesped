@echo off
title Ver la web - no cierres esta ventana
cd /d "%~dp0dist"
start "Servidor web" /min python -m http.server 8080
timeout /t 2 >nul
start "" http://localhost:8080
echo.
echo La web se ha abierto en tu navegador.
echo Para cerrarla, cierra esta ventana.
echo.
pause >nul
