# Bloques/plugins de Moodle para Entrega 2

Estado: **instalados y verificados** en el Moodle local (2026-10-18, issue E2-03).

Necesarios segun fuentes de Entrega 2:

- Estilos de Aprendizaje.
- Personalidad.
- CHASIDE / orientacion vocacional.

Regla: no implementar estos instrumentos desde cero. Se instalan desde IS-UTB o
repositorio oficial de Moodle y se diligencian con el equipo.

---

## Origen de los bloques

El docente indico que los instrumentos viven en la organizacion de GitHub
`ISCOUTB`. Confirmamos los repositorios y usamos sus **releases publicas**, asi
que no dependemos de una entrega manual de archivos.

| Instrumento | Repositorio | Version instalada | Componente |
| :--- | :--- | :--- | :--- |
| Estilos de Aprendizaje (Felder-Soloman) | `ISCOUTB/learning_style` | v2.0.4 | `block_learning_style` |
| Personalidad (MBTI) | `ISCOUTB/personality_test` | v2.0.5 | `block_personality_test` |
| CHASIDE (orientacion vocacional) | `ISCOUTB/chaside` | v2.0.4 | `block_chaside` |

Notas:

- Los tres declaran compatibilidad con Moodle 4.0+. El Moodle local es 5.0.2 y
  los tres funcionan.
- El encabezado de copyright de los tres bloques incluye al docente del proyecto.
- En la misma organizacion existe `ISCOUTB/selfdiscoverytracker`, que describe un
  circuito de 5 pruebas psicometricas. Ademas de estos tres hay `ISCOUTB/tmms_24`
  y `ISCOUTB/student_path`. No son necesarios para E2-03.
- El docente solo menciono "learning" y "personality"; CHASIDE se identifico
  buscando en la organizacion.

---

## Instalacion reproducible

El script `moodle/instalar-bloques.ps1` descarga las tres releases, las copia al
contenedor, registra los plugins y deja armado el curso. Es **idempotente**.

```powershell
powershell -ExecutionPolicy Bypass -File moodle\instalar-bloques.ps1
```

Equivalente manual (desde `moodle/`):

```bash
# 1. copiar cada bloque dentro del contenedor
docker cp personality_test moodle-moodle-1:/bitnami/moodle/blocks/personality_test

# 2. registrar los plugins (crea las tablas). Ejecutar como daemon, NO como root.
docker exec -u daemon moodle-moodle-1 /opt/bitnami/php/bin/php /bitnami/moodle/admin/cli/upgrade.php --non-interactive

# 3. refrescar caches
docker exec -u daemon moodle-moodle-1 /opt/bitnami/php/bin/php /bitnami/moodle/admin/cli/purge_caches.php
```

Via interfaz (alternativa): en Moodle, `Administracion del sitio -> Extensiones ->
Instalar plugins`, subir cada `.zip` y completar el asistente.

---

## Curso habilitador

- Nombre: `Pruebas psicopedagogicas E2-03`
- Shortname: `E2-03-psico`
- URL: `http://localhost:8080/course/view.php?id=2`
- Los tres bloques quedaron en la region `side-pre`.

---

## Cuentas del equipo

Cada integrante diligencia su test con su propia cuenta, ya matriculada como
estudiante en el curso:

| Usuario | Contrasena | Nombre para mostrar |
| :--- | :--- | :--- |
| `persona-1` | `Persona1!` | Persona 1 UTB |
| `persona-2` | `Persona2!` | Persona 2 UTB |
| `persona-3` | `Persona3!` | Persona 3 UTB |

> Credenciales de desarrollo local. No reutilizar en entornos reales.

El rol `student` ya trae las tres capacidades de diligenciamiento
(`take_test` / `taketest`), asi que las cuentas pueden responder los tests sin
configuracion adicional.

---

## Como entrar a los tests (interfaz)

