"""feedback_tracker.py - Circuito de retroalimentacion y metricas KPI (E2-11).

Registra eventos de feedback estudiantil sobre las recomendaciones semanales
generadas por el SLM (E2-10) en formato JSON Lines (.jsonl), validando cada
registro contra docs/especificaciones/feedback.schema.json, y calcula los
indicadores clave de desempeno pedagogico (Tasa de Acierto, Tasa de Descache
y promedio Likert).

Uso (desde la raiz del repositorio):
    # 1. Simular lote de eventos de prueba y mostrar reporte de KPIs
    python poc_slm/feedback_tracker.py --simular

    # 2. Registrar un evento de feedback manual
    python poc_slm/feedback_tracker.py \
        --recomendacion-id rec-demo-002-s1-b0557548 \
        --estudiante-id demo-002 \
        --semana 1 \
        --recurso-id tde-s1-B \
        --util --likert 5 \
        --comentario "La guia de lectura con ensayos anotados se ajusto a mi ritmo."

    # 3. Registrar feedback a partir del JSON generado por prompt_builder.py
    python poc_slm/feedback_tracker.py \
        --desde-recomendacion salidas/recomendacion_demo.json \
        --no-util --likert 2 \
        --comentario "El taller de 60 minutos fue demasiado extenso para esta semana."

    # 4. Consultar metricas acumuladas del archivo .jsonl
    python poc_slm/feedback_tracker.py --resumen
    python poc_slm/feedback_tracker.py --resumen --json

Dependencias: jsonschema (incluida en requirements.txt).
"""

import argparse
from datetime import datetime, timezone
import json
import re
import sys
from pathlib import Path

import jsonschema

# Forzar salida en UTF-8 para evitar caracteres corruptos en Windows / PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
SCHEMA_FEEDBACK = RAIZ / "docs" / "especificaciones" / "feedback.schema.json"
ARCHIVO_DEFAULT = RAIZ / "poc_slm" / "feedback" / "eventos_feedback.jsonl"

RE_ISO_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


# ---------------------------------------------------------------------------
# Carga y validacion contra schema
# ---------------------------------------------------------------------------

def cargar_schema(schema_path: Path = SCHEMA_FEEDBACK) -> dict:
    """Carga y verifica la integridad estructural de feedback.schema.json."""
    if not schema_path.exists():
        raise FileNotFoundError(f"No existe el schema de feedback: {schema_path}")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft7Validator.check_schema(schema)
    return schema


def derivar_resultado(util: bool) -> str:
    """Traduce la escala binaria util (true/false) al resultado canonico."""
    return "acierto" if util else "descache"


