"""Login & Register page."""
import streamlit as st
from utils.api import api_post

def show_login():
    st.markdown("""
    <div style="max-width:420px;margin:0 auto;padding-top:40px;">
      <div style="text-align:center;margin-bottom:28px;">
        <div style="width:56px;height:56px;background:#16a34a;border-radius:14px;display:inline-flex;align-items:center;justify-content:center;font-size:28px;margin-bottom:12px;">🌿</div>
        <h1 style="font-size:24px;font-weight:800;color:#111827;margin:0;">Welcome Back</h1>
        <p style="color:#6b7280;font-size:13px;margin-top:4px;">Global Food Waste Reduction and Redistribution Platform</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            with st.form("login_form"):
                email    = st.text_input("Email",    placeholder="Enter your email")
                password = st.text_input("Password", placeholder="Enter your password", type="password")
                submit   = st.form_submit_button("Login", use_container_width=True, type="primary")

            if submit:
                if not email or not password:
                    st.error("Please enter email and password.")
                else:
                    with st.spinner("Logging in…"):
                        data, status = api_post("/auth/login", {"email": email, "password": password})
                    if status == 200:
                        st.session_state.token = data["token"]
                        st.session_state.user  = data["user"]
                        st.session_state.page  = "dashboard"
                        st.success("Welcome back! 🌿")
                        st.rerun()
                    else:
                        st.error(data.get("error", "Login failed"))

            st.markdown("---")
            st.markdown("""
            <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:10px 14px;text-align:center;font-size:13px;color:#15803d;">
            🌿 Demo credentials:<br>
            <strong>demo@foodshare.com</strong> / <strong>demo1234</strong>
            </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚡ Quick Demo Login", use_container_width=True, type="primary"):
                with st.spinner("Loading demo…"):
                    data, status = api_post("/auth/login", {"email": "demo@foodshare.com", "password": "demo1234"})
                if status == 200:
                    st.session_state.token = data["token"]
                    st.session_state.user  = data["user"]
                    st.session_state.page  = "dashboard"
                    st.rerun()
                else:
                    st.error("Demo login failed. Ensure the backend is running on port 5000.")

        with tab2:
            with st.form("register_form"):
                full_name    = st.text_input("Full Name *",    placeholder="Your full name")
                reg_email    = st.text_input("Email *",        placeholder="your@email.com")
                reg_password = st.text_input("Password *",     placeholder="Min 6 characters", type="password")
                phone        = st.text_input("Phone",          placeholder="+1 234 567 8900")
                organization = st.text_input("Organization",   placeholder="Hotel, NGO, Restaurant…")
                address      = st.text_input("Address",        placeholder="123 Main Street, City")
                role         = st.selectbox("Role", ["donor", "recipient"])
                reg_submit   = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if reg_submit:
                if not full_name or not reg_email or not reg_password:
                    st.error("Name, email and password are required.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account…"):
                        data, status = api_post("/auth/register", {
                            "full_name": full_name, "email": reg_email,
                            "password": reg_password, "phone": phone,
                            "organization": organization, "address": address, "role": role
                        })
                    if status == 201:
                        st.session_state.token = data["token"]
                        st.session_state.user  = data["user"]
                        st.session_state.page  = "dashboard"
                        st.success("Account created! Welcome to FoodShare 🌿")
                        st.rerun()
                    else:
                        st.error(data.get("error", "Registration failed"))
