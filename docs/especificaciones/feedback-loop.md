# Especificacion: Circuito de retroalimentacion (Feedback Loop) y metricas KPI (E2-11)

- **Identificador:** E2-11 ([#28](https://github.com/ISCOUTB/savio-ai-recommender/issues/28))
- **Sprint:** 5 (Prompt builder y feedback)
- **Dueno:** Persona 2 | **Revisor:** Persona 3
- **Depende de:** E2-07 (`docs/especificaciones/perfil-estudiante.schema.json`), E2-10 (`poc_slm/prompt_builder.py`)
- **Desbloquea:** E2-12 (Demo local Entrega 2)
- **Artefactos asociados:** `docs/especificaciones/feedback.schema.json`, `poc_slm/feedback_tracker.py`, `poc_slm/test_feedback_tracker.py` y `poc_slm/feedback/eventos_feedback.jsonl`

---

## 1. Contexto y proposito

El subsistema de recomendacion de la Entrega 2 es **no determinista**: en lugar de aplicar reglas rigidas del tipo `si perfil visual -> recurso A`, el SLM local razona en contexto sobre la interseccion entre el perfil psicopedagogico consolidado (Estilos de Aprendizaje, Personalidad y CHASIDE) y los tres recursos contrastantes de la semana (`A`, `B`, `C`).

Dado que el modelo puede variar su eleccion o producir justificaciones con distinto grado de pertinencia, el sistema requiere un **circuito de retroalimentacion (feedback loop)** posterior al consumo del recurso. Este circuito cumple tres funciones tecnicas y pedagogicas:

1. **Verificacion empirica por recomendacion:** medir con datos reportados por el estudiante si la decision del SLM acerto o fallo ("descache") en la practica.
2. **Cuantificacion mediante KPIs operativos:** calcular la **Tasa de Acierto**, la **Tasa de Descache** y la satisfaccion en escala Likert para contrastarlas contra las metas de calidad de `docs/investigacion/propuesta-destilacion-slm.md` (meta $\ge 80\%$ de acierto) y preparar la validacion motivacional bajo el modelo **ARCS / IMMS**.
3. **Curacion continua para destilacion y fine-tuning (Dataset B):** transformar los registros de acierto y descache en muestras verificadas que retroalimentan el ajuste QLoRA del modelo Student (`Qwen 2.5 0.5B`) frente al Teacher (`Qwen 2.5 3B`).

---

## 2. Instrumentos de captura de feedback

Una vez que el estudiante recibe la recomendacion generada por `poc_slm/prompt_builder.py` y revisa el recurso sugerido (`A`, `B` o `C`), el sistema recoge su valoracion mediante tres instrumentos complementarios de baja friccion:

| Instrumento | Campo en JSON | Tipo / Rango | Obligatorio | Proposito pedagogico y tecnico |
|---|---|---|---|---|
| **1. Escala binaria primaria** | `util` (`true` / `false`) y `resultado` (`"acierto"` / `"descache"`) | `boolean` / `enum` | Si | Indicador primario de efectividad: determina de forma inequivoca si el recurso recomendado le sirvio al estudiante para el objetivo de aprendizaje de la semana. |
| **2. Escala Likert complementaria** | `likert` | `integer` (`1` a `5` estrellas) | No (recomendado) | Mide el grado de adecuacion percibida (1 = nada util / inadecuado al estilo; 5 = totalmente alineado en formato, tiempo y claridad). Permite distinguir un acierto marginal (`likert = 3`) de un caso ejemplar (`likert >= 4`). |
| **3. Campo abierto cualitativo** | `comentario` | `string` (max. 500 caracteres) | No | Captura la razon concreta del estudiante (ej. *"el taller de 60 min fue muy largo"* o *"el mapa interactivo me aclaro la estructura"*). Es el insumo clave para diagnosticar descaches y corregir la justificacion en el fine-tuning. |

### 2.1 Interpretacion de la escala Likert (1 a 5 estrellas)

| Valor | Etiqueta | Interpretacion frente al recurso recomendado | Uso en el pipeline |
|:---:|---|---|---|
| **1** | Muy inadecuado | El formato o la carga chocan frontalmente con el perfil o disponibilidad del estudiante. | Cola de revision humana prioritaria (descache severo). |
| **2** | Poco util | El recurso aborda el tema pero otro formato de la semana (`A`, `B` o `C`) habria sido mas efectivo. | Cola de revision humana para re-etiquetado con Teacher. |
| **3** | Aceptable / Neutro | Cumple el objetivo basico, aunque sin ventaja clara de personalizacion. | Se contabiliza en metricas; no se promueve como muestra *gold* de entrenamiento. |
| **4** | Util y adecuado | El formato, el canal y el tiempo estimado encajan bien con las preferencias del estudiante. | Candidato positivo elegible para **Dataset B**. |
| **5** | Excelente ajuste | El recurso y el enfoque sugerido coinciden plenamente con la forma de aprender del estudiante. | Muestra positiva prioritaria (*gold standard*) para **Dataset B**. |

---

## 3. Contrato de datos (`feedback.schema.json`)

El archivo `docs/especificaciones/feedback.schema.json` formaliza cada evento de retroalimentacion bajo **JSON Schema Draft-07**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "feedback_recomendacion_entrega_2",
  "type": "object",
  "required": ["recomendacion_id", "estudiante_id", "semana", "recurso_id", "util", "resultado", "fecha"],
  "additionalProperties": false,
  "properties": {
    "recomendacion_id": { "type": "string", "minLength": 1 },
    "estudiante_id": { "type": "string", "minLength": 1 },
    "semana": { "type": "integer", "minimum": 1 },
    "recurso_id": { "type": "string", "minLength": 1 },
    "util": { "type": "boolean" },
    "likert": { "type": "integer", "minimum": 1, "maximum": 5 },
    "resultado": { "type": "string", "enum": ["acierto", "descache"] },
    "comentario": { "type": "string", "maxLength": 500 },
    "fecha": { "type": "string", "format": "date-time" }
  },
  "if": {
    "properties": { "util": { "const": true } },
    "required": ["util"]
  },
  "then": {
    "properties": { "resultado": { "const": "acierto" } }
  },
  "else": {
    "properties": { "resultado": { "const": "descache" } }
  }
}
```

### 3.1 Reglas de integridad y trazabilidad

1. **Trazabilidad con E2-10 (`recomendacion_id`):** Cada corrida de `poc_slm/prompt_builder.py` genera un identificador determinista con formato `rec-<estudiante_id>-s<semana>-<hash8>` (por ejemplo, `rec-demo-002-s1-b0557548`). Ese ID une sin ambiguedad el feedback con el perfil de entrada, el orden en que se presentaron los recursos y la respuesta exacta del SLM.
2. **Coherencia binaria (`util` <-> `resultado`):** Tanto el schema (`if/then/else`) como el validador de `poc_slm/feedback_tracker.py` garantizan que:
   - Si `util == true`, entonces `resultado == "acierto"`.
   - Si `util == false`, entonces `resultado == "descache"`.
3. **Prohibicion de campos espurios (`additionalProperties: false`):** Ningun evento puede inyectar datos personales adicionales ni campos fuera del contrato.
4. **Marca temporal estandar (`fecha`):** Cadena en formato ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`), validada sintacticamente y con `FormatChecker`.

