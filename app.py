import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from data_processor import parse_gpx

st.set_page_config(page_title="Dashboard Vie Numérique & Physique", layout="wide")

st.title("📊 Mon Tableau de Bord Personnel")

# Création des onglets
tab_gps, tab_sante, tab_ecran = st.tabs(["📍 GPS & Trajets", "👣 Pas & Santé", "📱 Temps d'Écran"])

# Fonction mathématique pour calculer la distance entre deux points GPS
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Rayon de la Terre en km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c


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

# --- ONGLET 2 : SANTÉ (Pas) ---
with tab_sante:
    st.header("Activité Physique")
    st.write("Importez votre export CSV (ex: Gadgetbridge, Google Fit)")
    
    file_sante = st.file_uploader("Fichier de pas (CSV)", type=["csv"], key="sante")
    
    if file_sante:
        df_sante = pd.read_csv(file_sante)
        # On suppose que le CSV a des colonnes 'date' et 'steps'
        st.subheader("Évolution de vos pas")
        fig_pas = px.bar(df_sante, x='date', y='steps', title="Nombre de pas par jour", color_discrete_sequence=['#00CC96'])
        st.plotly_chart(fig_pas, use_container_width=True)
        
        col1, col2 = st.columns(2)
        col1.metric("Record de pas", f"{df_sante['steps'].max()} pas")
        col2.metric("Moyenne", f"{int(df_sante['steps'].mean())} pas/jour")

# --- ONGLET 3 : TEMPS D'ÉCRAN ---
with tab_ecran:
    st.header("Usage du Smartphone")
    st.write("Importez votre export JSON ou CSV (ex: ActivityWatch)")
    
    file_ecran = st.file_uploader("Fichier temps d'écran", type=["csv", "json"], key="ecran")
    
    if file_ecran:
        df_ecran = pd.read_csv(file_ecran)
        # On suppose des colonnes 'app_name' et 'duration_minutes'
        st.subheader("Top des applications utilisées")
        fig_app = px.pie(df_ecran, values='duration_minutes', names='app_name', title="Répartition du temps")
        st.plotly_chart(fig_app, use_container_width=True)
        
        st.info("💡 Conseil : Essayez de réduire de 10% l'app la plus utilisée demain !")