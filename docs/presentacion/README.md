# docs/presentacion — Presentacion tecnica de la Entrega 1

Material de presentacion de la PoC (Sprint 5, Issue #12).

> 📌 Documentacion del sprint: [docs/entregas/entrega-1-poc-funcional/sprint-5-presentacion.md](../entregas/entrega-1-poc-funcional/sprint-5-presentacion.md)

## Archivos

| Archivo | Contenido |
|---|---|
| [`presentacion-tecnica-entrega1.pptx`](presentacion-tecnica-entrega1.pptx) | Presentacion de 16 diapositivas (16:9) con notas del orador. **Generado: no editar a mano**, se regenera con el script de abajo |
| [`generar_presentacion.py`](generar_presentacion.py) | Script que genera el `.pptx` a partir de la evidencia del repositorio |
| [`demo-qwen2.5-3b/`](demo-qwen2.5-3b/) | Salidas reales del modelo seleccionado (escenarios A, B y ataques); plan B de la demo |
| [`requirements.txt`](requirements.txt) | Dependencias para regenerar la presentacion y el diagrama |

> El `.pptx` versionado es el entregable y se conserva para no regenerarlo en cada revision.
> Si cambia la evidencia, se regenera y se commitea el resultado: nunca se edita a mano.

## Secciones → diapositivas

| # | Seccion exigida | Diapositivas | Fuente de los datos |
|---|---|---|---|
| 1 | Portada y ficha tecnica | 1 (portada), 3 (ficha) | — |
| 2 | Problema y justificacion | 4 | README del proyecto |
| 3 | Estado del arte (ALEKS, Knewton Alta → alternativa abierta y local) | 5 | Resumen del equipo |
| 4 | Evaluacion de SLMs con benchmarks propios | 6 (grafica), 7 (tabla y modelo seleccionado) | [`benchmarks/README.md`](../../benchmarks/README.md), [`benchmarks/resultados/amd-ryzen-5-5600h-rtx-3050/resultados.json`](../../benchmarks/resultados/amd-ryzen-5-5600h-rtx-3050/resultados.json) |
| 5 | Arquitectura + guardrails con diagrama propio | 8 (diagrama), 9 (guardrails y pruebas adversariales) | [`docs/arquitectura/`](../arquitectura/), [`prompts/`](../../prompts/) |
| 6 | Adaptacion pedagogica + ARCS/IMMS | 10 (visual vs textual), 11 (ARCS/IMMS) | [`demo-qwen2.5-3b/`](demo-qwen2.5-3b/) |
| 7 | Demostracion funcional con plan B | 12 (guion), 13 (plan B) | [`prompts/salidas-respaldo/`](../../prompts/salidas-respaldo/), [`demo-qwen2.5-3b/`](demo-qwen2.5-3b/) |
| 8 | Cronograma + solicitud de infraestructura | 14 (cronograma), 15 (infraestructura) | Sprint 6, benchmarks |

Ademas: diapositiva 2 (agenda) y 16 (conclusiones y preguntas).

## Regenerar

La grafica y la tabla de benchmarks se leen de `resultados.json`, asi que si se repite el benchmark basta con regenerar:

```bash
pip install -r docs/presentacion/requirements.txt
python docs/arquitectura/generar_diagrama.py        # solo si cambio el diagrama
python docs/presentacion/generar_presentacion.py
```


## Revision del equipo (criterio de aceptacion)

Antes de marcar el issue como "Listo", cada integrante revisa la presentacion y lo deja registrado aqui:

| Integrante | Reviso | Observaciones |
|---|---|---|
| Jesus Velazquez | ✅ | |
| Sebastian Paternina | ✅ | |
| Yosser Caraballo | ✅ | |

Puntos a confirmar en la revision:
- Datos comerciales del estado del arte (diapositiva 5): proveedor, modelo de licencia e integracion vigentes.
- Alcance de la Entrega 2 y del cierre (diapositiva 14): es una **propuesta** sujeta a la direccion del proyecto.
- Licencia de Qwen 2.5 3B (diapositiva 15): validar el uso institucional o adoptar el respaldo Qwen 2.5 1.5B.
