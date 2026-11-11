"""Evaluacion SMART de fidelidad y rendimiento en CPU del SLM (E3-09).

Mide las salidas de un modelo frente al ground truth de E3-06 (split de
evaluacion de 28 registros) en cinco dimensiones:

  1. exactitud numerica: cada puntaje citado coincide con la entrada
     (0 alucinaciones) y cobertura de los 37 puntajes;
  2. coherencia del cruce: lectura de los tres instrumentos segun las bandas de
     baremos-psicometricos.md (sin polos invertidos ni preferencias exageradas,
     area CHASIDE de mayor total nombrada y sintesis que cruza los tres tests);
  3. estructura de 4 bloques en orden (mismo validador del backend E3-07);
  4. guardrails eticos: aviso no clinico, sin tipo MBTI, sin frases clinicas ni
     escalas o decimales no nativos;
  5. fidelidad global = promedio de las cuatro anteriores; meta >= 85 %.

Ademas mide, en CPU (num_gpu=0), la latencia por perfil, los tokens/s y el pico
de RAM de Ollama, y confirma 0 MB de VRAM.

Uso (desde la raiz del repositorio):
    # Referencia Teacher: el propio ground truth (calibra la metrica)
    python docs/especificaciones/evaluar-fidelidad.py referencia

    # Generar en CPU con un modelo y evaluarlo; escribe salidas.jsonl y reporte.json
    # en benchmarks/resultados/<equipo>/e3-09/<modelo>/ (equipo deducido de la CPU)
    python docs/especificaciones/evaluar-fidelidad.py generar --modelo qwen2.5:1.5b
    python docs/especificaciones/evaluar-fidelidad.py generar --gguf modelos/perfil-ia-e3-q4_k_m.gguf

    # Perfiles reales de E3-05 (salida local en salidas/reales/, ignorada por Git)
    python docs/especificaciones/evaluar-fidelidad.py generar --gguf <gguf> --perfiles perfiles/reales/persona-1-bruto.json

    # Reevaluar salidas ya generadas, sin modelo
    python docs/especificaciones/evaluar-fidelidad.py evaluar --salidas salidas/e3/eval/qwen2.5_1.5b/salidas.jsonl

Es una metrica automatica y reproducible, no un dictamen psicometrico: la
revision por un profesional sigue fuera del alcance de la Entrega 3.
"""

import argparse
import hashlib
import json
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "docs" / "especificaciones"))
sys.path.insert(0, str(RAIZ / "poc_slm"))

from contrato_bruto import AREAS_CHASIDE, PARES_ILS  # noqa: E402
from guardrail_etico import validar_salida_etica  # noqa: E402
from interpretador import (  # noqa: E402
    EJES_PERSONALIDAD,
    SECCIONES,
    cargar_perfil,
    construir_mensajes,
    normalizar_secciones,
    problemas_fidelidad,
    validar_estructura,
)

RUTA_CORPUS = RAIZ / "datos" / "corpus" / "corpus.jsonl"
DIR_EVAL = RAIZ / "salidas" / "e3" / "eval"          # referencia Teacher (no depende del equipo)
DIR_RESULTADOS = RAIZ / "benchmarks" / "resultados"  # <equipo>/e3-09/<modelo>/ (evidencia medida)
DIR_REALES = RAIZ / "salidas" / "reales" / "e3-09"   # perfiles reales: ignorado por Git
OLLAMA_URL = "http://localhost:11434/api/generate"

META_FIDELIDAD = 0.85
META_LATENCIA_S = 60.0
UMBRAL_ILS_MARCADA = 9      # baremos 2.2: diferencial 9 u 11
UMBRAL_PERSONALIDAD = 4     # baremos 3.2: diferencia 4 o mas
UMBRAL_AFINIDAD_ALTA = 11   # baremos 4.2: total 11 a 14

