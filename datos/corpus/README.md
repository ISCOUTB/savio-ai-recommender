# datos/corpus - Corpus sintetico de entrenamiento (E3-06)

Aqui vive el corpus *ground truth* con el que se entrena el SLM de la Entrega 3.
Cada linea es un registro sintetico que mapea **puntajes brutos -> perfil
integrado de 4 secciones**.

**Guia de uso:** [guia de entrenamiento en Colab](../../docs/entregas/entrega-3-interpretacion-psicometrica/guia-entrenamiento-colab.md).
**Diseno de la matriz:** [matriz-corpus-e306.md](../../docs/especificaciones/matriz-corpus-e306.md).
**Generador:** [scripts/generar_corpus_e306.py](../../scripts/generar_corpus_e306.py).

## Corrida del maestro - 2026-11-07

Generamos las 150 interpretaciones con `openai/gpt-6.1-sol` dentro de la sesion
de OpenCode, en 15 lotes de 10, sin usar las llamadas comerciales del generador
ni un SLM local como maestro. Conservamos los puntajes del CSV sin modificaciones.
Redactamos cada lectura por perfil; insertamos de forma determinista los titulos,
los conteos originales y el aviso no clinico, sin generar conclusiones con plantillas.

- [corpus.jsonl](corpus.jsonl): 150 entradas con sus cuatro secciones interpretativas.
- [manifiesto_generacion.json](manifiesto_generacion.json): maestro real, metodo,
  hash, cobertura y split de 122 entrenamiento / 28 evaluacion; cero fallidos.
- [manifiesto.json](manifiesto.json): gate de privacidad ejecutado con resultado `ok`.

**Estado:** corpus candidato validado automaticamente, pendiente de acreditar la
aprobacion de la matriz y de revisar 15 registros entre los tres integrantes.
Las firmas permanecen vacias: la generacion por IA no cuenta como revision del equipo.
El entrenamiento definitivo requiere resolver estos pendientes.

Aplicamos las bandas de E3 de `baremos-psicometricos.md`, no las normalizaciones
historicas de E2. Usamos los nombres institucionales de CHASIDE: I corresponde a
Ensenanzas Tecnicas y E a Ciencias Experimentales. Los arquetipos `GAP` no prueban
contradicciones personales ni obligan a asociar un interes con un estilo de aprendizaje.
Estas bandas son convenciones del contrato, no baremos poblacionales ni evidencia
de validez clinica. El texto sintetico del maestro no es un dictamen profesional.

Verificamos ids completos y unicos, igualdad de entradas con el CSV y la matriz,
cuatro secciones por salida, aviso canonico al final, ASCII y hashes coincidentes.
La fidelidad semantica y la calidad psicometrica requieren revision humana;
el validador de privacidad no las certifica.

## Que se versiona y que no

| Archivo | Se versiona | Motivo |
|---|---|---|
| `corpus.jsonl` | Si | Solo registros sinteticos (`id` `SINT-###`, `origen: "sintetico"`) |
| `manifiesto.json` | Si | Hash SHA-256 del corpus, lo escribe el validador de privacidad |
| `manifiesto_generacion.json` | Si | Procedencia del corpus: semilla, modelo maestro, hash y conteos por arquetipo |
| `corpus_expansion.csv` | Si | Auditoria de los 150 perfiles, una fila por id |
| `prompts_maestro.jsonl` | Si | Un prompt versionado por registro (permite regenerar el ground truth) |
| `reparto/persona-*.md` | No | Intermedios de trabajo: prompts y respuestas pegadas a mano por cada integrante |
| `lotes/prompts-lote-*.jsonl` | No | Entradas por tanda para el maestro; se derivan de `prompts_maestro.jsonl` |
| `respuestas-lotes/secciones-lote-*.json` | No | Cuatro lecturas redactadas por el maestro por perfil, antes de insertar conteos y aviso |
| `respuestas-lotes/*.jsonl` | No | Lotes intermedios del maestro; se consolidan en `corpus.jsonl` |
| `respuestas.jsonl` | No | Se regenera con `compilar`; la fuente de verdad es `corpus.jsonl` |
| `fallidos.jsonl` | No | Respuestas rechazadas por el guardrail; se regeneran |
| `ejemplo_mini.jsonl` | Si | 8 registros de ejemplo para probar el pipeline completo |
| Cualquier archivo con datos reales | **No** | Ver [lineamientos de datos psicometricos](../../docs/entregas/entrega-3-interpretacion-psicometrica/lineamientos-datos-psicometricos.md) |

