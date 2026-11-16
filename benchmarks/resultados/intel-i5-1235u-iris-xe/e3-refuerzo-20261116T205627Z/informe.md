# Prueba exploratoria de refuerzo de baremos

Perfil sintetico: `ejemplo-dominante`. Modelo: `savio-e3-9ed11dcc`.
SHA-256 GGUF: `9ed11dcc6d881c579207a325bc2092dcaf9e90f7920755030481c78d5800822f`.

Mismos parametros: temperatura 0, semilla 42, num_ctx=4096, num_predict=1200, num_gpu=0.
Una respuesta por modo, sin reintentos; calentamiento y reinicio del runner antes de cada modo.
El mismo validador estricto y el mismo auditor se aplican a las dos respuestas.
La condicion sin refuerzo conserva el prompt original. La otra agrega reglas y hechos calculados por Python.
Solo se agrega el aviso y se normalizan encabezados para validar; las respuestas crudas permanecen intactas.
Es un experimento sobre un fixture conocido. Un resultado favorable no acredita la meta global del 85%.

| Medida | Sin refuerzo | Con refuerzo |
|---|---:|---:|
| Latencia (s) | 28.60 | 63.25 |
| Velocidad (tokens/s) | 18.46 | 14.33 |
| RAM pico RSS (GB decimal) | 1.244 | 1.255 |
| VRAM del modelo (bytes) | 0 | 0 |
| Citas correctas / esperadas | 25/37 | 37/37 |
| Contradicciones de baremos reconocidas por auditor | 6 | 2 |
| Errores reconocidos por validador estricto | 20 | 2 |
| Aceptacion automatica parcial | False | False |

## Hallazgos: sin-refuerzo

- "falta citar el puntaje chaside.C.interes"
- "falta citar el puntaje chaside.C.aptitud"
- "falta citar el puntaje chaside.C.total"
- "falta citar el puntaje chaside.H.interes"
- "falta citar el puntaje chaside.H.aptitud"
- "falta citar el puntaje chaside.H.total"
- "falta citar el puntaje chaside.A.interes"
- "falta citar el puntaje chaside.A.aptitud"
- "falta citar el puntaje chaside.A.total"
- "falta citar el puntaje chaside.S.interes"
- "falta citar el puntaje chaside.S.aptitud"
- "falta citar el puntaje chaside.S.total"
- "personalidad.extraversion/introversion: declara equilibrio global pero corresponde preferencia hacia introversion"
- "personalidad.sensing/intuition: declara equilibrio global pero corresponde preferencia hacia intuition"
- "personalidad.sensing/intuition: declara un empate inexistente"
- "personalidad.thinking/feeling: declara equilibrio global pero corresponde preferencia hacia thinking"
- "personalidad.thinking/feeling: declara un empate inexistente"
- "personalidad.judging/perceptive: declara equilibrio global pero corresponde preferencia hacia judging"
- "CHASIDE I: banda incorrecta; corresponde alta"
- "CHASIDE E: banda incorrecta; corresponde alta"

## Hallazgos: con-refuerzo

- "CHASIDE A: banda incorrecta; corresponde baja"
- "CHASIDE E: banda incorrecta; corresponde alta"

## Evidencia

- [Protocolo](protocolo.json)
- [Respuesta original sin refuerzo](sin-refuerzo.json)
- [Respuesta original con refuerzo](con-refuerzo.json)
- [Reglas ejecutables](../../../../poc_slm/lectura_baremos.py)
- [Baremos del proyecto](../../../../docs/especificaciones/baremos-psicometricos.md)
