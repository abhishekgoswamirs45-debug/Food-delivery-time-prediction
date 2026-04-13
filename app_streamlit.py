import streamlit as st
import pickle
import numpy as np
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium
from geopy.distance import geodesic
import requests

# Load model
model = pickle.load(open("model.pkl", "rb"))
geolocator = Nominatim(user_agent="food_delivery_app")

# Page config
st.set_page_config(page_title="Delivery AI", page_icon="🚚", layout="centered")

# ---- UI STYLE ----
st.markdown("""
<style>
body {background-color: #0f172a;}
.title {font-size:40px; color:white; text-align:center; font-weight:bold;}
.sub {color:#94a3b8; text-align:center; margin-bottom:30px;}
.card {
    background:#1e293b;
    padding:25px;
    border-radius:15px;
    box-shadow:0px 0px 20px rgba(0,0,0,0.3);
}
.result {
    background:#22c55e;
    padding:15px;
    border-radius:10px;
    text-align:center;
    font-size:22px;
    color:white;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚚 Smart Delivery Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">AI + Real Road Map (Leaflet + OSRM)</div>', unsafe_allow_html=True)

# ---- INPUT ----
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        origin = st.text_input("📍 Restaurant", "DB Mall Bhopal")

    with col2:
        destination = st.text_input("🏠 Delivery", "Bhopal Railway Station")

    traffic = st.selectbox("🚦 Traffic", ["Low", "Medium", "High"])
    traffic_map = {"Low":1, "Medium":2, "High":3}

    btn = st.button("🚀 Predict Delivery Time", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---- ROUTE FUNCTION ----
def get_route(coords1, coords2):
    url = f"http://router.project-osrm.org/route/v1/driving/{coords1[1]},{coords1[0]};{coords2[1]},{coords2[0]}?overview=full&geometries=geojson"
    response = requests.get(url).json()
    route = response["routes"][0]["geometry"]["coordinates"]
    return [(point[1], point[0]) for point in route]

# ---- SESSION STATE (FIX) ----
if "map" not in st.session_state:
    st.session_state.map = None
    st.session_state.result = None

# ---- PREDICT ----
if btn:
    if origin and destination:
        try:
            loc1 = geolocator.geocode(origin)
            loc2 = geolocator.geocode(destination)

            if loc1 is None or loc2 is None:
                st.error("❌ Location not found. Try full names.")
            else:
                coords1 = (loc1.latitude, loc1.longitude)
                coords2 = (loc2.latitude, loc2.longitude)

                # Distance
                distance = geodesic(coords1, coords2).km

                # Prediction
                prep_time = 15
                input_data = np.array([[distance, prep_time, traffic_map[traffic]]])
                prediction = model.predict(input_data)

                # Route
                route_coords = get_route(coords1, coords2)

                # Map
                m = folium.Map(location=coords1, zoom_start=13, tiles="cartodbpositron")

                folium.Marker(coords1, tooltip="Restaurant", icon=folium.Icon(color="green")).add_to(m)
                folium.Marker(coords2, tooltip="Delivery", icon=folium.Icon(color="red")).add_to(m)

                folium.PolyLine(route_coords, color="blue", weight=5).add_to(m)

                # SAVE
                st.session_state.map = m
                st.session_state.result = (prediction[0], distance)

        except:
            st.error("⚠️ Something went wrong. Try different locations.")
    else:
        st.warning("Enter both locations bro 😄")

# ---- DISPLAY (STABLE) ----
if st.session_state.map:
    st.subheader("🗺️ Live Road Route")
    st_folium(st.session_state.map, width=700, height=500)

if st.session_state.result:
    pred, dist = st.session_state.result
    st.markdown(f"""
    <div class="result">
        ⏱ {round(pred,2)} minutes <br>
        📏 {round(dist,2)} km
    </div>
    """, unsafe_allow_html=True)