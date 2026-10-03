# Sprint 6 — Verificación pre-entrega y demo

**Entrega:** 1 — PoC Funcional
**Estado:** ⏳ Pendiente
**Issues:** #13
**Depende de:** Sprints 1 a 5 completados

---

## 🎯 Objetivo

Verificar que todo lo comprometido en la Entrega 1 funciona de extremo a extremo y dejar listo el plan B (salidas pre-generadas) para la demostración.

---

## 📋 Issues del sprint

### #13 — Checklist de verificación y respaldos · `docs` `infra`

**Checklist de verificación:**
- [ ] Ollama operativo y modelos precargados (inferencia de calentamiento ejecutada — la primera inferencia es siempre la más lenta)
- [ ] Escenario A (tutoría reactiva) ejecutado correctamente de extremo a extremo
- [ ] Escenario B (visual vs textual) ejecutado correctamente de extremo a extremo
- [ ] Salidas pre-generadas guardadas en `prompts/salidas-respaldo/`
- [ ] Repositorio con código, README y benchmarks publicados y actualizados
- [ ] Material de presentación completo
- [ ] Especificaciones de infraestructura listas (ver abajo)

---

## 🖥️ Especificaciones de infraestructura a solicitar

| Componente | Mínimo | Recomendado |
|---|---|---|
| SO | Ubuntu Server 22.04 LTS | Ubuntu Server 22.04 LTS |
| RAM | 16 GB | 32 GB |
| CPU | 4 vCPUs | 8 vCPUs |
| GPU | Opcional (inferencia CPU) | NVIDIA 8–16 GB VRAM (CUDA) |
| Disco | 50 GB SSD | 100 GB NVMe SSD |

**Argumento técnico:** los benchmarks del Sprint 4 evidencian el límite de la inferencia en CPU y justifican la aceleración por GPU.

---

## ✅ Criterio de cierre del sprint

- [ ] Checklist completo verificado
- [ ] Plan B (salidas de respaldo) disponible
- [ ] Entrega 1 lista para ser presentada

---

## 📝 Registro de ejecución

| Acción | Evidencia | Responsable | Estado |
|---|---|---|---|
| — | — | — | ⏳ |
