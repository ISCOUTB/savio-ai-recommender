"""generar_diagrama.py — Diagrama de arquitectura del subsistema SAVIO (Sprint 4, Issue #11).

Genera docs/arquitectura/arquitectura-subsistema.svg y .png con el flujo:
Savio/Moodle (evento) → Middleware orquestador → Prompt Engine (guardrails)
→ SLM local (Ollama) → Panel/mensajería del estudiante en Savio.

Uso:
    python docs/arquitectura/generar_diagrama.py

Dependencia: matplotlib (ver docs/presentacion/requirements.txt).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

DIR = Path(__file__).resolve().parent

TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
BORDE = "#c9c8c2"
AZUL = "#2a78d6"
AZUL_SUAVE = "#e8f1fc"
GRIS_SUAVE = "#f4f4f2"

# (x, y, ancho, alto, título, subtítulo, fondo, borde)
COMPONENTES = [
    (0.3, 3.3, 2.6, 1.6, "Savio (Moodle)", "Evento académico:\nnota, entrega, inactividad", GRIS_SUAVE, BORDE),
    (3.75, 3.3, 2.6, 1.6, "Middleware\norquestador", "recommender.py\nlee evento + contexto", AZUL_SUAVE, AZUL),
    (7.2, 3.3, 2.6, 1.6, "Prompt Engine", "system prompt + guardrails\n+ refuerzo + contexto", AZUL_SUAVE, AZUL),
    (10.65, 3.3, 2.6, 1.6, "SLM local (Ollama)", "Qwen 2.5 3B · Q4_K_M\nlocalhost:11434", AZUL_SUAVE, AZUL),
    (10.65, -0.9, 2.6, 1.6, "Savio · panel /\nmensajería", "Diagnóstico → Ruta →\nRecursos → Cierre", GRIS_SUAVE, BORDE),
]

# (desde, hasta, etiqueta)
FLECHAS = [
    ((2.9, 4.1), (3.75, 4.1), "JSON"),
    ((6.35, 4.1), (7.2, 4.1), "contexto"),
    ((9.8, 4.1), (10.65, 4.1), "prompt"),
    ((11.95, 3.3), (11.95, 0.7), "recomendación\nen Markdown"),
]


def dibujar() -> plt.Figure:
    fig, ax = plt.subplots(figsize=(13.4, 7.6), dpi=150)
    ax.set_xlim(0, 13.5)
    ax.set_ylim(-1.1, 6.4)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # Límite on-premise: todo lo que procesa datos del estudiante queda dentro
    ax.add_patch(FancyBboxPatch((3.5, 1.15), 9.95, 4.25, boxstyle="round,pad=0,rounding_size=0.15",
                                fill=False, ec=AZUL, lw=1.4, ls=(0, (5, 4))))
    ax.text(3.7, 5.12, "Subsistema de recomendación · servidor UTB on-premise · sin APIs externas",
            fontsize=10, color=AZUL, va="center", fontweight="bold")
    ax.text(3.75, 2.9, "Los datos del estudiante\nno salen del campus",
            ha="left", va="top", fontsize=9.5, color=AZUL, linespacing=1.35)

    for x, y, w, h, titulo, sub, fondo, borde in COMPONENTES:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                    fc=fondo, ec=borde, lw=1.6))
        ax.text(x + w / 2, y + h * 0.66, titulo, ha="center", va="center", fontsize=12,
                color=TEXTO, fontweight="bold", linespacing=1.1)
        ax.text(x + w / 2, y + h * 0.25, sub, ha="center", va="center", fontsize=9,
                color=TEXTO_2, linespacing=1.25)

    for (x0, y0), (x1, y1), etiqueta in FLECHAS:
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=16,
                                     color=TEXTO_2, lw=1.6))
        if x0 == x1:  # flecha vertical: etiqueta a la izquierda
            ax.text(x0 - 0.12, (y0 + y1) / 2, etiqueta, ha="right", va="center", fontsize=9, color=TEXTO_2)
        else:
            ax.text((x0 + x1) / 2, y0 + 0.15, etiqueta, ha="center", va="bottom", fontsize=9, color=TEXTO_2)

    # Detalle de los guardrails bajo el Prompt Engine
    reglas = ("Guardrails\n"
              "R1 Solo la materia (redirige off-topic)\n"
              "R2 Nunca soluciones completas\n"
              "R3 Tono empático, no punitivo\n"
              "R4 Estructura fija en Markdown\n"
              "+ anti-alucinación (sin URLs ni autores)")
    ax.text(7.2, 2.9, reglas, ha="left", va="top", fontsize=9, color=TEXTO, linespacing=1.4,
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=BORDE, lw=1))

    ax.text(0.3, 2.9, "Fuera del alcance de la PoC:\nla integración con Moodle se\nsimula con eventos JSON\n(poc_slm/eventos/)",
            ha="left", va="top", fontsize=9, color=TEXTO_2, linespacing=1.35, style="italic")

    ax.text(0.3, 6.05, "Arquitectura del subsistema de recomendación adaptativa — SAVIO",
            fontsize=15, color=TEXTO, fontweight="bold", va="center")
    return fig


def main() -> None:
    fig = dibujar()
    for ext in ("svg", "png"):
        destino = DIR / f"arquitectura-subsistema.{ext}"
        fig.savefig(destino, bbox_inches="tight", pad_inches=0.15, facecolor="white")
        print(f"Diagrama guardado en: {destino}")


if __name__ == "__main__":
    main()
