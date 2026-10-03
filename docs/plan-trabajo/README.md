# 📋 Plan de Trabajo — Índice Maestro

Este directorio documenta el desarrollo del proyecto **fase por fase**, con evidencias, comandos ejecutados, decisiones tomadas y criterios de cierre. Cada fase está asociada a issues del repositorio y a un milestone.

**Regla de avance:** ninguna fase se marca como ✅ completa sin que sus criterios de cierre estén verificados y sus issues asociados cerrados.

---

## Milestones

| Milestone | Meta | Fecha objetivo |
|---|---|---|
| **M1 — PoC Funcional** | SLM corriendo local + scripts + prompts + benchmarks | Día 3 |
| **M2 — Entrega (demo en vivo)** | Presentación terminada + ensayo + Teams enviado | Sábado 11:00 AM |

---

## Fases

| Fase | Documento | Issues | Milestone | Estado |
|---|---|---|---|---|
| 0 | [Preparación del entorno y repositorio](fase-0-preparacion.md) | #1, #2, #10 | M1 / M2 | 🔄 En curso |
| 1 | [Motor de inferencia local](fase-1-motor-inferencia.md) | #3 | M1 | ⏳ Pendiente |
| 2 | [Prompts y guardrails](fase-2-prompts-guardrails.md) | #4, #5, #6, #7 | M1 | ⏳ Pendiente |
| 3 | [Benchmarks y arquitectura](fase-3-benchmarks.md) | #8, #9, #11 | M1 / M2 | ⏳ Pendiente |
| 4 | [Presentación ejecutiva](fase-4-presentacion.md) | #12 | M2 | ⏳ Pendiente |
| 5 | [Entrega y demo en vivo](fase-5-entrega.md) | #13 | M2 | ⏳ Pendiente |

**Leyenda:** ⏳ Pendiente · 🔄 En curso · ✅ Completa

---

## Convenciones del equipo

### Flujo con issues
1. Máximo **1 issue "En progreso" por persona** (tablero Kanban: Backlog → En progreso → En revisión → Listo).
2. Todo entregable pasa por **revisión de otro integrante** antes de marcarse "Listo".
3. Los issues se cierran con el commit/comentario que los resuelve.

### Commits
Formato: `tipo(alcance): descripción` — ejemplos:
- `docs(fase-0): estructura inicial del plan de trabajo`
- `feat(poc): script de inferencia con Ollama (#3)`
- `prompts(guardrails): system prompt v1 (#4)`
- `bench(qwen): resultados de RAM y tokens/s (#8)`

### Reuniones

| Tipo | Cuándo | Duración | Contenido |
|---|---|---|---|
| Daily standup | Días 1-4 | 10 min | Qué hice / qué haré / qué me bloquea |
| Revisión de prompts | Día 2 (noche) | 30 min | Los 3 integrantes validan los escenarios |
| Ensayo general | Día 4 | 1 hora | Demo cronometrada + repaso de diapositivas |
