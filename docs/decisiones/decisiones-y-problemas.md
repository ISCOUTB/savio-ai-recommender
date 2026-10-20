# Decisiones y problemas del perfilamiento - Entrega 2

- **Fecha:** 2026-10-20
- **Alcance:** modelado del perfil del estudiante (E2-01, E2-04, E2-05, E2-06, E2-07), escala de conversion, contrato de datos y primer perfil real
- **Estado:** vigente; las secciones 11 y 12 marcan lo que sigue abierto
- **Fuentes de evidencia:** `docs/especificaciones/`, `perfiles/`, `experimentos/bitacora.md`, `docs/entregas/entrega-2-personalizacion/github-issues.md` y las tablas de Moodle

---

## 1. Para que sirve este documento

Este documento responde cuatro preguntas: que teniamos antes de la intervencion, que problemas aparecieron, que decidimos y con que evidencia se sostiene cada decision. Esta dirigido a cualquier integrante del equipo que se incorpore despues, y a la docente cuando pregunte por que el perfil tiene la forma que tiene.

No reemplaza las notas tecnicas. Cuando una decision necesita detalle de calculo, se remite a `docs/especificaciones/escala-canonica.md` (escala y formulas), `instrumento-estilos-aprendizaje.md` (E2-04) e `instrumento-personalidad.md` (E2-05).

---

## 2. Punto de partida: que teniamos antes

### 2.1 La PoC del recomendador

Antes de Entrega 2 el unico codigo ejecutable era la PoC de Entrega 1 (`poc_slm/recommender.py`). Consumia eventos planos como este:

```json
{
  "estudiante": "Estudiante Demo",
  "materia": "Estructuras de Datos",
  "tema": "Arboles AVL",
  "calificacion": 2.0,
  "escala": "0-5",
  "estilo_aprendizaje": "visual"
}
```

El estilo era **un solo texto** (`visual`, `textual`) escrito a mano en el JSON del evento. No habia perfil, ni puntajes, ni conversion desde un instrumento real. La regla 5 del refuerzo (`--refuerzo`) hacia un mapeo fijo: `visual` llevaba a diagramas, `textual` a texto.

### 2.2 El schema del perfil (E2-01)

El schema `perfil-estudiante.schema.json` estaba pensado para **VARK**:

```json
"estilos_aprendizaje": {
  "required": ["modelo", "dominante"],
  "dominante": { "enum": ["visual", "auditivo", "kinestesico", "lectura_escritura", "mixto"] },
  "puntajes": { "additionalProperties": { "type": "number" } }
}
```

Tres consecuencias de ese diseno:

1. Solo admitia **una etiqueta dominante**, propia de un instrumento unimodal.
2. Los `puntajes` no tenian rango: cualquier numero pasaba.
3. No existia el campo `origen`, asi que nada distinguia un perfil inventado de uno medido.

El perfil de ejemplo (`perfiles/ejemplo-perfil-estudiante.json`) usaba escala 0-10 y valores que despues se revelaron imposibles:

```json
"modelo": "vak",
"dominante": "visual",
"puntajes": { "visual": 8, "auditivo": 4, "kinestesico": 6, "lectura_escritura": 5 },
"personalidad": { "rasgos": { "introversion_extraversion": 3, "autonomia": 7, "metodicidad": 6, "apertura": 8 } }
```

### 2.3 Moodle local (E2-02 y E2-03)

Ya estaba operativo: Bitnami Moodle 5.0.2 sobre MariaDB 10.11, con los tres bloques institucionales IS-UTB instalados en el curso `E2-03-psico` (id 2):

| Bloque | Version | Que mide | Volumen |
| :--- | :--- | :--- | :--- |
| `learning_style` | 2.0.4 | Index of Learning Styles (Felder y Soloman), 4 ejes bipolares | 44 items, 11 por polo |
| `personality_test` | 2.0.5 | Cuestionario tipo MBTI, 8 polos | 72 items, 9 por polo |
| `chaside` | 2.0.4 | Intereses y aptitudes vocacionales, 7 areas | 98 items (10 interes + 4 aptitud por area) |

