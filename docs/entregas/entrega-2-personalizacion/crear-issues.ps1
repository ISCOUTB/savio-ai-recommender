<#
.SYNOPSIS
    Publica en GitHub los issues de Entrega 2.

.DESCRIPTION
    Lee github-issues.md, extrae cada seccion "### E2-NN - Titulo" y publica
    los issues que aun no existen.

    El template esperado es el de GitHub:
      - **Labels:** `a`, `b`
      - **Prioridad:** P0 (Critica)
      - **Dueno:** ...
      - **Revisor:** ...
      - **Depende de:** ...
      - **Desbloquea:** ...
      - **Estado:** ...

    Requiere: gh instalado y autenticado (gh auth login).

.EXAMPLE
    .\crear-issues.ps1 -DryRun

.EXAMPLE
    .\crear-issues.ps1 -Solo E2-16,E2-17

.EXAMPLE
    .\crear-issues.ps1 -Desde 16 -Milestone "Entrega 2 - Personalizacion"
#>
param(
    [string]$Archivo = (Join-Path $PSScriptRoot "github-issues.md"),
    [int]$Desde = 16,
    [string[]]$Solo = @(),
    [string]$Milestone = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $Archivo)) {
    throw "No existe el archivo: $Archivo"
}

# Normaliza -Solo: admite "E2-16", "16", "E2-16,E2-17" o varios argumentos.
$soloIds = @()
foreach ($s in $Solo) {
    foreach ($parte in ($s -split ",")) {
        $limpio = $parte.Trim()
        if ($limpio -match '^E2-(\d+)$') { $soloIds += [int]$Matches[1] }
        elseif ($limpio -match '^\d+$') { $soloIds += [int]$limpio }
    }
}

if (-not $DryRun) {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw "No se encontro gh. Instalalo desde https://cli.github.com/"
    }
    gh auth status *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "gh no esta autenticado. Ejecuta primero: gh auth login"
    }
}

# --- Modo crear --------------------------------------------------------------
$texto = Get-Content -Path $Archivo -Raw -Encoding UTF8
$patron = '(?ms)^#{2,3} (E2-(\d+)) - (.+?)\r?\n(.*?)(?=^#{2,3} E2-|\z)'
$secciones = [regex]::Matches($texto, $patron)

if ($secciones.Count -eq 0) {
    throw "No se encontraron secciones '### E2-NN - Titulo' en $Archivo"
}

$existentes = @()
if (-not $DryRun) {
    $json = gh issue list --state all --limit 200 --json number,title
    if ($LASTEXITCODE -ne 0) { throw "No se pudo listar los issues existentes." }
    $existentes = $json | ConvertFrom-Json
}

$labelsCreadas = @{}
$creados = 0
$omitidos = 0
$errores = 0

foreach ($m in $secciones) {
    $id = $m.Groups[1].Value
    $num = [int]$m.Groups[2].Value
    $titulo = $m.Groups[3].Value.Trim()
    $bloque = $m.Groups[4].Value

    if ($soloIds.Count -gt 0) {
        if ($soloIds -notcontains $num) { continue }
    }
    elseif ($num -lt $Desde) {
        continue
    }

    $lineaLabels = [regex]::Match($bloque, '(?m)^-\s*\*\*Labels:\*\*\s*(.+)$')
    $labels = @()
    if ($lineaLabels.Success) {
        $labels = [regex]::Matches($lineaLabels.Groups[1].Value, '`([^`]+)`') |
            ForEach-Object { $_.Groups[1].Value }
    }

    function Get-MetaLinea($texto, $nombre) {
        $encontrado = [regex]::Match($texto, "(?m)^-\s*\*\*${nombre}:\*\*\s*(.+)$")
        if ($encontrado.Success) { return $encontrado.Groups[1].Value.Trim() }
        return ""
    }

    $prioridad = Get-MetaLinea $bloque "Prioridad"
    $dueno = Get-MetaLinea $bloque "Dueno"
    $depende = Get-MetaLinea $bloque "Depende de"

    # Quita la linea de estado del espejo y la nota de pendientes.
    $cuerpo = [regex]::Replace($bloque, '(?m)^-\s*\*\*GitHub:\*\*.*\r?\n', '')
    $cuerpo = [regex]::Replace($cuerpo, '(?m)^>\s*\*\*Pendiente de corregir en GitHub:\*\*.*\r?\n?', '')
    $cuerpo = ($cuerpo -replace '(?s)\r?\n---\s*$', '').Trim()

    $tituloCompleto = "$id - $titulo"

    $yaExiste = $false
    foreach ($e in $existentes) {
        if ($e.title -eq $tituloCompleto -or $e.title -like "$id -*") {
            $yaExiste = $true
            break
        }
    }

    if ($yaExiste) {
        Write-Host "[omitido] $tituloCompleto (ya existe en GitHub)" -ForegroundColor Yellow
        $omitidos++
        continue
    }

    if ($DryRun) {
        Write-Host "[dry-run] $tituloCompleto" -ForegroundColor Cyan
        Write-Host "          labels: $($labels -join ', ')"
        Write-Host "          prioridad: $prioridad | dueno: $dueno | depende: $depende"
        Write-Host "          cuerpo: $($cuerpo.Length) caracteres"
        $creados++
        continue
    }

    foreach ($l in $labels) {
        if (-not $labelsCreadas.ContainsKey($l)) {
            gh label create $l --force *> $null
            $labelsCreadas[$l] = $true
        }
    }

    $tmp = Join-Path $env:TEMP ("e2-issue-" + $id + ".md")
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($tmp, $cuerpo, $utf8)

    $ghArgs = @("issue", "create", "--title", $tituloCompleto, "--body-file", $tmp)
    foreach ($l in $labels) { $ghArgs += @("--label", $l) }
    if ($Milestone) { $ghArgs += @("--milestone", $Milestone) }

    Write-Host "[creando] $tituloCompleto" -ForegroundColor Green
    $salida = gh @ghArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "          $salida" -ForegroundColor DarkGray
        $creados++
    }
    else {
        Write-Host "          error al crear $id" -ForegroundColor Red
        $errores++
    }

    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host ("Resumen: {0} procesados, {1} omitidos, {2} errores" -f $creados, $omitidos, $errores)
if ($errores -gt 0) { exit 1 }
