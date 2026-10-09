# Escenario B — Adaptacion por estilo de aprendizaje (Sprint 3, Issue #6)

## Evento

**La MISMA deficiencia conceptual** (2.0/5.0 en Arboles binarios de busqueda,
materia Estructuras de Datos No Lineales), con dos variantes de estilo:

- `poc_slm/eventos/B_visual.json` → `"estilo_aprendizaje": "visual"`
- `poc_slm/eventos/B_textual.json` → `"estilo_aprendizaje": "textual"`

## Salida esperada

- Visual → recomendacion de diagramas, videos, mapas.
- Textual → recomendacion de lecturas y analisis.

## Ejecucion de la prueba

```bash
python poc_slm/recommender.py --escenario B_visual --refuerzo
python poc_slm/recommender.py --escenario B_textual --refuerzo
```

## Resultados lado a lado (2026-10-06, `qwen2.5:1.5b`)

| Aspecto | Visual | Textual |
|---|---|---|
| Evidencia | [B_visual.md](../salidas-respaldo/B_visual.md) | [B_textual.md](../salidas-respaldo/B_textual.md) |
| Recurso principal | Diagramas de arboles | Lectura / definiciones escritas |
| Otros recursos | Ejercicios resueltos, problemas con estructura | Ejercicios practicos |
| Adaptacion de la ruta | ✅ diagramas y ejercicios visuales paso a paso | ✅ repaso de definiciones y resolucion escrita |

**Criterio de aceptacion:** ⚠️ *Cumplido con observacion*: las variantes son
**claramente diferenciadas** en la ruta de estudio y el recurso principal.
En la variante textual el modelo aun filtra **un recurso tipo diagrama**
(a pesar de la regla de exclusion) — limitacion residual del 1.5B,
documentada en `prompts/README.md` junto con la mitigacion (regla 5 del
`--refuerzo` ahora nombra dinamicamente el estilo del evento, lo que mejoro
notablemente la diferenciacion).

## Salidas lado a lado listas para la demostracion

Las respaldos pre-generados estan en `prompts/salidas-respaldo/B_visual.md` y
`prompts/salidas-respaldo/B_textual.md`.
