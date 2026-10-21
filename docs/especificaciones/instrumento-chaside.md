# Nota Tecnica: Instrumento CHASIDE de Intereses Vocacionales (E2-06)

- **Identificador:** E2-06
- **Modulo:** Perfilamiento psicopedagogico (`perfil.chaside`)
- **Depende de:** `docs/especificaciones/perfil-estudiante.schema.json` (E2-01)
- **Desbloquea:** E2-07, E2-10
- **Relacionado:** E2-03 (bloque instalado, ver `moodle/plugins.md`), `docs/especificaciones/escala-canonica.md` (escala 1.0 a 5.0), `docs/especificaciones/generar-perfil.py` (calculo implementado en E2-07)

---

## 1. Marco del instrumento y pertinencia en el proyecto

### 1.1 Que mide CHASIDE

CHASIDE es un cuestionario de orientacion vocacional de amplio uso en instituciones educativas de Latinoamerica (Tamayo Lopera et al., 2018). Se inscribe en la tradicion de los inventarios de intereses vocacionales, cuyo referente teorico mas citado es Holland (1997). La version instalada en el Moodle del proyecto es el bloque institucional `block_chaside` v2.0.4 (ISCOUTB, 2026), que aplica **98 items de respuesta si / no**: por cada area hay **10 items de intereses** (que le gusta hacer al estudiante) y **4 items de aptitudes** (en que se percibe habil), es decir, 70 items de intereses y 28 de aptitudes en total. El bloque reporta el Top 1 y Top 2 de areas, el desglose intereses / aptitudes y el porcentaje por area (`pct_total`).

El nombre es el acronimo de sus 7 areas. La segunda columna usa los nombres oficiales del bloque (`lang/es/block_chaside.php`), que son los que aparecen en `descripcion_para_analogias`:

| Codigo | Nombre oficial en el bloque | Que refleja un puntaje alto |
| :---: | :--- | :--- |
| `C` | Administrativa | Gusto por organizar, planificar, llevar registros, cuantificar y gestionar recursos. |
| `H` | Humanidades/Sociales/Juridicas | Interes por las personas, la comunicacion, la argumentacion, la historia y los problemas sociales. |
| `A` | Artistica | Sensibilidad estetica, creatividad, composicion visual, musical o narrativa. |
| `S` | Ciencias de la Salud | Interes por el cuidado, el diagnostico, el bienestar y el funcionamiento del cuerpo humano. |
| `I` | Ensenanzas Tecnicas | Gusto por disenar, construir, automatizar y entender como funcionan los sistemas. |
| `D` | Defensa y Seguridad | Interes por el liderazgo, la disciplina, el trabajo en equipo y los protocolos. |
| `E` | Ciencias Experimentales | Gusto por la investigacion, la experimentacion, la medicion y los datos. |

> **Sobre la autoria:** la autoria original del cuestionario CHASIDE no aparece documentada en las fuentes consultadas. Esta nota cita la version implementada en el bloque institucional (ISCOUTB, 2026) y un estudio empirico de su aplicacion en estudiantes universitarios colombianos (Tamayo Lopera et al., 2018).

### 1.2 Regla de oro pedagogica: CHASIDE solo guia analogias

En este proyecto CHASIDE **no** se usa para orientar la carrera del estudiante ni para decidir que aprende. Su unica funcion es indicar **que dominios de experiencia le resultan cercanos** al estudiante, para que el SLM elija metaforas, analogias y aplicaciones practicas que conecten la materia piloto con sus intereses. Esto apoya la dimension de **Relevancia** del modelo ARCS (Keller, 2010): las analogias funcionan cuando el dominio fuente es familiar para quien aprende (Gentner, 1983; Duit, 1991), y conectar el contenido con intereses previos favorece el desarrollo del interes por la materia (Hidi y Renninger, 2006).

