"""prompt_builder.py - Prompt Builder semanal de la Entrega 2 (E2-10).

Toma el perfil consolidado del estudiante (E2-07) y los recursos A/B/C de la
semana (E2-08), construye el prompt in-context, lo envia al SLM local via la
API de Ollama y devuelve la recomendacion estructurada: recurso elegido,
justificacion pedagogica y descarte de las otras dos opciones.

Uso (desde la raiz del repositorio):
    python poc_slm/prompt_builder.py \
        --perfil perfiles/ejemplo-perfil-estudiante.json \
        --recursos poc_slm/recursos/semana_1.json --refuerzo

    # Revisar el prompt sin llamar a Ollama
    python poc_slm/prompt_builder.py --perfil ... --recursos ... --dry-run

    # Salida maquina-legible (para E2-11 y E2-12)
    python poc_slm/prompt_builder.py --perfil ... --recursos ... --json

    # Permutar el orden de los recursos (control de sesgo de posicion)
    python poc_slm/prompt_builder.py --perfil ... --recursos ... --orden aleatorio --semilla 7

Dependencias: requests y jsonschema (ambas en requirements.txt).
"""

import argparse
import hashlib
import json
import random
import re
import sys
import time
import unicodedata
from pathlib import Path

import jsonschema
import requests

# Forzar salida en UTF-8 para evitar caracteres corruptos en Windows / PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_DEFAULT = "qwen2.5:1.5b"
MAX_TOKENS_SALIDA = 500  # 3 secciones (recomendado, justificacion, descarte).
TEMPERATURA_DEFAULT = 0.4  # Decision estable; el benchmark de Entrega 1 usa 0.7.

SYSTEM_PROMPT_PATH = RAIZ / "prompts" / "system_prompt_recomendacion.md"
SCHEMA_PERFIL = RAIZ / "docs" / "especificaciones" / "perfil-estudiante.schema.json"
SCHEMA_RECURSO = RAIZ / "docs" / "especificaciones" / "recurso-semanal.schema.json"

ETIQUETAS_ESTILOS = {
    "activo_reflexivo": ("activo", "reflexivo"),
    "sensorial_intuitivo": ("sensorial", "intuitivo"),
    "visual_verbal": ("visual", "verbal"),
    "secuencial_global": ("secuencial", "global"),
}

ETIQUETAS_PERSONALIDAD = {
    "introversion_extraversion": ("introversion", "extraversion"),
    "autonomia": ("baja autonomia", "alta autonomia"),
    "metodicidad": ("baja metodicidad", "alta metodicidad"),
    "apertura": ("baja apertura", "alta apertura"),
}

# Patron de enlaces: si el modelo lo usa, se rompe la regla 3 del system prompt.
RE_URL = re.compile(r"(https?://|www\.)\S+", re.IGNORECASE)

RE_ENCABEZADO = re.compile(r"^\s{0,3}(?:#{1,6}\s*(.+?)\s*|\*\*(.+?)\*\*\s*:?\s*)$")


# ---------------------------------------------------------------------------
# Carga y validacion de entradas
# ---------------------------------------------------------------------------

def _cargar_json(ruta: Path) -> dict | list:
    """Lee un JSON con UTF-8 y un mensaje de error accionable."""
    if not ruta.exists():
        print(f"[ERROR] No existe el archivo: {ruta}", file=sys.stderr)
        sys.exit(1)
    try:
        with ruta.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON invalido en {ruta}: {e}", file=sys.stderr)
        sys.exit(1)


def _validar_contra_schema(doc, schema_path: Path, etiqueta: str) -> None:
    """Valida un documento contra un schema draft-07 y corta con detalle si falla."""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errores = sorted(jsonschema.Draft7Validator(schema).iter_errors(doc), key=lambda e: list(e.path))
    if errores:
        print(f"[ERROR] {etiqueta} no cumple {schema_path.name}:", file=sys.stderr)
        for e in errores:
            ruta = " -> ".join(str(p) for p in e.path) or "(raiz)"
            print(f"        {ruta}: {e.message}", file=sys.stderr)
        print("        Corrige el archivo o usa uno de los fixtures de perfiles/.", file=sys.stderr)
        sys.exit(1)


