"""API client for the FoodShare backend."""
import streamlit as st
import requests

def get_base_url():
    try:
        return st.secrets["api"]["base_url"]
    except Exception:
        return "http://localhost:5000/api"

def get_headers():
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"} if token else {"Content-Type": "application/json"}

def api_get(path, params=None):
    try:
        r = requests.get(f"{get_base_url()}{path}", headers=get_headers(), params=params, timeout=10)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Make sure the API server is running on port 5000."}, 503
    except Exception as e:
        return {"error": str(e)}, 500

def api_post(path, data=None):
    try:
        r = requests.post(f"{get_base_url()}{path}", headers=get_headers(), json=data, timeout=15)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend."}, 503
    except Exception as e:
        return {"error": str(e)}, 500

def api_put(path, data=None):
    try:
        r = requests.put(f"{get_base_url()}{path}", headers=get_headers(), json=data, timeout=10)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend."}, 503
    except Exception as e:
        return {"error": str(e)}, 500

def api_delete(path):
    try:
        r = requests.delete(f"{get_base_url()}{path}", headers=get_headers(), timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500
