# Baremos psicometricos del contrato de puntajes brutos (E3-04)

- **Issue:** E3-04 (#50)
- **Contrato:** [perfil-bruto-psicometrico.schema.json](perfil-bruto-psicometrico.schema.json)
- **Validador:** [validar-perfiles-brutos.py](validar-perfiles-brutos.py)
- **Reglas compartidas:** [contrato_bruto.py](contrato_bruto.py)
- **Reemplaza a:** [escala-canonica.md](escala-canonica.md) (historica E2)

**Estado:** Documentado

---

## 1. Alcance y regla base

Este documento fija **como se leen los puntajes brutos** de los tres instrumentos
institucionales. No define una escala nueva ni normaliza nada: cada instrumento
se interpreta con sus propios conteos, tal como los entrega el bloque de Moodle.

Las tres reglas que hereda todo el subsistema:

1. **Puntaje bruto siempre entero.** Un valor decimal es senal de reescalamiento
   (1.0-5.0) y el validador lo rechaza.
2. **Sin indices compuestos.** Solo se interpretan los polos y areas que el
   instrumento mide de forma directa.
3. **Sin diagnostico.** Un puntaje describe una preferencia o un interes; no
   etiqueta al estudiante ni predice su desempeno.

El contrato ejecutable vive en [contrato_bruto.py](contrato_bruto.py): rangos,
invariantes y deteccion del formato antiguo. El schema JSON es la version
declarativa; el validador es la verificacion que corre en cada cierre.

---

## 2. Estilos de aprendizaje (Index of Learning Styles)

### 2.1 Estructura

44 items dicotomicos, 11 por cada dimension bipolar. Cada par suma
**exactamente 11**, y el diferencial es la resta entre polos:

```text
diferencial = puntaje_polo_izquierdo - puntaje_polo_derecho
```

El resultado es un entero **impar entre -11 y 11**. Un diferencial par o un par
que no suma 11 indica datos corruptos o un instrumento alterado.

| Dimension | Polo izquierdo (+) | Polo derecho (-) | Suma |
| :--- | :--- | :--- | :---: |
| `activo_reflexivo` | activo | reflexivo | 11 |
| `sensitivo_intuitivo` | sensitivo | intuitivo | 11 |
| `visual_verbal` | visual | verbal | 11 |
| `secuencial_global` | secuencial | global | 11 |

### 2.2 Bandas

Se conservan las bandas que el equipo ya uso en Entrega 2
([instrumento-estilos-aprendizaje.md](instrumento-estilos-aprendizaje.md),
seccion 2.4), ahora expresadas en el diferencial bruto:

| Banda | Diferencial (valor absoluto) | Lectura |
| :--- | :---: | :--- |
| Preferencia marcada | 9 u 11 | El polo con mayor conteo se reporta como preferencia clara |
| Sin preferencia clara | 1, 3, 5 o 7 | Se describen ambos polos; no se afirma una preferencia |

Un diferencial de 0 es imposible en un test completo; si aparece, el registro
esta incompleto y el validador lo rechaza por la regla de suma 11.

### 2.3 Regla de redaccion

El perfil nunca enuncia "eres visual". La redaccion correcta es descriptiva y
graduada: "en el eje visual-verbal el conteo se inclina hacia el polo visual con
un diferencial de 7". Con diferencial 9 u 11 la preferencia se puede mencionar
como marcada; con 1 a 7 se presentan las dos vertientes.

---

## 3. Personalidad (cuestionario tipo MBTI)

### 3.1 Estructura

72 items dicotomicos, 9 por polo. Cada polo produce un entero **0 a 9** y no hay
suma fija entre polos: los 8 conteos se reportan completos.

| Eje | Polos |
| :--- | :--- |
| Energia | `extraversion`, `introversion` |
| Percepcion | `sensing`, `intuition` |
| Decision | `thinking`, `feeling` |
| Estilo de vida | `judging`, `perceptive` |

### 3.2 Bandas

Se conserva el criterio de Entrega 2
([instrumento-personalidad.md](instrumento-personalidad.md), seccion 3.2): con
solo 9 items por polo, una diferencia menor a 4 no se considera confiable.

| Banda | Diferencia entre polos | Lectura |
| :--- | :---: | :--- |
| Preferencia | 4 o mas | Se puede mencionar el polo con mayor conteo |
| Equilibrado | 3 o menos | Se describen ambos polos; no se personaliza |

### 3.3 Por que no existe `autonomia`

`autonomia` era un indice derivado que combinaba los ejes S/N y T/F. Ningun item
del instrumento mide autonomia de forma directa, y el propio equipo la habia
marcado como "indice inferido, no validado psicometricamente". La directriz 2 de
Entrega 3 prohibe indices compuestos, asi que **el contrato no la admite**.

El efecto practico es que la interpretacion de autonomia se construye en el
texto a partir de los polos directos (`sensing`, `intuition`, `thinking`,
`feeling`), sin inventar un numero nuevo. Un perfil que traiga `autonomia`
se rechaza con el mensaje "es del formato de Entrega 2".

---

## 4. Intereses vocacionales (CHASIDE)

### 4.1 Estructura

98 items de respuesta si/no: **10 de interes y 4 de aptitud por area**, en las 7
areas del instrumento.

| Campo | Rango | Regla |
| :--- | :---: | :--- |
| `interes` | 0 a 10 | Suma de los 10 items de interes del area |
| `aptitud` | 0 a 4 | Suma de los 4 items de aptitud del area |
| `total` | 0 a 14 | Debe ser exactamente `interes + aptitud` |

### 4.2 Bandas

Se conserva la lectura de Entrega 2
([instrumento-chaside.md](instrumento-chaside.md), seccion 2.2), ahora sobre el
total bruto en lugar del puntaje normalizado:

| Banda | Total | Lectura para analogias |
| :--- | :---: | :--- |
| Afinidad alta | 11 a 14 | El area se puede usar como dominio principal de ejemplos |
| Afinidad media | 6 a 10 | Sirve como apoyo; no como analogia unica |
| Afinidad baja | 0 a 5 | No se usa como analogia |

### 4.3 Interes alto con aptitud baja

La brecha entre `interes` y `aptitud` es informativa pero **no tiene banda
oficial**: el instrumento no la define y el equipo no la va a inventar. Se
reportan los dos componentes por separado y el texto puede describir la
diferencia ("muestra interes alto en el area I con pocas respuestas de aptitud"),
sin traducirla a una etiqueta de capacidad ni a una recomendacion vocacional.

Aplican los guardrails de [instrumento-chaside.md](instrumento-chaside.md):
las areas solo eligen analogias, nunca carreras.

---

## 5. Lo que este baremo no hace

| Practica | Estado | Motivo |
| :--- | :--- | :--- |
| Convertir a 1.0-5.0 | Prohibido | Directriz 2: no reescalar escalas validadas |
| Calcular `autonomia` u otro indice compuesto | Prohibido | Directriz 2: no inventar indices |
| Clasificar al estudiante por tipo MBTI de 4 letras | Prohibido | Pierde la intensidad y fuerza un desempate artificial |
| Fijar puntos de corte clinicos o percentiles | Fuera de alcance | Requiere baremo poblacional validado, que el proyecto no tiene |
| Diagnostico o consejo vocacional | Prohibido | Guardrail etico del subsistema |

Un porcentaje o un percentil solo se puede citar si proviene del bloque
institucional y se identifica como tal; no se recalcula a mano.

---

## 6. Uso en las entregas siguientes

| Issue | Uso del baremo |
| :--- | :--- |
| E3-05 (#42) | Define que numeros debe exportar `generar-perfil.py` desde Moodle (`ap_*`, 8 polos, `score_*` mas items de interes y aptitud) |
| E3-06 (#43) | El corpus sintetico usa el contrato bruto y estas bandas para redactar la interpretacion esperada |
| E3-07 (#45) | El backend recibe el perfil bruto y arma el prompt con las bandas, sin recalcular puntajes |
| E3-08 (#44) | El SLM se entrena con interpretaciones redactadas segun estas reglas |

Regla de consistencia: si una banda cambia, se actualiza este documento, el
schema y los fixtures de `perfiles/`, y se corre el validador antes de cerrar.

---

## 7. Validacion

Desde la raiz del repositorio:

```bash
python docs/especificaciones/test_validar_perfiles_brutos.py
python docs/especificaciones/validar-perfiles-brutos.py
python docs/especificaciones/test_validar_corpus_anonimizado.py
```

Los tres deben terminar en `RESULTADO: OK`. El segundo valida los ejemplos
versionados; los otros dos cubren los casos negativos de cada contrato.

---

## 8. Referencias

- Felder, R. M., y Soloman, B. A. (s. f.). *Index of Learning Styles*. North Carolina State University.
- Felder, R. M., y Silverman, L. K. (1988). Learning and teaching styles in engineering education. *Engineering Education, 78*(7), 674-681.
- Tamayo Lopera, D. A., Cespedes Correa, A. M., Lopez Restrepo, S., y Valencia Torres, M. Y. (2018). Correspondencia entre la carrera cursada y resultados del test CHASIDE. *Psicoespacios, 12*(21), 76-93.
- McCrae, R. R., y Costa, P. T. (1989). Reinterpreting the Myers-Briggs Type Indicator from the perspective of the five-factor model of personality. *Journal of Personality, 57*(1), 17-40.
- Bloque `block_learning_style`, `block_personality_test` y `block_chaside` (IS-UTB / ISCOUTB, 2026): implementacion institucional de los tres instrumentos.
