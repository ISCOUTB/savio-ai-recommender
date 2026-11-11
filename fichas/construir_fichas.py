"""construir_fichas.py - Base de fichas interpretativas con fuente (Entrega 3, OE1 / E3-06).

Construye fichas/fichas_interpretativas.json a partir de fuentes verificables:

  - CHASIDE (70 fichas): matriz oficial del bloque institucional block_chaside
    (lang/es), una ficha por area x nivel (alto/medio/emergente) x brecha
    (balanceado/interes/aptitud) mas una de nivel bajo por area. Reglas de nivel y
    brecha tomadas de classes/facade.php del mismo bloque.
  - ILS (24 fichas): 4 dimensiones x 2 polos x 3 bandas. Texto del polo tomado del
    bloque block_learning_style (lang/es); fuerza de la preferencia segun Felder y
    Soloman (s. f.); bandas 1-3 / 5-7 / 9-11 del documento de formulacion (seccion 8).
  - Personalidad (8 + 16 fichas): un polo por ficha con la definicion de la Myers &
    Briggs Foundation (traducida; cita original incluida) y los 16 tipos descritos
    por el bloque block_personality_test (lang/es). Por R08, el tipo de 4 letras es
    contexto y no una etiqueta para el estudiante.
  - Principios (3 fichas): advertencias de las fuentes sobre el uso de los resultados.

Los textos de los bloques se descargan en un commit fijo (ver BLOQUES) para que la
base sea reproducible. Requiere internet (raw.githubusercontent.com, sin token).

Uso (desde la raiz del repo):
    python fichas/construir_fichas.py
"""

import json
import re
import sys
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "fichas" / "fichas_interpretativas.json"
VERSION = "1.0.0"

BLOQUES = {
    "chaside": "afd053afc3d95c8bcbf2df039a38501dadbff459",
    "learning_style": "8ee2def97e299142c97c70846d1a459fcf9beddd",
    "personality_test": "426a1013c17eb58fb522596b4d2b1c894c8b2720",
}
FELDER_SOLOMAN = ("Felder, R. M., y Soloman, B. A. (s. f.). Learning styles and strategies. North Carolina State "
                  "University. https://www.engr.ncsu.edu/wp-content/uploads/drive/1WPAfj3j5o5OuJMiHorJ-lv6fON1C8kCN/styles.pdf")
MBF_PREFERENCIAS = "https://www.myersbriggs.org/my-mbti-personality-type/the-mbti-preferences/"
MBF_OVERVIEW = "https://www.myersbriggs.org/my-mbti-personality-type/myers-briggs-overview/"
FORMULACION = "Documento de formulacion del proyecto (v5), seccion 8: bandas del ILS 1-3, 5-7 y 9-11"


def fuente_bloque(repo, clave):
    return {"tipo": "bloque_institucional", "referencia": f"ISCOUTB (2026). block_{repo}. https://github.com/ISCOUTB/{repo}",
            "ubicacion": f"lang/es/block_{repo}.php @ {BLOQUES[repo][:7]}, $string['{clave}']"}


def descargar_cadenas(repo):
    url = f"https://raw.githubusercontent.com/ISCOUTB/{repo}/{BLOQUES[repo]}/lang/es/block_{repo}.php"
    php = urllib.request.urlopen(url, timeout=60).read().decode("utf-8")
    cadenas = {}
    for m in re.finditer(r"\$string\[(['\"])(.+?)\1\]\s*=\s*(['\"])((?:\\.|(?!\3).)*)\3\s*;", php, re.S):
        cadenas[m.group(2)] = m.group(4).replace("\\'", "'").replace('\\"', '"')
    return cadenas


# ------------------------------------------------------------------ CHASIDE
NIVELES_CH = [("alto", "high", "pct_total >= 80 (total 12-14)"), ("medio", "medium", "60 <= pct_total < 80 (total 9-11)"),
              ("emergente", "emerging", "40 <= pct_total < 60 (total 6-8)")]
BRECHAS_CH = [("balanceado", "balanced", "|pct_interes - pct_aptitud| < 20"),
              ("interes_mayor", "interest", "pct_interes - pct_aptitud >= 20"),
              ("aptitud_mayor", "aptitude", "pct_aptitud - pct_interes >= 20")]


