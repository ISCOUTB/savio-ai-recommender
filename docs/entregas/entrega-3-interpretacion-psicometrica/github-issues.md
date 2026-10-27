# Issues de Entrega 3 - Tablero de trabajo y recategorizacion

> **Fuente de verdad:** GitHub (`ISCOUTB/savio-ai-recommender`).
> **Entrega:** [Entrega 3 - Interpretacion Psicometrica](README.md).
> **Milestone en GitHub:** `Entrega 3 - Interpretacion Psicometrica`.
> **Script de sincronizacion:** `sincronizar-github-e3.ps1`.

Labels utilizados: `entrega-3`, `smart`, `psicopedagogia`, `slm`, `destilacion`, `huggingface`, `cpu-only`, `backend`, `docs`, `equipo`, `persona-1`, `persona-2`, `persona-3`, `docente`, `legal`.

---

## 1. Consultas de Entrega 2 cerradas en GitHub por directriz del docente

En la sesion de revision, el docente respondio de forma definitiva las tres consultas psicometricas que permanecian abiertas:

| Issue GitHub | Codigo anterior | Titulo original | Estado en GitHub | Resolucion oficial del docente |
|---|---|---|---|---|
| [#37](https://github.com/ISCOUTB/savio-ai-recommender/issues/37) | E2-13 | Validar el indice `autonomia` del test de personalidad | **Cerrado (not planned)** | Queda prohibido inventar o derivar indices compuestos no validados psicometricamente, dado que carecen de sustento estadistico y no son aceptados en evaluacion psicologica. Se elimina `autonomia` y se conservan unicamente las dimensiones originales del instrumento de personalidad. |
| [#39](https://github.com/ISCOUTB/savio-ai-recommender/issues/39) | E2-15 | Confirmar la escala unificada 1.0-5.0 frente a los valores originales | **Cerrado (not planned)** | No se debe normalizar ni transformar arbitrariamente ninguna escala a `1.0-5.0`. El motor de inferencia de Entrega 3 debe recibir las **puntuaciones originales brutas** de los tres cuestionarios (`0-14` en CHASIDE, `0-11` en Felder-Silverman, `0-9` en Personalidad). |
| [#41](https://github.com/ISCOUTB/savio-ai-recommender/issues/41) | E2-17 | Confirmar instrumento de estilos: VARK o Felder-Soloman | **Cerrado (completed)** | El docente confirmo oficialmente el **Modelo de Felder-Silverman** (4 dimensiones bipolares: activo/reflexivo, sensitivo/intuitivo, visual/verbal, secuencial/global) como uno de los tres instrumentos definitivos junto a CHASIDE y el Test de Personalidad. |

---

## 2. Indice de Issues de la Entrega 3 (`E3-01` a `E3-10`)

| Issue | GitHub | Origen | Estado | Prioridad | Sprint | Objetivo SMART | Dueno | Titulo |
|---|---|---|---|---|---|---|---|---|
| **E3-01** | [#49](https://github.com/ISCOUTB/savio-ai-recommender/issues/49) | Directrices 1, 7, 8 | abierto | P0 (Critica) | Sprint 1 | Formulacion | Equipo completo | Formular Objetivos SMART y apartados tecnicos del formulario del proyecto |
| **E3-02** | [#40](https://github.com/ISCOUTB/savio-ai-recommender/issues/40) | Migrado de `E2-16` | abierto | P0 (Critica) | Sprint 1 | Formulacion (T) | Persona 1 (Coordinador) | Cronograma fechado SMART y plan de trabajo de Entrega 3 |
| **E3-03** | [#38](https://github.com/ISCOUTB/savio-ai-recommender/issues/38) | Migrado de `E2-14` | abierto | P1 (Alta) | Sprint 1 | Transversal | Equipo / Docente | Lineamientos de consentimiento, anonimizacion y manejo de datos psicometricos |
| **E3-04** | [#50](https://github.com/ISCOUTB/savio-ai-recommender/issues/50) | Directrices 2, 5 | abierto | P0 (Critica) | Sprint 2 | OE1 | Persona 1 (Apoyo: P2, P3) | Redefinir contrato de entrada con puntajes originales brutos (CHASIDE, Felder-Silverman, Personalidad) |
| **E3-05** | [#42](https://github.com/ISCOUTB/savio-ai-recommender/issues/42) | Migrado de `E2-18` | abierto | P1 (Alta) | Sprint 2 | OE1 | Persona 2 y Persona 3 | Completar diligenciamiento y extraccion de puntajes brutos reales de los 3 tests |
| **E3-06** | [#43](https://github.com/ISCOUTB/savio-ai-recommender/issues/43) | Migrado de `E2-19` | abierto | P0 (Critica) | Sprint 2 | OE1 | Persona 3 (Apoyo: P1, P2) | Construir corpus Ground Truth de interpretacion integrada con LLMs Maestros (Claude/ChatGPT) y literatura tecnica |
| **E3-07** | [#51](https://github.com/ISCOUTB/savio-ai-recommender/issues/51) | Directrices 2, 5, 6 | abierto | P0 (Critica) | Sprint 3 | OE2 | Persona 1 | Implementar pipeline backend de inferencia para interpretacion psicologica y vocacional integrada |
| **E3-08** | [#44](https://github.com/ISCOUTB/savio-ai-recommender/issues/44) | Migrado de `E2-20` | abierto | P0 (Critica) | Sprint 3 | OE2 | Persona 3 (Lider Tecnico SLM) | Ajustar/destilar SLM en Hugging Face y cuantizar a GGUF para ejecucion 100% en CPU (sin VRAM) |
| **E3-09** | [#52](https://github.com/ISCOUTB/savio-ai-recommender/issues/52) | Directrices 3, 4, 7 | abierto | P0 (Critica) | Sprint 4 | OE3 | Persona 2 | Evaluar metricas SMART: precision/fidelidad diagnostica frente a Ground Truth y tiempos de inferencia en CPU |
| **E3-10** | [#53](https://github.com/ISCOUTB/savio-ai-recommender/issues/53) | Directrices 6, 8 | abierto | P1 (Alta) | Sprint 4 | OE3 | Equipo completo | Demostracion funcional del backend de inferencia en CPU y cierre de Entrega 3 |

---

## 3. Orden de ejecucion (Camino Critico de Entrega 3)

1. **Paso inmediato (antes del jueves):** `E3-01` (#49, Objetivos SMART y formulario tecnico enviados por WhatsApp) + `E3-02` (`#40`, cronograma fechado).
2. **Etapa OE1 (Datos brutos y Ground Truth):** `E3-04` (#50, contrato de puntajes brutos sin alterar escalas) y `E3-05` (`#42`, tests reales de persona-2 y persona-3) -> desbloquean `E3-06` (`#43`, generacion del corpus *ground truth* con Claude/ChatGPT y literatura oficial de CHASIDE, Felder-Silverman y Personalidad).
3. **Etapa OE2 (Modelo en CPU y Backend):** `E3-07` (#51, pipeline backend de interpretacion integrada, sin frontend) en paralelo con `E3-08` (`#44`, ajuste en Hugging Face y cuantizacion GGUF para CPU sin VRAM).
4. **Etapa OE3 (Validacion y Cierre):** `E3-09` (#52, medicion de fidelidad diagnostica y tiempos de inferencia en CPU) -> `E3-10` (#53, demo del motor backend y cierre).

---

## 4. Detalle de cada Issue de la Entrega 3

### E3-01 - Formular Objetivos SMART y apartados tecnicos del formulario del proyecto

- **GitHub:** [#49](https://github.com/ISCOUTB/savio-ai-recommender/issues/49) | **Estado:** abierto | **Sprint:** Sprint 1
- **Labels:** `entrega-3`, `smart`, `docs`, `equipo`, `docente`
- **Prioridad:** P0 (Critica)
- **Dueno:** Equipo completo
- **Revisor:** Docente del proyecto (via WhatsApp antes de la sesion del jueves)
- **Depende de:** ninguno
- **Desbloquea:** E3-02, E3-04

### Contexto
El docente exigio delimitar el proyecto dejando atras la "generacion de contenido" difusa para enfocarse en un sistema de inferencia con IA para la **interpretacion psicologica y vocacional de estudiantes a partir de tres pruebas estandarizadas** (CHASIDE, Felder-Silverman y Personalidad). Para formalizar la propuesta academica, se requiere redactar 1 Objetivo General y 3 Objetivos Especificos bajo metodologia **SMART** y completar los apartados tecnicos del formulario del proyecto (el docente diligenciara los datos administrativos del grupo y lider de investigacion).

### Pasos Detallados de Ejecucion
1. **Redactar delimitacion y alcance:** Documentar el caso de estudio puntual (apoyo al diagnostico inicial sin reemplazar al profesional) en `docs/entregas/entrega-3-interpretacion-psicometrica/objetivos-smart-formulario.md`.
2. **Formular 1 Objetivo General y 3 Objetivos Especificos SMART:**
   - **OE1 (Specific/Measurable):** Adquisicion y estructuracion de las puntuaciones originales brutas de los 3 tests (sin alterar escalas) y construccion del corpus *ground truth* con LLMs maestros.
   - **OE2 (Achievable/Relevant):** Ajuste/destilacion en la nube (Hugging Face) y cuantizacion del SLM para ejecucion 100% en CPU estandar sin dependencia de VRAM, priorizando backend sobre frontend.
   - **OE3 (Measurable/Time-bound):** Validacion con metricas objetivas (fidelidad diagnostica frente a *ground truth* y tiempos de inferencia en CPU).
3. **Validacion agil por WhatsApp:** Enviar el borrador al docente antes de la sesion del jueves para depurar la redaccion.
4. **Diligenciar formulario:** Volcar el texto aprobado en los apartados tecnicos del formulario oficial del proyecto.

### Criterios de Aceptacion
- [x] Documento `objetivos-smart-formulario.md` creado en el repositorio con desglose S, M, A, R, T, ficha tecnica del formulario y escalas brutas exactas de los 3 bloques.
- [ ] Borrador enviado por WhatsApp al docente antes del encuentro del jueves 29 de octubre.
- [ ] Observaciones del docente incorporadas y apartados tecnicos del formulario completados.

### Entregables
`docs/entregas/entrega-3-interpretacion-psicometrica/objetivos-smart-formulario.md` y apartados tecnicos del formulario del proyecto diligenciados.

---

### E3-02 - Cronograma fechado SMART y plan de trabajo de Entrega 3

- **GitHub:** [#40](https://github.com/ISCOUTB/savio-ai-recommender/issues/40) (recategorizado desde `E2-16`) | **Estado:** abierto | **Sprint:** Sprint 1
- **Labels:** `entrega-3`, `smart`, `docs`, `equipo`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 1 (Coordinador)
- **Revisor:** Equipo completo + Docente
- **Depende de:** E3-01
- **Desbloquea:** E3-04, E3-06, E3-08, E3-09

### Contexto
Este issue absorbe y actualiza el antiguo `E2-16` (#40) para responder al componente **T (Time-bound / Temporal)** de los Objetivos SMART exigidos por el docente, asegurando que todo el sistema quede finalizado y listo para presentarse en la ventana del **3 al 9 de noviembre de 2026**. Define las fechas limite de las tres etapas de ingenieria de la Entrega 3 (`23 Oct al 09 Nov 2026`): (1) OE1 (`23 al 30 Oct`): estructuracion de datos brutos y *ground truth*, (2) OE2 (`31 Oct al 03 Nov`): ajuste en Hugging Face y cuantizacion GGUF para CPU, y (3) OE3 (`03 al 09 Nov`): validacion de metricas diagnosticas, latencia en CPU y presentacion final.

### Pasos Detallados de Ejecucion
1. **Alinear sprints con Objetivos SMART:** Dividir la Entrega 3 en 4 sprints secuenciales con fechas exactas (`Sprint 1: 23-26 Oct`, `Sprint 2 / OE1: 27-30 Oct`, `Sprint 3 / OE2: 31 Oct - 03 Nov`, `Sprint 4 / OE3: 03-09 Nov`).
2. **Hitos semanales (revision de los jueves):** Fijar los entregables que se envian por WhatsApp antes de cada sesion de los jueves (`29 de octubre` y `5 de noviembre`).
3. **Camino critico:** Marcar la secuencia `E3-01 -> E3-04 -> E3-06 -> E3-08 -> E3-09 -> E3-10` (con `E3-05` y `E3-07` en paralelo).
4. **Fecha de congelamiento del backend (*Freeze*):** Establecer el **martes 3 de noviembre de 2026** como fecha tope de ajuste en Hugging Face y congelamiento del modelo GGUF/backend para asegurar la validacion y presentacion entre el **3 y el 9 de noviembre**.

### Criterios de Aceptacion
- [x] Fechas de inicio y fin definidas para los 4 sprints de Entrega 3 y los 3 Objetivos Especificos SMART (`23 Oct al 09 Nov 2026`, con cierre y presentacion del `03 al 09 Nov`).
- [x] Hitos de revision de los jueves (`29 Oct` y `05 Nov`) y fecha de congelamiento (`03 Nov`) integrados en el cronograma.
- [ ] Cronograma aprobado por el equipo y remitido al docente por WhatsApp.

### Entregables
Cronograma fechado en `docs/entregas/entrega-3-interpretacion-psicometrica/README.md` y en `objetivos-smart-formulario.md`.

---

### E3-03 - Lineamientos de consentimiento, anonimizacion y manejo de datos psicometricos

- **GitHub:** [#38](https://github.com/ISCOUTB/savio-ai-recommender/issues/38) (recategorizado desde `E2-14`) | **Estado:** abierto | **Sprint:** Sprint 1
- **Labels:** `entrega-3`, `psicopedagogia`, `legal`, `docente`
- **Prioridad:** P1 (Alta)
- **Dueno:** Equipo / Docente
- **Revisor:** Docente del proyecto
- **Depende de:** ninguno
- **Desbloquea:** E3-05, E3-06

### Contexto
Recategorizado desde `E2-14` (#38). Dado que en la Entrega 3 el sistema procesa resultados de pruebas psicometricas estandarizadas (CHASIDE, Felder-Silverman y Personalidad) para apoyar el diagnostico inicial estudiantil, se mantiene la politica estricta de proteccion de datos personales y etica diagnostica.

### Pasos Detallados de Ejecucion
1. **Regla de repositorio publico:** Garantizar que en Git solo se versionen perfiles anonimizados o simulados (`perfiles/reales/` permanece en `.gitignore`).
2. **Anonimizacion en Hugging Face y LLMs Maestros:** Asegurar que ninguna llamada a Claude/ChatGPT ni ningun dataset subido a Hugging Face incluya nombres reales, correos o codigos estudiantiles identificables (usar solo vectores de puntajes brutos con IDs sinteticos).
3. **Alcance no clinico:** Explicitar en toda salida del backend que el perfil integrado es un insumo orientador para el profesional y no reemplaza el diagnostico psicologico.

### Criterios de Aceptacion
- [ ] Politica de no versionamiento de datos personales reales verificada en `.gitignore`.
- [ ] Protocolo de anonimizacion aplicado al corpus *ground truth* antes de subirlo a Hugging Face.
- [ ] Guardrail de advertencia etica ("apoyo al diagnostico inicial, no reemplaza al profesional") incluido en el backend.

### Entregables
Lineamientos documentados y verificados sobre el corpus de entrenamiento y el motor de inferencia.

---

### E3-04 - Redefinir contrato de entrada con puntajes originales brutos (CHASIDE, Felder-Silverman, Personalidad)

- **GitHub:** [#50](https://github.com/ISCOUTB/savio-ai-recommender/issues/50) | **Estado:** abierto | **Sprint:** Sprint 2 (OE1)
- **Labels:** `entrega-3`, `psicopedagogia`, `backend`, `docs`, `persona-1`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 1 (Apoyo: Persona 2 y Persona 3)
- **Revisor:** Equipo completo
- **Depende de:** E3-01
- **Desbloquea:** E3-05, E3-06, E3-07

### Contexto
En cumplimiento de la Directriz 2 del docente (prohibicion de modificar las escalas validadas por criterio de rigor psicometrico), el sistema de Entrega 3 no debe usar la escala normalizada `1.0-5.0` ni el indice inferido `autonomia`. Debe recibir y validar las **puntuaciones originales brutas** tal como las producen los tres instrumentos validados en los repositorios de Moodle, acompanadas de sus reglas de interpretacion teorica oficial.

### Pasos Detallados de Ejecucion
1. **Definir esquema de puntajes brutos (`docs/especificaciones/perfil-bruto-psicometrico.schema.json`):**
   - **CHASIDE:** puntajes nativos de Interes (`0 a 10`), Aptitud (`0 a 4`) y Total (`0 a 14`) para cada una de las 7 areas (`C, H, A, S, I, D, E`).
   - **Felder-Silverman (ILS):** puntajes nativos por polo (`0 a 11`, suma `11` por dimension) y diferencial oficial (`1, 3, 5, 7, 9, 11`) en las 4 dimensiones bipolares (`activo/reflexivo`, `sensitivo/intuitivo`, `visual/verbal`, `secuencial/global`).
   - **Test de Personalidad:** conteos nativos (`0 a 9` por polo) en los 8 polos del cuestionario institucional, sin el campo `autonomia`.
2. **Sintesis de literatura teorica oficial:** Documentar los baremos y criterios interpretativos originales de cada autor (Felder y Silverman, Holland/CHASIDE, dimensiones conductuales) que alimentaran tanto al LLM maestro como al SLM.
3. **Ejemplos de referencia:** Crear fixtures de perfiles con puntajes brutos reales/simulados validados contra el nuevo contrato.

### Criterios de Aceptacion
- [ ] Contrato JSON de puntajes brutos definido sin ninguna alteracion ni reescalado artificial de los 3 tests.
- [ ] Indice `autonomia` y escala `1.0-5.0` excluidos del flujo de Entrega 3 (conservando los archivos de E2 solo como registro historico).
- [ ] Baremos oficiales de CHASIDE, Felder-Silverman y Personalidad documentados para inyeccion en prompts.

### Entregables
Esquema de puntajes brutos, documentacion de baremos psicometricos originales y fixtures de validacion.

---

### E3-05 - Completar diligenciamiento y extraccion de puntajes brutos reales de los 3 tests

- **GitHub:** [#42](https://github.com/ISCOUTB/savio-ai-recommender/issues/42) (recategorizado desde `E2-18`) | **Estado:** abierto | **Sprint:** Sprint 2 (OE1)
- **Labels:** `entrega-3`, `psicopedagogia`, `persona-2`, `persona-3`
- **Prioridad:** P1 (Alta)
- **Dueno:** Persona 2 y Persona 3
- **Revisor:** Persona 1
- **Depende de:** E3-04
- **Desbloquea:** E3-06, E3-09

### Contexto
Recategorizado desde `E2-18` (#42). Actualmente solo `persona-1` tiene los tres cuestionarios completados en la base de datos. Para validar el sistema de interpretacion psicologica y vocacional con casos humanos reales y diversos, `persona-2` y `persona-3` deben completar las 214 preguntas (44 de Felder-Silverman, 72 de Personalidad y 98 de CHASIDE) y extraer sus **puntuaciones originales brutas**.

### Pasos Detallados de Ejecucion
1. **Diligenciamiento completo:** `persona-2` y `persona-3` completan los 3 cuestionarios estandarizados.
2. **Extraccion de puntajes brutos:** Extraer los conteos nativos (`0-11`, `0-9`, `0-14`) directamente al formato bruto definido en `E3-04`.
3. **Verificacion de integridad psicometrica:** Confirmar que cada eje de Felder-Silverman sume 11 y que los conteos de interes (`0-10`) y aptitud (`0-4`) de CHASIDE coincidan con las respuestas.

### Criterios de Aceptacion
- [ ] Los 3 integrantes (`persona-1`, `persona-2`, `persona-3`) cuentan con sus puntajes originales brutos extraidos y verificados.
- [ ] Los archivos reales se almacenan localmente en `perfiles/reales/` (fuera de Git) y se generan versiones anonimizadas para pruebas de validacion.

### Entregables
Perfiles brutos verificados de los tres integrantes y registro en `experimentos/bitacora.md`.

---

### E3-06 - Construir corpus Ground Truth de interpretacion integrada con LLMs Maestros (Claude/ChatGPT) y literatura tecnica

- **GitHub:** [#43](https://github.com/ISCOUTB/savio-ai-recommender/issues/43) (recategorizado desde `E2-19`) | **Estado:** abierto | **Sprint:** Sprint 2 (OE1)
- **Labels:** `entrega-3`, `slm`, `destilacion`, `psicopedagogia`, `docs`, `equipo`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 3 (Lider Tecnico SLM) | Apoyo: Persona 1 y Persona 2
- **Revisor:** Equipo completo
- **Depende de:** E3-04, E3-05
- **Desbloquea:** E3-08, E3-09

### Contexto
Recategorizado y actualizado desde `E2-19` (#43) segun las Directrices 1, 2 y 3 del docente. Los LLMs de frontera (**Claude, ChatGPT**) se utilizan en fase de laboratorio como modelos "maestros" (*Teacher*). Se les alimenta con la bibliografia tecnica oficial de CHASIDE, Felder-Silverman y Personalidad junto con combinaciones diversas de puntuaciones brutas para generar salidas interpretativas de alta calidad (*ground truth*) que ensenen al SLM a correlacionar los tres instrumentos.

### Pasos Detallados de Ejecucion
1. **Diseno del Prompt Maestro (Teacher):** Incluir los baremos oficiales y la literatura tecnica de los 3 tests para que Claude / ChatGPT redacte interpretaciones psicologicas, de aprendizaje y vocacionales cruzadas rigurosas.
2. **Muestreo de combinaciones psicometricas:** Generar al menos 150 vectores de puntajes brutos realistas y contrastantes (cubriendo distintas dominancias de CHASIDE, polos de Felder-Silverman y perfiles conductuales, incluyendo congruencias y brechas entre interes y aptitud).
3. **Generacion y curacion del Ground Truth:** Producir las salidas interpretativas con los LLMs maestros y auditar que ninguna altere los puntajes brutos ni emita juicios clinicos patologizantes.
4. **Estructuracion para Hugging Face:** Formatear el corpus en JSONL (`instruction`, `input`, `output`) con particion 80% entrenamiento / 20% validacion sin fuga de datos.

### Criterios de Aceptacion
- [ ] Prompt maestro fundamentado en la bibliografia tecnica de CHASIDE, Felder-Silverman y Personalidad documentado.
- [ ] Corpus JSONL con al menos 150 pares `(puntajes_brutos_3_tests -> interpretacion_integrada_ground_truth)`.
- [ ] 100% de las muestras verificadas: respetan las escalas originales brutas y el rol de apoyo al diagnostico inicial.
- [ ] Particion 80/20 (train/eval) lista para cargar en Hugging Face.

### Entregables
Corpus *ground truth* en formato JSONL, script/plantilla de generacion Teacher y documentacion del dataset.

---

### E3-07 - Implementar pipeline backend de inferencia para interpretacion psicologica y vocacional integrada

- **GitHub:** [#51](https://github.com/ISCOUTB/savio-ai-recommender/issues/51) | **Estado:** abierto | **Sprint:** Sprint 3 (OE2)
- **Labels:** `entrega-3`, `backend`, `slm`, `cpu-only`, `persona-1`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 1
- **Revisor:** Persona 2, Persona 3
- **Depende de:** E3-04
- **Desbloquea:** E3-09, E3-10

### Contexto
Aplica las Directrices 5 (*Rechazo a la sobreingenieria prematura*) y 6 (*Prioridad funcional: "Backend antes que Frontend"*) del docente. No se debe construir ninguna interfaz grafica ni arquitectura compleja de microservicios; la prioridad absoluta es un pipeline backend limpio en Python que reciba las puntuaciones originales brutas de los tres cuestionarios, ejecute la inferencia sobre CPU con el SLM cuantizado y devuelva el perfil interpretativo integrado estructurado y validado.

### Pasos Detallados de Ejecucion
1. **Definicion clara de Entrada -> Procesamiento -> Salida:**
   - **Entrada:** JSON con los puntajes originales brutos de CHASIDE, Felder-Silverman y Personalidad.
   - **Procesamiento:** Validacion de rangos nativos, inyeccion de baremos oficiales y llamada al motor de inferencia local en CPU.
   - **Salida:** Informe estructurado con (1) Lectura de Estilos Felder-Silverman, (2) Lectura Conductual de Personalidad, (3) Lectura Vocacional CHASIDE, y (4) Sintesis Integrada de Correlaciones para apoyo al diagnostico inicial.
2. **Verificador automatico de rigor psicometrico:** Comprobar en post-procesamiento que el modelo cite exactamente los puntajes brutos de entrada sin inventar escalas ni emitir etiquetas clinicas.
3. **Pruebas unitarias de backend:** Crear pruebas automatizadas sin necesidad de interfaz grafica.

### Criterios de Aceptacion
- [ ] Script backend ejecutable por linea de comandos sobre CPU estandar que procesa los puntajes brutos de los 3 tests.
- [ ] Salida estructurada en las 4 secciones de interpretacion integrada y exportable en JSON/Markdown.
- [ ] Validador post-inferencia que garantiza fidelidad a los puntajes brutos de entrada y respeto de guardrails.

### Entregables
Pipeline backend de interpretacion psicometrica integrada y suite de pruebas de verificacion.

---

### E3-08 - Ajustar/destilar SLM en Hugging Face y cuantizar a GGUF para ejecucion 100% en CPU (sin VRAM)

- **GitHub:** [#44](https://github.com/ISCOUTB/savio-ai-recommender/issues/44) (recategorizado desde `E2-20`) | **Estado:** abierto | **Sprint:** Sprint 3 (OE2)
- **Labels:** `entrega-3`, `slm`, `destilacion`, `huggingface`, `cpu-only`, `equipo`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 3 (Lider Tecnico SLM)
- **Revisor:** Equipo completo
- **Depende de:** E3-06
- **Desbloquea:** E3-09, E3-10

### Contexto
Recategorizado y actualizado desde `E2-20` (#44) para incorporar las Directrices 3 y 4 del docente: dado que ni los equipos locales del grupo ni los servidores institucionales (cluster Savio) cuentan con VRAM dedicada para este proposito, el entrenamiento/ajuste del SLM se realiza utilizando plataformas en la nube con capas gratuitas o gestionadas (**Hugging Face** / Colab) y el despliegue final se resuelve mediante un **modelo cuantizado (GGUF)** optimizado para ejecutarse sobre **CPU estandar**.

### Pasos Detallados de Ejecucion
1. **Entorno gestionado en la nube (Hugging Face):** Configurar el flujo de entrenamiento (SFT / LoRA / QLoRA) en el ecosistema de Hugging Face (`transformers`, `peft`, `trl`) sobre una capa gratuita/gestionada de GPU en la nube, sin depender del hardware local.
2. **Ajuste con el Ground Truth psicometrico:** Entrenar el SLM compacto (`Qwen 2.5 0.5B` o `1.5B`) con el dataset de interpretaciones integradas de `E3-06`, registrando hiperparametros y curva de perdida (*loss*).
3. **Fusion y cuantizacion para CPU:** Fusionar los adaptadores y convertir el modelo a formato **GGUF cuantizado (`Q4_K_M` / `Q8_0`)** para reducir la precision numerica manteniendo la capacidad interpretativa.
4. **Despliegue local sin VRAM:** Cargar el artefacto GGUF en el motor local (Ollama / `llama.cpp`) forzando ejecucion en **CPU estandar (`num_gpu=0`)** y verificar que corra en cualquier computador convencional.

### Criterios de Aceptacion
- [ ] Notebook/script reproducible de ajuste ejecutado en Hugging Face / entorno cloud gestionado con hiperparametros documentados.
- [ ] Pesos del SLM ajustado exportados a formato GGUF cuantizado y publicados/respaldados en Hugging Face Hub.
- [ ] Inferencia verificada localmente en modo **100% CPU (0 MB de VRAM obligatoria)**.

### Entregables
Repositorio/artefacto GGUF del SLM cuantizado en Hugging Face, notebook reproducible de entrenamiento y Modelfile para ejecucion en CPU.

---

### E3-09 - Evaluar metricas SMART: precision/fidelidad diagnostica frente a Ground Truth y tiempos de inferencia en CPU

- **GitHub:** [#52](https://github.com/ISCOUTB/savio-ai-recommender/issues/52) | **Estado:** abierto | **Sprint:** Sprint 4 (OE3)
- **Labels:** `entrega-3`, `smart`, `slm`, `cpu-only`, `psicopedagogia`, `persona-2`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 2 (Apoyo: Persona 1 y Persona 3)
- **Revisor:** Equipo completo + Docente
- **Depende de:** E3-06, E3-07, E3-08
- **Desbloquea:** E3-10

### Contexto
Responde a la Directriz 7 del docente (criterio **M - Measurable / Medible** de los Objetivos SMART): *"definir metricas objetivas para comprobar si el modelo quedo bien destiladito o cuantificado (precision de diagnostico, tiempos de inferencia)"*. Evalua cuantitativamente el SLM cuantizado corriendo en CPU frente a las interpretaciones de referencia (*ground truth*) producidas por los LLMs maestros.

### Pasos Detallados de Ejecucion
1. **Protocolo de evaluacion de fidelidad diagnostica:** Evaluar el SLM cuantizado sobre el 20% de prueba del dataset `E3-06` y los 3 perfiles reales de `E3-05` bajo 5 dimensiones objetivas:
   - Exactitud en la lectura de los puntajes brutos de CHASIDE, Felder-Silverman y Personalidad (0 alucinaciones numericas).
   - Coherencia de la correlacion cruzada entre los 3 instrumentos frente al *ground truth*.
   - Cumplimiento de estructura de 4 bloques del backend.
   - Respeto de guardrails eticos (tono descriptivo de apoyo inicial, sin diagnosticos clinicos ni alteracion de escalas).
2. **Benchmark de rendimiento en CPU estandar:** Medir sobre hardware convencional sin GPU dedicada:
   - Tiempo total de inferencia por perfil integrado (segundos).
   - Velocidad de generacion (tokens/segundo en CPU).
   - Consumo pico de memoria RAM (MB/GB) y confirmacion de `0 MB` de VRAM.
3. **Comparativa antes vs. despues del ajuste/cuantizacion:** Documentar la ganancia de calidad del SLM ajustado frente al SLM base sin ajustar.

### Criterios de Aceptacion
- [ ] Fidelidad interpretativa medida sobre el conjunto de validacion ($\ge 85\%$ respecto al *ground truth*).
- [ ] Tabla de tiempos de inferencia, tokens/s y huella de RAM en CPU estandar documentada con datos reales medidos.
- [ ] Comparativa objetiva entre modelo base, modelo ajustado cuantizado y referencia Teacher (Claude/ChatGPT).

### Entregables
Reporte de validacion SMART y resultados de benchmarks en CPU registrados en `experimentos/bitacora.md`.

---

### E3-10 - Demostracion funcional del backend de inferencia en CPU y cierre de Entrega 3

- **GitHub:** [#53](https://github.com/ISCOUTB/savio-ai-recommender/issues/53) | **Estado:** abierto | **Sprint:** Sprint 4 (OE3)
- **Labels:** `entrega-3`, `backend`, `cpu-only`, `equipo`, `docente`
- **Prioridad:** P1 (Alta)
- **Dueno:** Equipo completo (Persona 1, Persona 2, Persona 3)
- **Revisor:** Docente del proyecto
- **Depende de:** E3-07, E3-08, E3-09
- **Desbloquea:** Aprobacion de la Entrega 3

### Contexto
Consolidar y demostrar ante el docente el funcionamiento de extremo a extremo del motor backend de inferencia ejecutandose en CPU estandar: entrada de puntuaciones originales brutas de CHASIDE, Felder-Silverman y Personalidad -> procesamiento por el SLM destilado y cuantizado -> salida de interpretacion psicologica y vocacional integrada validada con metricas SMART.

### Pasos Detallados de Ejecucion
1. **Guion reproducible de demostracion (100% Backend en CPU):** Preparar los comandos de ejecucion en consola con perfiles contrastantes y respaldos pre-generados.
2. **Verificacion de los 8 acuerdos del docente:** Confirmar en el checklist final que se cumplieron todas las restricciones (caso concreto psicometrico, escalas brutas intactas, SLM destilado/cuantizado desde LLM maestro, inferencia en CPU sin VRAM, sin sobreingenieria, backend antes que frontend y objetivos SMART medidos).
3. **Cierre documental en el repositorio:** Actualizar `experimentos/bitacora.md` y el reporte de cierre en `docs/entregas/entrega-3-interpretacion-psicometrica/README.md`.

### Criterios de Aceptacion
- [ ] Demostracion del pipeline backend ejecutada en CPU estandar sin errores ni dependencia de GPU.
- [ ] Evidencia de entrada (puntajes brutos), salida (perfil integrado) y metricas SMART documentada en el repositorio.
- [ ] Todos los issues del milestone `Entrega 3 - Interpretacion Psicometrica` cerrados y verificados.

### Entregables
Guion y evidencias de demostracion del backend en CPU y reporte de cierre de la Entrega 3.

