"""feedback_tracker.py — Registro de feedback y KPIs del recomendador (E2-11).

Registra eventos de retroalimentacion del estudiante sobre una recomendacion
semanal A/B/C en formato JSON Lines (una linea JSON por evento), validados
contra docs/especificaciones/feedback.schema.json, y calcula los KPIs base:

    Tasa de Acierto  = (recomendaciones utiles    / total evaluadas) * 100
    Tasa de Descache = (recomendaciones no utiles / total evaluadas) * 100

Uso (desde la raiz del repositorio):
    python poc_slm/feedback_tracker.py registrar --recomendacion-id rec-001 --estudiante-id demo-001 \
        --semana 1 --recurso-id tde-s1-A --util si --likert 4 --comentario "El mapa me ayudo"
    python poc_slm/feedback_tracker.py simular --n 30 --semilla 42 --sobrescribir
    python poc_slm/feedback_tracker.py kpis --archivo poc_slm/feedback/feedback_simulado.jsonl
    python poc_slm/feedback_tracker.py importar-moodle --semana 1   # feedback real desde Moodle en Docker

Detalles del contrato y uso para fine-tuning: docs/especificaciones/feedback-loop.md

Dependencias externas: jsonschema. `importar-moodle` requiere Docker con el
compose de moodle/ levantado (no agrega dependencias de Python).
"""

import argparse
import json
import os
import random
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jsonschema

# Forzar salida en UTF-8 para evitar caracteres corruptos en Windows / PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Rutas relativas a la raiz del repositorio (este script vive en poc_slm/)
RAIZ = Path(__file__).resolve().parent.parent
SCHEMA_PATH = RAIZ / "docs" / "especificaciones" / "feedback.schema.json"
DIR_FEEDBACK = RAIZ / "poc_slm" / "feedback"
ARCHIVO_DEFAULT = DIR_FEEDBACK / "feedback.jsonl"
ARCHIVO_SIMULADO = DIR_FEEDBACK / "feedback_simulado.jsonl"
RECURSOS_DEFAULT = RAIZ / "poc_slm" / "recursos" / "semana_1.json"
DIR_RECOMENDACIONES = RAIZ / "poc_slm" / "recomendaciones"   # registro del Prompt Builder (E2-10)
COMPOSE_MOODLE = RAIZ / "moodle" / "docker-compose.yml"

ZONA_BOGOTA = timezone(timedelta(hours=-5))

# Conexion a la MariaDB del compose de moodle/ (mismos valores que docker-compose.yml)
MOODLE_DB_USER = os.environ.get("MOODLE_DB_USER", "moodle")
MOODLE_DB_PASSWORD = os.environ.get("MOODLE_DB_PASSWORD", "moodle")
MOODLE_DB_NAME = os.environ.get("MOODLE_DB_NAME", "moodle")
MOODLE_DB_PREFIX = os.environ.get("MOODLE_DB_PREFIX", "mdl_")

# Una fila JSON por respuesta enviada a la actividad Feedback de Moodle.
# Las preguntas se identifican por su "Etiqueta" (campo label): util, likert, comentario.
SQL_RESPUESTAS_MOODLE = """
SELECT JSON_OBJECT(
    'completed_id', c.id,
    'userid', c.userid,
    'idnumber', u.idnumber,
    'timemodified', c.timemodified,
    'respuestas', JSON_ARRAYAGG(JSON_OBJECT(
        'label', i.label, 'typ', i.typ, 'presentation', i.presentation, 'value', v.value))
)
FROM {p}feedback f
JOIN {p}feedback_completed c ON c.feedback = f.id
JOIN {p}feedback_value v ON v.completed = c.id
JOIN {p}feedback_item i ON i.id = v.item
LEFT JOIN {p}user u ON u.id = c.userid
WHERE f.name = '{actividad}'
GROUP BY c.id, c.userid, u.idnumber, c.timemodified
ORDER BY c.timemodified, c.id;
"""

# Comentarios de ejemplo para el feedback simulado (no son respuestas reales)
COMENTARIOS_UTIL = [
    "Me sirvio para entender la estructura.",
    "El formato se ajusto a como estudio.",
    "Pude aplicar lo visto en mi borrador.",
]
COMENTARIOS_NO_UTIL = [
    "Me tomo mas tiempo del que tenia.",
    "Hubiera preferido otro formato.",
    "No me quedo claro el contraargumento.",
]


