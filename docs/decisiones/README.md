# docs/decisiones - Decisiones y problemas del proyecto

Registro de las decisiones tecnicas y pedagogicas que sostienen el diseno del
subsistema, con el problema que las origino y la evidencia que las respalda.

## Indice

| Archivo | Contenido |
|---|---|
| [decisiones-y-problemas.md](decisiones-y-problemas.md) | Problemas encontrados, decisiones tomadas (Felder en vez de VARK, escala 1.0-5.0, contrato de datos), herramientas de validacion, datos reales y datos personales (E2-14) |

## Como se usa

- Una decision nueva se agrega como entrada en
  [decisiones-y-problemas.md](decisiones-y-problemas.md), con fecha, problema,
  opciones y decision.
- Una decision que cambie un contrato de datos obliga a actualizar el schema en
  [docs/especificaciones/](../especificaciones/) y los ejemplos de
  [perfiles/](../../perfiles/).
- Si una decision contradice un documento de [docs/investigacion/](../investigacion/),
  se resuelve aqui y se anota la correccion.

## Documentos que dependen de estas decisiones

- Contratos: [perfil-estudiante.schema.json](../especificaciones/perfil-estudiante.schema.json)
  y [escala-canonica.md](../especificaciones/escala-canonica.md)
- Perfiles de ejemplo: [perfiles/](../../perfiles/README.md)
- Prompt Builder: [poc_slm/prompt_builder.py](../../poc_slm/prompt_builder.py)
