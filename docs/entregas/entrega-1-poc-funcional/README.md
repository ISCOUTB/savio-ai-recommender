# Entrega 1 - PoC Funcional del Subsistema

**Estado:** Completado
**Milestone:** [Entrega 1 - PoC Funcional](../../../milestones)

---

## Objetivo de la entrega

Demostrar, con una prueba de concepto funcional ejecutable en local, que el subsistema de recomendacion puede:

1. Ejecutar un **SLM de pesos abiertos 100% en local** (sin APIs comerciales, sin conexion a internet en tiempo de inferencia).
2. Generar recomendaciones academicas **personalizadas en tiempo de ejecucion** a partir del contexto del estudiante (desempeno, tema, estilo de aprendizaje).
3. Operar bajo **guardrails rigurosos**: sin soluciones de tareas, sin off-topic, tono formativo y no punitivo.
4. Sustentar tecnicamente la eleccion del modelo mediante **benchmarks propios** y una arquitectura de integracion con Savio (Moodle) documentada.

---

## Sprints de esta entrega

| Sprint | Documento | Issues | Estado |
|---|---|---|---|
| 1 | [Preparacion del entorno y repositorio](sprint-1-preparacion.md) | #1, #2 | Completado |
| 2 | [Motor de inferencia local](sprint-2-motor-inferencia.md) | #3 | Completado |
| 3 | [Prompts y guardrails](sprint-3-prompts-guardrails.md) | #4, #5, #6, #7 | Completado |
| 4 | [Benchmarks de SLMs y arquitectura](sprint-4-benchmarks.md) | #8, #9, #11 | Completado |
| 5 | [Presentacion tecnica](sprint-5-presentacion.md) | #12 | Completado |
| 6 | [Verificacion pre-entrega y demo](sprint-6-verificacion-demo.md) | #13 | Completado |

**Dependencias:** Sprint 1 -> Sprint 2 -> Sprint 3 -> Sprint 4 -> Sprint 5 -> Sprint 6 (secuenciales).

---

## Criterio de cierre de la Entrega 1

- [x] Los 6 sprints completados (criterios de cierre verificados)
- [x] Todos los issues del milestone cerrados
- [x] PoC ejecutable de extremo a extremo: evento JSON -> SLM local -> recomendacion
- [x] Salidas de respaldo pre-generadas en `prompts/salidas-respaldo/`
- [x] Presentacion tecnica completa
- [x] Especificaciones de infraestructura documentadas y justificadas con benchmarks propios

---

## Validacion pedagogica

El diseno de las variables de adaptacion (estilos de aprendizaje, desempeno academico) y el marco de medicion de la motivacion (modelo **ARCS** de Keller / instrumento **IMMS**) seran revisados y validados por la asesoria pedagogica del proyecto. Los ajustes derivados de dicha validacion se registraran en el documento del sprint correspondiente.
