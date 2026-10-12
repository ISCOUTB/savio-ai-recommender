# Issues de Entrega 2 — Savio AI Recommender

Este documento contiene la especificacion exhaustiva de los 12 issues de la Entrega 2 (Personalizacion). Sirve como fuente de verdad para el seguimiento del equipo y para importar al tablero de tareas (Kanban).

Milestone: `Entrega 2 - Personalizacion`  
Labels disponibles: `entrega-2`, `docs`, `repo`, `moodle`, `psicopedagogia`, `slm`, `destilacion`, `feedback`, `persona-1`, `persona-2`, `persona-3`, `equipo`, `docente`.

Regla de flujo:
- Maximo 1 issue en 'En progreso' por persona de manera simultanea.
- Todo issue completado requiere revision obligatoria por par antes de cerrarse.
- Todo commit sigue el estandar: `tipo(alcance): descripcion (#issue)` en espanol sin tildes.

---

## E2-01 - Estructurar Entrega 2 en GitHub y ROADMAP

- **Labels:** `entrega-2`, `repo`, `docs`, `equipo`
- **Prioridad:** P0 (Critica)
- **Dueno:** Equipo (Lider: Persona 1)
- **Revisores:** Persona 2, Persona 3
- **Depende de:** Ninguno
- **Estado:** ✅ Completado

### Contexto y Objetivo
Dejar formalmente organizada y verificada la estructura documental, el plan operativo y el tablero de seguimiento para toda la Entrega 2, garantizando alineacion con las directrices institucionales del docente.

### Criterios de Aceptacion
- [x] Estructura de carpetas `docs/entregas/entrega-2-personalizacion/` creada con sus 6 archivos de sprint.
- [x] `ROADMAP.md` actualizado reflejando Entrega 1 completada y Entrega 2 en curso.
- [x] Tablero Kanban estructurado con columnas Backlog, En progreso, En revision y Listo.
- [x] Schemas base JSON en `docs/especificaciones/` y carpetas de soporte (`perfiles/`, `experimentos/`, `moodle/`) inicializadas.

### Entregable
Documentacion base de Entrega 2 en el repositorio y ROADMAP sincronizado.

---

## E2-02 - Moodle local en Docker operativo

- **Labels:** `entrega-2`, `moodle`, `equipo`, `docente`
- **Prioridad:** P1 (Alta)
- **Dueno:** Persona 2 (Apoyo: Equipo)
- **Revisor:** Persona 1
- **Depende de:** E2-01
- **Desbloquea:** E2-03, E2-12
- **Estado:** 🔄 Abierto / En progreso

### Contexto
Moodle es unicamente el habilitador minimo de la Entrega 2 (representa solo el 15% del esfuerzo). Su proposito es proporcionar una instancia local en Docker para alojar los cursos y los bloques de tests de la UTB. No se busca programar plugins desde cero ni hacer configuraciones avanzadas.

### Pasos Detallados de Ejecucion
1. **Verificar prerrequisitos:** Asegurarse de que Docker Desktop este ejecutandose en Windows (icono de la ballena activo).
2. **Ubicarse en el directorio:** Abrir terminal en la carpeta `moodle/` del repositorio.
3. **Comprobar puerto 8080:** Confirmar que el puerto 8080 este libre (el contenedor previo ya fue detenido).
4. **Levantar contenedores en segundo plano:** Ejecutar `docker compose up -d`. Docker descargara las imagenes de `mariadb:10.11` y `moodlehq/moodle:latest`.
5. **Verificar estado:** Ejecutar `docker compose ps` y confirmar que `moodle-db-1` y `moodle-moodle-1` tengan estado `Up`.
6. **Revisar logs de inicializacion:** Ejecutar `docker compose logs -f moodle` y esperar a que la base de datos termine su configuracion inicial.
7. **Acceso web:** Abrir el navegador e ingresar a `http://localhost:8080`.
8. **Documentar procedimiento:** Completar `moodle/README.md` con credenciales de acceso y comandos de parada (`docker compose stop`/`down`).
9. **Regla de contingencia:** Si Moodle presenta demoras o errores de red, registrar el incidente en `experimentos/bitacora.md` y continuar el trabajo usando fixtures JSON simulados en `perfiles/`. La investigacion de IA nunca se detiene por Moodle.

