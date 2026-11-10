"""extraer_curso_moodle.py - Copia los archivos y textos incluidos del curso desde Moodle (CUR-04).

Lee datos/curso/inventario.json (generado por inventario_curso_moodle.py) y:
  1. Copia cada archivo con incluir=true desde /bitnami/moodledata/filedir/<xx>/<yy>/<hash>
     hacia datos/curso/crudos/<seccion>/<filename>, con docker cp.
  2. Verifica el SHA-1 de cada copia contra contenthash (Moodle nombra los archivos por SHA-1).
  3. Exporta a HTML el contenido de paginas (mod_page) y libros (mod_book) incluidos.

Escribe datos/curso/extraccion.json con el resultado por elemento.

Uso (desde la raiz del repo, con el Moodle Docker arriba):
    python scripts/extraer_curso_moodle.py
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
CURSO_DIR = RAIZ / "datos" / "curso"
INVENTARIO = CURSO_DIR / "inventario.json"
CRUDOS = CURSO_DIR / "crudos"
SALIDA = CURSO_DIR / "extraccion.json"
CONTENEDOR_DB = "moodle-db-1"
CONTENEDOR_MOODLE = "moodle-moodle-1"
FILEDIR = "/bitnami/moodledata/filedir"
BASE_DATOS = "moodle"


def sha1(ruta: Path) -> str:
    h = hashlib.sha1()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def consultar(sql: str) -> str:
    r = subprocess.run(
        ["docker", "exec", CONTENEDOR_DB, "mysql", "-uroot", "-proot", "-N", "-B", BASE_DATOS, "-e", sql],
        capture_output=True, text=True, encoding="utf-8", check=False)
    if r.returncode != 0:
        raise SystemExit(f"[ERROR] consulta fallida: {r.stderr.strip()}")
    return r.stdout.strip()


def copiar_archivo(archivo: dict) -> dict:
    h = archivo["contenthash"]
    origen = f"{CONTENEDOR_MOODLE}:{FILEDIR}/{h[0:2]}/{h[2:4]}/{h}"
    seccion = f"seccion-{archivo['seccion']:02d}"
    destino = CRUDOS / seccion / archivo["filename"]
    destino.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["docker", "cp", origen, str(destino)], capture_output=True, text=True, check=False)
    if r.returncode != 0:
        return {"filename": archivo["filename"], "estado": "error", "detalle": r.stderr.strip()}
    digest = sha1(destino)
    ok = digest == h
    return {"filename": archivo["filename"], "ruta": str(destino.relative_to(RAIZ)),
            "bytes": destino.stat().st_size, "sha1_ok": ok,
            "estado": "ok" if ok else "hash_no_coincide"}


def exportar_texto(actividad: dict) -> dict:
    tipo, inst, seccion = actividad["tipo"], actividad["instancia"], f"seccion-{actividad['seccion']:02d}"
    if tipo == "page":
        filas = consultar(f"SELECT HEX(content) FROM mdl_page WHERE id = {inst}")
    else:
        filas = consultar(
            "SELECT HEX(CONCAT('<h2>', title, '</h2>', content)) FROM mdl_book_chapters "
            f"WHERE bookid = {inst} AND hidden = 0 ORDER BY pagenum")
    lineas = [linea for linea in filas.splitlines() if linea]
    if not lineas:
        return {"tipo": tipo, "instancia": inst, "estado": "vacio"}
    html = "\n".join(bytes.fromhex(linea).decode("utf-8") for linea in lineas)
    destino = CRUDOS / "texto" / f"{seccion}-{tipo}-{inst}.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    return {"tipo": tipo, "instancia": inst, "ruta": str(destino.relative_to(RAIZ)),
            "bytes": destino.stat().st_size, "estado": "ok"}


def main() -> None:
    inventario = json.loads(INVENTARIO.read_text(encoding="utf-8"))
    archivos = [copiar_archivo(a) for a in inventario["archivos"] if a["incluir"]]
    textos = [exportar_texto(a) for a in inventario["actividades"]
              if a["incluir"] and a["tipo"] in {"page", "book"}]

    resultado = {"archivos": archivos, "textos": textos}
    SALIDA.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")

    ok_archivos = sum(a["estado"] == "ok" for a in archivos)
    ok_textos = sum(t["estado"] == "ok" for t in textos)
    print(f"Archivos: {ok_archivos}/{len(archivos)} copiados con SHA-1 verificado")
    print(f"Textos (pagina/libro): {ok_textos}/{len(textos)} exportados")
    for a in archivos:
        if a["estado"] != "ok":
            print(f"  [FALLO] {a['filename']}: {a['estado']}")
    print(f"  escrito: {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
