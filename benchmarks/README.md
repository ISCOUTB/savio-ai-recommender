# benchmarks — Mediciones reales de SLMs en local

Resultados comparativos de consumo de memoria y velocidad de inferencia, medidos en el hardware del equipo. **Solo datos propios** — ninguna cifra copiada de fuentes externas.

> 📌 Documentación de la fase: [docs/plan-trabajo/fase-3-benchmarks.md](../docs/plan-trabajo/fase-3-benchmarks.md)

## Metodología (Fase 3)

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

*(Se completa al cierre de la Fase 3 — alimenta la diapositiva 4 y la solicitud de servidor).*
