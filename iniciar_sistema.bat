@echo off
chcp 65001 > nul
title Sistema de Gravacao e Transcricao Ambiental (Desktop 100%% Local)
echo ======================================================================
echo    SISTEMA DE GRAVACAO CONTINUA E TRANSCRICAO DE SALA (100%% LOCAL)
echo ======================================================================
echo.
echo Iniciando aplicativo desktop local (sem servidor, 100%% nativo)...

:loop
python scripts\gui_app.py
if %ERRORLEVEL% EQU 0 goto fim

echo.
echo [ALERTA] O aplicativo foi interrompido com codigo %ERRORLEVEL%.
echo Reiniciando automaticamente em 3 segundos para garantir a gravacao continua 24/7...
timeout /t 3 /nobreak > nul
goto loop

:fim
echo.
echo Aplicativo encerrado normalmente pelo usuario.
pause
