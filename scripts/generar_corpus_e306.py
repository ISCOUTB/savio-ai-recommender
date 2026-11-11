"""Generador del corpus ground truth de E3-06 (150 perfiles sinteticos).

Modos (desde la raiz del repositorio):

    python scripts/generar_corpus_e306.py matriz
        Escribe corpus_expansion.csv y prompts_maestro.jsonl. No usa red.

    python scripts/generar_corpus_e306.py generar --proveedor claude --modelo <modelo>
        Llama al LLM maestro y escribe corpus.jsonl + manifiesto_generacion.json.

    python scripts/generar_corpus_e306.py repartir
        Reparte los 150 prompts entre persona-1, persona-2 y persona-3 para que
        los diligencien a mano en Claude o ChatGPT (sin API).

    python scripts/generar_corpus_e306.py compilar
        Convierte los Markdown diligenciados de datos/corpus/reparto/ en
        datos/corpus/respuestas.jsonl (id + output).

    python scripts/generar_corpus_e306.py lotes
        Divide los 150 prompts en lotes de 10 (datos/corpus/lotes/) para que un
        LLM maestro los procese por tandas sin truncar la salida.

    python scripts/generar_corpus_e306.py ensamblar --respuestas datos/corpus/respuestas.jsonl
        Une respuestas hechas a mano (id + output) y escribe corpus.jsonl.

    python scripts/generar_corpus_e306.py ensamblar --respuestas-dir datos/corpus/respuestas-lotes \
        --maestro-proveedor openai --maestro-modelo gpt-6.1-sol
        Une lotes generados por un LLM maestro y registra su procedencia.

La matriz de cobertura esta en docs/especificaciones/matriz-corpus-e306.md.
Los rangos y las invariantes vienen de docs/especificaciones/contrato_bruto.py:
no se duplican aqui.

El corpus es 100% sintetico: solo numeros y texto generado. Nunca lee perfiles
reales.
"""

import argparse
import csv
import hashlib
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "docs" / "especificaciones"))
sys.path.insert(0, str(BASE / "poc_slm"))

from contrato_bruto import AREAS_CHASIDE, PARES_ILS, validar_perfil_bruto  # noqa: E402
from guardrail_etico import AVISO_NO_CLINICO, validar_salida_etica  # noqa: E402

SEMILLA = 42
PROMPT_VERSION = "v1.0"

# Reparto sin API: cada integrante pega sus prompts en la version web del LLM
# maestro y devuelve el Markdown con las respuestas entre estas marcas.
PERSONAS = ("persona-1", "persona-2", "persona-3")
MARCA_RESPUESTA = "<!-- RESPUESTA -->"
MARCA_FIN = "<!-- FIN -->"
RE_ENCABEZADO_REPARTO = re.compile(r"^## (SINT-\d{3})\s*$")

INSTRUCTION = (
    "Interpreta los puntajes brutos de CHASIDE, Felder-Silverman y Personalidad "
    "y genera el perfil integrado en cuatro secciones: estilos de aprendizaje, "
    "rasgos de personalidad, perfil vocacional y sintesis integrada."
)

SECCIONES = (
    "## 1. Estilos de aprendizaje",
    "## 2. Rasgos de personalidad",
    "## 3. Perfil vocacional",
    "## 4. Sintesis integrada",
)

EJES_PERSONALIDAD = (
    ("extraversion", "introversion"),
    ("sensing", "intuition"),
    ("thinking", "feeling"),
    ("judging", "perceptive"),
)

# Indice de cada dimension bipolar dentro de PARES_ILS.
DIM_INDEX = {izq + "_" + der: i for i, (izq, der) in enumerate(PARES_ILS)}

# Tensiones del arquetipo GAP-CHA-ILS: (area alta, dimension, hacia el polo izquierdo).
TENSIONES_CHA_ILS = (
    ("A", "secuencial_global", True),   # arte frente a paso a paso
    ("I", "visual_verbal", False),      # trabajo tecnico frente a canal verbal
    ("H", "sensitivo_intuitivo", True),  # contenido abstracto frente a lo concreto
    ("S", "secuencial_global", False),  # precision frente a vision global
    ("C", "activo_reflexivo", True),    # registro frente a accion
    ("E", "activo_reflexivo", False),   # interaccion frente a introspeccion
)

# Tensiones del arquetipo GAP-PER-ILS:
# (eje, polo preferido hacia la izquierda, dimension ILS, hacia el polo izquierdo).
TENSIONES_PER_ILS = (
    (0, True, "activo_reflexivo", False),      # extraversion + reflexivo
    (0, False, "activo_reflexivo", True),      # introversion + activo
    (1, True, "sensitivo_intuitivo", False),   # sensing + intuitivo
    (1, False, "sensitivo_intuitivo", True),   # intuition + sensitivo
)

ARQUETIPOS = (
    ("DOM-CHA", 21),
    ("DOM-ILS", 20),
    ("DOM-PER", 20),
    ("GAP-CHA-ILS", 24),
    ("GAP-PER-ILS", 20),
    ("FLAT", 20),
    ("EDGE", 25),
)


