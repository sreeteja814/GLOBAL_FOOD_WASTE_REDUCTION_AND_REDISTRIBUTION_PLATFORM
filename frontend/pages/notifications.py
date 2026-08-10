"""Notifications page."""
import streamlit as st
from utils.api import api_get, api_put

ICONS = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "urgent": "🔥"}
COLORS = {"info": "#3b82f6", "success": "#16a34a",
          "warning": "#f59e0b", "urgent": "#ef4444"}


def show_notifications():
    st.markdown("""
    <div class="hero-banner">
      <h1>🔔 Notifications</h1>
      <p>Stay updated on your food listings, requests, and AI agent alerts.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading notifications…"):
        notifs, code = api_get("/dashboard/notifications")

    if code != 200:
        st.error(notifs.get("error", "Failed to load notifications"))
        return

    unread = [n for n in notifs if not n.get("is_read")]
    read = [n for n in notifs if n.get("is_read")]

    # Top bar
    top1, top2 = st.columns([4, 1])
    with top1:
        st.markdown(
            f"**{len(unread)} unread notification{'s' if len(unread) != 1 else ''}**")
    with top2:
        if unread and st.button("✓ Mark all read", use_container_width=True):
            api_put("/dashboard/notifications/read-all")
            st.rerun()

    if not notifs:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#9ca3af;">
          <div style="font-size:48px;">🔔</div>
          <h3 style="color:#6b7280;">No notifications</h3>
          <p>You're all caught up!</p>
        </div>""", unsafe_allow_html=True)
        return

    tab1, tab2 = st.tabs(
        [f"🔴 Unread ({len(unread)})", f"✓ All ({len(notifs)})"])

    def render_notif(n, tab_prefix):
        ntype = n.get("type", "info")
        icon = ICONS.get(ntype, "ℹ️")
        color = COLORS.get(ntype, "#3b82f6")
        opacity = "1" if not n.get("is_read") else "0.65"
        ts = str(n.get("created_at", ""))[:16]

        st.markdown(f"""
        <div class="notif-row {ntype}" style="opacity:{opacity};border-left-color:{color};">
          <div style="display:flex;align-items:flex-start;gap:12px;">
            <span style="font-size:20px;flex-shrink:0;">{icon}</span>
            <div style="flex:1;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
                <strong>{n['title']}</strong>
                <div style="display:flex;align-items:center;gap:8px;">
                  <span style="font-size:12px;color:#9ca3af;">{ts}</span>
                  {'<span style="width:8px;height:8px;background:#16a34a;border-radius:50%;display:inline-block;"></span>' if not n.get("is_read") else ""}
                </div>
              </div>
              <span style="font-size:13px;color:#6b7280;">{n['message']}</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if not n.get("is_read"):
            if st.button("Mark as read", key=f"{tab_prefix}_read_{n['id']}", use_container_width=False):
                api_put(f"/dashboard/notifications/{n['id']}/read")
                st.rerun()

    with tab1:
        if not unread:
            st.success("🎉 All caught up! No unread notifications.")
        for n in unread:
            render_notif(n, "tab1")

    with tab2:
        for n in notifs:
            render_notif(n, "tab2")
