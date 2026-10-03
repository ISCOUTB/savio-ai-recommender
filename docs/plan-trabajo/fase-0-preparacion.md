# Fase 0 — Preparación del entorno y del repositorio

**Estado:** 🔄 En curso
**Issues asociados:** #1, #2, #10
**Milestone:** M1 / M2

---

## 🎯 Objetivo

Dejar listo el terreno de trabajo **antes de escribir código**: repositorio estructurado, Ollama instalado, modelos descargados, issues creados y mensaje de validación enviado a la profesora asesora.

---

## 📦 Issues de esta fase

### #1 — Instalar Ollama y descargar los modelos SLM · `infra`

**Pasos:**
1. Descargar e instalar Ollama desde https://ollama.com (instalador Windows).
2. Verificar instalación: `ollama --version`
3. Descargar modelos:
   ```bash
   ollama pull qwen2.5:1.5b
   ollama pull gemma2:2b
   ```
4. Prueba de humo (sin internet, para evidenciar ejecución local):
   ```bash
   ollama run qwen2.5:1.5b "Explica en dos líneas qué es la notación Big-O"
   ```

**Criterio de aceptación:**
- [ ] Ambos modelos responden correctamente en local
- [ ] Captura de terminal guardada como evidencia en esta fase

---

### #2 — Crear estructura del repositorio y README inicial · `docs` `infra`

**Estructura:**
```
├── docs/plan-trabajo/   (fases documentadas)
├── docs/arquitectura/   (diagramas — Fase 3)
├── poc_slm/             (scripts Python — Fase 1)
├── prompts/             (guardrails y escenarios — Fase 2)
└── benchmarks/          (mediciones — Fase 3)
```

**Criterio de aceptación:**
- [ ] Estructura creada con READMEs base por carpeta
- [ ] README principal con ficha del proyecto, equipo, estado de fases e inicio rápido

---

### #10 — Enviar mensaje de validación a la profesora asesora (Teams) · `docs`

**Mensaje aprobado (Fase 5 incluye la versión final lista para copiar):**

> Estimada Profesora, esperamos se encuentre muy bien. En seguimiento a nuestra reunión y atendiendo a sus valiosas recomendaciones sobre los casos de estudio y el modelo ARCS/IMMS, hemos consolidado el esquema preliminar de arquitectura y las variables de adaptación para el subsistema de Savio. Hemos preparado una propuesta de personalización basada en desempeño académico y recursos diferenciados para estilos de aprendizaje. Adjuntamos la síntesis de la arquitectura y los parámetros para su revisión. Agradecemos enormemente sus comentarios y sugerencias previas antes de nuestra sesión del sábado con el profesor Jairo. Quedamos muy atentos.

**Criterio de aceptación:**
- [ ] Mensaje enviado por Teams
- [ ] Respuesta/comentarios de la asesora documentados aquí (si aplica)

---

## ✅ Criterio de cierre de la fase

- [ ] Ollama operativo con Qwen 2.5 1.5B y Gemma 2 2B
- [ ] Repo estructurado y documentado
- [ ] Issues, labels y milestones creados y asignados por el líder
- [ ] Mensaje de Teams enviado

---

## 📝 Registro de ejecución

| Fecha | Acción | Evidencia | Responsable |
|---|---|---|---|
| _pendiente_ | Creación de estructura y documentación base | Commit inicial de Fase 0 | — |
| _pendiente_ | Instalación Ollama + modelos | Captura de terminal | — |
| _pendiente_ | Envío de Teams | Captura / confirmación | — |
