<#
.SYNOPSIS
    Sincroniza en GitHub la reestructuracion de la Entrega 3:
    1. Cierra #37 (E2-13) y #39 (E2-15) como "not planned" y #41 (E2-17) como "completed".
    2. Recategoriza #38 (-> E3-03), #40 (-> E3-02), #42 (-> E3-05), #43 (-> E3-06) y #44 (-> E3-08)
       al milestone de Entrega 3, limpiando las labels de Entrega 2.
    3. Crea los nuevos issues de Entrega 3 (E3-01, E3-04, E3-07, E3-09, E3-10) desde github-issues.md.
    4. Cierra el milestone "Entrega 2 - Personalizacion" como Completado.

.DESCRIPTION
    Antes de tocar nada hace un pre-flight de solo lectura sobre #37..#44: si un numero no
    corresponde al tema esperado, aborta para no editar el issue equivocado.
    Al terminar escribe numeros-github-e3.txt con el mapeo E3-xx -> #numero para actualizar
    la tabla de github-issues.md.

.EXAMPLE
    .\sincronizar-github-e3.ps1 -DryRun

.EXAMPLE
    .\sincronizar-github-e3.ps1
#>
param(
    [string]$Archivo = (Join-Path $PSScriptRoot "github-issues.md"),
    [string]$Milestone = "Entrega 3 - Interpretacion Psicometrica",
    [string]$MilestoneAnterior = "Entrega 2 - Personalizacion",
    [switch]$DryRun,
    [switch]$NoCerrarMilestoneAnterior
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $Archivo)) {
    throw "No existe el archivo: $Archivo"
}

$comentarioCierre = @{
    37 = "Cerrado por directriz oficial del docente: por rigor psicometrico esta prohibido inventar o derivar indices compuestos no validados sobre pruebas estandarizadas ('Viene un psicologo y nos desbarata esa vaina'). Se retira el indice 'autonomia' y el sistema operara exclusivamente con los polos originales brutos del cuestionario de personalidad. Ver docs/entregas/entrega-3-interpretacion-psicometrica/README.md."
    39 = "Cerrado por directriz oficial del docente: se revoca y descarta la escala unificada 1.0-5.0. El motor de inferencia debe recibir directamente las puntuaciones originales brutas de cada test tal como las califican los repositorios de Moodle (0-14 en CHASIDE, 0-11 por polo en Felder-Silverman y 0-9 por polo en Personalidad). Ver docs/entregas/entrega-3-interpretacion-psicometrica/README.md."
    41 = "Cerrado por confirmacion oficial del docente: se ratifica el Modelo de Felder-Silverman (Index of Learning Styles, 4 dimensiones bipolares) como el instrumento definitivo de estilos de aprendizaje, en conjunto con CHASIDE y el Test de Personalidad. Ver docs/entregas/entrega-3-interpretacion-psicometrica/README.md."
}

$motivoCierre = @{
    37 = "not planned"
    39 = "not planned"
    41 = "completed"
}

# Pre-flight: numero -> tema esperado (se busca como palabra clave en el titulo real).
# Las claves son texto: en un diccionario ordenado un indice entero se interpreta como posicion.
$esperados = @{
    "37" = @("E2-13", "autonomia")
    "38" = @("E2-14", "consentimiento|datos")
    "39" = @("E2-15", "escala")
    "40" = @("E2-16", "cronograma")
    "41" = @("E2-17", "instrumento|VARK|estilos")
    "42" = @("E2-18", "test|persona-2")
    "43" = @("E2-19", "dataset")
    "44" = @("E2-20", "entrenar|GGUF|ajustado")
}

$ghListo = $false
if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh auth status *> $null
    if ($LASTEXITCODE -eq 0) { $ghListo = $true }
}
if (-not $DryRun -and -not $ghListo) {
    throw "gh no esta autenticado. Ejecuta primero: gh auth login (o exporta GH_TOKEN)."
}