### Criterios de Aceptacion
- [ ] `docker compose up -d` arranca sin errores de red ni colisiones de puertos.
- [ ] Interfaz web de Moodle accesible en `http://localhost:8080`.
- [ ] Comandos de inicio, parada y credenciales documentados con claridad en `moodle/README.md`.
- [ ] Guia paso a paso para principiantes disponible para el equipo.

### Entregables
`moodle/README.md` actualizado con bitacora de encendido y guia paso a paso `Guia_Paso_a_Paso_Docker_Moodle_E2_02.docx`.

---

## E2-03 - Instalar bloques IS-UTB y diligenciar tests

- **Labels:** `entrega-2`, `moodle`, `psicopedagogia`, `docente`
- **Prioridad:** P1 (Alta)
- **Dueno:** Equipo (Lider de coordinacion: Persona 3)
- **Revisor:** Docente del proyecto
- **Depende de:** E2-02
- **Desbloquea:** E2-04, E2-05, E2-06 (con datos reales)
- **Estado:** ⏳ Pendiente

### Contexto
Para alimentar el perfil psicopedagogico se requieren tres instrumentos institucionales: Estilos de Aprendizaje, Personalidad y CHASIDE. Segun la directriz del docente, estos bloques se instalan en el Moodle local con su apoyo o se diligencian en Savio institucional. Si no estan disponibles a tiempo, se utilizan datos simulados del equipo.

### Pasos Detallados de Ejecucion
1. **Gestion con docente:** Solicitar la provision o guia de instalacion de los tres bloques IS-UTB en la instancia de Moodle.
2. **Diligenciamiento distribuido:**
   - Persona 1 diligencia el test de Estilos de Aprendizaje.
   - Persona 2 diligencia el test de Personalidad.
   - Persona 3 diligencia el test de CHASIDE.
3. **Extraccion de resultados:** Tomar captura o transcripcion de los puntajes obtenidos en cada bloque.
4. **Plan B (Fixtures simulados):** Si hay retraso con los bloques del docente, cada integrante genera un archivo JSON en `perfiles/` con valores representativos, indicando el campo `"origen": "simulado"`.
5. **Registro de estado:** Documentar en `moodle/plugins.md` el estado de instalacion de cada bloque o el bloqueo correspondiente.

### Criterios de Aceptacion
- [ ] Bloques instalados en Moodle local o bloqueo documentado en `moodle/plugins.md`.
- [ ] Cada integrante tiene un conjunto de respuestas diligenciadas (reales o fixture simulado).
- [ ] Los fixtures simulados siguen exactamente el formato de puntajes numericos requerido.

### Entregables
Archivo `moodle/plugins.md` actualizado y fixtures de prueba en `perfiles/`.

---

## E2-04 - Modelar Test de Estilos de Aprendizaje

- **Labels:** `entrega-2`, `psicopedagogia`, `persona-1`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 1
- **Revisor:** Persona 2
- **Depende de:** E2-01
- **Desbloquea:** E2-07, E2-10
- **Estado:** 🔄 Listo para ejecucion en rama `dev/persona-1`

### Contexto
El recomendador no debe usar reglas rigidas `si visual -> video`. Debe razonar in-context a partir de un resumen psicopedagogico claro. Persona 1 debe investigar el marco de Estilos de Aprendizaje (modelo VAK: Visual, Auditivo, Kinestesico, Lectura/Escritura, o modelo Felder-Silverman) y definir como convertir las metricas del bloque en directrices accionables para el SLM.