# Raices para reconocer cada polo en la prosa (masculino, femenino o ingles).
RAICES_ILS = {
    "activo": r"activ",
    "reflexivo": r"reflexiv",
    "sensitivo": r"(?:sensitiv|sensorial)",
    "intuitivo": r"intuitiv",
    "visual": r"visual",
    "verbal": r"verbal",
    "secuencial": r"secuencial",
    "global": r"global",
}
RAICES_PERSONALIDAD = {
    "extraversion": r"extr[ao]ver",
    "introversion": r"introver",
    "sensing": r"(?:sensing|sensaci)",
    "intuition": r"(?:intuition|intuici)",
    "thinking": r"(?:thinking|pensamiento)",
    "feeling": r"(?:feeling|sentimiento)",
    "judging": r"(?:judging|juicio)",
    # "Percepcion" es el nombre del eje sensing/intuition, no el polo perceptive.
    "perceptive": r"(?:perceptiv|perceiving)",
}
NOMBRES_AREA = {
    "C": r"administrativ|contable",
    "H": r"humanidades|humanistic|juridic",
    "A": r"artistic",
    "S": r"salud",
    "I": r"ingenier|computaci",
    "D": r"defensa|seguridad",
    "E": r"exactas|agrari",
}
VERBOS_AFIRMACION = r"(?:inclin|tiende|tendencia|prefier|preferencia|predomin|se orienta|favorece|marcad)"
PALABRAS_MARCADA = r"(?:marcad|clara|fuerte)"
NEGACION = re.compile(r"\b(?:no|sin|ningun\w*|ni|tampoco|nunca)\b", re.IGNORECASE)
MARCAS_ILS = r"(?:aprendizaje|felder|\bils\b)"
MARCAS_PERSONALIDAD = r"(?:personalidad|extr[ao]ver|introver|decisi|planificaci|sociab|conductual|\beje)"
MARCAS_VOCACIONAL = (r"(?:vocacional|chaside|afinidad|\barea|aptitud|\binteres|"
                     + "|".join(NOMBRES_AREA.values()) + ")")
MINIMO_INSTRUMENTOS_SINTESIS = 2  # el Teacher cruza a veces de forma implicita


# --------------------------------------------------------------------------
# Corpus y split
# --------------------------------------------------------------------------


def es_evaluacion(registro):
    """Mismo split determinista del notebook de E3-08 (celda 7)."""
    return int(hashlib.sha256(registro["id"].encode()).hexdigest(), 16) % 5 == 0


def cargar_corpus(ruta=RUTA_CORPUS):
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def split_evaluacion(ruta=RUTA_CORPUS):
    return [r for r in cargar_corpus(ruta) if es_evaluacion(r)]


