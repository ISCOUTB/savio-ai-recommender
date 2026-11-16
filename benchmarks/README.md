# benchmarks - mediciones reales de SLMs en local

Este directorio integra las mediciones del Sprint 4 en dos equipos del proyecto: un portatil AMD Ryzen con GPU NVIDIA dedicada y un portatil Intel Core i5 sin GPU dedicada. **Solo datos medidos por el equipo**; ninguna cifra se copia de fuentes externas.

- Documento del sprint: [docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md](../docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md)
- Reporte AMD/NVIDIA: [equipos/amd-ryzen-5-5600h-rtx-3050.md](equipos/amd-ryzen-5-5600h-rtx-3050.md)
- Reporte Intel sin GPU dedicada: [equipos/intel-i5-1235u-iris-xe.md](equipos/intel-i5-1235u-iris-xe.md)
- Datos y salidas: [resultados/](resultados/README.md)

---

## Metodologia comun

Ambas mediciones usan la carga de trabajo real de la PoC: system prompt [`prompts/system_guardrails.md`](../prompts/system_guardrails.md) + escenario `A_nota_baja` (Arboles AVL, nota 2.0/5, estilo visual) con refuerzo.

- Salida objetivo: `num_predict = 300` tokens, `temperature = 0.7`.
- Semillas fijas por corrida para poder comparar.
- RAM: pico RSS de procesos de Ollama medido con `psutil`.
- VRAM: solo en el equipo con NVIDIA, con `nvidia-smi`; en Intel se reporta N/D por no tener GPU dedicada.
- Velocidad: tokens/s de generacion reportados por Ollama.
- Latencia: tiempo de pared de la peticion completa con el modelo ya cargado.
- Calidad ES: revision tecnica preliminar del equipo; debe validarse con asesoria pedagogica en la Entrega 2.

---

## Hardware de prueba

| Equipo | CPU | RAM | GPU | Modos medidos |
|---|---|---|---|---|
| AMD/NVIDIA | Ryzen 5 5600H, 6 nucleos / 12 hilos | 16 GB | RTX 3050 Laptop, 4 GB VRAM | GPU y CPU |
| Intel | Core i5-1235U, 10 nucleos / 12 hilos | 16 GB | Iris Xe integrada, sin VRAM dedicada | Solo CPU |

> Los equipos no son identicos. La comparacion CPU-CPU sirve para estimar ordenes de magnitud, no para declarar un ganador absoluto de procesador.

---

## Comparativa CPU entre equipos

Escenario comun: `A_nota_baja` + refuerzo, 300 tokens objetivo.

| Modelo | Ryzen 5 5600H CPU | Intel i5-1235U CPU | RAM pico aprox. | Lectura para la PoC |
|---|---:|---:|---:|---|
| Qwen 2.5 1.5B | 19.3 tok/s, 18.0 s | 17.7 tok/s, 19.2 s | 1.2 GB | Mejor opcion para demo local sin GPU dedicada |
| Gemma 2 2B | 12.6 tok/s, 26.1 s | 11.3 tok/s, 28.5 s | 2.3 GB | Intermedio; menor sintesis y mas RAM |
| Qwen 2.5 3B | 11.6 tok/s, 22.8 s | 9.68 tok/s, 26.8 s | 2.2 GB | Mejor calidad, pero lento si solo hay CPU |

Prueba de estabilidad Intel para Qwen 2.5 3B, 5 corridas CPU: promedio **9.41 tok/s**, **26.46 s**, RAM pico **2.19 GB**. Ver [reporte Intel](equipos/intel-i5-1235u-iris-xe.md).

---

## Efecto de GPU dedicada en el equipo AMD/NVIDIA

En el equipo Ryzen + RTX 3050, el mismo modelo seleccionado por calidad sale del rango lento de CPU:

| Modelo | Tokens/s CPU | Tokens/s GPU | Aceleracion |
|---|---:|---:|---:|
| Qwen 2.5 1.5B | 19.3 | 69.4 | x3.6 |
| Gemma 2 2B | 12.6 | 45.9 | x3.7 |
| Qwen 2.5 3B | 11.6 | 44.2 | x3.8 |

Con RTX 3050, Qwen 2.5 3B queda cerca de **7.7 s por recomendacion completa** y usa alrededor de **2.2 GB de VRAM**.

---

## Calidad y guardrails

Lectura consolidada de ambos reportes:

- **Qwen 2.5 1.5B:** fluido y suficiente para demo local; en el reporte AMD mostro problemas para cerrar la estructura completa en 300 tokens, mientras que en el reporte Intel, con refuerzo, se califico como usable para demostracion.
- **Gemma 2 2B:** respeta mejor la forma, pero aparecieron riesgos de URLs o datos inventados en la revision AMD; requiere mas control anti-alucinacion.
- **Qwen 2.5 3B:** mejor lectura del contexto, tono y cumplimiento de guardrails; el costo es velocidad cuando no hay GPU dedicada.

---

## Decision reconciliada

