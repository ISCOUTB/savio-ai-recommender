"""Chequeos del contrato de puntajes brutos E3-04 (sin red, sin modelo).

Uso (desde la raiz del repositorio):
    python docs/especificaciones/test_validar_perfiles_brutos.py
"""

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
VALIDADOR = Path(__file__).with_name("validar-perfiles-brutos.py")

PERFIL = {
    "id": "persona-1",
    "origen": "real",
    "fecha_aplicacion": "2026-10-28",
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
    "diferencial": {
        "activo_reflexivo": 5,
        "sensitivo_intuitivo": -3,
        "visual_verbal": 7,
        "secuencial_global": 1,
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


def ejecutar(rutas):
    comando = [sys.executable, str(VALIDADOR)] + [str(ruta) for ruta in rutas]
    return subprocess.run(comando, capture_output=True, text=True, encoding="utf-8")


def escribir(carpeta, nombre, objeto):
    ruta = carpeta / nombre
    ruta.write_text(json.dumps(objeto, ensure_ascii=True, indent=2), encoding="utf-8")
    return ruta


def comprobar(fallos, nombre, resultado, codigo, esperado):
    if resultado.returncode != codigo:
        fallos.append(f"{nombre}: devolvio {resultado.returncode}, se esperaba {codigo}")
    if esperado not in resultado.stdout:
        fallos.append(f"{nombre}: no aparecio '{esperado}' en la salida")


def main() -> int:
    fallos = []

    caso("los tres ejemplos versionados pasan")
    resultado = ejecutar([])
    comprobar(fallos, "ejemplos versionados", resultado, 0, "RESULTADO: OK (3 perfil(es))")

    with tempfile.TemporaryDirectory(prefix="e3-04-") as temporal:
        carpeta = Path(temporal)

        caso("un perfil real valido pasa")
        ruta = escribir(carpeta, "valido.json", copy.deepcopy(PERFIL))
        comprobar(fallos, "perfil real", ejecutar([ruta]), 0, "perfil bruto valido")

        caso("un puntaje decimal (escala 1.0-5.0) se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante["ils"]["activo"] = 5.0
        ruta = escribir(carpeta, "decimal.json", variante)
        comprobar(fallos, "decimal", ejecutar([ruta]), 1, "es decimal")

        caso("un indice compuesto autonomia se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante["personalidad"]["autonomia"] = 4
        ruta = escribir(carpeta, "autonomia.json", variante)
        comprobar(fallos, "autonomia", ejecutar([ruta]), 1, "formato de Entrega 2")

        caso("las claves de Entrega 2 en la raiz se rechazan")
        variante = copy.deepcopy(PERFIL)
        variante["estilos_aprendizaje"] = {"puntajes": {}}
        ruta = escribir(carpeta, "e2.json", variante)
        comprobar(fallos, "claves E2", ejecutar([ruta]), 1, "formato de Entrega 2")

        caso("un total CHASIDE inconsistente se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante["chaside"]["I"]["total"] = 12
        ruta = escribir(carpeta, "chaside.json", variante)
        comprobar(fallos, "total CHASIDE", ejecutar([ruta]), 1, "no coincide con interes + aptitud")

        caso("un par ILS que no suma 11 se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante["ils"]["reflexivo"] = 4
        variante["diferencial"]["activo_reflexivo"] = 4
        ruta = escribir(carpeta, "ils.json", variante)
        comprobar(fallos, "par ILS", ejecutar([ruta]), 1, "debe sumar 11")

        caso("un interes fuera de 0-10 se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante["chaside"]["C"] = {"interes": 11, "aptitud": 2, "total": 13}
        ruta = escribir(carpeta, "rango.json", variante)
        comprobar(fallos, "interes 11", ejecutar([ruta]), 1, "fuera de rango 0-10")

        caso("un polo de personalidad fuera de 0-9 se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante["personalidad"]["feeling"] = 10
        ruta = escribir(carpeta, "personalidad.json", variante)
        comprobar(fallos, "personalidad 10", ejecutar([ruta]), 1, "fuera de rango 0-9")

        caso("un diferencial par se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante["diferencial"]["visual_verbal"] = 6
        ruta = escribir(carpeta, "diferencial-par.json", variante)
        comprobar(fallos, "diferencial par", ejecutar([ruta]), 1, "debe ser impar")

        caso("un diferencial que no coincide con ils se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante["diferencial"]["secuencial_global"] = 3
        ruta = escribir(carpeta, "diferencial-ils.json", variante)
        comprobar(fallos, "diferencial inconsistente", ejecutar([ruta]), 1, "no coincide con")

        caso("un perfil sin campos obligatorios se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante.pop("personalidad")
        ruta = escribir(carpeta, "incompleto.json", variante)
        comprobar(fallos, "sin personalidad", ejecutar([ruta]), 1, "faltan campos obligatorios")

        caso("un origen desconocido se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante["origen"] = "anonimo"
        ruta = escribir(carpeta, "origen.json", variante)
        comprobar(fallos, "origen anonimo", ejecutar([ruta]), 1, "origen debe ser")

        caso("una fecha mal formada se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante["fecha_aplicacion"] = "28/10/2026"
        ruta = escribir(carpeta, "fecha.json", variante)
        comprobar(fallos, "fecha invalida", ejecutar([ruta]), 1, "fecha AAAA-MM-DD")

        caso("un polo ILS no permitido se rechaza")
        variante = copy.deepcopy(PERFIL)
        variante["ils"]["mixto"] = 3
        ruta = escribir(carpeta, "polo-extra.json", variante)
        comprobar(fallos, "polo extra", ejecutar([ruta]), 1, "polos no permitidos")

        caso("un JSON malformado devuelve codigo 2")
        ruta = carpeta / "malformado.json"
        ruta.write_text("{ esto no es json", encoding="utf-8")
        comprobar(fallos, "JSON malformado", ejecutar([ruta]), 2, "RESULTADO: FALLO")

        caso("una carpeta sin JSON devuelve codigo 2")
        vacia = carpeta / "vacia"
        vacia.mkdir()
        comprobar(fallos, "carpeta vacia", ejecutar([vacia]), 2, "RESULTADO: FALLO")

    if fallos:
        print(f"\nFALLOS: {len(fallos)}")
        for fallo in fallos:
            print(f"  - {fallo}")
        return 1

    print("\nRESULTADO: OK (17/17 chequeos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
