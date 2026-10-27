# Nota Tecnica: Instrumento de Personalidad (E2-05)

- **Identificador:** E2-05
- **Modulo:** Perfilamiento psicopedagogico (`perfil.personalidad`)
- **Fuente de datos:** bloque Moodle `block_personality_test` (carpeta `personality/`)
- **Depende de:** `docs/especificaciones/perfil-estudiante.schema.json` (E2-01)
- **Escala compartida con:** `docs/especificaciones/instrumento-estilos-aprendizaje.md` (E2-04, escala 1.0 a 5.0)
- **Desbloquea:** E2-07, E2-10

---

## 1. Instrumento institucional: que mide realmente

### 1.1 Descripcion del bloque de personalidad

El bloque institucional **Exploracion de Personalidad** (`block_personality_test`, Moodle 4.0+, UTB) aplica un cuestionario tipo **MBTI** de **72 items dicotomicos (Si = 1 / No = 0)** distribuidos en 8 paginas. Cada item pertenece a uno de 8 polos (9 items por polo), por lo que cada polo produce un total entero en el rango **0 a 9**.

| Eje MBTI | Polo A (columna BD) | Items del polo A | Polo B (columna BD) | Items del polo B |
| :--- | :--- | :--- | :--- | :--- |
| Energia | Extraversion (`extraversion`) | 5, 7, 10, 13, 23, 25, 61, 68, 71 | Introversion (`introversion`) | 2, 9, 49, 54, 63, 65, 67, 69, 72 |
| Percepcion | Sensorial (`sensing`) | 15, 43, 45, 51, 53, 56, 59, 66, 70 | Intuicion (`intuition`) | 37, 39, 41, 44, 47, 52, 57, 62, 64 |
| Decision | Pensamiento (`thinking`) | 1, 4, 6, 18, 20, 48, 50, 55, 58 | Sentimiento (`feeling`) | 3, 8, 11, 14, 27, 31, 33, 35, 40 |
| Organizacion | Juicio (`judging`) | 19, 21, 24, 26, 29, 34, 36, 42, 46 | Percepcion (`perceptive`) | 12, 16, 17, 22, 28, 30, 32, 38, 60 |

Los 8 totales se guardan en la tabla `personality_test` (un registro **global por usuario**, no por curso) junto con `is_completed`. El bloque deriva ademas un tipo de 4 letras (ej. `ENTJ`) con reglas de desempate (I, N, T, P ante empate).

### 1.2 Brecha entre el issue y el instrumento

El issue describe rasgos de **autonomia, metodicidad, introversion/extraversion y apertura a la experiencia**. El instrumento **no mide esas dimensiones con esos nombres**: mide 4 ejes MBTI. Esta nota resuelve la brecha traduciendo los ejes MBTI a los 4 rasgos pedagogicos que ya usa el perfil unificado (`perfiles/ejemplo-perfil-estudiante.json`):

| Rasgo pedagogico (`rasgos.*`) | Origen en el instrumento | Tipo de medicion |
| :--- | :--- | :--- |
| `introversion_extraversion` | Eje E/I | **Directa** (eje completo) |
| `metodicidad` | Eje J/P | **Directa** (eje completo) |
| `apertura` | Eje S/N | **Directa** (eje completo) |
| `autonomia` | Ejes S/N + T/F combinados | **Derivada** (indice inferido, ver 2.4) |

**Decision de diseno:** el tipo MBTI de 4 letras **no se exporta al perfil ni al SLM**. Solo viajan los 4 rasgos numericos y los campos textuales de la seccion 4. Ver guardrails (seccion 6).

---

## 2. Dimensiones conductuales y su justificacion

### 2.1 `introversion_extraversion` (eje E/I)

- **Que describe:** de donde obtiene energia el estudiante para estudiar: interaccion con otros (polo alto) o reflexion individual (polo bajo).
- **Evidencia en items:** E: "prefiere generar ideas en grupo" (q25), "le gusta ir a reuniones y manifestar su opinion" (q71). I: "necesita recargar energias solo" (q2), "ensaya las cosas antes de decirlas" (q9), "desarrolla un alto poder de concentracion en su tiempo privado" (q72).
- **Relevancia pedagogica:** define la **modalidad social** del recurso (estudio individual vs. foros, debates, trabajo en pares).
- **Respaldo teorico:** el eje E/I de MBTI correlaciona fuertemente con Extraversion del modelo de Cinco Factores (McCrae y Costa, 1989).

### 2.2 `metodicidad` (eje J/P)

