from dotenv import load_dotenv
import requests
import os

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') # requires OpenAI Realtime API Access
url = "https://api.openai.com/v1/realtime/sessions"

headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-4o-realtime-preview-2024-12-17",
    "modalities": ["audio", "text"],
    "instructions": "You are a friendly assistant."
}

response = requests.post(url, json=data, headers=headers)

print(response.json())  # Print API response
