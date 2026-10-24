# docs - Indice de la documentacion

Punto de entrada a la documentacion del proyecto. Si buscas algo y no sabes
donde esta, empieza por la tabla de "Un tema, un documento".

## Mapa de carpetas

| Carpeta | Que contiene | Indice |
|---|---|---|
| `entregas/` | Entregas del proyecto divididas en sprints (Entregas 1, 2 y 3) | [entregas/README.md](entregas/README.md) |
| `especificaciones/` | Contratos JSON, notas de los instrumentos y validadores | [especificaciones/README.md](especificaciones/README.md) |
| `investigacion/` | Destilacion y fine-tuning (propuesta consolidada) | [investigacion/README.md](investigacion/README.md) |
| `decisiones/` | Decisiones, problemas y su justificacion | [decisiones/README.md](decisiones/README.md) |
| `arquitectura/` | Diagramas del subsistema e integracion con Savio | [arquitectura/README.md](arquitectura/README.md) |
| `presentacion/` | Presentacion tecnica y material de demo | [presentacion/README.md](presentacion/README.md) |

Carpetas fuera de `docs/` que tambien son documentacion:

| Carpeta | Que contiene | Indice |
|---|---|---|
| `../prompts/` | System prompts, escenarios y salidas de respaldo | [../prompts/README.md](../prompts/README.md) |
| `../benchmarks/` | Metodologia, equipos y resultados medidos | [../benchmarks/README.md](../benchmarks/README.md) |
| `../poc_slm/` | Scripts de inferencia y recursos de la semana | [../poc_slm/README.md](../poc_slm/README.md) |
| `../moodle/` | Moodle local minimo (habilitador de Entrega 2) | [../moodle/README.md](../moodle/README.md) |
| `../perfiles/` | Ejemplos y fixtures del perfil del estudiante | [../perfiles/README.md](../perfiles/README.md) |
| `../experimentos/` | Bitacora corta de pruebas de Entrega 2 | [../experimentos/README.md](../experimentos/README.md) |
| `../fuentes/` | Documentos base del docente (no versionados) | [../fuentes/README.md](../fuentes/README.md) |

## Un tema, un documento

Cuando dos archivos hablan de lo mismo, manda el canonico. Los demas son
punteros o borradores y no se editan por separado.

| Tema | Documento canonico | Punteros o copias |
|---|---|---|
| Plan operativo y cronograma | `../ROADMAP.md` | estados por sprint en `entregas/` |
| Estado de una entrega | `entregas/<entrega>/README.md` | `entregas/README.md` (tabla general) |
| Objetivos SMART y formulario tecnico (Entrega 3) | [entregas/entrega-3-interpretacion-psicometrica/objetivos-smart-formulario.md](entregas/entrega-3-interpretacion-psicometrica/objetivos-smart-formulario.md) | `entregas/entrega-3-interpretacion-psicometrica/README.md` |
| Issues de Entrega 3 | GitHub (milestone Entrega 3) | [entregas/entrega-3-interpretacion-psicometrica/github-issues.md](entregas/entrega-3-interpretacion-psicometrica/github-issues.md) |
| Issues de Entrega 2 (historico) | GitHub (milestone Entrega 2) | [entregas/entrega-2-personalizacion/github-issues.md](entregas/entrega-2-personalizacion/github-issues.md) |
| Contrato del perfil (Entrega 2) | `especificaciones/perfil-estudiante.schema.json` | `perfiles/ejemplo-perfil-*.json` (ejemplos que deben validar) |
| Escala 1.0 a 5.0 (historico Entrega 2, reemplazada en E3 por puntajes brutos) | `especificaciones/escala-canonica.md` | seccion 5 de `decisiones/decisiones-y-problemas.md` |
| Instrumento de estilos (Felder-Silverman) | `especificaciones/instrumento-estilos-aprendizaje.md` | - |
| Instrumento de personalidad | `especificaciones/instrumento-personalidad.md` | `../personalidad/README.md` (puntero) |
| Instrumento CHASIDE | `especificaciones/instrumento-chaside.md` | - |
| Recursos A/B/C de la semana (Entrega 2) | `especificaciones/materia-piloto-recursos.md` + `../poc_slm/recursos/semana_1.json` | - |
| Feedback loop (Entrega 2) | [especificaciones/feedback-loop.md](especificaciones/feedback-loop.md) | - |
| Destilacion y fine-tuning | `investigacion/propuesta-destilacion-slm.md` | tres notas preliminares en la misma carpeta |
| Decisiones tecnicas y transicion a Entrega 3 | `decisiones/decisiones-y-problemas.md` | - |
| Prompt de tutoria (Entrega 1) | `../prompts/system_guardrails.md` | - |
| Prompt de recomendacion semanal (Entrega 2) | `../prompts/system_prompt_recomendacion.md` | - |
| Ejemplos de recomendacion (E2-10) | `../prompts/escenarios/personalizacion_semanal.md` | - |

## Donde vive cada evidencia

La evidencia medida **no se edita**: se agrega una corrida nueva en la carpeta
que corresponda.

| Tipo de evidencia | Carpeta | Regla |
|---|---|---|
| Salidas de modelo de Entrega 1 | `../prompts/salidas-respaldo/` | no editar; plan B de la demo |
| Copias usadas en diapositivas | `presentacion/demo-qwen2.5-3b/` | copia de presentacion |
| Benchmark de rendimiento | `../benchmarks/resultados/<equipo>/` | una subcarpeta por maquina |
| Demo historica | `../poc_slm/evidencias/` | referencia, no se actualiza |

## Convenciones

- **Idioma:** espanol sin tildes ni caracteres especiales en documentos que
  escribimos nosotros. La evidencia transcrita se conserva tal cual.
- **Nombres:** minusculas, palabras separadas por guion (`sprint-5-prompt-y-feedback.md`).
  Las salidas de modelo conservan el nombre historico.
- **Estado:** cada sprint abre con `**Estado:**` (Pendiente, En curso, Completado).
- **Un tema, un documento:** si un contenido se repite, se deja en un solo lugar
  y el resto pasa a ser puntero.
- **Enlaces relativos:** siempre entre archivos del repo; nunca a rutas locales
  ni a carpetas que no existen.

## Validacion

```bash
python docs/validar-docs.py          # enlaces, indices, duplicados y ASCII
python docs/especificaciones/validar-perfiles.py
```

`validar-docs.py` devuelve codigo 1 si hay enlaces rotos o falta un H1; los
avisos (no-ASCII, docs sin enlace entrante, duplicados) se reportan sin cortar.
Con `--strict` los avisos tambien fallan.
