"""
🌍 Global Food Waste Reduction and Redistribution Platform
Streamlit Frontend — Main Entry Point
"""
import streamlit as st

st.set_page_config(
    page_title="FoodShare — Global Food Waste Reduction Platform",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e5e7eb; }
[data-testid="stSidebar"] .block-container { padding-top: 1rem; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
[data-testid="metric-container"] label { font-size: 13px !important; color: #6b7280 !important; font-weight: 600 !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 26px !important; font-weight: 800 !important; color: #111827 !important; }

/* Buttons */
.stButton > button {
    border-radius: 8px !important; font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all .15s !important;
}
.stButton > button[kind="primary"] {
    background: #16a34a !important; border: none !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover { background: #15803d !important; }

/* Cards */
.fs-card {
    background: #fff; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 18px; margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.fs-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.10); }
.fs-card h3 { font-size: 18px; font-weight: 700; color: #111827; margin: 0 0 8px 0; }
.fs-card p  { font-size: 13px; color: #6b7280; margin: 3px 0; }

/* Tag badges */
.tag { display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:700; margin-right:4px; }
.tag-available  { background:#dcfce7; color:#15803d; }
.tag-urgent     { background:#fef3c7; color:#92400e; }
.tag-category   { background:#f3f4f6; color:#4b5563; }
.tag-completed  { background:#dbeafe; color:#1e40af; }
.tag-expired    { background:#f3f4f6; color:#9ca3af; }
.tag-pending    { background:#fef3c7; color:#92400e; }
.tag-approved   { background:#dcfce7; color:#15803d; }
.tag-rejected   { background:#fee2e2; color:#991b1b; }

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #15803d, #22c55e);
    border-radius: 14px; padding: 28px; color: #fff; margin-bottom: 24px;
}
.hero-banner h1 { font-size: 24px; font-weight: 800; margin: 0 0 6px 0; }
.hero-banner p  { font-size: 14px; opacity: .9; margin: 0; }

/* AI insight box */
.ai-box {
    background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px;
    padding: 14px 16px; margin: 10px 0;
}
.ai-box p { font-size: 13px; color: #166534; margin: 0; }

/* Notification row */
.notif-row {
    background: #fff; border: 1px solid #e5e7eb; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 8px;
    border-left: 4px solid #22c55e;
}
.notif-row.urgent  { border-left-color: #ef4444; }
.notif-row.warning { border-left-color: #f59e0b; }
.notif-row.success { border-left-color: #22c55e; }
.notif-row.info    { border-left-color: #3b82f6; }
.notif-row strong  { font-size: 14px; color: #111827; }
.notif-row span    { font-size: 13px; color: #6b7280; }

/* Chat bubble */
.chat-user { background:#16a34a; color:#fff; border-radius:12px 12px 4px 12px; padding:10px 14px; margin:4px 0; max-width:80%; margin-left:auto; font-size:14px; }
.chat-ai   { background:#f3f4f6; color:#1f2937; border-radius:12px 12px 12px 4px; padding:10px 14px; margin:4px 0; max-width:80%; font-size:14px; }

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* Hide auto-generated Streamlit page navigation */
[data-testid="stSidebarNav"]      { display: none !important; }
[data-testid="stSidebarNavItems"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Session init ──────────────────────────────────────────────────────────────
for key, default in {
    "token": None, "user": None,
    "page": "login", "chat_history": [],
    "listing_filter_cat": "All", "listing_search": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Router ────────────────────────────────────────────────────────────────────
if not st.session_state.token:
    from pages.login import show_login
    show_login()
else:
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0 16px 0;border-bottom:1px solid #e5e7eb;margin-bottom:12px;">
            <div style="width:36px;height:36px;background:#16a34a;border-radius:10px;display:grid;place-items:center;font-size:18px;">🌿</div>
            <div style="font-size:15px;font-weight:800;color:#111827;line-height:1.2;">FoodShare</div>
        </div>
        """, unsafe_allow_html=True)

        user = st.session_state.user or {}
        initials = "".join(w[0] for w in user.get(
            "full_name", "U U").split()[:2]).upper()
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:10px 0;margin-bottom:12px;">
            <div style="width:40px;height:40px;background:#16a34a;border-radius:50%;display:grid;place-items:center;color:#fff;font-weight:800;font-size:15px;flex-shrink:0;">{initials}</div>
            <div><div style="font-size:14px;font-weight:700;color:#111827;">{user.get('full_name', 'Demo User')}</div>
            <div style="font-size:12px;color:#6b7280;text-transform:capitalize;">{user.get('role', 'donor')}</div></div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("🏠", "Dashboard",        "dashboard"),
            ("➕", "Create Listing",    "create_listing"),
            ("🔍", "Browse Listings",   "browse"),
            ("📦", "Manage Requests",   "requests"),
            ("📍", "Pickup Tracking",   "pickup"),
            ("📈", "Impact Dashboard",  "impact"),
            ("🤖", "AI Chat Assistant", "chat"),
            ("🔔", "Notifications",     "notifications"),
            ("👤", "Profile",           "profile"),
        ]
        for icon, label, key in nav_items:
            is_active = st.session_state.page == key
            btn_style = "primary" if is_active else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True, type=btn_style):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:8px 10px;text-align:center;font-size:12px;color:#15803d;margin-bottom:8px;">
        🌿 Demo Mode Active<br><span style="opacity:.7">Sample data shown</span>
        </div>""", unsafe_allow_html=True)

        if st.button("↩  Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = "login"
            st.session_state.chat_history = []
            st.rerun()

    # Page routing
    page = st.session_state.page
    if page == "dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif page == "browse":
        from pages.browse_listings import show_browse
        show_browse()
    elif page == "create_listing":
        from pages.create_listing import show_create
        show_create()
    elif page == "requests":
        from pages.manage_requests import show_requests
        show_requests()
    elif page == "pickup":
        from pages.pickup_tracking import show_pickup
        show_pickup()
    elif page == "impact":
        from pages.impact_dashboard import show_impact
        show_impact()
    elif page == "chat":
        from pages.ai_chat import show_chat
        show_chat()
    elif page == "notifications":
        from pages.notifications import show_notifications
        show_notifications()
    elif page == "profile":
        from pages.profile import show_profile
        show_profile()
    else:
        from pages.dashboard import show_dashboard
        show_dashboard()
