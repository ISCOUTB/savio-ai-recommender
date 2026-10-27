"""probar_notebook_local.py - Prueba de punta a punta del notebook de ajuste en CPU (E3-08, #44).

Ejecuta, en un directorio de trabajo aparte, las celdas del notebook
entrenamiento/ajuste_qlora_gguf.ipynb que no estan marcadas "solo-colab" (modo
prueba: pocos pasos, sin 4 bits), y luego reemplaza los pasos de Colab por sus
equivalentes locales:
  1. Convierte el modelo fusionado a GGUF F16 con convert_hf_to_gguf.py de llama.cpp.
  2. Cuantiza a Q4_K_M con `ollama create -q q4_K_M` (no requiere compilar llama.cpp).
  3. Ejecuta el modelo en Ollama con num_gpu 0 y verifica que no use VRAM.

No es el entrenamiento real: solo comprueba que el flujo funciona antes de correrlo en Colab.

Uso (con un entorno que tenga torch, transformers, peft, trl, datasets y gguf):
    python entrenamiento/probar_notebook_local.py --trabajo <dir> --llama-cpp <dir con llama.cpp clonado>
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parent.parent
NOTEBOOK = RAIZ / "entrenamiento" / "ajuste_qlora_gguf.ipynb"
DATOS = RAIZ / "entrenamiento" / "datos_prueba.jsonl"
OLLAMA = "http://localhost:11434"


def ejecutar_celdas(trabajo: Path) -> dict:
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    os.chdir(trabajo)
    ns = {}
    for i, celda in enumerate(nb["cells"]):
        if celda["cell_type"] != "code" or "solo-colab" in celda["metadata"].get("tags", []):
            continue
        fuente = "".join(celda["source"])
        print(f"\n===== celda {i} =====")
        exec(compile(fuente, f"celda_{i}", "exec"), ns)
        if "BASE_MODEL =" in fuente:          # celda de configuracion: apuntar a los datos de prueba
            ns["DATOS"] = str(DATOS)
            assert ns["MODO_PRUEBA"], "la prueba local exige MODO_PRUEBA = True"
    return ns


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trabajo", type=Path, required=True)
    parser.add_argument("--llama-cpp", type=Path, required=True)
    args = parser.parse_args()
    trabajo = args.trabajo.resolve()
    trabajo.mkdir(parents=True, exist_ok=True)

    ns = ejecutar_celdas(trabajo)
    nombre = ns["NOMBRE"]
    art = trabajo / "artefactos"

    print("\n===== GGUF F16 =====")
    f16 = art / f"{nombre}-f16.gguf"
    subprocess.run([sys.executable, str(args.llama_cpp.resolve() / "convert_hf_to_gguf.py"),
                    str(art / f"{nombre}-fusionado"), "--outtype", "f16", "--outfile", str(f16)], check=True)
    print(f"{f16.name}: {f16.stat().st_size / 1024**2:.0f} MB")

    print("\n===== Q4_K_M con Ollama =====")
    modelfile = (art / "Modelfile").read_text().replace(f"./{nombre}-q4_k_m.gguf", f"./{f16.name}")
    (art / "Modelfile.local").write_text(modelfile)
    etiqueta = f"{nombre}-prueba"
    subprocess.run(["ollama", "create", etiqueta, "-q", "q4_K_M", "-f", "Modelfile.local"], cwd=art, check=True)

    print("\n===== Inferencia solo en CPU =====")
    muestra = json.loads(DATOS.read_text(encoding="utf-8").splitlines()[0])
    inicio = time.perf_counter()
    r = requests.post(f"{OLLAMA}/api/generate", json={
        "model": etiqueta, "system": muestra["instruction"], "prompt": muestra["input"], "stream": False,
        "options": {"num_predict": 150}}, timeout=600).json()
    pared = time.perf_counter() - inicio
    ps = next(m for m in requests.get(f"{OLLAMA}/api/ps", timeout=10).json()["models"] if m["name"].startswith(etiqueta))
    resumen = {"modelo": etiqueta, "cuantizacion": ps.get("details", {}).get("quantization_level"),
               "tamano_mb": round(ps["size"] / 1024**2), "vram_mb": round(ps["size_vram"] / 1024**2),
               "tokens": r.get("eval_count"), "tokens_por_seg": round(r["eval_count"] / (r["eval_duration"] / 1e9), 1),
               "latencia_s": round(pared, 1), "perdidas": ns["perdidas"]}
    print(json.dumps(resumen, indent=1, ensure_ascii=False))
    print("\nInicio de la respuesta:\n", r.get("response", "")[:400])
    assert resumen["vram_mb"] == 0, "el modelo uso VRAM"
    requests.post(f"{OLLAMA}/api/generate", json={"model": etiqueta, "keep_alive": 0}, timeout=60)
    (trabajo / "resumen_prueba.json").write_text(json.dumps(resumen, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\nPRUEBA DE PUNTA A PUNTA: OK")


if __name__ == "__main__":
    main()
