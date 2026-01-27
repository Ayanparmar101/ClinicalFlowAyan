"""
Test Gemini API connectivity
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    print("✓ google-generativeai package is installed")
except ImportError as e:
    print(f"✗ Error: google-generativeai not installed: {e}")
    exit(1)

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-pro")

if not api_key:
    print("✗ Error: GEMINI_API_KEY not found in .env file")
    exit(1)

print(f"✓ API Key loaded: {api_key[:20]}...")
print(f"✓ Model: {model_name}")

# Configure Gemini
try:
    genai.configure(api_key=api_key)
    print("✓ Gemini API configured")
except Exception as e:
    print(f"✗ Error configuring Gemini: {e}")
    exit(1)

# Initialize model
try:
    model = genai.GenerativeModel(model_name)
    print(f"✓ Gemini model '{model_name}' initialized")
except Exception as e:
    print(f"✗ Error initializing model: {e}")
    exit(1)

# Test generation
try:
    print("\nTesting Gemini API...")
    response = model.generate_content(
        "What is a clinical trial? Answer in 2 sentences.",
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=200,
        )
    )
    
    if response.text:
        print(f"\n✓✓✓ SUCCESS! Gemini is working flawlessly! ✓✓✓\n")
        print(f"Response:\n{response.text}\n")
        print("=" * 60)
        print("Gemini AI is configured correctly and ready to use!")
        print("=" * 60)
    else:
        print("✗ Warning: Response was empty or blocked")
        if hasattr(response, 'prompt_feedback'):
            print(f"Feedback: {response.prompt_feedback}")
            
except Exception as e:
    print(f"\n✗ Error testing Gemini: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    exit(1)
