# 📦 Entregas del Proyecto — Indice

El proyecto avanza por **entregas** solicitadas por la direccion del proyecto. Cada entrega se divide en **sprints**: bloques de trabajo secuenciales (paso a paso) con objetivos, issues asociados, evidencias y criterios de cierre.

> Las entregas futuras se documentaran aqui a medida que sean definidas por la direccion del proyecto, cada una con sus propios procesos y procedimientos.

---

## Entregas

| Entrega | Descripcion | Sprints | Estado |
|---|---|---|---|
| [**Entrega 1 — PoC Funcional**](entrega-1-poc-funcional/README.md) | Prueba de concepto del subsistema de recomendacion con SLM local: motor de inferencia, prompts con guardrails, benchmarks, arquitectura y material de presentacion | 6 | ✅ Completada |
| [**Entrega 2 — Personalizacion**](entrega-2-personalizacion/README.md) | Perfil psicopedagogico por instrumentos, materia piloto, destilacion/fine-tuning de SLM y feedback loop | 6 | 🔄 En curso |

**Leyenda:** ⏳ No iniciada · 🔄 En curso · ✅ Completada

---

## Convenciones del repositorio

### Flujo con issues
1. Cada issue pertenece a una entrega (milestone) y a un sprint (label `sprint-N`).
2. Maximo **1 issue "En progreso" por persona** (tablero: Backlog → En progreso → En revision → Listo).
3. Todo entregable pasa por **revision de otro integrante** antes de marcarse "Listo".
4. Los issues se cierran con el commit/comentario que los resuelve.

### Commits
Formato: `tipo(alcance): descripcion (#issue)` — ejemplos:
- `docs(sprint-1): estructura inicial del repositorio (#2)`
- `feat(poc): script de inferencia con Ollama (#3)`
- `prompts(guardrails): system prompt v1 (#4)`
- `bench(qwen): resultados de RAM y tokens/s (#8)`

### Validacion pedagogica
Los instrumentos de adaptacion (estilos de aprendizaje) y las metricas de motivacion (modelo **ARCS** / instrumento **IMMS**) seran revisados y validados por la asesoria pedagogica del proyecto antes de su aplicacion. Las decisiones metodologicas validadas se documentaran en la entrega correspondiente.
