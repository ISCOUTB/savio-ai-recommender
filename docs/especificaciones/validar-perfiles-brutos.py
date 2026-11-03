"""Validador del contrato de puntajes brutos (E3-04, issue #50).

Uso (desde la raiz del repositorio):

    # Valida los tres ejemplos versionados
    python docs/especificaciones/validar-perfiles-brutos.py

    # Valida un perfil o una carpeta
    python docs/especificaciones/validar-perfiles-brutos.py perfiles/reales/persona-1.json
    python docs/especificaciones/validar-perfiles-brutos.py perfiles/

Reglas (las mismas que usa el corpus de E3-06, en `contrato_bruto.py`):
    - Sin escala 1.0-5.0: todo puntaje es entero nativo.
    - Sin indices compuestos (`autonomia` y demas claves de Entrega 2).
    - CHASIDE: interes 0-10, aptitud 0-4, total 0-14 y total = interes + aptitud.
    - Felder-Silverman: 8 polos 0-11 con cada par sumando 11.
    - Personalidad: 8 polos 0-9.
    - Diferencial opcional: impar entre -11 y 11, igual a polo izquierdo - derecho.

Codigos de salida:
    0 = todos los perfiles cumplen el contrato
    1 = al menos un perfil incumple el contrato
    2 = entrada invalida (no hay archivos, carpeta sin JSON o JSON malformado)
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE / "docs" / "especificaciones"))

from contrato_bruto import (  # noqa: E402
    CLAVES_ENTREGA_2,
    validar_perfil_bruto,
)

CAMPOS_EXTRA = ("diferencial", "fecha_aplicacion")
ORIGENES = {"real", "sintetico"}
RE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,39}$")
RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def cargar_json(ruta):
    """Devuelve el objeto JSON de la ruta o lanza ValueError."""
    try:
        return json.loads(ruta.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{ruta.name}: JSON invalido ({exc.msg})") from None


def rutas_de_entrada(argumentos):
    """Expande archivos y carpetas; sin argumentos usa los ejemplos versionados."""
    if not argumentos:
        return sorted((BASE / "perfiles" / "brutos").glob("*.json"))

    rutas = []
    for argumento in argumentos:
        ruta = Path(argumento)
        if not ruta.is_absolute():
            ruta = BASE / ruta
        if ruta.is_dir():
            rutas.extend(sorted(ruta.glob("*.json")))
        else:
            rutas.append(ruta)
    return rutas


def claves_entrega_2(objeto, ruta_actual="perfil"):
    """Busca claves del formato antiguo (1.0-5.0, autonomia) en cualquier nivel."""
    hallazgos = []
    if isinstance(objeto, dict):
        for clave, valor in objeto.items():
            aqui = f"{ruta_actual}.{clave}"
            if clave in CLAVES_ENTREGA_2:
                hallazgos.append(f"{aqui} es del formato de Entrega 2; usa puntajes brutos")
            hallazgos.extend(claves_entrega_2(valor, aqui))
    elif isinstance(objeto, list):
        for indice, valor in enumerate(objeto):
            hallazgos.extend(claves_entrega_2(valor, f"{ruta_actual}[{indice}]"))
    return hallazgos


def valores_decimales(objeto, ruta_actual="perfil"):
    """Busca numeros no enteros: delatan una escala reescalada."""
    hallazgos = []
    if isinstance(objeto, dict):
        for clave, valor in objeto.items():
            hallazgos.extend(valores_decimales(valor, f"{ruta_actual}.{clave}"))
    elif isinstance(objeto, list):
        for indice, valor in enumerate(objeto):
            hallazgos.extend(valores_decimales(valor, f"{ruta_actual}[{indice}]"))
    elif isinstance(objeto, float):
        hallazgos.append(f"{ruta_actual} es decimal; el contrato exige enteros nativos")
    return hallazgos


def validar_perfil(perfil, nombre):
    """Devuelve la lista de hallazgos del perfil bruto."""
    errores = validar_perfil_bruto(
        perfil,
        nombre,
        exigir_sintetico=False,
        campos_extra=CAMPOS_EXTRA,
    )
    if not isinstance(perfil, dict):
        return errores

    identificador = perfil.get("id")
    if isinstance(identificador, str) and not RE_ID.match(identificador):
        errores.append(
            f"{nombre}: id invalido; usa solo letras, digitos, punto, guion o guion bajo"
        )

    origen = perfil.get("origen")
    if origen not in ORIGENES:
        errores.append(f"{nombre}: origen debe ser 'real' o 'sintetico'")

    fecha = perfil.get("fecha_aplicacion")
    if fecha is not None:
        valida = isinstance(fecha, str) and RE_FECHA.match(fecha)
        if valida:
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
            except ValueError:
                valida = False
        if not valida:
            errores.append(f"{nombre}: fecha_aplicacion debe ser una fecha AAAA-MM-DD")

    errores.extend(f"{nombre}: {mensaje}" for mensaje in claves_entrega_2(perfil))
    errores.extend(f"{nombre}: {mensaje}" for mensaje in valores_decimales(perfil))
    return errores


def main():
    parser = argparse.ArgumentParser(
        description="Valida perfiles psicometricos con puntajes brutos (E3-04)."
    )
    parser.add_argument(
        "rutas",
        nargs="*",
        help="archivos o carpetas a validar (por defecto, los ejemplos de perfiles/)",
    )
    args = parser.parse_args()

    rutas = rutas_de_entrada(args.rutas)
    if not rutas:
        print("[FALLO] no se encontro ningun perfil para validar")
        print("RESULTADO: FALLO")
        return 2

    total = 0
    total_errores = 0

    for ruta in rutas:
        if not ruta.exists():
            print(f"[FALLO] {ruta.name}: no existe")
            total_errores += 1
            continue

        try:
            perfil = cargar_json(ruta)
        except ValueError as exc:
            print(f"[FALLO] {exc}")
            total_errores += 1
            continue

        total += 1
        errores = validar_perfil(perfil, ruta.name)
        if errores:
            print(f"[FALLO] {ruta.name}: {len(errores)} hallazgo(s)")
            for error in errores[:50]:
                print(f"  - {error}")
            total_errores += len(errores)
            continue

        print(f"[OK] {ruta.name}: perfil bruto valido")

    if total == 0 or total_errores:
        print("RESULTADO: FALLO")
        return 1 if total else 2

    print(f"RESULTADO: OK ({total} perfil(es))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
