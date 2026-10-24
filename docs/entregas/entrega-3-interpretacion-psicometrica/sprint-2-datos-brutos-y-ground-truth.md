# Entrega 3 - Sprint 2: OE1 - Datos brutos de los 3 tests y Ground Truth con LLM Maestro

**Estado:** Pendiente
**Issues:** E3-04, E3-05 (#42), E3-06 (#43)
**Objetivo SMART asociado:** Objetivo Especifico 1 (OE1)

## Objetivo

Cumplir la directriz de rigor psicometrico del docente: operar exclusivamente con las **puntuaciones originales brutas** de CHASIDE, Felder-Silverman y Test de Personalidad (sin alterar ni reescalar ninguna metrica), recolectar los perfiles reales restantes y construir el corpus *ground truth* de interpretaciones integradas usando LLMs de frontera (Claude / ChatGPT) alimentados con la literatura tecnica oficial de cada instrumento.

## Alcance

- **E3-04 (Contrato de puntajes brutos):** definir el schema JSON de entrada con las escalas nativas de los tres cuestionarios:
  - **CHASIDE:** interes (`0-10`), aptitud (`0-4`) y total (`0-14`) en las 7 areas (`C, H, A, S, I, D, E`).
  - **Felder-Silverman (ILS):** conteos por polo (`0-11`, suma `11` por eje) en las 4 dimensiones bipolares (`activo/reflexivo`, `sensitivo/intuitivo`, `visual/verbal`, `secuencial/global`).
  - **Personalidad:** conteos originales (`0-9` por polo) en las 4 dimensiones del bloque institucional, eliminando el indice inferido `autonomia`.
- **E3-05 / #42 (Perfiles brutos reales):** completar el diligenciamiento de `persona-2` y `persona-3` y extraer los puntajes crudos sin transformacion `1.0-5.0`.
- **E3-06 / #43 (Corpus Ground Truth con LLM Maestro):** alimentar a Claude / ChatGPT con los manuales y baremos oficiales de los 3 tests para generar al menos 150 interpretaciones psicologicas y vocacionales integradas de alta calidad (`instruction`, `input` con puntajes brutos, `output` con perfil integrado), con particion 80/20 (train/eval).

## Criterios de aceptacion

- [ ] Ningun puntaje de los 3 tests es reescalado ni alterado respecto al instrumento validado.
- [ ] El indice no validado `autonomia` queda retirado del contrato de entrada de Entrega 3.
- [ ] Los 3 perfiles reales del equipo estan extraidos con sus puntuaciones brutas originales (`E3-05` / `#42`).
- [ ] Corpus *ground truth* ($\ge 150$ muestras en formato JSONL) generado con LLMs maestros y revisado contra la literatura teorica de CHASIDE, Felder-Silverman y Personalidad (`E3-06` / `#43`).

