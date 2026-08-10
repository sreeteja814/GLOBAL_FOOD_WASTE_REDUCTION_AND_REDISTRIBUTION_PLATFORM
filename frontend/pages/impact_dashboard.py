"""Impact Dashboard page with HuggingFace AI insights."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.api import api_get
from utils.hf_ai import hf_impact_summary

def show_impact():
    st.markdown("""
    <div class="hero-banner">
      <h1>📈 Impact Dashboard</h1>
      <p>Your personal contribution to the Global Food Waste Reduction and Redistribution Platform.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Analyzing your impact with HuggingFace AI…"):
        impact, code = api_get("/dashboard/impact")

    if code != 200:
        st.error(impact.get("error","Failed to load impact data"))
        return

    stats   = impact.get("stats",   {})
    monthly = impact.get("monthly", [])

    # ── AI Insight Banner ─────────────────────────────────────────────────────
    summary = impact.get("summary","You are making a meaningful difference reducing global food waste.")
    trend   = impact.get("trend","stable")
    badge   = impact.get("badge","Food Hero")
    tip     = impact.get("tip","Keep listing food regularly to maximize your impact.")
    trend_icon = "📈" if trend == "up" else "📉" if trend == "down" else "➡️"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#15803d,#22c55e);border-radius:14px;padding:24px;color:#fff;margin-bottom:20px;">
      <h2 style="font-size:20px;font-weight:800;margin:0 0 6px 0;">🌍 Your Global Impact</h2>
      <p style="font-size:14px;opacity:.9;margin:0 0 18px 0;">{summary}</p>
      <div style="display:flex;gap:28px;flex-wrap:wrap;">
        <div style="text-align:center;">
          <div style="font-size:28px;font-weight:800;">{stats.get('total',0)}</div>
          <div style="font-size:12px;opacity:.8;">Total Listings</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:28px;font-weight:800;">{stats.get('completed',0)}</div>
          <div style="font-size:12px;opacity:.8;">Completed</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:28px;font-weight:800;">{stats.get('total_requests',stats.get('urgent',0))}</div>
          <div style="font-size:12px;opacity:.8;">Requests Received</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Insight Cards ─────────────────────────────────────────────────────────
    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        st.markdown(f"""
        <div class="fs-card" style="text-align:center;">
          <div style="font-size:32px;">{trend_icon}</div>
          <div style="font-weight:700;margin:6px 0 2px 0;">Trend</div>
          <div style="font-size:14px;color:#6b7280;text-transform:capitalize;">{trend}</div>
        </div>""", unsafe_allow_html=True)
    with ic2:
        st.markdown(f"""
        <div class="fs-card" style="text-align:center;">
          <div style="font-size:32px;">🏅</div>
          <div style="font-weight:700;margin:6px 0 2px 0;">Badge Earned</div>
          <div style="font-size:14px;color:#16a34a;font-weight:600;">{badge}</div>
        </div>""", unsafe_allow_html=True)
    with ic3:
        st.markdown(f"""
        <div class="fs-card">
          <div style="font-size:20px;">💡</div>
          <div style="font-weight:700;margin:6px 0 2px 0;">AI Tip</div>
          <div style="font-size:13px;color:#6b7280;">{tip}</div>
        </div>""", unsafe_allow_html=True)

    # ── Monthly Charts ────────────────────────────────────────────────────────
    if monthly:
        df = pd.DataFrame([{
            "month":  pd.to_datetime(m["metric_date"]).strftime("%b"),
            "meals":  m["meals_donated"],
            "kg":     float(m["weight_kg"]),
            "co2":    float(m["co2_saved_kg"])
        } for m in reversed(monthly)])

        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown("#### 🍽️ Monthly Meals Donated")
            fig = go.Figure(go.Scatter(
                x=df["month"], y=df["meals"], mode="lines+markers",
                fill="tozeroy", fillcolor="rgba(34,197,94,0.15)",
                line=dict(color="#16a34a",width=2.5), marker=dict(size=7,color="#16a34a"), name="Meals"
            ))
            fig.update_layout(height=220, margin=dict(l=0,r=0,t=10,b=0),
                              plot_bgcolor="white", paper_bgcolor="white",
                              xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with ch2:
            st.markdown("#### ♻️ Monthly CO₂ Saved (kg)")
            fig2 = go.Figure(go.Scatter(
                x=df["month"], y=df["co2"], mode="lines+markers",
                fill="tozeroy", fillcolor="rgba(59,130,246,0.15)",
                line=dict(color="#3b82f6",width=2.5), marker=dict(size=7,color="#3b82f6"), name="CO₂"
            ))
            fig2.update_layout(height=220, margin=dict(l=0,r=0,t=10,b=0),
                               plot_bgcolor="white", paper_bgcolor="white",
                               xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    # ── HuggingFace AI Extended Summary ──────────────────────────────────────
    st.markdown("#### 🤖 HuggingFace AI Deep Insight")
    if st.button("Generate Extended AI Analysis", type="primary"):
        with st.spinner("Running HuggingFace AI analysis…"):
            ai_text = hf_impact_summary({
                "total_listings": stats.get("total", 0),
                "completed": stats.get("completed", 0),
                "trend": trend,
                "badge": badge,
                "monthly_meals": [m.get("meals_donated", 0) for m in monthly]
            })
        st.markdown(f'<div class="ai-box"><p>🤖 <strong>HuggingFace AI Analysis:</strong><br>{ai_text}</p></div>',
                    unsafe_allow_html=True)

    # ── UN SDGs ───────────────────────────────────────────────────────────────
    st.markdown("#### 🌐 UN Sustainable Development Goals Supported")
    sdgs = [
        ("#DDA63A","🍚","SDG 2","Zero Hunger"),
        ("#BF8B2E","♻️","SDG 12","Responsible Consumption"),
        ("#3F7E44","🌍","SDG 13","Climate Action"),
        ("#19486A","🤝","SDG 17","Partnerships"),
    ]
    sc = st.columns(4)
    for i,(col,em,goal,label) in enumerate(sdgs):
        with sc[i]:
            st.markdown(f"""
            <div class="fs-card" style="text-align:center;">
              <div style="font-size:28px;">{em}</div>
              <div style="font-size:12px;font-weight:700;color:{col};margin-top:4px;">{goal}</div>
              <div style="font-size:13px;font-weight:600;color:#374151;">{label}</div>
            </div>""", unsafe_allow_html=True)