---

## 4. Formulacion matematica de metricas (KPIs)

Sea $N$ el total de recomendaciones evaluadas con feedback valido en un periodo, curso o corte experimental ($N \ge 1$).

Definimos:
- $U$: numero de recomendaciones marcadas como utiles (`util == true`, equivalentes a `resultado == "acierto"`).
- $D$: numero de recomendaciones marcadas como no utiles (`util == false`, equivalentes a `resultado == "descache"`).

Dado que `util` es una variable binaria exhaustiva y mutuamente excluyente sobre toda recomendacion evaluada, se cumple que $U + D = N$.

### 4.1 Tasa de Acierto

$$\text{Tasa de Acierto (\%)} = \left( \frac{U}{N} \right) \times 100 = \left( \frac{\text{Recomendaciones marcadas como utiles}}{\text{Total de recomendaciones evaluadas}} \right) \times 100$$

### 4.2 Tasa de Descache

$$\text{Tasa de Descache (\%)} = \left( \frac{D}{N} \right) \times 100 = \left( \frac{\text{Recomendaciones marcadas como no utiles}}{\text{Total de recomendaciones evaluadas}} \right) \times 100$$

Ambas tasas son complementarias:

$$\text{Tasa de Acierto (\%)} + \text{Tasa de Descache (\%)} = 100\%$$

### 4.3 Puntaje Likert Promedio (Indicador complementario)

Sea $M \le N$ el subconjunto de eventos evaluados que incluyen calificacion en la escala Likert $l_i \in \{1, 2, 3, 4, 5\}$:

$$\overline{L} = \frac{1}{M} \sum_{i=1}^{M} l_i$$

### 4.4 Umbrales de aceptacion del proyecto

Alineados con la seccion 12.2 de `docs/investigacion/propuesta-destilacion-slm.md`:

