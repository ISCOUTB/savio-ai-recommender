# Resultados de benchmarks

Estructura de datos y evidencias del Sprint 4, separada por equipo para evitar mezclar mediciones de hardware distinto.

```text
resultados/
  amd-ryzen-5-5600h-rtx-3050/
    resultados.json
    salidas/
  intel-i5-1235u-iris-xe/
    resultados.json
    salidas/
```

- `amd-ryzen-5-5600h-rtx-3050/resultados.json`: salida cruda generada por `benchmarks/benchmark.py` en el equipo con RTX 3050.
- `amd-ryzen-5-5600h-rtx-3050/salidas/`: respuestas generadas en ese equipo.
- `intel-i5-1235u-iris-xe/resultados.json`: resumen documental de las corridas reportadas en el equipo Intel sin GPU dedicada.
- `intel-i5-1235u-iris-xe/salidas/`: espacio reservado para salidas crudas del equipo Intel si se versionan despues.

Regla de orden: no mezclar corridas de equipos distintos en el mismo `resultados.json`. [`benchmarks/benchmark.py`](../benchmark.py) resuelve la carpeta del equipo a partir de la CPU medida y escribe ahi; si la maquina es nueva, se registra en [`benchmarks/equipos/`](../equipos/) y se ejecuta con `--equipo <nombre>`.

## Ensayos exploratorios de refuerzo E3

Pruebas sobre el fixture sintetico dominante con el mismo GGUF y CPU. Cada
carpeta conserva protocolo, prompts, respuestas originales y reporte, incluidos
los intentos rechazados. Son variantes sucesivas de un caso conocido; la
fidelidad global y la sintesis siguen pendientes de validacion.

- [Primer refuerzo](intel-i5-1235u-iris-xe/e3-refuerzo-20261116T205155Z/informe.md): respuestas rechazadas por los controles parciales.
- [Segundo refuerzo](intel-i5-1235u-iris-xe/e3-refuerzo-20261116T205627Z/informe.md): la respuesta reforzada tambien fue rechazada.
- [Formato acotado](intel-i5-1235u-iris-xe/e3-refuerzo-20261116T211402Z/informe.md): paso el control disponible entonces; la revision manual encontro eco de instrucciones en la sintesis.
- [Control contra el eco](intel-i5-1235u-iris-xe/e3-refuerzo-20261116T211835Z/informe.md): sintesis rechazada por introducir nuevas clasificaciones.

La [bitacora](../../experimentos/bitacora.md) conserva las revisiones posteriores;
los resultados historicos del validador permanecen intactos. Los prompts exactos
estan guardados y los protocolos identifican las fuentes usadas mediante hashes.
Las variantes anteriores no corresponden al codigo actual: una ejecucion nueva
del [comparador](../probar_refuerzo_e3.py) crea otra carpeta y otros resultados.

## Evaluacion completa de E3-09 en CPU

El [reporte de la corrida Intel](intel-i5-1235u-iris-xe/e3-20261116T184153Z/informe.md)
reune la comparacion del modelo base y el GGUF ajustado, los protocolos,
respuestas originales, mediciones y auditorias derivadas. Se conservan tanto
el resumen inicial como el ampliado; el reporte distingue cobertura numerica,
consistencia de los items evaluables y revision interpretativa integral pendiente.

Las salidas de los tres fixtures sinteticos estan en
[salidas/e3/ajustado](../../salidas/e3/ajustado/). Conservan la etiqueta historica
del validador original; las auditorias posteriores describen fallos de
interpretacion. Deben leerse junto con el reporte, sin convertir esa etiqueta
en aprobacion integral del contenido. La evidencia original permanece intacta.
