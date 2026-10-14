# Nota Tecnica: Instrumento de Estilos de Aprendizaje (E2-04)

- **Identificador:** E2-04
- **Modulo:** Perfilamiento psicopedagogico (`perfil.estilos_aprendizaje`)
- **Depende de:** `docs/especificaciones/perfil-estudiante.schema.json` (E2-01)
- **Desbloquea:** E2-07, E2-10

---

## 1. Marco teorico y pertinencia en educacion superior

### 1.1 Fundamentacion del modelo (VARK + Felder-Silverman)

Para el subsistema de recomendacion academica en entornos universitarios (Moodle / SAVIO), se adopta la taxonomia sensorial **VARK (Fleming y Mills, 1992)**, registrada en el esquema bajo el valor `"vak"`, combinada con el enfoque de **intensidad gradual de preferencia de Felder-Silverman (1988)**:

1. **Canales de representacion (Fleming):** divide la recepcion y procesamiento de informacion academica en cuatro dimensiones conectadas directamente con los formatos de recursos disponibles en cursos universitarios:
   - **Visual (`visual`):** procesamiento mediante relaciones espaciales, diagramacion, esquemas y simbologia grafica.
   - **Lectura/Escritura (`lectura_escritura`):** procesamiento mediante texto estructurado, analisis documental, sintesis escrita y definiciones formales.
   - **Auditivo (`auditivo`):** procesamiento mediante discurso hablado, explicacion dialogada, debate y secuencias sonoras.
   - **Kinestesico (`kinestesico`):** procesamiento mediante experimentacion practica, simulacion interactiva, resolucion de casos reales y aprendizaje basado en problemas.

2. **Continuidad e intensidad de preferencia (Felder-Silverman):** relevante en educacion superior e ingenieria, establece que los estilos no son cajas cerradas sino espectros de afinidad. Un estudiante puede presentar una preferencia marcada por un canal (perfil unimodal) o una combinacion equilibrada de varios canales (perfil multimodal o `mixto`).

### 1.2 Criterio de uso pedagogico (razonamiento in-context vs. reglas rigidas)

El sistema evita el determinismo de encasillar al estudiante con reglas rigidas (ej. `si visual -> solo mostrar video`). En su lugar, las metricas de los 4 canales se convierten en una **directriz psicopedagogica en lenguaje natural (`descripcion_para_prompt`)** para que el SLM razone *in-context* que formatos priorizar y cuales evitar de forma aislada. Este criterio es coherente con la mitigacion V2 ya aplicada en la PoC (`--refuerzo`), donde la regla 5 del refuerzo nombra dinamicamente el estilo del estudiante (ver seccion 6).

---

## 2. Estructura numerica y contrato de datos

El bloque `estilos_aprendizaje` se alinea con `docs/especificaciones/perfil-estudiante.schema.json` (E2-01).

### 2.1 Definicion de campos (`perfil.estilos_aprendizaje`)

| Campo | Tipo JSON | Requerido | Rango / valores permitidos | Descripcion tecnica |
| :--- | :--- | :---: | :--- | :--- |
| `modelo` | `string` | Si (schema) | `"vak"`, `"felder_silverman"`, `"kolb"`, `"otro"` | Marco psicopedagogico utilizado (valor estandar del instrumento: `"vak"`). |
| `dominante` | `string` | Si (schema) | `"visual"`, `"auditivo"`, `"kinestesico"`, `"lectura_escritura"`, `"mixto"` | Estilo principal calculado a partir de los puntajes (regla 2.2). |
| `puntajes` | `object` | Si (convencion del instrumento) | Objeto con 4 claves numericas (`1.0` a `5.0`) | Calificaciones obtenidas en cada canal de aprendizaje. |
| `puntajes.visual` | `number` | Si (convencion) | `1.0` a `5.0` | Afinidad por recursos graficos y esquematicos. |
| `puntajes.auditivo` | `number` | Si (convencion) | `1.0` a `5.0` | Afinidad por recursos hablados y dialogicos. |
| `puntajes.kinestesico` | `number` | Si (convencion) | `1.0` a `5.0` | Afinidad por recursos practicos e interactivos. |
| `puntajes.lectura_escritura` | `number` | Si (convencion) | `1.0` a `5.0` | Afinidad por recursos textuales y analiticos. |
| `descripcion_para_prompt` | `string` | Si (convencion del instrumento) | Cadena de texto (2 a 3 oraciones) | Sintesis accionable inyectada en el prompt del SLM (seccion 4). |

