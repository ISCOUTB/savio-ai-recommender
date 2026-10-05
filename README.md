# Savio AI Recommender

> **Subsistema de recomendación de contenido académico adaptativo basado en Inteligencia Artificial para Savio (Moodle) — Universidad Tecnológica de Bolívar.**

[![Estado](https://img.shields.io/badge/estado-Entrega%201%20en%20curso-yellow)]()
[![Modelo](https://img.shields.io/badge/SLM-Qwen%202.5%201.5B-blue)]()
[![Runtime](https://img.shields.io/badge/runtime-Ollama-lightgrey)]()

---

## 📌 Descripción

Este repositorio contiene el desarrollo del **subsistema de recomendación adaptativa** para la plataforma **Savio** (EVA institucional basado en Moodle). El sistema utiliza **Small Language Models (SLMs) de pesos abiertos, ejecutados 100% en local** (sin APIs comerciales), para generar recomendaciones académicas personalizadas en tiempo de ejecución, basadas en:

- 📊 **Desempeño académico** (calificaciones, historial de intentos)
- 🧠 **Estilo de aprendizaje** (VARK / Felder-Silverman)
- 💻 **Comportamiento en plataforma** (frecuencia y tipo de recursos consultados)

La validación pedagógica del modelo se realiza con el marco **ARCS** de John Keller y el instrumento **IMMS** (Instructional Materials Motivation Survey), revisados por la asesoría pedagógica del proyecto.

### Principios rectores del proyecto

1. ❌ **No es un chatbot genérico** ni de recordatorios.
2. ❌ **Sin APIs comerciales** — soberanía de datos estudiantiles y costo cero recurrente.
3. ✅ **SLMs locales** servidos con Ollama en infraestructura propia.
4. ✅ **Generación al vuelo** (in-context), no plantillas estáticas.
5. ✅ **Guardrails rigurosos**: sin soluciones de tareas, sin off-topic, tono formativo.
6. ✅ Respuesta **empática y no punitiva** ante bajo desempeño.

---

## 👥 Equipo

| Rol | Integrante | Responsabilidad |
|---|---|---|
| Desarrollador | Persona 1 | Infraestructura SLM / Backend |
| Desarrollador | Persona 2 | Prompts y Guardrails |
| Desarrollador | Persona 3 | Documentación y Presentación |
| Asesoría técnica | Persona 4 | Arquitectura IA, despliegue local, infraestructura |
| Asesoría pedagógica | Persona 5 | Diseño instruccional, ARCS/IMMS |
| Dirección del proyecto | Persona 6 | Seguimiento de asignatura |

---

## 🗺️ Entregas del proyecto

| Entrega | Descripción | Sprints | Estado |
|---|---|---|---|
| [Entrega 1 — PoC Funcional](docs/entregas/entrega-1-poc-funcional/README.md) | Motor de inferencia local, prompts con guardrails, benchmarks, arquitectura y presentación técnica | 6 | 🔄 En curso |
| Entrega 2 | *Por definir según la dirección del proyecto* | — | ⏳ No iniciada |

📖 **Índice de entregas y convenciones:** [docs/entregas/](docs/entregas/README.md)

---

## 📁 Estructura del repositorio

```
savio-ai-recommender/
├── README.md                 ← Este archivo
├── docs/
│   ├── entregas/             ← Entregas del proyecto divididas en sprints
│   └── arquitectura/         ← Diagramas del subsistema e integración con Savio
├── poc_slm/                  ← Scripts Python de inferencia local (Sprint 2)
├── prompts/                  ← System prompts, guardrails y escenarios (Sprint 3)
└── benchmarks/               ← Mediciones reales de RAM/velocidad de SLMs (Sprint 4)
```

---

## 🏃 Entrega 1 — Sprints

| Sprint | Documento | Issues | Estado |
|---|---|---|---|
| 1 | [Preparación del entorno y repositorio](docs/entregas/entrega-1-poc-funcional/sprint-1-preparacion.md) | #1, #2 | 🔄 En curso |
| 2 | [Motor de inferencia local](docs/entregas/entrega-1-poc-funcional/sprint-2-motor-inferencia.md) | #3 | ✅ Completado |
| 3 | [Prompts y guardrails](docs/entregas/entrega-1-poc-funcional/sprint-3-prompts-guardrails.md) | #4–#7 | ⏳ Pendiente |
| 4 | [Benchmarks de SLMs y arquitectura](docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md) | #8, #9, #11 | ⏳ Pendiente |
| 5 | [Presentación técnica](docs/entregas/entrega-1-poc-funcional/sprint-5-presentacion.md) | #12 | ⏳ Pendiente |
| 6 | [Verificación pre-entrega y demo](docs/entregas/entrega-1-poc-funcional/sprint-6-verificacion-demo.md) | #13 | ⏳ Pendiente |

---



Guía de instalación paso a paso: **[Sprint 1 — Preparación](docs/entregas/entrega-1-poc-funcional/sprint-1-preparacion.md)**.

---

## 🔬 Modelos evaluados

| Modelo | Tamaño | Rol en la PoC |
|---|---|---|
| Qwen 2.5 1.5B (Q4_K_M) | ~1.5 GB RAM | ✅ Modelo principal de la demo |
| Gemma 2 2B (Q4_K_M) | ~2 GB RAM | 🔄 Comparación en benchmark |
| Qwen 2.5 3B (Q4_K_M) | ~2.5 GB RAM | 🔄 Comparación (límite en CPU) |

Resultados medidos en [`benchmarks/`](benchmarks/README.md) *(Sprint 4)*.

---

## 🚀 Inicio rápido

```bash
# 1. Instalar Ollama desde https://ollama.com
# 2. Descargar el modelo
ollama pull qwen2.5:1.5b

# 3. Entorno Python
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# 4. Ejecutar un escenario de la PoC
python poc_slm/recommender.py --escenario bajo_desempeno
```

---

## 📚 Contexto académico

Proyecto de ingeniería — Universidad Tecnológica de Bolívar.
Alcance actual: arquitectura, requerimientos y PoC demostrable (Entrega 1).
Alcance posterior: despliegue controlado en Savio, piloto con estudiantes y validación ARCS/IMMS (entregas futuras).