| CHASIDE **SI** determina | CHASIDE **NO** determina |
| :--- | :--- |
| El dominio de las analogias y metaforas de la explicacion. | El contenido disciplinar de la materia ni el tema de la semana. |
| Los ejemplos de aplicacion practica que acompanan la recomendacion. | El nivel de dificultad del recurso. |
| El tono de la conexion motivacional ("esto se parece a..."). | La eleccion entre Recurso A, B o C (la deciden estilos de aprendizaje y personalidad). |

Consecuencia directa: si se eliminara el bloque `chaside` del perfil, el sistema debe seguir recomendando el **mismo recurso**; solo cambiarian los ejemplos con los que se explica.

La evidencia empirica refuerza esta restriccion: en una muestra de 216 estudiantes universitarios de primer semestre, la correspondencia entre la carrera cursada y el resultado de CHASIDE fue de 58.3 % en intereses y 44.4 % en aptitudes (Tamayo Lopera et al., 2018). Es una senal util de cercania, no una base para decisiones sobre el estudiante.

### 1.3 Guardrails eticos del instrumento

1. **Sin orientacion vocacional:** el SLM nunca sugiere cambiar de carrera ni afirma que el estudiante "es bueno para" un area ("deberias estudiar medicina" esta prohibido).
2. **Sin revelar puntajes:** los valores numericos de CHASIDE no se mencionan al estudiante; solo se usan las analogias.
3. **Sin estereotipos:** las analogias no se asocian a genero, origen ni condicion socioeconomica, y ningun area se presenta como superior a otra.
4. **Area `S` sin consejo clinico:** las analogias de salud usan procesos (diagnostico, tratamiento, seguimiento), nunca recomendaciones medicas.
5. **Area `D` sin violencia:** las analogias de defensa usan liderazgo, disciplina, trabajo en equipo y protocolos, nunca conflicto armado.
6. **Coherente con la Regla 3 de la PoC:** las analogias son empaticas y formativas; nunca se usan para senalar carencias del estudiante.

---

## 2. Estructura numerica y contrato de datos

El bloque `chaside` se alinea con `docs/especificaciones/perfil-estudiante.schema.json`, consolidado en E2-07. **Este issue no modifica el schema.**

### 2.1 Definicion de campos (`perfil.chaside`)

| Campo | Tipo JSON | Requerido | Rango / valores permitidos | Descripcion tecnica |
| :--- | :--- | :---: | :--- | :--- |
| `areas` | `object` | Si (schema) | Las 7 claves `C`, `H`, `A`, `S`, `I`, `D`, `E`, todas requeridas | Puntaje normalizado de cada area. El schema prohibe claves adicionales. |
| `areas.C` ... `areas.E` | `number` | Si (schema) | `1.0` a `5.0`, solo los 15 valores alcanzables (seccion 2.2) | Afinidad del estudiante con el area. |
| `areas_dominantes` | `array` de `string` | Si (convencion) | 2 elementos del enum `C`, `H`, `A`, `S`, `I`, `D`, `E`; lista vacia si el test esta incompleto | Top 2 del bloque, en orden (seccion 2.3). |
| `descripcion_para_analogias` | `string` | Si (convencion) | 1 oracion generada por plantilla (seccion 4) | Directriz en lenguaje natural inyectada en el prompt del SLM. |

**Nota sobre el contrato:** el schema exige `areas` con sus 7 claves y el rango 1.0 a 5.0; `validar-perfiles.py` ademas rechaza valores no alcanzables. `areas_dominantes` y `descripcion_para_analogias` son **requeridos por convencion**: `generar-perfil.py` siempre los produce, pero el schema los admite como opcionales.

### 2.2 Normalizacion a la escala canonica 1.0 a 5.0

CHASIDE hereda la convencion transversal de `escala-canonica.md`. Cada area suma un total de 0 a 14 respuestas "si" (10 de intereses + 4 de aptitudes) y el bloque ya entrega `pct_total = round(100 * total / 14, 1)`:

```text
puntaje = round(1 + 4 * pct_total / 100, 1)      equivalente a      round(1 + 4 * total / 14, 1)
```

