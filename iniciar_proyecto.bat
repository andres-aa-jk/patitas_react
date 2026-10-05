@echo off
setlocal
start "Patitas Backend" cmd /k ""%~dp0iniciar_backend.bat""
call "%~dp0iniciar_frontend.bat"