# Sprint 5 — Presentacion tecnica

**Entrega:** 1 — PoC Funcional
**Estado:** ✅ Completado
**Issues:** #12
**Depende de:** Sprints 3 y 4 (resultados de prompts y benchmarks)

---

## 🎯 Objetivo

Material de presentacion **completamente terminado** para sustentar la Entrega 1.

---

## 📋 Issues del sprint

### #12 — Presentacion tecnica de 8 secciones · `docs`

1. Portada y ficha tecnica
2. Problema y justificacion (uso estatico de Savio/Moodle, personalizacion sin sobrecargar al docente)
3. Estado del arte (ALEKS, Alta/Knewton → alternativa abierta y local)
4. Evaluacion tecnica de SLMs — **con datos propios de `benchmarks/`**
5. Arquitectura del subsistema + guardrails — **con diagrama de `docs/arquitectura/`**
6. Modelo de adaptacion pedagogica + metricas ARCS/IMMS
7. Demostracion funcional (incluye plan B: salidas pre-generadas)
8. Cronograma del proyecto + solicitud de infraestructura

**Criterio de aceptacion:**
- [x] 8 secciones completas, sin apartados pendientes → [docs/presentacion/](../../presentacion/README.md)
- [ ] Revisada y aprobada por todo el equipo

---

## ✅ Criterio de cierre del sprint

- [ ] Material de presentacion terminado y aprobado por el equipo

---

## 📝 Registro de ejecucion

| Accion | Evidencia | Responsable | Estado |
|---|---|---|---|
| Presentacion de 16 diapositivas (8 secciones + agenda y conclusiones) con notas del orador | [presentacion-tecnica-entrega1.pptx](../../presentacion/presentacion-tecnica-entrega1.pptx) | Persona 3 | ✅ |
| Generador reproducible (datos de benchmarks leidos de `resultados.json`) | [generar_presentacion.py](../../presentacion/generar_presentacion.py) | Persona 3 | ✅ |
| Diagrama de arquitectura propio (#11) | [arquitectura-savio-ia.png](../../arquitectura/arquitectura-savio-ia.png) (reemplaza al diagrama original del subsistema; la imagen original sigue incrustada en el `.pptx`) | Persona 3 | ✅ |
| Salidas de demo con el modelo seleccionado (Qwen 2.5 3B): escenarios A, B y 3 ataques | [demo-qwen2.5-3b/](../../presentacion/demo-qwen2.5-3b/) | Persona 3 | ✅ |
| Revision y aprobacion de todo el equipo | [Tabla de revision](../../presentacion/README.md#revision-del-equipo-criterio-de-aceptacion) | Equipo | ⏳ |
