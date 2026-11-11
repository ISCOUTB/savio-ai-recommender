"""Genera la fila de evidencia de extraccion de un perfil real (E3-05).

Comprueba que el perfil este ignorado por Git, lo valida contra el contrato
bruto y produce una fila lista para pegar en experimentos/bitacora.md.
No imprime puntajes: solo el identificador, el resultado del validador y el
SHA-256 del archivo, para demostrar que existe sin publicar el dato real.

Uso (desde la raiz del repositorio):
    python docs/especificaciones/evidencia-perfil.py --perfil perfiles/reales/persona-2-bruto.json
"""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[2]
VALIDADOR = RAIZ / "docs" / "especificaciones" / "validar-perfiles-brutos.py"


def resolver_perfil(valor):
    """Resuelve la ruta del perfil relativa a la raiz del repositorio."""
    ruta = Path(valor)
    if not ruta.is_absolute():
        ruta = RAIZ / ruta
    return ruta.resolve()


def esta_ignorado(ruta):
    """Devuelve la regla de .gitignore que cubre la ruta, o None si no esta ignorada."""
    try:
        proceso = subprocess.run(
            ["git", "check-ignore", "-v", str(ruta)],
            cwd=RAIZ,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None
    if proceso.returncode != 0:
        return None
    return proceso.stdout.strip()


def validar(ruta):
    """Corre el validador del contrato bruto y devuelve (ok, resumen)."""
    proceso = subprocess.run(
        [sys.executable, str(VALIDADOR), str(ruta)],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    lineas = [linea.strip() for linea in proceso.stdout.splitlines() if linea.strip()]
    resumen = next((linea for linea in reversed(lineas) if linea.startswith("RESULTADO:")), "")
    if not resumen:
        resumen = (proceso.stderr or proceso.stdout or "sin salida").strip().splitlines()[-1]
    return proceso.returncode == 0, resumen


def leer_cabecera(ruta):
    """Lee solo id y origen; nunca imprime puntajes."""
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, None, f"no se pudo leer el JSON: {error}"
    return datos.get("id"), datos.get("origen"), None


def sha256_archivo(ruta):
    """Calcula el SHA-256 del archivo en disco."""
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(65536), b""):
            digest.update(bloque)
    return digest.hexdigest()


def main(argv):
    parser = argparse.ArgumentParser(
        description="Genera la fila de bitacora que prueba la extraccion de un perfil real (E3-05)."
    )
    parser.add_argument("--perfil", required=True, help="ruta del perfil real en formato bruto")
    parser.add_argument(
        "--fecha",
        default=date.today().isoformat(),
        help="fecha de la fila en formato AAAA-MM-DD (por defecto: hoy)",
    )
    args = parser.parse_args(argv)

    ruta = resolver_perfil(args.perfil)
    if not ruta.is_file():
        print(f"ERROR: no existe el perfil {ruta}", file=sys.stderr)
        return 1

    regla = esta_ignorado(ruta)
    if regla is None:
        print(
            "ERROR: el perfil no esta ignorado por Git. Muevelo a perfiles/reales/ "
            "antes de generar evidencia; nunca se publica un perfil real.",
            file=sys.stderr,
        )
        return 1
    if "perfiles/reales" not in ruta.as_posix():
        print(
            "AVISO: el perfil esta ignorado, pero no vive en perfiles/reales/.",
            file=sys.stderr,
        )

    identificador, origen, error = leer_cabecera(ruta)
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if origen != "real":
        print(
            f"AVISO: el perfil declara origen '{origen}'. No sirve como evidencia de E3-05.",
            file=sys.stderr,
        )

    ok, resumen = validar(ruta)
    if not ok:
        print(f"ERROR: el validador rechazo el perfil: {resumen}", file=sys.stderr)
        return 1

    fila = (
        f"| {args.fecha} | {identificador} | Extraer perfil bruto real (E3-05) | "
        f"OK: validar-perfiles-brutos.py -> {resumen}; archivo local, no versionado "
        f"(regla {regla.split(':')[0]}:{regla.split(':')[1]}) | "
        f"SHA-256: {sha256_archivo(ruta)} |"
    )
    print(fila)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
