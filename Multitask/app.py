import re
import json
import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import T5ForConditionalGeneration, T5Tokenizer

import joblib
import numpy as np
from tensorflow.keras.models import load_model

from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os

from transformers import RobertaTokenizer
from peft import PeftModel

# ---------- INITIALISATION FASTAPI ----------
app = FastAPI()

# Chemin vers ton dossier modèle (tokenizer + modèle + adapter)
model_dir = "./code"

# Vérifie que le dossier existe
if not os.path.exists(model_dir):
    raise FileNotFoundError(f"Dossier modèle introuvable : {model_dir}")

# Charge le tokenizer et le modèle depuis ce dossier
tokenizer = RobertaTokenizer.from_pretrained(model_dir)
model = T5ForConditionalGeneration.from_pretrained(model_dir)

# Charge l'adapter PEFT depuis le même dossier
adapter_path = model_dir
if not os.path.exists(os.path.join(adapter_path, "adapter_config.json")):
    raise FileNotFoundError(f"Adapter introuvable dans {adapter_path}")

model = PeftModel.from_pretrained(model, adapter_path)
model.eval()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_code(request: PromptRequest):
    prompt = request.prompt
    input_text = f"Generate STM32 code for: {prompt}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=200, num_beams=5)
    generated_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"code": generated_code}



# ---------- CONFIGURATION ----------
# Détection de l'appareil (GPU ou CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------- CHARGEMENT DU VOCABULAIRE ----------
with open("vocab.json", "r") as f:
    vocab = json.load(f)

# ---------- MODELE DE CLASSIFICATION BI-LSTM ----------
class BugClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim=64, hidden_dim=128):
        super(BugClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.embedding(x)
        _, (hn, _) = self.lstm(x)
        hn = torch.cat((hn[-2], hn[-1]), dim=1)
        out = self.fc(hn)
        return self.sigmoid(out)

# Chargement du modèle LSTM
bug_model = BugClassifier(len(vocab)).to(device)
bug_model.load_state_dict(torch.load("bug_classifier.pth", map_location=device))
bug_model.eval()

# ---------- CHARGEMENT DU MODELE T5 ----------
MODEL_PATH = "AI/modeles"  # À adapter selon l'organisation de ton dossier
tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH)
t5_model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH).to(device)
t5_model.eval()

# ---------- SCHEMAS ----------
class CodeRequest(BaseModel):
    code: str

# ---------- FONCTION DE NETTOYAGE DU CODE ----------
def clean_code(code: str) -> str:
    return re.sub(r'\s+', ' ', code.strip())

# ---------- TOKENIZER POUR LSTM ----------
def tokenize_for_lstm(code: str):
    tokens = code.strip().split()
    ids = [vocab.index(tok) if tok in vocab else vocab.index("<UNK>") for tok in tokens]
    return torch.tensor([ids], dtype=torch.long).to(device)

