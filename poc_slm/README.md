# poc_slm — Scripts de inferencia local

Scripts en Python para ejecutar la PoC del subsistema de recomendación con SLMs locales (Ollama).

> 📌 Documentación de la fase: [docs/plan-trabajo/fase-1-motor-inferencia.md](../docs/plan-trabajo/fase-1-motor-inferencia.md)

## Contenido (Fase 1)

```
poc_slm/
├── recommender.py        ← Script principal (middleware simplificado de la PoC)
├── eventos/
│   └── bajo_desempeno.json  ← Evento académico simulado
└── README.md
```

## Uso

```bash
# Requisito previo: Ollama corriendo con qwen2.5:1.5b descargado
ollama pull qwen2.5:1.5b

# Ejecutar un escenario
python poc_slm/recommender.py --escenario bajo_desempeno
```

## Dependencias

- Python 3.11+
- `requests` (única dependencia externa)

```bash
pip install requests
```
