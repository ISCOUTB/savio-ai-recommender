# Nota Tecnica: Instrumento CHASIDE de Intereses Vocacionales (E2-06)

- **Identificador:** E2-06
- **Modulo:** Perfilamiento psicopedagogico (`perfil.chaside`)
- **Depende de:** `docs/especificaciones/perfil-estudiante.schema.json` (E2-01)
- **Desbloquea:** E2-07, E2-10
- **Relacionado:** E2-03 (diligenciamiento del bloque IS-UTB con datos reales), E2-04 (convencion de escala 1.0 a 5.0)

---

## 1. Marco del instrumento y pertinencia en el proyecto

### 1.1 Que mide CHASIDE

CHASIDE es un cuestionario de orientacion vocacional de amplio uso en instituciones educativas de Latinoamerica. Su version mas difundida consta de **98 items de respuesta dicotomica (si / no)** y, para cada una de las 7 areas, distingue items de **intereses** (que le gusta hacer al estudiante) e items de **aptitudes** (en que se percibe habil). El nombre es el acronimo de sus 7 areas:

| Codigo | Area vocacional | Que refleja un puntaje alto |
| :---: | :--- | :--- |
| `C` | Administrativas y Contables | Gusto por organizar, planificar, llevar registros, cuantificar y gestionar recursos. |
| `H` | Humanisticas y Sociales | Interes por las personas, la comunicacion, la argumentacion, la historia y los problemas sociales. |
| `A` | Artisticas | Sensibilidad estetica, creatividad, composicion visual, musical o narrativa. |
| `S` | Salud y Medicina | Interes por el cuidado, el diagnostico, el bienestar y el funcionamiento del cuerpo humano. |
| `I` | Ingenieria y Computacion | Gusto por disenar, construir, automatizar y entender como funcionan los sistemas. |
| `D` | Defensa y Seguridad | Interes por la proteccion, la estrategia, la disciplina, los protocolos y la gestion de riesgos. |
| `E` | Exactas y Agrarias | Gusto por la investigacion, la experimentacion, la medicion y los fenomenos naturales. |

> **Por confirmar en E2-03:** el numero de items y la forma en que el bloque IS-UTB entrega los resultados (conteo de respuestas "si", porcentaje o puntaje propio). La normalizacion de la seccion 2.2 esta disenada para funcionar con cualquiera de esos formatos.

### 1.2 Regla de oro pedagogica: CHASIDE solo guia analogias

En este proyecto CHASIDE **no** se usa para orientar la carrera del estudiante ni para decidir que aprende. Su unica funcion es indicar **que dominios de experiencia le resultan cercanos** al estudiante, para que el SLM elija metaforas, analogias y aplicaciones practicas que conecten la materia piloto con sus intereses (dimension de **Relevancia** del modelo ARCS).

| CHASIDE **SI** determina | CHASIDE **NO** determina |
| :--- | :--- |
| El dominio de las analogias y metaforas de la explicacion. | El contenido disciplinar de la materia ni el tema de la semana. |
| Los ejemplos de aplicacion practica que acompanan la recomendacion. | El nivel de dificultad del recurso. |
| El tono de la conexion motivacional ("esto se parece a..."). | La eleccion entre Recurso A, B o C (la deciden estilos de aprendizaje y personalidad). |

Consecuencia directa: si se eliminara el bloque `chaside` del perfil, el sistema debe seguir recomendando el **mismo recurso**; solo cambiarian los ejemplos con los que se explica.

### 1.3 Guardrails eticos del instrumento

1. **Sin orientacion vocacional:** el SLM nunca sugiere cambiar de carrera ni afirma que el estudiante "es bueno para" un area ("deberias estudiar medicina" esta prohibido).
2. **Sin revelar puntajes:** los valores numericos de CHASIDE no se mencionan al estudiante; solo se usan las analogias.
3. **Sin estereotipos:** las analogias no se asocian a genero, origen ni condicion socioeconomica, y ningun area se presenta como superior a otra.
4. **Area `S` sin consejo clinico:** las analogias de salud usan procesos (diagnostico, tratamiento, seguimiento), nunca recomendaciones medicas.
5. **Area `D` sin violencia:** las analogias de defensa usan estrategia, planificacion, protocolos y gestion de riesgos, nunca conflicto armado.
6. **Coherente con la Regla 3 de la PoC:** las analogias son empaticas y formativas; nunca se usan para senalar carencias del estudiante.

