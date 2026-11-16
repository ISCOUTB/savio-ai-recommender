"""Chequeos del backend E3-07 (sin Ollama, sin modelo).

Uso (desde la raiz del repositorio):
    python poc_slm/test_interpretador.py
"""

import ast
import contextlib
import io
import json
import re
import sys
import tempfile
from unittest.mock import patch
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "docs" / "especificaciones"))
sys.path.insert(0, str(RAIZ / "poc_slm"))

import importar_gguf as ig  # noqa: E402
import interpretador as it  # noqa: E402

RUTA_PERFIL = RAIZ / "perfiles" / "brutos" / "ejemplo-perfil-bruto-dominante.json"
RUTA_CORPUS_EJEMPLO = RAIZ / "datos" / "corpus" / "ejemplo_mini.jsonl"
RUTA_NOTEBOOK = (
    RAIZ
    / "docs"
    / "entregas"
    / "entrega-3-interpretacion-psicometrica"
    / "notebook-e3-08-sft-qlora.ipynb"
)


def caso(nombre):
    print(f"[TEST] {nombre}")


def cargar_ejemplo():
    primera = RUTA_CORPUS_EJEMPLO.read_text(encoding="utf-8").splitlines()[0]
    return json.loads(primera)


def texto_fiel(perfil):
    """Salida ficticia solo para pruebas; no se escribe como evidencia medida."""
    filas = it.filas_baremos(perfil)
    return "\n".join((it.SECCIONES[0], *filas["ils"], it.SECCIONES[1], *filas["personalidad"], it.SECCIONES[2],
                      *filas["chaside"], it.SECCIONES[3],
                      "Se pueden explorar actividades de analisis de procesos y contrastarlas con la experiencia de estudio.", it.AVISO_NO_CLINICO))


def system_del_notebook():
    """Extrae SYSTEM_E3 del notebook sin ejecutar el cuaderno."""
    datos = json.loads(RUTA_NOTEBOOK.read_text(encoding="utf-8"))
    for celda in datos.get("cells", []):
        fuente = "".join(celda.get("source", []))
        if "SYSTEM_E3" not in fuente:
            continue
        arbol = ast.parse(fuente)
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, ast.Assign):
                continue
            nombres = [t.id for t in nodo.targets if isinstance(t, ast.Name)]
            if "SYSTEM_E3" in nombres:
                return ast.literal_eval(nodo.value)
    return None


