"""Evaluacion E3-09 sobre corpus sintetico, CPU y evidencia sin sobrescrituras.

Uso: python benchmarks/evaluar_e3.py --modelo-ajustado savio-e3-<hash>
     --gguf modelos/modelo-q4_k_m.gguf --salida benchmarks/resultados/<equipo>/<corrida>

Reanudar con los mismos argumentos y --reanudar. Los casos ya medidos se leen,
no se repiten ni se alteran. No admite perfiles reales ni destinos externos.
"""

import argparse
import hashlib
import json
import shutil
import statistics
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from benchmark import equipo_desde_hardware, info_hardware  # noqa: E402
from rubrica_e3 import auditar  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "poc_slm"))
import interpretador as it  # noqa: E402
from importar_gguf import sha256_archivo, nombre_modelo  # noqa: E402

URL = "http://localhost:11434"
CORPUS = RAIZ / "datos/corpus/corpus.jsonl"
OPCIONES = {"num_gpu": 0, "num_predict": 1200, "num_ctx": 4096, "temperature": 0, "seed": 42, "stop": ["<|im_end|>"]}


def fecha():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def guardar(ruta, datos):
    with ruta.open("x", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=2, ensure_ascii=True)
        archivo.write("\n")


def api_ps():
    respuesta = requests.get(URL + "/api/ps", timeout=15)
    respuesta.raise_for_status()
    return respuesta.json()


def coincide(nombre, modelo):
    return nombre == modelo or nombre == modelo + ":latest"


class Muestreo(threading.Thread):
    """RSS de servidor y runner, y VRAM atribuida al modelo por Ollama.

    La ausencia de nvidia-smi no se transforma en una medicion NVIDIA de cero.
    RSS es working set residente bajo Windows; no memoria reservada total.
    """

    def __init__(self, modelo):
        super().__init__(daemon=True)
        self.modelo = modelo
        self.fin = threading.Event()
        self.rss = 0
        self.muestras_ram = 0
        self.ps = []
        self.errores = []

    def run(self):
        proxima_ps = 0.0
        while not self.fin.is_set():
            total = 0
            procesos = 0
            for proceso in psutil.process_iter(["name"]):
                nombre = (proceso.info["name"] or "").lower()
                if nombre.startswith(("ollama", "llama-server")) and "app" not in nombre:
                    try:
                        total += proceso.memory_info().rss
                        procesos += 1
                    except psutil.NoSuchProcess:
                        pass
                    except psutil.AccessDenied:
                        self.errores.append("acceso denegado a RAM de Ollama")
            if procesos:
                self.rss = max(self.rss, total)
                self.muestras_ram += 1
            if time.monotonic() >= proxima_ps:
                try:
                    self.ps.append(api_ps())
                except requests.RequestException as exc:
                    self.errores.append(type(exc).__name__)
                proxima_ps = time.monotonic() + 1
            self.fin.wait(0.25)

    def terminar(self):
        self.fin.set()
        self.join(timeout=20)

    def resultado(self, ps_final):
        self.ps.append(ps_final)
        modelos = [m for muestra in self.ps for m in muestra.get("models", []) if coincide(m["name"], self.modelo)]
        otros = [m["name"] for muestra in self.ps for m in muestra.get("models", []) if not coincide(m["name"], self.modelo)]
        vram = [m.get("size_vram") for m in modelos]
        return {"ram_pico_rss_bytes": self.rss if self.muestras_ram else None, "muestras_ram": self.muestras_ram,
                "muestras_api_ps": len(self.ps), "vram_modelo_max_bytes": max(vram) if vram and all(v is not None for v in vram) else None,
                "cpu_verificada": bool(vram) and all(v == 0 for v in vram) and not otros,
                "otros_modelos_cargados": sorted(set(otros)), "errores_muestreo": sorted(set(self.errores)),
                "api_ps_final": ps_final, "fuente_vram": "Ollama /api/ps size_vram; no medicion NVIDIA"}