---

## 2. Estructura numerica y contrato de datos

El bloque `chaside` se alinea con `docs/especificaciones/perfil-estudiante.schema.json` (E2-01), que ya declara los tres campos de este instrumento. **Este issue no modifica el schema.**

### 2.1 Definicion de campos (`perfil.chaside`)

| Campo | Tipo JSON | Requerido | Rango / valores permitidos | Descripcion tecnica |
| :--- | :--- | :---: | :--- | :--- |
| `areas` | `object` | Si (schema) | Objeto con las 7 claves `C`, `H`, `A`, `S`, `I`, `D`, `E` | Puntaje normalizado de cada area vocacional. El schema prohibe claves adicionales. |
| `areas.C` ... `areas.E` | `number` | Si (convencion) | `1.0` a `5.0`, un decimal | Afinidad del estudiante con el area (regla 2.2). |
| `areas_dominantes` | `array` de `string` | Si (convencion) | 0 a 2 elementos del enum `C`, `H`, `A`, `S`, `I`, `D`, `E`, ordenados de mayor a menor | Areas que guian las analogias (regla 2.3). Lista vacia si no hay afinidad marcada. |
| `descripcion_para_analogias` | `string` | Si (convencion) | 1 a 2 oraciones, maximo ~45 palabras | Directriz en lenguaje natural inyectada en el prompt del SLM (seccion 4). |

**Nota sobre el contrato:** el schema solo exige `areas`; este instrumento declara `areas_dominantes` y `descripcion_para_analogias` como **requeridos por convencion**, con el mismo criterio que E2-04. Endurecer el schema (claves de `areas` requeridas, `minimum`/`maximum`, `maxItems: 2`) queda propuesto para la consolidacion de E2-07.

### 2.2 Normalizacion a la escala canonica 1.0 a 5.0

Para que los tres instrumentos compartan escala (convencion de E2-04), el resultado bruto de cada area se convierte asi:

```
proporcion = respuestas_si_del_area / items_del_area        (o porcentaje / 100 si el bloque entrega porcentajes)
puntaje    = round(1 + 4 * proporcion, 1)                    -> rango 1.0 a 5.0
```

Ejemplo: con 14 items por area, un estudiante que responde "si" a 12 items de `I` obtiene `1 + 4 * 12/14 = 4.4`.

Interpretacion de la escala (mismos cortes que E2-04):

- Afinidad alta: `4.0` a `5.0`
- Afinidad moderada: `2.5` a `3.9`
- Afinidad baja: `1.0` a `2.4`

### 2.3 Regla de calculo de `areas_dominantes` (umbral delta = 0.5)

Se ordenan las 7 areas de mayor a menor puntaje (P1 >= P2 >= ... >= P7):

1. **Sin afinidad marcada:** si P1 < 2.5, `areas_dominantes = []` y el SLM usa analogias cotidianas neutrales (seccion 4.3).
2. **Una area dominante:** si P1 >= 2.5 y P1 - P2 >= 0.5, `areas_dominantes = [area de P1]`.
3. **Dos areas co-dominantes:** si P1 >= 2.5 y P1 - P2 < 0.5, `areas_dominantes = [area de P1, area de P2]`.
4. **Tope de 2 areas:** aunque haya un empate de tres o mas, solo se toman las dos primeras, para mantener el prompt corto (presupuesto de tokens de E2-07).
5. **Desempate:** si dos areas tienen exactamente el mismo puntaje, se respeta el orden del acronimo C, H, A, S, I, D, E.

---

## 3. Mapeo de areas a dominios de analogia

Cada area se traduce en un dominio de experiencia del que el SLM toma sus metaforas. Las columnas de ejemplo muestran el mismo recurso explicado con analogias distintas, tanto en la materia piloto propuesta (Taller de Escritura, E2-08) como en una materia de ingenieria (Estructuras de Datos, escenario de la Entrega 1).