def cargar_perfil(ruta: Path) -> dict:
    """Carga y valida el perfil consolidado del estudiante (E2-07)."""
    perfil = _cargar_json(ruta)
    if not isinstance(perfil, dict):
        print(f"[ERROR] El perfil debe ser un objeto JSON: {ruta}", file=sys.stderr)
        sys.exit(1)
    _validar_contra_schema(perfil, SCHEMA_PERFIL, "El perfil")
    return perfil


def cargar_recursos(ruta: Path) -> list[dict]:
    """Carga y valida los recursos de la semana (E2-08): 3 opciones A, B y C."""
    recursos = _cargar_json(ruta)
    if not isinstance(recursos, list) or not recursos:
        print(f"[ERROR] Los recursos deben ser un arreglo JSON no vacio: {ruta}", file=sys.stderr)
        sys.exit(1)
    for recurso in recursos:
        _validar_contra_schema(recurso, SCHEMA_RECURSO, "Un recurso")
    opciones = sorted(r.get("opcion") for r in recursos)
    if opciones != ["A", "B", "C"]:
        print(f"[ERROR] Se esperaban exactamente las opciones A, B y C; llego {opciones}", file=sys.stderr)
        sys.exit(1)
    ids = {r["recurso_id"] for r in recursos}
    if len(ids) != 3:
        print(f"[ERROR] Los recurso_id deben ser unicos; llego {sorted(ids)}", file=sys.stderr)
        sys.exit(1)
    semanas = {r["semana"] for r in recursos}
    if len(semanas) != 1:
        print(f"[ERROR] Los tres recursos deben ser de la misma semana; llego {sorted(semanas)}", file=sys.stderr)
        sys.exit(1)
    return recursos


def cargar_system_prompt() -> str:
    """Carga el system prompt de recomendacion semanal (E2-10)."""
    if not SYSTEM_PROMPT_PATH.exists():
        print(f"[ERROR] No se encontro el system prompt: {SYSTEM_PROMPT_PATH}", file=sys.stderr)
        sys.exit(1)
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()


# ---------------------------------------------------------------------------
# Construccion del prompt
# ---------------------------------------------------------------------------

def _tabla_puntajes(puntajes: dict, etiquetas: dict) -> list[str]:
    """Formatea puntajes 1.0-5.0 con su polo bajo/alto para que el modelo no adivine."""
    lineas = []
    for clave, valor in puntajes.items():
        izq, der = etiquetas.get(clave, ("polo bajo", "polo alto"))
        if valor <= 2.1:
            lectura = f"preferencia por {izq}"
        elif valor >= 3.9:
            lectura = f"preferencia por {der}"
        else:
            lectura = "equilibrado (sin preferencia clara)"
        lineas.append(f"  - {clave} ({izq} <-> {der}): {valor} -> {lectura}")
    return lineas


def texto_perfil(perfil: dict) -> str:
    """Bloque de perfil para el prompt: textos ya redactados + puntajes con lectura."""
    estilos = perfil["estilos_aprendizaje"]
    personalidad = perfil["personalidad"]
    chaside = perfil["chaside"]

    lineas = [
        f"- Estudiante: {perfil['estudiante_id']} (perfil de origen {perfil['origen']})",
        f"- Modelo de estilos: {estilos['modelo']}",
        f"- Preferencias declaradas: {', '.join(estilos['preferencias']) or 'ninguna (perfil equilibrado)'}",
        f"- Descripcion de estilos: {estilos['descripcion_para_prompt']}",
        "- Puntajes de estilos (escala 1.0 a 5.0):",
    ]
    lineas += _tabla_puntajes(estilos["puntajes"], ETIQUETAS_ESTILOS)

    lineas.append("- Rasgos de personalidad (escala 1.0 a 5.0):")
    lineas += _tabla_puntajes(personalidad["rasgos"], ETIQUETAS_PERSONALIDAD)
    if personalidad.get("resumen_conductual"):
        lineas.append(f"- Resumen conductual: {personalidad['resumen_conductual']}")
    preferencias_trabajo = personalidad.get("preferencias_trabajo") or []
    lineas.append(
        "- Preferencias de trabajo: "
        + (", ".join(preferencias_trabajo) if preferencias_trabajo else "sin preferencias claras")
    )

    lineas.append("- Areas CHASIDE (escala 1.0 a 5.0):")
    lineas.append("  - " + ", ".join(f"{area}={valor}" for area, valor in chaside["areas"].items()))
    lineas.append(f"- Areas dominantes: {', '.join(chaside.get('areas_dominantes') or []) or 'sin areas dominantes'}")
    if chaside.get("descripcion_para_analogias"):
        lineas.append(f"- Analogias sugeridas: {chaside['descripcion_para_analogias']}")

    if all(round(v, 1) == 3.0 for v in estilos["puntajes"].values()):
        lineas.append(
            "- AVISO DE PERFIL INCOMPLETO: todos los estilos estan en 3.0, lo que significa "
            "falta de datos (test de estilos no diligenciado), no un estudiante neutro. "
            "Recomienda de forma conservadora y dilo explicitamente."
        )

    return "\n".join(lineas)


