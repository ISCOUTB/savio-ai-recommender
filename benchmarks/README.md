# benchmarks — Mediciones reales de SLMs en local

Resultados comparativos de consumo de memoria y velocidad de inferencia, medidos en el hardware del equipo. **Solo datos propios** — ninguna cifra copiada de fuentes externas.

> 📌 Documentación del sprint: [docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md](../docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md)

## Metodología (Sprint 4 — Entrega 1)

Medición automatizada con [`benchmark.py`](benchmark.py) contra la API local de Ollama (fecha de medición: 2026-10-07).

- **Carga de trabajo real:** el mismo prompt del recomendador de la PoC — system prompt [`prompts/system_guardrails.md`](../prompts/system_guardrails.md) + escenario `A_nota_baja` (Árboles AVL, nota 2.0/5, estilo visual) con `--refuerzo`.
- **Salida fija:** `num_predict = 300` tokens, `temperature = 0.7`, semilla fija por corrida (1, 2, 3).
- **Repeticiones:** 1 carga en frío (reportada aparte) + **3 corridas medidas** por modelo y modo; las tablas muestran el promedio.
- **Dos modos de ejecución:** GPU (todas las capas en VRAM) y **solo CPU** (`num_gpu = 0`), para dimensionar el servidor con y sin aceleración.
- **RAM:** pico de RSS de los procesos de Ollama (`ollama.exe` + runner `llama-server.exe`) muestreado cada 0.2 s con `psutil` durante la inferencia.
- **VRAM:** pico de memoria usada en la GPU (`nvidia-smi`) menos la línea base previa a cargar el modelo.
- **Velocidad:** tokens/segundo de generación = `eval_count / eval_duration` reportados por Ollama (equivalente a `ollama run --verbose`).
- **Tiempo de respuesta:** tiempo de pared de la petición completa (prompt + generación) con el modelo ya cargado.
- **Calidad en español:** rúbrica 1–5 aplicada sobre las 6 salidas de cada modelo (3 GPU + 3 CPU), guardadas en [`resultados/salidas/`](resultados/salidas/).

Datos crudos por corrida: [`resultados/resultados.json`](resultados/resultados.json).

## Hardware de prueba

| Componente | Especificación |
|---|---|
| CPU | AMD Ryzen 5 5600H (6 núcleos / 12 hilos) |
| RAM | 16 GB (15.3 GB utilizables) |
| GPU | NVIDIA GeForce RTX 3050 Laptop — 4 GB VRAM (driver 610.74) |
| SO | Windows 11 Home (build 26200) |
| Runtime | Ollama 0.40.1 |

> ⚠️ Equipo portátil de uso personal: durante la medición había otras aplicaciones abiertas (navegador, Discord, Steam). No afectan la RAM medida de Ollama, pero pueden restar algo de velocidad, sobre todo en modo CPU (variación observada entre corridas: ±10 %).

## Resultados

### Modo GPU (RTX 3050, 4 GB)

| Modelo | Parámetros | Cuantización | VRAM en inferencia | RAM del proceso | Tokens/seg | Tiempo (~300 tok) | Calidad ES (1–5) |
|---|---|---|---|---|---|---|---|
| Qwen 2.5 1.5B | 1.5B | Q4_K_M | 1.2 GB | 0.6 GB | **69.4** | **6.7 s** | 2 |
| Gemma 2 2B | 2.6B | Q4_0 | 2.1 GB | 1.1 GB | 45.9 | 8.9 s | 3 |
| Qwen 2.5 3B | 3.1B | Q4_K_M | 2.2 GB | 0.7 GB | 44.2 | 7.7 s ¹ | **4** |

### Modo solo CPU (Ryzen 5 5600H)

| Modelo | Parámetros | Cuantización | RAM en inferencia | Tokens/seg | Tiempo (~300 tok) | Calidad ES (1–5) |
|---|---|---|---|---|---|---|
| Qwen 2.5 1.5B | 1.5B | Q4_K_M | **1.2 GB** | **19.3** | **18.0 s** | 2 |
| Gemma 2 2B | 2.6B | Q4_0 | 2.3 GB | 12.6 | 26.1 s | 3 |
| Qwen 2.5 3B | 3.1B | Q4_K_M | 2.2 GB | 11.6 | 22.8 s ¹ | **4** |

¹ Qwen 2.5 3B termina la recomendación antes del tope (promedio 235 tokens), por eso su tiempo es menor de lo que indicaría su velocidad.

### Aceleración GPU vs CPU

| Modelo | Tokens/seg CPU | Tokens/seg GPU | Aceleración |
|---|---|---|---|
| Qwen 2.5 1.5B | 19.3 | 69.4 | ×3.6 |
| Gemma 2 2B | 12.6 | 45.9 | ×3.7 |
| Qwen 2.5 3B | 11.6 | 44.2 | ×3.8 |

### Carga del modelo en frío

| Modelo | Tamaño cargado | Carga GPU | Carga CPU |
|---|---|---|---|
| Qwen 2.5 1.5B | 1.1 GB | 2.9 s | 2.1 s |
| Gemma 2 2B | 1.8 GB | 37.5 s ² | 2.9 s |
| Qwen 2.5 3B | 2.0 GB | 4.4 s | 3.2 s |