**Nota sobre el contrato:** el schema JSON marca como requeridos solo `modelo` y `dominante`; este instrumento declara `puntajes` y `descripcion_para_prompt` como **requeridos por convencion** (el schema admite ambos campos de forma opcional). La discrepancia se resuelve a favor del schema (no se modifica en este issue); endurecer el schema queda propuesto como trabajo posterior si el equipo lo decide.

### 2.2 Escala de calificacion (1.0 a 5.0) y calculo del estilo `dominante`

1. **Interpretacion de la escala (1 a 5):**
   - Afinidad alta: `4.0` a `5.0`
   - Afinidad moderada: `2.5` a `3.9`
   - Afinidad baja: `1.0` a `2.4`

2. **Regla de calculo para el campo `dominante` (umbral delta = 0.5):**
   Se ordenan los 4 puntajes del estudiante de mayor a menor (P1 >= P2 >= P3 >= P4):
   - **Estilo unico dominante:** si la diferencia entre el puntaje mas alto (P1) y el segundo mas alto (P2) es **mayor o igual a 0.5 puntos** (P1 - P2 >= 0.5), el campo `dominante` toma el nombre del canal P1.
   - **Estilo mixto (`"mixto"`):** si la diferencia entre el primero y el segundo es **menor a 0.5 puntos** (P1 - P2 < 0.5), existe empate tecnico o co-dominancia y el campo `dominante` se asigna como `"mixto"`.

### 2.3 Nota de compatibilidad con el perfil de ejemplo existente

El archivo `perfiles/ejemplo-perfil-estudiante.json` (E2-01) es **anterior a este instrumento** y registra `puntajes` en escala 0-10 (`visual: 8`, `kinestesico: 6`, etc.). Este instrumento define la escala canonica **1.0 a 5.0**. Se propone un issue de seguimiento para re-escalar el ejemplo (dividir entre 2) y armonizar tambien `personalidad.rasgos` y `chaside.areas`, que siguen en 0-10. **No se modifica ese archivo en el alcance de E2-04.**

---

## 3. Mapeo de estilos a formatos didacticos

Reglas formalizadas de inclusion (formatos a privilegiar) y exclusion (formatos a evitar sin apoyo) por cada canal:

| Estilo / canal | Formatos didacticos a privilegiar (inclusion) | Formatos a evitar en aislamiento (exclusion) |
| :--- | :--- | :--- |
| `visual` | Diagramas de flujo, infografias, mapas conceptuales y videos esquematicos. | Lecturas densas y extensas sin apoyo grafico. |
| `lectura_escritura` | Articulos analiticos, resumenes estructurados, definiciones formales y glosarios. | Diagramas excesivamente recargados sin contexto textual. |
| `auditivo` | Podcasts, notas de voz, debates y explicaciones dialogadas. | Bloques extensos de texto estatico sin apoyo verbal o explicativo. |
| `kinestesico` | Ejercicios interactivos, analisis de casos practicos, laboratorios y simulaciones. | Teoria abstracta prolongada sin aplicacion practica inmediata. |

---

## 4. Generador de texto para el prompt (`descripcion_para_prompt`)

Para transformar los valores de `puntajes` en una directriz *in-context* para el SLM, se ordenan los canales de mayor a menor (C1, C2, C3, C4 con puntajes P1 >= P2 >= P3 >= P4) y se aplica la regla de sintesis correspondiente:

### 4.1 Plantilla para perfil con dominante claro (`dominante != "mixto"`)

> `"Estudiante con estilo de aprendizaje predominantemente {C1} ({P1}/5), apoyado por afinidad {C2} ({P2}/5). Privilegiar {formatos_inclusion_C1} complementados con {formatos_inclusion_C2}. Evitar {formatos_exclusion_C1} o depender unicamente de recursos del canal {C4} ({P4}/5)."`

