# benchmarks — Mediciones reales de SLMs en local

Resultados comparativos de consumo de memoria y velocidad de inferencia, medidos en el hardware del equipo. **Solo datos propios** — ninguna cifra copiada de fuentes externas.

> 📌 Documentación del sprint: [docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md](../docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md)

## Metodología (Sprint 4 — Entrega 1)

- **RAM:** medida durante inferencia (Administrador de tareas / `psutil`).
- **Velocidad:** tokens/segundo reportados por `ollama run --verbose`.
- **Prompt estándar:** generación de ~300 tokens de salida para comparación justa.
- **Calidad en español:** rúbrica 1–5 con justificación (comprensión contextual, seguimiento de instrucciones, tono pedagógico).

## Hardware de prueba

| Componente | Especificación |
|---|---|
| CPU | _pendiente_ |
| RAM | _pendiente_ |
| GPU | _pendiente_ |
| SO | _pendiente_ |

## Resultados

| Modelo | Cuantización | RAM en inferencia | Tokens/seg | Tiempo (~300 tok) | Calidad ES (1–5) |
|---|---|---|---|---|---|
| Qwen 2.5 1.5B | Q4_K_M | _pendiente_ | _pendiente_ | _pendiente_ | _pendiente_ |
| Gemma 2 2B | Q4_K_M | _pendiente_ | _pendiente_ | _pendiente_ | _pendiente_ |
| Qwen 2.5 3B | Q4_K_M | _pendiente_ | _pendiente_ | _pendiente_ | _pendiente_ |

## Conclusión y modelo seleccionado

*(Se completa al cierre del Sprint 4 — alimenta la presentación técnica y la solicitud de infraestructura).*
