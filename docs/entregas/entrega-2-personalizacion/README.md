# Entrega 2 - Personalizacion de contenidos en Savio/Moodle

**Estado:** En curso
**Milestone sugerido:** Entrega 2 - Personalizacion
**Fuentes base:** `fuentes/Segunda_Entrega_Proyecto_LLM_Savio_Actualizado.docx` y `fuentes/Segunda_Entrega_Proyecto_LLM_Savio.docx`

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
| 1 | [Plan, repo y Moodle minimo](sprint-1-plan-y-moodle.md) | ROADMAP, issues, Docker Moodle minimo | En curso |
| 2 | [Perfil JSON y tests](sprint-2-perfil-json-tests.md) | Modelado de Estilos, Personalidad y CHASIDE | Pendiente |
| 3 | [Materia piloto y recursos](sprint-3-materia-piloto.md) | Taller de Escritura recomendado | Pendiente |
| 4 | [Destilacion y fine-tuning](sprint-4-destilacion-finetuning.md) | Nucleo tecnico de la entrega | Pendiente |
| 5 | [Prompt builder y feedback](sprint-5-prompt-y-feedback.md) | JSON -> prompt -> recomendacion -> feedback | Pendiente |
| 6 | [Demo y cierre](sprint-6-demo-y-cierre.md) | Flujo minimo verificable | Pendiente |

---

## Artefactos base

- Esquema de perfil: `docs/especificaciones/perfil-estudiante.schema.json`
- Esquema de recurso semanal: `docs/especificaciones/recurso-semanal.schema.json`
- Esquema de feedback: `docs/especificaciones/feedback.schema.json`
- Investigacion: `docs/investigacion/modelos-candidatos.md` y `docs/investigacion/destilacion-finetuning.md`
- Issues listos: `docs/entregas/entrega-2-personalizacion/github-issues.md`

---

## Criterio de cierre de la entrega, version base

- [ ] Plan documentado y tablero operativo.
- [ ] Moodle local minimo instalado con bloques base, con apoyo del docente.
- [ ] Tests modelados a un schema JSON unico.
- [ ] Materia piloto y recursos A/B/C definidos.
- [ ] Propuesta tecnica de destilacion/fine-tuning justificada por RAM, KV cache y latencia.
- [ ] Prompt builder minimo validado con ejemplos.
- [ ] Feedback loop y metricas definidos.
- [ ] Demo local minima documentada.
