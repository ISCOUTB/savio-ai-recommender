# Fichas interpretativas con fuente (Entrega 3)

Base de conocimiento del sistema: cada ficha es un texto interpretativo corto con su condicion de uso y su fuente verificable. La usan el prompt maestro (E3-06), el backend (E3-07) y la linea base sin IA (E3-09). Requisitos RF03, RF06 y HU04 del documento de formulacion.

| Archivo | Contenido |
| :--- | :--- |
| `fichas_interpretativas.json` | 121 fichas (version 1.0.0) |
| `construir_fichas.py` | Regenera la base descargando los textos de los bloques en un commit fijo (`python fichas/construir_fichas.py`) |

## Contenido

| Instrumento | Fichas | Condicion | Fuente |
| :--- | ---: | :--- | :--- |
| CHASIDE | 70 | area x nivel (alto, medio, emergente) x brecha (balanceado, interes mayor, aptitud mayor), mas nivel bajo por area | Matriz oficial de `block_chaside` (`lang/es`); reglas de nivel y brecha de `classes/facade.php` |
| ILS (Felder-Silverman) | 24 | polo x banda (equilibrio 1-3, moderada 5-7, fuerte 9-11) | Descripcion del polo de `block_learning_style`; fuerza de la preferencia segun Felder y Soloman; bandas de la seccion 8 de la formulacion |
| Personalidad | 8 | polo con mayor puntaje del eje | The Myers & Briggs Foundation, "The Preferences" (traduccion; cita original en `cita_original`) |
| Personalidad | 16 | tipo de 4 letras (`uso: contexto`) | Descripciones de tipos de `block_personality_test`; por R08 no se usan como etiqueta del estudiante |
| Principios | 3 | siempre | MBTI no mide capacidad; equilibrio deseable en el ILS; CHASIDE es orientativo (Tamayo Lopera et al., 2018) |

### Reglas de CHASIDE (del bloque)

- `pct_total = 100 * total / 14`: **alto** >= 80 (total 12-14), **medio** >= 60 (9-11), **emergente** >= 40 (6-8), **bajo** < 40 (0-5).
- `pct_interes = 100 * interes / 10` y `pct_aptitud = 100 * aptitud / 4`: **interes mayor** si la diferencia es >= 20 puntos, **aptitud mayor** si es <= -20, si no **balanceado**.

### Commits fijados de los bloques

| Bloque | Commit |
| :--- | :--- |
| `ISCOUTB/chaside` | `afd053a` |
| `ISCOUTB/learning_style` | `8ee2def` |
| `ISCOUTB/personality_test` | `426a101` |

## Pendientes

- **Verificar 3 fichas** (`verificado: false`): `PER-feeling`, `PER-judging` y `PER-perceptive`. El texto viene de un resumen de la pagina de la Myers & Briggs Foundation porque la lectura automatica se corto; hay que confirmar la cita textual en https://www.myersbriggs.org/my-mbti-personality-type/the-mbti-preferences/.
- **Bandas del ILS:** confirmar los cortes 1-3 / 5-7 / 9-11 en la pagina oficial del ILS de Felder (https://www.ncsu.edu/felder-public/ILSpage.html), que no se pudo leer de forma automatica.
- Los textos de los bloques se citan tal cual (con tildes, porque son citas); los textos propios siguen la convencion del repo sin tildes.
- La formulacion pedia al menos 39 fichas (7 + 24 + 8); la base supera ese minimo porque CHASIDE trae una matriz oficial de 70 interpretaciones.
