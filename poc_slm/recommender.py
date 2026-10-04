"""recommender.py — Middleware simplificado de la PoC SAVIO (Sprint 2, Issue #3).

Recibe un evento académico simulado (JSON), ensambla el prompt con el contexto
del estudiante y lo envía al SLM local vía API de Ollama, imprimiendo la
recomendación generada en consola.

Uso:
    python poc_slm/recommender.py --escenario bajo_desempeno

Única dependencia externa: requests.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

# Forzar salida en UTF-8 para evitar caracteres corruptos en Windows / PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_DEFAULT = "qwen2.5:1.5b"

# Rutas relativas a la raíz del repositorio (este script vive en poc_slm/)
RAIZ = Path(__file__).resolve().parent.parent
DIR_EVENTOS = RAIZ / "poc_slm" / "eventos"
SYSTEM_PROMPT_PATH = RAIZ / "prompts" / "system_guardrails.md"


def cargar_evento(escenario: str) -> dict:
    """Carga el evento académico simulado desde poc_slm/eventos/<escenario>.json."""
    ruta = DIR_EVENTOS / f"{escenario}.json"
    if not ruta.exists():
        escenarios = sorted(p.stem for p in DIR_EVENTOS.glob("*.json"))
        print(f"[ERROR] Escenario '{escenario}' no existe: {ruta}", file=sys.stderr)
        print(f"Escenarios disponibles: {', '.join(escenarios) or '(ninguno)'}", file=sys.stderr)
        sys.exit(1)
    with ruta.open(encoding="utf-8") as f:
        return json.load(f)


def cargar_system_prompt() -> str:
    """Carga el system prompt de guardrails (Sprint 2: placeholder; Sprint 3: definitivo)."""
    if not SYSTEM_PROMPT_PATH.exists():
        print(f"[ERROR] No se encontró el system prompt: {SYSTEM_PROMPT_PATH}", file=sys.stderr)
        sys.exit(1)
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()


def ensamblar_prompt(evento: dict) -> str:
    """Construye el prompt de usuario con el contexto del estudiante."""
    return (
        "Evento académico recibido desde la plataforma:\n"
        f"- Estudiante: {evento['estudiante']}\n"
        f"- Materia: {evento['materia']}\n"
        f"- Tema evaluado: {evento['tema']}\n"
        f"- Calificación: {evento['calificacion']} (escala {evento['escala']})\n"
        f"- Estilo de aprendizaje preferido: {evento['estilo_aprendizaje']}\n\n"
        "Genera una recomendación de estudio personalizada para este estudiante, "
        "adaptada a su estilo de aprendizaje, siguiendo la estructura indicada "
        "en tus instrucciones."
    )


def generar_recomendacion(system_prompt: str, prompt_usuario: str, modelo: str) -> dict:
    """Envía el prompt a Ollama (POST /api/generate) y retorna la respuesta completa."""
    payload = {
        "model": modelo,
        "system": system_prompt,
        "prompt": prompt_usuario,
        "stream": False,
    }
    try:
        respuesta = requests.post(OLLAMA_URL, json=payload, timeout=300)
        respuesta.raise_for_status()
    except requests.ConnectionError:
        print(
            "[ERROR] No se pudo conectar con Ollama en http://localhost:11434\n"
            "        Verifica que el servicio esté corriendo (ollama serve o la app de Ollama).",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.Timeout:
        print("[ERROR] La solicitud a Ollama agotó el tiempo de espera (300 s).", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"[ERROR] Ollama respondió con error HTTP: {e}", file=sys.stderr)
        sys.exit(1)
    return respuesta.json()


def imprimir_salida(evento: dict, modelo: str, resultado: dict, duracion: float) -> None:
    """Imprime la recomendación formateada en consola."""
    eval_count = resultado.get("eval_count", 0)
    eval_duration_ns = resultado.get("eval_duration", 0)
    tokens_por_seg = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns else 0.0

    print("=" * 70)
    print("SAVIO — Recomendador académico (PoC local con SLM)")
    print("=" * 70)
    print(f"Estudiante : {evento['estudiante']}")
    print(f"Materia    : {evento['materia']}")
    print(f"Tema       : {evento['tema']}")
    print(f"Calificación: {evento['calificacion']} / escala {evento['escala']}")
    print(f"Estilo     : {evento['estilo_aprendizaje']}")
    print("-" * 70)
    print(resultado.get("response", "").strip())
    print("-" * 70)
    print(f"Modelo     : {modelo}")
    print(f"Latencia   : {duracion:.1f} s (total)")
    print(f"Generación : {eval_count} tokens a ~{tokens_por_seg:.1f} tokens/s")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Middleware simplificado de la PoC SAVIO: evento JSON -> Ollama -> recomendación."
    )
    parser.add_argument(
        "--escenario",
        required=True,
        help="Nombre del escenario (archivo .json en poc_slm/eventos/). Ej: bajo_desempeno",
    )
    parser.add_argument(
        "--modelo",
        default=MODELO_DEFAULT,
        help=f"Modelo de Ollama a usar (default: {MODELO_DEFAULT})",
    )
    args = parser.parse_args()

    evento = cargar_evento(args.escenario)
    system_prompt = cargar_system_prompt()
    prompt_usuario = ensamblar_prompt(evento)

    inicio = time.perf_counter()
    resultado = generar_recomendacion(system_prompt, prompt_usuario, args.modelo)
    duracion = time.perf_counter() - inicio

    imprimir_salida(evento, args.modelo, resultado, duracion)


if __name__ == "__main__":
    main()
