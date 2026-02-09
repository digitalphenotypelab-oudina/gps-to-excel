import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from streamlit_js_eval import get_geolocation
from data_processor import parse_gpx
from supabase import create_client, Client

# --- 1. CONFIGURATION & CONNEXION ---
st.set_page_config(page_title="Dashboard Vie Numérique", layout="wide", page_icon="📊")

# Remplace par tes vrais identifiants Supabase (Section Settings > API)
SUPABASE_URL = "https://editeaqmqnnlvllefjop.supabase.co"
SUPABASE_KEY = "sb_publishable_e4BH8AM2iuDdS3gav7QM_w_6NXg6w4a"

# Initialisation sécurisée du client Supabase
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception:
    st.error("Erreur de connexion à Supabase. Vérifiez vos clés API.")

# --- 2. FONCTIONS UTILES ---
def haversine(lat1, lon1, lat2, lon2):
    """Calcul de distance entre deux points GPS en km"""
    R = 6371 
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def fetch_supabase_data():
    """Récupère les données synchronisées depuis le Cloud"""
    try:
        response = supabase.table("daily_metrics").select("*").order("date", desc=True).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.sidebar.error(f"Erreur Synchro : {e}")
        return pd.DataFrame()

# --- 3. INTERFACE PRINCIPALE ---
st.title("📊 Mon Tableau de Bord Personnel")

# Barre latérale pour la synchronisation Cloud
with st.sidebar:
    st.header("☁️ Cloud Sync")
    if st.button("🔄 Synchroniser avec Supabase"):
        df_cloud = fetch_supabase_data()
        if not df_cloud.empty:
            st.session_state['data_cloud'] = df_cloud
            st.success("Données récupérées !")
        else:
            st.warning("Aucune donnée trouvée sur le Cloud.")

# Création des onglets
tab_gps, tab_sante, tab_ecran, tab_cloud = st.tabs([
    "📍 GPS & Trajets", 
    "👣 Pas & Santé", 
    "📱 Temps d'Écran",
    "☁️ Historique Cloud"
])

# --- ONGLET 1 : GPS ---
with tab_gps:
    st.header("Capturer ma position en direct")
    location = get_geolocation()

    if location:
        curr_lat = location['coords']['latitude']
        curr_lon = location['coords']['longitude']
        st.metric("Position Actuelle", f"{curr_lat:.5f}, {curr_lon:.5f}")
        
        if st.button("📌 Enregistrer ce point"):
            new_point = {"timestamp": pd.Timestamp.now(), "latitude": curr_lat, "longitude": curr_lon}
            if 'live_points' not in st.session_state:
                st.session_state['live_points'] = []
            st.session_state['live_points'].append(new_point)
            st.toast("Point enregistré !")

    if 'live_points' in st.session_state and len(st.session_state['live_points']) > 1:
        df_live = pd.DataFrame(st.session_state['live_points'])
        dist = sum(haversine(df_live.iloc[i]['latitude'], df_live.iloc[i]['longitude'], 
                             df_live.iloc[i+1]['latitude'], df_live.iloc[i+1]['longitude']) 
                   for i in range(len(df_live)-1))
        st.info(f"📏 Distance parcourue : **{dist:.2f} km**")
        st.map(df_live)

    st.divider()
    st.header("Analyser un fichier GPX")
    file_gpx = st.file_uploader("Importez un .gpx", type=["gpx"])
    if file_gpx:
        df_gpx = parse_gpx(file_gpx)
        st.map(df_gpx)

# --- ONGLET 2 : SANTÉ ---
with tab_sante:
    st.header("👣 Activité Physique")
    file_sante = st.file_uploader("Fichier de pas (CSV)", type=["csv"], key="sante")
    if file_sante:
        df_s = pd.read_csv(file_sante)
        if 'date' in df_s.columns and 'steps' in df_s.columns:
            st.plotly_chart(px.bar(df_s, x='date', y='steps', title="Pas par jour"), use_container_width=True)
        else:
            st.error("Colonnes 'date' et 'steps' requises.")

# --- ONGLET 3 : TEMPS D'ÉCRAN ---
with tab_ecran:
    st.header("📱 Usage du Smartphone")
    file_ecran = st.file_uploader("Fichier temps d'écran (CSV)", type=["csv"], key="ecran")
    if file_ecran:
        df_e = pd.read_csv(file_ecran)
        if 'app_name' in df_e.columns and 'duration_minutes' in df_e.columns:
            st.plotly_chart(px.pie(df_e, values='duration_minutes', names='app_name'), use_container_width=True)

# --- ONGLET 4 : HISTORIQUE CLOUD ---
with tab_cloud:
    st.header("☁️ Données sauvegardées sur Supabase")
    if 'data_cloud' in st.session_state:
        df_c = st.session_state['data_cloud']
        st.dataframe(df_c, use_container_width=True)
        
        # Petit graphique combiné
        if not df_c.empty and 'steps' in df_c.columns:
            st.subheader("Évolution globale")
            fig = px.line(df_c, x='date', y=['steps', 'distance_gps'], title="Activité historique")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cliquez sur le bouton 'Synchroniser' dans la barre latérale pour voir vos données cloud.")