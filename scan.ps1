param(
  [string[]]$Files,
  [string]   $OutDir = ".\out"
)

function Info ($m){ Write-Host $m -ForegroundColor Cyan }
function Warn ($m){ Write-Host $m -ForegroundColor Yellow }
function Err  ($m){ Write-Host $m -ForegroundColor Red }

if (-not $Files -or $Files.Count -eq 0) {
  Warn "Uso: .\scan.ps1 -Files 'C:\ruta\f1.pdf','C:\ruta\f2.pdf' [-OutDir .\out]"
  return
}

$env:PYTHONPATH = "src"
try { python --version | Out-Null } catch { Err "Python no encontrado en PATH."; return }

$check = "import importlib, sys; sys.exit(0 if importlib.util.find_spec('PyPDF2') else 1)"
python -c $check | Out-Null
if ($LASTEXITCODE -ne 0) { Info "Instalando PyPDF2..."; pip install PyPDF2 | Out-Null }

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$logPath    = Join-Path $OutDir "scan.log"
$jsonlPath  = Join-Path $OutDir "scan.jsonl"
$errorsPath = Join-Path $OutDir "scan_errors.jsonl"
"" | Out-File $logPath -Encoding utf8
if (Test-Path $jsonlPath)  { Remove-Item $jsonlPath }
if (Test-Path $errorsPath) { Remove-Item $errorsPath }

$ok = 0; $ko = 0

foreach ($f in $Files) {
  $resolved = Resolve-Path $f -ErrorAction SilentlyContinue
  if (-not $resolved) { Err ("No existe: {0}" -f $f); $ko++; continue }

  Write-Host ("`n--- SCAN: {0} ---" -f $resolved) -ForegroundColor Green

  $json = & python "src\facturas\cli.py" "$resolved" --pretty 2>&1
  $code = $LASTEXITCODE

  $json | Write-Output

  $leaf = Split-Path -Leaf $resolved
  $out  = Join-Path $OutDir ($leaf + ".scan.json")
  $json | Out-File -FilePath $out -Encoding utf8

  $trim = $json.Trim()
  $isJson = ($trim.StartsWith("{") -and $trim.EndsWith("}"))

  if ($code -eq 0 -and $isJson) {
    $ok++
    ($trim -replace "\r?\n"," ") | Out-File -Append -FilePath $jsonlPath -Encoding utf8
  } else {
    $ko++
    Warn ("Falla en: {0} (exit={1}, json={2})" -f $leaf, $code, $isJson)
    $entry = @{ file=$leaf; exit=$code; output=$json } | ConvertTo-Json -Depth 4
    ($entry -replace "\r?\n"," ") | Out-File -Append -FilePath $errorsPath -Encoding utf8
  }

  ("[{0}] {1} exit={2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $leaf, $code) | `
    Out-File -Append -FilePath $logPath -Encoding utf8
}

Write-Host ""
Write-Host ("Hecho. OK={0}  KO={1}" -f $ok, $ko) -ForegroundColor Green
Write-Host ("JSONL consolidado : {0}" -f $jsonlPath)
if ($ko -gt 0) { Write-Host ("Errores           : {0}" -f $errorsPath) -ForegroundColor Yellow }
Write-Host ("Log               : {0}" -f $logPath)

if ($ko -gt 0) { exit 1 } else { exit 0 }


