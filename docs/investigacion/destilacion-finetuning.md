# Destilacion y fine-tuning

Este es el nucleo tecnico de Entrega 2.

## Pregunta de investigacion

Como reducir un SLM abierto hacia un modelo objetivo cercano a 0.5B y aun asi recomendar bien recursos A/B/C para una materia piloto usando el perfil psicopedagogico del estudiante.

## Justificacion

- Pesos del modelo: incluso 1.5B/2B ocupan GB relevantes en RAM o VRAM.
- KV cache: con usuarios concurrentes, la memoria escala por peticion activa.
- Latencia: la recomendacion debe sentirse usable dentro de la semana academica.

## Pipeline candidato

1. Elegir teacher: modelo mayor con buena calidad pedagogica.
2. Elegir student: modelo liviano objetivo.
3. Construir dataset A: contenido de la materia piloto.
4. Construir dataset B: ejemplos de mapeo perfil = recurso recomendado + justificacion.
5. Probar en orden simple:
   - baseline student sin ajuste;
   - prompting mejorado;
   - fine-tuning ligero LoRA/QLoRA si es viable;
   - destilacion/poda si el hardware y tiempo lo permiten.
6. Medir: RAM, tokens/s, latencia, calidad, guardrails y tasa de acierto.

## Subchecklist tecnico

- [ ] Definir teacher y student.
- [ ] Definir materia piloto y dataset A.
- [ ] Definir ejemplos psicopedagogicos dataset B.
- [ ] Definir formato de salida JSON o Markdown estricto.
- [ ] Definir evaluacion ciega minima entre recursos.
- [ ] Documentar licencias.
- [ ] Documentar limites: no consejo clinico, no certeza psicologica, no inventar recursos.

## Advertencia

No intentar destilar todo el conocimiento general. El objetivo es transferir la capacidad de decidir entre recursos de una materia usando el perfil del estudiante.