def fichas_chaside(c):
    fichas = []
    for area in "CHASIDE":
        nombre = c[f"area_{area.lower()}"]
        for nivel, suf_n, regla_n in NIVELES_CH:
            for brecha, suf_b, regla_b in BRECHAS_CH:
                clave = f"interpretation_{area.lower()}_{suf_n}_{suf_b}"
                fichas.append({"id": f"CH-{area}-{nivel}-{brecha}", "instrumento": "CHASIDE", "area": area,
                               "nombre_area": nombre, "condicion": {"nivel": nivel, "brecha": brecha},
                               "regla": f"{regla_n}; {regla_b}", "texto": c[clave],
                               "fuentes": [fuente_bloque("chaside", clave)], "verificado": True})
        clave = f"interpretation_{area.lower()}_low"
        fichas.append({"id": f"CH-{area}-bajo", "instrumento": "CHASIDE", "area": area, "nombre_area": nombre,
                       "condicion": {"nivel": "bajo"}, "regla": "pct_total < 40 (total 0-5)", "texto": c[clave],
                       "fuentes": [fuente_bloque("chaside", clave)], "verificado": True})
    return fichas


# ------------------------------------------------------------------ ILS
POLOS_ILS = [("activo", "active", "reflexivo"), ("reflexivo", "reflexive", "activo"),
             ("sensitivo", "sensorial", "intuitivo"), ("intuitivo", "intuitive", "sensitivo"),
             ("visual", "visual", "verbal"), ("verbal", "verbal", "visual"),
             ("secuencial", "sequential", "global"), ("global", "global", "secuencial")]
BANDAS_ILS = [
    ("equilibrio", "diferencia 1-3",
     "Equilibrio entre {polo} y {opuesto}, con leve inclinacion hacia {polo}. Segun Felder y Soloman, todos usamos "
     "ambos polos en distintos momentos y un equilibrio entre ellos es deseable."),
    ("moderada", "diferencia 5-7",
     "Preferencia moderada por el polo {polo}: {descripcion}. Es una preferencia de presentacion declarada, no una "
     "capacidad."),
    ("fuerte", "diferencia 9-11",
     "Preferencia fuerte por el polo {polo}: {descripcion}. Felder y Soloman senalan que conviene cultivar tambien el "
     "polo opuesto ({opuesto}), porque un equilibrio entre ambos es deseable."),
]


def fichas_ils(c):
    fichas = []
    for polo, clave_bloque, opuesto in POLOS_ILS:
        clave = f"profile_{clave_bloque}_description"
        descripcion = c[clave][0].lower() + c[clave][1:]
        for banda, regla, plantilla in BANDAS_ILS:
            fichas.append({"id": f"ILS-{polo}-{banda}", "instrumento": "ILS", "polo": polo, "opuesto": opuesto,
                           "condicion": {"banda": banda, "polo_preferido": polo}, "regla": regla,
                           "texto": plantilla.format(polo=polo, opuesto=opuesto, descripcion=descripcion),
                           "fuentes": [fuente_bloque("learning_style", clave),
                                       {"tipo": "literatura", "referencia": FELDER_SOLOMAN},
                                       {"tipo": "formulacion", "referencia": FORMULACION}],
                           "verificado": True})
    return fichas


# ------------------------------------------------------------------ Personalidad
# (polo, letra, texto en espanol, cita original, url, verificado)
POLOS_PERS = [
    ("extraversion", "E", "Las personas con preferencia por la Extraversion se sienten con energia al interactuar con el mundo exterior de personas y cosas.",
     "People who prefer Extraversion feel energized by interaction in the outer world of people and things.", MBF_PREFERENCIAS, True),
    ("introversion", "I", "Las personas con preferencia por la Introversion se sienten con energia al reflexionar sobre conceptos e ideas en su mundo interior.",
     "People who prefer Introversion feel energized when reflecting on concepts and ideas in their inner world.", MBF_PREFERENCIAS, True),
    ("sensing", "S", "Las personas con preferencia por la Sensacion prestan mas atencion a la informacion concreta y tangible.",
     "People who prefer Sensing pay more attention to information that is concrete and tangible.", MBF_PREFERENCIAS, True),
    ("intuition", "N", "Las personas con preferencia por la Intuicion prestan mas atencion a los patrones y posibilidades de la informacion que reciben.",
     "People who prefer Intuition pay more attention to the patterns and possibilities in the information they receive.", MBF_PREFERENCIAS, True),
    ("thinking", "T", "Las personas con preferencia por el Pensamiento dan mas peso a principios objetivos y hechos impersonales al decidir.",
     "People who prefer Thinking put more weight on objective principles and impersonal facts when decision-making.", MBF_PREFERENCIAS, True),
    ("feeling", "F", "Las personas con preferencia por el Sentimiento dan mas peso a las consideraciones personales y a las personas involucradas al decidir.",
     None, MBF_PREFERENCIAS, False),
    ("judging", "J", "Las personas con preferencia por el Juicio prefieren un estilo de vida mas estructurado y organizado.",
     None, MBF_PREFERENCIAS, False),
    ("perceptive", "P", "Las personas con preferencia por la Percepcion prefieren un estilo de vida mas flexible y abierto.",
     None, MBF_PREFERENCIAS, False),
]