### Pasos Detallados de Ejecucion
1. **Marco teorico:** Documentar el modelo VAK / Felder-Silverman y su pertinencia para cursos universitarios en Savio.
2. **Estructura numerica:** Definir los campos cuantitativos (`visual`, `auditivo`, `kinestesico`, `lectura_escritura`), su rango de puntuacion (ej. 0-10 o porcentajes) y el calculo del estilo dominante.
3. **Mapeo a formatos didacticos:**
   - Visual: Privilegiar diagramas de flujo, infografias, mapas conceptuales y videos esquematicos. Evitar lecturas densas sin apoyo grafico.
   - Textual/Lectura: Privilegiar articulos analiticos, resumenes estructurados, definiciones y glosarios. Evitar diagramas recargados.
   - Auditivo: Privilegiar podcasts, notas de voz, debates y explicaciones dialogadas.
   - Kinestesico: Privilegiar ejercicios interactivos, analisis de casos practicos y simulaciones.
4. **Generador de texto para el Prompt:** Construir la regla de sintesis que transforma los numeros en una frase in-context: `descripcion_para_prompt`.
5. **Redaccion de nota tecnica:** Crear el documento `docs/especificaciones/instrumento-estilos-aprendizaje.md` con tablas, ejemplos y justificacion.

### Criterios de Aceptacion
- [ ] Modelo psicopedagogico documentado y justificado teoricamente.
- [ ] Campos propuestos para `perfil.estilos_aprendizaje` definidos con tipos de datos y rangos.
- [ ] Reglas de inclusion y exclusion de formatos didacticos por estilo formalizadas.
- [ ] Ejemplo de descripcion textual validado con al menos dos perfiles contrastantes (ej. fuertemente visual vs mixto).

### Entregable
Documento tecnico `docs/especificaciones/instrumento-estilos-aprendizaje.md`.

---

## E2-05 - Modelar Test de Personalidad

- **Labels:** `entrega-2`, `psicopedagogia`, `persona-2`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 2
- **Revisor:** Persona 3
- **Depende de:** E2-01
- **Desbloquea:** E2-07, E2-10
- **Estado:** ⏳ Pendiente

### Contexto
El instrumento de personalidad institucional mide rasgos conductuales clave frente al estudio (autonomia, metodicidad, introversion/extraversion, apertura a la experiencia). Persona 2 debe traducir estos rasgos a preferencias pedagogicas utiles para la seleccion de recursos, respetando guardrails eticos estrictos (no etiquetar clinicamente al estudiante).

### Pasos Detallados de Ejecucion
1. **Identificacion de rasgos:** Documentar las dimensiones evaluadas por el bloque de personalidad institucional.
2. **Impacto en el consumo de recursos:** Explicar como influye cada rasgo en el aprendizaje:
   - Alta autonomia: Tolera recursos abiertos y retos exploratorios a ritmo propio.
   - Baja autonomia / Alta necesidad de guia: Requiere recursos estructurados paso a paso con checklists.
   - Alta metodicidad: Prefiere guias secuenciales y cronogramas definidos.
   - Introversion vs Extraversion: Define preferencias por estudio individual vs debates o foros.
3. **Estructura JSON:** Definir los campos de `perfil.personalidad` (puntajes numericos, `resumen_conductual` y `preferencias_trabajo`).
4. **Guardrail etico:** Establecer la regla explicita de que el sistema no emite diagnosticos psicologicos ni juicios de valor, unicamente sugerencias de formato de estudio.
5. **Redaccion de nota tecnica:** Crear `docs/especificaciones/instrumento-personalidad.md`.

### Criterios de Aceptacion
- [ ] Dimensiones conductuales documentadas y justificadas.
- [ ] Matriz de relacion entre rasgos de personalidad y formatos de recursos explicada.
- [ ] Campos de `perfil.personalidad` alineados con el schema unificado.
- [ ] Guardrails de lenguaje empatico y no punitivo integrados en la descripcion.

### Entregable
Documento tecnico `docs/especificaciones/instrumento-personalidad.md`.

---

## E2-06 - Modelar Test CHASIDE

- **Labels:** `entrega-2`, `psicopedagogia`, `persona-3`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 3
- **Revisor:** Persona 1
- **Depende de:** E2-01
- **Desbloquea:** E2-07, E2-10
- **Estado:** ⏳ Pendiente

