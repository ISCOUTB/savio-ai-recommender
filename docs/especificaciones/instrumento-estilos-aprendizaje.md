# Nota Tecnica: Instrumento de Estilos de Aprendizaje (E2-04)

- **Identificador:** E2-04
- **Modulo:** Perfilamiento psicopedagogico (`perfil.estilos_aprendizaje`)
- **Fuente de datos:** bloque Moodle `block_learning_style` (IS-UTB, v2.0.4)
- **Depende de:** `docs/especificaciones/perfil-estudiante.schema.json` (E2-01)
- **Escala compartida con:** `docs/especificaciones/instrumento-personalidad.md` (E2-05, escala 1.0 a 5.0)
- **Desbloquea:** E2-07, E2-10

---

## 1. Marco teorico y pertinencia en educacion superior

### 1.1 Instrumento institucional: Index of Learning Styles (Felder-Soloman)

El bloque institucional **Exploracion de Estilos de Aprendizaje** aplica el **Index of Learning Styles (ILS) de Felder y Soloman**. Es un cuestionario de **44 items dicotomicos (A / B)** distribuidos en 4 paginas, que mide **cuatro ejes bipolares** de procesamiento de la informacion:

| Eje | Polo A (izquierda) | Polo B (derecha) | Items por polo | Que mide |
| :--- | :--- | :--- | :---: | :--- |
| 1 | **Activo** | **Reflexivo** | 11 | Preferencia por experimentar (hacer, probar, discutir) frente a reflexionar (pensar, analizar, trabajar solo). |
| 2 | **Sensorial** | **Intuitivo** | 11 | Preferencia por hechos concretos, datos y procedimientos frente a principios, teorias y posibilidades. |
| 3 | **Visual** | **Verbal** | 11 | Preferencia por representaciones graficas (diagramas, esquemas, videos) frente a explicaciones escritas o habladas. |
| 4 | **Secuencial** | **Global** | 11 | Preferencia por aprendizaje paso a paso, lineal, frente a vision global, saltos intuitivos y panoramas integradores. |

Cada polo suma **0 a 11** (porque son 11 items por dimension, y cada item suma 1 a uno de los dos polos; la suma de los dos polos es siempre 11).

El bloque entrega:
- **Conteos crudos** por polo (`ap_active`, `ap_reflexivo`, `ap_sensorial`, `ap_intuitivo`, `ap_visual`, `ap_verbal`, `ap_secuencial`, `ap_global`).
- **Resultado compacto** por eje (`act_ref`, `sen_int`, `vis_vrb`, `seq_glo`) con formato `"<diferencia><lado>"` (ej. `5a` = diferencia 5 hacia el polo A).
- **Grafico radar** 0-11.

El test se almacena **globalmente por usuario** (no por curso), con `is_completed = 1` al finalizar.

### 1.2 Decision de diseno: Felder como modelo canonico

El equipo decidio adoptar **Felder-Soloman como modelo canonico** (valor `"felder_silverman"` en el schema) por tres razones:

1. **Es el instrumento real que se diligencia.** El bloque instalado (E2-03) mide esto, no VARK.
2. **No compite con los otros dos instrumentos.** El eje **Visual/Verbal** define el *canal* del recurso (video, texto, interactivo); los otros tres ejes (Activo/Reflexivo, Sensorial/Intuitivo, Secuencial/Global) definen *como se organiza* el estudio. La personalidad (E2-05) ya cubre organizacion, autonomia y nivel de abstraccion; CHASIDE (E2-06) cubre intereses vocacionales. Los tres instrumentos son complementarios, no redundantes.
3. **La escala 1.0-5.0 ya esta acordada.** La conversion de los conteos 0-11 a 1.0-5.0 usa la misma formula que E2-05 (diferencia normalizada), asi que el Prompt Builder (E2-10) recibe perfiles homogeneos.

**VARK queda en el schema como valor historico** (`"vak"` en la enumeracion de `modelo`) para compatibilidad, pero **no se usa** en perfiles nuevos.

---

## 2. Estructura numerica y contrato de datos

### 2.1 Definicion de campos (`perfil.estilos_aprendizaje`)