# --------------------------------------------------------------------------
# Muestreo
# --------------------------------------------------------------------------


def estratificado(n, minimo, maximo, rng):
    """Devuelve n enteros en [minimo, maximo] con cobertura estratificada.

    Divide el rango en n estratos, toma un valor por estrato y permuta el orden.
    Es la version 1-D del Latin Hypercube Sampling.
    """
    if n <= 0:
        return []
    ancho = maximo - minimo + 1
    if ancho <= 0:
        raise ValueError(f"rango invalido: {minimo}-{maximo}")
    valores = []
    for i in range(n):
        u = (i + rng.random()) / n
        valores.append(minimo + min(ancho - 1, int(u * ancho)))
    rng.shuffle(valores)
    return valores


def area_chaside(total, rng):
    """Reparte un total 0-14 entre interes (0-10) y aptitud (0-4)."""
    interes = rng.randint(max(0, total - 4), min(10, total))
    return {"interes": interes, "aptitud": total - interes, "total": total}


def chaside_desde_totales(totales, rng):
    return {area: area_chaside(totales[area], rng) for area in AREAS_CHASIDE}


def totales_con_uno(area_especial, total_especial, rango_otros, rng):
    """Un area con total fijo y las otras seis dentro de rango_otros."""
    otros = estratificado(6, rango_otros[0], rango_otros[1], rng)
    totales = {}
    indice = 0
    for area in AREAS_CHASIDE:
        if area == area_especial:
            totales[area] = total_especial
        else:
            totales[area] = otros[indice]
            indice += 1
    return totales


def ils_desde_izquierdos(izquierdos):
    """Construye los 8 polos a partir del polo izquierdo de cada par (suma 11)."""
    ils = {}
    for (izq, der), valor in zip(PARES_ILS, izquierdos):
        ils[izq] = valor
        ils[der] = 11 - valor
    return ils


def izquierdo_para_magnitud(magnitud, hacia_izquierda):
    """Polo izquierdo que produce el diferencial pedido (impar, -11..11)."""
    diferencial = magnitud if hacia_izquierda else -magnitud
    return (11 + diferencial) // 2


def eje_balanceado(rng, tolerancia=3):
    """Dos polos 0-9 con diferencia menor o igual a la tolerancia."""
    izquierdo = rng.randint(0, 9)
    derecho = rng.randint(max(0, izquierdo - tolerancia), min(9, izquierdo + tolerancia))
    return izquierdo, derecho


def eje_con_preferencia(rng, hacia_izquierda, minimo=4):
    """Dos polos 0-9 con diferencia >= minimo hacia el lado pedido."""
    preferido = rng.randint(6, 9)
    otro = rng.randint(0, preferido - minimo)
    return (preferido, otro) if hacia_izquierda else (otro, preferido)


def personalidad_desde_ejes(ejes):
    personalidad = {}
    for (izq, der), (valor_izq, valor_der) in zip(EJES_PERSONALIDAD, ejes):
        personalidad[izq] = valor_izq
        personalidad[der] = valor_der
    return personalidad


def perfil(arquetipo, chaside, ils, personalidad):
    return {
        "arquetipo": arquetipo,
        "chaside": chaside,
        "ils": ils,
        "personalidad": personalidad,
    }


# --------------------------------------------------------------------------
# Arquetipos
# --------------------------------------------------------------------------


