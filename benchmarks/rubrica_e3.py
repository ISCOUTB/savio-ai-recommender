"""Rubrica determinista parcial de E3-09; no sustituye revision profesional.

Cuenta citas etiquetadas, separa omisiones de errores y comprueba afirmaciones
explicitas de bandas/polos. Lo no reconocido queda sin evaluar, nunca aprobado.
Los 37 conteos y las bandas salen del perfil bruto y los baremos del proyecto.
"""

import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "poc_slm"))
import interpretador as it  # noqa: E402


def limpio(texto):
    return "".join(
        c for c in unicodedata.normalize("NFKD", texto.lower())
        if not unicodedata.combining(c)
    ).replace("*", "").replace("`", "")


def esperados(perfil):
    valores = {}
    for campo in ("ils", "personalidad"):
        valores.update({f"{campo}.{k}": v for k, v in perfil[campo].items()})
    for area, datos in perfil["chaside"].items():
        valores.update({f"chaside.{area}.{k}": v for k, v in datos.items()})
    return valores


def citas_etiquetadas(texto):
    """Reconoce key=N, key: N y key (N); no adivina numeros sin etiqueta."""
    texto = limpio(texto)
    citas = {}
    polos = [("ils", par) for par in it.PARES_ILS]
    polos += [("personalidad", par) for par in it.EJES_PERSONALIDAD]
    for campo, par in polos:
        for polo in par:
            patron = rf"\b{polo}\b\s*(?:=|:|\()\s*(-?\d+(?:[.,]\d+)?)"
            valores = re.findall(patron, texto)
            if valores:
                citas[f"{campo}.{polo}"] = [float(v.replace(",", ".")) for v in valores]
    for linea in texto.splitlines():
        area = re.match(r"\s*(?:[-+]\s*)?([chaside])\s*(?:\([^)]*\))?\s*:", linea)
        if not area:
            continue
        for campo in ("interes", "aptitud", "total"):
            valores = re.findall(rf"\b{campo}\s*(?:=|:)\s*(-?\d+(?:[.,]\d+)?)", linea)
            if valores:
                clave = f"chaside.{area.group(1).upper()}.{campo}"
                citas.setdefault(clave, []).extend(float(v.replace(",", ".")) for v in valores)
    return citas


def secciones(texto):
    texto = limpio(it.normalizar_secciones(texto))
    marcas = list(re.finditer(r"^## ([1-4])\. [^\n]+", texto, re.MULTILINE))
    return {
        int(m.group(1)): texto[m.end():marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)]
        for i, m in enumerate(marcas)
    }


ALIAS = {
    "activo": r"activ[oa]", "reflexivo": r"reflexiv[oa]",
    "sensitivo": r"sensitiv[oa]", "intuitivo": r"intuitiv[oa]",
    "visual": r"visual", "verbal": r"verbal",
    "secuencial": r"secuencial", "global": r"global",
    "extraversion": r"extraversion|extravertid[oa]",
    "introversion": r"introversion|introvertid[oa]",
    "sensing": r"sensing", "intuition": r"intuition",
    "thinking": r"thinking", "feeling": r"feeling",
    "judging": r"judging", "perceptive": r"perceptive",
}
EJES = ("energia", "percepcion", "decision", "organizacion|estilo de vida")


def baremos_esperados(perfil):
    etiquetas = {}
    for campo, pares, umbral in (("ils", it.PARES_ILS, 9), ("personalidad", it.EJES_PERSONALIDAD, 4)):
        for a, b in pares:
            x, y = perfil[campo][a], perfil[campo][b]
            polo = a if x > y else b if y > x else "empate"
            etiquetas[f"{campo}.{a}_{b}"] = {
                "banda": "preferencia" if abs(x - y) >= umbral else "sin_preferencia",
                "polo_mayor": polo,
            }
    for area, datos in perfil["chaside"].items():
        total = datos["total"]
        etiquetas[f"chaside.{area}"] = {"banda": "alta" if total >= 11 else "media" if total >= 6 else "baja"}
    return etiquetas


