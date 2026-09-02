import os
from .config import GEMINI_MODEL

_client = None
def get_client():
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY")
        if not key: raise RuntimeError("GEMINI_API_KEY is not configured")
        try:
            from google import genai
        except ImportError as error:
            raise RuntimeError("google-genai is not installed") from error
        _client = genai.Client(api_key=key)
    return _client

def structured(prompt: str, schema):
    response = get_client().models.generate_content(model=GEMINI_MODEL, contents=prompt, config={"response_mime_type": "application/json", "response_schema": schema})
    if getattr(response, "parsed", None) is None: raise RuntimeError("Gemini returned no structured response")
    return response.parsed

def grounded_answer(question: str, passages: list[dict]) -> str:
    """Explain only supplied, reviewed sources; Gemini never supplies legal facts itself."""
    context = "\n\n".join(f"SOURCE {i + 1}\nTitle: {item['title']}\nCitation: {item['citation']}\nPassage: {item['text']}" for i, item in enumerate(passages))
    prompt = f"""You are Clauz X, an Indian business compliance assistant. Answer in careful plain English using ONLY the verified passages below. Do not invent dates, thresholds, penalties, or section numbers. If the passages do not answer the question, say so. Keep the response under 150 words.\n\nQuestion: {question}\n\nVerified passages:\n{context}"""
    response = get_client().models.generate_content(model=GEMINI_MODEL, contents=prompt)
    if not getattr(response, "text", None): raise RuntimeError("Gemini returned no answer")
    return response.text.strip()