1. **Demo local en laptop sin GPU dedicada:** **Qwen 2.5 1.5B**. Responde en torno a 18-20 s por recomendacion con RAM cercana a 1.2 GB. Es la opcion mas segura para mostrar la PoC en equipos estandar.
2. **Objetivo institucional Savio:** **Qwen 2.5 3B**. Tiene la mejor calidad y cumplimiento de guardrails, pero en CPU tarda **22.8-26.8 s** por recomendacion. Para uso real con concurrencia se justifica servidor con GPU NVIDIA.
3. **Gemma 2 2B** queda como comparativo, no como seleccionado de Entrega 1, por riesgo de alucinaciones y mayor RAM sin mejor calidad.

> Riesgo pendiente: validar licencia de Qwen 2.5 3B antes de despliegue institucional. Si no aplica, mantener Qwen 2.5 1.5B como modelo de respaldo.

---

## Reproducir

```bash
pip install -r benchmarks/requirements.txt
python benchmarks/benchmark.py --dry-run          # ver equipo y rutas sin medir
python benchmarks/benchmark.py
python benchmarks/benchmark.py --modos cpu
python benchmarks/benchmark.py --modos cpu --repeticiones 5 --modelos qwen2.5:3b
python benchmarks/benchmark.py --equipo amd-ryzen-5-5600h-rtx-3050
```

Cada corrida escribe directamente en la carpeta de su equipo:
`benchmarks/resultados/<equipo>/resultados.json` y `benchmarks/resultados/<equipo>/salidas/`.
El equipo se deduce de la CPU medida comparandola con `benchmarks/equipos/*.md`; si
la maquina es nueva, se registra primero en `benchmarks/equipos/` y luego se pasa
`--equipo <nombre>`. Si no se puede deducir, el script no mide y pide `--equipo`,
para no dejar archivos sueltos en la raiz de `resultados/`.

## Evaluacion psicometrica E3-09 en CPU

Estas herramientas de Entrega 3 usan el corpus sintetico y los
[baremos del proyecto](../docs/especificaciones/baremos-psicometricos.md).
Su protocolo es distinto al benchmark de Entrega 1 descrito arriba.

| Archivo | Funcion |
|---|---|
| [evaluar_e3.py](evaluar_e3.py) | Compara base, ajustado y referencia del corpus; registra respuestas, latencia, tokens/s, RAM RSS y VRAM del modelo |
| [rubrica_e3.py](rubrica_e3.py) | Cuenta citas de los 37 campos y evalua afirmaciones explicitas de bandas y polos |
| [citas_json_e3.py](citas_json_e3.py) | Amplia la auditoria a JSON, variantes CHASIDE y direcciones explicitas; conserva la respuesta original |
| [test_rubrica_e3.py](test_rubrica_e3.py) | Comprueba omisiones, citas contradictorias, negaciones y limites de las metricas sin inferencia |
| [reauditar_e3.py](reauditar_e3.py) | Deriva una auditoria ampliada desde respuestas ya medidas y crea archivos nuevos |
| [reportar_e3.py](reportar_e3.py) | Genera el informe de la corrida local y su fila de bitacora desde el resumen ampliado |

El evaluador selecciona los 28 registros donde `int(sha256(id), 16) % 5 == 0`.
Fija `num_gpu=0`, temperatura 0, semilla 42, contexto 4096 y limite 1200 tokens.
La RAM se mide con `psutil`; la VRAM atribuida al modelo se consulta en Ollama.
El muestreo y el protocolo quedan guardados con cada corrida.

```bash
# Pruebas y ayuda: no ejecutan inferencia
python benchmarks/test_rubrica_e3.py
python benchmarks/evaluar_e3.py --help
python benchmarks/citas_json_e3.py --help
python benchmarks/reauditar_e3.py --help
python benchmarks/reportar_e3.py --help

# Ejemplo para el equipo Intel registrado y el GGUF local de esta sesion
python benchmarks/evaluar_e3.py --modelo-ajustado savio-e3-9ed11dcc --gguf modelos/modelo-q4_k_m.gguf --salida benchmarks/resultados/intel-i5-1235u-iris-xe/e3-nueva-corrida/evaluacion
```

El nombre del modelo debe corresponder al hash del GGUF. La carpeta de salida
debe ser nueva y pertenecer al equipo medido. `--reanudar` exige el mismo
protocolo y conserva los casos existentes. Una corrida completa se conserva;
para medir de nuevo se elige otra carpeta. El evaluador admite solo datos sinteticos.

La rubrica es parcial: lo no reconocido queda `sin_evaluar`. Se reportan por
separado cobertura, omisiones y consistencia de los items evaluables. La revision
integral de la prosa y la meta de fidelidad interpretativa siguen pendientes.
El aviso agregado por el backend se distingue del aviso generado por el modelo.
El auditor de citas devuelve codigo 1 si detecta hallazgos; conserva la salida
leida y no invoca Ollama. Estos controles no cierran automaticamente los issues.

La reauditoria y el informe trabajan sobre archivos existentes. El informe
incluye referencias historicas de esta sesion; antes de usarlo para otra
corrida, revisa ese contexto y la procedencia del artefacto. Los archivos
derivados se crean una sola vez para preservar la evidencia anterior.

Los hashes se calculan sobre bytes. Git puede convertir LF a CRLF al copiar
el corpus, conservando sus registros pero cambiando su SHA-256. Para reanudar
o reauditar una corrida se requieren los mismos bytes usados al medir. Si el
verificador informa que el corpus cambio, compara los archivos y sus saltos
de linea; conserva los hashes originales del protocolo y del manifiesto.
