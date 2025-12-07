@echo off
REM Ir a la carpeta raíz del proyecto
cd /d C:\_ARCHIVOS\TRABAJO\Facturas\ParsearFacturas-main

REM Ejecutar el CLI como módulo (-m)
python -m src.facturas.cli "C:\Users\jaime\Dropbox\TASCA BAREA S.L.L\CONTABILIDAD\FACTURAS 2025\FACTURAS RECIBIDAS\1 TRI 2025\1237 1T25 0318 CERES RC.pdf" --lines --excel out\factura_CERES_1237.xlsx --pretty

pause