| Campo | Tipo JSON | Requerido | Rango / valores | Descripcion |
| :--- | :--- | :---: | :--- | :--- |
| `modelo` | `string` | Si (schema) | `"vak"`, `"felder_silverman"`, `"kolb"`, `"otro"` | Marco psicopedagogico del instrumento. Valor canonico: `"felder_silverman"`. |
| `puntajes` | `object` | Si (schema) | 4 claves numericas (`1.0` a `5.0`) | Puntaje normalizado por eje. Claves fijas (ver 2.2). |
| `preferencias` | `array<string>` | Si (schema) | Subconjunto de 8 polos, max 4, sin duplicados | Polos con preferencia clara (ver 2.3). |
| `descripcion_para_prompt` | `string` | Si (schema) | 2 a 3 oraciones | Sintesis accionable para el SLM (seccion 4). |

> **Cambio frente a la version anterior:** el campo `dominante` (unico estilo VARK) **se elimina**. Con 4 ejes bipolares no tiene sentido un "dominante"; lo reemplaza `preferencias`, que lista los polos con preferencia clara.

### 2.2 Conversion: conteos 0-11 -> escala 1.0-5.0

El bloque guarda conteos crudos por polo (`ap_*`). Cada par suma 11. La formula es la misma que E2-05 usa para los ejes MBTI:

```text
eje = round(3 + 2 * (polo_derecho - polo_izquierdo) / 11, 1)
```

| Clave en `puntajes` | Polo izquierdo (0) | Polo derecho (1) | Interpretacion |
| :--- | :--- | :--- | :--- |
| `activo_reflexivo` | Activo | Reflexivo | 1.0 = muy activo / 5.0 = muy reflexivo |
| `sensorial_intuitivo` | Sensorial | Intuitivo | 1.0 = muy sensorial / 5.0 = muy intuitivo |
| `visual_verbal` | Visual | Verbal | 1.0 = muy visual / 5.0 = muy verbal |
| `secuencial_global` | Secuencial | Global | 1.0 = muy secuencial / 5.0 = muy global |

**Detalles de la formula:**
- La diferencia cruda va de -11 a +11 (impar, nunca 0).
- El factor `2/11` mapea el rango [-11, +11] a [-2, +2].
- Sumando 3 se obtiene [1.0, 5.0].
- **3.0 es el punto neutro matematico**, pero **es imposible en un test diligenciado** (la diferencia impar evita 0). Solo aparece en el perfil neutro de test incompleto.

### 2.3 Regla de `preferencias`

Se incluye el polo de cada eje cuyo puntaje normalizado sea **<= 2.1 o >= 3.9** (equivalente a diferencia cruda >= 5 en valor absoluto). Si todos los ejes quedan entre 2.2 y 3.8, el arreglo va vacio `[]`.

**Orden fijo** (para consistencia en el prompt): Activo/Reflexivo, Sensorial/Intuitivo, Visual/Verbal, Secuencial/Global.

### 2.4 Bandas de interpretacion

| Banda | Rango normalizado | Diferencia cruda | Significado |
| :--- | :--- | :--- | :--- |
| Polo izquierdo fuerte | `1.0` a `2.1` | 9 u 11 | Preferencia marcada por el polo izquierdo (incluye en `preferencias`) |
| Equilibrado | `2.2` a `3.8` | 1, 3, 5, 7 | Sin preferencia clara; no se incluye en `preferencias` |
| Polo derecho fuerte | `3.9` a `5.0` | 9 u 11 | Preferencia marcada por el polo derecho (incluye en `preferencias`) |

> **Nota:** `3.0` es imposible en un test completo (diferencia impar). Si aparece, indica test incompleto.

### 2.5 Perfil neutro (test incompleto o sin datos)

Si `is_completed = 0` o no hay registro en Moodle:
- Los 4 `puntajes` = `3.0`
- `preferencias: []`
- `descripcion_para_prompt` = `"Sin informacion suficiente de preferencias de aprendizaje; alternar formatos visuales y verbales, activos y reflexivos, concretos y abstractos, lineales y globales."`

---

## 3. Mapeo de ejes a formatos didacticos

Reglas de inclusion (privilegiar) y exclusion (evitar en aislamiento) por polo. **El eje Visual/Verbal es el que define el canal sensorial**; los otros tres definen la organizacion, que se combina con la personalidad (E2-05, seccion 5).

