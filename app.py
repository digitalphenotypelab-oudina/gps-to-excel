import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from streamlit_js_eval import get_geolocation
from data_processor import parse_gpx

# Fonction mathématique pour calculer la distance entre deux points GPS
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Rayon de la Terre en km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

# Configuration de la page
st.set_page_config(page_title="GPS Tracker & Analytics", page_icon="📍", layout="wide")

st.title("📍 Mon Assistant GPS & Statistiques")

# --- SECTION 1 : GPS EN DIRECT ---
st.header("1. Capturer ma position en direct")

location = get_geolocation()

if location:
    curr_lat = location['coords']['latitude']
    curr_lon = location['coords']['longitude']
    
    st.metric("Ma Position Actuelle", f"{curr_lat:.5f}, {curr_lon:.5f}")
    
    if st.button("📌 Enregistrer ce point"):
        new_point = {
            "timestamp": pd.Timestamp.now(),
            "latitude": curr_lat,
            "longitude": curr_lon
        }
        if 'live_points' not in st.session_state:
            st.session_state['live_points'] = []
        st.session_state['live_points'].append(new_point)

if 'live_points' in st.session_state and len(st.session_state['live_points']) > 1:
    df_live = pd.DataFrame(st.session_state['live_points'])
    
    # Calcul de la distance cumulative pour le direct
    dist_total_live = 0
    for i in range(len(df_live)-1):
        dist_total_live += haversine(df_live.iloc[i]['latitude'], df_live.iloc[i]['longitude'], 
                                     df_live.iloc[i+1]['latitude'], df_live.iloc[i+1]['longitude'])
    
    st.info(f"📏 Distance parcourue en direct : **{dist_total_live:.2f} km**")
    st.map(df_live)

st.divider()

# --- SECTION 2 : ANALYSE GPX ---
st.header("2. Analyser un fichier GPX (Historique)")
uploaded_file = st.file_uploader("Importez votre trajet", type=["gpx"])

if uploaded_file:
    df_gpx = parse_gpx(uploaded_file)
    
    # Calcul de la distance totale du fichier GPX
    dist_total_gpx = 0
    for i in range(len(df_gpx)-1):
        dist_total_gpx += haversine(df_gpx.iloc[i]['latitude'], df_gpx.iloc[i]['longitude'], 
                                    df_gpx.iloc[i+1]['latitude'], df_gpx.iloc[i+1]['longitude'])
    
    # Affichage des statistiques
    col1, col2, col3 = st.columns(3)
    col1.metric("Distance Totale", f"{dist_total_gpx:.2f} km")
    col2.metric("Nombre de points", len(df_gpx))
    
    if 'elevation' in df_gpx.columns:
        denivele = df_gpx['elevation'].diff().clip(lower=0).sum()
        col3.metric("Dénivelé Positif", f"{denivele:.1f} m")

    st.map(df_gpx)

    # Export Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_gpx.to_excel(writer, index=False, sheet_name='Donnees_GPS')
    
    st.download_button("📥 Télécharger l'analyse Excel", output.getvalue(), "analyse_gps.xlsx")