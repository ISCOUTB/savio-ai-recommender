"""Chequeos del validador de corpus anonimizado E3-03 (sin red, sin modelo).

Uso (desde la raiz del repositorio):
    python docs/especificaciones/test_validar_corpus_anonimizado.py
"""

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE / "poc_slm"))

from guardrail_etico import AVISO_NO_CLINICO  # noqa: E402

VALIDADOR = Path(__file__).with_name("validar-corpus-anonimizado.py")

PERFIL = {
    "id": "SINT-001",
    "origen": "sintetico",
    "chaside": {
        "C": {"interes": 4, "aptitud": 2, "total": 6},
        "H": {"interes": 5, "aptitud": 2, "total": 7},
        "A": {"interes": 3, "aptitud": 1, "total": 4},
        "S": {"interes": 2, "aptitud": 1, "total": 3},
        "I": {"interes": 9, "aptitud": 4, "total": 13},
        "D": {"interes": 2, "aptitud": 1, "total": 3},
        "E": {"interes": 8, "aptitud": 3, "total": 11},
    },
    "ils": {
        "activo": 8,
        "reflexivo": 3,
        "sensitivo": 4,
        "intuitivo": 7,
        "visual": 9,
        "verbal": 2,
        "secuencial": 6,
        "global": 5,
    },
    "personalidad": {
        "extraversion": 3,
        "introversion": 7,
        "sensing": 4,
        "intuition": 8,
        "thinking": 7,
        "feeling": 3,
        "judging": 8,
        "perceptive": 2,
    },
}


def caso(nombre):
    print(f"[TEST] {nombre}")


def escribir_jsonl(ruta, registros):
    lineas = [json.dumps(registro, ensure_ascii=True) for registro in registros]
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def ejecutar(entrada, manifiesto=None):
    comando = [sys.executable, str(VALIDADOR), "--entrada", str(entrada)]
    if manifiesto is not None:
        comando.extend(["--manifiesto", str(manifiesto)])
    return subprocess.run(comando, capture_output=True, text=True, encoding="utf-8")


