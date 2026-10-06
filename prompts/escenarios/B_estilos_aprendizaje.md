# Escenario B — Adaptación por estilo de aprendizaje (Sprint 3, Issue #6)

## Evento

**La MISMA deficiencia conceptual** (2.0/5.0 en Árboles binarios de búsqueda,
materia Estructuras de Datos No Lineales), con dos variantes de estilo:

- `poc_slm/eventos/B_visual.json` → `"estilo_aprendizaje": "visual"`
- `poc_slm/eventos/B_textual.json` → `"estilo_aprendizaje": "textual"`

## Salida esperada

- Visual → recomendación de diagramas, videos, mapas.
- Textual → recomendación de lecturas y análisis.

## Ejecución de la prueba

```bash
python poc_slm/recommender.py --escenario B_visual --refuerzo
python poc_slm/recommender.py --escenario B_textual --refuerzo
```

## Resultados lado a lado (2026-10-06, `qwen2.5:1.5b`)

| Aspecto | Visual | Textual |
|---|---|---|
| Evidencia | [B_visual.md](../salidas-respaldo/B_visual.md) | [B_textual.md](../salidas-respaldo/B_textual.md) |
| Recurso principal | Diagramas de árboles | Lectura / definiciones escritas |
| Otros recursos | Ejercicios resueltos, problemas con estructura | Ejercicios prácticos |
| Adaptación de la ruta | ✅ diagramas y ejercicios visuales paso a paso | ✅ repaso de definiciones y resolución escrita |

**Criterio de aceptación:** ⚠️ *Cumplido con observación*: las variantes son
**claramente diferenciadas** en la ruta de estudio y el recurso principal.
En la variante textual el modelo aún filtra **un recurso tipo diagrama**
(a pesar de la regla de exclusión) — limitación residual del 1.5B,
documentada en `prompts/README.md` junto con la mitigación (regla 5 del
`--refuerzo` ahora nombra dinámicamente el estilo del evento, lo que mejoró
notablemente la diferenciación).

## Salidas lado a lado listas para la demostración

Las respaldos pre-generados están en `prompts/salidas-respaldo/B_visual.md` y
`prompts/salidas-respaldo/B_textual.md`.