- **Que describe:** preferencia por planificar, cerrar tareas y seguir una secuencia (polo alto, J) frente a mantener opciones abiertas y trabajar de forma flexible o de ultimo momento (polo bajo, P).
- **Evidencia en items:** J: "hace listas y las utiliza" (q21), "tiene una agenda y la sigue" (q46), "le deleita el orden" (q24). P: "no planifica hasta ver lo que se requiere" (q32), "depende de descargas de adrenalina de ultimo minuto" (q38), "lo importante es la espontaneidad" (q60).
- **Relevancia pedagogica:** define la **estructura temporal** del recurso (cronograma y secuencia fija vs. bloques cortos y flexibles).
- **Respaldo teorico:** J/P correlaciona con Responsabilidad (Conscientiousness) del modelo de Cinco Factores (McCrae y Costa, 1989).

### 2.3 `apertura` (eje S/N)

- **Que describe:** atraccion por ideas, posibilidades y conexiones abstractas (polo alto, N) frente a preferencia por hechos concretos, datos especificos y resultados tangibles (polo bajo, S).
- **Evidencia en items:** N: "le interesa saber como funcionan las cosas solo por placer" (q47), "busca relaciones y conexiones subyacentes" (q62), "el futuro y sus posibilidades le resultan interesantes" (q41). S: "prefiere hechos y numeros que ideas y teorias; escuchar en forma secuencial" (q70), "trabajos con resultados tangibles" (q53), "prefiere respuestas especificas" (q56).
- **Relevancia pedagogica:** define el **nivel de abstraccion y novedad** del recurso (retos exploratorios y conexiones entre conceptos vs. ejemplos concretos y aplicacion inmediata).
- **Respaldo teorico:** S/N es el eje MBTI con mayor correlacion con Apertura a la Experiencia (McCrae y Costa, 1989).

### 2.4 `autonomia` (indice derivado de S/N y T/F)

- **Que describe:** tolerancia a trabajar con instrucciones generales y sin validacion externa constante (polo alto) frente a necesidad de guia explicita, pasos claros y retroalimentacion frecuente (polo bajo).
- **Por que es derivado:** ningun eje del instrumento mide autonomia de forma directa. Se combina:
  - **Tolerancia a la ambiguedad (S/N):** N "da respuestas generales; se irrita cuando lo presionan por especificaciones" (q64) vs. S "se frustra con instrucciones poco claras o 'nos ocuparemos de los detalles despues'" (q15).
  - **Independencia de juicio (T/F):** T "no cree necesario caerle bien a la gente para trabajar con ella" (q18), "se mantiene calmado y objetivo" (q50), "no le importa tomar decisiones dificiles" (q4) vs. F "se pregunta si alguien se preocupa por lo que desea" (q35), "prefiere la armonia; el conflicto lo abruma" (q14).
- **Limitaciones declaradas:**
  - Es un **indice inferido, no validado psicometricamente** como medida de autonomia. Su peso en el prompt debe ser igual o menor al de los rasgos directos.
  - Comparte el componente S/N con `apertura`, por lo que ambos rasgos estaran correlacionados.
  - El item mas cercano a dependencia de aprobacion externa (q61, "necesita aprobacion de colegas") esta asignado por el instrumento al polo E, no a T/F, y por eso no entra en este indice.
  - Revisar con el area de psicopedagogia antes de usarlo para decisiones que no sean de formato.

---

## 3. Transformacion numerica (Moodle -> `rasgos`)

### 3.1 Formulas (escala canonica 1.0 a 5.0)

Se usan las **diferencias entre polos** (no el tipo de 4 letras), para conservar la intensidad de la preferencia y evitar la regla de desempate forzado del bloque. Con totales de 0 a 9 por polo, cada diferencia va de -9 a +9:

```text
introversion_extraversion = round(3 + 2 * (extraversion - introversion) / 9, 1)
metodicidad               = round(3 + 2 * (judging      - perceptive)   / 9, 1)
apertura                  = round(3 + 2 * (intuition    - sensing)      / 9, 1)
autonomia                 = round(3 + ((intuition - sensing) + (thinking - feeling)) / 9, 1)
```

- Todas las salidas quedan en **[1.0, 5.0]**; `3.0` es el punto neutro (polos empatados).
- Convencion de direccion: valor **alto** = extraversion / metodico / abierto / autonomo; valor **bajo** = introversion / flexible / concreto / requiere guia.

### 3.2 Bandas de interpretacion

