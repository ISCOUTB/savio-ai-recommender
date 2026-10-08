# docs/presentacion — Presentación técnica de la Entrega 1

Material de presentación de la PoC (Sprint 5, Issue #12).

> 📌 Documentación del sprint: [docs/entregas/entrega-1-poc-funcional/sprint-5-presentacion.md](../entregas/entrega-1-poc-funcional/sprint-5-presentacion.md)

## Archivos

| Archivo | Contenido |
|---|---|
| [`presentacion-tecnica-entrega1.pptx`](presentacion-tecnica-entrega1.pptx) | Presentación de 16 diapositivas (16:9) con notas del orador |
| [`generar_presentacion.py`](generar_presentacion.py) | Script que genera el `.pptx` a partir de la evidencia del repositorio |
| [`demo-qwen2.5-3b/`](demo-qwen2.5-3b/) | Salidas reales del modelo seleccionado (escenarios A, B y ataques); plan B de la demo |
| [`requirements.txt`](requirements.txt) | Dependencias para regenerar la presentación y el diagrama |

## Secciones → diapositivas

| # | Sección exigida | Diapositivas | Fuente de los datos |
|---|---|---|---|
| 1 | Portada y ficha técnica | 1 (portada), 3 (ficha) | — |
| 2 | Problema y justificación | 4 | README del proyecto |
| 3 | Estado del arte (ALEKS, Knewton Alta → alternativa abierta y local) | 5 | Resumen del equipo |
| 4 | Evaluación de SLMs con benchmarks propios | 6 (gráfica), 7 (tabla y modelo seleccionado) | [`benchmarks/resultados/resultados.json`](../../benchmarks/resultados/resultados.json) |
| 5 | Arquitectura + guardrails con diagrama propio | 8 (diagrama), 9 (guardrails y pruebas adversariales) | [`docs/arquitectura/`](../arquitectura/), [`prompts/`](../../prompts/) |
| 6 | Adaptación pedagógica + ARCS/IMMS | 10 (visual vs textual), 11 (ARCS/IMMS) | [`demo-qwen2.5-3b/`](demo-qwen2.5-3b/) |
| 7 | Demostración funcional con plan B | 12 (guion), 13 (plan B) | [`prompts/salidas-respaldo/`](../../prompts/salidas-respaldo/), [`demo-qwen2.5-3b/`](demo-qwen2.5-3b/) |
| 8 | Cronograma + solicitud de infraestructura | 14 (cronograma), 15 (infraestructura) | Sprint 6, benchmarks |

Además: diapositiva 2 (agenda) y 16 (conclusiones y preguntas).

## Regenerar

La gráfica y la tabla de benchmarks se leen de `resultados.json`, así que si se repite el benchmark basta con regenerar:

```bash
pip install -r docs/presentacion/requirements.txt
python docs/arquitectura/generar_diagrama.py        # solo si cambió el diagrama
python docs/presentacion/generar_presentacion.py
```

> ⚠️ Si el equipo edita el `.pptx` a mano en PowerPoint, regenerarlo con el script sobrescribe esos cambios. Una vez aprobada la versión final, editar directamente el `.pptx`.

## Revisión del equipo (criterio de aceptación)

Antes de marcar el issue como "Listo", cada integrante revisa la presentación y lo deja registrado aquí:

| Integrante | Revisó | Observaciones |
|---|---|---|
| Jesús Velázquez | ⏳ | |
| Sebastián Paternina | ⏳ | |
| Yosser Caraballo | ⏳ | |

Puntos a confirmar en la revisión:
- Datos comerciales del estado del arte (diapositiva 5): proveedor, modelo de licencia e integración vigentes.
- Alcance de la Entrega 2 y del cierre (diapositiva 14): es una **propuesta** sujeta a la dirección del proyecto.
- Licencia de Qwen 2.5 3B (diapositiva 15): validar el uso institucional o adoptar el respaldo Qwen 2.5 1.5B.
