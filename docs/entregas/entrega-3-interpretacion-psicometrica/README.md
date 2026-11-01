# Entrega 3 - Interpretacion Psicometrica y Vocacional con SLM en CPU

**Estado:** En curso
**Milestone sugerido:** Entrega 3 - Interpretacion Psicometrica
**Documento de formulacion formal (Objetivos SMART y formulario):** [objetivos-smart-formulario.md](objetivos-smart-formulario.md)
**Tablero de issues y recategorizacion (E3-01 a E3-10):** [github-issues.md](github-issues.md)
**Trazabilidad requisito -> issue -> evidencia:** [seccion 5](#5-trazabilidad-requisito---issue---evidencia)

---

## 1. Reorientacion estrategica dictada por el docente

Tras la revision de los avances de las Entregas 1 y 2, el docente del proyecto establecio **8 directrices obligatorias** que redefinen y acotan el alcance del proyecto para la Entrega 3:

### 1.1 Delimitacion del alcance: de la generacion de contenido a un caso concreto
- **Problema de partida corregido:** abordar la "produccion o recomendacion masiva de contenidos" para cursos universitarios es inabarcable en el tiempo disponible.
- **Caso de estudio definitivo y medible:** construir un **sistema de inferencia con Inteligencia Artificial enfocado en la interpretacion psicologica y vocacional de personas a partir de pruebas estandarizadas**.
- **Valor aplicado:** demostrar que un modelo de IA pequeno puede procesar y cruzar datos humanos de tres instrumentos validados para **apoyar el diagnostico inicial de un estudiante sin pretender reemplazar al profesional**.

### 1.2 Rigor psicometrico: prohibicion de modificar las escalas validadas
- **Correccion critica de validez psicometrica:** los instrumentos psicometricos cuentan con decadas de validacion estadistica. Si se alteran las escalas (como la conversion previa a `1.0-5.0`), se inventan indices compuestos no validados (como `autonomia`) o se modifican las opciones de respuesta, los resultados pierden validez cientifica y no son aceptados por profesionales de psicologia.
- **Los tres instrumentos oficiales:**
  1. **CHASIDE:** test estandarizado de orientacion vocacional que mide areas de interes (10 items por area) y aptitudes (4 items por area) en 7 categorias (`C, H, A, S, I, D, E`).
  2. **Modelo de Felder-Silverman (ILS):** cuestionario de estilos de aprendizaje que clasifica al estudiante en 4 dimensiones bipolares (activo/reflexivo, sensitivo/intuitivo, visual/verbal, secuencial/global) con puntajes de `0 a 11` por polo.
  3. **Test de Personalidad:** instrumento institucional para caracterizar rasgos conductuales del estudiante en sus 8 polos originales (`0 a 9` por polo).
- **Funcion del software:** el sistema **no reinventa ni reescala los tests**. Recibe las **puntuaciones originales brutas**, las procesa junto a la literatura teorica oficial de cada instrumento y genera un **perfil integrado del usuario**.

### 1.3 Estrategia de modelos: SLMs especializados vs. LLMs de frontera
- **Rol de los LLMs de frontera (Claude, ChatGPT):** se utilizan unicamente como **modelos "maestros" (Teacher)** en la fase inicial de laboratorio. Se alimentan con la bibliografia tecnica de los tres tests para disenar prompts robustos y obtener salidas interpretativas de alta calidad (*ground truth*).
- **Objetivo final del proyecto (SLM - Small Language Model):** desarrollar, ajustar o destilar un modelo de lenguaje pequeno y especializado.
- **Justificacion del SLM:** un modelo compacto no necesita almacenar conocimiento enciclopedico general; solo requiere aprender a **interpretar las correlaciones entre los resultados de los tres cuestionarios**, reduciendo el consumo de computo y haciendolo viable para el equipo.

### 1.4 Restricciones criticas de hardware: inferencia sin dependencia de VRAM
- **Diagnostico de infraestructura:** el equipo no cuenta con GPUs de alta capacidad en sus maquinas locales y los servidores institucionales (cluster Savio) **no disponen de memoria de video dedicada (VRAM)** asignada para este proposito.
- **Solucion de entrenamiento y pruebas:** utilizar plataformas en la nube con capas gratuitas o gestionadas (**Hugging Face**, Google Colab / Kaggle) para las pruebas iniciales y el ajuste del modelo.
- **Solucion de despliegue:** obtener un **modelo cuantizado** (menor precision numerica, formato GGUF, pero funcional) optimizado para ejecutarse sobre **CPU estandar**, eliminando la necesidad obligatoria de VRAM y garantizando que el software funcione en cualquier computador convencional.

### 1.5 Rechazo a la sobreingenieria prematura
- Presentar una "arquitectura de software completa" con microservicios o infraestructura cloud compleja cuando aun se estan formalizando las entradas y salidas es hacer **sobreingenieria** (*overengineering*).
- **Principio de ingenieria:** primero se define con claridad la **entrada** (puntajes brutos de los 3 tests) y la **salida** (perfil psicologico y vocacional integrado); la arquitectura emerge despues como consecuencia directa del problema delimitado.

### 1.6 Prioridad funcional: "Backend antes que Frontend"
- La interfaz grafica o elementos visuales son **irrelevantes en esta etapa**.
- **Prioridad absoluta:** lograr que el **pipeline de inferencia (backend)** entregue respuestas coherentes, correctas, fieles a la psicometria y estructuradas. La capa visual solo se considerara cuando el motor de inferencia este validado.

### 1.7 Metodologia de formulacion: Objetivos SMART requeridos
- **1 Objetivo General:** orientado a solucionar el problema aplicado de interpretacion psicologica y vocacional mediante IA.
- **3 Objetivos Especificos SMART (Specific, Measurable, Achievable, Relevant, Time-bound):**
  1. **OE1 (Datos y psicometria):** adquisicion y estructuracion de las puntuaciones originales brutas de los 3 tests junto con su literatura teorica y corpus *ground truth*.
  2. **OE2 (Ajuste y cuantizacion en CPU):** ajuste/destilacion en la nube (Hugging Face) y cuantizacion del SLM para inferencia sobre CPU estandar sin dependencia de VRAM.
  3. **OE3 (Validacion y metricas):** validacion objetiva del motor backend midiendo fidelidad diagnostica frente al *ground truth* y tiempos de inferencia en CPU.
- Redaccion completa lista para el formulario y revision por WhatsApp: [objetivos-smart-formulario.md](objetivos-smart-formulario.md).

### 1.8 Acuerdos operativos y proximos pasos inmediatos
- **Canal de comunicacion rapida:** WhatsApp para consultas diarias, validacion de la redaccion de objetivos SMART y envio de borradores previos antes de la sesion del jueves.
- **Repositorio de codigo:** versionar avances, resguardar documentacion tecnica y registrar el progreso formal por sprints e issues.
- **Formulario del proyecto:** el equipo diligencia unicamente los apartados tecnicos; el docente completara la informacion administrativa del grupo y lider de investigacion.

---

## 2. Sprints y Cronograma Fechado de la Entrega 3 (`E3-02` / `#40`)

Cada sprint responde directamente a la formulacion SMART y a las etapas de ingenieria exigidas por el docente, con cierre total y presentacion en la ventana del **3 al 9 de noviembre de 2026**:

| Sprint | Fechas | Documento | Foco | Issues | Estado |
|---|---|---|---|---|---|
| 1 | `23 al 26 Oct 2026` | [Formulacion SMART, alcance y cierre psicometrico](sprint-1-formulacion-smart-y-alcance.md) | Objetivos SMART, formulario tecnico, cronograma y cierre de consultas de escala/instrumentos | E3-01 (#49), E3-02 (#40), E3-03 (#38) | En curso |
| 2 | `27 al 30 Oct 2026` | [OE1: Datos brutos de los 3 tests y Ground Truth con LLM Maestro](sprint-2-datos-brutos-y-ground-truth.md) | Contrato JSON de puntajes brutos (sin alterar escalas), literatura teorica y corpus *ground truth* con Claude/ChatGPT | E3-04 (#50), E3-05 (#42), E3-06 (#43) | Pendiente |
| 3 | `31 Oct al 03 Nov 2026` | [OE2: Destilacion en Hugging Face, cuantizacion y Backend en CPU](sprint-3-destilacion-cuantizacion-cpu.md) | Ajuste en nube (Hugging Face), cuantizacion GGUF sin VRAM y motor backend de interpretacion integrada | E3-07 (#51), E3-08 (#44) | Pendiente |
| 4 | `03 al 09 Nov 2026` | [OE3: Validacion psicometrica, metricas en CPU y cierre](sprint-4-validacion-metricas-y-cierre.md) | Evaluacion objetiva (fidelidad diagnostica vs. *ground truth*, latencia en CPU) y demo/presentacion final | E3-09 (#52), E3-10 (#53) | Pendiente |

### 2.1 Hitos del Cronograma SMART (`23 de octubre al 9 de noviembre de 2026`)

El detalle operativo completo se encuentra en la seccion 5 de [objetivos-smart-formulario.md](objetivos-smart-formulario.md#5-cronograma-fechado-smart-y-plan-de-trabajo---entrega-3-e3-02--40):

| Hito | Fecha | Objetivo SMART | Entregable / Evidencia Verificable |
|---|---|---|---|
| **Envio previo de Formulacion SMART** | `Lun 26 / Mar 27 Oct 2026` | Formulacion (`E3-01`, `E3-02`) | Borrador de Objetivos SMART, apartados tecnicos del formulario y cronograma enviados por WhatsApp al docente. |
| **Revision Docente Jueves 1 (Cierre OE1)** | `Jueves 29 Oct 2026` | **OE1** (`23 al 30 Oct`) | Aprobacion de formulario SMART (`E3-01`), contrato JSON de puntajes originales brutos (`E3-04`), 3 perfiles reales en bruto (`E3-05`) y avance del corpus *ground truth* $\ge 150$ (`E3-06`, cierre `Vie 30 Oct`). |
| **Congelamiento de Modelo GGUF y Backend (*Freeze*)** | `Martes 03 Nov 2026` | **OE2** (`31 Oct al 03 Nov`) | Fine-tuning en Hugging Face completado, modelo exportado a GGUF (`Q4_K_M`) corriendo 100% en CPU (`0 MB` VRAM, RAM $\le 2.5\text{ GB}$, `E3-08`) e integrado al pipeline backend en Python sin frontend (`E3-07`). |
| **Revision Docente Jueves 2 y Ventana de Presentacion Final** | `Jueves 05 Nov` (Ventana `03 al 09 Nov 2026`) | **OE3** (`03 al 09 Nov`) | Evaluacion sobre el 20% de prueba + 3 perfiles reales (fidelidad $\ge 85\%$, guardrails `100%`, latencia en CPU $\le 60\text{ s}$, `E3-09`) y demostracion funcional completa en consola lista para presentar (`E3-10`). |

- **Camino critico:** `E3-01 (#49)` $\rightarrow$ `E3-04 (#50)` $\rightarrow$ `E3-06 (#43)` $\rightarrow$ `E3-08 (#44)` $\rightarrow$ `E3-09 (#52)` $\rightarrow$ `E3-10 (#53)` (con `E3-05` y `E3-07` ejecutandose en paralelo).

### 2.2 Lineamientos de datos psicometricos (E3-03)

El documento canonico es [lineamientos-datos-psicometricos.md](lineamientos-datos-psicometricos.md). Fija el consentimiento de los tres integrantes, la seudonimizacion de los perfiles reales, la regla de no versionamiento, el protocolo previo a Hugging Face, el guardrail no clinico y el checklist de verificacion. La aplicacion al corpus es gate de E3-06 y la integracion en el backend es gate de E3-07.

---

## 3. Reclasificacion de los issues abiertos de Entrega 2 hacia Entrega 3

En GitHub, los issues `E2-01` a `E2-12` (`#18` al `#29`) quedaron cerrados al completarse la fase anterior. Los 8 issues que permanecian abiertos (`#37` al `#44`) se reorganizan asi tras las instrucciones del docente:

### 3.1 Issues cerrados por respuesta directa del docente en reunion

| Issue GitHub | Codigo previo | Tema consultado | Resolucion oficial del docente |
|---|---|---|---|
| [#37](https://github.com/ISCOUTB/savio-ai-recommender/issues/37) | E2-13 | Validar el indice inferido `autonomia` del test de personalidad | **Cerrado / Descartado:** prohibido inventar o derivar escalas no validadas psicometricamente. Se usan solo los puntajes originales brutos del test. |
| [#39](https://github.com/ISCOUTB/savio-ai-recommender/issues/39) | E2-15 | Confirmar la escala unificada `1.0-5.0` frente a los valores originales | **Cerrado / Resuelto:** se descarta la normalizacion `1.0-5.0`. El sistema debe recibir las **puntuaciones originales brutas** de cada instrumento. |
| [#41](https://github.com/ISCOUTB/savio-ai-recommender/issues/41) | E2-17 | Confirmar instrumento de estilos: VARK o Felder-Soloman | **Cerrado / Confirmado:** se ratifica oficialmente el **Modelo de Felder-Silverman** (4 dimensiones bipolares) junto con CHASIDE y Test de Personalidad. |

Confirmado en GitHub el 2026-10-23: `#37` y `#39` cerrados con motivo `not planned`; `#41` cerrado con motivo `completed`. El milestone `Entrega 2 - Personalizacion` quedo cerrado como Completado.

### 3.2 Issues migrados y nuevos issues de la Entrega 3

| Codigo E3 | Issue GitHub | Origen | Sprint | Prioridad | Dueno | Titulo |
|---|---|---|---|---|---|---|
| **E3-01** | [#49](https://github.com/ISCOUTB/savio-ai-recommender/issues/49) | Directriz 1, 7 y 8 | Sprint 1 | P0 (Critica) | Equipo completo | Formular Objetivos SMART y apartados tecnicos del formulario del proyecto |
| **E3-02** | [#40](https://github.com/ISCOUTB/savio-ai-recommender/issues/40) | Recategorizado de `E2-16` | Sprint 1 | P0 (Critica) | Persona 1 (Coordinador) | Cronograma fechado SMART y plan de trabajo de Entrega 3 |
| **E3-03** | [#38](https://github.com/ISCOUTB/savio-ai-recommender/issues/38) | Recategorizado de `E2-14` | Sprint 1 | P1 (Alta) | Equipo / Docente | Lineamientos de consentimiento, anonimizacion y manejo de datos psicometricos |
| **E3-04** | [#50](https://github.com/ISCOUTB/savio-ai-recommender/issues/50) | Directriz 2 y 5 (OE1) | Sprint 2 | P0 (Critica) | Persona 1 (Apoyo: P2, P3) | Redefinir contrato de entrada con puntajes originales brutos (CHASIDE, Felder-Silverman, Personalidad) |
| **E3-05** | [#42](https://github.com/ISCOUTB/savio-ai-recommender/issues/42) | Recategorizado de `E2-18` (OE1) | Sprint 2 | P1 (Alta) | Persona 2 y Persona 3 | Completar diligenciamiento y extraccion de puntajes brutos reales de los 3 tests |
| **E3-06** | [#43](https://github.com/ISCOUTB/savio-ai-recommender/issues/43) | Recategorizado de `E2-19` (OE1) | Sprint 2 | P0 (Critica) | Persona 3 (Apoyo: P1, P2) | Construir corpus Ground Truth de interpretacion integrada con LLMs Maestros (Claude/ChatGPT) y literatura tecnica |
| **E3-07** | [#51](https://github.com/ISCOUTB/savio-ai-recommender/issues/51) | Directriz 2 y 6 (OE2) | Sprint 3 | P0 (Critica) | Persona 1 | Implementar pipeline backend de inferencia para interpretacion psicologica y vocacional integrada |
| **E3-08** | [#44](https://github.com/ISCOUTB/savio-ai-recommender/issues/44) | Recategorizado de `E2-20` (OE2) | Sprint 3 | P0 (Critica) | Persona 3 (Lider Tecnico SLM) | Ajustar/destilar SLM en Hugging Face y cuantizar a GGUF para ejecucion 100% en CPU (sin VRAM) |
| **E3-09** | [#52](https://github.com/ISCOUTB/savio-ai-recommender/issues/52) | Directriz 4 y 7 (OE3) | Sprint 4 | P0 (Critica) | Persona 2 | Evaluar metricas SMART: precision/fidelidad diagnostica frente a Ground Truth y tiempos de inferencia en CPU |
| **E3-10** | [#53](https://github.com/ISCOUTB/savio-ai-recommender/issues/53) | Directriz 6 y 8 (OE3) | Sprint 4 | P1 (Alta) | Equipo completo | Demostracion funcional del backend de inferencia en CPU y cierre de Entrega 3 |

---

## 4. Criterios de cierre de la Entrega 3

- [ ] Borrador de Objetivos SMART (1 General + 3 Especificos) y apartados tecnicos del formulario validados con el docente por WhatsApp antes de la sesion del jueves (`E3-01`).
- [ ] Cronograma con fechas limite por objetivo SMART aprobado (`E3-02` / `#40`).
- [x] Lineamientos de consentimiento, anonimizacion y guardrail no clinico documentados y probados; su aplicacion al corpus y al backend queda como gate de `E3-06` y `E3-07` (`E3-03` / `#38`).
- [ ] Consultas psicometricas `#37`, `#39` y `#41` cerradas documentalmente y en GitHub con la directriz de no alterar escalas validadas.
- [ ] Contrato de entrada/salida actualizado para consumir **puntuaciones originales brutas** de CHASIDE (`0-14`), Felder-Silverman (`0-11` por polo) y Personalidad (`0-9` por polo) sin reescalado artificial (`E3-04`, `E3-05` / `#42`).
- [ ] Corpus *ground truth* de interpretaciones psicologicas y vocacionales integradas generado con LLMs de frontera (Claude/ChatGPT) respaldado en la literatura tecnica oficial de los 3 instrumentos (`E3-06` / `#43`).
- [ ] Modelo SLM ajustado/destilado en entorno gestionado (Hugging Face) y cuantizado en formato GGUF ejecutable en **CPU estandar sin VRAM** (`E3-08` / `#44`).
- [ ] Pipeline backend de inferencia funcional (sin frontend decorativo ni sobreingenieria) que recibe los puntajes brutos de los 3 cuestionarios y entrega el perfil interpretativo integrado (`E3-07`).
- [ ] Reporte de validacion SMART con metricas objetivas de fidelidad diagnostica y tiempos de inferencia en CPU (`E3-09`, `E3-10`).

---

## 5. Trazabilidad requisito -> issue -> evidencia

Esta tabla responde tres preguntas para cada requisito: **que se pidio** (objetivo SMART),
**quien lo ejecuta** (issue) y **donde esta la prueba** (archivo o corrida medida).
No reemplaza ningun documento: es un indice. El canon sigue en
[objetivos-smart-formulario.md](objetivos-smart-formulario.md) para los objetivos,
[github-issues.md](github-issues.md) para el detalle de cada issue y este README para sprints y criterios de cierre.

**Estados:** `Documentado` (la especificacion o el contrato ya existe en el repo) -
`En curso` (existe avance parcial verificable) - `Pendiente` (sin evidencia todavia).

| Requisito SMART | Issue | Meta verificable | Evidencia o prueba | Estado |
|---|---|---|---|---|
| Formulacion: 1 Objetivo General + 3 OE bajo metodologia SMART | E3-01 ([#49](https://github.com/ISCOUTB/savio-ai-recommender/issues/49)) | Objetivos redactados y enviados al docente antes de la sesion del jueves | [objetivos-smart-formulario.md](objetivos-smart-formulario.md) | Pendiente de validacion docente |
| Cronograma fechado y plan de trabajo | E3-02 ([#40](https://github.com/ISCOUTB/savio-ai-recommender/issues/40)) | 4 sprints con fechas y 4 hitos entre el 23 Oct y el 9 Nov 2026 | Seccion 2 de este README y los cuatro documentos de sprint ([sprint 1](sprint-1-formulacion-smart-y-alcance.md), [sprint 2](sprint-2-datos-brutos-y-ground-truth.md), [sprint 3](sprint-3-destilacion-cuantizacion-cpu.md), [sprint 4](sprint-4-validacion-metricas-y-cierre.md)) | Documentado |
| Datos psicometricos: consentimiento, seudonimizacion y guardrail no clinico | E3-03 ([#38](https://github.com/ISCOUTB/savio-ai-recommender/issues/38)) | Reglas escritas y validador de privacidad ejecutable (gate de E3-06 y E3-07) | [lineamientos-datos-psicometricos.md](lineamientos-datos-psicometricos.md), [validar-corpus-anonimizado.py](../../especificaciones/validar-corpus-anonimizado.py), [test del validador](../../especificaciones/test_validar_corpus_anonimizado.py) | Documentado |
| **OE1-R1:** recibir puntajes originales brutos sin reescalar (CHASIDE `0-14`, Felder-Silverman `0-11` por polo, Personalidad `0-9` por polo) | E3-04 ([#50](https://github.com/ISCOUTB/savio-ai-recommender/issues/50)) | Contrato JSON de entrada con rangos brutos y cero transformaciones de escala | [perfil-estudiante.schema.json](../../especificaciones/perfil-estudiante.schema.json) (contrato vigente de E2, a redefinir en E3-04) | En curso |
| **OE1-R2:** tres perfiles reales diligenciados en bruto | E3-05 ([#42](https://github.com/ISCOUTB/savio-ai-recommender/issues/42)) | 3 perfiles reales extraidos de los tests aplicados | [perfiles/reales/persona-1.json](../../../perfiles/reales/persona-1.json) (1 de 3) | En curso |
| **OE1-R3:** literatura tecnica oficial de los 3 instrumentos como base del *ground truth* | E3-06 ([#43](https://github.com/ISCOUTB/savio-ai-recommender/issues/43)) | Notas tecnicas por instrumento enlazadas en el prompt maestro | [instrumento-chaside.md](../../especificaciones/instrumento-chaside.md), [instrumento-estilos-aprendizaje.md](../../especificaciones/instrumento-estilos-aprendizaje.md), [instrumento-personalidad.md](../../especificaciones/instrumento-personalidad.md) | Documentado |
| **OE1-R4:** corpus *ground truth* de interpretacion integrada | E3-06 ([#43](https://github.com/ISCOUTB/savio-ai-recommender/issues/43)) | `>= 150` registros sinteticos, sin PII y con rangos validos antes de subir a Hugging Face | `datos/corpus/corpus.jsonl` + `datos/corpus/manifiesto.json` (pendiente de generar; se valida con [validar-corpus-anonimizado.py](../../especificaciones/validar-corpus-anonimizado.py)) | Pendiente |
| **OE2-R1:** ajuste o destilacion del SLM en entorno gestionado | E3-08 ([#44](https://github.com/ISCOUTB/savio-ai-recommender/issues/44)) | Modelo ajustado con el corpus de E3-06 y ficha reproducible | Pendiente: enlace al repositorio de Hugging Face y constancia en [propuesta-destilacion-slm.md](../../investigacion/propuesta-destilacion-slm.md) | Pendiente |
| **OE2-R2:** cuantizacion GGUF `Q4_K_M` ejecutable en CPU estandar | E3-08 ([#44](https://github.com/ISCOUTB/savio-ai-recommender/issues/44)) | `0 MB` de VRAM requerida, `RAM <= 2.5 GB`, latencia medida en CPU | Pendiente: corrida medida en `benchmarks/resultados/<equipo>/` con la [metodologia de benchmarks](../../../benchmarks/README.md) | Pendiente |
| **OE2-R3:** pipeline backend de inferencia sin frontend | E3-07 ([#51](https://github.com/ISCOUTB/savio-ai-recommender/issues/51)) | Recibe los brutos de los 3 tests y entrega el perfil integrado con guardrail no clinico aplicado | Pendiente: modulo de backend en `poc_slm/`, hoy solo existe la PoC de tutoria ([README de poc_slm](../../../poc_slm/README.md)) | Pendiente |
| **OE3-R1:** fidelidad diagnostica frente al *ground truth* | E3-09 ([#52](https://github.com/ISCOUTB/savio-ai-recommender/issues/52)) | Rubrica cuantitativa aplicada con fidelidad `>= 85%` y guardrails `100%` | Pendiente: reporte de validacion de E3 (se apoya en el conjunto de validacion de E3-06) | Pendiente |
| **OE3-R2:** tiempos de inferencia en CPU | E3-09 ([#52](https://github.com/ISCOUTB/savio-ai-recommender/issues/52)) | Latencia `<= 60 s` por perfil en CPU estandar | Pendiente: corrida medida en `benchmarks/resultados/<equipo>/` | Pendiente |
| **OE3-R3:** demostracion funcional y cierre | E3-10 ([#53](https://github.com/ISCOUTB/savio-ai-recommender/issues/53)) | Guion de demo en consola con entradas y salidas respaldadas | Pendiente: material en `docs/presentacion/` y salidas de respaldo en `prompts/salidas-respaldo/` (evidencia medida, no se edita) | Pendiente |

### 5.1 Reglas de uso de esta tabla

1. **No se duplica contenido:** si un dato ya vive en otro documento, aqui va solo el enlace.
2. **El estado se cambia con evidencia, no con intencion:** `Documentado` exige archivo enlazado; `En curso` exige avance verificable; `Pendiente` es el estado por defecto.
3. **Las cifras no se escriben a mano:** fidelidad, latencia y consumo de RAM/VRAM se toman de `benchmarks/resultados/<equipo>/`, que es evidencia medida por el equipo.
4. **Si cambia un requisito SMART**, se actualiza primero [objetivos-smart-formulario.md](objetivos-smart-formulario.md) y luego esta tabla, en el mismo commit con su issue.
5. **Verificacion documental:** los enlaces de esta seccion los revisa `python docs/validar-docs.py` desde la raiz del repositorio.

