"""generar_perfiles_sinteticos.py - Perfiles sinteticos con puntajes originales brutos (E3-06, #43).

Genera N perfiles (por defecto 150) con el formato del Anexo A, validos segun
poc_slm/perfil_bruto.py, y estratificados para que el corpus ground truth cubra
casos contrastantes:

  CHASIDE (escenario por perfil, area dominante rotando entre las 7):
    unica          una area claramente dominante (total 11-14)
    co_dominantes  dos areas altas con diferencia de 0 o 1 en el total
    plano          sin area dominante (totales 4-9, rango <= 4)
    brecha_interes area con interes alto (9-10) y aptitud baja (0-1)
    brecha_aptitud area con aptitud maxima (4) e interes bajo (2-4), distinta de la de mayor interes
  ILS: banda por dimension (equilibrio 1-3, moderada 5-7, fuerte 9-11) en partes iguales.
  Personalidad: por eje, preferencia clara (diferencia 4-9), leve (1-3) o empate (0).

Ademas asigna la particion train/eval (80/20) por perfil, estratificada por
escenario de CHASIDE, para que el corpus no tenga fuga entre particiones.

Uso (desde la raiz del repo):
    python poc_slm/generar_perfiles_sinteticos.py
    python poc_slm/generar_perfiles_sinteticos.py --n 150 --semilla 2026

Salida (versionable, solo datos sinteticos):
    perfiles/sinteticos/perfiles_sinteticos.jsonl   un perfil por linea (Anexo A)
    perfiles/sinteticos/estratos.json               escenario, bandas y particion de cada perfil
"""

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "poc_slm"))
from perfil_bruto import AREAS_CHASIDE, PARES_ILS, PARES_PERSONALIDAD, validar_perfil_bruto  # noqa: E402

DIR_SALIDA = RAIZ / "perfiles" / "sinteticos"
ESCENARIOS = [("unica", 0.40), ("co_dominantes", 0.20), ("plano", 0.15), ("brecha_interes", 0.15),
              ("brecha_aptitud", 0.10)]
BANDAS_ILS = {"equilibrio": [1, 3], "moderada": [5, 7], "fuerte": [9, 11]}
FUERZAS_PERS = [("clara", 0.50), ("leve", 0.35), ("empate", 0.15)]
FRACCION_EVAL = 0.20


def repartir(opciones_pesos, n, rng):
    """Lista de n etiquetas con las proporciones pedidas (redondeo por mayor resto), barajada."""
    cuotas = [(op, p * n) for op, p in opciones_pesos]
    lista = [op for op, c in cuotas for _ in range(int(c))]
    restos = sorted(cuotas, key=lambda x: x[1] - int(x[1]), reverse=True)
    for op, _ in restos[: n - len(lista)]:
        lista.append(op)
    rng.shuffle(lista)
    return lista


def area(interes, aptitud):
    return {"interes": interes, "aptitud": aptitud, "total": interes + aptitud}


def area_baja(rng, tope_total):
    """Area secundaria con total <= tope_total."""
    while True:
        a = area(rng.randint(0, 7), rng.randint(0, 3))
        if a["total"] <= tope_total:
            return a


def generar_chaside(escenario, dominante, rng):
    otras = [a for a in AREAS_CHASIDE if a != dominante]
    ch = {}
    if escenario == "unica":
        ch[dominante] = area(rng.randint(8, 10), rng.randint(3, 4))
        for a in otras:
            ch[a] = area_baja(rng, ch[dominante]["total"] - 3)
    elif escenario == "co_dominantes":
        segunda = rng.choice(otras)
        ch[dominante] = area(rng.randint(8, 10), rng.randint(2, 4))
        while True:
            b = area(rng.randint(7, 10), rng.randint(2, 4))
            if abs(b["total"] - ch[dominante]["total"]) <= 1:
                break
        ch[segunda] = b
        tope = min(ch[dominante]["total"], b["total"]) - 3
        for a in otras:
            if a != segunda:
                ch[a] = area_baja(rng, tope)
    elif escenario == "plano":
        while True:
            for a in AREAS_CHASIDE:
                ch[a] = area(rng.randint(3, 7), rng.randint(1, 2))
            totales = [ch[a]["total"] for a in AREAS_CHASIDE]
            if all(4 <= t <= 9 for t in totales) and max(totales) - min(totales) <= 4:
                break
    elif escenario == "brecha_interes":
        ch[dominante] = area(rng.randint(9, 10), rng.randint(0, 1))
        for a in otras:
            ch[a] = area_baja(rng, ch[dominante]["total"] - 2)
    elif escenario == "brecha_aptitud":
        de_interes = rng.choice(otras)
        ch[dominante] = area(rng.randint(2, 4), 4)
        ch[de_interes] = area(rng.randint(8, 10), rng.randint(1, 3))
        for a in otras:
            if a != de_interes:
                ch[a] = area(rng.randint(0, 5), rng.randint(0, 2))
    return {a: ch[a] for a in AREAS_CHASIDE}


