# 📦 Entrega 1 — PoC Funcional del Subsistema

**Estado:** 🔄 En curso
**Milestone:** [Entrega 1 - PoC Funcional](../../../milestones)

---

## 🎯 Objetivo de la entrega

Demostrar, con una prueba de concepto funcional ejecutable en local, que el subsistema de recomendación puede:

1. Ejecutar un **SLM de pesos abiertos 100% en local** (sin APIs comerciales, sin conexión a internet en tiempo de inferencia).
2. Generar recomendaciones académicas **personalizadas en tiempo de ejecución** a partir del contexto del estudiante (desempeño, tema, estilo de aprendizaje).
3. Operar bajo **guardrails rigurosos**: sin soluciones de tareas, sin off-topic, tono formativo y no punitivo.
4. Sustentar técnicamente la elección del modelo mediante **benchmarks propios** y una arquitectura de integración con Savio (Moodle) documentada.

---

## 🏃 Sprints de esta entrega

| Sprint | Documento | Issues | Estado |
|---|---|---|---|
| 1 | [Preparación del entorno y repositorio](sprint-1-preparacion.md) | #1, #2 | 🔄 En curso |
| 2 | [Motor de inferencia local](sprint-2-motor-inferencia.md) | #3 | ✅ Completado |
| 3 | [Prompts y guardrails](sprint-3-prompts-guardrails.md) | #4, #5, #6, #7 | ⏳ Pendiente |
| 4 | [Benchmarks de SLMs y arquitectura](sprint-4-benchmarks.md) | #8, #9, #11 | ⏳ Pendiente |
| 5 | [Presentación técnica](sprint-5-presentacion.md) | #12 | ⏳ Pendiente |
| 6 | [Verificación pre-entrega y demo](sprint-6-verificacion-demo.md) | #13 | ⏳ Pendiente |

**Dependencias:** Sprint 1 → Sprint 2 → Sprint 3 → Sprint 4 → Sprint 5 → Sprint 6 (secuenciales).

---

## ✅ Criterio de cierre de la Entrega 1

- [ ] Los 6 sprints completados (criterios de cierre verificados)
- [ ] Todos los issues del milestone cerrados
- [ ] PoC ejecutable de extremo a extremo: evento JSON → SLM local → recomendación
- [ ] Salidas de respaldo pre-generadas en `prompts/salidas-respaldo/`
- [ ] Presentación técnica completa
- [ ] Especificaciones de infraestructura documentadas y justificadas con benchmarks propios

---

## 🧪 Validación pedagógica

El diseño de las variables de adaptación (estilos de aprendizaje, desempeño académico) y el marco de medición de la motivación (modelo **ARCS** de Keller / instrumento **IMMS**) serán revisados y validados por la asesoría pedagógica del proyecto. Los ajustes derivados de dicha validación se registrarán en el documento del sprint correspondiente.
