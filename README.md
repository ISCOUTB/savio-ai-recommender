# Savio AI Recommender

> **Subsistema de recomendación de contenido académico adaptativo basado en Inteligencia Artificial para Savio (Moodle) — Universidad Tecnológica de Bolívar.**

[![Estado](https://img.shields.io/badge/estado-PoC%20en%20desarrollo-yellow)]()
[![Modelo](https://img.shields.io/badge/SLM-Qwen%202.5%201.5B-blue)]()
[![Runtime](https://img.shields.io/badge/runtime-Ollama-lightgrey)]()

---

## 📌 Descripción

Este repositorio contiene la **Prueba de Concepto (PoC)** del subsistema de recomendación adaptativa para la plataforma **Savio** (EVA institucional basado en Moodle). El sistema utiliza **Small Language Models (SLMs) de pesos abiertos, ejecutados 100% en local** (sin APIs comerciales), para generar recomendaciones académicas personalizadas en tiempo de ejecución, basadas en:

- 📊 **Desempeño académico** (calificaciones, historial de intentos)
- 🧠 **Estilo de aprendizaje** (VARK / Felder-Silverman)
- 💻 **Comportamiento en plataforma** (frecuencia y tipo de recursos consultados)

La validación pedagógica se realiza con el modelo **ARCS** de John Keller y el instrumento **IMMS** (Instructional Materials Motivation Survey).

### Principios rectores del proyecto

1. ❌ **No es un chatbot genérico** ni de recordatorios.
2. ❌ **Sin APIs comerciales** (OpenAI, Claude) — soberanía de datos estudiantiles y costo cero recurrente.
3. ✅ **SLMs locales** servidos con Ollama en infraestructura propia.
4. ✅ **Generación al vuelo** (in-context), no plantillas estáticas.
5. ✅ **Guardrails rigurosos**: sin soluciones de tareas, sin off-topic, tono formativo.
6. ✅ Respuesta **empática y no punitiva** ante bajo desempeño.

---

## 👥 Equipo

| Rol | Nombre | Responsabilidad |
|---|---|---|
| Integrante 1 | *(por definir)* | Infraestructura SLM / Backend |
| Integrante 2 | *(por definir)* | Prompts y Guardrails |
| Integrante 3 | *(por definir)* | Documentación y Presentación |
| Asesor técnico | Prof. Jairo | Arquitectura IA, despliegue local, infraestructura |
| Asesora pedagógica | *(por definir)* | Diseño instruccional, ARCS/IMMS |
| Director | Prof. Eisner / Edwin | Seguimiento de asignatura |

---

## 🗺️ Estado del plan de trabajo

| Fase | Descripción | Estado |
|---|---|---|
| [Fase 0](docs/plan-trabajo/fase-0-preparacion.md) | Preparación del entorno y del repositorio | 🔄 En curso |
| [Fase 1](docs/plan-trabajo/fase-1-motor-inferencia.md) | Motor de inferencia local (Ollama + Python) | ⏳ Pendiente |
| [Fase 2](docs/plan-trabajo/fase-2-prompts-guardrails.md) | Prompts contextuales y guardrails | ⏳ Pendiente |
| [Fase 3](docs/plan-trabajo/fase-3-benchmarks.md) | Benchmarks de SLMs y arquitectura | ⏳ Pendiente |
| [Fase 4](docs/plan-trabajo/fase-4-presentacion.md) | Presentación ejecutiva (8 diapositivas) | ⏳ Pendiente |
| [Fase 5](docs/plan-trabajo/fase-5-entrega.md) | Entrega y demo en vivo | ⏳ Pendiente |

📖 **Índice maestro del plan:** [docs/plan-trabajo/](docs/plan-trabajo/README.md)

---

## 📁 Estructura del repositorio

```
savio-ai-recommender/
├── README.md                 ← Este archivo
├── docs/
│   ├── plan-trabajo/         ← Fases del proyecto, paso a paso documentado
│   └── arquitectura/         ← Diagramas del subsistema e integración con Savio
├── poc_slm/                  ← Scripts Python de inferencia local (Fase 1)
├── prompts/                  ← System prompts, guardrails y escenarios (Fase 2)
└── benchmarks/               ← Mediciones reales de RAM/velocidad de SLMs (Fase 3)
```

---

## ⚙️ Requisitos (PoC local)

| Componente | Mínimo | Recomendado |
|---|---|---|
| RAM | 8 GB | 16 GB |
| CPU | 4 núcleos | 8 núcleos |
| GPU | No requerida (inferencia CPU) | NVIDIA 8+ GB VRAM |
| Disco | 10 GB libres | 20 GB SSD |
| Software | Ollama, Python 3.11+ | — |

La guía de instalación paso a paso está en la **[Fase 0](docs/plan-trabajo/fase-0-preparacion.md)**.

---

## 🔬 Modelos evaluados

| Modelo | Tamaño | Rol en la PoC |
|---|---|---|
| Qwen 2.5 1.5B (Q4_K_M) | ~1.5 GB RAM | ✅ Modelo principal de la demo |
| Gemma 2 2B (Q4_K_M) | ~2 GB RAM | 🔄 Comparación en benchmark |
| Qwen 2.5 3B (Q4_K_M) | ~2.5 GB RAM | 🔄 Comparación (límite en CPU) |

Resultados medidos en [`benchmarks/`](benchmarks/README.md) *(Fase 3)*.

---

## 🚀 Inicio rápido *(disponible al cierre de la Fase 1)*

```bash
# 1. Instalar Ollama desde https://ollama.com
# 2. Descargar el modelo
ollama pull qwen2.5:1.5b

# 3. Ejecutar un escenario de la PoC
python poc_slm/recommender.py --escenario bajo_desempeno
```

---

## 📚 Contexto académico

Proyecto de ingeniería — Universidad Tecnológica de Bolívar.
Semestre actual: arquitectura, requerimientos y PoC demostrable.
Siguiente semestre: despliegue controlado en Savio, piloto con estudiantes y validación ARCS/IMMS.
