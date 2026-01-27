"""
List all available Gemini models for the current API key
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing API Key: {api_key[:10]}...")
print("-" * 50)

try:
    # Configure API
    genai.configure(api_key=api_key)
    
    # List all available models
    print("Available models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  ✓ {model.name}")
    
    print("\n✓ API key is valid!")
    
except Exception as e:
    print(f"✗ ERROR: {str(e)}")
    print("\nYour API key may be invalid or not have permissions.")
