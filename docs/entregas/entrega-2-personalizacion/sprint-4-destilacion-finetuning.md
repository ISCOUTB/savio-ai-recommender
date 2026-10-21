# Entrega 2 - Sprint 4: Nucleo de destilacion y fine-tuning

**Estado:** Pendiente
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

- [ ] Comparativa de modelos candidatos con RAM estimada, latencia y licencia.
- [ ] Decision de pipeline: poda, destilacion, fine-tuning o combinacion.
- [ ] Plan de dataset: materia piloto + ejemplos de mapeo perfil-recurso.
- [ ] Riesgos documentados: perdida de guardrails, sobreajuste, licencias y hardware.
- [ ] Metricas definidas: RAM, tokens/s, latencia, calidad pedagogica y tasa de acierto.
