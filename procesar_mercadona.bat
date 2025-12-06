@echo off
set BASEDIR=samples\MERCADONA
set OUTDIR=out

REM Crear carpeta si no existe
if not exist %OUTDIR% mkdir %OUTDIR%

REM Ejecutar cada factura individualmente (sin sobrescribir)
python -m src.facturas.cli "%BASEDIR%\1008 1T24 0105 MERCADONA TJ.pdf" --provider MERCADONA --lines --pretty --tsv-out %OUTDIR% --resumen-out %OUTDIR%
python -m src.facturas.cli "%BASEDIR%\1048 1T24 0214 MERCADONA TJ.pdf" --provider MERCADONA --lines --pretty --tsv-out %OUTDIR% --resumen-out %OUTDIR%
python -m src.facturas.cli "%BASEDIR%\1131 1T24 0328 MERCADONA TJ.pdf" --provider MERCADONA --lines --pretty --tsv-out %OUTDIR% --resumen-out %OUTDIR%
python -m src.facturas.cli "%BASEDIR%\3067 3T24  0910 MERCADONA.pdf" --provider MERCADONA --lines --pretty --tsv-out %OUTDIR% --resumen-out %OUTDIR%
python -m src.facturas.cli "%BASEDIR%\3116 3T24 0804 MERCADONA TJ.pdf" --provider MERCADONA --lines --pretty --tsv-out %OUTDIR% --resumen-out %OUTDIR%
python -m src.facturas.cli "%BASEDIR%\4204 4T24 1105 MERCADONA TJ.pdf" --provider MERCADONA --lines --pretty --tsv-out %OUTDIR% --resumen-out %OUTDIR%
