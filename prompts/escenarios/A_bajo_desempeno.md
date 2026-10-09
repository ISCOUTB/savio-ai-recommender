# Escenario A — Tutoria reactiva ante nota baja (Sprint 3, Issue #5)

## Evento

`poc_slm/eventos/A_nota_baja.json`: estudiante con **2.0/5.0** en el parcial de
**Estructuras de Datos No Lineales** (tema: Arboles AVL), estilo visual.

```json
{
  "estudiante": "Estudiante Demo",
  "materia": "Estructuras de Datos No Lineales",
  "tema": "Arboles AVL",
  "calificacion": 2.0,
  "escala": "0-5",
  "estilo_aprendizaje": "visual"
}
```

## Salida esperada

Mensaje empatico (no punitivo) + identificacion del tema debil + ruta de
estudio paso a paso, siguiendo el esquema fijo:
Diagnostico → Ruta de estudio → Recursos → Cierre motivacional.

## Ejecucion de la prueba

```bash
python poc_slm/recommender.py --escenario A_nota_baja --refuerzo
```

## Resultados (2026-10-06, `qwen2.5:1.5b`, 3 ejecuciones consecutivas)

| Ejecucion | Estructura 4 secciones | Nota leida como "baja" | Tono empatico | Sin soluciones de tareas | Latencia | Evidencia |
|---|---|---|---|---|---|---|
| 1 | ✅ | ✅ "indica una baja calificacion" | ✅ | ✅ | 43.0 s | [A_nota_baja_ejec1.md](../salidas-respaldo/A_nota_baja_ejec1.md) |
| 2 | ✅ | ✅ "calificacion baja (2.0 en una escala de 0-5)" | ✅ | ✅ | 31.4 s | [A_nota_baja_ejec2.md](../salidas-respaldo/A_nota_baja_ejec2.md) |
| 3 | ✅ | ✅ "dificultades significativas" | ✅ | ✅ | 29.5 s | [A_nota_baja_ejec3.md](../salidas-respaldo/A_nota_baja_ejec3.md) |

**Criterio de aceptacion:** ✅ 3/3 ejecuciones con calidad consistente y
salidas de respaldo pre-generadas en `prompts/salidas-respaldo/`.

### Observaciones

- La regla de interpretacion de la escala corrige la alucinacion del Sprint 2
  ("rendimiento mediano" ya no aparece).
- La ejecucion 1 muestra el "efecto eco": el modelo repite literalmente la
  frase del refuerzo ("recuerda que no debes incluir URLs") dentro de la
  seccion de recursos. Cosmetico; documentado en `prompts/README.md`.
