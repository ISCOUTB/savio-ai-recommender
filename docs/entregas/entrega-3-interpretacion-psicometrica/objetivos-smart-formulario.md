# Formulacion del Proyecto y Objetivos SMART - Entrega 3

**Estado:** En revision (borrador listo para validacion por el docente y diligenciamiento del formulario tecnico)
**Entrega:** [Entrega 3 - Interpretacion Psicometrica](README.md)
**Issue asociado:** `E3-01` y `E3-02` ([#40](https://github.com/ISCOUTB/savio-ai-recommender/issues/40))

---

## 1. Delimitacion del Problema y Caso de Estudio (Apartado Tecnico del Formulario)

### 1.1 Problema delimitado
En los procesos de acompanamiento estudiantil universitario, la aplicacion de pruebas estandarizadas de orientacion vocacional (**CHASIDE**), estilos de aprendizaje (**Modelo de Felder-Silverman**) y rasgos conductuales (**Test de Personalidad**) genera datos cuantitativos aislados que requieren tiempo y cruce manual especializado para convertirse en una lectura integral del estudiante.

Abordar la generacion masiva de contenidos academicos resulta inviable y difuso para el alcance de un proyecto de ingenieria aplicada; en cambio, el reto tecnico concreto y medible consiste en construir un **motor backend de inferencia basado en un Modelo de Lenguaje Pequeno (SLM)** capaz de recibir las **puntuaciones originales brutas** de los tres instrumentos validados, cruzarlas con su literatura teorica oficial y generar una **interpretacion psicologica, conductual y vocacional integrada** que sirva como insumo de apoyo al diagnostico inicial sin reemplazar el criterio del profesional.

### 1.2 Restricciones de diseno e ingenieria
1. **Rigor psicometrico estricto:** se prohibe alterar, reescalar o normalizar arbitrariamente los puntajes de los cuestionarios validados, asi como inventar indices derivados sin sustento estadistico. El sistema opera directamente sobre las escalas nativas de cada instrumento.
2. **Estrategia Teacher-Student (LLM de frontera -> SLM especializado):** los modelos comerciales de gran escala (Claude, ChatGPT) se emplean exclusivamente en etapa de laboratorio como modelos maestros (*Teacher*), alimentados con la bibliografia oficial de CHASIDE, Felder-Silverman y Personalidad para sintetizar el conjunto de referencia (*ground truth*). El sistema final utiliza un **SLM especializado**.
3. **Independencia total de VRAM (ejecucion en CPU):** dado que ni las maquinas locales del equipo ni el cluster institucional (Savio) cuentan con memoria de video dedicada (VRAM) asignada para este servicio, el ajuste se realiza mediante plataformas en la nube con capas gratuitas/gestionadas (**Hugging Face**) y el despliegue final se ejecuta con un **modelo cuantizado sobre CPU estandar**.
4. **Prioridad funcional (Backend antes que Frontend, sin sobreingenieria):** se descarta el diseno prematuro de arquitecturas complejas de microservicios o interfaces visuales decorativas. El proyecto se centra en validar la entrada, el procesamiento y la salida coherente del pipeline de inferencia.

---

## 2. Objetivo General

> **Objetivo General:**
> Desarrollar y validar un sistema backend de inferencia basado en un Modelo de Lenguaje Pequeno (SLM) especializado y cuantizado para ejecucion en CPU estandar, capaz de generar interpretaciones psicologicas, de estilos de aprendizaje y vocacionales integradas a partir de las puntuaciones originales brutas de los instrumentos estandarizados CHASIDE, Felder-Silverman y Test de Personalidad, como herramienta de apoyo al diagnostico inicial estudiantil en la Universidad Tecnologica de Bolivar.

---

## 3. Objetivos Especificos (Metodologia SMART)

### Objetivo Especifico 1 (OE1): Estructuracion de Datos Psicometricos Brutos y Corpus Ground Truth

> **Texto para el formulario:**
> Estructurar el contrato de datos de entrada/salida con las puntuaciones originales brutas de los tres instrumentos validados (CHASIDE, Felder-Silverman y Test de Personalidad) y construir un corpus de referencia (*ground truth*) de al menos 150 perfiles interpretados mediante LLMs de frontera (Claude/ChatGPT) fundamentados en la literatura tecnica oficial de cada prueba, durante las semanas 1 y 2 de la Entrega 3.

| Criterio SMART | Aplicacion concreta en OE1 |
|---|---|
| **S (Specific / Especifico)** | Definir el esquema JSON de entrada con los puntajes nativos sin alterar escalas (CHASIDE `0-14` en 7 areas, Felder-Silverman `0-11` en 4 dimensiones bipolares, Personalidad `0-9` en 8 polos) y generar el dataset *ground truth* cruzado con la bibliografia psicometrica. |
| **M (Measurable / Medible)** | 100% de fidelidad a las escalas originales (0 escalas modificadas o inventadas), 1 schema JSON validado automaticamente y $\ge 150$ pares `(puntajes_brutos -> interpretacion_integrada)` verificados contra guardrails. |
| **A (Achievable / Alcanzable)** | Los bloques ya estan instalados en el entorno local de extraccion y la generacion del *ground truth* se realiza en lote con LLMs maestros a partir de los manuales tecnicos de los 3 tests. |
| **R (Relevant / Relevante)** | Garantiza la validez cientifica y psicometrica del sistema ("que un psicologo no pueda desbaratar la escala") y provee los datos de alta calidad indispensables para entrenar/destilar el SLM. |
| **T (Time-bound / Temporal)** | Semanas 1 y 2 del cronograma de Entrega 3 (entrega de avance preliminar el jueves de revision semanal). |

---

### Objetivo Especifico 2 (OE2): Ajuste/Destilacion en la Nube y Cuantizacion del SLM para CPU

> **Texto para el formulario:**
> Ajustar y cuantizar un Modelo de Lenguaje Pequeno (SLM de escala 0.5B a 1.5B parametros) en plataformas gestionadas en la nube (Hugging Face) a partir del corpus *ground truth*, e integrarlo en un pipeline backend de inferencia optimizado para ejecutarse 100% sobre CPU estandar sin dependencia de memoria de video (VRAM), durante las semanas 3 y 4 de la Entrega 3.

| Criterio SMART | Aplicacion concreta en OE2 |
|---|---|
| **S (Specific / Especifico)** | Ejecutar el fine-tuning supervisado (SFT/QLoRA) del SLM en Hugging Face / Colab, exportar los pesos cuantizados (formato GGUF `Q4_K_M`) e implementar el motor backend en Python que procesa los puntajes brutos y produce el informe integrado. |
| **M (Measurable / Medible)** | Consumo de VRAM en despliegue igual a `0 MB` (ejecucion 100% en CPU), huella en memoria RAM $\le 2.5\text{ GB}$ y cumplimiento del 100% de la estructura de salida del backend. |
| **A (Achievable / Alcanzable)** | Utiliza capas gratuitas/gestionadas en la nube (Hugging Face) para el ajuste pesado y cuantizacion a 4 bits para que la inferencia corra en cualquier computador convencional o servidor CPU de Savio. |
| **R (Relevant / Relevante)** | Resuelve la restriccion critica de infraestructura del proyecto (ausencia de GPUs dedicadas en equipos locales y en el cluster Savio) y prioriza el backend funcional sobre el frontend. |
| **T (Time-bound / Temporal)** | Semanas 3 y 4 del cronograma de Entrega 3. |

---

### Objetivo Especifico 3 (OE3): Validacion Cuantitativa del Diagnostico Inicial y Rendimiento en CPU

> **Texto para el formulario:**
> Evaluar el desempeno del sistema backend de inferencia mediante pruebas controladas sobre perfiles estudiantiles de validacion (no vistos en el ajuste), midiendo la precision/fidelidad interpretativa frente al *ground truth*, la adherencia a guardrails eticos (no emitir diagnosticos clinicos ni alterar puntajes) y los tiempos de respuesta en CPU estandar, durante las semanas 5 y 6 de la Entrega 3.

| Criterio SMART | Aplicacion concreta en OE3 |
|---|---|
| **S (Specific / Especifico)** | Ejecutar el protocolo de evaluacion sobre el particionado de prueba (20% del dataset + perfiles reales del equipo), comparando las salidas del SLM cuantizado contra el *ground truth* de los LLMs maestros y midiendo latencia/throughput en CPU. |
| **M (Measurable / Medible)** | Fidelidad de correlacion psicometrica $\ge 85\%$ en la rubrica de evaluacion contra *ground truth*, `100%` de aprobacion en pruebas de guardrails (cero invencion de puntajes o juicios clinicos) y tiempo de inferencia en CPU documentado ($\le 60\text{ s}$ por perfil integrado). |
| **A (Achievable / Alcanzable)** | La validacion se ejecuta de manera automatizada por consola sobre los equipos CPU del grupo sin requerir infraestructura externa ni interfaz grafica. |
| **R (Relevant / Relevante)** | Demuestra cientifica y tecnicamente que el SLM quedo bien destilado y cuantizado, entregando valor real como herramienta de apoyo al diagnostico inicial. |
| **T (Time-bound / Temporal)** | Semanas 5 y 6 del cronograma de Entrega 3. |

---

## 4. Definicion Formal de Entrada y Salida del Sistema (Sin Sobreingenieria)

Siguiendo el principio de ingenieria indicado por el docente (*"primero se define con claridad la entrada y la salida del sistema; luego se estructura la arquitectura necesaria"*):

### 4.1 Entrada del Backend (Puntuaciones Originales Brutas)

El motor recibe un objeto JSON con los puntajes nativos exactos que entregan los tres instrumentos validados, sin reescalado artificial:

1. **CHASIDE (98 items dicotomicos Si/No):**
   - Puntajes brutos de **Interes** (`0 a 10`) y **Aptitud** (`0 a 4`), y total por area (`0 a 14`) para las 7 areas: `C` (Administrativas/Contables), `H` (Humanisticas/Sociales), `A` (Artisticas), `S` (Salud/Medicina), `I` (Ingenieria/Computacion), `D` (Defensa/Seguridad), `E` (Exactas/Agrarias).
2. **Modelo de Felder-Silverman - ILS (44 items A/B):**
   - Conteos brutos por cada polo (`0 a 11`, donde cada par bipolar suma `11`) o diferencial oficial de Felder (`1, 3, 5, 7, 9, 11` hacia el polo correspondiente) en las 4 dimensiones:
     - `Activo` vs. `Reflexivo`
     - `Sensitivo` (Sensorial) vs. `Intuitivo`
     - `Visual` vs. `Verbal`
     - `Secuencial` vs. `Global`
3. **Test de Personalidad Institucional (72 items Si/No, 8 polos):**
   - Conteos brutos originales (`0 a 9` por polo) en las 4 dimensiones evaluadas por el cuestionario, sin el indice inferido `autonomia`.

### 4.2 Salida del Backend (Perfil Interpretativo Integrado)

El SLM genera un informe estructurado en Markdown/JSON con cuatro bloques verificables:

1. **Sintesis de Estilos de Aprendizaje (Felder-Silverman):** interpretacion de las 4 dimensiones bipolares segun la banda oficial del autor (equilibrio `1-3`, preferencia moderada `5-7`, preferencia muy fuerte `9-11`).
2. **Sintesis Conductual (Personalidad):** caracterizacion de habitos y preferencias de trabajo academico a partir de los puntajes brutos del test, con lenguaje descriptivo y no clinico.
3. **Sintesis Vocacional (CHASIDE):** identificacion de areas de interes y aptitud predominantes y su concordancia o brecha.
4. **Integracion Psicopedagogica y Vocacional Cruzada:** correlacion entre los tres instrumentos (como interactuan su estilo de procesamiento de informacion, sus rasgos conductuales y sus intereses/aptitudes vocacionales) para orientar el diagnostico inicial del profesional.

---

## 5. Resumen Ejecutivo para Envio por WhatsApp al Docente

> **Mensaje sugerido para validacion previa al jueves:**
>
> Profesor, siguiendo las indicaciones de la ultima sesion, reestructuramos el alcance hacia la **Entrega 3 (Interpretacion Psicometrica y Vocacional con SLM en CPU)** y redactamos los objetivos bajo metodologia **SMART** para el formulario:
>
> **1. Caso de estudio delimitado:** Sistema backend de inferencia con IA que recibe las **puntuaciones originales brutas** (sin alterar ni normalizar escalas) de **CHASIDE, Felder-Silverman y Test de Personalidad**, y genera un perfil interpretativo integrado para apoyar el diagnostico inicial del estudiante.
>
> **2. Objetivo General:** Desarrollar y validar un sistema backend de inferencia basado en un Modelo de Lenguaje Pequeno (SLM) especializado y cuantizado para ejecucion en CPU estandar, capaz de generar interpretaciones psicologicas, de estilos de aprendizaje y vocacionales integradas a partir de las puntuaciones originales brutas de los instrumentos estandarizados CHASIDE, Felder-Silverman y Test de Personalidad, como herramienta de apoyo al diagnostico inicial estudiantil.
>
> **3. Objetivos Especificos SMART:**
> - **OE1 (Datos brutos y Ground Truth - Semanas 1-2):** Estructurar el contrato JSON con los puntajes originales brutos de los 3 tests (0 modificaciones de escala) y construir un corpus *ground truth* ($\ge 150$ perfiles interpretados) usando LLMs maestros (Claude/ChatGPT) alimentados con la literatura tecnica oficial de cada instrumento.
> - **OE2 (Destilacion en Hugging Face y Cuantizacion CPU - Semanas 3-4):** Ajustar/destilar un SLM (0.5B-1.5B) en entornos gestionados en la nube (Hugging Face) y cuantizarlo (GGUF 4-bit) dentro de un pipeline backend que opere 100% sobre CPU estandar (`0 MB` de VRAM obligatoria, $\le 2.5\text{ GB}$ RAM).
> - **OE3 (Validacion de Diagnostico y Rendimiento - Semanas 5-6):** Evaluar objetivamente el motor backend midiendo fidelidad diagnostica frente al *ground truth* ($\ge 85\%$), cumplimiento de guardrails eticos (`100%`) y tiempos de inferencia en CPU ($\le 60\text{ s}$).
>
> Quedamos atentos a sus comentarios para dejar cerrado el apartado tecnico del formulario antes de la sesion del jueves.
