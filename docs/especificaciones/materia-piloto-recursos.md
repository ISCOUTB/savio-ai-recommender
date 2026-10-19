# Especificacion: Materia piloto y recursos semanales A/B/C (E2-08)

- **Identificador:** E2-08
- **Modulo:** Catalogo de recursos semanales (entrada del recomendador)
- **Depende de:** `docs/especificaciones/recurso-semanal.schema.json` (E2-01)
- **Desbloquea:** E2-09 (dataset A de materia), E2-10 (Prompt Builder semanal)
- **Archivo de datos:** `poc_slm/recursos/semana_1.json`

---

## 1. Materia piloto seleccionada: Taller de Escritura

### 1.1 Decision

Se adopta **Taller de Escritura** como curso piloto de la Entrega 2, como recomienda el docente (`docs/entregas/entrega-2-personalizacion/sprint-3-materia-piloto.md`). **Arquitectura de Software** queda como alternativa documentada (seccion 1.3).

### 1.2 Justificacion

El objetivo del piloto es medir si el SLM **adapta la recomendacion al perfil** del estudiante. Por eso la materia tiene que dejar aislado el efecto del perfil y no meter otras variables. Taller de Escritura cumple esa condicion por cinco razones:

| # | Criterio | Por que Taller de Escritura lo cumple |
|---|---|---|
| 1 | **Sin sesgo de codigo** | Los SLMs candidatos (Qwen 2.5 1.5B/3B) tienen mucho codigo en su preentrenamiento. Con una materia de programacion el modelo tiende a preferir el recurso practico o con codigo por familiaridad del dominio y no por el perfil. Con un dominio humanistico ese atajo desaparece y la eleccion depende del perfil. |
| 2 | **Formatos naturalmente contrastantes** | Un mismo tema de escritura se ensena con un esquema visual, con lectura analitica de textos modelo o con un taller de produccion. Los tres formatos son igual de legitimos, asi que ninguno es la opcion correcta por defecto. |
| 3 | **Transversal a todos los perfiles** | Todos los estudiantes cursan escritura sin importar su area vocacional. Los perfiles CHASIDE varian de verdad (H y A no quedan favorecidos sobre I o C), y las analogias de `chaside.descripcion_para_analogias` tienen algo que aportar. |
| 4 | **Evaluable por humanos sin experticia tecnica** | Cualquier integrante del equipo o el docente puede juzgar si la justificacion pedagogica del modelo tiene sentido. Eso facilita etiquetar el feedback (E2-11) y armar el dataset de destilacion (E2-09). |
| 5 | **Riesgo bajo de alucinacion tecnica** | El tema no depende de versiones, APIs ni sintaxis que el modelo pueda inventar. Los errores del modelo quedan en el plano pedagogico, que es justo lo que se quiere medir. |

### 1.3 Alternativa: Arquitectura de Software

Se usa solo si el docente o el equipo exigen una materia de informatica. En ese caso se aplica la misma plantilla A/B/C con un tema no ligado a codigo (ej. "Estilos arquitectonicos: capas vs. microservicios") para reducir el sesgo del criterio 1. El cambio no toca el schema; solo implica generar `poc_slm/recursos/semana_1.json` con otro contenido.

---

## 2. Diseno de la Semana 1

| Campo | Valor |
|---|---|
| **Semana** | 1 |
| **Tema** | Estructura del ensayo argumentativo: tesis y contraargumentos |
| **Objetivo de aprendizaje** | Al cerrar la semana, el estudiante identifica la tesis y el contraargumento de un ensayo y formula una tesis propia defendible con al menos una objecion anticipada. |
| **Prerrequisitos** | Ninguno especifico de la materia (primera semana del curso). |
| **Evidencia esperada** | Tesis propia + un contraargumento + un parrafo de refutacion (lo produce el Recurso C; con A o B el docente lo pide como tarea comun de la semana). |

**Por que este tema:** es el nucleo conceptual del curso, se puede estudiar con cualquiera de los tres formatos sin perder contenido esencial y su resultado (una tesis bien formulada) se puede verificar.

---

## 3. Recursos de la Semana 1

Los tres recursos cubren **el mismo tema y el mismo objetivo de aprendizaje**. Cambian el canal de representacion, el tipo de actividad, la demanda cognitiva y el tiempo.

### 3.1 Tabla resumen

| Opcion | `recurso_id` | Titulo | `tipo` | `formato` | `nivel` | `carga_estimada_min` |
|:---:|---|---|---|---|---|---:|
| **A** | `tde-s1-A` | Mapa interactivo: del problema a la tesis defendible | `diagrama` | `html` | `basico` | 15 |
| **B** | `tde-s1-B` | Guia de lectura analitica: dos ensayos modelo y glosario | `lectura` | `pdf` | `intermedio` | 45 |
| **C** | `tde-s1-C` | Taller guiado: construye tu tesis y anticipa la objecion | `ejercicio` | `markdown` | `avanzado` | 60 |

### 3.2 Recurso A - Visual / Sintetico

