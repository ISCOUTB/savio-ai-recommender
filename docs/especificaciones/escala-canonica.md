# Escala canonica 1.0 - 5.0 (Historica - Entrega 2)

> **AVISO DE CAMBIO DE DECISION (Entrega 3 - 2026-10-23):**
> Por directriz oficial del docente del proyecto (prohibicion de modificar o reescalar instrumentos validados por criterio de rigor psicometrico), la escala unificada `1.0-5.0` y el indice inventado `autonomia` quedan **revocados y descartados para la Entrega 3** (resolucion de los issues `#37` y `#39`).
> En la Entrega 3 los datos se miden **exactamente como los califican los 3 repositorios oficiales** de Moodle (`ISCOUTB/learning_style`, `ISCOUTB/personality_test`, `ISCOUTB/chaside`):
> - **Estilos de Aprendizaje (Felder-Silverman):** conteos originales de `0 a 11` por polo (suma 11 por dimension) y bandas oficiales de diferencia (`1-3`, `5-7`, `9-11`).
> - **Personalidad:** conteos brutos originales de `0 a 9` por cada uno de los 8 polos, sin `autonomia`.
> - **CHASIDE:** conteos brutos de Interes (`0 a 10`), Aptitud (`0 a 4`) y Total (`0 a 14`), con porcentajes nativos `0 a 100%`.
>
> Este documento se conserva unicamente como registro historico de la Entrega 2. El contrato activo de la Entrega 3 se define bajo el issue `E3-04`.

**Aprobada:** 2026-10-19 (Entrega 2) | **Revocada:** 2026-10-23 (Entrega 3)  
**Afecta:** `estilos_aprendizaje.puntajes`, `personalidad.rasgos`, `chaside.areas` (historico)  
**Refuerza:** `docs/especificaciones/perfil-estudiante.schema.json` (rangos E2), `docs/especificaciones/validar-perfiles.py` (reglas semanticas E2)

---

## 1. Regla unica

Todos los puntajes numericos del perfil del estudiante se expresan en **escala 1.0 a 5.0**, con **3.0 como punto neutro**. No hay excepciones.

---

## 2. Conversion por instrumento (verificada en el bloque instalado)

| Instrumento | Entrada del bloque | Formula | Rango resultante |
| :--- | :--- | :--- | :--- |
| **Estilos de Aprendizaje** (Felder-Soloman) | 2 conteos por eje, 11 items por polo (par suma 11) | `round(3 + 2 * (polo_derecho - polo_izquierdo) / 11, 1)` | 1.0 - 5.0 |
| **Personalidad** (MBTI-like) | 2 conteos por eje, **9 items por polo** (verificado en `personality_test/save.php`) | `round(3 + 2 * (polo_derecho - polo_izquierdo) / 9, 1)` | 1.0 - 5.0 |
| **CHASIDE** | total 0-14 por area (10 interes + 4 aptitud). El bloque entrega `pct_total = round(100 * total / 14, 1)` | `round(1 + 4 * pct_total / 100, 1)`  <br>equivalentemente: `round(1 + 4 * total / 14, 1)` | 1.0 - 5.0 |

> **Nota:** Para CHASIDE se usa el `pct_total` que el propio bloque ya calcula, porque respeta el peso 10/4 entre interes y aptitud.

---

## 3. Valores alcanzables (discretos)

Por ser formulas con numeros enteros, **no todos los decimales son posibles**.

### Estilos (diferencia impar: -11, -9, ..., +11)

```
1.0, 1.4, 1.7, 2.1, 2.5, 2.8, 3.2, 3.5, 3.9, 4.3, 4.6, 5.0
```
**12 valores unicos.** Cualquier otro (ej. 1.6, 4.2, 1.8, 3.6) **indica error de calculo o dato inventado**.

### Personalidad - 3 rasgos directos (diferencia -9 a +9, cualquier entero)

Cada polo se puntua de 0 a 9 de forma independiente (9 items Si/No por polo), asi que la
diferencia **no** es siempre impar.

```
1.0, 1.2, 1.4, 1.7, 1.9, 2.1, 2.3, 2.6, 2.8, 3.0,
3.2, 3.4, 3.7, 3.9, 4.1, 4.3, 4.6, 4.8, 5.0
```
**19 valores unicos.** `3.0` es alcanzable con empate exacto.

### Personalidad - autonomia (suma de 2 diferencias -> 3 + s/9, s de -18 a 18)

