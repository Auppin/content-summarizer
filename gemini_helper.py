import google.generativeai as genai

# Auto fallback logic
def get_gemini_model():
    preferred_models = [
        "models/gemini-2.0-flash",
        "models/gemini-1.5-flash",
        "models/gemini-pro"
    ]

    for model_name in preferred_models:
        try:
            model = genai.GenerativeModel(model_name)
            # Test call to confirm model availability
            model.generate_content("ping")
            return model
        except Exception:
            continue

    raise RuntimeError("No available Gemini model found. Check API key or model access.")