def texto_recursos(recursos: list[dict]) -> str:
    """Lista de recursos en el orden recibido, con los campos que el modelo debe cruzar."""
    bloques = []
    for i, recurso in enumerate(recursos, start=1):
        bloques.append(
            f"Opcion {i} - {recurso['recurso_id']}\n"
            f"  - Titulo: {recurso['titulo']}\n"
            f"  - Tipo: {recurso['tipo']} | Formato: {recurso['formato']} | Nivel: {recurso['nivel']}\n"
            f"  - Carga estimada: {recurso['carga_estimada_min']} min\n"
            f"  - Tema: {recurso['tema']}\n"
            f"  - Resumen: {recurso['resumen']}"
        )
    return "\n\n".join(bloques)


def refuerzo_reglas(perfil: dict) -> str:
    """Mitigacion V2: repite las reglas criticas dentro del prompt de usuario.

    Los SLMs de 1.5B-2B tienden a ignorar el system prompt (hallazgo del Sprint 3);
    el refuerzo nombra las preferencias reales del estudiante y el formato exacto.
    """
    estilos = perfil["estilos_aprendizaje"]
    preferencias = ", ".join(estilos["preferencias"]) or "sin preferencia clara"
    return (
        "\nRECUERDA LAS REGLAS CRITICAS DE ESTA TAREA:\n"
        "1. Elige UNO de los tres recursos entregados, por su identificador exacto. "
        "No inventes recursos ni opciones distintas.\n"
        f"2. ESTE ESTUDIANTE TIENE ESTAS PREFERENCIAS: {preferencias}. "
        f"Descripcion: {estilos['descripcion_para_prompt']}\n"
        "3. Usa solo los datos del perfil. No inventes fortalezas ni afirmes certeza psicologica.\n"
        "4. NUNCA incluyas URLs, enlaces, titulos de libros ni autores.\n"
        "5. Respeta el formato exacto: '## Recurso recomendado', '## Justificacion pedagogica' "
        "y '## Razon de descarte' con los dos recursos no elegidos, uno por linea.\n"
        "6. El nivel del recurso es demanda cognitiva, no calidad; el orden de la lista no es una senal.\n"
    )


def ordenar_recursos(recursos: list[dict], modo: str = "abc", semilla: int | None = None) -> list[dict]:
    """Devuelve los recursos en orden alfabetico o en orden aleatorio reproducible."""
    copia = sorted(recursos, key=lambda r: r["opcion"])
    if modo == "abc":
        return copia
    random.Random(semilla).shuffle(copia)
    return copia


def construir_prompt(perfil: dict, recursos: list[dict], refuerzo: bool = True, mensaje: str | None = None) -> str:
    """Ensambla el prompt de usuario con el perfil y los recursos en el orden dado."""
    semana = recursos[0]["semana"]
    tema = recursos[0]["tema"]
    prompt = (
        "Tarea: recomendar un recurso de estudio para esta semana academica.\n\n"
        f"SEMANA: {semana}\n"
        f"TEMA Y OBJETIVO DE APRENDIZAJE: {tema}\n"
        "Los tres recursos cubren el mismo tema y el mismo objetivo; cambian el canal, "
        "la demanda cognitiva y el tiempo.\n\n"
        "PERFIL DEL ESTUDIANTE:\n"
        f"{texto_perfil(perfil)}\n\n"
        "RECURSOS DISPONIBLES:\n"
        f"{texto_recursos(recursos)}\n"
    )
    if mensaje:
        prompt += f'\nMENSAJE DEL ESTUDIANTE: "{mensaje}"\n'
    if refuerzo:
        prompt += refuerzo_reglas(perfil)
    prompt += (
        "\nEntrega la recomendacion con el formato exacto indicado en tus instrucciones: "
        "recurso recomendado por identificador y titulo, justificacion pedagogica y razon "
        "de descarte de los otros dos recursos."
    )
    return prompt