### Contexto
El test CHASIDE es un instrumento de orientacion vocacional clasificado en 7 areas: Administrativas y Contables (C), Humanisticas y Sociales (H), Artisticas (A), Salud y Medicina (S), Ingenieria y Computacion (I), Defensa y Seguridad (D), Exactas y Agrarias (E). En este proyecto se utiliza exclusivamente para generar analogias y ejemplos contextuales dentro de la materia piloto, mejorando la conexion afectiva y motivacion del estudiante (modelo ARCS).

### Pasos Detallados de Ejecucion
1. **Documentacion de areas:** Detallar el significado de las 7 categorias del test CHASIDE.
2. **Regla de oro pedagogica:** CHASIDE no determina el contenido disciplinar de la materia ni el nivel de dificultad; su unica funcion es guiar las metaforas, analogias y aplicaciones practicas usadas por el SLM.
3. **Estructura JSON:** Definir los campos de `perfil.chaside` (puntajes de C a E, lista de `areas_dominantes` y `descripcion_para_analogias`).
4. **Ejemplos aplicados a la materia piloto:**
   - Estudiante con dominancia 'I' (Ingenieria) en Taller de Escritura: Ejemplificar la estructura de un ensayo usando analogias de arquitectura de software o diseno de sistemas.
   - Estudiante con dominancia 'H' (Humanidades): Ejemplificar usando debates sociales o comunicacion persuasiva.
5. **Redaccion de nota tecnica:** Crear `docs/especificaciones/instrumento-chaside.md`.

### Criterios de Aceptacion
- [ ] Las 7 areas vocacionales documentadas con ejemplos aplicables a ingenieria.
- [ ] Reglas de restriccion pedagogica (uso exclusivo para analogias) formalizadas.
- [ ] Campos de `perfil.chaside` especificados con precision.
- [ ] Al menos dos ejemplos de analogias contextuales documentados.

### Entregable
Documento tecnico `docs/especificaciones/instrumento-chaside.md`.

---

## E2-07 - Consolidar schema JSON del perfil

- **Labels:** `entrega-2`, `psicopedagogia`, `docs`, `equipo`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 1 (Coordinador) | Apoyo: Persona 2 y Persona 3
- **Revisor:** Equipo completo
- **Depende de:** E2-04, E2-05, E2-06
- **Desbloquea:** E2-10, E2-11
- **Estado:** ⏳ Pendiente

### Contexto
Unificar las especificaciones de los tres instrumentos psicopedagogicos en un unico archivo JSON Schema (Draft-07). El esquema resultante debe ser plano, sin anidacion innecesaria, facil de validar y optimizado para consumir pocos tokens cuando se inyecte en el prompt del SLM.

### Pasos Detallados de Ejecucion
1. **Consolidacion:** Integrar las definiciones tecnicas de E2-04, E2-05 y E2-06.
2. **Actualizar Schema:** Ajustar `docs/especificaciones/perfil-estudiante.schema.json` asegurando validacion de tipos, minimos, maximos y enums.
3. **Generar Fixture Realista:** Actualizar `perfiles/ejemplo-perfil-estudiante.json` con un perfil representativo completo.
4. **Script de validacion:** Crear un script ligero en Python (`poc_slm/validar_schemas.py`) que compruebe automaticamente la validez del fixture contra el schema JSON.
5. **Medicion de tamano en tokens:** Verificar que el perfil completo serializado ocupe menos de 350 tokens para no saturar la ventana de contexto del SLM.

### Criterios de Aceptacion
- [ ] `docs/especificaciones/perfil-estudiante.schema.json` es sintacticamente valido bajo JSON Schema Draft-07.
- [ ] `perfiles/ejemplo-perfil-estudiante.json` pasa la validacion automatizada sin advertencias.
- [ ] El esquema prohíbe propiedades no declaradas (`additionalProperties: false`) para evitar datos espurios.
- [ ] Script de validacion ejecutable con `python poc_slm/validar_schemas.py`.

### Entregables
`perfil-estudiante.schema.json`, `ejemplo-perfil-estudiante.json` y script validador en Python.

---

## E2-08 - Seleccionar materia piloto y recursos A/B/C

- **Labels:** `entrega-2`, `docs`, `slm`, `equipo`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 2
- **Revisor:** Persona 1, Persona 3
- **Depende de:** E2-01
- **Desbloquea:** E2-09, E2-10
- **Estado:** ⏳ Pendiente

