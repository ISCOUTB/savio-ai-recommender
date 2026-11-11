"""linea_base_fichas.py - Linea base sin IA y datos de prueba del ajuste (E3-09 / E3-08).

Para cada perfil con puntajes brutos calcula sus resultados (resultados_calculados.py)
y arma el perfil "integrado" concatenando las fichas que le corresponden, sin modelo
de lenguaje. Es la variante "Linea base (sin IA)" de la seccion 17 de la formulacion.

Tambien escribe el resultado en el formato JSONL del corpus (instruction, input,
output) para probar de punta a punta el notebook de ajuste antes de tener el corpus
real. Estas salidas NO son ground truth: el campo "fuente" lo deja explicito.

Uso (desde la raiz del repo):
    python poc_slm/linea_base_fichas.py                       # 150 perfiles sinteticos
    python poc_slm/linea_base_fichas.py --limite 10 --salida entrenamiento/datos_prueba.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "poc_slm"))
from perfil_bruto import validar_perfil_bruto  # noqa: E402
from resultados_calculados import calcular  # noqa: E402

FICHAS = RAIZ / "fichas" / "fichas_interpretativas.json"
PERFILES = RAIZ / "perfiles" / "sinteticos" / "perfiles_sinteticos.jsonl"
ESTRATOS = RAIZ / "perfiles" / "sinteticos" / "estratos.json"

INSTRUCCION = (
    "Eres un asistente que redacta un borrador de perfil integrado para que lo revise un profesional de orientacion. "
    "Recibes los puntajes originales de CHASIDE, el Indice de Estilos de Aprendizaje de Felder-Silverman y el test de "
    "personalidad institucional, y los resultados ya calculados. Redacta en espanol las secciones: Sintesis vocacional, "
    "Preferencias de presentacion, Rasgos de personalidad, Lectura integrada y Limitaciones. Cita entre corchetes los "
    "identificadores de las fichas que uses. No emitas diagnosticos ni decisiones sobre el estudiante y no cambies "
    "ningun puntaje."
)


def cargar_fichas() -> dict:
    return {f["id"]: f for f in json.loads(FICHAS.read_text(encoding="utf-8"))["fichas"]}


def ficha_chaside(area: str, r: dict) -> str:
    return f"CH-{area}-bajo" if r["nivel"] == "bajo" else f"CH-{area}-{r['nivel']}-{r['brecha']}"


def perfil_linea_base(perfil: dict, fichas: dict) -> tuple:
    res = calcular(perfil)
    ch, ils, pers = res["chaside"], res["ils"], res["personalidad"]
    usadas = []

    def citar(fid):
        usadas.append(fid)
        return f"{fichas[fid]['texto']} [{fid}]"

    voc = [f"{fichas[ficha_chaside(a, ch['areas'][a])]['nombre_area']}: " + citar(ficha_chaside(a, ch["areas"][a]))
           for a in ch["top2"]]
    pres = [citar(f"ILS-{d['polo']}-{d['banda']}") for d in ils.values()]
    ras = [citar(f"PER-{e['polo']}") + (" (empate en el eje; se aplica la regla del bloque)" if e["empate"] else "")
           for e in pers["ejes"].values()]
    texto = (
        "## Sintesis vocacional\n" + "\n".join(f"- {t}" for t in voc) + "\n\n"
        "## Preferencias de presentacion\n" + "\n".join(f"- {t}" for t in pres) + "\n\n"
        "## Rasgos de personalidad\n" + "\n".join(f"- {t}" for t in ras) + "\n\n"
        "## Lectura integrada\nNo disponible en la linea base sin IA: las fichas se presentan por separado.\n\n"
        "## Limitaciones\n- " + citar("PRIN-01") + "\n- " + citar("PRIN-02") + "\n- " + citar("PRIN-03")
        + "\n- Borrador generado automaticamente; debe revisarlo un profesional."
    )
    return res, texto, usadas


def main() -> None:
    parser = argparse.ArgumentParser(description="Linea base sin IA a partir de fichas.")
    parser.add_argument("--perfiles", type=Path, default=PERFILES)
    parser.add_argument("--limite", type=int, default=None)
    parser.add_argument("--salida", type=Path, default=RAIZ / "perfiles" / "sinteticos" / "linea_base_fichas.jsonl")
    args = parser.parse_args()

    fichas = cargar_fichas()
    particion = {e["id"]: e["particion"] for e in json.loads(ESTRATOS.read_text(encoding="utf-8"))["perfiles"]}
    perfiles = [json.loads(l) for l in args.perfiles.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limite:
        perfiles = perfiles[: args.limite]

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    with open(args.salida, "w", encoding="utf-8", newline="\n") as f:
        for p in perfiles:
            errores = validar_perfil_bruto(p)
            if errores:
                raise SystemExit(f"[ERROR] {p['id']}: {errores}")
            res, texto, usadas = perfil_linea_base(p, fichas)
            entrada = {"puntajes": {k: p[k] for k in ("chaside", "ils", "personalidad")}, "resultados": res}
            f.write(json.dumps({"id": p["id"], "particion": particion.get(p["id"], "train"),
                                "fuente": "linea_base_fichas (sin IA; no es ground truth)",
                                "instruction": INSTRUCCION, "input": json.dumps(entrada, ensure_ascii=False),
                                "output": texto, "fichas_usadas": usadas}, ensure_ascii=False) + "\n")
    print(f"{len(perfiles)} ejemplos en {args.salida.resolve().relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
