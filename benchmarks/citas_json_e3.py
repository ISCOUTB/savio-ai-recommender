"""Amplia citas a JSON y variantes etiquetadas, sin modificar la evidencia.

La copia de puntajes JSON cuenta como cita numerica; no como interpretacion.
La misma regla se aplica a base, ajustado y Teacher. Una repeticion incorrecta
no se oculta seleccionando solo la primera cita.
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import rubrica_e3 as rubrica  # noqa: E402


def direcciones_explicitas(texto, perfil):
    """Detecta inversiones explicitas de polo, incluso con conteos correctos.

    No interpreta una simple lista de ambos polos como una preferencia.
    Tampoco convierte ausencia de contradiccion reconocida en aprobacion.
    """
    hallazgos = []
    partes = rubrica.secciones(texto)
    for seccion, campo, pares in ((1, "ils", rubrica.it.PARES_ILS), (2, "personalidad", rubrica.it.EJES_PERSONALIDAD)):
        for frase in re.split(r"[.!?\n]+", partes.get(seccion, "")):
            if re.search(r"\b\w+\s*=\s*\d", frase):
                continue
            disparadores = list(re.finditer(r"\b(?:inclinacion(?:es)?|mayor conteo|preferencia(?:s)?|predominio|dominancia)\b", frase))
            positivos = [m for m in disparadores if not re.search(r"\b(?:no|sin|ni|ninguna)\b", frase[max(0, m.start() - 35):m.start()])]
            if not positivos:
                continue
            for a, b in pares:
                citados = [p for p in (a, b) if re.search(rf"\b(?:{rubrica.ALIAS[p]})\b", frase)]
                if len(citados) != 1:
                    continue
                polo = citados[0]
                x, y = perfil[campo][a], perfil[campo][b]
                esperado = a if x > y else b if y > x else "empate"
                if polo != esperado:
                    hallazgos.append({"eje": f"{campo}.{a}_{b}", "esperado": esperado, "afirmado": polo, "fragmento": frase.strip()})
    return hallazgos


def chaside_explicito(texto, perfil):
    """Distingue la letra A de la preposicion a y respeta negaciones."""
    normalizado = rubrica.it.normalizar_secciones(texto)
    normalizado = "".join(c for c in unicodedata.normalize("NFKD", normalizado) if not unicodedata.combining(c)).replace("*", "")
    inicio = normalizado.find(rubrica.it.SECCIONES[2])
    final = normalizado.find(rubrica.it.SECCIONES[3], inicio + 1)
    cuerpo = normalizado[inicio:final if final >= 0 else len(normalizado)] if inicio >= 0 else ""
    esperados = rubrica.baremos_esperados(perfil)
    citas = {area: [] for area in rubrica.it.AREAS_CHASIDE}
    fragmentos = {area: [] for area in rubrica.it.AREAS_CHASIDE}
    for frase in re.split(r"[.!?\n]+", cuerpo):
        if re.search(r"\b(?:interes|aptitud|total)\s*=", frase, re.IGNORECASE):
            continue
        global_banda = re.search(r"(?:todos? (?:los |las )?(?:ejes|areas|totales)|siete areas)[^.;]*?\b(media|alta|baja)s?\b", frase, re.IGNORECASE)
        if global_banda and not re.search(r"\b(?:no|sin|excepto|salvo)\b", global_banda.group(0), re.IGNORECASE):
            for area in citas:
                citas[area].append((global_banda.group(1).lower(), None))
                fragmentos[area].append(frase.strip())
        patron = r"\b([CHASIDE](?:(?:\s*,\s*|\s+y\s+)[CHASIDE])*)\b([^.;:]{0,100}?)\b(alta|media|baja)s?\b"
        for hallazgo in re.finditer(patron, frase):
            # No adjudicar el adjetivo si aparece otra area dentro del enlace.
            enlace = hallazgo.group(2)
            if re.search(r"\b(?:no|sin|ni|excepto|salvo)\b", enlace, re.IGNORECASE) or re.search(r"\b[CHASIDE]\b", enlace):
                continue
            for area in re.findall(r"\b[CHASIDE]\b", hallazgo.group(1)):
                citas[area].append((hallazgo.group(3), None))
                fragmentos[area].append(frase.strip())
    resultado = {}
    for area, observadas in citas.items():
        clave = f"chaside.{area}"
        referencia = esperados[clave]
        estado = "sin_evaluar" if not observadas else "correcto" if all(banda == referencia["banda"] for banda, _ in observadas) else "contradiccion"
        resultado[clave] = {"esperado": referencia, "estado": estado, "afirmaciones": observadas, "fragmentos": fragmentos[area]}
    return resultado


def citas_ampliadas(texto):
    citas = rubrica.citas_etiquetadas(texto)
    texto = rubrica.limpio(texto)
    # Variante observada: '- C=interes=3 / aptitud=4 / total=7'.
    # La regla inicial solo reconoce el separador ':' despues del area.
    for linea in texto.splitlines():
        area = re.match(r"\s*(?:[-+]\s*)?([chaside])\s*=\s*(.*)", linea)
        if area:
            for campo in ("interes", "aptitud", "total"):
                valores = re.findall(rf"\b{campo}\s*(?:=|:)\s*(-?\d+(?:[.,]\d+)?)", area.group(2))
                if valores:
                    clave = f"chaside.{area.group(1).upper()}.{campo}"
                    citas.setdefault(clave, []).extend(float(v.replace(",", ".")) for v in valores)
    # El parser inicial ya reconoce key=N, key: N y key (N). Aqui se
    # incorporan claves entre comillas, para no contar dos veces lo mismo.
    for campo, pares in (("ils", rubrica.it.PARES_ILS), ("personalidad", rubrica.it.EJES_PERSONALIDAD)):
        for par in pares:
            for polo in par:
                patron = rf"[\"']{polo}[\"']\s*:\s*(-?\d+(?:\.\d+)?)"
                valores = [float(v) for v in re.findall(patron, texto)]
                if valores:
                    citas.setdefault(f"{campo}.{polo}", []).extend(valores)
    # Reconoce las areas completas incluso dentro de un JSON final truncado.
    for area in re.finditer(r"[\"']([chaside])[\"']\s*:\s*\{([^{}]*)\}", texto):
        for campo in ("interes", "aptitud", "total"):
            patron = rf"[\"']{campo}[\"']\s*:\s*(-?\d+(?:\.\d+)?)"
            valores = [float(v) for v in re.findall(patron, area.group(2))]
            if valores:
                citas.setdefault(f"chaside.{area.group(1).upper()}.{campo}", []).extend(valores)
    return citas


def auditar_ampliado(texto, perfil):
    resultado = rubrica.auditar(texto, perfil)
    resultado["baremos"].update(chaside_explicito(texto, perfil))
    resultado["direcciones_contradictorias_reconocidas"] = direcciones_explicitas(texto, perfil)
    esperados = rubrica.esperados(perfil)
    citas = citas_ampliadas(texto)
    correctos = [k for k, valores in citas.items() if k in esperados and all(v == esperados[k] for v in valores)]
    errores = {k: {"esperado": esperados[k], "citado": valores} for k, valores in citas.items() if k in esperados and any(v != esperados[k] for v in valores)}
    resultado["numerica"] = {
        "esperados": len(esperados), "campos_citados": len(citas), "campos_correctos": len(correctos),
        "errores": errores, "faltantes": sorted(set(esperados) - set(citas)),
        "escalas_o_rangos": resultado["numerica"]["escalas_o_rangos"],
    }
    return resultado


def main():
    parser = argparse.ArgumentParser(description="Audita una salida sintetica sin invocar Ollama ni modificarla.")
    parser.add_argument("--perfil", required=True, type=Path)
    parser.add_argument("--salida", required=True, type=Path)
    args = parser.parse_args()
    perfil = json.loads(args.perfil.read_text(encoding="utf-8-sig"))
    if perfil.get("origen") != "sintetico":
        raise SystemExit("[FALLO] este auditor publico solo admite perfiles sinteticos")
    salida = json.loads(args.salida.read_text(encoding="utf-8"))
    texto = salida.get("perfil_markdown", salida.get("respuesta_ollama", {}).get("response"))
    if not isinstance(texto, str):
        raise SystemExit("[FALLO] salida sin perfil_markdown ni respuesta_ollama.response")
    resultado = auditar_ampliado(texto, perfil)
    numeros = resultado["numerica"]
    fallos = bool(numeros["errores"] or numeros["faltantes"] or numeros["escalas_o_rangos"]
                  or resultado["direcciones_contradictorias_reconocidas"]
                  or any(v["estado"] == "contradiccion" for v in resultado["baremos"].values())
                  or not resultado["estructura_ok"] or not resultado["guardrail_backend_ok"]
                  or resultado["alerta_revision_profesional_inventada"])
    print(json.dumps({"fallos_detectados": fallos, "revision_integral_pendiente": True,
                      "alcance": "auditoria parcial; el texto leido puede incluir postprocesamiento del backend", "auditoria": resultado}, indent=2, ensure_ascii=True))
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