def gen_dom_cha(n, rng):
    perfiles = []
    for i in range(n):
        area = AREAS_CHASIDE[i % 7]
        total_dominante = (11, 12, 14)[(i // 7) % 3]
        totales = totales_con_uno(area, total_dominante, (2, 9), rng)
        ils = ils_desde_izquierdos([rng.randint(3, 8) for _ in range(4)])
        ejes = [eje_balanceado(rng) for _ in range(4)]
        perfiles.append(
            perfil("DOM-CHA", chaside_desde_totales(totales, rng), ils, personalidad_desde_ejes(ejes))
        )
    return perfiles


def gen_dom_ils(n, rng):
    variantes = ((11, True), (9, False), (11, False), (9, True), (11, True))
    perfiles = []
    for i in range(n):
        dimension = DIM_INDEX[DIMENSIONES[i % 4]]
        magnitud, hacia_izquierda = variantes[i // 4]
        izquierdos = [rng.randint(2, 9) for _ in range(4)]
        izquierdos[dimension] = izquierdo_para_magnitud(magnitud, hacia_izquierda)
        totales = dict(zip(AREAS_CHASIDE, estratificado(7, 3, 10, rng)))
        ejes = [eje_balanceado(rng) for _ in range(4)]
        perfiles.append(
            perfil("DOM-ILS", chaside_desde_totales(totales, rng), ils_desde_izquierdos(izquierdos), personalidad_desde_ejes(ejes))
        )
    return perfiles


def gen_dom_per(n, rng):
    lados = (True, False, True, False, True)
    perfiles = []
    for i in range(n):
        eje_dominante = i % 4
        hacia_izquierda = lados[i // 4]
        ejes = []
        for indice_eje in range(4):
            if indice_eje == eje_dominante:
                ejes.append(eje_con_preferencia(rng, hacia_izquierda))
            else:
                ejes.append(eje_balanceado(rng))
        totales = dict(zip(AREAS_CHASIDE, estratificado(7, 2, 9, rng)))
        ils = ils_desde_izquierdos([rng.randint(3, 8) for _ in range(4)])
        perfiles.append(
            perfil("DOM-PER", chaside_desde_totales(totales, rng), ils, personalidad_desde_ejes(ejes))
        )
    return perfiles


def gen_gap_cha_ils(n, rng):
    perfiles = []
    for i in range(n):
        area, dimension_nombre, hacia_izquierda = TENSIONES_CHA_ILS[i % 6]
        j = i // 6
        total_dominante = 11 + j
        magnitud = 11 if j % 2 == 0 else 9
        totales = totales_con_uno(area, total_dominante, (2, 9), rng)
        izquierdos = [rng.randint(2, 9) for _ in range(4)]
        izquierdos[DIM_INDEX[dimension_nombre]] = izquierdo_para_magnitud(magnitud, hacia_izquierda)
        ejes = [eje_balanceado(rng) for _ in range(4)]
        perfiles.append(
            perfil("GAP-CHA-ILS", chaside_desde_totales(totales, rng), ils_desde_izquierdos(izquierdos), personalidad_desde_ejes(ejes))
        )
    return perfiles


def gen_gap_per_ils(n, rng):
    perfiles = []
    for i in range(n):
        eje, hacia_personalidad, dimension_nombre, hacia_ils = TENSIONES_PER_ILS[i % 4]
        magnitud = 11 if (i // 4) % 2 == 0 else 9
        ejes = []
        for indice_eje in range(4):
            if indice_eje == eje:
                ejes.append(eje_con_preferencia(rng, hacia_personalidad))
            else:
                ejes.append(eje_balanceado(rng))
        izquierdos = [rng.randint(3, 8) for _ in range(4)]
        izquierdos[DIM_INDEX[dimension_nombre]] = izquierdo_para_magnitud(magnitud, hacia_ils)
        totales = dict(zip(AREAS_CHASIDE, estratificado(7, 3, 9, rng)))
        perfiles.append(
            perfil("GAP-PER-ILS", chaside_desde_totales(totales, rng), ils_desde_izquierdos(izquierdos), personalidad_desde_ejes(ejes))
        )
    return perfiles


def gen_flat(n, rng):
    perfiles = []
    for _ in range(n):
        totales = dict(zip(AREAS_CHASIDE, estratificado(7, 6, 10, rng)))
        ils = ils_desde_izquierdos([rng.randint(3, 8) for _ in range(4)])
        ejes = [eje_balanceado(rng, tolerancia=2) for _ in range(4)]
        perfiles.append(
            perfil("FLAT", chaside_desde_totales(totales, rng), ils, personalidad_desde_ejes(ejes))
        )
    return perfiles


def gen_edge(n, rng):
    perfiles = []
    for i in range(n):
        familia = i % 5
        j = i // 5
        inferior = j < 3
        area = AREAS_CHASIDE[j % 7]
        dimension_nombre = DIMENSIONES[j % 4]
        eje = j % 4

        if familia == 0:  # limite CHASIDE baja/media: 5 o 6
            totales = totales_con_uno(area, 5 if inferior else 6, (6, 10), rng)
            izquierdos = [rng.randint(3, 8) for _ in range(4)]
            ejes = [eje_balanceado(rng) for _ in range(4)]
        elif familia == 1:  # limite CHASIDE media/alta: 10 u 11
            totales = totales_con_uno(area, 10 if inferior else 11, (4, 9), rng)
            izquierdos = [rng.randint(3, 8) for _ in range(4)]
            ejes = [eje_balanceado(rng) for _ in range(4)]
        elif familia == 2:  # limite ILS 7/9
            totales = dict(zip(AREAS_CHASIDE, estratificado(7, 4, 9, rng)))
            izquierdos = [rng.randint(3, 8) for _ in range(4)]
            izquierdos[DIM_INDEX[dimension_nombre]] = izquierdo_para_magnitud(
                7 if inferior else 9, hacia_izquierda=(j % 2 == 0)
            )
            ejes = [eje_balanceado(rng) for _ in range(4)]
        elif familia == 3:  # reparto extremo 10/1 u 11/0
            totales = dict(zip(AREAS_CHASIDE, estratificado(7, 4, 9, rng)))
            izquierdos = [rng.randint(4, 7) for _ in range(4)]
            izquierdos[DIM_INDEX[dimension_nombre]] = 10 if inferior else 11
            ejes = [eje_balanceado(rng) for _ in range(4)]
        else:  # diferencia de personalidad 3 o 4
            totales = dict(zip(AREAS_CHASIDE, estratificado(7, 4, 9, rng)))
            izquierdos = [rng.randint(3, 8) for _ in range(4)]
            ejes = [eje_balanceado(rng, tolerancia=2) for _ in range(4)]
            diferencia = 3 if inferior else 4
            preferido = rng.randint(diferencia, 9)
            ejes[eje] = (preferido, preferido - diferencia) if j % 2 == 0 else (preferido - diferencia, preferido)

        perfiles.append(
            perfil("EDGE", chaside_desde_totales(totales, rng), ils_desde_izquierdos(izquierdos), personalidad_desde_ejes(ejes))
        )
    return perfiles


GENERADORES = {
    "DOM-CHA": gen_dom_cha,
    "DOM-ILS": gen_dom_ils,
    "DOM-PER": gen_dom_per,
    "GAP-CHA-ILS": gen_gap_cha_ils,
    "GAP-PER-ILS": gen_gap_per_ils,
    "FLAT": gen_flat,
    "EDGE": gen_edge,
}

DIMENSIONES = tuple(DIM_INDEX)


# --------------------------------------------------------------------------
# Perfiles y validacion
# --------------------------------------------------------------------------


def generar_perfiles(semilla=SEMILLA, limite=None):
    """Genera, valida y numera los perfiles de la matriz."""
    perfiles = []
    for codigo, cantidad in ARQUETIPOS:
        rng = random.Random(f"{semilla}:{codigo}")
        perfiles.extend(GENERADORES[codigo](cantidad, rng))

    if limite is not None:
        perfiles = perfiles[:limite]

    for indice, item in enumerate(perfiles, start=1):
        item["id"] = f"SINT-{indice:03d}"
        item["origen"] = "sintetico"
        limpio = {clave: valor for clave, valor in item.items() if clave != "arquetipo"}
        errores = validar_perfil_bruto(limpio, item["id"])
        if errores:
            detalle = "; ".join(errores[:5])
            raise SystemExit(f"[FALLO] {item['id']} no cumple el contrato bruto: {detalle}")

    return perfiles


def es_eval(identificador):
    return int(hashlib.sha256(identificador.encode()).hexdigest(), 16) % 5 == 0


def perfil_limpio(item):
    return {clave: valor for clave, valor in item.items() if clave != "arquetipo"}


def construir_registro(item, salida):
    limpio = perfil_limpio(item)
    return {
        "id": limpio["id"],
        "origen": limpio["origen"],
        "chaside": limpio["chaside"],
        "ils": limpio["ils"],
        "personalidad": limpio["personalidad"],
        "instruction": INSTRUCTION,
        "output": salida.strip(),
    }


def problemas_output(texto):
    """Devuelve los problemas de estructura y guardrail de una respuesta."""
    if not isinstance(texto, str) or not texto.strip():
        return ["output vacio"]

    problemas = []
    posiciones = []
    for seccion in SECCIONES:
        posicion = texto.find(seccion)
        if posicion < 0:
            problemas.append(f"falta la seccion: {seccion}")
        else:
            posiciones.append(posicion)
    if len(posiciones) == len(SECCIONES) and posiciones != sorted(posiciones):
        problemas.append("las secciones no estan en orden")
    problemas.extend(validar_salida_etica(texto))
    return problemas


# --------------------------------------------------------------------------
# Prompt maestro
# --------------------------------------------------------------------------


def prompt_maestro(item):
    chaside = "\n".join(
        f"{area}: interes={valor['interes']}, aptitud={valor['aptitud']}, total={valor['total']}"
        for area, valor in item["chaside"].items()
    )
    ils = "\n".join(
        f"{izq}={item['ils'][izq]} / {der}={item['ils'][der]} "
        f"(diferencial {item['ils'][izq] - item['ils'][der]})"
        for izq, der in PARES_ILS
    )
    personalidad = "\n".join(
        f"{izq}={item['personalidad'][izq]} / {der}={item['personalidad'][der]} "
        f"(diferencia {abs(item['personalidad'][izq] - item['personalidad'][der])})"
        for izq, der in EJES_PERSONALIDAD
    )

    return f"""Actua como psicopedagogo experto en orientacion vocacional y estilos de aprendizaje.

Recibes los puntajes brutos de tres instrumentos institucionales. Redacta una
interpretacion integrada, en espanol y sin tildes ni caracteres especiales, con
exactamente estas cuatro secciones Markdown y en este orden:

## 1. Estilos de aprendizaje
## 2. Rasgos de personalidad
## 3. Perfil vocacional
## 4. Sintesis integrada

PUNTAJES BRUTOS

CHASIDE (interes 0-10, aptitud 0-4, total 0-14 = interes + aptitud):
{chaside}

Felder-Silverman (cada par suma 11; diferencial = polo izquierdo - polo derecho):
{ils}

Personalidad (8 polos de 0 a 9):
{personalidad}

REGLAS OBLIGATORIAS
1. Cita los puntajes exactos recibidos; no inventes escalas ni recalcules nada.
2. Aplica estas bandas: CHASIDE alta 11-14, media 6-10, baja 0-5; Felder con
   preferencia marcada si el valor absoluto del diferencial es 9 u 11, sin
   preferencia clara si es 1, 3, 5 o 7; personalidad con preferencia si la
   diferencia entre polos es 4 o mas, equilibrada si es 3 o menos.
3. No uses etiquetas de tipo de cuatro letras.
4. No emitas diagnosticos ni menciones trastornos, medicacion o tratamiento.
5. No recomiendes carreras concretas; describe areas y entornos.
6. Redacta de forma descriptiva y graduada; no afirmes "eres visual".
7. Cierra el texto con esta frase exacta, en su propia linea:
{AVISO_NO_CLINICO}
"""


# --------------------------------------------------------------------------
# Reparto sin API (los 3 integrantes pegan los prompts en Claude/ChatGPT web)
# --------------------------------------------------------------------------


def repartir_perfiles(perfiles, personas=PERSONAS):
    """Reparte por turnos para que cada arquetipo quede balanceado."""
    asignados = {persona: [] for persona in personas}
    for indice, item in enumerate(perfiles):
        asignados[personas[indice % len(personas)]].append(item)
    return asignados


def bloque_reparto(item):
    return (
        f"## {item['id']}\n\n"
        f"**Arquetipo:** {item['arquetipo']}\n\n"
        "**Prompt (copiar):**\n\n"
        "```text\n"
        f"{prompt_maestro(item)}"
        "```\n\n"
        "**Respuesta (pegar aqui):**\n\n"
        f"{MARCA_RESPUESTA}\n\n"
        f"{MARCA_FIN}\n"
    )


def texto_reparto(persona, items):
    ids = ", ".join(item["id"] for item in items)
    cabecera = (
        f"# Ground truth E3-06 - {persona}\n\n"
        f"Registros asignados: {len(items)}\n\n"
        "Instrucciones:\n\n"
        "1. Copia cada bloque `Prompt` en Claude o ChatGPT (version web).\n"
        "2. Pega la respuesta completa entre `<!-- RESPUESTA -->` y `<!-- FIN -->`.\n"
        "3. No edites los puntajes ni agregues nombres, correos o codigos.\n"
        "4. Cuando termines, desde la raiz del repositorio:\n\n"
        "```bash\n"
        "python scripts/generar_corpus_e306.py compilar\n"
        "python scripts/generar_corpus_e306.py ensamblar --respuestas datos/corpus/respuestas.jsonl\n"
        "```\n\n"
        f"Ids asignados: {ids}\n"
    )
    return cabecera + "\n---\n\n" + "\n---\n\n".join(bloque_reparto(item) for item in items)


def leer_reparto(ruta):
    """Extrae {id: output} de un Markdown diligenciado.

    Solo lee lo que esta entre MARCA_RESPUESTA y MARCA_FIN. Un bloque vacio no
    cuenta: el id queda pendiente y `compilar` lo reporta.
    """
    if not ruta.exists():
        return {}

    respuestas = {}
    identificador = None
    dentro = False
    lineas = []
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
        encabezado = RE_ENCABEZADO_REPARTO.match(linea)
        if encabezado:
            identificador = encabezado.group(1)
            dentro = False
            lineas = []
            continue
        if linea.strip() == MARCA_RESPUESTA:
            dentro = True
            lineas = []
            continue
        if linea.strip() == MARCA_FIN:
            if dentro and identificador:
                texto = "\n".join(lineas).strip()
                if texto:
                    respuestas[identificador] = texto
            dentro = False
            lineas = []
            continue
        if dentro:
            lineas.append(linea)
    return respuestas


# --------------------------------------------------------------------------
# Escritura de artefactos
# --------------------------------------------------------------------------


def escribir_texto(ruta, contenido):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_name(ruta.name + ".tmp")
    temporal.write_text(contenido, encoding="utf-8")
    os.replace(temporal, ruta)


def escribir_json(ruta, datos):
    escribir_texto(ruta, json.dumps(datos, indent=2, ensure_ascii=True) + "\n")


def escribir_jsonl(ruta, filas):
    lineas = "".join(json.dumps(fila, ensure_ascii=True) + "\n" for fila in filas)
    escribir_texto(ruta, lineas)


def columnas_expansion():
    columnas = ["id", "arquetipo"]
    columnas += [f"chaside_{area}_{campo}" for area in AREAS_CHASIDE for campo in ("interes", "aptitud", "total")]
    for izq, der in PARES_ILS:
        columnas += [f"ils_{izq}", f"ils_{der}"]
    for izq, der in EJES_PERSONALIDAD:
        columnas += [f"per_{izq}", f"per_{der}"]
    return columnas


def fila_expansion(item):
    fila = {"id": item["id"], "arquetipo": item["arquetipo"]}
    for area, valor in item["chaside"].items():
        for campo in ("interes", "aptitud", "total"):
            fila[f"chaside_{area}_{campo}"] = valor[campo]
    for izq, der in PARES_ILS:
        fila[f"ils_{izq}"] = item["ils"][izq]
        fila[f"ils_{der}"] = item["ils"][der]
    for izq, der in EJES_PERSONALIDAD:
        fila[f"per_{izq}"] = item["personalidad"][izq]
        fila[f"per_{der}"] = item["personalidad"][der]
    return fila


def escribir_expansion(ruta, perfiles):
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas_expansion())
        escritor.writeheader()
        for item in perfiles:
            escritor.writerow(fila_expansion(item))


def hash_archivo(ruta):
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def resumen_cobertura(perfiles):
    totales = {}
    evaluacion = {}
    for item in perfiles:
        codigo = item["arquetipo"]
        totales[codigo] = totales.get(codigo, 0) + 1
        if es_eval(item["id"]):
            evaluacion[codigo] = evaluacion.get(codigo, 0) + 1
    return totales, evaluacion


def escribir_manifiesto_generacion(ruta, perfiles, corpus, proveedor, modelo, fallidos):
    totales, evaluacion = resumen_cobertura(perfiles)
    datos = {
        "generador": "scripts/generar_corpus_e306.py",
        "version_corpus": "1.0",
        "prompt_version": PROMPT_VERSION,
        "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "semilla": SEMILLA,
        "proveedor": proveedor or "manual",
        "modelo": modelo or "no aplica",
        "total_registros": len(perfiles),
        "arquetipos": totales,
        "split": {
            "entrenamiento": len(perfiles) - sum(evaluacion.values()),
            "evaluacion": sum(evaluacion.values()),
            "evaluacion_por_arquetipo": evaluacion,
        },
        "sha256_corpus": hash_archivo(corpus) if corpus.exists() else None,
        "fallidos": len(fallidos),
        "firmas_calidad": {},
    }
    escribir_json(ruta, datos)


def escribir_fallidos(ruta, fallidos):
    if fallidos:
        escribir_jsonl(ruta, fallidos)
    elif ruta.exists():
        ruta.unlink()


# --------------------------------------------------------------------------
# Proveedores
# --------------------------------------------------------------------------


def llamar_claude(prompt, modelo):
    try:
        import anthropic
    except ImportError as exc:
        raise SystemExit("Falta el paquete anthropic: pip install anthropic") from exc

    cliente = anthropic.Anthropic()
    respuesta = cliente.messages.create(
        model=modelo,
        max_tokens=900,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(
        bloque.text for bloque in respuesta.content if getattr(bloque, "type", "") == "text"
    )


def llamar_openai(prompt, modelo):
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("Falta el paquete openai: pip install openai") from exc

    cliente = OpenAI()
    respuesta = cliente.chat.completions.create(
        model=modelo,
        temperature=0.2,
        max_tokens=900,
        messages=[{"role": "user", "content": prompt}],
    )
    return respuesta.choices[0].message.content or ""


PROVEEDORES = {"claude": llamar_claude, "openai": llamar_openai}


# --------------------------------------------------------------------------
# Modos
# --------------------------------------------------------------------------


def modo_matriz(args):
    perfiles = generar_perfiles(args.semilla, args.limite)
    salida = args.salida_dir
    salida.mkdir(parents=True, exist_ok=True)

    ruta_expansion = salida / "corpus_expansion.csv"
    ruta_prompts = salida / "prompts_maestro.jsonl"
    escribir_expansion(ruta_expansion, perfiles)
    escribir_jsonl(
        ruta_prompts,
        [
            {"id": item["id"], "arquetipo": item["arquetipo"], "prompt_version": PROMPT_VERSION, "prompt": prompt_maestro(item)}
            for item in perfiles
        ],
    )

    totales, evaluacion = resumen_cobertura(perfiles)
    print(f"Perfiles generados y validados contra contrato_bruto: {len(perfiles)}")
    for codigo, _ in ARQUETIPOS:
        impresos = totales.get(codigo, 0)
        if impresos:
            print(f"  {codigo:<12} {impresos:>3} registros | {evaluacion.get(codigo, 0):>2} en evaluacion")
    print(f"  {'TOTAL':<12} {len(perfiles):>3} registros | {sum(evaluacion.values()):>2} en evaluacion")

    sin_eval = [codigo for codigo in totales if evaluacion.get(codigo, 0) == 0]
    if sin_eval:
        print(f"[AVISO] arquetipos sin registros de evaluacion: {', '.join(sin_eval)}")
    print(f"[OK] {ruta_expansion}")
    print(f"[OK] {ruta_prompts}")
    return 0


def modo_repartir(args):
    perfiles = generar_perfiles(args.semilla, args.limite)
    asignados = repartir_perfiles(perfiles)
    carpeta = args.salida_dir / "reparto"
    carpeta.mkdir(parents=True, exist_ok=True)

    for persona, items in asignados.items():
        ruta = carpeta / f"{persona}.md"
        if ruta.exists() and not args.sobrescribir:
            print(f"[AVISO] {ruta} ya existe; no se sobrescribe (usa --sobrescribir)")
            continue
        escribir_texto(ruta, texto_reparto(persona, items))
        print(f"[OK] {ruta}: {len(items)} registros")

    print(f"Total repartido: {len(perfiles)} registros entre {len(asignados)} personas")
    return 0


def modo_compilar(args):
    entrada = args.entrada_dir or (args.salida_dir / "reparto")
    esperados = {item["id"]: item for item in generar_perfiles(args.semilla, args.limite)}
    respuestas = {}
    duplicados = []

    for persona in PERSONAS:
        ruta = entrada / f"{persona}.md"
        if not ruta.exists():
            print(f"[AVISO] no existe {ruta}")
            continue
        propias = leer_reparto(ruta)
        duplicados.extend(sorted(set(propias) & set(respuestas)))
        for identificador, texto in propias.items():
            if identificador not in respuestas:
                respuestas[identificador] = texto
        print(f"[OK] {persona}: {len(propias)} respuestas")

    if duplicados:
        raise SystemExit(
            "[FALLO] ids duplicados entre archivos: " + ", ".join(sorted(set(duplicados)))
        )

    desconocidos = sorted(set(respuestas) - set(esperados))
    if desconocidos:
        raise SystemExit(
            "[FALLO] ids que no pertenecen a la matriz: " + ", ".join(desconocidos)
        )

    ruta_salida = args.salida_respuestas or (args.salida_dir / "respuestas.jsonl")
    escribir_jsonl(
        ruta_salida,
        [{"id": identificador, "output": respuestas[identificador]} for identificador in sorted(respuestas)],
    )
    print(f"[OK] {ruta_salida}: {len(respuestas)} respuestas")

    problemas = []
    for identificador in sorted(respuestas):
        hallazgos = problemas_output(respuestas[identificador])
        if hallazgos:
            problemas.append((identificador, hallazgos))
    if problemas:
        print(f"[FALLO] {len(problemas)} respuestas no cumplen estructura o guardrail:")
        for identificador, hallazgos in problemas[:10]:
            print(f"  - {identificador}: {'; '.join(hallazgos)}")

    faltan = sorted(set(esperados) - set(respuestas))
    if faltan:
        muestra = ", ".join(faltan[:10]) + (" ..." if len(faltan) > 10 else "")
        print(f"[PENDIENTE] {len(faltan)} sin respuesta: {muestra}")

    if problemas or faltan:
        return 1

    print(f"RESULTADO: OK ({len(esperados)} respuestas listas para ensamblar)")
    return 0


def modo_lotes(args):
    if args.tamano_lote < 1:
        raise SystemExit("--tamano-lote debe ser 1 o mas")

    perfiles = generar_perfiles(args.semilla, args.limite)
    carpeta = args.salida_dir / "lotes"
    carpeta.mkdir(parents=True, exist_ok=True)

    total = 0
    for numero, inicio in enumerate(range(0, len(perfiles), args.tamano_lote), start=1):
        lote = perfiles[inicio : inicio + args.tamano_lote]
        ruta = carpeta / f"prompts-lote-{numero:02d}.jsonl"
        escribir_jsonl(
            ruta,
            [
                {
                    "id": item["id"],
                    "arquetipo": item["arquetipo"],
                    "prompt": prompt_maestro(item),
                }
                for item in lote
            ],
        )
        print(f"[OK] {ruta}: {len(lote)} prompts ({lote[0]['id']} a {lote[-1]['id']})")
        total += len(lote)

    print(f"Total en lotes: {total} prompts")
    return 0


def escribir_corpus(perfiles, respuestas, args, proveedor, modelo):
    salida = args.salida_dir
    salida.mkdir(parents=True, exist_ok=True)
    registros = []
    fallidos = []

    for item in perfiles:
        texto = respuestas.get(item["id"])
        problemas = problemas_output(texto) if texto is not None else ["sin respuesta"]
        if problemas:
            fallidos.append({"id": item["id"], "arquetipo": item["arquetipo"], "problemas": problemas})
            continue
        registros.append(construir_registro(item, texto))

    ruta_corpus = salida / "corpus.jsonl"
    escribir_jsonl(ruta_corpus, registros)
    escribir_fallidos(salida / "fallidos.jsonl", fallidos)
    escribir_manifiesto_generacion(
        salida / "manifiesto_generacion.json", perfiles, ruta_corpus, proveedor, modelo, fallidos
    )

    print(f"[OK] {ruta_corpus}: {len(registros)} registros")
    if fallidos:
        print(f"[FALLO] {len(fallidos)} registros sin respuesta valida (ver fallidos.jsonl)")
        for fallido in fallidos[:5]:
            print(f"  - {fallido['id']}: {'; '.join(fallido['problemas'])}")
        if len(fallidos) > 5:
            print(f"  - ... {len(fallidos) - 5} mas")

    if fallidos and not args.permitir_fallidos:
        return 1
    return 0


def modo_generar(args):
    if not args.proveedor or not args.modelo:
        raise SystemExit("generar exige --proveedor claude|openai y --modelo <identificador>")

    perfiles = generar_perfiles(args.semilla, args.limite)
    funcion = PROVEEDORES[args.proveedor]
    respuestas = {}

    for indice, item in enumerate(perfiles, start=1):
        prompt = prompt_maestro(item)
        for intento in range(1, args.reintentos + 1):
            try:
                texto = funcion(prompt, args.modelo)
            except Exception as exc:  # noqa: BLE001 - se reporta y se reintenta
                texto = ""
                error = f"error del proveedor: {exc}"
            problemas = problemas_output(texto)
            if not problemas:
                respuestas[item["id"]] = texto
                break
            error = "; ".join(problemas)
        if indice % 10 == 0 or indice == len(perfiles):
            print(f"  [{indice}/{len(perfiles)}] {item['id']} {'OK' if item['id'] in respuestas else 'FALLO: ' + error}")

    return escribir_corpus(perfiles, respuestas, args, args.proveedor, args.modelo)


def modo_ensamblar(args):
    rutas = list(args.respuestas or [])
    if args.respuestas_dir:
        if not args.respuestas_dir.is_dir():
            raise SystemExit(f"No existe la carpeta de respuestas: {args.respuestas_dir}")
        rutas.extend(sorted(args.respuestas_dir.glob("*.jsonl")))
    if not rutas:
        rutas = [args.salida_dir / "respuestas.jsonl"]

    respuestas = {}
    for ruta in rutas:
        if not ruta.exists():
            raise SystemExit(f"No existe el archivo de respuestas: {ruta}")

        with ruta.open("r", encoding="utf-8-sig") as archivo:
            for numero, linea in enumerate(archivo, start=1):
                texto = linea.strip()
                if not texto:
                    continue
                try:
                    objeto = json.loads(texto)
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"{ruta.name}:{numero}: JSON invalido ({exc.msg})") from None
                identificador = objeto.get("id")
                salida = objeto.get("output")
                if not isinstance(identificador, str) or not isinstance(salida, str):
                    raise SystemExit(f"{ruta.name}:{numero}: se esperaba id y output de texto")
                if identificador in respuestas:
                    raise SystemExit(f"{ruta.name}:{numero}: id duplicado: {identificador}")
                respuestas[identificador] = salida

    perfiles = generar_perfiles(args.semilla, args.limite)
    return escribir_corpus(
        perfiles,
        respuestas,
        args,
        args.maestro_proveedor,
        args.maestro_modelo,
    )


def construir_parser():
    parser = argparse.ArgumentParser(
        description="Genera el corpus sintetico de E3-06 a partir de la matriz de cobertura."
    )
    parser.add_argument(
        "modo", choices=("matriz", "generar", "repartir", "lotes", "compilar", "ensamblar")
    )
    parser.add_argument(
        "--salida-dir",
        type=Path,
        default=BASE / "datos" / "corpus",
        help="carpeta de salida (por defecto datos/corpus)",
    )
    parser.add_argument("--semilla", type=int, default=SEMILLA)
    parser.add_argument("--limite", type=int, help="genera solo los primeros N perfiles (pruebas)")
    parser.add_argument("--proveedor", choices=tuple(PROVEEDORES))
    parser.add_argument("--modelo", help="identificador del LLM maestro")
    parser.add_argument("--reintentos", type=int, default=2)
    parser.add_argument(
        "--respuestas",
        type=Path,
        nargs="+",
        help="uno o varios JSONL con id y output para el modo ensamblar",
    )
    parser.add_argument(
        "--respuestas-dir",
        type=Path,
        help="carpeta con lotes *.jsonl de id y output para el modo ensamblar",
    )
    parser.add_argument(
        "--maestro-proveedor",
        default="manual",
        help="procedencia registrada en manifiesto_generacion.json (default: manual)",
    )
    parser.add_argument(
        "--maestro-modelo",
        default="ensamblado",
        help="modelo maestro registrado en manifiesto_generacion.json (default: ensamblado)",
    )
    parser.add_argument(
        "--entrada-dir",
        type=Path,
        help="carpeta con los Markdown diligenciados (por defecto datos/corpus/reparto)",
    )
    parser.add_argument(
        "--tamano-lote",
        type=int,
        default=10,
        help="prompts por lote en el modo lotes (default: 10)",
    )
    parser.add_argument(
        "--salida-respuestas",
        type=Path,
        help="JSONL que escribe compilar (por defecto datos/corpus/respuestas.jsonl)",
    )
    parser.add_argument(
        "--sobrescribir",
        action="store_true",
        help="sobrescribe los repartos existentes (borra las respuestas ya pegadas)",
    )
    parser.add_argument(
        "--permitir-fallidos",
        action="store_true",
        help="escribe el corpus aunque falten respuestas (codigo de salida 0)",
    )
    return parser


def main(argv=None):
    args = construir_parser().parse_args(argv)
    if args.modo == "matriz":
        return modo_matriz(args)
    if args.modo == "generar":
        return modo_generar(args)
    if args.modo == "repartir":
        return modo_repartir(args)
    if args.modo == "lotes":
        return modo_lotes(args)
    if args.modo == "compilar":
        return modo_compilar(args)
    return modo_ensamblar(args)


if __name__ == "__main__":
    sys.exit(main())
