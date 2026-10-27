# Especificacion: Feedback loop y metricas (E2-11)

- **Identificador:** E2-11
- **Modulo:** Retroalimentacion del estudiante y KPIs del recomendador
- **Depende de:** E2-07 (perfil JSON), E2-10 (Prompt Builder semanal); captura en el Moodle local en Docker (E2-02)
- **Desbloquea:** E2-12 (demo local)
- **Artefactos:** `docs/especificaciones/feedback.schema.json`, `poc_slm/feedback_tracker.py`, `poc_slm/feedback/feedback_simulado.jsonl`

---

## 1. Proposito

El recomendador no es determinista: con el mismo perfil y los mismos recursos A/B/C puede elegir opciones distintas. No basta con revisar a mano unas cuantas salidas; hay que **medir de forma sistematica** si las recomendaciones aciertan. Este modulo define:

1. como califica el estudiante la recomendacion que recibio (instrumentos),
2. como se registra cada calificacion (contrato JSON + persistencia JSON Lines),
3. que metricas salen de esos registros (KPIs),
4. como se reutilizan los datos para el fine-tuning del SLM (E2-09) y como base de una futura validacion ARCS/IMMS.

## 2. Circuito de retroalimentacion

```
Perfil (E2-07) + Recursos A/B/C (E2-08)
        |
        v
Prompt Builder + SLM (E2-10) --> recomendacion { recomendacion_id, recurso_id, justificacion }
        |
        v
Estudiante usa el recurso de la semana
        |
        v
Actividad Feedback en Moodle (Docker, E2-02) { util, likert?, comentario? }
        |
        v
importar-moodle (MariaDB del compose + registro E2-10)  -->  feedback.jsonl  (append-only)
        |
        v
KPIs (acierto / descache, por recurso)  -->  analisis de sesgos + dataset de fine-tuning (E2-09)
```

`recomendacion_id` es la llave que une el feedback con la recomendacion que lo origino. El Prompt Builder (E2-10) debe generar ese identificador y guardar su salida con el mismo valor (ver seccion 7.1).

---

## 3. Instrumentos de feedback

| Instrumento | Campo | Obligatorio | Valores | Pregunta sugerida al estudiante |
|---|---|:---:|---|---|
| Escala binaria primaria | `util` | Si | `true` / `false` | "Te fue util el recurso recomendado esta semana?" (Si / No) |
| Escala Likert complementaria | `likert` | No | entero de 1 a 5 | "Que tan adecuado fue el formato para tu forma de estudiar?" (1 = nada adecuado, 5 = totalmente adecuado) |
| Campo abierto | `comentario` | No | texto, max. 500 caracteres | "Que cambiarias del recurso? (opcional)" |

**Criterios de diseno:**

- **Binaria primero.** Es la respuesta de menor friccion y la unica obligatoria; los KPIs base salen solo de ella. Pedir Likert o comentario obligatorios bajaria la tasa de respuesta.
- **Likert como matiz.** Separa un "util pero apenas" (`util=true`, 3 estrellas) de un acierto claro (`util=true`, 5 estrellas). Sirve para ponderar ejemplos en el dataset (seccion 7).
- **Comentario como diagnostico.** Explica *por que* hubo descache (formato, tiempo, dificultad) y alimenta la revision docente.

---

## 4. Contrato de datos: `feedback.schema.json`

Cada evento es un objeto JSON validado contra `docs/especificaciones/feedback.schema.json` (draft-07, `additionalProperties: false`).

| Campo | Tipo | Requerido | Regla |
|---|---|:---:|---|
| `recomendacion_id` | string | Si | No vacio. Llave hacia la salida del Prompt Builder. |
| `estudiante_id` | string | Si | No vacio. Seudonimizado; mismo valor que en `perfil-estudiante.schema.json`. |
| `semana` | integer | Si | `>= 1`. Coincide con `recurso-semanal.schema.json`. |
| `recurso_id` | string | Si | No vacio. Recurso recomendado (ej. `tde-s1-A`). |
| `util` | boolean | Si | Respuesta binaria del estudiante. |
| `resultado` | string | Si | `acierto` o `descache`; **debe ser coherente con `util`** (regla 4.1). |
| `likert` | integer | No | 1 a 5. |
| `comentario` | string | No | Max. 500 caracteres. |
| `fecha` | string | Si | ISO 8601 / RFC 3339 **con zona horaria** (ej. `2026-10-18T20:00:00-05:00`). |

