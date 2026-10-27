# Entrega 3 - Sprint 4: OE3 - Validacion psicometrica, metricas en CPU y cierre

**Estado:** Pendiente
**Issues:** E3-09, E3-10
**Objetivo SMART asociado:** Objetivo Especifico 3 (OE3)

## Objetivo

Validar con metricas objetivas si el modelo SLM quedo bien destilado y cuantizado, midiendo su precision/fidelidad interpretativa frente al *ground truth* de los LLMs maestros, el respeto estricto a las escalas psicometricas y los tiempos de inferencia en CPU estandar.

## Alcance

- **E3-09 (Evaluacion SMART de fidelidad diagnostica y rendimiento en CPU):**
  - Evaluar el SLM cuantizado sobre el conjunto de prueba (20% reservado de `E3-06` + los 3 perfiles reales de `E3-05`).
  - Medir fidelidad de interpretacion de cada test (CHASIDE, Felder-Silverman, Personalidad) y calidad del cruce vocacional/conductual frente al *ground truth*.
  - Medir tiempos de respuesta (latencia total, tokens/s y consumo de RAM) ejecutando 100% en CPU estandar.
  - Verificar guardrails eticos: que el modelo no altere los puntajes brutos recibidos ni emita diagnosticos clinicos patologizantes (apoyo al diagnostico inicial, sin reemplazar al profesional).
- **E3-10 (Demostracion de Backend y Cierre de Entrega 3):**
  - Preparar y verificar la ejecucion reproducible por consola del motor backend de inferencia integrada y consolidar el informe de resultados de la Entrega 3.

## Criterios de aceptacion

- [ ] Rubrica cuantitativa aplicada sobre el conjunto de validacion con fidelidad $\ge 85\%$ respecto al *ground truth* (`E3-09`).
- [ ] Benchmark en CPU estandar registrado (RAM $\le 2.5\text{ GB}$, `0 MB` VRAM, tiempo de inferencia por perfil documentado) (`E3-09`).
- [ ] `100%` de cumplimiento en verificacion de rigor psicometrico (respeta puntajes originales brutos y tono de apoyo no clinico) (`E3-09`).
- [ ] Flujo backend de extremo a extremo demostrado y documentado en la bitacora de cierre (`E3-10`).

