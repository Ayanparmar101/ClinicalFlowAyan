"""
Quick test to verify Gemini API key and connection
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

print(f"Testing Gemini API...")
print(f"API Key (first 10 chars): {api_key[:10]}...")
print(f"Model: {model_name}")
print("-" * 50)

try:
    # Configure API
    genai.configure(api_key=api_key)
    
    # Create model
    model = genai.GenerativeModel(model_name)
    
    # Test simple generation
    print("Sending test prompt...")
    response = model.generate_content("Say 'API key is working correctly' if you can read this.")
    
    print("\n✓ SUCCESS!")
    print(f"Response: {response.text}")
    print("\nYour Gemini API is configured correctly!")
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    print("\nPossible issues:")
    print("1. Invalid API key")
    print("2. Invalid model name")
    print("3. API key doesn't have permissions")
    print("4. Network/connection issue")
    print("\nPlease check your .env file and API key in Google AI Studio")
