from fastapi import FastAPI
from pydantic import BaseModel
from transformers import RobertaTokenizer, T5ForConditionalGeneration
from peft import PeftModel
import torch
import os

app = FastAPI()

# Load the base CodeT5 model and tokenizer from local files
model_path = "./"
tokenizer = RobertaTokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path)

# Load the fine-tuned PEFT adapter
adapter_path = "./"
if not os.path.exists(os.path.join(adapter_path, "adapter_config.json")):
    raise FileNotFoundError(f"Adapter files not found at {adapter_path}")
model = PeftModel.from_pretrained(model, adapter_path)
model.eval()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_code(request: PromptRequest):
    prompt = request.prompt
    input_text = f"Generate STM32 code for: {prompt}"  # Adjust based on your fine-tuning
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=200, num_beams=5)
    generated_code = tokenizer.decode(outputs[0], skip_special_tokens=True)  # Fixed line
    return {"code": generated_code}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)