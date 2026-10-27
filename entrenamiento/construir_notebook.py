"""construir_notebook.py - Genera entrenamiento/ajuste_qlora_gguf.ipynb (E3-08, #44).

El notebook se mantiene como codigo en este archivo para poder revisarlo en git y
probarlo en local (entrenamiento/probar_notebook_local.py). Las celdas marcadas con
la etiqueta "solo-colab" (instalacion, compilacion de llama.cpp, subida a Hugging
Face) se saltan en la prueba local.

Uso:
    python entrenamiento/construir_notebook.py
"""

import json
from pathlib import Path

DESTINO = Path(__file__).resolve().parent / "ajuste_qlora_gguf.ipynb"

CELDAS = [
    ("markdown", [], """# Ajuste del SLM (Qwen 2.5 0.5B) con QLoRA y exportacion a GGUF para CPU

**Proyecto:** Sistema de inferencia con un modelo de lenguaje pequeno para la interpretacion integrada de CHASIDE, Felder-Silverman y personalidad (Proyecto de Ingenieria I, UTB). **Issue:** E3-08 (#44).

Flujo: corpus JSONL (`instruction`, `input`, `output`, `particion`) -> ajuste QLoRA en GPU de Colab -> fusion del adaptador -> GGUF F16 -> GGUF **Q4_K_M** -> `Modelfile` de Ollama para ejecutar **solo en CPU**.

**Antes de ejecutar:**
1. *Entorno de ejecucion > Cambiar tipo de entorno > GPU T4*.
2. Subir el corpus cuando la celda de datos lo pida. Para una prueba rapida, subir `entrenamiento/datos_prueba.jsonl` (salidas de la linea base sin IA, no son ground truth).
3. Para publicar en Hugging Face, poner el token en *Secretos* de Colab con el nombre `HF_TOKEN`.

**Politica de datos:** el corpus debe contener solo perfiles sinteticos. Los perfiles reales del equipo no se suben a Colab ni a Hugging Face."""),

    ("code", ["solo-colab"], """!pip -q install -U transformers peft trl datasets accelerate bitsandbytes huggingface_hub sentencepiece"""),

    ("code", [], """# Configuracion
import json, os, platform, time
import torch

BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"   # respaldo: "Qwen/Qwen2.5-1.5B-Instruct"
DATOS = "datos.jsonl"                     # corpus con instruction, input, output y particion
NOMBRE = "savio-slm-0.5b-v1"              # nombre versionado del modelo ajustado
HF_REPO = None                            # ej. "usuario/savio-slm-0.5b-v1" para publicar (privado)
MODO_PRUEBA = True                        # True: pocos pasos para verificar el flujo de punta a punta

GPU = torch.cuda.is_available()
HIPER = dict(epocas=3, max_pasos=-1, lr=2e-4, batch=4, acumulacion=4, max_longitud=2048,
             lora_r=16, lora_alpha=32, lora_dropout=0.05, semilla=2026, qlora_4bit=GPU)
if MODO_PRUEBA:
    HIPER.update(epocas=1, max_pasos=4, batch=1, acumulacion=1)
print("GPU:", torch.cuda.get_device_name(0) if GPU else "no (prueba en CPU, sin 4 bits)")
print(json.dumps(HIPER, indent=1))"""),

    ("code", ["solo-colab"], """# Subir el corpus si no esta en el entorno
if not os.path.exists(DATOS):
    from google.colab import files
    subido = files.upload()
    DATOS = next(iter(subido))
print("Corpus:", DATOS)"""),

    ("code", [], """# Cargar corpus y separar por la particion asignada a cada perfil (sin fuga entre train y eval)
from datasets import Dataset

filas = [json.loads(l) for l in open(DATOS, encoding="utf-8") if l.strip()]
for f in filas:
    assert {"instruction", "input", "output"} <= set(f), "faltan campos instruction/input/output"

def a_conversacion(f):
    return {"prompt": [{"role": "system", "content": f["instruction"]},
                       {"role": "user", "content": f["input"]}],
            "completion": [{"role": "assistant", "content": f["output"]}]}

train = Dataset.from_list([a_conversacion(f) for f in filas if f.get("particion", "train") == "train"])
evalu = Dataset.from_list([a_conversacion(f) for f in filas if f.get("particion") == "eval"])
print(f"train: {len(train)} | eval: {len(evalu)}")"""),

    ("code", [], """# Modelo base y tokenizador (QLoRA en 4 bits si hay GPU)
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
if HIPER["qlora_4bit"]:
    cuant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                               bnb_4bit_compute_dtype=torch.float16)
    modelo = AutoModelForCausalLM.from_pretrained(BASE_MODEL, quantization_config=cuant, device_map="auto")
else:
    modelo = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float32)
print("Parametros del modelo base:", sum(p.numel() for p in modelo.parameters()))"""),

    ("code", [], """# Ajuste supervisado con LoRA (la perdida se calcula solo sobre la respuesta del asistente)
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer

lora = LoraConfig(r=HIPER["lora_r"], lora_alpha=HIPER["lora_alpha"], lora_dropout=HIPER["lora_dropout"],
                  target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                  task_type="CAUSAL_LM")
config = SFTConfig(output_dir=f"salida/{NOMBRE}", num_train_epochs=HIPER["epocas"], max_steps=HIPER["max_pasos"],
                   per_device_train_batch_size=HIPER["batch"], gradient_accumulation_steps=HIPER["acumulacion"],
                   learning_rate=HIPER["lr"], max_length=HIPER["max_longitud"], logging_steps=1,
                   eval_strategy="no", save_strategy="no", fp16=GPU, seed=HIPER["semilla"], report_to="none",
                   gradient_checkpointing=GPU)
trainer = SFTTrainer(model=modelo, args=config, train_dataset=train, processing_class=tokenizer, peft_config=lora)
inicio = time.time()
resultado = trainer.train()
duracion = time.time() - inicio
perdidas = [h["loss"] for h in trainer.state.log_history if "loss" in h]
print(f"Entrenamiento: {duracion:.0f} s | perdida inicial {perdidas[0]:.3f} -> final {perdidas[-1]:.3f}")"""),

    ("code", [], """# Evaluacion: perdida en el split de evaluacion y una generacion de muestra
if len(evalu):
    print("Perdida en eval:", trainer.evaluate(eval_dataset=evalu).get("eval_loss"))
muestra = (evalu if len(evalu) else train)[0]
entrada = tokenizer.apply_chat_template(muestra["prompt"], add_generation_prompt=True, return_tensors="pt").to(trainer.model.device)
with torch.no_grad():
    salida = trainer.model.generate(entrada, max_new_tokens=200, do_sample=False)
print(tokenizer.decode(salida[0][entrada.shape[1]:], skip_special_tokens=True))"""),

    ("code", [], """# Guardar adaptador, registro de hiperparametros y modelo fusionado
from peft import PeftModel
import transformers, peft, trl

os.makedirs("artefactos", exist_ok=True)
trainer.model.save_pretrained(f"artefactos/{NOMBRE}-adaptador")
registro = {"modelo_base": BASE_MODEL, "nombre": NOMBRE, "hiperparametros": HIPER, "train": len(train),
            "eval": len(evalu), "perdidas": perdidas, "segundos": round(duracion, 1), "gpu": GPU,
            "versiones": {"torch": torch.__version__, "transformers": transformers.__version__,
                          "peft": peft.__version__, "trl": trl.__version__, "python": platform.python_version()},
            "fecha": time.strftime("%Y-%m-%d %H:%M")}
json.dump(registro, open(f"artefactos/{NOMBRE}-registro.json", "w"), indent=1)

base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float16 if GPU else torch.float32)
fusionado = PeftModel.from_pretrained(base, f"artefactos/{NOMBRE}-adaptador").merge_and_unload()
fusionado.save_pretrained(f"artefactos/{NOMBRE}-fusionado", safe_serialization=True)
tokenizer.save_pretrained(f"artefactos/{NOMBRE}-fusionado")
print("Modelo fusionado en", f"artefactos/{NOMBRE}-fusionado")"""),

    ("code", ["solo-colab"], """# Convertir a GGUF F16 y cuantizar a Q4_K_M con llama.cpp
!git clone -q --depth 1 https://github.com/ggml-org/llama.cpp
!pip -q install -r llama.cpp/requirements/requirements-convert_hf_to_gguf.txt
!python llama.cpp/convert_hf_to_gguf.py artefactos/{NOMBRE}-fusionado --outtype f16 --outfile artefactos/{NOMBRE}-f16.gguf
!cmake -S llama.cpp -B llama.cpp/build -DGGML_CUDA=OFF > /dev/null && cmake --build llama.cpp/build --target llama-quantize -j 4 > /dev/null
!llama.cpp/build/bin/llama-quantize artefactos/{NOMBRE}-f16.gguf artefactos/{NOMBRE}-q4_k_m.gguf Q4_K_M
!ls -lh artefactos/*.gguf"""),

    ("code", [], """# Modelfile de Ollama (plantilla de chat de Qwen 2.5; ejecucion solo en CPU con num_gpu 0)
MODELFILE = f'''FROM ./{NOMBRE}-q4_k_m.gguf
TEMPLATE \"\"\"{{{{ if .System }}}}<|im_start|>system
{{{{ .System }}}}<|im_end|>
{{{{ end }}}}{{{{ if .Prompt }}}}<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
{{{{ end }}}}<|im_start|>assistant
{{{{ .Response }}}}<|im_end|>
\"\"\"
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|im_start|>"
PARAMETER num_ctx 4096
PARAMETER num_gpu 0
PARAMETER temperature 0.3
'''
open(f"artefactos/Modelfile", "w").write(MODELFILE)
print(MODELFILE)"""),

    ("code", ["solo-colab"], """# Publicar en Hugging Face Hub (repositorio privado) solo si HF_REPO esta definido
if HF_REPO:
    from google.colab import userdata
    from huggingface_hub import HfApi
    api = HfApi(token=userdata.get("HF_TOKEN"))
    api.create_repo(HF_REPO, private=True, exist_ok=True)
    for archivo in [f"{NOMBRE}-q4_k_m.gguf", "Modelfile", f"{NOMBRE}-registro.json"]:
        api.upload_file(path_or_fileobj=f"artefactos/{archivo}", path_in_repo=archivo, repo_id=HF_REPO)
    api.upload_folder(folder_path=f"artefactos/{NOMBRE}-adaptador", path_in_repo="adaptador", repo_id=HF_REPO)
    print("Publicado en https://huggingface.co/" + HF_REPO)"""),

    ("code", ["solo-colab"], """# Descargar los artefactos para probarlos en un computador sin GPU
!cd artefactos && zip -q -r ../{NOMBRE}.zip {NOMBRE}-q4_k_m.gguf Modelfile {NOMBRE}-registro.json
from google.colab import files
files.download(f"{NOMBRE}.zip")"""),

    ("markdown", [], """## Prueba en CPU (en el computador local)

```bash
unzip savio-slm-0.5b-v1.zip -d savio-slm && cd savio-slm
ollama create savio-slm-0.5b-v1 -f Modelfile
ollama run savio-slm-0.5b-v1 --verbose
```

El `Modelfile` fija `num_gpu 0`: el modelo corre solo en CPU (0 MB de VRAM). Registrar latencia, tokens/s y RAM con el protocolo de la seccion 17 de la formulacion."""),
]


def construir() -> dict:
    celdas = []
    for tipo, etiquetas, fuente in CELDAS:
        celda = {"cell_type": tipo, "metadata": {"tags": etiquetas} if etiquetas else {},
                 "source": fuente.splitlines(keepends=True)}
        if tipo == "code":
            celda.update(execution_count=None, outputs=[])
        celdas.append(celda)
    return {"cells": celdas, "metadata": {"accelerator": "GPU", "colab": {"provenance": []},
                                         "kernelspec": {"name": "python3", "display_name": "Python 3"},
                                         "language_info": {"name": "python"}},
            "nbformat": 4, "nbformat_minor": 5}


if __name__ == "__main__":
    DESTINO.write_text(json.dumps(construir(), indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Notebook escrito en {DESTINO}")