Ejemplo: un estudiante que responde "si" a 12 de los 14 items de `I` obtiene `1 + 4 * 12/14 = 4.4`.

Como el total es entero, solo hay **15 valores alcanzables**:

```text
1.0, 1.3, 1.6, 1.9, 2.1, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.1, 4.4, 4.7, 5.0
```

Interpretacion para la redaccion de analogias:

- Afinidad alta: `4.1` a `5.0` (11 a 14 respuestas "si").
- Afinidad media: `2.7` a `3.9` (6 a 10). `3.0` (total 7) es un **interes medio real**, no un dato vacio (`escala-canonica.md`, seccion 4).
- Afinidad baja: `1.0` a `2.4` (0 a 5).

### 2.3 Regla de calculo de `areas_dominantes` (implementada en `generar-perfil.py`)

1. **Test completo:** `areas_dominantes` toma siempre las **dos primeras areas** del ordenamiento oficial del bloque (`facade.php`): mayor total; si empatan, mayor aptitud; si siguen empatadas, menor brecha entre intereses y aptitudes; y por ultimo, orden alfabetico.
2. **Test incompleto:** las 7 areas quedan en `3.0`, `areas_dominantes = []` y se usa la descripcion neutral de la seccion 4.
3. **Orden con significado:** la primera area es la principal. Cuando la segunda esta claramente por debajo (por ejemplo, `I: 4.4` frente a `E: 3.6`), el SLM debe preferir analogias de la primera y usar la segunda solo como apoyo.

> **Observacion para E2-10 (no implementada):** se podria omitir la segunda area cuando su puntaje este 2 o mas respuestas por debajo de la primera (diferencia >= 0.5 en la escala), para ahorrar tokens. Hoy el generador no lo hace y esta nota no lo exige.

---

## 3. Mapeo de areas a dominios de analogia

Cada area se traduce en un dominio de experiencia del que el SLM toma sus metaforas. La columna "Dominio" es el texto exacto que `generar-perfil.py` inserta en `descripcion_para_analogias` (`CONEXION_AREA`). Las columnas de ejemplo muestran el mismo tema explicado con analogias distintas, en la materia piloto propuesta (Taller de Escritura, E2-08) y en una materia de ingenieria (Estructuras de Datos, escenario de la Entrega 1).

| Area | Dominio (`CONEXION_AREA`) | Ejemplo en Taller de Escritura (ensayo argumentativo) | Ejemplo en ingenieria (arboles AVL) |
| :---: | :--- | :--- | :--- |
| `C` | organizacion, gestion y tareas administrativas | La tesis es el presupuesto del ensayo: cada parrafo "gasta" en un argumento y al final las cuentas deben cuadrar con la conclusion. | Rebalancear un AVL es como cuadrar un balance contable: si una columna pesa mas, se redistribuye hasta que la diferencia sea minima. |
| `H` | comunicacion, analisis social y textos | Escribir un ensayo es preparar un debate: anticipar al oponente (contraargumento) y responderle con evidencia. | Un AVL es como un comite que exige equilibrio de representacion: ningun lado puede tener dos votos mas que el otro. |
| `A` | creacion, diseno y expresion | El ensayo tiene composicion como una pintura: un punto focal (tesis) y elementos que guian la mirada hacia el. | El factor de balance funciona como la simetria de una composicion: si un lado pesa mas, la obra se "cae" y hay que recomponerla. |
| `S` | cuidado de personas y practicas de salud | Revisar un borrador es como un diagnostico: identificar sintomas (ideas sueltas) antes de aplicar el tratamiento (reescritura). | Cada insercion es un chequeo de signos vitales: se mide el balance en cada nodo y, si se sale del rango, se aplica una rotacion correctiva. |
| `I` | procesos tecnicos, sistemas y resolucion de problemas | La estructura del ensayo es una arquitectura de software: la tesis es la interfaz y cada argumento un modulo que la implementa y se prueba con evidencia. | Un AVL es un sistema autorregulado: como un controlador que corrige el error cada vez que el sistema se desvia del punto de equilibrio. |
| `D` | liderazgo, disciplina y trabajo en equipo | El ensayo es como coordinar un equipo: la tesis es el objetivo comun y cada parrafo cumple un rol definido para alcanzarlo. | Las rotaciones son un protocolo disciplinado: ante cada desequilibrio el equipo sigue un procedimiento definido (simple o doble) que restablece el orden. |
| `E` | experimentacion, datos y metodo cientifico | La tesis es una hipotesis y cada argumento un experimento que la pone a prueba con datos verificables. | El balance de un AVL se comprueba como un experimento: se mide la altura de cada subarbol y se corrige cuando los datos muestran desequilibrio. |