def cargar_schema() -> dict:
    """Carga el schema JSON del evento de feedback."""
    with SCHEMA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def validar_evento(evento: dict, schema: dict) -> None:
    """Valida un evento contra el schema. Lanza ValueError con el motivo si no es valido.

    jsonschema no verifica `format: date-time` sin dependencias extra, por eso la
    fecha se valida aparte (ISO 8601 con zona horaria obligatoria).
    """
    try:
        jsonschema.validate(evento, schema)
    except jsonschema.ValidationError as e:
        campo = ".".join(str(p) for p in e.absolute_path) or "(raiz)"
        raise ValueError(f"campo {campo}: {e.message}") from None
    try:
        fecha = datetime.fromisoformat(evento["fecha"])
    except ValueError:
        raise ValueError(f"campo fecha: '{evento['fecha']}' no es ISO 8601") from None
    if fecha.tzinfo is None:
        raise ValueError(f"campo fecha: '{evento['fecha']}' no incluye zona horaria")


def construir_evento(recomendacion_id: str, estudiante_id: str, semana: int, recurso_id: str,
                     util: bool, likert: int | None = None, comentario: str | None = None,
                     fecha: datetime | None = None) -> dict:
    """Arma un evento de feedback. `resultado` se deriva de `util` para que nunca se contradigan."""
    fecha = fecha or datetime.now(ZONA_BOGOTA)
    evento = {
        "recomendacion_id": recomendacion_id,
        "estudiante_id": estudiante_id,
        "semana": semana,
        "recurso_id": recurso_id,
        "util": util,
        "resultado": "acierto" if util else "descache",
        "fecha": fecha.isoformat(timespec="seconds"),
    }
    if likert is not None:
        evento["likert"] = likert
    if comentario:
        evento["comentario"] = comentario.strip()
    return evento


def registrar_feedback(evento: dict, archivo: Path = ARCHIVO_DEFAULT, schema: dict | None = None) -> dict:
    """Valida el evento y lo agrega como una linea al archivo JSON Lines (solo append)."""
    validar_evento(evento, schema or cargar_schema())
    archivo.parent.mkdir(parents=True, exist_ok=True)
    with archivo.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    return evento


def cargar_feedback(archivo: Path, schema: dict | None = None) -> list[dict]:
    """Lee el archivo JSON Lines. Las lineas invalidas se reportan por stderr y se omiten."""
    schema = schema or cargar_schema()
    eventos = []
    with archivo.open(encoding="utf-8") as f:
        for n, linea in enumerate(f, start=1):
            if not linea.strip():
                continue
            try:
                evento = json.loads(linea)
                validar_evento(evento, schema)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"[AVISO] {archivo.name}:{n} omitida: {e}", file=sys.stderr)
                continue
            eventos.append(evento)
    return eventos


def _tasas(eventos: list[dict]) -> dict:
    """Cuenta aciertos/descaches y calcula las tasas sobre un grupo de eventos."""
    total = len(eventos)
    aciertos = sum(1 for e in eventos if e["util"])
    descaches = total - aciertos
    likerts = [e["likert"] for e in eventos if "likert" in e]
    return {
        "total_evaluadas": total,
        "aciertos": aciertos,
        "descaches": descaches,
        "tasa_acierto": round(aciertos / total * 100, 2) if total else None,
        "tasa_descache": round(descaches / total * 100, 2) if total else None,
        "likert_respuestas": len(likerts),
        "likert_promedio": round(sum(likerts) / len(likerts), 2) if likerts else None,
    }


def calcular_kpis(eventos: list[dict]) -> dict:
    """Calcula los KPIs globales y por recurso.

    Si una recomendacion tiene varios eventos (el estudiante cambio su respuesta),
    cuenta solo el ultimo registrado: el denominador es recomendaciones evaluadas,
    no eventos.
    """
    ultimos = {e["recomendacion_id"]: e for e in eventos}
    evaluadas = list(ultimos.values())
    # Senal de baja confianza: util=si con 1-2 estrellas o util=no con 4-5 estrellas
    contradicciones = sum(
        1 for e in evaluadas
        if "likert" in e and ((e["util"] and e["likert"] <= 2) or (not e["util"] and e["likert"] >= 4))
    )
    por_recurso = {}
    for recurso_id in sorted({e["recurso_id"] for e in evaluadas}):
        por_recurso[recurso_id] = _tasas([e for e in evaluadas if e["recurso_id"] == recurso_id])
    return {
        "eventos_registrados": len(eventos),
        "duplicados_descartados": len(eventos) - len(evaluadas),
        **_tasas(evaluadas),
        "contradicciones_util_likert": contradicciones,
        "por_recurso": por_recurso,
    }


