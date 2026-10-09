"""benchmark.py — Benchmark local de SLMs para la PoC SAVIO (Sprint 4, Issues #8 y #9).

Mide, para cada modelo y modo de ejecucion (GPU / solo CPU):
  - RAM del proceso de inferencia de Ollama (pico de RSS, muestreado con psutil)
  - VRAM usada (pico, muestreado con nvidia-smi; solo modo GPU)
  - Tokens/segundo de generacion (eval_count / eval_duration reportado por Ollama)
  - Tiempo total de respuesta para ~300 tokens de salida
  - Tiempo de carga del modelo en frio

Usa el mismo prompt real del recomendador (escenario A_nota_baja + refuerzo) para
que la medicion represente la carga de trabajo de la PoC, y guarda cada salida
generada para la evaluacion de calidad en espanol.

Uso:
    python benchmarks/benchmark.py
    python benchmarks/benchmark.py --modelos qwen2.5:1.5b gemma2:2b --modos gpu --repeticiones 5

Dependencias: requests, psutil (ver benchmarks/requirements.txt).
"""

import argparse
import json
import platform
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import psutil
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "poc_slm"))
from recommender import cargar_evento, cargar_system_prompt, ensamblar_prompt  # noqa: E402

OLLAMA = "http://localhost:11434"
MODELOS_DEFAULT = ["qwen2.5:1.5b", "gemma2:2b", "qwen2.5:3b"]
ESCENARIO = "A_nota_baja"
TOKENS_SALIDA = 300  # Longitud fija de salida para comparacion justa (Sprint 4)
DIR_RESULTADOS = RAIZ / "benchmarks" / "resultados"


class Muestreador(threading.Thread):
    """Muestrea en segundo plano el pico de RAM de Ollama y de VRAM de la GPU."""

    def __init__(self, intervalo: float = 0.2):
        super().__init__(daemon=True)
        self.intervalo = intervalo
        self.pico_ram = 0
        self.pico_vram_mib = 0
        self._parar = threading.Event()

    def run(self) -> None:
        while not self._parar.is_set():
            self.pico_ram = max(self.pico_ram, ram_ollama())
            self.pico_vram_mib = max(self.pico_vram_mib, vram_usada_mib())
            self._parar.wait(self.intervalo)

    def detener(self) -> None:
        self._parar.set()
        self.join()


def ram_ollama() -> int:
    """Suma el RSS (bytes) de los procesos de Ollama (servidor + runner llama-server del modelo)."""
    total = 0
    for p in psutil.process_iter(["name", "memory_info"]):
        nombre = (p.info["name"] or "").lower()
        es_ollama = nombre.startswith(("ollama", "llama-server")) and "app" not in nombre
        if es_ollama and p.info["memory_info"]:
            total += p.info["memory_info"].rss
    return total


def vram_usada_mib() -> int:
    """VRAM total usada en la GPU NVIDIA (MiB); 0 si no hay nvidia-smi."""
    try:
        salida = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        ).stdout
        return int(salida.strip().splitlines()[0])
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
        return 0


def info_hardware() -> dict:
    """Recolecta las especificaciones del equipo de prueba."""
    gpu = "N/D"
    try:
        gpu = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except OSError:
        pass
    cpu = platform.processor()
    so = f"{platform.system()} {platform.release()} ({platform.version()})"
    if platform.system() == "Windows":
        # platform.release() reporta "10" tambien en Windows 11 (build >= 22000)
        if int(platform.version().split(".")[-1]) >= 22000:
            so = f"Windows 11 ({platform.version()})"
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as clave:
            cpu = winreg.QueryValueEx(clave, "ProcessorNameString")[0].strip()
    version_ollama = requests.get(f"{OLLAMA}/api/version", timeout=10).json().get("version")
    return {
        "cpu": cpu,
        "nucleos_fisicos": psutil.cpu_count(logical=False),
        "hilos": psutil.cpu_count(logical=True),
        "ram_total_gb": round(psutil.virtual_memory().total / 1024**3, 1),
        "gpu": gpu,
        "so": so,
        "ollama": version_ollama,
    }


def descargar_modelos() -> None:
    """Libera todos los modelos cargados en Ollama para partir de un estado limpio."""
    cargados = requests.get(f"{OLLAMA}/api/ps", timeout=10).json().get("models", [])
    for m in cargados:
        requests.post(f"{OLLAMA}/api/generate", json={"model": m["name"], "keep_alive": 0}, timeout=60)
    time.sleep(2)


def generar(modelo: str, system: str, prompt: str, opciones: dict) -> tuple[dict, float, Muestreador]:
    """Ejecuta una generacion midiendo latencia de pared y picos de memoria."""
    muestreador = Muestreador()
    muestreador.start()
    inicio = time.perf_counter()
    r = requests.post(
        f"{OLLAMA}/api/generate",
        json={"model": modelo, "system": system, "prompt": prompt, "stream": False,
              "keep_alive": "10m", "options": opciones},
        timeout=900,
    )
    duracion = time.perf_counter() - inicio
    muestreador.detener()
    r.raise_for_status()
    return r.json(), duracion, muestreador


