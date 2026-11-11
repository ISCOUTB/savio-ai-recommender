"""convertir_curso_markdown.py - Convierte el contenido extraido del curso a Markdown (CUR-05).

Toma los archivos de datos/curso/crudos/ y los textos exportados de paginas y libros
(datos/curso/crudos/texto/), y escribe datos/curso/markdown/<seccion>/<archivo>.md con
markitdown (licencia MIT). Los ZIP se descomprimen en un directorio temporal y solo
se convierten sus .md.

Video y PNG no se convierten: se registran como excluidos en el reporte.

Escribe datos/curso/reporte_conversion.json.

Uso (desde la raiz del repo):
    python scripts/convertir_curso_markdown.py
"""

import json
import sys
import re
import tempfile
import zipfile
from pathlib import Path

from markitdown import MarkItDown

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
CURSO_DIR = RAIZ / "datos" / "curso"
CRUDOS = CURSO_DIR / "crudos"
MARKDOWN = CURSO_DIR / "markdown"
REPORTE = CURSO_DIR / "reporte_conversion.json"
EXTENSIONES = {".pdf", ".html", ".docx"}
PATRON_CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

convertidor = MarkItDown()


def convertir(origen: Path, destino: Path, etiqueta: str | None = None) -> dict:
    fuente = etiqueta or str(origen.relative_to(RAIZ))
    try:
        texto = convertidor.convert(str(origen)).text_content or ""
    except Exception as e:
        return {"fuente": fuente, "estado": "error", "detalle": str(e)[:200]}
    if not texto.strip():
        estado = "requiere_ocr" if origen.suffix.lower() == ".pdf" else "vacio"
        return {"fuente": fuente, "estado": estado}
    texto = PATRON_CORREO.sub("[correo]", texto)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    return {"fuente": fuente, "salida": str(destino.relative_to(RAIZ)),
            "caracteres": len(texto), "estado": "ok"}


def main() -> None:
    resultados = []
    for origen in sorted(CRUDOS.rglob("*")):
        if not origen.is_file() or "texto" in origen.relative_to(CRUDOS).parts:
            continue
        seccion = origen.parent.name
        if origen.suffix.lower() == ".zip":
            with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(origen) as z:
                z.extractall(tmp)
                for md in sorted(Path(tmp).rglob("*.md")):
                    destino = MARKDOWN / seccion / f"{origen.stem}-{md.name}"
                    etiqueta = f"{origen.relative_to(RAIZ)}!/{md.relative_to(tmp)}"
                    resultados.append(convertir(md, destino, etiqueta))
        elif origen.suffix.lower() in EXTENSIONES:
            destino = MARKDOWN / seccion / f"{origen.name}.md"
            resultados.append(convertir(origen, destino))
        else:
            resultados.append({"fuente": str(origen.relative_to(RAIZ)), "estado": "excluido",
                               "detalle": "formato no convertible en este flujo"})

    for texto in sorted((CRUDOS / "texto").glob("*.html")):
        destino = MARKDOWN / "texto" / f"{texto.stem}.md"
        resultados.append(convertir(texto, destino))

    REPORTE.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")

    ok = [r for r in resultados if r["estado"] == "ok"]
    malos = [r for r in resultados if r["estado"] in {"error", "vacio", "requiere_ocr"}]
    excluidos = [r for r in resultados if r["estado"] == "excluido"]
    print(f"Convertidos: {len(ok)} | excluidos: {len(excluidos)} | pendientes o con error: {len(malos)}")
    print(f"  caracteres totales: {sum(r['caracteres'] for r in ok)}")
    for r in malos:
        print(f"  [FALLO] {r['fuente']}: {r['estado']} {r.get('detalle', '')}")
    print(f"  escrito: {REPORTE.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