Cuentas creadas: `persona-1` (id 3), `persona-2` (id 4), `persona-3` (id 5). Los tests se guardan **por usuario, no por curso**.

### 2.4 Los issues

Estaban definidos E2-01 a E2-12. Faltaban dos problemas que ya se veian venir pero no tenian issue: la validez psicopedagogica del indice `autonomia` y el manejo legal de los datos de los tests.

---

## 3. Problemas que encontramos

| # | Problema | Como se manifesto | Por que importaba |
| :--- | :--- | :--- | :--- |
| P1 | **El schema no correspondia al instrumento real** | El bloque instalado mide 4 ejes bipolares de Felder-Soloman, no canales VARK | El perfil habria descrito un instrumento que nadie diligencia |
| P2 | **`dominante` no tiene sentido con 4 ejes** | Un estudiante puede ser visual y global a la vez; no hay un unico "dominante" | Se perdia informacion y se forzaba una etiqueta falsa |
| P3 | **Tres escalas distintas** | Estilos 0-11, personalidad 0-9, CHASIDE 0-14 (o porcentaje 0-100) | El Prompt Builder tendria que normalizar en cada consulta y compararia peras con manzanas |
| P4 | **Valores incompatibles con la escala en el perfil de ejemplo** | `personalidad` en 0-10 (3, 7, 6, 8) y `chaside` con valores de 1 a 8; con la escala 1.0-5.0 ninguno es valido | Ejemplo que no se podia reproducir con los datos del bloque |
| P5 | **No existia conversion Moodle -> perfil** | Las respuestas se guardaban en MariaDB y ahi se quedaban | Sin E2-07 no habia perfil, y sin perfil no habia E2-10 |
| P6 | **Los tests estaban sin diligenciar** | `is_completed = 0` en `learning_style` y `personality_test`; CHASIDE sin filas | Cualquier validacion con datos reales era imposible |
| P7 | **El validador rechazaba valores validos** | `apertura = 2.6` era marcado como "no alcanzable" | Un perfil real se habria descartado por un error nuestro |
| P8 | **Dos riesgos sin issue** | `autonomia` es un indice inferido sin aval; no habia regla de consentimiento | Decisiones tomadas por el equipo sin respaldo del area correspondiente |
| P9 | **Riesgo de versionar datos personales** | Nada impedia un `git add` de un perfil real | Una vez en el historial, no se puede borrar de verdad |
| P10 | **Documentos de referencia eliminados** | Se quitaron `guia-del-proyecto.md` y `consultas-al-docente.md` con sus `.docx`; quedan copias Word en poder del equipo | Si hay que actualizarlos no hay fuente en el repo |

---

## 4. Decisiones tomadas

### 4.1 Cronologia