def medir(modelo: str, modo: str, repeticiones: int, system: str, prompt: str) -> dict:
    """Mide un modelo en un modo (gpu/cpu): carga en frio + N corridas de ~300 tokens."""
    opciones = {"num_predict": TOKENS_SALIDA, "temperature": 0.7}
    if modo == "cpu":
        opciones["num_gpu"] = 0  # Fuerza inferencia 100% en CPU

    descargar_modelos()
    ram_base = ram_ollama()
    vram_base = vram_usada_mib()

    # Carga en frio (el modelo no esta en memoria): se reporta aparte, no entra al promedio
    frio, dur_frio, _ = generar(modelo, system, prompt, {**opciones, "seed": 0})
    ps = next((m for m in requests.get(f"{OLLAMA}/api/ps", timeout=10).json().get("models", [])
               if m["name"] == modelo), {})

    corridas = []
    for i in range(1, repeticiones + 1):
        res, dur, mu = generar(modelo, system, prompt, {**opciones, "seed": i})
        tps = res["eval_count"] / (res["eval_duration"] / 1e9) if res.get("eval_duration") else 0.0
        corrida = {
            "corrida": i,
            "tokens_generados": res.get("eval_count", 0),
            "tokens_por_seg": round(tps, 2),
            "tokens_prompt": res.get("prompt_eval_count", 0),
            "prompt_eval_s": round(res.get("prompt_eval_duration", 0) / 1e9, 2),
            "tiempo_total_s": round(dur, 2),
            "pico_ram_ollama_mb": round(mu.pico_ram / 1024**2),
            "pico_vram_mib": mu.pico_vram_mib - vram_base if modo == "gpu" else 0,
        }
        corridas.append(corrida)
        print(f"  [{modelo} | {modo}] corrida {i}: {corrida['tokens_generados']} tok, "
              f"{corrida['tokens_por_seg']} tok/s, {corrida['tiempo_total_s']} s, "
              f"RAM {corrida['pico_ram_ollama_mb']} MB")

        salida = DIR_RESULTADOS / "salidas" / f"{modelo.replace(':', '_')}_{modo}_corrida{i}.md"
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(
            f"> Modelo: {modelo} | Modo: {modo} | Escenario: {ESCENARIO} + refuerzo | seed {i}\n"
            f"> {corrida['tokens_generados']} tokens a {corrida['tokens_por_seg']} tok/s "
            f"| {corrida['tiempo_total_s']} s\n\n{res.get('response', '').strip()}\n",
            encoding="utf-8",
        )

    def prom(campo: str) -> float:
        return round(sum(c[campo] for c in corridas) / len(corridas), 2)

    return {
        "modelo": modelo,
        "modo": modo,
        "cuantizacion": ps.get("details", {}).get("quantization_level"),
        "parametros": ps.get("details", {}).get("parameter_size"),
        "tamano_cargado_mb": round(ps.get("size", 0) / 1024**2),
        "tamano_en_vram_mb": round(ps.get("size_vram", 0) / 1024**2),
        "ram_ollama_base_mb": round(ram_base / 1024**2),
        "carga_en_frio_s": round(frio.get("load_duration", 0) / 1e9, 2),
        "tiempo_total_frio_s": round(dur_frio, 2),
        "promedio": {
            "tokens_por_seg": prom("tokens_por_seg"),
            "tiempo_total_s": prom("tiempo_total_s"),
            "tokens_generados": prom("tokens_generados"),
            "pico_ram_ollama_mb": prom("pico_ram_ollama_mb"),
            "pico_vram_mib": prom("pico_vram_mib"),
        },
        "corridas": corridas,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark local de SLMs (Sprint 4 SAVIO).")
    parser.add_argument("--modelos", nargs="+", default=MODELOS_DEFAULT)
    parser.add_argument("--modos", nargs="+", choices=["gpu", "cpu"], default=["gpu", "cpu"])
    parser.add_argument("--repeticiones", type=int, default=3)
    args = parser.parse_args()

    system = cargar_system_prompt()
    prompt = ensamblar_prompt(cargar_evento(ESCENARIO), refuerzo=True)

    resultados = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "hardware": info_hardware(),
        "configuracion": {"escenario": ESCENARIO, "refuerzo": True, "num_predict": TOKENS_SALIDA,
                          "temperature": 0.7, "repeticiones": args.repeticiones},
        "mediciones": [],
    }
    print(json.dumps(resultados["hardware"], indent=2, ensure_ascii=False))

    for modelo in args.modelos:
        for modo in args.modos:
            resultados["mediciones"].append(medir(modelo, modo, args.repeticiones, system, prompt))
    descargar_modelos()

    DIR_RESULTADOS.mkdir(parents=True, exist_ok=True)
    destino = DIR_RESULTADOS / "resultados.json"
    destino.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultados guardados en: {destino}")


if __name__ == "__main__":
    main()
