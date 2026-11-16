"""Lectura determinista y controles parciales de los baremos E3-04.

Aplica las convenciones de docs/especificaciones/baremos-psicometricos.md.
No cambia puntajes, no crea indices ni constituye una interpretacion clinica.
El control de prosa reconoce patrones explicitos; no certifica toda la salida.
"""

import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "docs/especificaciones"))
from contrato_bruto import (  # noqa: E402
    AREAS_CHASIDE, PARES_ILS, POLOS_PERSONALIDAD,
    validar_chaside, validar_ils, validar_personalidad,
)
from guardrail_etico import AVISO_NO_CLINICO  # noqa: E402

PARES_PERSONALIDAD = tuple(zip(POLOS_PERSONALIDAD[::2], POLOS_PERSONALIDAD[1::2]))
ALIAS = {
    "activo": "activ[oa]", "reflexivo": "reflexiv[oa]",
    "sensitivo": "sensitiv[oa]", "intuitivo": "intuitiv[oa]",
    "visual": "visual", "verbal": "verbal", "secuencial": "secuencial", "global": "global",
    "extraversion": "extraversion|extravertid[oa]", "introversion": "introversion|introvertid[oa]",
    "sensing": "sensing", "intuition": "intuition", "thinking": "thinking", "feeling": "feeling",
    "judging": "judging", "perceptive": "perceptive",
}
NOMBRES_EJES = ("energia", "percepcion", "decision", "organizacion|estilo de vida")


def calcular_lecturas(perfil):
    """Obtiene bandas, mayor conteo y empates sin mutar el perfil recibido."""
    errores = validar_chaside(perfil.get("chaside"), "perfil")
    errores += validar_ils(perfil.get("ils"), "perfil")
    errores += validar_personalidad(perfil.get("personalidad"), "perfil")
    if errores:
        raise ValueError("; ".join(errores))
    lectura = {"ils": {}, "personalidad": {}, "chaside": {}}
    for campo, pares, umbral in (("ils", PARES_ILS, 9), ("personalidad", PARES_PERSONALIDAD, 4)):
        for a, b in pares:
            x, y = perfil[campo][a], perfil[campo][b]
            marcada = abs(x - y) >= umbral
            banda = ("preferencia marcada" if marcada else "sin preferencia clara") if campo == "ils" else ("preferencia" if marcada else "equilibrado")
            lectura[campo][f"{a}/{b}"] = {
                "diferencia_absoluta": abs(x - y), "banda": banda,
                "polo_mayor": a if x > y else b if y > x else None, "empate": x == y,
            }
    for area in AREAS_CHASIDE:
        total = perfil["chaside"][area]["total"]
        lectura["chaside"][area] = {"banda": "alta" if total >= 11 else "media" if total >= 6 else "baja"}
    return lectura


def filas_baremos(perfil):
    """Filas de lectura compactas que el modelo debe reproducir sin reclasificar."""
    lectura = calcular_lecturas(perfil)
    filas = {"ils": [], "personalidad": [], "chaside": []}
    for campo in ("ils", "personalidad"):
        for eje, datos in lectura[campo].items():
            a, b = eje.split("/")
            descripcion = datos["banda"]
            if datos["banda"] in ("preferencia", "preferencia marcada"):
                descripcion += " hacia " + datos["polo_mayor"]
            elif campo == "personalidad":
                descripcion += "; " + ("empate exacto" if datos["empate"] else "sin empate")
            filas[campo].append(f"- {a}={perfil[campo][a]} / {b}={perfil[campo][b]}; {descripcion}.")
    for area, datos in lectura["chaside"].items():
        valores = perfil["chaside"][area]
        filas["chaside"].append(f"- {area}: interes={valores['interes']}, aptitud={valores['aptitud']}, total={valores['total']}; banda {datos['banda']}.")
    return filas


