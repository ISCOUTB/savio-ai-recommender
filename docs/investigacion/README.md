# docs/investigacion - Destilacion y fine-tuning

Documentos de investigacion tecnica de la Entrega 2. La **propuesta consolidada
es el documento canonico**; los demas son notas preliminares que quedaron como
contexto y no deben editarse por separado.

## Documento canonico

| Archivo | Contenido | Issue |
|---|---|---|
| [propuesta-destilacion-slm.md](propuesta-destilacion-slm.md) | Propuesta completa: pregunta de investigacion, comparativa de modelos, KV cache, pipeline de destilacion, datasets A y B, riesgos, licencias, metricas y criterios de aceptacion | E2-09 |

## Notas preliminares (no editar)

| Archivo | Rol actual |
|---|---|
| [modelos-candidatos.md](modelos-candidatos.md) | Primera lista de modelos; la comparativa final esta en las secciones 4 y 5 del canonico |
| [destilacion-finetuning.md](destilacion-finetuning.md) | Primer esquema del pipeline; la version definitiva esta en las secciones 6 y 7 del canonico |
| [riesgos-y-licencias.md](riesgos-y-licencias.md) | Primer borrador de riesgos; la matriz completa esta en las secciones 10 y 11 del canonico |

Regla: cualquier hallazgo nuevo entra al documento canonico. Si una nota
preliminar contradice al canonico, gana el canonico.

## Relacion con el resto del repositorio

- Los datasets A y B que define la propuesta se construyen en E2-19.
- El ajuste, exportacion a GGUF y validacion se ejecutan en E2-20.
- Las decisiones de modelo se apoyan en los benchmarks medidos de
  [benchmarks/resultados/](../../benchmarks/resultados/) (evidencia, no se edita).
