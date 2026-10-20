# Perfiles de estudiante

Esta carpeta guarda ejemplos y fixtures del perfil consolidado del estudiante.

- Schema: `docs/especificaciones/perfil-estudiante.schema.json`
- Ejemplo valido: `ejemplo-perfil-estudiante.json`

Regla: mientras Moodle local no este listo, se pueden usar perfiles simulados del equipo, marcados como simulados, para avanzar en Prompt Builder y destilacion.

**Campo `origen` (obligatorio):**
- `real`: perfil generado a partir de tests diligenciados en Moodle.
- `simulado`: perfil de ejemplo o fixture para pruebas tecnicas.

En este repositorio **solo se versionan perfiles con `origen: "simulado"`**. Los perfiles reales viven fuera del control de versiones por politica de datos.

**Perfiles reales (E2-07):** se generan con

```bash
python docs/especificaciones/generar-perfil.py --usuario persona-1
```

El script lee las respuestas desde Moodle (Docker), aplica las formulas y escribe en `perfiles/reales/<usuario>.json`. Esa carpeta esta en `.gitignore`: no se versiona.

---

## Escala unica 1.0 - 5.0

Todos los puntajes numericos del perfil (`estilos_aprendizaje.puntajes`, `personalidad.rasgos`, `chaside.areas`) usan **escala 1.0 a 5.0**, con 3.0 como punto neutro. La conversion desde los conteos crudos de cada bloque esta documentada en `docs/especificaciones/escala-canonica.md`.

**Resumen de formulas:**

| Bloque | Entrada | Formula |
| :--- | :--- | :--- |
| Estilos (Felder) | 2 conteos, 11 items/polo | `round(3 + 2*(der - izq)/11, 1)` |
| Personalidad | 2 conteos, 9 items/polo | `round(3 + 2*(der - izq)/9, 1)` |
| CHASIDE | total 0-14 (pct_total 0-100) | `round(1 + 4*total/14, 1)` |

El validador `docs/especificaciones/validar-perfiles.py` rechaza valores fuera del conjunto alcanzable por cada formula.