def reforzar_prompt(perfil, texto_base, aviso):
    """Agrega hechos y un contrato de salida acotado; conserva los brutos."""
    filas = filas_baremos(perfil)
    lineas = [texto_base, "", "REGLAS Y LECTURA OBLIGATORIA DEL PROYECTO:",
        "ILS: diferencia absoluta 9 u 11 = preferencia marcada; 1, 3, 5 o 7 = sin preferencia clara.",
        "Personalidad: diferencia absoluta de 4 o mas = preferencia; de 0 a 3 = equilibrado.",
        "No apliques el umbral ILS de 9 a personalidad: personalidad usa el umbral 4.",
        "Equilibrado no significa empate. Solo hay empate cuando ambos conteos son iguales.",
        "CHASIDE: total de 11 a 14 = banda alta; de 6 a 10 = media; de 0 a 5 = baja.",
        "Son convenciones del proyecto, no puntos de corte clinicos ni baremos poblacionales.", "",
        "LECTURA CHASIDE Y DE LOS EJES CALCULADA POR EL BACKEND:",
        "FORMATO OBLIGATORIO: reproduce estas tres secciones y sus filas exactamente, sin parrafos ni resumenes adicionales:",
        "## 1. Estilos de aprendizaje", *filas["ils"], "", "## 2. Rasgos de personalidad", *filas["personalidad"],
        "", "## 3. Perfil vocacional", *filas["chaside"], "", "## 4. Sintesis integrada",
        "Redacta una o dos frases originales que indiquen una tarea concreta que podria hacer el estudiante y el material o recurso para realizarla.",
        "No repitas instrucciones ni digas solamente que se propongan actividades. Describe directamente que se podria hacer y con que.",
        "En la sintesis no menciones numeros, letras CHASIDE, bandas, polos, preferencias, comparaciones ni carreras. No vuelvas a clasificar resultados.",
        "No inventes capacidades, causas ni revision profesional. Las tres primeras secciones ya contienen toda la lectura factual.",
        "Tras la sintesis agrega este aviso literal: " + aviso]
    return "\n".join(lineas)


def _limpio(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)).replace("*", "").replace("`", "")


def _banda_canonica(palabra):
    return {"alt": "alta", "med": "media", "baj": "baja"}[palabra.lower()[:3]]


def _citas(texto):
    texto = _limpio(texto)
    citas = {}
    for campo, pares in (("ils", PARES_ILS), ("personalidad", PARES_PERSONALIDAD)):
        for par in pares:
            for polo in par:
                valores = re.findall(rf"\b{polo}\b[\"']?\s*(?:=|:|\()\s*(-?\d+(?:[.,]\d+)?)", texto, re.IGNORECASE)
                if valores:
                    citas[f"{campo}.{polo}"] = [float(v.replace(",", ".")) for v in valores]
    bloques = [(m.group(1), m.group(2)) for m in re.finditer(r"^\s*(?:[-+]\s*)?([CHASIDE])\s*(?:=|:)\s*([^\n]+)", texto, re.MULTILINE)]
    bloques += [(m.group(1), m.group(2)) for m in re.finditer(r"[\"']([CHASIDE])[\"']\s*:\s*\{([^{}]*)\}", texto)]
    for area, bloque in bloques:
        for campo in ("interes", "aptitud", "total"):
            valores = re.findall(rf"\b{campo}\b[\"']?\s*(?:=|:)\s*(-?\d+(?:[.,]\d+)?)", bloque, re.IGNORECASE)
            if valores:
                citas.setdefault(f"chaside.{area}.{campo}", []).extend(float(v.replace(",", ".")) for v in valores)
    return citas


