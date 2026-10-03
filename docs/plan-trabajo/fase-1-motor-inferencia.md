# Fase 1 — Motor de inferencia local

**Estado:** ⏳ Pendiente
**Issues asociados:** #3
**Milestone:** M1 — PoC Funcional
**Depende de:** Fase 0 (Ollama instalado y modelos descargados)

---

## 🎯 Objetivo

Construir el script Python que actúa como **middleware simplificado de la PoC**: recibe un evento académico simulado (JSON), ensambla el prompt con contexto del estudiante y lo envía al SLM local vía API de Ollama, imprimiendo la recomendación generada.

> En la arquitectura final, este rol lo cumple el middleware conectado a los eventos de Moodle/Savio. En la PoC, el evento se simula con archivos JSON.

---

## 📦 Issues de esta fase

### #3 — Script `recommender.py`: conexión con API de Ollama + evento simulado · `backend`

**Alcance:**
- `poc_slm/recommender.py` — script principal (CLI con `--escenario`).
- `poc_slm/eventos/bajo_desempeno.json` — evento de ejemplo:
  ```json
  {
    "estudiante": "Camila R.",
    "materia": "Estructuras de Datos",
    "tema": "Árboles AVL",
    "calificacion": 2.0,
    "escala": "0-5",
    "estilo_aprendizaje": "visual"
  }
  ```
- Carga del system prompt desde `prompts/system_guardrails.md` (se poblará en Fase 2; en Fase 1 se usa placeholder).
- Llamada a `http://localhost:11434/api/generate` usando **solo `requests`** (sin frameworks).
- Salida formateada en consola.

**Criterio de aceptación:**
- [ ] `python poc_slm/recommender.py --escenario bajo_desempeno` ejecuta y devuelve una respuesta coherente del SLM
- [ ] Sin dependencias externas además de `requests`
- [ ] Evidencia de ejecución registrada en el log de esta fase

---

## ✅ Criterio de cierre de la fase

- [ ] Script funcional de extremo a extremo (evento JSON → Ollama → respuesta en consola)
- [ ] Código en `poc_slm/` con README de uso actualizado

---

## 📝 Registro de ejecución

| Fecha | Acción | Evidencia | Responsable |
|---|---|---|---|
| _pendiente_ | — | — | — |