| Fecha | Decision | Motivo | Evidencia |
| :--- | :--- | :--- | :--- |
| 2026-10-18 | Instalar los bloques IS-UTB y dejar el curso armado | El instrumento real es el que entrega la institucion | `moodle/plugins.md`, bitacora |
| 2026-10-19 | **Felder-Soloman como modelo canonico** (`modelo: "felder_silverman"`) | Es el instrumento que se diligencia de verdad y sus 4 ejes son compatibles con formato de recurso | `learning_style/save.php`, nota E2-04 |
| 2026-10-19 | `vak` queda en el enum como valor **historico** | No romper perfiles viejos ni el schema | schema, `instrumento-estilos-aprendizaje.md` 1.2 |
| 2026-10-19 | **`origen` obligatorio** (`real` / `simulado`) | Sin este campo no se puede distinguir dato medido de dato inventado | schema, `perfiles/README.md` |
| 2026-10-19 | **Eliminar `dominante` y agregar `preferencias`** | Con 4 ejes bipolares no existe un unico dominante; se listan los polos con preferencia clara | schema 2.1, nota E2-04 |
| 2026-10-19 | **Escala unica 1.0 - 5.0** para los tres bloques | Un solo rango simplifica el Prompt Builder y el validador | `escala-canonica.md` |
| 2026-10-19 | **CHASIDE se cierra ya**, sin esperar E2-06 | El schema solo valida rango, asi que la formula es reversible; bloqueaba E2-07 | issue E2-06, `escala-canonica.md` 9 |
| 2026-10-19 | **E2-06 hereda** la formula y solo decide el significado pedagogico | Evita que dos issues definan la misma conversion | nota E2-06 |
| 2026-10-19 | **`autonomia` no se toca**; se registra E2-13 | Es un criterio psicopedagogico, no tecnico | issue E2-13 |
| 2026-10-19 | **E2-14 se difiere a P2/backlog** | El riesgo irreversible (versionar un perfil real) ya lo cubre la regla de solo simulados | issue E2-14 |
| 2026-10-19 | **Solo perfiles `simulado` en git** | Politica de datos; los reales viven fuera del repo | `perfiles/README.md`, `.gitignore` |
| 2026-10-20 | **Los conjuntos de valores se calculan**, no se escriben a mano | Dos listas distintas, repartidas en tres archivos, quedaron mal y se desincronizaron del documento | `validar-perfiles.py` |
| 2026-10-20 | **Perfiles reales en `perfiles/reales/`**, ignorada por git | Separacion fisica entre dato medido y fixture | `.gitignore` |
| 2026-10-20 | **Desempate CHASIDE oficial** (total, aptitud, brecha, alfabetico) | Es la regla del bloque; inventar otra daria areas dominantes distintas a las que ve el estudiante | `chaside/classes/facade.php` |

### 4.2 Por que Felder y no VARK

La nota tecnica original fundamentaba VARK (Fleming y Mills, 1992) y lo registraba como `"vak"`. El problema es simple: **el bloque institucional aplica el Index of Learning Styles de Felder y Soloman**. Documentar VARK habria descrito un instrumento que ningun estudiante diligencia, y el perfil no habria podido generarse desde Moodle.

Se conserva `"vak"` en el enum por compatibilidad, pero **no se usa en perfiles nuevos**.

Ademas, los 4 ejes no compiten con los otros dos instrumentos:

- **Visual/Verbal** define el *canal* del recurso (video, texto, interactivo).
- **Activo/Reflexivo y Secuencial/Global** definen *como se organiza* el estudio.
- **Personalidad** cubre organizacion, autonomia y nivel de abstraccion.
- **CHASIDE** cubre intereses vocacionales para analogias.

---

## 5. La escala canonica 1.0 - 5.0

### 5.1 Formulas

| Instrumento | Entrada del bloque | Formula | Rango |
| :--- | :--- | :--- | :--- |
| Estilos (Felder) | 2 conteos por eje, 11 items (el par suma 11) | `round(3 + 2 * (derecho - izquierdo) / 11, 1)` | 1.0 - 5.0 |
| Personalidad | 2 conteos por eje, 9 items por polo (0-9) | `round(3 + 2 * (derecho - izquierdo) / 9, 1)` | 1.0 - 5.0 |
| Personalidad (autonomia) | suma de dos diferencias | `round(3 + ((N - S) + (T - F)) / 9, 1)` | 1.0 - 5.0 |
| CHASIDE | total 0-14 por area | `round(1 + 4 * total / 14, 1)` | 1.0 - 5.0 |

### 5.2 Valores alcanzables

Por ser formulas con enteros, no todos los decimales son posibles:

- **Estilos: 12 valores** (la diferencia es impar): `1.0, 1.4, 1.7, 2.1, 2.5, 2.8, 3.2, 3.5, 3.9, 4.3, 4.6, 5.0`
- **Personalidad, 3 rasgos directos: 19 valores**: `1.0, 1.2, 1.4, 1.7, 1.9, 2.1, 2.3, 2.6, 2.8, 3.0, 3.2, 3.4, 3.7, 3.9, 4.1, 4.3, 4.6, 4.8, 5.0`
- **Personalidad, autonomia: 37 valores** (no aparecen 1.5, 2.5, 3.5 ni 4.5)
- **CHASIDE: 15 valores**: `1.0, 1.3, 1.6, 1.9, 2.1, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.1, 4.4, 4.7, 5.0`

Un valor fuera de esas listas **no es un dato, es un error de calculo**.