### 4.1 Cambios de formalizacion aplicados en este issue

Se mantuvieron los mismos campos y requeridos del schema original de E2-01; ningun productor existente se rompe. Se agrego:

1. **Regla de coherencia `util` <-> `resultado`** con `if/then/else` de draft-07: `util=true` exige `resultado="acierto"` y `util=false` exige `resultado="descache"`. Sin esa regla el schema aceptaba eventos contradictorios que distorsionaban los KPIs.
2. **`maxLength: 500` en `comentario`**, para limitar texto libre y el riesgo de que se cuelen datos personales.
3. **`description` en cada campo**, con el significado y la relacion con los otros schemas.

**Nota sobre `format: date-time`:** la libreria `jsonschema` no verifica formatos sin dependencias extra. Por eso `feedback_tracker.py` valida la fecha por su cuenta (ISO 8601 con zona horaria obligatoria).

### 4.2 Ejemplo valido

```json
{"recomendacion_id": "rec-001", "estudiante_id": "demo-001", "semana": 1, "recurso_id": "tde-s1-A", "util": true, "resultado": "acierto", "fecha": "2026-10-18T21:21:52-05:00", "likert": 4, "comentario": "El mapa me ayudo"}
```

---

## 5. KPIs

### 5.1 Formulas

Sea **N** el total de recomendaciones evaluadas (recomendaciones con al menos un feedback valido):

```
Tasa de Acierto  (%) = (Recomendaciones con util = true  / N) * 100
Tasa de Descache (%) = (Recomendaciones con util = false / N) * 100
```

Propiedades:

- `Tasa de Acierto + Tasa de Descache = 100%` (la escala es binaria y obligatoria).
- Si `N = 0`, las tasas no estan definidas y se reportan como `n/a`, no como 0%.

### 5.2 Reglas de conteo

1. **Una recomendacion cuenta una vez.** Si un estudiante cambia su respuesta, el registro conserva ambos eventos (es append-only), pero el KPI usa **el ultimo registrado** de cada `recomendacion_id`. El denominador son recomendaciones, no eventos.
2. **Los eventos invalidos no cuentan.** Las lineas que no pasan el schema se informan por consola y se excluyen.
3. **Los KPIs se reportan siempre con su `N`.** Una tasa de 100% con N = 3 no dice lo mismo que con N = 300. Para comparar recursos se recomienda al menos 10 evaluaciones por recurso.

### 5.3 Metricas complementarias

| Metrica | Definicion | Uso |
|---|---|---|
| Tasa de acierto/descache **por recurso** | Las mismas formulas, filtradas por `recurso_id` | Detectar si una opcion (A, B o C) falla mas que las otras o si el modelo la elige demasiado (riesgo 4.3 de `materia-piloto-recursos.md`) |
| Likert promedio | Media de `likert` entre las recomendaciones que lo tienen, reportando cuantas respuestas hubo | Intensidad de la satisfaccion |
| Contradicciones util/Likert | `util=true` con 1-2 estrellas, o `util=false` con 4-5 estrellas | Senal de respuesta poco confiable; esos ejemplos no se usan para entrenar sin revision |
| Duplicados descartados | Eventos registrados menos recomendaciones evaluadas | Calidad del registro |

---

## 6. Persistencia: `poc_slm/feedback_tracker.py`

### 6.1 Formato JSON Lines

Cada evento se agrega como **una linea JSON** al final del archivo (`.jsonl`, UTF-8). Se eligio este formato porque:

