"""Pickup Tracking page."""
import streamlit as st
from utils.api import api_get

def progress_bar(status):
    steps = ["Submitted", "Approved", "En Route", "Completed"]
    done_map = {
        "pending":   0,
        "approved":  2,
        "completed": 4,
    }
    done = done_map.get(status, 0)
    html = '<div style="display:flex;align-items:center;gap:0;margin-top:10px;">'
    for i, step in enumerate(steps):
        is_done   = i < done
        is_active = i == done - 1 if done > 0 else i == 0
        bg    = "#16a34a" if is_done else ("#dcfce7" if is_active else "#f3f4f6")
        tc    = "#fff"    if is_done else ("#15803d" if is_active else "#9ca3af")
        bord  = "2px solid #16a34a" if is_active and not is_done else "none"
        icon  = "✓" if is_done else ("●" if is_active else "○")
        html += f"""
        <div style="flex:1;text-align:center;">
          <div style="width:32px;height:32px;border-radius:50%;background:{bg};border:{bord};
                      display:inline-flex;align-items:center;justify-content:center;
                      color:{tc};font-weight:700;font-size:13px;">{icon}</div>
          <div style="font-size:11px;color:{'#15803d' if is_done else '#9ca3af'};margin-top:4px;font-weight:{'600' if is_done else '400'};">{step}</div>
        </div>"""
        if i < len(steps)-1:
            line_color = "#16a34a" if i < done - 1 else "#e5e7eb"
            html += f'<div style="flex:0 0 20px;height:2px;background:{line_color};margin-bottom:18px;"></div>'
    html += "</div>"
    return html

def show_pickup():
    st.markdown("""
    <div class="hero-banner">
      <h1>📍 Pickup Tracking</h1>
      <p>Track the real-time status of all your food pickup operations.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading pickup data…"):
        pickups, code = api_get("/dashboard/pickup-tracking")

    if code != 200:
        st.error(pickups.get("error", "Failed to load pickup tracking data"))
        return

    if not pickups:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#9ca3af;">
          <div style="font-size:48px;">🚗</div>
          <h3 style="color:#6b7280;">No active pickups</h3>
          <p>Approved requests will appear here for tracking.</p>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown(f"**{len(pickups)} pickup{'s' if len(pickups)!=1 else ''} found**")

    for p in pickups:
        status = p.get("status","pending")
        status_colors = {"approved":"#16a34a","completed":"#2563eb","pending":"#92400e"}
        sc = status_colors.get(status, "#6b7280")

        st.markdown(f"""
        <div class="fs-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
            <div>
              <h3 style="margin:0;">{p['food_name']}</h3>
              <span style="font-size:13px;color:#6b7280;">{p['category']} · {p['quantity']}</span>
            </div>
            <span style="background:{sc}20;color:{sc};border-radius:20px;padding:4px 12px;font-size:12px;font-weight:700;text-transform:uppercase;">{status}</span>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:14px;">
            <div>
              <span style="font-size:11px;color:#9ca3af;font-weight:600;">PICKUP LOCATION</span><br>
              <span style="font-size:13px;">📍 {p['pickup_location']}</span>
            </div>
            <div>
              <span style="font-size:11px;color:#9ca3af;font-weight:600;">DONOR</span><br>
              <span style="font-size:13px;">🏢 {p.get('donor_org','')}</span><br>
              {f'<span style="font-size:12px;color:#6b7280;">📞 {p["donor_phone"]}</span>' if p.get('donor_phone') else ''}
            </div>
            <div>
              <span style="font-size:11px;color:#9ca3af;font-weight:600;">RECIPIENT</span><br>
              <span style="font-size:13px;">👤 {p.get('recipient_name','')}</span><br>
              {f'<span style="font-size:12px;color:#6b7280;">📞 {p["recipient_phone"]}</span>' if p.get('recipient_phone') else ''}
            </div>
          </div>
          {progress_bar(status)}
          {f'<div style="margin-top:12px;padding:8px 12px;background:#dcfce7;border-radius:8px;font-size:13px;color:#15803d;">🎉 Completed: {str(p.get("pickup_completed_at",""))[:16]}</div>' if status == "completed" else ""}
        </div>
        """, unsafe_allow_html=True)
