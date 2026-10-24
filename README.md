# Savio AI Recommender

> **Subsistema de recomendacion de contenido academico adaptativo basado en Inteligencia Artificial para Savio (Moodle) - Universidad Tecnologica de Bolivar.**

[![Estado](https://img.shields.io/badge/estado-Entrega%203%20en%20curso-green)]()
[![Demo local](https://img.shields.io/badge/SLM%20CPU-Cuantizado%20GGUF-blue)]()
[![Entrenamiento](https://img.shields.io/badge/Ajuste%20Cloud-Hugging%20Face-yellow)]()
[![Runtime](https://img.shields.io/badge/runtime-CPU%20sin%20VRAM-lightgrey)]()

---

## Descripcion

Este repositorio contiene el desarrollo del **sistema de inferencia con Inteligencia Artificial para interpretacion psicologica, de estilos de aprendizaje y vocacional** orientado a la plataforma **Savio** - Universidad Tecnologica de Bolivar.

Siguiendo la delimitacion de alcance establecida para la **Entrega 3**, el sistema emplea un **Small Language Model (SLM) especializado y cuantizado para ejecutarse sobre CPU estandar (sin dependencia de VRAM)** que procesa y cruza las **puntuaciones originales brutas** de tres instrumentos psicometricos validados junto con su literatura teorica para apoyar el diagnostico inicial de un estudiante (sin reemplazar al profesional):

- **CHASIDE:** test estandarizado de orientacion vocacional (intereses y aptitudes en 7 areas).
- **Modelo de Felder-Silverman (ILS):** cuestionario de estilos de aprendizaje en 4 dimensiones bipolares (activo/reflexivo, sensitivo/intuitivo, visual/verbal, secuencial/global).
- **Test de Personalidad:** caracterizacion de rasgos conductuales del estudiante.


### Principios rectores del proyecto (Entrega 3)

1. **Caso de estudio concreto y medible:** interpretacion psicologica y vocacional integrada como apoyo al diagnostico inicial, dejando atras la generacion masiva de contenidos.
2. **Rigor psicometrico estricto:** prohibicion absoluta de alterar, reescalar o inventar escalas sobre los instrumentos validados; el motor recibe las **puntuaciones originales brutas**.
3. **Estrategia LLM Maestro -> SLM Especializado:** Claude/ChatGPT se usan solo en laboratorio con la bibliografia oficial de los 3 tests para construir el *ground truth*; el objetivo final es un SLM pequeno y especializado.
4. **Inferencia en CPU sin dependencia de VRAM:** pruebas y ajuste en capas gratuitas/gestionadas en la nube (**Hugging Face**) y despliegue con modelo cuantizado (GGUF) sobre CPU estandar.
5. **Backend antes que Frontend y cero sobreingenieria:** prioridad total en la coherencia y exactitud del motor de inferencia antes de disenar interfaces visuales o arquitecturas complejas.
6. **Formulacion con Objetivos SMART:** 1 Objetivo General y 3 Objetivos Especificos medibles ([objetivos-smart-formulario.md](docs/entregas/entrega-3-interpretacion-psicometrica/objetivos-smart-formulario.md)).


## Entregas del proyecto

| Entrega | Descripcion | Sprints | Estado |
|---|---|---|---|
| [Entrega 1 - PoC Funcional](docs/entregas/entrega-1-poc-funcional/README.md) | Motor de inferencia local, prompts con guardrails, benchmarks, arquitectura y presentacion tecnica | 6 | Completada |
| [Entrega 2 - Personalizacion](docs/entregas/entrega-2-personalizacion/README.md) | Bloques psicopedagogicos en Moodle Docker, propuesta de destilacion de SLM y prototipo inicial (E2-01 a E2-12) | 6 | Completada |
| [Entrega 3 - Interpretacion Psicometrica](docs/entregas/entrega-3-interpretacion-psicometrica/README.md) | Interpretacion psicologica y vocacional integrada sobre puntajes brutos (CHASIDE, Felder-Silverman, Personalidad), ajuste en Hugging Face, cuantizacion para CPU y validacion SMART | 4 | En curso |

Indice general de documentacion: [docs/](docs/README.md)  
Indice de entregas y convenciones: [docs/entregas/](docs/entregas/README.md)  
Formulacion SMART y apartado tecnico del formulario: [objetivos-smart-formulario.md](docs/entregas/entrega-3-interpretacion-psicometrica/objetivos-smart-formulario.md)  
Plan operativo del proyecto: [ROADMAP.md](ROADMAP.md)

---

## Estructura del repositorio

```text
savio-ai-recommender/
  README.md
  ROADMAP.md              Plan operativo del proyecto
  AGENTS.md               Instrucciones para agentes de codigo (OpenCode)
  opencode.jsonc          Config de OpenCode (registra ./skills)
  skills/                 Habilidades locales de OpenCode (inventario en skills/README.md)
  docs/
    README.md             Indice general de la documentacion
    entregas/             Entregas del proyecto divididas en sprints
    especificaciones/     Schemas JSON de perfil, recursos y feedback
    investigacion/        Modelos candidatos, destilacion y riesgos
    decisiones/           Decisiones, problemas y su justificacion
    arquitectura/         Diagramas del subsistema e integracion con Savio
    presentacion/         Presentacion tecnica y generador
  poc_slm/                Scripts Python de inferencia local (Sprint 2)
    prompt_builder.py     Prompt Builder semanal de Entrega 2 (E2-10)
    recursos/             Recursos A/B/C de la semana piloto
    evidencias/           Salidas de demostracion ordenadas
  prompts/                System prompts, guardrails y escenarios (Sprint 3 y E2-10)
  benchmarks/             Mediciones reales de RAM/velocidad de SLMs (Sprint 4)
    equipos/              Reporte por hardware de prueba
    resultados/           Datos separados por equipo
  moodle/                 Moodle local minimo con Docker (habilitador Entrega 2)
  perfiles/               Ejemplos y fixtures del perfil psicopedagogico (simulados)
  personalidad/           Instrumento de personalidad (puntero al documento canonico)
  experimentos/           Bitacora de pruebas de Entrega 2
  fuentes/                Documentos base del docente (no versionados, ver README)
```

---

## Entrega 1 - Sprints

| Sprint | Documento | Issues | Estado |
|---|---|---|---|
| 1 | [Preparacion del entorno y repositorio](docs/entregas/entrega-1-poc-funcional/sprint-1-preparacion.md) | #1, #2 | Completado |
| 2 | [Motor de inferencia local](docs/entregas/entrega-1-poc-funcional/sprint-2-motor-inferencia.md) | #3 | Completado |
| 3 | [Prompts y guardrails](docs/entregas/entrega-1-poc-funcional/sprint-3-prompts-guardrails.md) | #4-#7 | Completado |
| 4 | [Benchmarks de SLMs y arquitectura](docs/entregas/entrega-1-poc-funcional/sprint-4-benchmarks.md) | #8, #9, #11 | Completado |
| 5 | [Presentacion tecnica](docs/entregas/entrega-1-poc-funcional/sprint-5-presentacion.md) | #12 | Completado |
| 6 | [Verificacion pre-entrega y demo](docs/entregas/entrega-1-poc-funcional/sprint-6-verificacion-demo.md) | #13 | Completado |

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

- **Alcance completado (Entrega 1):** PoC de inferencia local con SLMs, guardrails y benchmarks iniciales.
- **Alcance completado (Entrega 2):** bloques psicometricos IS-UTB en Moodle Docker, propuesta de destilacion y ciclo de feedback (`E2-01` a `E2-12`).
- **Alcance actual (Entrega 3):** motor backend de inferencia con SLM destilado en Hugging Face y cuantizado para CPU estandar (sin VRAM), enfocado en la interpretacion psicologica y vocacional integrada sobre puntuaciones originales brutas de CHASIDE, Felder-Silverman y Personalidad bajo metodologia SMART.
