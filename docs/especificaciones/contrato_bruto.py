"""Reglas compartidas del contrato de puntajes brutos (E3-04).

Fuente unica de verdad de rangos e invariantes de los tres instrumentos. La usan
tanto el validador de corpus (E3-06) como el validador de perfiles brutos
(E3-04/E3-05), para que el corpus, los perfiles reales y el backend no puedan
divergir.

Reglas (directriz 2 del docente, sin reescalar nada):
    - CHASIDE: interes 0-10, aptitud 0-4, total 0-14 y total = interes + aptitud.
    - Felder-Silverman: 8 polos 0-11; cada par bipolar suma exactamente 11.
    - Personalidad: 8 polos 0-9, sin indices compuestos (sin `autonomia`).

No conoce esquemas de archivo ni rutas: solo objetos Python. Los mensajes usan
el prefijo que recibe el llamador ("linea 3", "perfil.json", etc.).
"""

import re

AREAS_CHASIDE = ("C", "H", "A", "S", "I", "D", "E")
CAMPOS_AREA = {"interes", "aptitud", "total"}

RE_ID_SINTETICO = re.compile(r"^SINT-\d{3}$")

POLOS_ILS = (
    "activo",
    "reflexivo",
    "sensitivo",
    "intuitivo",
    "visual",
    "verbal",
    "secuencial",
    "global",
)

PARES_ILS = (
    ("activo", "reflexivo"),
    ("sensitivo", "intuitivo"),
    ("visual", "verbal"),
    ("secuencial", "global"),
)

POLOS_PERSONALIDAD = (
    "extraversion",
    "introversion",
    "sensing",
    "intuition",
    "thinking",
    "feeling",
    "judging",
    "perceptive",
)

CAMPOS_RAIZ = {"id", "origen", "chaside", "ils", "personalidad"}
CAMPOS_ENTRENAMIENTO = {"instruction", "input", "output"}
CAMPOS_PERMITIDOS = CAMPOS_RAIZ | CAMPOS_ENTRENAMIENTO

# Nombres oficiales de las 4 dimensiones bipolares y su polo izquierdo.
DIMENSIONES_ILS = {
    "activo_reflexivo": ("activo", "reflexivo"),
    "sensitivo_intuitivo": ("sensitivo", "intuitivo"),
    "visual_verbal": ("visual", "verbal"),
    "secuencial_global": ("secuencial", "global"),
}

# Valores oficiales del diferencial: impar de -11 a 11 (0 significa empate).
DIFERENCIALES_VALIDOS = frozenset(
    valor for valor in range(-11, 12) if valor % 2 != 0
)

# Claves que delatan el formato de Entrega 2 (escala 1.0-5.0).
CLAVES_ENTREGA_2 = frozenset(
    {
        "estudiante_id",
        "estilos_aprendizaje",
        "areas_dominantes",
        "descripcion_para_prompt",
        "autonomia",
        "preferencias",
        "resumen_conductual",
        "preferencias_trabajo",
        "rasgos",
    }
)


