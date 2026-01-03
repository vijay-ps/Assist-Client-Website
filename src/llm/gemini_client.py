import os
from dotenv import load_dotenv
from google import genai
from utils.text_cleaner import clean_llm_output

load_dotenv()

_client = None

def get_client():
    global _client
    if _client:
        return _client
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    
    _client = genai.Client(api_key=api_key)
    return _client

def ask_gemini(context_text: str) -> str:
    try:
        client = get_client()
        prompt = f"""
You are a senior corporate professional.

Respond in plain text only.
No bullet points. No markdown.
Be concise, calm, and confident.

Recent conversation:
{context_text}
"""
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return clean_llm_output(response.text)
    except Exception as e:
        return f"AI Error: {str(e)}"