# ---------- FONCTION : GENERATION DE COMMENTAIRES ----------
def generate_comment(code: str, max_length: int = 128) -> str:
    code = clean_code(code)
    input_text = f"generate comment: {code}"
    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=512
    ).to(device)

    outputs = t5_model.generate(
        **inputs,
        max_length=max_length,
        num_beams=5,
        early_stopping=True
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# ---------- ENDPOINT : COMMENTAIRE ----------
@app.post("/generate-comment")
async def generate_comment_api(request: CodeRequest):
    try:
        comment = generate_comment(request.code)
        return {"commented_code": comment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- ENDPOINT : CLASSIFICATION BUGGY ----------
@app.post("/predict")
def predict_bug_api(request: CodeRequest):
    try:
        inputs = tokenize_for_lstm(request.code)
        with torch.no_grad():
            output = bug_model(inputs)
            pred = int(output.item() > 0.5)
        label = "buggy" if pred == 1 else "clean"
        return {"prediction": label}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- CHARGEMENT DU MODELE DE DETECTION D'ERREURS (Keras + Vectorizer) ----------
vectorizer = joblib.load("vectorizer.joblib")
label_encoder = joblib.load("label_encoder.joblib")
keras_model = load_model("model.h5")

# ---------- FONCTION DE PREDICTION DU TYPE D'ERREUR ----------
def predict_error_type(code_snippet: str) -> str:
    X = vectorizer.transform([code_snippet]).toarray()
    proba = keras_model.predict(X, verbose=0)
    idx = int(np.argmax(proba, axis=1)[0])
    return label_encoder.inverse_transform([idx])[0]

# ---------- ENDPOINT : PREDICTION DU TYPE D'ERREUR ----------
@app.post("/predict-error-type")
def predict_error_type_api(request: CodeRequest):
    try:
        if not request.code.strip():
            raise HTTPException(status_code=400, detail="Code is empty.")
        error_type = predict_error_type(request.code)
        return {"error_type": error_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- ENDPOINT : PREDICTION DU TYPE D'ERREUR PAR LIGNE ----------
@app.post("/predict-lines-error-type")
def predict_lines_error_type_api(request: CodeRequest):
    try:
        lines = request.code.splitlines()
        results = []
        for i, line in enumerate(lines, start=1):
            etype = predict_error_type(line)
            if etype != "aucune erreur":
                results.append({"line": i, "error_type": etype, "code": line})
        return {"errors": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- CHARGEMENT DU MODELE GPT-2 POUR STM32 ----------
MODEL_DIR = os.path.abspath("best-stm32-pytorch")
tokenizer_gpt2 = GPT2Tokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
model_gpt2 = GPT2LMHeadModel.from_pretrained(MODEL_DIR, local_files_only=True).to(device)
model_gpt2.eval()

# ---------- CHARGEMENT DES SNIPPETS ET SYMBOLES ----------
with open("symbol_table.json") as f:
    sym_tbl = json.load(f)
symbol_names = {s["name"] for s in sym_tbl["symbols"]}

with open("stm32_snippets.txt", encoding="utf-8") as f:
    static_snippets = [ln.strip() for ln in f if ln.strip()]

# ---------- FONCTION DE RETOUR STATIQUE EN CAS D'ECHEC ----------
def fallback(prefix: str) -> str:
    for sn in static_snippets:
        if sn.startswith(prefix):
            return sn[len(prefix):]
    return ""

# ---------- SCHEMA DE DEMANDE POUR AUTOCOMPLETION ----------
class PrefixRequest(BaseModel):
    prefix: str

@app.post("/stm32-autocomplete")
async def predict_stm32(req: PrefixRequest):
    prefix = (req.prefix or "").strip()
    if not prefix:
        raise HTTPException(400, "`prefix` must be non-empty")

    inputs = tokenizer_gpt2(prefix, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    gen_kwargs = {
        "max_new_tokens": 24,
        "pad_token_id": tokenizer_gpt2.eos_token_id,
        "eos_token_id": tokenizer_gpt2.eos_token_id,
        "early_stopping": True
    }
    if len(prefix) <= 5:
        gen_kwargs.update(do_sample=False, num_beams=5)
    else:
        gen_kwargs.update(do_sample=True, temperature=0.8, top_p=0.9)

    with torch.no_grad():
        outputs = model_gpt2.generate(**inputs, **gen_kwargs)

    full = tokenizer_gpt2.decode(outputs[0], skip_special_tokens=True)

    if full.startswith(prefix):
        cont = full[len(prefix):].strip()
        base_tok = (prefix + cont).split('(')[0].split()[0]
        if base_tok in symbol_names:
            if ";" in cont:
                cont = cont.split(";", 1)[0] + ";"
            elif "\n" in cont:
                cont = cont.split("\n", 1)[0]
            return {"completion": cont}

    cont = fallback(prefix)
    return {"completion": cont if cont else ""}



# ---------- ROOT ----------
@app.get("/")
def read_root():
    return {"message": "API combinée pour génération de commentaires et détection de bugs"}

# ---------- EXECUTION ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
