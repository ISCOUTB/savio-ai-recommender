"""Genera el perfil JSON de un estudiante a partir de sus respuestas en Moodle (E2-07).

Uso (desde la raiz del repo):
    python docs/especificaciones/generar-perfil.py
    python docs/especificaciones/generar-perfil.py --usuario persona-1
    python docs/especificaciones/generar-perfil.py --salida perfiles/reales/prueba.json

Lee las tablas mdl_learning_style, mdl_personality_test y mdl_block_chaside_responses
a traves de `docker exec` (no requiere cliente MySQL en Python), aplica las formulas de
docs/especificaciones/escala-canonica.md y valida el resultado con validar-perfiles.py.

Los perfiles con origen "real" se escriben en perfiles/reales/, que esta en .gitignore.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent.parent.parent
SALIDA_POR_DEFECTO = BASE / "perfiles/reales"
VALIDADOR = BASE / "docs/especificaciones/validar-perfiles.py"

CONTENEDOR_DB = "moodle-db-1"
BASE_DATOS = "moodle"

AREAS = ["C", "H", "A", "S", "I", "D", "E"]

# Nombres oficiales del bloque (lang/es/block_chaside.php).
NOMBRE_AREA = {
    "C": "Administrativa",
    "H": "Humanidades/Sociales/Juridicas",
    "A": "Artistica",
    "S": "Ciencias de la Salud",
    "I": "Ensenanzas Tecnicas",
    "D": "Defensa y Seguridad",
    "E": "Ciencias Experimentales",
}

# Ejemplos con los que se puede conectar la materia, por area.
CONEXION_AREA = {
    "C": "organizacion, gestion y tareas administrativas",
    "H": "comunicacion, analisis social y textos",
    "A": "creacion, diseno y expresion",
    "S": "cuidado de personas y practicas de salud",
    "I": "procesos tecnicos, sistemas y resolucion de problemas",
    "D": "liderazgo, disciplina y trabajo en equipo",
    "E": "experimentacion, datos y metodo cientifico",
}

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

# Estilos: clave del perfil, columna del polo izquierdo, columna del polo derecho,
# nombre del polo izquierdo, nombre del polo derecho.
EJES_ESTILOS = [
    ("activo_reflexivo", "ap_active", "ap_reflexivo", "activo", "reflexivo"),
    ("sensorial_intuitivo", "ap_sensorial", "ap_intuitivo", "sensorial", "intuitivo"),
    ("visual_verbal", "ap_visual", "ap_verbal", "visual", "verbal"),
    ("secuencial_global", "ap_secuencial", "ap_global", "secuencial", "global"),
]

FRAGMENTO_ESTILO = {
    "activo": "aprende mejor experimentando y aplicando los conceptos de forma inmediata",
    "reflexivo": "aprende mejor reflexionando antes de actuar y trabajando de forma individual",
    "sensorial": "conecta mejor con ejemplos concretos, datos especificos y procedimientos claros",
    "intuitivo": "disfruta explorar principios, teorias y conexiones entre ideas",
    "visual": "privilegia recursos graficos, diagramas, mapas y videos",
    "verbal": "prefiere explicaciones escritas o habladas, resumenes y definiciones",
    "secuencial": "rinde mejor con una secuencia definida y progresion paso a paso",
    "global": "necesita ver el panorama general antes de entrar en los detalles",
}

INCLUIR_ESTILO = {
    "activo": "ejercicios y aplicacion inmediata",
    "reflexivo": "lectura previa y pausas para pensar",
    "sensorial": "ejemplos concretos y procedimientos paso a paso",
    "intuitivo": "casos integradores y preguntas de porque",
    "visual": "esquemas visuales y diagramas",
    "verbal": "resumenes y definiciones",
    "secuencial": "guias numeradas de lo simple a lo complejo",
    "global": "panoramas integradores",
}

EVITAR_ESTILO = {
    "activo": "teoria pasiva prolongada",
    "reflexivo": "respuesta inmediata en vivo",
    "sensorial": "abstraccion sin aplicacion",
    "intuitivo": "repeticion mecanica sin proposito",
    "visual": "textos densos sin apoyo grafico",
    "verbal": "graficos sin texto de apoyo",
    "secuencial": "saltos sin secuencia",
    "global": "detalles sin proposito global",
}

NEUTRO_ESTILOS = (
    "Sin informacion suficiente de preferencias de aprendizaje; alternar formatos visuales "
    "y verbales, activos y reflexivos, concretos y abstractos, lineales y globales."
)

# Personalidad: rasgo, columnas (polo alto, polo bajo) y textos por polo.
RASGOS_PERSONALIDAD = [
    ("introversion_extraversion", "extraversion", "introversion"),
    ("metodicidad", "judging", "perceptive"),
    ("apertura", "intuition", "sensing"),
]

ETIQUETAS_PERSONALIDAD = {
    ("introversion_extraversion", "alto"): ["colaborativo", "foros y debates"],
    ("introversion_extraversion", "bajo"): ["individual", "reflexion previa"],
    ("autonomia", "alto"): ["ritmo propio", "retos abiertos"],
    ("autonomia", "bajo"): ["guia paso a paso", "checklist", "retroalimentacion frecuente"],
    ("metodicidad", "alto"): ["secuencia definida", "cronograma"],
    ("metodicidad", "bajo"): ["bloques cortos flexibles", "variedad de actividades"],
    ("apertura", "alto"): ["exploratorio", "conexiones entre ideas"],
    ("apertura", "bajo"): ["ejemplos concretos", "aplicacion practica inmediata"],
}

FRAGMENTO_PERSONALIDAD = {
    ("introversion_extraversion", "alto"): "suele aprovechar el intercambio de ideas con otras personas, como foros o debates",
    ("introversion_extraversion", "bajo"): "suele preferir el estudio individual, con tiempo para reflexionar antes de participar",
    ("autonomia", "alto"): "se desenvuelve bien con retos abiertos a su propio ritmo",
    ("autonomia", "bajo"): "se beneficia de instrucciones claras, pasos explicitos y retroalimentacion frecuente",
    ("metodicidad", "alto"): "rinde mejor con una secuencia definida y un cronograma claro",
    ("metodicidad", "bajo"): "aprovecha mejor actividades variadas en bloques cortos y flexibles",
    ("apertura", "alto"): "disfruta explorar el porque de los conceptos y las conexiones entre ideas",
    ("apertura", "bajo"): "conecta mejor con ejemplos concretos y aplicacion practica inmediata",
}

NEUTRO_PERSONALIDAD = (
    "Muestra preferencias de trabajo equilibradas; conviene combinar formatos individuales "
    "y colaborativos, guiados y abiertos."
)


class ErrorSistema(Exception):
    """Error de entorno (Docker, MariaDB) con mensaje para el usuario."""


# ---------------------------------------------------------------------------
# Acceso a datos
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
    columnas = ["extraversion", "introversion", "sensing", "intuition",
                "thinking", "feeling", "judging", "perceptive"]
    fila = una_fila(
        f"SELECT is_completed, {', '.join(columnas)} FROM mdl_personality_test WHERE user = {userid}",
        "un test de personalidad para este usuario",
    )
    completo = fila[0] == "1"
    valores = [int(v) if v not in ("", "NULL") else 0 for v in fila[1:9]]
    return completo, dict(zip(columnas, valores))


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
# Calculo
# ---------------------------------------------------------------------------

def enumerar(items):
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " y " + items[-1]


def capitalizar(texto):
    return texto[0].upper() + texto[1:]


def calcular_estilos(completo, conteos):
    if not completo:
        return {
            "modelo": "felder_silverman",
            "puntajes": {clave: 3.0 for clave, *_ in EJES_ESTILOS},
            "preferencias": [],
            "descripcion_para_prompt": NEUTRO_ESTILOS,
        }

    puntajes = {}
    preferencias = []
    for clave, col_izq, col_der, polo_izq, polo_der in EJES_ESTILOS:
        izquierdo, derecho = conteos[col_izq], conteos[col_der]
        if izquierdo + derecho != 11:
            raise ErrorSistema(
                f"El eje {clave} suma {izquierdo + derecho} en vez de 11 "
                f"({polo_izq}={izquierdo}, {polo_der}={derecho}). Revisa el test en Moodle."
            )
        valor = round(3 + 2 * (derecho - izquierdo) / 11, 1)
        puntajes[clave] = valor
        if valor <= 2.1:
            preferencias.append(polo_izq)
        elif valor >= 3.9:
            preferencias.append(polo_der)

    if not preferencias:
        descripcion = NEUTRO_ESTILOS
    else:
        cuerpo = "El estudiante " + enumerar([FRAGMENTO_ESTILO[p] for p in preferencias]) + "."
        incluir = [INCLUIR_ESTILO[p] for p in preferencias]
        evitar = [EVITAR_ESTILO[p] for p in preferencias]
        if len(incluir) == 1:
            recomendacion = f"Se recomienda priorizar {incluir[0]} y evitar {evitar[0]}."
        else:
            recomendacion = (
                f"Se recomienda priorizar {incluir[0]}, complementado con {enumerar(incluir[1:])}, "
                f"y evitar {enumerar(evitar)}."
            )
        descripcion = cuerpo + " " + recomendacion

    return {
        "modelo": "felder_silverman",
        "puntajes": puntajes,
        "preferencias": preferencias,
        "descripcion_para_prompt": descripcion,
    }


def calcular_personalidad(completo, totales):
    if not completo:
        return {
            "rasgos": {
                "introversion_extraversion": 3.0,
                "autonomia": 3.0,
                "metodicidad": 3.0,
                "apertura": 3.0,
            },
            "resumen_conductual": NEUTRO_PERSONALIDAD,
            "preferencias_trabajo": [],
        }

    rasgos = {}
    for rasgo, col_alto, col_bajo in RASGOS_PERSONALIDAD:
        rasgos[rasgo] = round(3 + 2 * (totales[col_alto] - totales[col_bajo]) / 9, 1)
    rasgos["autonomia"] = round(
        3 + ((totales["intuition"] - totales["sensing"]) + (totales["thinking"] - totales["feeling"])) / 9,
        1,
    )
    rasgos = {
        "introversion_extraversion": rasgos["introversion_extraversion"],
        "autonomia": rasgos["autonomia"],
        "metodicidad": rasgos["metodicidad"],
        "apertura": rasgos["apertura"],
    }

    preferencias = []
    fragmentos = []
    for rasgo in ["introversion_extraversion", "autonomia", "metodicidad", "apertura"]:
        valor = rasgos[rasgo]
        if valor <= 2.1:
            polo = "bajo"
        elif valor >= 3.9:
            polo = "alto"
        else:
            continue
        preferencias.extend(ETIQUETAS_PERSONALIDAD[(rasgo, polo)])
        fragmentos.append(FRAGMENTO_PERSONALIDAD[(rasgo, polo)])

    if not fragmentos:
        resumen = NEUTRO_PERSONALIDAD
    else:
        oraciones = [capitalizar(enumerar(fragmentos[:2])) + "."]
        if len(fragmentos) > 2:
            oraciones.append(capitalizar(enumerar(fragmentos[2:])) + ".")
        resumen = " ".join(oraciones)

    return {
        "rasgos": rasgos,
        "resumen_conductual": resumen,
        "preferencias_trabajo": preferencias,
    }


def calcular_chaside(completo, respuestas, guardados):
    if not completo:
        return {
            "areas": {area: 3.0 for area in AREAS},
            "areas_dominantes": [],
            "descripcion_para_analogias": (
                "Sin informacion suficiente de intereses vocacionales; usar ejemplos de "
                "varias areas y evitar supuestos sobre la orientacion del estudiante."
            ),
        }

    detalle = []
    areas = {}
    for area in AREAS:
        interes = sum(respuestas[q] for q in INTERESES[area])
        aptitud = sum(respuestas[q] for q in APTITUDES[area])
        total = interes + aptitud
        if total != guardados[area]:
            raise ErrorSistema(
                f"CHASIDE area {area}: el calculo da {total} pero la base guarda {guardados[area]}. "
                "Puede haber cambiado el mapeo de preguntas del bloque."
            )
        areas[area] = round(1 + 4 * total / 14, 1)
        detalle.append({
            "area": area,
            "total": total,
            "aptitud": aptitud,
            "brecha": abs(interes - aptitud),
        })

    # Desempate oficial de facade.php: total, aptitud, brecha y orden alfabetico.
    orden = sorted(detalle, key=lambda d: (-d["total"], -d["aptitud"], d["brecha"], d["area"]))
    dominantes = [d["area"] for d in orden[:2]]

    nombres = [f"{NOMBRE_AREA[a]} ({a})" for a in dominantes]
    conexiones = [CONEXION_AREA[a] for a in dominantes]
    descripcion = (
        f"Conviene conectar la materia con ejemplos de {enumerar(conexiones)}; "
        f"areas principales: {enumerar(nombres)}."
    )

    return {
        "areas": areas,
        "areas_dominantes": dominantes,
        "descripcion_para_analogias": descripcion,
    }


# ---------------------------------------------------------------------------
# Orquestacion
# ---------------------------------------------------------------------------

def generar(username):
    userid = id_de_usuario(username)
    print(f"Usuario {username}: id {userid} en Moodle")

    completo_e, conteos = leer_estilos(userid)
    completo_p, totales = leer_personalidad(userid)
    completo_c, respuestas, guardados = leer_chaside(userid)

    for nombre, completo in (
        ("estilos de aprendizaje", completo_e),
        ("personalidad", completo_p),
        ("CHASIDE", completo_c),
    ):
        print(f"  {nombre}: {'completo' if completo else 'INCOMPLETO -> perfil neutro'}")

    perfil = {
        "estudiante_id": username,
        "origen": "real",
        "estilos_aprendizaje": calcular_estilos(completo_e, conteos),
        "personalidad": calcular_personalidad(completo_p, totales),
        "chaside": calcular_chaside(completo_c, respuestas, guardados),
    }
    return perfil


def validar(archivo):
    proc = subprocess.run(
        [sys.executable, str(VALIDADOR), str(archivo)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return proc.returncode == 0, (proc.stdout or "").strip(), (proc.stderr or "").strip()


def main():
    parser = argparse.ArgumentParser(description="Genera el perfil JSON de un estudiante desde Moodle.")
    parser.add_argument("--usuario", default="persona-1", help="username de Moodle (por defecto: persona-1)")
    parser.add_argument("--salida", default=None, help="ruta del JSON de salida")
    args = parser.parse_args()

    salida = Path(args.salida) if args.salida else SALIDA_POR_DEFECTO / f"{args.usuario}.json"
    if not salida.is_absolute():
        salida = BASE / salida

    try:
        perfil = generar(args.usuario)
    except ErrorSistema as e:
        print(f"\nERROR: {e}")
        return 1

    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(perfil, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nPerfil escrito en {salida.relative_to(BASE)}")

    ok, stdout, stderr = validar(salida)
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)
    if not ok:
        print("ERROR: el perfil generado no pasa la validacion.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