def es_entero(valor):
    """True si es un entero real (bool no cuenta)."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def validar_chaside(chaside, prefijo):
    """Valida estructura y rangos nativos de CHASIDE."""
    errores = []
    if not isinstance(chaside, dict):
        return [f"{prefijo}: chaside debe ser un objeto"]

    faltan = sorted(set(AREAS_CHASIDE) - set(chaside))
    sobran = sorted(set(chaside) - set(AREAS_CHASIDE))
    if faltan:
        errores.append(f"{prefijo}: chaside sin areas obligatorias: {', '.join(faltan)}")
    if sobran:
        errores.append(f"{prefijo}: chaside con areas no permitidas: {', '.join(sobran)}")

    for area in AREAS_CHASIDE:
        bloque = chaside.get(area)
        if not isinstance(bloque, dict):
            errores.append(f"{prefijo}: chaside.{area} debe ser un objeto")
            continue

        faltan_campos = sorted(CAMPOS_AREA - set(bloque))
        sobran_campos = sorted(set(bloque) - CAMPOS_AREA)
        if faltan_campos:
            errores.append(f"{prefijo}: chaside.{area} sin campos: {', '.join(faltan_campos)}")
        if sobran_campos:
            errores.append(f"{prefijo}: chaside.{area} con campos no permitidos: {', '.join(sobran_campos)}")

        valores = {}
        for campo, maximo in (("interes", 10), ("aptitud", 4), ("total", 14)):
            valor = bloque.get(campo)
            if not es_entero(valor):
                errores.append(f"{prefijo}: chaside.{area}.{campo} debe ser entero")
                continue
            if not 0 <= valor <= maximo:
                errores.append(f"{prefijo}: chaside.{area}.{campo} fuera de rango 0-{maximo}")
                continue
            valores[campo] = valor

        if len(valores) == 3 and valores["total"] != valores["interes"] + valores["aptitud"]:
            errores.append(f"{prefijo}: chaside.{area}.total no coincide con interes + aptitud")

    return errores


def validar_ils(ils, prefijo):
    """Valida los 8 polos de Felder-Silverman y la suma 11 por dimension."""
    errores = []
    if not isinstance(ils, dict):
        return [f"{prefijo}: ils debe ser un objeto"]

    faltan = sorted(set(POLOS_ILS) - set(ils))
    sobran = sorted(set(ils) - set(POLOS_ILS))
    if faltan:
        errores.append(f"{prefijo}: ils sin polos obligatorios: {', '.join(faltan)}")
    if sobran:
        errores.append(f"{prefijo}: ils con polos no permitidos: {', '.join(sobran)}")

    valores = {}
    for polo in POLOS_ILS:
        valor = ils.get(polo)
        if not es_entero(valor):
            errores.append(f"{prefijo}: ils.{polo} debe ser entero")
            continue
        if not 0 <= valor <= 11:
            errores.append(f"{prefijo}: ils.{polo} fuera de rango 0-11")
            continue
        valores[polo] = valor

    for izquierdo, derecho in PARES_ILS:
        if izquierdo in valores and derecho in valores:
            if valores[izquierdo] + valores[derecho] != 11:
                errores.append(f"{prefijo}: ils.{izquierdo} + ils.{derecho} debe sumar 11")

    return errores


def validar_personalidad(personalidad, prefijo):
    """Valida los 8 polos del test de personalidad en 0-9."""
    errores = []
    if not isinstance(personalidad, dict):
        return [f"{prefijo}: personalidad debe ser un objeto"]

    faltan = sorted(set(POLOS_PERSONALIDAD) - set(personalidad))
    sobran = sorted(set(personalidad) - set(POLOS_PERSONALIDAD))
    if faltan:
        errores.append(f"{prefijo}: personalidad sin polos obligatorios: {', '.join(faltan)}")
    if sobran:
        errores.append(f"{prefijo}: personalidad con polos no permitidos: {', '.join(sobran)}")

    for polo in POLOS_PERSONALIDAD:
        valor = personalidad.get(polo)
        if not es_entero(valor):
            errores.append(f"{prefijo}: personalidad.{polo} debe ser entero")
            continue
        if not 0 <= valor <= 9:
            errores.append(f"{prefijo}: personalidad.{polo} fuera de rango 0-9")

    return errores


def validar_diferencial(diferencial, ils, prefijo):
    """Valida el diferencial oficial (impar -11..11) contra los puntajes ILS."""
    errores = []
    if not isinstance(diferencial, dict):
        return [f"{prefijo}: diferencial debe ser un objeto"]

    sobra = sorted(set(diferencial) - set(DIMENSIONES_ILS))
    if sobra:
        errores.append(f"{prefijo}: diferencial con dimensiones no permitidas: {', '.join(sobra)}")

    for dimension, (izquierdo, derecho) in DIMENSIONES_ILS.items():
        if dimension not in diferencial:
            continue
        valor = diferencial[dimension]
        if not es_entero(valor):
            errores.append(f"{prefijo}: diferencial.{dimension} debe ser entero")
            continue
        if valor not in DIFERENCIALES_VALIDOS:
            errores.append(
                f"{prefijo}: diferencial.{dimension} debe ser impar entre -11 y 11 "
                "(positivo hacia el polo izquierdo)"
            )
            continue
        if isinstance(ils, dict):
            puntaje_izq, puntaje_der = ils.get(izquierdo), ils.get(derecho)
            if es_entero(puntaje_izq) and es_entero(puntaje_der):
                esperado = puntaje_izq - puntaje_der
                if valor != esperado:
                    errores.append(
                        f"{prefijo}: diferencial.{dimension} no coincide con "
                        f"{izquierdo} - {derecho} ({esperado})"
                    )

    return errores


def validar_perfil_bruto(perfil, prefijo, exigir_sintetico=True, campos_extra=()):
    """Valida estructura, rangos e invariantes del perfil bruto.

    `exigir_sintetico=True` mantiene el contrato del corpus (id `SINT-###` y
    `origen: sintetico`). Los perfiles reales llaman con `False` y pueden usar
    cualquier id alfanumerico.
    """
    if not isinstance(perfil, dict):
        return [f"{prefijo}: el perfil debe ser un objeto JSON"]

    errores = []
    permitidos = CAMPOS_PERMITIDOS | set(campos_extra)

    faltan = sorted(CAMPOS_RAIZ - set(perfil))
    sobran = sorted(set(perfil) - permitidos)
    if faltan:
        errores.append(f"{prefijo}: faltan campos obligatorios: {', '.join(faltan)}")
    if sobran:
        errores.append(f"{prefijo}: campos no permitidos en el perfil: {', '.join(sobran)}")

    if exigir_sintetico:
        identificador = perfil.get("id")
        if not es_id_sintetico(identificador):
            errores.append(f"{prefijo}: id debe cumplir el patron SINT-###")
        if perfil.get("origen") != "sintetico":
            errores.append(f"{prefijo}: origen debe ser 'sintetico'")

    if "chaside" in perfil:
        errores.extend(validar_chaside(perfil["chaside"], prefijo))
    if "ils" in perfil:
        errores.extend(validar_ils(perfil["ils"], prefijo))
    if "personalidad" in perfil:
        errores.extend(validar_personalidad(perfil["personalidad"], prefijo))
    if "diferencial" in perfil and "ils" in perfil:
        errores.extend(validar_diferencial(perfil["diferencial"], perfil["ils"], prefijo))

    return errores


def es_id_sintetico(identificador):
    """True si el id cumple el patron SINT-###."""
    return isinstance(identificador, str) and bool(RE_ID_SINTETICO.match(identificador))