def sha256_archivo(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# Utilidades de texto
# --------------------------------------------------------------------------


def secciones(texto):
    """Devuelve {n: cuerpo} de las secciones 1-4 presentes (texto ya normalizado)."""
    posiciones = sorted((texto.find(s), i + 1) for i, s in enumerate(SECCIONES) if s in texto)
    cuerpos = {}
    for k, (inicio, numero) in enumerate(posiciones):
        fin = posiciones[k + 1][0] if k + 1 < len(posiciones) else len(texto)
        cuerpos[numero] = texto[inicio + len(SECCIONES[numero - 1]):fin]
    return cuerpos


def prosa(cuerpo):
    """Quita las lineas de conteos (las que llevan '=' o empiezan con viñeta de area)."""
    return "\n".join(
        l for l in cuerpo.splitlines()
        if "=" not in l and not re.match(r"^\s*[-*]\s*\**[CHASIDE]\**\s*[:(]", l)
    )


def oraciones(texto):
    return [o for o in re.split(r"(?<=[.;!?])\s+|\n+", texto) if o.strip()]


def contiene(raiz, texto):
    return re.search(r"\b" + raiz, texto, re.IGNORECASE) is not None


# --------------------------------------------------------------------------
# Dimension 1: exactitud numerica
# --------------------------------------------------------------------------


def valores_esperados(perfil):
    esperados = {}
    for area in AREAS_CHASIDE:
        for campo in ("interes", "aptitud", "total"):
            esperados[f"chaside.{area}.{campo}"] = perfil["chaside"][area][campo]
    for polo in RAICES_ILS:
        esperados[f"ils.{polo}"] = perfil["ils"][polo]
    for polo in RAICES_PERSONALIDAD:
        esperados[f"personalidad.{polo}"] = perfil["personalidad"][polo]
    return esperados


def citas_polos(texto, raices, bloque):
    citas = []
    for polo, raiz in raices.items():
        patron = re.compile(
            r"\b" + raiz + r"\w*\**\s*(?:=|:|\(|\bde\b|\bcon\b)?\s*(\d+)\b", re.IGNORECASE
        )
        citas += [(f"{bloque}.{polo}", int(m.group(1))) for m in patron.finditer(texto)]
    return citas


def citas_chaside(texto):
    citas = []
    for linea in texto.splitlines():
        area = None
        m = re.match(r"^\s*(?:[-*]\s*)?\**([CHASIDE])\**\s*[:(,\-]", linea)
        if m:
            area = m.group(1)
        else:
            for letra, nombres in NOMBRES_AREA.items():
                if re.search(nombres, linea, re.IGNORECASE) and re.search(r"interes|aptitud|total", linea, re.IGNORECASE):
                    area = letra
                    break
        if not area:
            continue
        for campo in ("interes", "aptitud", "total"):
            for m in re.finditer(campo + r"\w*\s*(?:=|:|\bde\b)?\s*(\d+)\b", linea, re.IGNORECASE):
                citas.append((f"chaside.{area}.{campo}", int(m.group(1))))
    return citas


def evaluar_exactitud(texto, perfil):
    esperados = valores_esperados(perfil)
    partes = secciones(texto)
    texto_ils = partes.get(1, "") + partes.get(4, "")
    texto_pers = partes.get(2, "") + partes.get(4, "")
    citas = (
        citas_polos(texto_ils, RAICES_ILS, "ils")
        + citas_polos(texto_pers, RAICES_PERSONALIDAD, "personalidad")
        + citas_chaside(partes.get(3, "") + partes.get(4, ""))
    )
    correctos = {clave for clave, valor in citas if esperados.get(clave) == valor}
    errores = sorted({f"{clave}={valor} (entrada {esperados[clave]})"
                      for clave, valor in citas if esperados.get(clave) != valor})
    _, fuera_rango = problemas_fidelidad(texto, perfil)
    errores += [f"numero fuera del rango nativo: {n}" for n in fuera_rango]
    cobertura = len(correctos) / len(esperados)
    return {
        "puntaje": 0.0 if errores else cobertura,
        "cobertura": round(cobertura, 4),
        "citados_correctos": len(correctos),
        "esperados": len(esperados),
        "alucinaciones": errores,
    }


# --------------------------------------------------------------------------
# Dimension 2: coherencia del cruce (bandas de baremos-psicometricos.md)
# --------------------------------------------------------------------------


def chequear_ejes(prosa_seccion, ejes, raices, umbral, nombre):
    """Por eje: polo dominante nombrado si supera el umbral, sin inversion ni exageracion."""
    chequeos = []
    frases = oraciones(prosa_seccion)
    for izquierdo, derecho, valor_izq, valor_der in ejes:
        diferencia = abs(valor_izq - valor_der)
        if valor_izq == valor_der:
            dominante = minoritario = None
        elif valor_izq > valor_der:
            dominante, minoritario = izquierdo, derecho
        else:
            dominante, minoritario = derecho, izquierdo

        if dominante and diferencia >= umbral:
            chequeos.append((f"{nombre} {izquierdo}/{derecho}: nombra el polo {dominante}",
                             contiene(raices[dominante], prosa_seccion)))

        invertido = exagerado = False
        for frase in frases:
            afirma = re.search(VERBOS_AFIRMACION, frase, re.IGNORECASE) and not NEGACION.search(frase)
            if not afirma:
                continue
            if minoritario and contiene(raices[minoritario], frase) and not contiene(raices[dominante], frase):
                invertido = True
            if (dominante and diferencia < umbral and contiene(raices[dominante], frase)
                    and re.search(PALABRAS_MARCADA, frase, re.IGNORECASE)):
                exagerado = True
        chequeos.append((f"{nombre} {izquierdo}/{derecho}: sin polo invertido", not invertido))
        chequeos.append((f"{nombre} {izquierdo}/{derecho}: sin preferencia exagerada", not exagerado))
    return chequeos


def evaluar_coherencia(texto, perfil):
    partes = secciones(texto)
    chequeos = []

    ils = perfil["ils"]
    chequeos += chequear_ejes(
        prosa(partes.get(1, "")),
        [(i, d, ils[i], ils[d]) for i, d in PARES_ILS],
        RAICES_ILS, UMBRAL_ILS_MARCADA, "ILS",
    )
    pers = perfil["personalidad"]
    chequeos += chequear_ejes(
        prosa(partes.get(2, "")),
        [(i, d, pers[i], pers[d]) for i, d in EJES_PERSONALIDAD],
        RAICES_PERSONALIDAD, UMBRAL_PERSONALIDAD, "Personalidad",
    )

    totales = {a: perfil["chaside"][a]["total"] for a in AREAS_CHASIDE}
    maximo = max(totales.values())
    prosa_voc = prosa(partes.get(3, ""))
    for area in (a for a, t in totales.items() if t == maximo):
        nombrada = re.search(r"\b" + area + r"\b", prosa_voc) or re.search(
            NOMBRES_AREA[area], prosa_voc, re.IGNORECASE)
        chequeos.append((f"CHASIDE: nombra el area de mayor total {area}", bool(nombrada)))
    if maximo < UMBRAL_AFINIDAD_ALTA:
        exagera = any(
            re.search(r"afinidad alta", f, re.IGNORECASE) and not NEGACION.search(f)
            for f in oraciones(prosa_voc)
        )
        chequeos.append(("CHASIDE: no declara afinidad alta sin total >= 11", not exagera))

    sintesis = partes.get(4, "")
    instrumentos = sum(
        1 for marca in (
            MARCAS_ILS + "|" + "|".join(RAICES_ILS.values()),
            MARCAS_PERSONALIDAD,
            MARCAS_VOCACIONAL,
        )
        if re.search(marca, sintesis, re.IGNORECASE)
    )
    chequeos.append((f"Sintesis: cruza al menos {MINIMO_INSTRUMENTOS_SINTESIS} instrumentos",
                     instrumentos >= MINIMO_INSTRUMENTOS_SINTESIS))

    aprobados = sum(1 for _, ok in chequeos if ok)
    return {
        "puntaje": aprobados / len(chequeos),
        "aprobados": aprobados,
        "total": len(chequeos),
        "fallos": [nombre for nombre, ok in chequeos if not ok],
    }


# --------------------------------------------------------------------------
# Dimensiones 3 y 4: estructura y guardrails
# --------------------------------------------------------------------------


def evaluar_estructura(texto):
    problemas = validar_estructura(texto)
    presentes = sum(1 for s in SECCIONES if s in texto)
    puntaje = 1.0 if not problemas else presentes / len(SECCIONES) * 0.75
    return {"puntaje": puntaje, "problemas": problemas}


def evaluar_guardrails(texto, perfil):
    """Puntaje sobre el texto del modelo, sin el aviso que agrega el backend.

    `contenido_ok` separa lo que el backend no puede corregir (tipos MBTI,
    frases clinicas, escalas) del aviso no clinico, que el backend E3-07
    agrega siempre con agregar_aviso().
    """
    hallazgos = validar_salida_etica(texto)
    escala, _ = problemas_fidelidad(texto, perfil)
    hallazgos += [p for p in escala if not p.startswith("numeros fuera")]
    contenido = [h for h in hallazgos if h != "falta el aviso no clinico"]
    return {
        "puntaje": 0.0 if hallazgos else 1.0,
        "contenido_ok": not contenido,
        "hallazgos": hallazgos,
    }


# --------------------------------------------------------------------------
# Similitud informativa con el ground truth (no entra en la fidelidad)
# --------------------------------------------------------------------------


def rouge_l(candidato, referencia):
    a = re.findall(r"\w+", candidato.lower())
    b = re.findall(r"\w+", referencia.lower())
    if not a or not b:
        return 0.0
    previo = [0] * (len(b) + 1)
    for x in a:
        actual = [0]
        for j, y in enumerate(b, 1):
            actual.append(previo[j - 1] + 1 if x == y else max(previo[j], actual[j - 1]))
        previo = actual
    lcs = previo[-1]
    if not lcs:
        return 0.0
    p, r = lcs / len(a), lcs / len(b)
    return 2 * p * r / (p + r)


# --------------------------------------------------------------------------
# Evaluacion de un registro y agregados
# --------------------------------------------------------------------------


def evaluar_registro(texto, perfil, referencia=None):
    texto = normalizar_secciones(texto or "")
    dimensiones = {
        "exactitud": evaluar_exactitud(texto, perfil),
        "coherencia": evaluar_coherencia(texto, perfil),
        "estructura": evaluar_estructura(texto),
        "guardrails": evaluar_guardrails(texto, perfil),
    }
    global_ = statistics.mean(d["puntaje"] for d in dimensiones.values())
    resultado = {
        "id": perfil.get("id"),
        "fidelidad": round(global_, 4),
        "dimensiones": dimensiones,
    }
    if referencia:
        resultado["rouge_l_vs_gt"] = round(rouge_l(texto, referencia), 4)
    return resultado


def resumen(evaluaciones, metricas=None):
    def media(clave):
        return round(statistics.mean(e["dimensiones"][clave]["puntaje"] for e in evaluaciones), 4)

    fidelidad = round(statistics.mean(e["fidelidad"] for e in evaluaciones), 4)
    alucinados = [e["id"] for e in evaluaciones if e["dimensiones"]["exactitud"]["alucinaciones"]]
    salida = {
        "registros": len(evaluaciones),
        "fidelidad_global": fidelidad,
        "meta_fidelidad": META_FIDELIDAD,
        "cumple_fidelidad": fidelidad >= META_FIDELIDAD,
        "exactitud": media("exactitud"),
        "coherencia": media("coherencia"),
        "estructura": media("estructura"),
        "guardrails": media("guardrails"),
        "guardrails_contenido": round(statistics.mean(
            1.0 if e["dimensiones"]["guardrails"]["contenido_ok"] else 0.0 for e in evaluaciones), 4),
        "registros_con_alucinacion": len(alucinados),
        "alucinaciones_total": sum(len(e["dimensiones"]["exactitud"]["alucinaciones"]) for e in evaluaciones),
        "ids_con_alucinacion": alucinados,
        "cobertura_media": round(statistics.mean(
            e["dimensiones"]["exactitud"]["cobertura"] for e in evaluaciones), 4),
    }
    rouges = [e["rouge_l_vs_gt"] for e in evaluaciones if "rouge_l_vs_gt" in e]
    if rouges:
        salida["rouge_l_vs_gt_medio"] = round(statistics.mean(rouges), 4)
    if metricas:
        latencias = [m["latencia_s"] for m in metricas]
        salida["rendimiento_cpu"] = {
            "latencia_media_s": round(statistics.mean(latencias), 2),
            "latencia_mediana_s": round(statistics.median(latencias), 2),
            "latencia_max_s": round(max(latencias), 2),
            "meta_latencia_s": META_LATENCIA_S,
            "cumple_latencia": max(latencias) <= META_LATENCIA_S,
            "tokens_por_s_medio": round(statistics.mean(m["tokens_por_s"] for m in metricas), 2),
            "tokens_salida_medio": round(statistics.mean(m["tokens_salida"] for m in metricas), 1),
            "ram_pico_mb": max(m["ram_pico_mb"] for m in metricas),
            "vram_modelo_mib": max(m.get("vram_modelo_mib", 0) for m in metricas),
            "vram_sistema_pico_mib": max(m["vram_pico_mib"] for m in metricas),
        }
    return salida


def imprimir_resumen(titulo, res):
    print("=" * 70)
    print(titulo)
    print("=" * 70)
    print(f"Registros evaluados      : {res['registros']}")
    print(f"Fidelidad global         : {res['fidelidad_global']:.1%} "
          f"(meta {res['meta_fidelidad']:.0%}: {'CUMPLE' if res['cumple_fidelidad'] else 'NO CUMPLE'})")
    print(f"  1. Exactitud numerica  : {res['exactitud']:.1%} "
          f"(cobertura media {res['cobertura_media']:.1%}; "
          f"{res['alucinaciones_total']} alucinacion(es) en {res['registros_con_alucinacion']} registro(s))")
    print(f"  2. Coherencia del cruce: {res['coherencia']:.1%}")
    print(f"  3. Estructura 4 bloques: {res['estructura']:.1%}")
    print(f"  4. Guardrails eticos   : {res['guardrails']:.1%} "
          f"(contenido sin MBTI, frases clinicas ni escalas: {res['guardrails_contenido']:.1%}; "
          "el aviso lo agrega el backend)")
    if "rouge_l_vs_gt_medio" in res:
        print(f"  (informativo) ROUGE-L vs ground truth: {res['rouge_l_vs_gt_medio']:.3f}")
    rend = res.get("rendimiento_cpu")
    if rend:
        print(f"Latencia media / max     : {rend['latencia_media_s']} s / {rend['latencia_max_s']} s "
              f"(meta {rend['meta_latencia_s']:.0f} s: {'CUMPLE' if rend['cumple_latencia'] else 'NO CUMPLE'})")
        print(f"Tokens/s medio           : {rend['tokens_por_s_medio']}")
        print(f"RAM pico Ollama          : {rend['ram_pico_mb']} MB")
        print(f"VRAM del modelo (Ollama) : {rend['vram_modelo_mib']} MiB "
              f"(VRAM total del sistema, otras apps incluidas: {rend['vram_sistema_pico_mib']} MiB)")


def escribir_reporte(carpeta, nombre, evaluaciones, res, extra):
    carpeta.mkdir(parents=True, exist_ok=True)
    reporte = {
        "fecha_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "corpus_sha256": sha256_archivo(RUTA_CORPUS),
        **extra,
        "resumen": res,
        "registros": evaluaciones,
    }
    ruta = carpeta / nombre
    ruta.write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nReporte: {ruta.relative_to(RAIZ)}")
    return ruta


# --------------------------------------------------------------------------
# Generacion en CPU
# --------------------------------------------------------------------------


def generar_cpu(modelo, perfil, max_tokens, muestreador_cls):
    import requests

    mensajes = construir_mensajes(perfil)
    payload = {
        "model": modelo,
        "system": mensajes[0]["content"],
        "prompt": mensajes[1]["content"],
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.2, "seed": 42, "num_gpu": 0},
    }
    muestreador = muestreador_cls()
    muestreador.start()
    inicio = time.perf_counter()
    try:
        respuesta = requests.post(OLLAMA_URL, json=payload, timeout=900)
        respuesta.raise_for_status()
    except requests.RequestException as exc:
        raise SystemExit(f"[FALLO] Ollama no respondio: {exc}") from None
    finally:
        latencia = time.perf_counter() - inicio
        muestreador.detener()
    datos = respuesta.json()
    tokens = int(datos.get("eval_count") or 0)
    duracion = (datos.get("eval_duration") or 0) / 1e9
    return datos.get("response", ""), {
        "latencia_s": round(latencia, 2),
        "tokens_salida": tokens,
        "tokens_por_s": round(tokens / duracion, 2) if duracion else 0.0,
        "ram_pico_mb": round(muestreador.pico_ram / 1024**2),
        "vram_modelo_mib": vram_modelo_mib(modelo),
        "vram_pico_mib": muestreador.pico_vram_mib,
    }


