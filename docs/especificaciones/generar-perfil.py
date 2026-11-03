"""Genera el perfil JSON en formato bruto de un estudiante desde Moodle (E3-04 / E3-05).

Uso (desde la raiz del repo):
    python docs/especificaciones/generar-perfil.py
    python docs/especificaciones/generar-perfil.py --usuario persona-1
    python docs/especificaciones/generar-perfil.py --usuario persona-2 --fecha 2026-11-03
    python docs/especificaciones/generar-perfil.py --salida perfiles/reales/persona-1.json

Lee las tablas mdl_learning_style, mdl_personality_test y mdl_block_chaside_responses
a traves de `docker exec` (no requiere cliente MySQL en Python), empaqueta los conteos
originales brutos sin reescalar nada (directriz 2 del docente) y valida el archivo
resultante con `docs/especificaciones/validar-perfiles-brutos.py`.

Los perfiles con origen "real" se escriben en `perfiles/reales/`, que esta en `.gitignore`.
"""

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent.parent.parent
SALIDA_POR_DEFECTO = BASE / "perfiles/reales"
VALIDADOR = BASE / "docs/especificaciones/validar-perfiles-brutos.py"

CONTENEDOR_DB = "moodle-db-1"
BASE_DATOS = "moodle"

AREAS = ["C", "H", "A", "S", "I", "D", "E"]

# Mapeo oficial de preguntas CHASIDE (facade.php: get_question_mapping()).
INTERESES = {
    "C": [1, 12, 20, 53, 64, 71, 78, 85, 91, 98],
    "H": [9, 25, 34, 41, 56, 67, 74, 80, 89, 95],
    "A": [3, 11, 21, 28, 36, 45, 50, 57, 81, 96],
    "S": [8, 16, 23, 33, 44, 52, 62, 70, 87, 92],
    "I": [6, 19, 27, 38, 47, 54, 60, 75, 83, 97],
    "D": [5, 14, 24, 31, 37, 48, 58, 65, 73, 84],
    "E": [17, 32, 35, 42, 49, 61, 68, 77, 88, 93],
}
APTITUDES = {
    "C": [2, 15, 46, 51],
    "H": [30, 63, 72, 86],
    "A": [22, 39, 76, 82],
    "S": [4, 29, 40, 69],
    "I": [10, 26, 59, 90],
    "D": [13, 18, 43, 66],
    "E": [7, 55, 79, 94],
}

# Dimensiones de Felder-Silverman (ILS):
# (clave_diferencial, col_moodle_izq, col_moodle_der, clave_ils_izq, clave_ils_der)
EJES_ILS = [
    ("activo_reflexivo", "ap_active", "ap_reflexivo", "activo", "reflexivo"),
    ("sensitivo_intuitivo", "ap_sensorial", "ap_intuitivo", "sensitivo", "intuitivo"),
    ("visual_verbal", "ap_visual", "ap_verbal", "visual", "verbal"),
    ("secuencial_global", "ap_secuencial", "ap_global", "secuencial", "global"),
]

COLUMNAS_PERSONALIDAD = [
    "extraversion",
    "introversion",
    "sensing",
    "intuition",
    "thinking",
    "feeling",
    "judging",
    "perceptive",
]


class ErrorSistema(Exception):
    """Error de entorno (Docker, MariaDB o test incompleto) con mensaje para el usuario."""


# ---------------------------------------------------------------------------
# Acceso a datos en MariaDB (Moodle en Docker)
# ---------------------------------------------------------------------------

def consultar(sql):
    """Ejecuta SQL en MariaDB via docker exec y devuelve filas como listas de texto."""
    comando = [
        "docker", "exec", CONTENEDOR_DB,
        "mysql", "-u", "root", "-proot", BASE_DATOS,
        "--batch", "--skip-column-names", "-e", sql,
    ]
    try:
        proc = subprocess.run(
            comando, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=90,
        )
    except FileNotFoundError:
        raise ErrorSistema(
            "No se encontro el comando 'docker'. Instala Docker Desktop y verifica que este en el PATH."
        )
    except subprocess.TimeoutExpired:
        raise ErrorSistema("La consulta a MariaDB tardo mas de 90 segundos.")

    if proc.returncode != 0:
        detalle = (proc.stderr or "").strip()
        if any(pista in detalle for pista in ("Cannot connect", "daemon", "npipe", "No such container")):
            raise ErrorSistema(
                "Docker no esta corriendo o el contenedor de Moodle no esta arriba.\n"
                "Levanta la pila con:  cd moodle && docker compose up -d"
            )
        raise ErrorSistema(f"Fallo la consulta a MariaDB:\n{detalle}")

    filas = []
    for linea in proc.stdout.splitlines():
        if linea.strip():
            filas.append(linea.split("\t"))
    return filas