| KPI | Meta objetivo | Umbral de alerta | Accion correctiva si cae en alerta |
|---|---|---|---|
| **Tasa de Acierto** | $\ge 80.0\%$ | $< 70.0\%$ | Revisar pesos de reglas en prompt (`--refuerzo`) y auditar muestras de Dataset B por tipo de perfil. |
| **Tasa de Descache** | $\le 20.0\%$ | $> 30.0\%$ | Analizar `comentario` y desglose por `recurso_id` para detectar sesgo de posicion o de canal. |
| **Likert promedio ($\overline{L}$)** | $\ge 4.0 / 5.0$ | $< 3.5 / 5.0$ | Ajustar longitud, tono empatico y especificidad de la justificacion pedagogica. |

### 4.5 Articulacion con el modelo ARCS e instrumento IMMS

Segun las convenciones pedagogicas del proyecto (`docs/entregas/README.md`), las metricas operativas de este feedback loop preparan la evaluacion motivacional bajo el modelo **ARCS** (Keller) y su instrumento **IMMS** (*Instructional Materials Motivation Survey*):

| Dimension ARCS | Como la aproxima el Feedback Loop de E2-11 |
|---|---|
| **Attention (Atencion)** | Tasa de acierto en perfiles visuales/activos cuando el formato evita saturacion textual (ej. Recurso A de 15 min). |
| **Relevance (Relevancia)** | Valoracion en `likert` y `comentario` sobre la utilidad de la justificacion y las analogias vocacionales derivadas de **CHASIDE**. |
| **Confidence (Confianza)** | Reduccion del descache asociado a sobrecarga cognitiva o falta de guia paso a paso en estudiantes con baja autonomia o alta metodicidad. |
| **Satisfaction (Satisfaccion)** | Tasa de Acierto global ($\ge 80\%$) y promedio Likert ($\overline{L} \ge 4.0$) tras completar la actividad semanal. |

---

## 5. Modulo de persistencia en Python (`poc_slm/feedback_tracker.py`)

El script `poc_slm/feedback_tracker.py` implementa la validacion, persistencia en **JSON Lines (`.jsonl`)** y calculo de KPIs. Se eligio el formato `.jsonl` (un objeto JSON valido por linea, codificado en UTF-8) porque:
1. Permite escritura incremental (*append-only*) sin reescribir todo el historial en cada evaluacion.
2. Es directamente compatible con los pipelines de entrenamiento de Hugging Face `datasets`, `unsloth` y `axolotl` definidos en E2-09.

### 5.1 Flujo de extremo a extremo

```
[Perfil JSON] + [Recursos Semana JSON]
                 |
                 v
     poc_slm/prompt_builder.py  ---> Genera recomendacion + recomendacion_id
                 |                   (opcional: --guardar-json salidas/rec.json)
                 v
     Estudiante consume recurso (A, B o C) y emite feedback (util, likert, comentario)
                 |
                 v
    poc_slm/feedback_tracker.py ---> Valida contra feedback.schema.json
                 |
                 +---> Persiste linea en poc_slm/feedback/eventos_feedback.jsonl
                 +---> Calcula KPIs (Tasa de Acierto, Tasa de Descache, Likert)
```

### 5.2 Comandos de uso y verificacion

Desde la raiz del repositorio, con el entorno virtual activo:

```bash
# 1. Ejecutar los chequeos automatizados del modulo (sin Ollama)
python poc_slm/test_feedback_tracker.py

# 2. Generar y validar el lote simulado de referencia (5 eventos ligados a E2-10)
python poc_slm/feedback_tracker.py --simular

# 3. Registrar un evento individual manualmente
python poc_slm/feedback_tracker.py \
    --recomendacion-id rec-demo-002-s1-b0557548 \
    --estudiante-id demo-002 \
    --semana 1 \
    --recurso-id tde-s1-B \
    --util --likert 5 \
    --comentario "La guia de lectura con ensayos anotados se ajusto a mi ritmo."

# 4. Registrar feedback leyendo directamente el JSON exportado por prompt_builder.py
python poc_slm/feedback_tracker.py \
    --desde-recomendacion salidas/recomendacion_demo.json \
    --no-util --likert 2 \
    --comentario "Preferia un diagrama rapido antes del taller de 60 minutos."

# 5. Consultar el reporte de metricas en consola o en JSON
python poc_slm/feedback_tracker.py --resumen
python poc_slm/feedback_tracker.py --resumen --json
```

### 5.3 Ejemplo de registro en `poc_slm/feedback/eventos_feedback.jsonl`

