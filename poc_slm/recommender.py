"""recommender.py — Middleware simplificado de la PoC SAVIO.

Recibe un evento academico simulado (JSON), ensambla el prompt con el contexto
del estudiante y lo envia al SLM local via API de Ollama, imprimiendo la
recomendacion generada en consola.

Uso:
    python poc_slm/recommender.py --escenario bajo_desempeno
    python poc_slm/recommender.py --escenario bajo_desempeno --refuerzo
    python poc_slm/recommender.py --escenario bajo_desempeno --mensaje "pregunta del estudiante"
    python poc_slm/recommender.py --escenario bajo_desempeno --guardar salidas/mi_salida.md

Opciones (Sprint 3, Issue #4):
    --refuerzo   Repite las reglas criticas dentro del prompt de usuario
                 (mitigacion documentada: los SLMs 1.5B-2B tienden a ignorar
                 el system prompt).
    --mensaje    Simula un mensaje/pregunta del estudiante (pruebas adversariales).
    --guardar    Guarda la recomendacion generada en un archivo Markdown.

Unica dependencia externa: requests.
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
MAX_TOKENS_SALIDA = 600  # Tope duro de generacion. El limite pedagogico es ~300 palabras;
# el margen extra da espacio a que el modelo complete las 4 secciones del esquema.

# Reglas criticas repetidas en el prompt de usuario cuando se usa --refuerzo
# (mitigacion V2 del Sprint 3). La regla 5 nombra dinamicamente el estilo del
# evento para reforzar la adaptacion (los SLMs pequenos la ignoran si es generica).
def refuerzo_reglas(evento: dict) -> str:
    estilo = evento.get("estilo_aprendizaje", "no indicado")
    return (
        "\n⚠️ RECUERDA TUS REGLAS CRITICAS:\n"
        "1. Responde SOLO sobre la materia y el tema de este evento. Si la pregunta es de otro tema, redirige amablemente.\n"
        "2. NUNCA entregues soluciones completas de tareas o talleres; solo guias metodologicas.\n"
        "3. Usa SOLO los datos del evento: no inventes libros, autores ni fortalezas, NUNCA incluyas enlaces o URLs, y lee la nota segun su escala (2.0 en 0-5 es nota baja).\n"
        "4. Estructura fija: Diagnostico → Ruta de estudio (max. 3 pasos) → Recursos (max. 3, solo TIPOS: video/diagrama/lectura/ejercicio) → Cierre motivacional. Se breve.\n"
        f"5. ESTE ESTUDIANTE ES DE ESTILO '{estilo}'. Adapta TODO a ese estilo: "
        "visual → diagramas/videos/mapas (sin lecturas largas); "
        "textual → lecturas/resumenes/definiciones escritas (sin diagramas ni videos como recurso principal).\n"
    )

# Rutas relativas a la raiz del repositorio (este script vive en poc_slm/)
RAIZ = Path(__file__).resolve().parent.parent
DIR_EVENTOS = RAIZ / "poc_slm" / "eventos"
SYSTEM_PROMPT_PATH = RAIZ / "prompts" / "system_guardrails.md"


def cargar_evento(escenario: str) -> dict:
    """Carga el evento academico simulado desde poc_slm/eventos/<escenario>.json."""
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
        print(f"[ERROR] No se encontro el system prompt: {SYSTEM_PROMPT_PATH}", file=sys.stderr)
        sys.exit(1)
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()


def ensamblar_prompt(evento: dict, mensaje: str | None = None, refuerzo: bool = False) -> str:
    """Construye el prompt de usuario con el contexto del estudiante.

    - mensaje: pregunta/comentario del estudiante (pruebas adversariales, #7).
    - refuerzo: repite las reglas criticas dentro del prompt de usuario (mitigacion V2, #4).
    """
    prompt = (
        "Evento academico recibido desde la plataforma:\n"
        f"- Estudiante: {evento['estudiante']}\n"
        f"- Materia: {evento['materia']}\n"
        f"- Tema evaluado: {evento['tema']}\n"
        f"- Calificacion: {evento['calificacion']} (escala {evento['escala']})\n"
        f"- Estilo de aprendizaje preferido: {evento['estilo_aprendizaje']}\n"
    )
    if mensaje:
        prompt += f'\nMensaje del estudiante: "{mensaje}"\n'
    if refuerzo:
        prompt += refuerzo_reglas(evento)
    prompt += (
        "\nGenera una recomendacion de estudio personalizada para este estudiante, "
        "adaptada a su estilo de aprendizaje, siguiendo la estructura indicada "
        "en tus instrucciones."
    )
    return prompt


def generar_recomendacion(system_prompt: str, prompt_usuario: str, modelo: str) -> dict:
    """Envia el prompt a Ollama (POST /api/generate) y retorna la respuesta completa."""
    payload = {
        "model": modelo,
        "system": system_prompt,
        "prompt": prompt_usuario,
        "stream": False,
        "options": {"num_predict": MAX_TOKENS_SALIDA},
    }
    try:
        respuesta = requests.post(OLLAMA_URL, json=payload, timeout=300)
        respuesta.raise_for_status()
    except requests.ConnectionError:
        print(
            "[ERROR] No se pudo conectar con Ollama en http://localhost:11434\n"
            "        Verifica que el servicio este corriendo (ollama serve o la app de Ollama).",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.Timeout:
        print("[ERROR] La solicitud a Ollama agoto el tiempo de espera (300 s).", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"[ERROR] Ollama respondio con error HTTP: {e}", file=sys.stderr)
        sys.exit(1)
    return respuesta.json()


def imprimir_salida(evento: dict, modelo: str, resultado: dict, duracion: float) -> None:
    """Imprime la recomendacion formateada en consola."""
    eval_count = resultado.get("eval_count", 0)
    eval_duration_ns = resultado.get("eval_duration", 0)
    tokens_por_seg = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns else 0.0

    print("=" * 70)
    print("SAVIO — Recomendador academico (PoC local con SLM)")
    print("=" * 70)
    print(f"Estudiante : {evento['estudiante']}")
    print(f"Materia    : {evento['materia']}")
    print(f"Tema       : {evento['tema']}")
    print(f"Calificacion: {evento['calificacion']} / escala {evento['escala']}")
    print(f"Estilo     : {evento['estilo_aprendizaje']}")
    print("-" * 70)
    print(resultado.get("response", "").strip())
    print("-" * 70)
    print(f"Modelo     : {modelo}")
    print(f"Latencia   : {duracion:.1f} s (total)")
    print(f"Generacion : {eval_count} tokens a ~{tokens_por_seg:.1f} tokens/s")
    print("=" * 70)


def guardar_salida(texto: str, ruta: Path, metadatos: str) -> None:
    """Guarda la recomendacion generada en un archivo Markdown con sus metadatos."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(f"{metadatos}\n\n{texto}\n", encoding="utf-8")
    print(f"Salida guardada en: {ruta}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Middleware simplificado de la PoC SAVIO: evento JSON -> Ollama -> recomendacion."
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
    parser.add_argument(
        "--refuerzo",
        action="store_true",
        help="Repite las reglas criticas dentro del prompt de usuario (mitigacion V2 del Sprint 3).",
    )
    parser.add_argument(
        "--mensaje",
        default=None,
        help="Mensaje/pregunta del estudiante que se adjunta al evento (pruebas adversariales).",
    )
    parser.add_argument(
        "--guardar",
        default=None,
        help="Ruta de un archivo .md donde guardar la recomendacion generada.",
    )
    args = parser.parse_args()

    evento = cargar_evento(args.escenario)
    system_prompt = cargar_system_prompt()
    prompt_usuario = ensamblar_prompt(evento, mensaje=args.mensaje, refuerzo=args.refuerzo)

    inicio = time.perf_counter()
    resultado = generar_recomendacion(system_prompt, prompt_usuario, args.modelo)
    duracion = time.perf_counter() - inicio

    imprimir_salida(evento, args.modelo, resultado, duracion)

    if args.guardar:
        eval_count = resultado.get("eval_count", 0)
        eval_duration_ns = resultado.get("eval_duration", 0)
        tokens_por_seg = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns else 0.0
        metadatos = (
            f"> Modelo: {args.modelo} | Refuerzo: {'si' if args.refuerzo else 'no'}"
            + (f" | Mensaje del estudiante: {args.mensaje}" if args.mensaje else "")
            + f"\n> Latencia: {duracion:.1f} s | Generacion: {eval_count} tokens a ~{tokens_por_seg:.1f} tokens/s"
        )
        guardar_salida(
            resultado.get("response", "").strip(),
            Path(args.guardar),
            metadatos,
        )


if __name__ == "__main__":
    main()
