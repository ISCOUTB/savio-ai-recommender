# Entrega 3 - Interpretacion Psicometrica y Vocacional con SLM en CPU

**Estado:** En curso
**Milestone sugerido:** Entrega 3 - Interpretacion Psicometrica
**Documento de formulacion formal (Objetivos SMART y formulario):** [objetivos-smart-formulario.md](objetivos-smart-formulario.md)
**Tablero de issues y recategorizacion (E3-01 a E3-10):** [github-issues.md](github-issues.md)

---

## 1. Reorientacion estrategica dictada por el docente

Tras la revision de los avances de las Entregas 1 y 2, el docente del proyecto establecio **8 directrices obligatorias** que redefinen y acotan el alcance del proyecto para la Entrega 3:

### 1.1 Delimitacion del alcance: de la generacion de contenido a un caso concreto
- **Problema de partida corregido:** abordar la "produccion o recomendacion masiva de contenidos" para cursos universitarios es inabarcable en el tiempo disponible.
- **Caso de estudio definitivo y medible:** construir un **sistema de inferencia con Inteligencia Artificial enfocado en la interpretacion psicologica y vocacional de personas a partir de pruebas estandarizadas**.
- **Valor aplicado:** demostrar que un modelo de IA pequeno puede procesar y cruzar datos humanos de tres instrumentos validados para **apoyar el diagnostico inicial de un estudiante sin pretender reemplazar al profesional**.

### 1.2 Rigor psicometrico: prohibicion de modificar las escalas validadas
- **Correccion critica ("Viene un psicologo y nos desbarata esa vaina"):** los instrumentos psicometricos cuentan con decadas de validacion estadistica. Si un ingeniero altera las escalas (como la conversion previa a `1.0-5.0`), inventa indices compuestos no validados (como `autonomia`) o modifica las opciones de respuesta, los resultados pierden validez cientifica y el proyecto queda invalidado.
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

## 2. Sprints de la Entrega 3

Cada sprint responde directamente a la formulacion SMART y a las etapas de ingenieria exigidas por el docente:

| Sprint | Documento | Foco | Issues | Estado |
|---|---|---|---|---|
| 1 | [Formulacion SMART, alcance y cierre psicometrico](sprint-1-formulacion-smart-y-alcance.md) | Objetivos SMART, formulario tecnico, cronograma y cierre de consultas de escala/instrumentos | E3-01, E3-02 (#40), E3-03 (#38) | En curso |
| 2 | [OE1: Datos brutos de los 3 tests y Ground Truth con LLM Maestro](sprint-2-datos-brutos-y-ground-truth.md) | Contrato JSON de puntajes brutos (sin alterar escalas), literatura teorica y corpus *ground truth* con Claude/ChatGPT | E3-04, E3-05 (#42), E3-06 (#43) | Pendiente |
| 3 | [OE2: Destilacion en Hugging Face, cuantizacion y Backend en CPU](sprint-3-destilacion-cuantizacion-cpu.md) | Ajuste en nube (Hugging Face), cuantizacion GGUF sin VRAM y motor backend de interpretacion integrada | E3-07, E3-08 (#44) | Pendiente |
| 4 | [OE3: Validacion psicometrica, metricas en CPU y cierre](sprint-4-validacion-metricas-y-cierre.md) | Evaluacion objetiva (fidelidad diagnostica vs. *ground truth*, latencia en CPU) y demo de backend | E3-09, E3-10 | Pendiente |

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
- [ ] Consultas psicometricas `#37`, `#39` y `#41` cerradas documentalmente y en GitHub con la directriz de no alterar escalas validadas.
- [ ] Contrato de entrada/salida actualizado para consumir **puntuaciones originales brutas** de CHASIDE (`0-14`), Felder-Silverman (`0-11` por polo) y Personalidad (`0-9` por polo) sin reescalado artificial (`E3-04`, `E3-05` / `#42`).
- [ ] Corpus *ground truth* de interpretaciones psicologicas y vocacionales integradas generado con LLMs de frontera (Claude/ChatGPT) respaldado en la literatura tecnica oficial de los 3 instrumentos (`E3-06` / `#43`).
- [ ] Modelo SLM ajustado/destilado en entorno gestionado (Hugging Face) y cuantizado en formato GGUF ejecutable en **CPU estandar sin VRAM** (`E3-08` / `#44`).
- [ ] Pipeline backend de inferencia funcional (sin frontend decorativo ni sobreingenieria) que recibe los puntajes brutos de los 3 cuestionarios y entrega el perfil interpretativo integrado (`E3-07`).
- [ ] Reporte de validacion SMART con metricas objetivas de fidelidad diagnostica y tiempos de inferencia en CPU (`E3-09`, `E3-10`).

