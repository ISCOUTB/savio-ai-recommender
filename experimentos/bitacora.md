# Bitacora de experimentos - Entrega 2

| Fecha | Autor | Objetivo | Resultado | Decision |
|---|---|---|---|---|
| Pendiente | equipo | Inicializar Entrega 2 | Pendiente | Seguir ROADMAP |
| 2026-10-18 | persona-1 | Levantar Moodle local en Docker (E2-02) | OK: `moodle-db-1` healthy + `moodle-moodle-1` Up, web en http://localhost:8080, login `admin` validado | Imagen `moodlehq/moodle` no existe en Docker Hub; se adopta `bitnamilegacy/moodle:5.0.2` |
| 2026-10-18 | persona-1 | Instalar bloques IS-UTB y dejar el curso listo (E2-03) | OK: `learning_style` v2.0.4, `personality_test` v2.0.5 y `chaside` v2.0.4 instalados; tablas creadas; curso `E2-03-psico` (id 2) con los tres bloques y sus tests cargando HTTP 200; sobrevive a `docker compose restart` | Los bloques son publicos en la organizacion `ISCOUTB`, asi que no hay que esperar entrega del docente. Reproducible con `moodle/instalar-bloques.ps1` |
| 2026-10-18 | persona-1 | Diagnosticar fallo "permisos no validos al tratar de crear un directorio" (E2-03) | Causa: los scripts CLI de Moodle corriendo como `root` dejaron 167 archivos root-owned en `moodledata`; la web corre como usuario `daemon` | Los scripts CLI de Moodle se ejecutan con `docker exec -u daemon`; si ya paso, corregir con `chown -R daemon:daemon /bitnami/moodledata` |
| 2026-10-18 | persona-1 | Preparar las cuentas del equipo para diligenciar los tests (E2-03) | OK: `persona-1`, `persona-2` y `persona-3` creados y matriculados como estudiantes; cada uno entra, ve los tres bloques y abre su test sin error de permisos | El rol `student` ya trae las capacidades `take_test`; cada integrante diligencia con su propia cuenta |
