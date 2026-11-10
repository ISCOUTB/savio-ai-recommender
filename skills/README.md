# skills - Habilidades locales de OpenCode

Esta carpeta contiene **codigo y documentacion de terceros** y **skills propias
del proyecto** que el agente puede cargar como habilidades. Se registra desde
`opencode.jsonc` con `"skills": ["./skills"]`; no hay que tocar esa config al
agregar una carpeta nueva.

Es la mayor parte del repositorio en conteo de archivos: 248 de los 536 archivos
versionados estan aqui, y solo `archify` aporta casi todo el peso (8 MB). Se
versionan para que cualquier integrante tenga las mismas habilidades sin
descargar nada.

## Inventario

| Skill | Archivos | Peso | Origen | Licencia | Uso previsto |
|---|---|---|---|---|---|
| `archify` | 219 | 8.0 MB | tt-a1i, v2.17 (basado en Cocoon-AI, MIT) | MIT (ver `archify/LICENSE`) | **Ahora:** diagramas de arquitectura, flujo y secuencia de las entregas |
| `prompt-engineering-patterns` | 10 | 83 KB | comunidad | no declarada | **Ahora:** auditoria del prompt de recomendacion (E2-10) y futuros prompts |
| `moodle-external-api-development` | 2 | 19 KB | comunidad | no declarada | **Futuro:** feedback loop (E2-11) e integracion con Moodle (E2-12) |
| `docker-patterns` | 1 | 15 KB | comunidad | no declarada | **Futuro:** Moodle local y pruebas de instalacion |
| `adversarial-review` | 4 | 7 KB | comunidad | no declarada | **Futuro:** revision cruzada de cambios grandes |
| `python-project-structure` | 1 | 7 KB | comunidad | no declarada | **Futuro:** si `poc_slm/` pasa a paquete instalable |
| `trl-training` | 2 | 16 KB | huggingface/skills | Apache-2.0 | **Ahora:** SFT/DPO con TRL para E3-08 (#44) |
| `huggingface-local-models` | 5 | 28 KB | huggingface/skills | Apache-2.0 | **Ahora:** seleccion de GGUF y serving local en CPU para E3-08 y E3-10 |
| `ollama-runtime` | 1 | 3 KB | propia | interna | **Ahora:** runtime Ollama, Modelfile y medicion de latencia (#44, #53) |
| `corpus-psicometrico` | 1 | 4 KB | propia | interna | **Ahora:** gates del corpus E3-06 antes de entrenar (#38, #43, #50) |
| `entrenamiento-qlora` | 1 | 4 KB | propia | interna | **Ahora:** hiperparametros T4 y conversion GGUF de E3-08 (#44) |

Regla de permanencia: se queda una skill si se usa hoy o si hay un issue
identificable que la va a usar. Si deja de cumplirse, se propone su salida.

## Reglas

1. **No se edita el contenido de una skill de terceros.** Si hay que adaptarla,
   se copia fuera de esta carpeta y se documenta el cambio.
2. **Agregar una skill requiere tres cosas:** justificacion escrita (que issue la
   necesita), revision de licencia y registro en `opencode.jsonc`.
3. **Licencias:** `archify` es MIT; `trl-training` y `huggingface-local-models`
   son Apache-2.0 y llevan el `LICENSE` completo en su carpeta. Las demas no
   declaran licencia: antes de redistribuir fuera del repositorio, revisarla.
4. **Peso:** una skill nueva de mas de 1 MB necesita justificacion explicita;
   `archify` es la unica excepcion autorizada.

## Procedencia de las skills de Hugging Face

`trl-training` y `huggingface-local-models` se copiaron textuales desde
`github.com/huggingface/skills`, commit `25910b3d0ba31a2ba102f901cdc9e008c278a69c`
(2026-10-29), licencia Apache-2.0. No se editan: si hace falta adaptarlas, se
copia la version propia fuera de la carpeta original.

Para actualizarlas, repetir la descarga con el commit nuevo, revisar el diff de
`SKILL.md` y actualizar este bloque y la tabla. No se actualizan solas.

Descartadas a proposito: `huggingface-llm-trainer` (28 KB y orientada a HF Jobs
de pago), `hf-mem` (exige `uv` y red) y las skills genericas de PyTorch de
comunidad (sin licencia declarada y redundantes con `trl-training`).

## Verificacion

```bash
node skills/archify/bin/archify.mjs doctor
```

Requiere Node 18 o superior.
