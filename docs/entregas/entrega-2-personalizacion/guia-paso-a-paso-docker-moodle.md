# Guia paso a paso: Docker + Moodle local (E2-02)

Esta guia es para cualquier integrante del equipo, incluso si nunca uso Docker.
Al terminarla tendras Moodle corriendo en tu computador en `http://localhost:8080`.

Tiempo estimado: 10 a 15 minutos (la mayor parte es la descarga de imagenes).

## Que vas a lograr

- Un sitio Moodle propio, local, para alojar los cursos y los bloques de tests de la UTB.
- La base de datos MariaDB asociada, tambien en Docker.
- Todo dentro de tu equipo: no depende de internet despues de la primera descarga.

## Antes de empezar

- Windows con **Docker Desktop** instalado.
- Conexion a internet solo para la primera descarga (~350 MB).
- El proyecto descargado, con la carpeta `moodle/` dentro.

## Paso 1: Verificar que Docker Desktop esta corriendo

Abre Docker Desktop y espera a que el icono de la ballena diga **"Engine running"**.

Para confirmarlo, abre una terminal (PowerShell) y escribe:

```bash
docker version
```

Si ves informacion del cliente y del servidor, todo bien. Si aparece
`Cannot connect to the Docker daemon`, Docker Desktop aun no esta listo: espera y reintenta.

## Paso 2: Abrir la terminal en la carpeta del proyecto

```bash
cd moodle
```

Estar dentro de `moodle/` es importante: ahi vive el archivo `docker-compose.yml`.

## Paso 3: Levantar Moodle y la base de datos

```bash
docker compose up -d
```

- `up` crea y arranca los contenedores.
- `-d` los deja en segundo plano (no bloquea la terminal).

La primera vez Docker descarga dos imagenes, `mariadb:10.11` y `bitnamilegacy/moodle:5.0.2`,
y luego instala Moodle solo. Esto tarda alrededor de 2 minutos.

## Paso 4: Confirmar que los contenedores estan arriba

```bash
docker compose ps
```

Debes ver:

- `moodle-db-1` en estado `Up (healthy)`.
- `moodle-moodle-1` en estado `Up`, con `0.0.0.0:8080->8080/tcp`.

## Paso 5: Seguir la instalacion (opcional)

```bash
docker compose logs -f moodle
```

Espera el mensaje `** Moodle setup finished! **`. Sal del seguimiento con `Ctrl+C`.

## Paso 6: Abrir Moodle en el navegador

Entra a:

```text
http://localhost:8080
```

Deberias ver la pagina principal con el titulo "Moodle UTB local".

## Paso 7: Iniciar sesion como administrador

- Usuario: `admin`
- Contrasena: `moodle123`

Estas credenciales son solo para desarrollo local. No las reutilices en entornos reales.

## Como detener y volver a arrancar

```bash
docker compose stop       # detiene sin borrar datos
docker compose start      # vuelve a arrancar sin reinstalar
docker compose down       # elimina contenedores y red, conserva los datos
docker compose down -v    # borra TODO, incluida la base de datos
```

## Problemas comunes

| Sintoma | Causa probable | Solucion |
| :--- | :--- | :--- |
| `Cannot connect to the Docker daemon` | Docker Desktop apagado | abrirlo y esperar "Engine running" |
| `bind: address already in use` | el puerto 8080 esta ocupado | usar `"8081:8080"` en el compose y entrar a `http://localhost:8081` |
| La web no responde al inicio | instalador en curso (~2 min) | esperar `Moodle setup finished!` en los logs |
| La descarga se ve detenida | ~350 MB de imagenes | esperar; no es un error |
| `pull access denied for moodlehq/moodle` | tag inexistente (hallazgo E2-02) | usar el compose de este repo |

## Si algo falla y no se resuelve

Registra el incidente en `experimentos/bitacora.md` y continua con los fixtures JSON
simulados de `perfiles/`. La investigacion de IA no depende de Moodle.

## Siguiente paso

Con Moodle operativo, sigue el issue **E2-03**: instalar los bloques IS-UTB de
Estilos de Aprendizaje, Personalidad y CHASIDE, y diligenciar los tests con el equipo.

## Notas tecnicas

- Imagen de Moodle: `bitnamilegacy/moodle:5.0.2` (Moodle 5.0.2 con instalacion automatica).
  El tag `moodlehq/moodle:latest` del enunciado original no existe en Docker Hub.
- Base de datos: `mariadb:10.11`.
- Datos persistidos en volumenes Docker: `moodle_db_data`, `moodle_moodle_data`, `moodle_moodledata_data`.
- Credenciales de la base (interno): host `db`, base `moodle`, usuario `moodle`, contrasena `moodle`.