def main() -> int:
    fallos = []

    with tempfile.TemporaryDirectory(prefix="e3-03-") as temporal:
        carpeta = Path(temporal)

        caso("un corpus sintetico valido pasa y genera manifiesto")
        valido = copy.deepcopy(PERFIL)
        valido["output"] = "Perfil integrado de prueba.\n\n---\n" + AVISO_NO_CLINICO
        ruta_valida = carpeta / "corpus_valido.jsonl"
        manifiesto = carpeta / "manifiesto.json"
        escribir_jsonl(ruta_valida, [valido])
        resultado = ejecutar(ruta_valida, manifiesto)
        if resultado.returncode != 0:
            fallos.append(f"el corpus valido fallo: {resultado.stdout}{resultado.stderr}")
        if "RESULTADO: OK" not in resultado.stdout:
            fallos.append("el corpus valido no reporto OK")
        if not manifiesto.exists():
            fallos.append("no se genero el manifiesto")
        else:
            datos = json.loads(manifiesto.read_text(encoding="utf-8"))
            if len(datos.get("entradas", [{}])[0].get("sha256", "")) != 64:
                fallos.append("el manifiesto no tiene un sha256 de 64 caracteres")
            if datos.get("registros") != 1:
                fallos.append("el manifiesto no reporta 1 registro")

        caso("un registro instruction/input/output valido pasa")
        entrenamiento = {
            "instruction": "Interpreta de forma integrada los puntajes brutos.",
            "input": copy.deepcopy(PERFIL),
            "output": "Perfil integrado de prueba.\n\n---\n" + AVISO_NO_CLINICO,
        }
        ruta_entrenamiento = carpeta / "entrenamiento.jsonl"
        escribir_jsonl(ruta_entrenamiento, [entrenamiento])
        resultado = ejecutar(ruta_entrenamiento)
        if resultado.returncode != 0:
            fallos.append(f"el registro instruction/input/output fallo: {resultado.stdout}{resultado.stderr}")

        caso("un origen real se rechaza")
        real = copy.deepcopy(PERFIL)
        real["origen"] = "real"
        ruta = carpeta / "origen_real.jsonl"
        escribir_jsonl(ruta, [real])
        resultado = ejecutar(ruta)
        if resultado.returncode != 1 or "origen" not in resultado.stdout:
            fallos.append("no se rechazo el origen real")

        caso("un id no sintetico se rechaza")
        mal_id = copy.deepcopy(PERFIL)
        mal_id["id"] = "persona-1"
        ruta = carpeta / "id_real.jsonl"
        escribir_jsonl(ruta, [mal_id])
        resultado = ejecutar(ruta)
        if resultado.returncode != 1 or "SINT-###" not in resultado.stdout:
            fallos.append("no se rechazo el id no sintetico")

        caso("un id sintetico duplicado se rechaza")
        duplicado = copy.deepcopy(PERFIL)
        ruta = carpeta / "id_duplicado.jsonl"
        escribir_jsonl(ruta, [duplicado, copy.deepcopy(PERFIL)])
        resultado = ejecutar(ruta)
        if resultado.returncode != 1 or "duplicado" not in resultado.stdout:
            fallos.append("no se rechazo el id sintetico duplicado")

        caso("una clave prohibida se rechaza")
        con_clave = copy.deepcopy(PERFIL)
        con_clave["estudiante_id"] = "persona-1"
        ruta = carpeta / "clave_prohibida.jsonl"
        escribir_jsonl(ruta, [con_clave])
        resultado = ejecutar(ruta)
        if resultado.returncode != 1 or "estudiante_id" not in resultado.stdout:
            fallos.append("no se rechazo la clave prohibida")

        caso("un total CHASIDE inconsistente se rechaza")
        mal_chaside = copy.deepcopy(PERFIL)
        mal_chaside["chaside"]["I"]["total"] = 12
        ruta = carpeta / "chaside_inconsistente.jsonl"
        escribir_jsonl(ruta, [mal_chaside])
        resultado = ejecutar(ruta)
        if resultado.returncode != 1 or "total no coincide" not in resultado.stdout:
            fallos.append("no se rechazo el total CHASIDE inconsistente")

        caso("un par ILS que no suma 11 se rechaza")
        mal_ils = copy.deepcopy(PERFIL)
        mal_ils["ils"]["activo"] = 7
        ruta = carpeta / "ils_inconsistente.jsonl"
        escribir_jsonl(ruta, [mal_ils])
        resultado = ejecutar(ruta)
        if resultado.returncode != 1 or "sumar 11" not in resultado.stdout:
            fallos.append("no se rechazo el par ILS inconsistente")

        caso("un polo de personalidad fuera de 0-9 se rechaza")
        mal_personalidad = copy.deepcopy(PERFIL)
        mal_personalidad["personalidad"]["extraversion"] = 10
        ruta = carpeta / "personalidad_inconsistente.jsonl"
        escribir_jsonl(ruta, [mal_personalidad])
        resultado = ejecutar(ruta)
        if resultado.returncode != 1 or "0-9" not in resultado.stdout:
            fallos.append("no se rechazo el polo de personalidad fuera de rango")

        caso("un correo en la salida se rechaza")
        con_correo = copy.deepcopy(PERFIL)
        con_correo["output"] = "Contacto: ana@example.com\n\n---\n" + AVISO_NO_CLINICO
        ruta = carpeta / "correo.jsonl"
        escribir_jsonl(ruta, [con_correo])
        resultado = ejecutar(ruta)
        if resultado.returncode != 1 or "correo" not in resultado.stdout:
            fallos.append("no se rechazo el correo")

        caso("una salida sin aviso no clinico se rechaza")
        sin_aviso = copy.deepcopy(PERFIL)
        sin_aviso["output"] = "Perfil integrado de prueba."
        ruta = carpeta / "sin_aviso.jsonl"
        escribir_jsonl(ruta, [sin_aviso])
        resultado = ejecutar(ruta)
        if resultado.returncode != 1 or "aviso" not in resultado.stdout:
            fallos.append("no se rechazo la salida sin aviso")

        caso("un tipo MBTI de 4 letras en la salida se rechaza")
        con_mbti = copy.deepcopy(PERFIL)
        con_mbti["output"] = "El tipo es INTP.\n\n---\n" + AVISO_NO_CLINICO
        ruta = carpeta / "mbti.jsonl"
        escribir_jsonl(ruta, [con_mbti])
        resultado = ejecutar(ruta)
        if resultado.returncode != 1 or "MBTI" not in resultado.stdout:
            fallos.append("no se rechazo el tipo MBTI")

        caso("un JSONL malformado devuelve codigo 2")
        ruta = carpeta / "malformado.jsonl"
        ruta.write_text("{no es json}\n", encoding="utf-8")
        resultado = ejecutar(ruta)
        if resultado.returncode != 2:
            fallos.append(f"un JSONL malformado devolvio {resultado.returncode}, se esperaba 2")

        caso("un archivo vacio devuelve codigo 2")
        ruta = carpeta / "vacio.jsonl"
        ruta.write_text("", encoding="utf-8")
        resultado = ejecutar(ruta)
        if resultado.returncode != 2:
            fallos.append(f"un archivo vacio devolvio {resultado.returncode}, se esperaba 2")

        caso("una carpeta con un JSONL valido pasa")
        carpeta_corpus = carpeta / "corpus"
        carpeta_corpus.mkdir()
        escribir_jsonl(carpeta_corpus / "sintetico_001.jsonl", [valido])
        resultado = ejecutar(carpeta_corpus)
        if resultado.returncode != 0:
            fallos.append(f"la carpeta valida fallo: {resultado.stdout}{resultado.stderr}")

    print()
    if fallos:
        print(f"FALLOS: {len(fallos)}")
        for fallo in fallos:
            print(f"  - {fallo}")
        return 1

    print("RESULTADO: OK (15/15 chequeos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
