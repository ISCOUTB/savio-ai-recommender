# Guion de demostracion E3-10: backend de interpretacion en CPU

Demostracion por consola, sin frontend (directriz 6), del flujo completo:
puntajes brutos de los 3 tests -> SLM ajustado y cuantizado en CPU -> perfil
integrado validado -> metricas SMART. Duracion estimada: 10 minutos.

Todos los comandos se ejecutan en PowerShell desde la raiz del repositorio.

---

## 0. Preparacion (antes de la sesion)

1. **Modelo:** descargar el GGUF `Q4_K_M` de E3-08 desde
   `https://huggingface.co/ssebatiaan/perfil-ia-e3-qwen2.5-1.5b-qlora` (repositorio
   privado; pedir acceso a Persona 3) y guardarlo como
   `modelos/perfil-ia-e3-q4_k_m.gguf` (`modelos/` esta en `.gitignore`).
2. **Importarlo en Ollama** (nombre estable por hash, `savio-e3-2531a770`):

   ```powershell
   python poc_slm/importar_gguf.py --gguf modelos/perfil-ia-e3-q4_k_m.gguf
   ```

3. **Forzar CPU.** El Modelfile de `importar_gguf.py` no fija `num_gpu 0`
   (hallazgo de E3-08). En un equipo con GPU NVIDIA, cerrar la app de Ollama y
   levantar el servidor sin GPU visible:

   ```powershell
   $env:CUDA_VISIBLE_DEVICES = "-1"; ollama serve
   ```

   En un equipo sin GPU dedicada no hace falta. `evaluar-fidelidad.py` fuerza
   `num_gpu = 0` en cada solicitud, asi que sus metricas son de CPU en ambos casos.
4. **Respaldo:** si la inferencia en vivo falla, se muestran las salidas ya
   medidas (seccion 5). No se editan a mano.

---

## 1. Entrada: puntajes brutos sin reescalar (OE1)

```powershell
python docs/especificaciones/validar-perfiles-brutos.py perfiles/brutos/ejemplo-perfil-bruto-dominante.json perfiles/brutos/ejemplo-perfil-bruto-brecha.json perfiles/brutos/ejemplo-perfil-bruto-plano.json
```

Mostrar uno de los JSON: CHASIDE `0-14` (interes + aptitud), Felder-Silverman
`0-11` por polo y personalidad `0-9` por polo. No hay escala `1.0-5.0` ni
`autonomia` (directriz 2).

## 2. Contrato de inferencia (sin modelo)

```powershell
python poc_slm/interpretador.py --perfil perfiles/brutos/ejemplo-perfil-bruto-dominante.json --gguf modelos/perfil-ia-e3-q4_k_m.gguf --dry-run
```

Muestra el par system/user, que es identico al del entrenamiento de E3-08.

## 3. Inferencia en CPU con los 3 perfiles contrastantes (OE2)

```powershell
foreach ($p in "dominante", "brecha", "plano") {
  python poc_slm/interpretador.py --perfil "perfiles/brutos/ejemplo-perfil-bruto-$p.json" --gguf modelos/perfil-ia-e3-q4_k_m.gguf --salida-dir salidas/e3/ajustado
}
ollama ps
```

Que mirar:

- las 4 secciones en orden y el aviso no clinico al final;
- los puntajes citados son los de la entrada;
- `ollama ps` muestra `100% CPU`;
- el resumen imprime latencia y tokens/s (meta OE3: `<= 60 s` por perfil).

Perfiles: `dominante` (preferencias marcadas y area CHASIDE alta), `brecha`
(interes alto con aptitud baja) y `plano` (diferencias minimas: el texto no
debe personalizar).

## 4. Metricas SMART (OE3)

```powershell
# Calibracion: el ground truth del Teacher sobre el split de 28
python docs/especificaciones/evaluar-fidelidad.py referencia

# Modelo ajustado en CPU sobre el mismo split (aprox. 15 min; puede mostrarse el reporte ya medido)
python docs/especificaciones/evaluar-fidelidad.py generar --gguf modelos/perfil-ia-e3-q4_k_m.gguf
```

El evaluador imprime la fidelidad global (meta `>= 85 %`), las cuatro
dimensiones, las alucinaciones numericas, la latencia, los tokens/s, la RAM
pico y la VRAM pico.

## 5. Evidencia de respaldo (ya medida)

| Evidencia | Ruta |
|---|---|
| Linea base sin ajustar (3 fixtures, backend E3-07) | `salidas/e3/base/` |
| Referencia Teacher (split de 28) | `salidas/e3/eval/teacher/reporte.json` |
| Modelo base en CPU (split de 28) | `benchmarks/resultados/intel-i5-12500h-rtx-3050/e3-09/qwen2.5_1.5b/` (corrida en curso) |
| Modelo ajustado en CPU (split de 28) | `benchmarks/resultados/<equipo>/e3-09/savio-e3-2531a770/` (pendiente: la corre quien tenga el GGUF) |
| Ajuste QLoRA, GGUF y prueba de humo | Fila de E3-08 en `experimentos/bitacora.md` |

---

## 6. Checklist de las 8 directrices del docente

Verificacion contra la seccion 1 del [README de la entrega](README.md).

| # | Directriz | Como se demuestra | Evidencia | Estado |
|---|---|---|---|---|
| 1 | Caso concreto: interpretacion psicologica y vocacional a partir de pruebas estandarizadas | El sistema solo recibe los puntajes de los 3 tests y produce el perfil integrado | Pasos 1 y 3 | Cumple |
| 2 | Escalas validadas intactas (puntajes brutos, sin `1.0-5.0` ni `autonomia`) | Contrato bruto validado; el backend rechaza escalas y decimales; el evaluador mide 0 alucinaciones numericas | [perfil-bruto-psicometrico.schema.json](../../especificaciones/perfil-bruto-psicometrico.schema.json), paso 4 | Cumple en el contrato; la exactitud del modelo ajustado se reporta en el paso 4 |
| 3 | SLM especializado; LLM de frontera solo como Teacher | Corpus de 150 interpretaciones de `openai/gpt-6.1-sol`; Qwen2.5-1.5B ajustado con QLoRA | [manifiesto_generacion.json](../../../datos/corpus/manifiesto_generacion.json), fila E3-08 de la bitacora | Cumple |
| 4 | Entrenamiento en la nube y despliegue cuantizado en CPU sin VRAM | GGUF `Q4_K_M` (986 MB) en CPU con `num_gpu 0`; 0 MB de VRAM | Paso 3 y reporte E3-09 | Cumple en el despliegue. El ajuste corrio en la RTX 3050 local como fallback de Colab (documentado en la bitacora) |
| 5 | Sin sobreingenieria | Scripts de linea de comandos en Python; sin microservicios ni nube propia | `poc_slm/`, `docs/especificaciones/` | Cumple |
| 6 | Backend antes que frontend | Toda la demo es por consola; no hay interfaz grafica | Este guion | Cumple |
| 7 | Objetivos SMART medidos | Fidelidad `>= 85 %`, guardrails 100 %, latencia `<= 60 s` y RAM `<= 2.5 GB` medidos con script reproducible | [evaluar-fidelidad.py](../../especificaciones/evaluar-fidelidad.py); informe de cierre pendiente de la corrida del modelo ajustado | En curso |
| 8 | Acuerdos operativos: repositorio con avance por issues y bitacora | Issues E3-01 a E3-10, PR por integrante, bitacora con hashes | `experimentos/bitacora.md`, issues del milestone | Cumple |
