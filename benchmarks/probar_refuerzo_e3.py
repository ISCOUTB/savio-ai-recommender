"""Compara un perfil sintetico con/sin refuerzo, mismo GGUF y CPU.

Uso desde la raiz: python benchmarks/probar_refuerzo_e3.py
Es una prueba exploratoria de un caso conocido, no una nueva validacion global.
Cada ejecucion crea otra carpeta; conserva respuestas incluso si son rechazadas.
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from benchmark import equipo_desde_hardware, info_hardware  # noqa: E402
from evaluar_e3 import Muestreo, api_ps, coincide, guardar, OPCIONES, URL  # noqa: E402
from citas_json_e3 import auditar_ampliado  # noqa: E402
import interpretador as it  # noqa: E402
from importar_gguf import sha256_archivo, nombre_modelo  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


def generar(modelo, perfil, refuerzo):
    # Reiniciar solo el runner de este modelo para igualar carga y cache.
    for activo in api_ps().get("models", []):
        if not coincide(activo["name"], modelo):
            raise SystemExit("[FALLO] otro modelo cargado; no se mezclara su RAM")
        respuesta = requests.post(URL + "/api/generate", json={"model": activo["name"], "keep_alive": 0}, timeout=120)
        respuesta.raise_for_status()
    calentamiento = requests.post(URL + "/api/generate", json={"model": modelo, "prompt": "Responde listo", "stream": False,
        "keep_alive": "10m", "options": {**OPCIONES, "num_predict": 8}}, timeout=180)
    calentamiento.raise_for_status()
    ps = api_ps()
    cargados = [m for m in ps.get("models", []) if coincide(m["name"], modelo)]
    if not cargados or any(m.get("size_vram") != 0 for m in cargados):
        raise SystemExit("[FALLO] el calentamiento no confirma CPU")
    mensajes = it.construir_mensajes(perfil, refuerzo_baremos=refuerzo)
    prompt = ("<|im_start|>system\n" + mensajes[0]["content"] + "<|im_end|>\n"
              + "<|im_start|>user\n" + mensajes[1]["content"] + "<|im_end|>\n<|im_start|>assistant\n")
    muestreo = Muestreo(modelo)
    muestreo.start()
    inicio = time.perf_counter()
    try:
        respuesta = requests.post(URL + "/api/generate", json={"model": modelo, "prompt": prompt, "raw": True,
            "stream": False, "keep_alive": "10m", "options": OPCIONES}, timeout=900)
        latencia = time.perf_counter() - inicio
        respuesta.raise_for_status()
        datos = respuesta.json()
    finally:
        muestreo.terminar()
    memoria = muestreo.resultado(api_ps())
    crudo = datos.get("response", "")
    publicado = it.agregar_aviso(it.normalizar_secciones(crudo))
    # Aplicar el mismo validador estricto a los dos modos, no comparar dos reglas.
    validacion = it.validar_interpretacion(publicado, perfil, refuerzo_baremos=True)
    duracion = datos.get("eval_duration", 0)
    return {"refuerzo_baremos": refuerzo, "mensajes": mensajes, "respuesta_ollama": datos,
            "calentamiento": calentamiento.json(), "texto_postprocesado": publicado,
            "latencia_s": latencia, "tokens_por_s": datos.get("eval_count", 0) * 1e9 / duracion if duracion else None,
            "memoria": memoria, "validacion_estricta_comun": validacion, "auditoria": auditar_ampliado(crudo, perfil)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--perfil", type=Path, default=Path("perfiles/brutos/ejemplo-perfil-bruto-dominante.json"))
    parser.add_argument("--gguf", type=Path, default=Path("modelos/modelo-q4_k_m.gguf"))
    args = parser.parse_args()
    entrada = json.loads(args.perfil.read_text(encoding="utf-8-sig"))
    if not isinstance(entrada, dict) or entrada.get("origen") != "sintetico":
        raise SystemExit("[FALLO] esta prueba publica solo admite perfiles sinteticos")
    perfil = it.cargar_perfil(args.perfil)
    hardware = info_hardware()
    equipo = equipo_desde_hardware(hardware)
    if not equipo:
        raise SystemExit("[FALLO] equipo no registrado en benchmarks/equipos/")
    digest = sha256_archivo(args.gguf)
    modelo = nombre_modelo(digest)
    marca = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    carpeta = RAIZ / "benchmarks/resultados" / equipo / ("e3-refuerzo-" + marca)
    carpeta.mkdir(parents=True, exist_ok=False)
    fuentes = ("poc_slm/interpretador.py", "poc_slm/lectura_baremos.py", "benchmarks/probar_refuerzo_e3.py", "benchmarks/citas_json_e3.py", "docs/especificaciones/baremos-psicometricos.md")
    guardar(carpeta / "protocolo.json", {"fecha_utc": marca, "hardware": hardware, "modelo": modelo,
        "gguf_sha256": digest, "perfil": str(args.perfil), "perfil_sha256": sha256_archivo(args.perfil),
        "opciones": OPCIONES, "lectura_calculada": it.calcular_lecturas(perfil),
        "contrato_refuerzo": "Tres secciones de filas calculadas que el modelo debe reproducir; sintesis de una o dos frases sin reclasificar. El backend valida, no reemplaza la respuesta por esas filas.",
        "fuentes_sha256": {p: sha256_archivo(RAIZ / p) for p in fuentes},
        "alcance": "Un perfil conocido, una respuesta por modo, sin reintentos; no acredita fidelidad global ni selecciona la mejor salida"})
    casos = {}
    for etiqueta, refuerzo in (("sin-refuerzo", False), ("con-refuerzo", True)):
        print("Ejecutando", etiqueta, "sobre", perfil["id"], "en CPU...", flush=True)
        caso = generar(modelo, perfil, refuerzo)
        guardar(carpeta / (etiqueta + ".json"), caso)
        casos[etiqueta] = caso
        print(f"{etiqueta}: {caso['latencia_s']:.2f} s; CPU={caso['memoria']['cpu_verificada']}; validador estricto={caso['validacion_estricta_comun']['ok']}", flush=True)
        if not caso["memoria"]["cpu_verificada"]:
            raise SystemExit("[FALLO] CPU no verificada; se conserva la respuesta medida")
    lineas = ["# Prueba exploratoria de refuerzo de baremos", "", f"Perfil sintetico: `{perfil['id']}`. Modelo: `{modelo}`.",
        f"SHA-256 GGUF: `{digest}`.", "",
        "Mismos parametros: temperatura 0, semilla 42, num_ctx=4096, num_predict=1200, num_gpu=0.",
        "Una respuesta por modo, sin reintentos; calentamiento y reinicio del runner antes de cada modo.",
        "El mismo validador estricto y el mismo auditor se aplican a las dos respuestas.",
        "La condicion sin refuerzo conserva el prompt original. La otra agrega reglas y hechos calculados por Python.",
        "El refuerzo exige solo filas verificadas en las tres primeras secciones y una sintesis breve sin puntajes, bandas ni polos.",
        "La respuesta completa procede del modelo. El backend no sustituye los errores por una plantilla para aprobarlos.",
        "Solo se agrega el aviso y se normalizan encabezados para validar; las respuestas crudas permanecen intactas.",
        "Es un experimento sobre un fixture conocido. Un resultado favorable no acredita la meta global del 85%.", "",
        "| Medida | Sin refuerzo | Con refuerzo |", "|---|---:|---:|"]
    a, b = casos.values()
    for titulo, valores in (
        ("Latencia (s)", [f"{c['latencia_s']:.2f}" for c in (a, b)]),
        ("Velocidad (tokens/s)", [f"{c['tokens_por_s']:.2f}" for c in (a, b)]),
        ("RAM pico RSS (GB decimal)", [f"{c['memoria']['ram_pico_rss_bytes']/1e9:.3f}" for c in (a, b)]),
        ("VRAM del modelo (bytes)", [str(c["memoria"]["vram_modelo_max_bytes"]) for c in (a, b)]),
        ("Citas correctas / esperadas", [f"{c['auditoria']['numerica']['campos_correctos']}/{c['auditoria']['numerica']['esperados']}" for c in (a, b)]),
        ("Contradicciones de baremos reconocidas por auditor", [str(sum(v["estado"] == "contradiccion" for v in c["auditoria"]["baremos"].values())) for c in (a, b)]),
        ("Errores reconocidos por validador estricto", [str(len(c["validacion_estricta_comun"]["errores"])) for c in (a, b)]),
        ("Aceptacion automatica parcial", [str(c["validacion_estricta_comun"]["ok"]) for c in (a, b)]),
    ):
        lineas.append(f"| {titulo} | {valores[0]} | {valores[1]} |")
    for etiqueta, caso in casos.items():
        lineas.extend(["", "## Hallazgos: " + etiqueta, ""])
        errores = caso["validacion_estricta_comun"]["errores"]
        lineas += ["- " + json.dumps(e, ensure_ascii=True) for e in errores] or ["Sin hallazgos en los controles parciales. Revision integral pendiente."]
    lineas += ["", "## Evidencia", "", "- [Protocolo](protocolo.json)", "- [Respuesta original sin refuerzo](sin-refuerzo.json)",
        "- [Respuesta original con refuerzo](con-refuerzo.json)", "- [Reglas ejecutables](../../../../poc_slm/lectura_baremos.py)",
        "- [Baremos del proyecto](../../../../docs/especificaciones/baremos-psicometricos.md)", ""]
    with (carpeta / "informe.md").open("x", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas))
    relativo = carpeta.relative_to(RAIZ).as_posix()
    bitacora = RAIZ / "experimentos/bitacora.md"
    dia = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fila = (f"| {dia} | persona-1 con asistencia de IA | Probar refuerzo de reglas y lecturas en un solo perfil sintetico (#51, #52) | "
        f"[Experimento](../{relativo}/informe.md): {perfil['id']}, {modelo}; sin/con refuerzo {a['latencia_s']:.2f}/{b['latencia_s']:.2f} s; "
        f"validador estricto comun {a['validacion_estricta_comun']['ok']}/{b['validacion_estricta_comun']['ok']}; CPU verificada en ambos | "
        "Prueba exploratoria, no nueva validacion global ni nuevo entrenamiento. Conservar respuestas rechazadas y revision integral pendiente |\n")
    with bitacora.open("a", encoding="utf-8") as archivo:
        archivo.write(fila)
    print("Informe:", carpeta / "informe.md", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