- **es append-only:** registrar no reescribe el archivo, se puede auditar y un fallo a mitad de escritura afecta como mucho la ultima linea;
- **se procesa por linea:** una linea danada no invalida el resto (el script la omite y avisa);
- **es compatible con el entrenamiento:** JSONL es el formato habitual de los datasets de fine-tuning (Hugging Face `datasets`, Unsloth, etc.).

### 6.2 Archivos

| Archivo | Contenido | En git |
|---|---|:---:|
| `poc_slm/feedback/feedback.jsonl` | Feedback real (valor por defecto de `registrar` y `kpis`) | No (`.gitignore`, contiene datos de estudiantes) |
| `poc_slm/feedback/feedback_simulado.jsonl` | 30 eventos simulados, semilla 42, sobre `poc_slm/recursos/semana_1.json` | Si (evidencia reproducible del modulo) |

Los eventos simulados se reconocen por sus ids: `recomendacion_id` = `sim-s<semana>-<n>` y `estudiante_id` = `sim-est-<n>`. **No son datos medidos** y no deben reportarse como resultados del recomendador.

### 6.3 Funciones

| Funcion | Que hace |
|---|---|
| `construir_evento(...)` | Arma el evento y **deriva `resultado` de `util`**, para que el productor no pueda contradecirlos |
| `validar_evento(evento, schema)` | Valida contra el schema y la fecha ISO 8601 con zona horaria; lanza `ValueError` con el campo que falla |
| `registrar_feedback(evento, archivo)` | Valida y agrega la linea al `.jsonl` |
| `cargar_feedback(archivo)` | Lee el `.jsonl`, omite y reporta las lineas invalidas |
| `calcular_kpis(eventos)` | KPIs globales y por recurso con las reglas de la seccion 5.2 |
| `simular_feedback(...)` | Genera eventos simulados reproducibles (misma semilla = mismo archivo) |

E2-10 y E2-12 pueden importar estas funciones directamente (`from feedback_tracker import registrar_feedback, construir_evento`), con el mismo patron de `sys.path` que usa `benchmarks/benchmark.py`.

### 6.4 Uso (desde la raiz del repo, con `.venv` activo)

```bash
# Registrar un feedback
python poc_slm/feedback_tracker.py registrar --recomendacion-id rec-001 --estudiante-id demo-001 \
    --semana 1 --recurso-id tde-s1-A --util si --likert 4 --comentario "El mapa me ayudo"

# Regenerar el feedback simulado (reproducible)
python poc_slm/feedback_tracker.py simular --n 30 --semilla 42 --sobrescribir

# Calcular KPIs de un archivo
python poc_slm/feedback_tracker.py kpis --archivo poc_slm/feedback/feedback_simulado.jsonl
```

### 6.5 Verificacion realizada

Salida de `simular --n 30 --semilla 42 --sobrescribir` (datos **simulados**, `--prob-util 0.7`):

```
  Eventos registrados:        30
  Duplicados descartados:     0
  Recomendaciones evaluadas:  30
  Tasa de acierto:            80.00% (24)
  Tasa de descache:           20.00% (6)
  Likert promedio (1-5):      3.76 (n=25)
  Contradicciones util/likert: 0
  Por recurso:
    tde-s1-A: n=8  acierto=100.00%  descache=0.00%  likert=4.33
    tde-s1-B: n=14  acierto=71.43%  descache=28.57%  likert=3.82
    tde-s1-C: n=8  acierto=75.00%  descache=25.00%  likert=3.25
```

Casos negativos comprobados:

- `likert` fuera de rango y `semana = 0` se rechazan con el campo que falla;
- un `resultado` contradictorio con `util`, una fecha sin zona horaria y una linea que no es JSON se omiten con aviso;
- un `recomendacion_id` duplicado cuenta una sola vez (gana el ultimo evento);
- dos simulaciones con la misma semilla producen archivos identicos.

### 6.6 Captura real desde Moodle en Docker

El feedback real no se digita a mano: el estudiante responde en el Moodle local que levanta `moodle/docker-compose.yml` (E2-02) y `importar-moodle` lo trae al `.jsonl`. Se usa la actividad **Feedback** que ya viene con Moodle (`mod_feedback`), asi que no se crea ningun plugin.

