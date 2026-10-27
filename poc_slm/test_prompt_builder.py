"""Chequeos de regresion del Prompt Builder E2-10 (sin pytest, sin Ollama).

Uso (desde la raiz del repositorio, con el entorno virtual activo):
    python poc_slm/test_prompt_builder.py

Verifica el ensamblado del prompt, el orden reproducible de recursos, el
parser de la respuesta del modelo y las reglas de validacion de guardrails.
No llama a Ollama: los casos de salida son textos fijos.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prompt_builder as pb  # noqa: E402

PERFIL_VISUAL = pb.cargar_perfil(pb.RAIZ / "perfiles" / "ejemplo-perfil-estudiante.json")
PERFIL_TEXTUAL = pb.cargar_perfil(pb.RAIZ / "perfiles" / "ejemplo-perfil-textual.json")
PERFIL_KINESTESICO = pb.cargar_perfil(pb.RAIZ / "perfiles" / "ejemplo-perfil-kinestesico.json")
RECURSOS = pb.cargar_recursos(pb.RAIZ / "poc_slm" / "recursos" / "semana_1.json")

SALIDA_CANONICA = """## Recurso recomendado
`tde-s1-B` - Guia de lectura analitica: dos ensayos modelo y glosario

## Justificacion pedagogica
El perfil muestra preferencia verbal y reflexiva, con alta apertura: una guia
escrita con dos ensayos anotados permite analisis pausado y trabajo individual.

## Razon de descarte
- `tde-s1-A`: diagrama de 15 minutos sin produccion propia; no aprovecha el canal verbal.
- `tde-s1-C`: taller de 60 minutos centrado en producir texto; no coincide con la preferencia reflexiva.
"""

SALIDA_MINIMA = """## Recurso recomendado
A - Mapa interactivo: del problema a la tesis defendible

## Justificacion pedagogica
El perfil es visual y prefiere pasos cortos, por lo que el mapa interactivo de
quince minutos se ajusta mejor que la lectura o el taller.

## Razon de descarte
B: lectura de 45 minutos, exige canal verbal y analisis extenso.
C: taller de 60 minutos con produccion propia, demasiado largo para el perfil.
"""


def caso(nombre):
    print(f"[TEST] {nombre}")


def main() -> int:
    fallos = []

    caso("prompt incluye los 3 recursos, el perfil y las reglas")
    prompt = pb.construir_prompt(PERFIL_TEXTUAL, RECURSOS, refuerzo=True)
    for fragmento in ("tde-s1-A", "tde-s1-B", "tde-s1-C", "demo-002", "RECUERDA LAS REGLAS CRITICAS"):
        if fragmento not in prompt:
            fallos.append(f"el prompt no contiene {fragmento!r}")
    if "reflexivo" not in prompt:
        fallos.append("el prompt no menciona las preferencias del perfil")

    caso("sin refuerzo no repite reglas")
    sin_refuerzo = pb.construir_prompt(PERFIL_TEXTUAL, RECURSOS, refuerzo=False)
    if "RECUERDA LAS REGLAS CRITICAS" in sin_refuerzo:
        fallos.append("--sin-refuerzo sigue incluyendo el bloque de refuerzo")

    caso("perfil neutro recibe aviso de perfil incompleto")
    neutro = {
        "estudiante_id": "demo-neutro",
        "origen": "simulado",
        "estilos_aprendizaje": {
            "modelo": "felder_silverman",
            "puntajes": {"activo_reflexivo": 3.0, "sensorial_intuitivo": 3.0, "visual_verbal": 3.0, "secuencial_global": 3.0},
            "preferencias": [],
            "descripcion_para_prompt": "Sin datos de estilos.",
        },
        "personalidad": {"rasgos": {"introversion_extraversion": 3.0, "autonomia": 3.0, "metodicidad": 3.0, "apertura": 3.0}},
        "chaside": {"areas": {k: 3.0 for k in "CHASIDE"}},
    }
    if "PERFIL INCOMPLETO" not in pb.texto_perfil(neutro):
        fallos.append("no se avisa el perfil incompleto cuando todos los estilos son 3.0")

    caso("orden alfabetico y aleatorio reproducible")
    abc = pb.ordenar_recursos(RECURSOS, "abc", 7)
    if [r["opcion"] for r in abc] != ["A", "B", "C"]:
        fallos.append("el orden abc no es A, B, C")
    orden1 = [r["opcion"] for r in pb.ordenar_recursos(RECURSOS, "aleatorio", 42)]
    orden2 = [r["opcion"] for r in pb.ordenar_recursos(RECURSOS, "aleatorio", 42)]
    if orden1 != orden2:
        fallos.append("el orden aleatorio no es reproducible con la misma semilla")
    if sorted(orden1) != ["A", "B", "C"]:
        fallos.append("el orden aleatorio pierde o duplica recursos")

    caso("parser de una salida canonica")
    datos = pb.parsear_salida(SALIDA_CANONICA, RECURSOS)
    errores = pb.validar_salida(datos, RECURSOS, SALIDA_CANONICA)
    if datos["recurso_elegido"] != "tde-s1-B":
        fallos.append(f"parser canonico eligio {datos['recurso_elegido']!r}")
    if set(datos["descarte"]) != {"tde-s1-A", "tde-s1-C"}:
        fallos.append(f"parser canonico no detecto ambos descartes: {sorted(datos['descarte'])}")
    if errores:
        fallos.append(f"salida canonica marcada con errores: {errores}")

    caso("parser tolera respuesta minima con la letra de la opcion")
    datos_min = pb.parsear_salida(SALIDA_MINIMA, RECURSOS)
    if datos_min["recurso_elegido"] != "tde-s1-A":
        fallos.append(f"parser minimo eligio {datos_min['recurso_elegido']!r}")

    caso("validacion detecta descarte incompleto")
    sin_descarte = SALIDA_CANONICA.replace("- `tde-s1-C`: taller de 60 minutos centrado en producir texto; no coincide con la preferencia reflexiva.", "")
    datos_incompletos = pb.parsear_salida(sin_descarte, RECURSOS)
    errores_incompletos = pb.validar_salida(datos_incompletos, RECURSOS, sin_descarte)
    if not any("descarte de tde-s1-C" in e for e in errores_incompletos):
        fallos.append("no se detecto el descarte faltante de tde-s1-C")

    caso("parser acepta descarte con id y vinetas de continuacion")
    descarte_vinetas = """## Recurso recomendado
