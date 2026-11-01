# Perfiles de estudiante

Esta carpeta guarda ejemplos y fixtures del perfil consolidado del estudiante.

- Schema: `docs/especificaciones/perfil-estudiante.schema.json`
- Validador: `docs/especificaciones/validar-perfiles.py`
- Fixtures (todos `origen: "simulado"`):

| Archivo | Perfil | Recurso esperado (E2-08, referencia de evaluacion) |
|---|---|---|
| `ejemplo-perfil-estudiante.json` | activo + intuitivo + visual, alta metodicidad | A o C (perfil mixto; se evalua la justificacion) |
| `ejemplo-perfil-textual.json` | reflexivo + verbal + secuencial, alta apertura | B |
| `ejemplo-perfil-kinestesico.json` | activo + sensorial + secuencial, alta metodicidad | C |

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

> **Entrega 3:** el contrato vigente usa los **puntajes brutos originales** de cada instrumento (`0-14`, `0-11` y `0-9`) y no la escala 1.0-5.0. Los perfiles reales solo se procesan en local y no se versionan. Ver [lineamientos de datos psicometricos](../docs/entregas/entrega-3-interpretacion-psicometrica/lineamientos-datos-psicometricos.md).

## Contrato de puntajes brutos (E3-04, vigente)

- Schema: `docs/especificaciones/perfil-bruto-psicometrico.schema.json`
- Baremos: `docs/especificaciones/baremos-psicometricos.md`
- Validador: `docs/especificaciones/validar-perfiles-brutos.py`
- Fixtures en `perfiles/brutos/` (todos `origen: "sintetico"`):

| Archivo | Caso que ilustra |
|---|---|
| `ejemplo-perfil-bruto-dominante.json` | Preferencias marcadas en los cuatro ejes y area CHASIDE con afinidad alta |
| `ejemplo-perfil-bruto-brecha.json` | Interes alto con aptitud baja; sirve para el guardrail de no convertir la brecha en etiqueta |
| `ejemplo-perfil-bruto-plano.json` | Diferencias minimas en todos los polos; el texto no debe personalizar |

Ruta: `perfiles/brutos/`. Se validan con `python docs/especificaciones/validar-perfiles-brutos.py`.

Cambios frente a Entrega 2:

| Aspecto | Entrega 2 | Entrega 3 |
|---|---|---|
| Puntajes | `1.0` a `5.0` normalizado | Enteros nativos (`0-14`, `0-11`, `0-9`) |
| `autonomia` | Indice derivado | Prohibida |
| `origen` de fixtures | `"simulado"` | `"sintetico"` |

Los fixtures de Entrega 2 (`ejemplo-perfil-estudiante.json` y compania) se
conservan como evidencia: siguen validando con `validar-perfiles.py` y **no**
pasan el contrato bruto, a proposito.

## Escala unica 1.0 - 5.0 (historico Entrega 2)

En la Entrega 2, todos los puntajes numericos del perfil (`estilos_aprendizaje.puntajes`, `personalidad.rasgos`, `chaside.areas`) usaban **escala 1.0 a 5.0**, con 3.0 como punto neutro. La conversion desde los conteos crudos de cada bloque esta documentada en `docs/especificaciones/escala-canonica.md`.

**Resumen de formulas:**

| Bloque | Entrada | Formula |
| :--- | :--- | :--- |
| Estilos (Felder) | 2 conteos, 11 items/polo | `round(3 + 2*(der - izq)/11, 1)` |
| Personalidad | 2 conteos, 9 items/polo | `round(3 + 2*(der - izq)/9, 1)` |
| CHASIDE | total 0-14 (pct_total 0-100) | `round(1 + 4*total/14, 1)` |

El validador `docs/especificaciones/validar-perfiles.py` rechaza valores fuera del conjunto alcanzable por cada formula.