def vram_modelo_mib(modelo):
    """VRAM que Ollama asigno al modelo cargado (size_vram de /api/ps); 0 = 100 % CPU.

    nvidia-smi mide la VRAM de todo el sistema (navegador, escritorio), asi que
    no sirve para confirmar que el modelo corre sin GPU.
    """
    import requests

    try:
        cargados = requests.get(OLLAMA_URL.replace("/api/generate", "/api/ps"), timeout=10).json()
    except (requests.RequestException, ValueError):
        return -1
    for m in cargados.get("models", []):
        if m.get("name") == modelo or m.get("model") == modelo or m.get("name", "").startswith(modelo + ":"):
            return round((m.get("size_vram") or 0) / 1024**2)
    return -1


def cmd_generar(args):
    sys.path.insert(0, str(RAIZ / "benchmarks"))
    from benchmark import Muestreador, equipo_desde_hardware, info_hardware  # noqa: E402
    from importar_gguf import importar as importar_gguf  # noqa: E402

    if bool(args.modelo) == bool(args.gguf):
        raise SystemExit("[FALLO] indica --modelo o --gguf (uno de los dos).")
    hardware = info_hardware()
    equipo = args.equipo or equipo_desde_hardware(hardware)
    if not equipo and not args.perfiles:
        raise SystemExit(
            f"[FALLO] no se reconoce el equipo ({hardware['cpu']}). Registralo en "
            "benchmarks/equipos/ y ejecuta con --equipo <nombre>."
        )
    gguf_sha = None
    modelo = args.modelo
    if args.gguf:
        info = importar_gguf(args.gguf)
        modelo, gguf_sha = info["nombre"], info["sha256"]

    if args.perfiles:
        casos = [(cargar_perfil(Path(p)), None) for p in args.perfiles]
        carpeta = DIR_REALES / modelo.replace(":", "_")
    else:
        casos = [(r, r["output"]) for r in split_evaluacion()]
        carpeta = DIR_RESULTADOS / equipo / "e3-09" / modelo.replace(":", "_")
    if args.limite:
        casos = casos[: args.limite]

    print(f"Modelo {modelo} en CPU (num_gpu=0); {len(casos)} perfil(es). Calentando...")
    generar_cpu(modelo, casos[0][0], 16, Muestreador)  # carga del modelo, no se mide

    carpeta.mkdir(parents=True, exist_ok=True)
    evaluaciones, metricas, lineas = [], [], []
    for n, (perfil, referencia) in enumerate(casos, 1):
        texto, met = generar_cpu(modelo, perfil, args.max_tokens, Muestreador)
        ev = evaluar_registro(texto, perfil, referencia)
        ev["metricas"] = met
        evaluaciones.append(ev)
        metricas.append(met)
        lineas.append(json.dumps({"id": perfil.get("id"), "modelo": modelo, "texto": texto,
                                  "metricas": met}, ensure_ascii=False))
        print(f"  [{n:>2}/{len(casos)}] {perfil.get('id')}: fidelidad {ev['fidelidad']:.0%}, "
              f"{met['latencia_s']} s, {met['tokens_por_s']} tok/s, RAM {met['ram_pico_mb']} MB")
    (carpeta / "salidas.jsonl").write_text("\n".join(lineas) + "\n", encoding="utf-8")

    res = resumen(evaluaciones, metricas)
    imprimir_resumen(f"E3-09 - {modelo}", res)
    extra = {"modelo": modelo, "gguf_sha256": gguf_sha, "equipo": equipo, "hardware": hardware,
             "opciones": {"num_gpu": 0, "temperature": 0.2, "seed": 42, "num_predict": args.max_tokens}}
    escribir_reporte(carpeta, "reporte.json", evaluaciones, res, extra)
    return 0 if res["cumple_fidelidad"] else 1


