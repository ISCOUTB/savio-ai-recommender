# Entrega 2 - Sprint 5: Prompt builder y feedback

**Estado:** En curso
**Issues:** E2-10, E2-11

## Objetivo

Disenar el prompt que combina perfil del estudiante y recursos A/B/C, y definir como se mide si la recomendacion acerto.

## Reglas del prompt

- Entrada: `perfil-estudiante.schema.json` + lista de recursos de la semana.
- Salida: recurso recomendado, justificacion breve y razon de descarte de los otros recursos.
- Guardrails: no inventar recursos, no inventar datos del estudiante, no afirmar certeza clinica o psicologica.

## Implementacion (E2-10)

- System prompt: `prompts/system_prompt_recomendacion.md` (5 reglas y formato de tres secciones).
- Script: `poc_slm/prompt_builder.py` (valida entradas, ensambla el prompt, llama a Ollama, parsea y valida la salida).
- Refuerzo V2: `--refuerzo` repite las reglas criticas en el prompt de usuario.
- Fixtures de perfil: `perfiles/ejemplo-perfil-textual.json` y `perfiles/ejemplo-perfil-kinestesico.json`.
- Chequeos sin Ollama: `python poc_slm/test_prompt_builder.py`.
- Evidencia: `prompts/escenarios/personalizacion_semanal.md` (3 perfiles, prueba adversarial y control de orden).

## Feedback

- Escala minima: util si/no.
- Escala opcional: Likert corta de 1 a 5.
- Registro: acierto o descache por recomendacion.

## Criterios de aceptacion

- [x] Prompt template documentado.
- [x] 3 ejemplos de entrada y salida esperada.
- [ ] `feedback.schema.json` valido.
- [ ] KPI base definido: tasa de acierto y tasa de descache.
