# Entregas del Proyecto - Indice

El proyecto avanza por **entregas** solicitadas por la direccion del proyecto. Cada entrega se divide en **sprints**: bloques de trabajo secuenciales (paso a paso) con objetivos, issues asociados, evidencias y criterios de cierre.

> Las entregas se documentan aqui a medida que son definidas por la direccion del proyecto, conservando la trazabilidad historica de cada fase.

---

## Entregas

| Entrega | Descripcion | Sprints | Estado |
|---|---|---|---|
| [**Entrega 1 - PoC Funcional**](entrega-1-poc-funcional/README.md) | Prueba de concepto del subsistema de recomendacion con SLM local: motor de inferencia, prompts con guardrails, benchmarks, arquitectura y material de presentacion | 6 | Completada |
| [**Entrega 2 - Personalizacion**](entrega-2-personalizacion/README.md) | Perfil psicopedagogico por instrumentos, materia piloto, propuesta de destilacion/fine-tuning de SLM y feedback loop (issues E2-01 a E2-12 cerrados) | 6 | Completada |
| [**Entrega 3 - Interpretacion Psicometrica**](entrega-3-interpretacion-psicometrica/README.md) | Sistema backend de inferencia con SLM cuantizado en CPU (sin VRAM) para interpretacion psicologica y vocacional integrada sobre puntajes originales brutos de CHASIDE, Felder-Silverman y Personalidad, bajo metodologia SMART | 4 | En curso |

**Leyenda:** Pendiente - En curso - Completada

---

## Convenciones del repositorio

### Flujo con issues
1. Cada issue pertenece a una entrega (milestone) y a un sprint (label `sprint-N` o `entrega-N`).
2. Maximo **1 issue "En progreso" por persona** (tablero: Backlog -> En progreso -> En revision -> Listo).
3. Todo entregable pasa por **revision de otro integrante** antes de marcarse "Listo".
4. Los issues se cierran con el commit/comentario que los resuelve.

### Commits
Formato: `tipo(alcance): descripcion (#issue)` - ejemplos:
- `docs(sprint-1): estructura inicial del repositorio (#2)`
- `feat(poc): script de inferencia con Ollama (#3)`
- `prompts(guardrails): system prompt v1 (#4)`
- `bench(qwen): resultados de RAM y tokens/s (#8)`
- `docs(entrega-3): formular objetivos SMART y reestructurar alcance (#40)`

### Rigor psicometrico y validacion (Directriz de Entrega 3)
Los tres instrumentos seleccionados (**CHASIDE**, **Modelo de Felder-Silverman** y **Test de Personalidad**) estan cientificamente validados. Queda **estrictamente prohibido alterar, normalizar o modificar sus escalas o puntajes originales**. El sistema de IA recibe las puntuaciones brutas nativas, las cruza con la literatura teorica de cada test y genera un perfil interpretativo integrado para apoyar el diagnostico inicial sin reemplazar al profesional.
