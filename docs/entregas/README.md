# 📦 Entregas del Proyecto — Índice

El proyecto avanza por **entregas** solicitadas por la dirección del proyecto. Cada entrega se divide en **sprints**: bloques de trabajo secuenciales (paso a paso) con objetivos, issues asociados, evidencias y criterios de cierre.

> Las entregas futuras se documentarán aquí a medida que sean definidas por la dirección del proyecto, cada una con sus propios procesos y procedimientos.

---

## Entregas

| Entrega | Descripción | Sprints | Estado |
|---|---|---|---|
| [**Entrega 1 — PoC Funcional**](entrega-1-poc-funcional/README.md) | Prueba de concepto del subsistema de recomendación con SLM local: motor de inferencia, prompts con guardrails, benchmarks, arquitectura y material de presentación | 6 | 🔄 En curso |
| Entrega 2 | *Por definir según los lineamientos de la dirección del proyecto* | — | ⏳ No iniciada |

**Leyenda:** ⏳ No iniciada · 🔄 En curso · ✅ Completada

---

## Convenciones del repositorio

### Flujo con issues
1. Cada issue pertenece a una entrega (milestone) y a un sprint (label `sprint-N`).
2. Máximo **1 issue "En progreso" por persona** (tablero: Backlog → En progreso → En revisión → Listo).
3. Todo entregable pasa por **revisión de otro integrante** antes de marcarse "Listo".
4. Los issues se cierran con el commit/comentario que los resuelve.

### Commits
Formato: `tipo(alcance): descripción (#issue)` — ejemplos:
- `docs(sprint-1): estructura inicial del repositorio (#2)`
- `feat(poc): script de inferencia con Ollama (#3)`
- `prompts(guardrails): system prompt v1 (#4)`
- `bench(qwen): resultados de RAM y tokens/s (#8)`

### Validación pedagógica
Los instrumentos de adaptación (estilos de aprendizaje) y las métricas de motivación (modelo **ARCS** / instrumento **IMMS**) serán revisados y validados por la asesoría pedagógica del proyecto antes de su aplicación. Las decisiones metodológicas validadas se documentarán en la entrega correspondiente.
