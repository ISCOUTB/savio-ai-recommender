# 🤝 Guía de contribución — Savio AI Recommender

Guía paso a paso para trabajar en equipo en este repositorio. **Léela completa una vez** y consúltala cada vez que vayas a entregar trabajo.

---

## 📌 Regla de oro

> **¿La tarea modifica archivos del repositorio?**
> - **SÍ** → trabajas en tu rama + commit + Pull Request.
> - **NO** (es algo en tu PC, como instalar Ollama) → solo cierras el issue con un comentario de evidencia.

Y siempre: **`main` no se toca directamente.** Todo entra por Pull Request.

---

## 🌿 Ramas del equipo

Cada integrante tiene su rama de trabajo, creada desde `main`:

| Rama | Integrante |
|---|---|
| `dev/persona-1` | Persona 1 — Infraestructura SLM / Backend |
| `dev/persona-2` | Persona 2 — Prompts y Guardrails |
| `dev/persona-3` | Persona 3 — Documentación y Presentación |

Cada quien desarrolla sus issues en su rama y cuando termina una tarea abre un **Pull Request hacia `main`** para que otro compañero lo revise.

---

## 🚀 Flujo paso a paso (úsalo SIEMPRE)

### 1. Primera vez — clonar el repositorio

```bash
git clone https://github.com/ISCOUTB/savio-ai-recommender.git
cd savio-ai-recommender
```

### 2. Entrar a TU rama (y actualizarla antes de trabajar)

```bash
git checkout dev/persona-1        # ← usa TU rama
git merge main                    # trae lo último de main a tu rama
```

> ⚠️ **Siempre** actualiza tu rama con `main` antes de empezar a trabajar. Así evitas conflictos.

### 3. Trabajar en tu issue

Editas tus archivos normalmente (código, documentación, prompts...).

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

> 📌 `Closes #N` = el issue queda 100% terminado (se cierra solo al mergear).
> 📌 `Ref #N` = es un avance parcial, el issue sigue abierto.

**Plantilla de tipos de commit:**

| Tipo | Úsalo para... | Ejemplo |
|---|---|---|
| `docs(sprint-N):` | Documentación | `docs(sprint-4): tabla de benchmarks completa` |
| `feat(poc):` | Código nuevo | `feat(poc): conexion con API de Ollama` |
| `prompts(...):` | Prompts/guardrails | `prompts(escenario-a): ruta de estudio nota baja` |
| `bench(...):` | Mediciones | `bench(gemma): resultados tokens/s` |
| `fix(...):` | Correcciones | `fix(poc): timeout en llamada a Ollama` |

### 5. Subir tu rama a GitHub

```bash
git push -u origin dev/persona-1   # ← TU rama
```

### 6. Abrir el Pull Request (PR)

1. Entra a https://github.com/ISCOUTB/savio-ai-recommender
2. Aparecerá un botón verde **"Compare & pull request"** → click.
3. En la descripción escribe: `Closes #N` (el número de tu issue).
4. En **Reviewers** (barra derecha) asigna a un compañero.
5. Click en **"Create pull request"**.

### 7. Revisión y merge

- El compañero revisa tu PR y lo aprueba (o te deja comentarios).
- Se hace **"Merge pull request"** → tu trabajo entra a `main` → el issue se cierra automáticamente.
- Después del merge, actualiza tu rama para lo siguiente: `git merge main` (estando en tu rama).

---

## 🚨 Si aparece un CONFLICTO al hacer merge

No entres en pánico — es normal. Significa que tú y `main` tocaron la misma línea:

```bash
git merge main
# CONFLICT (content): Merge conflict in README.md
```

1. Abre el archivo conflictivo — verás marcas así:
   ```
   <<<<<<< HEAD
   tu version
   =======
   la version de main
   >>>>>>> main
   ```
2. Borra las marcas y deja el contenido correcto final.
3. Guarda, luego:
   ```bash
   git add .
   git commit -m "fix: resuelto conflicto de merge con main"
   git push
   ```
4. Si no sabes cuál versión es la correcta: **pregunta al equipo antes de mergear.**

---

## ✅ ¿Qué necesita revisión de un compañero (PR) y qué no?

| Requiere PR con reviewer 🔍 | Merge rápido (rama propia) ⚡ | Sin rama, solo cerrar issue 💻 |
|---|---|---|
| Scripts Python (`poc_slm/`) | Registrar tu evidencia en el doc del sprint | Instalar Ollama en tu PC |
| Prompts y guardrails (`prompts/`) | Corregir un typo | Configurar tu entorno local |
| Tabla de benchmarks | Actualizar el estado ✅ de una tabla | Ejecutar pruebas de verificación |
| Presentación técnica | | |
| Cambios en README/CONTRIBUTING | | |

---

## 📊 ¿Cómo se sabe qué está hecho?

- **Issues abiertos (🟢)** = pendiente · **Issues cerrados (🟣)** = hecho.
- El milestone **"Entrega 1 - PoC Funcional"** muestra el % de avance automáticamente.
- Cada sprint tiene su tabla **"Registro de ejecución"** donde se deja la evidencia.

---

## 🗺️ Estado de las entregas

Ver el índice completo en [docs/entregas/README.md](docs/entregas/README.md).