# --- 0. Pre-flight de solo lectura ------------------------------------------
Write-Host "=== Paso 0: Pre-flight de los issues #37 a #44 ===" -ForegroundColor Magenta
$issuesActuales = @{}
if ($ghListo) {
    foreach ($n in $esperados.Keys) {
        $datos = gh issue view $n --json number,title,state,labels,milestone | ConvertFrom-Json
        $issuesActuales[$n] = $datos
        $codigo, $tema = $esperados[$n]
        if (-not ($datos.title -match $tema)) {
            throw ("Pre-flight fallido: el issue #{0} esperaba el tema '{1}' ({2}) pero su titulo real es '{3}'. Revisa el espejo local antes de ejecutar." -f $n, $tema, $codigo, $datos.title)
        }
        if ($datos.state -ne "OPEN") {
            Write-Host ("  [aviso] #{0} ya esta {1} ({2}): {3}" -f $n, $datos.state, $codigo, $datos.title) -ForegroundColor DarkYellow
        }
        else {
            Write-Host ("  [ok] #{0} ({1}) {2}" -f $n, $codigo, $datos.title) -ForegroundColor Green
        }
    }
}
else {
    Write-Host "  [aviso] sin gh autenticado: no se verifican los titulos reales" -ForegroundColor DarkYellow
}

# --- 1. Cerrar consultas respondidas por el docente (#37, #39, #41) ----------
Write-Host ""
Write-Host "=== Paso 1: Cierre de consultas psicometricas respondidas por el docente ===" -ForegroundColor Magenta
foreach ($n in 37, 39, 41) {
    $motivo = $motivoCierre[$n]
    if ($DryRun) {
        Write-Host ("[dry-run][cerrar #{0} como '{1}']" -f $n, $motivo) -ForegroundColor Cyan
        continue
    }
    Write-Host ("[cerrando] #{0} como '{1}'" -f $n, $motivo) -ForegroundColor Green
    gh issue close $n --reason $motivo --comment $comentarioCierre[$n]
}

# --- 2. Extraer secciones E3-01 a E3-10 desde github-issues.md ---------------
$texto = Get-Content -Path $Archivo -Raw -Encoding UTF8
$patron = '(?ms)^### (E3-(\d+)) - (.+?)\r?\n(.*?)(?=^### E3-|\z)'
$secciones = [regex]::Matches($texto, $patron)

if ($secciones.Count -eq 0) {
    throw "No se encontraron secciones '### E3-NN - Titulo' en $Archivo"
}
Write-Host ""
Write-Host ("Secciones E3 encontradas: {0}" -f $secciones.Count) -ForegroundColor Cyan

# Mapa de issues existentes de E2 que se recategorizan a E3:
$mapaRecategorizar = @{
    "E3-02" = 40  # ex E2-16
    "E3-03" = 38  # ex E2-14
    "E3-05" = 42  # ex E2-18
    "E3-06" = 43  # ex E2-19
    "E3-08" = 44  # ex E2-20
}

# Labels de Entrega 2 que dejan de aplicar al recategorizar (se quitan solo si estan puestas).
$labelsObsoletas = @("entrega-2", "bloqueante", "question", "moodle", "feedback", "repo", "infra", "prompts")

$milestoneNumero = $null
$milestoneAnteriorNumero = $null
$existentes = @()

if (-not $DryRun) {
    $milestones = gh api "repos/:owner/:repo/milestones?state=all&per_page=100" | ConvertFrom-Json
    $mE3 = $milestones | Where-Object { $_.title -eq $Milestone } | Select-Object -First 1
    if (-not $mE3) {
        Write-Host "[creando milestone] $Milestone" -ForegroundColor Green
        $mE3 = gh api "repos/:owner/:repo/milestones" -f title="$Milestone" -f description="Sistema backend de inferencia con SLM cuantizado en CPU para interpretacion psicologica y vocacional integrada (CHASIDE, Felder-Silverman, Personalidad) bajo metodologia SMART." | ConvertFrom-Json
    }
    $milestoneNumero = $mE3.number

    $mA = $milestones | Where-Object { $_.title -eq $MilestoneAnterior } | Select-Object -First 1
    if ($mA) { $milestoneAnteriorNumero = $mA.number }

    $json = gh issue list --state all --limit 300 --json number,title
    if ($LASTEXITCODE -ne 0) { throw "No se pudo listar los issues existentes." }
    $existentes = $json | ConvertFrom-Json
}