def cmd_evaluar(args):
    salidas = [json.loads(l) for l in Path(args.salidas).read_text(encoding="utf-8").splitlines() if l.strip()]
    corpus = {r["id"]: r for r in cargar_corpus()}
    evaluaciones, metricas = [], []
    for s in salidas:
        registro = corpus.get(s["id"])
        if not registro:
            raise SystemExit(f"[FALLO] {s['id']} no esta en el corpus; usa 'generar --perfiles' para reales.")
        ev = evaluar_registro(s["texto"], registro, registro["output"])
        if s.get("metricas"):
            ev["metricas"] = s["metricas"]
            metricas.append(s["metricas"])
        evaluaciones.append(ev)
    res = resumen(evaluaciones, metricas or None)
    imprimir_resumen(f"E3-09 - {args.salidas}", res)
    if args.reporte:
        escribir_reporte(Path(args.reporte).parent, Path(args.reporte).name, evaluaciones, res,
                         {"origen_salidas": str(args.salidas)})
    return 0 if res["cumple_fidelidad"] else 1


def cmd_referencia(args):
    registros = split_evaluacion()
    evaluaciones = [evaluar_registro(r["output"], r) for r in registros]
    res = resumen(evaluaciones)
    imprimir_resumen("E3-09 - Referencia Teacher (ground truth del split de evaluacion)", res)
    for e in evaluaciones:
        fallos = e["dimensiones"]["coherencia"]["fallos"] + e["dimensiones"]["exactitud"]["alucinaciones"]
        if fallos:
            print(f"  {e['id']}: {fallos}")
    escribir_reporte(DIR_EVAL / "teacher", "reporte.json", evaluaciones, res,
                     {"modelo": "teacher (ground truth E3-06)"})
    return 0 if res["cumple_fidelidad"] else 1


