# Lineamientos de consentimiento, anonimizacion y manejo de datos psicometricos (E3-03)

**Estado:** Completado en lineamientos y controles; la aplicacion al corpus es gate de E3-06 y la integracion en el backend es gate de E3-07.
**Issue:** [#38](https://github.com/ISCOUTB/savio-ai-recommender/issues/38) / E3-03
**Sprint:** Sprint 1
**Referencia principal:** formulacion del proyecto PerfilIA v6 (corte del 27 de octubre de 2026), secciones 6, 11, 19, 21 y 25.

---

## 1. Alcance y advertencia

Este documento fija las reglas tecnicas y operativas para tratar los resultados de CHASIDE, Felder-Silverman y el test de personalidad durante la Entrega 3. Aplica al corpus de entrenamiento, a los perfiles de los tres integrantes, a las llamadas a los LLMs maestros, a los datasets y modelos publicados en Hugging Face y a las salidas del backend.

No es un dictamen legal ni reemplaza la revision de la oficina juridica o de proteccion de datos de la UTB. La formulacion v6 deja pendiente esa validacion (seccion 25). Mientras no exista, se aplican las reglas de este documento y la regla de minimizacion: **si un dato no es necesario para la interpretacion, no se recoge, no se guarda y no se envia**.

Tampoco reemplaza el consentimiento informado de cada titular ni las politicas institucionales. La ejecucion local reduce la exposicion, pero no garantiza por si sola el cumplimiento de la Ley 1581 de 2012.

---

## 2. Principios

1. **Minimizacion:** solo puntajes brutos y metadatos tecnicos; nunca respuestas individuales, nombres, correos o codigos en el corpus.
2. **Finalidad:** los datos se usan para construir y validar el perfil integrado de apoyo a la orientacion inicial, no para diagnosticos ni decisiones automaticas.
3. **Consentimiento:** los tres integrantes firman antes de procesar sus puntajes reales.
4. **Seguridad:** los datos reales viven solo en local, en rutas ignoradas por Git.
5. **No discriminacion:** el sistema no etiqueta al estudiante, no usa el tipo MBTI de 4 letras y no emite juicios patologizantes.
6. **Trazabilidad:** cada corpus y cada salida se pueden auditar por hash, version del validador y registro de ejecucion.
7. **Transparencia:** toda salida declara que fue generada con IA y que requiere revision profesional.

---

## 3. Definiciones

- **Dato personal:** informacion que identifica o permite identificar a una persona (nombre, correo, documento, codigo estudiantil, usuario de Moodle, IP).
- **Dato sensible:** dato cuya divulgacion puede afectar la intimidad o generar discriminacion. Los resultados de personalidad y orientacion pueden caer en esta categoria segun su contenido y la Ley 1581 de 2012.
- **Seudonimo:** identificador que reemplaza el nombre, por ejemplo `persona-1` o `SINT-001`. No es anonimizacion absoluta: sigue siendo un dato personal mientras exista una tabla que permita asociarlo.
- **Perfil sintetico:** vector de puntajes construido con los rangos de cada instrumento, sin corresponder a una persona real. Es el unico insumo que puede salir a la nube.
- **Anonimizacion:** proceso que busca que el dato no permita identificar a la persona. Con vectores de puntajes psicometricos combinados no se puede garantizar anonimato absoluto, porque una combinacion puede ser unica.
- **Seudonimizacion:** reemplazo de identificadores directos, manteniendo la posibilidad de reidentificar con informacion adicional. Es lo que se aplica a los tres perfiles reales, que permanecen en local.
- **Ground truth:** interpretacion integrada de referencia generada con un LLM maestro a partir de un perfil sintetico y de las fichas con fuente.
- **LLM maestro:** modelo grande de frontera usado solo en laboratorio (Claude o ChatGPT) para producir las interpretaciones de referencia. No recibe datos reales.

---

## 4. Inventario y flujo de datos

Las rutas `datos/` y `salidas/` son convenciones de la Entrega 3; se crean cuando E3-04 y E3-06 las necesiten. La regla se aplica desde ahora.

| Dato | Origen | Almacenamiento | Git | Nube | Retencion |
|---|---|---|---|---|---|
| Respuestas individuales de los tests | Moodle local en Docker | Base de datos local de Moodle | No | No | Hasta extraer los puntajes y cerrar la validacion |
| Perfil real con puntajes brutos | Extraccion local de Moodle | `perfiles/reales/<seudonimo>.json` | No (ignorado) | No | Hasta el cierre de E3 o el retiro del consentimiento |
| Consentimiento firmado | Cada integrante | `perfiles/reales/consentimientos/` | No (ignorado) | No | Mientras dure el proyecto y la finalidad |
| Perfil sintetico | Generacion con los rangos de cada instrumento | `perfiles/` o `datos/sinteticos/` | Si | Si, solo el vector | Permanente |
| Corpus ground truth | LLM maestro con perfiles sinteticos | `datos/corpus/` | Solo despues del validador | Si, solo el JSONL validado | Permanente |
| Fichas interpretativas | Literatura y documentacion de los instrumentos | `docs/especificaciones/` o `datos/fichas/` | Si | Si | Permanente |
| Salidas del backend con datos reales | Motor de inferencia | `salidas/reales/` | No (ignorado) | No | Hasta la revision profesional y el borrado |
| Logs de ejecucion | Backend | `logs/` local | No | No | Rotacion corta, sin PII |
| Modelo GGUF ajustado | Entrenamiento en la nube con corpus sintetico | Repositorio de artefactos o Hugging Face Hub | Si | Si | Permanente |
| Notebook de ajuste | Colab o Hugging Face | Repositorio, sin salidas con datos | Si, sin outputs | Si | Permanente |

Regla de oro del flujo: **Moodle local -> perfil real local -> validacion local**. El unico camino hacia la nube es **perfil sintetico -> validador -> corpus JSONL -> Hugging Face**.

La formulacion v6 en PDF no se versiona porque incluye nombres y codigos de los integrantes; se conserva en local. Si el equipo necesita una copia publica, se genera una version sanitizada sin esos datos.

---

## 5. Reglas no negociables

- **R1. Solo tres integrantes.** En Proyecto de Ingenieria I no se procesan datos de estudiantes distintos de los tres integrantes del equipo, conforme a la seccion 6 de la formulacion v6.
- **R2. Consentimiento previo.** Antes de procesar los puntajes reales, cada integrante firma el consentimiento del Anexo A. Sin firma no se ejecuta la extraccion ni la validacion con su perfil.
- **R3. Reales solo en local.** Los perfiles reales, las respuestas de Moodle y las salidas con datos reales no se envian a Claude, ChatGPT, Hugging Face, Colab ni ningun servicio externo.
- **R4. Git solo con datos sinteticos.** Al repositorio solo entran perfiles sinteticos, corpus sinteticos, fichas, codigo y documentacion. `perfiles/reales/`, `datos/reales/` y `salidas/reales/` estan en `.gitignore`.
- **R5. Corpus con IDs sinteticos.** Cada registro del corpus usa `id` con el patron `SINT-###` y `origen: "sintetico"`. No se aceptan usuarios de Moodle, nombres, correos, documentos ni codigos estudiantiles.
- **R6. LLM maestro solo con sinteticos.** El prompt del modelo grande incluye el vector de puntajes, las fichas y la instruccion; nunca incluye respuestas individuales ni perfiles reales.
- **R7. Guardrail no clinico.** Toda salida del backend lleva el aviso canonico de la seccion 8, no usa el tipo MBTI de 4 letras como etiqueta y no emite diagnosticos, tratamientos ni juicios patologizantes.
- **R8. Logs sin PII.** El registro de ejecucion guarda modelo, version de fichas, latencia, tokens y resultado de validacion; no guarda nombre, correo, codigo ni respuestas.
- **R9. Terminos de uso del LLM maestro.** Antes de E3-08 se revisan los terminos del proveedor para entrenar con sus salidas (riesgo R09 de la formulacion v6). Si no lo permiten, se genera la referencia con Qwen 2.5 7B (Apache 2.0) usando solo datos sinteticos.
- **R10. Retencion y borrado.** Al cierre de E3 o al retirar el consentimiento se elimina el perfil real y sus derivados locales. El corpus sintetico y el modelo no contienen datos reales y pueden conservarse.
- **R11. Agregacion fisica controlada.** Si una corrida necesita los tres perfiles juntos, se copian por USB a un solo equipo designado, dentro de `perfiles/reales/`; al terminar la corrida se borran conforme a R10 y se deja constancia en la bitacora sin datos personales. Queda prohibido usar Drive, OneDrive, correo, WhatsApp, repositorio privado o contenedor cifrado en Git sin autorizacion escrita del docente. Detalle en [procedimiento-consentimientos.md](procedimiento-consentimientos.md).

---

## 6. Consentimiento informado

### 6.1 Contenido minimo

El consentimiento debe explicar, en lenguaje claro:

1. Quien es el responsable del tratamiento y como contactarlo.
2. Que datos se recogen: puntajes brutos de CHASIDE, Felder-Silverman y personalidad, mas el seudonimo.
3. Para que se usan: construir un perfil integrado de apoyo a la orientacion inicial y validar el prototipo academico.
4. Que el sistema no emite diagnosticos y que la decision final es del profesional.
5. Donde se procesan: solo en local; no se envian a modelos grandes ni a la nube.
6. Que no se publican en el repositorio ni en Hugging Face.
7. Los riesgos y las medidas: acceso limitado, rutas ignoradas, borrado al cierre.
8. Los derechos del titular: conocer, actualizar, rectificar, suprimir y retirar el consentimiento.
9. El procedimiento de retiro y el efecto: se borra el perfil real y sus derivados; el corpus sintetico no se afecta.
10. La vigencia y la fecha de la firma.

### 6.2 Custodia

- La copia firmada se guarda en `perfiles/reales/consentimientos/`, fuera de Git.
- Procedimiento paso a paso y copia imprimible: [procedimiento-consentimientos.md](procedimiento-consentimientos.md).
- La prueba publica de que el perfil se extrajo es una fila en `experimentos/bitacora.md` generada con `docs/especificaciones/evidencia-perfil.py`; contiene el resultado del validador y el SHA-256, nunca los puntajes.
- El equipo no incluye nombres, documentos ni firmas en documentos del repositorio.
- El docente o la instancia institucional que corresponda puede solicitar la copia para revision.

### 6.3 Retiro

Si un integrante retira el consentimiento:

1. Se elimina su perfil real de `perfiles/reales/`.
2. Se eliminan las salidas locales generadas con ese perfil en `salidas/reales/`.
3. Se deja constancia en `experimentos/bitacora.md` sin datos personales.
4. No se reentrena ni se vuelve a usar ese perfil. El corpus sintetico no se modifica porque no deriva de personas reales.

---

## 7. Protocolo de anonimizacion y seudonimizacion antes de Hugging Face

Se ejecuta antes de subir cualquier dataset al Hub o a un notebook en la nube. Si el corpus no existe, el validador devuelve codigo 2 y el corpus **no se considera verificado**.

1. **Inventario:** identificar el archivo JSONL, su origen y la persona responsable. Si el archivo contiene datos reales, se detiene el proceso.
2. **Filtro de origen:** cada registro debe tener `origen: "sintetico"`. Un registro `real` se rechaza.
3. **Identificador:** reemplazar cualquier identificador por `SINT-###`. No se aceptan `persona-1`, usuarios de Moodle, correos ni codigos.
4. **Allowlist:** dejar solo `id`, `origen`, `chaside`, `ils`, `personalidad` y, si aplica, `instruction`, `input`, `output`. El perfil bruto puede estar en la raiz o dentro de `input` (objeto o texto JSON). Cualquier otra clave se rechaza; en particular `nombre`, `correo`, `codigo`, `documento`, `estudiante_id`, `usuario`, `telefono`, `direccion` y `fecha_nacimiento`.
5. **Rangos e invariantes:** validar CHASIDE (`0-10`, `0-4`, `0-14`, `total = interes + aptitud`), ILS (cada par suma 11) y personalidad (`0-9` por polo), segun el Anexo A de la formulacion v6.
6. **Escaneo de PII:** buscar correos, telefonos, `@usuario`, codigos `T########`, numeros largos y nombres de una lista sensible local. La lista de nombres no se versiona; se pasa por `--lista-sensible` desde una ruta ignorada.
7. **Validacion automatica:** ejecutar el validador y guardar el manifiesto con el hash SHA-256 del archivo validado.
8. **Revision por par:** una persona genera el corpus y otra revisa el resultado y el manifiesto. La revision se registra en `experimentos/bitacora.md`.
9. **Subida controlada:** subir solo el JSONL validado y su dataset card. Nunca subir exports de Moodle, perfiles reales, capturas con nombres ni notebooks con salidas que contengan datos.

Comando de referencia:

```bash
python docs/especificaciones/validar-corpus-anonimizado.py \
    --entrada datos/corpus/corpus.jsonl \
    --manifiesto datos/corpus/manifiesto.json \
    --lista-sensible perfiles/reales/lista-sensible.txt
```

El validador esta en [validar-corpus-anonimizado.py](../../especificaciones/validar-corpus-anonimizado.py) y sus pruebas en [test_validar_corpus_anonimizado.py](../../especificaciones/test_validar_corpus_anonimizado.py).

Si cambia el corpus, se repiten los pasos 1 a 9 y se actualiza el hash. Un manifiesto viejo no certifica un archivo nuevo.

---

## 8. Guardrail no clinico

### 8.1 Texto canonico

```text
Este perfil es un apoyo para el diagnostico inicial y fue generado con asistencia de IA. No reemplaza al profesional ni constituye un diagnostico psicologico.
```

### 8.2 Donde debe aparecer

1. Al final de la salida Markdown que ve el profesional.
2. En el campo `aviso_etico` del JSON de salida.
3. En el prompt del sistema de la Entrega 3, como regla explicita.
4. En el validador posterior a la inferencia, que rechaza la salida si falta.

### 8.3 Prohibiciones de redaccion

- No usar el tipo MBTI de 4 letras como etiqueta del estudiante.
- No escribir "diagnostico definitivo", "diagnostico clinico", "el estudiante padece", "trastorno de", "patologia", "medicacion" ni "tratamiento psicologico".
- No presentar los estilos de aprendizaje como fundamento pedagogico ni como diagnostico; son preferencias de presentacion declaradas.
- No emitir recomendaciones clinicas, decisiones automaticas ni juicios de valor sobre la persona.

### 8.4 Implementacion

El texto y las comprobaciones viven en [guardrail_etico.py](../../../poc_slm/guardrail_etico.py). E3-07 debe importar `AVISO_NO_CLINICO`, `agregar_aviso` y `validar_salida_etica`; E3-09 verifica que el 100 % de las salidas cumpla. Las pruebas estan en [test_guardrail_etico.py](../../../poc_slm/test_guardrail_etico.py).

Este modulo no modifica `poc_slm/recommender.py` ni `prompts/system_guardrails.md`: la demo de Entrega 1 conserva su comportamiento y el guardrail se aplica al backend de la Entrega 3.

---

## 9. LLMs maestros y Hugging Face

1. **Solo perfiles sinteticos.** El prompt del modelo grande lleva el vector de puntajes, las fichas y la instruccion. No lleva respuestas individuales, nombres, correos ni codigos.
2. **Revision de terminos.** Antes de E3-08 se documenta si el proveedor permite usar sus salidas para ajustar otro modelo. Si no lo permite, se activa el plan B de la formulacion v6: Qwen 2.5 7B con datos sinteticos.
3. **Dataset card.** Debe declarar que el corpus es sintetico, incluir el hash del manifiesto y no contener datos personales.
4. **Notebooks.** Se versionan sin outputs. Si un output local muestra un perfil real, se borra antes de guardar y no se sube.
5. **Trazabilidad.** Se registra modelo, version, fecha, instruccion usada y hash del corpus. Sin esos datos, el corpus no se puede auditar.

---

## 10. Retencion, borrado e incidentes

### 10.1 Retencion

- Perfiles reales: hasta el cierre de la Entrega 3 o hasta el retiro del consentimiento.
- Salidas con datos reales: hasta que el profesional termine la revision; luego se eliminan.
- Corpus sintetico, fichas y modelo: se conservan como evidencia academica.
- Logs: rotacion corta y sin PII.

### 10.2 Borrado

El borrado de datos reales se hace en local, se verifica que la ruta ignorada quede vacia y se deja constancia en la bitacora sin reproducir el dato. No basta con borrar el archivo del disco si existe una copia en la papelera, en un notebook o en un correo.

### 10.3 Incidentes

Si se detecta un dato real en Git, en Hugging Face o en una salida compartida:

1. Detener la publicacion o el entrenamiento.
2. Informar al docente y al responsable del repositorio.
3. Retirar el dato del archivo y, si ya se versiono, evaluar la reescritura del historial con aprobacion del equipo.
4. Rotar credenciales si el incidente las expuso.
5. Documentar causa, alcance y accion correctiva en la bitacora, sin repetir el dato.

---

## 11. Checklist de verificacion

| Control | Comando | Resultado esperado |
|---|---|---|
| Perfiles reales ignorados | `git check-ignore -v perfiles/reales/persona-1.json` | Muestra la regla de `.gitignore` |
| Evidencia de extraccion sin publicar puntajes | `python docs/especificaciones/evidencia-perfil.py --perfil perfiles/reales/persona-1-bruto.json` | Imprime la fila de bitacora con `RESULTADO: OK` y SHA-256; rechaza perfiles no ignorados |
| PDF de formulacion ignorado | `git check-ignore -v Formulacion_Proyecto_PerfilIA_v6.pdf` | Muestra la regla de `.gitignore` |
| Nada real en el indice de Git | `git ls-files` | No aparecen `perfiles/reales/`, `datos/reales/`, `salidas/reales/` ni el PDF |
| Documentacion navegable | `python docs/validar-docs.py` | `RESULTADO: OK` sin errores |
| Pruebas del validador | `python docs/especificaciones/test_validar_corpus_anonimizado.py` | `RESULTADO: OK (15/15 chequeos)` |
| Pruebas del guardrail | `python poc_slm/test_guardrail_etico.py` | `RESULTADO: OK (10/10 chequeos)` |
| Perfil real rechazado | `python docs/especificaciones/validar-corpus-anonimizado.py --entrada perfiles/reales/persona-1.json` | Codigo 1 y hallazgos por `origen` y `estudiante_id` |
| Corpus sintetico aceptado | Ejecutar el validador sobre `datos/corpus/corpus.jsonl` | Codigo 0, sin PII y con manifiesto SHA-256 |

El ultimo control solo puede pasar cuando E3-06 produzca el corpus. Hasta entonces, E3-03 deja el protocolo y el validador probados con fixtures sinteticos, no una certificacion ficticia del corpus.

---

## 12. Pendientes y responsables

| Pendiente | Responsable | Cuando |
|---|---|---|
| Firmar el consentimiento de los tres integrantes ([procedimiento](procedimiento-consentimientos.md)) | Persona 1, Persona 2 y Persona 3 | Antes de E3-05 |
| Validar el tratamiento de datos con la oficina juridica o de proteccion de datos de la UTB | Docente / area legal | Pendiente de la formulacion v6, seccion 25 |
| Revisar y aprobar este lineamiento | Docente del proyecto | Revision del issue #38 |
| Revisar los terminos de uso del LLM maestro | Persona 3 | Antes de E3-08 |
| Aplicar el validador al corpus y guardar el manifiesto | Persona 3, con revision por par | E3-06, antes de Hugging Face |
| Integrar el guardrail en el backend | Persona 1 | E3-07 |
| Verificar el 100 % de adherencia al aviso | Persona 2 | E3-09 |

---

## Anexo A. Texto base de consentimiento informado

Plantilla sujeta a revision juridica. No usar datos reales en este documento; las copias firmadas van en `perfiles/reales/consentimientos/`.

```text
CONSENTIMIENTO INFORMADO PARA EL TRATAMIENTO DE RESULTADOS PSICOMETRICOS
Proyecto PerfilIA - Proyecto de Ingenieria I - UTB

Yo, [NOMBRE COMPLETO], identificado con [DOCUMENTO], autorizo de forma
voluntaria al equipo del proyecto PerfilIA a tratar mis puntajes brutos de
CHASIDE, Felder-Silverman y el test de personalidad, junto con un seudonimo,
para la siguiente finalidad:

1. Construir un perfil integrado de apoyo a la orientacion inicial.
2. Validar el prototipo academico de inferencia con un modelo de lenguaje
   pequeno ejecutado en CPU.

Entiendo que:

- El sistema no emite diagnosticos ni reemplaza la valoracion de un profesional.
- Mis datos reales se procesan solo en local y no se envian a Claude, ChatGPT,
  Hugging Face, Colab ni ningun servicio externo.
- Mis datos no se publican en el repositorio ni en Hugging Face.
- El corpus de entrenamiento se construye con perfiles sinteticos, no con mi
  perfil real.
- Puedo conocer, actualizar, rectificar, suprimir y retirar este consentimiento
  en cualquier momento.
- Si retiro el consentimiento, mi perfil real y sus derivados locales se
  eliminan; el corpus sintetico no se afecta.
- La informacion se conserva hasta el cierre de la Entrega 3 o hasta el retiro
  del consentimiento.

Contacto del responsable: [CORREO O CANAL DEL EQUIPO]
Fecha: [FECHA]
Firma: ______________________________
```
