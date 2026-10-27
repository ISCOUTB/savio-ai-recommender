# prompts — Guardrails y escenarios de demostracion

Coleccion versionada de system prompts, escenarios de la PoC y pruebas adversariales.

> 📌 Documentacion del sprint: [docs/entregas/entrega-1-poc-funcional/sprint-3-prompts-guardrails.md](../docs/entregas/entrega-1-poc-funcional/sprint-3-prompts-guardrails.md)

## Contenido (Sprint 3 — Entrega 1)

```
prompts/
├── system_guardrails.md        ← System prompt con las 4 reglas de seguridad
├── escenarios/
│   ├── A_bajo_desempeno.md     ← Tutoria reactiva ante nota baja
│   └── B_estilos_aprendizaje.md ← Adaptacion visual vs. textual
├── pruebas-adversariales.md    ← Ataques de prueba y resultados reales
├── salidas-respaldo/           ← Respuestas pre-generadas (plan B de la demo)
└── README.md
```

## Contenido (Entrega 2 - personalizacion semanal)

| Archivo | Que contiene |
|---|---|
| [system_prompt_recomendacion.md](system_prompt_recomendacion.md) | Prompt de recomendacion semanal (E2-10): 5 reglas y formato fijo de tres secciones |
| [escenarios/personalizacion_semanal.md](escenarios/personalizacion_semanal.md) | Evidencia de E2-10: 3 perfiles, prueba adversarial y control de orden |

El system prompt de Entrega 2 es distinto del de tutoria: no redacta una clase,
elige uno de los recursos A/B/C de la semana y justifica el descarte. Se carga en
runtime desde `poc_slm/prompt_builder.py`.

## Las 4 reglas de guardrails

1. Solo temas de la materia — redirigir ante off-topic.
2. Nunca soluciones completas de tareas — solo guias metodologicas.
3. Tono empatico, formativo, no punitivo.
4. Salida estructurada (Markdown con esquema fijo).

## Hallazgos tecnicos

Documentados durante el Sprint 3 con `qwen2.5:1.5b` (2026-10-06):

1. **Los SLMs de 1.5B–2B si tienden a ignorar el system prompt** (nota
   tecnica del issue #4 confirmada). Comparacion V1 (reglas solo en system
   prompt) vs V2 (reglas criticas repetidas en el prompt de usuario con
   `--refuerzo`) sobre el mismo evento:
   - **V1:** encabezados con formato equivocado (`###` en vez de `##`),
     **URLs inventadas** (`example.com`) y codigo cortado a mitad.
   - **V2:** estructura `##` exacta, sin URLs, guia metodologica limpia.
   - **Conclusion:** el refuerzo en el prompt de usuario mejora notablemente
     el cumplimiento de las reglas. `recommender.py` incluye la bandera
     `--refuerzo` para alternar ambos comportamientos en la demo.
2. **La regla 5 del refuerzo debe nombrar el estilo del evento**
   ("ESTE ESTUDIANTE ES DE ESTILO 'textual'"): con la regla generica, el
   modelo recomendaba diagramas incluso en la variante textual; al nombrar el
   estilo dinamicamente, la diferenciacion visual/textual mejora claramente.
3. **Efecto eco:** ocasionalmente el modelo repite literalmente frases del
   refuerzo dentro de la respuesta ("recuerda que no debes incluir URLs").
   Cosmetico; aceptable para la PoC.
4. **Alucinaciones residuales:** incluso con refuerzo, el 1.5B a veces
   inventa URLs (ataque 1, ejec. 1) o citas de libros (ataque 2, ejec. 2), y
   mostro una contradiccion ("nota baja... es media") en una ejecucion.
   Mitigaciones aplicadas: regla anti-alucinacion + interpretacion explicita
   de la escala (2.0/5 = baja) + limite por seccion. Mitigacion futura:
   modelo ≥3B o few-shot en el prompt.
5. **Limite de longitud:** la instruccion pide max. 300 palabras y el codigo
   aplica tope duro `num_predict: 600` (el espanol gasta ~2 tokens por
   palabra y las 4 secciones no cabian en 300 tokens). El tope garantiza
   salidas acotadas y comparables para el benchmark (#8).
