"""perfil_bruto.py - Reglas del perfil con puntajes originales brutos (Entrega 3).

Formato: Anexo A del documento de formulacion (v4/v5), a la espera del schema
formal de E3-04 (#50). Los tres instrumentos se usan con su puntuacion original,
sin reescalar:

  - CHASIDE: por area C, H, A, S, I, D, E -> interes (0-10), aptitud (0-4) y total = interes + aptitud (0-14).
  - ILS (Felder-Silverman): 8 polos de 0 a 11; cada par de polos suma 11.
  - Personalidad (bloque institucional tipo MBTI): 8 polos de 0 a 9.

Uso como modulo:
    from perfil_bruto import validar_perfil_bruto
    errores = validar_perfil_bruto(perfil)   # lista vacia = perfil valido
"""

AREAS_CHASIDE = ["C", "H", "A", "S", "I", "D", "E"]
PARES_ILS = [("activo", "reflexivo"), ("sensitivo", "intuitivo"), ("visual", "verbal"), ("secuencial", "global")]
PARES_PERSONALIDAD = [("extraversion", "introversion"), ("sensing", "intuition"),
                      ("thinking", "feeling"), ("judging", "perceptive")]
ORIGENES = {"real", "sintetico"}


def _entero_en(valor, minimo, maximo):
    return isinstance(valor, int) and not isinstance(valor, bool) and minimo <= valor <= maximo


def validar_perfil_bruto(perfil: dict) -> list:
    """Devuelve la lista de errores del perfil segun las reglas del Anexo A."""
    errores = []
    if set(perfil) != {"id", "origen", "chaside", "ils", "personalidad"}:
        errores.append(f"claves de primer nivel inesperadas: {sorted(perfil)}")
    if not isinstance(perfil.get("id"), str) or not perfil.get("id"):
        errores.append("id vacio o no es texto")
    if perfil.get("origen") not in ORIGENES:
        errores.append(f"origen debe ser uno de {sorted(ORIGENES)}")

    chaside = perfil.get("chaside", {})
    if set(chaside) != set(AREAS_CHASIDE):
        errores.append(f"chaside debe tener exactamente las areas {AREAS_CHASIDE}")
    for area in AREAS_CHASIDE:
        a = chaside.get(area, {})
        if set(a) != {"interes", "aptitud", "total"}:
            errores.append(f"chaside.{area}: claves deben ser interes, aptitud y total")
            continue
        if not _entero_en(a["interes"], 0, 10):
            errores.append(f"chaside.{area}.interes fuera de 0-10: {a['interes']}")
        if not _entero_en(a["aptitud"], 0, 4):
            errores.append(f"chaside.{area}.aptitud fuera de 0-4: {a['aptitud']}")
        if a["total"] != a["interes"] + a["aptitud"]:
            errores.append(f"chaside.{area}.total ({a['total']}) != interes + aptitud")

    ils = perfil.get("ils", {})
    polos_ils = {p for par in PARES_ILS for p in par}
    if set(ils) != polos_ils:
        errores.append(f"ils debe tener exactamente los polos {sorted(polos_ils)}")
    else:
        for izq, der in PARES_ILS:
            if not (_entero_en(ils[izq], 0, 11) and _entero_en(ils[der], 0, 11)):
                errores.append(f"ils.{izq}/{der} fuera de 0-11")
            elif ils[izq] + ils[der] != 11:
                errores.append(f"ils.{izq} + ils.{der} = {ils[izq] + ils[der]} (debe sumar 11)")

    pers = perfil.get("personalidad", {})
    polos_pers = {p for par in PARES_PERSONALIDAD for p in par}
    if set(pers) != polos_pers:
        errores.append(f"personalidad debe tener exactamente los polos {sorted(polos_pers)}")
    else:
        for polo in sorted(polos_pers):
            if not _entero_en(pers[polo], 0, 9):
                errores.append(f"personalidad.{polo} fuera de 0-9: {pers[polo]}")
    return errores
