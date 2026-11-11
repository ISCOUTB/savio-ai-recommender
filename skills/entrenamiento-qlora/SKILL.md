---
name: Entrenamiento QLoRA
description: Ajustar el SLM del proyecto con QLoRA y TRL en una GPU T4, usando los hiperparametros ya medidos para este corpus. Usar al escribir o depurar el notebook de E3-08, estimar VRAM o convertir el adaptador a GGUF.
license: Uso interno del proyecto Savio AI Recommender
---

# Entrenamiento QLoRA (E3-08)

SFT con LoRA/QLoRA sobre un modelo ya entrenado. No es preentrenamiento desde cero.
Detalle de la API de TRL: skill `trl-training`. Este documento fija las decisiones
del proyecto y los valores que no se inventan.

## Hardware y entorno

| Decision | Valor | Motivo |
|---|---|---|
| GPU | T4 16 GB (Colab) | Capa gratuita; sin VRAM local |
| Precision | `float16` | La T4 no soporta `bfloat16` |
| Dependencias | `requirements-entrenamiento.txt` | Se instalan en Colab |
| PyTorch | No declarar en requirements | Colab trae la build CUDA; reemplazarla rompe el entorno |

Modelo base: `Qwen2.5-1.5B` (demo) o `0.5B` (pruebas rapidas). El 3B queda para
la version institucional y depende de validar licencia.

## Cuantizacion y LoRA

| Parametro | Valor |
|---|---|
| `load_in_4bit` | `True` |
| `bnb_4bit_quant_type` | `nf4` |
| `bnb_4bit_use_double_quant` | `True` |
| `bnb_4bit_compute_dtype` | `float16` |
| LoRA `r` / `alpha` | 16 / 32 |
| `lora_dropout` | 0.05 |
| `target_modules` | `q, k, v, o, gate, up, down` |
| Entrenables | 1 a 2 por ciento del total |

## Hiperparametros

| Parametro | Valor |
|---|---|
| `num_train_epochs` | 3 (150 registros); 1 con `ejemplo_mini.jsonl` |
| `learning_rate` | `2e-4` |
| `per_device_train_batch_size` | 1 |
| `gradient_accumulation_steps` | 8 |
| `max_length` | 2048 |
| `warmup_ratio` | 0.1 |
| `lr_scheduler_type` | `cosine` |
| `fp16` | `True` |
| `gradient_checkpointing` | `True` |
| `optim` | `paged_adamw_8bit` |
| `seed` | 42 |

## Formato y mascara de loss

Cada registro es una conversacion de 3 turnos: `system` (contrato de 4 secciones y
prohibicion de diagnosticos), `user` (puntajes brutos) y `assistant` (`output`).
Se aplica `tokenizer.apply_chat_template`; no se inventa formato.

**La mascara es obligatoria:** `-100` en los tokens de `system` y `user`. Solo se
calcula perdida sobre el informe. Sin mascara el modelo aprende a repetir los
puntajes y la calidad cae.

`tokenizer.pad_token` es `None` en Qwen: asignar `eos_token` antes de entrenar.

## Senales de que va bien

| Senal | Esperado | Si no |
|---|---|---|
| `train_loss` inicial | 1.8 a 2.6 | Revisar labels en `-100` |
| `train_loss` final | 0.5 a 0.9 | Subir `lr` a `3e-4` o revisar corpus |
| `eval_loss` | Baja y pegada al train | Sobreajuste: bajar a 2 epocas |
| Duracion por epoca | 3 a 8 min | Mas de 15 min: modelo muy grande para T4 |
| `CUDA out of memory` | No aparece | `max_length` 1536 y batch 1 |

## Merge y GGUF

```bash
# En Colab, tras entrenar
merged = model.merge_and_unload()
merged.save_pretrained("merged")

python convert_hf_to_gguf.py merged --outtype f16
cmake -B build && cmake --build build -j
./build/bin/llama-quantize modelo-f16.gguf modelo-q4_k_m.gguf Q4_K_M
```

| Artefacto | Tamano aproximado |
|---|---|
| `merged/` safetensors | ~3 GB (1.5B en f16) |
| `modelo-q4_k_m.gguf` | ~1.1 GB |
| Plan B `q8_0` | ~1.7 GB |

Si Colab se queda sin RAM al compilar, usar `--outtype q8_0` y aceptar el plan B.
Importar a Ollama con la skill `ollama-runtime`.

## Evidencia de cierre

- Notebook ejecutado con hiperparametros y versiones de librerias anotadas.
- Loss final, tamano del GGUF y latencia en `experimentos/bitacora.md`.
- GGUF respaldado con model card: corpus sintetico + hash del manifiesto.
- Dataset card con el mismo hash y sin datos personales.
- Una salida de ejemplo con las 4 secciones y el aviso no clinico.

## Errores conocidos

| Sintoma | Causa | Solucion |
|---|---|---|
| El modelo repite el prompt | Falta la mascara de loss | Marcar `-100` en system y user |
| `pad_token` None | Qwen no lo define | `tokenizer.pad_token = tokenizer.eos_token` |
| Colab se desconecta | Limite de 90 min | Checkpoints en Drive |
| Salidas sin aviso | Corpus sin aviso o pocas epocas | Validar corpus; 4 epocas |
| Perdida estancada | Corpus repetitivo o lr baja | Revisar corpus; `3e-4` |
