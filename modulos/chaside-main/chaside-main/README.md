# Bloque Exploración de Orientación Vocacional (Moodle)

El bloque **CHASIDE** permite a estudiantes responder un instrumento de **98 ítems (Sí/No)** y obtener un resultado orientativo por **áreas vocacionales**: **C, H, A, S, I, D, E**. El cálculo separa **Intereses** (70 ítems) y **Aptitudes** (28 ítems), generando un resumen ejecutivo (Top 1/Top 2), porcentajes, niveles y alertas de brecha.

Este repositorio incluye:
- Experiencia de estudiante con **guardado progresivo**, validación por página y reanudación.
- Herramientas docentes con **panel de administración**, vista de resultados por estudiante y **exportación CSV/JSON**.

## Contenido

- [Funcionalidades](#funcionalidades)
- [Recorrido Visual](#recorrido-visual)
- [Sección técnica (modelo de datos, cálculo, flujos, permisos, endpoints)](#sección-técnica)
- [Instalación](#instalación)
- [Operación y soporte](#operación-y-soporte)
- [Contribuciones](#contribuciones)
- [Equipo de desarrollo](#equipo-de-desarrollo)

---

## Funcionalidades

### Para estudiantes
- **Aplicación del test** (98 ítems, Sí/No) distribuido en **10 preguntas por página**.
- **Guardado progresivo** con autosave (tras inactividad) y reanudación desde la primera pregunta pendiente.
- **Validación por página** antes de avanzar o finalizar (resaltado y scroll a pendientes).
- **Resultados** con:
  - Top 1 y Top 2 de áreas.
  - Desglose Intereses/Aptitudes.
  - Porcentajes y niveles.
  - Alertas de brecha cuando intereses y aptitudes difieren significativamente.

### Para docentes / administradores
- **Vista del bloque** con accesos rápidos a reportes y gestión.
- **Panel de administración** con:
  - **Conteos** (matriculados, completados, en progreso, tasa de finalización),
  - **Tabla de participantes** (nombre, correo, estado, área principal).
  - Acceso a **vista individual** por estudiante.
  - Posibilidad de **eliminación** de resultados individuales.
  - **Agregados por área** (promedios/distribuciones) basados en estudiantes matriculados.
  - **Exportación** de resultados completados del curso en **CSV** o **JSON**.
- Opción para **mostrar/ocultar** las descripciones en el bloque principal **(oculto por defecto)**.
- **Controles de privacidad**: acceso restringido por capacidades y por matrícula en el curso.
---

## Recorrido Visual

### 1. Experiencia del Estudiante

**Acceso Intuitivo y Llamado a la Acción**

El recorrido comienza con una invitación clara y directa. Desde el bloque principal del curso, el estudiante puede visualizar su estado actual y acceder al test con un solo click, facilitando la participación sin fricciones.
<p align="center">
  <img src="https://github.com/user-attachments/assets/00ee44ce-6df6-413f-879d-e2a3f069b7b7" alt="Invitación al Test" width="528">
</p>

**Interfaz de Evaluación Optimizada**

Se presenta un entorno de respuesta limpio y libre de distracciones. La interfaz ha sido diseñada para priorizar la legibilidad y la facilidad de uso, permitiendo que el estudiante se concentre totalmente en el proceso de autodescubrimiento.
<p align="center">
  <img src="https://github.com/user-attachments/assets/d8c9fba5-1e8f-4a45-a7ce-2442246d4873" alt="Formulario del Test" width="650">
</p>

**Asistencia y Validación en Tiempo Real**

Para garantizar la integridad de los datos, el sistema implementa una validación inteligente. Si el usuario olvida alguna respuesta, el sistema lo guía visualmente mediante alertas en rojo y un desplazamiento automático hacia los campos pendientes, asegurando una experiencia sin errores.

<p align="center">
  <img src="https://github.com/user-attachments/assets/3af5441c-ca78-4792-ada5-33d0a533a5af" alt="Validación" width="650">
</p>

**Persistencia de Progreso y Continuidad**

Entendemos que el tiempo es valioso. Si el estudiante debe interrumpir su sesión, el sistema guarda automáticamente su avance. Al regresar, el bloque muestra el porcentaje de progreso y permite reanudar el test exactamente donde se dejó, resaltando visualmente la siguiente pregunta a responder.
	
<p align="center">
  <img src="https://github.com/user-attachments/assets/da62058b-cd95-41fd-a23b-04d294fc86db" alt="Progreso del Test" height="350">
  &nbsp;&nbsp;
  <img src="https://github.com/user-attachments/assets/d51e2a2e-e78e-461d-b97c-5cdf89ca1f68" alt="Continuar Test" height="350">
</p>

**Confirmación de Envío Pendiente**
Si el estudiante ha completado las 44 preguntas pero aún no ha procesado el envío, el bloque muestra una notificación clara y amigable, invitándolo a formalizar la entrega y conocer su orientación vocacional.

<p align="center">
  <img src="https://github.com/user-attachments/assets/f6695cfb-5d47-4140-848c-f91115f2eb9a" alt="Confirmación de Test Completado" width="528">
</p>

**Análisis de Perfil y Recomendaciones Personalizadas**

Al concluir, el estudiante recibe un diagnóstico de su orientación vocacional. La presentación incluye un resumen ejecutivo con las áreas principales, alertas de brecha, todo acompañado de pequeñas recomendaciones. Por último tiene la opción de ver un resultado detallado con toda la información completa.

<p align="center">
  <img src="https://github.com/user-attachments/assets/b678e63c-146b-4e0f-8ed5-fcd0cde4455e" alt="Resultados del Estudiante - Bloque" width="528">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/d3e9e14c-59fc-4198-9134-eca112bf9021" alt="Resultados del Estudiante - Page" width="800">
</p>

### 2. Experiencia del Profesor

**Dashboard de Control Rápido (Vista del Bloque)**

El profesor cuenta con una vista ejecutiva desde el bloque, donde puede monitorizar métricas clave, además de acceder a funciones avanzadas de administración.

<p align="center">
  <img src="https://github.com/user-attachments/assets/3b6b253e-71af-47de-a899-dc32e700b345" alt="Bloque del Profesor" width="528">
</p>

**Centro de Gestión y Analíticas**

Un panel de administración que centraliza el seguimiento grupal. Permite visualizar quiénes han completado el proceso, quiénes están en curso y gestionar los resultados colectivos para adaptar la estrategia pedagógica del aula.

<p align="center">
  <img src="https://github.com/user-attachments/assets/97043093-a093-4389-96ff-b891de215a39" alt="Panel de Administración" width="800">
</p>

**Seguimiento Individualizado y Detallado**

El docente puede profundizar en la orientación vocacional específica de cada estudiante. Esta vista permite comprender las necesidades particulares de cada alumno y las recomendaciones sugeridas por el sistema para brindar un apoyo docente más humano y dirigido.

- **Nota:** Esta vista es la misma que la del estudiante, pero accesible por el profesor para cualquier alumno del curso.

---

## Sección técnica

Esta sección describe el comportamiento **tal como está implementado** en el bloque (cálculo, persistencia, flujos y controles de acceso).

### 1) Estructura del test y codificación de respuestas

- Total de preguntas: **98**.
- Opciones por pregunta: **Sí/No**.
- Paginación: **10 preguntas por página (excepto la última que tiene 8)**.
- Persistencia en base de datos:
  - Se almacena una columna por pregunta: `q1` … `q98`.
  - Valores: **Sí = 1**, **No = 0**.

### 2) Mapeo oficial de preguntas a áreas (Intereses vs Aptitudes)

El mapeo se centraliza en `\block_chaside\facade::get_question_mapping()` y separa:

- **Intereses**: 70 ítems (10 por área).
- **Aptitudes**: 28 ítems (4 por área).

Listas por área (tal como están definidas en el `facade`):

- **C** (Intereses): 1, 12, 20, 53, 64, 71, 78, 85, 91, 98 | (Aptitudes): 2, 15, 46, 51
- **H** (Intereses): 9, 25, 34, 41, 56, 67, 74, 80, 89, 95 | (Aptitudes): 30, 63, 72, 86
- **A** (Intereses): 3, 11, 21, 28, 36, 45, 50, 57, 81, 96 | (Aptitudes): 22, 39, 76, 82
- **S** (Intereses): 8, 16, 23, 33, 44, 52, 62, 70, 87, 92 | (Aptitudes): 4, 29, 40, 69
- **I** (Intereses): 6, 19, 27, 38, 47, 54, 60, 75, 83, 97 | (Aptitudes): 10, 26, 59, 90
- **D** (Intereses): 5, 14, 24, 31, 37, 48, 58, 65, 73, 84 | (Aptitudes): 13, 18, 43, 66
- **E** (Intereses): 17, 32, 35, 42, 49, 61, 68, 77, 88, 93 | (Aptitudes): 7, 55, 79, 94

### 3) Cálculo de puntajes, porcentajes, niveles y “Top áreas”

El cálculo se realiza a partir de las respuestas con valor **1**:

- `calculate_detailed_scores()` computa, por área:
  - `interes_score` (0–10)
  - `aptitud_score` (0–4)
- `calculate_percentages()` deriva:
  - `pct_interes = 100 * interes_score / 10`
  - `pct_aptitud = 100 * aptitud_score / 4`
  - `pct_total = 100 * (interes_score + aptitud_score) / 14`

Niveles (según `pct_total`) vía `determine_levels()`:

- **Alto**: $pct\_total \ge 80$ → `level_alto`
- **Medio**: $60 \le pct\_total < 80$ → `level_medio`
- **Emergente**: $40 \le pct\_total < 60$ → `level_emergente`
- **Bajo**: $pct\_total < 40$ → `level_bajo`

Brecha Intereses vs Aptitudes (umbral 20 puntos porcentuales) vía `detect_gaps()`:

- `gap_interest_higher`: `pct_interes - pct_aptitud >= 20`
- `gap_aptitude_higher`: `pct_interes - pct_aptitud <= -20`
- `gap_balanced`: en caso contrario

Selección de “Top áreas” (desempate oficial) vía `get_top_areas_v2()`:

1. Mayor **total_score** (interés + aptitud)
2. Mayor **aptitud_score**
3. Menor brecha absoluta $|interes\_score - aptitud\_score|$
4. Orden alfabético por área

`generate_results_json()` integra todo lo anterior para construir el resumen ejecutivo y la tabla detallada que consumen las vistas.

### 4) Guardado progresivo, navegación y reanudación

El formulario se implementa en `view.php` con POST al mismo script, usando `action`:

- `autosave`: guardado silencioso en segundo plano mediante `fetch()`.
- `next` / `previous`: navegación por páginas guardando el estado.
- `finish`: validación completa y cierre del test.

Comportamientos clave:

- Autosave: se ejecuta tras **400 milisegundos** desde el último cambio.
- Validación por página en cliente: al intentar **Siguiente** o **Finalizar**, marca tarjetas “unanswered” y hace scroll a la primera pendiente.
- Validación final en servidor: no permite finalizar si falta alguna respuesta; redirige a la página donde está la primera pregunta sin responder.
- Anti-salto de páginas: el servidor calcula una **página máxima permitida** a partir del progreso guardado.
- No retake: si `is_completed = 1`, el usuario es redirigido directamente a resultados.
- Reanudación: al continuar un test incompleto, se hace scroll y resaltado temporal a la primera pregunta pendiente (verde). Si ya está todo respondido pero falta “Finalizar”, puede redirigir y hacer scroll al botón de finalización.

### 5) Modelo de datos (tabla principal)

Tabla: `block_chaside_responses`

- `userid` (índice **único**): el test se almacena **globalmente por usuario**.
- `is_completed`: 0 (en progreso) / 1 (completado).
- `q1..q98`: respuestas individuales.
- Totales por área: `score_c`, `score_h`, `score_a`, `score_s`, `score_i`, `score_d`, `score_e`.
- Trazabilidad: `timecreated`, `timemodified`.

Implicación importante:

- Al ser **único por usuario** y sin campo de curso, el resultado puede reutilizarse entre cursos. Las vistas docentes filtran participantes por **matrícula en el curso**, pero el registro del test pertenece al usuario a nivel global.

### 6) Vistas, endpoints y exportación

**Estudiante**

- Formulario del test: `view.php?courseid=<courseid>`
- Resultados (propios): `view_results.php?courseid=<courseid>`

**Docente / Administrador**

- Panel de administración del curso: `admin_view.php?courseid=<courseid>`
- Resultados de un estudiante: `view_results.php?courseid=<courseid>&userid=<userid>`
- Exportación CSV/JSON: `export.php?courseid=<courseid>&format=csv|json`
- Eliminación de respuesta (con confirmación): `delete_response.php?courseid=<courseid>&id=<responseid>`

### 7) Permisos (capabilities) y controles de acceso

Capacidades definidas por el bloque:

- `block/chaside:take_test` (estudiante): permite tomar el test.
- `block/chaside:viewreports` (docente/manager): permite ver reportes, panel y resultados de otros usuarios.
- `block/chaside:manage_responses` (docente/manager): permite exportar resultados del curso.
- `block/chaside:addinstance` / `block/chaside:myaddinstance`: gestión de instancias del bloque.

Controles adicionales implementados:

- Escrituras protegidas con `sesskey` (campo en formulario y confirmación en eliminación).
- `view_results.php` restringe ver resultados de terceros a `viewreports` (si no, redirección al curso).
- Exportación restringida a `manage_responses`.
- Filtrado defensivo en exportación: excluye site admins y usuarios con capacidades de reportes/gestión aunque estén matriculados.

---

## Instalación

1. Descargar el plugin desde las *releases* del repositorio oficial: https://github.com/ISCOUTB/chaside/releases
2. En Moodle (como administrador):
   - Ir a **Administración del sitio → Extensiones → Instalar plugins**.
   - Subir el archivo ZIP.
   - Completar el asistente de instalación.
3. En un curso, agregar el bloque **Exploración de Orientación Vocacional** desde el selector de bloques.

---

## Operación y soporte

### Consideraciones de despliegue

- Compatibilidad declarada: Moodle **4.0+**.

### Resolución de problemas (rápido)

- **El estudiante no ve el test**: validar que tenga la capacidad `block/chaside:take_test` en el contexto del curso.
- **El docente no ve reportes o resultados de otros**: validar `block/chaside:viewreports`.
- **No puede exportar**: validar `block/chaside:manage_responses`.
- **El progreso no se guarda**: revisar que el POST incluya `sesskey` válido y que no haya bloqueos del navegador/red.

---

## Contribuciones

¡Las contribuciones son bienvenidas! Si deseas mejorar este bloque, por favor sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama para tu característica o corrección de errores.
3. Realiza tus cambios y asegúrate de que todo funcione correctamente.
4. Envía un pull request describiendo tus cambios.

---

## Equipo de desarrollo

- Jairo Enrique Serrano Castañeda
- Yuranis Henriquez Núñez
- Isaac David Sánchez Sánchez
- Santiago Andrés Orejuela Cueter
- María Valentina Serna González

<div align="center">
<strong>Desarrollado con ❤️ para la Universidad Tecnológica de Bolívar</strong>
</div>
