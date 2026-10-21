# poc_slm — Scripts de inferencia local

Scripts en Python para ejecutar la PoC del subsistema de recomendacion con SLMs locales (Ollama).

> 📌 Documentacion del sprint: [docs/entregas/entrega-1-poc-funcional/sprint-2-motor-inferencia.md](../docs/entregas/entrega-1-poc-funcional/sprint-2-motor-inferencia.md)

## Contenido (Sprint 2 — Entrega 1)

```
poc_slm/
├── recommender.py        ← Script principal (middleware simplificado de la PoC)
├── eventos/
│   ├── bajo_desempeno.json   ← Evento de ejemplo (Sprint 2)
│   ├── A_nota_baja.json      ← Escenario A: tutoria reactiva ante nota baja (Sprint 3)
│   ├── B_visual.json         ← Escenario B: misma deficiencia, estilo visual (Sprint 3)
│   └── B_textual.json        ← Escenario B: misma deficiencia, estilo textual (Sprint 3)
└── README.md
```

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