def problemas_lectura(texto, perfil):
    """Rechaza omisiones/citas erradas y contradicciones reconocidas en la prosa.

    Un resultado sin hallazgos sigue requiriendo revision semantica integral.
    """
    lectura = calcular_lecturas(perfil)
    citas = _citas(texto)
    esperado = {f"{campo}.{p}": v for campo in ("ils", "personalidad") for p, v in perfil[campo].items()}
    esperado.update({f"chaside.{area}.{campo}": v for area, datos in perfil["chaside"].items() for campo, v in datos.items()})
    errores = []
    for clave, valor in esperado.items():
        if clave not in citas:
            errores.append(f"falta citar el puntaje {clave}")
        elif any(v != valor for v in citas[clave]):
            errores.append(f"puntaje {clave} distinto de la entrada: corresponde {valor}")
    texto = _limpio(texto)
    marcas = list(re.finditer(r"^\s*## ([1-4])\. [^\n]+", texto, re.MULTILINE))
    partes = {int(m.group(1)): texto[m.end():marcas[i+1].start() if i+1 < len(marcas) else len(texto)] for i, m in enumerate(marcas)}
    filas = filas_baremos(perfil)
    for numero, campo in ((1, "ils"), (2, "personalidad"), (3, "chaside")):
        observadas = [_normalizar_fila(l) for l in partes.get(numero, "").splitlines() if l.strip()]
        requeridas = [_normalizar_fila(l) for l in filas[campo]]
        if sorted(observadas) != sorted(requeridas):
            errores.append(f"{campo}: la seccion debe contener solo las filas calculadas, completas y sin resumen adicional")
    sintesis = partes.get(4, "").lower().replace(_limpio(AVISO_NO_CLINICO).lower(), "").replace("---", "").strip()
    if not sintesis or len(sintesis.split()) > 80 or len([f for f in re.split(r"[.!?]+", sintesis) if f.strip()]) > 2:
        errores.append("sintesis: se requieren una o dos frases breves, ademas del aviso")
    if re.search(r"actividades o contextos|compatibles con (?:las|estas) lecturas|escribe aqui|una o dos frases|redacta .*frases|describe directamente", sintesis):
        errores.append("sintesis: repite instrucciones o una formula generica; requiere una propuesta concreta")
    palabras = [*ALIAS.values(), "chaside", "bandas?", "preferencias?", "equilibrad[oa]s?", "empates?", "alt[oa]s?", "medi[oa]s?", "baj[oa]s?", "mayor(?:es)?", "menor(?:es)?", "dominancia", "carreras?"]
    if re.search(r"\d|\b(?:" + "|".join(palabras) + r")\b", sintesis) or re.search(r"\barea\s+[CHASIDE]\b", sintesis, re.IGNORECASE):
        errores.append("sintesis: no debe reclasificar numeros, bandas o polos; la lectura ya esta en las filas")
    for numero, campo, pares in ((1, "ils", PARES_ILS), (2, "personalidad", PARES_PERSONALIDAD)):
        for frase in re.split(r"[.!?\n]+", partes.get(numero, "").lower()):
            if re.search(r"\b\w+\s*=\s*\d", frase):
                continue
            global_neutral = bool(re.search(r"(?:todos? (?:los )?(?:ejes|pares)|los cuatro ejes)[^.;]*(?:equilibrad|sin preferencias? (?:claras?|marcadas?))", frase))
            if re.search(r"\bno (?:todos|son|quedan)\b", frase):
                global_neutral = False
            if campo == "personalidad" and all(d["banda"] == "preferencia" for d in lectura[campo].values()) and re.search(r"otros ejes[^.;]*equilibrad", frase):
                errores.append("personalidad: declara otros ejes equilibrados, pero los cuatro tienen preferencia")
            for indice, (a, b) in enumerate(pares):
                datos = lectura[campo][f"{a}/{b}"]
                neutral = datos["banda"] in ("sin preferencia clara", "equilibrado")
                if global_neutral and not neutral:
                    errores.append(f"{campo}.{a}/{b}: declara equilibrio global pero corresponde {datos['banda']} hacia {datos['polo_mayor']}")
                if campo == "personalidad" and not datos["empate"]:
                    for hallazgo in re.finditer(rf"empate[^.;]*\b(?:{NOMBRES_EJES[indice]})\b", frase):
                        prefijo = frase[max(0, hallazgo.start()-25):hallazgo.start()]
                        if not re.search(r"\b(?:no|sin|ningun)\b", prefijo):
                            errores.append(f"personalidad.{a}/{b}: declara un empate inexistente")
                mencionados = [p for p in (a, b) if re.search(rf"\b(?:{ALIAS[p]})\b", frase)]
                if len(mencionados) != 1:
                    continue
                for disparador in re.finditer(r"\b(?:inclinacion(?:es)?|mayor conteo|preferencia(?:s)?|predominio|dominancia)\b", frase):
                    prefijo = frase[max(0, disparador.start()-35):disparador.start()]
                    if re.search(r"\b(?:no|sin|ni|ninguna)\b", prefijo):
                        continue
                    if mencionados[0] != datos["polo_mayor"]:
                        errores.append(f"{campo}.{a}/{b}: invierte el polo mayor; corresponde {datos['polo_mayor'] or 'empate'}")
                    if disparador.group(0).startswith(("preferencia", "predominio", "dominancia")) and neutral:
                        errores.append(f"{campo}.{a}/{b}: afirma preferencia pero corresponde {datos['banda']}")
    for linea in partes.get(3, "").splitlines():
        hallazgo = re.match(r"\s*(?:[-+]\s*)?([CHASIDE])\s*(?:=|:).*?\b(?:banda|afinidad)\s*(?:=|:)?\s*(alt[oa]|medi[oa]|baj[oa])\b", linea)
        if hallazgo and _banda_canonica(hallazgo.group(2)) != lectura["chaside"][hallazgo.group(1)]["banda"]:
            errores.append(f"CHASIDE {hallazgo.group(1)}: banda junto a puntajes incorrecta; corresponde {lectura['chaside'][hallazgo.group(1)]['banda']}")
    for frase in re.split(r"[.!?\n]+", partes.get(3, "")):
        if re.search(r"\b(?:interes|aptitud|total)\s*=", frase, re.IGNORECASE):
            continue
        global_banda = re.search(r"(?:todos? (?:los |las )?(?:ejes|areas|totales)|siete areas)[^.;]*?\b(medi[oa]|alt[oa]|baj[oa])s?\b", frase, re.IGNORECASE)
        if global_banda and not re.search(r"\b(?:no|sin|excepto|salvo)\b", global_banda.group(0), re.IGNORECASE):
            for area, datos in lectura["chaside"].items():
                if _banda_canonica(global_banda.group(1)) != datos["banda"]:
                    errores.append(f"CHASIDE {area}: banda global incorrecta; corresponde {datos['banda']}")
        for hallazgo in re.finditer(r"\b([CHASIDE](?:(?:\s*,\s*|\s+[ye]\s+)[CHASIDE])*)\b([^.;:]{0,100}?)\b(alt[oa]|medi[oa]|baj[oa])s?\b", frase):
            enlace = hallazgo.group(2)
            if re.search(r"\b(?:no|sin|ni|excepto|salvo)\b", enlace, re.IGNORECASE) or re.search(r"\b[CHASIDE]\b", enlace):
                continue
            for area in re.findall(r"\b[CHASIDE]\b", hallazgo.group(1)):
                if _banda_canonica(hallazgo.group(3)) != lectura["chaside"][area]["banda"]:
                    errores.append(f"CHASIDE {area}: banda incorrecta; corresponde {lectura['chaside'][area]['banda']}")
    bajo = texto.lower()
    for hallazgo in re.finditer(r"(?:vist[oa]|revisad[oa]|validad[oa]|aprobad[oa]) por un profesional", bajo):
        if not re.search(r"\b(?:no|sin|nunca)\b", bajo[max(0, hallazgo.start()-35):hallazgo.start()]):
            errores.append("afirma revision profesional sin evidencia")
    return list(dict.fromkeys(errores))


def _normalizar_fila(linea):
    """Tolera espacios, mayusculas y punto final; no cambia valores ni bandas."""
    return re.sub(r"\s+", "", _limpio(linea).lower().rstrip(". "))
