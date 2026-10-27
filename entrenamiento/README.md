# Entrenamiento del SLM (E3-08, #44)

Ajuste de Qwen 2.5 0.5B con QLoRA en Google Colab y exportacion a GGUF Q4_K_M para ejecutar **solo en CPU** con Ollama.

| Archivo | Contenido |
| :--- | :--- |
| `ajuste_qlora_gguf.ipynb` | Notebook para Colab (GPU T4): carga del corpus, ajuste QLoRA, fusion del adaptador, GGUF F16 y Q4_K_M, `Modelfile` con `num_gpu 0` y publicacion privada en Hugging Face |
| `construir_notebook.py` | Genera el notebook desde codigo revisable en git (`python entrenamiento/construir_notebook.py`) |
| `datos_prueba.jsonl` | 12 ejemplos de la linea base sin IA para verificar el flujo. **No son ground truth** |
| `probar_notebook_local.py` | Prueba de punta a punta en CPU: ejecuta las celdas del notebook en modo prueba, convierte a GGUF, cuantiza con `ollama create -q q4_K_M` y verifica 0 MB de VRAM |

## Uso en Colab

1. Abrir `ajuste_qlora_gguf.ipynb` en Colab y elegir GPU T4.
2. Para la corrida real: `MODO_PRUEBA = False` y subir el corpus de E3-06 (`instruction`, `input`, `output`, `particion`).
3. Ejecutar todas las celdas. Los artefactos quedan en `artefactos/` y se descargan como `.zip`.

## Prueba de punta a punta (2026-10-27)

`probar_notebook_local.py` ejecuto las celdas del notebook en CPU (AMD Ryzen 5 5600H, 16 GB) con los 12 ejemplos de prueba y reemplazo los pasos de Colab por sus equivalentes locales. Versiones: torch 2.14.1 (CPU), transformers 5.21.0, peft 0.21.2, trl 1.16.0, llama.cpp b11606, Ollama 0.40.7.

| Paso | Resultado |
| :--- | :--- |
| Entrenamiento LoRA (4 pasos, sin 4 bits) | 160 s; perdida 2.46 -> 1.80; perdida en eval 1.84 |
| Fusion del adaptador (fp16) y GGUF F16 | 948 MB |
| Cuantizacion Q4_K_M (llama-quantize) | 379 MB; 144 de 290 tensores usan q5_0/q8_0 porque la dimension 896 de Qwen 0.5B no es multiplo de 256 (igual que el `qwen2.5:0.5b` oficial) |
| Importacion en Ollama con el `Modelfile` del notebook y ejecucion con `num_gpu 0` | 0 MB de VRAM; 60.9 tokens/s; 13.1 s para 150 tokens |

Con 4 pasos el modelo ya imita la estructura de secciones pero inventa puntajes: es esperable en una prueba de flujo y confirma la necesidad del validador de salidas (R01). **No es una medicion de calidad.**

Errores encontrados y corregidos antes de usar Colab: bf16 activado por defecto en TRL (la T4 no lo soporta), `torch_dtype` obsoleto, `apply_chat_template` devuelve un diccionario en transformers 5, memoria insuficiente sin gradient checkpointing y modelo fusionado en fp32 (ahora fp16). Ollama 0.40.7 no cuantiza a formatos K-quant, por eso se usa `llama-quantize`.

## Formato del corpus

Una linea JSON por ejemplo, con la particion asignada por perfil en `perfiles/sinteticos/estratos.json` (120 train / 30 eval, sin fuga):

```json
{"id": "SINT-001", "particion": "train", "instruction": "...", "input": "{\"puntajes\": ..., \"resultados\": ...}", "output": "## Sintesis vocacional ..."}
```

Solo perfiles sinteticos: los perfiles reales del equipo no se suben a Colab ni a Hugging Face.