```
1.0, 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.6, 2.7,
2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4,
4.6, 4.7, 4.8, 4.9, 5.0
```
**37 valores unicos.** No aparecen 1.5, 2.5, 3.5 ni 4.5.

### CHASIDE (total 0-14 -> 1 + 4*total/14)

```
1.0, 1.3, 1.6, 1.9, 2.1, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.1, 4.4, 4.7, 5.0
```
**15 valores unicos.** `3.0` corresponde a total 7.

---

## 4. Significado del 3.0 por bloque (critico para E2-10)

| Bloque | 3.0 significa | Aparicion en test completo |
| :--- | :--- | :--- |
| Estilos | **Sin informacion** (test incompleto) | **Imposible** (diferencia impar) |
| Personalidad | **Equilibrado** (polos empatados) | **Posible** (diferencia 0) |
| CHASIDE | **Interes medio** (total 7/14) | **Posible** |

> **Regla para E2-10:** El Prompt Builder **no debe** tratar `3.0` como "vacio" en los tres bloques. En estilos indica ausencia de datos; en personalidad y CHASIDE indica preferencia equilibrada/mediana real.

---

## 5. Contrato minimo en el schema

`perfil-estudiante.schema.json` exige:

```json
"puntajes": { "type": "object", "minProperties": 4, "additionalProperties": { "type": "number", "minimum": 1.0, "maximum": 5.0 } },
"rasgos":   { "type": "object", "additionalProperties": { "type": "number", "minimum": 1.0, "maximum": 5.0 } },
"areas":    { "type": "object", "required": ["C","H","A","S","I","D","E"], "additionalProperties": { "type": "number", "minimum": 1.0, "maximum": 5.0 } }
```

---

## 6. Validacion semantica (validar-perfiles.py)

El validador rechaza un perfil si:

1. `estilos_aprendizaje.modelo == "felder_silverman"` y `puntajes` contiene valores fuera del conjunto de 12 alcanzables.
2. `estilos_aprendizaje.preferencias` no coincide con la regla de la seccion 2.3 (<=2.1 o >=3.9).
3. `personalidad.rasgos` contiene valores fuera del conjunto de la seccion 3 (19 para los 3 rasgos directos, 37 para `autonomia`).
4. `chaside.areas` contiene valores fuera del conjunto de 15 alcanzables.

El perfil neutro (todos los `puntajes` en 3.0) **es valido**: representa un test incompleto, y el
schema no guarda el estado de completitud. No se puede distinguir de un dato mal cargado, asi que
el validador no lo rechaza.

---

## 7. Ejemplo valido (perfiles/ejemplo-perfil-estudiante.json)

```json
"estilos_aprendizaje": {
  "modelo": "felder_silverman",
  "puntajes": { "activo_reflexivo": 1.7, "sensorial_intuitivo": 4.6, "visual_verbal": 1.7, "secuencial_global": 3.2 },
  "preferencias": ["activo", "intuitivo", "visual"],
  "descripcion_para_prompt": "..."
},
"personalidad": {
  "rasgos": { "introversion_extraversion": 1.9, "autonomia": 2.8, "metodicidad": 4.6, "apertura": 1.9 },
  "resumen_conductual": "...",
  "preferencias_trabajo": ["individual", "secuencia definida", "ejemplos concretos"]
},
"chaside": {
  "areas": { "C": 2.1, "H": 3.0, "A": 2.7, "S": 1.9, "I": 3.3, "D": 1.3, "E": 2.4 },
  "areas_dominantes": ["I", "H"],
  "descripcion_para_analogias": "..."
}
```

---

## 8. Referencias a los bloques

- `learning_style`: `/bitnami/moodle/blocks/learning_style/` -> 44 items A/B, 4 ejes x 11, salida `ap_*` 0-11.
- `personality_test`: `/bitnami/moodle/blocks/personality_test/` -> 72 items, 8 ejes x 9 items (`save.php` lineas 234-268).
- `chaside`: `/bitnami/moodle/blocks/chaside/classes/facade.php` -> 98 items, 7 areas, `pct_total = 100 * total / 14`.

---

## 9. E2-06 hereda esta convencion

El issue E2-06 (instrumento CHASIDE) **no decide la unidad**. Hereda 1.0-5.0 y la formula `1 + 4*total/14`. Si el area pide otra conversion, se cambia la nota y el ejemplo; **el schema no se modifica** (solo valida rango).
