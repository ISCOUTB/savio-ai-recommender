# poc_slm — Scripts de inferencia local

Scripts en Python para ejecutar la PoC del subsistema de recomendacion con SLMs locales (Ollama).

> 📌 Documentacion del sprint: [docs/entregas/entrega-1-poc-funcional/sprint-2-motor-inferencia.md](../docs/entregas/entrega-1-poc-funcional/sprint-2-motor-inferencia.md)

## Contenido (Sprint 2 — Entrega 1)

```
poc_slm/
├── recommender.py        ← Script principal (middleware simplificado de la PoC)
├── interpretador.py      ← Backend de interpretacion psicometrica integrada (Entrega 3, E3-07)
├── importar_gguf.py      ← Importa el GGUF ajustado en Ollama con ChatML (E3-07)
├── test_interpretador.py ← 50 chequeos del backend, sin Ollama
├── eventos/
│   ├── bajo_desempeno.json   ← Evento de ejemplo (Sprint 2)
│   ├── A_nota_baja.json      ← Escenario A: tutoria reactiva ante nota baja (Sprint 3)
│   ├── B_visual.json         ← Escenario B: misma deficiencia, estilo visual (Sprint 3)
│   └── B_textual.json        ← Escenario B: misma deficiencia, estilo textual (Sprint 3)
├── feedback_tracker.py   ← Registro de feedback JSONL y KPIs acierto/descache (Entrega 2, E2-11)
├── recursos/
│   └── semana_1.json         ← Recursos A/B/C de la materia piloto (Entrega 2, E2-08)
├── feedback/
│   ├── feedback_simulado.jsonl ← 30 eventos simulados reproducibles (semilla 42)
│   └── feedback.jsonl          ← Feedback real (no se versiona, ver .gitignore)
└── README.md
```

## Feedback y KPIs (Entrega 2, E2-11)

```bash
python poc_slm/feedback_tracker.py registrar --recomendacion-id rec-001 --estudiante-id demo-001 --semana 1 --recurso-id tde-s1-A --util si --likert 4
python poc_slm/feedback_tracker.py simular --n 30 --semilla 42 --sobrescribir
python poc_slm/feedback_tracker.py kpis --archivo poc_slm/feedback/feedback_simulado.jsonl

# Feedback real: respuestas de la actividad Feedback del Moodle en Docker (moodle/ levantado)
python poc_slm/feedback_tracker.py importar-moodle --semana 1
```

`importar-moodle` necesita el registro de recomendaciones de E2-10 en `poc_slm/recomendaciones/semana_<n>.jsonl`.

Especificacion completa: [docs/especificaciones/feedback-loop.md](../docs/especificaciones/feedback-loop.md)

## Backend de interpretacion psicometrica (Entrega 3, E3-07)

Recibe un perfil bruto, lo valida contra `docs/especificaciones/contrato_bruto.py`,
reproduce el par system/user del notebook de E3-08 y aplica guardrail etico,
estructura de 4 secciones y chequeo de fidelidad numerica.

```bash
# Ver el prompt y validar el perfil sin llamar a Ollama
python poc_slm/interpretador.py --perfil perfiles/brutos/ejemplo-perfil-bruto-dominante.json --dry-run

# Interpretacion completa con el SLM local
python poc_slm/interpretador.py --perfil perfiles/brutos/ejemplo-perfil-bruto-dominante.json --modelo qwen2.5:1.5b

# Importar el GGUF ajustado de E3-08 y ver el Modelfile sin importar nada
python poc_slm/importar_gguf.py --gguf C:\modelos\savio-e3-q4km.gguf --dry-run

# Importarlo en Ollama y correr el backend con el modelo ajustado
python poc_slm/importar_gguf.py --gguf C:\modelos\savio-e3-q4km.gguf
python poc_slm/interpretador.py --perfil perfiles/brutos/ejemplo-perfil-bruto-dominante.json --gguf C:\modelos\savio-e3-q4km.gguf

# Exportar Markdown y JSON
python poc_slm/interpretador.py --perfil perfiles/brutos/ejemplo-perfil-bruto-dominante.json --salida-dir salidas/e3

# Pruebas (sin Ollama)
python poc_slm/test_interpretador.py
```

`importar_gguf.py` crea el modelo `savio-e3-<8 hex del SHA-256>` con plantilla
ChatML, temperatura `0.2` y `num_predict=1200`. El nombre es estable, asi que la
bitacora puede citar el modelo y el hash del GGUF sin ambiguedad. Los archivos
`.gguf` y los Modelfiles quedan en `modelos/`, que esta en `.gitignore`.

El Modelfile y cada solicitud del interpretador fijan `num_gpu=0` para ejecutar
en CPU. Para actualizar el Modelfile de un modelo ya importado, repite la
importacion con `--forzar`.

