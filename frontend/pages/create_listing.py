"""Create Surplus Food Listing page."""
import streamlit as st
from datetime import date, time
from utils.api import api_post

CATEGORIES = ["Prepared Food","Vegetables","Fruits","Bakery","Dairy","Grains","Beverages","Other"]

def show_create():
    st.markdown("""
    <div class="hero-banner">
      <h1>➕ Create Surplus Food Listing</h1>
      <p>Fill in the details about the surplus food you want to donate to the community.</p>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_tips = st.columns([2, 1])

    with col_form:
        with st.form("create_listing_form", clear_on_submit=True):
            st.markdown("#### 📋 Food Details")
            c1, c2 = st.columns(2)
            with c1:
                food_name = st.text_input("Food Name *", placeholder="e.g., Rice & Curry, Fresh Vegetables")
            with c2:
                category = st.selectbox("Category *", CATEGORIES)

            quantity = st.text_input("Quantity *", placeholder="e.g., 20 meals, 15 kg, 30 loaves")

            st.markdown("#### ⏰ Expiry Information")
            d1, d2 = st.columns(2)
            with d1:
                expiry_date = st.date_input("Expiry Date *", min_value=date.today())
            with d2:
                expiry_time = st.time_input("Expiry Time *", value=time(18, 0))

            st.markdown("#### 📍 Pickup Details")
            pickup_location = st.text_input("Pickup Location *", placeholder="Enter full address")
            c3, c4 = st.columns(2)
            with c3:
                pickup_lat = st.number_input("Latitude (optional)",  value=0.0, format="%.6f")
            with c4:
                pickup_lng = st.number_input("Longitude (optional)", value=0.0, format="%.6f")

            additional_details = st.text_area(
                "Additional Details (Optional)",
                placeholder="Dietary info, handling instructions, allergens…",
                height=90
            )

            submitted = st.form_submit_button("🌿 Create Listing", use_container_width=True, type="primary")

        if submitted:
            if not food_name or not quantity or not pickup_location:
                st.error("Please fill all required fields (marked with *).")
            else:
                payload = {
                    "food_name":        food_name,
                    "category":         category,
                    "quantity":         quantity,
                    "expiry_date":      str(expiry_date),
                    "expiry_time":      str(expiry_time),
                    "pickup_location":  pickup_location,
                    "pickup_lat":       pickup_lat if pickup_lat != 0.0 else None,
                    "pickup_lng":       pickup_lng if pickup_lng != 0.0 else None,
                    "additional_details": additional_details or None
                }
                with st.spinner("Creating listing…"):
                    data, code = api_post("/listings", payload)
                if code == 201:
                    st.success(f"✅ Listing created successfully! ID: {data.get('id')}")
                    st.balloons()
                    st.markdown("""
                    <div class="ai-box">
                    <p>🤖 AI agents are now monitoring your listing — they will alert you before expiry and match it with nearby recipients automatically.</p>
                    </div>""", unsafe_allow_html=True)
                    if st.button("➡ View Browse Listings"):
                        st.session_state.page = "browse"
                        st.rerun()
                else:
                    st.error(data.get("error", "Failed to create listing"))

    with col_tips:
        st.markdown("#### 💡 Listing Tips")
        tips = [
            ("🕐", "List food at least 4 hours before expiry for maximum recipient reach."),
            ("📦", "Be specific about quantity — '20 meals' is better than 'some food'."),
            ("🌿", "Add dietary info (vegan, halal, gluten-free) to help recipients."),
            ("📍", "Accurate pickup location speeds up the matching process."),
            ("🔥", "Urgent listings get 3× more visibility in the platform."),
        ]
        for icon, tip in tips:
            st.markdown(f"""
            <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:10px 12px;margin-bottom:8px;">
            <span style="font-size:16px;">{icon}</span> <span style="font-size:13px;color:#4b5563;">{tip}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🤖 AI Agent Features")
        st.markdown("""
        <div class="ai-box">
        <p>Your listing will be powered by HuggingFace AI agents that:<br><br>
        • <strong>Match</strong> recipients based on compatibility<br>
        • <strong>Monitor</strong> expiry and send alerts<br>
        • <strong>Recommend</strong> optimal pickup windows<br>
        • <strong>Analyze</strong> your donation impact
        </p>
        </div>""", unsafe_allow_html=True)