- **Que es:** infografia interactiva de una pantalla con el flujo logico del ensayo como diagrama de nodos: `problema -> tesis -> argumentos -> contraargumento -> refutacion -> conclusion`.
- **Estructura del contenido:**
  1. Diagrama principal de 6 nodos conectados por flechas.
  2. Cada nodo se expande al hacer clic: definicion de una linea + ejemplo minimo.
  3. Codigo de colores: piezas que **afirman** (tesis, argumentos) vs. piezas que **cuestionan** (contraargumento).
  4. Lista visual de 4 verificaciones de una tesis bien formulada (es discutible, es especifica, toma postura, se puede sostener con evidencia).
- **Lo que no incluye:** textos largos ni ejercicios de produccion.
- **Demanda cognitiva (Bloom):** recordar / comprender.

### 3.3 Recurso B - Textual / Analitico

- **Que es:** guia escrita de 8 a 10 paginas con dos ensayos modelo anotados y un glosario.
- **Estructura del contenido:**
  1. Introduccion breve al ensayo argumentativo (1 pagina).
  2. Dos ensayos de aprox. 900 palabras cada uno que defienden **posturas opuestas** del mismo debate. Cada uno trae anotaciones al margen: donde esta la tesis, que tipo de argumento usa cada parrafo, como se introduce y como se refuta el contraargumento.
  3. Preguntas de lectura critica por parrafo.
  4. Comparacion escrita entre las estrategias argumentativas de ambos autores.
  5. Glosario de 12 terminos: tesis, premisa, argumento, evidencia, contraargumento, refutacion, concesion, falacia, postura, conclusion, conector argumentativo, audiencia.
- **Lo que no incluye:** diagramas ni actividades de produccion propia.
- **Demanda cognitiva (Bloom):** comprender / analizar.

### 3.4 Recurso C - Practico / Interactivo

- **Que es:** taller de produccion en 5 pasos con plantillas, ejemplos resueltos a medias y rubrica de autoevaluacion.
- **Estructura del contenido:**
  1. Elegir un tema de una lista corta de debates.
  2. Redactar una tesis y mejorarla con una lista de chequeo.
  3. Escribir dos argumentos de apoyo.
  4. Formular el contraargumento mas fuerte contra la propia postura.
  5. Redactar un parrafo de refutacion.
  - Cada paso trae un ejercicio corto con plantilla y un ejemplo **resuelto a medias**, coherente con la regla de guardrails "nunca soluciones completas" (`prompts/system_guardrails.md`).
  - Rubrica de autoevaluacion: 4 criterios (claridad de la tesis, pertinencia de los argumentos, fuerza del contraargumento, calidad de la refutacion) en 3 niveles de desempeno (en desarrollo, logrado, destacado).
- **Lo que no incluye:** teoria extensa ni lecturas modelo completas.
- **Demanda cognitiva (Bloom):** aplicar / crear.

### 3.5 Origen del material

Esta especificacion define **la curaduria**: estructura, alcance y contrato de cada recurso. Los textos finales (ensayos modelo, infografia, plantillas) los elabora el equipo o se extraen de Savio con apoyo del docente, segun la directriz de la entrega. Para que el recomendador funcione solo se necesitan los metadatos de `semana_1.json`: el SLM decide con `tipo`, `formato`, `resumen`, `nivel` y `carga_estimada_min`, no con el material completo.

---

## 4. Verificacion de contraste

El objetivo es que el SLM no pueda elegir de forma trivial (siempre la misma opcion, o la primera de la lista) y que la eleccion salga de cruzar el perfil con el recurso.

### 4.1 Matriz de contraste

| Dimension | A | B | C | Distintas entre si |
|---|---|---|---|:---:|
| Canal VARK que favorece | visual | lectura_escritura | kinestesico | Si |
| Tipo de actividad | explorar un esquema | leer y analizar | producir texto propio | Si |
| `tipo` (schema) | `diagrama` | `lectura` | `ejercicio` | Si |
| `formato` (schema) | `html` | `pdf` | `markdown` | Si |
| `nivel` (schema) | `basico` | `intermedio` | `avanzado` | Si |
| `carga_estimada_min` | 15 | 45 | 60 | Si |
| Producto que deja el estudiante | ninguno (consulta) | respuestas de analisis | tesis + contraargumento + refutacion | Si |
| Modo de trabajo (personalidad) | rapido, autonomo | reflexivo, individual | estructurado, guiado paso a paso | Si |
| Tema y objetivo de aprendizaje | identico | identico | identico | No (a proposito) |

El tema y el objetivo son iguales en las tres opciones **a proposito**: asi la diferencia entre recursos es solo de forma y demanda, y una recomendacion no puede justificarse con "este recurso cubre mas contenido".

### 4.2 Controles anti-decision-trivial

