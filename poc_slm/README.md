# poc_slm — Scripts de inferencia local

Scripts en Python para ejecutar la PoC del subsistema de recomendación con SLMs locales (Ollama).

> 📌 Documentación del sprint: [docs/entregas/entrega-1-poc-funcional/sprint-2-motor-inferencia.md](../docs/entregas/entrega-1-poc-funcional/sprint-2-motor-inferencia.md)

## Contenido (Sprint 2 — Entrega 1)

```
poc_slm/
├── recommender.py        ← Script principal (middleware simplificado de la PoC)
├── eventos/
│   └── bajo_desempeno.json  ← Evento académico simulado
└── README.md
```

## Instalación (desde la raíz del repositorio)

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
```

El script carga el system prompt desde `prompts/system_guardrails.md` (placeholder en Sprint 2; definitivo en Sprint 3) e imprime la recomendación junto con modelo, latencia y tokens/s.

## Dependencias

- Python 3.11+
- `requests` (única dependencia externa, fijada en `requirements.txt`)
