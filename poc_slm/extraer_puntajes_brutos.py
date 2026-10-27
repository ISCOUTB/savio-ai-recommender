"""extraer_puntajes_brutos.py - Extrae los puntajes originales de un integrante desde Moodle (E3-05, #42).

Lee las tres tablas de los bloques IS-UTB en el Moodle local (Docker) con las
funciones de docs/especificaciones/generar-perfil.py, arma el perfil con el
formato del Anexo A (sin reescalar) y verifica su integridad:
  - CHASIDE: recalcula interes y aptitud desde las 98 respuestas con el mapeo
    oficial del bloque y comprueba que el total coincida con el que guardo el bloque.
  - ILS: cada par de polos suma 11.
  - Personalidad: cada polo entre 0 y 9.

Escribe dos archivos en perfiles/reales/ (carpeta ignorada por git):
  <usuario>-bruto.json      perfil identificado, solo para uso local
  <seudonimo>-anonimo.json  mismo perfil con seudonimo, para pruebas de validacion

Uso (desde la raiz del repo, con Docker y el Moodle local corriendo):
    python poc_slm/extraer_puntajes_brutos.py --usuario persona-3 --seudonimo REAL-03
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "poc_slm"))
from perfil_bruto import AREAS_CHASIDE, validar_perfil_bruto  # noqa: E402

_spec = importlib.util.spec_from_file_location("generar_perfil", RAIZ / "docs/especificaciones/generar-perfil.py")
gp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gp)

DIR_REALES = RAIZ / "perfiles" / "reales"
ILS_DESDE_BLOQUE = {
    "ap_active": "activo", "ap_reflexivo": "reflexivo", "ap_sensorial": "sensitivo", "ap_intuitivo": "intuitivo",
    "ap_visual": "visual", "ap_verbal": "verbal", "ap_secuencial": "secuencial", "ap_global": "global",
}


def extraer(usuario: str) -> dict:
    userid = gp.id_de_usuario(usuario)
    completo_ils, ils_bloque = gp.leer_estilos(userid)
    completo_pers, personalidad = gp.leer_personalidad(userid)
    completo_ch, respuestas, guardados = gp.leer_chaside(userid)
    incompletos = [n for n, c in (("estilos", completo_ils), ("personalidad", completo_pers), ("CHASIDE", completo_ch))
                   if not c]
    if incompletos:
        raise SystemExit(f"[ERROR] {usuario} no ha completado: {', '.join(incompletos)}")

    chaside = {}
    for area in AREAS_CHASIDE:
        interes = sum(respuestas[q] for q in gp.INTERESES[area])
        aptitud = sum(respuestas[q] for q in gp.APTITUDES[area])
        if interes + aptitud != guardados[area]:
            raise SystemExit(f"[ERROR] CHASIDE {area}: recalculado {interes + aptitud} != guardado {guardados[area]}")
        chaside[area] = {"interes": interes, "aptitud": aptitud, "total": interes + aptitud}

    return {
        "id": usuario,
        "origen": "real",
        "chaside": chaside,
        "ils": {ILS_DESDE_BLOQUE[k]: v for k, v in ils_bloque.items()},
        "personalidad": personalidad,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae puntajes originales brutos desde el Moodle local.")
    parser.add_argument("--usuario", required=True, help="username de Moodle (ej. persona-3)")
    parser.add_argument("--seudonimo", required=True, help="id anonimo para pruebas (ej. REAL-03)")
    args = parser.parse_args()

    try:
        perfil = extraer(args.usuario)
    except gp.ErrorSistema as e:
        raise SystemExit(f"[ERROR] {e}")
    errores = validar_perfil_bruto(perfil)
    if errores:
        raise SystemExit("[ERROR] Perfil invalido:\n  - " + "\n  - ".join(errores))

    DIR_REALES.mkdir(parents=True, exist_ok=True)
    bruto = DIR_REALES / f"{args.usuario}-bruto.json"
    anonimo = DIR_REALES / f"{args.seudonimo}-anonimo.json"
    bruto.write_text(json.dumps(perfil, indent=2, ensure_ascii=False), encoding="utf-8")
    anonimo.write_text(json.dumps({**perfil, "id": args.seudonimo}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Perfil de {args.usuario} verificado (CHASIDE recalculado, ILS suma 11, personalidad 0-9).")
    print(f"  {bruto.relative_to(RAIZ)}")
    print(f"  {anonimo.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
