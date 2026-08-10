"""Manage Requests page."""
import streamlit as st
from utils.api import api_get, api_put

STATUS_COLOR = {
    "pending":   "#fef3c7",
    "approved":  "#dcfce7",
    "completed": "#dbeafe",
    "rejected":  "#fee2e2",
    "cancelled": "#f3f4f6",
}
STATUS_TEXT = {
    "pending":   "#92400e",
    "approved":  "#15803d",
    "completed": "#1e40af",
    "rejected":  "#991b1b",
    "cancelled": "#6b7280",
}


def status_badge(status):
    bg = STATUS_COLOR.get(status, "#f3f4f6")
    tc = STATUS_TEXT.get(status, "#374151")
    return f'<span class="tag" style="background:{bg};color:{tc};">{status.upper()}</span>'


def show_requests():
    user = st.session_state.user or {}

    st.markdown("""
    <div class="hero-banner">
      <h1>📦 Manage Requests</h1>
      <p>Review, approve, and track all food pickup requests.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading requests…"):
        requests, code = api_get("/requests")

    if code != 200:
        st.error(requests.get("error", "Failed to load requests"))
        return

    if not requests:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#9ca3af;">
          <div style="font-size:48px;">📭</div>
          <h3 style="color:#6b7280;">No requests yet</h3>
          <p>Requests will appear here when recipients request your listings.</p>
        </div>""", unsafe_allow_html=True)
        return

    # ── Tabs: Pending | All ───────────────────────────────────────────────────
    pending = [r for r in requests if r["status"] == "pending"]
    others = [r for r in requests if r["status"] != "pending"]

    tab1, tab2 = st.tabs(
        [f"⏳ Pending ({len(pending)})", f"📋 All Requests ({len(requests)})"])

    def render_request(r, show_actions=True):
        is_donor = user.get("role") == "donor"
        other_party = r.get("recipient_org") or r.get(
            "recipient_name", "") if is_donor else r.get("donor_org", "")
        score = r.get("ai_match_score")
        try:
            score = int(score) if score is not None else None
        except (ValueError, TypeError):
            score = None
        score_color = "#16a34a" if (score and score >= 80) else "#f97316" if (
            score and score >= 60) else "#ef4444"

        st.markdown(f"""
        <div class="fs-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
            <div>
              <strong style="font-size:16px;color:#111827;">{r['food_name']}</strong>
              <span class="tag tag-category" style="margin-left:8px;">{r['category']}</span>
            </div>
            {status_badge(r['status'])}
          </div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:10px;">
            <div><span style="font-size:11px;color:#9ca3af;font-weight:600;">{'RECIPIENT' if is_donor else 'DONOR'}</span><br>
                 <span style="font-size:13px;color:#374151;">{other_party}</span></div>
            <div><span style="font-size:11px;color:#9ca3af;font-weight:600;">QUANTITY</span><br>
                 <span style="font-size:13px;color:#374151;">{r['quantity']}</span></div>
            <div><span style="font-size:11px;color:#9ca3af;font-weight:600;">AI MATCH</span><br>
                 <span style="font-size:14px;font-weight:700;color:{score_color};">{f"{score}%" if score else "—"}</span></div>
            <div><span style="font-size:11px;color:#9ca3af;font-weight:600;">DATE</span><br>
                 <span style="font-size:13px;color:#374151;">{str(r['created_at'])[:10]}</span></div>
          </div>
          {f'<p style="font-size:12px;color:#9ca3af;margin-top:6px;">📍 {r["pickup_location"]}</p>' if r.get("pickup_location") else ""}
        </div>
        """, unsafe_allow_html=True)

        if show_actions and is_donor and r["status"] == "pending":
            a1, a2, a3 = st.columns([1, 1, 3])
            with a1:
                if st.button("✓ Approve", key=f"appr_{r['id']}", type="primary", use_container_width=True):
                    data, c = api_put(
                        f"/requests/{r['id']}/status", {"status": "approved"})
                    st.success("Request approved!") if c == 200 else st.error(
                        data.get("error"))
                    st.rerun()
            with a2:
                if st.button("✕ Reject", key=f"rej_{r['id']}", use_container_width=True):
                    data, c = api_put(
                        f"/requests/{r['id']}/status", {"status": "rejected"})
                    st.success("Request rejected.") if c == 200 else st.error(
                        data.get("error"))
                    st.rerun()

        if show_actions and is_donor and r["status"] == "approved":
            if st.button("🎉 Mark as Completed", key=f"comp_{r['id']}", use_container_width=True):
                data, c = api_put(
                    f"/requests/{r['id']}/status", {"status": "completed"})
                st.success("Marked as completed!") if c == 200 else st.error(
                    data.get("error"))
                st.rerun()

    with tab1:
        if not pending:
            st.info("No pending requests at the moment.")
        for r in pending:
            render_request(r, show_actions=True)

    with tab2:
        if not requests:
            st.info("No requests found.")
        for r in requests:
            render_request(r, show_actions=True)
