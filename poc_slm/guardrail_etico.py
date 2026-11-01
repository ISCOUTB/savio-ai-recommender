"""Guardrail etico para las salidas de interpretacion psicometrica (E3-03).

Uso:
    from guardrail_etico import AVISO_NO_CLINICO, agregar_aviso, validar_salida_etica

El modulo no llama al modelo ni conoce el esquema de entrada: solo fija el
texto canonico y las comprobaciones que E3-07 debe aplicar antes de entregar
una salida. No modifica el comportamiento de la demo de Entrega 1.
"""

import re

AVISO_NO_CLINICO = (
    "Este perfil es un apoyo para el diagnostico inicial y fue generado con "
    "asistencia de IA. No reemplaza al profesional ni constituye un diagnostico "
    "psicologico."
)

# Frases que sugieren un juicio clinico. No se prohibe la palabra "diagnostico"
# sola porque el aviso canonico la usa para negar el alcance clinico.
FRASES_CLINICAS = (
    "diagnostico definitivo",
    "diagnostico clinico",
    "el estudiante padece",
    "trastorno de",
    "patologia",
    "medicacion",
    "tratamiento psicologico",
)

# Tipo MBTI de 4 letras como etiqueta (por ejemplo INTP o ESFJ). El texto puede
# nombrar el instrumento, pero no usar el tipo como identificador del estudiante.
RE_TIPO_MBTI = re.compile(r"\b[EI][NS][TF][JP]\b")


def contiene_aviso(texto):
    """True si el texto ya incluye el aviso canonico, sin importar mayusculas."""
    return AVISO_NO_CLINICO.lower() in (texto or "").lower()


def agregar_aviso(texto):
    """Agrega el aviso al final una sola vez y devuelve el texto resultante."""
    base = (texto or "").rstrip()
    if not base:
        return AVISO_NO_CLINICO
    if contiene_aviso(base):
        return base
    return f"{base}\n\n---\n{AVISO_NO_CLINICO}"


def validar_salida_etica(texto):
    """Devuelve los hallazgos del guardrail. Lista vacia = salida aceptable.

    Es una comprobacion automatica, no un dictamen profesional: E3-07 decide si
    reintenta o entrega la respuesta segura.
    """
    limpio = (texto or "").strip()
    if not limpio:
        return ["salida vacia"]

    hallazgos = []
    if not contiene_aviso(limpio):
        hallazgos.append("falta el aviso no clinico")

    tipo = RE_TIPO_MBTI.search(limpio)
    if tipo:
        hallazgos.append(f"incluye un tipo MBTI de 4 letras: {tipo.group(0)}")

    bajo = limpio.lower()
    for frase in FRASES_CLINICAS:
        if frase in bajo:
            hallazgos.append(f"incluye frase clinica prohibida: {frase}")

    return hallazgos
