# Guia de entrenamiento del SLM en Google Colab (E3-08)

**Entrega:** [Entrega 3 - Interpretacion Psicometrica](README.md)
**Issue:** E3-08 (`#44`) - Ajustar/destilar SLM en Hugging Face y cuantizar a GGUF para CPU
**Notebook:** [notebook-e3-08-sft-qlora.ipynb](notebook-e3-08-sft-qlora.ipynb)
**Dependencias:** [../../../requirements-entrenamiento.txt](../../../requirements-entrenamiento.txt)
**Prerequisito bloqueante:** E3-06 (`#43`) - corpus *ground truth* validado
**Ejemplo ejecutable:** [../../../datos/corpus/ejemplo_mini.jsonl](../../../datos/corpus/ejemplo_mini.jsonl) (8 registros)

**Estado:** Documentado

---

## 1. Que se entrena y que no

| Se hace | No se hace |
|---|---|
| SFT (fine-tuning supervisado) con LoRA/QLoRA sobre un modelo ya entrenado | Preentrenar un modelo desde cero |
| Se ensena el formato: puntajes brutos -> informe de 4 secciones | Se ensena psicologia nueva al modelo |
| Se ajustan ~1 por ciento de los parametros (adaptadores) | Se reescriben los pesos base |
| Se usa corpus sintetico | Se usan datos reales de estudiantes (prohibido por [lineamientos](lineamientos-datos-psicometricos.md)) |
| Se exporta GGUF `Q4_K_M` para CPU | Se depende de GPU al desplegar |

**Modelo base:** `Qwen/Qwen2.5-1.5B-Instruct` (licencia Apache-2.0; verificar la model card antes de publicar).
**Plan B si falta memoria:** `Qwen/Qwen2.5-0.5B-Instruct`, 2 epocas y `MAX_LEN=1536`.

El modelo no aprende a diagnosticar: aprende a **ordenar y correlacionar** los puntajes que recibe, con el estilo y la estructura de las respuestas del corpus. Por eso la calidad del corpus manda mas que el numero de epocas.

---

## 2. Prerrequisitos

| Requisito | Como se cumple | Si falta |
|---|---|---|
| Corpus de 150 registros validado | Ver seccion 3 | Usar `ejemplo_mini.jsonl` (8 registros) solo para aprender el flujo |
| GPU en Colab | `Entorno de ejecucion > Cambiar tipo de entorno > T4 GPU` | Sin GPU el entrenamiento no es viable |
| Cuenta Google | Colab gratis alcanza | Si se agota la cuota, repetir en la cuenta de otro integrante |
| Gate de privacidad en verde | `validar-corpus-anonimizado.py` | Corregir el corpus antes de entrenar |
| Cuenta Hugging Face (opcional) | Solo para publicar el modelo | El GGUF se puede descargar sin publicar |

Tiempos medidos en el flujo completo, con 150 registros y 3 epocas en T4: instalacion 3 min, carga 2 min, entrenamiento 15 a 25 min, merge y GGUF 15 min.

---

## 3. El corpus (E3-06)

### 3.1 Contrato exacto

Cada linea de `datos/corpus/corpus.jsonl` es un objeto con estos campos:

```json
{"id": "SINT-001", "origen": "sintetico",
 "chaside": {"C": {"interes": 3, "aptitud": 1, "total": 4}, "H": {"interes": 5, "aptitud": 2, "total": 7},
             "A": {"interes": 3, "aptitud": 1, "total": 4}, "S": {"interes": 2, "aptitud": 1, "total": 3},
             "I": {"interes": 9, "aptitud": 4, "total": 13}, "D": {"interes": 2, "aptitud": 1, "total": 3},
             "E": {"interes": 8, "aptitud": 3, "total": 11}},
 "ils": {"activo": 8, "reflexivo": 3, "sensitivo": 4, "intuitivo": 7,
         "visual": 9, "verbal": 2, "secuencial": 6, "global": 5},
 "personalidad": {"extraversion": 3, "introversion": 7, "sensing": 4, "intuition": 8,
                  "thinking": 7, "feeling": 3, "judging": 8, "perceptive": 2},
 "instruction": "Interpreta los puntajes brutos y genera el perfil integrado en cuatro secciones.",
 "output": "## 1. Estilos de aprendizaje ..."}
```

