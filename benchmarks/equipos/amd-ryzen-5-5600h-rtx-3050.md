# Equipo AMD Ryzen 5 5600H + RTX 3050

Mediciones reales de SLMs para la PoC Savio. **Solo datos propios medidos**; ninguna cifra se copia de fuentes externas.

- Integracion principal: [benchmarks/README.md](../README.md)
- Sprint: [docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md](../../docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md)
- Datos crudos: [resultados/amd-ryzen-5-5600h-rtx-3050/resultados.json](../resultados/amd-ryzen-5-5600h-rtx-3050/resultados.json)

## Hardware

| Componente | Especificacion |
|---|---|
| CPU | AMD Ryzen 5 5600H, 6 nucleos / 12 hilos |
| RAM | 16 GB, 15.3 GB utilizables |
| GPU | NVIDIA GeForce RTX 3050 Laptop, 4 GB VRAM, driver 610.74 |
| SO | Windows 11 Home, build 26200 |
| Runtime | Ollama 0.40.1 |

Portatil de uso personal con aplicaciones abiertas durante la medicion; la RAM de Ollama se midio por procesos, pero la velocidad puede variar alrededor de ±10% en CPU.

## Metodologia

Script: [`benchmarks/benchmark.py`](../benchmark.py), contra API local de Ollama, fecha 2026-10-07.

- Carga real: [`prompts/system_guardrails.md`](../../prompts/system_guardrails.md) + escenario `A_nota_baja` con refuerzo.
- Salida: `num_predict = 300`, `temperature = 0.7`, semillas 1, 2 y 3.
- Repeticiones: 1 carga en frio reportada aparte + 3 corridas medidas por modelo y modo.
- Modos: GPU completa y solo CPU con `num_gpu = 0`.
- RAM: pico RSS de `ollama.exe` y `llama-server.exe` con muestreo cada 0.2 s.
- VRAM: pico `nvidia-smi` menos linea base previa.
- Calidad ES: rubrica 1 a 5 sobre 6 salidas por modelo, 3 GPU + 3 CPU.

## Resultados GPU, RTX 3050 4 GB

| Modelo | Parametros | Cuantizacion | VRAM inferencia | RAM proceso | Tokens/s | Tiempo ~300 tok | Calidad ES |
|---|---|---|---|---:|---:|---:|---:|
| Qwen 2.5 1.5B | 1.5B | Q4_K_M | 1.2 GB | 0.6 GB | 69.4 | 6.7 s | 2 |
| Gemma 2 2B | 2.6B | Q4_0 | 2.1 GB | 1.1 GB | 45.9 | 8.9 s | 3 |
| Qwen 2.5 3B | 3.1B | Q4_K_M | 2.2 GB | 0.7 GB | 44.2 | 7.7 s | 4 |

Nota: Qwen 2.5 3B suele terminar antes del tope de 300 tokens; su tiempo total es menor que el que sugiere solo su velocidad por token.

## Resultados solo CPU

| Modelo | Parametros | Cuantizacion | RAM inferencia | Tokens/s | Tiempo ~300 tok | Calidad ES |
|---|---|---|---|---:|---:|---:|
| Qwen 2.5 1.5B | 1.5B | Q4_K_M | 1.2 GB | 19.3 | 18.0 s | 2 |
| Gemma 2 2B | 2.6B | Q4_0 | 2.3 GB | 12.6 | 26.1 s | 3 |
| Qwen 2.5 3B | 3.1B | Q4_K_M | 2.2 GB | 11.6 | 22.8 s | 4 |

## Aceleracion GPU vs CPU

| Modelo | Tokens/s CPU | Tokens/s GPU | Aceleracion |
|---|---:|---:|---:|
| Qwen 2.5 1.5B | 19.3 | 69.4 | x3.6 |
| Gemma 2 2B | 12.6 | 45.9 | x3.7 |
| Qwen 2.5 3B | 11.6 | 44.2 | x3.8 |

## Carga en frio

| Modelo | Tamano cargado | Carga GPU | Carga CPU |
|---|---:|---:|---:|
| Qwen 2.5 1.5B | 1.1 GB | 2.9 s | 2.1 s |
| Gemma 2 2B | 1.8 GB | 37.5 s | 2.9 s |
| Qwen 2.5 3B | 2.0 GB | 4.4 s | 3.2 s |

La primera lectura de Gemma 2 2B en GPU salio desde disco sin cache del SO; en operacion normal el modelo queda residente con `keep_alive`.

## Calidad en espanol

Criterios: comprension contextual, seguimiento de instrucciones, tono pedagogico y cumplimiento de guardrails.

| Modelo | Estructura completa | Violaciones de guardrails | Nota | Justificacion |
|---|---|---|---:|---|
| Qwen 2.5 1.5B | 0/6 | Sin encabezados Markdown en 2/6; nota 2.0 descrita como dificultad media en 1/6 | 2 | Buen espanol, pero no respeta el formato dentro del limite |
| Gemma 2 2B | 6/6 | Inventa URLs de YouTube/ejemplo en 2/6; inventa debilidades y conceptos | 3 | Respeta estructura, pero viola anti-alucinacion |
| Qwen 2.5 3B | 5/6 | Ninguna; 1 recurso textual en salida visual permitido como secundario | 4 | Completo, breve, sin URLs y con nota interpretada bien |

## Conclusion del equipo

- **Seleccion por calidad y guardrails:** Qwen 2.5 3B.
- **Uso interactivo:** viable con GPU, cerca de 7.7 s por recomendacion.
- **Solo CPU:** funcional pero lento para Qwen 2.5 3B, cerca de 22.8 s en este equipo.
- Riesgo a validar antes de produccion: licencia de Qwen 2.5 3B.
