"""inventario_curso_moodle.py - Inventario de archivos y actividades de un curso de Moodle (CUR-02).

Lee mdl_course_modules, mdl_course_sections y mdl_files del contenedor moodle-db-1 con
`docker exec` y solo ejecuta SELECT. Escribe datos/curso/inventario.json.

Uso (desde la raiz del repo, con el Moodle Docker arriba):
    python scripts/inventario_curso_moodle.py --curso 3
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "datos" / "curso" / "inventario.json"
CONTENEDOR_DB = "moodle-db-1"
BASE_DATOS = "moodle"

TIPOS_CONTENIDO = {"resource", "url", "page", "book"}
MIMES_CONVERTIBLES = {
    "application/pdf",
    "text/html",
    "application/zip",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}


def decidir_actividad(tipo: str) -> tuple[bool, str, bool]:
    if tipo in TIPOS_CONTENIDO:
        return True, "actividad de contenido", False
    if tipo == "label":
        return False, "etiqueta: pendiente de revision manual del texto", True
    if tipo in {"assign", "forum", "feedback"}:
        return False, "actividad de estudiantes (datos personales)", False
    return False, "tipo no considerado para el corpus", False


def decidir_archivo(archivo: dict) -> tuple[bool, str]:
    if archivo["mimetype"].startswith("video/"):
        return False, "video: no convertible en este flujo"
    if archivo["mimetype"].startswith("image/"):
        return False, "imagen: no convertible en este flujo"
    if archivo["tipo_actividad"] is None:
        return False, "archivo de nivel curso sin actividad asociada"
    if archivo["tipo_actividad"] not in TIPOS_CONTENIDO:
        return False, f"archivo de actividad {archivo['tipo_actividad']}"
    if archivo["mimetype"] not in MIMES_CONVERTIBLES:
        return False, f"formato {archivo['mimetype']} no previsto"
    return True, "documento de contenido convertible"


def consultar(sql: str) -> list[list[str]]:
    r = subprocess.run(
        ["docker", "exec", CONTENEDOR_DB, "mysql", "-uroot", "-proot", "-N", "-B", BASE_DATOS, "-e", sql],
        capture_output=True, text=True, encoding="utf-8", check=False)
    if r.returncode != 0:
        raise SystemExit(f"[ERROR] consulta fallida: {r.stderr.strip()}")
    return [linea.split("\t") for linea in r.stdout.splitlines() if linea]


def inventariar(curso: int) -> dict:
    modulos = consultar(
        "SELECT cm.id, cs.section, m.name, cm.instance FROM mdl_course_modules cm "
        "JOIN mdl_modules m ON m.id = cm.module "
        "JOIN mdl_course_sections cs ON cs.id = cm.section "
        f"WHERE cm.course = {curso} ORDER BY cs.section, cm.id")
    actividades = []
    for c, s, t, i in modulos:
        incluir, motivo, revision = decidir_actividad(t)
        actividades.append({"cmid": int(c), "seccion": int(s), "tipo": t, "instancia": int(i),
                            "incluir": incluir, "motivo": motivo, "revision_manual": revision})

    archivos_sql = consultar(
        "SELECT f.filename, f.contenthash, f.mimetype, f.filesize, c.contextlevel, c.instanceid, f.component "
        "FROM mdl_files f JOIN mdl_context c ON c.id = f.contextid "
        f"WHERE f.filename <> '.' AND ((c.contextlevel = 50 AND c.instanceid = {curso}) "
        f"OR (c.contextlevel = 70 AND c.instanceid IN (SELECT id FROM mdl_course_modules WHERE course = {curso}))) "
        "ORDER BY f.filesize DESC")
    tipo_por_cmid = {a["cmid"]: a for a in actividades}
    archivos = []
    for nombre, hash_, mime, bytes_, nivel, inst, comp in archivos_sql:
        ubicacion = tipo_por_cmid.get(int(inst)) if int(nivel) == 70 else None
        registro = {
            "filename": nombre,
            "contenthash": hash_,
            "mimetype": mime,
            "bytes": int(bytes_),
            "componente": comp,
            "nivel_contexto": "curso" if int(nivel) == 50 else "actividad",
            "cmid": int(inst) if int(nivel) == 70 else None,
            "seccion": ubicacion["seccion"] if ubicacion else None,
            "tipo_actividad": ubicacion["tipo"] if ubicacion else None,
        }
        registro["incluir"], registro["motivo"] = decidir_archivo(registro)
        archivos.append(registro)

    return {
        "curso": curso,
        "resumen": {
            "actividades_por_tipo": dict(Counter(a["tipo"] for a in actividades)),
            "actividades_incluidas": sum(a["incluir"] for a in actividades),
            "archivos": len(archivos),
            "archivos_incluidos": sum(a["incluir"] for a in archivos),
            "bytes_total": sum(a["bytes"] for a in archivos),
            "bytes_incluidos": sum(a["bytes"] for a in archivos if a["incluir"]),
        },
        "actividades": actividades,
        "archivos": archivos,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventario de un curso de Moodle (solo lectura).")
    parser.add_argument("--curso", type=int, required=True, help="id del curso en mdl_course (ej. 3)")
    args = parser.parse_args()

    inventario = inventariar(args.curso)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(inventario, indent=2, ensure_ascii=False), encoding="utf-8")
    r = inventario["resumen"]
    print(f"Curso {args.curso}: {len(inventario['actividades'])} actividades, {r['archivos']} archivos, "
          f"{r['bytes_total'] / 1024**2:.1f} MB")
    print(f"  incluidos: {r['actividades_incluidas']} actividades, {r['archivos_incluidos']} archivos, "
          f"{r['bytes_incluidos'] / 1024**2:.1f} MB")
    print(f"  actividades por tipo: {r['actividades_por_tipo']}")
    print(f"  escrito: {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
