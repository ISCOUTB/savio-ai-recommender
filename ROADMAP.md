# ROADMAP - Savio AI Recommender

> Plan operativo del proyecto. Detalle de sprints e issues en cada carpeta de [docs/entregas/](docs/entregas/README.md).

## Vista general

| Entrega | Alcance | Estado |
|---|---|---|
| [Entrega 1 - PoC Funcional](docs/entregas/entrega-1-poc-funcional/README.md) | SLM local con Ollama, prompts con guardrails, benchmarks propios, arquitectura y presentacion tecnica | Completada |
| [Entrega 2 - Personalizacion](docs/entregas/entrega-2-personalizacion/README.md) | Modelado inicial de instrumentos (Estilos de Aprendizaje, Personalidad, CHASIDE), Moodle local en Docker, diseno de destilacion y prototipo de recomendacion semanal (E2-01 a E2-12 cerrados) | Completada |
| [Entrega 3 - Interpretacion Psicometrica](docs/entregas/entrega-3-interpretacion-psicometrica/README.md) | Reorientacion docente: motor backend de inferencia con SLM destilado en Hugging Face y cuantizado para CPU estandar (sin VRAM), enfocado en la interpretacion psicologica y vocacional integrada a partir de puntajes originales brutos de CHASIDE, Felder-Silverman y Personalidad, bajo metodologia SMART | En curso |

## Secuencia de trabajo

1. **Entrega 1 (Completada):** demuestra que un SLM local genera respuestas bajo guardrails (Sprints 1-6).
2. **Entrega 2 (Completada):** instala los bloques institucionales IS-UTB en Moodle local, explora el perfilamiento y deja formulada la base de destilacion y feedback (issues `#18` a `#29` cerrados).
3. **Entrega 3 (En curso):** aterriza el proyecto en un caso de estudio puntual y medible dictado por el docente:
   - **Caso concreto:** interpretacion psicologica y vocacional integrada como apoyo al diagnostico inicial del estudiante (sin reemplazar al profesional).
   - **Rigor psicometrico:** prohibido alterar o normalizar escalas validadas; el backend consume directamente las **puntuaciones originales brutas** de **CHASIDE**, **Felder-Silverman** y **Test de Personalidad**.
   - **Estrategia Teacher -> Student:** LLMs de frontera (Claude, ChatGPT) alimentados con literatura tecnica oficial generan el *ground truth* en fase de laboratorio; con el se ajusta/destila un SLM especializado en entornos cloud gestionados (**Hugging Face**).
   - **Inferencia 100% en CPU (sin VRAM):** modelo cuantizado (GGUF) optimizado para CPU estandar, sin depender de GPUs locales ni de VRAM en el cluster Savio.
   - **Ingenieria pragmatica:** backend antes que frontend, sin sobreingenieria de microservicios y guiado por **1 Objetivo General y 3 Objetivos Especificos SMART** ([objetivos-smart-formulario.md](docs/entregas/entrega-3-interpretacion-psicometrica/objetivos-smart-formulario.md)).

## Decisiones tecnicas activas (Entrega 3)

- **Instrumentos y escalas (directriz docente):** CHASIDE (`0-14` en 7 areas), Modelo de Felder-Silverman (`0-11` por polo en 4 dimensiones bipolares) y Test de Personalidad (`0-9` por polo). Se descarta la escala `1.0-5.0` y el indice inferido `autonomia` de Entrega 2 (cerrados en `#37`, `#39` y `#41`).
- **Modelos y entrenamiento:** LLMs de frontera (Claude / ChatGPT) exclusivamente como *Teacher* para sintetizar el *ground truth*; ajuste del SLM en **Hugging Face** y cuantizacion GGUF (`Q4_K_M`) para despliegue en CPU estandar.
- **Runtime:** inferencia local sobre CPU sin dependencia obligatoria de VRAM (`http://localhost:11434` / GGUF).
- **Prioridad funcional:** validacion completa del pipeline backend de entrada/salida antes de cualquier interfaz grafica.

## Convenciones operativas

Flujo de issues, formato de commits y revision por par: [docs/entregas/README.md](docs/entregas/README.md).
