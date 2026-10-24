# Entrega 2 - Personalizacion de contenidos en Savio/Moodle

**Estado:** Completada (fase cerrada; evolucion y nuevo rumbo en [Entrega 3 - Interpretacion Psicometrica](../entrega-3-interpretacion-psicometrica/README.md))
**Milestone sugerido:** Entrega 2 - Personalizacion
**Fuentes base:** documentos de la direccion del proyecto (no versionados): [fuentes/](../../../fuentes/README.md). Archivos referenciados: `Segunda_Entrega_Proyecto_LLM_Savio_Actualizado.docx` y `Segunda_Entrega_Proyecto_LLM_Savio.docx`.

> **Nota de cierre y transicion a Entrega 3 (2026-10-23):**
> Los issues nucleares de esta entrega (`E2-01` a `E2-12`, `#18` al `#29`) fueron completados y cerrados en GitHub. En la sesion de revision con el docente se respondieron las consultas psicometricas `#37` (`E2-13`), `#39` (`E2-15`) y `#41` (`E2-17`) -estableciendo el uso exclusivo de **puntuaciones originales brutas** sin alterar escalas validadas- y quedaron **cerradas en GitHub** el mismo dia (`not planned` para `#37` y `#39`; `completed` para `#41`). Los issues abiertos restantes (`#38`, `#40`, `#42`, `#43`, `#44`) fueron recategorizados dentro de la **[Entrega 3 - Interpretacion Psicometrica](../entrega-3-interpretacion-psicometrica/README.md)** y el milestone se cerro como **Completado**.

---

## Directriz central

El profesor delimita el trabajo asi:

- **Lo que el profesor maneja y facilita:** extraccion y gestion de recursos de Savio, activacion e instalacion de bloques de Moodle en Docker, y provision de servidor cuando el prototipo funcione.
- **Lo que el profesor no controla y es el reto del equipo:** destilacion y fine-tuning de un SLM pequeno, con investigacion, experimentacion e innovacion.

Regla de ejecucion para esta entrega:

> Moodle es habilitador minimo. El esfuerzo del equipo se concentra en destilar y ajustar el modelo.

Peso sugerido del trabajo:

- 60% destilacion / fine-tuning.
- 25% modelado psicopedagogico y JSON.
- 15% Moodle local minimo viable.

---

## Objetivo de la entrega

Construir el plan y el prototipo base de un recomendador **no determinista** que, para una semana academica, elija entre Recurso A, Recurso B o Recurso C segun el perfil del estudiante y deje una justificacion pedagogica breve.

No se resuelve con reglas fijas `si perfil 1 -> recurso A`; el modelo razona sobre la interseccion entre perfil, tema y formato del recurso.

---

## Instrumentos por integrante

| Integrante | Instrumento | Salida concreta |
|---|---|---|
| Persona 1 | Estilos de Aprendizaje | Metricas del bloque y traduccion a `perfil.estilos_aprendizaje` para el prompt |
| Persona 2 | Personalidad | Rasgos conductuales y traduccion a `perfil.personalidad` |
| Persona 3 | CHASIDE | Areas vocacionales y traduccion a `perfil.chaside` para analogias contextuales |

---

## Sprints propuestos

| Sprint | Documento | Foco | Estado |
|---|---|---|---|
| 1 | [Plan, repo y Moodle minimo](sprint-1-plan-y-moodle.md) | ROADMAP, issues, Docker Moodle minimo | Completado (E2-16 migrado a E3-02) |
| 2 | [Perfil JSON y tests](sprint-2-perfil-json-tests.md) | Modelado de Estilos, Personalidad y CHASIDE | Completado (E2-17 resuelto, E2-18 migrado a E3-05) |
| 3 | [Materia piloto y recursos](sprint-3-materia-piloto.md) | Taller de Escritura recomendado | Completado |
| 4 | [Destilacion y fine-tuning](sprint-4-destilacion-finetuning.md) | Nucleo tecnico de la entrega | Completado (E2-19/E2-20 migrados a E3-06/E3-08) |
| 5 | [Prompt builder y feedback](sprint-5-prompt-y-feedback.md) | JSON -> prompt -> recomendacion -> feedback | Completado |
| 6 | [Demo y cierre](sprint-6-demo-y-cierre.md) | Flujo minimo verificable | Completado |

