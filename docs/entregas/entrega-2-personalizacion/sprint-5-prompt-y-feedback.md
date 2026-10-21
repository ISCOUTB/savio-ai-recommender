# Entrega 2 - Sprint 5: Prompt builder y feedback

**Estado:** Pendiente
**Issues:** E2-10, E2-11

## Objetivo

Disenar el prompt que combina perfil del estudiante y recursos A/B/C, y definir como se mide si la recomendacion acerto.

## Reglas del prompt

- Entrada: `perfil-estudiante.schema.json` + lista de recursos de la semana.
- Salida: recurso recomendado, justificacion breve y razon de descarte de los otros recursos.
- Guardrails: no inventar recursos, no inventar datos del estudiante, no afirmar certeza clinica o psicologica.

## Feedback

- Escala minima: util si/no.
- Escala opcional: Likert corta de 1 a 5.
- Registro: acierto o descache por recomendacion.

## Criterios de aceptacion

- [ ] Prompt template documentado.
- [ ] 3 ejemplos de entrada y salida esperada.
- [ ] `feedback.schema.json` valido.
- [ ] KPI base definido: tasa de acierto y tasa de descache.
