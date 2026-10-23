# Entrega 2 - Sprint 2: Perfil JSON y tests

**Estado:** En curso
**Issues:** E2-04, E2-05, E2-06, E2-07, E2-17, E2-18
**Pendiente:** E2-17 (confirmar instrumento con la docente) y E2-18 (tests de persona-2 y persona-3)

## Objetivo

Convertir los tres instrumentos psicopedagogicos en un schema JSON unico, simple y consumible por el Prompt Builder.

## Trabajo por integrante

- Persona 1: Estilos de Aprendizaje. Investigar bloque de Moodle y metricas numericas. Salida: campos para preferencia visual, auditiva, kinestesica o modelo equivalente.
- Persona 2: Personalidad. Investigar rasgos conductuales y como influyen en el consumo de recursos.
- Persona 3: CHASIDE. Mapear areas vocacionales C, H, A, S, I, D, E y su uso para analogias dentro de la materia.

## Criterios de aceptacion

- [x] Cada integrante entrega nota tecnica breve de su instrumento.
- [x] `perfil-estudiante.schema.json` consolidado.
- [x] `perfiles/ejemplo-perfil-estudiante.json` valida contra el schema.
- [x] El JSON evita anidacion profunda y queda listo para inyectar en prompt.

> Evidencia: `docs/especificaciones/instrumento-*.md`, el schema y
> `python docs/especificaciones/validar-perfiles.py`.