Reglas que el validador exige (no son sugerencias):

1. `id` cumple el patron `SINT-###` y `origen` es exactamente `sintetico`.
2. CHASIDE: 7 areas (`C, H, A, S, I, D, E`), `interes` 0-10, `aptitud` 0-4, `total` 0-14 y `total = interes + aptitud`.
3. ILS: los 8 polos, 0-11 cada uno, y cada par suma exactamente 11 (`activo+reflexivo`, `sensitivo+intuitivo`, `visual+verbal`, `secuencial+global`).
4. Personalidad: los 8 polos, 0-9 cada uno.
5. Sin correos, telefonos, `@usuario`, codigos `T########` ni numeros de 6 o mas digitos.
6. `output` debe incluir el aviso no clinico canonico de [guardrail_etico.py](../../../poc_slm/guardrail_etico.py).

### 3.2 Cuantos y como se reparten

- Minimo **150** registros: **120 entrenamiento** y **30 evaluacion** (80/20 sin fuga).
- El notebook hace el corte de forma determinista con `sha256(id) % 5 == 0`, asi el mismo corpus siempre produce el mismo split.
- Los 3 perfiles reales **no entran al corpus**: se usan en E3-09 y E3-10.

### 3.3 Como generarlos (plantilla para el LLM maestro)

Se le pide al LLM de frontera un lote de 10 a 15 registros por vez, con este mensaje:

```
Actua como psicometrista. Te doy puntajes brutos de tres instrumentos y la
literatura oficial de cada uno. Devuelve SOLO un arreglo JSON con N objetos,
cada uno con: id SINT-###, origen "sintetico", chaside (7 areas con interes
0-10, aptitud 0-4 y total = interes + aptitud), ils (8 polos 0-11, cada par
suma 11), personalidad (8 polos 0-9), instruction fija y output en 4 secciones
(estilos, personalidad, vocacional, sintesis) que cite los puntajes recibidos,
sin diagnosticos, sin etiquetas MBTI y terminando con este aviso literal:
"Este perfil es un apoyo para el diagnostico inicial y fue generado con
asistencia de IA. No reemplaza al profesional ni constituye un diagnostico
psicologico."
No inventes escalas distintas a las indicadas. No incluyas nombres ni datos
personales.
```

### 3.4 Tabla de cobertura (evita 150 variaciones del mismo perfil)

| Eje | Cobertura minima |
|---|---|
| CHASIDE | Al menos 2 perfiles por area dominante (7 areas), y 6 con dominancia compartida |
| Brecha interes/aptitud | Al menos 20 registros con interes alto y aptitud baja (caso borde de E2) |
| Perfil plano | Al menos 10 registros sin dominancia (todas las areas parejas) |
| ILS | Al menos 1 perfil por polo dominante en cada una de las 4 dimensiones |
| Personalidad | Al menos 1 perfil por polo dominante en cada una de las 4 dimensiones |
| Estructura | 100 por ciento de los `output` con las 4 secciones y el aviso |

### 3.5 Validacion (gate obligatorio)

```bash
python docs/especificaciones/validar-corpus-anonimizado.py --entrada datos/corpus/corpus.jsonl --manifiesto datos/corpus/manifiesto.json
```

Errores frecuentes y su causa:

| Mensaje | Causa | Solucion |
|---|---|---|
| `id debe cumplir el patron SINT-###` | ID con otro formato | Renumerar `SINT-001` en adelante |
| `origen debe ser 'sintetico'` | Copiado de un perfil real | Regenerar el registro como sintetico |
| `ils.activo + ils.reflexivo debe sumar 11` | Polo calculado a mano | Calcular el complemento como `11 - valor` |
| `chaside.X.total no coincide` | Total escrito suelto | Recalcular `interes + aptitud` |
| `output: falta el aviso no clinico` | Se copio la plantilla sin el aviso | Pegar el texto canonico de `guardrail_etico.py` |
| `posible identificador numerico` | Un numero de 6 digitos en el texto | Quitar el numero |

---

## 4. Preparar Colab

