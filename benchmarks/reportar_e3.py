"""Genera informe y fila de bitacora desde evidencia E3-09 ya medida.

No modifica respuestas ni metricas. Requiere resumen completo, 28 casos por
modelo, y escribe el informe una sola vez. Uso desde la raiz:
python benchmarks/reportar_e3.py --corrida benchmarks/resultados/<equipo>/<corrida>
"""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent


def numero(valor, decimales=2):
    return "N/D" if valor is None else f"{valor:.{decimales}f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corrida", required=True, type=Path)
    args = parser.parse_args()
    corrida = args.corrida.resolve()
    if not corrida.is_relative_to(RAIZ / "benchmarks/resultados"):
        raise SystemExit("[FALLO] la corrida debe estar en benchmarks/resultados/")
    evaluacion = corrida / "evaluacion"
    resumen = json.loads((evaluacion / "resumen-ampliado.json").read_text(encoding="utf-8"))
    protocolo = resumen["protocolo"]
    resultados = resumen["resultados"]
    bitacora = RAIZ / "experimentos/bitacora.md"
    identidad_aportada = any(
        protocolo["gguf_sha256"] in linea and "coincide con el hash aportado por el usuario" in linea
        for linea in bitacora.read_text(encoding="utf-8").splitlines()
    )
    for modelo in ("base", "ajustado"):
        if resultados[modelo]["perfiles"] != 28 or len(list((evaluacion / modelo).glob("SINT-*.json"))) != 28:
            raise SystemExit("[FALLO] evaluacion incompleta; no se genera informe final")
    b, a, t = (resultados[k] for k in ("base", "ajustado", "teacher"))
    lineas = [
        "# Evaluacion E3-09 del GGUF local en CPU", "",
        f"Fecha UTC del resumen: {resumen['fecha_utc']}",
        f"Equipo: {resumen['hardware']['cpu']}; Ollama {resumen['hardware']['ollama']}.",
        f"Modelo ajustado: `{protocolo['modelos']['ajustado']}`.",
        f"SHA-256 GGUF: `{protocolo['gguf_sha256']}`.",
        f"SHA-256 corpus: `{protocolo['corpus_sha256']}`.", "",
        "## Protocolo y alcance", "",
        "28 registros sinteticos seleccionados con sha256(id) % 5 == 0; 122 quedan fuera de esta evaluacion.",
        "Una generacion por modelo y registro, sin reintentos. ChatML identico para ambos modelos, temperatura 0,",
        "semilla 42, num_predict=1200, num_ctx=4096 y num_gpu=0. Calentamiento separado de las latencias.",
        "RSS de servidor y runner de Ollama muestreado cada 0.25 s; size_vram consultado cada 1 s y al terminar.",
        "GB decimal = bytes / 1e9. La confirmacion de VRAM pertenece al modelo segun Ollama; no se inventa una medicion NVIDIA.",
        "Los benchmarks historicos de Entrega 1 y las tres salidas base anteriores no se mezclan con esta comparacion.", "",
        "La evaluacion se completo en varias sesiones con calentamientos separados. Las pausas y la carga del equipo limitan una comparacion causal de velocidad.",
        "Se conservaron los casos previos al reanudar; no se eligieron ni repitieron respuestas segun su resultado.", "",
        "## Comparacion con la referencia Teacher", "",
        "| Medida | Base | Ajustado | Teacher |", "|---|---:|---:|---:|",
    ]
    for titulo, clave in (
        ("Fidelidad numerica sobre los 37 campos esperados (%)", "fidelidad_numerica_sobre_esperados_pct"),
        ("Precision de las citas etiquetadas reconocidas (%)", "precision_citas_reconocidas_pct"),
        ("Cobertura de campos numericos (%)", "cobertura_citas_pct"),
        ("Estructura de cuatro secciones (%)", "estructura_pct"),
        ("Guardrail automatico sobre texto crudo (%)", "guardrail_crudo_pct"),
        ("Guardrail automatico despues del backend (%)", "guardrail_backend_pct"),
        ("Bandas/polos: consistencia en items evaluables (%)", "baremos_consistencia_en_evaluables_pct"),
        ("Bandas/polos: cobertura de la rubrica parcial (%)", "baremos_cobertura_pct"),
        ("Bandas/polos: items acreditados sobre 420 posibles (%)", "baremos_acreditados_sobre_total_pct"),
    ):
        lineas.append(f"| {titulo} | {numero(b[clave])} | {numero(a[clave])} | {numero(t[clave])} |")
    lineas.extend([
        f"| Perfiles con inversion de polo reconocida en prosa | {b['perfiles_con_inversion_polo_reconocida']} | {a['perfiles_con_inversion_polo_reconocida']} | {t['perfiles_con_inversion_polo_reconocida']} |",
        f"| Perfiles con contradiccion de baremos reconocida | {b['perfiles_con_contradiccion_baremos_reconocida']} | {a['perfiles_con_contradiccion_baremos_reconocida']} | {t['perfiles_con_contradiccion_baremos_reconocida']} |",
        f"| Perfiles con escalas o rangos prohibidos reconocidos | {b['perfiles_con_escalas_o_rangos_prohibidos']} | {a['perfiles_con_escalas_o_rangos_prohibidos']} | {t['perfiles_con_escalas_o_rangos_prohibidos']} |",
        "", "La precision sin citas es N/D. Las omisiones reducen cobertura y fidelidad sobre esperados.",
        "El parser reconoce citas key=N, key: N, key (N), listas CHASIDE por area con ':' o '=' y JSON incrustado. No adivina numeros sin etiqueta.",
        "La auditoria ampliada incorpora JSON, letras de areas CHASIDE en mayusculas y negaciones por igual para base, ajustado y Teacher. El resumen y las auditorias iniciales siguen intactos.",
        "Cada campo vale una vez; una segunda cita contradictoria lo convierte en error. Las respuestas crudas se conservan.",
        "La rubrica de bandas/polos solo puntua afirmaciones explicitas reconocidas. Ausencia de hallazgos no equivale a correccion.",
        "Los items sin evaluar son desconocidos, no fallos del modelo. Las coberturas distintas impiden comparar estos porcentajes parciales como fidelidad integral.",
        "La fidelidad interpretativa integral, las correlaciones y el cumplimiento etico exhaustivo siguen pendientes de revision humana.",
        "Por esa razon no se acredita la meta de fidelidad integral >=85% a partir de estos indicadores parciales.",
        "El conjunto se uso como evaluacion durante entrenamiento: es validacion, no una prueba independiente.", "",
        "## Rendimiento observado", "",
        "| Medida | Base | Ajustado |", "|---|---:|---:|",
    ])
    for titulo, clave in (
        ("Latencia media (s)", "latencia_media_s"), ("Latencia mediana (s)", "latencia_mediana_s"),
        ("Latencia maxima (s)", "latencia_max_s"), ("Generacion media (tokens/s)", "tokens_por_s_media"),
        ("Longitud media de respuesta (tokens)", "tokens_generados_media"),
        ("RAM pico RSS (GB decimal)", "ram_pico_gb_decimal"), ("RAM pico RSS (GiB)", "ram_pico_gib"),
    ):
        lineas.append(f"| {titulo} | {numero(b[clave])} | {numero(a[clave])} |")
    lineas.extend([
        f"| Perfiles con latencia <=60 s | {b['perfiles_hasta_60s']}/28 | {a['perfiles_hasta_60s']}/28 |",
        f"| CPU verificada en todos los casos | {b['cpu_verificada_todos']} | {a['cpu_verificada_todos']} |",
        f"| Muestreo RAM completo sin errores | {b['muestras_ram_validas_todos']} | {a['muestras_ram_validas_todos']} |",
        f"| Respuestas cortadas por limite de tokens | {b['truncados_por_limite']} | {a['truncados_por_limite']} |",
        "", "Las longitudes reales de salida difieren y afectan la latencia. La tasa de tokens/s mide solo generacion; la latencia incluye toda la solicitud.",
        "", "## Hallazgos y limites para el cierre", "",
        f"En el ajustado hay {a['baremos_contradicciones']} items con contradiccion explicita reconocida y {a['baremos_sin_evaluar']} sin evaluar.",
        f"La referencia Teacher tiene {t['baremos_contradicciones']} contradicciones reconocidas y {t['baremos_sin_evaluar']} items sin evaluar con la misma rubrica.",
        f"El detector encontro {a['afirmaciones_revision_profesional']} respuestas ajustadas que afirman revision profesional sin evidencia de esa revision.",
        "El guardrail de produccion comprueba un conjunto limitado de frases y puede aceptar errores semanticos.",
        "La auditoria posterior detecta fallos; no modifica ni corrige las respuestas medidas.",
        "El hash local difiere del artefacto 2531a770 citado en la bitacora anterior; las mediciones de aquel artefacto no se atribuyen a este modelo.",
        ("Identidad Colab/local confirmada con el SHA-256 aportado por el usuario desde /content/entrenamiento-final/modelo-q4_k_m.gguf. El usuario aporto logs de 150 registros, split 122/28, 48 pasos y 3 epocas. Esa evidencia aportada se distingue de las mediciones CPU realizadas localmente."
         if identidad_aportada else "Identidad con el artefacto de Colab pendiente de acreditar con su hash y cuaderno ejecutado."),
        "La configuracion mini de procedencia-local.json es una observacion historica del archivo local; no acredita por si sola el entrenamiento del GGUF.",
        "Las firmas del corpus y la fidelidad integral no se suplen con metricas automaticas. Los issues remotos permanecen sin cambios.", "",
        "## Evidencia reproducible", "",
        "- [Protocolo y hardware](evaluacion/protocolo.json)",
        "- [Resumen ampliado calculado](evaluacion/resumen-ampliado.json)",
        "- [Auditoria ampliada por caso](evaluacion/auditoria-ampliada.json)",
        "- [Resumen inicial conservado](evaluacion/resumen.json)",
        "- [Gate de privacidad](evaluacion/gate-privacidad.json)",
        "- [Prueba de CPU del bloque 1](bloque1-cpu.json)",
        "- [Configuracion local observada y limite de procedencia](procedencia-local.json)",
        "- [Auditoria de los tres fixtures](bloque2-auditoria.json)",
        "- [Auditoria ampliada de los tres fixtures](bloque2-auditoria-ampliada.json)",
        "- [Auditoria de la referencia](evaluacion/teacher-auditoria.json)",
        "- Las subcarpetas `evaluacion/base/` y `evaluacion/ajustado/` contienen respuesta cruda, tiempos, muestreo y auditoria por caso.",
        "- Codigo: [evaluador](../../../evaluar_e3.py), [rubrica](../../../rubrica_e3.py), [citas JSON](../../../citas_json_e3.py), [reauditoria](../../../reauditar_e3.py) y [pruebas](../../../test_rubrica_e3.py).", "",
    ])
    with (corrida / "informe.md").open("x", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas))
    relativo = corrida.relative_to(RAIZ).as_posix()
    enlace = f"[{corrida.name}](../{relativo}/informe.md)"
    fila = (f"| {resumen['fecha_utc'][:10]} | persona-1 con asistencia de IA | Validar GGUF local en CPU y comparar 28 casos de E3-09 (#44, #51, #52, #53) | "
            f"{enlace}: {protocolo['modelos']['ajustado']}, SHA-256 {protocolo['gguf_sha256']}; "
            f"citas correctas {a['puntajes_correctos']}/{a['puntajes_esperados']}, estructura {numero(a['estructura_pct'])}%, "
            f"guardrail automatico backend {numero(a['guardrail_backend_pct'])}%; latencia media/max {numero(a['latencia_media_s'])}/{numero(a['latencia_max_s'])} s, "
            f"RAM RSS pico {numero(a['ram_pico_gb_decimal'])} GB, CPU verificada {a['cpu_verificada_todos']} | "
            f"Conservar evidencia cruda; no cerrar issues: quedan revision humana integral, firmas del corpus y fallos de bandas/polos. Identidad Colab/local aportada y registrada={identidad_aportada} |\n")
    if relativo + "/informe.md" not in bitacora.read_text(encoding="utf-8"):
        with bitacora.open("a", encoding="utf-8") as archivo:
            archivo.write(fila)
    print("Informe:", corrida / "informe.md")
    print("Bitacora actualizada desde resumen-ampliado.json, sin modificar metricas previas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
