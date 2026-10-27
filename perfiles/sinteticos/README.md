# Perfiles sinteticos con puntajes originales brutos (Entrega 3)

Insumo del corpus ground truth de E3-06 (#43). **Datos 100 % sinteticos** (`origen: "sintetico"`): no corresponden a ninguna persona y se pueden versionar y enviar al modelo maestro.

| Archivo | Contenido |
| :--- | :--- |
| `perfiles_sinteticos.jsonl` | 150 perfiles, uno por linea, con el formato del Anexo A del documento de formulacion |
| `estratos.json` | Para cada perfil: escenario de CHASIDE, area dominante, banda del ILS por dimension, fuerza de personalidad por eje y particion (`train` / `eval`) |

Generados con `python poc_slm/generar_perfiles_sinteticos.py` (semilla 2026, reproducible) y validados con `poc_slm/perfil_bruto.py`.

## Reglas de validez (Anexo A)

- **CHASIDE:** por area, interes 0-10, aptitud 0-4 y `total = interes + aptitud` (0-14).
- **ILS (Felder-Silverman):** cada polo 0-11 y cada par de polos suma 11.
- **Personalidad:** cada polo 0-9.

Ningun puntaje se reescala. Si el schema formal de E3-04 (#50) cambia nombres de campos, se regenera con el mismo script.

## Cobertura

| Dimension | Reparto |
| :--- | :--- |
| Escenario CHASIDE | unica 60, co-dominantes 30, brecha interes alto / aptitud baja 22, plano 23, brecha aptitud alta / interes bajo 15 |
| Area dominante | entre 20 y 25 perfiles por cada una de las 7 areas |
| ILS (cada dimension) | 50 equilibrio (diferencia 1-3), 50 moderada (5-7), 50 fuerte (9-11) |
| Personalidad (cada eje) | 75 preferencia clara (diferencia 4-9), 53 leve (1-3), 22 empate (0), para probar la regla de desempate del bloque |
| Particion | 120 `train` / 30 `eval`, estratificada por escenario de CHASIDE; el split es por perfil, asi que el corpus no tiene fuga entre particiones |

## Perfiles reales

Los puntajes brutos de los integrantes se extraen con `python poc_slm/extraer_puntajes_brutos.py --usuario <usuario> --seudonimo <REAL-NN>` y quedan en `perfiles/reales/` (ignorada por git). Nunca se envian al modelo maestro ni a la nube.
