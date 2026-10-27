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

## Formato del corpus

Una linea JSON por ejemplo, con la particion asignada por perfil en `perfiles/sinteticos/estratos.json` (120 train / 30 eval, sin fuga):

```json
{"id": "SINT-001", "particion": "train", "instruction": "...", "input": "{\"puntajes\": ..., \"resultados\": ...}", "output": "## Sintesis vocacional ..."}
```

Solo perfiles sinteticos: los perfiles reales del equipo no se suben a Colab ni a Hugging Face.
