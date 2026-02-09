import streamlit as st
import pandas as pd
from io import BytesIO
from data_processor import parse_gpx # On importe notre nouveau décodeur

st.title("📍 Mon Journal GPS Réel")

# --- ZONE D'IMPORT ---
st.header("1. Importez vos données")
uploaded_file = st.file_uploader("Choisissez un fichier .gpx issu de votre téléphone", type=["gpx"])

if uploaded_file is not None:
    # Lecture du fichier réel
    df = parse_gpx(uploaded_file)
    st.session_state['data'] = df
    st.success("Données chargées avec succès !")

# --- AFFICHAGE ET EXPORT ---
if 'data' in st.session_state:
    df = st.session_state['data']
    
    st.subheader("Aperçu du trajet")
    st.map(df)
    
    # Export Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Trajet_GPS')
        
    st.download_button(
        label="📥 Télécharger en Excel",
        data=output.getvalue(),
        file_name="mon_trajet_gps.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )