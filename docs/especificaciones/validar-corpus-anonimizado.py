"""Validador de privacidad del corpus psicometrico antes de Hugging Face (E3-03).

Uso (desde la raiz del repositorio):
    python docs/especificaciones/validar-corpus-anonimizado.py \
        --entrada datos/corpus/corpus.jsonl \
        --manifiesto datos/corpus/manifiesto.json

    python docs/especificaciones/validar-corpus-anonimizado.py \
        --entrada perfiles/reales/persona-1.json

Reglas:
    - Solo perfiles sinteticos con id SINT-### y origen "sintetico".
    - Sin claves de identificacion (nombre, correo, codigo, documento, usuario,
      estudiante_id, telefono, direccion, etc.).
    - Rangos e invariantes del Anexo A de la formulacion v6.
    - Sin PII en campos de texto; si hay `output`, exige el aviso no clinico.
    - Los mensajes no imprimen valores sensibles, solo el campo afectado.

Codigos de salida:
    0 = corpus valido (y manifiesto generado si se pidio)
    1 = hallazgos de privacidad, estructura o etica
    2 = entrada invalida, vacia o sin registros
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE / "poc_slm"))

from guardrail_etico import validar_salida_etica  # noqa: E402

# Rangos e invariantes compartidos con el contrato de E3-04: una sola fuente de
# verdad para corpus, perfiles reales y backend.
from contrato_bruto import (  # noqa: E402
    CAMPOS_PERMITIDOS,
    CAMPOS_RAIZ,
    RE_ID_SINTETICO,
    validar_chaside as _validar_chaside,
    validar_ils as _validar_ils,
    validar_perfil_bruto as _validar_perfil_bruto,
    validar_personalidad as _validar_personalidad,
)

CAMPOS_PROHIBIDOS = {
    "nombre",
    "nombres",
    "apellido",
    "apellidos",
    "correo",
    "email",
    "e_mail",
    "codigo",
    "codigo_estudiante",
    "documento",
    "cedula",
    "identificacion",
    "usuario",
    "username",
    "user",
    "estudiante_id",
    "student_id",
    "moodle_id",
    "telefono",
    "celular",
    "direccion",
    "fecha_nacimiento",
    "ip",
}

RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+", re.IGNORECASE)
RE_TELEFONO = re.compile(r"(?<!\d)(?:\+?57\s?)?(?:3\d{2}|60\d)[\s-]?\d{3}[\s-]?\d{4}(?!\d)")
RE_ARROBA = re.compile(r"(?<![\w.])@\w{2,}")
RE_CODIGO_UTB = re.compile(r"\bT\d{8}\b")
RE_NUMERO_LARGO = re.compile(r"(?<![\w/.])\d{6,}(?![\w/.])")


def cargar_lista_sensible(ruta):
    """Lee una lista local de nombres, usuarios o correos. No se versiona."""
    if ruta is None:
        return []
    if not ruta.exists():
        raise FileNotFoundError(f"no existe la lista sensible: {ruta}")
    lineas = ruta.read_text(encoding="utf-8-sig").splitlines()
    return [linea.strip() for linea in lineas if linea.strip() and not linea.strip().startswith("#")]


def cargar_registros(ruta):
    """Devuelve [(numero_de_linea, objeto)] de un .jsonl o de un .json."""
    if ruta.suffix.lower() == ".jsonl":
        registros = []
        with ruta.open("r", encoding="utf-8-sig") as archivo:
            for numero, linea in enumerate(archivo, start=1):
                texto = linea.strip()
                if not texto:
                    continue
                try:
                    objeto = json.loads(texto)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"{ruta.name}:{numero}: JSON invalido en la linea ({exc.msg})"
                    ) from None
                registros.append((numero, objeto))
        return registros

    if ruta.suffix.lower() == ".json":
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{ruta.name}: JSON invalido ({exc.msg})") from None
        if isinstance(datos, list):
            return [(numero + 1, objeto) for numero, objeto in enumerate(datos)]
        return [(1, datos)]

    raise ValueError(f"{ruta.name}: se esperaba un archivo .jsonl o .json")


def _prefijo(linea):
    return f"linea {linea}"


def _perfil_desde_input(entrada, prefijo):
    """Devuelve (perfil, errores) a partir de un input dict o de texto JSON."""
    if isinstance(entrada, dict):
        return entrada, []
    if isinstance(entrada, str):
        try:
            objeto = json.loads(entrada)
        except json.JSONDecodeError as exc:
            return None, [f"{prefijo}: no es JSON valido ({exc.msg})"]
        if isinstance(objeto, dict):
            return objeto, []
        return None, [f"{prefijo}: debe contener un objeto JSON"]
    return None, [f"{prefijo}: debe ser un objeto o un texto JSON"]


def validar_perfil(perfil, linea):
    """Valida un perfil bruto o un registro instruction/input/output."""
    prefijo = _prefijo(linea)
    if not isinstance(perfil, dict):
        return [f"{prefijo}: el registro debe ser un objeto JSON"]

    errores = []
    tiene_perfil = bool(set(perfil) & CAMPOS_RAIZ)
    sobran = sorted(set(perfil) - CAMPOS_PERMITIDOS)
    if sobran and not tiene_perfil:
        errores.append(f"{prefijo}: campos no permitidos en la raiz: {', '.join(sobran)}")

    if tiene_perfil:
        errores.extend(_validar_perfil_bruto(perfil, prefijo))

    if "input" in perfil:
        entrada, errores_entrada = _perfil_desde_input(perfil["input"], f"{prefijo}: input")
        errores.extend(errores_entrada)
        if entrada is not None:
            errores.extend(_validar_perfil_bruto(entrada, f"{prefijo}: input"))

    if not tiene_perfil and "input" not in perfil:
        errores.append(f"{prefijo}: faltan campos obligatorios: {', '.join(sorted(CAMPOS_RAIZ))}")

    if ("instruction" in perfil or "input" in perfil) and "output" not in perfil:
        errores.append(f"{prefijo}: falta output de la interpretacion")

    return errores


def _cadenas(objeto, prefijo=""):
    """Recorre el registro y devuelve (campo, texto) solo para valores string."""
    if isinstance(objeto, dict):
        for clave, valor in objeto.items():
            ruta = f"{prefijo}.{clave}" if prefijo else str(clave)
            yield from _cadenas(valor, ruta)
    elif isinstance(objeto, list):
        for indice, valor in enumerate(objeto):
            yield from _cadenas(valor, f"{prefijo}[{indice}]")
    elif isinstance(objeto, str):
        yield prefijo, objeto


def escanear_pii(perfil, linea, lista_sensible):
    """Busca identificadores en claves y valores. No imprime los valores."""
    prefijo = _prefijo(linea)
    hallazgos = set()

    if isinstance(perfil, dict):
        for clave in perfil:
            if str(clave).lower() in CAMPOS_PROHIBIDOS:
                hallazgos.add(f"{prefijo}: clave prohibida: {clave}")

    for campo, texto in _cadenas(perfil):
        if RE_EMAIL.search(texto):
            hallazgos.add(f"{prefijo}: posible correo en {campo}")
        if RE_TELEFONO.search(texto):
            hallazgos.add(f"{prefijo}: posible telefono en {campo}")
        if RE_ARROBA.search(texto):
            hallazgos.add(f"{prefijo}: posible usuario en {campo}")
        if RE_CODIGO_UTB.search(texto):
            hallazgos.add(f"{prefijo}: posible codigo estudiantil en {campo}")
        if RE_NUMERO_LARGO.search(texto):
            hallazgos.add(f"{prefijo}: posible identificador numerico en {campo}")

        bajo = texto.lower()
        for sensible in lista_sensible:
            if sensible and sensible.lower() in bajo:
                hallazgos.add(f"{prefijo}: dato de la lista sensible en {campo}")

    return sorted(hallazgos)


def validar_salida(perfil, linea):
    """Si el registro trae `output`, exige el guardrail etico."""
    if not isinstance(perfil, dict) or "output" not in perfil:
        return []

    prefijo = _prefijo(linea)
    salida = perfil.get("output")
    if not isinstance(salida, str):
        return [f"{prefijo}: output debe ser texto"]

    return [f"{prefijo}: output: {hallazgo}" for hallazgo in validar_salida_etica(salida)]


def validar_registro(perfil, linea, lista_sensible):
    """Ejecuta todas las comprobaciones de un registro."""
    return (
        validar_perfil(perfil, linea)
        + escanear_pii(perfil, linea, lista_sensible)
        + validar_salida(perfil, linea)
    )


def hash_archivo(ruta):
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def escribir_manifiesto(ruta, entradas, total_registros):
    """Guarda el manifiesto sin datos personales: hashes, conteos y fecha."""
    datos = {
        "validador": "validar-corpus-anonimizado.py",
        "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entradas": entradas,
        "registros": total_registros,
        "resultado": "ok",
    }
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _rutas_de_entrada(entrada):
    if entrada.is_file():
        return [entrada]
    if entrada.is_dir():
        return sorted(entrada.glob("*.jsonl"))
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description="Valida que el corpus sea sintetico y no tenga PII.")
    parser.add_argument("--entrada", required=True, type=Path, help="archivo .jsonl/.json o carpeta con .jsonl")
    parser.add_argument("--manifiesto", type=Path, help="ruta del manifiesto SHA-256 a generar")
    parser.add_argument("--lista-sensible", type=Path, help="lista local de nombres/usuarios/correos a buscar")
    args = parser.parse_args(argv)

    try:
        lista_sensible = cargar_lista_sensible(args.lista_sensible)
    except FileNotFoundError as exc:
        print(f"[FALLO] {exc}")
        return 2

    rutas = _rutas_de_entrada(args.entrada)
    if not rutas:
        print(f"[FALLO] no hay archivos .jsonl en {args.entrada}")
        return 2

    total_registros = 0
    total_errores = 0
    entradas = []

    for ruta in rutas:
        try:
            registros = cargar_registros(ruta)
        except ValueError as exc:
            print(f"[FALLO] {exc}")
            total_errores += 1
            continue

        if not registros:
            print(f"[FALLO] {ruta.name}: sin registros")
            total_errores += 1
            continue

        errores = []
        vistos = set()
        for linea, perfil in registros:
            errores.extend(validar_registro(perfil, linea, lista_sensible))
            if isinstance(perfil, dict):
                identificador = perfil.get("id")
                if isinstance(identificador, str) and RE_ID_SINTETICO.match(identificador):
                    if identificador in vistos:
                        errores.append(f"linea {linea}: id sintetico duplicado: {identificador}")
                    vistos.add(identificador)

        total_registros += len(registros)
        if errores:
            print(f"[FALLO] {ruta.name}: {len(errores)} hallazgo(s) en {len(registros)} registro(s)")
            for error in errores[:50]:
                print(f"  - {error}")
            if len(errores) > 50:
                print(f"  - ... {len(errores) - 50} hallazgo(s) mas")
            total_errores += len(errores)
            continue

        sha256 = hash_archivo(ruta)
        entradas.append({"archivo": ruta.name, "sha256": sha256, "registros": len(registros)})
        print(f"[OK] {ruta.name}: {len(registros)} registro(s) sinteticos, sin PII ni rangos invalidos")

    if total_registros == 0 or total_errores:
        print("RESULTADO: FALLO")
        return 1 if total_registros else 2

    if args.manifiesto:
        escribir_manifiesto(args.manifiesto, entradas, total_registros)
        print(f"[OK] manifiesto: {args.manifiesto}")

    print("RESULTADO: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