Cada linea del archivo `.jsonl` es un objeto autocontenido y validado:

```json
{"recomendacion_id": "rec-demo-002-s1-b0557548", "estudiante_id": "demo-002", "semana": 1, "recurso_id": "tde-s1-B", "util": true, "resultado": "acierto", "fecha": "2026-10-22T10:15:00Z", "likert": 5, "comentario": "Los dos ensayos anotados y el glosario encajaron con mi preferencia reflexiva y verbal."}
{"recomendacion_id": "rec-demo-001-s1-53ef6765", "estudiante_id": "demo-001", "semana": 1, "recurso_id": "tde-s1-C", "util": false, "resultado": "descache", "fecha": "2026-10-22T10:25:00Z", "likert": 2, "comentario": "Preferia un esquema visual corto como el mapa interactivo antes de pasar a un taller de 60 minutos."}
```

---

## 6. Como retroalimenta el Feedback Loop al Fine-Tuning del SLM

El proposito estrategico de capturar `util`, `likert` y `comentario` es cerrar el ciclo de mejora continua del modelo Student (`Qwen 2.5 0.5B`) disenado en `docs/investigacion/propuesta-destilacion-slm.md` (E2-09 y issues post-entrega E2-19 / E2-20).

### 6.1 Reglas de enrutamiento hacia el Dataset B (Psicopedagogico)

Al cruzar cada linea de `eventos_feedback.jsonl` con su recomendacion original (mediante `recomendacion_id`), el registro se clasifica en una de tres rutas:

| Condicion del evento | Clasificacion | Destino en el pipeline de Destilacion / Fine-Tuning |
|---|---|---|
| `util == true` **y** (`likert >= 4` o sin Likert) | **Acierto confirmado (*Gold Positive*)** | La tripleta `(perfil, recursos_semana, salida_modelo)` se promueve como muestra candidata validada para el **Dataset B** de ajuste supervisado (SFT / QLoRA), reforzando ese patron de razonamiento. |
| `util == true` **y** `likert == 3` | **Acierto tibio (*Neutral*)** | Se contabiliza como acierto en el KPI operativo, pero **no** entra al conjunto de entrenamiento SFT sin antes revisar si la justificacion o el descarte fueron superficiales. |
| `util == false` **o** `likert <= 2` | **Descache (*Hard Negative / Revision*)** | Entra a la **cola de curacion humana** (Personas 1 y 3). Nunca se entrena el modelo imitando una salida con `resultado == "descache"`. |

### 6.2 Proceso de correccion de descaches para reentrenamiento

Cuando un evento se marca como `"descache"` (por ejemplo, el caso documentado de `demo-001` en E2-10 donde el modelo eligio el taller `tde-s1-C` de 60 min pese a que el estudiante tenia preferencia visual marcada):

1. **Diagnostico con el comentario:** El equipo revisa el campo `comentario` del estudiante junto con el perfil y los recursos de la semana para identificar la causa raiz (ej. el SLM dio mas peso al polo `activo` que al canal `visual` y a la carga de 15 min de `tde-s1-A`).
2. **Regeneracion asistida por el Teacher (`Qwen 2.5 3B`):** Se invoca al modelo Teacher indicando la restriccion omitida para generar la justificacion y el descarte corregidos hacia el recurso adecuado (`tde-s1-A`), con validacion humana (acuerdo inter-anotador $\kappa \ge 0.7$).
3. **Incorporacion al Dataset B (SFT / QLoRA):** La tripleta corregida se incorpora a `dataset_b.jsonl` para el siguiente ciclo de ajuste QLoRA, reduciendo la probabilidad de que el Student de `0.5B` repita el mismo error en perfiles equivalentes.
4. **Insumo opcional para alineamiento de preferencias (DPO):** Dado que para un mismo `recomendacion_id` se dispone tanto de la respuesta rechazada (`descache`) como de la respuesta corregida (`acierto`), el par `(chosen, rejected)` queda listo por si en fases posteriores se aplica *Direct Preference Optimization* (DPO) sobre el Student.

### 6.3 Salvaguardas de privacidad y gobernanza de datos (E2-14)

- En el repositorio versionado (`poc_slm/feedback/eventos_feedback.jsonl`) **unicamente** se almacenan eventos correspondientes a perfiles con `"origen": "simulado"` (`demo-001`, `demo-002`, `demo-003`, `sim-*`).
- El campo `estudiante_id` utiliza identificadores pseudonimizados (nunca nombres completos, correos ni codigos estudiantiles reales), y el campo `comentario` no debe contener datos personales sensibles antes de integrarse a cualquier lote de entrenamiento.
