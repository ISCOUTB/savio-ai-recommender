# Entrega 3 - Sprint 3: OE2 - Destilacion en Hugging Face, cuantizacion y Backend en CPU

**Estado:** Pendiente
**Issues:** E3-07, E3-08 (#44)
**Objetivo SMART asociado:** Objetivo Especifico 2 (OE2)

## Objetivo

Ajustar/destilar un Modelo de Lenguaje Pequeno (SLM) especializado en interpretar las correlaciones entre los tres cuestionarios utilizando plataformas en la nube con capas gratuitas o gestionadas (**Hugging Face**), cuantizarlo para eliminar cualquier dependencia de VRAM y construir el pipeline backend de inferencia que se ejecute sobre CPU estandar.

## Alcance

- **E3-07 (Pipeline Backend de Inferencia Integrada):**
  - Prioridad absoluta en el backend (cero interfaz grafica o efectos visuales).
  - Sin sobreingenieria: un modulo Python limpio que recibe el JSON de puntajes brutos originales de los 3 tests, inyecta el contexto psicometrico y consulta al SLM local para devolver el perfil interpretativo integrado.
- **E3-08 / #44 (Ajuste en Hugging Face y Cuantizacion para CPU):**
  - Ejecutar las pruebas y el fine-tuning supervisado (SFT / QLoRA) del SLM (`Qwen 2.5 0.5B` / `1.5B`) en entornos gestionados en la nube (Hugging Face / notebooks con GPU gratuita) usando el corpus *ground truth* de `E3-06`.
  - Cuantizar y exportar el modelo resultante a formato **GGUF (`Q4_K_M`)** optimizado para inferencia en **CPU estandar**, garantizando que funcione en cualquier computador convencional o en el cluster Savio sin VRAM dedicada.

## Criterios de aceptacion

- [ ] Entrenamiento/ajuste ejecutado en entorno cloud gestionado (Hugging Face) con hiperparametros y logs documentados (`E3-08` / `#44`).
- [ ] Modelo exportado a GGUF cuantizado y operativo sobre CPU estandar con `0 MB` de VRAM requerida (`E3-08` / `#44`).
- [ ] Pipeline backend de inferencia recibe puntajes brutos de CHASIDE, Felder-Silverman y Personalidad y entrega la interpretacion integrada estructurada (`E3-07`).
- [ ] Sin componentes de frontend ni arquitecturas de microservicios innecesarias (cumplimiento de las directrices 5 y 6 del docente).

