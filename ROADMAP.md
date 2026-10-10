# ROADMAP — Savio AI Recommender

> Plan operativo del proyecto. Detalle de sprints e issues en cada carpeta de [docs/entregas/](docs/entregas/README.md).

## Vista general

| Entrega | Alcance | Estado |
|---|---|---|
| [Entrega 1 - PoC Funcional](docs/entregas/entrega-1-poc-funcional/README.md) | SLM local con Ollama, prompts con guardrails, benchmarks propios, arquitectura y presentacion tecnica | Completada |
| [Entrega 2 - Personalizacion](docs/entregas/entrega-2-personalizacion/README.md) | Perfil psicopedagogico (Estilos de Aprendizaje, Personalidad, CHASIDE), materia piloto, destilacion/fine-tuning del SLM y feedback loop | En curso |

## Secuencia de trabajo

1. **Entrega 1** demuestra que un SLM local genera recomendaciones utiles bajo guardrails (Sprints 1-6 en secuencia; dependencias en su README).
2. **Entrega 2** personaliza con datos psicopedagogicos reales. Regla de ejecucion: Moodle es habilitador minimo; el nucleo es destilacion/fine-tuning (peso sugerido: 60% destilacion, 25% modelado psicopedagogico, 15% Moodle local).

## Decisiones tecnicas activas

- **Modelos:** Qwen 2.5 1.5B para demo local sin GPU; Qwen 2.5 3B objetivo institucional (validar licencia antes de despliegue). Ver `benchmarks/README.md`.
- **Runtime:** Ollama local, sin APIs comerciales (`http://localhost:11434`).
- **Guardrails:** system prompt versionado en `prompts/system_guardrails.md` + mitigacion `--refuerzo` (V2) en el prompt de usuario.
- **Schemas de Entrega 2:** `docs/especificaciones/` (perfil-estudiante, recurso-semanal, feedback).

## Convenciones operativas

Flujo de issues, formato de commits y revision por par: [docs/entregas/README.md](docs/entregas/README.md).
