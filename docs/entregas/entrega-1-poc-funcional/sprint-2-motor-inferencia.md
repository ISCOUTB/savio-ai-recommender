# Sprint 2 — Motor de inferencia local

**Entrega:** 1 — PoC Funcional
**Estado:** ✅ Completado
**Issues:** #3
**Depende de:** Sprint 1 (Ollama instalado y modelos descargados)

---

## 🎯 Objetivo

Construir el script Python que actúa como **middleware simplificado de la PoC**: recibe un evento académico simulado (JSON), ensambla el prompt con el contexto del estudiante y lo envía al SLM local vía API de Ollama, imprimiendo la recomendación generada.

> En la arquitectura final, este rol lo cumple el middleware conectado a los eventos de Moodle/Savio. En la PoC, el evento se simula con archivos JSON.

---

## 📋 Issues del sprint

### #3 — Script `recommender.py`: conexión con API de Ollama + evento simulado · `backend`

**Alcance:**
- `poc_slm/recommender.py` — script principal (CLI con `--escenario`).
- `poc_slm/eventos/bajo_desempeno.json` — evento de ejemplo:
  ```json
  {
    "estudiante": "Estudiante Demo",
    "materia": "Estructuras de Datos",
    "tema": "Árboles AVL",
    "calificacion": 2.0,
    "escala": "0-5",
    "estilo_aprendizaje": "visual"
  }
  ```
- Carga del system prompt desde `prompts/system_guardrails.md` (se poblará en Sprint 3; en Sprint 2 se usa placeholder).
- Llamada a `http://localhost:11434/api/generate` usando **solo `requests`** (sin frameworks).
- Salida formateada en consola.

**Criterio de aceptación:**
- [x] `python poc_slm/recommender.py --escenario bajo_desempeno` ejecuta y devuelve una respuesta coherente del SLM
- [x] Sin dependencias externas además de `requests`
- [x] Evidencia de ejecución registrada en este documento

---

## ✅ Criterio de cierre del sprint

- [x] Script funcional de extremo a extremo (evento JSON → Ollama → respuesta en consola)
- [x] Código en `poc_slm/` con README de uso actualizado

---

## 📝 Registro de ejecución

| Acción | Evidencia | Responsable | Estado |
|---|---|---|---|
| Entorno Python (`.venv`, `requirements.txt`, `.gitignore`) | Python 3.12.10 + `requests==2.34.2` | Persona 1 | ✅ |
| Script `recommender.py` + evento `bajo_desempeno.json` | Commit `5a0740c` en `dev/persona-1` | Persona 1 | ✅ |
| Placeholder `prompts/system_guardrails.md` | Contenido definitivo en Sprint 3 (#4) | Persona 1 | ✅ |
| Ejecución end-to-end con `qwen2.5:1.5b` | Salida de consola (abajo) | Persona 1 | ✅ |
| Manejo de error (escenario inexistente) | Mensaje claro + lista de escenarios, exit 1 | Persona 1 | ✅ |

### Evidencia de ejecución (2026-10-04)

Entorno: Windows, Ollama 0.35.1, inferencia 100% local (sin APIs externas).

```text
$ python poc_slm/recommender.py --escenario bajo_desempeno
======================================================================
SAVIO — Recomendador académico (PoC local con SLM)
======================================================================
Estudiante : Estudiante Demo
Materia    : Estructuras de Datos
Tema       : Árboles AVL
Calificación: 2.0 / escala 0-5
Estilo     : visual
----------------------------------------------------------------------
### Diagnóstico
...
### Recomendaciones
...
   - **Aprendizaje Visual:** ...
     - **Graficar árboles AVL:** Realizar actividades de dibujo o ilustración
       para entender cómo se estructuran los árboles AVL.
...
### Siguiente paso
...
----------------------------------------------------------------------
Modelo     : qwen2.5:1.5b
Latencia   : 42.5 s (total)
Generación : 668 tokens a ~19.6 tokens/s
======================================================================

$ python poc_slm/recommender.py --escenario no_existe
[ERROR] Escenario 'no_existe' no existe: ...\poc_slm\eventos\no_existe.json
Escenarios disponibles: bajo_desempeno
```

| Métrica | Valor |
|---|---|
| Latencia total (incluye carga del modelo) | 42.5 s |
| Tokens generados | 668 |
| Velocidad de generación | ~19.6 tokens/s |

### Hallazgos para el Sprint 3

- ✅ El modelo respeta la estructura Markdown (Diagnóstico → Recomendaciones → Siguiente paso), el tono empático y adapta la recomendación al estilo **visual**.
- ⚠️ Con el system prompt placeholder, el modelo **alucina datos**: califica 2.0/5 como "rendimiento mediano", afirma fortalezas no presentes en el evento e inventa un libro de texto. Insumo para el diseño definitivo de guardrails (#4).
- ⚠️ La salida es extensa (668 tokens). Para el benchmark (#8) se recomienda fijar la longitud de salida (~300 tokens).