---

## 4. Generacion de `descripcion_para_analogias`

El texto lo genera `generar-perfil.py` a partir de `areas_dominantes`, con los nombres oficiales de la seccion 1.1 y los dominios de la seccion 3. No incluye puntajes, carreras ni contenido de la materia (el tema lo aporta el evento o la semana academica).

### 4.1 Plantilla con test completo (Top 2)

> `"Conviene conectar la materia con ejemplos de {dominio_area_1} y {dominio_area_2}; areas principales: {nombre_area_1} ({codigo_1}) y {nombre_area_2} ({codigo_2})."`

### 4.2 Texto con test incompleto

> `"Sin informacion suficiente de intereses vocacionales; usar ejemplos de varias areas y evitar supuestos sobre la orientacion del estudiante."`

---

## 5. Ejemplos validados (perfiles contrastantes)

Los tres bloques se generaron con la funcion `calcular_chaside` de `generar-perfil.py` (a partir de respuestas sinteticas con los totales indicados) y pasan `validar-perfiles.py` y el schema consolidado al insertarlos en `perfiles/ejemplo-perfil-estudiante.json`.

### 5.1 Ejemplo 1: dominancia `I` (Ensenanzas Tecnicas)

- **Totales (0-14):** `I: 12`, `E: 9`, `C: 7`, `A: 5`, `H: 4`, `S: 2`, `D: 1`.
- **Puntajes:** `I: 4.4`, `E: 3.6`, `C: 3.0`, `A: 2.4`, `H: 2.1`, `S: 1.6`, `D: 1.3` → Top 2 = `["I", "E"]`.
- **Analogia esperada (Taller de Escritura, area principal I):** "Piensa la estructura de tu ensayo como la arquitectura de un software: la tesis es la interfaz que promete algo, y cada argumento es un modulo que la implementa y se prueba con evidencia."

```json
{
  "chaside": {
    "areas": { "C": 3.0, "H": 2.1, "A": 2.4, "S": 1.6, "I": 4.4, "D": 1.3, "E": 3.6 },
    "areas_dominantes": ["I", "E"],
    "descripcion_para_analogias": "Conviene conectar la materia con ejemplos de procesos tecnicos, sistemas y resolucion de problemas y experimentacion, datos y metodo cientifico; areas principales: Ensenanzas Tecnicas (I) y Ciencias Experimentales (E)."
  }
}
```

### 5.2 Ejemplo 2: dominancia `H` (Humanidades/Sociales/Juridicas)

- **Totales (0-14):** `H: 13`, `A: 10`, `C: 7`, `S: 6`, `E: 4`, `I: 3`, `D: 1`.
- **Puntajes:** `H: 4.7`, `A: 3.9`, `C: 3.0`, `S: 2.7`, `E: 2.1`, `I: 1.9`, `D: 1.3` → Top 2 = `["H", "A"]`.
- **Analogia esperada (Taller de Escritura, area principal H):** "Escribir tu ensayo es como preparar un debate: antes de defender tu postura, anticipa lo que diria quien piensa distinto y respondele con evidencia."