### Contexto
Para probar el recomendador adaptativo se debe seleccionar un curso piloto y reunir recursos didacticos en formatos marcadamente contrastantes para una semana especifica. Siguiendo la recomendacion docente, la primera opcion es 'Taller de Escritura' (alternativa si se requiere informatica: Arquitectura de Software). El modelo debera elegir entre Recurso A, Recurso B o Recurso C segun el perfil.

### Pasos Detallados de Ejecucion
1. **Seleccion de materia:** Formalizar la seleccion de 'Taller de Escritura' y justificar por que es ideal para evaluar adaptacion pedagogica sin sesgos de codigo.
2. **Diseno de Semana 1:** Seleccionar un tema academico concreto (ej. 'Estructura del Ensayo Argumentativo: Tesis y Contraargumentos').
3. **Curaduria de los 3 recursos contrastantes:**
   - **Recurso A (Visual/Sintetico):** Mapa conceptual o infografia interactiva con flujo logico de la tesis.
   - **Recurso B (Textual/Analitico):** Guia de lectura con analisis de dos ensayos modelo y glosario.
   - **Recurso C (Practico/Interactiva):** Taller guiado de aplicacion paso a paso con rubrica y ejercicios cortos.
4. **Estructuracion en JSON:** Formalizar los tres recursos segun `docs/especificaciones/recurso-semanal.schema.json` y guardarlos en `poc_slm/recursos/semana_1.json`.
5. **Verificacion de contraste:** Validar que los recursos sean genuinamente distintos para que el SLM no pueda tomar decisiones triviales por defecto.

### Criterios de Aceptacion
- [ ] Materia piloto justificada formalmente en documentacion.
- [ ] Semana 1 definida con tema academico claro.
- [ ] Opciones A, B y C con tipo, formato, resumen, nivel y tiempo estimado diferenciados.
- [ ] Archivo `poc_slm/recursos/semana_1.json` validado contra `recurso-semanal.schema.json`.

### Entregables
Documento `docs/especificaciones/materia-piloto-recursos.md` y archivo de recursos `poc_slm/recursos/semana_1.json`.

---

## E2-09 - Pipeline de destilacion y fine-tuning (60% del esfuerzo)

- **Labels:** `entrega-2`, `slm`, `destilacion`, `equipo`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 3 (Lider Tecnico SLM) | Apoyo: Persona 1 (Dataset B) y Persona 2 (Dataset A)
- **Revisor:** Equipo completo + Docente
- **Depende de:** E2-01, E2-08
- **Desbloquea:** E2-12
- **Estado:** ⏳ Pendiente

### Contexto
Este es el nucleo innovador de la Entrega 2. El equipo debe investigar y proponer como llevar un modelo de referencia (Teacher, ej. Qwen 2.5 1.5B o 3B) hacia un Small Language Model especializado de escala ultra-reducida (Student, ~0.5B, ej. Qwen 2.5 0.5B o SmolLM2), capaz de razonar sobre perfiles y recursos consumiendo minima memoria RAM y KV cache.

### Pasos Detallados de Ejecucion
1. **Analisis comparativo de modelos:** Evaluar candidatos (Qwen 2.5 0.5B, SmolLM2 360M/1.7B, Gemma 2 2B, Llama 3.2 1B) en memoria base, soporte de espanol y formato de despliegue en Ollama.
2. **Modelado de memoria y KV Cache:** Calcular la memoria consumida por usuario concurrente para estimar la capacidad institucional de Savio.
3. **Estructuracion de Datasets:**
   - **Dataset A (Materia piloto):** Conceptos, explicaciones y errores comunes de Taller de Escritura (a cargo de Persona 2).
   - **Dataset B (Psicopedagogico):** Ejemplos de tripletas (Perfil del estudiante + 3 Recursos -> Recurso elegido con justificacion formativa y descarte de alternativas) (a cargo de Persona 1).
