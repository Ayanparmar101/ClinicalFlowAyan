"""Test Gemini with REST API"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

payload = {
    "contents": [{
        "parts": [{
            "text": "What is a clinical trial? Answer in 2 sentences."
        }]
    }],
    "generationConfig": {
        "temperature": 0.3,
        "maxOutputTokens": 200
    }
}

print("Testing Gemini API via REST...")
print(f"Model: gemini-1.5-flash")
print(f"API Key: {api_key[:20]}...")

try:
    response = requests.post(url, json=payload)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"\n✓✓✓ SUCCESS! Gemini is working flawlessly! ✓✓✓\n")
            print(f"Response:\n{text}\n")
            print("=" * 60)
            print("Gemini AI is configured correctly and ready to use!")
            print("=" * 60)
        else:
            print(f"Unexpected response format: {result}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