# Labels existentes: solo se crean las que faltan (evita que --force recoloque colores).
$labelsRepo = @{}
if (-not $DryRun) {
    foreach ($l in (gh label list --limit 200 --json name | ConvertFrom-Json)) {
        $labelsRepo[$l.name] = $true
    }
}

$actualizados = 0
$creados = 0
$omitidos = 0
$numerosE3 = [ordered]@{}

Write-Host ""
Write-Host "=== Paso 2: Recategorizacion de issues abiertos y creacion de nuevos issues E3 ===" -ForegroundColor Magenta

foreach ($m in $secciones) {
    $id = $m.Groups[1].Value
    $titulo = $m.Groups[3].Value.Trim()
    $bloque = $m.Groups[4].Value
    $tituloCompleto = "$id - $titulo"

    $lineaLabels = [regex]::Match($bloque, '(?m)^-\s*\*\*Labels:\*\*\s*(.+)$')
    $labels = @()
    if ($lineaLabels.Success) {
        $labels = [regex]::Matches($lineaLabels.Groups[1].Value, '`([^`]+)`') |
            ForEach-Object { $_.Groups[1].Value }
    }

    $cuerpo = [regex]::Replace($bloque, '(?m)^-\s*\*\*GitHub:\*\*.*\r?\n', '')
    $cuerpo = ($cuerpo -replace '(?s)\r?\n---\s*$', '').Trim()

    if ($mapaRecategorizar.ContainsKey($id)) {
        $origen = $esperados["$($mapaRecategorizar[$id])"][0]
        $cuerpo = "> Migrado desde ``$origen`` en la reorientacion a Entrega 3 (2026-10-23). Contenido original de Entrega 2 conservado en ``docs/entregas/entrega-2-personalizacion/github-issues.md``.`n`n$cuerpo"
    }

    if (-not $DryRun) {
        foreach ($l in $labels) {
            if (-not $labelsRepo.ContainsKey($l)) {
                gh label create $l *> $null
                $labelsRepo[$l] = $true
                Write-Host ("  [label creada] {0}" -f $l) -ForegroundColor DarkCyan
            }
        }
    }

    # Verificar si corresponde a un issue existente a recategorizar
    if ($mapaRecategorizar.ContainsKey($id)) {
        $issueNum = $mapaRecategorizar[$id]
        $numerosE3[$id] = $issueNum

        # Solo se quitan las labels obsoletas que el issue realmente tiene puestas.
        $quitar = @()
        if ($issuesActuales.ContainsKey("$issueNum")) {
            $quitar = @($issuesActuales["$issueNum"].labels |
                ForEach-Object { $_.name } |
                Where-Object { $labelsObsoletas -contains $_ })
        }

        if ($DryRun) {
            Write-Host ("[dry-run][recategorizar #{0} -> {1}] {2}" -f $issueNum, $id, $tituloCompleto) -ForegroundColor Yellow
            Write-Host ("          labels: +{0} | -{1} | milestone: {2}" -f ($labels -join ", "), $(if ($quitar.Count -gt 0) { $quitar -join "," } else { "(ninguna)" }), $Milestone)
            $actualizados++
            continue
        }

        $tmp = Join-Path $env:TEMP ("e3-issue-" + $id + ".md")
        $utf8 = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($tmp, $cuerpo, $utf8)

        $editArgs = @("issue", "edit", "$issueNum", "--title", $tituloCompleto, "--body-file", $tmp, "--milestone", $Milestone)
        if ($quitar.Count -gt 0) { $editArgs += @("--remove-label", ($quitar -join ",")) }
        foreach ($l in $labels) { $editArgs += @("--add-label", $l) }

        Write-Host ("[recategorizando #{0}] {1}" -f $issueNum, $tituloCompleto) -ForegroundColor Yellow
        gh @editArgs
        Remove-Item $tmp -Force -ErrorAction SilentlyContinue
        $actualizados++
        continue
    }

    # Caso issue nuevo de Entrega 3
    $yaExiste = $false
    $numeroExistente = $null
    foreach ($e in $existentes) {
        if ($e.title -eq $tituloCompleto -or $e.title -like "$id -*") {
            $yaExiste = $true
            $numeroExistente = $e.number
            break
        }
    }

    if ($yaExiste) {
        Write-Host ("[omitido] {0} (ya existe como #{1})" -f $tituloCompleto, $numeroExistente) -ForegroundColor DarkYellow
        $numerosE3[$id] = $numeroExistente
        $omitidos++
        continue
    }

    if ($DryRun) {
        Write-Host ("[dry-run][crear nuevo] {0}" -f $tituloCompleto) -ForegroundColor Cyan
        Write-Host ("          labels: {0} | milestone: {1}" -f ($labels -join ", "), $Milestone)
        $creados++
        continue
    }

    $tmp = Join-Path $env:TEMP ("e3-issue-" + $id + ".md")
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($tmp, $cuerpo, $utf8)

    $createArgs = @("issue", "create", "--title", $tituloCompleto, "--body-file", $tmp, "--milestone", $Milestone)
    foreach ($l in $labels) { $createArgs += @("--label", $l) }

    Write-Host ("[creando nuevo] {0}" -f $tituloCompleto) -ForegroundColor Green
    $urlCreada = gh @createArgs
    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
    $numero = [int](($urlCreada | Select-Object -Last 1) -replace '.*/', '')
    $numerosE3[$id] = $numero
    Write-Host ("          -> #{0} {1}" -f $numero, $urlCreada) -ForegroundColor Green
    $creados++
}

