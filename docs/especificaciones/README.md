# docs/especificaciones - Contratos de datos e instrumentos

Aqui viven los **contratos** del subsistema: los schemas JSON que valida el
codigo y las notas tecnicas de los tres instrumentos psicopedagogicos.

## Contratos de datos (fuente de verdad)

| Archivo | Describe | Valida con | Issue |
|---|---|---|---|
| [perfil-bruto-psicometrico.schema.json](perfil-bruto-psicometrico.schema.json) | **Vigente E3.** Perfil con puntajes brutos nativos (`0-14`, `0-11`, `0-9`), sin indices compuestos | [validar-perfiles-brutos.py](validar-perfiles-brutos.py) | E3-04 |
| [perfil-estudiante.schema.json](perfil-estudiante.schema.json) | Historico E2. Perfil consolidado en escala 1.0-5.0 (se conserva como evidencia, no se edita) | [validar-perfiles.py](validar-perfiles.py) | E2-07 |
| [recurso-semanal.schema.json](recurso-semanal.schema.json) | Un recurso semanal (A, B o C) de la materia piloto | `prompt_builder.py` y la validacion de E2-08 | E2-08 |
| [feedback.schema.json](feedback.schema.json) | Feedback del estudiante sobre una recomendacion | pendiente (E2-11) | E2-11 |

## Instrumentos y escalas (notas tecnicas)

| Archivo | Que documenta |
|---|---|
| [baremos-psicometricos.md](baremos-psicometricos.md) | **Vigente E3.** Lectura de los puntajes brutos: bandas por instrumento, diferencial oficial y lo que queda prohibido |
| [matriz-corpus-e306.md](matriz-corpus-e306.md) | **Vigente E3.** Diseno de cobertura del corpus sintetico de E3-06: 150 perfiles, 7 arquetipos, rangos y criterios de revision |
| [escala-canonica.md](escala-canonica.md) | Escala unificada 1.0 a 5.0 (historica E2, reemplazada por puntajes brutos en E3): formulas, valores alcanzables y semantica de 3.0 |
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
| [validar-perfiles-brutos.py](validar-perfiles-brutos.py) | Valida perfiles con puntajes brutos (E3-04): rangos, invariantes, diferencial y rechazo del formato 1.0-5.0 |
| [contrato_bruto.py](contrato_bruto.py) | Fuente unica de rangos e invariantes que comparten el corpus (E3-06) y los perfiles (E3-04) |
| [test_validar_perfiles_brutos.py](test_validar_perfiles_brutos.py) | Pruebas del contrato bruto, incluidos los casos que deben fallar (E3-04) |
| [validar-perfiles.py](validar-perfiles.py) | Valida los perfiles historicos de Entrega 2 contra el schema 1.0-5.0 |
| [generar-perfil.py](generar-perfil.py) | Genera un perfil real desde las respuestas de Moodle (E2-07; E3-05 le agrega la salida en bruto) |
| [validar-corpus-anonimizado.py](validar-corpus-anonimizado.py) | Verifica que el corpus ground truth sea sintetico, sin PII y con rangos validos antes de subirlo a Hugging Face (E3-03) |
| [../../scripts/generar_corpus_e306.py](../../scripts/generar_corpus_e306.py) | Genera los 150 perfiles de la matriz y los prompts del LLM maestro (E3-06) |
| [test_validar_corpus_anonimizado.py](test_validar_corpus_anonimizado.py) | Pruebas del validador de privacidad del corpus (E3-03) |

## Validacion

Desde la raiz del repositorio:

```bash
python docs/especificaciones/test_validar_perfiles_brutos.py
python docs/especificaciones/validar-perfiles-brutos.py
python docs/especificaciones/test_validar_corpus_anonimizado.py
python docs/especificaciones/validar-corpus-anonimizado.py --entrada datos/corpus/corpus.jsonl
python docs/especificaciones/validar-perfiles.py
```

Regla: si cambia un schema, se actualizan los ejemplos de `perfiles/` y se corre
el validador antes de cerrar el issue.
