import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Paramètres", page_icon="⚙️")

st.title("⚙️ Paramètres")
st.markdown("---")

st.subheader("Configuration de l'application")

# Paramètres
theme = st.selectbox("Thème", ["Clair", "Sombre"])
nb_lignes = st.slider("Nombre de lignes à générer", 10, 1000, 100)

if st.button("Générer de nouvelles données"):
    st.session_state.data = pd.DataFrame({
        'A': np.random.randn(nb_lignes),
        'B': np.random.randn(nb_lignes),
        'C': np.random.randn(nb_lignes)
    })
    st.success(f"✅ {nb_lignes} nouvelles lignes générées !")

st.subheader("Importer des données")
uploaded_file = st.file_uploader("Choisir un fichier CSV", type=['csv'])

if uploaded_file is not None:
    st.session_state.data = pd.read_csv(uploaded_file)
    st.success("✅ Fichier importé avec succès !")
    st.dataframe(st.session_state.data.head())
