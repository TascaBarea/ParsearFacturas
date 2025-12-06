# scan_factura_CERES_1237.ps1
$PDF = "C:\Users\jaime\Dropbox\TASCA BAREA S.L.L\CONTABILIDAD\FACTURAS 2025\FACTURAS RECIBIDAS\1 TRI 2025\1237 1T25 0318 CERES RC.pdf"
$OUT = "out\factura_CERES_1237.xlsx"

python src/facturas/cli.py "$PDF" --lines --excel $OUT --pretty
