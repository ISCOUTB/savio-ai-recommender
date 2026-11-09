# Curso del profesor: corpus de adaptacion del SLM (CUR-01)

Material docente de la asignatura **ARQUITECTURA DE SOFTWARE - METACURSO 202620**, usado como corpus de adaptacion del SLM. Es un corpus distinto al de Entrega 3 (`datos/corpus/`, perfiles sinteticos psicometricos): no se mezclan.

## Fuente

| Dato | Valor |
| :--- | :--- |
| Curso en Moodle | id 3, restaurado desde el backup enviado por el docente |
| Base de datos | contenedor `moodle-db-1` (mariadb 10.11) |
| Moodle | contenedor `moodle-moodle-1` (bitnamilegacy/moodle 5.0.2), moodledata en `/bitnami/moodledata` |
| Backup | `copia_de_seguridad-moodle2-course-18890-arquitectura_de_software_-_metacurso_202620-20261105-1057-nu (1).mbz` (54,1 MB), en la raiz del repo, no versionado |
| Permiso de uso | Concedido por el docente para este proyecto |

## Inventario medido (2026-11-09)

- 18 secciones.
- Actividades: 20 recursos, 18 tareas, 17 etiquetas, 10 foros, 6 URL, 1 libro, 1 pagina, 1 feedback.
- Archivos con contenido: 24 (20 de recurso con 20,2 MB, 1 video de 34,2 MB, 3 PNG de 3,2 MB).
- No hay presentaciones PPTX: el material es PDF y HTML.

## Criterios de seleccion

- Entran: recursos, paginas, libros y URL con contenido de la materia.
- Salen: foros y tareas (contienen mensajes y entregas de estudiantes), insignias, bloques, usuarios y bancos de preguntas.
- Salen por formato: video MP4 y PNG (no convertibles a texto en este flujo).

## Estado

Restaurado en Moodle. Sin extraer ni convertir. Las fases siguen el milestone "Curso Arquitectura - corpus y adaptacion del SLM" (CUR-02 a CUR-09).

## Archivos de esta carpeta

Versionados en git:
- `README.md`: este documento.
- `inventario.json`, `extraccion.json`, `reporte_conversion.json`, `reporte_limpieza.json`: reportes sin texto del curso.
- Scripts en `scripts/`: `inventario_curso_moodle.py`, `extraer_curso_moodle.py`, `convertir_curso_markdown.py` y `limpiar_corpus_curso.py`.

Solo locales (ignorados por git, se regeneran con los scripts desde el backup del profesor):
- `crudos/`: copias de los archivos y textos exportados de paginas y libros.
- `markdown/`: texto del curso convertido a Markdown.
- `corpus_curso.jsonl`: corpus fragmentado para el ajuste del modelo.

## Tratamiento de datos personales

Los correos de terceros que aparecen en el material se reemplazan por `[correo]` en la conversion y en la limpieza. La verificacion se hace sobre el texto decodificado del corpus, no sobre el JSON crudo.