| Area | Dominio de analogias | Ejemplo en Taller de Escritura (ensayo argumentativo) | Ejemplo en ingenieria (arboles AVL) |
| :---: | :--- | :--- | :--- |
| `C` | Presupuestos, inventarios, flujo de caja, planificacion. | La tesis es el presupuesto del ensayo: cada parrafo "gasta" en un argumento y al final las cuentas deben cuadrar con la conclusion. | Rebalancear un AVL es como cuadrar un balance contable: si una columna pesa mas, se redistribuye hasta que la diferencia sea minima. |
| `H` | Debates, comunicacion persuasiva, historia, dinamicas sociales. | Escribir un ensayo es preparar un debate: anticipar al oponente (contraargumento) y responderle con evidencia. | Un AVL es como un comite que exige equilibrio de representacion: ningun lado puede tener dos votos mas que el otro. |
| `A` | Composicion visual, ritmo musical, narrativa, diseno. | El ensayo tiene composicion como una pintura: un punto focal (tesis) y elementos que guian la mirada hacia el. | El factor de balance funciona como la simetria de una composicion: si un lado pesa mas, la obra se "cae" y hay que recomponerla. |
| `S` | Diagnostico, tratamiento, seguimiento, cuidado. | Revisar un borrador es como un diagnostico: identificar sintomas (ideas sueltas) antes de aplicar el tratamiento (reescritura). | Cada insercion es un chequeo de signos vitales: se mide el balance en cada nodo y, si se sale del rango, se aplica una rotacion correctiva. |
| `I` | Arquitectura de software, diseno de sistemas, modulos, pruebas. | La estructura del ensayo es una arquitectura de software: la tesis es la interfaz y cada argumento un modulo que la implementa y se prueba con evidencia. | Un AVL es un sistema autorregulado: como un controlador que corrige el error cada vez que el sistema se desvia del punto de equilibrio. |
| `D` | Estrategia, planificacion de operaciones, protocolos, gestion de riesgos. | El ensayo es un plan estrategico: se anticipan los riesgos (contraargumentos) y se define un protocolo de respuesta para cada uno. | Las rotaciones son protocolos de contingencia: ante cada desequilibrio hay un procedimiento definido (simple o doble) que restablece el orden. |
| `E` | Metodo cientifico, experimentos, medicion, ciclos naturales. | La tesis es una hipotesis y cada argumento un experimento que la pone a prueba con datos verificables. | El balance de un AVL es como el equilibrio de un ecosistema: cuando una poblacion crece demasiado, el sistema se reajusta para volver al equilibrio. |

---

## 4. Generador de texto para el prompt (`descripcion_para_analogias`)

El campo traduce `areas_dominantes` en una directriz breve para el SLM. Restricciones: 1 a 2 oraciones, en tercera persona, sin puntajes, sin mencionar carreras y sin contenido de la materia (el tema lo aporta el evento o la semana academica).

### 4.1 Plantilla con una area dominante

> `"Sus intereses se orientan al area {nombre_area_1}. Conectar las explicaciones con analogias de {dominio_area_1}."`

### 4.2 Plantilla con dos areas co-dominantes

> `"Sus intereses combinan las areas {nombre_area_1} y {nombre_area_2}. Conectar las explicaciones con analogias de {dominio_area_1} o de {dominio_area_2}."`

### 4.3 Plantilla sin afinidad marcada (`areas_dominantes = []`)

> `"Sin un area de interes vocacional marcada. Usar analogias de la vida cotidiana universitaria, sin asumir intereses particulares."`

Donde `{dominio_area}` se toma de la columna "Dominio de analogias" de la seccion 3, en minusculas.

---

## 5. Ejemplos validados (perfiles contrastantes)

Los tres bloques se validaron contra `docs/especificaciones/perfil-estudiante.schema.json` (draft-07), insertados en el perfil de ejemplo de E2-01, y cumplen las reglas 2.2 y 2.3.

### 5.1 Ejemplo 1: dominancia `I` (Ingenieria y Computacion)

- **Puntajes:** `I: 4.4`, `E: 3.6`, `C: 3.0`, `A: 2.4`, `H: 2.1`, `S: 1.6`, `D: 1.3`.
- **Verificacion de la regla:** P1 = 4.4 >= 2.5 y 4.4 - 3.6 = 0.8 >= 0.5 → `areas_dominantes: ["I"]`.
- **Analogia esperada (Taller de Escritura):** "Piensa la estructura de tu ensayo como la arquitectura de un software: la tesis es la interfaz que promete algo, y cada argumento es un modulo que la implementa y se prueba con evidencia."

```json
{
  "chaside": {
    "areas": { "C": 3.0, "H": 2.1, "A": 2.4, "S": 1.6, "I": 4.4, "D": 1.3, "E": 3.6 },
    "areas_dominantes": ["I"],
    "descripcion_para_analogias": "Sus intereses se orientan al area Ingenieria y Computacion. Conectar las explicaciones con analogias de arquitectura de software, diseno de sistemas, modulos y pruebas."
  }
}
```

