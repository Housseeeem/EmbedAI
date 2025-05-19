import re
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

# 1) Point this at your model folder
MODEL_PATH = "C:\\Users\\Dell\\Desktop\\AI\\modeles"

# 2) Load
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH)
model     = T5ForConditionalGeneration.from_pretrained(MODEL_PATH).to(device)


def clean_code(code: str) -> str:
    code = re.sub(r'\s+', ' ', code.strip())
    code = re.sub(r'\n+', ' ', code)
    return code


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

    outputs = model.generate(
        **inputs,
        max_length=max_length,
        num_beams=5,
        early_stopping=True
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


if __name__ == "__main__":
    # Example STM32 snippet
    sample_code = """
    void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
    {
        if (htim->Instance == TIM2)
        {
            HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
        }
    }

        """

    comment = generate_comment(sample_code)
    print("📝 Generated comment:\n", comment)