**Configuracion de la actividad (una por semana):**

| Ajuste | Valor |
|---|---|
| Nombre | `Feedback semana <n>` (ej. `Feedback semana 1`) |
| Registrar nombres de usuario | **No anonimo** (las respuestas anonimas no se pueden unir con la recomendacion y se omiten) |
| Pregunta 1 | Opcion multiple, una respuesta, **Etiqueta `util`**, opciones `Si` / `No`, obligatoria |
| Pregunta 2 | Opcion multiple, una respuesta, **Etiqueta `likert`**, opciones `1` a `5` en ese orden, opcional |
| Pregunta 3 | Respuesta de texto largo, **Etiqueta `comentario`**, opcional |

El texto visible de cada pregunta es el de la seccion 3; el script solo mira la **Etiqueta**.

**Como se une con las dependencias:**

| Campo del evento | Origen |
|---|---|
| `estudiante_id` | Campo "Numero de ID" (`idnumber`) del usuario en Moodle. Debe ser el mismo seudonimo del perfil (E2-07). Si esta vacio se usa `moodle-<userid>`. |
| `recomendacion_id`, `recurso_id` | Registro del Prompt Builder (E2-10) en `poc_slm/recomendaciones/semana_<n>.jsonl`, buscado por `(estudiante_id, semana)` (seccion 7.1) |
| `util`, `likert`, `comentario` | Respuestas de la actividad, por etiqueta |
| `fecha` | Hora de envio de la respuesta en Moodle, en zona `-05:00` |

**Como lee los datos:** ejecuta `docker compose -f moodle/docker-compose.yml exec db mariadb ...` sobre el servicio `db` del compose. No hace falta exponer el puerto de la base ni instalar un driver MySQL en Python. Las credenciales por defecto son las del compose y se pueden cambiar con las variables `MOODLE_DB_USER`, `MOODLE_DB_PASSWORD`, `MOODLE_DB_NAME` y `MOODLE_DB_PREFIX`.

```bash
cd moodle && docker compose up -d && cd ..
python poc_slm/feedback_tracker.py importar-moodle --semana 1
python poc_slm/feedback_tracker.py kpis
```

**Reglas:**

- Se puede ejecutar varias veces: una respuesta ya importada (misma `recomendacion_id` y `fecha`) no se repite. Si el estudiante edita su respuesta en Moodle, cambia la fecha, entra como evento nuevo y el KPI usa la ultima (regla 5.2.1).
- Las respuestas anonimas, sin recomendacion en E2-10 o con valores invalidos se omiten y se informan por consola.
- Si Docker no esta disponible, el comando falla con un mensaje claro. El respaldo sigue siendo `registrar` / `simular` (criterio de bloqueo de E2-02).

**Verificacion realizada:** con respuestas de prueba en el mismo formato que devuelve la consulta se importaron 3 respuestas validas y se omitieron con aviso una anonima, una sin recomendacion y una con opcion fuera de rango. Al reimportar no se agrego ninguna linea. **Pendiente:** probar contra un contenedor real, porque en el equipo donde se escribio esto no hay Docker instalado.

---

## 7. Uso de los datos para el fine-tuning del modelo

El feedback es la senal que dice **cuales decisiones del modelo fueron buenas** desde el punto de vista del estudiante. Por si solo no basta para entrenar: hay que unirlo con lo que el modelo vio y respondio.

### 7.1 Union con el registro de recomendaciones (requisito para E2-10)

Para que el feedback sirva de dato de entrenamiento, el Prompt Builder (E2-10) debe guardar cada recomendacion con al menos:

| Campo propuesto | Contenido |
|---|---|
| `recomendacion_id` | La misma llave que el feedback |
| `estudiante_id` | Para unir con el perfil (`perfil-estudiante.schema.json`) |
| `semana` | Para unir con `poc_slm/recursos/semana_<n>.json` |
| `modelo` | Modelo y version que genero la salida (ej. `qwen2.5:1.5b`) |
| `prompt` | Prompt completo enviado al modelo |
| `recurso_id` | Recurso elegido |
| `justificacion` | Texto de la justificacion pedagogica |

