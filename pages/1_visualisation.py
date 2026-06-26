import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Visualisation", page_icon="📊", layout="wide")

st.title("📊 Visualisation des données")
st.markdown("---")

# Récupération des données depuis session_state
if 'data' in st.session_state:
    data = st.session_state.data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Aperçu des données")
        st.dataframe(data.head(10))
    
    with col2:
        st.subheader("Statistiques descriptives")
        st.write(data.describe())
    
    # Graphique
    st.subheader("Graphique de distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    data.hist(ax=ax, bins=20)
    plt.tight_layout()
    st.pyplot(fig)
    
else:
    st.warning("⚠️ Aucune donnée disponible. Retournez à l'accueil.")