| Eje / polo | Formatos a privilegiar | Formatos a evitar en aislamiento |
| :--- | :--- | :--- |
| **Activo** | Ejercicios, aplicacion inmediata, trabajo en pares, simulaciones, problemas abiertos. | Teoria pasiva prolongada, lecturas extensas sin practica. |
| **Reflexivo** | Lectura previa, pausas para pensar, escritura reflexiva, analisis individual. | Respuesta inmediata en vivo, exposicion oral sin preparacion. |
| **Sensorial** | Hechos, datos, ejemplos concretos, procedimientos paso a paso, casos reales. | Abstraccion sin aplicacion, teoria sin ejemplos tangibles. |
| **Intuitivo** | Principios, teoria, conexiones entre conceptos, novedad, preguntas "por que" y "que pasaria si". | Repeticion mecanica, ejercicios rutinarios sin proposito. |
| **Visual** | Diagramas, esquemas, mapas conceptuales, videos esquematicos, infografias. | Texto denso sin apoyo grafico, lecturas extensas sin diagramas. |
| **Verbal** | Explicaciones escritas o habladas, resumenes, definiciones formales, glosarios. | Graficos sin texto de apoyo, videos sin narracion ni subtitulos. |
| **Secuencial** | Pasos ordenados, de lo simple a lo complejo, guias numeradas, cronogramas. | Saltos sin secuencia, temas desconectados sin transicion. |
| **Global** | Panorama general primero, ejemplos integradores, vision de conjunto, analogias. | Pasos lineales sin contexto, detalle sin proposito global. |

---

## 4. Generador de texto para el prompt (`descripcion_para_prompt`)

Se construye en **orden fijo** (los 4 ejes) concatenando solo los polos que estan en `preferencias`. Cada polo aporta un fragmento segun la tabla de la seccion 3. El resultado son 2 a 3 oraciones en tercera persona.

**Fragmentos por polo:**

| Polo | Fragmento |
| :--- | :--- |
| `activo` | "aprende mejor experimentando y aplicando los conceptos de forma inmediata" |
| `reflexivo` | "aprende mejor reflexionando antes de actuar y trabajando de forma individual" |
| `sensorial` | "conecta mejor con ejemplos concretos, datos especificos y procedimientos claros" |
| `intuitivo` | "disfruta explorar principios, teorias y conexiones entre ideas" |
| `visual` | "privilegia recursos graficos, diagramas, mapas y videos" |
| `verbal` | "prefiere explicaciones escritas o habladas, resumenes y definiciones" |
| `secuencial` | "rinde mejor con una secuencia definida y progresion paso a paso" |
| `global` | "necesita ver el panorama general antes de entrar en los detalles" |

**Plantilla:**

> `"El estudiante {fragmento_1}, {fragmento_2}, {fragmento_3} y {fragmento_4}. Se recomienda {inclusion_1} complementado con {inclusion_2} y evitar {exclusion_1}."`

- Si `preferencias` esta vacio: usa la frase neutra de la seccion 2.5.
- El numero de fragmentos depende de cuantas preferencias haya (0 a 4). La redaccion se ajusta para que queden 2-3 oraciones gramaticales.

---

## 5. Ejemplos validados

Ambos validados contra `perfil-estudiante.schema.json` (draft-07) y construidos con la formula de la seccion 2.2. Los valores usan diferencias crudas impares (regla de 11 items por polo).

### 5.1 Ejemplo 1: intuitivo fuerte, visual moderado, activo y secuencial equilibrados

- **Conteos Moodle:** `ap_active 6`, `ap_reflexivo 5`, `ap_sensorial 1`, `ap_intuitivo 10`, `ap_visual 9`, `ap_verbal 2`, `ap_secuencial 6`, `ap_global 5`.
- **Puntajes normalizados:**
  - `activo_reflexivo` = 3 + 2*(5-6)/11 = **3.2** (equilibrado)
  - `sensorial_intuitivo` = 3 + 2*(10-1)/11 = **4.6** (intuitivo fuerte)
  - `visual_verbal` = 3 + 2*(2-9)/11 = **1.7** (visual moderado)
  - `secuencial_global` = 3 + 2*(5-6)/11 = **3.2** (equilibrado)
- **Preferencias:** `["intuitivo", "visual"]` (solo estos dos salen de la banda equilibrada).

```json
{
  "estilos_aprendizaje": {
    "modelo": "felder_silverman",
    "puntajes": {
      "activo_reflexivo": 3.2,
      "sensorial_intuitivo": 4.6,
      "visual_verbal": 1.7,
      "secuencial_global": 3.2
    },
    "preferencias": ["intuitivo", "visual"],
    "descripcion_para_prompt": "El estudiante disfruta explorar principios, teorias y conexiones entre ideas, y privilegia recursos graficos, diagramas, mapas y videos. Se recomienda combinar casos integradores con esquemas visuales y evitar repeticion mecanica sin proposito y textos densos sin apoyo grafico."
  }
}
```

