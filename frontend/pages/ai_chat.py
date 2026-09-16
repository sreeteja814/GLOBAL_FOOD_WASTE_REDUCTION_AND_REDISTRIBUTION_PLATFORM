"""AI Chat Assistant page — calls HuggingFace directly, no backend needed."""
import streamlit as st
import requests

SYSTEM_CONTEXT = "You are FoodShare AI, a helpful assistant for the Global Food Waste Reduction Platform. Help users with food donation listings, reducing food waste, platform navigation, and impact insights."

SUGGESTIONS = [
    "What food listings are expiring soon?",
    "How can I reduce food waste at my restaurant?",
    "What's my current impact on reducing food waste?",
    "How does the AI matching system work?",
    "Tips for creating better food listings",
    "How do I approve a food request?",
]

HF_ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"
HF_MODELS = [
    "Qwen/Qwen2.5-7B-Instruct:hf-inference",
    "microsoft/Phi-3-mini-4k-instruct:hf-inference",
    "HuggingFaceH4/zephyr-7b-beta:hf-inference",
]

def get_hf_token():
    try:
        return st.secrets["huggingface"]["token"]
    except Exception:
        return ""


def call_hf(user_message: str, history: list) -> str:
    token = get_hf_token()
    if not token:
        return "⚠️ HuggingFace token not found in secrets.toml. Please add it and restart."

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Build message list in OpenAI chat format, including recent history for context
    messages = [{"role": "system", "content": SYSTEM_CONTEXT}]
    for m in history[-6:]:
        role = "assistant" if m["role"] == "assistant" else "user"
        messages.append({"role": role, "content": m["content"]})
    messages.append({"role": "user", "content": user_message})

    last_error = None
    for model in HF_MODELS:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 300,
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
                continue

        except requests.exceptions.Timeout:
            last_error = "Request timed out"
            continue
        except Exception as e:
            last_error = str(e)
            continue

    return f"⚠️ AI Error: all models failed. Last error: {last_error}"


def show_chat():
    st.markdown("""
    <div class="hero-banner">
      <h1>🤖 AI Chat Assistant</h1>
      <p>Powered by HuggingFace — Ask anything about food waste reduction, listings, and the platform.</p>
    </div>
    """, unsafe_allow_html=True)

    token = get_hf_token()
    if not token:
        st.error(
            "⚠️ HuggingFace token not found in secrets.toml. Please add it and restart the app.")
        return

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": "Hi! I'm FoodShare AI, powered by HuggingFace. I can help you find food donations, reduce waste, and navigate the platform. How can I help you today?"
        }]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    with st.expander("💡 Suggested questions"):
        for s in SUGGESTIONS:
            if st.button(s, key=f"sugg_{s}"):
                st.session_state.chat_history.append(
                    {"role": "user", "content": s})
                with st.spinner("Thinking..."):
                    reply = call_hf(s, st.session_state.chat_history)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": reply})
                st.rerun()

    user_input = st.chat_input("Type your message here...")
    if user_input:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            reply = call_hf(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply})
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": "Chat cleared! How can I help you today?"
        }]
        st.rerun()


if __name__ == "__main__":
    show_chat()