En `--dry-run` el backend valida el GGUF y muestra el nombre del modelo, pero no
importa nada en Ollama. `--gguf` y `--modelo` son mutuamente excluyentes: el
primero importa un archivo GGUF; el segundo usa un nombre ya instalado en Ollama.

### Refuerzo experimental de baremos

`--refuerzo-baremos` agrega al turno de usuario las reglas del proyecto y la
lectura calculada de cada eje y area. El system original y los puntajes brutos
se conservan. Las reglas ejecutables viven en [lectura_baremos.py](lectura_baremos.py)
y siguen [los baremos E3-04](../docs/especificaciones/baremos-psicometricos.md):
diferencias ILS 9/11, diferencia de personalidad >=4 y bandas CHASIDE 0-5/6-10/11-14.
Un empate requiere conteos iguales; equilibrio y empate son conceptos distintos.

```bash
# Revisar los hechos que recibira el modelo, sin inferencia
python poc_slm/interpretador.py --perfil perfiles/brutos/ejemplo-perfil-bruto-dominante.json --modelo savio-e3-9ed11dcc --refuerzo-baremos --dry-run

# Comparar un solo perfil con/sin refuerzo, mismo GGUF y parametros fijos
python benchmarks/probar_refuerzo_e3.py --perfil perfiles/brutos/ejemplo-perfil-bruto-dominante.json
```

El [comparador](../benchmarks/probar_refuerzo_e3.py) admite solo perfiles sinteticos
y escribe una carpeta nueva en `benchmarks/resultados/<equipo>/`. Conserva las
respuestas crudas incluso si se rechazan y usa el mismo validador estricto para
ambos modos. Es una exploracion sobre un caso conocido, no una nueva validacion
del 85% ni evidencia de otro entrenamiento.

El comparador usa temperatura 0 y semilla 42; el interpretador conserva
temperatura 0.2. Las mediciones del comparador pertenecen a esos parametros.
El comparador puede terminar con codigo 0 y respuestas rechazadas: revisa el
campo de aceptacion y los hallazgos guardados en cada respuesta.

Con el flag, el backend rechaza citas incorrectas u omitidas y contradicciones
reconocidas de bandas, polos, empates y revision profesional. No reescribe el
contenido del modelo para aprobarlo. El control semantico es parcial; la revision
integral sigue pendiente aunque no se encuentren hallazgos. Los reintentos
conservan las lecturas calculadas. El refuerzo se activa solo al pasar el flag.

El formato reforzado es acotado: las tres primeras secciones contienen solo las
filas calculadas que se entregaron como contexto. El SLM debe reproducirlas;
Python comprueba su contenido y no las inserta para ocultar errores. La sintesis
admite una o dos frases breves sobre actividades y contextos, sin numeros,
bandas, polos ni nuevas clasificaciones. Este formato busca limitar las
contradicciones y el tamano de salida. La sintesis debe proponer una tarea y un recurso, no repetir
la instruccion del prompt; su utilidad psicopedagogica requiere revision humana.

Estado del prototipo: no aprobado. La [ultima prueba de un perfil sintetico](../benchmarks/resultados/intel-i5-1235u-iris-xe/e3-refuerzo-20261116T211835Z/informe.md)
reprodujo los puntajes y las filas, pero la sintesis introdujo afirmaciones
incompatibles y fue rechazada. El flag sigue siendo opcional; falta resolver
la sintesis antes de ampliar la evaluacion. La [bitacora](../experimentos/bitacora.md)
conserva tambien los hallazgos de la lectura manual de los ensayos anteriores.

## Instalacion (desde la raiz del repositorio)

```bash
# 1. Ollama corriendo con el modelo descargado
ollama pull qwen2.5:1.5b

# 2. Entorno virtual + dependencias
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell: .venv\Scripts\Activate.ps1)
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
```

## Uso

```bash
# Ejecutar un escenario (nombre del archivo .json en poc_slm/eventos/)
python poc_slm/recommender.py --escenario bajo_desempeno

# Opcional: usar otro modelo de Ollama
python poc_slm/recommender.py --escenario bajo_desempeno --modelo qwen2.5:3b

# Opciones del Sprint 3 (prompts y guardrails):
python poc_slm/recommender.py --escenario A_nota_baja --refuerzo      # repite reglas criticas en el prompt de usuario
python poc_slm/recommender.py --escenario A_nota_baja --refuerzo --mensaje "Dame la solucion del taller 3"  # prueba adversarial
python poc_slm/recommender.py --escenario B_visual --refuerzo --guardar prompts/salidas-respaldo/B_visual.md  # guarda la salida
```

El script carga el system prompt definitivo desde `prompts/system_guardrails.md`
(Sprint 3), aplica un tope duro de 600 tokens de salida e imprime la
recomendacion junto con modelo, latencia y tokens/s.

## Dependencias

- Python 3.11+
- `requests` (unica dependencia externa, fijada en `requirements.txt`)
