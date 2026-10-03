# ðŸ¤ GuÃ­a de contribuciÃ³n â€” Savio AI Recommender

GuÃ­a paso a paso para trabajar en equipo en este repositorio. **LÃ©ela completa una vez** y consÃºltala cada vez que vayas a entregar trabajo.

---

## ðŸ“Œ Regla de oro

> **Â¿La tarea modifica archivos del repositorio?**
> - **SÃ** â†’ trabajas en tu rama + commit + Pull Request.
> - **NO** (es algo en tu PC, como instalar Ollama) â†’ solo cierras el issue con un comentario de evidencia.

Y siempre: **`master` no se toca directamente.** Todo entra por Pull Request.

---

## ðŸŒ¿ Ramas del equipo

Cada integrante tiene su rama de trabajo, creada desde `master`:

| Rama | Integrante |
|---|---|
| `dev/persona-1` | Persona 1 â€” Infraestructura SLM / Backend |
| `dev/persona-2` | Persona 2 â€” Prompts y Guardrails |
| `dev/persona-3` | Persona 3 â€” DocumentaciÃ³n y PresentaciÃ³n |

Cada quien desarrolla sus issues en su rama y cuando termina una tarea abre un **Pull Request hacia `master`** para que otro compaÃ±ero lo revise.

---

## ðŸš€ Flujo paso a paso (Ãºsalo SIEMPRE)

### 1. Primera vez â€” clonar el repositorio

```bash
git clone https://github.com/ISCOUTB/savio-ai-recommender.git
cd savio-ai-recommender
```

### 2. Entrar a TU rama (y actualizarla antes de trabajar)

```bash
git checkout dev/persona-1        # â† usa TU rama
git merge master                    # trae lo Ãºltimo de master a tu rama
```

> âš ï¸ **Siempre** actualiza tu rama con `master` antes de empezar a trabajar. AsÃ­ evitas conflictos.

### 3. Trabajar en tu issue

Editas tus archivos normalmente (cÃ³digo, documentaciÃ³n, prompts...).

### 4. Hacer commit

```bash
git add .
git commit -m "tipo(alcance): descripcion. Closes #NUMERO_DEL_ISSUE"
```

**Ejemplos reales:**

```bash
git commit -m "docs(sprint-1): ollama instalado y modelos verificados. Closes #1"
git commit -m "feat(poc): script recommender.py con evento JSON. Closes #3"
git commit -m "prompts(guardrails): system prompt con 4 reglas. Closes #4"
git commit -m "bench(qwen): RAM y tokens/s medidos. Ref #8"
```

> ðŸ“Œ `Closes #N` = el issue queda 100% terminado (se cierra solo al mergear).
> ðŸ“Œ `Ref #N` = es un avance parcial, el issue sigue abierto.

**Plantilla de tipos de commit:**

| Tipo | Ãšsalo para... | Ejemplo |
|---|---|---|
| `docs(sprint-N):` | DocumentaciÃ³n | `docs(sprint-4): tabla de benchmarks completa` |
| `feat(poc):` | CÃ³digo nuevo | `feat(poc): conexion con API de Ollama` |
| `prompts(...):` | Prompts/guardrails | `prompts(escenario-a): ruta de estudio nota baja` |
| `bench(...):` | Mediciones | `bench(gemma): resultados tokens/s` |
| `fix(...):` | Correcciones | `fix(poc): timeout en llamada a Ollama` |

### 5. Subir tu rama a GitHub

```bash
git push -u origin dev/persona-1   # â† TU rama
```

### 6. Abrir el Pull Request (PR)

1. Entra a https://github.com/ISCOUTB/savio-ai-recommender
2. AparecerÃ¡ un botÃ³n verde **"Compare & pull request"** â†’ click.
3. En la descripciÃ³n escribe: `Closes #N` (el nÃºmero de tu issue).
4. En **Reviewers** (barra derecha) asigna a un compaÃ±ero.
5. Click en **"Create pull request"**.

### 7. RevisiÃ³n y merge

- El compaÃ±ero revisa tu PR y lo aprueba (o te deja comentarios).
- Se hace **"Merge pull request"** â†’ tu trabajo entra a `master` â†’ el issue se cierra automÃ¡ticamente.
- DespuÃ©s del merge, actualiza tu rama para lo siguiente: `git merge master` (estando en tu rama).

---

## ðŸš¨ Si aparece un CONFLICTO al hacer merge

No entres en pÃ¡nico â€” es normal. Significa que tÃº y `master` tocaron la misma lÃ­nea:

```bash
git merge master
# CONFLICT (content): Merge conflict in README.md
```

1. Abre el archivo conflictivo â€” verÃ¡s marcas asÃ­:
   ```
   <<<<<<< HEAD
   tu version
   =======
   la version de master
   >>>>>>> master
   ```
2. Borra las marcas y deja el contenido correcto final.
3. Guarda, luego:
   ```bash
   git add .
   git commit -m "fix: resuelto conflicto de merge con master"
   git push
   ```
4. Si no sabes cuÃ¡l versiÃ³n es la correcta: **pregunta al equipo antes de mergear.**

---

## âœ… Â¿QuÃ© necesita revisiÃ³n de un compaÃ±ero (PR) y quÃ© no?

| Requiere PR con reviewer ðŸ” | Merge rÃ¡pido (rama propia) âš¡ | Sin rama, solo cerrar issue ðŸ’» |
|---|---|---|
| Scripts Python (`poc_slm/`) | Registrar tu evidencia en el doc del sprint | Instalar Ollama en tu PC |
| Prompts y guardrails (`prompts/`) | Corregir un typo | Configurar tu entorno local |
| Tabla de benchmarks | Actualizar el estado âœ… de una tabla | Ejecutar pruebas de verificaciÃ³n |
| PresentaciÃ³n tÃ©cnica | | |
| Cambios en README/CONTRIBUTING | | |

---

## ðŸ“Š Â¿CÃ³mo se sabe quÃ© estÃ¡ hecho?

- **Issues abiertos (ðŸŸ¢)** = pendiente Â· **Issues cerrados (ðŸŸ£)** = hecho.
- El milestone **"Entrega 1 - PoC Funcional"** muestra el % de avance automÃ¡ticamente.
- Cada sprint tiene su tabla **"Registro de ejecuciÃ³n"** donde se deja la evidencia.

---

## ðŸ—ºï¸ Estado de las entregas

Ver el Ã­ndice completo en [docs/entregas/README.md](docs/entregas/README.md).