# ---------------------------------------------------------------------------
# Inferencia
# ---------------------------------------------------------------------------

def llamar_ollama(system_prompt: str, prompt_usuario: str, modelo: str, temperatura: float) -> dict:
    """Envia el prompt a Ollama (POST /api/generate) y retorna la respuesta completa."""
    payload = {
        "model": modelo,
        "system": system_prompt,
        "prompt": prompt_usuario,
        "stream": False,
        "options": {"num_predict": MAX_TOKENS_SALIDA, "temperature": temperatura},
    }
    try:
        respuesta = requests.post(OLLAMA_URL, json=payload, timeout=300)
        respuesta.raise_for_status()
    except requests.ConnectionError:
        print(
            "[ERROR] No se pudo conectar con Ollama en http://localhost:11434\n"
            "        Verifica que el servicio este corriendo (ollama serve o la app de Ollama).",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.Timeout:
        print("[ERROR] La solicitud a Ollama agoto el tiempo de espera (300 s).", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"[ERROR] Ollama respondio con error HTTP: {e}", file=sys.stderr)
        print(
            "        Si el modelo no esta descargado: ollama pull " + modelo,
            file=sys.stderr,
        )
        sys.exit(1)
    return respuesta.json()


# ---------------------------------------------------------------------------
# Parseo y validacion de la salida
# ---------------------------------------------------------------------------

def _normalizar(texto: str) -> str:
    """Minusculas sin tildes, para comparar encabezados."""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sin_tildes.strip().lower()


def _seccion_de(encabezado: str) -> str | None:
    """Mapea un encabezado a una de las tres secciones esperadas."""
    titulo = _normalizar(encabezado).strip(" :")
    if "recomendad" in titulo:
        return "recomendado"
    if "justificaci" in titulo:
        return "justificacion"
    if "descarte" in titulo:
        return "descarte"
    return None


def _partir_secciones(texto: str) -> dict[str, str]:
    """Parte la salida en secciones por encabezados Markdown o negritas."""
    secciones: dict[str, list[str]] = {}
    actual: str | None = None
    for linea in texto.splitlines():
        match = RE_ENCABEZADO.match(linea)
        if match:
            titulo = match.group(1) or match.group(2) or ""
            clave = _seccion_de(titulo)
            if clave:
                actual = clave
                secciones.setdefault(clave, [])
                resto = linea.split(":", 1)
                if len(resto) == 2 and resto[1].strip():
                    secciones[clave].append(resto[1].strip())
                continue
        if actual:
            secciones[actual].append(linea)
    return {clave: "\n".join(lineas).strip() for clave, lineas in secciones.items()}


def _buscar_recurso(texto: str, recursos: list[dict]) -> str | None:
    """Busca un recurso_id exacto o una opcion A/B/C suelta en un texto corto."""
    por_id = {r["recurso_id"]: r for r in recursos}
    match = re.search(r"\btde-[a-z0-9\-]+-[ABC]\b", texto, re.IGNORECASE)
    if match:
        candidato = next((rid for rid in por_id if rid.lower() == match.group(0).lower()), None)
        if candidato:
            return candidato
    match = re.search(r"\b(?:opcion|recurso)\s*[:\-]?\s*`?([ABC])`?\b", texto, re.IGNORECASE)
    if match:
        return next((r["recurso_id"] for r in recursos if r["opcion"] == match.group(1).upper()), None)
    # Respuesta minima del tipo "A - Mapa interactivo" al inicio de una linea.
    match = re.search(r"^\s*`?\(?([ABC])\)?`?\s*[-\u2013:]", texto, re.MULTILINE)
    if match:
        return next((r["recurso_id"] for r in recursos if r["opcion"] == match.group(1).upper()), None)
    return None


def _recurso_de_linea(linea: str, recursos: list[dict]) -> str | None:
    """Detecta si una linea del bloque de descarte abre un recurso nuevo."""
    for recurso in recursos:
        if re.search(re.escape(recurso["recurso_id"]), linea, re.IGNORECASE):
            return recurso["recurso_id"]
    match = re.match(r"^`?\(?([ABC])\)?`?\s*[-\u2013:]", linea)
    if match:
        return next((r["recurso_id"] for r in recursos if r["opcion"] == match.group(1)), None)
    return None


def _limpiar_motivo(motivo: str, titulo: str) -> str:
    """Quita el titulo del recurso y los separadores que el modelo deja delante del motivo."""
    motivo = re.sub(r"\s+", " ", motivo).strip()
    motivo = re.sub(r"^[\s:\-\u2013]+", "", motivo)
    if titulo:
        exacto = re.compile(r"^`?\s*" + re.escape(titulo.strip()) + r"\s*[:\-\u2013]?\s*", re.IGNORECASE)
        motivo = exacto.sub("", motivo)
    motivo = re.sub(r"^[\s:\-\u2013]+", "", motivo)
    motivo = re.sub(r"[\s:\-\u2013]+$", "", motivo)
    return motivo.strip()


def _motivos_descarte(texto: str, recursos: list[dict]) -> dict[str, str]:
    """Asocia cada motivo del bloque de descarte al recurso que lo precede.

    Acepta las tres formas que producen los SLM: una linea por recurso, una
    linea con el id seguida de vinetas, o la letra de la opcion. Una linea que
    solo repite el titulo no cuenta como motivo.
    """
    titulos = {r["recurso_id"]: r["titulo"] for r in recursos}
    motivos: dict[str, str] = {}
    actual: str | None = None
    buffer: list[str] = []

    def cerrar() -> None:
        if not actual or not buffer:
            return
        motivo = _limpiar_motivo(" ".join(buffer), titulos.get(actual, ""))
        if len(motivo) >= 15 and actual not in motivos:
            motivos[actual] = motivo

    for linea in texto.splitlines():
        limpia = linea.strip().lstrip("-*0123456789. ").strip()
        if not limpia:
            continue
        detectado = _recurso_de_linea(limpia, recursos)
        if detectado:
            cerrar()
            actual = detectado
            resto = re.sub(re.escape(detectado), "", limpia, count=1, flags=re.IGNORECASE)
            resto = re.sub(rf"^`?\(?{next(r['opcion'] for r in recursos if r['recurso_id'] == detectado)}\)?`?", "", resto).strip()
            buffer = [resto] if resto else []
        elif actual:
            buffer.append(limpia)
    cerrar()
    return motivos


def parsear_salida(texto: str, recursos: list[dict]) -> dict:
    """Extrae recurso elegido, justificacion y descarte de la respuesta del modelo."""
    secciones = _partir_secciones(texto)
    bloque_recomendado = secciones.get("recomendado", "")
    ids = {r["recurso_id"] for r in recursos}
    elegido = None
    if bloque_recomendado:
        # Si el modelo escribe un id con formato valido, se usa tal cual: si no
        # existe en el catalogo, la validacion lo reporta en vez de adivinar otro.
        candidatos = re.findall(r"\btde-[a-z0-9\-]+-[A-Z0-9]\b", bloque_recomendado, re.IGNORECASE)
        for candidato in candidatos:
            real = next((rid for rid in ids if rid.lower() == candidato.lower()), None)
            elegido = real if real else candidato.lower()
            break
        if elegido is None:
            elegido = _buscar_recurso(bloque_recomendado, recursos)
    if elegido is None:
        # Ultimo recurso: primer id mencionado en cualquier parte de la respuesta.
        elegido = _buscar_recurso(texto, recursos)

    justificacion = secciones.get("justificacion", "").strip()
    bloque_descarte = secciones.get("descarte", "")
    descarte = {
        recurso_id: motivo
        for recurso_id, motivo in _motivos_descarte(bloque_descarte, recursos).items()
        if recurso_id != elegido
    }

    return {
        "recurso_elegido": elegido,
        "opcion": next((r["opcion"] for r in recursos if r["recurso_id"] == elegido), None),
        "titulo": next((r["titulo"] for r in recursos if r["recurso_id"] == elegido), None),
        "justificacion": justificacion,
        "descarte": descarte,
        "secciones_detectadas": sorted(secciones),
    }


def validar_salida(datos: dict, recursos: list[dict], texto_completo: str) -> list[str]:
    """Aplica los criterios de guardrails y de forma. Devuelve la lista de errores."""
    errores = []
    ids = {r["recurso_id"] for r in recursos}
    elegido = datos.get("recurso_elegido")

    if elegido not in ids:
        errores.append(
            f"recurso_elegido invalido: {elegido!r}. Debe ser uno de {sorted(ids)}."
        )
    if len(datos.get("justificacion", "")) < 40:
        errores.append("justificacion ausente o demasiado corta (minimo 40 caracteres).")
    for recurso_id in ids - {elegido}:
        if recurso_id not in datos.get("descarte", {}):
            errores.append(f"falta el descarte de {recurso_id}.")
    urls = RE_URL.findall(texto_completo)
    if urls:
        errores.append(f"la respuesta incluye enlaces prohibidos: {urls[:3]}.")
    if "secciones_detectadas" in datos and len(datos["secciones_detectadas"]) < 3:
        errores.append(
            f"se detectaron {len(datos['secciones_detectadas'])} de 3 secciones "
            f"({datos['secciones_detectadas']}); revisa el formato."
        )
    return errores


def recomendacion_id(perfil: dict, recursos: list[dict], semilla: int) -> str:
    """Identificador estable para que E2-11 registre feedback sobre esta recomendacion."""
    base = json.dumps(perfil, sort_keys=True, ensure_ascii=True) + f"|{recursos[0]['semana']}|{semilla}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:8]
    return f"rec-{perfil['estudiante_id']}-s{recursos[0]['semana']}-{digest}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def imprimir_humano(datos: dict, resultado: dict, modelo: str, duracion: float, errores: list[str]) -> None:
    """Salida para consola: respuesta completa + metadatos + validacion."""
    eval_count = resultado.get("eval_count", 0)
    eval_duration_ns = resultado.get("eval_duration", 0)
    tokens_por_seg = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns else 0.0

    print("=" * 72)
    print("SAVIO - Recomendacion semanal personalizada (E2-10)")
    print("=" * 72)
    print(f"Recomendacion : {datos['recomendacion_id']}")
    print(f"Estudiante    : {datos['estudiante_id']}")
    print(f"Semana        : {datos['semana']}")
    print(f"Orden recursos: {' -> '.join(datos['orden'])}")
    print("-" * 72)
    print(datos["respuesta_md"].strip())
    print("-" * 72)
    print(f"Recurso elegido: {datos['recurso_elegido']} (opcion {datos['opcion']})")
    print(f"Modelo         : {modelo}")
    print(f"Latencia       : {duracion:.1f} s (total)")
    print(f"Generacion     : {eval_count} tokens a ~{tokens_por_seg:.1f} tokens/s")
    if errores:
        print("Validacion     : FALLO")
        for error in errores:
            print(f"  - {error}")
    else:
        print("Validacion     : OK (recurso valido, justificacion y descarte completos, sin enlaces)")
    print("=" * 72)


def guardar_json(datos: dict, ruta: Path) -> None:
    """Guarda la recomendacion estructurada (insumo de E2-11 y E2-12)."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"JSON guardado en: {ruta}")


def guardar_markdown(texto: str, datos: dict, ruta: Path) -> None:
    """Guarda la respuesta del modelo con metadatos minimos."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    metadatos = (
        f"> Recomendacion: {datos['recomendacion_id']} | Estudiante: {datos['estudiante_id']} "
        f"| Semana: {datos['semana']} | Modelo: {datos['modelo']}\n"
        f"> Recurso elegido: {datos['recurso_elegido']} (opcion {datos['opcion']}) "
        f"| Orden: {' -> '.join(datos['orden'])} | Validacion: "
        f"{'OK' if not datos['validacion']['errores'] else 'FALLO'}"
    )
    ruta.write_text(f"{metadatos}\n\n{texto.strip()}\n", encoding="utf-8")
    print(f"Markdown guardado en: {ruta}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prompt Builder semanal E2-10: perfil + recursos A/B/C -> Ollama -> recomendacion."
    )
    parser.add_argument("--perfil", required=True, help="Ruta al JSON del perfil (E2-07).")
    parser.add_argument("--recursos", required=True, help="Ruta al JSON de recursos de la semana (E2-08).")
    parser.add_argument("--modelo", default=MODELO_DEFAULT, help=f"Modelo de Ollama (default: {MODELO_DEFAULT}).")
    parser.add_argument(
        "--refuerzo",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Repite las reglas criticas en el prompt de usuario (default: activo).",
    )
    parser.add_argument("--orden", choices=["abc", "aleatorio"], default="abc", help="Orden de los recursos.")
    parser.add_argument("--semilla", type=int, default=7, help="Semilla del orden aleatorio y del id (default: 7).")
    parser.add_argument("--temperatura", type=float, default=TEMPERATURA_DEFAULT, help="Temperatura de muestreo.")
    parser.add_argument(
        "--mensaje",
        default=None,
        help="Mensaje del estudiante que se adjunta al prompt (pruebas adversariales).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Imprime el prompt ensamblado sin llamar a Ollama.")
    parser.add_argument("--json", action="store_true", help="Imprime solo el JSON estructurado por stdout.")
    parser.add_argument("--guardar-md", default=None, help="Ruta donde guardar la respuesta en Markdown.")
    parser.add_argument("--guardar-json", default=None, help="Ruta donde guardar la recomendacion estructurada.")
    args = parser.parse_args()

    perfil = cargar_perfil(Path(args.perfil))
    recursos = cargar_recursos(Path(args.recursos))
    system_prompt = cargar_system_prompt()
    ordenados = ordenar_recursos(recursos, args.orden, args.semilla)
    prompt = construir_prompt(perfil, ordenados, refuerzo=args.refuerzo, mensaje=args.mensaje)

    if args.dry_run:
        print("=" * 72)
        print("DRY-RUN: prompt ensamblado (no se llama a Ollama)")
        print("=" * 72)
        print(f"System prompt: {SYSTEM_PROMPT_PATH.name} ({len(system_prompt)} caracteres)")
        print(f"Prompt usuario: {len(prompt)} caracteres")
        print("-" * 72)
        print(prompt)
        print("=" * 72)
        return 0

    inicio = time.perf_counter()
    resultado = llamar_ollama(system_prompt, prompt, args.modelo, args.temperatura)
    duracion = time.perf_counter() - inicio

    texto = (resultado.get("response") or "").strip()
    if not texto:
        print("[ERROR] Ollama devolvio una respuesta vacia.", file=sys.stderr)
        return 2

    datos = parsear_salida(texto, ordenados)
    errores = validar_salida(datos, ordenados, texto)

    salida = {
        "recomendacion_id": recomendacion_id(perfil, ordenados, args.semilla),
        "estudiante_id": perfil["estudiante_id"],
        "semana": ordenados[0]["semana"],
        "recurso_elegido": datos["recurso_elegido"],
        "opcion": datos["opcion"],
        "titulo": datos["titulo"],
        "justificacion": datos["justificacion"],
        "descarte": datos["descarte"],
        "modelo": args.modelo,
        "refuerzo": args.refuerzo,
        "mensaje": args.mensaje,
        "orden": [r["recurso_id"] for r in ordenados],
        "temperatura": args.temperatura,
        "latencia_s": round(duracion, 2),
        "tokens_generados": resultado.get("eval_count", 0),
        "validacion": {"ok": not errores, "errores": errores},
        "respuesta_md": texto,
    }

    if args.json:
        print(json.dumps(salida, ensure_ascii=False, indent=2))
    else:
        imprimir_humano(salida, resultado, args.modelo, duracion, errores)

    if args.guardar_md:
        guardar_markdown(texto, salida, Path(args.guardar_md))
    if args.guardar_json:
        guardar_json(salida, Path(args.guardar_json))

    return 0 if not errores else 2


if __name__ == "__main__":
    sys.exit(main())
