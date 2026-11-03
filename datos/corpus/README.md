# datos/corpus - Corpus sintetico de entrenamiento (E3-06)

Aqui vive el corpus *ground truth* con el que se entrena el SLM de la Entrega 3.
Cada linea es un registro sintetico que mapea **puntajes brutos -> perfil
integrado de 4 secciones**.

**Guia de uso:** [guia de entrenamiento en Colab](../../docs/entregas/entrega-3-interpretacion-psicometrica/guia-entrenamiento-colab.md).

## Que se versiona y que no

| Archivo | Se versiona | Motivo |
|---|---|---|
| `corpus.jsonl` | Si | Solo registros sinteticos (`id` `SINT-###`, `origen: "sintetico"`) |
| `manifiesto.json` | Si | Hash SHA-256 del corpus, evidencia de E3-06 |
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
| `corpus.jsonl` | 150 minimo | Entrenamiento real: 120 train / 30 eval |

El corte 80/20 es determinista (`sha256(id) % 5 == 0`), asi que el mismo corpus
siempre produce el mismo split y no hay fuga entre entrenamiento y evaluacion.