### 4.2 Plantilla para perfil mixto (`dominante == "mixto"`)

> `"Estudiante con estilo de aprendizaje mixto, con alta afinidad en los canales {C1} ({P1}/5) y {C2} ({P2}/5). Combinar equilibradamente {formatos_inclusion_C1} con {formatos_inclusion_C2}. Evitar {formatos_exclusion_C1} y {formatos_exclusion_C2} presentados de forma aislada."`

Restricciones del campo: 2 a 3 oraciones, en tercera persona, sin recomendaciones concretas de materia (eso es tarea del SLM con el evento academico), y siempre derivado de la tabla de la seccion 3.

---

## 5. Ejemplos validados (perfiles contrastantes)

Ambos ejemplos fueron validados contra `docs/especificaciones/perfil-estudiante.schema.json` (draft-07) y cumplen la regla de calculo del dominante en escala 1.0 a 5.0.

### 5.1 Ejemplo 1: perfil fuertemente visual (dominante claro)

- **Puntajes:** `visual: 4.8`, `kinestesico: 3.5`, `lectura_escritura: 2.5`, `auditivo: 1.5`.
- **Verificacion de la regla:** 4.8 - 3.5 = 1.3 >= 0.5 → `dominante: "visual"`.

```json
{
  "estilos_aprendizaje": {
    "modelo": "vak",
    "dominante": "visual",
    "puntajes": {
      "visual": 4.8,
      "auditivo": 1.5,
      "kinestesico": 3.5,
      "lectura_escritura": 2.5
    },
    "descripcion_para_prompt": "Estudiante con estilo de aprendizaje predominantemente visual (4.8/5), apoyado por afinidad kinestesica (3.5/5). Privilegiar diagramas de flujo, infografias, mapas conceptuales y videos esquematicos complementados con ejercicios interactivos y analisis de casos practicos. Evitar lecturas densas sin apoyo grafico o depender unicamente de recursos del canal auditivo (1.5/5)."
  }
}
```

### 5.2 Ejemplo 2: perfil equilibrado o multimodal (`mixto`)

- **Puntajes:** `lectura_escritura: 4.5`, `kinestesico: 4.3`, `visual: 3.2`, `auditivo: 2.0`.
- **Verificacion de la regla:** 4.5 - 4.3 = 0.2 < 0.5 → `dominante: "mixto"`.

```json
{
  "estilos_aprendizaje": {
    "modelo": "vak",
    "dominante": "mixto",
    "puntajes": {
      "visual": 3.2,
      "auditivo": 2.0,
      "kinestesico": 4.3,
      "lectura_escritura": 4.5
    },
    "descripcion_para_prompt": "Estudiante con estilo de aprendizaje mixto, con alta afinidad en los canales lectura_escritura (4.5/5) y kinestesico (4.3/5). Combinar equilibradamente articulos analiticos, resumenes estructurados y glosarios con ejercicios interactivos, analisis de casos practicos y simulaciones. Evitar diagramas recargados sin contexto textual y teoria abstracta prolongada sin aplicacion practica presentados de forma aislada."
  }
}
```

---

## 6. Acoplamiento con la PoC actual y preparacion para E2-07 / E2-10

Hoy la PoC (`poc_slm/recommender.py`) consume un campo plano `estilo_aprendizaje` por evento (`poc_slm/eventos/*.json`), con valores como `"visual"` o `"textual"`, y la regla 5 del refuerzo (`--refuerzo`) lo adapta dinamicamente en el prompt de usuario. Mapeo de equivalencia para la futura integracion:

| Valor actual en eventos PoC | Canal canonico del instrumento |
| :--- | :--- |
| `"visual"` | `"visual"` |
| `"textual"` | `"lectura_escritura"` |

En E2-07/E2-10, `descripcion_para_prompt` reemplazara a la frase fija actual de la regla 5: la regla dinamica pasara a inyectar esta sintesis (inclusion + exclusion por canal) en lugar de la correspondencia fija `visual -> diagramas/videos/mapas`. Este issue no modifica `recommender.py` ni los eventos; solo fija el contrato psicopedagogico.
