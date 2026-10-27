"""Validador de perfiles de estudiante contra el schema oficial + reglas semanticas.

Uso (desde la raiz del repo):
    python docs/especificaciones/validar-perfiles.py

Requiere: jsonschema (incluido en requirements.txt).
"""

import json
import sys
from pathlib import Path

import jsonschema

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent.parent.parent
SCHEMA = BASE / "docs/especificaciones/perfil-estudiante.schema.json"
PERFILES_DIR = BASE / "perfiles"

schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
jsonschema.Draft7Validator.check_schema(schema)
validator = jsonschema.Draft7Validator(schema)

# Valores alcanzables por formula (redondeados a 1 decimal).
# Se calculan en vez de escribirlos a mano para que no vuelvan a desincronizarse
# de las formulas de escala-canonica.md.

# Estilos: 11 items repartidos entre los 2 polos (el par suma 11).
# La diferencia es siempre impar (-11..11) -> 3 + 2*d/11.
FELDER_VALORES = {round(3 + 2 * d / 11, 1) for d in range(-11, 12, 2)}

# Personalidad: 9 items por polo, cada polo se puntua 0-9 de forma independiente.
# La diferencia es cualquier entero (-9..9) -> 3 + 2*d/9.
PERSONALIDAD_3RASGOS = {round(3 + 2 * d / 9, 1) for d in range(-9, 10)}

# autonomia: suma de dos diferencias, cada una -9..9 -> suma -18..18 -> 3 + s/9.
PERSONALIDAD_AUTONOMIA = {round(3 + s / 9, 1) for s in range(-18, 19)}

# CHASIDE: total 0-14 por area -> 1 + 4*t/14.
CHASIDE_VALORES = {round(1 + 4 * t / 14, 1) for t in range(0, 15)}

# Mapeo de clave de puntaje a polo izquierdo/derecho
EJES_FELDER = {
    "activo_reflexivo": ("activo", "reflexivo"),
    "sensorial_intuitivo": ("sensorial", "intuitivo"),
    "visual_verbal": ("visual", "verbal"),
    "secuencial_global": ("secuencial", "global"),
}

ORDEN_PREFERENCIAS = ["activo", "reflexivo", "sensorial", "intuitivo", "visual", "verbal", "secuencial", "global"]


def preferencias_esperadas(puntajes):
    """Calcula las preferencias segun la regla: <=2.1 o >=3.9."""
    resultado = []
    for clave, (izq, der) in EJES_FELDER.items():
        v = puntajes.get(clave)
        if v is None:
            continue
        if v <= 2.1:
            resultado.append(izq)
        elif v >= 3.9:
            resultado.append(der)
    # Ordenar segun orden canonico
    return sorted(resultado, key=lambda p: ORDEN_PREFERENCIAS.index(p) if p in ORDEN_PREFERENCIAS else 99)


def validar_semantico(doc):
    """Reglas que el schema no puede expresar. Devuelve lista de strings (errores)."""
    errores = []

    # 1. Estilos: modelo felder_silverman -> puntajes en valores alcanzables
    ea = doc.get("estilos_aprendizaje", {})
    if ea.get("modelo") == "felder_silverman":
        puntajes = ea.get("puntajes", {})
        for clave, valor in puntajes.items():
            if round(valor, 1) not in FELDER_VALORES:
                errores.append(f"estilos_aprendizaje.puntajes.{clave}: {valor} no es un valor alcanzable (validos: {sorted(FELDER_VALORES)})")

        # 3. Preferencias coinciden con regla
        pref_esperadas = preferencias_esperadas(puntajes)
        pref_declaradas = ea.get("preferencias", [])
        if pref_esperadas != pref_declaradas:
            errores.append(f"estilos_aprendizaje.preferencias: declaradas {pref_declaradas}, esperadas {pref_esperadas}")

    # 4. Personalidad: valores alcanzables
    pers = doc.get("personalidad", {})
    rasgos = pers.get("rasgos", {})
    for clave, valor in rasgos.items():
        if clave == "autonomia":
            validos = PERSONALIDAD_AUTONOMIA
        else:
            validos = PERSONALIDAD_3RASGOS
        if round(valor, 1) not in validos:
            errores.append(f"personalidad.rasgos.{clave}: {valor} no es un valor alcanzable (validos: {sorted(validos)})")

    # 5. CHASIDE: valores alcanzables
    ch = doc.get("chaside", {})
    areas = ch.get("areas", {})
    for clave, valor in areas.items():
        if round(valor, 1) not in CHASIDE_VALORES:
            errores.append(f"chaside.areas.{clave}: {valor} no es un valor alcanzable (validos: {sorted(CHASIDE_VALORES)})")

    return errores


def validar(archivo):
    try:
        doc = json.loads(archivo.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return f"  {archivo.name}: JSON invalido -> {e}"

    # Validacion schema
    errs = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    if errs:
        lineas = [f"  {archivo.name}: INVALIDO (schema)"]
        for e in errs:
            ruta = " -> ".join(str(p) for p in e.path) or "(raiz)"
            lineas.append(f"    {ruta}: {e.message}")
        return "\n".join(lineas)

    # Validacion semantica
    sem = validar_semantico(doc)
    if sem:
        lineas = [f"  {archivo.name}: INVALIDO (semantica)"]
        for e in sem:
            lineas.append(f"    {e}")
        return "\n".join(lineas)

    return f"  {archivo.name}: OK"


def main():
    # Uso: validar-perfiles.py [archivo-o-carpeta]
    # Sin argumento valida perfiles/*.json (incluye subcarpetas como perfiles/reales/).
    objetivo = Path(sys.argv[1]) if len(sys.argv) > 1 else PERFILES_DIR
    if len(sys.argv) > 1 and not objetivo.is_absolute():
        objetivo = BASE / objetivo

    if not objetivo.exists():
        print(f"ERROR: no existe {objetivo}")
        return 1

    if objetivo.is_dir():
        archivos = sorted(objetivo.rglob("*.json"))
        origen = objetivo
    else:
        archivos = [objetivo]
        origen = objetivo.parent

    if not archivos:
        print(f"No hay perfiles JSON en {origen}")
        return 0
    print(f"Validando {len(archivos)} archivo(s) contra {SCHEMA.name} + reglas semanticas...")
    ok = 0
    for a in archivos:
        res = validar(a)
        print(res)
        if res.endswith("OK"):
            ok += 1
    print(f"\nResumen: {ok}/{len(archivos)} validos")
    return 0 if ok == len(archivos) else 1


if __name__ == "__main__":
    sys.exit(main())
