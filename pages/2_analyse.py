import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Analyse", page_icon="📈", layout="wide")

st.title("📈 Analyse des données")
st.markdown("---")

# Charger les résultats du notebook scoring_runs
score_path = Path("data") / "run_scores.csv"
@st.cache_data
def load_scoring_data(path):
    if path.exists():
        return pd.read_csv(path)
    return None

score_df = load_scoring_data(score_path)

st.header("Résultats du notebook `scoring_runs`")
if score_df is None:
    st.warning("⚠️ Le fichier `data/run_scores.csv` est introuvable. Exécutez le notebook `scoring_runs.ipynb` pour générer les résultats.")
else:
    st.markdown("### Vue d'ensemble des runs scorés")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nombre de runs", f"{len(score_df):,}")
    col2.metric("Taux de victoire", f"{score_df['victory'].mean() * 100:.1f}%")
    col3.metric("Score moyen", f"{score_df['score'].mean():.1f}")
    col4.metric("Durée moyenne", f"{score_df['duration'].mean():.0f} frames")

    with st.expander("Afficher les scores bruts"):
        st.dataframe(score_df.head(15), use_container_width=True)

    st.markdown("---")
    st.subheader("Filtres et comparaisons")
    difficulty = st.selectbox("Filtrer par difficulté", options=["Toutes"] + sorted(score_df['difficulty'].unique().astype(str).tolist()))
    character = st.selectbox("Filtrer par personnage", options=["Tous"] + sorted(score_df['character'].unique().astype(str).tolist()))

    filtered = score_df.copy()
    if difficulty != "Toutes":
        filtered = filtered[filtered['difficulty'].astype(str) == difficulty]
    if character != "Tous":
        filtered = filtered[filtered['character'].astype(str) == character]

    st.markdown(f"**Runs affichés :** {len(filtered)}")
    
    tabs = st.tabs(["Distribution", "Corrélations", "Analyse personnalisée"])
    
    with tabs[0]:
        st.subheader("Distribution des scores")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(filtered['score'], bins=20, kde=True, ax=ax, color='#4c78a8')
        ax.set_xlabel('Score')
        ax.set_ylabel('Nombre de runs')
        st.pyplot(fig)

        st.subheader("Durée vs score")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.scatter(filtered['duration'], filtered['score'], alpha=0.6)
        ax.set_xlabel('Durée (frames)')
        ax.set_ylabel('Score')
        st.pyplot(fig)

    with tabs[1]:
        st.subheader("Matrice de corrélation des métriques")
        numeric_cols = filtered.select_dtypes(include=np.number).columns.tolist()
        if len(numeric_cols) >= 2:
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(filtered[numeric_cols].corr(), annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
            st.pyplot(fig)
        else:
            st.info("Pas assez de colonnes numériques pour afficher une corrélation.")

    with tabs[2]:
        st.subheader("Analyse personnalisée")
        custom_cols = st.multiselect(
            "Choisissez 2 colonnes numériques pour le scatter plot",
            options=numeric_cols,
            default=numeric_cols[:2] if len(numeric_cols) >= 2 else []
        )
        if len(custom_cols) == 2:
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.scatter(filtered[custom_cols[0]], filtered[custom_cols[1]], alpha=0.7)
            ax.set_xlabel(custom_cols[0])
            ax.set_ylabel(custom_cols[1])
            st.pyplot(fig)
        else:
            st.info("Sélectionnez exactement 2 colonnes numériques pour le graphique.")

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
