# Sprint 5 — Presentación técnica

**Entrega:** 1 — PoC Funcional
**Estado:** 🔄 En revisión del equipo
**Issues:** #12
**Depende de:** Sprints 3 y 4 (resultados de prompts y benchmarks)

---

## 🎯 Objetivo

Material de presentación **completamente terminado** para sustentar la Entrega 1.

---

## 📋 Issues del sprint

### #12 — Presentación técnica de 8 secciones · `docs`

1. Portada y ficha técnica
2. Problema y justificación (uso estático de Savio/Moodle, personalización sin sobrecargar al docente)
3. Estado del arte (ALEKS, Alta/Knewton → alternativa abierta y local)
4. Evaluación técnica de SLMs — **con datos propios de `benchmarks/`**
5. Arquitectura del subsistema + guardrails — **con diagrama de `docs/arquitectura/`**
6. Modelo de adaptación pedagógica + métricas ARCS/IMMS
7. Demostración funcional (incluye plan B: salidas pre-generadas)
8. Cronograma del proyecto + solicitud de infraestructura

**Criterio de aceptación:**
- [x] 8 secciones completas, sin apartados pendientes → [docs/presentacion/](../../presentacion/README.md)
- [ ] Revisada y aprobada por todo el equipo

---

## ✅ Criterio de cierre del sprint

- [ ] Material de presentación terminado y aprobado por el equipo

---

## 📝 Registro de ejecución

| Acción | Evidencia | Responsable | Estado |
|---|---|---|---|
| Presentación de 16 diapositivas (8 secciones + agenda y conclusiones) con notas del orador | [presentacion-tecnica-entrega1.pptx](../../presentacion/presentacion-tecnica-entrega1.pptx) | Persona 3 | ✅ |
| Generador reproducible (datos de benchmarks leídos de `resultados.json`) | [generar_presentacion.py](../../presentacion/generar_presentacion.py) | Persona 3 | ✅ |
| Diagrama de arquitectura propio (#11) | [arquitectura-subsistema.svg](../../arquitectura/arquitectura-subsistema.svg) | Persona 3 | ✅ |
| Salidas de demo con el modelo seleccionado (Qwen 2.5 3B): escenarios A, B y 3 ataques | [demo-qwen2.5-3b/](../../presentacion/demo-qwen2.5-3b/) | Persona 3 | ✅ |
| Revisión y aprobación de todo el equipo | [Tabla de revisión](../../presentacion/README.md#revisión-del-equipo-criterio-de-aceptación) | Equipo | ⏳ |
