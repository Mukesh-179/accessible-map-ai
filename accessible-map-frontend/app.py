import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import folium
from streamlit_folium import st_folium
import time

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="🧭 Accessible Map AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# STYLING & THEME
# ============================================

st.markdown("""
    <style>
    .main {
        padding-top: 0rem;
    }
    
    .st-emotion-cache-1f7y0th {
        padding: 2rem 1rem 10rem 1rem;
    }
    
    h1, h2, h3 {
        color: #1f77b4;
        font-weight: 700;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .status-online {
        color: #00d084;
        font-weight: bold;
    }
    
    .status-offline {
        color: #ff4444;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# API CONFIGURATION
# ============================================

API_URL = "http://localhost:8000"

def api_call(method, endpoint, data=None, headers=None):
    """Make API calls to backend"""
    try:
        url = f"{API_URL}{endpoint}"
        if headers is None:
            headers = {}
        
        if "Authorization" not in headers and "token" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.token}"
        
        response = None
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(url, json=data, headers=headers, timeout=10)
        else:
            st.error(f"❌ Unsupported HTTP method: {method}")
        
        return response
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.accessibility_mode = "none"
    st.session_state.user_id = None

# ============================================
# SESSION MANAGEMENT
# ============================================

def start_app(accessibility_mode):
    """Start the application"""
    st.session_state.started = True
    st.session_state.accessibility_mode = accessibility_mode
    st.session_state.user_id = "guest_" + str(int(datetime.now().timestamp()))

# ============================================
# START PAGE
# ============================================

def show_start_page():
    """Display start/welcome page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>🧭 Accessible Map AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px; color: #666;'>Smart Inclusive Mobility Platform</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Welcome to Accessible Map AI")
        st.markdown("Navigate the world with confidence and accessibility in mind.")
        st.markdown("")
        
        st.markdown("#### 🎯 Choose Your Accessibility Mode:")
        accessibility_mode = st.selectbox(
            "Select how you navigate:",
            ["none", "wheelchair", "visually-impaired", "elderly"],
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("🚀 Start Using App", use_container_width=True, key="start_btn"):
                start_app(accessibility_mode)
                st.rerun()
        
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #999; font-size: 12px;'>Powered by Advanced AI & Computer Vision</p>", unsafe_allow_html=True)

# ============================================
# MAIN APP PAGES
# ============================================

def show_dashboard():
    """Main dashboard"""
    st.title("🏠 Dashboard")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### 👋 Welcome!")
    with col3:
        if st.button("🔄 Restart"):
            st.session_state.started = False
            st.rerun()
    
    st.markdown("---")
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>🗺️ Routes</h3>
            <p style='font-size: 24px; margin: 0;'>0</p>
            <p style='font-size: 12px; margin: 0;'>This Month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>📍 Saved Places</h3>
            <p style='font-size: 24px; margin: 0;'>0</p>
            <p style='font-size: 12px; margin: 0;'>Locations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h3>⭐ Safety Score</h3>
            <p style='font-size: 24px; margin: 0;'>100%</p>
            <p style='font-size: 12px; margin: 0;'>Excellent</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <h3>🤝 Volunteers</h3>
            <p style='font-size: 24px; margin: 0;'>0</p>
            <p style='font-size: 12px; margin: 0;'>Available</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Feature grid
    st.subheader("🌟 Quick Access")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧭 Plan Route", use_container_width=True):
            st.session_state.page = "Route"
            st.rerun()
    
    with col2:
        if st.button("👁️ Obstacle Detection", use_container_width=True):
            st.session_state.page = "Vision"
            st.rerun()
    
    with col3:
        if st.button("🚨 Emergency SOS", use_container_width=True):
            st.session_state.page = "Emergency"
            st.rerun()
    
    st.markdown("---")
    
    # Health status
    st.subheader("⚙️ System Status")
    
    response = api_call("GET", "/health")
    if response and response.status_code == 200:
        health = response.json()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            db_status = "🟢 Connected" if health.get("database") == "connected" else "🔴 Disconnected"
            st.write(f"**Database:** {db_status}")
        
        with col2:
            redis_status = "🟢 Connected" if health.get("redis") == "connected" else "🔴 Disconnected"
            st.write(f"**Cache:** {redis_status}")
        
        with col3:
            st.write(f"**Time:** {health.get('timestamp')}")
    else:
        st.error("❌ Unable to connect to backend")

def show_routing_page():
    """Route planning page"""
    st.title("🧭 Smart Route Planning")
    
    st.markdown("Calculate accessible routes based on your mobility needs")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📍 Route Details")
        
        col_a, col_b = st.columns(2)
        with col_a:
            start_lat = st.number_input("Start Latitude", value=40.7128, format="%.6f")
            start_lng = st.number_input("Start Longitude", value=-74.0060, format="%.6f")
        
        with col_b:
            end_lat = st.number_input("End Latitude", value=40.7580, format="%.6f")
            end_lng = st.number_input("End Longitude", value=-73.9855, format="%.6f")
        
        mode = st.selectbox("Travel Mode", ["wheelchair", "walking", "stroller"])
        
        if st.button("🔍 Plan Route"):
            response = api_call("POST", "/api/v1/routes/plan", {
                "start_lat": start_lat,
                "start_lng": start_lng,
                "end_lat": end_lat,
                "end_lng": end_lng,
                "mode": mode
            })
            
            if response and response.status_code == 200:
                route = response.json()
                st.session_state.current_route = route
                st.success("✅ Route planned successfully!")
            else:
                st.error("❌ Failed to plan route")
    
    with col2:
        st.subheader("⚙️ Filters")
        
        st.checkbox("Step-Free Only", value=True)
        st.checkbox("Avoid Tolls", value=False)
        st.checkbox("Prefer Well-Lit", value=True)
        st.checkbox("Avoid Crowds", value=False)
    
    # Display route if available
    if "current_route" in st.session_state:
        route = st.session_state.current_route
        
        st.markdown("---")
        st.subheader("📊 Route Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = route.get("metrics", {})
        with col1:
            st.metric("Distance", f"{metrics.get('total_distance', 0) / 1000:.2f} km")
        with col2:
            st.metric("Duration", f"{metrics.get('total_duration', 0) / 60:.0f} min")
        with col3:
            st.metric("Accessibility", f"{metrics.get('accessibility_score', 0):.0f}%")
        with col4:
            st.metric("Safety", f"{metrics.get('safety_score', 0):.0f}%")
        
        # Map
        st.subheader("🗺️ Route Map")
        m = folium.Map(
            location=[(40.7128 + 40.7580) / 2, (-74.0060 - 73.9855) / 2],
            zoom_start=13,
            tiles="OpenStreetMap"
        )
        
        folium.Marker([40.7128, -74.0060], popup="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker([40.7580, -73.9855], popup="End", icon=folium.Icon(color="red")).add_to(m)
        
        st_folium(m, width=700, height=500)

def show_vision_page():
    """Computer vision page"""
    st.title("👁️ Obstacle Detection & Vision Assistance")
    
    st.markdown("Real-time obstacle detection and signboard reading for safe navigation")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚧 Obstacle Detection",
        "📄 Sign Reading",
        "🚸 Crossing Detection",
        "🛣️ Surface Analysis"
    ])
    
    with tab1:
        st.subheader("Detect Obstacles")
        uploaded_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
        
        if uploaded_file and st.button("🔍 Analyze"):
            st.info("🔄 Analyizing image...")
            
            files = {"file": uploaded_file}
            try:
                response = requests.post(
                    f"{API_URL}/api/v1/vision/detect-obstacles",
                    files=files,
                    headers={"Authorization": f"Bearer {st.session_state.token}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(uploaded_file, use_column_width=True)
                    with col2:
                        st.success(result.get("voice_feedback", "Analysis complete"))
                        st.metric("Obstacles Found", result.get("obstacle_count", 0))
                        st.metric("Danger Alert", "⚠️ YES" if result.get("has_danger") else "✅ SAFE")
                        
                        if result.get("detections"):
                            st.write("**Detected Objects:**")
                            for det in result["detections"][:5]:
                                st.write(f"- {det['class']}: {det['confidence']:.0%} confidence, {det['distance']:.1f}m away")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.subheader("Read Sign Text")
        uploaded_file = st.file_uploader("Upload sign image", type=["jpg", "jpeg", "png"], key="sign")
        
        if uploaded_file and st.button("📖 Read Text"):
            st.info("🔄 Reading text...")
            
            files = {"file": uploaded_file}
            try:
                response = requests.post(
                    f"{API_URL}/api/v1/vision/read-sign",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(uploaded_file, use_column_width=True)
                    with col2:
                        if result.get("text"):
                            st.success(f"📖 Text Found:\n\n{result['text']}")
                            st.info(result.get("voice_output"))
                        else:
                            st.warning("No text detected in image")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with tab3:
        st.subheader("Pedestrian Crossing Detection")
        uploaded_file = st.file_uploader("Upload crossing image", type=["jpg", "jpeg", "png"], key="crossing")
        
        if uploaded_file and st.button("🚸 Detect Crossing"):
            st.info("🔄 Analyzing crossing...")
            
            files = {"file": uploaded_file}
            try:
                response = requests.post(
                    f"{API_URL}/api/v1/vision/detect-crossing",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(uploaded_file, use_column_width=True)
                    with col2:
                        if result["crossing_detected"]:
                            st.success(f"🚸 Crossing Found! Confidence: {result['confidence']:.0%}")
                        else:
                            st.info("No crossing detected")
                        st.info(result.get("voice_guidance"))
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with tab4:
        st.subheader("Analyze Surface Quality")
        uploaded_file = st.file_uploader("Upload surface image", type=["jpg", "jpeg", "png"], key="surface")
        
        if uploaded_file and st.button("🛣️ Analyze Surface"):
            st.info("🔄 Analyzing surface...")
            
            files = {"file": uploaded_file}
            try:
                response = requests.post(
                    f"{API_URL}/api/v1/vision/analyze-surface",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(uploaded_file, use_column_width=True)
                    with col2:
                        st.metric("Smoothness", f"{result.get('smoothness_score', 0):.0f}%")
                        st.metric("Surface Type", result.get("surface_type", "unknown").title())
                        wheelchair_friendly = "✅ YES" if result.get("wheelchair_friendly") else "❌ NO"
                        st.metric("Wheelchair Friendly", wheelchair_friendly)
                        st.write(f"Has Obstacles: {'⚠️ YES' if result.get('has_obstacles') else '✅ NO'}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

def show_emergency_page():
    """Emergency SOS page"""
    st.title("🚨 Emergency & Safety")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🆘 SOS Emergency Alert")
        st.warning("Press the button below in case of emergency. Your location will be shared with emergency contacts.")
        
        if st.button("🆘 TRIGGER SOS", key="sos_button"):
            response = api_call("POST", "/api/v1/emergency/sos", {
                "lat": 40.7128,
                "lng": -74.0060
            })
            
            if response and response.status_code == 200:
                result = response.json()
                st.success(result.get("message", "SOS Triggered!"))
                st.balloons()
            else:
                st.error("❌ Failed to trigger SOS")
    
    with col2:
        st.subheader("📋 Emergency Contacts")
        
        response = api_call("GET", "/api/v1/emergency/contacts")
        if response and response.status_code == 200:
            contacts = response.json()
            if contacts:
                for contact in contacts:
                    st.write(f"👤 {contact['name']}")
                    st.write(f"📱 {contact['phone']}")
                    st.write(f"💬 {contact['relationship']}")
                    st.markdown("---")
            else:
                st.info("No emergency contacts added yet")
    
    st.markdown("---")
    st.subheader("➕ Add Emergency Contact")
    
    col1, col2 = st.columns(2)
    with col1:
        contact_name = st.text_input("Contact Name")
        contact_phone = st.text_input("Phone Number")
    with col2:
        contact_relation = st.selectbox("Relationship", ["Family", "Friend", "Doctor", "Caregiver", "Other"])
        notify = st.checkbox("Notify on SOS", value=True)
    
    if st.button("➕ Add Contact"):
        if contact_name and contact_phone:
            response = api_call("POST", "/api/v1/emergency/contacts", {
                "name": contact_name,
                "phone": contact_phone,
                "relationship": contact_relation,
                "notify_on_sos": notify
            })
            
            if response and response.status_code == 200:
                st.success("✅ Contact added!")
            else:
                st.error("❌ Failed to add contact")

def show_reports_page():
    """Community reports page"""
    st.title("📊 Accessibility Reports")
    
    st.subheader("Report Issues & Help Others")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🆕 Create Report")
        
        report_type = st.selectbox(
            "Issue Type",
            ["broken_ramp", "obstacle", "accident", "accessibility_issue", "other"]
        )
        
        report_lat = st.number_input("Latitude", value=40.7128, format="%.6f")
        report_lng = st.number_input("Longitude", value=-74.0060, format="%.6f")
        
        description = st.text_area("Description")
        severity = st.selectbox("Severity", ["low", "medium", "high"])
        
        if st.button("📝 Submit Report"):
            if description:
                response = api_call("POST", "/api/v1/reports", {
                    "type": report_type,
                    "lat": report_lat,
                    "lng": report_lng,
                    "description": description,
                    "severity": severity
                })
                
                if response and response.status_code == 200:
                    st.success("✅ Report submitted! Thank you for helping the community.")
                else:
                    st.error("❌ Failed to submit report")
            else:
                st.error("Please fill in all fields")
    
    with col2:
        st.markdown("### 📍 Nearby Reports")
        
        nearby_lat = st.number_input("Search Latitude", value=40.7128, format="%.6f", key="nearby_lat")
        nearby_lng = st.number_input("Search Longitude", value=-74.0060, format="%.6f", key="nearby_lng")
        radius = st.slider("Radius (meters)", 500, 5000, 1000)
        
        if st.button("🔍 Find Reports"):
            response = api_call("GET", f"/api/v1/reports/nearby?lat={nearby_lat}&lng={nearby_lng}&radius={radius}")
            
            if response and response.status_code == 200:
                reports = response.json()
                if reports:
                    for report in reports[:10]:
                        with st.container():
                            st.write(f"**{report.get('type', 'Unknown').upper()}** - {report.get('severity', '').upper()}")
                            st.write(f"📍 {report.get('description', '')}")
                            st.write(f"📅 {report.get('created_at', '')}")
                            st.markdown("---")
                else:
                    st.info("No reports found in this area")

def show_parking_page():
    """Parking assistance page"""
    st.title("🅿️ Smart Parking Assistance")
    
    st.markdown("Find nearby accessible parking with real-time availability")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Find Parking")
        
        park_lat = st.number_input("Latitude", value=40.7128, format="%.6f", key="park_lat")
        park_lng = st.number_input("Longitude", value=-74.0060, format="%.6f", key="park_lng")
        radius = st.slider("Search Radius (meters)", 100, 2000, 500, key="park_radius")
        
        col_a, col_b = st.columns(2)
        with col_a:
            accessible_only = st.checkbox("Accessible Only", value=True)
        with col_b:
            if st.button("🔍 Search"):
                response = api_call(
                    "GET",
                    f"/api/v1/parking/nearby?lat={park_lat}&lng={park_lng}&radius={radius}&accessible_only={accessible_only}"
                )
                
                if response and response.status_code == 200:
                    parkings = response.json()
                    st.session_state.parking_results = parkings
    
    with col2:
        st.subheader("⭐ Filters")
        min_available = st.slider("Min Available Spots", 0, 100, 1)
        max_price = st.slider("Max Price ($/hr)", 0, 50, 20)
    
    # Display results
    if "parking_results" in st.session_state and st.session_state.parking_results:
        st.markdown("---")
        st.subheader("📝 Results")
        
        for parking in st.session_state.parking_results:
            with st.container():
                col_1, col_2 = st.columns([2, 1])
                
                with col_1:
                    st.write(f"**{parking.get('name', 'Parking')}**")
                    st.write(f"📍 {parking.get('address', '')}")
                with col_2:
                    st.metric("Available", f"{parking.get('accessible_available', 0)}/{parking.get('accessible_spots', 0)}")
                    if parking.get("price_per_hour"):
                        st.metric("Price", f"${parking.get('price_per_hour', 0):.2f}/hr")
                
                if parking.get("has_ramp"):
                    st.write("♿ Has Accessible Ramp")
                
                st.markdown("---")

def show_profile_page():
    """User profile page"""
    st.title("👤 User Profile")
    
    if st.session_state.user:
        user = st.session_state.user
        profile = user.get("profile", {})
        preferences = user.get("preferences", {})
        
        st.subheader("📋 Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text(f"Name: {profile.get('name', 'N/A')}")
            st.text(f"Email: {user.get('email', 'N/A')}")
        with col2:
            st.text(f"Phone: {profile.get('phone', 'N/A')}")
            st.text(f"Safety Score: {user.get('safety_score', 100):.0f}/100")
        
        st.markdown("---")
        st.subheader("♿ Accessibility Settings")
        
        mode = st.selectbox(
            "Accessibility Mode",
            ["none", "wheelchair", "visually-impaired", "elderly"],
            index=["none", "wheelchair", "visually-impaired", "elderly"].index(profile.get("accessibility_mode", "none"))
        )
        
        st.multiselect("Disabilities", ["mobility", "vision", "hearing", "cognitive"], default=profile.get("disabilities", []))
        st.multiselect("Mobility Aids", ["crutches", "walker", "cane", "wheelchair", "scooter"], default=profile.get("mobility_aids", []))
        
        st.markdown("---")
        st.subheader("⚙️ Preferences")
        
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Voice Guidance", value=preferences.get("voice_guidance", False))
            st.checkbox("Avoid Tolls", value=preferences.get("avoid_tolls", False))
        with col2:
            st.checkbox("Haptic Feedback", value=preferences.get("haptic_feedback", True))
            st.checkbox("Step-Free Routes", value=preferences.get("require_step_free", False))
        
        language = st.selectbox("Language", ["en", "es", "fr", "hi"], index=0)
        
        if st.button("💾 Save Profile"):
            st.success("✅ Profile updated!")

# ============================================
# MAIN APP FLOW
# ============================================

def main():
    # Initialize page
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"
    
    # Show start or main app
    if not st.session_state.started:
        show_start_page()
    else:
        # Sidebar navigation
        with st.sidebar:
            st.title("🧭 Accessible Map AI")
            st.markdown("***")
            
            pages = {
                "🏠 Dashboard": "Dashboard",
                "🧭 Route Planning": "Route",
                "👁️ Vision Assist": "Vision",
                "📊 Reports": "Reports",
                "🅿️ Parking": "Parking",
                "🚨 Emergency": "Emergency",
                "👤 Profile": "Profile",
            }
            
            for page_name, page_key in pages.items():
                if st.button(page_name, use_container_width=True, key=page_key):
                    st.session_state.page = page_key
            
            st.markdown("***")
            st.markdown("### 📱 Quick Info")
            st.write(f"**Mode:** {st.session_state.accessibility_mode.title()}")
            st.write(f"**User ID:** {st.session_state.user_id}")
        
        # Show selected page
        if st.session_state.page == "Dashboard":
            show_dashboard()
        elif st.session_state.page == "Route":
            show_routing_page()
        elif st.session_state.page == "Vision":
            show_vision_page()
        elif st.session_state.page == "Emergency":
            show_emergency_page()
        elif st.session_state.page == "Reports":
            show_reports_page()
        elif st.session_state.page == "Parking":
            show_parking_page()
        elif st.session_state.page == "Profile":
            show_profile_page()

if __name__ == "__main__":
    main()