### Issues por sprint

| Sprint | Issues | Foco |
| :--- | :--- | :--- |
| 1 | E2-01, E2-02, E2-03, E2-16 | Plan, Moodle y cronograma |
| 2 | E2-04, E2-05, E2-06, E2-07, E2-17, E2-18 | Perfil, instrumento y tres perfiles reales |
| 3 | E2-08 | Materia piloto y recursos A/B/C |
| 4 | E2-09 | Nucleo de destilacion |
| 5 | E2-10, E2-11 | Prompt builder y feedback |
| 6 | E2-12 | Demo y cierre |
| Post-entrega | E2-19, E2-20 | Datasets y ajuste, solo si alcanza |
| Transversal | E2-13, E2-14, E2-15 | Consultas a docente y area legal |

Orden de ejecucion acordado (2026-10-20): cronograma (E2-16) y consulta del
instrumento (E2-17) primero; luego el flujo demostrable
(E2-08 -> E2-10 -> E2-11 -> E2-12), con E2-09 en paralelo y E2-18 donde haya
hueco. El ajuste (E2-19 y E2-20) va despues de la demo y **no** es dependencia
de ella.

La arquitectura, la rubrica de calidad y la medicion de concurrencia quedan como
criterios dentro de E2-12, E2-11 y E2-09; no se crean como issues separados para
no duplicar el trabajo.

---

## Artefactos base

- Esquema de perfil: `docs/especificaciones/perfil-estudiante.schema.json`
- Esquema de recurso semanal: `docs/especificaciones/recurso-semanal.schema.json`
- Esquema de feedback: `docs/especificaciones/feedback.schema.json`, `docs/especificaciones/feedback-loop.md` y `poc_slm/feedback_tracker.py` (E2-11)
- Prompt y builder: `prompts/system_prompt_recomendacion.md`, `poc_slm/prompt_builder.py` y evidencia en `prompts/escenarios/personalizacion_semanal.md` (E2-10)
- Moodle local: [guia-paso-a-paso-docker-moodle.md](guia-paso-a-paso-docker-moodle.md) (fuente) y `Guia_Paso_a_Paso_Docker_Moodle_E2_02.docx` (entregable **generado**, no editar a mano; se regenera con `guia_a_docx.py`)
- Investigacion: `docs/investigacion/propuesta-destilacion-slm.md` (E2-09 consolidado), `docs/investigacion/modelos-candidatos.md`, `docs/investigacion/destilacion-finetuning.md`, `docs/investigacion/riesgos-y-licencias.md`
- Decisiones y problemas del perfilamiento: `docs/decisiones/decisiones-y-problemas.md`
- Issues listos: [github-issues.md](github-issues.md)

---

## Criterio de cierre de la entrega, version base

- [x] Plan documentado y tablero operativo.
- [x] Moodle local minimo instalado con los bloques IS-UTB de Estilos de Aprendizaje, Personalidad y CHASIDE (E2-02 y E2-03); ver `moodle/plugins.md`.
- [x] Tests modelados a un schema JSON unico (`docs/especificaciones/perfil-estudiante.schema.json` y `validar-perfiles.py`, E2-04 a E2-07).
- [x] Materia piloto y recursos A/B/C definidos (`docs/especificaciones/materia-piloto-recursos.md` y `poc_slm/recursos/semana_1.json`, E2-08).
- [x] Propuesta tecnica de destilacion/fine-tuning justificada por RAM, KV cache y latencia (`docs/investigacion/propuesta-destilacion-slm.md`, E2-09).
- [x] Prompt builder minimo validado con ejemplos.
- [x] Feedback loop y metricas definidos.
- [x] Demo local minima documentada ([sprint-6-demo-y-cierre.md](sprint-6-demo-y-cierre.md) y `experimentos/bitacora.md`, E2-12).
- [ ] Cronograma con fechas aprobado por el equipo (E2-16).
- [x] Instrumento de estilos confirmado con la docente o supuesto declarado (Felder-Soloman declarado como supuesto canonico en `docs/especificaciones/instrumento-estilos-aprendizaje.md`, E2-17).
