"""Pruebas de fallos de fidelidad y de la rubrica parcial; sin inferencia."""

import json
import sys
import unittest
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from rubrica_e3 import auditar, evaluar_baremos  # noqa: E402
from citas_json_e3 import auditar_ampliado  # noqa: E402
from evaluar_e3 import resumen_modelo  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


class PruebasRubrica(unittest.TestCase):
    def setUp(self):
        self.perfil = json.loads((RAIZ / "perfiles/brutos/ejemplo-perfil-bruto-dominante.json").read_text(encoding="utf-8-sig"))

    def test_omitir_no_es_acertar(self):
        resultado = auditar("Sin conteos.", self.perfil)
        self.assertEqual(resultado["numerica"]["campos_correctos"], 0)
        self.assertEqual(len(resultado["numerica"]["faltantes"]), 37)

    def test_puntaje_incorrecto_dentro_de_rango(self):
        resultado = auditar("activo=7; reflexivo=4", self.perfil)
        self.assertIn("ils.activo", resultado["numerica"]["errores"])
        self.assertIn("ils.reflexivo", resultado["numerica"]["errores"])

    def test_repetir_cita_con_error(self):
        resultado = auditar("activo=8; activo=7", self.perfil)
        self.assertEqual(resultado["numerica"]["campos_correctos"], 0)

    def test_chaside_separa_area_y_campo(self):
        resultado = auditar("- I: interes=9, aptitud=4, total=13.", self.perfil)
        self.assertEqual(resultado["numerica"]["campos_correctos"], 3)
        self.assertEqual(len(resultado["numerica"]["faltantes"]), 34)

    def test_equilibrio_global_falso(self):
        resultado = evaluar_baremos("## 2. Rasgos de personalidad\nTodos los ejes son equilibrados.", self.perfil)
        self.assertEqual(resultado["personalidad.extraversion_introversion"]["estado"], "contradiccion")

    def test_ils_sin_preferencia_con_diferencia_siete(self):
        resultado = evaluar_baremos("## 1. Estilos de aprendizaje\nLos cuatro ejes quedan sin preferencia clara.", self.perfil)
        self.assertEqual(resultado["ils.visual_verbal"]["estado"], "correcto")

    def test_preferencia_invertida(self):
        resultado = evaluar_baremos("## 2. Rasgos de personalidad\nPreferencia extravertida.", self.perfil)
        self.assertEqual(resultado["personalidad.extraversion_introversion"]["estado"], "contradiccion")

    def test_no_confundir_negacion_con_preferencia(self):
        resultado = evaluar_baremos("## 2. Rasgos de personalidad\nNo se establece una preferencia extravertida.", self.perfil)
        self.assertEqual(resultado["personalidad.extraversion_introversion"]["estado"], "sin_evaluar")

    def test_banda_chaside_falsa(self):
        resultado = evaluar_baremos("## 3. Perfil vocacional\nI presenta banda media.", self.perfil)
        self.assertEqual(resultado["chaside.I"]["estado"], "contradiccion")

    def test_guardrail_agregado_no_atribuido_al_modelo(self):
        resultado = auditar("Texto sin aviso.", self.perfil)
        self.assertFalse(resultado["guardrail_crudo_ok"])
        self.assertTrue(resultado["guardrail_backend_ok"])
        self.assertTrue(resultado["aviso_agregado"])

    def test_revision_profesional_no_acreditada(self):
        resultado = auditar("Fue visto por un profesional.", self.perfil)
        self.assertTrue(resultado["alerta_revision_profesional_inventada"])

    def test_json_copiado_cuenta_como_cita_no_como_interpretacion(self):
        texto = json.dumps({k: self.perfil[k] for k in ("chaside", "ils", "personalidad")})
        resultado = auditar_ampliado(texto, self.perfil)
        self.assertEqual(resultado["numerica"]["campos_correctos"], 37)
        self.assertTrue(all(v["estado"] == "sin_evaluar" for v in resultado["baremos"].values()))

    def test_json_repetido_erroneo_no_se_oculta(self):
        texto = 'activo=8; {"activo": 7}'
        resultado = auditar_ampliado(texto, self.perfil)
        self.assertIn("ils.activo", resultado["numerica"]["errores"])

    def test_json_final_truncado_conserva_areas_completas(self):
        texto = '{"C": {"interes": 4, "aptitud": 2, "total": 6}, "H": {'
        resultado = auditar_ampliado(texto, self.perfil)
        self.assertEqual(resultado["numerica"]["campos_correctos"], 3)

    def caso_de_metricas(self, latencia, ram):
        # Datos ficticios exclusivos de pruebas; nunca se escriben como evidencia.
        return {"auditoria": auditar("", self.perfil), "latencia_s": latencia,
                "tokens_por_s": 10, "memoria": {"ram_pico_rss_bytes": ram,
                "cpu_verificada": True, "muestras_ram": 1, "errores_muestreo": []},
                "respuesta_ollama": {"done_reason": "stop"}}

    def test_media_baja_no_oculta_un_caso_lento(self):
        resumen = resumen_modelo([self.caso_de_metricas(10, 1_000_000_000), self.caso_de_metricas(61, 1_000_000_000)])
        self.assertLess(resumen["latencia_media_s"], 60)
        self.assertFalse(resumen["metas"]["latencia_todos_60s"])

    def test_meta_ram_usa_gb_decimal_no_gib(self):
        resumen = resumen_modelo([self.caso_de_metricas(10, 2_600_000_000)])
        self.assertLess(resumen["ram_pico_gib"], 2.5)
        self.assertFalse(resumen["metas"]["ram_2_5_gb"])

    def test_preposicion_a_no_es_area_chaside(self):
        texto = "## 3. Perfil vocacional\nI registra aptitud sin interes, lo que no equivale a afinidad alta."
        resultado = auditar_ampliado(texto, self.perfil)
        self.assertEqual(resultado["baremos"]["chaside.A"]["estado"], "sin_evaluar")
        self.assertEqual(resultado["baremos"]["chaside.I"]["estado"], "sin_evaluar")

    def test_area_chaside_con_mayor_total_y_banda_falsa(self):
        texto = "## 3. Perfil vocacional\nI presenta el mayor total en banda media; D y E tambien son medias."
        resultado = auditar_ampliado(texto, self.perfil)
        self.assertEqual(resultado["baremos"]["chaside.I"]["estado"], "contradiccion")
        self.assertEqual(resultado["baremos"]["chaside.D"]["estado"], "contradiccion")
        self.assertEqual(resultado["baremos"]["chaside.E"]["estado"], "contradiccion")

    def test_mayor_conteo_invertido_en_prosa(self):
        texto = "## 2. Rasgos de personalidad\nEl mayor conteo de extraversion no demuestra una identidad."
        resultado = auditar_ampliado(texto, self.perfil)
        self.assertEqual(resultado["direcciones_contradictorias_reconocidas"][0]["esperado"], "introversion")

    def test_lista_de_ambos_polos_no_es_direccion(self):
        texto = "## 1. Estilos de aprendizaje\nLas inclinaciones activa y reflexiva deben describirse."
        resultado = auditar_ampliado(texto, self.perfil)
        self.assertFalse(resultado["direcciones_contradictorias_reconocidas"])

    def test_activo_cuatro_reflexivo_siete_no_es_inclinacion_activa(self):
        self.perfil["ils"].update(activo=4, reflexivo=7)
        texto = "## 1. Estilos de aprendizaje\nLas inclinaciones activa y visual no imponen un formato."
        resultado = auditar_ampliado(texto, self.perfil)
        self.assertEqual(resultado["direcciones_contradictorias_reconocidas"][0]["esperado"], "reflexivo")

    def test_chaside_area_separada_con_igual(self):
        texto = "- C=interes=4 / aptitud=2 / total=6."
        resultado = auditar_ampliado(texto, self.perfil)
        self.assertEqual(resultado["numerica"]["campos_correctos"], 3)
        self.assertFalse(resultado["numerica"]["errores"])


if __name__ == "__main__":
    unittest.main()