El tema **Boost** (el de Moodle 5) no muestra los bloques en una columna de la
pagina: los guarda en un **panel lateral que se abre desde la derecha** y que
arranca **cerrado**. Por eso, al entrar al curso, no se ven de inmediato.

1. Abrir `http://localhost:8080/course/view.php?id=2`.
2. En la esquina superior derecha del area del curso, junto al icono de lista
   ("Abrir indice del curso"), hay un icono de panel cuyo texto es
   **"Abrir cajon de bloques"**. Pasar el mouse encima para verlo.
3. Al hacer clic, se desliza el panel con los tres bloques. Cada uno trae su
   boton para empezar (por ejemplo, CHASIDE dice "Iniciar Exploracion"). Moodle
   recuerda si el panel quedo abierto.

Atajo verificado: cada test tiene URL directa y responde con las cuentas de
estudiante (HTTP 200, sin error de permisos).

| Test | Enlace directo |
| :--- | :--- |
| Estilos de Aprendizaje | `http://localhost:8080/blocks/learning_style/view.php?cid=2` |
| Personalidad | `http://localhost:8080/blocks/personality_test/view.php?cid=2` |
| CHASIDE | `http://localhost:8080/blocks/chaside/view.php?courseid=2` |

> Si cambia el identificador del curso, hay que actualizar estos enlaces.

---

## Detalle tecnico (verificado)

- Tablas creadas: `mdl_learning_style`, `mdl_personality_test`,
  `mdl_block_chaside_responses`.
- Version registrada en `mdl_config_plugins`: `2026072800` para los tres.
- Los bloques sobreviven a `docker compose restart`: viven en el volumen
  `moodle_data`.
- Capacidades para diligenciar: `block/learning_style:take_test`,
  `block/personality_test:taketest`, `block/chaside:take_test`.
- Exportacion de resultados: CHASIDE (CSV y JSON), Estilos (CSV), Personalidad
  (CSV y PDF).
- **Los scripts CLI de Moodle deben correr como usuario `daemon`**
  (`docker exec -u daemon ...`). Si corren como `root`, dejan archivos root-owned
  en `moodledata` y la web falla con "permisos no validos al tratar de crear un
  directorio". Correccion:
  `docker exec moodle-moodle-1 chown -R daemon:daemon /bitnami/moodledata`.
- **Al asociar los bloques a la pagina**, `mdl_block_instances.subpagepattern` debe
  quedar en `NULL` (no en `*`). Si queda en `*`, Moodle lo compara contra el
  subpage real de la pagina (vacio) y el bloque no se carga.

---

## Checklist

- [x] Moodle local accesible.
- [x] Plugin/bloque de Estilos instalado.
- [x] Plugin/bloque de Personalidad instalado.
- [x] Plugin/bloque CHASIDE instalado.
- [ ] Tres integrantes diligencian tests.
- [ ] Resultados exportados o transcritos a fixtures JSON.

---

## Pendiente (decision de equipo)

- **Plan B (fixtures simulados):** el equipo decidio **no generarlos por ahora**.
  Primero se diligencian los tests reales con las tres cuentas; si algo bloquea el
  diligenciamiento, se retoma la generacion de fixtures.
- El campo `"origen": "simulado"` que pide el issue E2-03 ya esta resuelto:
  se agrego `origen` obligatorio (`real` / `simulado`) a nivel de perfil en
  `perfil-estudiante.schema.json`.
- `estilos_aprendizaje.dominante` (VARK) **resuelto (2026-10-19):** se elimino
  `dominante` y se agrego `preferencias` (8 polos, max 4) con Felder-Soloman
  como modelo canonico. Ver `docs/especificaciones/instrumento-estilos-aprendizaje.md`.
- `personalidad` guarda `rasgos` numericos libres; falta definir donde se anota
  el tipo MBTI de 4 letras (por ejemplo `ENTJ`).
- Confirmar con el docente si se usan estos bloques en Savio institucional o en
  el Moodle local, y si existe una version distinta a la publica.
