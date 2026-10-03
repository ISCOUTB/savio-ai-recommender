# Sprint 2 — Motor de inferencia local

**Entrega:** 1 — PoC Funcional
**Estado:** ⏳ Pendiente
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
- [ ] `python poc_slm/recommender.py --escenario bajo_desempeno` ejecuta y devuelve una respuesta coherente del SLM
- [ ] Sin dependencias externas además de `requests`
- [ ] Evidencia de ejecución registrada en este documento

---

## ✅ Criterio de cierre del sprint

- [ ] Script funcional de extremo a extremo (evento JSON → Ollama → respuesta en consola)
- [ ] Código en `poc_slm/` con README de uso actualizado

---

## 📝 Registro de ejecución

| Acción | Evidencia | Responsable | Estado |
|---|---|---|---|
| — | — | — | ⏳ |
