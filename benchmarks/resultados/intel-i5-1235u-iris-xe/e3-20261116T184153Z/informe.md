# Evaluacion E3-09 del GGUF local en CPU

Fecha UTC del resumen: 2026-11-16T20:03:02Z
Equipo: 12th Gen Intel(R) Core(TM) i5-1235U; Ollama 0.40.16.
Modelo ajustado: `savio-e3-9ed11dcc`.
SHA-256 GGUF: `9ed11dcc6d881c579207a325bc2092dcaf9e90f7920755030481c78d5800822f`.
SHA-256 corpus: `c74e2e6252e06047bdc8067d7b784c182ca7f396657c2947bc2777e9f9aaae1c`.

## Protocolo y alcance

28 registros sinteticos seleccionados con sha256(id) % 5 == 0; 122 quedan fuera de esta evaluacion.
Una generacion por modelo y registro, sin reintentos. ChatML identico para ambos modelos, temperatura 0,
semilla 42, num_predict=1200, num_ctx=4096 y num_gpu=0. Calentamiento separado de las latencias.
RSS de servidor y runner de Ollama muestreado cada 0.25 s; size_vram consultado cada 1 s y al terminar.
GB decimal = bytes / 1e9. La confirmacion de VRAM pertenece al modelo segun Ollama; no se inventa una medicion NVIDIA.
Los benchmarks historicos de Entrega 1 y las tres salidas base anteriores no se mezclan con esta comparacion.

La evaluacion se completo en varias sesiones con calentamientos separados. Las pausas y la carga del equipo limitan una comparacion causal de velocidad.
Se conservaron los casos previos al reanudar; no se eligieron ni repitieron respuestas segun su resultado.

## Comparacion con la referencia Teacher

| Medida | Base | Ajustado | Teacher |
|---|---:|---:|---:|
| Fidelidad numerica sobre los 37 campos esperados (%) | 39.00 | 100.00 | 100.00 |
| Precision de las citas etiquetadas reconocidas (%) | 97.58 | 100.00 | 100.00 |
| Cobertura de campos numericos (%) | 39.96 | 100.00 | 100.00 |
| Estructura de cuatro secciones (%) | 96.43 | 100.00 | 100.00 |
| Guardrail automatico sobre texto crudo (%) | 0.00 | 50.00 | 100.00 |
| Guardrail automatico despues del backend (%) | 100.00 | 100.00 | 100.00 |
| Bandas/polos: consistencia en items evaluables (%) | N/D | 85.58 | 100.00 |
| Bandas/polos: cobertura de la rubrica parcial (%) | 0.00 | 75.95 | 56.19 |
| Bandas/polos: items acreditados sobre 420 posibles (%) | 0.00 | 65.00 | 56.19 |
| Perfiles con inversion de polo reconocida en prosa | 0 | 2 | 0 |
| Perfiles con contradiccion de baremos reconocida | 0 | 26 | 0 |
| Perfiles con escalas o rangos prohibidos reconocidos | 0 | 0 | 0 |

La precision sin citas es N/D. Las omisiones reducen cobertura y fidelidad sobre esperados.
El parser reconoce citas key=N, key: N, key (N), listas CHASIDE por area con ':' o '=' y JSON incrustado. No adivina numeros sin etiqueta.
La auditoria ampliada incorpora JSON, letras de areas CHASIDE en mayusculas y negaciones por igual para base, ajustado y Teacher. El resumen y las auditorias iniciales siguen intactos.
Cada campo vale una vez; una segunda cita contradictoria lo convierte en error. Las respuestas crudas se conservan.
La rubrica de bandas/polos solo puntua afirmaciones explicitas reconocidas. Ausencia de hallazgos no equivale a correccion.
Los items sin evaluar son desconocidos, no fallos del modelo. Las coberturas distintas impiden comparar estos porcentajes parciales como fidelidad integral.
La fidelidad interpretativa integral, las correlaciones y el cumplimiento etico exhaustivo siguen pendientes de revision humana.
Por esa razon no se acredita la meta de fidelidad integral >=85% a partir de estos indicadores parciales.
El conjunto se uso como evaluacion durante entrenamiento: es validacion, no una prueba independiente.

## Rendimiento observado

| Medida | Base | Ajustado |
|---|---:|---:|
| Latencia media (s) | 44.73 | 31.68 |
| Latencia mediana (s) | 35.44 | 31.04 |
| Latencia maxima (s) | 80.34 | 40.54 |
| Generacion media (tokens/s) | 18.08 | 17.78 |
| Longitud media de respuesta (tokens) | 702.82 | 456.68 |
| RAM pico RSS (GB decimal) | 2.05 | 1.66 |
| RAM pico RSS (GiB) | 1.91 | 1.55 |
| Perfiles con latencia <=60 s | 20/28 | 28/28 |
| CPU verificada en todos los casos | True | True |
| Muestreo RAM completo sin errores | True | True |
| Respuestas cortadas por limite de tokens | 7 | 0 |

Las longitudes reales de salida difieren y afectan la latencia. La tasa de tokens/s mide solo generacion; la latencia incluye toda la solicitud.

## Hallazgos y limites para el cierre

En el ajustado hay 46 items con contradiccion explicita reconocida y 101 sin evaluar.
La referencia Teacher tiene 0 contradicciones reconocidas y 184 items sin evaluar con la misma rubrica.
El detector encontro 0 respuestas ajustadas que afirman revision profesional sin evidencia de esa revision.
El guardrail de produccion comprueba un conjunto limitado de frases y puede aceptar errores semanticos.
La auditoria posterior detecta fallos; no modifica ni corrige las respuestas medidas.
El hash local difiere del artefacto 2531a770 citado en la bitacora anterior; las mediciones de aquel artefacto no se atribuyen a este modelo.
Identidad Colab/local confirmada con el SHA-256 aportado por el usuario desde /content/entrenamiento-final/modelo-q4_k_m.gguf. El usuario aporto logs de 150 registros, split 122/28, 48 pasos y 3 epocas. Esa evidencia aportada se distingue de las mediciones CPU realizadas localmente.
La configuracion mini de procedencia-local.json es una observacion historica del archivo local; no acredita por si sola el entrenamiento del GGUF.
Las firmas del corpus y la fidelidad integral no se suplen con metricas automaticas. Los issues remotos permanecen sin cambios.

## Evidencia reproducible

- [Protocolo y hardware](evaluacion/protocolo.json)
- [Resumen ampliado calculado](evaluacion/resumen-ampliado.json)
- [Auditoria ampliada por caso](evaluacion/auditoria-ampliada.json)
- [Resumen inicial conservado](evaluacion/resumen.json)
- [Gate de privacidad](evaluacion/gate-privacidad.json)
- [Prueba de CPU del bloque 1](bloque1-cpu.json)
- [Configuracion local observada y limite de procedencia](procedencia-local.json)
- [Auditoria de los tres fixtures](bloque2-auditoria.json)
- [Auditoria ampliada de los tres fixtures](bloque2-auditoria-ampliada.json)
- [Auditoria de la referencia](evaluacion/teacher-auditoria.json)
- Las subcarpetas `evaluacion/base/` y `evaluacion/ajustado/` contienen respuesta cruda, tiempos, muestreo y auditoria por caso.
- Codigo: [evaluador](../../../evaluar_e3.py), [rubrica](../../../rubrica_e3.py), [citas JSON](../../../citas_json_e3.py), [reauditoria](../../../reauditar_e3.py) y [pruebas](../../../test_rubrica_e3.py).