| Banda | Rango | Equivale a | Uso en el prompt |
| :--- | :--- | :--- | :--- |
| Polo bajo | `1.0` a `2.1` | Diferencia de 4 o mas puntos hacia el polo bajo | Se aplica la fila "polo bajo" de la matriz (seccion 5) |
| Equilibrado | `2.2` a `3.8` | Diferencia de 3 puntos o menos | No se emite preferencia para ese rasgo; formatos mixtos |
| Polo alto | `3.9` a `5.0` | Diferencia de 4 o mas puntos hacia el polo alto | Se aplica la fila "polo alto" de la matriz |

La banda equilibrada es deliberadamente amplia: con solo 9 items por polo, diferencias pequenas no son una preferencia confiable y el sistema no debe sobre-personalizar con ellas.

### 3.3 Casos de borde

- **Test incompleto (`is_completed = 0`) o sin registro:** el schema exige `personalidad.rasgos`, asi que se emite el **perfil neutro**: los 4 rasgos en `3.0`, `resumen_conductual` = `"Sin informacion suficiente de preferencias de trabajo; usar formatos variados."` y `preferencias_trabajo` = `[]`.
- **Registro global por usuario:** el resultado puede venir de otro curso. Se usa igual (son preferencias personales, no de la materia), registrando `updated_at` del bloque para trazabilidad en E2-07.
- **Antiguedad del test:** si el registro tiene mas de 12 meses, se sugiere invitar al estudiante a repetirlo; mientras tanto se usa el valor existente.

---

## 4. Contrato de datos: `perfil.personalidad`

Alineado con `docs/especificaciones/perfil-estudiante.schema.json` (E2-01). El schema solo exige `rasgos` (objeto de valores numericos, claves libres). Este instrumento fija las claves por convencion.

| Campo | Tipo JSON | Requerido | Rango / valores | Descripcion |
| :--- | :--- | :---: | :--- | :--- |
| `rasgos` | `object` | Si (schema) | 4 claves numericas | Rasgos pedagogicos derivados del instrumento. |
| `rasgos.introversion_extraversion` | `number` | Si (convencion) | `1.0` a `5.0` | Bajo = estudio individual / alto = estudio en interaccion. |
| `rasgos.autonomia` | `number` | Si (convencion) | `1.0` a `5.0` | **Derivado.** Bajo = requiere guia paso a paso / alto = tolera recursos abiertos. |
| `rasgos.metodicidad` | `number` | Si (convencion) | `1.0` a `5.0` | Bajo = trabajo flexible / alto = secuencia y cronograma. |
| `rasgos.apertura` | `number` | Si (convencion) | `1.0` a `5.0` | Bajo = ejemplos concretos / alto = exploracion y conexiones. |
| `resumen_conductual` | `string` | Si (convencion) | 2 a 3 oraciones | Sintesis de preferencias de trabajo para el prompt (seccion 4.2). |
| `preferencias_trabajo` | `array<string>` | Si (convencion) | Vocabulario controlado (seccion 4.1) | Etiquetas de formato que el Prompt Builder puede usar de forma deterministica. |

**Campos que NO se incluyen (minimizacion de datos):** tipo MBTI de 4 letras, los 8 totales crudos, las 72 respuestas individuales y las descripciones de tipo del bloque (`mbti_*`). Permanecen en Moodle.

### 4.1 Vocabulario controlado de `preferencias_trabajo`

Solo se emiten etiquetas para rasgos fuera de la banda equilibrada. Valores permitidos:

| Rasgo y polo | Etiquetas emitidas |
| :--- | :--- |
| `introversion_extraversion` bajo | `"individual"`, `"reflexion previa"` |
| `introversion_extraversion` alto | `"colaborativo"`, `"foros y debates"` |
| `autonomia` bajo | `"guia paso a paso"`, `"checklist"`, `"retroalimentacion frecuente"` |
| `autonomia` alto | `"ritmo propio"`, `"retos abiertos"` |
| `metodicidad` bajo | `"bloques cortos flexibles"`, `"variedad de actividades"` |
| `metodicidad` alto | `"secuencia definida"`, `"cronograma"` |
| `apertura` bajo | `"ejemplos concretos"`, `"aplicacion practica inmediata"` |
| `apertura` alto | `"exploratorio"`, `"conexiones entre ideas"` |

Si todos los rasgos estan en banda equilibrada, el arreglo queda vacio `[]` (no se inventan preferencias).

### 4.2 Plantilla de `resumen_conductual`