def consulta(modelo, perfil):
    mensajes = it.construir_mensajes(perfil)
    prompt = ("<|im_start|>system\n" + mensajes[0]["content"] + "<|im_end|>\n"
              + "<|im_start|>user\n" + mensajes[1]["content"] + "<|im_end|>\n<|im_start|>assistant\n")
    muestreo = Muestreo(modelo)
    muestreo.start()
    inicio = time.perf_counter()
    try:
        respuesta = requests.post(URL + "/api/generate", json={"model": modelo, "prompt": prompt,
            "raw": True, "stream": False, "keep_alive": "10m", "options": OPCIONES}, timeout=900)
        latencia = time.perf_counter() - inicio
        respuesta.raise_for_status()
        datos = respuesta.json()
    finally:
        muestreo.terminar()
    memoria = muestreo.resultado(api_ps())
    duracion = datos.get("eval_duration", 0)
    return {"fecha_utc": fecha(), "id": perfil["id"], "modelo": modelo,
            "latencia_s": latencia, "tokens_generados": datos.get("eval_count", 0),
            "tokens_por_s": datos.get("eval_count", 0) * 1e9 / duracion if duracion else None,
            "memoria": memoria, "respuesta_ollama": datos, "auditoria": auditar(datos.get("response", ""), perfil)}


def porcentaje(numerador, denominador):
    return 100 * numerador / denominador if denominador else None


def resumen_calidad(auditorias):
    esperados = sum(a["numerica"]["esperados"] for a in auditorias)
    citados = sum(a["numerica"]["campos_citados"] for a in auditorias)
    correctos = sum(a["numerica"]["campos_correctos"] for a in auditorias)
    baremos = [e["estado"] for a in auditorias for e in a["baremos"].values()]
    evaluados = sum(e != "sin_evaluar" for e in baremos)
    return {"perfiles": len(auditorias), "puntajes_esperados": esperados, "puntajes_citados": citados,
            "puntajes_correctos": correctos, "fidelidad_numerica_sobre_esperados_pct": porcentaje(correctos, esperados),
            "precision_citas_reconocidas_pct": porcentaje(correctos, citados), "cobertura_citas_pct": porcentaje(citados, esperados),
            "perfiles_con_37_citas_correctas": sum(a["numerica"]["campos_correctos"] == 37 and not a["numerica"]["escalas_o_rangos"] for a in auditorias),
            "estructura_pct": porcentaje(sum(a["estructura_ok"] for a in auditorias), len(auditorias)),
            "guardrail_crudo_pct": porcentaje(sum(a["guardrail_crudo_ok"] for a in auditorias), len(auditorias)),
            "guardrail_backend_pct": porcentaje(sum(a["guardrail_backend_ok"] for a in auditorias), len(auditorias)),
            "afirmaciones_revision_profesional": sum(a["alerta_revision_profesional_inventada"] for a in auditorias),
            "baremos_items": len(baremos), "baremos_correctos": baremos.count("correcto"),
            "baremos_contradicciones": baremos.count("contradiccion"), "baremos_sin_evaluar": baremos.count("sin_evaluar"),
            "baremos_cobertura_pct": porcentaje(evaluados, len(baremos)),
            "baremos_consistencia_en_evaluables_pct": porcentaje(baremos.count("correcto"), evaluados),
            "baremos_acreditados_sobre_total_pct": porcentaje(baremos.count("correcto"), len(baremos)),
            "fidelidad_interpretativa_integral_pct": None,
            "revision_semantica_integral": "pendiente: la rubrica parcial no certifica correlaciones ni toda la prosa"}


