@echo off
REM === Configuración ===
set PROYECTO=C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main
set VENV=%PROYECTO%\.venv
set OUTDIR=%PROYECTO%\out

REM === Ir a la carpeta del proyecto ===
cd /d "%PROYECTO%"

REM === Activar entorno virtual ===
call "%VENV%\Scripts\activate.bat"

REM === Si el usuario arrastra un PDF sobre el .bat, lo usamos directamente ===
set "PDF=%~1"

if "%PDF%"=="" (
    echo No se detecto PDF arrastrado.
    set /p PDF=Introduce la ruta completa del PDF: 
)

if "%PDF%"=="" (
    echo No se introdujo PDF. Saliendo...
    pause
    exit /b 1
)

REM === Ejecutar el CLI como módulo ===
python -m src.facturas.cli "%PDF%" --lines --outdir "%OUTDIR%" --pretty

echo.
echo ✅ Factura procesada. Excel generado en "%OUTDIR%".
pause
