# Moodle local minimo

Alcance: habilitador de Entrega 2. No es el nucleo del proyecto.

## Objetivo minimo

- Levantar Moodle local con Docker.
- Instalar bloques IS-UTB de Estilos de Aprendizaje, Personalidad y CHASIDE con apoyo del docente.
- Diligenciar tests entre integrantes para generar datos de referencia.

## Arranque base

```bash
cd moodle
docker compose up -d
```

Detener:

```bash
docker compose down
```

## Limites de alcance

- No crear plugins desde cero.
- No hacer integracion avanzada con Savio institucional en esta fase.
- Si Moodle bloquea el avance, continuar con fixtures JSON simulados y documentar bloqueo.