def generar_ils(bandas, rng):
    ils = {}
    for (izq, der), banda in zip(PARES_ILS, bandas):
        d = rng.choice(BANDAS_ILS[banda])
        alto, bajo = (11 + d) // 2, (11 - d) // 2
        if rng.random() < 0.5:
            ils[izq], ils[der] = alto, bajo
        else:
            ils[izq], ils[der] = bajo, alto
    return ils


def generar_personalidad(fuerzas, rng):
    pers = {}
    for (izq, der), fuerza in zip(PARES_PERSONALIDAD, fuerzas):
        if fuerza == "empate":
            a = b = rng.randint(2, 8)
        else:
            k = rng.randint(4, 9) if fuerza == "clara" else rng.randint(1, 3)
            a = rng.randint(k, 9)
            b = a - k
            if rng.random() < 0.5:
                a, b = b, a
        pers[izq], pers[der] = a, b
    return pers


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera perfiles sinteticos con puntajes brutos (Anexo A).")
    parser.add_argument("--n", type=int, default=150)
    parser.add_argument("--semilla", type=int, default=2026)
    args = parser.parse_args()
    rng = random.Random(args.semilla)
    n = args.n

    escenarios = repartir(ESCENARIOS, n, rng)
    bandas_ils = [repartir([(b, 1 / 3) for b in BANDAS_ILS], n, rng) for _ in PARES_ILS]
    fuerzas_pers = [repartir(FUERZAS_PERS, n, rng) for _ in PARES_PERSONALIDAD]
    contador_dom = Counter()

    perfiles, estratos, vistos = [], [], set()
    for i in range(n):
        esc = escenarios[i]
        dominante = AREAS_CHASIDE[contador_dom[esc] % 7]
        contador_dom[esc] += 1
        while True:
            perfil = {
                "id": f"SINT-{i + 1:03d}",
                "origen": "sintetico",
                "chaside": generar_chaside(esc, dominante, rng),
                "ils": generar_ils([b[i] for b in bandas_ils], rng),
                "personalidad": generar_personalidad([f[i] for f in fuerzas_pers], rng),
            }
            clave = json.dumps({k: perfil[k] for k in ("chaside", "ils", "personalidad")}, sort_keys=True)
            if clave not in vistos:
                vistos.add(clave)
                break
        errores = validar_perfil_bruto(perfil)
        if errores:
            raise SystemExit(f"[ERROR] {perfil['id']} invalido: {errores}")
        perfiles.append(perfil)
        estratos.append({"id": perfil["id"], "escenario_chaside": esc, "area_dominante": dominante,
                         "bandas_ils": {f"{a}/{b}": bd[i] for (a, b), bd in zip(PARES_ILS, bandas_ils)},
                         "fuerza_personalidad": {f"{a}/{b}": fz[i] for (a, b), fz in zip(PARES_PERSONALIDAD, fuerzas_pers)}})

    # Particion 80/20 estratificada por escenario de CHASIDE
    for esc, _ in ESCENARIOS:
        ids = [e for e in estratos if e["escenario_chaside"] == esc]
        rng.shuffle(ids)
        n_eval = round(len(ids) * FRACCION_EVAL)
        for j, e in enumerate(ids):
            e["particion"] = "eval" if j < n_eval else "train"

    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    with open(DIR_SALIDA / "perfiles_sinteticos.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for p in perfiles:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    (DIR_SALIDA / "estratos.json").write_text(
        json.dumps({"semilla": args.semilla, "n": n, "perfiles": estratos}, indent=1, ensure_ascii=False),
        encoding="utf-8")

    print(f"{n} perfiles validos y unicos en {DIR_SALIDA.relative_to(RAIZ)}")
    print("Escenarios CHASIDE:", dict(Counter(escenarios)))
    print("Areas dominantes:", dict(sorted(Counter(e["area_dominante"] for e in estratos).items())))
    for (a, b), bd in zip(PARES_ILS, bandas_ils):
        print(f"ILS {a}/{b}:", dict(Counter(bd)))
    for (a, b), fz in zip(PARES_PERSONALIDAD, fuerzas_pers):
        print(f"Personalidad {a}/{b}:", dict(Counter(fz)))
    print("Particion:", dict(Counter(e["particion"] for e in estratos)),
          "| eval por escenario:", dict(Counter(e["escenario_chaside"] for e in estratos if e["particion"] == "eval")))


if __name__ == "__main__":
    main()
