"""Profile page."""
import streamlit as st
from utils.api import api_get, api_put

def show_profile():
    st.markdown("""
    <div class="hero-banner">
      <h1>👤 Profile</h1>
      <p>Manage your account details and view your listing history.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading profile…"):
        me, mc = api_get("/auth/me")
        listings, lc = api_get("/listings/my/all")

    if mc != 200:
        st.error(me.get("error","Failed to load profile"))
        return

    # ── Profile header ────────────────────────────────────────────────────────
    initials = "".join(w[0] for w in me.get("full_name","U U").split()[:2]).upper()
    st.markdown(f"""
    <div class="fs-card">
      <div style="display:flex;align-items:center;gap:16px;">
        <div style="width:72px;height:72px;background:#16a34a;border-radius:50%;display:flex;
                    align-items:center;justify-content:center;color:#fff;font-size:26px;font-weight:800;flex-shrink:0;">
          {initials}
        </div>
        <div>
          <h2 style="font-size:22px;font-weight:800;margin:0;">{me.get('full_name','')}</h2>
          <p style="color:#6b7280;margin:2px 0;text-transform:capitalize;">{me.get('role','donor')}</p>
          <p style="color:#9ca3af;font-size:13px;margin:0;">{me.get('organization','')}</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_stats = st.columns([3, 2])

    with col_form:
        st.markdown("#### ✏️ Edit Profile")
        with st.form("profile_form"):
            full_name    = st.text_input("Full Name",      value=me.get("full_name",""))
            email        = st.text_input("Email",          value=me.get("email",""),  disabled=True)
            phone        = st.text_input("Phone",          value=me.get("phone","")  or "")
            organization = st.text_input("Organization",   value=me.get("organization","") or "")
            address      = st.text_input("Address",        value=me.get("address","") or "")
            bio          = st.text_area( "Bio",            value=me.get("bio","")    or "", height=80)
            save = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")

        if save:
            data, code = api_put("/auth/profile", {
                "full_name": full_name, "phone": phone,
                "organization": organization, "address": address, "bio": bio
            })
            if code == 200:
                # Update session
                user = st.session_state.user or {}
                user.update({"full_name": full_name, "organization": organization})
                st.session_state.user = user
                st.success("Profile updated successfully! ✅")
                st.rerun()
            else:
                st.error(data.get("error", "Update failed"))

    with col_stats:
        # Stats summary
        listing_list = listings if lc == 200 else []
        total     = len(listing_list)
        active    = sum(1 for l in listing_list if l.get("status") == "available")
        completed = sum(1 for l in listing_list if l.get("status") == "completed")
        requests  = sum(l.get("request_count", 0) for l in listing_list)

        st.markdown("#### 📊 My Statistics")
        m1, m2 = st.columns(2)
        m1.metric("Total Listings",    total)
        m2.metric("Active Now",        active)
        m3, m4 = st.columns(2)
        m3.metric("Completed",         completed)
        m4.metric("Total Requests",    requests)

        # Recent listings
        st.markdown("#### 📋 Recent Listings")
        if not listing_list:
            st.info("No listings yet. Create your first one!")
        else:
            for l in listing_list[:6]:
                status = l.get("status","available")
                sc_map = {"available":"#dcfce7","completed":"#dbeafe","expired":"#f3f4f6","cancelled":"#f3f4f6","requested":"#fef3c7"}
                tc_map = {"available":"#15803d","completed":"#1e40af","expired":"#6b7280","cancelled":"#6b7280","requested":"#92400e"}
                bg = sc_map.get(status,"#f3f4f6")
                tc = tc_map.get(status,"#374151")
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:8px 10px;background:#f9fafb;border-radius:8px;margin-bottom:6px;
                            border:1px solid #e5e7eb;">
                  <div>
                    <div style="font-size:13px;font-weight:600;">{l['food_name']}</div>
                    <div style="font-size:11px;color:#9ca3af;">{l['quantity']} · {l['category']}</div>
                  </div>
                  <span style="background:{bg};color:{tc};border-radius:20px;padding:2px 8px;font-size:11px;font-weight:700;">{status.upper()}</span>
                </div>""", unsafe_allow_html=True)

        # Account info
        st.markdown("#### 🔐 Account")
        st.markdown(f"""
        <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:12px;">
          <p style="font-size:13px;color:#374151;margin:3px 0;">📧 {me.get('email','')}</p>
          <p style="font-size:13px;color:#374151;margin:3px 0;">📅 Joined: {str(me.get('created_at',''))[:10]}</p>
          <p style="font-size:13px;color:#374151;margin:3px 0;text-transform:capitalize;">🎭 Role: {me.get('role','donor')}</p>
        </div>""", unsafe_allow_html=True)
