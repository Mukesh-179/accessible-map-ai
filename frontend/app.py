from urllib import response

import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from datetime import datetime
import pandas as pd
import folium
from streamlit_folium import st_folium
import time
from streamlit_autorefresh import st_autorefresh
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
body {
    margin: 0;
    overflow-x: hidden;
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

.login-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(14px);
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.6);
    animation: fadeIn 1s ease-in-out;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(20px);}
    to {opacity: 1; transform: translateY(0);}
}

.login-title {
    text-align: center;
    font-size: 34px;
    font-weight: bold;
    color: white;
}

.stButton>button {
    border-radius: 12px;
    background: linear-gradient(135deg, #3b82f6, #06b6d4);
    color: white;
    font-weight: bold;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #06b6d4, #3b82f6);
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

.login-container {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}

.login-title {
    text-align: center;
    font-size: 32px;
    font-weight: bold;
    color: white;
}

.stButton>button {
    border-radius: 10px;
    background: linear-gradient(135deg, #3b82f6, #06b6d4);
    color: white;
    font-weight: bold;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #06b6d4, #3b82f6);
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}

.metric-box {
    background: linear-gradient(135deg, #1f2937, #111827);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    transition: transform 0.2s ease-in-out;
}

.metric-box:hover {
    transform: scale(1.05);
}

.metric-title {
    font-size: 14px;
    color: #9ca3af;
}

.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #38bdf8;
}
</style>
""", unsafe_allow_html=True)
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

API_URL = "http://127.0.0.1:8000"
def api_call(method, endpoint, data=None):
    try:
        url = f"{API_URL}{endpoint}"

        headers = {}
        if "token" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.token}"

        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)

        elif method == "POST":
            headers["Content-Type"] = "application/json"
            
            response = requests.post(url, json=data, headers=headers, timeout=30)

        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(url, json=data, headers=headers, timeout=10)

        else:
            st.error("Unsupported HTTP method")
            return None

        return response

    except Exception as e:
        import traceback
        st.error("API Exception:")
        st.code(traceback.format_exc())
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
    
    def show_login_page():
        col1, col2, col3 = st.columns([1,2,1])

        with col2:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            st.markdown("<div class='login-title'>🧭 Accessible Map AI</div>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center;color:#cbd5e1;'>Smart Inclusive Mobility Platform</p>", unsafe_allow_html=True)
            st.markdown("---")

            tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

            # ================= LOGIN =================
            with tab1:
                email = st.text_input("📧 Email")
                password = st.text_input("🔑 Password", type="password")

                if st.button("🚀 Login", use_container_width=True):
                    response = api_call("POST", "/api/v1/auth/login", {
                    "email": email,
                    "password": password
                    })

                    if response and response.status_code == 200:
                        data = response.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.refresh_token = data["refresh_token"]
                        st.session_state.started = True
                        st.session_state.page = "Dashboard"
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

        # ================= REGISTER =================
            with tab2:
                name = st.text_input("👤 Full Name")
                reg_email = st.text_input("📧 Email", key="reg_email")
                phone = st.text_input("📱 Phone")
                reg_password = st.text_input("🔑 Password", type="password", key="reg_pass")

                accessibility_mode = st.selectbox(
                "♿ Accessibility Mode",
                ["none", "wheelchair", "visually_impaired", "hearing_impaired", "senior_citizen"]
                )

                if st.button("📝 Register", use_container_width=True):
                    response = api_call("POST", "/api/v1/auth/register", {
                    "email": reg_email,
                    "password": reg_password,
                    "name": name,
                    "phone": phone,
                    "accessibility_modes": [accessibility_mode]
                    })

                    if response and response.status_code == 200:
                        st.success("Registered successfully! Please login.")
                    else:
                        if response:
                            st.error(f"Error {response.status_code}")
                            st.write(response.text if response else "No response from backend")
                        else:
                            st.error("No response from backend")

            st.markdown("</div>", unsafe_allow_html=True)
    
# ============================================
# MAIN APP PAGES
# ============================================
def show_dashboard():
    st_autorefresh(interval=5000, key="dashboard_refresh")  # Auto refresh every 5 sec

    st.title("🚀 Smart Analytics Dashboard")

    # =============================
    # GET LIVE DATA
    # =============================
    response = api_call("GET", "/api/v1/dashboard/summary")

    if response and response.status_code == 200:
        stats = response.json()
    else:
        stats = {
            "total_routes": 0,
            "total_reports": 0,
            "emergency_contacts": 0,
            "safety_score": 100
        }

    # =============================
    # METRIC CARDS
    # =============================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🗺️ Routes", stats["total_routes"])
    col2.metric("📊 Reports", stats["total_reports"])
    col3.metric("🚨 Contacts", stats["emergency_contacts"])
    col4.metric("⭐ Safety Score", f"{stats['safety_score']:.0f}%")

    st.markdown("---")

    # =============================
    # LINE GRAPH (Simulated History)
    # =============================
    st.subheader("📈 Route Activity Trend")

    history_data = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Routes": [
            stats["total_routes"] * 0.6,
            stats["total_routes"] * 0.7,
            stats["total_routes"] * 0.8,
            stats["total_routes"] * 0.9,
            stats["total_routes"],
            stats["total_routes"] * 1.1,
            stats["total_routes"] * 1.2
        ]
    })

    st.line_chart(history_data.set_index("Day"))

    st.markdown("---")

    # =============================
    # AI INSIGHTS
    # =============================
    st.subheader("🧠 AI Insights")

    insights = []

    if stats["total_routes"] > 10:
        insights.append("📍 High mobility activity detected.")
    if stats["total_reports"] > 5:
        insights.append("⚠️ Increased accessibility issues reported.")
    if stats["safety_score"] < 80:
        insights.append("🚨 Safety score declining. Review routes.")

    if not insights:
        insights.append("✅ Everything looks great! Safe and active.")

    for insight in insights:
        st.info(insight)

    st.markdown("---")

    # =============================
    # QUICK ACTIONS
    # =============================
    st.subheader("⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    if col1.button("🧭 Plan Route", use_container_width=True):
        st.session_state.page = "Route"
        st.rerun()

    if col2.button("👁️ Vision Assist", use_container_width=True):
        st.session_state.page = "Vision"
        st.rerun()

    if col3.button("🚨 Emergency", use_container_width=True):
        st.session_state.page = "Emergency"
        st.rerun()

def show_routing_page():
    """Route planning with Dark Mode + Traffic Overlay"""

    st.title("🧭 Smart Route Planning")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📍 Route Details")

        col_a, col_b = st.columns(2)

        with col_a:
            start_lat = st.number_input("Start Latitude", value=12.9716, format="%.6f")
            start_lng = st.number_input("Start Longitude", value=77.5946, format="%.6f")

        with col_b:
            end_lat = st.number_input("End Latitude", value=12.9352, format="%.6f")
            end_lng = st.number_input("End Longitude", value=77.6245, format="%.6f")

        mode = st.selectbox(
            "🚘 Travel Mode",
            ["wheelchair", "walking", "car", "motorcycle", "bicycle", "bus"]
        )

        if st.button("🔍 Plan Route"):
            response = api_call("POST", "/api/v1/routes/plan", {
                "start_lat": start_lat,
                "start_lng": start_lng,
                "end_lat": end_lat,
                "end_lng": end_lng,
                "mode": mode
            })

            if response and response.status_code == 200:
                st.session_state.current_route = response.json()
                st.success("✅ Route planned successfully!")
            else:
                st.error("❌ Failed to plan route")

    with col2:
        st.subheader("🗺 Map Options")

        dark_mode = st.toggle("🌙 Dark Mode")
        show_traffic = st.toggle("🚦 Show Traffic Layer")

    # ===============================
    # DISPLAY ROUTE + MAP
    # ===============================

    if "current_route" in st.session_state:

        route = st.session_state.current_route
        metrics = route.get("metrics", {})

        st.markdown("---")
        st.subheader("📊 Route Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Distance", f"{metrics.get('total_distance', 0) / 1000:.2f} km")
        with col2:
            st.metric("Duration", f"{metrics.get('total_duration', 0) / 60:.0f} min")
        with col3:
            st.metric("Accessibility", f"{metrics.get('accessibility_score', 0):.0f}%")
        with col4:
            st.metric("Safety", f"{metrics.get('safety_score', 0):.0f}%")

        # 🌍 Tile selection
        if dark_mode:
            tile_style = "CartoDB dark_matter"
        else:
            tile_style = "CartoDB positron"

        m = folium.Map(
            location=[start_lat, start_lng],
            zoom_start=14,
            tiles=tile_style
        )

        # Start & End markers
        folium.Marker(
            [start_lat, start_lng],
            popup="Start",
            icon=folium.Icon(color="green")
        ).add_to(m)

        folium.Marker(
            [end_lat, end_lng],
            popup="End",
            icon=folium.Icon(color="red")
        ).add_to(m)

        # Draw Route
        if route.get("polyline"):

            coordinates = route["polyline"]
            latlng = [[coord[1], coord[0]] for coord in coordinates]

            mode_colors = {
                "car": "blue",
                "motorcycle": "purple",
                "bus": "orange",
                "bicycle": "green",
                "walking": "black",
                "wheelchair": "red"
            }

            color = mode_colors.get(route.get("mode"), "blue")

            folium.PolyLine(
                latlng,
                color=color,
                weight=6,
                opacity=0.9
            ).add_to(m)

        # 🚦 Simulated Traffic Overlay (Free)
        if show_traffic:
            folium.TileLayer(
                tiles="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
                attr="Traffic Layer",
                name="Traffic",
                overlay=True,
                control=True
            ).add_to(m)

        folium.LayerControl().add_to(m)

        st_folium(m, width=1000, height=550)

        

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
                        st.image(uploaded_file, width=400)
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
                    headers={"Authorization": f"Bearer {st.session_state.token}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(uploaded_file, width="stretch")
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
                headers={"Authorization": f"Bearer {st.session_state.token}"},
                timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(uploaded_file, width="stretch")
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
                    headers={"Authorization": f"Bearer {st.session_state.token}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(uploaded_file, width="stretch")
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
            response = requests.post(
                 f"{API_URL}/api/v1/emergency/sos",
                params={
                       "lat": 40.7128,
                        "lng": -74.0060
            })
            if "token" not in st.session_state:
                st.error("⚠️ Please login first.")
                return
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.post(
                f"{API_URL}/api/v1/emergency/sos",
                params={
        "lat": 40.7128,
        "lng": -74.0060
                },
                headers=headers
          )
         
            
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
        
        park_lat = st.number_input("Latitude", value=12.9716, format="%.6f", key="park_lat")
        park_lng = st.number_input("Longitude", value=77.5946, format="%.6f", key="park_lng")
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
                    parkings = response.json().get("parking", [])
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
    st.title("👤 User Profile")

    st.write("Token exists:", "token" in st.session_state)
    st.write("Started:", st.session_state.get("started"))
    st.write("Current Page:", st.session_state.get("page"))

    response = api_call("GET", "/api/v1/users/me")

    if not response:
        st.error("No response from backend")
        return

    if response.status_code != 200:
        st.error(f"Backend returned status {response.status_code}")
        st.write(response.text)
        return

    user = response.json()

    st.success("Profile Loaded Successfully")

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

    mode_list = ["none", "wheelchair", "visually_impaired", "elderly"]

    current_mode = profile.get("accessibility_mode", "none")
    if current_mode not in mode_list:
        current_mode = "none"

    st.selectbox(
        "Accessibility Mode",
        mode_list,
        index=mode_list.index(current_mode)
    )



# ============================================
# MAIN APP FLOW
# ============================================

def show_login_page():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = api_call("POST", "/api/v1/auth/login", {
            "email": email,
            "password": password
        })
        if response and response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.refresh_token = data["refresh_token"]
            st.session_state.started = True

             # 🔥 FETCH USER PROFILE
            profile_res = api_call("GET", "/api/v1/users/me")
            if profile_res and profile_res.status_code == 200:
                user = profile_res.json()
                st.session_state.accessibility_mode = user.get("profile", {}).get("accessibility_mode", "none")
                st.session_state.user_id = user.get("id")

            st.session_state.page = "Dashboard"
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.markdown("---")
    st.subheader("New user? Register")

    name = st.text_input("Full Name")
    reg_email = st.text_input("Register Email")
    phone = st.text_input("Phone Number")
    reg_password = st.text_input("Register Password", type="password")

    accessibility_mode = st.selectbox(
    "Accessibility Mode",
    ["none", "wheelchair", "visually_impaired", "hearing_impaired", "senior_citizen"]
    )

    if st.button("Register"):
        response = api_call("POST", "/api/v1/auth/register", {
        "email": reg_email,
        "password": reg_password,
        "name": name,
        "phone": phone,
        "accessibility_mode": accessibility_mode
        })

        if response and response.status_code == 200:
            st.success("Registered successfully! Please login.")
        else:
            if response:
                st.error(f"Error {response.status_code}")
                st.write(response.text)
            else:
                st.error("No response from backend")

    
        
def main():
    # Initialize page
        if "page" not in st.session_state:
            st.session_state.page = "Dashboard"
    
    # Show start or main app
        if "token" not in st.session_state:
            show_login_page()
            return
        if not st.session_state.started:
             show_start_page()
             return
        # Sidebar navigation
        with st.sidebar:
            st.title("🧭 Accessible Map AI")
            st.markdown("***")
            if st.button("🚪 Logout"):
                st.session_state.clear()
                st.rerun()
        
            
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
