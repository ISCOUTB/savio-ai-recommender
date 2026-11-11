> Modelo: smollm2:360m | Modo: cpu | Escenario: A_nota_baja + refuerzo | seed 2
> 294 tokens a 24.46 tok/s | 14.34 s

```
def recomendaciones_visual(estudiante, materia, tema, calificacion, estilo_de_aprendizaje):
    recomendaciones = {
        "visual": {
            "materia": materia,
            "tema": tema,
            "calificacion": calificacion,
            "estilo_de_aprendizaje": estilo_de_aprendizaje
        }
    }
    return recomendaciones

estudiante = "Estudiante Demo"
materia = "Estructuras de Datos No Lineales"
tema = "Arboles AVL"
calificacion = 2.0
estilo_de_aprendizaje = "visual"

recomendaciones_visual = recomendaciones_visual(estudiante, materia, tema, calificacion, estilo_de_aprendizaje)

for recomendacion in recomendaciones_visual:
    print(f"{recomendacion['materia']}: {recomendacion['tema']}: {recomendacion['calificacion']}: {recomendacion['estilo_de_aprendizaje']}")
```