² Primera lectura desde disco (sin caché del SO); las demás cargas ya tenían el archivo en caché. En producción el modelo se mantiene residente (`keep_alive`), por lo que la carga solo ocurre al arrancar el servicio.

### Calidad en español — rúbrica

Criterios: **comprensión contextual** (lee bien la nota y el tema), **seguimiento de instrucciones** (4 secciones, máx. 3 pasos/recursos, sin URLs, sin inventar datos) y **tono pedagógico** (empático, adaptado al estilo visual).

| Modelo | Estructura completa en 300 tok | Violaciones de guardrails | Nota | Justificación |
|---|---|---|---|---|
| Qwen 2.5 1.5B | 0 / 6 | Sin encabezados Markdown en 2/6; describe la nota 2.0 como "dificultad media" en 1/6 | **2** | Verboso: nunca llega al cierre motivacional dentro del límite y desborda la ruta con sub-pasos. Buen español y buena lectura del tema, pero no respeta el formato. |
| Gemma 2 2B | 6 / 6 | **Inventa URLs de YouTube/ejemplo en 2/6**; inventa debilidades ("dificultad de visualización") y conceptos ("tipos de árboles AVL") | **3** | Respeta la estructura y adapta bien al estilo visual, pero viola la regla anti-alucinación (crítica para un sistema institucional) y tiene errores gramaticales ("un Árboles AVL"). |
| Qwen 2.5 3B | 5 / 6 | Ninguna; incluye 1 recurso textual en una salida visual (permitido como secundario) | **4** | Respuestas breves y completas (≈100–155 palabras), los 4 encabezados exactos, nota interpretada como baja en todos los casos, tono empático y sin URLs. |

> La calificación de calidad es una evaluación preliminar del equipo de desarrollo sobre 6 salidas por modelo; debe validarse con la asesoría pedagógica (ARCS/IMMS) en la Entrega 2.

## Conclusión y modelo seleccionado

### ✅ Modelo seleccionado: **Qwen 2.5 3B (Q4_K_M)**

1. **Mejor calidad y cumplimiento de guardrails.** Es el único modelo que produjo recomendaciones completas y sin violaciones de guardrails de forma consistente (5/6 completas, 0 URLs, nota interpretada correctamente). Qwen 2.5 1.5B no completa la estructura en 300 tokens y Gemma 2 2B inventa enlaces, lo que es inaceptable en un tutor institucional.
2. **Latencia apta para uso interactivo en GPU.** ≈44 tokens/s y **≈7.7 s por recomendación completa**. Es más lento por token que Qwen 1.5B, pero al ser más conciso el tiempo real por recomendación es comparable (7.7 s vs 6.7 s, y el 1.5B deja la respuesta incompleta).
3. **Huella de memoria pequeña.** 2.2 GB de VRAM o 2.2 GB de RAM: cabe en una GPU de 4 GB y deja margen en un servidor de 16 GB.
4. **Plan alternativo:** Qwen 2.5 1.5B queda como modelo de respaldo para hardware muy limitado (1.2 GB de RAM, 19 tok/s en CPU), aceptando respuestas menos estructuradas.

> ⚠️ **Riesgo a validar — licencia:** Qwen 2.5 3B se distribuye con la *Qwen Research License* (uso no comercial), a diferencia de Qwen 2.5 1.5B (Apache 2.0). Antes del despliegue institucional se debe validar con la UTB que el uso académico interno está cubierto; si no lo está, se adopta el modelo de respaldo.

### Implicaciones para la solicitud de infraestructura

- **La inferencia solo en CPU es funcional pero lenta:** con el modelo seleccionado, una recomendación tarda **≈23 s** en CPU frente a **≈7.7 s** en GPU. Una GPU modesta acelera la generación **×3.6–3.8** en todos los modelos medidos.
- **RAM:** el modelo usa ≈2.2 GB; el **mínimo de 16 GB** propuesto en el Sprint 6 es suficiente para el SO, Ollama y el middleware con holgura.
- **GPU:** incluso una GPU de 4 GB aloja el modelo completo. La recomendación de **8–16 GB de VRAM** se justifica por el margen para atender varias solicitudes concurrentes y para evaluar modelos de mayor tamaño en la Entrega 2 (estimación, no medida en esta PoC).
- **Límites de esta medición:** solicitudes secuenciales (sin concurrencia), un solo escenario y hardware de portátil. Se recomienda repetir el benchmark en el servidor asignado y medir concurrencia antes de producción.

## Reproducir el benchmark

```bash
# Requiere Ollama corriendo y los modelos descargados:
# ollama pull qwen2.5:1.5b && ollama pull gemma2:2b && ollama pull qwen2.5:3b
pip install -r benchmarks/requirements.txt
python benchmarks/benchmark.py                       # 3 modelos x (GPU, CPU) x 3 corridas
python benchmarks/benchmark.py --modos cpu --repeticiones 5 --modelos qwen2.5:3b
```
