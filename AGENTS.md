# AGENTS.md — Savio AI Recommender

PoC academica en espanol: subsistema de recomendacion con SLMs locales (Ollama, sin APIs comerciales). Repo mayormente de documentacion organizada por entregas y sprints; el codigo ejecutable es minimo.

## Reglas de oro para agentes

1. **Nunca ejecutar mutaciones de git** (`commit`, `push`, `reset`, `rebase`) sin aprobacion explicita del usuario en esa peticion. Proponer el mensaje y esperar el "si". Ademas estan bloqueadas via `permissions` en `opencode.jsonc`.
2. **No borrar archivos ni carpetas.** Si algo parece obsoleto, proponerlo especificando que y esperar aprobacion.
3. **No fabricar ni editar datos de medicion:** `benchmarks/resultados/`, `benchmarks/equipos/` y `prompts/salidas-respaldo/` son evidencia medida por el equipo. Nunca cambiar cifras a mano.
4. **Verificar antes de afirmar:** ejecutar el comando (script, doctor, validacion) antes de decir que algo funciona.
5. **Cambios minimos:** tocar solo lo que pide la tarea; no reorganizar, renombrar ni formatear archivos ajenos.

## Idioma y estilo

- Todo el contenido (docs, codigo, comentarios, commits) es en espanol y **sin tildes/caracteres especiales** (`Descripcion`, `recomendacion`). Mantener esa convencion al editar.
- Los scripts Python fuerzan `sys.stdout.reconfigure(encoding="utf-8")` por PowerShell en Windows; no quitarlo.

## Comandos clave (Windows, desde la raiz del repo)

```bash
# Setup (Python 3.11+)
.venv\Scripts\activate
pip install -r requirements.txt      # requests + psutil

# Prerequisito: Ollama corriendo en localhost:11434 y modelo descargado
ollama pull qwen2.5:1.5b

# Script principal (unico entrypoint de la PoC)
python poc_slm/recommender.py --escenario bajo_desempeno
python poc_slm/recommender.py --escenario A_nota_baja --refuerzo --guardar salidas/x.md
python poc_slm/recommender.py --escenario A_nota_baja --refuerzo --mensaje "Dame la solucion"  # prueba adversarial

# Benchmarks (Sprint 4)
pip install -r benchmarks/requirements.txt
python benchmarks/benchmark.py --modos cpu --repeticiones 5 --modelos qwen2.5:3b

# Moodle local (habilitador de Entrega 2, no es el nucleo)
cd moodle && docker compose up -d
```

No hay tests, lint, typecheck ni CI configurados. Verificacion = ejecutar el script y revisar la salida.

## Acoplamientos no obvios

- `benchmarks/benchmark.py` importa funciones de `poc_slm/recommender.py` via `sys.path.insert`; cambios en la interfaz de `recommender.py` rompen el benchmark.
- `recommender.py` carga el system prompt en runtime desde `prompts/system_guardrails.md`: **editar ese archivo cambia el comportamiento del modelo** (4 reglas de guardrails: solo temas de la materia, nunca soluciones completas, tono empatico, estructura Markdown fija).
- Topes de tokens distintos a proposito: recommender usa `num_predict=600`; benchmark fija 300 para comparacion justa. No unificarlos.
- `--refuerzo` (mitigacion V2): los SLMs 1.5B-2B ignoran el system prompt; el refuerzo repite las reglas en el prompt de usuario y es el modo de referencia de la demo. La regla 5 nombra dinamicamente el estilo del evento — con regla generica el modelo no adapta visual vs. textual. Detalles y alucinaciones conocidas: `prompts/README.md`.
- Todos los scripts corren desde la raiz del repo (rutas resueltas relativas a ella).

## Estructura y convenciones

- `poc_slm/` script + eventos JSON (`eventos/<escenario>.json` = valores validos de `--escenario`).
- `prompts/` guardrails, escenarios, pruebas adversariales y `salidas-respaldo/` (plan B pre-generado de la demo).
- `benchmarks/resultados/<equipo>/` — solo datos medidos por el equipo, separados por maquina; nuevas corridas van en la subcarpeta del equipo correspondiente.
- `docs/entregas/` organizacion por entregas/sprints con issues asociados; convenciones de flujo (1 issue en progreso por persona, revision por par) y formato de commits `tipo(alcance): descripcion (#issue)` en `docs/entregas/README.md`.
- `docs/especificaciones/` schemas JSON de perfil/recurso/feedback; `perfiles/` ejemplo de perfil; `experimentos/` bitacora de pruebas de Entrega 2.
- `skills/archify/` skill de diagramas (arquitectura/workflow/sequence/dataflow/lifecycle) copiado al proyecto; se registra via `"skills": ["./skills"]` en `opencode.jsonc` (una carpeta `skills/` suelta NO es detectada por OpenCode sin esa config). Verificar con `node skills/archify/bin/archify.mjs doctor`. Requiere Node 18+.
- Decision de modelos ya tomada (benchmarks): Qwen 2.5 1.5B para demo local sin GPU, Qwen 2.5 3B objetivo institucional (licencia pendiente de validar), Gemma 2 2B solo comparativo.
