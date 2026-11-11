# Revision del corpus E3-06: matriz y 15 registros (control de calidad)

Constancia del paso 6 de E3-06 ([#43](https://github.com/ISCOUTB/savio-ai-recommender/issues/43)):
los tres integrantes revisan 5 registros cada uno (15 = 10 % del corpus) y el
par aprueba la [matriz de cobertura](../../especificaciones/matriz-corpus-e306.md).

- **Corpus revisado:** `datos/corpus/corpus.jsonl`, SHA-256
  `c74e2e6252e06047bdc8067d7b784c182ca7f396657c2947bc2777e9f9aaae1c` (el mismo
  de `manifiesto_generacion.json` y del entrenamiento de E3-08).
- **Criterio:** bandas de [baremos-psicometricos.md](../../especificaciones/baremos-psicometricos.md)
  (ILS marcada con diferencial 9 u 11; personalidad con diferencia de 4 o mas;
  CHASIDE alta 11-14, media 6-10, baja 0-5), guardrail etico y fidelidad a los
  puntajes de entrada.

---

## 1. Verificacion automatica de la matriz (apoyo para la aprobacion del par)

| Chequeo | Resultado |
|---|---|
| Registros por arquetipo frente a la matriz (21 + 20 + 20 + 24 + 20 + 20 + 25) | Coinciden: DOM-CHA 21, DOM-ILS 20, DOM-PER 20, GAP-CHA-ILS 24, GAP-PER-ILS 20, FLAT 20, EDGE 25 = 150 |
| `corpus_expansion.csv` frente a los puntajes de `corpus.jsonl` | 0 celdas distintas en 150 filas x 37 puntajes |
| Hash del corpus frente al manifiesto | Coincide |
| Gate de privacidad E3-03 (`manifiesto.json`) | `RESULTADO: OK` (2026-11-07) |
| Ground truth frente a sus propios puntajes y bandas (`evaluar-fidelidad.py`) | 150/150 sin alucinaciones numericas; 4 secciones y aviso en 150/150; fidelidad media 99.8 % |

La aprobacion de la matriz le corresponde a **Persona 1** (par revisor, seccion 7
de la matriz) y se registra en el issue #43. Este documento no la sustituye.

---

## 2. Seleccion de los 15 registros

Seleccion determinista y estratificada: dentro de cada arquetipo se ordenan los
ids por `sha256("revision-e306:" + id)` y se toman en orden. Cada integrante
cubre arquetipos distintos y uno de casos borde.

| Integrante | Registros (arquetipo) |
|---|---|
| Persona 1 | SINT-021 (DOM-CHA), SINT-016 (DOM-CHA), SINT-025 (DOM-ILS), SINT-027 (DOM-ILS), SINT-140 (EDGE) |
| Persona 2 | SINT-049 (DOM-PER), SINT-045 (DOM-PER), SINT-066 (GAP-CHA-ILS), SINT-070 (GAP-CHA-ILS), SINT-141 (EDGE) |
| Persona 3 | SINT-091 (GAP-PER-ILS), SINT-104 (GAP-PER-ILS), SINT-120 (FLAT), SINT-117 (FLAT), SINT-130 (EDGE) |

---

## 3. Revision de Persona 2 (2026-11-11)

Revision asistida con IA (Claude Code) contra las bandas del baremo, con
dictamen final de Persona 2.

| Registro | Puntos verificados | Dictamen |
|---|---|---|
| SINT-049 (DOM-PER) | Perceptive 8 / judging 1 (dif. 7) se lee como preferencia; empates 6/6 y 1/1 equilibrados; ILS reflexivo 8/3 (dif. 5) sin preferencia clara; S = 9 mayor total en banda media; A con interes 7 y aptitud 0 matizado | Aprobado |
| SINT-045 (DOM-PER) | Judging 7 / perceptive 3 en el umbral exacto (dif. 4) se lee como preferencia; resto equilibrado; H = 8 mayor total en banda media; brechas de interes sin aptitud en H y D matizadas; sintesis evita convertir la estructura conductual en preferencia secuencial | Aprobado |
| SINT-066 (GAP-CHA-ILS) | Activo 11/0 marcada; visual y global con dif. 7 no se exageran; personalidad equilibrada sin confundir extraversion con procesamiento activo; C = 11 afinidad alta | Aprobado |
| SINT-070 (GAP-CHA-ILS) | Sensitivo 10/1 marcada; reflexivo, visual y secuencial sin preferencia clara; empate 0/0 de organizacion; H = 12 afinidad alta; E con aptitud 4 e interes 0 no se eleva | Aprobado |
| SINT-141 (EDGE) | Todos los ejes ILS por debajo de 9; empate 8/8 en energia; I = 10 en el borde del corte no se eleva a afinidad alta | Aprobado |

Los 37 puntajes de cada registro coinciden con la entrada, las cuatro secciones
estan en orden y el aviso no clinico aparece al final. No hay tipos MBTI,
frases clinicas ni escalas distintas a las nativas.

**Observacion (no bloquea):** el texto llama "percepcion" al eje
sensing/intuition, termino que se presta a confusion con el polo `perceptive`.
Conviene tenerlo en cuenta si se regenera el corpus.

---

## 4. Estado del control de calidad

| Paso | Responsable | Estado |
|---|---|---|
| Aprobar la matriz | Persona 1 | Pendiente (issue #43) |
| Revisar 5 registros | Persona 1 | Pendiente |
| Revisar 5 registros | Persona 2 | Hecho el 2026-11-11: 5/5 aprobados |
| Revisar 5 registros | Persona 3 | Pendiente |
| Mover #43 a revision con hash y split | Persona 3 | Pendiente de las dos revisiones restantes |

Cada integrante completa su fila de la seccion 3 con el mismo formato y
agrega su firma en `firmas_calidad` de `datos/corpus/manifiesto_generacion.json`.
