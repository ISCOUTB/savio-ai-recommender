# Sprint 6 — Verificacion pre-entrega y demo

**Entrega:** 1 — PoC Funcional
**Estado:** ✅ Completado
**Issues:** #13
**Depende de:** Sprints 1 a 5 completados

---

## 🎯 Objetivo

Verificar que todo lo comprometido en la Entrega 1 funciona de extremo a extremo y dejar listo el plan B (salidas pre-generadas) para la demostracion.

---

## 📋 Issues del sprint

### #13 — Checklist de verificacion y respaldos · `docs` `infra`

**Checklist de verificacion:**
- [ ] Ollama operativo y modelos precargados (inferencia de calentamiento ejecutada — la primera inferencia es siempre la mas lenta)
- [ ] Escenario A (tutoria reactiva) ejecutado correctamente de extremo a extremo
- [ ] Escenario B (visual vs textual) ejecutado correctamente de extremo a extremo
- [ ] Salidas pre-generadas guardadas en `prompts/salidas-respaldo/`
- [ ] Repositorio con codigo, README y benchmarks publicados y actualizados
- [ ] Material de presentacion completo
- [ ] Especificaciones de infraestructura listas (ver abajo)

---

## 🖥️ Especificaciones de infraestructura a solicitar

| Componente | Minimo | Recomendado |
|---|---|---|
| SO | Ubuntu Server 22.04 LTS | Ubuntu Server 22.04 LTS |
| RAM | 16 GB | 32 GB |
| CPU | 4 vCPUs | 8 vCPUs |
| GPU | Opcional (inferencia CPU) | NVIDIA 8–16 GB VRAM (CUDA) |
| Disco | 50 GB SSD | 100 GB NVMe SSD |

**Argumento tecnico:** los benchmarks del Sprint 4 evidencian el limite de la inferencia en CPU y justifican la aceleracion por GPU.

---

## ✅ Criterio de cierre del sprint

- [ ] Checklist completo verificado
- [ ] Plan B (salidas de respaldo) disponible
- [ ] Entrega 1 lista para ser presentada

---

## 📝 Registro de ejecucion

| Accion | Evidencia | Responsable | Estado |
|---|---|---|---|
| — | — | — | ⏳ |