def main() -> int:
    fallos = []
    perfil = json.loads(RUTA_PERFIL.read_text(encoding="utf-8-sig"))
    registro = cargar_ejemplo()
    texto_ok = it.agregar_aviso(registro["output"])

    caso("el perfil de ejemplo pasa la validacion del backend")
    errores = it.validar_perfil_backend(perfil, "ejemplo.json")
    if errores:
        fallos.append(f"se rechazo el perfil de ejemplo: {errores}")

    caso("un par ILS que no suma 11 se rechaza")
    variante = json.loads(json.dumps(perfil))
    variante["ils"]["activo"] = 7
    if not it.validar_perfil_backend(variante, "variante.json"):
        fallos.append("no se detecto el par ILS que no suma 11")

    caso("un origen distinto de real/sintetico se rechaza")
    variante = json.loads(json.dumps(perfil))
    variante["origen"] = "simulado"
    if not it.validar_perfil_backend(variante, "variante.json"):
        fallos.append("no se detecto el origen invalido")

    caso("perfil_legible usa el formato de entrenamiento")
    canonico = it.perfil_canonico(perfil)
    esperado = "Puntajes brutos:\n" + "\n".join(
        f"{campo.upper()}: " + json.dumps(canonico[campo], ensure_ascii=True)
        for campo in ("chaside", "ils", "personalidad")
    )
    if it.perfil_legible(perfil) != esperado:
        fallos.append("perfil_legible no reproduce el formato del notebook")

    caso("construir_mensajes devuelve system y user")
    mensajes = it.construir_mensajes(perfil)
    if [mensaje["role"] for mensaje in mensajes] != ["system", "user"]:
        fallos.append("los roles no son system y user")
    if mensajes[0]["content"] != it.SYSTEM_E3:
        fallos.append("el system no es SYSTEM_E3")
    if mensajes[1]["content"] != it.perfil_legible(perfil):
        fallos.append("el user no es perfil_legible")

    caso("SYSTEM_E3 coincide con el notebook de E3-08")
    del_notebook = system_del_notebook()
    if del_notebook != it.SYSTEM_E3:
        fallos.append("SYSTEM_E3 divergio del notebook de E3-08")

    caso("la salida de ejemplo cumple estructura, guardrail y rango numerico")
    validacion = it.validar_interpretacion(texto_ok, registro)
    if not validacion["ok"]:
        fallos.append(f"se rechazo la salida de ejemplo: {validacion['errores']}")

    caso("una seccion faltante se detecta")
    roto = texto_ok.replace(it.SECCIONES[3], "## Cierre")
    if not it.validar_estructura(roto):
        fallos.append("no se detecto la seccion faltante")

    caso("las secciones fuera de orden se detectan")
    roto = it.SECCIONES[3] + "\n" + texto_ok
    if not any("orden" in problema for problema in it.validar_estructura(roto)):
        fallos.append("no se detecto el orden incorrecto")

    caso("los titulos en negrita se normalizan a Markdown canonico")
    variante = texto_ok
    for seccion in it.SECCIONES:
        variante = variante.replace(seccion, "**" + seccion[3:] + "**")
    normalizado = it.normalizar_secciones(variante)
    if it.validar_estructura(normalizado):
        fallos.append("no se normalizaron los titulos en negrita")

    caso("los titulos con dos puntos finales se normalizan")
    variante = texto_ok
    for seccion in it.SECCIONES:
        variante = variante.replace(seccion, seccion + ":")
    normalizado = it.normalizar_secciones(variante)
    if it.validar_estructura(normalizado):
        fallos.append("no se normalizaron los titulos con dos puntos")

    caso("la escala 1.0-5.0 y el indice autonomia se rechazan")
    roto = "\n\n".join(it.SECCIONES) + (
        "\nSe uso la escala 1.0-5.0 y el indice autonomia.\n\n" + it.AVISO_NO_CLINICO
    )
    problemas, _ = it.problemas_fidelidad(roto, perfil)
    if not any("prohibido" in problema for problema in problemas):
        fallos.append("no se detecto la escala o el indice prohibido")

    caso("un decimal no nativo se rechaza")
    roto = "\n\n".join(it.SECCIONES) + "\nEl puntaje fue 4.5.\n\n" + it.AVISO_NO_CLINICO
    problemas, _ = it.problemas_fidelidad(roto, perfil)
    if not any("decimal" in problema for problema in problemas):
        fallos.append("no se detecto el decimal")

    caso("un numero mayor a 14 se rechaza")
    roto = "\n\n".join(it.SECCIONES) + "\nEl total fue 20.\n\n" + it.AVISO_NO_CLINICO
    problemas, fuera = it.problemas_fidelidad(roto, perfil)
    if 20 not in fuera or not any("rango nativo" in problema for problema in problemas):
        fallos.append("no se detecto el numero fuera de rango")

    caso("construir_salida arma el JSON con aviso y metricas")
    salida = it.construir_salida(
        perfil,
        "modelo-x",
        texto_ok,
        {"eval_count": 10, "eval_duration": 1_000_000_000, "total_duration": 2_000_000_000},
        1.5,
        validacion,
    )
    if salida["aviso_etico"] != it.AVISO_NO_CLINICO:
        fallos.append("el JSON no incluye el aviso etico")
    if salida["metricas"]["tokens_por_s"] != 10.0:
        fallos.append("la tasa de tokens/s es incorrecta")
    if salida["metricas"]["latencia_s"] != 1.5:
        fallos.append("la latencia es incorrecta")

    caso("escribir_salidas exporta Markdown y JSON")
    with tempfile.TemporaryDirectory() as temporal:
        carpeta = Path(temporal)
        with contextlib.redirect_stdout(io.StringIO()):
            it.escribir_salidas(carpeta, salida)
        if not (carpeta / "ejemplo-dominante.md").exists():
            fallos.append("no se escribio el Markdown")
        if not (carpeta / "ejemplo-dominante.json").exists():
            fallos.append("no se escribio el JSON")

    caso("el CLI exporta una salida valida de extremo a extremo (Ollama simulado)")
    with tempfile.TemporaryDirectory() as temporal:
        original = it.generar_interpretacion
        it.generar_interpretacion = lambda mensajes, modelo, max_tokens: (
            {
                "response": registro["output"],
                "eval_count": 100,
                "eval_duration": 2_000_000_000,
                "total_duration": 3_000_000_000,
            },
            2.0,
        )
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                codigo = it.main(["--perfil", str(RUTA_PERFIL), "--salida-dir", temporal])
        finally:
            it.generar_interpretacion = original
        if codigo != 0:
            fallos.append("el CLI rechazo una salida valida")
        if not (Path(temporal) / "ejemplo-dominante.json").exists():
            fallos.append("el CLI no exporto el JSON de una salida valida")

    caso("el CLI en modo dry-run valida el perfil sin llamar a Ollama")
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        codigo = it.main(["--perfil", str(RUTA_PERFIL), "--dry-run"])
    if codigo != 0:
        fallos.append("el dry-run devolvio codigo distinto de cero")
    if "Puntajes brutos:" not in buffer.getvalue():
        fallos.append("el dry-run no imprimio el prompt")

    caso("un perfil inexistente se rechaza")
    try:
        it.cargar_perfil(RAIZ / "perfiles" / "brutos" / "no-existe.json")
    except SystemExit:
        pass
    else:
        fallos.append("no se rechazo el perfil inexistente")

    caso("el nombre del modelo GGUF es estable y valido para Ollama")
    with tempfile.TemporaryDirectory() as temporal:
        gguf = Path(temporal) / "modelo.gguf"
        gguf.write_bytes(b"GGUF-falso-para-probar-el-hash")
        digest = ig.sha256_archivo(gguf)
        nombre = ig.nombre_modelo(digest)
        if nombre != ig.nombre_modelo(digest):
            fallos.append("el nombre del modelo GGUF no es estable")
        if not re.fullmatch(r"savio-e3-[0-9a-f]{8}", nombre):
            fallos.append(f"el nombre del modelo GGUF no es valido: {nombre}")

    caso("el Modelfile fija CPU, ChatML, temperatura y stop")
    modelfile = ig.construir_modelfile(Path("C:/modelos/savio-e3-q4km.gguf"))
    for fragmento in (
        "FROM C:/modelos/savio-e3-q4km.gguf",
        "TEMPLATE",
        "PARAMETER num_gpu 0",
        "<|im_start|>system",
        "PARAMETER temperature 0.2",
        'PARAMETER stop "<|im_end|>"',
    ):
        if fragmento not in modelfile:
            fallos.append(f"el Modelfile no contiene: {fragmento}")

    caso("--gguf inexistente se rechaza antes de llamar a Ollama")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            it.main(["--perfil", str(RUTA_PERFIL), "--gguf", str(RAIZ / "no-existe.gguf")])
    except SystemExit as exc:
        if exc.code in (0, None):
            fallos.append("--gguf inexistente no devolvio error")
    else:
        fallos.append("--gguf inexistente no se rechazo")

    caso("--gguf y --modelo juntos se rechazan")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            it.main(
                [
                    "--perfil",
                    str(RUTA_PERFIL),
                    "--modelo",
                    "qwen2.5:1.5b",
                    "--gguf",
                    str(RAIZ / "no-existe.gguf"),
                ]
            )
    except SystemExit as exc:
        if exc.code in (0, None):
            fallos.append("la combinacion --gguf y --modelo no devolvio error")
    else:
        fallos.append("la combinacion --gguf y --modelo no se rechazo")

    caso("cada solicitud de inferencia fuerza CPU con num_gpu=0")
    with patch.object(it.requests, "post") as solicitud:
        solicitud.return_value.json.return_value = {"response": "prueba"}
        it.generar_interpretacion(it.construir_mensajes(perfil), "modelo-x", 10)
        if solicitud.call_args.kwargs["json"]["options"].get("num_gpu") != 0:
            fallos.append("la solicitud de inferencia no fuerza CPU")

    caso("las secciones duplicadas se rechazan")
    if not it.validar_estructura(texto_ok + "\n" + it.SECCIONES[0]):
        fallos.append("no se detecto la seccion duplicada")

    caso("las lecturas calculadas no mutan los brutos ni convierten bandas en empates")
    copia = json.loads(json.dumps(perfil))
    lecturas = it.calcular_lecturas(perfil)
    if perfil != copia or lecturas["personalidad"]["extraversion/introversion"]["polo_mayor"] != "introversion":
        fallos.append("la lectura altera datos o invierte el polo mayor")
    if lecturas["chaside"]["I"]["banda"] != "alta" or lecturas["chaside"]["D"]["banda"] != "baja":
        fallos.append("la lectura de CHASIDE no respeta el baremo")

    caso("ILS distingue diferencias 7 y 9 y no permite un empate imposible")
    variante = json.loads(json.dumps(perfil))
    variante["ils"].update(activo=9, reflexivo=2)
    if it.calcular_lecturas(variante)["ils"]["activo/reflexivo"]["banda"] != "sin preferencia clara":
        fallos.append("diferencia ILS 7 se marco como preferencia")
    variante["ils"].update(activo=10, reflexivo=1)
    if it.calcular_lecturas(variante)["ils"]["activo/reflexivo"]["banda"] != "preferencia marcada":
        fallos.append("diferencia ILS 9 no se marco como preferencia")
    variante["ils"].update(activo=5, reflexivo=5)
    try:
        it.calcular_lecturas(variante)
    except ValueError:
        pass
    else:
        fallos.append("se acepto un ILS que no suma 11")

    caso("personalidad distingue diferencia 3, diferencia 4 y empate exacto")
    variante = json.loads(json.dumps(perfil))
    for x, y, banda, empate in ((3, 6, "equilibrado", False), (3, 7, "preferencia", False), (4, 4, "equilibrado", True)):
        variante["personalidad"].update(extraversion=x, introversion=y)
        datos = it.calcular_lecturas(variante)["personalidad"]["extraversion/introversion"]
        if datos["banda"] != banda or datos["empate"] != empate:
            fallos.append("frontera o empate de personalidad incorrectos")

    caso("CHASIDE distingue las fronteras 5/6 y 10/11")
    variante = json.loads(json.dumps(perfil))
    for total, banda in ((5, "baja"), (6, "media"), (10, "media"), (11, "alta")):
        interes = min(total, 10)
        variante["chaside"]["C"].update(interes=interes, aptitud=total-interes, total=total)
        if it.calcular_lecturas(variante)["chaside"]["C"]["banda"] != banda:
            fallos.append(f"frontera de CHASIDE incorrecta para total {total}")

    caso("el refuerzo es opcional y conserva el system original de entrenamiento")
    original = it.construir_mensajes(perfil)
    reforzado = it.construir_mensajes(perfil, True)
    if original[0] != reforzado[0] or original[1]["content"] != it.perfil_legible(perfil):
        fallos.append("el modo original o el system fueron alterados")
    if not reforzado[1]["content"].startswith(original[1]["content"]) or "LECTURA CHASIDE" not in reforzado[1]["content"]:
        fallos.append("el refuerzo no conserva los brutos ni agrega la lectura")
    if it.AVISO_NO_CLINICO not in reforzado[1]["content"]:
        fallos.append("falta el aviso literal en el refuerzo")

    caso("el modo reforzado acepta citas fieles con revision integral pendiente")
    fiel = texto_fiel(perfil)
    validacion = it.validar_interpretacion(fiel, perfil, True)
    if not validacion["ok"] or validacion.get("revision_semantica_integral") != "pendiente":
        fallos.append(f"se rechazo el texto fiel o se omitio el limite semantico: {validacion}")

    caso("el refuerzo detecta un puntaje incorrecto aunque este dentro de rango")
    roto = fiel.replace("extraversion=3", "extraversion=2")
    if it.validar_interpretacion(roto, perfil, True)["ok"]:
        fallos.append("no se detecto la cita incorrecta dentro del rango")

    caso("el refuerzo detecta puntajes omitidos")
    roto = fiel.replace("- C: interes=4, aptitud=2, total=6; banda media.", "")
    if it.validar_interpretacion(roto, perfil, True)["ok"]:
        fallos.append("no se detectaron citas CHASIDE omitidas")

    caso("el refuerzo rechaza equilibrio global falso y banda CHASIDE incorrecta")
    roto = fiel.replace(it.SECCIONES[2], "Todos los ejes son equilibrados.\n" + it.SECCIONES[2])
    roto = roto.replace(it.SECCIONES[3], "I presenta el mayor total en banda media.\n" + it.SECCIONES[3])
    validacion = it.validar_interpretacion(roto, perfil, True)
    if not any("equilibrio global" in e for e in validacion["errores"]) or not any("CHASIDE I" in e for e in validacion["errores"]):
        fallos.append("no se detectaron las contradicciones de bandas")

    caso("el refuerzo detecta un polo invertido con numeros bien copiados")
    roto = fiel.replace(it.SECCIONES[2], "El mayor conteo de extraversion no determina una identidad.\n" + it.SECCIONES[2])
    if not any("invierte el polo" in e for e in it.validar_interpretacion(roto, perfil, True)["errores"]):
        fallos.append("no se detecto el polo invertido")

    caso("una inclinacion compatible fuera de filas se rechaza por formato, no por invertir el polo")
    correcto = fiel.replace(it.SECCIONES[1], "La inclinacion activa no implica un estilo exclusivo.\n" + it.SECCIONES[1])
    validacion = it.validar_interpretacion(correcto, perfil, True)
    if validacion["ok"] or any("invierte el polo" in e for e in validacion["errores"]):
        fallos.append("no se separo el formato acotado de una inclinacion compatible")

    caso("el refuerzo detecta un empate falso y una revision profesional inventada")
    roto = fiel.replace(it.SECCIONES[2], "Hay empate en percepcion.\n" + it.SECCIONES[2])
    roto += "\nFue visto por un profesional."
    errores = it.validar_interpretacion(roto, perfil, True)["errores"]
    if not any("empate inexistente" in e for e in errores) or not any("revision profesional" in e for e in errores):
        fallos.append("no se detecto el empate o la revision profesional")

    caso("el reintento y el dry-run conservan las lecturas calculadas")
    if "LECTURA CHASIDE" not in it.mensaje_correctivo(perfil, ["prueba"], True):
        fallos.append("el reintento perdio la lectura")
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        codigo = it.main(["--perfil", str(RUTA_PERFIL), "--refuerzo-baremos", "--dry-run"])
    if codigo != 0 or "LECTURA CHASIDE" not in buffer.getvalue():
        fallos.append("el CLI no activa el refuerzo en dry-run")

    caso("el CLI reforzado no exporta una salida con contradicciones reconocidas")
    roto = fiel.replace(it.SECCIONES[2], "Todos los ejes son equilibrados.\n" + it.SECCIONES[2])
    with tempfile.TemporaryDirectory() as temporal, patch.object(it, "generar_interpretacion", return_value=({"response": roto}, 0.0)):
        with contextlib.redirect_stdout(io.StringIO()):
            codigo = it.main(["--perfil", str(RUTA_PERFIL), "--refuerzo-baremos", "--salida-dir", temporal])
        if codigo != 1 or list(Path(temporal).iterdir()):
            fallos.append("el CLI reforzado exporto una salida incorrecta")

    caso("la banda CHASIDE junto a puntajes correctos tambien se valida")
    roto = fiel.replace("total=13; banda alta.", "total=13; banda media.")
    if not any("banda junto a puntajes" in e for e in it.validar_interpretacion(roto, perfil, True)["errores"]):
        fallos.append("se acepto una banda incorrecta junto a los puntajes")

    caso("no se acepta otros ejes equilibrados cuando los cuatro tienen preferencia")
    roto = fiel.replace(it.SECCIONES[2], "Los otros ejes son equilibrados.\n" + it.SECCIONES[2])
    if not any("otros ejes equilibrados" in e for e in it.validar_interpretacion(roto, perfil, True)["errores"]):
        fallos.append("se acepto el equilibrio falso de los otros ejes")

    caso("negar un empate inexistente no es afirmar un empate")
    correcto = fiel.replace(it.SECCIONES[2], "No hay empate en percepcion ni decision.\n" + it.SECCIONES[2])
    if any("empate inexistente" in e for e in it.validar_interpretacion(correcto, perfil, True)["errores"]):
        fallos.append("se confundio una negacion de empate con un empate")

    caso("el resumen CHASIDE reconoce altos y listas con conjuncion e")
    roto = fiel.replace(it.SECCIONES[3], "I, S e E tambien son altos.\n" + it.SECCIONES[3])
    if not any("CHASIDE S" in e for e in it.validar_interpretacion(roto, perfil, True)["errores"]):
        fallos.append("no se detecto la banda alta incorrecta de S en una lista")

    caso("un resumen extra aunque sea compatible no cumple las filas acotadas")
    roto = fiel.replace(it.SECCIONES[3], "Se pueden explorar estos resultados.\n" + it.SECCIONES[3])
    if not any("chaside: la seccion" in e for e in it.validar_interpretacion(roto, perfil, True)["errores"]):
        fallos.append("se permitio prosa extra despues de las filas CHASIDE")

    caso("la sintesis no puede volver a clasificar datos aunque la afirmacion sea correcta")
    inicio = fiel.index(it.SECCIONES[3])
    roto = fiel[:inicio] + it.SECCIONES[3] + "\nI tiene total 13 y banda alta.\n" + it.AVISO_NO_CLINICO
    if not any("sintesis: no debe reclasificar" in e for e in it.validar_interpretacion(roto, perfil, True)["errores"]):
        fallos.append("la sintesis permitio volver a clasificar bandas")

    caso("la sintesis requiere contenido y como maximo dos frases")
    for cuerpo in ("", "Explora actividades. Contrasta experiencias. Revisa resultados."):
        roto = fiel[:inicio] + it.SECCIONES[3] + "\n" + cuerpo + "\n" + it.AVISO_NO_CLINICO
        if not any("sintesis: se requieren" in e for e in it.validar_interpretacion(roto, perfil, True)["errores"]):
            fallos.append("la sintesis vacia o extensa se acepto")

    caso("la preposicion A en la sintesis no es el area CHASIDE A")
    correcto = fiel[:inicio] + it.SECCIONES[3] + "\nA partir de actividades concretas se pueden contrastar experiencias de estudio.\n" + it.AVISO_NO_CLINICO
    if not it.validar_interpretacion(correcto, perfil, True)["ok"]:
        fallos.append("se confundio la preposicion A con una reclasificacion CHASIDE")

    caso("las filas tampoco pueden invertir una preferencia con numeros bien copiados")
    roto = fiel.replace("preferencia hacia introversion", "preferencia hacia extraversion")
    if it.validar_interpretacion(roto, perfil, True)["ok"]:
        fallos.append("se acepto una fila con la preferencia invertida")

    caso("la sintesis no puede ser un eco de la instruccion del prompt")
    roto = fiel[:inicio] + it.SECCIONES[3] + "\nPropone actividades o contextos de exploracion compatibles con las lecturas.\n" + it.AVISO_NO_CLINICO
    if not any("repite instrucciones" in e for e in it.validar_interpretacion(roto, perfil, True)["errores"]):
        fallos.append("se acepto una instruccion generica como sintesis")

    caso("la sintesis puede describir una actividad concreta con un recurso")
    correcto = fiel[:inicio] + it.SECCIONES[3] + "\nSe puede analizar un proceso usando un diagrama y registrar observaciones durante su ejecucion.\n" + it.AVISO_NO_CLINICO
    if not it.validar_interpretacion(correcto, perfil, True)["ok"]:
        fallos.append("se rechazo una propuesta concreta sin reclasificaciones")

    print()
    if fallos:
        print(f"FALLOS: {len(fallos)}")
        for fallo in fallos:
            print(f"  - {fallo}")
        return 1

    print("RESULTADO: OK (50/50 chequeos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