def fichas_personalidad(c):
    fichas = []
    for polo, letra, texto, cita, url, verificado in POLOS_PERS:
        f = {"id": f"PER-{polo}", "instrumento": "personalidad", "polo": polo, "letra": letra,
             "condicion": {"polo_mayor": polo}, "texto": texto,
             "fuentes": [{"tipo": "literatura", "referencia": f"The Myers & Briggs Foundation (2026). The Preferences: E-I, S-N, T-F, J-P. {url}"},
                         fuente_bloque("personality_test", polo)],
             "verificado": verificado}
        if cita:
            f["cita_original"] = cita
        else:
            f["nota"] = "Texto tomado de un resumen de la pagina; falta verificar la cita textual en la fuente."
        fichas.append(f)
    tipos = sorted(k for k in c if re.fullmatch(r"mbti_[ei][sn][tf][jp]", k))
    for clave in tipos:
        tipo = clave[-4:].upper()
        fichas.append({"id": f"PER-TIPO-{tipo}", "instrumento": "personalidad", "tipo": tipo,
                       "condicion": {"tipo": tipo}, "texto": c[clave], "uso": "contexto",
                       "nota": "R08: el tipo de 4 letras se usa como contexto para el profesional, no como etiqueta del estudiante.",
                       "fuentes": [fuente_bloque("personality_test", clave)], "verificado": True})
    return fichas


# ------------------------------------------------------------------ Principios
def fichas_principios():
    return [
        {"id": "PRIN-01", "instrumento": "personalidad", "condicion": {"siempre": True},
         "texto": "El MBTI clasifica preferencias; no mide rasgos, capacidad, habilidad ni caracter. No hay tipos mejores ni peores.",
         "cita_original": "The MBTI assessment sorts for preferences; it does not measure traits, ability, skill, or character. ... There are no better or worse types.",
         "fuentes": [{"tipo": "literatura", "referencia": f"The Myers & Briggs Foundation (2026). Myers-Briggs Overview. {MBF_OVERVIEW}"}],
         "verificado": True},
        {"id": "PRIN-02", "instrumento": "ILS", "condicion": {"siempre": True},
         "texto": "Todos somos a veces de un polo y a veces del otro; la preferencia puede ser fuerte, moderada o leve, y un equilibrio entre ambos polos es deseable.",
         "cita_original": "Everybody is active sometimes and reflective sometimes. Your preference for one category or the other may be strong, moderate, or mild. A balance of the two is desirable.",
         "fuentes": [{"tipo": "literatura", "referencia": FELDER_SOLOMAN}], "verificado": True},
        {"id": "PRIN-03", "instrumento": "CHASIDE", "condicion": {"siempre": True},
         "texto": "Los resultados de CHASIDE son orientativos: en una muestra de 216 universitarios colombianos coincidieron con la carrera cursada en 58,3 % por intereses y 44,4 % por aptitudes.",
         "fuentes": [{"tipo": "literatura", "referencia": "Tamayo Lopera, D. A., Cespedes Correa, A. M., Lopez Restrepo, S., y Valencia Torres, M. Y. (2018). Psicoespacios, 12(21), 76-93. https://doi.org/10.25057/21452776.1099"}],
         "verificado": True},
    ]


def main() -> None:
    cadenas = {r: descargar_cadenas(r) for r in BLOQUES}
    fichas = (fichas_chaside(cadenas["chaside"]) + fichas_ils(cadenas["learning_style"])
              + fichas_personalidad(cadenas["personality_test"]) + fichas_principios())
    ids = [f["id"] for f in fichas]
    assert len(ids) == len(set(ids)), "ids duplicados"
    assert all(f["texto"].strip() for f in fichas), "ficha sin texto"
    salida = {"version": VERSION, "fecha": date.today().isoformat(),
              "bloques": {r: sha for r, sha in BLOQUES.items()}, "total": len(fichas), "fichas": fichas}
    SALIDA.write_text(json.dumps(salida, indent=1, ensure_ascii=False), encoding="utf-8")
    por = Counter((f["instrumento"], "tipo" if "tipo" in f else ("principio" if f["id"].startswith("PRIN") else "base"))
                  for f in fichas)
    print(f"{len(fichas)} fichas en {SALIDA.relative_to(RAIZ)}")
    for k, v in sorted(por.items()):
        print(f"  {k[0]:13} {k[1]:9} {v}")
    print("  sin verificar:", [f["id"] for f in fichas if not f["verificado"]])


if __name__ == "__main__":
    main()
