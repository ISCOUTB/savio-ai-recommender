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

## Limites de alcance

- No crear plugins desde cero.
- No hacer integracion avanzada con Savio institucional en esta fase.
- Si Moodle bloquea el avance, continuar con fixtures JSON simulados y documentar bloqueo.
