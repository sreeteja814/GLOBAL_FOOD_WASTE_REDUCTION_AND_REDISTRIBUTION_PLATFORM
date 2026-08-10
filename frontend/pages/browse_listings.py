"""Browse Surplus Listings page."""
import streamlit as st
from utils.api import api_get, api_post
from utils.hf_ai import hf_match_recommendation

CATEGORIES = ["All", "Prepared Food", "Vegetables", "Fruits", "Bakery", "Dairy", "Grains", "Beverages", "Other"]

def fmt_time(minutes_left):
    if minutes_left is None: return "Unknown"
    if minutes_left <= 0:    return "⛔ Expired"
    if minutes_left < 60:    return f"⚠️ {minutes_left} min"
    h = minutes_left // 60
    m = minutes_left % 60
    return f"{'🔴 ' if h < 2 else ''}{h}h {m}m" if m else f"{'🔴 ' if h < 2 else ''}{h}h"

def show_browse():
    st.markdown("""
    <div class="hero-banner">
      <h1>🔍 Browse Surplus Listings</h1>
      <p>Find available surplus food in your area and help reduce global food waste.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ──────────────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([3, 1, 1])
    with fc1:
        search = st.text_input("🔍 Search food items…", placeholder="e.g. Rice, Vegetables")
    with fc2:
        category = st.selectbox("Category", CATEGORIES)
    with fc3:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh = st.button("🔄 Refresh", use_container_width=True)

    # ── Fetch listings ────────────────────────────────────────────────────────
    params = {}
    if search:                              params["search"]   = search
    if category and category != "All":      params["category"] = category

    with st.spinner("Finding listings…"):
        listings, code = api_get("/listings", params=params)

    if code != 200:
        st.error(listings.get("error", "Failed to load listings"))
        return

    st.markdown(f"**{len(listings)} listing{'s' if len(listings)!=1 else ''} found**")

    if not listings:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#9ca3af;">
          <div style="font-size:48px;">🍽️</div>
          <h3 style="color:#6b7280;">No listings available</h3>
          <p>Check back soon or adjust your filters.</p>
        </div>""", unsafe_allow_html=True)
        return

    # ── Listing grid (3 per row) ──────────────────────────────────────────────
    for i in range(0, len(listings), 3):
        row = listings[i:i+3]
        cols = st.columns(3)
        for j, listing in enumerate(row):
            with cols[j]:
                urgent_tag  = '<span class="tag tag-urgent">🔥 Urgent</span>'   if listing.get("is_urgent") else '<span class="tag tag-available">✓ Available</span>'
                cat_tag     = f'<span class="tag tag-category">{listing["category"]}</span>'
                mins_left   = listing.get("minutes_left")
                time_str    = fmt_time(mins_left)
                time_color  = "color:#ef4444;font-weight:700;" if (mins_left is not None and mins_left < 120) else ""

                st.markdown(f"""
                <div class="fs-card">
                  <div style="margin-bottom:8px;">{urgent_tag}{cat_tag}</div>
                  <h3>{listing['food_name']}</h3>
                  <p>📦 <strong>{listing['quantity']}</strong></p>
                  <p>📍 {listing['pickup_location']}</p>
                  <p>⏰ <span style="{time_color}">{time_str}</span></p>
                  <p style="color:#9ca3af;font-size:12px;">Donor: {listing.get('donor_org') or listing.get('donor_name','')}</p>
                </div>
                """, unsafe_allow_html=True)

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("👁 View", key=f"view_{listing['id']}_{i}_{j}", use_container_width=True):
                        st.session_state[f"view_listing"] = listing
                        st.session_state[f"show_detail"] = True
                with b2:
                    if st.button("📦 Request", key=f"req_{listing['id']}_{i}_{j}", use_container_width=True, type="primary"):
                        st.session_state["request_listing"] = listing
                        st.session_state["show_request_modal"] = True

    # ── Detail drawer ────────────────────────────────────────────────────────
    if st.session_state.get("show_detail") and st.session_state.get("view_listing"):
        l = st.session_state["view_listing"]
        with st.expander(f"📋 Details: {l['food_name']}", expanded=True):
            d1, d2 = st.columns(2)
            with d1:
                st.markdown(f"**Category:** {l['category']}")
                st.markdown(f"**Quantity:** {l['quantity']}")
                st.markdown(f"**Pickup:** {l['pickup_location']}")
                st.markdown(f"**Expires in:** {fmt_time(l.get('minutes_left'))}")
            with d2:
                st.markdown(f"**Donor:** {l.get('donor_org') or l.get('donor_name','')}")
                if l.get("additional_details"):
                    st.markdown(f"**Notes:** {l['additional_details']}")

            # AI match insight
            user = st.session_state.user or {}
            if st.button("🤖 Get AI Match Insight", key="ai_insight_btn"):
                with st.spinner("Analysing compatibility with HuggingFace AI…"):
                    insight = hf_match_recommendation(
                        {"food": l["food_name"], "category": l["category"], "qty": l["quantity"], "urgent": l.get("is_urgent")},
                        {"org": user.get("organization"), "role": user.get("role"), "address": user.get("address")}
                    )
                st.markdown(f'<div class="ai-box"><p>🤖 <strong>AI Match Insight:</strong> {insight}</p></div>', unsafe_allow_html=True)

            if st.button("Close", key="close_detail"):
                st.session_state["show_detail"] = False
                st.rerun()

    # ── Request modal ─────────────────────────────────────────────────────────
    if st.session_state.get("show_request_modal") and st.session_state.get("request_listing"):
        l = st.session_state["request_listing"]
        with st.expander(f"📦 Request: {l['food_name']}", expanded=True):
            st.markdown(f"**Pickup:** {l['pickup_location']}  |  **Quantity:** {l['quantity']}")
            notes = st.text_area("Notes (optional)", placeholder="Specific requirements or pickup details…")
            st.markdown("""
            <div class="ai-box">
              <p>🤖 Our AI will calculate a match score using HuggingFace when you submit the request.</p>
            </div>""", unsafe_allow_html=True)
            rb1, rb2 = st.columns(2)
            with rb1:
                if st.button("Cancel", key="cancel_req", use_container_width=True):
                    st.session_state["show_request_modal"] = False
                    st.rerun()
            with rb2:
                if st.button("✅ Submit Request", key="submit_req", use_container_width=True, type="primary"):
                    with st.spinner("Submitting + running AI match…"):
                        data, code = api_post("/requests", {"listing_id": l["id"], "notes": notes})
                    if code == 201:
                        score = data.get("ai_match", {}).get("score", "N/A")
                        st.success(f"Request submitted! 🤖 AI Match Score: {score}%")
                        st.session_state["show_request_modal"] = False
                        st.rerun()
                    else:
                        st.error(data.get("error", "Request failed"))
