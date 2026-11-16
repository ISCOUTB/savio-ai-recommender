"""Deriva auditoria ampliada desde respuestas crudas sin repetir inferencias.

Escribe archivos nuevos; no modifica tiempos, RSS, respuestas ni resumen.json.
Uso: python benchmarks/reauditar_e3.py --evaluacion <carpeta-evaluacion>
"""

import argparse
import copy
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from citas_json_e3 import auditar_ampliado  # noqa: E402
from evaluar_e3 import resumen_calidad, resumen_modelo, guardar, fecha  # noqa: E402
from importar_gguf import sha256_archivo  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluacion", required=True, type=Path)
    args = parser.parse_args()
    carpeta = args.evaluacion.resolve()
    if not carpeta.is_relative_to(RAIZ / "benchmarks/resultados"):
        raise SystemExit("[FALLO] la carpeta debe estar en benchmarks/resultados/")
    original = json.loads((carpeta / "resumen.json").read_text(encoding="utf-8"))
    corpus = RAIZ / "datos/corpus/corpus.jsonl"
    if sha256_archivo(corpus) != original["protocolo"]["corpus_sha256"]:
        raise SystemExit("[FALLO] el corpus cambio desde la medicion")
    registros = {r["id"]: r for r in (json.loads(l) for l in corpus.read_text(encoding="utf-8").splitlines() if l.strip())}
    resultados = {}
    detalle = {}
    for modelo in ("base", "ajustado"):
        casos = []
        for identificador in original["protocolo"]["evaluacion_ids"]:
            caso = json.loads((carpeta / modelo / (identificador + ".json")).read_text(encoding="utf-8"))
            caso["auditoria"] = auditar_ampliado(caso["respuesta_ollama"]["response"], registros[identificador])
            casos.append(caso)
        resultados[modelo] = resumen_modelo(casos)
        resultados[modelo]["tokens_generados_media"] = sum(c["tokens_generados"] for c in casos) / len(casos)
        resultados[modelo]["perfiles_con_escalas_o_rangos_prohibidos"] = sum(bool(c["auditoria"]["numerica"]["escalas_o_rangos"]) for c in casos)
        resultados[modelo]["perfiles_con_inversion_polo_reconocida"] = sum(bool(c["auditoria"]["direcciones_contradictorias_reconocidas"]) for c in casos)
        resultados[modelo]["perfiles_con_contradiccion_baremos_reconocida"] = sum(any(v["estado"] == "contradiccion" for v in c["auditoria"]["baremos"].values()) for c in casos)
        detalle[modelo] = [{"id": c["id"], "auditoria": c["auditoria"]} for c in casos]
    teacher = [{"id": identificador, "auditoria": auditar_ampliado(registros[identificador]["output"], registros[identificador])} for identificador in original["protocolo"]["evaluacion_ids"]]
    resultados["teacher"] = resumen_calidad([c["auditoria"] for c in teacher])
    resultados["teacher"]["perfiles_con_escalas_o_rangos_prohibidos"] = sum(bool(c["auditoria"]["numerica"]["escalas_o_rangos"]) for c in teacher)
    resultados["teacher"]["perfiles_con_inversion_polo_reconocida"] = sum(bool(c["auditoria"]["direcciones_contradictorias_reconocidas"]) for c in teacher)
    resultados["teacher"]["perfiles_con_contradiccion_baremos_reconocida"] = sum(any(v["estado"] == "contradiccion" for v in c["auditoria"]["baremos"].values()) for c in teacher)
    detalle["teacher"] = teacher
    ampliado = copy.deepcopy(original)
    ampliado["fecha_auditoria_utc"] = fecha()
    ampliado["auditoria_ampliada"] = {"motivo": "Incluir JSON, variantes etiquetadas CHASIDE y alcance de negaciones por igual para todos los modelos, sin alterar evidencia medida", "codigo_sha256": sha256_archivo(Path(__file__).with_name("citas_json_e3.py")), "script_reauditoria_sha256": sha256_archivo(Path(__file__)), "origen": "resumen.json y respuestas_ollama originales"}
    ampliado["resultados"] = resultados
    guardar(carpeta / "auditoria-ampliada.json", detalle)
    guardar(carpeta / "resumen-ampliado.json", ampliado)
    ruta_fixtures = carpeta.parent / "bloque2-auditoria.json"
    if ruta_fixtures.exists():
        anterior = json.loads(ruta_fixtures.read_text(encoding="utf-8"))
        fixtures = []
        for caso in anterior["casos"]:
            ruta_perfil = RAIZ / caso["perfil"]
            ruta_salida = RAIZ / caso["salida"]
            perfil = json.loads(ruta_perfil.read_text(encoding="utf-8-sig"))
            if perfil.get("origen") != "sintetico":
                raise SystemExit("[FALLO] no se admiten fixtures reales en evidencia publica")
            salida = json.loads(ruta_salida.read_text(encoding="utf-8"))
            fixtures.append({"perfil": caso["perfil"], "salida": caso["salida"],
                "perfil_sha256": sha256_archivo(ruta_perfil), "salida_sha256": sha256_archivo(ruta_salida),
                "auditoria_texto_postprocesado": auditar_ampliado(salida["perfil_markdown"], perfil)})
        guardar(carpeta.parent / "bloque2-auditoria-ampliada.json", {"nota": anterior["nota"], "casos": fixtures})
    print(json.dumps(resultados, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