`feedback.recomendacion_id = recomendacion.recomendacion_id` da la tupla completa **(perfil, recursos A/B/C, salida del modelo, juicio del estudiante)**, que es la unidad del dataset B de `docs/investigacion/destilacion-finetuning.md`.

### 7.2 Como se usa cada tipo de evento

| Evento | Uso en el pipeline de E2-09 |
|---|---|
| **Acierto confiable** (`util=true`, `likert >= 4`, sin contradiccion) | Ejemplo positivo para el dataset B: entrada = perfil + recursos, salida = recurso elegido + justificacion. Sirve para SFT/LoRA del student o para filtrar las salidas del teacher en la destilacion. |
| **Acierto debil** (`util=true`, `likert = 3` o sin Likert) | Se puede usar con menor peso, o solo si el ejemplo esta poco representado. |
| **Descache** (`util=false`) | (a) **Revision docente:** el docente marca cual recurso debio recomendarse y el ejemplo corregido entra al dataset. (b) **Par de preferencia** (recurso corregido vs. recurso descartado) si mas adelante se prueba un ajuste por preferencias tipo DPO. (c) **Diagnostico** de sesgos por recurso y por tipo de perfil. |
| **Contradiccion util/Likert** | Se excluye del entrenamiento hasta que alguien la revise. |
| **Comentario** | No entra tal cual al dataset: puede tener datos personales. Se usa para entender los descaches y solo pasa al dataset despues de anonimizarlo. |

### 7.3 Evaluacion del modelo

La tasa de acierto es tambien la **metrica de calidad** que E2-09 compara entre modelos: baseline del student sin ajuste vs. student ajustado vs. teacher, con el mismo conjunto de perfiles. Para que la comparacion sea justa:

- la meta de tasa de acierto se fija **despues** de medir el baseline con datos reales, no antes;
- las tasas por recurso se revisan junto con la global, para que una mejora global no oculte que el modelo dejo de recomendar una de las opciones.

### 7.4 Base para la validacion ARCS/IMMS

El modelo ARCS (Keller) evalua la motivacion en cuatro dimensiones: Atencion, Relevancia, Confianza y Satisfaccion. Su instrumento IMMS es un cuestionario Likert extenso. El feedback de este issue **no lo reemplaza**: la pregunta binaria y la Likert de una sola pregunta miden sobre todo la utilidad percibida, cercana a Relevancia y Satisfaccion. Lo que se deja preparado para esa validacion posterior:

- la llave `recomendacion_id` / `estudiante_id`, para unir las respuestas IMMS con las recomendaciones;
- el patron JSONL + schema, para registrar el cuestionario con otro schema sin cambiar el pipeline.

---

## 8. Limitaciones conocidas

1. **Utilidad percibida no es aprendizaje.** Un estudiante puede marcar "util" el recurso mas corto aunque aprenda menos. Validar contra el desempeno (notas de Moodle) queda fuera del alcance de la Entrega 2.
2. **Sesgo de no respuesta.** Los estudiantes que responden pueden no representar a todo el grupo. Conviene reportar la tasa de respuesta (feedback recibidos / recomendaciones emitidas) cuando exista el registro de E2-10.
3. **Los datos simulados no son evidencia.** `feedback_simulado.jsonl` solo prueba que el modulo funciona; sus tasas dependen de `--prob-util` y no dicen nada del modelo.
4. **Privacidad.** `estudiante_id` debe estar seudonimizado y el feedback real no se versiona en git.

---

## 9. Criterios de aceptacion

- [x] `docs/especificaciones/feedback.schema.json` formalizado y validado (seccion 4 y 6.5).
- [x] Formulas de los KPIs de acierto y descache documentadas (seccion 5).
- [x] `poc_slm/feedback_tracker.py` registra correctamente eventos de feedback simulados (seccion 6.5).
- [x] Documento `docs/especificaciones/feedback-loop.md` completado.