```json
{
  "chaside": {
    "areas": { "C": 3.0, "H": 4.7, "A": 3.9, "S": 2.7, "I": 1.9, "D": 1.3, "E": 2.1 },
    "areas_dominantes": ["H", "A"],
    "descripcion_para_analogias": "Conviene conectar la materia con ejemplos de comunicacion, analisis social y textos y creacion, diseno y expresion; areas principales: Humanidades/Sociales/Juridicas (H) y Artistica (A)."
  }
}
```

### 5.3 Ejemplo 3: test incompleto (perfil neutro)

- **Situacion:** el estudiante no termino el test CHASIDE en Moodle.
- **Comportamiento esperado:** el SLM no asume intereses y usa analogias de la vida cotidiana universitaria o de varias areas.

```json
{
  "chaside": {
    "areas": { "C": 3.0, "H": 3.0, "A": 3.0, "S": 3.0, "I": 3.0, "D": 3.0, "E": 3.0 },
    "areas_dominantes": [],
    "descripcion_para_analogias": "Sin informacion suficiente de intereses vocacionales; usar ejemplos de varias areas y evitar supuestos sobre la orientacion del estudiante."
  }
}
```

---

## 6. Acoplamiento con la PoC y preparacion para E2-10

1. **Datos reales (E2-03 / E2-07):** el bloque `block_chaside` esta instalado en el Moodle local (`moodle/plugins.md`) y `generar-perfil.py` lee `mdl_block_chaside_responses`, recalcula los totales con el mapeo oficial de preguntas y verifica que coincidan con los guardados por el bloque. Los perfiles reales van a `perfiles/reales/` (fuera de git); en el repositorio solo se versionan perfiles con `"origen": "simulado"`.
2. **Presupuesto de tokens:** medido con el tokenizador de `qwen2.5:1.5b` sobre JSON compacto, el bloque `chaside` ocupa entre 91 tokens (test incompleto) y 117 tokens (Top 2) en los ejemplos de la seccion 5, alrededor de un tercio del presupuesto de 350 tokens del perfil.
3. **E2-10 (Prompt Builder):** `descripcion_para_analogias` se inyecta en la seccion "Datos del estudiante" del prompt, junto con una regla fija en las instrucciones: *"Usa los intereses del estudiante solo para elegir analogias y ejemplos; prioriza la primera area; no cambies el recurso recomendado, el contenido ni la dificultad por ellos, y no menciones carreras ni puntajes."* Prueba de verificacion sugerida: ejecutar el mismo perfil con y sin el bloque `chaside` y comprobar que el recurso elegido (A, B o C) no cambia.
4. **PoC actual:** `poc_slm/recommender.py` y los eventos de `poc_slm/eventos/` no usan CHASIDE; este issue no los modifica, solo fija el contrato psicopedagogico.

---

## 7. Referencias

- Duit, R. (1991). On the role of analogies and metaphors in learning science. *Science Education, 75*(6), 649-672.
- Gentner, D. (1983). Structure-mapping: A theoretical framework for analogy. *Cognitive Science, 7*(2), 155-170.
- Hidi, S., y Renninger, K. A. (2006). The four-phase model of interest development. *Educational Psychologist, 41*(2), 111-127.
- Holland, J. L. (1997). *Making vocational choices: A theory of vocational personalities and work environments* (3a ed.). Psychological Assessment Resources.
- Keller, J. M. (2010). *Motivational design for learning and performance: The ARCS model approach*. Springer.
- Tamayo Lopera, D. A., Cespedes Correa, A. M., Lopez Restrepo, S., y Valencia Torres, M. Y. (2018). Correspondencia entre la carrera cursada y resultados del test CHASIDE en una muestra de estudiantes universitarios del primer semestre. *Psicoespacios, 12*(21), 76-93. https://doi.org/10.25057/21452776.1099
- Bloque `block_chaside` v2.0.4 (ISCOUTB / SAVIO, 2026): https://github.com/ISCOUTB/chaside (98 items si/no, 70 de intereses y 28 de aptitudes; mapeo de preguntas y desempate en `classes/facade.php`).
