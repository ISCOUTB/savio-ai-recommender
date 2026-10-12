# Issues listos para Entrega 2

`gh` no esta instalado en esta maquina, asi que aqui quedan listos para crear manual o con script cuando exista GitHub CLI.

Milestone sugerido: `Entrega 2 - Personalizacion`.

Labels sugeridas: `entrega-2`, `docs`, `repo`, `moodle`, `psicopedagogia`, `slm`, `destilacion`, `feedback`, `persona-1`, `persona-2`, `persona-3`, `equipo`, `docente`.

---

## E2-01 - Estructurar Entrega 2 en GitHub y ROADMAP

- Labels: `entrega-2`, `repo`, `docs`, `equipo`
- Prioridad: P0
- Dueno: equipo
- Depende de: ninguno

Objetivo: dejar creada la organizacion base de Entrega 2.

Criterios:
- [ ] Estructura `docs/entregas/entrega-2-personalizacion/` creada.
- [ ] `ROADMAP.md` actualizado.
- [ ] Tablero Kanban visible con Backlog, En progreso, En revision y Listo.

---

## E2-02 - Moodle local en Docker operativo

- Labels: `entrega-2`, `moodle`, `equipo`, `docente`
- Prioridad: P1
- Dueno: equipo + docente
- Depende de: E2-01

Objetivo: levantar Moodle local como habilitador minimo.

Criterios:
- [ ] `docker compose up -d` funciona.
- [ ] Acceso local documentado.
- [ ] Si falla, queda bloqueo escrito y se usa fixture JSON simulado.

Nota de foco: no crear modulos nuevos ni integracion avanzada.

---

## E2-03 - Instalar bloques IS-UTB y diligenciar tests

- Labels: `entrega-2`, `moodle`, `psicopedagogia`, `docente`
- Prioridad: P1
- Dueno: equipo + docente
- Depende de: E2-02

Objetivo: activar Estilos de Aprendizaje, Personalidad y CHASIDE.

Criterios:
- [ ] Bloques instalados o bloqueo documentado.
- [ ] Cada integrante tiene un test diligenciado o fixture simulado marcado como simulado.

Nota de foco: el aprendizaje fuerte del equipo no esta en administrar Moodle.

---

## E2-04 - Modelar Test de Estilos de Aprendizaje

- Labels: `entrega-2`, `psicopedagogia`, `persona-1`
- Prioridad: P0
- Dueno sugerido: persona-1
- Depende de: E2-01

Objetivo: explicar que metricas entrega el bloque y como traducirlas a prompt.

Criterios:
- [ ] Modelo usado documentado: VAK, Felder-Silverman, Kolb u otro.
- [ ] Campos propuestos para `perfil.estilos_aprendizaje`.
- [ ] Ejemplo de descripcion textual para prompt.

---

## E2-05 - Modelar Test de Personalidad

- Labels: `entrega-2`, `psicopedagogia`, `persona-2`
- Prioridad: P0
- Dueno sugerido: persona-2
- Depende de: E2-01

Objetivo: convertir rasgos conductuales a campos utiles para recomendacion.

Criterios:
- [ ] Rasgos del bloque documentados.
- [ ] Relacion con consumo de recursos explicada.
- [ ] Campos propuestos para `perfil.personalidad`.

---

## E2-06 - Modelar Test CHASIDE

- Labels: `entrega-2`, `psicopedagogia`, `persona-3`
- Prioridad: P0
- Dueno sugerido: persona-3
- Depende de: E2-01

Objetivo: mapear areas CHASIDE para analogias dentro de la materia.

Criterios:
- [ ] Areas C, H, A, S, I, D, E documentadas.
- [ ] Reglas de uso pedagogico descritas.
- [ ] Campos propuestos para `perfil.chaside`.

---

## E2-07 - Consolidar schema JSON del perfil

- Labels: `entrega-2`, `psicopedagogia`, `docs`, `equipo`
- Prioridad: P0
- Dueno: equipo
- Depende de: E2-04, E2-05, E2-06

Objetivo: unificar el perfil en un solo JSON validado.

Criterios:
- [ ] `docs/especificaciones/perfil-estudiante.schema.json` valido.
- [ ] `perfiles/ejemplo-perfil-estudiante.json` validado.
- [ ] El schema queda simple para prompt.

---

## E2-08 - Seleccionar materia piloto y recursos A/B/C

- Labels: `entrega-2`, `docs`, `slm`, `equipo`
- Prioridad: P0
- Dueno: equipo
- Depende de: E2-01

Objetivo: definir el curso piloto y recursos semanales contrastantes.

Criterios:
- [ ] Materia piloto definida; recomendada Taller de Escritura.
- [ ] Tabla de semana 1/2 con recursos A/B/C.
- [ ] `recurso-semanal.schema.json` validado con ejemplos.

---

## E2-09 - Pipeline de destilacion y fine-tuning

- Labels: `entrega-2`, `slm`, `destilacion`, `equipo`
- Prioridad: P0
- Dueno: equipo, lider tecnico por definir
- Depende de: E2-01, E2-08

Objetivo: proponer como llevar un modelo ~1.5B/2B a un SLM objetivo ~0.5B especializado.

Criterios:
- [ ] Comparativa de candidatos Qwen, Gemma, Nemotron y Mistral.
- [ ] Decision teacher/student y tecnica.
- [ ] Plan de dataset A materia y dataset B psicopedagogico.
- [ ] Metricas: RAM, KV cache, latencia, tokens/s, calidad y tasa de acierto.
- [ ] Riesgos y licencias documentados.

---

## E2-10 - Prototipo de Prompt Builder semanal

- Labels: `entrega-2`, `slm`, `docs`, `equipo`
- Prioridad: P0
- Dueno: equipo
- Depende de: E2-07, E2-08

Objetivo: definir el JSON/prompt que recomienda entre A/B/C.

Criterios:
- [ ] Template de prompt documentado.
- [ ] 3 ejemplos de entrada y salida esperada.
- [ ] Guardrails anti-invencion incluidos.

---

## E2-11 - Feedback loop y metricas

- Labels: `entrega-2`, `feedback`, `docs`, `equipo`
- Prioridad: P2
- Dueno: equipo
- Depende de: E2-07, E2-10

Objetivo: especificar como se mide acierto o descache.

Criterios:
- [ ] `feedback.schema.json` valido.
- [ ] Escala si/no y Likert opcional definida.
- [ ] KPI base: tasa de acierto y tasa de descache.

---

## E2-12 - Demo local Entrega 2

- Labels: `entrega-2`, `slm`, `feedback`, `equipo`
- Prioridad: P2
- Dueno: equipo
- Depende de: E2-02, E2-09, E2-10, E2-11

Objetivo: mostrar flujo minimo verificable.

Criterios:
- [ ] Perfil JSON + recursos -> prompt -> recomendacion -> feedback simulado.
- [ ] Bitacora de experimentos actualizada.
- [ ] Limites y siguiente paso con servidor del docente documentados.