def construir_parser():
    parser = argparse.ArgumentParser(description="Evaluacion SMART de fidelidad y CPU (E3-09).")
    sub = parser.add_subparsers(dest="comando", required=True)

    sub.add_parser("referencia", help="evalua el ground truth del split (calibracion Teacher)")

    gen = sub.add_parser("generar", help="genera en CPU con un modelo y lo evalua")
    gen.add_argument("--modelo", help="modelo de Ollama (por ejemplo qwen2.5:1.5b)")
    gen.add_argument("--gguf", help="ruta del GGUF ajustado; se importa con importar_gguf.py")
    gen.add_argument("--perfiles", nargs="+", help="perfiles reales (sin ground truth)")
    gen.add_argument("--equipo", help="carpeta de benchmarks/resultados/ (por defecto se deduce de la CPU)")
    gen.add_argument("--limite", type=int, help="evaluar solo los N primeros (prueba rapida)")
    gen.add_argument("--max-tokens", type=int, default=1200)

    ev = sub.add_parser("evaluar", help="evalua un JSONL de salidas ya generadas")
    ev.add_argument("--salidas", required=True, help="JSONL con {id, texto, metricas?}")
    ev.add_argument("--reporte", help="ruta del reporte JSON a escribir")
    return parser


def main(argv=None):
    args = construir_parser().parse_args(argv)
    comandos = {"referencia": cmd_referencia, "generar": cmd_generar, "evaluar": cmd_evaluar}
    return comandos[args.comando](args)


if __name__ == "__main__":
    sys.exit(main())
