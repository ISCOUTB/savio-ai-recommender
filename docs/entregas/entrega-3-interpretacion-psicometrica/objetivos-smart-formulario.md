# Formulacion del Proyecto, Objetivos SMART y Cronograma - Entrega 3

**Estado:** Listo para validacion por el docente y diligenciamiento del formulario tecnico
**Entrega:** [Entrega 3 - Interpretacion Psicometrica](README.md)
**Issues asociados:** `E3-01` ([#49](https://github.com/ISCOUTB/savio-ai-recommender/issues/49)) y `E3-02` ([#40](https://github.com/ISCOUTB/savio-ai-recommender/issues/40))
**Ventana de ejecucion y cierre:** `2026-10-23` al `2026-11-09` (presentacion y entrega completa del **3 al 9 de noviembre de 2026**)

---

## 1. Delimitacion del Problema y Caso de Estudio (Apartado Tecnico del Formulario)

### 1.1 Problema delimitado
En los procesos de acompanamiento estudiantil universitario, la aplicacion de pruebas estandarizadas de orientacion vocacional (**CHASIDE**), estilos de aprendizaje (**Modelo de Felder-Silverman**) y rasgos conductuales (**Test de Personalidad**) genera datos cuantitativos aislados que requieren tiempo y cruce manual especializado para convertirse en una lectura integral del estudiante.

Abordar la generacion o recomendacion masiva de contenidos academicos para cursos universitarios resulta inabarcable y difuso para el tiempo disponible; en cambio, el caso de estudio concreto, delimitado y medible consiste en construir un **motor backend de inferencia basado en un Modelo de Lenguaje Pequeno (SLM)** capaz de recibir las **puntuaciones originales brutas** de los tres instrumentos validados, cruzarlas con su literatura teorica oficial y generar una **interpretacion psicologica, conductual y vocacional integrada** que sirva como insumo de apoyo al diagnostico inicial sin reemplazar el criterio del profesional.

### 1.2 Restricciones de diseno e ingenieria (Directrices del docente)
1. **Rigor psicometrico estricto:** queda estrictamente prohibido alterar, reescalar o normalizar arbitrariamente los puntajes de los cuestionarios validados (como la antigua escala `1.0-5.0`), asi como inventar indices compuestos sin sustento estadistico (como `autonomia`), ya que cualquier modificacion carece de validez ante profesionales de psicologia. El sistema opera directamente sobre las puntuaciones originales brutas tal como las califican los bloques oficiales en Moodle.
2. **Estrategia Teacher-Student (LLM de frontera -> SLM especializado):** los modelos comerciales de gran escala (Claude, ChatGPT) se emplean exclusivamente en etapa de laboratorio como modelos maestros (*Teacher*), alimentados con la bibliografia oficial de CHASIDE, Felder-Silverman y Personalidad para sintetizar el conjunto de referencia (*ground truth*). El sistema final utiliza un **SLM especializado** (`0.5B` a `1.5B` parametros), dado que no requiere almacenar conocimiento enciclopedico general sino aprender a interpretar las correlaciones entre los tres cuestionarios.
3. **Independencia total de VRAM (ejecucion 100% en CPU):** dado que ni las maquinas locales del equipo ni el cluster institucional (Savio) cuentan con memoria de video dedicada (VRAM) asignada para este servicio, el ajuste se realiza mediante plataformas en la nube con capas gratuitas o gestionadas (**Hugging Face**) y el despliegue final se ejecuta con un **modelo cuantizado (formato GGUF)** optimizado para **CPU estandar**.
4. **Prioridad funcional (Backend antes que Frontend, sin sobreingenieria):** se descarta el diseno prematuro de arquitecturas complejas de microservicios o interfaces visuales decorativas. Primero se define con claridad la **entrada** y la **salida** del sistema, priorizando que el pipeline backend entregue respuestas coherentes, fieles a la psicometria y estructuradas.

### 1.3 Ficha Resumen para Diligenciamiento Directo del Formulario del Proyecto

> **Nota operativa:** El equipo diligencia unicamente estos apartados tecnicos; el docente completara los datos administrativos del grupo y lider de investigacion.

| Campo Tecnico del Formulario | Texto Oficial Listo para Copiar y Pegar |
|---|---|
| **Titulo tentativo del proyecto** | Sistema Backend de Inferencia con Modelos de Lenguaje Pequenos (SLM) Cuantizados en CPU para la Interpretacion Psicometrica y Vocacional Integrada de Estudiantes Universitarios |
| **Caso de estudio / Alcance** | Interpretacion psicologica, de estilos de aprendizaje y vocacional integrada a partir de las puntuaciones originales brutas de tres instrumentos estandarizados (CHASIDE, Modelo de Felder-Silverman y Test de Personalidad Institucional) como apoyo al diagnostico inicial estudiantil sin reemplazar al profesional. |
| **Pregunta / Problema tecnico** | Como procesar y correlacionar automaticamente las puntuaciones originales brutas de los instrumentos CHASIDE, Felder-Silverman y Test de Personalidad mediante un Modelo de Lenguaje Pequeno (SLM) especializado y cuantizado que opere 100% en CPU estandar (sin VRAM), garantizando rigor psicometrico y fidelidad frente a un corpus *ground truth* experto? |
| **Metodologia de ingenieria** | Enfoque *Teacher-Student* en tres fases sobre 4 sprints (`23 de octubre al 9 de noviembre de 2026`): (1) Estructuracion del contrato JSON de puntajes brutos sin alterar escalas y generacion de un corpus *ground truth* ($\ge 150$ perfiles) con LLMs maestros (Claude/ChatGPT) y literatura oficial; (2) Ajuste supervisado (SFT/QLoRA) de un SLM (`0.5B-1.5B`) en la nube (Hugging Face), cuantizacion a GGUF (`Q4_K_M`) para CPU estandar (`0 MB` VRAM) e integracion en un pipeline backend en Python sin frontend; (3) Validacion cuantitativa de fidelidad diagnostica ($\ge 85\%$), adherencia a guardrails eticos (`100%`) y tiempos de inferencia en CPU ($\le 60\text{ s}$). |
| **Resultados e indicadores verificables** | 1. Esquema JSON de puntajes originales brutos y corpus *ground truth* ($\ge 150$ muestras 80/20).<br>2. Artefacto SLM cuantizado en GGUF ejecutable en CPU (`0 MB` VRAM, RAM $\le 2.5\text{ GB}$) y motor backend por consola.<br>3. Reporte de validacion SMART con fidelidad $\ge 85\%$, `0` escalas alteradas y latencia en CPU documentada. |

---

## 2. Objetivo General

> **Texto para el formulario:**
> Desarrollar y validar un sistema backend de inferencia basado en un Modelo de Lenguaje Pequeno (SLM) especializado y cuantizado para ejecucion en CPU estandar, capaz de generar interpretaciones psicologicas, de estilos de aprendizaje y vocacionales integradas a partir de las puntuaciones originales brutas de los instrumentos estandarizados CHASIDE, Felder-Silverman y Test de Personalidad, como herramienta de apoyo al diagnostico inicial estudiantil en la Universidad Tecnologica de Bolivar.

---

## 3. Objetivos Especificos (Metodologia SMART)

### Objetivo Especifico 1 (OE1): Estructuracion de Datos Psicometricos Brutos y Corpus Ground Truth

> **Texto para el formulario:**
> Estructurar el contrato de datos de entrada/salida con las puntuaciones originales brutas de los tres instrumentos validados (CHASIDE, Felder-Silverman y Test de Personalidad) y construir un corpus de referencia (*ground truth*) de al menos 150 perfiles interpretados mediante LLMs de frontera (Claude/ChatGPT) fundamentados en la literatura tecnica oficial de cada prueba, entre el 23 y el 30 de octubre de 2026 (Sprints 1 y 2).

| Criterio SMART | Aplicacion concreta en OE1 |
|---|---|
| **S (Specific / Especifico)** | Definir el esquema JSON de entrada con los puntajes nativos sin alterar escalas (CHASIDE `0-14` en 7 areas, Felder-Silverman `0-11` en 4 dimensiones bipolares, Personalidad `0-9` en 8 polos), extraer los 3 perfiles reales del equipo en bruto y generar el dataset *ground truth* cruzado con la bibliografia psicometrica. |
| **M (Measurable / Medible)** | `100%` de fidelidad a las escalas originales (`0` escalas modificadas o inventadas), `1` schema JSON validado automaticamente, `3` perfiles reales en bruto y $\ge 150$ pares `(puntajes_brutos -> interpretacion_integrada)` con particion 80/20 (120 train / 30 eval). |
| **A (Achievable / Alcanzable)** | Los tres bloques ya estan instalados en el entorno local de extraccion y la sintesis del *ground truth* se realiza en lote con LLMs maestros a partir de los manuales tecnicos oficiales de los 3 tests. |
| **R (Relevant / Relevante)** | Garantiza la validez cientifica y psicometrica del sistema ante criterios profesionales de psicologia y provee los datos de alta calidad indispensables para ajustar/destilar el SLM. |
| **T (Time-bound / Temporal)** | Del **23 al 30 de octubre de 2026** (Sprints 1 y 2, con revision docente el **jueves 29 de octubre**). |

---

### Objetivo Especifico 2 (OE2): Ajuste/Destilacion en la Nube y Cuantizacion del SLM para CPU

> **Texto para el formulario:**
> Ajustar y cuantizar un Modelo de Lenguaje Pequeno (SLM de escala 0.5B a 1.5B parametros) en plataformas gestionadas en la nube (Hugging Face) a partir del corpus *ground truth*, e integrarlo en un pipeline backend de inferencia optimizado para ejecutarse 100% sobre CPU estandar sin dependencia de memoria de video (VRAM), entre el 31 de octubre y el 3 de noviembre de 2026 (Sprint 3).

| Criterio SMART | Aplicacion concreta en OE2 |
|---|---|
| **S (Specific / Especifico)** | Ejecutar el fine-tuning supervisado (SFT/QLoRA) del SLM (`Qwen 2.5 0.5B` / `1.5B`) en Hugging Face / Colab, exportar los pesos cuantizados a formato GGUF (`Q4_K_M`) e implementar el motor backend en Python (sin frontend) que procesa los puntajes brutos y produce el informe integrado. |
| **M (Measurable / Medible)** | Consumo de VRAM en despliegue igual a `0 MB` (ejecucion 100% en CPU con `num_gpu=0`), huella en memoria RAM $\le 2.5\text{ GB}$ y cumplimiento del `100%` de la estructura de 4 secciones de salida del backend. |
| **A (Achievable / Alcanzable)** | Utiliza capas gratuitas/gestionadas en la nube (Hugging Face) para el ajuste pesado y cuantizacion a 4 bits para que la inferencia corra en cualquier computador convencional o servidor CPU de Savio. |
| **R (Relevant / Relevante)** | Resuelve la restriccion critica de infraestructura del proyecto (ausencia de GPUs dedicadas en equipos locales y en el cluster Savio) y cumple la directriz de priorizar el backend funcional sobre el frontend. |
| **T (Time-bound / Temporal)** | Del **31 de octubre al 3 de noviembre de 2026** (Sprint 3, con fecha de congelamiento del modelo GGUF y del backend el **martes 3 de noviembre**). |

---

### Objetivo Especifico 3 (OE3): Validacion Cuantitativa del Diagnostico Inicial, Rendimiento en CPU y Presentacion

> **Texto para el formulario:**
> Evaluar el desempeno del sistema backend de inferencia mediante pruebas controladas sobre perfiles estudiantiles de validacion (no vistos en el ajuste), midiendo la precision/fidelidad interpretativa frente al *ground truth*, la adherencia a guardrails eticos (no emitir diagnosticos clinicos ni alterar puntajes) y los tiempos de respuesta en CPU estandar, consolidando la entrega y presentacion final entre el 3 y el 9 de noviembre de 2026 (Sprint 4).

| Criterio SMART | Aplicacion concreta en OE3 |
|---|---|
| **S (Specific / Especifico)** | Ejecutar el protocolo de evaluacion sobre el particionado de prueba (20% del dataset + los 3 perfiles reales del equipo), comparando las salidas del SLM cuantizado contra el SLM base y el *ground truth* de los LLMs maestros, y midiendo latencia/throughput en CPU. |
| **M (Measurable / Medible)** | Fidelidad de correlacion psicometrica $\ge 85\%$ en la rubrica de evaluacion contra *ground truth*, `100%` de aprobacion en pruebas de guardrails (cero invencion de puntajes o juicios clinicos) y tiempo de inferencia en CPU documentado ($\le 60\text{ s}$ por perfil integrado). |
| **A (Achievable / Alcanzable)** | La validacion se ejecuta de manera automatizada por consola sobre los equipos CPU del grupo sin requerir infraestructura externa ni interfaz grafica. |
| **R (Relevant / Relevante)** | Demuestra cientifica y tecnicamente que el SLM quedo bien destilado y cuantizado, entregando valor real como herramienta de apoyo al diagnostico inicial. |
| **T (Time-bound / Temporal)** | Del **3 al 9 de noviembre de 2026** (Sprint 4, con revision docente el **jueves 5 de noviembre** y entrega/presentacion completa en el rango del **3 al 9 de noviembre de 2026**). |

---

## 4. Definicion Formal de Entrada y Salida del Sistema (Sin Sobreingenieria)

Siguiendo el principio de ingenieria indicado por el docente (*"primero se define con claridad la entrada y la salida del sistema; luego se estructura la arquitectura necesaria"*):

### 4.1 Entrada del Backend (Puntuaciones Originales Brutas Exactas de los 3 Bloques)

El motor recibe un objeto JSON con los puntajes nativos exactos que califican los tres bloques oficiales instalados en Moodle (`ISCOUTB/chaside`, `ISCOUTB/learning_style`, `ISCOUTB/personality_test`), sin ninguna transformacion a escala `1.0-5.0`:

1. **CHASIDE (`block_chaside`, 98 items dicotomicos Si/No = 70 de interes + 28 de aptitud):**
   - Por cada una de las 7 areas oficiales se recibe el conteo bruto de **Interes** (`0 a 10`), **Aptitud** (`0 a 4`), **Total** (`0 a 14`) y porcentaje nativo del bloque (`pct_total = round(100 * total / 14, 1)`):
     - `C` (**Administrativa**): organizacion, planificacion, control y gestion de recursos.
     - `H` (**Humanidades/Sociales/Juridicas**): comunicacion, argumentacion, ciencias sociales y relacion humana.
     - `A` (**Artistica**): sensibilidad estetica, creatividad, diseno visual, musical o expresivo.
     - `S` (**Ciencias de la Salud**): cuidado, asistencia, bienestar y comprension de sistemas biologicos.
     - `I` (**Ensenanzas Tecnicas**): ingenieria, computacion, diseno de sistemas y resolucion tecnica.
     - `D` (**Defensa y Seguridad**): liderazgo, disciplina, protocolos y trabajo en equipo bajo normas.
     - `E` (**Ciencias Experimentales**): investigacion cientifica, medicion, laboratorio y analisis empirico.
2. **Modelo de Felder-Silverman (`block_learning_style`, Index of Learning Styles - ILS, 44 items A/B):**
   - Conteos brutos nativos por cada uno de los 8 polos (`0 a 11`, donde la suma de cada par bipolar es siempre `11`):
     - Dimension Procesamiento (`act_ref`): `ap_active` (Activo, `0-11`) vs. `ap_reflexivo` (Reflexivo, `0-11`).
     - Dimension Percepcion (`sen_int`): `ap_sensorial` (Sensorial/Sensitivo, `0-11`) vs. `ap_intuitivo` (Intuitivo, `0-11`).
     - Dimension Canal de Entrada (`vis_vrb`): `ap_visual` (Visual, `0-11`) vs. `ap_verbal` (Verbal, `0-11`).
     - Dimension Comprension (`seq_glo`): `ap_secuencial` (Secuencial, `0-11`) vs. `ap_global` (Global, `0-11`).
   - Diferencial oficial impar (`1, 3, 5, 7, 9, 11` hacia el polo dominante) e interpretacion por bandas originales del autor: `1-3` (equilibrio entre ambos polos), `5-7` (preferencia moderada), `9-11` (preferencia muy fuerte).
3. **Test de Personalidad Institucional (`block_personality_test`, 72 items dicotomicos Si/No, 9 items por polo):**
   - Conteos brutos independientes (`0 a 9` por polo) en los **8 polos originales** de la tabla `personality_test`, organizados en sus 4 ejes nativos (sin el indice inventado `autonomia`):
     - Eje Energia: `extraversion` (Extraversion, `0-9`) vs. `introversion` (Introversion, `0-9`).
     - Eje Percepcion: `sensing` (Sensorial, `0-9`) vs. `intuition` (Intuicion, `0-9`).
     - Eje Decision: `thinking` (Pensamiento, `0-9`) vs. `feeling` (Sentimiento, `0-9`).
     - Eje Organizacion: `judging` (Juicio/Estructura, `0-9`) vs. `perceptive` (Percepcion/Flexibilidad, `0-9`).

#### Ejemplo concreto de JSON de entrada al Backend (Puntajes Brutos Nativos)

```json
{
  "estudiante_id": "est-anon-001",
  "version_contrato": "3.0-bruto",
  "felder_silverman": {
    "activo_reflexivo": { "ap_active": 8, "ap_reflexivo": 3, "diferencial": "5a", "polo_dominante": "activo", "banda": "moderada" },
    "sensorial_intuitivo": { "ap_sensorial": 4, "ap_intuitivo": 7, "diferencial": "3b", "polo_dominante": "intuitivo", "banda": "equilibrio" },
    "visual_verbal": { "ap_visual": 9, "ap_verbal": 2, "diferencial": "7a", "polo_dominante": "visual", "banda": "moderada" },
    "secuencial_global": { "ap_secuencial": 6, "ap_global": 5, "diferencial": "1a", "polo_dominante": "secuencial", "banda": "equilibrio" }
  },
  "personalidad": {
    "extraversion": 3,
    "introversion": 7,
    "sensing": 4,
    "intuition": 8,
    "thinking": 7,
    "feeling": 3,
    "judging": 8,
    "perceptive": 2
  },
  "chaside": {
    "C": { "interes": 4, "aptitud": 2, "total": 6, "pct_total": 42.9 },
    "H": { "interes": 5, "aptitud": 2, "total": 7, "pct_total": 50.0 },
    "A": { "interes": 3, "aptitud": 1, "total": 4, "pct_total": 28.6 },
    "S": { "interes": 2, "aptitud": 1, "total": 3, "pct_total": 21.4 },
    "I": { "interes": 9, "aptitud": 4, "total": 13, "pct_total": 92.9 },
    "D": { "interes": 2, "aptitud": 1, "total": 3, "pct_total": 21.4 },
    "E": { "interes": 8, "aptitud": 3, "total": 11, "pct_total": 78.6 },
    "top_areas": ["I", "E"]
  }
}
```

### 4.2 Salida del Backend (Perfil Interpretativo Integrado en 4 Bloques)

El SLM cuantizado genera en CPU un informe estructurado en Markdown/JSON con cuatro bloques verificables y una nota etica obligatoria:

1. **Bloque 1 - Sintesis de Estilos de Aprendizaje (Felder-Silverman):** lectura de las 4 dimensiones bipolares citando los conteos brutos (`0-11`) y su ubicacion en las bandas oficiales del autor (`1-3` equilibrio, `5-7` preferencia moderada, `9-11` preferencia muy fuerte).
2. **Bloque 2 - Sintesis Conductual y de Habitos (Test de Personalidad):** caracterizacion de las preferencias de interaccion (`extraversion`/`introversion`), procesamiento (`sensing`/`intuition`), toma de decisiones (`thinking`/`feeling`) y organizacion (`judging`/`perceptive`) a partir de los puntajes brutos (`0-9`), empleando lenguaje descriptivo y no clinico.
3. **Bloque 3 - Sintesis Vocacional de Intereses y Aptitudes (CHASIDE):** identificacion de las areas predominantes (`0-14`) diferenciando explicitamente entre interes (`0-10`) y aptitud percibida (`0-4`), senalando si existe congruencia (alto interes y alta aptitud) o brecha a fortalecer (alto interes con baja aptitud o viceversa).
4. **Bloque 4 - Integracion Psicopedagogica y Vocacional Cruzada (Apoyo al Diagnostico Inicial):** correlacion integral entre los tres instrumentos (como dialogan su canal y ritmo de aprendizaje en Felder-Silverman con su estructura conductual en Personalidad y su inclinacion vocacional en CHASIDE), ofreciendo pautas orientadoras para el profesional de acompanamiento estudiantil sin emitir juicios clinicos ni reemplazar su criterio.

---

## 5. Cronograma Fechado SMART y Plan de Trabajo - Entrega 3 (`E3-02` / `#40`)

En cumplimiento del componente **T (Time-bound / Temporal)** de los Objetivos SMART y de la ventana oficial de entrega, todo el desarrollo, ajuste, validacion en CPU y preparacion de la sustentacion se ejecuta entre el **23 de octubre y el 9 de noviembre de 2026**, garantizando que en el rango del **3 al 9 de noviembre de 2026** el sistema completo este finalizado y listo para presentarse ante el docente.

### 5.1 Mapa Temporal de los 4 Sprints (`23 Oct` al `09 Nov 2026`)

| Sprint | Fechas Exactas | Objetivo SMART | Issues Asociados | Responsable Lider | Entregables de Cierre del Sprint |
|---|---|---|---|---|---|
| **Sprint 1: Formulacion SMART, Alcance y Cierre Psicometrico** | `Vie 23 Oct` al `Lun 26 Oct 2026` | Formulacion (`S, M, A, R, T`) y Transversal | `E3-01` (#49), `E3-02` (#40), `E3-03` (#38) + Cierre `#37, #39, #41` | Equipo completo (Coordina: `Persona 1`) | 1. `objetivos-smart-formulario.md` completo.<br>2. Cronograma fechado `E3-02` publicado.<br>3. Lineamientos de anonimizacion (`E3-03`).<br>4. Envio por WhatsApp al docente. |
| **Sprint 2: Datos Brutos de los 3 Tests y Corpus Ground Truth** | `Mar 27 Oct` al `Vie 30 Oct 2026` | **OE1** (100% escalas nativas, $\ge 150$ perfiles) | `E3-04` (#50), `E3-05` (#42), `E3-06` (#43) | `Persona 1` (`E3-04`), `Persona 2 y 3` (`E3-05`), `Persona 3` (`E3-06`) | 1. Schema JSON bruto `perfil-bruto-psicometrico.schema.json` y baremos.<br>2. Puntajes brutos reales de los 3 integrantes.<br>3. Corpus *ground truth* ($\ge 150$ muestras JSONL 80/20) generado con Claude/ChatGPT y literatura oficial. |
| **Sprint 3: Destilacion en Hugging Face, Cuantizacion GGUF y Backend en CPU** | `Sab 31 Oct` al `Mar 03 Nov 2026` | **OE2** (`0 MB` VRAM, RAM $\le 2.5\text{ GB}$, 100% CPU) | `E3-07` (#51), `E3-08` (#44) | `Persona 1` (`E3-07` Backend), `Persona 3` (`E3-08` SLM/GGUF) | 1. Notebook reproducible de SFT/QLoRA en Hugging Face.<br>2. Modelo SLM exportado a GGUF `Q4_K_M` en CPU (`0 MB` VRAM).<br>3. Pipeline backend en Python con validador post-inferencia.<br>4. **Congelamiento (Freeze): Martes 3 de noviembre**. |
| **Sprint 4: Validacion Psicometrica, Metricas en CPU y Presentacion Final** | `Mar 03 Nov` al `Lun 09 Nov 2026` | **OE3** (Fidelidad $\ge 85\%$, Guardrails `100%`, CPU $\le 60\text{ s}$) | `E3-09` (#52), `E3-10` (#53) | `Persona 2` (`E3-09` Metricas), Equipo completo (`E3-10` Demo) | 1. Reporte cuantitativo de fidelidad ($\ge 85\%$) y guardrails (`100%`).<br>2. Benchmark en CPU estandar (latencia, tokens/s, RAM).<br>3. Comparativa Base vs. Ajustado vs. Teacher.<br>4. Demo reproducible en consola lista para presentar (**3 al 9 de noviembre**). |

---

### 5.2 Desglose Operativo Dia a Dia y Ventana de Cierre (`3 al 9 de Noviembre`)

| Tramo de Fechas | Actividades Criticas de Ingenieria | Issues | Producto Verificable |
|---|---|---|---|
| **23 al 26 de octubre** | Redaccion de Objetivos SMART, ficha tecnica del formulario, cierre en GitHub de `#37`, `#39` y `#41`, definicion del cronograma intensivo y envio de borrador por WhatsApp al docente. | `E3-01`, `E3-02`, `E3-03` | Formulario tecnico y cronograma enviados por WhatsApp. |
| **27 al 28 de octubre** |Construccion del schema JSON de puntajes originales brutos (`0-14`, `0-11`, `0-9`), sintesis de baremos oficiales y diligenciamiento/extraccion de los tests de `persona-2` y `persona-3`. | `E3-04`, `E3-05` | Contrato JSON validado + 3 perfiles reales en bruto (`perfiles/reales/`). |
| **28 al 30 de octubre** | Diseno del Prompt Maestro (*Teacher*) con la literatura tecnica de CHASIDE, Felder-Silverman y Personalidad; generacion y curacion de $\ge 150$ perfiles interpretados en JSONL (120 train / 30 eval). **Jueves 29 Oct:** Primera sesion de revision con el docente. | `E3-06` | Corpus *ground truth* verificado y particionado 80/20. |
| **31 de octubre al 2 de noviembre** | Ejecucion del fine-tuning supervisado (SFT/QLoRA) del SLM (`Qwen 2.5 0.5B/1.5B`) en Hugging Face en paralelo con la programacion del motor backend en Python (sin frontend). | `E3-07`, `E3-08` | Pesos ajustados en Hugging Face + script backend funcional. |
| **3 de noviembre (Fecha de Congelamiento / Freeze)** | Fusion de adaptadores, cuantizacion a formato **GGUF (`Q4_K_M`)**, prueba de humo en CPU estandar (`num_gpu=0`, `0 MB` VRAM) y congelamiento de codigo y modelo para iniciar la validacion formal. | `E3-07`, `E3-08` | **Hito Freeze:** Modelo GGUF y pipeline backend congelados en CPU. |
| **3 al 5 de noviembre** | Corrida automatizada del 20% de prueba (30 perfiles) + los 3 perfiles reales en CPU; calculo de fidelidad diagnostica ($\ge 85\%$), auditoria de guardrails (`100%`) y medicion de tiempos de inferencia y RAM en CPU. **Jueves 5 Nov:** Segunda sesion de revision con el docente. | `E3-09` | Tablas de fidelidad diagnostica y benchmarks de CPU en `experimentos/bitacora.md`. |
| **6 al 9 de noviembre (Ventana Final de Presentacion)** | Consolidacion de la tabla comparativa (SLM Base vs. SLM Destilado GGUF vs. Teacher), empaquetado del guion de demostracion por consola y sustentacion/entrega final ante el docente. | `E3-09`, `E3-10` | **Entrega 3 completada al 100%** y lista para presentacion en el rango del **3 al 9 de noviembre**. |

---

### 5.3 Hitos de Revision con el Docente (WhatsApp y Sesiones de los Jueves)

| Hito | Fecha | Canal | Que se presenta / entrega al docente | Issues |
|---|---|---|---|---|
| **Hito 1: Validacion de Objetivos SMART y Formulario** | **Lunes 26 / Martes 27 de octubre de 2026** (previo al jueves 29 Oct) | WhatsApp | Resumen ejecutivo con Caso de Estudio, 1 Objetivo General, 3 Objetivos Especificos SMART y Cronograma con cierre del 3 al 9 de noviembre. | `E3-01`, `E3-02` |
| **Hito 2: Sesion de Seguimiento Jueves 1 (Cierre OE1)** | **Jueves 29 de octubre de 2026** | Sesion del jueves + WhatsApp | Formulario tecnico definitivo, contrato JSON de puntajes originales brutos (0 escalas alteradas), los 3 perfiles reales extraidos y avance del corpus *Ground Truth* con Claude/ChatGPT. | `E3-01`, `E3-04`, `E3-05`, `E3-06` |
| **Hito 3: Congelamiento de Modelo GGUF y Backend (Cierre OE2)** | **Martes 3 de noviembre de 2026** | Repositorio + WhatsApp | Evidencia del entrenamiento en Hugging Face, modelo cuantizado en GGUF corriendo 100% en CPU (`0 MB` VRAM) y salida estructurada del backend. | `E3-07`, `E3-08` |
| **Hito 4: Sesion de Seguimiento Jueves 2 y Ventana de Presentacion (Cierre OE3)** | **Jueves 5 de noviembre de 2026** (dentro del rango **3 al 9 de noviembre**) | Sesion del jueves / Sustentacion | Demostracion en vivo del backend en CPU, reporte de metricas SMART (fidelidad $\ge 85\%$, guardrails `100%`, latencia en CPU $\le 60\text{ s}$) y cierre de la Entrega 3. | `E3-09`, `E3-10` |

---

### 5.4 Camino Critico, Paralelismo y Regla de Congelamiento

1. **Secuencia del Camino Critico (cero holgura):**
   `E3-01 (#49, Formulacion SMART)` $\rightarrow$ `E3-04 (#50, Contrato Bruto)` $\rightarrow$ `E3-06 (#43, Corpus Ground Truth >=150)` $\rightarrow$ `E3-08 (#44, SFT en Hugging Face y GGUF CPU)` $\rightarrow$ `E3-09 (#52, Metricas de Fidelidad y Latencia CPU)` $\rightarrow$ `E3-10 (#53, Demo y Presentacion 3-9 Nov)`.
2. **Ramas en paralelo para cumplir el plazo del 3 al 9 de noviembre:**
   - Mientras `Persona 3` lidera la generacion del corpus *Ground Truth* (`E3-06`), `Persona 2` completa la extraccion de perfiles reales (`E3-05`) y `Persona 1` programa la estructura del pipeline backend (`E3-07`) sobre el contrato bruto de `E3-04`.
   - De este modo, el **martes 3 de noviembre** el backend ya esta listo para conectar directamente el archivo GGUF resultante de `E3-08`.
3. **Regla de Congelamiento (*Model & Backend Freeze* - 3 de noviembre de 2026):**
   - El **martes 3 de noviembre a las 23:59** se congelan los pesos GGUF del SLM y la logica del backend. Entre el **3 y el 9 de noviembre** no se agregan funciones nuevas; el equipo se dedica exclusivamente a medir metricas reales en CPU (`E3-09`), documentar evidencias y presentar (`E3-10`).

---

### 5.5 Matriz de Responsabilidades por Integrante y Mitigacion de Riesgos

| Integrante | Rol en Entrega 3 | Issues bajo su responsabilidad directa | Apoyo clave |
|---|---|---|---|
| **Persona 1** | Coordinador y Lider de Backend / Contrato de Datos | `E3-01` (#49), `E3-02` (#40), `E3-04` (#50), `E3-07` (#51), `E3-10` (#53) | Revisar extraccion de `E3-05` y auditar validador de guardrails en `E3-09`. |
| **Persona 2** | Lider de Evaluacion Psicometrica y Benchmarks en CPU | `E3-01` (#49), `E3-05` (#42), `E3-09` (#52), `E3-10` (#53) | Apoyar sintesis de baremos en `E3-04` y curacion del corpus en `E3-06`. |
| **Persona 3** | Lider Tecnico de SLM, Destilacion Cloud y Cuantizacion GGUF | `E3-01` (#49), `E3-03` (#38), `E3-05` (#42), `E3-06` (#43), `E3-08` (#44), `E3-10` (#53) | Integrar el artefacto GGUF con el backend (`E3-07`) y ejecutar comparativa en `E3-09`. |

| Riesgo Identificado | Impacto | Plan de Mitigacion Inmediato |
|---|---|---|
| Limite de cuota gratuita de GPU en Hugging Face / Colab durante `E3-08` | Alto | Usar `Qwen 2.5 0.5B` / `1.5B` con QLoRA 4-bit (entrenamiento de 150 muestras toma $< 25$ minutos) y mantener cuentas de respaldo de los 3 integrantes. |
| Latencia elevada en CPU estandar ($> 60\text{ s}$) en `E3-09` | Medio | Cuantizar en `Q4_K_M`, acotar `num_predict` a los 4 bloques estructurados y disponer tanto de `1.5B` como de `0.5B` cuantizado. |
| Alucinacion numerica del SLM al citar puntajes brutos en `E3-07` | Alto | Inyectar tabla resumen determinista desde Python y aplicar validador post-inferencia que verifique que cada puntaje citado coincida con el JSON de entrada. |

---

## 6. Resumen Ejecutivo Listo para Envio por WhatsApp al Docente (`E3-01` + `E3-02`)

> **Mensaje sugerido para enviar por WhatsApp al profesor:**
>
> Profesor, siguiendo las directrices de la ultima sesion, reestructuramos el alcance hacia la **Entrega 3 (Interpretacion Psicometrica y Vocacional con SLM en CPU)**, cerramos las consultas previas acatando el uso exclusivo de puntajes originales brutos y dejamos listos los **Objetivos SMART** y el **Cronograma** (con cierre y presentacion en la ventana del **3 al 9 de noviembre**) para el formulario:
>
> **1. Caso de estudio delimitado:** Sistema backend de inferencia con IA que recibe las **puntuaciones originales brutas** (sin alterar, reescalar ni inventar escalas) de **CHASIDE (`0-14` en 7 areas), Modelo de Felder-Silverman (`0-11` por polo en 4 dimensiones) y Test de Personalidad (`0-9` en sus 8 polos originales)**, y genera un perfil interpretativo integrado para apoyar el diagnostico inicial del estudiante sin reemplazar al profesional.
>
> **2. Objetivo General:** Desarrollar y validar un sistema backend de inferencia basado en un Modelo de Lenguaje Pequeno (SLM) especializado y cuantizado para ejecucion en CPU estandar, capaz de generar interpretaciones psicologicas, de estilos de aprendizaje y vocacionales integradas a partir de las puntuaciones originales brutas de los instrumentos estandarizados CHASIDE, Felder-Silverman y Test de Personalidad, como herramienta de apoyo al diagnostico inicial estudiantil en la Universidad Tecnologica de Bolivar.
>
> **3. Objetivos Especificos SMART y Cronograma (23 de octubre al 9 de noviembre):**
> - **OE1 - Datos brutos y Ground Truth (23 al 30 de octubre | Sprints 1 y 2):** Estructurar el contrato JSON con las puntuaciones originales brutas de los 3 tests (`0` modificaciones de escala), extraer los 3 perfiles reales del equipo y construir un corpus *ground truth* ($\ge 150$ perfiles interpretados, particion 80/20) usando LLMs maestros (Claude/ChatGPT) alimentados con la literatura tecnica oficial de cada instrumento. *(Revision: jueves 29 de octubre).*
> - **OE2 - Destilacion en Hugging Face y Cuantizacion CPU (31 de octubre al 3 de noviembre | Sprint 3):** Ajustar/destilar un SLM (`0.5B-1.5B`) en entornos gestionados en la nube (Hugging Face) y cuantizarlo a formato GGUF (`Q4_K_M`) integrado en un pipeline backend en Python (sin frontend) que opere 100% sobre CPU estandar (`0 MB` de VRAM obligatoria, $\le 2.5\text{ GB}$ RAM). *(Congelamiento de modelo y backend: martes 3 de noviembre).*
> - **OE3 - Validacion de Diagnostico, Metricas en CPU y Presentacion (3 al 9 de noviembre | Sprint 4):** Evaluar objetivamente el motor backend sobre perfiles de validacion midiendo fidelidad diagnostica frente al *ground truth* ($\ge 85\%$), cumplimiento de guardrails eticos (`100%`) y tiempos de inferencia en CPU ($\le 60\text{ s}$), dejando todo el sistema listo y documentado para su presentacion en la ventana del **3 al 9 de noviembre**. *(Revision: jueves 5 de noviembre).*
>
> Quedamos atentos a su visto bueno para volcar estos textos en el apartado tecnico del formulario antes de la sesion del jueves.
