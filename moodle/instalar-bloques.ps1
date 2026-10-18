# Instala los bloques IS-UTB de psicopedagogia en el Moodle local de Docker
# (Estilos de Aprendizaje, Personalidad y CHASIDE). Issue E2-03.
#
# Ademas deja armado el curso "Pruebas psicopedagogicas E2-03" con los tres
# bloques y los usuarios del equipo (persona-1, persona-2, persona-3) ya
# matriculados como estudiantes.
#
# Uso (desde la raiz del repo):
#   powershell -ExecutionPolicy Bypass -File moodle\instalar-bloques.ps1
#
# Requisitos:
#   - Docker Desktop corriendo y la pila de moodle/ levantada (issue E2-02).
#   - Conexion a internet (descarga las releases publicas de la organizacion ISCOUTB).
#
# El script es idempotente: volver a ejecutarlo reinstala la misma version y no
# duplica los bloques en el curso.

$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$contenedor = "moodle-moodle-1"
$php        = "/opt/bitnami/php/bin/php"
$moodle     = "/bitnami/moodle"
$tmp        = Join-Path $env:TEMP "isutb-bloques"

# Release publica de cada bloque (organizacion ISCOUTB en GitHub).
$bloques = @(
    @{ nombre = "learning_style";   version = "v2.0.4" },
    @{ nombre = "personality_test"; version = "v2.0.5" },
    @{ nombre = "chaside";          version = "v2.0.4" }
)

# Ejecuta un comando de docker capturando stderr sin que PowerShell lo trate
# como error terminante, y falla si el codigo de salida no es cero.
function Invoke-Docker {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Comando)
    $previo = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    try {
        $salida = (& docker @Comando 2>&1 | Out-String)
        $codigo = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previo
    }
    if ($salida.Trim()) { Write-Host $salida.TrimEnd() }
    if ($codigo -ne 0) {
        throw ("Fallo: docker " + ($Comando -join " ") + " (codigo " + $codigo + ")")
    }
}

$estado = (& docker inspect -f "{{.State.Running}}" $contenedor 2>$null)
if ($estado -ne "true") {
    throw "El contenedor $contenedor no esta corriendo. Levanta la pila con: docker compose -f moodle/docker-compose.yml up -d"
}

New-Item -ItemType Directory -Force -Path $tmp | Out-Null

# 1. Descargar y copiar cada bloque dentro del contenedor.
foreach ($b in $bloques) {
    $zip = "$($b.nombre)-$($b.version).zip"
    $url = "https://github.com/ISCOUTB/$($b.nombre)/releases/download/$($b.version)/$zip"
    Write-Host "Descargando $zip ..."
    Invoke-WebRequest -Uri $url -OutFile (Join-Path $tmp $zip) -UseBasicParsing

    $destino = Join-Path $tmp $b.nombre
    if (Test-Path $destino) { Remove-Item -Recurse -Force $destino }
    Expand-Archive -Path (Join-Path $tmp $zip) -DestinationPath $destino -Force

    Invoke-Docker cp "$destino\$($b.nombre)" "${contenedor}:$moodle/blocks/$($b.nombre)"
    Write-Host "  copiado a $moodle/blocks/$($b.nombre)"
}

# 2. Registrar los plugins en Moodle (crea las tablas). Se ejecuta como el
#    usuario daemon, igual que Apache, para no romper permisos en moodledata.
Write-Host "Ejecutando la actualizacion de Moodle ..."
Invoke-Docker exec -u daemon $contenedor $php "$moodle/admin/cli/upgrade.php" --non-interactive

# 3. Refrescar caches.
Invoke-Docker exec -u daemon $contenedor $php "$moodle/admin/cli/purge_caches.php"

