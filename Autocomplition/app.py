from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch, json, os

# ─────────────────────────────────────────────────────────────────────────────
# 1) FastAPI & device setup
# ─────────────────────────────────────────────────────────────────────────────
app    = FastAPI()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ─────────────────────────────────────────────────────────────────────────────
# 2) Load fine‑tuned GPT-2 & tokenizer
# ─────────────────────────────────────────────────────────────────────────────
MODEL_DIR = os.path.abspath("best-stm32-pytorch/best-stm32-pytorch")
tokenizer = GPT2Tokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
model     = GPT2LMHeadModel.from_pretrained(MODEL_DIR, local_files_only=True).to(device)
model.eval()

# ─────────────────────────────────────────────────────────────────────────────
# 3) Load your static tables
#    • symbol_table.json → {"symbols":[{"name",...}], "snippets":[...]}
#    • stm32_snippets.txt  → list of valid code lines
# ─────────────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
with open(os.path.join(BASE, "symbol_table.json")) as f:
    sym_tbl = json.load(f)
symbol_names = {s["name"] for s in sym_tbl["symbols"]}

with open(os.path.join(BASE, "stm32_snippets.txt"), encoding="utf-8") as f:
    static_snippets = [ln.strip() for ln in f if ln.strip()]


def fallback(prefix: str) -> str:
    """Return the suffix of the first snippet that starts with prefix, or empty."""
    for sn in static_snippets:
        if sn.startswith(prefix):
            return sn[len(prefix):]
    return ""

# ─────────────────────────────────────────────────────────────────────────────
# 4) Request schema
# ─────────────────────────────────────────────────────────────────────────────
class PrefixRequest(BaseModel):
    prefix: str

# ─────────────────────────────────────────────────────────────────────────────
# 5) /predict endpoint
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/predict")
async def predict(req: PrefixRequest):
    prefix = (req.prefix or "").strip()
    if not prefix:
        raise HTTPException(400, "`prefix` must be non-empty")

    # Tokenize & send to device
    inputs = tokenizer(prefix, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Generation parameters
    gen_kwargs = {
        "max_new_tokens": 24,
        "pad_token_id": tokenizer.eos_token_id,
        "eos_token_id": tokenizer.eos_token_id,
        "early_stopping": True
    }
    if len(prefix) <= 5:
        # Very short: beam search for stability
        gen_kwargs.update(do_sample=False, num_beams=5)
    else:
        # Longer: nucleus sampling for variety
        gen_kwargs.update(do_sample=True, temperature=0.8, top_p=0.9)

    # Generate
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)

    # Decode the full text (prefix + continuation)
    full = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # If the model preserved the prefix, extract continuation
    if full.startswith(prefix):
        cont = full[len(prefix):].strip()
        # Determine the base token (function or keyword)
        base_tok = (prefix + cont).split('(')[0].split()[0]
        # Only accept if base_tok is in your real symbol list
        if base_tok in symbol_names:
            # Truncate at first semicolon/newline
            if ";" in cont:
                cont = cont.split(";", 1)[0] + ";"
            elif "\n" in cont:
                cont = cont.split("\n", 1)[0]
            return {"completion": cont}
 
    # Otherwise, fallback to static snippet
    cont = fallback(prefix)
    if cont:
        return {"completion": cont}

    # If still nothing valid, return empty
    return {"completion": ""}

# ─────────────────────────────────────────────────────────────────────────────
# 6) Run with Uvicorn
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)



#old code

# from fastapi import FastAPI
# from pydantic import BaseModel
# from transformers import GPT2LMHeadModel, GPT2Tokenizer
# import torch

# # Initialize FastAPI
# app = FastAPI()

# # Path to your model and tokenizer
# model_dir = "C:/Users/ASUS/Desktop/VS extension/best-stm32-pytorch/best-stm32-pytorch"

# # Load model and tokenizer
# tokenizer = GPT2Tokenizer.from_pretrained(model_dir, local_files_only=True)
# model = GPT2LMHeadModel.from_pretrained(model_dir, local_files_only=True)

# # Set model to evaluation mode
# model.eval()

# # Define the input structure for the request
# class Request(BaseModel):
#     prefix: str

# # Define the prediction route
# @app.post("/predict")
# async def predict(request: Request):
#     # Tokenize input text
#     inputs = tokenizer(request.prefix, return_tensors="pt")

#     # Generate model outputs
#     with torch.no_grad():
#         outputs = model.generate(inputs["input_ids"], max_length=100)

#     # Decode the generated output
#     decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
#     return {"generated_text": decoded_output}

# # Run the app
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)