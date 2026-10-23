"""validador de documentacion del repositorio.

Comprueba que la documentacion narrativa este ordenada y sea navegable:

  ERROR (corta con codigo 1)
    - enlaces relativos que no resuelven
    - archivo sin encabezado H1
    - sprint sin la linea **Estado:**

  AVISO (no corta, salvo --strict)
    - caracteres no-ASCII fuera de la evidencia
    - documento narrativo sin ningun enlace entrante
    - pares de documentos con mas del 40% de lineas repetidas

Quedan fuera del analisis las carpetas de evidencia medida, las salidas de
modelo y el codigo de skills de terceros.

Uso (desde la raiz del repositorio):
    python docs/validar-docs.py
    python docs/validar-docs.py --strict
"""

import re
import sys
from itertools import combinations
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent

# Carpetas y archivos que no son documentacion narrativa del proyecto.
EXCLUIR_PREFIJOS = (
    "skills/",
    "benchmarks/resultados/",
    "prompts/salidas-respaldo/",
    "poc_slm/evidencias/",
    "docs/presentacion/demo-",
    ".git/",
    ".venv/",
    "node_modules/",
)
EXCLUIR_ARCHIVOS = {"AGENTS.md"}

RE_ENLACE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)")
RE_ESTADO = re.compile(r"^\*\*Estado:\*\*", re.MULTILINE)
UMBRAL_DUPLICADO = 0.40
MIN_LINEAS_COMUNES = 20


def listar_markdown():
    """Lista los .md del repositorio, excluyendo evidencia y codigo de terceros."""
    rutas = sorted(p.relative_to(RAIZ).as_posix() for p in RAIZ.rglob("*.md"))
    return [rel for rel in rutas if not es_evidencia(rel)]


def es_evidencia(rel):
    """True si el archivo es evidencia, codigo de terceros o configuracion del agente."""
    return rel in EXCLUIR_ARCHIVOS or rel.startswith(EXCLUIR_PREFIJOS)


def leer(rel):
    return (RAIZ / rel).read_text(encoding="utf-8", errors="replace")


def resolver(rel, destino):
    """Resuelve un enlace relativo y devuelve su ruta normalizada o None."""
    destino = destino.split("#")[0].split("?")[0]
    if not destino or destino.startswith(("http://", "https://", "mailto:")):
        return None
    base = (RAIZ / rel).parent
    return (base / destino).resolve()


def normalizar_enlace(ruta):
    try:
        return ruta.relative_to(RAIZ.resolve()).as_posix()
    except ValueError:
        return None


def analizar():
    archivos = sorted(listar_markdown())
    errores = []
    avisos = []
    entrantes = {rel: set() for rel in archivos}

    for rel in archivos:
        texto = leer(rel)

        if not re.search(r"^#\s+\S", texto, re.MULTILINE):
            errores.append(f"{rel}: falta el encabezado H1")

        if "/sprint-" in rel and not RE_ESTADO.search(texto):
            errores.append(f"{rel}: sprint sin la linea **Estado:**")

        for destino in RE_ENLACE.findall(texto):
            ruta = resolver(rel, destino)
            if ruta is None:
                continue
            if not ruta.exists():
                errores.append(f"{rel}: enlace roto -> {destino}")
                continue
            objetivo = normalizar_enlace(ruta)
            if objetivo in entrantes and objetivo != rel:
                entrantes[objetivo].add(rel)

        no_ascii = sorted({c for c in texto if ord(c) > 127})
        if no_ascii:
            avisos.append(f"{rel}: {len(no_ascii)} caracter(es) no-ASCII ({''.join(no_ascii)[:12]})")

    # Alcanzabilidad desde los indices.
    raices = {"README.md", "docs/README.md"} & set(archivos)
    alcanzables = set(raices)
    pendientes = list(raices)
    while pendientes:
        actual = pendientes.pop()
        for destino in RE_ENLACE.findall(leer(actual)):
            ruta = resolver(actual, destino)
            if ruta is None:
                continue
            objetivo = normalizar_enlace(ruta)
            if objetivo in entrantes and objetivo not in alcanzables:
                alcanzables.add(objetivo)
                pendientes.append(objetivo)

    for rel in archivos:
        if rel in raices or rel.endswith("README.md"):
            continue
        if rel not in alcanzables:
            avisos.append(f"{rel}: sin enlace entrante desde un indice")

    # Duplicados por lineas repetidas.
    firmas = {}
    for rel in archivos:
        lineas = {
            linea.strip().lower()
            for linea in leer(rel).splitlines()
            if len(linea.strip()) > 25
        }
        firmas[rel] = lineas
    for a, b in combinations(archivos, 2):
        sa, sb = firmas[a], firmas[b]
        if min(len(sa), len(sb)) < MIN_LINEAS_COMUNES:
            continue
        comunes = len(sa & sb)
        proporcion = comunes / min(len(sa), len(sb))
        if comunes >= MIN_LINEAS_COMUNES and proporcion >= UMBRAL_DUPLICADO:
            avisos.append(f"{a} <-> {b}: {proporcion:.0%} de lineas repetidas")

    return archivos, errores, avisos


def main(argv):
    estricto = "--strict" in argv
    archivos, errores, avisos = analizar()

    print(f"Documentacion analizada: {len(archivos)} archivos narrativos")
    print(f"Errores: {len(errores)} | Avisos: {len(avisos)}")
    print()

    if errores:
        print("ERRORES")
        for error in errores:
            print(f"  - {error}")
        print()

    if avisos:
        print("AVISOS")
        for aviso in avisos:
            print(f"  - {aviso}")
        print()

    if errores or (estricto and avisos):
        print("RESULTADO: FALLO")
        return 1
    print("RESULTADO: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
