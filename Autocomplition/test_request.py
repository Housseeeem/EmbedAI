import requests

# 1) List of prefixes you want to test
prefixes = [
    "HAL_",
    "ww",
    "whi",
    "whil",
    "while",
    "f",
    "fo",
    "pr",
    "prin",
    "print"
]

# 2) Dict to hold results
results = {}

# 3) Loop over each prefix and call the API
for prefix in prefixes:
    try:
        resp = requests.post(
            "http://127.0.0.1:8000/predict",
            json={"prefix": prefix},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            # adapt the key if your API returns {"completion": ...} or {"generated_text": ...}
            suggestion = data.get("completion") or data.get("generated_text") or ""
            results[prefix] = suggestion
        else:
            results[prefix] = f"<HTTP {resp.status_code}> {resp.text}"
    except Exception as e:
        results[prefix] = f"<Error> {e}"

# 4) Print them out in a neat table
print("\nPrefix → Suggestion\n" + "-"*30)
for prefix, suggestion in results.items():
    print(f"{prefix:10} → {suggestion}")