4. **Definicion de tecnica:** Comparar destilacion teacher-student vs LoRA/QLoRA ligero vs cuantizacion en 4 bits (Q4_K_M).
5. **Analisis de licencias:** Revisar licencias de cada modelo candidato (Apache 2.0 vs Tongyi Qianwen Research/Commercial) para garantizar viabilidad institucional.
6. **Preservacion de Guardrails:** Definir el protocolo de pruebas para comprobar que el modelo afinado no pierda las restricciones aprendidas en Entrega 1.
7. **Documento tecnico:** Redactar la propuesta formal completa en `docs/investigacion/propuesta-destilacion-slm.md`.

### Criterios de Aceptacion
- [ ] Tabla comparativa de modelos con RAM estimada, latencia, tokens/s y licencias.
- [ ] Arquitectura Teacher-Student y tecnica de adaptacion seleccionada y justificada.
- [ ] Esquema y formato de muestras para Dataset A y Dataset B definidos.
- [ ] Mediciones o calculos teoricos de KV cache documentados.
- [ ] Matriz de riesgos y preservacion de guardrails incluida.

### Entregable
Documento de investigacion `docs/investigacion/propuesta-destilacion-slm.md`.

---

## E2-10 - Prototipo de Prompt Builder semanal

- **Labels:** `entrega-2`, `slm`, `docs`, `equipo`
- **Prioridad:** P0 (Critica)
- **Dueno:** Persona 1
- **Revisor:** Persona 2, Persona 3
- **Depende de:** E2-07, E2-08
- **Desbloquea:** E2-11, E2-12
- **Estado:** ⏳ Pendiente

### Contexto
Desarrollar el componente de software que toma en tiempo de ejecucion el JSON del perfil del estudiante y la lista de recursos A/B/C de la semana, construye el prompt in-context y se lo envia al SLM local para producir una recomendacion adaptada, con justificacion pedagogica y explicacion del descarte de las demas opciones.

### Pasos Detallados de Ejecucion
1. **Diseno de plantilla de prompt:** Crear la estructura del prompt dividida en secciones:
   - Datos del estudiante (estilo, personalidad, chaside).
   - Opciones disponibles (Recurso A, B, C con sus caracteristicas).
   - Instruccion de decision y formato de salida estricto.
2. **Inyeccion de guardrails:** Incluir regla anti-alucinacion (solo seleccionar entre las opciones dadas, no inventar enlaces ni autores) y regla de tono empatico.
3. **Implementacion en Python:** Desarrollar `poc_slm/prompt_builder.py` que importe `requests`, cargue los archivos JSON y realice la inferencia contra la API de Ollama (`http://localhost:11434/api/generate`).
4. **Formato de respuesta:** Exigir al modelo una salida estructurada:
   - Recurso Recomendado (A, B o C y titulo).
   - Justificacion Pedagogica (por que se ajusta a su perfil).
   - Razon de Descarte (por que no se priorizaron las otras dos opciones).
5. **Pruebas de ejecucion:** Probar el script con al menos 3 perfiles contrastantes y guardar las respuestas.

### Criterios de Aceptacion
- [ ] Script funcional `poc_slm/prompt_builder.py` que ensambla perfil + recursos y llama a Ollama.
- [ ] Formato de salida que incluye recomendacion, justificacion y descarte razonado.
- [ ] Guardrails de no invencion verificados en pruebas de generacion.
- [ ] 3 ejemplos de ejecucion documentados en `prompts/escenarios/personalizacion_semanal.md`.

### Entregables
Script `poc_slm/prompt_builder.py` y archivo de ejemplos `prompts/escenarios/personalizacion_semanal.md`.

---

## E2-11 - Feedback loop y metricas

- **Labels:** `entrega-2`, `feedback`, `docs`, `equipo`
- **Prioridad:** P2 (Media)
- **Dueno:** Persona 2
- **Revisor:** Persona 3
- **Depende de:** E2-07, E2-10
- **Desbloquea:** E2-12
- **Estado:** ⏳ Pendiente

### Contexto
El sistema no es determinista y requiere medir si sus decisiones aciertan pedagogicamente. Este issue modela el circuito de retroalimentacion por el cual el estudiante califica la recomendacion recibida, permitiendo cuantificar los resultados y sentar las bases para la posterior validacion ARCS/IMMS.