1. Abrir [notebook-e3-08-sft-qlora.ipynb](notebook-e3-08-sft-qlora.ipynb) en Colab (`Archivo > Subir notebook`).
2. `Entorno de ejecucion > Cambiar tipo de entorno > T4 GPU`.
3. Correr las celdas en orden. La celda 2 verifica GPU y version de PyTorch; si dice `CUDA disponible: False`, el tipo de entorno no se aplico.
4. La celda 4 instala [../../../requirements-entrenamiento.txt](../../../requirements-entrenamiento.txt). Si Colab pide reiniciar el entorno, reiniciar y volver a correr desde la celda 2 (las variables se pierden).

---

## 5. Carga del modelo

| Decision | Valor | Motivo |
|---|---|---|
| Cuantizacion | `load_in_4bit`, `nf4`, doble cuantizacion | 1.5B en 4-bit ocupa ~1.2 GB de VRAM; deja espacio para activaciones |
| Tipo de calculo | `float16` | La T4 no soporta `bfloat16` |
| LoRA `r` / `alpha` | 16 / 32 | Suficiente para cambiar formato con 150 ejemplos |
| `target_modules` | `q, k, v, o, gate, up, down` | Cubre atencion y MLP; solo `q,v` aprende menos |
| `dropout` | 0.05 | Regulariza un corpus pequeno |

El notebook imprime el porcentaje de parametros entrenables. Debe quedar entre 1 y 2 por ciento del total.

---

## 6. Formato de entrenamiento y mascara de loss

Cada registro se convierte en una conversacion con tres turnos: `system` (contrato de 4 secciones y prohibicion de diagnosticos), `user` (los puntajes brutos) y `assistant` (el `output` del corpus). Se aplica el `chat_template` del tokenizer para no inventar un formato propio.

**La mascara de loss es obligatoria:** los tokens del `system` y del `user` se marcan con `-100` para que el modelo **no** aprenda a generar la pregunta. Solo se calcula perdida sobre el informe. Sin esto, el modelo aprende a repetir los puntajes y la calidad cae.

---

## 7. Hiperparametros

| Parametro | Valor | Por que |
|---|---|---|
| `num_train_epochs` | 3 (150 registros) / 1 (ejemplo mini) | Con 150 ejemplos, mas de 3 epocas memoriza |
| `learning_rate` | `2e-4` | Estandar para LoRA (10 veces la tasa de un ajuste completo) |
| `per_device_train_batch_size` | 1 | T4 con `max_length` 2048 |
| `gradient_accumulation_steps` | 8 | Batch efectivo 8 sin pedir mas VRAM |
| `max_length` | 2048 | Los informes de 4 secciones rondan 700 a 1200 tokens |
| `warmup_ratio` | 0.1 | Evita pasos grandes al inicio |
| `lr_scheduler_type` | `cosine` | Bajada suave al final |
| `fp16` | `True` | T4 |
| `gradient_checkpointing` | `True` | Ahorra VRAM a cambio de ~20 por ciento de tiempo |
| `optim` | `paged_adamw_8bit` | Optimizador de 8 bits, evita picos de memoria |
| `seed` | 42 | Reproducibilidad |

---

## 8. Entrenamiento: como saber si va bien

| Senal | Valor esperado | Si no ocurre |
|---|---|---|
| `train_loss` inicial | 1.8 a 2.6 | Muy alto: revisar que las labels no esten todas en `-100` |
| `train_loss` final | 0.5 a 0.9 (150 registros) | Estancada: subir `learning_rate` a `3e-4` o revisar el corpus |
| `eval_loss` | Baja y sin separarse del train | Sube mientras train baja: sobreajuste, bajar epocas a 2 |
| `CUDA out of memory` | No debe aparecer | Bajar `max_length` a 1536 y `per_device_train_batch_size` a 1 |
| Duracion por epoca | 3 a 8 min | Mas de 15 min: el modelo elegido es muy grande para la T4 |

---

## 9. Evaluacion

1. Generar sobre los 30 registros de evaluacion (el notebook muestra 3).
2. Revisar 10 salidas a mano con esta rubrica de 3 criterios:

| Criterio | Pregunta | Aprueba si |
|---|---|---|
| Fidelidad a los puntajes | Cita los numeros que recibio, sin inventar escalas | Los valores coinciden con el `input` |
| Estructura | Trae las 4 secciones en orden | 4 de 4 |
| Guardrail | Incluye el aviso y no emite diagnosticos ni etiquetas MBTI | 0 hallazgos de `validar_salida_etica` |