Se concatenan, en el orden E/I, autonomia, metodicidad, apertura, los fragmentos de los rasgos **fuera de banda equilibrada**, en 2 a 3 oraciones:

| Rasgo y polo | Fragmento |
| :--- | :--- |
| E/I bajo | "suele preferir el estudio individual, con tiempo para reflexionar antes de participar" |
| E/I alto | "suele aprovechar el intercambio de ideas con otras personas, como foros o debates" |
| autonomia baja | "se beneficia de instrucciones claras, pasos explicitos y retroalimentacion frecuente" |
| autonomia alta | "se desenvuelve bien con retos abiertos a su propio ritmo" |
| metodicidad baja | "aprovecha mejor actividades variadas en bloques cortos y flexibles" |
| metodicidad alta | "rinde mejor con una secuencia definida y un cronograma claro" |
| apertura baja | "conecta mejor con ejemplos concretos y aplicacion practica inmediata" |
| apertura alta | "disfruta explorar el porque de los conceptos y las conexiones entre ideas" |

Si ningun rasgo esta fuera de banda: `"Muestra preferencias de trabajo equilibradas; conviene combinar formatos individuales y colaborativos, guiados y abiertos."`

Restricciones del texto: tercera persona, verbos de preferencia (`suele`, `prefiere`, `se beneficia`, `aprovecha`), sin nombrar el tipo MBTI ni polos tecnicos, y siempre sujeto a los guardrails de la seccion 6.

---

## 5. Matriz rasgo -> formato de recurso

La personalidad **no decide el canal sensorial** (eso es responsabilidad de `estilos_aprendizaje`, E2-04). Decide **como se organiza** el recurso: modalidad social, grado de estructura, ritmo y nivel de abstraccion. Asi ambos instrumentos son complementarios y no compiten.

| Rasgo / polo | Impacto en el aprendizaje | Formatos a privilegiar | Formatos a evitar en aislamiento |
| :--- | :--- | :--- | :--- |
| **Autonomia alta** | Tolera recursos abiertos y retos exploratorios a ritmo propio. | Retos o proyectos abiertos, lecturas de profundizacion opcionales, problemas sin solucion guiada, rutas de estudio autogestionadas. | Guias excesivamente paso a paso que limiten la iniciativa. |
| **Autonomia baja** (alta necesidad de guia) | Requiere recursos estructurados paso a paso. | Tutoriales paso a paso, checklists de avance, ejemplos resueltos antes del ejercicio, autoevaluaciones cortas con retroalimentacion inmediata. | Tareas abiertas sin criterios claros ni puntos de control. |
| **Metodicidad alta** | Prefiere guias secuenciales y cronogramas definidos. | Guias secuenciales numeradas, cronograma semanal con hitos, recursos ordenados de lo basico a lo avanzado. | Material disperso o sin orden sugerido de consumo. |
| **Metodicidad baja** | Prefiere flexibilidad y variedad. | Micro-recursos de 10 a 15 minutos, actividades variadas e intercambiables, recordatorios de fechas clave. | Cronogramas rigidos y extensos sin opciones. |
| **Introversion** (E/I bajo) | Prefiere estudio individual y reflexion previa. | Lecturas y videos para estudio individual, ejercicios autocorregibles, participacion escrita asincronica con tiempo para preparar. | Actividades que exijan exposicion oral inmediata o debate en vivo como unica opcion. |
| **Extraversion** (E/I alto) | Prefiere debates, foros y trabajo con pares. | Foros de discusion, debates, estudio en pares, explicar el tema a otros, actividades colaborativas. | Estudio individual prolongado sin espacios de intercambio. |
| **Apertura alta** | Atraccion por ideas nuevas y conexiones. | Casos abiertos, preguntas de "por que" y "que pasaria si", recursos que conecten la materia con otros temas. | Repeticion mecanica sin contexto ni proposito. |
| **Apertura baja** | Prefiere lo concreto y aplicable. | Ejemplos concretos, datos especificos, ejercicios aplicados con resultado tangible, explicaciones secuenciales. | Teoria abstracta o especulativa sin aplicacion inmediata. |

**Banda equilibrada:** no se aplica ninguna fila de ese rasgo; el SLM puede combinar formatos libremente.

**Regla de prioridad en el Prompt Builder (E2-10):** `estilos_aprendizaje` define el canal (video, texto, interactivo...). `personalidad` define la organizacion de ese recurso. Si hay tension (ej. estudiante visual con alta necesidad de guia), se privilegia el canal del estilo **organizado** segun la personalidad (ej. video tutorial paso a paso con checklist), nunca descartando el canal.

