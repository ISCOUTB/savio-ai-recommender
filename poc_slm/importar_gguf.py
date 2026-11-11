"""importar_gguf.py - Importa un GGUF ajustado en Ollama (E3-07).

Convierte un archivo `.gguf` en un modelo de Ollama con nombre estable
(`savio-e3-<hash>`), plantilla ChatML y parametros de inferencia fijos. El
nombre depende del SHA-256, asi que el mismo archivo siempre produce el mismo
modelo y la bitacora puede citarlo sin ambiguedad.

Uso (desde la raiz del repositorio):
    python poc_slm/importar_gguf.py --gguf C:\\modelos\\savio-e3-q4km.gguf
    python poc_slm/importar_gguf.py --gguf C:\\modelos\\savio-e3-q4km.gguf --dry-run
"""

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_MODELFILES = RAIZ / "modelos"
PREFIJO_MODELO = "savio-e3"
TEMPERATURA = 0.2
NUM_PREDICT = 1200
STOP = "<|im_end|>"

# Plantilla ChatML de Qwen 2.5. Se fija en el Modelfile para que la inferencia
# no dependa de la plantilla que traiga (o no traiga) el GGUF convertido.
PLANTILLA_CHATML = (
    'TEMPLATE """{{ if .System }}<|im_start|>system\n'
    "{{ .System }}<|im_end|>\n"
    "{{ end }}{{ if .Prompt }}<|im_start|>user\n"
    "{{ .Prompt }}<|im_end|>\n"
    "{{ end }}<|im_start|>assistant\n"
    '"""'
)


def sha256_archivo(ruta):
    """Calcula el SHA-256 del archivo en disco."""
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(65536), b""):
            digest.update(bloque)
    return digest.hexdigest()


def nombre_modelo(digest):
    """Deriva un nombre de modelo estable y valido para Ollama desde el hash."""
    return f"{PREFIJO_MODELO}-{digest[:8]}"


def construir_modelfile(ruta, temperatura=TEMPERATURA, num_predict=NUM_PREDICT):
    """Arma el contenido del Modelfile para un GGUF dado (sin escribir nada)."""
    ruta_abs = Path(ruta).resolve().as_posix()
    origen = f'"{ruta_abs}"' if " " in ruta_abs else ruta_abs
    return (
        f"FROM {origen}\n"
        f"{PLANTILLA_CHATML}\n"
        f"PARAMETER temperature {temperatura}\n"
        f"PARAMETER num_predict {num_predict}\n"
        f'PARAMETER stop "{STOP}"\n'
    )


def validar_gguf(ruta):
    """Comprueba que la ruta sea un GGUF existente y no vacio."""
    ruta = Path(ruta)
    if not ruta.is_file():
        raise SystemExit(f"[FALLO] no existe el GGUF: {ruta}")
    if ruta.suffix.lower() != ".gguf":
        raise SystemExit(f"[FALLO] el archivo no tiene extension .gguf: {ruta.name}")
    if ruta.stat().st_size == 0:
        raise SystemExit(f"[FALLO] el GGUF esta vacio: {ruta.name}")
    return ruta.resolve()


def modelos_instalados():
    """Devuelve el conjunto de modelos que reporta `ollama list`."""
    try:
        proceso = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        raise SystemExit(
            "[FALLO] no se encontro el comando 'ollama'. Instala Ollama o agrega su ruta al PATH."
        ) from None
    if proceso.returncode != 0:
        raise SystemExit(
            "[FALLO] 'ollama list' fallo. Verifica que el servicio este corriendo con 'ollama serve'."
        )
    lineas = proceso.stdout.splitlines()[1:]
    return {linea.split()[0] for linea in lineas if linea.split()}


def escribir_modelfile(nombre, contenido, carpeta=CARPETA_MODELFILES):
    """Guarda el Modelfile en modelos/ y devuelve su ruta."""
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{nombre}.Modelfile"
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def importar(ruta, nombre=None, forzar=False, dry_run=False):
    """Importa el GGUF en Ollama y devuelve los metadatos de la importacion.

    Con dry_run solo valida el archivo y calcula hash, nombre y Modelfile; no
    escribe archivos ni invoca a Ollama.
    """
    ruta = validar_gguf(ruta)
    digest = sha256_archivo(ruta)
    nombre = nombre or nombre_modelo(digest)
    modelfile = construir_modelfile(ruta)
    info = {
        "ruta": str(ruta),
        "sha256": digest,
        "nombre": nombre,
        "modelfile": modelfile,
        "importado": False,
    }
    if dry_run:
        return info

    if not forzar and nombre in modelos_instalados():
        print(f"[OK] el modelo {nombre} ya existe en Ollama; no se reimporta.")
        return info

    ruta_modelfile = escribir_modelfile(nombre, modelfile)
    print(f"Modelfile: {ruta_modelfile}")
    print(f"Importando {ruta.name} como {nombre} (puede tardar unos minutos)...")
    try:
        proceso = subprocess.run(
            ["ollama", "create", nombre, "-f", str(ruta_modelfile)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        raise SystemExit(
            "[FALLO] no se encontro el comando 'ollama'. Instala Ollama o agrega su ruta al PATH."
        ) from None
    if proceso.returncode != 0:
        detalle = (proceso.stderr or proceso.stdout or "sin salida").strip()
        raise SystemExit(f"[FALLO] 'ollama create' fallo:\n{detalle}")

    info["importado"] = True
    return info


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Importa un GGUF ajustado en Ollama con nombre estable y ChatML (E3-07)."
    )
    parser.add_argument("--gguf", required=True, type=Path, help="ruta del archivo .gguf ajustado")
    parser.add_argument("--nombre", help="nombre de modelo en Ollama (por defecto: savio-e3-<hash>)")
    parser.add_argument(
        "--forzar",
        action="store_true",
        help="reimporta aunque el modelo ya exista en Ollama",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="valida el GGUF y muestra el Modelfile sin importar nada",
    )
    args = parser.parse_args(argv)

    info = importar(args.gguf, nombre=args.nombre, forzar=args.forzar, dry_run=args.dry_run)
    if args.dry_run:
        print(info["modelfile"])
    print(f"Modelo   : {info['nombre']}")
    print(f"GGUF     : {info['ruta']}")
    print(f"SHA-256  : {info['sha256']}")
    print(f"Estado   : {'importado' if info['importado'] else 'no importado'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
