# docs/arquitectura — Diagramas del subsistema

Diagramas de arquitectura, flujo de datos e integración con Savio (Moodle).

> 📌 Documentación de la fase: [docs/plan-trabajo/fase-3-benchmarks.md](../plan-trabajo/fase-3-benchmarks.md) (Issue #11)

## Flujo de datos del subsistema (diseño)

```
┌─────────────┐   evento (nota, entrega, inactividad)
│ Savio/Moodle│──────────────┐
└─────────────┘              ▼
                     ┌───────────────┐   consulta: nota, tema,
                     │  Middleware / │   estilo de aprendizaje
                     │  Orquestador  │
                     └───────┬───────┘
                             ▼
                     ┌───────────────┐   system prompt + guardrails
                     │ Prompt Engine │   + contexto del estudiante
                     └───────┬───────┘
                             ▼
                     ┌───────────────┐   inferencia local
                     │  SLM (Ollama) │   sin APIs externas
                     └───────┬───────┘
                             ▼
                     ┌───────────────┐
                     │ Panel Savio / │   recomendación personalizada
                     │  Mensajería   │
                     └───────────────┘
```

*(Versión enriquecida para la diapositiva 5: pendiente — Fase 3).*