### 5.2 Ejemplo 2: dominancia `H` (Humanisticas y Sociales)

- **Puntajes:** `H: 4.7`, `A: 3.9`, `C: 2.9`, `S: 2.6`, `E: 2.0`, `I: 1.9`, `D: 1.4`.
- **Verificacion de la regla:** P1 = 4.7 >= 2.5 y 4.7 - 3.9 = 0.8 >= 0.5 → `areas_dominantes: ["H"]`.
- **Analogia esperada (Taller de Escritura):** "Escribir tu ensayo es como preparar un debate: antes de defender tu postura, anticipa lo que diria quien piensa distinto y respondele con evidencia."

```json
{
  "chaside": {
    "areas": { "C": 2.9, "H": 4.7, "A": 3.9, "S": 2.6, "I": 1.9, "D": 1.4, "E": 2.0 },
    "areas_dominantes": ["H"],
    "descripcion_para_analogias": "Sus intereses se orientan al area Humanisticas y Sociales. Conectar las explicaciones con analogias de debates, comunicacion persuasiva, historia y dinamicas sociales."
  }
}
```

### 5.3 Ejemplo 3: co-dominancia `C` + `S` (regla del umbral)

- **Puntajes:** `C: 4.1`, `S: 3.8`, `E: 3.2`, `H: 2.7`, `I: 2.2`, `A: 1.8`, `D: 1.5`.
- **Verificacion de la regla:** P1 = 4.1 >= 2.5 y 4.1 - 3.8 = 0.3 < 0.5 → `areas_dominantes: ["C", "S"]`.

```json
{
  "chaside": {
    "areas": { "C": 4.1, "H": 2.7, "A": 1.8, "S": 3.8, "I": 2.2, "D": 1.5, "E": 3.2 },
    "areas_dominantes": ["C", "S"],
    "descripcion_para_analogias": "Sus intereses combinan las areas Administrativas y Contables y Salud y Medicina. Conectar las explicaciones con analogias de presupuestos, inventarios y planificacion o de diagnostico, tratamiento y seguimiento."
  }
}
```

---

## 6. Acoplamiento con la PoC y preparacion para E2-03 / E2-07 / E2-10

1. **E2-03 (datos reales):** cuando el bloque IS-UTB este disponible, confirmar el formato del resultado y aplicar la normalizacion 2.2. Mientras tanto, el plan B de E2-03 usa fixtures simulados en `perfiles/` con `"origen": "simulado"`. **Atencion:** el schema actual tiene `additionalProperties: false` en la raiz, asi que el campo `origen` debe incorporarse al schema en E2-07 o el fixture no validara.
2. **E2-07 (consolidacion del schema):** se propone endurecer `chaside` con las 7 claves de `areas` requeridas, `minimum: 1` y `maximum: 5` por area, y `maxItems: 2` en `areas_dominantes`. Medido con el tokenizador de `qwen2.5:1.5b` (JSON compacto), el bloque completo ocupa entre 101 y 111 tokens en los tres ejemplos de la seccion 5: cerca de un tercio del presupuesto de 350 tokens del perfil, por lo que `descripcion_para_analogias` no debe superar las 2 oraciones.
3. **Compatibilidad con el perfil de ejemplo:** `perfiles/ejemplo-perfil-estudiante.json` registra `chaside.areas` en escala 0-10 (`I: 8`, `H: 7`, ...). Igual que se senalo en E2-04, el re-escalado a 1.0-5.0 queda para E2-07. **Este issue no modifica ese archivo.**
4. **E2-10 (Prompt Builder):** `descripcion_para_analogias` se inyecta en la seccion "Datos del estudiante" del prompt, junto con una regla fija en las instrucciones: *"Usa los intereses del estudiante solo para elegir analogias y ejemplos; no cambies el recurso recomendado, el contenido ni la dificultad por ellos, y no menciones carreras ni puntajes."* Prueba de verificacion sugerida: ejecutar el mismo perfil con y sin el bloque `chaside` y comprobar que el recurso elegido (A, B o C) no cambia.
5. **PoC actual:** `poc_slm/recommender.py` y los eventos de `poc_slm/eventos/` no usan CHASIDE; este issue no los modifica, solo fija el contrato psicopedagogico.
