import os
import random
import config
from groq import Groq

# Initialize Groq client
client = Groq(api_key="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")

def test_ai_connection():
    """Tests if the Groq API key is set and model responds."""
    if not config.GROQ_API_KEY or config.GROQ_API_KEY.startswith("your_"):
        print("❌ API Connection Failed: No valid Groq API key found.")
        return False
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Test"}],
            model=config.AI_MODEL_NAME,
            max_tokens=5
        )
        return bool(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"❌ API Connection Failed: {e}")
        return False

def get_fallback_compliment():
    """Reads a fallback compliment from the local file."""
    try:
        with open(config.FALLBACK_COMPLIMENTS_PATH, 'r', encoding='utf-8') as f:
            compliments = [line.strip() for line in f if line.strip()]
        return random.choice(compliments) if compliments else "You are definitely a person."
    except FileNotFoundError:
        return "You are definitely a person."

def get_ai_response(roast_mode=False, attributes=None):
    """Calls the Groq AI model to get a response based on a persona."""
    if not config.ENABLE_AI:
        return get_fallback_compliment()

    if roast_mode:
        prompt = (
            "You are a grumpy, sarcastic robot. Make a witty, observational roast "
            "about the user's general appearance. It must be clever and funny, not "
            "genuinely mean. Provide only the roast in one sentence."
        )
    else:
        prompt = (
            "You are an overly dramatic, theatrical AI. Give a user an absurdly grand, "
            "one-sentence compliment. Provide only the compliment."
        )

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=config.AI_MODEL_NAME,
            max_tokens=40,
            temperature=0.9
        )
        text = response.choices[0].message.content.strip().replace('"', '')
        if text:
            print(f"🤖 AI Response: {text}")
            return text
        raise ValueError("AI returned empty text.")
    except Exception as e:
        print(f"❌ AI Error: {e}. Using fallback.")
        return get_fallback_compliment()
