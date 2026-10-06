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

Documentados durante el Sprint 3 con `qwen2.5:1.5b` (2026-10-06):

1. **Los SLMs de 1.5B–2B sí tienden a ignorar el system prompt** (nota
   técnica del issue #4 confirmada). Comparación V1 (reglas solo en system
   prompt) vs V2 (reglas críticas repetidas en el prompt de usuario con
   `--refuerzo`) sobre el mismo evento:
   - **V1:** encabezados con formato equivocado (`###` en vez de `##`),
     **URLs inventadas** (`example.com`) y código cortado a mitad.
   - **V2:** estructura `##` exacta, sin URLs, guía metodológica limpia.
   - **Conclusión:** el refuerzo en el prompt de usuario mejora notablemente
     el cumplimiento de las reglas. `recommender.py` incluye la bandera
     `--refuerzo` para alternar ambos comportamientos en la demo.
2. **La regla 5 del refuerzo debe nombrar el estilo del evento**
   ("ESTE ESTUDIANTE ES DE ESTILO 'textual'"): con la regla genérica, el
   modelo recomendaba diagramas incluso en la variante textual; al nombrar el
   estilo dinámicamente, la diferenciación visual/textual mejora claramente.
3. **Efecto eco:** ocasionalmente el modelo repite literalmente frases del
   refuerzo dentro de la respuesta ("recuerda que no debes incluir URLs").
   Cosmético; aceptable para la PoC.
4. **Alucinaciones residuales:** incluso con refuerzo, el 1.5B a veces
   inventa URLs (ataque 1, ejec. 1) o citas de libros (ataque 2, ejec. 2), y
   mostró una contradicción ("nota baja... es media") en una ejecución.
   Mitigaciones aplicadas: regla anti-alucinación + interpretación explícita
   de la escala (2.0/5 = baja) + límite por sección. Mitigación futura:
   modelo ≥3B o few-shot en el prompt.
5. **Límite de longitud:** la instrucción pide máx. 300 palabras y el código
   aplica tope duro `num_predict: 600` (el español gasta ~2 tokens por
   palabra y las 4 secciones no cabían en 300 tokens). El tope garantiza
   salidas acotadas y comparables para el benchmark (#8).
