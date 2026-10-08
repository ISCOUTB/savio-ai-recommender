# Sprint 4 — Benchmarks de SLMs y arquitectura

**Entrega:** 1 — PoC Funcional
**Estado:** 🔄 En curso
**Issues:** #8, #9, #11
**Depende de:** Sprint 1 (modelos descargados)

---

## 🎯 Objetivo

Medir el rendimiento real de los SLMs candidatos en el hardware disponible y documentar la arquitectura de integración con Savio (Moodle). **Solo datos propios medidos** — ninguna cifra copiada de fuentes externas.

---

## 📋 Issues del sprint

### #8 — Benchmark: RAM, tokens/s y tiempo de respuesta · `backend` `infra`

**Mediciones:**
- RAM durante inferencia (Administrador de tareas o `psutil`)
- Tokens/segundo (`ollama run --verbose`)
- Tiempo de respuesta para ~300 tokens de salida

**Modelos:** Qwen 2.5 1.5B, Gemma 2 2B, Qwen 2.5 3B (si es viable).

**Criterio de aceptación:**
- [ ] Mediciones registradas para cada modelo

---

### #9 — Tabla comparativa y modelo seleccionado · `docs`

Resultados en `benchmarks/README.md` con justificación del modelo seleccionado.

**Criterio de aceptación:**
- [x] Tabla completa con datos propios
- [x] Conclusión que alimente la presentación técnica y la solicitud de infraestructura

---

### #11 — Diagrama de arquitectura · `docs`

Flujo: Savio/Moodle (evento) → Middleware orquestador → Prompt Engine (guardrails) → SLM local (Ollama) → Panel/mensajería del estudiante. Archivo en `docs/arquitectura/`.

**Criterio de aceptación:**
- [x] Diagrama exportado (PNG/SVG) y referenciado en la presentación técnica

---

## ✅ Criterio de cierre del sprint

- [x] Tabla de benchmarks con datos propios documentada
- [x] Diagrama de arquitectura exportado y versionado
- [x] Modelo seleccionado justificado técnicamente (Qwen 2.5 3B — ver [benchmarks/README.md](../../../benchmarks/README.md))

---

## 📝 Registro de ejecución

| Acción | Evidencia | Responsable | Estado |
|---|---|---|---|
| Script de benchmark (RAM, VRAM, tokens/s, latencia; GPU y CPU) | [benchmarks/benchmark.py](../../../benchmarks/benchmark.py) | Persona 3 | ✅ |
| Mediciones: 3 modelos × 2 modos × 3 corridas (2026-10-07) | [benchmarks/resultados/](../../../benchmarks/resultados/) | Persona 3 | ✅ |
| #9 — Tabla comparativa y modelo seleccionado | [benchmarks/README.md](../../../benchmarks/README.md) | Persona 3 | ✅ |
| #11 — Diagrama de arquitectura (SVG/PNG + generador) | [docs/arquitectura/](../../arquitectura/README.md) | Persona 3 | ✅ |
