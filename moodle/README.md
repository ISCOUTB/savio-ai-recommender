# Moodle local minimo

Alcance: habilitador de Entrega 2. No es el nucleo del proyecto.

## Objetivo minimo

- Levantar Moodle local con Docker.
- Instalar bloques IS-UTB de Estilos de Aprendizaje, Personalidad y CHASIDE con apoyo del docente.
- Diligenciar tests entre integrantes para generar datos de referencia.

## Requisitos

- Docker Desktop instalado y abierto (Windows: con WSL 2).
- Puerto `8080` libre.

## Arranque base

```bash
cd moodle
docker compose up -d
```

La primera vez descarga las imagenes y **Moodle se instala solo**: tarda unos minutos. Ver el avance con:

```bash
docker compose logs -f moodle
```

Cuando termine, abrir **http://localhost:8080**.

| Dato | Valor |
|---|---|
| Usuario admin | `admin` |
| Contrasena | `Admin123!` |
| Base de datos | MariaDB 11.4, servicio `db`, usuario/clave `moodle`/`moodle`, prefijo `mdl_` |

Imagen de Moodle: `erseco/alpine-moodle` (Moodle 5.3 LTS, exige MariaDB >= 11.4). La anterior `moodlehq/moodle` no existe en Docker Hub.

Detener (conserva los datos):

```bash
docker compose down
```

Borrar todo y empezar de cero (elimina cursos, usuarios y base de datos):

```bash
docker compose down -v
```

## Tests psicopedagogicos

### 1. Instalar los bloques (una vez, o despues de `docker compose down -v`)

En Moodle 5.3 los bloques van en `public/blocks/`. Desde `moodle/`:

```bash
docker compose cp ../modulos/learning_style-main/learning_style-main/. moodle:/var/www/html/public/blocks/learning_style
docker compose cp ../modulos/chaside-main/chaside-main/. moodle:/var/www/html/public/blocks/chaside
docker compose cp ../modulos/personality_test-main/personality_test-main/. moodle:/var/www/html/public/blocks/personality_test
MSYS_NO_PATHCONV=1 docker compose exec -T -u root moodle chown -R nobody:nobody /var/www/html/public/blocks/learning_style /var/www/html/public/blocks/chaside /var/www/html/public/blocks/personality_test
MSYS_NO_PATHCONV=1 docker compose exec -T moodle php /var/www/html/admin/cli/upgrade.php --non-interactive
```

`MSYS_NO_PATHCONV=1` evita que Git Bash convierta las rutas del contenedor en rutas de Windows (en PowerShell no hace falta).

| Bloque | Estado |
|---|---|
| Estilos de aprendizaje (`block_learning_style`) | Instalado |
| Personalidad (`block_personality_test`) | Instalado (desde `modulos/personality_test-main/`) |
| CHASIDE (`block_chaside`) | Instalado (desde `modulos/chaside-main/`) |

### 2. Preparar el curso y los usuarios

```bash
docker compose cp preparar_curso.php moodle:/tmp/preparar_curso.php
MSYS_NO_PATHCONV=1 docker compose exec -T moodle php /tmp/preparar_curso.php
```

Crea el curso **Taller de Escritura (piloto)**, un estudiante por integrante y agrega los bloques instalados al curso. Se puede ejecutar varias veces sin duplicar nada.

| Usuario | Integrante | Numero de ID (`estudiante_id`) | Clave |
|---|---|---|---|
| `jvelazquez` | Jesus Velazquez | `est-001` | `Estudiante123!` |
| `spaternina` | Sebastian Paternina | `est-002` | `Estudiante123!` |
| `ycaraballo` | Yosser Caraballo | `est-003` | `Estudiante123!` |

### 3. Hacer el test

1. Abrir http://localhost:8080 y entrar con el usuario propio.
2. Ir al curso **Taller de Escritura (piloto)**.
3. En el bloque **Estilos de Aprendizaje**, iniciar el test (44 preguntas A/B, guarda el avance solo).
4. En el bloque **CHASIDE** (Orientacion Vocacional), iniciar el test (98 preguntas Si/No, 10 por pagina, guarda el avance solo).
5. En el bloque **Exploracion de Personalidad**, iniciar el test (72 preguntas Si/No en 8 paginas).
6. Al terminar, cada bloque muestra el resultado. El admin ve los resultados de todos desde los mismos bloques (vista docente y exportacion CSV; CHASIDE tambien JSON).

## Feedback de recomendaciones (E2-11)

El feedback del estudiante se recoge con la actividad **Feedback** nativa de Moodle, una por semana (`Feedback semana <n>`), no anonima, con preguntas de etiqueta `util`, `likert` y `comentario`. El "Numero de ID" de cada usuario debe ser su `estudiante_id` seudonimizado. Configuracion completa: [feedback-loop.md seccion 6.6](../docs/especificaciones/feedback-loop.md).

Con el compose levantado, desde la raiz del repo:

```bash
python poc_slm/feedback_tracker.py importar-moodle --semana 1
```

## Limites de alcance

- No crear plugins desde cero.
- No hacer integracion avanzada con Savio institucional en esta fase.
- Si Moodle bloquea el avance, continuar con fixtures JSON simulados y documentar bloqueo.
