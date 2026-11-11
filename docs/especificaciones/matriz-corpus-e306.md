# Matriz de cobertura del corpus E3-06 (150 perfiles sinteticos)

- **Issue:** E3-06 (#43)
- **Contrato de entrada:** [perfil-bruto-psicometrico.schema.json](perfil-bruto-psicometrico.schema.json)
- **Reglas de rangos:** [contrato_bruto.py](contrato_bruto.py)
- **Baremos:** [baremos-psicometricos.md](baremos-psicometricos.md)
- **Generador:** [scripts/generar_corpus_e306.py](../../scripts/generar_corpus_e306.py)
- **Validador:** [validar-corpus-anonimizado.py](validar-corpus-anonimizado.py)
- **Semilla:** 42 (fija)
- **Split:** `sha256(id) % 5 == 0` -> evaluacion (~19%: 28 de 150 con la semilla 42)

**Estado:** Documentado. La matriz se revisa por par antes de generar el corpus.

---

## 1. Reglas que la matriz no puede romper

Tomadas de `contrato_bruto.py`, que es la fuente unica de verdad:

| Instrumento | Estructura | Invariante |
|---|---|---|
| CHASIDE | 7 areas (`C, H, A, S, I, D, E`), cada una con `interes` (0-10), `aptitud` (0-4) y `total` (0-14) | `total = interes + aptitud` |
| Felder-Silverman | 8 polos (0-11), 4 pares bipolares | Cada par suma exactamente 11; el diferencial es impar entre -11 y 11 |
| Personalidad | 8 polos (0-9), 4 ejes | Sin suma fija; se reportan los 8 conteos |
| Identidad | `id` con patron `SINT-###` y `origen: "sintetico"` | Unico por registro |

Bandas usadas para construir los arquetipos:

| Instrumento | Banda | Criterio |
|---|---|---|
| CHASIDE | Alta / media / baja | `total` 11-14 / 6-10 / 0-5 |
| Felder-Silverman | Preferencia marcada / sin preferencia clara | `|diferencial|` 9 u 11 / 1, 3, 5 o 7 |
| Personalidad | Preferencia / equilibrado | Diferencia entre polos >= 4 / <= 3 |

La matriz **no** usa indices compuestos ni etiquetas de tipo de 4 letras.

---

## 2. Arquetipos (150 registros)

| Arquetipo | Codigo | Registros | Que aisla |
|---|---|---|---|
| Dominante CHASIDE | `DOM-CHA` | 21 | Una sola area con afinidad alta |
| Dominante Felder-Silverman | `DOM-ILS` | 20 | Un solo polo con preferencia marcada |
| Dominante Personalidad | `DOM-PER` | 20 | Un solo eje con preferencia |
| Brecha CHASIDE-Felder | `GAP-CHA-ILS` | 24 | Interes alto contra estilo de aprendizaje opuesto |
| Brecha Personalidad-Felder | `GAP-PER-ILS` | 20 | Rasgo fuerte contra estilo opuesto |
| Perfil plano | `FLAT` | 20 | Ausencia de senales fuertes |
| Casos borde | `EDGE` | 25 | Limites exactos de banda |
| **Total** | | **150** | |

El reparto es fijo: cambiar un conteo exige actualizar esta tabla y volver a
correr el generador. Los ids se asignan en este mismo orden (`SINT-001` a
`SINT-150`), asi que el arquetipo de cada id es reproducible.

---

## 3. Definicion por arquetipo

### 3.1 DOM-CHA - Dominante CHASIDE (21)

| Campo | Regla |
|---|---|
| Area dominante | Rota entre las 7 areas: 3 registros por area |
| `total` del area dominante | 11, 12 o 14 (rota por area) |
| `total` de las otras 6 areas | Estratificado en 2-9 |
| Felder-Silverman | Diferencial en 1, 3 o 5 en los 4 pares (sin preferencia marcada) |
| Personalidad | Los 4 ejes con diferencia <= 3 |

**Proposito:** el modelo aprende a sostener una afinidad vocacional alta sin
ruido de estilos ni rasgos extremos.

### 3.2 DOM-ILS - Dominante Felder-Silverman (20)

| Campo | Regla |
|---|---|
| Dimension dominante | Rota entre los 4 pares: 5 registros por par |
| Diferencial dominante | 9 u 11, con signo alternado |
| Otros 3 pares | Diferencial en 1, 3, 5 o 7 |
| CHASIDE | `total` estratificado en 3-10 (sin area alta) |
| Personalidad | Los 4 ejes con diferencia <= 3 |

**Proposito:** aisla un polo de aprendizaje marcado y evita que CHASIDE o la
personalidad expliquen la interpretacion.

### 3.3 DOM-PER - Dominante Personalidad (20)

| Campo | Regla |
|---|---|
| Eje dominante | Rota entre los 4 ejes: 5 registros por eje |
| Preferencia dominante | Diferencia >= 4, con el polo preferido en 6-9 y el otro en 0-(preferido-4) |
| Otros 3 ejes | Diferencia <= 3 |
| CHASIDE | `total` estratificado en 2-9 |
| Felder-Silverman | Diferencial en 1, 3 o 5 |

**Proposito:** prueba la lectura conductual cuando el unico rasgo fuerte es de
personalidad.

### 3.4 GAP-CHA-ILS - Brecha CHASIDE-Felder (24)

Seis tensiones, 4 registros cada una. La tension es entre un interes alto y el
estilo de aprendizaje que suele asociarse a esa area:

| Area alta | Estilo marcado | Lectura de la tension |
|---|---|---|
| A (artistica) | `secuencial` | Creacion frente a avance paso a paso |
| I (ingenieria) | `verbal` | Trabajo tecnico frente a canal verbal |
| H (humanidades) | `sensitivo` | Contenido abstracto frente a lo concreto |
| S (salud) | `global` | Precision frente a vision de conjunto |
| C (administrativa) | `activo` | Registro y detalle frente a accion |
| E (educacion) | `reflexivo` | Interaccion frente a introspeccion |

| Campo | Regla |
|---|---|
| Area de la tension | `total` 11-14 |
| Otras 6 areas | `total` en 2-9 |
| Dimension marcada | Diferencial 9 u 11 hacia el polo de la tabla |
| Otras 3 dimensiones | Diferencial en 1, 3, 5 o 7 |
| Personalidad | Diferencia <= 3 en los 4 ejes |

### 3.5 GAP-PER-ILS - Brecha Personalidad-Felder (20)

Cuatro tensiones, 5 registros cada una:

| Eje de personalidad | Preferencia | Estilo marcado |
|---|---|---|
| Energia | `extraversion` | `reflexivo` |
| Energia | `introversion` | `activo` |
| Percepcion | `sensing` | `intuitivo` |
| Percepcion | `intuition` | `sensitivo` |

| Campo | Regla |
|---|---|
| Eje de la tension | Diferencia >= 4 hacia el polo de la tabla |
| Dimension marcada | Diferencial 9 u 11 hacia el polo de la tabla |
| Otros ejes y dimensiones | Diferencia <= 3 / diferencial en 1, 3 o 5 |
| CHASIDE | `total` estratificado en 3-9 |

### 3.6 FLAT - Perfil plano (20)

| Campo | Regla |
|---|---|
| CHASIDE | Los 7 totales estratificados en 6-10 |
| Felder-Silverman | Diferencial en 1, 3 o 5 en los 4 pares |
| Personalidad | Diferencia <= 2 en los 4 ejes |

**Proposito:** caso sin senales fuertes. Verifica que el modelo no invente
dominancias ni etiquetas.

### 3.7 EDGE - Casos borde (25)

Cinco familias, 5 registros cada una (3 en el limite inferior, 2 en el superior):

| Familia | Limite inferior | Limite superior |
|---|---|---|
| CHASIDE baja/media | `total` 5 | `total` 6 |
| CHASIDE media/alta | `total` 10 | `total` 11 |
| Felder sin preferencia/marcada | `|diferencial|` 7 | `|diferencial|` 9 |
| Felder reparto extremo | 10 / 1 | 11 / 0 |
| Personalidad equilibrada/preferencia | Diferencia 3 | Diferencia 4 |

El resto de dimensiones queda en rango medio para que el borde sea el unico
factor que cambia.

---

## 4. Algoritmo de muestreo

1. **Semilla fija por arquetipo:** `random.Random(f"{semilla}:{codigo}")`. Agregar
   registros a un arquetipo no altera los otros.
2. **Muestreo estratificado por campo:** para `n` registros y un rango
   `[minimo, maximo]`, se divide el rango en `n` estratos, se toma un valor
   entero por estrato y se permuta el orden. Es la version 1-D del *Latin
   Hypercube Sampling*, suficiente porque los campos son independientes dentro
   de cada arquetipo.
3. **Invariantes por construccion:**
   - CHASIDE: se sortea `total` y luego `interes` dentro de
     `[max(0, total-4), min(10, total)]`; `aptitud` es el resto.
   - Felder: se sortea el polo izquierdo; el derecho es `11 - izquierdo`.
   - Personalidad: se sortean los dos polos del eje respetando la diferencia
     exigida por el arquetipo.
4. **Validacion inmediata:** cada perfil pasa por
   `contrato_bruto.validar_perfil_bruto`. Si un solo perfil falla, el generador
   aborta y no escribe nada.
5. **Ids:** `SINT-001` a `SINT-150` en el orden de la tabla de arquetipos.

---

## 5. Prompt maestro y formato de salida

El ground truth lo redacta un LLM maestro (Claude o ChatGPT) con un prompt
versionado (`v1.0`) que incluye los puntajes exactos, las bandas y las
prohibiciones. La version vive en el generador y se cita en el manifiesto.

Formato obligatorio de `output`:

```text
## 1. Estilos de aprendizaje
## 2. Rasgos de personalidad
## 3. Perfil vocacional
## 4. Sintesis integrada

<AVISO_NO_CLINICO>
```

Reglas del prompt:

1. Citar los puntajes recibidos; no inventar escalas ni recalcular.
2. Aplicar las bandas de la seccion 1.
3. No usar etiquetas de tipo de 4 letras.
4. No emitir diagnosticos, ni mencionar trastornos, medicacion o tratamiento.
5. No recomendar carreras concretas; describir areas y entornos.
6. Redaccion descriptiva y graduada ("la inclinacion se inclina hacia..."), no
   etiquetas ("eres visual").
7. Cerrar con el aviso no clinico canonico de `poc_slm/guardrail_etico.py`.

El generador valida las 4 secciones en orden y el aviso antes de aceptar una
respuesta; si falla, reintenta y, si sigue fallando, la deja en `fallidos.jsonl`.

---

## 6. Validacion y gate

```bash
# 1. Matriz + prompts (sin red, no requiere API)
python scripts/generar_corpus_e306.py matriz

# 2. Generacion del ground truth (requiere clave del proveedor)
python scripts/generar_corpus_e306.py generar --proveedor claude --modelo <modelo>

# 3. O ensamblaje de respuestas hechas a mano
python scripts/generar_corpus_e306.py ensamblar --respuestas datos/corpus/respuestas.jsonl

# 4. Gate de privacidad (obligatorio, E3-03)
python docs/especificaciones/validar-corpus-anonimizado.py \
  --entrada datos/corpus/corpus.jsonl \
  --manifiesto datos/corpus/manifiesto.json

# 5. Split determinista
python -c "import hashlib,json;r=[json.loads(l) for l in open('datos/corpus/corpus.jsonl',encoding='utf-8')];e=[x for x in r if int(hashlib.sha256(x['id'].encode()).hexdigest(),16)%5==0];print(len(r),'total,',len(e),'eval')"
```

El manifiesto de privacidad (`manifiesto.json`) lo escribe el validador. El
generador escribe aparte `manifiesto_generacion.json` con la procedencia
(semilla, modelo, hash y conteos).

---

## 7. Reparto de trabajo

| Actividad | Responsable | Entregable |
|---|---|---|
| Revisar y aprobar esta matriz | Persona 1 (par) | Aprobacion registrada en el issue #43 |
| Mantener el generador | Persona 3 | `scripts/generar_corpus_e306.py` |
| Ejecutar la generacion | Persona 2 | `corpus.jsonl` + `manifiesto_generacion.json` |
| Correr el gate de privacidad | Persona 1 | Salida `RESULTADO: OK` en `manifiesto.json` |
| Revisar el 10% (15 registros) | Los 3, 5 cada uno | Firma en `manifiesto_generacion.json` |
| Mover el issue a revision | Persona 3 | Issue #43 actualizado |

E3-05 (perfiles reales) **no bloquea** este corpus: los 150 registros son
sinteticos. Solo hace falta para la validacion cualitativa posterior.

---

## 8. Criterios de aceptacion

- [ ] `datos/corpus/corpus.jsonl` con exactamente 150 lineas JSONL.
- [ ] Ids `SINT-001` a `SINT-150`, unicos, sin huecos.
- [ ] Los 150 perfiles pasan `contrato_bruto.validar_perfil_bruto`.
- [ ] Cada `output` tiene las 4 secciones en orden y el aviso no clinico.
- [ ] `validar-corpus-anonimizado.py` devuelve `RESULTADO: OK` y genera `manifiesto.json`.
- [ ] Split por hash: 122 entrenamiento / 28 evaluacion con ids `SINT-001` a `SINT-150` (18.7%; el conteo es consecuencia del hash, no se ajusta a mano).
- [ ] `manifiesto_generacion.json` declara semilla, modelo, version del prompt y hash del corpus.
- [ ] El 10% (15 registros) quedo revisado por los 3 integrantes.
- [ ] La cobertura de evaluacion por arquetipo quedo reportada (si un arquetipo queda en 0, se documenta como limitacion).

---

## 9. Riesgos

| Riesgo | Mitigacion |
|---|---|
| El LLM maestro altera puntajes o inventa escalas | Prompt con los valores exactos + revision del 10% |
| Respuestas incompletas o sin aviso | Validacion automatica de secciones y guardrail, con reintento |
| Cuota de API agotada | Modo `ensamblar` con respuestas hechas a mano; dividir en 3 bloques |
| Un arquetipo queda sin registros de evaluacion | Se reporta en el manifiesto; el split no se manipula a mano |
| Se filtra un dato real al corpus | El corpus se construye solo con numeros; el gate de E3-03 lo verifica |

---

## 10. Uso del generador

```bash
python scripts/generar_corpus_e306.py matriz --limite 10   # prueba rapida
python scripts/generar_corpus_e306.py matriz               # 150 perfiles + prompts
python scripts/generar_corpus_e306.py --help
```

`matriz` no llama a ningun servicio externo: solo escribe la expansion y los
prompts. Asi se puede revisar la cobertura antes de gastar cuota de API.
