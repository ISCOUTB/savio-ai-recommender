"""limpiar_corpus_curso.py - Limpia y fragmenta el Markdown del curso (CUR-06).

Lee datos/curso/markdown/**/*.md y escribe:
  datos/curso/corpus_curso.jsonl      {id, seccion, archivo, texto}, un fragmento por linea
  datos/curso/reporte_limpieza.json   conteos por archivo, duplicados y alertas de privacidad

Pasos:
  1. Normaliza espacios y saltos de linea. No borra lineas: todo el texto del curso es contenido.
     Reemplaza correos por [correo] (dato personal de terceros).
  2. Deduplica fragmentos por SHA-256.
  3. Parte en fragmentos de 800 a 1200 caracteres, con solape de 120 caracteres.
  4. Descarta fragmentos de menos de 200 caracteres.
  5. Cuenta correos y usuarios de Moodle sobre el texto original (no deben existir en el corpus).

Uso (desde la raiz del repo):
    python scripts/limpiar_corpus_curso.py
"""

import hashlib
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
CURSO_DIR = RAIZ / "datos" / "curso"
MARKDOWN = CURSO_DIR / "markdown"
CORPUS = CURSO_DIR / "corpus_curso.jsonl"
REPORTE = CURSO_DIR / "reporte_limpieza.json"

MIN_FRAGMENTO = 200
MIN_CHUNK, MAX_CHUNK, SOLAPE = 800, 1200, 120
PATRON_CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PATRON_USUARIO = re.compile(r"\bpersona-\d\b", re.IGNORECASE)


def normalizar(texto: str) -> str:
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    lineas = [re.sub(r"[ \t]+", " ", linea).strip() for linea in texto.split("\n")]
    return "\n".join(lineas)


def partir_parrafos(texto: str) -> list[str]:
    bloques = []
    for p in re.split(r"\n\s*\n", texto):
        p = p.strip()
        while len(p) > MAX_CHUNK:
            corte = p.rfind(" ", 0, MAX_CHUNK)
            corte = corte if corte > MIN_CHUNK else MAX_CHUNK
            bloques.append(p[:corte].strip())
            p = p[corte:].strip()
        if p:
            bloques.append(p)
    return bloques


def fragmentar(texto: str) -> list[str]:
    fragmentos, actual = [], ""
    for p in partir_parrafos(texto):
        if not actual:
            actual = p
        elif len(actual) + 2 + len(p) <= MAX_CHUNK:
            actual = f"{actual}\n\n{p}"
        else:
            fragmentos.append(actual)
            cola = actual[-SOLAPE:]
            cola = cola[cola.find(" ") + 1:] if " " in cola else cola
            candidato = f"{cola}\n\n{p}"
            actual = candidato if len(candidato) <= MAX_CHUNK else p
    if actual:
        fragmentos.append(actual)
    return fragmentos


def main() -> None:
    archivos = sorted(MARKDOWN.rglob("*.md"))
    vistos: set[str] = set()
    registros, por_archivo = [], {}
    duplicados_bloque = 0
    alertas = {"correos_reemplazados": 0, "usuarios_moodle": 0}

    for ruta in archivos:
        bruto = ruta.read_text(encoding="utf-8")
        alertas["correos_reemplazados"] += len(PATRON_CORREO.findall(bruto))
        alertas["usuarios_moodle"] += len(PATRON_USUARIO.findall(bruto))
        texto = PATRON_CORREO.sub("[correo]", normalizar(bruto))
        texto = re.sub(r"\n{3,}", "\n\n", texto).strip()
        seccion = ruta.parent.name
        fragmentos_ok, descartados, caracteres = 0, 0, 0
        for fragmento in fragmentar(texto):
            if len(fragmento) < MIN_FRAGMENTO:
                descartados += 1
                continue
            firma = hashlib.sha256(re.sub(r"\s+", " ", fragmento).strip().lower().encode("utf-8")).hexdigest()
            if firma in vistos:
                duplicados_bloque += 1
                continue
            vistos.add(firma)
            registros.append({"id": f"CUR-{len(registros) + 1:04d}", "seccion": seccion,
                              "archivo": ruta.name, "texto": fragmento})
            fragmentos_ok += 1
            caracteres += len(fragmento)
        por_archivo[str(ruta.relative_to(RAIZ))] = {"fragmentos": fragmentos_ok,
                                                    "descartados_menor_200": descartados,
                                                    "caracteres": caracteres}

    with CORPUS.open("w", encoding="utf-8") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    reporte = {
        "archivos_entrada": len(archivos),
        "fragmentos_finales": len(registros),
        "caracteres_finales": sum(len(r["texto"]) for r in registros),
        "duplicados_eliminados": duplicados_bloque,
        "alertas_privacidad": alertas,
        "por_archivo": por_archivo,
    }
    REPORTE.write_text(json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Fragmentos: {len(registros)} | caracteres: {reporte['caracteres_finales']}")
    print(f"Duplicados eliminados: {duplicados_bloque}")
    print(f"Privacidad: correos reemplazados={alertas['correos_reemplazados']} usuarios Moodle={alertas['usuarios_moodle']}")
    print(f"  escrito: {CORPUS.relative_to(RAIZ)} y {REPORTE.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