### 5.2 Ejemplo 2: sensorial fuerte, verbal fuerte, reflexivo fuerte, global fuerte

- **Conteos Moodle:** `ap_active 3`, `ap_reflexivo 8`, `ap_sensorial 9`, `ap_intuitivo 2`, `ap_visual 2`, `ap_verbal 9`, `ap_secuencial 3`, `ap_global 8`.
- **Puntajes normalizados:**
  - `activo_reflexivo` = 3 + 2*(8-3)/11 = **3.9** (reflexivo fuerte)
  - `sensorial_intuitivo` = 3 + 2*(2-9)/11 = **1.7** (sensorial fuerte)
  - `visual_verbal` = 3 + 2*(9-2)/11 = **4.3** (verbal fuerte)
  - `secuencial_global` = 3 + 2*(8-3)/11 = **3.9** (global fuerte)
- **Preferencias:** `["reflexivo", "sensorial", "verbal", "global"]` (los 4 fuera de banda).

```json
{
  "estilos_aprendizaje": {
    "modelo": "felder_silverman",
    "puntajes": {
      "activo_reflexivo": 3.9,
      "sensorial_intuitivo": 1.7,
      "visual_verbal": 4.3,
      "secuencial_global": 3.9
    },
    "preferencias": ["reflexivo", "sensorial", "verbal", "global"],
    "descripcion_para_prompt": "El estudiante aprende mejor reflexionando antes de actuar, conecta mejor con ejemplos concretos y procedimientos claros, prefiere explicaciones escritas o habladas y necesita ver el panorama general antes de los detalles. Se recomienda priorizar lecturas previas con ejemplos concretos y resumenes estructurados, complementados con panoramas integradores, y evitar exposicion oral inmediata, teoria sin aplicacion y graficos sin texto."
  }
}
```

### 5.3 Ejemplo 3: test incompleto (perfil neutro)

```json
{
  "estilos_aprendizaje": {
    "modelo": "felder_silverman",
    "puntajes": {
      "activo_reflexivo": 3.0,
      "sensorial_intuitivo": 3.0,
      "visual_verbal": 3.0,
      "secuencial_global": 3.0
    },
    "preferencias": [],
    "descripcion_para_prompt": "Sin informacion suficiente de preferencias de aprendizaje; alternar formatos visuales y verbales, activos y reflexivos, concretos y abstractos, lineales y globales."
  }
}
```

---

## 6. Acoplamiento con la PoC actual y preparacion para E2-07 / E2-10

Hoy la PoC (`poc_slm/recommender.py`) consume un campo plano `estilo_aprendizaje` por evento (`poc_slm/eventos/*.json`), con valores como `"visual"` o `"textual"`. Mapeo de equivalencia para la futura integracion:

| Valor actual en eventos PoC | Eje / polo canonico del instrumento |
| :--- | :--- |
| `"visual"` | `visual_verbal` -> polo `visual` |
| `"textual"` | `visual_verbal` -> polo `verbal` |

En E2-07/E2-10, `descripcion_para_prompt` reemplazara a la frase fija actual de la regla 5 (refuerzo `--refuerzo`): la regla dinamica pasara a inyectar esta sintesis (inclusion + exclusion por polo) en lugar de la correspondencia fija `visual -> diagramas`. Este issue no modifica `recommender.py` ni los eventos; solo fija el contrato psicopedagogico.

---

## 7. Referencias

- Felder, R. M., y Soloman, B. A. (s. f.). *Index of Learning Styles*. North Carolina State University. https://www.ncsu.edu/felder-public/ILSpage.html
- Felder, R. M., y Silverman, L. K. (1988). Learning and teaching styles in engineering education. *Engineering Education, 78*(7), 674-681.
- Zywno, M. S. (2003). A contribution to validation of score meaning for Felder-Soloman's Index of Learning Styles. *ASEE Annual Conference*.
- Coffield, F., Moseley, D., Hall, E., y Ecclestone, K. (2004). *Learning styles and pedagogy in post-16 learning: A systematic and critical review*. Learning and Skills Research Centre.
- Pashler, H., McDaniel, M., Rohrer, D., y Bjork, R. (2008). Learning styles: Concepts and evidence. *Psychological Science in the Public Interest, 9*(3), 105-119.
- Bloque `block_learning_style` (IS-UTB / SAVIO): carpeta `learning_style` del contenedor Moodle (mapeo de items, calculo de conteos y salida radar 0-11).
