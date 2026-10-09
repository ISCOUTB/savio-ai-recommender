# Sprint 4 - Benchmarks de SLMs y arquitectura

**Entrega:** 1 - PoC Funcional
**Estado:** En curso
**Issues:** #8, #9, #11
**Depende de:** Sprint 1 (modelos descargados)

---

## Objetivo

Medir el rendimiento real de los SLMs candidatos en el hardware disponible y documentar la arquitectura de integracion con Savio (Moodle). **Solo datos propios medidos**; ninguna cifra se copia de fuentes externas.

---

## Issues del sprint

### #8 - Benchmark: RAM, tokens/s y tiempo de respuesta · `backend` `infra`

**Mediciones:**
- RAM durante inferencia (`psutil`)
- Tokens/segundo reportados por Ollama
- Tiempo de respuesta para ~300 tokens de salida
- VRAM cuando el equipo tiene GPU NVIDIA dedicada

**Modelos:** Qwen 2.5 1.5B, Gemma 2 2B, Qwen 2.5 3B.

**Criterio de aceptacion:**
- [x] Mediciones registradas para cada modelo en equipo AMD/NVIDIA
- [x] Mediciones registradas para cada modelo en equipo Intel sin GPU dedicada

---

### #9 - Tabla comparativa y modelo seleccionado · `docs`

Resultados integrados en [`benchmarks/README.md`](../../../benchmarks/README.md), con reporte por equipo en [`benchmarks/equipos/`](../../../benchmarks/equipos/).

**Criterio de aceptacion:**
- [x] Tabla completa con datos propios
- [x] Comparacion CPU entre Ryzen 5 5600H e Intel i5-1235U
- [x] Decision reconciliada: Qwen 2.5 1.5B para demo local sin GPU dedicada; Qwen 2.5 3B como objetivo institucional con GPU recomendada

---

### #11 - Diagrama de arquitectura · `docs`

Flujo: Savio/Moodle (evento) -> Middleware orquestador -> Prompt Engine (guardrails) -> SLM local (Ollama) -> Panel/mensajeria del estudiante. Archivo en `docs/arquitectura/`.

**Criterio de aceptacion:**
- [x] Diagrama exportado (PNG/SVG) y referenciado en la presentacion tecnica

---

## Criterio de cierre del sprint

- [x] Tabla de benchmarks con datos propios documentada
- [x] Resultados ordenados por equipo en `benchmarks/resultados/`
- [x] Diagrama de arquitectura exportado y versionado
- [x] Modelo seleccionado justificado tecnicamente: ver [`benchmarks/README.md`](../../../benchmarks/README.md)
- [ ] Validar licencia de Qwen 2.5 3B antes de despliegue institucional

---

## Registro de ejecucion

| Accion | Evidencia | Responsable | Estado |
|---|---|---|---|
| Script de benchmark (RAM, VRAM, tokens/s, latencia; GPU y CPU) | [benchmarks/benchmark.py](../../../benchmarks/benchmark.py) | Persona 3 | Completado |
| Mediciones AMD Ryzen + RTX 3050: 3 modelos x 2 modos x 3 corridas | [benchmarks/resultados/amd-ryzen-5-5600h-rtx-3050/](../../../benchmarks/resultados/amd-ryzen-5-5600h-rtx-3050/) | Persona 3 | Completado |
| Mediciones Intel i5 sin GPU dedicada: comparativa y estabilidad CPU | [benchmarks/equipos/intel-i5-1235u-iris-xe.md](../../../benchmarks/equipos/intel-i5-1235u-iris-xe.md) | Persona 1 | Completado |
| #9 - Tabla comparativa integrada y modelo seleccionado | [benchmarks/README.md](../../../benchmarks/README.md) | Persona 1 / Persona 3 | Completado |
| #11 - Diagrama de arquitectura (SVG/PNG + generador) | [docs/arquitectura/](../../arquitectura/README.md) | Persona 3 | Completado |
