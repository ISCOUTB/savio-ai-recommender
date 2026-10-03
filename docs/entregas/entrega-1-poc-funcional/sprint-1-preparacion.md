# Sprint 1 — Preparación del entorno y repositorio

**Entrega:** 1 — PoC Funcional
**Estado:** 🔄 En curso
**Issues:** #1, #2

---

## 🎯 Objetivo

Dejar listo el terreno de trabajo **antes de escribir código**: repositorio estructurado y documentado, Ollama instalado, modelos SLM descargados e issues etiquetados por sprint.

---

## 📋 Issues del sprint

### #1 — Instalar Ollama y descargar los modelos SLM · `infra`

**Pasos:**
1. Descargar e instalar Ollama desde https://ollama.com
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
- [ ] Captura de terminal registrada como evidencia en este documento

---

### #2 — Crear estructura del repositorio y README inicial · `docs` `infra`

**Estructura:**
```
├── docs/entregas/       (entregas del proyecto, divididas en sprints)
├── docs/arquitectura/   (diagramas — Sprint 4)
├── poc_slm/             (scripts Python — Sprint 2)
├── prompts/             (guardrails y escenarios — Sprint 3)
└── benchmarks/          (mediciones — Sprint 4)
```

**Criterio de aceptación:**
- [ ] Estructura creada con READMEs base por carpeta
- [ ] README principal con ficha del proyecto, equipo, estado de entregas e inicio rápido

---

## ✅ Criterio de cierre del sprint

- [ ] Ollama operativo con Qwen 2.5 1.5B y Gemma 2 2B
- [ ] Repositorio estructurado y documentado
- [ ] Issues #1 y #2 cerrados

---

## 📝 Registro de ejecución

| Acción | Evidencia | Responsable | Estado |
|---|---|---|---|
| Creación de estructura y documentación base | Commit inicial del Sprint 1 | — | ✅ |
| Instalación Ollama + modelos | Captura de terminal | — | ⏳ |