### 5.3 Bandas

| Banda | Rango | Uso |
| :--- | :--- | :--- |
| Polo bajo | 1.0 a 2.1 | Se emite preferencia por el polo izquierdo/bajo |
| Equilibrado | 2.2 a 3.8 | No se emite preferencia; formatos mixtos |
| Polo alto | 3.9 a 5.0 | Se emite preferencia por el polo derecho/alto |

La banda equilibrada es amplia a proposito: con 9 o 11 items, una diferencia de 3 puntos no es una preferencia confiable y el sistema no debe sobre-personalizar.

### 5.4 El 3.0 significa cosas distintas

| Bloque | 3.0 significa | Aparicion en test completo |
| :--- | :--- | :--- |
| Estilos | **Sin informacion** (test incompleto) | **Imposible** (la diferencia es impar) |
| Personalidad | **Equilibrado** (polos empatados) | **Posible** |
| CHASIDE | **Interes medio** (7 de 14) | **Posible** |

Regla para E2-10: el Prompt Builder **no debe** tratar 3.0 como "vacio" en los tres bloques. En estilos indica ausencia de datos; en personalidad y CHASIDE indica preferencia equilibrada o mediana real.

---

## 6. El contrato de datos: antes y despues

| Campo | Antes | Ahora | Decision |
| :--- | :--- | :--- | :--- |
| `origen` | no existia | **obligatorio**: `real` / `simulado` | Distingue dato medido de fixture |
| `estilos_aprendizaje.modelo` | `vak` por defecto | `felder_silverman` canonico; `vak` historico | El instrumento real es Felder |
| `estilos_aprendizaje.dominante` | obligatorio (5 valores VARK) | **eliminado** | No hay dominante con 4 ejes |
| `estilos_aprendizaje.preferencias` | no existia | array de 0 a 4 polos, sin duplicados | Lista los polos fuera de banda |
| `estilos_aprendizaje.puntajes` | sin rango, sin minimo de claves | 4 claves, `1.0` a `5.0` | Escala unica |
| `personalidad.rasgos` | sin rango | `1.0` a `5.0` | Escala unica |
| `chaside.areas` | 7 claves opcionales, sin rango | 7 claves **obligatorias**, `1.0` a `5.0` | Un perfil sin las 7 areas no es util para analogias |

Consecuencia practica: un perfil sin `origen` o sin las 7 areas CHASIDE **ya no valida**.

---

## 7. Las dos herramientas

### 7.1 `validar-perfiles.py`

Valida contra el schema (draft-07) **y** contra reglas semanticas que el schema no puede expresar:

1. Los puntajes de estilos pertenecen a los 12 valores alcanzables.
2. `preferencias` coincide con la regla de bandas (recalculada, no declarada).
3. Los rasgos de personalidad pertenecen a sus 19 o 37 valores.
4. Las areas CHASIDE pertenecen a sus 15 valores.

```bash
python docs/especificaciones/validar-perfiles.py
python docs/especificaciones/validar-perfiles.py perfiles/reales/persona-1.json
```

### 7.2 `generar-perfil.py` (E2-07)

Convierte las respuestas de Moodle en el perfil JSON:

```bash
python docs/especificaciones/generar-perfil.py --usuario persona-1
```

Flujo: `docker exec` -> leer las tres tablas -> verificar integridad -> aplicar formulas -> construir textos -> calcular areas dominantes -> escribir `perfiles/reales/<usuario>.json` -> validar el archivo generado.

Tres controles de integridad que hace antes de escribir:

- Cada par de estilos debe sumar **11**.
- El total CHASIDE recalculado desde `q1` a `q98` debe coincidir con el `score_*` que guardo el bloque.
- Si Docker esta apagado, falla con un mensaje que indica el comando para levantar la pila.

---

## 8. El caso del bug del validador

Este es el error mas importante que cometimos y conviene dejarlo escrito.

**Como se detecto:** al ir a validar el primer perfil real, el validador respondio que `personalidad.rasgos.apertura = 2.6` no era un valor alcanzable. El valor era correcto.

