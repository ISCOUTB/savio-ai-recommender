"""e2_09_concurrencia.py - Medicion de concurrencia para E2-09.

Envia N solicitudes A/B/C simultaneas a Ollama (N = 1, 2, 4, 8) y mide la
latencia por usuario, el rendimiento agregado (tokens/s del servidor) y la
memoria que reporta /api/ps. Reutiliza el system prompt, los perfiles
simulados y el formato de prompt de benchmarks/e2_09_candidatos.py.

Para no modificar el Ollama del equipo, se recomienda un servidor aparte con
paralelismo explicito (PowerShell):
    $env:OLLAMA_HOST = "127.0.0.1:11435"; $env:OLLAMA_NUM_PARALLEL = "8"; ollama serve

Uso (desde la raiz del repo):
    python benchmarks/e2_09_concurrencia.py --host http://127.0.0.1:11435 --recursos <semana_1.json>

Salida: benchmarks/resultados/amd-ryzen-5-5600h-rtx-3050/e2-09/concurrencia.json
"""

import argparse
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e2_09_candidatos import DIR_SALIDA, PERFILES, RECURSOS, SYSTEM, prompt_usuario  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOKENS_SALIDA = 200
NIVELES = [1, 2, 4, 8]


def una_solicitud(host: str, modelo: str, prompt: str, semilla: int) -> dict:
    inicio = time.perf_counter()
    r = requests.post(f"{host}/api/generate", json={
        "model": modelo, "system": SYSTEM, "prompt": prompt, "stream": False, "keep_alive": "5m",
        "options": {"num_predict": TOKENS_SALIDA, "temperature": 0.7, "seed": semilla, "num_ctx": 2048},
    }, timeout=900).json()
    return {"latencia_s": time.perf_counter() - inicio, "tokens": r.get("eval_count", 0)}


def medir_nivel(host: str, modelo: str, prompts: list, n: int) -> dict:
    with ThreadPoolExecutor(max_workers=n) as pool:
        inicio = time.perf_counter()
        futuros = [pool.submit(una_solicitud, host, modelo, prompts[i % len(prompts)], i + 1) for i in range(n)]
        res = [f.result() for f in futuros]
        pared = time.perf_counter() - inicio
    ps = requests.get(f"{host}/api/ps", timeout=10).json().get("models", [])
    cargado = next((m for m in ps if m["name"] == modelo), {})
    lat = sorted(x["latencia_s"] for x in res)
    tokens = sum(x["tokens"] for x in res)
    return {
        "usuarios_simultaneos": n,
        "tiempo_pared_s": round(pared, 2),
        "latencia_media_s": round(statistics.mean(lat), 2),
        "latencia_max_s": round(lat[-1], 2),
        "tokens_totales": tokens,
        "tokens_por_seg_agregado": round(tokens / pared, 1),
        "memoria_reportada_mb": round(cargado.get("size", 0) / 1024**2),
        "memoria_en_vram_mb": round(cargado.get("size_vram", 0) / 1024**2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Concurrencia A/B/C para E2-09.")
    parser.add_argument("--host", default="http://127.0.0.1:11435")
    parser.add_argument("--modelos", nargs="+", default=["qwen2.5:0.5b", "qwen2.5:1.5b", "qwen2.5:3b"])
    parser.add_argument("--recursos", type=Path, default=RECURSOS)
    args = parser.parse_args()

    recursos = json.loads(args.recursos.read_text(encoding="utf-8"))
    prompts = [prompt_usuario(p, recursos) for p in PERFILES]
    version = requests.get(f"{args.host}/api/version", timeout=10).json().get("version")
    salida = {"fecha": datetime.now().isoformat(timespec="seconds"), "ollama": version,
              "configuracion": {"niveles": NIVELES, "num_predict": TOKENS_SALIDA, "num_ctx": 2048,
                                "host": args.host}, "modelos": []}
    for modelo in args.modelos:
        print(f"== {modelo}")
        una_solicitud(args.host, modelo, prompts[0], 0)  # calentamiento: carga el modelo
        niveles = []
        for n in NIVELES:
            r = medir_nivel(args.host, modelo, prompts, n)
            niveles.append(r)
            print(f"  {n} usuarios: pared {r['tiempo_pared_s']} s | latencia media {r['latencia_media_s']} s "
                  f"(max {r['latencia_max_s']}) | {r['tokens_por_seg_agregado']} tok/s agregados | "
                  f"memoria {r['memoria_reportada_mb']} MB")
        salida["modelos"].append({"modelo": modelo, "niveles": niveles})
        requests.post(f"{args.host}/api/generate", json={"model": modelo, "keep_alive": 0}, timeout=60)

    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    destino = DIR_SALIDA / "concurrencia.json"
    destino.write_text(json.dumps(salida, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultados guardados en: {destino}")


if __name__ == "__main__":
    main()