# 4. Crear el curso habilitador y agregar los tres bloques (solo si faltan).
$phpCurso = Join-Path $tmp "crear_curso_e203.php"
@'
<?php
define('CLI_SCRIPT', true);
require('/bitnami/moodle/config.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->libdir . '/clilib.php');

$shortname = 'E2-03-psico';
$course = $DB->get_record('course', ['shortname' => $shortname]);
if (!$course) {
    $d = new stdClass();
    $d->fullname = 'Pruebas psicopedagogicas E2-03';
    $d->shortname = $shortname;
    $d->category = 1;
    $d->format = 'topics';
    $d->visible = 1;
    $d->summary = 'Curso habilitador para diligenciar los tests IS-UTB: Estilos de Aprendizaje, Personalidad y CHASIDE.';
    $d->summaryformat = FORMAT_HTML;
    $course = create_course($d);
    echo "Curso creado: id=" . $course->id . "\n";
} else {
    echo "Curso ya existia: id=" . $course->id . "\n";
}

$context = context_course::instance($course->id);
$nombres = ['learning_style', 'personality_test', 'chaside'];
$faltan = [];
foreach ($nombres as $bn) {
    if (!$DB->record_exists('block_instances', ['blockname' => $bn, 'parentcontextid' => $context->id])) {
        $faltan[] = $bn;
    }
}

if ($faltan) {
    $page = new moodle_page();
    $page->set_context($context);
    $page->set_course($course);
    $page->set_pagetype('course-view-' . $course->format);
    $page->set_pagelayout('course');
    $page->set_url(new moodle_url('/course/view.php', ['id' => $course->id]));
    // OJO: el segundo argumento es el patron de pagetype; NO pasar '*' como
    // subpage, porque el subpage real de la pagina es vacio y el bloque no cargaria.
    $page->blocks->add_blocks(['side-pre' => $faltan], 'course-view-*');
    echo "Bloques agregados: " . implode(', ', $faltan) . "\n";
} else {
    echo "Los tres bloques ya estaban en el curso.\n";
}
echo "Curso URL: /course/view.php?id=" . $course->id . "\n";
'@ | Set-Content -Path $phpCurso -Encoding ascii

Invoke-Docker cp $phpCurso "${contenedor}:/tmp/crear_curso_e203.php"
Invoke-Docker exec -u daemon $contenedor $php /tmp/crear_curso_e203.php
Invoke-Docker exec $contenedor rm -f /tmp/crear_curso_e203.php

# 5. Crear los usuarios del equipo y matricularlos como estudiantes.
$phpUsuarios = Join-Path $tmp "crear_usuarios_e203.php"
@'
<?php
define('CLI_SCRIPT', true);
require('/bitnami/moodle/config.php');
require_once($CFG->dirroot . '/user/lib.php');
require_once($CFG->libdir . '/enrollib.php');
require_once($CFG->libdir . '/clilib.php');

$course = $DB->get_record('course', ['shortname' => 'E2-03-psico'], '*', MUST_EXIST);
$studentrole = $DB->get_field('role', 'id', ['shortname' => 'student'], MUST_EXIST);
$context = context_course::instance($course->id);

$plugin = enrol_get_plugin('manual');
$manual = null;
foreach (enrol_get_instances($course->id, true) as $i) {
    if ($i->enrol === 'manual') { $manual = $i; break; }
}
if (!$manual) {
    $manualid = $plugin->add_default_instance($course);
    $manual = $DB->get_record('enrol', ['id' => $manualid], '*', MUST_EXIST);
    echo "Instancia de matriculacion manual creada (id $manualid)\n";
}

// usuario, nombre, contrasena
$personas = [
    ['persona-1', 'Persona 1', 'Persona1!'],
    ['persona-2', 'Persona 2', 'Persona2!'],
    ['persona-3', 'Persona 3', 'Persona3!'],
];

foreach ($personas as [$username, $nombre, $password]) {
    $user = $DB->get_record('user', ['username' => $username, 'deleted' => 0]);
    if (!$user) {
        $u = new stdClass();
        $u->auth = 'manual';
        $u->confirmed = 1;
        $u->mnethostid = $CFG->mnet_localhost_id;
        $u->username = $username;
        $u->password = $password;
        $u->firstname = $nombre;
        $u->lastname = 'UTB';
        $u->email = $username . '@utb.local';
        $u->lang = 'es';
        $u->timezone = '99';
        $u->city = 'Cartagena';
        $u->country = 'CO';
        $u->policyagreed = 1;
        $u->auth_forcepasswordchange = 0;
        $uid = user_create_user($u, true, false);
        $user = $DB->get_record('user', ['id' => $uid], '*', MUST_EXIST);
        echo "Usuario creado: $username (id $uid)\n";
    } else {
        echo "Usuario ya existia: $username (id {$user->id})\n";
    }

    if (!is_enrolled($context, $user, '', true)) {
        $plugin->enrol_user($manual, $user->id, $studentrole);
        echo "  matriculado como estudiante\n";
    } else {
        echo "  ya estaba matriculado\n";
    }
}
'@ | Set-Content -Path $phpUsuarios -Encoding ascii

Invoke-Docker cp $phpUsuarios "${contenedor}:/tmp/crear_usuarios_e203.php"
Invoke-Docker exec -u daemon $contenedor $php /tmp/crear_usuarios_e203.php
Invoke-Docker exec $contenedor rm -f /tmp/crear_usuarios_e203.php

Write-Host ""
Write-Host "Version registrada de cada bloque:"
$consulta = @('exec', 'moodle-db-1', 'mysql', '-umoodle', '-pmoodle', 'moodle',
    '-e', "SELECT plugin, value AS version FROM mdl_config_plugins WHERE plugin IN ('block_learning_style','block_personality_test','block_chaside') AND name='version';")
Invoke-Docker @consulta

Write-Host ""
Write-Host "Cuentas del equipo (estudiantes del curso):"
Write-Host "  persona-1 / Persona1!"
Write-Host "  persona-2 / Persona2!"
Write-Host "  persona-3 / Persona3!"
Write-Host ""
Write-Host "Listo. Curso: http://localhost:8080/course/view.php?id=2"
Write-Host "Admin del sitio: admin / moodle123"
