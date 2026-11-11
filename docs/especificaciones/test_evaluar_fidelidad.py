"""Chequeos del evaluador de fidelidad E3-09 (sin Ollama, sin modelo).

Uso (desde la raiz del repositorio):
    python docs/especificaciones/test_evaluar_fidelidad.py
"""

import importlib.util
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RUTA = Path(__file__).with_name("evaluar-fidelidad.py")
spec = importlib.util.spec_from_file_location("evaluar_fidelidad", RUTA)
ef = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ef)

FALLOS = []


def caso(nombre, condicion):
    print(f"[{'OK' if condicion else 'FALLO'}] {nombre}")
    if not condicion:
        FALLOS.append(nombre)


def registro(id_):
    return next(r for r in ef.cargar_corpus() if r["id"] == id_)


# SINT-016: activo 4 / reflexivo 7. Es el caso en que el GGUF de E3-08 dijo "activa".
base = registro("SINT-016")
texto_gt = base["output"]

# 1. El split es el del notebook de E3-08: 28 registros de evaluacion.
split = ef.split_evaluacion()
caso("split de evaluacion de 28 registros", len(split) == 28)
caso("split determinista por sha256(id) % 5", all(ef.es_evaluacion(r) for r in split))

# 2. El ground truth obtiene fidelidad maxima.
ev = ef.evaluar_registro(texto_gt, base, texto_gt)
caso("ground truth: fidelidad 100 %", ev["fidelidad"] == 1.0)
caso("ground truth: cobertura de los 37 puntajes", ev["dimensiones"]["exactitud"]["citados_correctos"] == 37)
caso("ground truth: ROUGE-L contra si mismo = 1", ev["rouge_l_vs_gt"] == 1.0)

# 3. Un puntaje mal citado es una alucinacion y anula la exactitud.
alterado = texto_gt.replace("reflexivo=7", "reflexivo=9")
ex = ef.evaluar_registro(alterado, base)["dimensiones"]["exactitud"]
caso("detecta puntaje ILS alterado", any("ils.reflexivo=9" in a for a in ex["alucinaciones"]))
caso("alucinacion deja exactitud en 0", ex["puntaje"] == 0.0)

alterado = texto_gt.replace("H: interes=10, aptitud=4, total=14", "H: interes=10, aptitud=4, total=13")
ex = ef.evaluar_registro(alterado, base)["dimensiones"]["exactitud"]
caso("detecta total CHASIDE alterado", any("chaside.H.total=13" in a for a in ex["alucinaciones"]))

ex = ef.evaluar_registro(texto_gt + "\nUn puntaje de 3.5 en la escala.", base)["dimensiones"]
caso("decimal no nativo cae en guardrails", ex["guardrails"]["puntaje"] == 0.0)

# 4. Coherencia: polo invertido (el error real de E3-08).
invertido = texto_gt.replace(
    "Las inclinaciones reflexiva, sensitiva, visual y secuencial no llegan a preferencia marcada.",
    "El estudiante tiene una inclinacion activa para aprender.",
)
co = ef.evaluar_registro(invertido, base)["dimensiones"]["coherencia"]
caso("detecta polo ILS invertido (activa con activo 4 / reflexivo 7)",
     "ILS activo/reflexivo: sin polo invertido" in co["fallos"])

# 5. Coherencia: preferencia marcada donde el baremo dice que no la hay.
exagerado = texto_gt.replace(
    "Las inclinaciones reflexiva, sensitiva, visual y secuencial no llegan a preferencia marcada.",
    "Presenta una preferencia visual marcada.",
)
co = ef.evaluar_registro(exagerado, base)["dimensiones"]["coherencia"]
caso("detecta preferencia ILS exagerada (visual 7 / verbal 4)",
     "ILS visual/verbal: sin preferencia exagerada" in co["fallos"])

# 6. Coherencia: no nombrar el area CHASIDE de mayor total.
sin_area = texto_gt.replace(
    "H, Humanidades/Sociales/Juridicas, alcanza afinidad alta y el maximo total; C, A e I son medias.",
    "C, A e I son medias.",
)
co = ef.evaluar_registro(sin_area, base)["dimensiones"]["coherencia"]
caso("detecta area de mayor total omitida", "CHASIDE: nombra el area de mayor total H" in co["fallos"])

# 7. Estructura y guardrails.
sin_seccion = texto_gt.replace("## 4. Sintesis integrada", "Resumen")
caso("detecta seccion faltante", ef.evaluar_registro(sin_seccion, base)["dimensiones"]["estructura"]["puntaje"] < 1)

con_mbti = texto_gt.replace("no identifica un tipo de personalidad", "corresponde a un ENFP")
caso("detecta tipo MBTI", ef.evaluar_registro(con_mbti, base)["dimensiones"]["guardrails"]["puntaje"] == 0.0)

sin_aviso = texto_gt.split("Este perfil es un apoyo")[0]
caso("detecta aviso no clinico ausente",
     ef.evaluar_registro(sin_aviso, base)["dimensiones"]["guardrails"]["puntaje"] == 0.0)

# 8. Titulos en negrita se normalizan como en el backend.
negrita = texto_gt.replace("## 1. Estilos de aprendizaje", "**1. Estilos de aprendizaje**")
caso("titulo en negrita se acepta", ef.evaluar_registro(negrita, base)["dimensiones"]["estructura"]["puntaje"] == 1.0)

# 9. Agregados.
res = ef.resumen([ef.evaluar_registro(r["output"], r, r["output"]) for r in split])
caso("referencia Teacher cumple la meta de 85 %", res["cumple_fidelidad"])
caso("referencia Teacher sin alucinaciones", res["alucinaciones_total"] == 0)

print()
if FALLOS:
    print(f"RESULTADO: FALLO ({len(FALLOS)} chequeo(s))")
    sys.exit(1)
print("RESULTADO: OK")