Los perfiles reales del equipo viven en `perfiles/reales/` (ignorado por Git) y
**nunca** se suben a Colab, a Hugging Face ni a ningun servicio externo.

## Contrato del registro

```json
{"id": "SINT-001", "origen": "sintetico", "chaside": {"...": "7 areas"},
 "ils": {"...": "8 polos, cada par suma 11"}, "personalidad": {"...": "8 polos 0-9"},
 "instruction": "...", "output": "## 1. ... hasta el aviso no clinico"}
```

Reglas completas y errores frecuentes: seccion 3 de la guia.

## Generacion sin API (reparto entre 3 integrantes)

Si no hay clave de API, el ground truth se produce a mano en Claude o ChatGPT web:

```bash
# 1. Genera los 150 prompts y los reparte 50/50/50 (no sobrescribe si ya existen)
python scripts/generar_corpus_e306.py repartir

# 2. Cada integrante diligencia datos/corpus/reparto/persona-N.md:
#    copia el prompt en el LLM maestro y pega la respuesta entre
#    <!-- RESPUESTA --> y <!-- FIN -->

# 3. Compila los tres Markdown en respuestas.jsonl
python scripts/generar_corpus_e306.py compilar

# 4. Ensambla el corpus y pasa el gate de privacidad
python scripts/generar_corpus_e306.py ensamblar --respuestas datos/corpus/respuestas.jsonl
python docs/especificaciones/validar-corpus-anonimizado.py --entrada datos/corpus/corpus.jsonl --manifiesto datos/corpus/manifiesto.json
```

`compilar` reporta los ids pendientes y no deja avanzar hasta tener las 150 respuestas.
`repartir --sobrescribir` borra las respuestas ya pegadas: usarlo solo para reiniciar
el reparto.

## Generacion con un LLM maestro dentro de OpenCode

Si el maestro se ejecuta como agente de OpenCode (por ejemplo
`openai/gpt-6.1-sol#max`), se trabaja por lotes de 10 para no truncar la salida:

```bash
# 1. Genera 15 archivos con 10 prompts cada uno
python scripts/generar_corpus_e306.py lotes

# 2. Para cada datos/corpus/lotes/prompts-lote-XX.jsonl, el maestro escribe
#    datos/corpus/respuestas-lotes/lote-XX.jsonl con {"id": "...", "output": "..."}

# 3. Consolida y registra la procedencia real
python scripts/generar_corpus_e306.py ensamblar --respuestas-dir datos/corpus/respuestas-lotes --maestro-proveedor openai --maestro-modelo gpt-6.1-sol
```

`manifiesto_generacion.json` guarda el proveedor y el modelo reales; no se declara
"manual" cuando el texto lo genero un modelo. El maestro debe ser un LLM de
frontera: no se usa el SLM local (`qwen2.5:*`) como maestro, porque E3-06 exige
un Teacher de mayor capacidad que el Student.

## Validacion obligatoria

Desde la raiz del repositorio:

```bash
python docs/especificaciones/validar-corpus-anonimizado.py --entrada datos/corpus/ejemplo_mini.jsonl
python docs/especificaciones/validar-corpus-anonimizado.py --entrada datos/corpus/corpus.jsonl --manifiesto datos/corpus/manifiesto.json
```

Si el validador devuelve codigo distinto de cero, el corpus **no se sube** a
ningun servicio externo ni se usa para entrenar.

## Tamano esperado

| Conjunto | Registros | Uso |
|---|---|---|
| `ejemplo_mini.jsonl` | 8 | Prueba de humo del notebook (1 epoca) |
| `corpus.jsonl` | 150 minimo | Entrenamiento real: 122 train / 28 eval con la semilla 42 |

El corte 80/20 es determinista (`sha256(id) % 5 == 0`), asi que el mismo corpus
siempre produce el mismo split y no hay fuga entre entrenamiento y evaluacion.
El conteo exacto depende de los ids: con `SINT-001` a `SINT-150` da 28 de
evaluacion (18.7%), no 30. No se ajusta a mano para forzar el porcentaje.
