# Modelos candidatos para Entrega 2

> **Nota:** Este documento es una version preliminar. La comparativa completa con datos medidos, KV cache y decision final esta en `docs/investigacion/propuesta-destilacion-slm.md` (Secciones 4 y 5, E2-09).

Corto lista inicial, pendiente de validacion con pipeline de destilacion.

| Familia | Escala util | Ventaja | Riesgo o limite |
|---|---|---|---|
| Qwen 2.5 | 0.5B, 1.5B, 3B | Buen razonamiento en modelos pequenos, ya medido en Entrega 1 | Revisar licencia antes de uso institucional |
| Gemma 2 | 2B | Abierto y documentado | En la PoC mostro riesgo de URLs inventadas |
| Nemotron | pequeno/mini | Enfoque de eficiencia | Validar soporte y formato de despliegue local |
| Mistral / Mixtral | 7B o mas | Robusto en instrucciones | Puede ser pesado para servidor modesto |

Criterios de seleccion:

1. RAM base del modelo.
2. KV cache por concurrencia estimada.
3. Latencia por recomendacion.
4. Capacidad de seguir guardrails.
5. Licencia compatible con uso academico institucional.
6. Facilidad de destilar o ajustar en Hugging Face.

Decision pendiente: E2-09.
