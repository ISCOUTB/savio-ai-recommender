# Sprint 2 — Motor de inferencia local

**Entrega:** 1 — PoC Funcional
**Estado:** ✅ Completado
**Issues:** #3
**Depende de:** Sprint 1 (Ollama instalado y modelos descargados)

---

## 🎯 Objetivo

Construir el script Python que actua como **middleware simplificado de la PoC**: recibe un evento academico simulado (JSON), ensambla el prompt con el contexto del estudiante y lo envia al SLM local via API de Ollama, imprimiendo la recomendacion generada.

> En la arquitectura final, este rol lo cumple el middleware conectado a los eventos de Moodle/Savio. En la PoC, el evento se simula con archivos JSON.

---

## 📋 Issues del sprint

### #3 — Script `recommender.py`: conexion con API de Ollama + evento simulado · `backend`

**Alcance:**
- `poc_slm/recommender.py` — script principal (CLI con `--escenario`).
- `poc_slm/eventos/bajo_desempeno.json` — evento de ejemplo:
  ```json
  {
    "estudiante": "Estudiante Demo",
    "materia": "Estructuras de Datos",
    "tema": "Arboles AVL",
    "calificacion": 2.0,
    "escala": "0-5",
    "estilo_aprendizaje": "visual"
  }
  ```
- Carga del system prompt desde `prompts/system_guardrails.md` (se poblara en Sprint 3; en Sprint 2 se usa placeholder).
- Llamada a `http://localhost:11434/api/generate` usando **solo `requests`** (sin frameworks).
- Salida formateada en consola.

**Criterio de aceptacion:**
- [x] `python poc_slm/recommender.py --escenario bajo_desempeno` ejecuta y devuelve una respuesta coherente del SLM
- [x] Sin dependencias externas ademas de `requests`
- [x] Evidencia de ejecucion registrada en este documento

---

## ✅ Criterio de cierre del sprint

- [x] Script funcional de extremo a extremo (evento JSON → Ollama → respuesta en consola)
- [x] Codigo en `poc_slm/` con README de uso actualizado

---

## 📝 Registro de ejecucion

| Accion | Evidencia | Responsable | Estado |
|---|---|---|---|
| Entorno Python (`.venv`, `requirements.txt`, `.gitignore`) | Python 3.12.10 + `requests==2.34.2` | Persona 1 | ✅ |
| Script `recommender.py` + evento `bajo_desempeno.json` | Commit `5a0740c` en `dev/persona-1` | Persona 1 | ✅ |
| Placeholder `prompts/system_guardrails.md` | Contenido definitivo en Sprint 3 (#4) | Persona 1 | ✅ |
| Ejecucion end-to-end con `qwen2.5:1.5b` | Salida de consola (abajo) | Persona 1 | ✅ |
| Manejo de error (escenario inexistente) | Mensaje claro + lista de escenarios, exit 1 | Persona 1 | ✅ |

### Evidencia de ejecucion (2026-10-04)

Entorno: Windows, Ollama 0.35.1, inferencia 100% local (sin APIs externas).

```text
$ python poc_slm/recommender.py --escenario bajo_desempeno
======================================================================
SAVIO — Recomendador academico (PoC local con SLM)
======================================================================
Estudiante : Estudiante Demo
Materia    : Estructuras de Datos
Tema       : Arboles AVL
Calificacion: 2.0 / escala 0-5
Estilo     : visual
----------------------------------------------------------------------
### Diagnostico
...
### Recomendaciones
...
   - **Aprendizaje Visual:** ...
     - **Graficar arboles AVL:** Realizar actividades de dibujo o ilustracion
       para entender como se estructuran los arboles AVL.
...
### Siguiente paso
...
----------------------------------------------------------------------
Modelo     : qwen2.5:1.5b
Latencia   : 42.5 s (total)
Generacion : 668 tokens a ~19.6 tokens/s
======================================================================

$ python poc_slm/recommender.py --escenario no_existe
[ERROR] Escenario 'no_existe' no existe: ...\poc_slm\eventos\no_existe.json
Escenarios disponibles: bajo_desempeno
```

| Metrica | Valor |
|---|---|
| Latencia total (incluye carga del modelo) | 42.5 s |
| Tokens generados | 668 |
| Velocidad de generacion | ~19.6 tokens/s |

### Hallazgos para el Sprint 3

- ✅ El modelo respeta la estructura Markdown (Diagnostico → Recomendaciones → Siguiente paso), el tono empatico y adapta la recomendacion al estilo **visual**.
- ⚠️ Con el system prompt placeholder, el modelo **alucina datos**: califica 2.0/5 como "rendimiento mediano", afirma fortalezas no presentes en el evento e inventa un libro de texto. Insumo para el diseno definitivo de guardrails (#4).
- ⚠️ La salida es extensa (668 tokens). Para el benchmark (#8) se recomienda fijar la longitud de salida (~300 tokens).
