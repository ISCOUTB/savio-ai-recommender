<?php
// Prepara el Moodle local para diligenciar los tests psicopedagogicos (Entrega 2).
// Crea el curso piloto, un usuario estudiante por integrante, los matricula
// y agrega el bloque de Estilos de aprendizaje al curso. Se puede ejecutar varias veces.
//
// Uso (desde moodle/, con el compose levantado):
//   docker compose cp preparar_curso.php moodle:/tmp/preparar_curso.php
//   MSYS_NO_PATHCONV=1 docker compose exec -T moodle php /tmp/preparar_curso.php

define('CLI_SCRIPT', true);
require('/var/www/html/config.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->dirroot . '/user/lib.php');
require_once($CFG->libdir . '/enrollib.php');

\core\session\manager::set_user(get_admin());

const CURSO = 'TDE-PILOTO';
const CLAVE = 'Estudiante123!';
// estudiante_id seudonimizado en el campo "Numero de ID" (idnumber), igual que el perfil JSON.
$integrantes = [
    ['username' => 'jvelazquez', 'firstname' => 'Jesus', 'lastname' => 'Velazquez', 'idnumber' => 'est-001'],
    ['username' => 'spaternina', 'firstname' => 'Sebastian', 'lastname' => 'Paternina', 'idnumber' => 'est-002'],
    ['username' => 'ycaraballo', 'firstname' => 'Yosser', 'lastname' => 'Caraballo', 'idnumber' => 'est-003'],
];

// 1. Curso piloto
$curso = $DB->get_record('course', ['shortname' => CURSO]);
if (!$curso) {
    $curso = create_course((object) [
        'fullname' => 'Taller de Escritura (piloto)',
        'shortname' => CURSO,
        'category' => $DB->get_field_sql('SELECT MIN(id) FROM {course_categories}'),
        'summary' => 'Curso de pruebas para diligenciar los tests psicopedagogicos del recomendador.',
        'format' => 'topics',
    ]);
    echo "Curso creado: {$curso->fullname} (id {$curso->id})\n";
} else {
    echo "Curso ya existe: {$curso->fullname} (id {$curso->id})\n";
}

// 2. Usuarios y matricula como estudiantes
$manual = enrol_get_plugin('manual');
$instancia = $DB->get_record('enrol', ['courseid' => $curso->id, 'enrol' => 'manual']);
if (!$instancia) {
    $manual->add_default_instance($curso);
    $instancia = $DB->get_record('enrol', ['courseid' => $curso->id, 'enrol' => 'manual'], '*', MUST_EXIST);
}
$rolestudiante = $DB->get_field('role', 'id', ['shortname' => 'student'], MUST_EXIST);

foreach ($integrantes as $i) {
    $usuario = $DB->get_record('user', ['username' => $i['username'], 'deleted' => 0]);
    if (!$usuario) {
        $id = user_create_user((object) ($i + [
            'auth' => 'manual',
            'confirmed' => 1,
            'mnethostid' => $CFG->mnet_localhost_id,
            'password' => CLAVE,
            'email' => $i['username'] . '@example.com',
            'lang' => 'es',
        ]));
        $usuario = $DB->get_record('user', ['id' => $id]);
        echo "Usuario creado: {$usuario->username} ({$i['idnumber']})\n";
    } else {
        echo "Usuario ya existe: {$usuario->username}\n";
    }
    $manual->enrol_user($instancia, $usuario->id, $rolestudiante);
}

// 3. Bloques de los tests en la pagina del curso (solo los que esten instalados)
$contexto = context_course::instance($curso->id);
$bloques = [
    'learning_style' => 'Estilos de aprendizaje',
    'personality_test' => 'Personalidad',
    'chaside' => 'CHASIDE',
];
foreach ($bloques as $bloque => $nombre) {
    if (!$DB->record_exists('block', ['name' => $bloque])) {
        echo "Bloque {$nombre} no instalado: se omite\n";
        continue;
    }
    if ($DB->record_exists('block_instances', ['blockname' => $bloque, 'parentcontextid' => $contexto->id])) {
        echo "Bloque {$nombre} ya esta en el curso\n";
        continue;
    }
    $pagina = new moodle_page();
    $pagina->set_course($curso);
    $pagina->set_pagelayout('course');
    $pagina->set_pagetype('course-view-' . $curso->format);
    $pagina->blocks->load_blocks();
    $pagina->blocks->add_block_at_end_of_default_region($bloque);
    echo "Bloque {$nombre} agregado al curso\n";
}

echo "\nListo: {$CFG->wwwroot}/course/view.php?id={$curso->id}\n";
echo "Clave de los estudiantes: " . CLAVE . "\n";
