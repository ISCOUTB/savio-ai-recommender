"""Chequeos del guardrail etico E3-03 (sin Ollama, sin modelo).

Uso (desde la raiz del repositorio):
    python poc_slm/test_guardrail_etico.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import guardrail_etico as ge  # noqa: E402


def caso(nombre):
    print(f"[TEST] {nombre}")


def main() -> int:
    fallos = []

    caso("un texto sin aviso recibe el aviso canonico")
    texto = ge.agregar_aviso("Perfil integrado de prueba.")
    if not ge.contiene_aviso(texto):
        fallos.append("el aviso no se agrego")
    if not texto.startswith("Perfil integrado de prueba."):
        fallos.append("se perdio el contenido original")

    caso("agregar el aviso dos veces no lo duplica")
    texto_dos_veces = ge.agregar_aviso(texto)
    if texto_dos_veces != texto:
        fallos.append("el aviso se duplico o cambio el texto")

    caso("un texto vacio devuelve solo el aviso")
    if ge.agregar_aviso("") != ge.AVISO_NO_CLINICO:
        fallos.append("el texto vacio no devolvio el aviso canonico")

    caso("una salida vacia se rechaza")
    if "salida vacia" not in ge.validar_salida_etica(""):
        fallos.append("no se detecto la salida vacia")

    caso("una salida sin aviso se rechaza")
    if "falta el aviso no clinico" not in ge.validar_salida_etica("Perfil integrado de prueba."):
        fallos.append("no se detecto la ausencia del aviso")

    caso("un tipo MBTI de 4 letras se rechaza")
    salida_mbti = ge.agregar_aviso("El estudiante corresponde al tipo INTP.")
    if not any("tipo MBTI" in h for h in ge.validar_salida_etica(salida_mbti)):
        fallos.append("no se detecto el tipo MBTI")

    caso("una frase clinica se rechaza")
    salida_clinica = ge.agregar_aviso("Se confirma un diagnostico definitivo.")
    if not any("frase clinica" in h for h in ge.validar_salida_etica(salida_clinica)):
        fallos.append("no se detecto la frase clinica")

    caso("mencionar el instrumento sin el tipo de 4 letras es aceptable")
    salida_instrumento = ge.agregar_aviso(
        "El test de personalidad es una implementacion institucional y no el MBTI oficial."
    )
    if ge.validar_salida_etica(salida_instrumento):
        fallos.append("se rechazo una mencion legitima del instrumento")

    caso("una salida con aviso y lenguaje no clinico es aceptable")
    salida_ok = ge.agregar_aviso(
        "Perfil orientador: intereses vocacionales por las areas I y E, "
        "preferencias visuales y rasgos equilibrados. Requiere revision profesional."
    )
    if ge.validar_salida_etica(salida_ok):
        fallos.append(f"se rechazo una salida valida: {ge.validar_salida_etica(salida_ok)}")

    caso("una cita con DOI no se confunde con un dato clinico")
    salida_doi = ge.agregar_aviso(
        "Fuente: https://doi.org/10.1000/xyz123. Lectura de apoyo para la orientacion."
    )
    if ge.validar_salida_etica(salida_doi):
        fallos.append("se rechazo una cita con DOI")

    print()
    if fallos:
        print(f"FALLOS: {len(fallos)}")
        for fallo in fallos:
            print(f"  - {fallo}")
        return 1

    print("RESULTADO: OK (10/10 chequeos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