### Pasos Detallados de Ejecucion
1. **Validacion de Schema:** Comprobar y asegurar la integridad de `docs/especificaciones/feedback.schema.json`.
2. **Definicion de instrumentos de feedback:**
   - Escala binaria primaria: `util` (true / false).
   - Escala Likert complementaria: valor de 1 a 5 estrellas.
   - Campo abierto opcional: comentario del estudiante.
3. **Formulacion de metricas (KPIs):**
   - Tasa de Acierto = (Recomendaciones marcadas como utiles / Total recomendaciones evaluadas) * 100.
   - Tasa de Descache = (Recomendaciones marcadas como no utiles / Total recomendaciones evaluadas) * 100.
4. **Modulo de persistencia:** Implementar en Python (`poc_slm/feedback_tracker.py`) la funcion para registrar eventos de feedback en formato JSON Lines (`.jsonl`).
5. **Documentacion tecnica:** Crear `docs/especificaciones/feedback-loop.md` explicando como los datos recopilados serviran para retroalimentar el fine-tuning del modelo.

### Criterios de Aceptacion
- [ ] `docs/especificaciones/feedback.schema.json` formalizado y validado.
- [ ] Formulas matematicas de los KPIs de acierto y descache documentadas.
- [ ] Script `poc_slm/feedback_tracker.py` registra correctamente eventos de feedback simulados.
- [ ] Documento explicativo `docs/especificaciones/feedback-loop.md` completado.

### Entregables
Documento `docs/especificaciones/feedback-loop.md` y script `poc_slm/feedback_tracker.py`.

---

## E2-12 - Demo local Entrega 2 y cierre

- **Labels:** `entrega-2`, `slm`, `feedback`, `equipo`
- **Prioridad:** P2 (Media)
- **Dueno:** Equipo completo (Persona 1, Persona 2, Persona 3)
- **Revisor:** Docente del proyecto
- **Depende de:** E2-02, E2-09, E2-10, E2-11
- **Desbloquea:** Evaluacion y aprobacion de Entrega 2
- **Estado:** ⏳ Pendiente

### Contexto
Demostrar el flujo integral de la Entrega 2 de extremo a extremo en entorno local, evidenciando como el perfil psicopedagogico conduce a una seleccion adaptativa de recursos con justificacion formativa y registro de feedback.

### Pasos Detallados de Ejecucion
1. **Preparacion de la demostracion:** Configurar un entorno limpio con Ollama corriendo en local.
2. **Ejecucion del flujo completo:**
   - Entrada: Cargar perfil de estudiante en JSON.
   - Recursos: Cargar semana 1 de la materia piloto (Recursos A, B, C).
   - Motor: Ejecutar `prompt_builder.py` con el SLM local.
   - Salida: Visualizar en consola y Markdown la recomendacion, justificacion y descarte.
   - Feedback: Registrar una evaluacion simulada con `feedback_tracker.py`.
3. **Registro en bitacora:** Documentar en `experimentos/bitacora.md` la fecha, hardware de prueba, latencia total, tokens generados y velocidad (tokens/s).
4. **Limites y trabajo futuro:** Redactar en el reporte de cierre los limites del prototipo y los requerimientos especificos de hardware (servidor con GPU) que facilitara el docente para las siguientes fases.
5. **Checklist final:** Verificar que todos los criterios de aceptacion de `docs/entregas/entrega-2-personalizacion/README.md` esten cumplidos.

### Criterios de Aceptacion
- [ ] Flujo completo e2e demostrable en vivo sin conexion a internet durante la inferencia.
- [ ] Bitacora en `experimentos/bitacora.md` actualizada con evidencia verificable.
- [ ] Limites declarados con honestidad tecnica y requerimientos para el docente listos.
- [ ] Cierre formal del milestone Entrega 2 con todos sus issues terminados o justificados.

### Entregables
`experimentos/bitacora.md` actualizado, reporte de cierre en `docs/entregas/entrega-2-personalizacion/README.md` y material de presentacion de la demo.
