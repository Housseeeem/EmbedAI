import json
import torch
import torch.nn as nn
from fastapi import FastAPI
from pydantic import BaseModel

# ----- Load vocabulary -----
with open("vocab.json", "r") as f:
    vocab = json.load(f)

# ----- BugClassifier (bi-LSTM) -----
class BugClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim=64, hidden_dim=128):
        super(BugClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, 1)  # bi-LSTM => hidden_dim * 2
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.embedding(x)
        _, (hn, _) = self.lstm(x)
        hn = torch.cat((hn[-2], hn[-1]), dim=1)  # concat forward + backward
        out = self.fc(hn)
        return self.sigmoid(out)

# ----- Model setup -----
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = BugClassifier(len(vocab)).to(device)
model.load_state_dict(torch.load("bug_classifier.pth", map_location=device))
model.eval()

# ----- FastAPI setup -----
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bug Classifier API is running!"}

# ----- Input schema -----
class CodeInput(BaseModel):
    code: str

# ----- Tokenizer -----
def tokenize(code: str):
    tokens = code.strip().split()  # simple tokenizer
    ids = [vocab.index(tok) if tok in vocab else vocab.index("<UNK>") for tok in tokens]
    return torch.tensor([ids], dtype=torch.long).to(device)

# ----- Prediction endpoint -----
@app.post("/predict")
def predict(input_data: CodeInput):
    print(input_data)  # Add this line to log the input
    inputs = tokenize(input_data.code)
    with torch.no_grad():
        output = model(inputs)
        pred = int(output.item() > 0.5)
    label = "buggy" if pred == 1 else "clean"
    return {"prediction": label}