# --- 3. Cierre del milestone de Entrega 2 -----------------------------------
Write-Host ""
Write-Host "=== Paso 3: Cierre del milestone de Entrega 2 ===" -ForegroundColor Magenta
if ($NoCerrarMilestoneAnterior) {
    Write-Host "[omitido por -NoCerrarMilestoneAnterior] $MilestoneAnterior" -ForegroundColor DarkYellow
}
elseif ($DryRun) {
    Write-Host ("[dry-run][cerrar milestone] {0} (solo si queda sin issues abiertos)" -f $MilestoneAnterior) -ForegroundColor Cyan
}
elseif (-not $milestoneAnteriorNumero) {
    Write-Host ("[aviso] no existe el milestone '{0}'" -f $MilestoneAnterior) -ForegroundColor DarkYellow
}
else {
    $mActual = gh api "repos/:owner/:repo/milestones/$milestoneAnteriorNumero" | ConvertFrom-Json
    if ($mActual.state -eq "closed") {
        Write-Host ("[ya cerrado] {0}" -f $MilestoneAnterior) -ForegroundColor DarkYellow
    }
    elseif ($mActual.open_issues -gt 0) {
        Write-Host ("[aviso] {0} conserva {1} issue(s) abiertos; no se cierra. Revisa manualmente." -f $MilestoneAnterior, $mActual.open_issues) -ForegroundColor Red
    }
    else {
        gh api "repos/:owner/:repo/milestones/$milestoneAnteriorNumero" -X PATCH -f state=closed *> $null
        Write-Host ("[cerrado como Completado] {0} (12 issues cerrados, 5 migrados a Entrega 3)" -f $MilestoneAnterior) -ForegroundColor Green
    }
}

# --- 4. Reporte -------------------------------------------------------------
Write-Host ""
Write-Host ("Resumen E3: 3 cerrados por directriz docente, {0} recategorizados, {1} nuevos creados, {2} omitidos" -f $actualizados, $creados, $omitidos)

if ($numerosE3.Count -gt 0) {
    $destino = Join-Path $PSScriptRoot "numeros-github-e3.txt"
    $lineas = $numerosE3.Keys | ForEach-Object { "{0} = #{1}" -f $_, $numerosE3[$_] }
    if (-not $DryRun) {
        $lineas | Set-Content -Path $destino -Encoding UTF8
        Write-Host ("Mapeo guardado en {0}" -f $destino) -ForegroundColor Cyan
    }
    $lineas | ForEach-Object { Write-Host ("  {0}" -f $_) }
}
