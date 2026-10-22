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
