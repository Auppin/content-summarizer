import os
import re
import google.generativeai as genai
from dotenv import load_dotenv
from gemini_helper import get_gemini_model

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not GEMINI_KEY:
    raise RuntimeError("Please set GEMINI_API_KEY or GOOGLE_API_KEY in your .env file")

genai.configure(api_key=GEMINI_KEY)

def clean_text(text: str, max_len: int = 5000) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    cleaned_lines = [ln for ln in lines if not re.fullmatch(r'\d{1,4}', ln) and len(ln) >= 3]
    cleaned = "\n".join(cleaned_lines)
    return cleaned[:max_len]

def build_prompt(text: str, length: str = "medium", action_items: bool = False) -> str:
    length_map = {
        "short": "Write a concise 2–3 line summary.",
        "medium": "Write a clear one-paragraph summary (3–6 sentences).",
        "detailed": "Write a detailed summary with multiple paragraphs highlighting main points, context, and implications."
    }
    length_instr = length_map.get(length, length_map["medium"])
    actions_instr = "\n\nAlso provide a separate 'Action Items' section as a bulleted list with 3–6 practical actions or next steps." if action_items else ""
    return (
        f"You are an expert content summarizer.\n\n{length_instr}\n"
        f"Be factual, use plain language, and emphasize key findings and takeaways.\n"
        f"{actions_instr}\n\nBegin with:\nSummary:\n<summary here>\n\n"
        "Text to summarize:\n----\n"
        f"{text}\n----"
    )

def summarize_text(text: str, length: str = "medium", action_items: bool = False) -> str:
    model = get_gemini_model()
    prompt = build_prompt(text, length, action_items)
    response = model.generate_content(prompt)
    return response.text.strip() if response and response.text else "No summary generated."