---

## 6. Guardrails eticos y de lenguaje

### 6.1 Reglas obligatorias

1. **Sin diagnostico psicologico.** El sistema no emite diagnosticos, tipos de personalidad, ni interpretaciones clinicas o de salud mental. Solo produce **sugerencias de formato de estudio**.
2. **Sin juicios de valor.** Ningun polo es mejor que otro. Baja autonomia o baja metodicidad son **preferencias de apoyo**, no deficiencias.
3. **No etiquetar.** Ni el perfil ni el prompt ni la respuesta del SLM incluyen el tipo MBTI (`INTJ`, `ESFP`...), ni expresiones como "es introvertido", "es desorganizado" o "es dependiente". Se describe la **preferencia** ("suele preferir..."), no la identidad ("es...").
4. **Preferencia, no capacidad.** Los rasgos nunca se usan para inferir rendimiento, inteligencia, aptitud ni probabilidad de exito.
5. **Sugerir, nunca restringir.** La personalidad ordena y adapta recursos; **no oculta ni bloquea** contenido. El estudiante siempre puede acceder a todos los formatos.
6. **Rasgos mutables.** Se tratan como preferencias actuales y autorreportadas, que pueden cambiar. El perfil debe poder recalcularse si el estudiante repite el test.
7. **Minimizacion de datos.** Solo los 4 rasgos y los textos derivados salen de Moodle (seccion 4). Las respuestas individuales y el tipo MBTI no se envian al SLM.
8. **Transparencia.** Si el estudiante pregunta por que recibe cierto formato, la explicacion debe referirse a sus preferencias de estudio declaradas en el test, en lenguaje sencillo.

### 6.2 Lexico prohibido y alternativas

| Evitar (etiqueta o juicio) | Usar (preferencia de formato) |
| :--- | :--- |
| "es introvertido / timido / reservado" | "suele preferir el estudio individual" |
| "es extrovertido / hablador" | "aprovecha el intercambio de ideas con otras personas" |
| "es desorganizado / procrastina / impuntual" | "aprovecha mejor bloques cortos y flexibles" |
| "es dependiente / inseguro / necesita que lo validen" | "se beneficia de pasos claros y retroalimentacion frecuente" |
| "es rigido / inflexible" | "rinde mejor con una secuencia definida" |
| "le falta imaginacion / es poco creativo" | "conecta mejor con ejemplos concretos" |
| "es disperso / distraido" | "disfruta explorar conexiones entre ideas" |
| "su tipo de personalidad es ..." / "perfil ENTJ" | (no se menciona) |
| "trastorno", "deficit", "patologia", "ansiedad", "problema de..." | (nunca; fuera del alcance del sistema) |

### 6.3 Regla para el prompt del SLM (insumo para E2-10)

Texto propuesto para incluir en las instrucciones del sistema cuando se inyecte `perfil.personalidad`:

> "Las preferencias de trabajo del estudiante son orientativas y solo sirven para adaptar el formato y la organizacion de los recursos. No menciones tipos de personalidad, no describas el caracter del estudiante y no emitas juicios, diagnosticos ni etiquetas. Redacta con tono empatico y no punitivo, en terminos de lo que puede ayudarle a estudiar mejor."

---

## 7. Ejemplos (perfiles contrastantes)

### 7.1 Ejemplo 1: individual, autonomo, flexible y exploratorio

- **Totales Moodle:** `extraversion 2`, `introversion 7`, `sensing 3`, `intuition 7`, `thinking 7`, `feeling 2`, `judging 2`, `perceptive 7`.
- **Calculo:**
  - `introversion_extraversion` = 3 + 2(2 - 7)/9 = 1.89 -> **1.9** (polo bajo)
  - `autonomia` = 3 + ((7 - 3) + (7 - 2))/9 = 4.00 -> **4.0** (polo alto)
  - `metodicidad` = 3 + 2(2 - 7)/9 = 1.89 -> **1.9** (polo bajo)
  - `apertura` = 3 + 2(7 - 3)/9 = 3.89 -> **3.9** (polo alto)