1. **Sin etiqueta de estilo en el JSON.** Ningun recurso dice "para estudiantes visuales". El schema no tiene ese campo (`additionalProperties: false`) y los resumenes describen el recurso, no a su destinatario. El modelo tiene que inferir la afinidad.
2. **Resumenes de longitud y detalle parecidos.** Los tres `resumen` tienen un nivel de detalle comparable, para que el modelo no favorezca el que este mejor descrito.
3. **Ninguna opcion es "mejor" en abstracto.** A es la mas corta pero no deja producto; C deja producto pero es la mas larga; B es intermedia en todo. Cada una gana y pierde en algo.
4. **Orden neutral.** E2-10 debe presentar las opciones en orden aleatorio, o probar el mismo perfil con el orden permutado, para descartar sesgo de posicion.
5. **Perfil sin recurso directo.** No hay un recurso auditivo. Un perfil con `dominante: "auditivo"` obliga al modelo a decidir con dimensiones secundarias (puntajes restantes, personalidad, carga). Es un caso de prueba que vale la pena incluir.

### 4.3 Riesgo conocido: `nivel` y `carga` correlacionados con el formato

El issue pide que nivel y tiempo sean distintos entre opciones. La consecuencia es que **formato, nivel y carga se mueven juntos** (A siempre es la mas facil y corta). Un SLM pequeno podria elegir A por "menor esfuerzo" en vez de por el estilo. Mitigacion propuesta para E2-10 y E2-11:

- El prompt debe decir que `nivel` describe la **demanda cognitiva** del recurso y no su calidad, y que la eleccion se justifica con el perfil.
- Las pruebas deben incluir perfiles en los que A no sea la respuesta esperada (por ejemplo, kinestesico con alta metodicidad -> C) y medir si el modelo los respeta.
- Si el sesgo aparece, se puede preparar una Semana 2 con niveles cruzados (ej. A intermedio, C basico) para separar los dos efectos.

### 4.4 Hipotesis de recomendacion esperada (para pruebas, no se pasa al modelo)

Esta tabla es una **referencia de evaluacion** para E2-10/E2-11. No es una regla de decision: el sistema es no determinista y una eleccion distinta con buena justificacion pedagogica puede considerarse acierto.

| Perfil de prueba | Recurso esperado | Razon |
|---|---|---|
| `perfiles/ejemplo-perfil-estudiante.json` (visual 8, ritmo propio, retroalimentacion breve) | A | Visual dominante y preferencia por pasos cortos |
| Lectura/escritura dominante, introvertido, alta apertura | B | Canal textual y gusto por el analisis reflexivo |
| Kinestesico dominante, alta metodicidad, necesita estructura | C | Aprender haciendo con pasos guiados y rubrica |
| Auditivo dominante (sin recurso directo) | A o C | Depende de los puntajes secundarios; se evalua la justificacion |
| Mixto (empate visual/kinestesico) | A o C | Se evalua que la justificacion mencione ambos canales |

---

## 5. Contrato de datos: `poc_slm/recursos/semana_1.json`

- El archivo es un **arreglo JSON de 3 objetos** (opciones A, B y C). `recurso-semanal.schema.json` describe **un solo** recurso, asi que se valida cada elemento del arreglo por separado. No se modifico el schema.
- Convencion de `recurso_id`: `<materia>-s<semana>-<opcion>`, con `tde` = Taller de Escritura (ej. `tde-s1-A`).
- Todos los campos opcionales del schema (`nivel`, `carga_estimada_min`) estan presentes porque el criterio de aceptacion los exige.
- Para semanas siguientes: `poc_slm/recursos/semana_<n>.json` con la misma estructura.

### 5.1 Validacion

Desde la raiz del repo, con el entorno virtual activo (`jsonschema` esta incluido en `requirements.txt`):

```bash
python -c "import json, jsonschema; s = json.load(open('docs/especificaciones/recurso-semanal.schema.json', encoding='utf-8')); rs = json.load(open('poc_slm/recursos/semana_1.json', encoding='utf-8')); [jsonschema.validate(r, s) for r in rs]; assert sorted(r['opcion'] for r in rs) == ['A', 'B', 'C']; assert len({r['recurso_id'] for r in rs}) == 3; assert len({r['semana'] for r in rs}) == 1; assert all(len({r[k] for r in rs}) == 3 for k in ('tipo', 'formato', 'nivel', 'carga_estimada_min')); print('OK: 3 recursos validos y contrastantes')"
```

La validacion revisa: (1) cada recurso cumple el schema, (2) las opciones son exactamente A, B y C, (3) los ids no se repiten, (4) los tres son de la misma semana, (5) `tipo`, `formato`, `nivel` y `carga_estimada_min` son distintos en las tres opciones.

---

## 6. Criterios de aceptacion

- [x] Materia piloto justificada formalmente (seccion 1).
- [x] Semana 1 definida con tema academico claro (seccion 2).
- [x] Opciones A, B y C con tipo, formato, resumen, nivel y tiempo estimado diferenciados (secciones 3 y 4.1).
- [x] `poc_slm/recursos/semana_1.json` validado contra `recurso-semanal.schema.json` (seccion 5.1).