def timestamp_utc() -> str:
    """Devuelve la fecha y hora actual en formato ISO 8601 UTC."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validar_evento_feedback(evento: dict, schema: dict | None = None) -> list[str]:
    """Valida un evento de feedback contra feedback.schema.json y reglas semanticas.

    Devuelve una lista de errores (vacia si el evento es valido).
    """
    if schema is None:
        schema = cargar_schema()

    validador = jsonschema.Draft7Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )
    errores = []
    for err in sorted(validador.iter_errors(evento), key=lambda e: list(e.path)):
        ruta = " -> ".join(str(p) for p in err.path) or "(raiz)"
        errores.append(f"{ruta}: {err.message}")

    if not isinstance(evento, dict):
        return errores

    # Reglas semanticas adicionales
    util = evento.get("util")
    resultado = evento.get("resultado")
    if isinstance(util, bool) and resultado in ("acierto", "descache"):
        esperado = derivar_resultado(util)
        if resultado != esperado:
            errores.append(
                f"resultado incoherente: para util={util} se esperaba {esperado!r}, llego {resultado!r}"
            )

    fecha = evento.get("fecha")
    if isinstance(fecha, str) and not RE_ISO_DATETIME.match(fecha):
        errores.append(
            f"fecha: {fecha!r} no cumple el formato ISO 8601 date-time (ej. 2026-10-22T12:00:00Z)"
        )

    for campo in ("recomendacion_id", "estudiante_id", "recurso_id"):
        valor = evento.get(campo)
        if isinstance(valor, str) and not valor.strip():
            errores.append(f"{campo}: no puede ser una cadena vacia o de solo espacios")

    return errores


# ---------------------------------------------------------------------------
# Construccion y persistencia en JSON Lines (.jsonl)
# ---------------------------------------------------------------------------

def construir_evento_feedback(
    recomendacion_id: str,
    estudiante_id: str,
    semana: int,
    recurso_id: str,
    util: bool,
    likert: int | None = None,
    comentario: str | None = None,
    resultado: str | None = None,
    fecha: str | None = None,
) -> dict:
    """Construye un diccionario de feedback alineado con feedback.schema.json."""
    evento = {
        "recomendacion_id": recomendacion_id,
        "estudiante_id": estudiante_id,
        "semana": semana,
        "recurso_id": recurso_id,
        "util": util,
        "resultado": resultado if resultado is not None else derivar_resultado(util),
        "fecha": fecha if fecha is not None else timestamp_utc(),
    }
    if likert is not None:
        evento["likert"] = likert
    if comentario is not None and comentario.strip():
        evento["comentario"] = comentario.strip()
    return evento


def construir_desde_recomendacion(
    recomendacion_doc: dict,
    util: bool,
    likert: int | None = None,
    comentario: str | None = None,
    fecha: str | None = None,
) -> dict:
    """Construye un evento de feedback a partir del JSON generado por prompt_builder.py."""
    recurso_id = recomendacion_doc.get("recurso_id") or recomendacion_doc.get("recurso_elegido")
    if not recurso_id:
        raise ValueError(
            "El JSON de recomendacion no contiene 'recurso_elegido' ni 'recurso_id'."
        )
    for clave in ("recomendacion_id", "estudiante_id", "semana"):
        if clave not in recomendacion_doc:
            raise ValueError(f"El JSON de recomendacion no contiene el campo obligatorio {clave!r}.")

    return construir_evento_feedback(
        recomendacion_id=str(recomendacion_doc["recomendacion_id"]),
        estudiante_id=str(recomendacion_doc["estudiante_id"]),
        semana=int(recomendacion_doc["semana"]),
        recurso_id=str(recurso_id),
        util=util,
        likert=likert,
        comentario=comentario,
        fecha=fecha,
    )


def registrar_feedback(
    evento: dict,
    ruta_jsonl: Path = ARCHIVO_DEFAULT,
    schema: dict | None = None,
) -> Path:
    """Valida el evento y lo agrega como una nueva linea en el archivo .jsonl."""
    errores = validar_evento_feedback(evento, schema=schema)
    if errores:
        detalle = "; ".join(errores)
        raise ValueError(f"Evento de feedback invalido: {detalle}")

    ruta_jsonl.parent.mkdir(parents=True, exist_ok=True)
    linea = json.dumps(evento, ensure_ascii=False) + "\n"
    with ruta_jsonl.open("a", encoding="utf-8") as f:
        f.write(linea)
    return ruta_jsonl


def cargar_eventos_feedback(
    ruta_jsonl: Path = ARCHIVO_DEFAULT,
    schema: dict | None = None,
) -> list[dict]:
    """Lee y valida todos los eventos almacenados en un archivo .jsonl."""
    if not ruta_jsonl.exists():
        raise FileNotFoundError(f"No existe el archivo de feedback: {ruta_jsonl}")
    if schema is None:
        schema = cargar_schema()

    eventos: list[dict] = []
    with ruta_jsonl.open("r", encoding="utf-8") as f:
        for num_linea, linea in enumerate(f, start=1):
            contenido = linea.strip()
            if not contenido:
                continue
            try:
                evento = json.loads(contenido)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON invalido en {ruta_jsonl.name}:{num_linea}: {e}") from e
            errores = validar_evento_feedback(evento, schema=schema)
            if errores:
                raise ValueError(
                    f"Evento invalido en {ruta_jsonl.name}:{num_linea}: {'; '.join(errores)}"
                )
            eventos.append(evento)
    return eventos


# ---------------------------------------------------------------------------
# Formulacion de metricas (KPIs)
# ---------------------------------------------------------------------------

def calcular_metricas(eventos: list[dict]) -> dict:
    """Calcula los KPIs de desempeno del recomendador sobre los eventos evaluados.

    Formulas:
      - Tasa de Acierto (%)  = (Recomendaciones utiles / Total evaluadas) * 100
      - Tasa de Descache (%) = (Recomendaciones no utiles / Total evaluadas) * 100
    """
    total = len(eventos)
    utiles = sum(1 for e in eventos if e.get("util") is True)
    no_utiles = sum(1 for e in eventos if e.get("util") is False)

    if total > 0:
        tasa_acierto = round((utiles / total) * 100.0, 2)
        tasa_descache = round((no_utiles / total) * 100.0, 2)
    else:
        tasa_acierto = 0.0
        tasa_descache = 0.0

    valores_likert = [
        int(e["likert"])
        for e in eventos
        if isinstance(e.get("likert"), int) and not isinstance(e.get("likert"), bool)
    ]
    likert_promedio = (
        round(sum(valores_likert) / len(valores_likert), 2) if valores_likert else None
    )

    por_recurso: dict[str, dict] = {}
    for recurso_id in sorted({str(e.get("recurso_id", "")) for e in eventos if e.get("recurso_id")}):
        sub = [e for e in eventos if e.get("recurso_id") == recurso_id]
        sub_total = len(sub)
        sub_aciertos = sum(1 for e in sub if e.get("util") is True)
        sub_descaches = sub_total - sub_aciertos
        sub_likerts = [
            int(e["likert"])
            for e in sub
            if isinstance(e.get("likert"), int) and not isinstance(e.get("likert"), bool)
        ]
        por_recurso[recurso_id] = {
            "evaluadas": sub_total,
            "aciertos": sub_aciertos,
            "descaches": sub_descaches,
            "tasa_acierto_pct": round((sub_aciertos / sub_total) * 100.0, 2) if sub_total else 0.0,
            "tasa_descache_pct": round((sub_descaches / sub_total) * 100.0, 2) if sub_total else 0.0,
            "likert_promedio": round(sum(sub_likerts) / len(sub_likerts), 2) if sub_likerts else None,
        }

    # Clasificacion para retroalimentacion del fine-tuning (Dataset B)
    candidatos_dataset_b_positivos = sum(
        1
        for e in eventos
        if e.get("util") is True and (e.get("likert") is None or e.get("likert", 0) >= 4)
    )
    casos_revisar_descache = sum(
        1 for e in eventos if e.get("util") is False or (isinstance(e.get("likert"), int) and e["likert"] <= 2)
    )

    return {
        "total_evaluadas": total,
        "utiles": utiles,
        "no_utiles": no_utiles,
        "tasa_acierto_pct": tasa_acierto,
        "tasa_descache_pct": tasa_descache,
        "likert_evaluadas": len(valores_likert),
        "likert_promedio": likert_promedio,
        "por_recurso": por_recurso,
        "retroalimentacion_finetuning": {
            "candidatos_positivos_dataset_b": candidatos_dataset_b_positivos,
            "casos_revision_humana": casos_revisar_descache,
        },
    }


# ---------------------------------------------------------------------------
# Lote de eventos simulados (alineados con las corridas de E2-10)
# ---------------------------------------------------------------------------

def eventos_simulados_base() -> list[dict]:
    """Devuelve 5 eventos simulados ligados a los perfiles de prueba de E2-10."""
    return [
        construir_evento_feedback(
            recomendacion_id="rec-demo-002-s1-b0557548",
            estudiante_id="demo-002",
            semana=1,
            recurso_id="tde-s1-B",
            util=True,
            likert=5,
            comentario="Los dos ensayos anotados y el glosario encajaron con mi preferencia reflexiva y verbal.",
            fecha="2026-10-22T10:15:00Z",
        ),
        construir_evento_feedback(
            recomendacion_id="rec-demo-003-s1-263363f9",
            estudiante_id="demo-003",
            semana=1,
            recurso_id="tde-s1-C",
            util=True,
            likert=5,
            comentario="El taller guiado de 5 pasos me permitio construir la tesis practicando.",
            fecha="2026-10-22T10:20:00Z",
        ),
        construir_evento_feedback(
            recomendacion_id="rec-demo-001-s1-53ef6765",
            estudiante_id="demo-001",
            semana=1,
            recurso_id="tde-s1-C",
            util=False,
            likert=2,
            comentario="Preferia un esquema visual corto como el mapa interactivo antes de pasar a un taller de 60 minutos.",
            fecha="2026-10-22T10:25:00Z",
        ),
        construir_evento_feedback(
            recomendacion_id="rec-demo-002-s1-4f81a2c1",
            estudiante_id="demo-002",
            semana=1,
            recurso_id="tde-s1-B",
            util=True,
            likert=4,
            comentario="Con el orden permutado mantuvo la guia de lectura analitica; muy util para comparar posturas.",
            fecha="2026-10-22T10:30:00Z",
        ),
        construir_evento_feedback(
            recomendacion_id="rec-sim-vis-001-s1-9a12bc34",
            estudiante_id="sim-vis-001",
            semana=1,
            recurso_id="tde-s1-A",
            util=True,
            likert=5,
            comentario="El mapa interactivo de 15 minutos sintetizo el flujo de tesis y contraargumento con claridad.",
            fecha="2026-10-22T10:35:00Z",
        ),
    ]


# ---------------------------------------------------------------------------
# Salida por consola y CLI
# ---------------------------------------------------------------------------

def imprimir_reporte(ruta_jsonl: Path, eventos: list[dict], metricas: dict) -> None:
    """Imprime en consola el resumen de eventos registrados y KPIs calculados."""
    print("=" * 72)
    print("SAVIO - Feedback Loop y Metricas de Recomendacion (E2-11)")
    print("=" * 72)
    print(f"Archivo JSONL        : {ruta_jsonl}")
    print(f"Total evaluadas (N)  : {metricas['total_evaluadas']}")
    print(f"Recomendaciones utiles   : {metricas['utiles']}")
    print(f"Recomendaciones no utiles: {metricas['no_utiles']}")
    print("-" * 72)
    print(f"Tasa de Acierto      : {metricas['tasa_acierto_pct']:.2f}%")
    print(f"Tasa de Descache     : {metricas['tasa_descache_pct']:.2f}%")
    if metricas["likert_promedio"] is not None:
        print(
            f"Likert promedio (1-5): {metricas['likert_promedio']:.2f} "
            f"(sobre {metricas['likert_evaluadas']} respuestas)"
        )
    else:
        print("Likert promedio (1-5): N/A (sin respuestas en escala Likert)")
    print("-" * 72)
    print("Desglose por recurso:")
    for recurso_id, info in metricas["por_recurso"].items():
        likert_txt = f"{info['likert_promedio']:.2f}" if info["likert_promedio"] is not None else "N/A"
        print(
            f"  - {recurso_id}: {info['evaluadas']} eval. | "
            f"acierto={info['tasa_acierto_pct']:.2f}% ({info['aciertos']}) | "
            f"descache={info['tasa_descache_pct']:.2f}% ({info['descaches']}) | "
            f"likert={likert_txt}"
        )
    print("-" * 72)
    ft = metricas["retroalimentacion_finetuning"]
    print(
        f"Insumo Fine-Tuning (Dataset B): "
        f"{ft['candidatos_positivos_dataset_b']} candidatos positivos (gold) | "
        f"{ft['casos_revision_humana']} casos para curacion humana"
    )
    print("=" * 72)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Modulo de persistencia y metricas de feedback para el recomendador SAVIO (E2-11)."
    )
    parser.add_argument(
        "--archivo",
        default=str(ARCHIVO_DEFAULT),
        help=f"Ruta del archivo .jsonl de feedback (default: {ARCHIVO_DEFAULT.relative_to(RAIZ)}).",
    )
    parser.add_argument(
        "--simular",
        action="store_true",
        help="Escribe el lote de eventos simulados de verificacion y calcula los KPIs.",
    )
    parser.add_argument(
        "--resumen",
        action="store_true",
        help="Lee el archivo .jsonl existente y muestra las metricas KPI.",
    )
    parser.add_argument(
        "--desde-recomendacion",
        default=None,
        help="Ruta a un archivo JSON generado por prompt_builder.py --guardar-json.",
    )
    parser.add_argument("--recomendacion-id", default=None, help="Identificador de la recomendacion.")
    parser.add_argument("--estudiante-id", default=None, help="Identificador del estudiante.")
    parser.add_argument("--semana", type=int, default=None, help="Numero de semana academica (>= 1).")
    parser.add_argument("--recurso-id", default=None, help="Identificador del recurso evaluado (ej. tde-s1-B).")

    grupo_util = parser.add_mutually_exclusive_group()
    grupo_util.add_argument(
        "--util",
        dest="util",
        action="store_true",
        default=None,
        help="Marca la recomendacion como util (util=true -> resultado='acierto').",
    )
    grupo_util.add_argument(
        "--no-util",
        dest="util",
        action="store_false",
        help="Marca la recomendacion como no util (util=false -> resultado='descache').",
    )

    parser.add_argument(
        "--likert",
        type=int,
        default=None,
        help="Calificacion opcional en escala Likert de 1 a 5 estrellas.",
    )
    parser.add_argument(
        "--comentario",
        default=None,
        help="Comentario abierto opcional del estudiante (max. 500 caracteres).",
    )
    parser.add_argument(
        "--fecha",
        default=None,
        help="Fecha ISO 8601 opcional (default: hora UTC actual).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprime el resultado o reporte en formato JSON por stdout.",
    )

    args = parser.parse_args()
    ruta_jsonl = Path(args.archivo)
    if not ruta_jsonl.is_absolute():
        ruta_jsonl = RAIZ / ruta_jsonl

    try:
        schema = cargar_schema()
    except Exception as e:
        print(f"[ERROR] Fallo al validar feedback.schema.json: {e}", file=sys.stderr)
        return 1

    # Modo 1: Simulacion de eventos base
    if args.simular:
        ruta_jsonl.parent.mkdir(parents=True, exist_ok=True)
        if ruta_jsonl.exists():
            ruta_jsonl.write_text("", encoding="utf-8")
        for ev in eventos_simulados_base():
            registrar_feedback(ev, ruta_jsonl=ruta_jsonl, schema=schema)
        eventos = cargar_eventos_feedback(ruta_jsonl=ruta_jsonl, schema=schema)
        metricas = calcular_metricas(eventos)
        if args.json:
            print(json.dumps({"archivo": str(ruta_jsonl), "metricas": metricas, "eventos": eventos}, ensure_ascii=False, indent=2))
        else:
            imprimir_reporte(ruta_jsonl, eventos, metricas)
        return 0

    # Modo 2: Registrar un nuevo evento (desde JSON de recomendacion o por flags)
    quiere_registrar = (
        args.desde_recomendacion is not None
        or args.recomendacion_id is not None
        or args.util is not None
    )
    if quiere_registrar:
        if args.util is None:
            print("[ERROR] Debes indicar --util o --no-util para registrar un evento.", file=sys.stderr)
            return 1
        try:
            if args.desde_recomendacion:
                ruta_rec = Path(args.desde_recomendacion)
                if not ruta_rec.is_absolute():
                    ruta_rec = RAIZ / ruta_rec
                doc_rec = json.loads(ruta_rec.read_text(encoding="utf-8"))
                evento = construir_desde_recomendacion(
                    doc_rec,
                    util=args.util,
                    likert=args.likert,
                    comentario=args.comentario,
                    fecha=args.fecha,
                )
            else:
                faltantes = [
                    nombre
                    for nombre, val in (
                        ("--recomendacion-id", args.recomendacion_id),
                        ("--estudiante-id", args.estudiante_id),
                        ("--semana", args.semana),
                        ("--recurso-id", args.recurso_id),
                    )
                    if val is None
                ]
                if faltantes:
                    print(
                        f"[ERROR] Faltan argumentos obligatorios para registrar: {', '.join(faltantes)}",
                        file=sys.stderr,
                    )
                    return 1
                evento = construir_evento_feedback(
                    recomendacion_id=args.recomendacion_id,
                    estudiante_id=args.estudiante_id,
                    semana=args.semana,
                    recurso_id=args.recurso_id,
                    util=args.util,
                    likert=args.likert,
                    comentario=args.comentario,
                    fecha=args.fecha,
                )
            registrar_feedback(evento, ruta_jsonl=ruta_jsonl, schema=schema)
        except Exception as e:
            print(f"[ERROR] No se pudo registrar el feedback: {e}", file=sys.stderr)
            return 1

        if args.json and not args.resumen:
            print(json.dumps(evento, ensure_ascii=False, indent=2))
        elif not args.resumen:
            print(f"Feedback registrado en {ruta_jsonl}: {evento['recomendacion_id']} -> {evento['resultado']}")

        if not args.resumen:
            return 0

    # Modo 3: Resumen de metricas sobre el archivo .jsonl
    if args.resumen or not quiere_registrar:
        if not ruta_jsonl.exists():
            print(
                f"[ERROR] No existe el archivo {ruta_jsonl}. Usa --simular o registra un evento primero.",
                file=sys.stderr,
            )
            return 1
        try:
            eventos = cargar_eventos_feedback(ruta_jsonl=ruta_jsonl, schema=schema)
        except Exception as e:
            print(f"[ERROR] Error al leer {ruta_jsonl}: {e}", file=sys.stderr)
            return 1
        metricas = calcular_metricas(eventos)
        if args.json:
            print(json.dumps({"archivo": str(ruta_jsonl), "metricas": metricas}, ensure_ascii=False, indent=2))
        else:
            imprimir_reporte(ruta_jsonl, eventos, metricas)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
