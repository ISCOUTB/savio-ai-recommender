# Savio AI Recommender

> **Subsistema de recomendacion de contenido academico adaptativo basado en Inteligencia Artificial para Savio (Moodle) - Universidad Tecnologica de Bolivar.**

[![Estado](https://img.shields.io/badge/estado-Entrega%201%20en%20curso-yellow)]()
[![Demo local](https://img.shields.io/badge/SLM%20demo-Qwen%202.5%201.5B-blue)]()
[![Objetivo Savio](https://img.shields.io/badge/SLM%20objetivo-Qwen%202.5%203B-green)]()
[![Runtime](https://img.shields.io/badge/runtime-Ollama-lightgrey)]()

---

## Descripcion

Este repositorio contiene el desarrollo del **subsistema de recomendacion adaptativa** para la plataforma **Savio** (EVA institucional basado en Moodle). El sistema utiliza **Small Language Models (SLMs) de pesos abiertos, ejecutados 100% en local** (sin APIs comerciales), para generar recomendaciones academicas personalizadas en tiempo de ejecucion, basadas en:

- **Desempeno academico** (calificaciones, historial de intentos)
- **Estilo de aprendizaje** (VARK / Felder-Silverman)
- **Comportamiento en plataforma** (frecuencia y tipo de recursos consultados)

La validacion pedagogica del modelo se realiza con el marco **ARCS** de John Keller y el instrumento **IMMS** (Instructional Materials Motivation Survey), revisados por la asesoria pedagogica del proyecto.

### Principios rectores del proyecto

1. **No es un chatbot generico** ni de recordatorios.
2. **Sin APIs comerciales**: soberania de datos estudiantiles y costo cero recurrente.
3. **SLMs locales** servidos con Ollama en infraestructura propia.
4. **Generacion al vuelo** (in-context), no plantillas estaticas.
5. **Guardrails rigurosos**: sin soluciones de tareas, sin off-topic, tono formativo.
6. Respuesta **empatica y no punitiva** ante bajo desempeno.

---

## Equipo

| Rol | Integrante | Responsabilidad |
|---|---|---|
| Desarrollador | Persona 1 | Infraestructura SLM / Backend |
| Desarrollador | Persona 2 | Prompts y Guardrails |
| Desarrollador | Persona 3 | Documentacion y Presentacion |
| Asesoria tecnica | Persona 4 | Arquitectura IA, despliegue local, infraestructura |
| Asesoria pedagogica | Persona 5 | Diseno instruccional, ARCS/IMMS |
| Direccion del proyecto | Persona 6 | Seguimiento de asignatura |

---

## Entregas del proyecto

| Entrega | Descripcion | Sprints | Estado |
|---|---|---|---|
| [Entrega 1 - PoC Funcional](docs/entregas/entrega-1-poc-funcional/README.md) | Motor de inferencia local, prompts con guardrails, benchmarks, arquitectura y presentacion tecnica | 6 | En curso |
| Entrega 2 | *Por definir segun la direccion del proyecto* | - | No iniciada |

Indice de entregas y convenciones: [docs/entregas/](docs/entregas/README.md)

---

## Estructura del repositorio

```text
savio-ai-recommender/
  README.md
  docs/
    entregas/             Entregas del proyecto divididas en sprints
    arquitectura/         Diagramas del subsistema e integracion con Savio
    presentacion/         Presentacion tecnica y generador
  poc_slm/                Scripts Python de inferencia local (Sprint 2)
    evidencias/           Salidas de demostracion ordenadas
  prompts/                System prompts, guardrails y escenarios (Sprint 3)
  benchmarks/             Mediciones reales de RAM/velocidad de SLMs (Sprint 4)
    equipos/              Reporte por hardware de prueba
    resultados/           Datos separados por equipo
```

---

## Entrega 1 - Sprints

| Sprint | Documento | Issues | Estado |
|---|---|---|---|
| 1 | [Preparacion del entorno y repositorio](docs/entregas/entrega-1-poc-funcional/sprint-1-preparacion.md) | #1, #2 | En curso |
| 2 | [Motor de inferencia local](docs/entregas/entrega-1-poc-funcional/sprint-2-motor-inferencia.md) | #3 | Completado |
| 3 | [Prompts y guardrails](docs/entregas/entrega-1-poc-funcional/sprint-3-prompts-guardrails.md) | #4-#7 | Completado |
| 4 | [Benchmarks de SLMs y arquitectura](docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md) | #8, #9, #11 | En curso |
| 5 | [Presentacion tecnica](docs/entregas/entrega-1-poc-funcional/sprint-5-presentacion.md) | #12 | Pendiente |
| 6 | [Verificacion pre-entrega y demo](docs/entregas/entrega-1-poc-funcional/sprint-6-verificacion-demo.md) | #13 | Pendiente |

Guia de instalacion paso a paso: **[Sprint 1 - Preparacion](docs/entregas/entrega-1-poc-funcional/sprint-1-preparacion.md)**.

---

## Modelos evaluados

| Modelo | Tamano | Rol en la PoC |
|---|---|---|
| Qwen 2.5 1.5B (Q4_K_M) | ~1.2 GB RAM | Modelo principal para demo local sin GPU dedicada |
| Gemma 2 2B (Q4_K_M/Q4_0) | ~2.3 GB RAM | Comparativo de benchmark |
| Qwen 2.5 3B (Q4_K_M) | ~2.2 GB RAM | Objetivo institucional por calidad; pedir GPU para produccion |

Resultados medidos e integrados en [`benchmarks/README.md`](benchmarks/README.md).

---

## Inicio rapido

```bash
# 1. Instalar Ollama desde https://ollama.com
# 2. Descargar el modelo de demo local
ollama pull qwen2.5:1.5b

# 3. Entorno Python
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# 4. Ejecutar un escenario de la PoC
python poc_slm/recommender.py --escenario bajo_desempeno
```

---

## Contexto academico

Proyecto de ingenieria - Universidad Tecnologica de Bolivar.

Alcance actual: arquitectura, requerimientos y PoC demostrable (Entrega 1).
Alcance posterior: despliegue controlado en Savio, piloto con estudiantes y validacion ARCS/IMMS (entregas futuras).
