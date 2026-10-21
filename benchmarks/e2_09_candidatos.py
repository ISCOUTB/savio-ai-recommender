"""e2_09_candidatos.py - Mediciones de modelos candidatos para E2-09 (destilacion y fine-tuning).

Complementa a benchmarks/benchmark.py (RAM, VRAM, tokens/s) con tres mediciones
propias de la Entrega 2:

  1. Metadatos y licencia de cada modelo, leidos de Ollama (/api/show).
  2. KV cache: teorico (formula con la arquitectura) y medido (diferencia del
     tamano reportado por /api/ps al cargar el modelo con dos num_ctx distintos).
  3. Linea base de la tarea A/B/C: el modelo sin ajuste recibe un perfil y los
     3 recursos de la semana 1 y debe responder JSON con opcion, justificacion
     y descarte. Se mide formato valido, opcion valida, URLs inventadas y latencia.

Uso (desde la raiz del repo, con Ollama corriendo):
    python benchmarks/e2_09_candidatos.py
    python benchmarks/e2_09_candidatos.py --modelos qwen2.5:0.5b qwen2.5:3b --semillas 1

Salida: benchmarks/resultados/amd-ryzen-5-5600h-rtx-3050/e2-09/candidatos.json
Dependencias: requests (ver benchmarks/requirements.txt).
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
OLLAMA = "http://localhost:11434"
RECURSOS = RAIZ / "poc_slm" / "recursos" / "semana_1.json"
DIR_SALIDA = RAIZ / "benchmarks" / "resultados" / "amd-ryzen-5-5600h-rtx-3050" / "e2-09"

MODELOS_DEFAULT = [
    "smollm2:360m", "qwen2.5:0.5b", "llama3.2:1b", "qwen2.5:1.5b",
    "smollm2:1.7b", "gemma2:2b", "qwen2.5:3b",
]
CTX_BAJO, CTX_ALTO = 2048, 8192  # Contextos usados para medir el KV cache
TOKENS_SALIDA = 300

# Perfiles simulados contrastantes (valores alcanzables de escala-canonica.md).
# La "opcion_esperada" es una etiqueta de referencia del equipo, no una verdad absoluta.
PERFILES = [
    {
        "estudiante_id": "sim-visual-guiado",
        "origen": "simulado",
        "opcion_esperada": "A",
        "estilos_aprendizaje": {
            "modelo": "felder_silverman",
            "puntajes": {"activo_reflexivo": 1.7, "sensorial_intuitivo": 3.2, "visual_verbal": 1.4, "secuencial_global": 2.8},
            "preferencias": ["activo", "visual"],
            "descripcion_para_prompt": "Prefiere diagramas, esquemas y ejemplos visuales breves; aprende mejor viendo la estructura antes que leyendo textos largos.",
        },
        "personalidad": {
            "rasgos": {"introversion_extraversion": 3.4, "autonomia": 2.2, "metodicidad": 4.3, "apertura": 3.2},
            "resumen_conductual": "Necesita guia clara y pasos cortos; se desanima con tareas largas sin estructura.",
            "preferencias_trabajo": ["pasos cortos", "guia explicita", "retroalimentacion inmediata"],
        },
        "chaside": {
            "areas": {"C": 2.4, "H": 2.1, "A": 3.0, "S": 1.6, "I": 4.4, "D": 1.3, "E": 3.6},
            "areas_dominantes": ["I", "E"],
            "descripcion_para_analogias": "Conviene conectar la materia con ejemplos de procesos tecnicos, sistemas y resolucion de problemas y experimentacion, datos y metodo cientifico; areas principales: Ensenanzas Tecnicas (I) y Ciencias Experimentales (E).",
        },
    },
    {
        "estudiante_id": "sim-verbal-reflexivo",
        "origen": "simulado",
        "opcion_esperada": "B",
        "estilos_aprendizaje": {
            "modelo": "felder_silverman",
            "puntajes": {"activo_reflexivo": 4.3, "sensorial_intuitivo": 3.5, "visual_verbal": 4.6, "secuencial_global": 2.5},
            "preferencias": ["reflexivo", "verbal"],
            "descripcion_para_prompt": "Prefiere leer y analizar textos con calma, tomar notas y reflexionar antes de producir; los diagramas sin texto le aportan poco.",
        },
        "personalidad": {
            "rasgos": {"introversion_extraversion": 1.9, "autonomia": 3.9, "metodicidad": 3.7, "apertura": 4.1},
            "resumen_conductual": "Trabaja bien de forma individual y con lecturas extensas; disfruta comparar puntos de vista.",
            "preferencias_trabajo": ["individual", "lectura profunda", "ritmo propio"],
        },
        "chaside": {
            "areas": {"C": 3.0, "H": 4.7, "A": 3.9, "S": 2.7, "I": 1.9, "D": 1.3, "E": 2.1},
            "areas_dominantes": ["H", "A"],
            "descripcion_para_analogias": "Conviene conectar la materia con ejemplos de comunicacion, analisis social y textos y creacion, diseno y expresion; areas principales: Humanidades/Sociales/Juridicas (H) y Artistica (A).",
        },
    },
    {
        "estudiante_id": "sim-practico-autonomo",
        "origen": "simulado",
        "opcion_esperada": "C",
        "estilos_aprendizaje": {
            "modelo": "felder_silverman",
            "puntajes": {"activo_reflexivo": 1.4, "sensorial_intuitivo": 1.7, "visual_verbal": 3.2, "secuencial_global": 2.1},
            "preferencias": ["activo", "sensorial", "secuencial"],
            "descripcion_para_prompt": "Aprende haciendo: prefiere ejercicios concretos paso a paso y aplicar de inmediato lo que estudia.",
        },
        "personalidad": {
            "rasgos": {"introversion_extraversion": 3.9, "autonomia": 4.4, "metodicidad": 4.1, "apertura": 3.4},
            "resumen_conductual": "Autonomo y constante; tolera retos largos si producen algo propio.",
            "preferencias_trabajo": ["practica", "retos", "autoevaluacion"],
        },
        "chaside": {
            "areas": {"C": 4.1, "H": 2.7, "A": 1.9, "S": 3.9, "I": 2.1, "D": 1.6, "E": 3.3},
            "areas_dominantes": ["C", "S"],
            "descripcion_para_analogias": "Conviene conectar la materia con ejemplos de organizacion, gestion y tareas administrativas y cuidado de personas y practicas de salud; areas principales: Administrativa (C) y Ciencias de la Salud (S).",
        },
    },
]

SYSTEM = (
    "Eres el recomendador academico de SAVIO. Recibes el perfil de un estudiante y tres recursos "
    "(A, B, C) de la misma semana. Eliges UNO de esos tres recursos. Reglas: responde en espanol; "
    "no inventes recursos, enlaces, URLs, autores ni titulos; usa el tono empatico; no menciones "
    "puntajes ni carreras. Responde SOLO con un objeto JSON con las claves "
    '"opcion" (A, B o C), "justificacion" (2 oraciones) y "descarte" (1 oracion por cada opcion no elegida).'
)


def prompt_usuario(perfil: dict, recursos: list) -> str:
    datos = {
        "estilo": perfil["estilos_aprendizaje"]["descripcion_para_prompt"],
        "personalidad": perfil["personalidad"]["resumen_conductual"],
        "analogias": perfil["chaside"]["descripcion_para_analogias"],
    }
    lineas = [f"Perfil del estudiante: {json.dumps(datos, ensure_ascii=False)}", "", "Recursos de la semana:"]
    for r in recursos:
        lineas.append(f"- {r['opcion']}: {r['titulo']} | tipo {r['tipo']} | nivel {r['nivel']} | "
                      f"{r['carga_estimada_min']} min | {r['resumen']}")
    lineas += ["", "Elige el recurso mas adecuado y responde solo con el JSON pedido."]
    return "\n".join(lineas)


def api(ruta: str, **payload) -> dict:
    r = requests.post(f"{OLLAMA}{ruta}", json=payload, timeout=900)
    r.raise_for_status()
    return r.json()


def descargar_todo() -> None:
    for m in requests.get(f"{OLLAMA}/api/ps", timeout=10).json().get("models", []):
        api("/api/generate", model=m["name"], keep_alive=0)
    time.sleep(2)


def metadatos(modelo: str) -> dict:
    d = api("/api/show", model=modelo)
    info, det = d.get("model_info", {}), d.get("details", {})
    arq = info.get("general.architecture", "")
    capas = info.get(f"{arq}.block_count")
    cabezas = info.get(f"{arq}.attention.head_count")
    cabezas_kv = info.get(f"{arq}.attention.head_count_kv", cabezas)
    embedding = info.get(f"{arq}.embedding_length")
    dim_k = info.get(f"{arq}.attention.key_length") or (embedding // cabezas if embedding and cabezas else None)
    dim_v = info.get(f"{arq}.attention.value_length") or dim_k
    # KV cache en f16: por cada capa se guardan K y V de cabezas_kv cabezas (2 bytes por valor)
    kv_bytes_token = capas * cabezas_kv * (dim_k + dim_v) * 2 if all((capas, cabezas_kv, dim_k, dim_v)) else None
    return {
        "arquitectura": arq,
        "parametros": det.get("parameter_size"),
        "parametros_exactos": info.get("general.parameter_count"),
        "cuantizacion": det.get("quantization_level"),
        "licencia": info.get("general.license") or "no declarada en metadatos",
        "licencia_link": info.get("general.license.link"),
        "capas": capas, "cabezas_atencion": cabezas, "cabezas_kv": cabezas_kv,
        "dim_k": dim_k, "dim_v": dim_v,
        "contexto_max": info.get(f"{arq}.context_length"),
        "kv_teorico_kib_por_token": round(kv_bytes_token / 1024, 2) if kv_bytes_token else None,
    }


def tamano_cargado(modelo: str, num_ctx: int) -> int:
    """Carga el modelo solo en CPU con num_ctx dado y devuelve el tamano total que reporta Ollama."""
    descargar_todo()
    api("/api/generate", model=modelo, prompt="hola", stream=False, keep_alive="2m",
        options={"num_ctx": num_ctx, "num_gpu": 0, "num_predict": 1})
    ps = requests.get(f"{OLLAMA}/api/ps", timeout=10).json().get("models", [])
    return next(m["size"] for m in ps if m["name"] == modelo)


def kv_medido(modelo: str) -> dict:
    bajo, alto = tamano_cargado(modelo, CTX_BAJO), tamano_cargado(modelo, CTX_ALTO)
    return {
        "tamano_ctx_bajo_mb": round(bajo / 1024**2),
        "tamano_ctx_alto_mb": round(alto / 1024**2),
        "kv_medido_kib_por_token": round((alto - bajo) / (CTX_ALTO - CTX_BAJO) / 1024, 2),
    }


def evaluar_respuesta(texto: str) -> dict:
    bloque = re.search(r"\{.*\}", texto, re.S)
    try:
        obj = json.loads(bloque.group(0)) if bloque else None
    except json.JSONDecodeError:
        obj = None
    opcion = str(obj.get("opcion", "")).strip().upper()[:1] if isinstance(obj, dict) else ""
    return {
        "json_valido": isinstance(obj, dict),
        "claves_completas": isinstance(obj, dict) and all(k in obj for k in ("opcion", "justificacion", "descarte")),
        "opcion": opcion if opcion in "ABC" and opcion else None,
        "inventa_url": bool(re.search(r"https?://|www\.", texto)),
    }


def linea_base(modelo: str, recursos: list, semillas: list) -> list:
    descargar_todo()
    corridas = []
    for perfil in PERFILES:
        for semilla in semillas:
            inicio = time.perf_counter()
            r = api("/api/generate", model=modelo, system=SYSTEM, prompt=prompt_usuario(perfil, recursos),
                    stream=False, keep_alive="5m",
                    options={"num_predict": TOKENS_SALIDA, "temperature": 0.7, "seed": semilla})
            dur = time.perf_counter() - inicio
            ev = evaluar_respuesta(r.get("response", ""))
            corridas.append({
                "perfil": perfil["estudiante_id"], "semilla": semilla,
                "opcion_esperada": perfil["opcion_esperada"], **ev,
                "coincide_esperada": ev["opcion"] == perfil["opcion_esperada"],
                "tokens_prompt": r.get("prompt_eval_count"), "tokens_salida": r.get("eval_count"),
                "latencia_s": round(dur, 2), "respuesta": r.get("response", "").strip(),
            })
            print(f"  [{modelo}] {perfil['estudiante_id']} seed {semilla}: json={ev['json_valido']} "
                  f"opcion={ev['opcion']} url={ev['inventa_url']} {dur:.1f}s")
    return corridas


def resumen(corridas: list) -> dict:
    n = len(corridas)
    def tasa(clave):
        return round(100 * sum(1 for c in corridas if c[clave]) / n)
    return {
        "corridas": n,
        "json_valido_pct": tasa("json_valido"),
        "claves_completas_pct": tasa("claves_completas"),
        "opcion_valida_pct": round(100 * sum(1 for c in corridas if c["opcion"]) / n),
        "coincide_esperada_pct": tasa("coincide_esperada"),
        "inventa_url_pct": tasa("inventa_url"),
        "latencia_media_s": round(sum(c["latencia_s"] for c in corridas) / n, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Mediciones de candidatos para E2-09.")
    parser.add_argument("--modelos", nargs="+", default=MODELOS_DEFAULT)
    parser.add_argument("--semillas", nargs="+", type=int, default=[1, 2])
    parser.add_argument("--recursos", type=Path, default=RECURSOS,
                        help="JSON de recursos A/B/C (por defecto poc_slm/recursos/semana_1.json, de E2-08)")
    args = parser.parse_args()

    recursos = json.loads(args.recursos.read_text(encoding="utf-8"))
    version = requests.get(f"{OLLAMA}/api/version", timeout=10).json().get("version")
    salida = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "ollama": version,
        "configuracion": {"ctx_bajo": CTX_BAJO, "ctx_alto": CTX_ALTO, "num_predict": TOKENS_SALIDA,
                          "temperature": 0.7, "semillas": args.semillas,
                          "recursos": "poc_slm/recursos/semana_1.json", "perfiles": "simulados (ver PERFILES)"},
        "perfiles": PERFILES,
        "modelos": [],
    }
    for modelo in args.modelos:
        print(f"== {modelo}")
        meta = metadatos(modelo)
        kv = kv_medido(modelo)
        corridas = linea_base(modelo, recursos, args.semillas)
        salida["modelos"].append({"modelo": modelo, **meta, **kv, "linea_base": resumen(corridas),
                                  "corridas": corridas})
        print(f"  KV teorico {meta['kv_teorico_kib_por_token']} KiB/token | medido {kv['kv_medido_kib_por_token']} KiB/token")
    descargar_todo()

    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    destino = DIR_SALIDA / "candidatos.json"
    destino.write_text(json.dumps(salida, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultados guardados en: {destino}")


if __name__ == "__main__":
    main()
