import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("XAI_API_KEY")
model = os.getenv("XAI_MODEL", "grok-4.5")

print("API KEY LOADED:", bool(api_key))
print("MODEL:", model)

response = requests.post(
    "https://api.x.ai/v1/chat/completions",
    headers={
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    },
    json={
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Say hello"
            }
        ]
    },
    timeout=60
)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)
