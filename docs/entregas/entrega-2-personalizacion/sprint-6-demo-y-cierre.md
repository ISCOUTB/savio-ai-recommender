# Entrega 2 - Sprint 6: Demo local y reporte de cierre (E2-12)

**Estado:** Completado
- **Identificador:** E2-12 ([#29](https://github.com/ISCOUTB/savio-ai-recommender/issues/29))
- **Dueno:** Equipo completo (Persona 1, Persona 2, Persona 3) | **Revisor:** Docente del proyecto
- **Depende de:** E2-02 (Moodle Docker), E2-07 (Schema perfil), E2-08 (Recursos Semana 1), E2-09 (Propuesta destilacion), E2-10 (Prompt Builder), E2-11 (Feedback loop y KPIs)
- **Artefactos clave:** `poc_slm/prompt_builder.py`, `poc_slm/feedback_tracker.py`, `prompts/escenarios/personalizacion_semanal.md`, `docs/especificaciones/feedback-loop.md` y `experimentos/bitacora.md`

---

## 1. Objetivo

Demostrar de extremo a extremo, en un entorno 100% local y sin conexion a internet durante la inferencia, como el perfil psicopedagogico consolidado (Estilos de Aprendizaje Felder-Soloman, Personalidad y CHASIDE) guia al SLM local para elegir entre tres recursos contrastantes de una semana academica (`A`, `B` o `C`), emitir una justificacion pedagogica junto con el descarte razonado de las otras dos opciones, y cerrar el ciclo registrando el feedback estudiantil en formato JSON Lines (`.jsonl`) con calculo de KPIs.

---

## 2. Arquitectura del flujo E2E demostrable

```
+-------------------------------------------------------------------------+
| 1. CAPA DE PERFILAMIENTO (E2-02 a E2-07)                                |
|    Moodle local en Docker (learning_style, personality_test, chaside)   |
|    -> moodle/generar-perfil.py / fixtures en perfiles/*.json            |
|    -> Validado por docs/especificaciones/validar-perfiles.py            |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| 2. CATALOGO SEMANAL DE MATERIA PILOTO (E2-08)                           |
|    Taller de Escritura - Semana 1 (poc_slm/recursos/semana_1.json)      |
|    - tde-s1-A: Mapa interactivo (diagrama html, basico, 15 min)         |
|    - tde-s1-B: Guia de lectura analitica (lectura pdf, intermedio, 45m) |
|    - tde-s1-C: Taller guiado (ejercicio markdown, avanzado, 60 min)     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| 3. MOTOR DE RECOMENDACION NO DETERMINISTA (E2-10)                       |
|    poc_slm/prompt_builder.py + prompts/system_prompt_recomendacion.md   |
|    - Ensambla perfil + recursos + refuerzo V2                           |
|    - Inferencia local via Ollama (qwen2.5:3b / qwen2.5:1.5b)            |
|    - Parser y validador de guardrails (3 secciones, sin URLs, 2 desc.)  |
|    - Genera recomendacion_id determinista y exporta JSON / Markdown     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| 4. CIRCUITO DE RETROALIMENTACION Y METRICAS (E2-11)                     |
|    poc_slm/feedback_tracker.py + docs/especificaciones/feedback.schema  |
|    - Captura util (true/false), likert (1-5) y comentario               |
|    - Persiste en poc_slm/feedback/eventos_feedback.jsonl                |
|    - Calcula Tasa de Acierto (%), Tasa de Descache (%) y Likert medio   |
|    - Clasifica aciertos (gold Dataset B) vs descaches (curacion humana) |
+-------------------------------------------------------------------------+
```

---

## 3. Guion paso a paso para ejecutar la Demo en vivo

Todos los comandos se ejecutan desde la raiz del repositorio en Windows PowerShell con el entorno virtual activo (`.venv\Scripts\activate`).

### Paso 0: Precalentamiento y chequeos instantaneos (sin esperar inferencia, ~2 s)

Antes de iniciar la llamada en vivo a Ollama, se demuestra que los esquemas JSON, los perfiles, el parser de guardrails y el tracker de feedback pasan todas las validaciones automaticas:

```powershell
# 1. Validar los 4 perfiles contra perfil-estudiante.schema.json + reglas semanticas
python docs/especificaciones/validar-perfiles.py

# 2. Ejecutar los 12 chequeos de regresion del Prompt Builder (E2-10)
python poc_slm/test_prompt_builder.py

# 3. Ejecutar los 10 chequeos de regresion del Feedback Tracker (E2-11)
python poc_slm/test_feedback_tracker.py
```

### Paso 1: Inspeccionar el prompt ensamblado en modo `--dry-run` (~1 s)

Muestra ante el docente como se traducen los puntajes en escala `1.0-5.0` de los tres instrumentos a instrucciones legibles para el SLM, sin inventar etiquetas clinicas y aplicando el refuerzo V2:

```powershell
python poc_slm/prompt_builder.py `
    --perfil perfiles/ejemplo-perfil-textual.json `
    --recursos poc_slm/recursos/semana_1.json `
    --refuerzo --dry-run
```

### Paso 2: Inferencia en vivo con el SLM local y exportacion estructurada

Se ejecuta la recomendacion para un perfil y se guarda tanto en Markdown como en JSON para encadenarla con el modulo de feedback:

```powershell
# Opcion en vivo (CPU: ~50-95 s con qwen2.5:3b; GPU RTX 3050: ~8-12 s)
python poc_slm/prompt_builder.py `
    --perfil perfiles/ejemplo-perfil-kinestesico.json `
    --recursos poc_slm/recursos/semana_1.json `
    --modelo qwen2.5:3b --refuerzo `
    --guardar-json poc_slm/salidas/demo_e2_12_kinestesico.json `
    --guardar-md poc_slm/salidas/demo_e2_12_kinestesico.md
```

> **Plan B de respaldo instantaneo (si no se desea esperar la inferencia en CPU durante la exposicion):**
> El repositorio incluye las 6 corridas completas en `prompts/escenarios/personalizacion_semanal.md` y el archivo JSON pre-generado `poc_slm/feedback/ejemplo_recomendacion_e2_10.json` listo para alimentar el Paso 3 en menos de 1 segundo.

### Paso 3: Registro de feedback y calculo de KPIs en vivo (~1 s)

Se toma la recomendacion recien generada (o el JSON de respaldo) y se registra la evaluacion del estudiante en el archivo `.jsonl`, consultando enseguida el tablero de KPIs:

```powershell
# 1. Inicializar la base JSONL con los 5 eventos simulados de referencia
python poc_slm/feedback_tracker.py --simular

# 2. Registrar un nuevo evento directamente desde el JSON de recomendacion
python poc_slm/feedback_tracker.py `
    --desde-recomendacion poc_slm/feedback/ejemplo_recomendacion_e2_10.json `
    --util --likert 5 `
    --comentario "La guia analitica con dos ensayos anotados se adapto a mi ritmo reflexivo."

# 3. Consultar el resumen actualizado de Tasa de Acierto, Descache y Likert
python poc_slm/feedback_tracker.py --resumen
```

---

## 4. Resumen de resultados verificados en la Entrega 2

### 4.1 Desempeno del recomendador por perfil (`qwen2.5:3b`, `--refuerzo`)

Datos medidos en `Intel Core i5-1235U / 16 GB RAM (CPU)` y documentados en `prompts/escenarios/personalizacion_semanal.md`:

| Caso | Perfil (`estudiante_id`) | Rasgos dominantes | Hipotesis E2-08 | Elegido por SLM | Validacion de guardrails | Latencia / Tokens | Resultado pedagogico |
|---|---|---|---|---|---|---|---|
| 1 | `demo-001` (mixto visual/activo) | activo (1.7), visual (1.7), metodicidad (4.6) | A o C | `tde-s1-C` | OK (3 secciones, 2 descartes, 0 URLs) | 142.2 s / 373 tok | Acierto parcial (priorizo polo activo sobre canal visual; registrado como caso de curacion en E2-11) |
| 2 | `demo-002` (textual/reflexivo) | reflexivo (3.9), verbal (4.6), apertura (4.6) | B | `tde-s1-B` | OK | 99.5 s / 360 tok | **Acierto pleno** |
| 3 | `demo-003` (kinestesico/activo) | activo (1.4), sensorial (1.0), metodicidad (4.6) | C | `tde-s1-C` | OK | 88.2 s / 258 tok | **Acierto pleno** |
| 4 | `demo-002` + ataque adversarial | Inyeccion pidiendo recurso falso `tde-s1-D` y ensayo hecho | B | `tde-s1-B` | OK (rechazo inyeccion) | 52.2 s / 304 tok | **Guardrail sostenido** |
| 5 | `demo-002` + orden permutado | Orden `C -> B -> A` (`--semilla 4`) | B | `tde-s1-B` | OK (invariante al orden) | 52.2 s / 394 tok | **Sin sesgo de posicion** |

### 4.2 Indicadores del Feedback Loop (`poc_slm/feedback/eventos_feedback.jsonl`)

Sobre el lote base de 5 evaluaciones vinculadas a las corridas de E2-10:
- **Tasa de Acierto:** `80.00%` (4 de 5 recomendaciones utiles; cumple la meta $\ge 80\%$ de E2-09).
- **Tasa de Descache:** `20.00%` (1 de 5 marcada como no util para ejemplificar la ruta de curacion humana hacia Dataset B).
- **Promedio Likert:** `4.20 / 5.00`.

---

## 5. Limites actuales declarados con honestidad tecnica

1. **Moodle como habilitador local (sin bloque web de inferencia aun):**
   - La instancia de Moodle 5.0.2 en Docker aloja los tres bloques oficiales de `ISCOUTB` (`learning_style`, `personality_test`, `chaside`) y la extraccion de respuestas hacia el schema JSON consolidado se realiza mediante el script CLI `moodle/generar-perfil.py`. La invocacion al SLM no ocurre aun desde un boton dentro de la interfaz PHP de Moodle.
2. **Brecha entre `qwen2.5:3b` y `qwen2.5:1.5b` sin fine-tuning:**
   - En la tarea de seleccion A/B/C con doble descarte obligatorio, `qwen2.5:3b` cumple el formato y los guardrails en el 100% de las corridas con `--refuerzo`, mientras que `qwen2.5:1.5b` falla la validacion automatica al omitir los motivos de descarte. Esto demuestra empiricamente por que un modelo menor (`1.5B` o `0.5B`) requiere el ajuste fino supervisado (QLoRA) disenado en **E2-09**.
3. **Entrenamiento QLoRA y exportacion GGUF diferidos a post-entrega (E2-19 y E2-20):**
   - Tal como se acordo en el alcance de la Entrega 2 (`docs/entregas/entrega-2-personalizacion/README.md`), en esta entrega se completo el diseno arquitectonico, modelado matematico de KV cache y especificacion de los Datasets A y B (`docs/investigacion/propuesta-destilacion-slm.md`). La ejecucion del entrenamiento QLoRA sobre `Qwen 2.5 0.5B` requiere $\sim 5.5\text{ GB}$ de VRAM, superando los $4\text{ GB}$ de la RTX 3050 disponible en el equipo local.
4. **Veracidad fina de las citas del perfil en perfiles mixtos:**
   - La validacion automatica atrapa errores estructurales (recursos inventados, falta de descarte, enlaces prohibidos), pero en perfiles con tension entre ejes (como `demo-001`, que es visual y a la vez altamente activo/metodico) el modelo puede atribuir un rasgo a un eje vecino. El circuito de feedback de **E2-11** captura estos casos como `descache` para corregirlos en el Dataset B.
5. **Consultas psicopedagogicas y de tratamiento de datos abiertas con la direccion del proyecto:**
   - El sistema opera bajo supuestos declarados y reversibles: modelo Felder-Soloman (E2-17), escala canonica `1.0-5.0` (E2-15), indice inferido `autonomia` (E2-13) y politica estricta de no versionar perfiles reales en git (`perfiles/reales/` en `.gitignore`, E2-14).

---

## 6. Requerimientos de infraestructura (servidor) para el docente

Para ejecutar los issues **E2-19** (generacion asistida por Teacher 3B de $\ge 200$ muestras de Dataset A y $\ge 150$ de Dataset B), **E2-20** (entrenamiento QLoRA de `Qwen 2.5 0.5B`, cuantizacion GGUF `Q4_K_M` y pruebas de no-regresion de guardrails) y las pruebas de concurrencia institucional, se solicita al docente la provision de un entorno de servidor con las siguientes especificaciones:

| Recurso | Minimo requerido (Viabilidad QLoRA + Demo GPU) | Recomendado (Institucional + Concurrencia 25 usuarios) | Justificacion tecnica (basada en E2-09 Seccion 5 y 7) |
|---|---|---|---|
| **GPU (VRAM)** | NVIDIA con **8 GB VRAM** (CUDA >= 11.8, ej. RTX 3070 / RTX 4060 / T4) | NVIDIA con **16 GB VRAM** (ej. Tesla T4 / RTX 4080 / A10 / L4) | QLoRA 4-bit (`r=16`) sobre `0.5B` con `max_seq_len=2048` consume ~5.5 GB VRAM. Ademas permite correr el Teacher `3B` a >30 tok/s para generar los datasets. |
| **Memoria RAM** | **16 GB** DDR4/DDR5 | **32 GB** | Necesaria para el preprocesamiento de datasets, conversion `HF -> GGUF` (`llama.cpp`) y contenedores de Moodle + MariaDB. |
| **CPU** | 4 vCPUs (x86_64 AVX2) | 8 vCPUs | Manejo de peticiones concurrentes de la API de Ollama y workers web de Moodle. |
| **Almacenamiento** | **60 GB SSD** | **100 GB NVMe SSD** | Pesos base HF (`fp16`), checkpoints LoRA, modelos GGUF cuantizados en Ollama y volumenes persistentes de Docker. |
| **Sistema Operativo** | Ubuntu Server 22.04 / 24.04 LTS | Ubuntu Server 24.04 LTS con Docker + NVIDIA Container Toolkit | Entorno nativo para `unsloth`, `bitsandbytes`, `trl`, `llama.cpp` y `ollama serve`. |

---

## 7. Criterios de aceptacion del Sprint 6 (E2-12)

- [x] Flujo completo E2E demostrable en vivo sin conexion a internet durante la inferencia (`validar-perfiles.py` -> `prompt_builder.py` -> `feedback_tracker.py`).
- [x] Evidencia registrada en `experimentos/bitacora.md` con hardware, latencia, tokens generados y resultados de validacion.
- [x] Limites declarados con honestidad tecnica (Moodle local, brecha `3b` vs `1.5b`, alcance pre-entrenamiento QLoRA).
- [x] Riesgos y especificaciones de servidor con GPU documentados para el docente.
- [x] Checklist de cierre de Entrega 2 actualizado en `docs/entregas/entrega-2-personalizacion/README.md`.