def evaluar_baremos(texto, perfil):
    """Solo puntua afirmaciones cuyo alcance y polo son explicitamente legibles.

    Una banda sin polo no acredita una preferencia. Una omision no acredita
    fidelidad. Esta rubrica parcial no evalua correlaciones ni toda la prosa.
    """
    partes = secciones(texto)
    esperado = baremos_esperados(perfil)
    afirmaciones = {clave: [] for clave in esperado}
    evidencias = {clave: [] for clave in esperado}
    for numero, campo, pares in ((1, "ils", it.PARES_ILS), (2, "personalidad", it.EJES_PERSONALIDAD)):
        cuerpo = partes.get(numero, "")
        for frase in re.split(r"[.!?\n]+", cuerpo):
            # Los conteos correctos no demuestran que la prosa los interprete bien.
            if not frase.strip() or re.search(r"\b\w+\s*=\s*\d", frase):
                continue
            neutral = bool(re.search(r"equilibrad|sin preferencias? (?:claras?|marcadas?)|no (?:hay|se establece) preferencia", frase))
            todos = bool(re.search(r"(?:todos? (?:los )?(?:ejes|pares)|(?:los )?cuatro (?:ejes|pares))", frase))
            for indice, (a, b) in enumerate(pares):
                clave = f"{campo}.{a}_{b}"
                menciona = any(re.search(rf"\b(?:{ALIAS[p]})\b", frase) for p in (a, b))
                menciona = menciona or (campo == "personalidad" and bool(re.search(rf"\b(?:{EJES[indice]})\b", frase)))
                if neutral and (todos or menciona):
                    afirmaciones[clave].append(("sin_preferencia", None))
                    evidencias[clave].append(frase.strip())
                # Preferencia positiva explicita; evita interpretar una negacion como afirmacion.
                for polo in (a, b):
                    patrones = (
                        rf"(?:preferencia(?: marcada)?|predominio|dominancia)\s+(?:(?:hacia|por|del polo)\s+)?(?:{ALIAS[polo]})\b",
                        rf"\b(?:{ALIAS[polo]})\s+(?:es|resulta)\s+(?:el polo )?dominante\b",
                    )
                    for patron in patrones:
                        for hallazgo in re.finditer(patron, frase):
                            prefijo = frase[max(0, hallazgo.start() - 45):hallazgo.start()]
                            if re.search(r"\b(?:no|sin|ni|ninguna)\b", prefijo):
                                continue
                            afirmaciones[clave].append(("preferencia", polo))
                            evidencias[clave].append(frase.strip())
    for frase in re.split(r"[.!?\n]+", partes.get(3, "")):
        if not frase.strip() or re.search(r"\b(?:interes|aptitud|total)\s*=", frase):
            continue
        global_banda = re.search(r"(?:todos? (?:los |las )?(?:ejes|areas|totales)|siete areas)[^.;]*?\b(?:medias?|altas?|bajas?)\b", frase)
        if global_banda:
            banda = re.findall(r"\b(media|alta|baja)s?\b", global_banda.group(0))[-1]
            for area in it.AREAS_CHASIDE:
                afirmaciones[f"chaside.{area}"].append((banda, None))
                evidencias[f"chaside.{area}"].append(frase.strip())
        # Listas explicitas: 'A, S y D quedan en banda media'.
        patron = r"\b([chaside](?:(?:\s*,\s*|\s+y\s+)[chaside])*)\b\s*(?:\([^)]*\)|,\s*[a-z]+,)?\s*(?:presenta[n]?|queda[n]?|son|es|tambien son|tiene[^.;]*?en)?\s*(?:(?:afinidad|banda)\s+)?(alta|media|baja)s?\b"
        for hallazgo in re.finditer(patron, frase):
            for area in re.findall(r"\b[chaside]\b", hallazgo.group(1)):
                clave = f"chaside.{area.upper()}"
                afirmaciones[clave].append((hallazgo.group(2), None))
                evidencias[clave].append(frase.strip())
    detalles = {}
    for clave, referencia in esperado.items():
        observadas = afirmaciones[clave]
        correctas = [banda == referencia["banda"] and (banda != "preferencia" or polo == referencia["polo_mayor"]) for banda, polo in observadas]
        estado = "sin_evaluar" if not observadas else "correcto" if all(correctas) else "contradiccion"
        detalles[clave] = {"esperado": referencia, "estado": estado, "afirmaciones": observadas, "fragmentos": evidencias[clave]}
    return detalles


def auditar(texto, perfil):
    valores = esperados(perfil)
    citas = citas_etiquetadas(texto)
    correctos = [k for k, v in citas.items() if k in valores and all(n == valores[k] for n in v)]
    errores = {k: {"esperado": valores[k], "citado": v} for k, v in citas.items() if k in valores and any(n != valores[k] for n in v)}
    faltantes = sorted(set(valores) - set(citas))
    normalizado = it.normalizar_secciones(texto)
    publicado = it.agregar_aviso(normalizado)
    escala, _ = it.problemas_fidelidad(normalizado, perfil)
    return {
        "numerica": {"esperados": len(valores), "campos_citados": len(citas), "campos_correctos": len(correctos), "errores": errores, "faltantes": faltantes, "escalas_o_rangos": escala},
        "estructura_ok": not it.validar_estructura(normalizado),
        "guardrail_crudo_ok": not it.validar_salida_etica(normalizado),
        "guardrail_backend_ok": not it.validar_salida_etica(publicado),
        "aviso_agregado": publicado != normalizado,
        "baremos": evaluar_baremos(texto, perfil),
        "alerta_revision_profesional_inventada": bool(re.search(r"(?:vist[oa]|revisad[oa]|validad[oa]|aprobad[oa]) por un profesional", limpio(texto))),
    }
