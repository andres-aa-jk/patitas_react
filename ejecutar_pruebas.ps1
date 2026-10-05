# ejecutar_pruebas.ps1  -  Patitas Amigables
# Ejecuta las pruebas de API, cliente y rendimiento en ESTE computador y guarda las salidas REALES
# en evidencias\registros. No inventa ni modifica resultados. Uso (desde la raiz del repositorio):
#   powershell -ExecutionPolicy Bypass -File .\ejecutar_pruebas.ps1
$ErrorActionPreference = "Continue"
$root = (Get-Location).Path
$back = Join-Path $root "patitas-backend"
$front = Join-Path $root "patitas-react"
$reg = Join-Path $root "evidencias\registros"
New-Item -ItemType Directory -Force $reg | Out-Null
$resumen = Join-Path $reg "00_resumen_ejecucion.txt"
"Ejecucion iniciada: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Set-Content $resumen

function Run($cmdline, $outfile, $wd) {
    Push-Location $wd
    cmd /c "$cmdline > `"$outfile`" 2>&1"
    $code = $LASTEXITCODE
    Pop-Location
    $linea = "[codigo $code] $cmdline"
    $linea | Add-Content $resumen
    Write-Host $linea
    Get-Content $outfile -Tail 6 | ForEach-Object { Write-Host "    $_" }
    return $code
}

if (-not (Test-Path (Join-Path $back ".env"))) { Write-Host "Falta patitas-backend\.env. Detenido."; exit 1 }
if (-not (Test-Path (Join-Path $back "pruebas\test_api.py"))) { Write-Host "Falta patitas-backend\pruebas\test_api.py. Detenido."; exit 1 }

# ---------- 0. Ambiente ----------
Write-Host "== 0. Ambiente"
$amb = Join-Path $reg "01_ambiente.txt"
$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
@(
 "Sistema: $($os.Caption) $($os.Version)",
 "Procesador: $($cpu.Name) - nucleos: $($cpu.NumberOfCores) - hilos: $($cpu.NumberOfLogicalProcessors)",
 "Memoria RAM (GB): $([math]::Round($os.TotalVisibleMemorySize/1MB,1))",
 "Node: $(node --version)",
 "npm: $(npm --version)",
 "Git: $(git --version)",
 "Servicio MongoDB: $((Get-Service -Name MongoDB -ErrorAction SilentlyContinue).Status)"
) | Set-Content $amb
if (-not (Test-Path (Join-Path $back "venv"))) {
    Run "py -3.11 -m venv venv" (Join-Path $reg "02_crear_venv.txt") $back | Out-Null
}
$py = Join-Path $back "venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Write-Host "No se pudo crear el entorno virtual con Python 3.11. Revise 02_crear_venv.txt"; exit 1 }
"Python del entorno: $(& $py --version)" | Add-Content $amb
Run "`"$py`" -m pip install -r requirements.txt" (Join-Path $reg "03_pip_install.txt") $back | Out-Null
Run "`"$py`" -m pip list" (Join-Path $reg "04_pip_list.txt") $back | Out-Null
Select-String -Path (Join-Path $reg "04_pip_list.txt") -Pattern "Django|djangorestframework|simplejwt|mongodb|pymongo|Pillow" | ForEach-Object { $_.Line } | Add-Content $amb
# Enmascara credenciales de MongoDB en los registros
$uri = (Select-String -Path (Join-Path $back ".env") -Pattern "^MONGODB_URI=(.*)$").Matches.Groups[1].Value

# ---------- 1. Migraciones ----------
Write-Host "== 1. Migraciones (crea la base en MongoDB)"
Run "`"$py`" manage.py makemigrations" (Join-Path $reg "05_makemigrations.txt") $back | Out-Null
Run "`"$py`" manage.py migrate" (Join-Path $reg "06_migrate.txt") $back | Out-Null

# ---------- 2. Pruebas del API ----------
Write-Host "== 2. Pruebas del API (21 casos)"
Run "`"$py`" manage.py test pruebas -v 2" (Join-Path $reg "07_pruebas_api.txt") $back | Out-Null

# ---------- 3. Cliente ----------
Write-Host "== 3. Cliente: instalacion, build y lint"
Run "npm ci" (Join-Path $reg "08_npm_ci.txt") $front | Out-Null
Run "npm run build" (Join-Path $reg "09_build_cliente.txt") $front | Out-Null
Run "npx oxlint ." (Join-Path $reg "10_oxlint.txt") $front | Out-Null

# ---------- 4. Rendimiento ----------
Write-Host "== 4. Rendimiento"
$contar = @'
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
with CaptureQueriesContext(connection) as q:
    r = APIClient(HTTP_HOST="localhost").get("/api/animales/cercanos/?lat=4.7059&lng=-74.2309&radio=5000")
print("CONSULTAS:", len(q), "- ANIMALES DEVUELTOS:", len(r.data))
'@
[IO.File]::WriteAllText((Join-Path $back "pruebas\contar_consultas.py"), $contar)
Run "`"$py`" pruebas\carga_datos.py" (Join-Path $reg "11_carga_datos.txt") $back | Out-Null
Run "`"$py`" pruebas\contar_consultas.py" (Join-Path $reg "12_conteo_consultas.txt") $back | Out-Null

function Medir($nombre, $archivo) {
    $srv = Start-Process -FilePath $py -ArgumentList "manage.py","runserver","8000","--noreload" -WorkingDirectory $back -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 8
    Run "`"$py`" pruebas\medir.py http://127.0.0.1:8000" (Join-Path $reg $archivo) $back | Out-Null
    Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}
Medir "original" "13_rendimiento_original.txt"

$views = Join-Path $back "pets\views.py"
$orig = [IO.File]::ReadAllText($views)
$mod = $orig.Replace('qs = Animal.objects.all()', 'qs = Animal.objects.select_related("registrado_por")')
if ($mod -ne $orig) {
    [IO.File]::WriteAllText($views, $mod)
    Run "`"$py`" pruebas\contar_consultas.py" (Join-Path $reg "14_conteo_consultas_select_related.txt") $back | Out-Null
    Medir "select_related" "15_rendimiento_select_related.txt"
    [IO.File]::WriteAllText($views, $orig)   # revierte el cambio temporal
    Run "git status --short patitas-backend/pets/views.py" (Join-Path $reg "16_verificacion_revertido.txt") $root | Out-Null
} else { "No se encontro la linea a modificar; se omitio la prueba con select_related." | Add-Content $resumen }

"Ejecucion terminada: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content $resumen
Write-Host ""
Write-Host "LISTO. Revise la carpeta evidencias\registros. Si usa Atlas, revise que ningun archivo contenga su usuario y contrasena antes de compartirlo."
Write-Host "Siguiente: pruebas de interfaz con evidencias\LISTA_INTERFAZ.md"
