# Entrega 2 - Sprint 4: Nucleo de destilacion y fine-tuning

**Estado:** Completado (el ajuste E2-19/E2-20 se ejecuta post-entrega)
**Issues:** E2-09 (E2-19 y E2-20 se ejecutan post-entrega)

## Objetivo

Investigar y proponer como llevar un modelo abierto de ~1.5B/2B a un SLM objetivo cercano a ~0.5B, especializado en la materia piloto y en interpretacion psicopedagogica.

## Enfoque

- Teacher: modelo mayor de referencia.
- Student: modelo liviano objetivo.
- Tecnicas a evaluar: poda de capas, destilacion teacher-student, LoRA/QLoRA de especializacion, cuantizacion.
- Doble dominio:
  - A: contenido de la materia piloto.
  - B: reglas psicopedagogicas para mapear perfil a recurso didactico.

## Criterios de aceptacion

- [x] Comparativa de modelos candidatos con RAM estimada, latencia y licencia (Seccion 4 propuesta-destilacion-slm.md).
- [x] Decision de pipeline: destilacion de datos + QLoRA 4-bit + Q4_K_M (Seccion 7).
- [x] Plan de dataset: esquemas JSONL completos Dataset A (materia) y Dataset B (psicopedagogico) con muestras (Secciones 8, 9).
- [x] Riesgos documentados: matriz 10 riesgos + protocolo guardrails 12 pruebas (Secciones 10, 11).
- [x] Metricas definidas: sistema (RAM, tok/s, latencia, concurrencia) + calidad (acierto, guardrails, fidelidad, consistencia) (Seccion 12).