def resumen_modelo(casos):
    calidad = resumen_calidad([c["auditoria"] for c in casos])
    latencias = [c["latencia_s"] for c in casos]
    ram = [c["memoria"]["ram_pico_rss_bytes"] for c in casos if c["memoria"]["ram_pico_rss_bytes"] is not None]
    tasas = [c["tokens_por_s"] for c in casos if c["tokens_por_s"] is not None]
    calidad.update({"latencia_media_s": statistics.mean(latencias), "latencia_mediana_s": statistics.median(latencias),
                    "latencia_max_s": max(latencias), "perfiles_hasta_60s": sum(t <= 60 for t in latencias),
                    "tokens_por_s_media": statistics.mean(tasas) if tasas else None,
                    "ram_pico_rss_bytes": max(ram) if ram else None,
                    "ram_pico_gb_decimal": max(ram) / 1e9 if ram else None,
                    "ram_pico_gib": max(ram) / 1024**3 if ram else None,
                    "cpu_verificada_todos": all(c["memoria"]["cpu_verificada"] for c in casos),
                    "muestras_ram_validas_todos": all(c["memoria"]["muestras_ram"] and not c["memoria"]["errores_muestreo"] for c in casos),
                    "truncados_por_limite": sum(c["respuesta_ollama"].get("done_reason") == "length" for c in casos)})
    calidad["metas"] = {"fidelidad_integral_85_pct": None, "estructura_100_pct": calidad["estructura_pct"] == 100,
                        "guardrail_backend_100_pct": calidad["guardrail_backend_pct"] == 100,
                        "latencia_todos_60s": all(t <= 60 for t in latencias),
                        "ram_2_5_gb": len(ram) == len(casos) and max(ram) <= 2.5e9,
                        "cpu_cero_vram": calidad["cpu_verificada_todos"]}
    return calidad


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo-ajustado", required=True)
    parser.add_argument("--gguf", required=True, type=Path)
    parser.add_argument("--salida", required=True, type=Path)
    parser.add_argument("--reanudar", action="store_true")
    args = parser.parse_args()
    hardware = info_hardware()
    equipo = equipo_desde_hardware(hardware)
    if not equipo:
        raise SystemExit("[FALLO] equipo no registrado en benchmarks/equipos/")
    raiz_equipo = (RAIZ / "benchmarks/resultados" / equipo).resolve()
    salida = args.salida.resolve()
    if not salida.is_relative_to(raiz_equipo) or salida == raiz_equipo:
        raise SystemExit("[FALLO] salida debe ser una subcarpeta nueva del equipo medido")
    digest = sha256_archivo(args.gguf)
    if args.modelo_ajustado != nombre_modelo(digest):
        raise SystemExit("[FALLO] el nombre del modelo no coincide con el hash del GGUF")
    registros = [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines() if l.strip()]
    ids = [r["id"] for r in registros]
    if len(ids) != len(set(ids)):
        raise SystemExit("[FALLO] ids repetidos")
    for registro in registros:
        if registro.get("origen") != "sintetico":
            raise SystemExit("[FALLO] solo se admite el corpus sintetico")
        errores = it.validar_perfil_backend(registro, registro["id"])
        if errores:
            raise SystemExit("[FALLO] corpus invalido: " + str(errores))
    evaluacion = [r for r in registros if int(hashlib.sha256(r["id"].encode()).hexdigest(), 16) % 5 == 0]
    if len(registros) != 150 or len(evaluacion) != 28:
        raise SystemExit("[FALLO] se esperaba corpus 150 y split de evaluacion 28")
    modelo_base = "qwen2.5:1.5b"
    protocolo = {"corpus_sha256": sha256_archivo(CORPUS), "gguf_sha256": digest,
                 "script_sha256": sha256_archivo(Path(__file__)), "rubrica_sha256": sha256_archivo(Path(__file__).with_name("rubrica_e3.py")),
                 "modelos": {"base": modelo_base, "ajustado": args.modelo_ajustado}, "opciones": OPCIONES,
                 "evaluacion_ids": [r["id"] for r in evaluacion], "repeticiones": 1,
                 "prompt": "ChatML crudo identico para ambos modelos, SYSTEM_E3 y perfil_legible del backend",
                 "rubrica": "citas etiquetadas de 37 campos; bandas y polos explicitos; sin reconocimiento no hay aprobacion",
                 "limitaciones": ["sin revision humana integral ni evaluacion clinica", "28 casos; una repeticion por modelo", "RAM RSS muestreada cada 0.25 s; VRAM del modelo segun API cada 1 s", "el split usado durante entrenamiento es validacion, no prueba independiente"]}
    if args.reanudar:
        previo = json.loads((salida / "protocolo.json").read_text(encoding="utf-8"))
        if previo["protocolo"] != protocolo:
            raise SystemExit("[FALLO] protocolo distinto; usar otra carpeta, no mezclar mediciones")
    else:
        salida.mkdir(parents=True, exist_ok=False)
        guardar(salida / "protocolo.json", {"fecha_utc": fecha(), "hardware": hardware, "nvidia_smi_disponible": bool(shutil.which("nvidia-smi")), "protocolo": protocolo})
    # El gate no modifica el manifiesto original.
    validacion = subprocess.run([sys.executable, str(RAIZ / "docs/especificaciones/validar-corpus-anonimizado.py"), "--entrada", str(CORPUS)], capture_output=True, text=True, encoding="utf-8")
    if validacion.returncode:
        raise SystemExit("[FALLO] gate de privacidad: " + validacion.stdout)
    if not args.reanudar:
        guardar(salida / "gate-privacidad.json", {"codigo": validacion.returncode, "salida": validacion.stdout})
    conjuntos = {}
    for etiqueta, modelo in protocolo["modelos"].items():
        carpeta = salida / etiqueta
        carpeta.mkdir(exist_ok=True)
        pendientes = [r for r in evaluacion if not (carpeta / (r["id"] + ".json")).exists()]
        if pendientes:
            # Liberar runners antes de medir: solo modelos de esta comparacion.
            activos = api_ps().get("models", [])
            for activo in activos:
                if not any(coincide(activo["name"], m) for m in protocolo["modelos"].values()):
                    raise SystemExit("[FALLO] hay otro modelo cargado; no se mezclara su RAM")
                liberacion = requests.post(URL + "/api/generate", json={"model": activo["name"], "keep_alive": 0}, timeout=120)
                liberacion.raise_for_status()
            calentamiento = requests.post(URL + "/api/generate", json={"model": modelo, "prompt": "Responde listo", "stream": False, "keep_alive": "10m", "options": {**OPCIONES, "num_predict": 8}}, timeout=180)
            calentamiento.raise_for_status()
            numero = len(list(carpeta.glob("calentamiento-*.json"))) + 1
            guardar(carpeta / f"calentamiento-{numero}.json", {"fecha_utc": fecha(), "respuesta": calentamiento.json(), "api_ps": api_ps()})
        casos = []
        for indice, perfil in enumerate(evaluacion, 1):
            ruta = carpeta / (perfil["id"] + ".json")
            if ruta.exists():
                caso = json.loads(ruta.read_text(encoding="utf-8"))
            else:
                caso = consulta(modelo, perfil)
                guardar(ruta, caso)
                (carpeta / (perfil["id"] + ".md")).write_text(caso["respuesta_ollama"].get("response", ""), encoding="utf-8")
            casos.append(caso)
            print(f"[{etiqueta} {indice}/28] {perfil['id']} | {caso['latencia_s']:.2f} s | {caso['tokens_por_s'] or 0:.2f} tok/s | CPU={caso['memoria']['cpu_verificada']} | citas={caso['auditoria']['numerica']['campos_correctos']}/37", flush=True)
            if not caso["memoria"]["cpu_verificada"]:
                raise SystemExit("[FALLO] CPU no verificada; se detiene conservando evidencia")
        conjuntos[etiqueta] = resumen_modelo(casos)
    teacher = [{"id": r["id"], "auditoria": auditar(r["output"], r)} for r in evaluacion]
    if not (salida / "teacher-auditoria.json").exists():
        guardar(salida / "teacher-auditoria.json", teacher)
    conjuntos["teacher"] = resumen_calidad([c["auditoria"] for c in teacher])
    resumen = {"fecha_utc": fecha(), "hardware": hardware, "protocolo": protocolo, "resultados": conjuntos}
    guardar(salida / "resumen.json", resumen)
    print(json.dumps(resumen["resultados"], indent=2, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
