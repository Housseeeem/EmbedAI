from fastapi.testclient import TestClient
from app import app  # Assuming your FastAPI app is in app.py

client = TestClient(app)

def test_predict():
    response = client.post("/predict", json={"code": "int main() { int a = 5; int b = 0; int result = a / b; return 0; }"})
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert response.json()["prediction"] in ["buggy", "clean"]
