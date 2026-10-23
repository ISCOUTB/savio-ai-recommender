# skills - Habilidades locales de OpenCode

Esta carpeta contiene **codigo y documentacion de terceros** que el agente puede
cargar como habilidades. Se registra desde `opencode.jsonc` con `"skills": ["./skills"]`.

No es trabajo del proyecto: 237 de los 365 archivos versionados estan aqui, y
solo uno (`archify`) aporta casi todo el peso. Se versionan para que cualquier
integrante tenga las mismas habilidades sin descargar nada.

## Inventario

| Skill | Archivos | Peso | Origen | Licencia | Uso previsto |
|---|---|---|---|---|---|
| `archify` | 219 | 8.0 MB | tt-a1i, v2.17 (basado en Cocoon-AI, MIT) | MIT (ver `archify/LICENSE`) | **Ahora:** diagramas de arquitectura, flujo y secuencia de las entregas |
| `prompt-engineering-patterns` | 10 | 83 KB | comunidad | no declarada | **Ahora:** auditoria del prompt de recomendacion (E2-10) y futuros prompts |
| `moodle-external-api-development` | 2 | 19 KB | comunidad | no declarada | **Futuro:** feedback loop (E2-11) e integracion con Moodle (E2-12) |
| `docker-patterns` | 1 | 15 KB | comunidad | no declarada | **Futuro:** Moodle local y pruebas de instalacion |
| `adversarial-review` | 4 | 7 KB | comunidad | no declarada | **Futuro:** revision cruzada de cambios grandes |
| `python-project-structure` | 1 | 7 KB | comunidad | no declarada | **Futuro:** si `poc_slm/` pasa a paquete instalable |

Regla de permanencia: se queda una skill si se usa hoy o si hay un issue
identificable que la va a usar. Si deja de cumplirse, se propone su salida.

## Reglas

1. **No se edita el contenido de una skill de terceros.** Si hay que adaptarla,
   se copia fuera de esta carpeta y se documenta el cambio.
2. **Agregar una skill requiere tres cosas:** justificacion escrita (que issue la
   necesita), revision de licencia y registro en `opencode.jsonc`.
3. **Licencias:** solo `archify` declara licencia MIT con su archivo `LICENSE`.
   Antes de redistribuir fuera del repositorio, revisar la licencia de las demas.
4. **Peso:** una skill nueva de mas de 1 MB necesita justificacion explicita;
   `archify` es la unica excepcion autorizada.

## Verificacion

```bash
node skills/archify/bin/archify.mjs doctor
```

Requiere Node 18 o superior.
