"""Chequeos de regresion del modulo de feedback y metricas E2-11 (sin pytest).

Uso (desde la raiz del repositorio, con el entorno virtual activo):
    python poc_slm/test_feedback_tracker.py

Verifica la integridad de docs/especificaciones/feedback.schema.json, la
validacion de eventos (incluyendo coherencia util <-> resultado, rangos Likert
y formato de fecha), la persistencia en JSON Lines (.jsonl) y el calculo
matematico de las tasas de acierto y descache.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import feedback_tracker as ft  # noqa: E402


def caso(nombre: str) -> None:
    print(f"[TEST] {nombre}")


def main() -> int:
    fallos: list[str] = []

    caso("schema feedback.schema.json es valido bajo Draft-07")
    try:
        schema = ft.cargar_schema()
    except Exception as e:
        fallos.append(f"feedback.schema.json invalido: {e}")
        schema = {}

    caso("evento completo valido (con likert y comentario)")
    ev_ok = ft.construir_evento_feedback(
        recomendacion_id="rec-demo-002-s1-b0557548",
        estudiante_id="demo-002",
        semana=1,
        recurso_id="tde-s1-B",
        util=True,
        likert=5,
        comentario="Excelente guia analitica.",
        fecha="2026-10-22T10:00:00Z",
    )
    errores_ok = ft.validar_evento_feedback(ev_ok, schema=schema)
    if errores_ok:
        fallos.append(f"evento valido fue rechazado: {errores_ok}")
    if ev_ok.get("resultado") != "acierto":
        fallos.append(f"resultado esperado 'acierto', llego {ev_ok.get('resultado')!r}")

    caso("evento minimo valido (sin opcionales likert ni comentario)")
    ev_min = ft.construir_evento_feedback(
        recomendacion_id="rec-demo-001-s1-53ef6765",
        estudiante_id="demo-001",
        semana=1,
        recurso_id="tde-s1-C",
        util=False,
        fecha="2026-10-22T10:05:00Z",
    )
    if "likert" in ev_min or "comentario" in ev_min:
        fallos.append("evento minimo no debe incluir claves opcionales vacias")
    if ev_min.get("resultado") != "descache":
        fallos.append(f"resultado esperado 'descache', llego {ev_min.get('resultado')!r}")
    errores_min = ft.validar_evento_feedback(ev_min, schema=schema)
    if errores_min:
        fallos.append(f"evento minimo valido fue rechazado: {errores_min}")

    caso("rechaza incoherencia entre util y resultado")
    ev_incoherente = dict(ev_ok, resultado="descache")
    err_inc = ft.validar_evento_feedback(ev_incoherente, schema=schema)
    if not err_inc:
        fallos.append("no se detecto incoherencia util=True con resultado='descache'")

    caso("rechaza escala Likert fuera de rango 1..5")
    for valor_invalido in (0, 6, -1):
        ev_likert = dict(ev_ok, likert=valor_invalido)
        if not ft.validar_evento_feedback(ev_likert, schema=schema):
            fallos.append(f"no se rechazo likert={valor_invalido}")

    caso("rechaza propiedades no declaradas (additionalProperties: false)")
    ev_extra = dict(ev_ok, campo_inventado="x")
    if not ft.validar_evento_feedback(ev_extra, schema=schema):
        fallos.append("no se rechazo una propiedad adicional no declarada")

    caso("rechaza fecha que no sea ISO 8601 date-time")
    ev_fecha = dict(ev_ok, fecha="22/10/2026")
    if not ft.validar_evento_feedback(ev_fecha, schema=schema):
        fallos.append("no se rechazo una fecha con formato invalido")

    caso("construccion desde JSON de salida de prompt_builder.py")
    salida_pb = {
        "recomendacion_id": "rec-demo-003-s1-263363f9",
        "estudiante_id": "demo-003",
        "semana": 1,
        "recurso_elegido": "tde-s1-C",
        "opcion": "C",
    }
    ev_desde_pb = ft.construir_desde_recomendacion(
        salida_pb,
        util=True,
        likert=4,
        comentario="Practico y estructurado.",
        fecha="2026-10-22T11:00:00Z",
    )
    if ev_desde_pb["recurso_id"] != "tde-s1-C":
        fallos.append(f"no mapeo recurso_elegido -> recurso_id: {ev_desde_pb}")
    if ft.validar_evento_feedback(ev_desde_pb, schema=schema):
        fallos.append("evento construido desde prompt_builder no paso validacion")

    caso("persistencia JSONL y calculo de KPIs (Tasa de Acierto y Descache)")
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_tmp = Path(tmpdir) / "test_eventos.jsonl"
        simulados = ft.eventos_simulados_base()
        for ev in simulados:
            ft.registrar_feedback(ev, ruta_jsonl=ruta_tmp, schema=schema)

        cargados = ft.cargar_eventos_feedback(ruta_jsonl=ruta_tmp, schema=schema)
        if len(cargados) != 5:
            fallos.append(f"se esperaban 5 eventos cargados, llegaron {len(cargados)}")

        metricas = ft.calcular_metricas(cargados)
        if metricas["total_evaluadas"] != 5:
            fallos.append(f"total_evaluadas esperado 5, llego {metricas['total_evaluadas']}")
        if metricas["utiles"] != 4 or metricas["no_utiles"] != 1:
            fallos.append(f"conteo utiles/no_utiles inesperado: {metricas}")
        if metricas["tasa_acierto_pct"] != 80.0:
            fallos.append(f"tasa_acierto_pct esperada 80.0, llego {metricas['tasa_acierto_pct']}")
        if metricas["tasa_descache_pct"] != 20.0:
            fallos.append(f"tasa_descache_pct esperada 20.0, llego {metricas['tasa_descache_pct']}")
        if round(metricas["tasa_acierto_pct"] + metricas["tasa_descache_pct"], 2) != 100.0:
            fallos.append("la suma de tasa de acierto y descache no es 100%")
        if metricas["likert_promedio"] != 4.2:
            fallos.append(f"likert_promedio esperado 4.2, llego {metricas['likert_promedio']}")

    caso("calculo de KPIs con lista vacia no divide por cero")
    vacio = ft.calcular_metricas([])
    if vacio["tasa_acierto_pct"] != 0.0 or vacio["tasa_descache_pct"] != 0.0 or vacio["likert_promedio"] is not None:
        fallos.append(f"metricas para lista vacia incorrectas: {vacio}")

    print()
    if fallos:
        print(f"FALLARON {len(fallos)} chequeo(s):")
        for fallo in fallos:
            print(f"  - {fallo}")
        return 1
    print("OK: todos los chequeos de feedback_tracker pasaron")
    return 0


if __name__ == "__main__":
    sys.exit(main())
