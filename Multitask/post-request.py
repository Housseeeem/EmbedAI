import requests

url = "http://127.0.0.1:8000/generate-comment"  # Change this to the correct URL of your FastAPI app
headers = {"Content-Type": "application/json"}
data = {
    "code": "void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) { if (htim->Instance == TIM2) { HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5); } }"
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    print("Comment Generated:", response.json())  # Print the generated comment
else:
    print(f"Error: {response.status_code}, {response.text}")
