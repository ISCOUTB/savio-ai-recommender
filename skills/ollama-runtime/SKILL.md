---
name: Ollama Runtime
description: Operar el runtime local de Ollama del proyecto (servir el SLM, crear un modelo desde GGUF, medir latencia y depurar localhost:11434). Usar cuando haya que ejecutar o diagnosticar inferencia local en CPU.
license: Uso interno del proyecto Savio AI Recommender
---

# Ollama Runtime

Runtime de inferencia local del subsistema Savio. Todo corre en CPU con
`http://localhost:11434`. Esta skill no cubre entrenamiento: para eso usar
`entrenamiento-qlora` y `trl-training`.

## Reglas del proyecto

1. No cambiar los topes de tokens: `poc_slm/recommender.py` usa `num_predict=600`;
   `benchmarks/benchmark.py` usa 300. Son distintos a proposito.
2. No editar `benchmarks/resultados/`, `benchmarks/equipos/` ni
   `prompts/salidas-respaldo/`: son evidencia medida.
3. Reportar solo valores medidos. Si no se ejecuto, decir que no se midio.
4. No usar APIs comerciales: la PoC es 100% local.

## Estado esperado

```bash
ollama list
curl http://localhost:11434/api/tags
```

Modelo de demo: `qwen2.5:1.5b` (~1.2 GB en RAM con Q4_K_M).
Si falta: `ollama pull qwen2.5:1.5b`.

## Ejecutar la PoC

Desde la raiz del repo:

```bash
python poc_slm/recommender.py --escenario bajo_desempeno
python poc_slm/recommender.py --escenario A_nota_baja --refuerzo --guardar salidas/x.md
```

`--escenario` toma los nombres de `poc_slm/eventos/*.json`.

## Crear un modelo desde GGUF

`Modelfile` con los valores fijados en
`docs/entregas/entrega-3-interpretacion-psicometrica/guia-entrenamiento-colab.md`:

```text
FROM ./modelo-q4_k_m.gguf
PARAMETER num_ctx 4096
PARAMETER temperature 0.2
PARAMETER repeat_penalty 1.1
```

```bash
ollama create perfil-ia-e3 -f Modelfile
ollama run perfil-ia-e3
```

## API minima

`POST /api/generate` con `stream: false`:

```json
{
  "model": "perfil-ia-e3",
  "prompt": "<prompt ensamblado>",
  "stream": false,
  "options": { "num_predict": 600, "temperature": 0.2, "num_ctx": 4096 }
}
```

Campos utiles de la respuesta: `response`, `eval_count`, `eval_duration` (ns),
`total_duration` (ns). `tokens/s = eval_count / (eval_duration / 1e9)`.

En PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:11434/api/generate `
  -ContentType 'application/json' -Body $json
```

## Medicion de latencia

Patron obligatorio (el mismo de `benchmarks/benchmark.py`):

1. `time.perf_counter()` antes y despues de la llamada.
2. Registrar modelo, escenario, tokens de salida, segundos y tokens/s.
3. Agregar la corrida a `benchmarks/resultados/<equipo>/` sin tocar las anteriores.
4. Comparar contra el tope de 60 s de OE3.

## Errores frecuentes

| Sintoma | Causa | Solucion |
|---|---|---|
| `Connection refused` en 11434 | Ollama no esta corriendo | Abrir la app o `ollama serve` |
| `model not found` | Modelo no descargado | `ollama pull <modelo>` |
| Respuesta vacia | `num_predict` muy bajo o prompt sin instruccion | Revisar el payload |
| Muy lento en el primer token | Carga en frio del modelo | Calentar con una llamada corta antes de medir |
| Se queda sin RAM | Modelo grande para el equipo | Usar 1.5B en Q4_K_M |

## Verificacion antes de afirmar que funciona

```bash
ollama list
python poc_slm/recommender.py --escenario bajo_desempeno
```

Si Ollama no esta disponible, se puede validar logica sin modelo con
`python poc_slm/test_guardrail_etico.py` y los demas `test_*.py`.
