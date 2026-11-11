---
name: Corpus Psicometrico
description: Construir, validar y particionar el corpus ground truth de E3-06 con puntajes brutos de CHASIDE, Felder-Silverman y Personalidad. Usar antes de generar, revisar, dividir o entrenar con datos/corpus.
license: Uso interno del proyecto Savio AI Recommender
---

# Corpus Psicometrico (E3-06)

Corpus sintetico que mapea **puntajes brutos -> perfil integrado de 4 secciones**.
Fuente de verdad: `datos/corpus/corpus.jsonl` (150 registros).

## Regla 0: las escalas no se tocan

| Instrumento | Escala nativa | Conteo |
|---|---|---|
| CHASIDE | `0-14` por area | 7 areas |
| Felder-Silverman (ILS) | `0-11` por polo | 4 dimensiones bipolares (8 polos) |
| Personalidad | `0-9` por polo | 8 polos |

Prohibido normalizar, reescalar, invertir o inventar valores. El motor recibe
las puntuaciones originales. Si un registro no cumple el rango, se rechaza; no
se corrige a mano.

## Fuentes canonicas

- Contrato: `docs/especificaciones/perfil-bruto-psicometrico.schema.json`
- Reglas compartidas: `docs/especificaciones/contrato_bruto.py`
- Bandas por instrumento: `docs/especificaciones/baremos-psicometricos.md`
- Matriz del corpus: `docs/especificaciones/matriz-corpus-e306.md`
- Guia de entrenamiento: `docs/entregas/entrega-3-interpretacion-psicometrica/guia-entrenamiento-colab.md`

## Contrato del registro

```json
{"id": "SINT-001", "origen": "sintetico", "chaside": {"...": "7 areas"},
 "ils": {"...": "8 polos, cada par suma 11"}, "personalidad": {"...": "8 polos 0-9"},
 "instruction": "...", "output": "## 1. ... hasta el aviso no clinico"}
```

- `id` unico con prefijo `SINT-###`.
- `origen` siempre `sintetico`.
- `output` con las 4 secciones en orden y el aviso no clinico al final.
- ASCII, sin nombres ni identificadores de personas.

## Pipeline sin API

```bash
python scripts/generar_corpus_e306.py repartir
python scripts/generar_corpus_e306.py compilar
python scripts/generar_corpus_e306.py ensamblar --respuestas datos/corpus/respuestas.jsonl
```

Con API: `python scripts/generar_corpus_e306.py generar --proveedor <p> --modelo <m>`.
Los intermedios (`reparto/`, `lotes/`, `respuestas-lotes/`) estan ignorados por Git
y no son fuente de verdad.

## Gate de privacidad (obligatorio)

```bash
python docs/especificaciones/validar-corpus-anonimizado.py --entrada datos/corpus/corpus.jsonl --manifiesto datos/corpus/manifiesto.json
```

Sin `RESULTADO: OK` el corpus no se usa ni se sube a Hugging Face. El validador
escribe el SHA-256 en `manifiesto.json`.

## Split

- `sha256(id) % 5 == 0` -> evaluacion; el resto, entrenamiento.
- Semilla de generacion 42. Resultado esperado: 122 entrenamiento / 28 evaluacion.
- El split es determinista y no se ajusta a mano.
- Los 3 perfiles reales no entran al corpus: se usan en E3-09 y E3-10.

## Estado real del corpus

`datos/corpus/README.md` declara el corpus como **candidato validado
automaticamente**, pendiente de:

1. aprobacion de la matriz por el equipo;
2. revision de 15 registros entre los tres integrantes (firmas vacias hoy).

No declarar E3-06 cerrado ni entrenar la version definitiva hasta cumplir ambos.

## Prohibiciones

- `perfiles/reales/` y `datos/reales/` nunca salen a Claude, ChatGPT, Colab ni Hugging Face.
- Nada de diagnosticos, etiquetas MBTI ni lenguaje patologizante.
- No editar `corpus.jsonl` a mano: se regenera y se vuelve a validar.
- No cambiar cifras de `benchmarks/` ni de `prompts/salidas-respaldo/`.

## Checklist antes de entrenar

- [ ] `corpus.jsonl` con 150 lineas e ids unicos.
- [ ] Conteos iguales a `corpus_expansion.csv`.
- [ ] `RESULTADO: OK` del validador de privacidad.
- [ ] Hash del manifiesto anotado en el issue y en la dataset card.
- [ ] Split 122/28 verificado.
- [ ] Revision humana y aprobacion de la matriz registradas.