```json
{
  "personalidad": {
    "rasgos": {
      "introversion_extraversion": 1.9,
      "autonomia": 4.0,
      "metodicidad": 1.9,
      "apertura": 3.9
    },
    "resumen_conductual": "Suele preferir el estudio individual, con tiempo para reflexionar antes de participar, y se desenvuelve bien con retos abiertos a su propio ritmo. Aprovecha mejor actividades variadas en bloques cortos y flexibles, y disfruta explorar el porque de los conceptos y las conexiones entre ideas.",
    "preferencias_trabajo": [
      "individual",
      "reflexion previa",
      "ritmo propio",
      "retos abiertos",
      "bloques cortos flexibles",
      "variedad de actividades",
      "exploratorio",
      "conexiones entre ideas"
    ]
  }
}
```

### 7.2 Ejemplo 2: colaborativo, con necesidad de guia, metodico y concreto

- **Totales Moodle:** `extraversion 8`, `introversion 2`, `sensing 7`, `intuition 2`, `thinking 3`, `feeling 7`, `judging 8`, `perceptive 1`.
- **Calculo:**
  - `introversion_extraversion` = 3 + 2(8 - 2)/9 = 4.33 -> **4.3** (polo alto)
  - `autonomia` = 3 + ((2 - 7) + (3 - 7))/9 = 2.00 -> **2.0** (polo bajo)
  - `metodicidad` = 3 + 2(8 - 1)/9 = 4.56 -> **4.6** (polo alto)
  - `apertura` = 3 + 2(2 - 7)/9 = 1.89 -> **1.9** (polo bajo)

```json
{
  "personalidad": {
    "rasgos": {
      "introversion_extraversion": 4.3,
      "autonomia": 2.0,
      "metodicidad": 4.6,
      "apertura": 1.9
    },
    "resumen_conductual": "Suele aprovechar el intercambio de ideas con otras personas, como foros o debates, y se beneficia de instrucciones claras, pasos explicitos y retroalimentacion frecuente. Rinde mejor con una secuencia definida y un cronograma claro, y conecta mejor con ejemplos concretos y aplicacion practica inmediata.",
    "preferencias_trabajo": [
      "colaborativo",
      "foros y debates",
      "guia paso a paso",
      "checklist",
      "retroalimentacion frecuente",
      "secuencia definida",
      "cronograma",
      "ejemplos concretos",
      "aplicacion practica inmediata"
    ]
  }
}
```

### 7.3 Ejemplo 3: test no completado (perfil neutro)

```json
{
  "personalidad": {
    "rasgos": {
      "introversion_extraversion": 3.0,
      "autonomia": 3.0,
      "metodicidad": 3.0,
      "apertura": 3.0
    },
    "resumen_conductual": "Sin informacion suficiente de preferencias de trabajo; usar formatos variados.",
    "preferencias_trabajo": []
  }
}
```

Los tres bloques cumplen el sub-schema `personalidad` de `perfil-estudiante.schema.json` (`rasgos` requerido con valores numericos; `resumen_conductual` string; `preferencias_trabajo` arreglo de strings; sin propiedades adicionales).

---

## 8. Compatibilidad y trabajo pendiente

- **Perfil de ejemplo existente:** `perfiles/ejemplo-perfil-estudiante.json` usa las mismas 4 claves de `rasgos` pero en escala 0-10 y etiquetas libres en `preferencias_trabajo` (`"ritmo propio"`, `"retroalimentacion breve"`). Se suma al issue de armonizacion propuesto en E2-04: re-escalar a 1.0-5.0 y ajustar las etiquetas al vocabulario de la seccion 4.1. **No se modifica ese archivo en el alcance de E2-05.**
- **E2-07 (schema consolidado):** se propone fijar en el schema las 4 claves de `rasgos` con `minimum: 1` / `maximum: 5` y un `enum` para `preferencias_trabajo`. Este issue no modifica el schema.
- **E2-10 (Prompt Builder):** inyectar `resumen_conductual` y la regla de la seccion 6.3; aplicar la regla de prioridad estilo -> canal, personalidad -> organizacion (seccion 5).
- **Validacion psicopedagogica:** revisar con el area de psicopedagogia la validez del indice `autonomia` (seccion 2.4) antes de darle mas peso en la recomendacion.

---

## Referencias

- McCrae, R. R., y Costa, P. T. (1989). Reinterpreting the Myers-Briggs Type Indicator from the perspective of the five-factor model of personality. *Journal of Personality*, 57(1), 17-40.
- Myers, I. B., McCaulley, M. H., Quenk, N. L., y Hammer, A. L. (1998). *MBTI Manual: A guide to the development and use of the Myers-Briggs Type Indicator* (3a ed.). Consulting Psychologists Press.
- Bloque `block_personality_test` (UTB / SAVIO): carpeta `personality/` de este repositorio (mapeo de items y calculo de totales).
