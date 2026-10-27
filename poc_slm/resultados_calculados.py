"""resultados_calculados.py - Calculo deterministico de resultados por instrumento (RF02).

Aplica las reglas de cada instrumento sobre los puntajes originales brutos
(formato del Anexo A, ver poc_slm/perfil_bruto.py), sin modelo de lenguaje:

  - CHASIDE (reglas de classes/facade.php del bloque block_chaside):
      pct_total = 100*total/14 -> alto >= 80, medio >= 60, emergente >= 40, bajo < 40
      pct_interes = 100*interes/10, pct_aptitud = 100*aptitud/4 -> brecha si la diferencia es >= 20 puntos
      top 2: mayor total, luego mayor aptitud, luego menor |interes - aptitud|, luego orden alfabetico
  - ILS (Felder-Silverman): polo con mayor conteo; banda por la diferencia
      equilibrio 1-3, moderada 5-7, fuerte 9-11
  - Personalidad: polo con mayor conteo en cada eje; en empate se elige I, N, T o P
    (regla del bloque, seccion 8 de la formulacion)

Coordinar con E3-07 (#51): el backend puede importar este modulo para no duplicar reglas.
"""

from perfil_bruto import AREAS_CHASIDE, PARES_ILS, PARES_PERSONALIDAD

DESEMPATE_PERSONALIDAD = {"extraversion/introversion": "introversion", "sensing/intuition": "intuition",
                          "thinking/feeling": "thinking", "judging/perceptive": "perceptive"}
LETRA = {"extraversion": "E", "introversion": "I", "sensing": "S", "intuition": "N",
         "thinking": "T", "feeling": "F", "judging": "J", "perceptive": "P"}


def nivel_chaside(total: int) -> str:
    pct = round(100 * total / 14, 1)
    if pct >= 80.0:
        return "alto"
    if pct >= 60.0:
        return "medio"
    if pct >= 40.0:
        return "emergente"
    return "bajo"


def brecha_chaside(interes: int, aptitud: int) -> str:
    dif = round(100 * interes / 10, 1) - round(100 * aptitud / 4, 1)
    if dif >= 20.0:
        return "interes_mayor"
    if dif <= -20.0:
        return "aptitud_mayor"
    return "balanceado"


def calcular_chaside(chaside: dict) -> dict:
    areas = {a: {**chaside[a], "nivel": nivel_chaside(chaside[a]["total"]),
                 "brecha": brecha_chaside(chaside[a]["interes"], chaside[a]["aptitud"])} for a in AREAS_CHASIDE}
    orden = sorted(AREAS_CHASIDE, key=lambda a: (-areas[a]["total"], -areas[a]["aptitud"],
                                                 abs(areas[a]["interes"] - areas[a]["aptitud"]), a))
    return {"areas": areas, "top2": orden[:2]}


def banda_ils(diferencia: int) -> str:
    if diferencia <= 3:
        return "equilibrio"
    if diferencia <= 7:
        return "moderada"
    return "fuerte"


def calcular_ils(ils: dict) -> dict:
    dims = {}
    for izq, der in PARES_ILS:
        polo = izq if ils[izq] > ils[der] else der  # suman 11 (impar): nunca empatan
        dims[f"{izq}/{der}"] = {"polo": polo, "diferencia": abs(ils[izq] - ils[der]),
                                "banda": banda_ils(abs(ils[izq] - ils[der]))}
    return dims


def calcular_personalidad(pers: dict) -> dict:
    ejes = {}
    for izq, der in PARES_PERSONALIDAD:
        eje = f"{izq}/{der}"
        if pers[izq] == pers[der]:
            polo, empate = DESEMPATE_PERSONALIDAD[eje], True
        else:
            polo, empate = (izq if pers[izq] > pers[der] else der), False
        ejes[eje] = {"polo": polo, "diferencia": abs(pers[izq] - pers[der]), "empate": empate}
    tipo = "".join(LETRA[e["polo"]] for e in ejes.values())
    return {"ejes": ejes, "tipo": tipo}


def calcular(perfil: dict) -> dict:
    return {"chaside": calcular_chaside(perfil["chaside"]), "ils": calcular_ils(perfil["ils"]),
            "personalidad": calcular_personalidad(perfil["personalidad"])}