**Causa:** al calcular los valores posibles de personalidad asumimos que la diferencia entre polos siempre es impar, como ocurre en estilos (donde los 11 items se reparten entre dos polos y el par suma 11). En personalidad **cada polo se puntua 0-9 de forma independiente** (9 items Si/No por polo), asi que la diferencia puede ser cualquier entero de -9 a 9.

**Alcance:** el error estaba en tres lugares y con tres listas distintas, las tres equivocadas:

| Archivo | Lista que tenia | Problema |
| :--- | :--- | :--- |
| `validar-perfiles.py` | 10 valores (solo diferencias impares) | Rechazaba 2.6, 3.4, 4.3, 1.2... |
| `escala-canonica.md` | 10 valores (otra lista, solo pares) | Documentaba valores inexistentes |
| Word de consultas al docente | la lista de impares | Tabla ilustrativa incorrecta |

**Correccion:** los conjuntos ya no se escriben a mano. Se calculan en el validador con la misma formula que documenta la escala:

```python
FELDER_VALORES = {round(3 + 2 * d / 11, 1) for d in range(-11, 12, 2)}
PERSONALIDAD_3RASGOS = {round(3 + 2 * d / 9, 1) for d in range(-9, 10)}
PERSONALIDAD_AUTONOMIA = {round(3 + s / 9, 1) for s in range(-18, 19)}
CHASIDE_VALORES = {round(1 + 4 * t / 14, 1) for t in range(0, 15)}
```

**Verificacion:** el perfil real de persona-1 pasa; un valor no alcanzable (`apertura = 2.4`) sigue siendo rechazado.

**Leccion:** una lista de valores derivada de una formula debe calcularse, no transcribirse. Y el validador se prueba contra datos reales, no solo contra ejemplos escritos por quien lo programo.

Efecto secundario de la revision: se elimino la regla que rechazaba un perfil con los cuatro puntajes de estilos en `3.0`. Ese perfil es el **perfil neutro** de un test incompleto y es valido; el schema no guarda completitud, asi que no se puede distinguir de un dato mal cargado sin agregar un campo.

---

## 9. Los datos reales

### 9.1 Estado de los tests

| Tabla | Filas | Estado |
| :--- | :--- | :--- |
| `mdl_learning_style` | 1 (usuario 3) | `is_completed = 1` |
| `mdl_personality_test` | 1 (usuario 3) | `is_completed = 1` |
| `mdl_block_chaside_responses` | 1 (usuario 3) | `is_completed = 1` |

Solo `persona-1` diligencio los tres tests. `persona-2` y `persona-3` no tienen datos.

### 9.2 Primer perfil generado

`perfiles/reales/persona-1.json`, validado (1/1):

| Bloque | Valores | Lectura |
| :--- | :--- | :--- |
| Estilos | activo_reflexivo 2.5, sensorial_intuitivo 1.4, visual_verbal 1.4, secuencial_global 2.5 | Preferencias `["sensorial", "visual"]`: canal visual fuerte, concreto |
| Personalidad | introversion_extraversion 3.2, autonomia 2.8, metodicidad 2.8, apertura 2.6 | Los cuatro en banda equilibrada; `preferencias_trabajo: []` |
| CHASIDE | S 3.9, C 3.6, H 3.6, A 3.3, I 3.3, D 2.4, E 1.9 | Dominantes S y H |

Dos observaciones utiles para la demo:

1. **Todos los rasgos de personalidad quedaron equilibrados.** Es un resultado legitimo (la persona respondio centrada) y demuestra que el sistema **no debe sobre-personalizar** cuando no hay preferencia clara. El perfil emite `preferencias_trabajo: []` en lugar de inventar etiquetas.
2. **El desempate CHASIDE funciono como el bloque.** C y H empataron en total (9); H gano por aptitud (3 contra 2), porque el script recalcula interes y aptitud desde las 98 respuestas en lugar de mirar solo los totales.

---

## 10. Datos personales y consentimiento (E2-14)

### 10.1 Que se guarda y donde

