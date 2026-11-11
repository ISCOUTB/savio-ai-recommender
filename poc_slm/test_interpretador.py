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
from pathlib import Path

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

    caso("el Modelfile fija ChatML, temperatura y stop")
    modelfile = ig.construir_modelfile(Path("C:/modelos/savio-e3-q4km.gguf"))
    for fragmento in (
        "FROM C:/modelos/savio-e3-q4km.gguf",
        "TEMPLATE",
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

    print()
    if fallos:
        print(f"FALLOS: {len(fallos)}")
        for fallo in fallos:
            print(f"  - {fallo}")
        return 1

    print("RESULTADO: OK (23/23 chequeos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
