"""Dashboard page with stats, charts and AI recommendations."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.api import api_get

# ── Default fallback data (used only if API returns nothing) ──────────────────
DEFAULT_STATS = {
    "total_listings": 0,
    "active_requests": 0,
    "pending_approval": 0,
    "meals_donated": 0,
    "waste_reduced_kg": 0,
    "co2_saved": 0,
    "monthly_trend": [
        {"month": "Jan", "meals": 0},
        {"month": "Feb", "meals": 0},
        {"month": "Mar", "meals": 0},
        {"month": "Apr", "meals": 0},
        {"month": "May", "meals": 0},
        {"month": "Jun", "meals": 0},
    ],
    "category_distribution": []
}


def safe_int(val, default=0):
    try:
        return int(val) if val is not None else default
    except (ValueError, TypeError):
        return default


def safe_float(val, default=0.0):
    try:
        return float(val) if val is not None else default
    except (ValueError, TypeError):
        return default


def show_dashboard():
    user = st.session_state.user or {}

    st.markdown(f"""
    <div class="hero-banner">
      <h1>🌍 Dashboard</h1>
      <p>Welcome back, <strong>{user.get('full_name', user.get('username', 'User'))}</strong>!
      Here's your impact overview for the Global Food Waste Reduction Platform.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch data ────────────────────────────────────────────────────────────
    with st.spinner("Loading dashboard…"):
        stats, s_code = api_get("/dashboard/stats")
        recs,  r_code = api_get("/dashboard/recommendations")

    # ── Merge API data with defaults safely ───────────────────────────────────
    if s_code != 200 or not isinstance(stats, dict):
        if s_code == 503:
            st.warning(
                "⚠️ Cannot connect to backend server. Showing empty data.")
        elif s_code != 200:
            st.warning(
                f"⚠️ Could not load stats (code {s_code}). Showing empty data.")
        stats = {}

    # Pull values safely — use whatever key the API returns
    total_listings = safe_int(
        stats.get("total_listings",  stats.get("listings_count",  0)))
    active_requests = safe_int(
        stats.get("active_requests", stats.get("requests_count",  0)))
    pending = safe_int(stats.get("pending_approval",
                       stats.get("pending",         0)))
    meals_donated = safe_int(
        stats.get("meals_donated",   stats.get("meals",           0)))
    waste_kg = safe_float(stats.get("waste_reduced_kg", stats.get(
        "waste_reduced", stats.get("waste_kg", 0))))
    co2_saved = safe_float(
        stats.get("co2_saved",     stats.get("co2",             waste_kg * 2)))

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Total Listings",  total_listings,  "+12% from last month")
    c2.metric("✅ Active Requests", active_requests,
              f"{pending} pending approval")
    c3.metric("🍽️ Meals Donated",
              f"{meals_donated:,}", "+18% from last month")
    c4.metric("♻️ Waste Reduced",
              f"{waste_kg:.0f} kg", f"≈{co2_saved:.0f} kg CO₂ saved")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📈 Monthly Impact Trends")

        monthly_raw = stats.get("monthly_trend", stats.get("monthly", []))

        # Normalise: accept {month, meals} or {month, count} or {name, value}
        monthly = []
        for item in monthly_raw:
            if isinstance(item, dict):
                month = item.get("month") or item.get(
                    "name") or item.get("label", "")
                meals = safe_int(item.get("meals") or item.get(
                    "count") or item.get("value", 0))
                monthly.append({"month": str(month), "meals": meals})

        if not monthly:
            monthly = DEFAULT_STATS["monthly_trend"]

        df_m = pd.DataFrame(monthly)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_m["month"], y=df_m["meals"],
            mode="lines+markers",
            fill="tozeroy",
            fillcolor="rgba(34,197,94,0.15)",
            line=dict(color="#16a34a", width=2.5),
            marker=dict(color="#16a34a", size=7),
            name="Meals Donated"
        ))
        fig.update_layout(
            height=260,
            margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(showgrid=False, tickfont=dict(size=12)),
            yaxis=dict(gridcolor="#f0f0f0", tickfont=dict(size=12)),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### 🗂️ Food Category Distribution")

        cats_raw = stats.get("category_distribution",
                             stats.get("categories", []))

        # Normalise: accept {category, count} or {name, value} or {label, count}
        cats = []
        for item in cats_raw:
            if isinstance(item, dict):
                cat = item.get("category") or item.get(
                    "name") or item.get("label", "Other")
                count = safe_int(item.get("count") or item.get(
                    "value") or item.get("total", 0))
                cats.append({"category": str(cat), "count": count})

        if not cats:
            st.info("No category data available yet.")
        else:
            df_c = pd.DataFrame(cats)
            df_c = df_c.sort_values("count", ascending=True)
            fig2 = px.bar(
                df_c, x="count", y="category",
                orientation="h",
                color_discrete_sequence=["#16a34a"]
            )
            fig2.update_layout(
                height=260,
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(gridcolor="#f0f0f0", tickfont=dict(
                    size=12), title="count"),
                yaxis=dict(showgrid=False, tickfont=dict(size=11), title=""),
                showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ── AI Recommendations ────────────────────────────────────────────────────
    st.markdown("#### 🤖 AI-Powered Recommendations")

    priority_color = {"high": "#ef4444", "medium": "#f97316", "low": "#16a34a"}
    action_page = {
        "browse":  "browse",
        "create":  "create_listing",
        "profile": "profile",
        "impact":  "impact",
        "requests": "requests",
    }

    rec_list = []
    if r_code == 200 and isinstance(recs, dict):
        rec_list = recs.get("recommendations", recs.get("data", []))
    elif r_code == 200 and isinstance(recs, list):
        rec_list = recs

    if rec_list:
        cols = st.columns(min(len(rec_list), 3))
        for i, rec in enumerate(rec_list[:3]):
            with cols[i]:
                pcolor = priority_color.get(
                    rec.get("priority", "low"), "#16a34a")
                st.markdown(f"""
                <div class="fs-card" style="min-height:140px;">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
                    <strong style="font-size:14px;color:#111827;">{rec.get('title', 'Recommendation')}</strong>
                    <span style="font-size:10px;font-weight:700;color:{pcolor};text-transform:uppercase;">{rec.get('priority', '')}</span>
                  </div>
                  <p style="font-size:13px;color:#6b7280;margin-bottom:0;">{rec.get('description', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                target = action_page.get(rec.get("action", "browse"), "browse")
                if st.button("Take Action →", key=f"rec_{i}", use_container_width=True):
                    st.session_state.page = target
                    st.rerun()
    else:
        # Friendly default cards when API has no recommendations
        defaults = [
            {"title": "Add a Food Listing", "desc": "You can donate surplus food by creating a new listing.",
                "page": "create_listing", "icon": "➕"},
            {"title": "Browse Available Food",
                "desc": "Check what food is available for pickup near you.", "page": "browse", "icon": "🔍"},
            {"title": "View Your Impact", "desc": "See how much food waste you have helped reduce.",
                "page": "impact", "icon": "📈"},
        ]
        dcols = st.columns(3)
        for i, d in enumerate(defaults):
            with dcols[i]:
                st.markdown(f"""
                <div class="fs-card" style="min-height:140px;">
                  <div style="font-size:28px;margin-bottom:8px;">{d['icon']}</div>
                  <strong style="font-size:14px;color:#111827;">{d['title']}</strong>
                  <p style="font-size:13px;color:#6b7280;margin-top:6px;">{d['desc']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Go →", key=f"def_rec_{i}", use_container_width=True):
                    st.session_state.page = d["page"]
                    st.rerun()

    # ── Quick Actions ─────────────────────────────────────────────────────────
    st.markdown("#### ⚡ Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)
    if qa1.button("➕ Create Listing",  use_container_width=True, type="primary"):
        st.session_state.page = "create_listing"
        st.rerun()
    if qa2.button("🔍 Browse Food",     use_container_width=True):
        st.session_state.page = "browse"
        st.rerun()
    if qa3.button("📦 View Requests",   use_container_width=True):
        st.session_state.page = "requests"
        st.rerun()
    if qa4.button("📈 My Impact",       use_container_width=True):
        st.session_state.page = "impact"
        st.rerun()
