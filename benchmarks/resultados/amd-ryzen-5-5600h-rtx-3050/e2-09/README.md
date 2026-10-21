# Mediciones E2-09 - Equipo AMD Ryzen 5 5600H + RTX 3050

Evidencia de la propuesta de destilacion: [`docs/investigacion/propuesta-destilacion-slm.md`](../../../../docs/investigacion/propuesta-destilacion-slm.md). Fecha: 2026-10-20, Ollama 0.40.6. **Solo datos medidos; no editar cifras a mano.**

| Archivo | Generado con | Contenido |
| :--- | :--- | :--- |
| `benchmark/resultados.json` | `python benchmarks/benchmark.py --modelos smollm2:360m qwen2.5:0.5b llama3.2:1b qwen2.5:1.5b smollm2:1.7b gemma2:2b qwen2.5:3b` | RAM, VRAM, tokens/s y latencia de los 7 candidatos en GPU y CPU (3 corridas) |
| `benchmark/salidas/` | Mismo comando | 42 respuestas del prompt de la PoC (6 por modelo) |
| `candidatos.json` | `python benchmarks/e2_09_candidatos.py --recursos <semana_1.json de E2-08>` | Metadatos, licencia, KV cache teorico y medido, y linea base A/B/C con 3 perfiles simulados x 2 semillas |

Nota: `benchmark.py` escribe en `benchmarks/resultados/`; los archivos se movieron a esta carpeta al terminar, segun la regla de separar corridas por equipo. Las velocidades de esta sesion no son comparables con las de la Entrega 1 (Ollama 0.40.1).
