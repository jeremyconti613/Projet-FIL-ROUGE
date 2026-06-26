import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analyse", page_icon="📈", layout="wide")

st.title("📈 Analyse des données")
st.markdown("---")

if 'data' in st.session_state:
    data = st.session_state.data
    
    # Sélection de colonnes
    colonnes = st.multiselect(
        "Sélectionnez les colonnes à analyser",
        options=data.columns.tolist(),
        default=data.columns.tolist()[:2]
    )
    
    if len(colonnes) >= 2:
        st.subheader("Matrice de corrélation")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(data[colonnes].corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)
        
        st.subheader("Nuage de points")
        fig, ax = plt.subplots()
        ax.scatter(data[colonnes[0]], data[colonnes[1]], alpha=0.5)
        ax.set_xlabel(colonnes[0])
        ax.set_ylabel(colonnes[1])
        st.pyplot(fig)
    else:
        st.info("Sélectionnez au moins 2 colonnes pour l'analyse")
else:
    st.warning("⚠️ Aucune donnée disponible.")