tde-s1-B - Guia de lectura analitica: dos ensayos modelo y glosario

## Justificacion pedagogica
El perfil prefiere el canal verbal y el trabajo reflexivo; la guia escrita con
dos ensayos anotados permite analisis pausado y trabajo individual sostenido.

## Razon de descarte
tde-s1-A - Mapa interactivo: del problema a la tesis defendible:
- Este recurso es de tipo diagrama y no cubre el canal verbal del perfil.

tde-s1-C - Taller guiado: construye tu tesis y anticipa la objecion:
- Este recurso exige 60 minutos de produccion y el perfil pide cargas breves.
"""
    datos_vinetas = pb.parsear_salida(descarte_vinetas, RECURSOS)
    errores_vinetas = pb.validar_salida(datos_vinetas, RECURSOS, descarte_vinetas)
    if errores_vinetas:
        fallos.append(f"no se acepto el descarte con vinetas: {errores_vinetas}")
    if "diagrama" not in datos_vinetas["descarte"].get("tde-s1-A", ""):
        fallos.append(f"motivo de tde-s1-A mal extraido: {datos_vinetas['descarte']}")

    caso("validacion rechaza descarte que solo repite el titulo")
    solo_titulos = """## Recurso recomendado
tde-s1-B - Guia de lectura analitica: dos ensayos modelo y glosario

## Justificacion pedagogica
El perfil es verbal y reflexivo, asi que una guia de lectura con ensayos
anotados permite analisis pausado y trabajo individual sostenido.

## Razon de descarte
tde-s1-A - Mapa interactivo: del problema a la tesis defendible
tde-s1-C - Taller guiado: construye tu tesis y anticipa la objecion
"""
    datos_titulos = pb.parsear_salida(solo_titulos, RECURSOS)
    errores_titulos = pb.validar_salida(datos_titulos, RECURSOS, solo_titulos)
    if sum("falta el descarte" in e for e in errores_titulos) != 2:
        fallos.append(f"no se rechazo el descarte que solo repite titulos: {errores_titulos}")

    caso("validacion detecta recurso inventado")
    inventado = SALIDA_CANONICA.replace("tde-s1-B", "tde-s1-D")
    datos_inv = pb.parsear_salida(inventado, RECURSOS)
    errores_inv = pb.validar_salida(datos_inv, RECURSOS, inventado)
    if not any("recurso_elegido invalido" in e for e in errores_inv):
        fallos.append("no se detecto el recurso inventado tde-s1-D")

    caso("validacion detecta enlaces")
    con_url = SALIDA_CANONICA + "\nMas recursos en https://example.com\n"
    datos_url = pb.parsear_salida(con_url, RECURSOS)
    errores_url = pb.validar_salida(datos_url, RECURSOS, con_url)
    if not any("enlaces prohibidos" in e for e in errores_url):
        fallos.append("no se detectaron enlaces prohibidos")

    caso("identificador estable de recomendacion")
    id1 = pb.recomendacion_id(PERFIL_VISUAL, RECURSOS, 7)
    id2 = pb.recomendacion_id(PERFIL_VISUAL, RECURSOS, 7)
    id3 = pb.recomendacion_id(PERFIL_TEXTUAL, RECURSOS, 7)
    if id1 != id2:
        fallos.append("el recomendacion_id no es estable con la misma entrada")
    if id1 == id3:
        fallos.append("dos perfiles distintos generan el mismo recomendacion_id")
    if not id1.startswith("rec-demo-001-s1-"):
        fallos.append(f"formato inesperado de recomendacion_id: {id1}")

    print()
    if fallos:
        print(f"FALLARON {len(fallos)} chequeo(s):")
        for fallo in fallos:
            print(f"  - {fallo}")
        return 1
    print("OK: todos los chequeos del Prompt Builder pasaron")
    return 0


if __name__ == "__main__":
    sys.exit(main())