def simular_feedback(n: int, semilla: int, prob_util: float, archivo: Path, recursos_path: Path) -> list[dict]:
    """Genera y registra `n` eventos simulados reproducibles sobre los recursos de una semana."""
    with recursos_path.open(encoding="utf-8") as f:
        recursos = json.load(f)
    rng = random.Random(semilla)
    schema = cargar_schema()
    base = datetime(2026, 10, 19, 8, 0, tzinfo=ZONA_BOGOTA)
    eventos = []
    for i in range(1, n + 1):
        recurso = rng.choice(recursos)
        util = rng.random() < prob_util
        likert = rng.choice([3, 4, 5] if util else [1, 2, 3]) if rng.random() < 0.8 else None
        comentario = rng.choice(COMENTARIOS_UTIL if util else COMENTARIOS_NO_UTIL) if rng.random() < 0.4 else None
        evento = construir_evento(
            recomendacion_id=f"sim-s{recurso['semana']}-{i:04d}",
            estudiante_id=f"sim-est-{i:03d}",
            semana=recurso["semana"],
            recurso_id=recurso["recurso_id"],
            util=util,
            likert=likert,
            comentario=comentario,
            fecha=base + timedelta(minutes=17 * i),
        )
        eventos.append(registrar_feedback(evento, archivo, schema))
    return eventos


def consultar_moodle(actividad: str) -> list[dict]:
    """Lee las respuestas de la actividad Feedback desde la MariaDB del compose de moodle/.

    Usa `docker compose exec` sobre el servicio `db`, asi que no necesita un driver
    MySQL en Python ni exponer el puerto de la base. JSON_OBJECT escapa saltos de
    linea y tabuladores, por eso cada fila de la salida es un JSON completo.
    """
    sql = SQL_RESPUESTAS_MOODLE.format(p=MOODLE_DB_PREFIX, actividad=actividad.replace("'", "''"))
    comando = [
        "docker", "compose", "-f", str(COMPOSE_MOODLE), "exec", "-T",
        "-e", f"MYSQL_PWD={MOODLE_DB_PASSWORD}", "db",
        "mariadb", "-u", MOODLE_DB_USER, MOODLE_DB_NAME,
        "--batch", "--raw", "--skip-column-names", "-e", sql,
    ]
    try:
        proceso = subprocess.run(comando, capture_output=True, text=True, encoding="utf-8", check=False)
    except FileNotFoundError:
        raise RuntimeError("no se encontro el comando docker; instala Docker y levanta moodle/ "
                           "con `docker compose up -d`") from None
    if proceso.returncode != 0:
        raise RuntimeError(f"fallo la consulta a Moodle en Docker: {proceso.stderr.strip()}")
    return [json.loads(linea) for linea in proceso.stdout.splitlines() if linea.strip()]


def _opcion_elegida(respuesta: dict) -> str:
    """Traduce el valor de una pregunta de opcion multiple de Moodle al texto de la opcion.

    Moodle guarda el indice (desde 1) de la opcion elegida y las opciones en
    `presentation` con el formato `r>>>>>Si|No<<<<<1`.
    """
    opciones = respuesta["presentation"].split(">>>>>", 1)[-1].split("<<<<<", 1)[0].split("|")
    indice = int(respuesta["value"])
    if not 1 <= indice <= len(opciones):
        raise ValueError(f"opcion {indice} fuera de rango en la pregunta '{respuesta['label']}'")
    return opciones[indice - 1].strip()


def respuesta_moodle_a_campos(fila: dict) -> dict:
    """Extrae util, likert y comentario de una respuesta de Moodle (por la etiqueta de cada pregunta)."""
    por_etiqueta = {r["label"].strip().lower(): r for r in fila["respuestas"] if r.get("label")}
    if "util" not in por_etiqueta or not str(por_etiqueta["util"]["value"]).strip():
        raise ValueError("no respondio la pregunta con etiqueta 'util'")
    campos = {"util": _si_no(_opcion_elegida(por_etiqueta["util"]))}
    likert = por_etiqueta.get("likert")
    if likert and str(likert["value"]).strip():
        campos["likert"] = int(_opcion_elegida(likert))
    comentario = por_etiqueta.get("comentario")
    if comentario and str(comentario["value"]).strip():
        campos["comentario"] = str(comentario["value"])
    return campos


