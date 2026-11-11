# Procedimiento de consentimientos informados (E3-05)

Este documento convierte el Anexo A de los lineamientos en pasos ejecutables
para que los tres integrantes firmen antes de completar los tests
psicometricos. Sin consentimiento firmado no se procesa ningun puntaje real
(regla R2 de [lineamientos-datos-psicometricos.md](lineamientos-datos-psicometricos.md)).

- **Fuente unica del texto legal:** Anexo A de
  [lineamientos-datos-psicometricos.md](lineamientos-datos-psicometricos.md).
  Si ese anexo cambia, se actualiza aqui la copia imprimible.
- **Issue asociado:** E3-03 ([#38](https://github.com/ISCOUTB/savio-ai-recommender/issues/38))
  y E3-05 ([#42](https://github.com/ISCOUTB/savio-ai-recommender/issues/42)).
- **Responsable de custodiar las copias:** cada integrante firma la suya; el
  equipo no versiona ninguna.

---

## 1. Quien firma

| Integrante | Cuenta de Moodle | Estado del consentimiento |
|---|---|---|
| Persona 1 | `persona-1` | Firmado el 2026-11-10; perfil extraido el 2026-11-09 y fila registrada en la bitacora |
| Persona 2 | `persona-2` | Firmado el 2026-11-10 (copia fuera de OneDrive); perfil extraido el 2026-11-10 y fila registrada en la bitacora |
| Persona 3 | `persona-3` | Firmado el 2026-11-10; perfil extraido y fila registrada en la bitacora (filas del 2026-10-27 y 2026-11-10) |

Nadie mas firma: en Proyecto de Ingenieria I no se procesan datos de personas
distintas de los tres integrantes (regla R1).

---

## 2. Pasos por integrante (en este orden)

1. **Leer** el Anexo A y la seccion 6 de los lineamientos.
2. **Diligenciar** la copia imprimible de la seccion 5 de este documento con
   nombre completo, documento, fecha y firma.
3. **Escanear o fotografiar** la hoja firmada en un solo PDF.
4. **Guardar** el PDF en `perfiles/reales/consentimientos/` con el nombre
   `persona-N-consentimiento.pdf`. Esa carpeta esta en `.gitignore`: no se
   versiona y no debe salir del equipo.
5. **Borrar** el archivo temporal de Descargas, de la papelera y del chat por
   donde se haya enviado. No se envia por correo, Drive, OneDrive, WhatsApp ni
   Git.
6. **Avisar** en el issue #42 con la linea `consentimiento persona-N: firmado y
   en custodia local`. Sin nombre, sin documento, sin imagen.
7. **Solo entonces** completar las 214 preguntas en el Moodle local y extraer el
   perfil con:

   ```bash
   python docs/especificaciones/generar-perfil.py --usuario persona-N --salida perfiles/reales/persona-N-bruto.json
   ```

8. **Generar la evidencia publica** y pegarla en `experimentos/bitacora.md`:

   ```bash
   python docs/especificaciones/evidencia-perfil.py --perfil perfiles/reales/persona-N-bruto.json
   ```

   El comando imprime una fila con el resultado del validador y el SHA-256.
   No imprime puntajes. Si el archivo no esta ignorado por Git, aborta.

---

## 3. Que se publica y que no

| Dato | Git | Nube | Donde vive |
|---|---|---|---|
| Consentimiento firmado | No | No | `perfiles/reales/consentimientos/persona-N-consentimiento.pdf` |
| Perfil real en bruto | No | No | `perfiles/reales/persona-N-bruto.json` |
| Fila de evidencia (validador + SHA-256) | Si | Si | `experimentos/bitacora.md` |
| Respuestas individuales de Moodle | No | No | Base de datos del Moodle local |

El hash demuestra que el archivo existe y no cambio, sin revelar los puntajes:
el espacio de combinaciones de los tres instrumentos es demasiado grande para
reconstruirlo por fuerza bruta.

---

## 4. Agregacion fisica controlada

Si una corrida necesita los tres perfiles juntos (por ejemplo E3-09), se copian
por USB a un solo equipo designado, dentro de `perfiles/reales/`, se corre la
validacion y se borran al terminar (regla R10). No se usa Drive, OneDrive,
correo, WhatsApp, repositorio privado ni contenedor cifrado en Git sin
autorizacion escrita del docente.

---

## 5. Copia imprimible del consentimiento

```text
CONSENTIMIENTO INFORMADO PARA EL TRATAMIENTO DE RESULTADOS PSICOMETRICOS
Proyecto PerfilIA - Proyecto de Ingenieria I - UTB

Yo, [NOMBRE COMPLETO], identificado con [DOCUMENTO], autorizo de forma
voluntaria al equipo del proyecto PerfilIA a tratar mis puntajes brutos de
CHASIDE, Felder-Silverman y el test de personalidad, junto con un seudonimo,
para la siguiente finalidad:

1. Construir un perfil integrado de apoyo a la orientacion inicial.
2. Validar el prototipo academico de inferencia con un modelo de lenguaje
   pequeno ejecutado en CPU.

Entiendo que:

- El sistema no emite diagnosticos ni reemplaza la valoracion de un profesional.
- Mis datos reales se procesan solo en local y no se envian a Claude, ChatGPT,
  Hugging Face, Colab ni ningun servicio externo.
- Mis datos no se publican en el repositorio ni en Hugging Face.
- El corpus de entrenamiento se construye con perfiles sinteticos, no con mi
  perfil real.
- Puedo conocer, actualizar, rectificar, suprimir y retirar este consentimiento
  en cualquier momento.
- Si retiro el consentimiento, mi perfil real y sus derivados locales se
  eliminan; el corpus sintetico no se afecta.
- La informacion se conserva hasta el cierre de la Entrega 3 o hasta el retiro
  del consentimiento.

Contacto del responsable: [CORREO O CANAL DEL EQUIPO]
Fecha: [FECHA]
Firma: ______________________________
```

---

## 6. Mensaje listo para enviar a persona-2 y persona-3

> Hola. Para cerrar E3-05 (#42) necesitamos que cada uno haga esto, en su propia
> maquina y sin subir nada al repo:
>
> 1. Leer `docs/entregas/entrega-3-interpretacion-psicometrica/procedimiento-consentimientos.md`.
> 2. Firmar el consentimiento de la seccion 5 y guardarlo como
>    `perfiles/reales/consentimientos/persona-N-consentimiento.pdf`. Esa carpeta
>    es local e ignorada por Git.
> 3. Completar las 214 preguntas en su Moodle local (44 estilos, 72 personalidad,
>    98 CHASIDE) con la cuenta `persona-N`.
> 4. Correr:
>    `python docs/especificaciones/generar-perfil.py --usuario persona-N --salida perfiles/reales/persona-N-bruto.json`
> 5. Correr:
>    `python docs/especificaciones/evidencia-perfil.py --perfil perfiles/reales/persona-N-bruto.json`
> 6. Pegar en `experimentos/bitacora.md` la fila que imprime el paso 5 y avisar
>    en el issue #42 con "perfil persona-N extraido".
>
> El JSON no se comparte, no se envia por WhatsApp y no se sube a Git. Lo unico
> publico es la fila de la bitacora con el hash.

---

## 7. Checklist de cierre de E3-05

- [x] `perfiles/reales/consentimientos/persona-1-consentimiento.pdf` en custodia local.
- [x] `perfiles/reales/consentimientos/persona-2-consentimiento.pdf` en custodia local. Por diseno no esta en esa ruta: el repositorio de persona-2 esta dentro de OneDrive, asi que la copia firmada vive fuera de esa carpeta (declarado en #42).
- [x] `perfiles/reales/consentimientos/persona-3-consentimiento.pdf` en custodia local.
- [x] Tres filas de extraccion en `experimentos/bitacora.md` con SHA-256 (persona-1, persona-2 y persona-3).
- [x] `git ls-files perfiles` no lista ningun archivo de `perfiles/reales/` (verificado el 2026-11-11 sobre master).
- [x] Confirmado por persona-2 el 2026-11-11: `perfiles/reales/persona-2-bruto.json` no esta en OneDrive (ver 6.2 de los lineamientos).

Verificacion rapida:

```bash
git ls-files perfiles
git check-ignore -v perfiles/reales/persona-2-bruto.json
python docs/especificaciones/evidencia-perfil.py --perfil perfiles/reales/persona-1-bruto.json
```
