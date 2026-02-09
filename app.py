import streamlit as st
import pandas as pd
from io import BytesIO
from data_generator import generate_fake_gps_data # Import de notre script précédent

# Configuration de la page
st.set_page_config(page_title="GPS to Excel Exporter", page_icon="📍")

st.title("📍 Exportateur de Données GPS")
st.markdown("Générez une trace GPS test ou importez vos données pour les convertir en Excel.")

# --- SECTION 1 : GÉNÉRATION DE DONNÉES TEST ---
st.header("1. Créer une Pipeline de Test")

col1, col2 = st.columns(2)
with col1:
    num_points = st.slider("Nombre de points GPS", 10, 500, 50)
with col2:
    generate_btn = st.button("Générer les données simulées")

if generate_btn:
    # Appel à notre fonction de pipeline
    df = generate_fake_gps_data(num_points=num_points)
    
    # Stocker dans la session pour ne pas perdre les données au rechargement
    st.session_state['data'] = df
    st.success(f"{num_points} points générés avec succès !")

# --- SECTION 2 : VISUALISATION & EXPORT ---
if 'data' in st.session_state:
    df = st.session_state['data']
    
    # Aperçu des données
    st.subheader("Aperçu des données")
    st.dataframe(df.head())
    
    # Carte simple (Streamlit gère ça automatiquement)
    st.map(df)
    
    # --- LE PIPELINE D'EXPORT EXCEL ---
    st.subheader("Exporter vers Excel")
    
    # Création du fichier Excel en mémoire (buffer)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='GPS_Data')
        # On peut ajouter ici des calculs ou formattage Excel si besoin
        
    processed_data = output.getvalue()
    
    st.download_button(
        label="📥 Télécharger le fichier Excel",
        data=processed_data,
        file_name="ma_journee_gps.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )