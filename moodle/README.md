# Moodle local minimo

Alcance: habilitador de Entrega 2 (issue E2-02). No es el nucleo del proyecto.

## Objetivo minimo

- Levantar Moodle local con Docker.
- Instalar bloques IS-UTB de Estilos de Aprendizaje, Personalidad y CHASIDE con apoyo del docente.
- Diligenciar tests entre integrantes para generar datos de referencia.

## Requisitos previos

- Docker Desktop instalado y **en ejecucion** (icono de la ballena activo).
- Puertos libres: `8080` (Moodle). Verificar con `netstat -ano | findstr :8080`.

## Imagenes y version

- `mariadb:10.11` - base de datos (imagen oficial).
- `bitnamilegacy/moodle:5.0.2` - Moodle 5.0.2 con instalacion automatica.

> **Hallazgo (2026-10-18):** el tag original `moodlehq/moodle:latest` **no existe** en
> Docker Hub. Se reemplazo por la imagen autoinstalable de Bitnami publicada en el
> registro legacy (`bitnamilegacy/`). Ver `docker-compose.yml` para el detalle.

## Arranque

Desde la carpeta `moodle/`:

```bash
cd moodle
docker compose up -d
```

La **primera vez** descarga ~350 MB y ejecuta el instalador de Moodle (tarda ~2 minutos).
Cuando el log muestra `** Moodle setup finished! **` y `** Starting Apache **`, el sitio esta listo.

## Estado y logs

```bash
docker compose ps                 # estado de los contenedores
docker compose logs -f moodle     # seguir la inicializacion (Ctrl+C para salir)
```

Estado esperado:

- `moodle-db-1` -> `Up (healthy)`
- `moodle-moodle-1` -> `Up`, con `0.0.0.0:8080->8080/tcp`

## Acceso web y credenciales

- URL: **http://localhost:8080**
- Administrador del sitio:
  - Usuario: `admin`
  - Contrasena: `moodle123`
  - Correo: `admin@utb.local`
- Base de datos (uso interno entre contenedores):
  - Host: `db` (puerto `3306`), base `moodle`, usuario `moodle`, contrasena `moodle`
  - Root de la base: usuario `root`, contrasena `root`

> Credenciales de desarrollo local. No reutilizar en entornos reales.

## Detener y limpiar

```bash
docker compose stop       # detiene sin borrar nada
docker compose down       # elimina contenedores y red (CONSERVA los volumenes)
docker compose down -v    # elimina tambien la base de datos y los datos de Moodle
```

Reiniciar sin reinstalar:

```bash
docker compose start
```

## Verificacion rapida

```bash
docker compose ps                       # ambos contenedores Up / healthy
curl -I http://localhost:8080           # espera HTTP/1.1 200 (o 303)
```

## Solucion de problemas

| Sintoma | Causa probable | Solucion |
| :--- | :--- | :--- |
| `pull access denied for moodlehq/moodle` | tag inexistente | usar el `docker-compose.yml` de este repo (imagen `bitnamilegacy/moodle:5.0.2`) |
| `bind: address already in use` / puerto ocupado | otro proceso usa 8080 | cambiar a `"8081:8080"` y entrar a `http://localhost:8081` |
| `Cannot connect to the Docker daemon` | Docker Desktop apagado | abrir Docker Desktop y esperar "Engine running" |
| Descarga larga al primer arranque | ~350 MB de imagenes | esperar; no es un cuelgue |
| Web no responde durante ~2 min | instalador en curso | esperar `Moodle setup finished!` en los logs |
| Base de datos inconsistente | volumen danado | `docker compose down -v` y `docker compose up -d` (borra datos) |
| Cambio de version de la imagen | incompatibilidad de datos | respaldar el sitio o usar `down -v` antes de cambiar de tag |

## Contingencia

Si Moodle presenta demoras o errores de red, registrar el incidente en
`experimentos/bitacora.md` y continuar el trabajo con los fixtures JSON simulados
de `perfiles/`. La investigacion de IA no se detiene por Moodle.

## Limites de alcance

- No crear plugins desde cero.
- No hacer integracion avanzada con Savio institucional en esta fase.
- Si Moodle bloquea el avance, continuar con fixtures JSON simulados y documentar el bloqueo.

## Guia paso a paso

Para el detalle de cada paso (pensado para principiantes) ver
`docs/entregas/entrega-2-personalizacion/guia-paso-a-paso-docker-moodle.md`
y su version `.docx`.