def una_fila(sql, descripcion):
    filas = consultar(sql)
    if not filas:
        raise ErrorSistema(f"No se encontro {descripcion}.")
    return filas[0]


def id_de_usuario(username):
    fila = una_fila(
        f"SELECT id FROM mdl_user WHERE username = '{username}'",
        f"el usuario '{username}' en Moodle",
    )
    return int(fila[0])


def leer_estilos(userid):
    fila = una_fila(
        "SELECT is_completed, ap_active, ap_reflexivo, ap_sensorial, ap_intuitivo, "
        f"ap_visual, ap_verbal, ap_secuencial, ap_global FROM mdl_learning_style WHERE user = {userid}",
        "un test de estilos de aprendizaje para este usuario",
    )
    completo = fila[0] == "1"
    valores = [int(v) if v not in ("", "NULL") else 0 for v in fila[1:9]]
    return completo, dict(zip(
        ["ap_active", "ap_reflexivo", "ap_sensorial", "ap_intuitivo",
         "ap_visual", "ap_verbal", "ap_secuencial", "ap_global"],
        valores,
    ))


def leer_personalidad(userid):
    fila = una_fila(
        f"SELECT is_completed, {', '.join(COLUMNAS_PERSONALIDAD)} FROM mdl_personality_test WHERE user = {userid}",
        "un test de personalidad para este usuario",
    )
    completo = fila[0] == "1"
    valores = [int(v) if v not in ("", "NULL") else 0 for v in fila[1:9]]
    return completo, dict(zip(COLUMNAS_PERSONALIDAD, valores))


def leer_chaside(userid):
    preguntas = ", ".join(f"q{i}" for i in range(1, 99))
    puntajes = ", ".join(f"score_{a.lower()}" for a in AREAS)
    fila = una_fila(
        f"SELECT is_completed, {preguntas}, {puntajes} "
        f"FROM mdl_block_chaside_responses WHERE userid = {userid}",
        "un test CHASIDE para este usuario",
    )
    completo = fila[0] == "1"
    respuestas = {
        i: (1 if fila[i] == "1" else 0) for i in range(1, 99)
    }
    guardados = {
        area: int(fila[99 + i]) if fila[99 + i] not in ("", "NULL") else 0
        for i, area in enumerate(AREAS)
    }
    return completo, respuestas, guardados


# ---------------------------------------------------------------------------
# Empaquetado en formato bruto (Entrega 3 - sin alterar escalas)
# ---------------------------------------------------------------------------

def calcular_estilos_bruto(completo, conteos):
    """Empaqueta los 8 polos originales (0-11) de Felder-Silverman y su diferencial."""
    if not completo:
        raise ErrorSistema(
            "El test de Estilos de Aprendizaje (Felder-Silverman) no esta completado en Moodle "
            "(is_completed = 0). En Entrega 3 no se inventan puntajes neutros."
        )

    ils = {}
    diferencial = {}
    for clave_dif, col_izq, col_der, polo_izq, polo_der in EJES_ILS:
        izquierdo = int(conteos[col_izq])
        derecho = int(conteos[col_der])
        if izquierdo + derecho != 11:
            raise ErrorSistema(
                f"El eje {clave_dif} suma {izquierdo + derecho} en vez de 11 "
                f"({polo_izq}={izquierdo}, {polo_der}={derecho}). Revisa el test en Moodle."
            )
        ils[polo_izq] = izquierdo
        ils[polo_der] = derecho
        diferencial[clave_dif] = izquierdo - derecho

    return ils, diferencial


def calcular_personalidad_bruto(completo, totales):
    """Empaqueta los 8 polos originales (0-9) del test de personalidad sin autonomia."""
    if not completo:
        raise ErrorSistema(
            "El test de Personalidad no esta completado en Moodle (is_completed = 0). "
            "En Entrega 3 no se inventan puntajes neutros."
        )

    personalidad = {}
    for col in COLUMNAS_PERSONALIDAD:
        valor = int(totales[col])
        if valor < 0 or valor > 9:
            raise ErrorSistema(
                f"Personalidad polo {col} fuera de rango 0-9 ({valor}). Revisa el test en Moodle."
            )
        personalidad[col] = valor
    return personalidad


