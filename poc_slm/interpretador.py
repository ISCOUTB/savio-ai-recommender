"""interpretador.py - Backend de interpretacion psicometrica integrada (E3-07).

Recibe un perfil bruto (JSON), valida los rangos nativos de CHASIDE,
Felder-Silverman y Personalidad, construye el mismo par system/user con el que
se entrena el SLM de E3-08 y consulta Ollama en CPU. La salida se post-procesa:
cuatro secciones en orden, guardrail etico y chequeo de fidelidad numerica.

Uso (desde la raiz del repositorio):
    python poc_slm/interpretador.py --perfil perfiles/brutos/ejemplo-perfil-bruto-dominante.json
    python poc_slm/interpretador.py --perfil perfiles/reales/persona-1.json --modelo qwen2.5:1.5b
    python poc_slm/interpretador.py --perfil perfiles/brutos/ejemplo-perfil-bruto-dominante.json --gguf modelos/savio-e3-q4km.gguf
    python poc_slm/interpretador.py --perfil perfiles/brutos/ejemplo-perfil-bruto-dominante.json --dry-run
    python poc_slm/interpretador.py --perfil perfiles/brutos/ejemplo-perfil-bruto-dominante.json --salida-dir salidas/e3

El contrato y los baremos no se duplican aqui: viven en
docs/especificaciones/contrato_bruto.py y docs/especificaciones/baremos-psicometricos.md.
El formato de inferencia debe coincidir con SYSTEM_E3 y perfil_legible del
notebook de E3-08; la prueba test_interpretador.py verifica esa coincidencia.
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "docs" / "especificaciones"))
sys.path.insert(0, str(RAIZ / "poc_slm"))

from contrato_bruto import AREAS_CHASIDE, PARES_ILS, validar_perfil_bruto  # noqa: E402
from guardrail_etico import AVISO_NO_CLINICO, agregar_aviso, validar_salida_etica  # noqa: E402
from importar_gguf import importar as importar_modelo_gguf  # noqa: E402

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_DEFAULT = "qwen2.5:1.5b"
MAX_TOKENS_SALIDA = 1200

# Mismo texto que SYSTEM_E3 del notebook de E3-08. Si cambia uno, cambia el otro:
# el modelo se entrena con este contrato y la inferencia debe repetirlo.
SYSTEM_E3 = (
    "Eres un asistente de orientacion psicopedagogica. Recibes los puntajes brutos "
    "de CHASIDE, Felder-Silverman y el test de personalidad, sin transformarlos. "
    "Respondes siempre en cuatro secciones: 1. Estilos de aprendizaje, 2. Rasgos de "
    "personalidad, 3. Perfil vocacional, 4. Sintesis integrada. Citas los puntajes "
    "recibidos, no inventas escalas, no emites diagnosticos ni etiquetas de tipo de "
    "personalidad, y cierras con el aviso de que el perfil es un apoyo al diagnostico "
    "inicial y no reemplaza al profesional."
)

SECCIONES = (
    "## 1. Estilos de aprendizaje",
    "## 2. Rasgos de personalidad",
    "## 3. Perfil vocacional",
    "## 4. Sintesis integrada",
)

EJES_PERSONALIDAD = (
    ("extraversion", "introversion"),
    ("sensing", "intuition"),
    ("thinking", "feeling"),
    ("judging", "perceptive"),
)


def _patron_seccion(numero, titulo):
    return re.compile(
        rf"^\s{{0,3}}(?:#{{1,6}}\s*)?\**\s*{numero}\.\s*{titulo}\s*\**\s*:?\s*$",
        re.IGNORECASE | re.MULTILINE,
    )


# Variantes aceptadas de titulo (Markdown, negrita o texto plano) que se
# normalizan a la forma canonica del corpus antes de validar.
PATRONES_SECCION = {
    "## 1. Estilos de aprendizaje": _patron_seccion(1, "Estilos de aprendizaje"),
    "## 2. Rasgos de personalidad": _patron_seccion(2, "Rasgos de personalidad"),
    "## 3. Perfil vocacional": _patron_seccion(3, "Perfil vocacional"),
    "## 4. Sintesis integrada": _patron_seccion(4, "Sintesis integrada"),
}

CAMPOS_EXTRA = ("diferencial", "fecha_aplicacion")
ORIGENES = {"real", "sintetico"}
RE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,39}$")
RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_DECIMAL = re.compile(r"(?<![\w.])\d+\.\d+(?!\d)")
RE_ENTERO = re.compile(r"(?<![\w.])\d+(?!\w|\.\d)")

# Frases que delatan un reescalado o un indice no validado (directriz 2).
FRASES_PROHIBIDAS = (
    "1.0-5.0",
    "1.0 a 5.0",
    "escala 1.0",
    "escala 1 a 5",
    "autonomia",
)


# --------------------------------------------------------------------------
# Perfil de entrada
# --------------------------------------------------------------------------


def cargar_perfil(ruta):
    """Lee un JSON y valida que sea un perfil bruto aceptable para el backend."""
    if not ruta.exists():
        raise SystemExit(f"[FALLO] no existe el perfil: {ruta}")

    try:
        perfil = json.loads(ruta.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[FALLO] {ruta.name}: JSON invalido ({exc.msg})") from None

    errores = validar_perfil_backend(perfil, ruta.name)
    if errores:
        detalle = "\n  - ".join(errores)
        raise SystemExit(f"[FALLO] {ruta.name}: {len(errores)} hallazgo(s)\n  - {detalle}")
    return perfil


def validar_perfil_backend(perfil, nombre):
    """Valida el perfil con el contrato compartido y las reglas de E3-04.

    `validar-perfiles-brutos.py` sigue siendo el validador canonico de perfiles;
    aqui se replican sus chequeos minimos para que el backend no dependa de un
    script con guion en el nombre.
    """
    errores = validar_perfil_bruto(
        perfil,
        nombre,
        exigir_sintetico=False,
        campos_extra=CAMPOS_EXTRA,
    )
    if not isinstance(perfil, dict):
        return errores

    identificador = perfil.get("id")
    if isinstance(identificador, str) and not RE_ID.match(identificador):
        errores.append(
            f"{nombre}: id invalido; usa solo letras, digitos, punto, guion o guion bajo"
        )

    if perfil.get("origen") not in ORIGENES:
        errores.append(f"{nombre}: origen debe ser 'real' o 'sintetico'")

    fecha = perfil.get("fecha_aplicacion")
    if fecha is not None:
        valida = isinstance(fecha, str) and RE_FECHA.match(fecha)
        if valida:
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
            except ValueError:
                valida = False
        if not valida:
            errores.append(f"{nombre}: fecha_aplicacion debe ser una fecha AAAA-MM-DD")

    return errores


def perfil_canonico(perfil):
    """Reordena los bloques como los genera el corpus de E3-06."""
    return {
        "chaside": {area: dict(perfil["chaside"][area]) for area in AREAS_CHASIDE},
        "ils": {
            polo: perfil["ils"][polo]
            for izquierdo, derecho in PARES_ILS
            for polo in (izquierdo, derecho)
        },
        "personalidad": {
            polo: perfil["personalidad"][polo]
            for izquierdo, derecho in EJES_PERSONALIDAD
            for polo in (izquierdo, derecho)
        },
    }


def perfil_legible(perfil):
    """Mismo formato user que perfil_legible() del notebook de E3-08."""
    canonico = perfil_canonico(perfil)
    lineas = []
    for campo in ("chaside", "ils", "personalidad"):
        lineas.append(f"{campo.upper()}: " + json.dumps(canonico[campo], ensure_ascii=True))
    return "Puntajes brutos:\n" + "\n".join(lineas)


def construir_mensajes(perfil):
    """Par system/user identico al de entrenamiento."""
    return [
        {"role": "system", "content": SYSTEM_E3},
        {"role": "user", "content": perfil_legible(perfil)},
    ]


def mensaje_correctivo(perfil, problemas):
    """Refuerza el contrato cuando el primer intento del SLM no lo cumple."""
    refuerzo = (
        "\n\nCORRECCION OBLIGATORIA: la respuesta anterior fallo por: "
        + "; ".join(problemas)
        + ". Vuelve a redactar las cuatro secciones en orden, cita solo los "
        "puntajes recibidos, no uses escalas distintas, no emitas diagnosticos "
        "ni etiquetas de tipo de personalidad y cierra con el aviso no clinico."
    )
    return perfil_legible(perfil) + refuerzo


# --------------------------------------------------------------------------
# Post-procesamiento y guardrails
# --------------------------------------------------------------------------


def validar_estructura(texto):
    """Devuelve los problemas de las 4 secciones (vacio = estructura correcta)."""
    problemas = []
    posiciones = []
    for seccion in SECCIONES:
        posicion = texto.find(seccion)
        if posicion < 0:
            problemas.append(f"falta la seccion: {seccion}")
        else:
            posiciones.append(posicion)
    if len(posiciones) == len(SECCIONES) and posiciones != sorted(posiciones):
        problemas.append("las secciones no estan en orden")
    return problemas


def normalizar_secciones(texto):
    """Lleva los titulos a la forma canonica `## N. Titulo` sin tocar el contenido.

    Acepta variantes con negrita, con otro nivel de `#` o sin marca Markdown. No
    corrige secciones faltantes ni cambia puntajes: solo la forma del titulo.
    """
    for canonico, patron in PATRONES_SECCION.items():
        texto = patron.sub(canonico, texto)
    return texto


def problemas_fidelidad(texto, perfil):
    """Chequeos numericos y de escala. Devuelve (problemas, numeros_fuera_rango).

    Es una comprobacion automatica, no una rubrica psicometrica: la fidelidad
    exacta frente al ground truth se mide en E3-09. Aqui se rechazan los errores
    inequivocos (decimales, escala 1.0-5.0, `autonomia`) y se reportan los
    enteros fuera del rango nativo 0-14.
    """
    cuerpo = texto
    for seccion in SECCIONES:
        cuerpo = cuerpo.replace(seccion, " ")

    bajo = cuerpo.lower()
    problemas = []
    for frase in FRASES_PROHIBIDAS:
        if frase in bajo:
            problemas.append(f"usa una escala o indice prohibido: {frase}")

    for decimal in sorted(set(RE_DECIMAL.findall(cuerpo))):
        problemas.append(f"usa un valor decimal no nativo: {decimal}")

    fuera_rango = sorted({int(valor) for valor in RE_ENTERO.findall(cuerpo) if int(valor) > 14})
    if fuera_rango:
        problemas.append(
            "numeros fuera del rango nativo 0-14: "
            + ", ".join(str(valor) for valor in fuera_rango)
        )

    return problemas, fuera_rango


def validar_interpretacion(texto, perfil):
    """Valida estructura, guardrail etico y fidelidad numerica de una salida."""
    estructura = validar_estructura(texto)
    etica = validar_salida_etica(texto)
    fidelidad, fuera_rango = problemas_fidelidad(texto, perfil)
    errores = estructura + etica + fidelidad
    return {
        "ok": not errores,
        "estructura_ok": not estructura,
        "errores": errores,
        "numeros_fuera_rango": fuera_rango,
    }


# --------------------------------------------------------------------------
# Inferencia en Ollama
# --------------------------------------------------------------------------


def generar_interpretacion(mensajes, modelo, max_tokens):
    """Envia el par system/user a Ollama y devuelve (respuesta_json, segundos)."""
    payload = {
        "model": modelo,
        "system": mensajes[0]["content"],
        "prompt": mensajes[1]["content"],
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.2},
    }
    inicio = time.perf_counter()
    try:
        respuesta = requests.post(OLLAMA_URL, json=payload, timeout=600)
        respuesta.raise_for_status()
    except requests.ConnectionError:
        raise SystemExit(
            "[FALLO] no se pudo conectar con Ollama en http://localhost:11434\n"
            "        Verifica que el servicio este corriendo (ollama serve o la app)."
        ) from None
    except requests.Timeout:
        raise SystemExit("[FALLO] la solicitud a Ollama agoto el tiempo de espera (600 s).") from None
    except requests.HTTPError as exc:
        raise SystemExit(f"[FALLO] Ollama respondio con error HTTP: {exc}") from None
    return respuesta.json(), time.perf_counter() - inicio


# --------------------------------------------------------------------------
# Salida
# --------------------------------------------------------------------------


def construir_salida(perfil, modelo, texto, resultado, latencia, validacion, gguf_sha256=None):
    """Arma el objeto JSON exportable con metadatos y metricas."""
    eval_count = int(resultado.get("eval_count", 0) or 0)
    eval_duration_ns = int(resultado.get("eval_duration", 0) or 0)
    tokens_por_s = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns else 0.0
    total_duration_ms = (resultado.get("total_duration", 0) or 0) / 1e6
    salida = {
        "id": perfil.get("id"),
        "origen": perfil.get("origen"),
        "modelo": modelo,
        "fecha_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "perfil_markdown": texto,
        "aviso_etico": AVISO_NO_CLINICO,
        "validacion": validacion,
        "metricas": {
            "latencia_s": round(latencia, 2),
            "tokens_generados": eval_count,
            "tokens_por_s": round(tokens_por_s, 2),
            "total_duration_ms": round(total_duration_ms, 1),
        },
    }
    if gguf_sha256:
        salida["gguf_sha256"] = gguf_sha256
    return salida


def escribir_salidas(carpeta, salida):
    """Escribe <id>.md y <id>.json en la carpeta indicada."""
    carpeta.mkdir(parents=True, exist_ok=True)
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", str(salida.get("id") or "perfil")).strip("-")
    base = base or "perfil"

    metadatos = (
        f"> Modelo: {salida['modelo']} | Latencia: {salida['metricas']['latencia_s']:.2f} s"
        f" | Tokens: {salida['metricas']['tokens_generados']}"
        f" | Validacion: {'OK' if salida['validacion']['ok'] else 'FALLO'}"
    )
    ruta_md = carpeta / f"{base}.md"
    ruta_json = carpeta / f"{base}.json"
    ruta_md.write_text(f"{metadatos}\n\n{salida['perfil_markdown']}\n", encoding="utf-8")
    ruta_json.write_text(
        json.dumps(salida, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Salida guardada en: {ruta_md}")
    print(f"Salida guardada en: {ruta_json}")


def imprimir_resumen(salida):
    metricas = salida["metricas"]
    print("-" * 70)
    print(f"Modelo     : {salida['modelo']}")
    print(f"Latencia   : {metricas['latencia_s']:.2f} s (total)")
    print(f"Generacion : {metricas['tokens_generados']} tokens a ~{metricas['tokens_por_s']:.1f} tokens/s")
    print(f"Validacion : {'OK' if salida['validacion']['ok'] else 'FALLO'}")
    print("=" * 70)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def construir_parser():
    parser = argparse.ArgumentParser(
        description="Interpretacion psicometrica integrada con SLM local (E3-07)."
    )
    parser.add_argument("--perfil", required=True, help="JSON con el perfil bruto de entrada")
    parser.add_argument(
        "--modelo",
        help=f"modelo de Ollama (default: {MODELO_DEFAULT}); incompatible con --gguf",
    )
    parser.add_argument(
        "--gguf",
        type=Path,
        help="GGUF ajustado de E3-08; se importa en Ollama y se usa como modelo",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=MAX_TOKENS_SALIDA,
        help=f"tope de tokens generados (default: {MAX_TOKENS_SALIDA})",
    )
    parser.add_argument(
        "--reintentos",
        type=int,
        default=1,
        help="intentos totales si la salida no cumple el contrato (default: 1)",
    )
    parser.add_argument(
        "--salida-dir",
        type=Path,
        help="carpeta donde escribir <id>.md y <id>.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="valida el perfil y muestra el prompt sin llamar a Ollama",
    )
    return parser


def main(argv=None):
    args = construir_parser().parse_args(argv)
    if args.reintentos < 1:
        raise SystemExit("[FALLO] --reintentos debe ser 1 o mas")
    if args.max_tokens < 1:
        raise SystemExit("[FALLO] --max-tokens debe ser 1 o mas")
    if args.gguf and args.modelo:
        raise SystemExit("[FALLO] usa --gguf o --modelo, no ambos: el GGUF ya define el modelo.")

    perfil = cargar_perfil(Path(args.perfil))
    mensajes = construir_mensajes(perfil)

    modelo = args.modelo or MODELO_DEFAULT
    gguf_sha256 = None
    if args.gguf:
        info_gguf = importar_modelo_gguf(args.gguf, dry_run=args.dry_run)
        modelo = info_gguf["nombre"]
        gguf_sha256 = info_gguf["sha256"]
        estado = "importacion omitida en --dry-run" if args.dry_run else "importado en Ollama"
        print(f"[OK] GGUF {info_gguf['ruta']} -> modelo {modelo} ({estado})")

    if args.dry_run:
        print(f"[OK] perfil bruto valido: {perfil.get('id')}")
        print("=" * 70)
        print("SYSTEM:")
        print(mensajes[0]["content"])
        print("-" * 70)
        print("USER:")
        print(mensajes[1]["content"])
        print("=" * 70)
        return 0

    validacion = None
    resultado = {}
    texto = ""
    latencia = 0.0

    for intento in range(1, args.reintentos + 1):
        contenido = (
            mensajes[1]["content"]
            if intento == 1
            else mensaje_correctivo(perfil, validacion["errores"])
        )
        resultado, latencia = generar_interpretacion(
            [mensajes[0], {"role": "user", "content": contenido}],
            modelo,
            args.max_tokens,
        )
        texto = agregar_aviso(
            normalizar_secciones(resultado.get("response", "").strip())
        )
        validacion = validar_interpretacion(texto, perfil)
        if validacion["ok"]:
            break
        print(f"[AVISO] intento {intento}/{args.reintentos} rechazado:")
        for error in validacion["errores"]:
            print(f"  - {error}")

    if not validacion["ok"]:
        print("[FALLO] la salida no cumple el contrato de E3-07; no se exporta.")
        print("-" * 70)
        print(texto)
        print("-" * 70)
        return 1

    salida = construir_salida(
        perfil, modelo, texto, resultado, latencia, validacion, gguf_sha256=gguf_sha256
    )
    print(salida["perfil_markdown"])
    imprimir_resumen(salida)
    if args.salida_dir:
        escribir_salidas(args.salida_dir, salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
