import streamlit as st
import pandas as pd
import numpy as np  # Indispensable pour les calculs mathématiques
import plotly.express as px
from io import BytesIO
from streamlit_js_eval import get_geolocation  # L'import qui manquait !
from data_processor import parse_gpx

# Configuration de la page
st.set_page_config(page_title="Dashboard Vie Numérique & Physique", layout="wide", page_icon="📊")

# Fonction mathématique pour calculer la distance entre deux points GPS
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Rayon de la Terre en km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

st.title("📊 Mon Tableau de Bord Personnel")

# Création des onglets
tab_gps, tab_sante, tab_ecran = st.tabs(["📍 GPS & Trajets", "👣 Pas & Santé", "📱 Temps d'Écran"])

# --- ONGLET 1 : GPS ---
with tab_gps:
    st.header("1. Capturer ma position en direct")
    
    # Appel de la fonction de géolocalisation
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
            st.toast("Point enregistré !")

    if 'live_points' in st.session_state and len(st.session_state['live_points']) > 1:
        df_live = pd.DataFrame(st.session_state['live_points'])
        
        # Calcul de la distance
        dist_total_live = 0
        for i in range(len(df_live)-1):
            dist_total_live += haversine(df_live.iloc[i]['latitude'], df_live.iloc[i]['longitude'], 
                                         df_live.iloc[i+1]['latitude'], df_live.iloc[i+1]['longitude'])
        
        st.info(f"📏 Distance parcourue en direct : **{dist_total_live:.2f} km**")
        st.map(df_live)

    st.divider()
    st.header("2. Analyser un fichier GPX")
    file_gpx = st.file_uploader("Importez un fichier .gpx", type=["gpx"])
    if file_gpx:
        df_gpx = parse_gpx(file_gpx)
        st.map(df_gpx)

# --- ONGLET 2 : SANTÉ (Pas) ---
with tab_sante:
    st.header("👣 Activité Physique")
    file_sante = st.file_uploader("Fichier de pas (CSV)", type=["csv"], key="sante")
    
    if file_sante:
        df_sante = pd.read_csv(file_sante)
        if 'date' in df_sante.columns and 'steps' in df_sante.columns:
            fig_pas = px.bar(df_sante, x='date', y='steps', title="Nombre de pas par jour", color_discrete_sequence=['#00CC96'])
            st.plotly_chart(fig_pas, use_container_width=True)
        else:
            st.error("Le CSV doit contenir des colonnes 'date' et 'steps'.")

# --- ONGLET 3 : TEMPS D'ÉCRAN ---
with tab_ecran:
    st.header("📱 Usage du Smartphone")
    file_ecran = st.file_uploader("Fichier temps d'écran (CSV)", type=["csv"], key="ecran")
    
    if file_ecran:
        df_ecran = pd.read_csv(file_ecran)
        if 'app_name' in df_ecran.columns and 'duration_minutes' in df_ecran.columns:
            fig_app = px.pie(df_ecran, values='duration_minutes', names='app_name', title="Répartition du temps")
            st.plotly_chart(fig_app, use_container_width=True)
        else:
            st.error("Le CSV doit contenir 'app_name' et 'duration_minutes'.")