def cargar_recomendaciones(semana: int, archivo: Path | None = None) -> dict:
    """Carga el registro del Prompt Builder (E2-10) e indexa por estudiante_id.

    Cada linea debe traer al menos recomendacion_id, estudiante_id, semana y recurso_id
    (seccion 7.1 de feedback-loop.md). Si hay varias para el mismo estudiante gana la ultima.
    """
    archivo = archivo or DIR_RECOMENDACIONES / f"semana_{semana}.jsonl"
    if not archivo.exists():
        raise RuntimeError(f"no existe el registro de recomendaciones de E2-10: {archivo}")
    indice = {}
    with archivo.open(encoding="utf-8") as f:
        for linea in f:
            if linea.strip():
                rec = json.loads(linea)
                if rec.get("semana") == semana:
                    indice[rec["estudiante_id"]] = rec
    return indice


def importar_moodle(semana: int, actividad: str, archivo: Path, recomendaciones: Path | None = None,
                    filas: list[dict] | None = None) -> tuple[list[dict], int]:
    """Convierte las respuestas de Moodle en eventos de feedback y las agrega al .jsonl.

    - estudiante_id = campo "Numero de ID" (idnumber) del usuario en Moodle, el mismo
      seudonimo del perfil (E2-07); sin idnumber se usa `moodle-<userid>`.
    - recomendacion_id y recurso_id salen del registro de E2-10 para (estudiante, semana).
    - Es idempotente: una respuesta ya importada (misma recomendacion y fecha) no se repite.
      Si el estudiante edita su respuesta en Moodle, cambia la fecha y entra como evento nuevo.

    Devuelve (eventos importados, respuestas omitidas).
    """
    filas = consultar_moodle(actividad) if filas is None else filas
    recs = cargar_recomendaciones(semana, recomendaciones)
    schema = cargar_schema()
    ya_importados = set()
    if archivo.exists():
        ya_importados = {(e["recomendacion_id"], e["fecha"]) for e in cargar_feedback(archivo, schema)}

    importados, omitidos = [], 0
    for fila in filas:
        ref = f"respuesta Moodle {fila['completed_id']}"
        if not fila.get("userid"):
            print(f"[AVISO] {ref} omitida: es anonima, la actividad debe ser no anonima", file=sys.stderr)
            omitidos += 1
            continue
        estudiante_id = (fila.get("idnumber") or "").strip() or f"moodle-{fila['userid']}"
        rec = recs.get(estudiante_id)
        if rec is None:
            print(f"[AVISO] {ref} omitida: {estudiante_id} no tiene recomendacion en la semana {semana}",
                  file=sys.stderr)
            omitidos += 1
            continue
        try:
            campos = respuesta_moodle_a_campos(fila)
            evento = construir_evento(
                recomendacion_id=rec["recomendacion_id"],
                estudiante_id=estudiante_id,
                semana=semana,
                recurso_id=rec["recurso_id"],
                fecha=datetime.fromtimestamp(int(fila["timemodified"]), ZONA_BOGOTA),
                **campos,
            )
            if (evento["recomendacion_id"], evento["fecha"]) in ya_importados:
                continue
            importados.append(registrar_feedback(evento, archivo, schema))
        except (ValueError, argparse.ArgumentTypeError) as e:
            print(f"[AVISO] {ref} omitida: {e}", file=sys.stderr)
            omitidos += 1
    return importados, omitidos


def imprimir_kpis(kpis: dict, archivo: Path) -> None:
    """Imprime los KPIs en consola en formato legible."""
    def pct(v):
        return "n/a" if v is None else f"{v:.2f}%"

    print(f"KPIs de feedback - {archivo.relative_to(RAIZ) if archivo.is_relative_to(RAIZ) else archivo}")
    print(f"  Eventos registrados:        {kpis['eventos_registrados']}")
    print(f"  Duplicados descartados:     {kpis['duplicados_descartados']}")
    print(f"  Recomendaciones evaluadas:  {kpis['total_evaluadas']}")
    print(f"  Tasa de acierto:            {pct(kpis['tasa_acierto'])} ({kpis['aciertos']})")
    print(f"  Tasa de descache:           {pct(kpis['tasa_descache'])} ({kpis['descaches']})")
    print(f"  Likert promedio (1-5):      {kpis['likert_promedio'] or 'n/a'} (n={kpis['likert_respuestas']})")
    print(f"  Contradicciones util/likert: {kpis['contradicciones_util_likert']}")
    print("  Por recurso:")
    for recurso_id, t in kpis["por_recurso"].items():
        print(f"    {recurso_id}: n={t['total_evaluadas']}  acierto={pct(t['tasa_acierto'])}  "
              f"descache={pct(t['tasa_descache'])}  likert={t['likert_promedio'] or 'n/a'}")


