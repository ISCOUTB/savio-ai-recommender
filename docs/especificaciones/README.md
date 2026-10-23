# docs/especificaciones - Contratos de datos e instrumentos

Aqui viven los **contratos** del subsistema: los schemas JSON que valida el
codigo y las notas tecnicas de los tres instrumentos psicopedagogicos.

## Contratos de datos (fuente de verdad)

| Archivo | Describe | Valida con | Issue |
|---|---|---|---|
| [perfil-estudiante.schema.json](perfil-estudiante.schema.json) | Perfil consolidado del estudiante (estilos, personalidad, CHASIDE) | [validar-perfiles.py](validar-perfiles.py) | E2-07 |
| [recurso-semanal.schema.json](recurso-semanal.schema.json) | Un recurso semanal (A, B o C) de la materia piloto | `prompt_builder.py` y la validacion de E2-08 | E2-08 |
| [feedback.schema.json](feedback.schema.json) | Feedback del estudiante sobre una recomendacion | pendiente (E2-11) | E2-11 |

## Instrumentos y escalas (notas tecnicas)

| Archivo | Que documenta |
|---|---|
| [escala-canonica.md](escala-canonica.md) | Escala unificada 1.0 a 5.0: formulas, valores alcanzables y semantica de 3.0 |
| [instrumento-estilos-aprendizaje.md](instrumento-estilos-aprendizaje.md) | Bloque Moodle de estilos, traduccion a Felder-Silverman |
| [instrumento-personalidad.md](instrumento-personalidad.md) | Bloque Moodle de personalidad, rasgos y traduccion al perfil |
| [instrumento-chaside.md](instrumento-chaside.md) | Areas vocacionales CHASIDE y uso como analogias |

## Materia piloto

| Archivo | Que documenta |
|---|---|
| [materia-piloto-recursos.md](materia-piloto-recursos.md) | Curso piloto, semana 1, recursos A/B/C, matriz de contraste e hipotesis de recomendacion (E2-08) |

## Herramientas

| Archivo | Uso |
|---|---|
| [validar-perfiles.py](validar-perfiles.py) | Valida todos los perfiles de `perfiles/` contra el schema y las reglas de escala |
| [generar-perfil.py](generar-perfil.py) | Genera un perfil real desde las respuestas de Moodle (E2-07) |

## Validacion

Desde la raiz del repositorio:

```bash
python docs/especificaciones/validar-perfiles.py
```

Regla: si cambia un schema, se actualizan los ejemplos de `perfiles/` y se corre
el validador antes de cerrar el issue.