| Donde | Que se guarda |
| :--- | :--- |
| Moodle (fuente de verdad) | respuestas individuales de los tres tests, tipo MBTI, conteos crudos, fecha |
| Perfil JSON | pseudonimo, 4 ejes de estilos, 4 rasgos, 7 areas CHASIDE, textos derivados |
| Modelo SLM (local) | solo el perfil; nunca las respuestas ni el tipo MBTI |
| Repositorio git | **solo perfiles simulados** |

### 10.2 Regla adoptada

- `origen` es obligatorio y distingue `real` de `simulado`.
- `perfiles/reales/` esta en `.gitignore`: un perfil medido no entra al historial.
- `estudiante_id` es el username de Moodle (`persona-1`), no nombre ni correo.
- El perfil nunca incluye las 214 respuestas ni el tipo MBTI de 4 letras.

### 10.3 Lo que sigue pendiente

E2-14 quedo en P2 con label `backlog`, y se activa cuando: (a) se apliquen tests a estudiantes fuera del equipo, o (b) se quieran mostrar perfiles reales en la demo E2-12. Contiene 30 preguntas agrupadas en 9 bloques (marco normativo, consentimiento, finalidad, acceso, conservacion, derechos, seguridad, comunicacion y publicacion) para la oficina de datos personales o el comite de etica.

La regla de solo simulados **no reemplaza** el consentimiento: solo evita el dano irreversible mientras se consigue el lineamiento.

---

## 11. Lo que queda abierto

| Tema | Estado | Quien |
| :--- | :--- | :--- |
| E2-03: tests de `persona-2` y `persona-3` | Pendiente (214 preguntas por persona) | persona-2 y persona-3 |
| E2-06: nota tecnica de CHASIDE | Pendiente; ya hereda formula y escala | persona-3 |
| E2-10: Prompt Builder | Pendiente; es el consumidor del perfil | equipo |
| E2-13: validar el indice `autonomia` | Bloqueado a concepto psicopedagogico | docente / psicopedagogia |
| E2-14: lineamientos de consentimiento | P2, backlog | docente / area legal |
| Word de consultas al docente | Contiene la tabla de personalidad con la lista vieja (10 valores) | equipo |
| `.md` de guia y consultas | Eliminados; solo quedan copias Word | equipo |

---

## 12. Glosario

- **Felder-Soloman (ILS):** instrumento de 44 items que mide 4 ejes bipolares de aprendizaje: activo/reflexivo, sensorial/intuitivo, visual/verbal, secuencial/global.
- **CHASIDE:** inventario vocacional de 7 areas (C, H, A, S, I, D, E) con 10 preguntas de interes y 4 de aptitud por area.
- **Banda:** tramo de la escala 1.0-5.0 que decide si se emite o no una preferencia (<=2.1, 2.2-3.8, >=3.9).
- **Perfil neutro:** perfil que se emite cuando el test esta incompleto; todos los puntajes en 3.0 y sin preferencias.
- **`origen`:** campo obligatorio que indica si el perfil se midio (`real`) o se construyo para pruebas (`simulado`).
- **Valor alcanzable:** valor que la formula puede producir. Fuera de esa lista, el dato es un error.
- **E2-13:** issue para validar psicopedagogicamente el indice `autonomia`.
- **E2-14:** issue de consentimiento y manejo de datos de los tests.

---

## 13. Anexo: comandos de verificacion

```bash
# Validar todos los perfiles del repo (y de perfiles/reales/)
python docs/especificaciones/validar-perfiles.py

# Generar el perfil de un usuario desde Moodle
python docs/especificaciones/generar-perfil.py --usuario persona-1

# Ver si los tests quedaron completos
docker exec moodle-db-1 mysql -u root -proot moodle -e \
  "SELECT user, is_completed FROM mdl_learning_style;"

# Levantar la pila si Docker esta apagado
cd moodle && docker compose up -d
```

Referencias:

- `docs/especificaciones/escala-canonica.md`
- `docs/especificaciones/instrumento-estilos-aprendizaje.md`
- `docs/especificaciones/instrumento-personalidad.md`
- `docs/especificaciones/perfil-estudiante.schema.json`
- `perfiles/README.md`
- `experimentos/bitacora.md`
