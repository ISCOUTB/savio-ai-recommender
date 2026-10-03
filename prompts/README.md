# prompts — Guardrails y escenarios de demostración

Colección versionada de system prompts, escenarios de la PoC y pruebas adversariales.

> 📌 Documentación del sprint: [docs/entregas/entrega-1-poc-funcional/sprint-3-prompts-guardrails.md](../docs/entregas/entrega-1-poc-funcional/sprint-3-prompts-guardrails.md)

## Contenido (Sprint 3 — Entrega 1)

```
prompts/
├── system_guardrails.md        ← System prompt con las 4 reglas de seguridad
├── escenarios/
│   ├── A_bajo_desempeno.md     ← Tutoría reactiva ante nota baja
│   └── B_estilos_aprendizaje.md ← Adaptación visual vs. textual
├── pruebas-adversariales.md    ← Ataques de prueba y resultados reales
├── salidas-respaldo/           ← Respuestas pre-generadas (plan B de la demo)
└── README.md
```

## Las 4 reglas de guardrails

1. Solo temas de la materia — redirigir ante off-topic.
2. Nunca soluciones completas de tareas — solo guías metodológicas.
3. Tono empático, formativo, no punitivo.
4. Salida estructurada (Markdown con esquema fijo).

## Hallazgos técnicos

*(Se documentan aquí durante el Sprint 3 — ej. comportamiento de SLMs pequeños ante system prompts).*