def calcular_chaside_bruto(completo, respuestas, guardados):
    """Empaqueta interes (0-10), aptitud (0-4) y total (0-14) por cada area CHASIDE."""
    if not completo:
        raise ErrorSistema(
            "El test CHASIDE no esta completado en Moodle (is_completed = 0). "
            "En Entrega 3 no se inventan puntajes neutros."
        )

    chaside = {}
    for area in AREAS:
        interes = int(sum(respuestas[q] for q in INTERESES[area]))
        aptitud = int(sum(respuestas[q] for q in APTITUDES[area]))
        total = interes + aptitud
        if total != guardados[area]:
            raise ErrorSistema(
                f"CHASIDE area {area}: el calculo da {total} pero la base guarda {guardados[area]}. "
                "Puede haber cambiado el mapeo de preguntas del bloque."
            )
        chaside[area] = {
            "interes": interes,
            "aptitud": aptitud,
            "total": total,
        }
    return chaside


def construir_perfil_bruto(
    username,
    completo_e,
    conteos_e,
    completo_p,
    totales_p,
    completo_c,
    respuestas_c,
    guardados_c,
    fecha_aplicacion=None,
):
    """Construye el diccionario del perfil bruto conforme a perfil-bruto-psicometrico.schema.json."""
    chaside = calcular_chaside_bruto(completo_c, respuestas_c, guardados_c)
    ils, diferencial = calcular_estilos_bruto(completo_e, conteos_e)
    personalidad = calcular_personalidad_bruto(completo_p, totales_p)

    return {
        "id": username,
        "origen": "real",
        "fecha_aplicacion": fecha_aplicacion or date.today().isoformat(),
        "chaside": chaside,
        "ils": ils,
        "diferencial": diferencial,
        "personalidad": personalidad,
    }


# ---------------------------------------------------------------------------
# Orquestacion
# ---------------------------------------------------------------------------

def generar(username, fecha_aplicacion=None):
    userid = id_de_usuario(username)
    print(f"Usuario {username}: id {userid} en Moodle")

    completo_e, conteos = leer_estilos(userid)
    completo_p, totales = leer_personalidad(userid)
    completo_c, respuestas, guardados = leer_chaside(userid)

    for nombre, completo in (
        ("estilos de aprendizaje (Felder-Silverman)", completo_e),
        ("personalidad", completo_p),
        ("CHASIDE", completo_c),
    ):
        print(f"  {nombre}: {'completo' if completo else 'INCOMPLETO'}")

    return construir_perfil_bruto(
        username,
        completo_e,
        conteos,
        completo_p,
        totales,
        completo_c,
        respuestas,
        guardados,
        fecha_aplicacion=fecha_aplicacion,
    )


def validar(archivo):
    proc = subprocess.run(
        [sys.executable, str(VALIDADOR), str(archivo)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return proc.returncode == 0, (proc.stdout or "").strip(), (proc.stderr or "").strip()


def main():
    parser = argparse.ArgumentParser(
        description="Genera el perfil JSON en formato bruto de un estudiante desde Moodle (E3-04/E3-05)."
    )
    parser.add_argument(
        "--usuario",
        default="persona-1",
        help="username de Moodle (por defecto: persona-1)",
    )
    parser.add_argument(
        "--fecha",
        default=None,
        help="fecha de aplicacion en formato AAAA-MM-DD (por defecto: fecha de hoy)",
    )
    parser.add_argument(
        "--salida",
        default=None,
        help="ruta del JSON de salida (por defecto: perfiles/reales/<usuario>.json)",
    )
    args = parser.parse_args()

    salida = Path(args.salida) if args.salida else SALIDA_POR_DEFECTO / f"{args.usuario}.json"
    if not salida.is_absolute():
        salida = BASE / salida

    try:
        perfil = generar(args.usuario, fecha_aplicacion=args.fecha)
    except ErrorSistema as e:
        print(f"\nERROR: {e}")
        return 1

    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(perfil, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nPerfil bruto escrito en {salida.relative_to(BASE)}")

    ok, stdout, stderr = validar(salida)
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)
    if not ok:
        print("ERROR: el perfil generado no pasa la validacion de contrato bruto.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