def _si_no(valor: str) -> bool:
    valor = valor.strip().lower().replace("í", "i")   # Moodle puede mostrar la opcion con tilde
    if valor in ("si", "true", "1"):
        return True
    if valor in ("no", "false", "0"):
        return False
    raise argparse.ArgumentTypeError("usa si/no")


def main() -> None:
    parser = argparse.ArgumentParser(description="Registro de feedback y KPIs del recomendador (E2-11).")
    sub = parser.add_subparsers(dest="comando", required=True)

    p_reg = sub.add_parser("registrar", help="Registra un evento de feedback.")
    p_reg.add_argument("--recomendacion-id", required=True)
    p_reg.add_argument("--estudiante-id", required=True)
    p_reg.add_argument("--semana", type=int, required=True)
    p_reg.add_argument("--recurso-id", required=True)
    p_reg.add_argument("--util", type=_si_no, required=True, help="si / no")
    p_reg.add_argument("--likert", type=int, help="1 a 5 estrellas (opcional)")
    p_reg.add_argument("--comentario", help="Comentario abierto (opcional)")
    p_reg.add_argument("--archivo", type=Path, default=ARCHIVO_DEFAULT)

    p_sim = sub.add_parser("simular", help="Genera eventos simulados reproducibles.")
    p_sim.add_argument("--n", type=int, default=30)
    p_sim.add_argument("--semilla", type=int, default=42)
    p_sim.add_argument("--prob-util", type=float, default=0.7, help="Probabilidad de util=si (0-1)")
    p_sim.add_argument("--recursos", type=Path, default=RECURSOS_DEFAULT)
    p_sim.add_argument("--archivo", type=Path, default=ARCHIVO_SIMULADO)
    p_sim.add_argument("--sobrescribir", action="store_true", help="Vacia el archivo antes de simular")

    p_kpi = sub.add_parser("kpis", help="Calcula tasa de acierto y descache.")
    p_kpi.add_argument("--archivo", type=Path, default=ARCHIVO_DEFAULT)

    p_imp = sub.add_parser("importar-moodle", help="Importa el feedback real desde Moodle en Docker.")
    p_imp.add_argument("--semana", type=int, required=True)
    p_imp.add_argument("--actividad", help='Nombre de la actividad Feedback (default: "Feedback semana N")')
    p_imp.add_argument("--recomendaciones", type=Path,
                       help="Registro de E2-10 (default: poc_slm/recomendaciones/semana_N.jsonl)")
    p_imp.add_argument("--archivo", type=Path, default=ARCHIVO_DEFAULT)

    args = parser.parse_args()

    try:
        if args.comando == "registrar":
            evento = construir_evento(args.recomendacion_id, args.estudiante_id, args.semana,
                                      args.recurso_id, args.util, args.likert, args.comentario)
            registrar_feedback(evento, args.archivo)
            print(f"[OK] Feedback registrado en {args.archivo}:")
            print(json.dumps(evento, ensure_ascii=False, indent=2))

        elif args.comando == "simular":
            if not 0 <= args.prob_util <= 1:
                parser.error("--prob-util debe estar entre 0 y 1")
            if args.sobrescribir and args.archivo.exists():
                args.archivo.unlink()
            eventos = simular_feedback(args.n, args.semilla, args.prob_util, args.archivo, args.recursos)
            print(f"[OK] {len(eventos)} eventos simulados registrados en {args.archivo}\n")
            imprimir_kpis(calcular_kpis(cargar_feedback(args.archivo)), args.archivo)

        elif args.comando == "kpis":
            if not args.archivo.exists():
                print(f"[ERROR] No existe el archivo de feedback: {args.archivo}", file=sys.stderr)
                sys.exit(1)
            imprimir_kpis(calcular_kpis(cargar_feedback(args.archivo)), args.archivo)

        elif args.comando == "importar-moodle":
            actividad = args.actividad or f"Feedback semana {args.semana}"
            importados, omitidos = importar_moodle(args.semana, actividad, args.archivo, args.recomendaciones)
            print(f"[OK] {len(importados)} eventos importados de '{actividad}' en {args.archivo} "
                  f"({omitidos} respuestas omitidas)\n")
            if args.archivo.exists():
                imprimir_kpis(calcular_kpis(cargar_feedback(args.archivo)), args.archivo)

    except ValueError as e:
        print(f"[ERROR] Evento invalido: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
