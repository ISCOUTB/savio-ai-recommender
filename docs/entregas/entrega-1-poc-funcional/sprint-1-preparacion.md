# Sprint 1 — Preparacion del entorno y repositorio

**Entrega:** 1 — PoC Funcional  
**Estado:** ✅ Completado  
**Issues:** #1, #2  

---

## 🎯 Objetivo

Dejar listo el terreno de trabajo **antes de escribir codigo**: repositorio estructurado y documentado, Ollama instalado, modelos SLM descargados e issues etiquetados por sprint.

---

## 📋 Issues del sprint

### #1 — Instalar Ollama y descargar los modelos SLM · `infra`

**Pasos:**
1. Descargar e instalar Ollama desde https://ollama.com
2. Verificar instalacion: `ollama --version`
3. Descargar modelos:
   ```bash
   ollama pull qwen2.5:1.5b
   ollama pull gemma2:2b
   ollama pull qwen2.5:3b
   ```
4. Prueba de humo (sin internet, para evidenciar ejecucion local):
   ```bash
   ollama run qwen2.5:1.5b "Explica en dos lineas que es la notacion Big-O"
   ```

**Criterio de aceptacion:**
- [x] Modelos responden correctamente en local
- [x] Captura de terminal registrada como evidencia en este documento

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

**Criterio de aceptacion:**
- [x] Estructura creada con READMEs base por carpeta
- [x] README principal con ficha del proyecto, equipo, estado de entregas e inicio rapido

---

## ✅ Criterio de cierre del sprint

- [x] Ollama operativo con Qwen 2.5 1.5B, Gemma 2 2B y Qwen 2.5 3B
- [x] Repositorio estructurado y documentado
- [x] Issues #1 y #2 cerrados

---

## 📝 Registro de ejecucion

| Accion | Evidencia | Responsable | Estado |
|---|---|---|---|
| Creacion de estructura y documentacion base | Commit inicial del Sprint 1 | Persona 1 | ✅ |
| Instalacion Ollama + descarga de modelos | Salida de `ollama list` (abajo) | Persona 1 | ✅ |

### Evidencia de verificacion (`ollama list`):

```text
$ ollama list
NAME            ID              SIZE      MODIFIED
gemma2:2b       8ccf136fdd52    1.6 GB    Reciente
qwen2.5:1.5b    65ec06548149    986 MB    3 days ago
qwen2.5:3b      357c53fb659c    1.9 GB    3 days ago
```
