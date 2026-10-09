# Equipo Intel Core i5-1235U, Iris Xe integrada

Mediciones reales de SLMs en hardware estandar sin GPU dedicada. **Solo datos propios reales**; ninguna cifra se estima ni se copia de fuentes externas.

- Integracion principal: [benchmarks/README.md](../README.md)
- Sprint: [docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md](../../docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md)
- Resumen de datos: [resultados/intel-i5-1235u-iris-xe/resultados.json](../resultados/intel-i5-1235u-iris-xe/resultados.json)

## Hardware

| Componente | Especificacion |
|---|---|
| CPU | 12th Gen Intel Core i5-1235U, 10 nucleos: 2 P-cores + 8 E-cores, 12 hilos |
| RAM | 16 GB, 15.7 GB utilizables |
| GPU | N/D; graficos integrados Intel Iris Xe; inferencia 100% en CPU |
| SO | Windows 11 Home/Pro, build 10.0.26200 |
| Runtime | Ollama 0.40.1 |

## Metodologia

Script: [`benchmarks/benchmark.py`](../benchmark.py), contra API local de Ollama.

- Carga real: [`prompts/system_guardrails.md`](../../prompts/system_guardrails.md) + escenario `A_nota_baja` con refuerzo.
- Salida: `num_predict = 300`, `temperature = 0.7`.
- Semillas fijas por corrida para comparacion justa.
- Modo de ejecucion: CPU con `num_gpu = 0`.
- RAM: pico RSS de procesos de Ollama muestreado con `psutil`.
- Velocidad y tiempo: tokens/s de Ollama y latencia total de pared.

## Bateria 1: comparativa general en CPU

3 modelos x 3 corridas en CPU.

| Modelo | Cuantizacion | RAM pico | Tokens/s promedio | Latencia media | Calidad ES |
|---|---|---:|---:|---:|---:|
| Qwen 2.5 1.5B | Q4_K_M | 1.24 GB | 17.74 | 19.18 s | 4.0/5 |
| Gemma 2 2B | Q4_K_M | 2.33 GB | 11.34 | 28.47 s | 3.5/5 |
| Qwen 2.5 3B | Q4_K_M | 2.19 GB | 9.68 | 26.76 s | 4.5/5 |

Nota: Qwen 2.5 3B completa recomendaciones mas concisas y suele cerrar antes del tope de 300 tokens, con promedio cercano a 236 tokens.

### Detalle de corridas

Qwen 2.5 1.5B CPU:

| Corrida | Tokens | Tokens/s | Tiempo | RAM pico |
|---:|---:|---:|---:|---:|
| 1 | 300 | 17.93 | 19.01 s | 1241 MB |
| 2 | 300 | 17.67 | 19.22 s | 1242 MB |
| 3 | 300 | 17.63 | 19.32 s | 1243 MB |

Gemma 2 2B CPU:

| Corrida | Tokens | Tokens/s | Tiempo | RAM pico |
|---:|---:|---:|---:|---:|
| 1 | 300 | 11.44 | 28.63 s | 2326 MB |
| 2 | 300 | 11.19 | 29.28 s | 2327 MB |
| 3 | 285 | 11.39 | 27.51 s | 2331 MB |

Qwen 2.5 3B CPU:

| Corrida | Tokens | Tokens/s | Tiempo | RAM pico |
|---:|---:|---:|---:|---:|
| 1 | 181 | 9.85 | 20.66 s | 2195 MB |
| 2 | 300 | 9.57 | 33.68 s | 2195 MB |
| 3 | 227 | 9.62 | 25.93 s | 2195 MB |

## Bateria 2: estabilidad de Qwen 2.5 3B

5 corridas consecutivas en CPU.

| Corrida | Tokens | Tokens/s | Tiempo | RAM pico |
|---:|---:|---:|---:|---:|
| 1 | 181 | 9.46 | 21.49 s | 2197 MB |
| 2 | 300 | 8.95 | 35.92 s | 2195 MB |
| 3 | 227 | 9.39 | 26.51 s | 2194 MB |
| 4 | 236 | 9.55 | 27.05 s | 2191 MB |
| 5 | 185 | 9.72 | 21.34 s | 2191 MB |
| Promedio | 225.8 | 9.41 | 26.46 s | 2.19 GB |

## Evaluacion cualitativa

- **Qwen 2.5 1.5B, 4.0/5:** buena fluidez, tono empatico y cumplimiento del esquema con refuerzo. Puede llenar los 300 tokens si no se acota con firmeza.
- **Gemma 2 2B, 3.5/5:** buen vocabulario pedagogico, pero mayor RAM y menor sintesis.
- **Qwen 2.5 3B, 4.5/5:** mejor razonamiento pedagogico; interpreta la nota baja con precision y evita URLs o libros falsos. La velocidad en CPU es el limite para multi-usuario.

Sujeto a validacion y rubrica formal con asesoria pedagogica.

## Conclusion del equipo

- **Para demo local sin GPU dedicada:** Qwen 2.5 1.5B, por 17.74 tok/s, menos de 20 s y 1.24 GB de RAM.
- **Para objetivo institucional:** Qwen 2.5 3B sigue siendo el modelo deseado por calidad, pero las 5 corridas muestran cerca de 26.5 s en CPU. Eso justifica pedir servidor con GPU NVIDIA para la plataforma.

## Reproducir

```powershell
python benchmarks/benchmark.py --modos cpu
python benchmarks/benchmark.py --modos cpu --repeticiones 5 --modelos qwen2.5:3b
```