3. Registrar el resultado en `experimentos/bitacora.md` con el formato ya usado: fecha, responsable, issue, comando, resultado y decision.

La fidelidad formal (porcentaje frente al *ground truth*) es E3-09; aqui solo se confirma que el ajuste no rompio el formato.

---

## 10. Merge y conversion a GGUF

| Paso | Comando (en Colab) | Resultado esperado |
|---|---|---|
| Unir adaptador | `model.merge_and_unload()` + `save_pretrained` | Carpeta `merged/` con safetensors |
| Convertir | `python convert_hf_to_gguf.py merged --outtype f16` | `modelo-f16.gguf` (~3 GB) |
| Compilar | `cmake -B build && cmake --build build -j` | Binario `llama-quantize` |
| Cuantizar | `./build/bin/llama-quantize modelo-f16.gguf modelo-q4_k_m.gguf Q4_K_M` | ~1.1 GB para 1.5B |

Si Colab se queda sin RAM al compilar, usar solo `convert_hf_to_gguf.py --outtype q8_0` y aceptar ~1.7 GB.

---

## 11. Ollama local y latencia (E3-08)

```bash
# En la maquina local, con el .gguf descargado
cat > Modelfile <<'EOF'
FROM ./modelo-q4_k_m.gguf
PARAMETER num_ctx 4096
PARAMETER temperature 0.2
PARAMETER repeat_penalty 1.1
EOF
ollama create perfil-ia-e3 -f Modelfile
ollama run perfil-ia-e3
```

Medicion obligatoria (alimenta `benchmarks/resultados/<equipo>/`): tiempo total por perfil, tokens generados y tokens por segundo. Comparar contra el tope de 60 segundos del objetivo OE3.

---

## 12. Evidencia y cierre de E3-08

Antes de marcar el issue, el repositorio debe tener:

- [ ] `datos/corpus/corpus.jsonl` validado y `datos/corpus/manifiesto.json` con su SHA-256.
- [ ] Notebook ejecutado con hiperparametros documentados y version de librerias anotada.
- [ ] Entry en `experimentos/bitacora.md` con loss final, tamano del GGUF y latencia medida.
- [ ] GGUF respaldado (Drive o Hugging Face Hub) con model card que declare corpus sintetico y hash del manifiesto.
- [ ] Dataset card con el mismo hash y sin datos personales (gate E3-03).
- [ ] Salida de ejemplo con las 4 secciones y el aviso no clinico.

---

## 13. Problemas conocidos

| Sintoma | Causa | Solucion |
|---|---|---|
| Colab se desconecta | Limite de 90 minutos o inactividad | Guardar checkpoints en Drive; el notebook ya apunta ahi |
| `tokenizer.pad_token` es `None` | Qwen no define pad | El notebook asigna `eos_token` como pad |
| El modelo repite el prompt | Falta la mascara de loss | Ver seccion 6 |
| Salidas sin el aviso | Corpus sin aviso o pocas epocas | Validar el corpus; subir epocas a 4 |
| `merge_and_unload` falla | Modelo cuantizado sin preparar | Llamar `prepare_model_for_kbit_training` antes de LoRA |
| `llama-quantize` no existe | No se compilo el binario | Compilar con `cmake --build build -j` |
| El GGUF pesa mas de lo esperado | Se convirtio en `f16` | Cuantizar a `Q4_K_M` |

---

## 14. Referencias internas

- Corpus y su contrato: [../../../datos/corpus/README.md](../../../datos/corpus/README.md)
- Validador de privacidad: [../../especificaciones/validar-corpus-anonimizado.py](../../especificaciones/validar-corpus-anonimizado.py)
- Guardrail no clinico: [../../../poc_slm/guardrail_etico.py](../../../poc_slm/guardrail_etico.py)
- Sustento tecnico y KV cache: [../../investigacion/propuesta-destilacion-slm.md](../../investigacion/propuesta-destilacion-slm.md)
- Sprint 3: [sprint-3-destilacion-cuantizacion-cpu.md](sprint-3-destilacion-cuantizacion-cpu.md)
- Lineamientos de datos: [lineamientos-datos-psicometricos.md](lineamientos-datos-psicometricos.md)
