import os
from dotenv import load_dotenv
from google import genai
from utils.text_cleaner import clean_llm_output

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(context_text: str) -> str:
    prompt = f"""
You are a senior corporate professional.

Respond in plain text only.
No bullet points. No markdown.
Be concise, calm, and confident.

Recent conversation:
{context_text}
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return clean_llm_output(response.text)
