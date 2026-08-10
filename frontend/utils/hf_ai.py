"""HuggingFace Inference API helper — used by Streamlit frontend for direct AI calls.
Uses the modern router (OpenAI-compatible chat completions) endpoint, which is
more reliable than pinging individual legacy model endpoints directly.
"""
import requests
import json
import streamlit as st

# hf-inference is not available to all accounts. Use explicit model:provider
# format so the router knows exactly where to send the request.
HF_ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"

# Confirmed working for this account via the "together" provider.
HF_MODELS = [
    "Qwen/Qwen2.5-7B-Instruct:together",
]


def get_hf_token():
    try:
        return st.secrets["huggingface"]["token"]
    except Exception:
        return ""


def hf_chat(system_prompt: str, user_message: str, max_tokens: int = 300) -> str:
    """Call HuggingFace hf-inference provider, trying multiple models until one works."""
    token = get_hf_token()
    if not token:
        return "⚠️ HuggingFace token not found in secrets.toml. Please add it and restart."

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    last_error = None
    for model in HF_MODELS:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.4
        }
        try:
            r = requests.post(HF_ROUTER_URL, headers=headers,
                              json=payload, timeout=60)
            data = r.json()

            if r.status_code == 200:
                choices = data.get("choices", [])
                if choices and choices[0].get("message", {}).get("content"):
                    return choices[0]["message"]["content"].strip()

            if isinstance(data, dict) and data.get("error"):
                err = data["error"]
                err_msg = err.get("message", str(err)) if isinstance(
                    err, dict) else str(err)
                last_error = err_msg
                # Try next model in the list
                continue

        except requests.exceptions.Timeout:
            last_error = "Request timed out"
            continue
        except Exception as e:
            last_error = str(e)
            continue

    return f"⚠️ AI Error: all models failed. Last error: {last_error}"


def hf_analyze_food_waste(listings_data: list) -> str:
    """Analyze food waste patterns from listings."""
    system = (
        "You are a food waste reduction expert AI. "
        "Analyze the provided food listing data and give a short 3-bullet insight "
        "about patterns, urgency, and recommendations. Be concise."
    )
    user = f"Analyze these food listings: {json.dumps(listings_data[:10])}"
    return hf_chat(system, user, max_tokens=250)


def hf_match_recommendation(listing: dict, user_profile: dict) -> str:
    """Get AI recommendation for a specific listing-user match."""
    system = (
        "You are a food donation matching AI. "
        "In 2 sentences, explain why this listing is or isn't a good match for this recipient. Be direct."
    )
    user = f"Listing: {json.dumps(listing)}\nRecipient: {json.dumps(user_profile)}"
    return hf_chat(system, user, max_tokens=150)


def hf_impact_summary(metrics: dict) -> str:
    """Generate a personalized impact summary."""
    system = (
        "You are an impact reporting AI for a global food waste reduction platform. "
        "Write 2 motivating sentences summarizing this donor's positive environmental impact."
    )
    user = f"Metrics: {json.dumps(metrics)}"
    return hf_chat(system, user, max_tokens=150)
