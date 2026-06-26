import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image  # ← IMPORTANT : Ajouter cette ligne

# Configuration de la page
st.set_page_config(
    page_title="Mon Application",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Page d'accueil
st.title("🏠 Bienvenue dans mon application")
st.markdown("---")

# Logo
st.image("assets/images/logo.png", width=400)

# Exemple de données dans la session
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'A': np.random.randn(100),
        'B': np.random.randn(100),
        'C': np.random.randn(100)
    })

# Résultats générés par le notebook
output_dir = Path("notebooks/outputs")
data_dir = Path("data")

corr_matrix_file = output_dir / "correlation_matrix.csv"
run_features_file = output_dir / "run_level_features.csv"
run_scores_file = data_dir / "run_scores.csv"

corr_df = pd.read_csv(corr_matrix_file) if corr_matrix_file.exists() else None
features_df = pd.read_csv(run_features_file) if run_features_file.exists() else None
scores_df = pd.read_csv(run_scores_file) if run_scores_file.exists() else None

st.markdown("## 📊 Résultats générés par le notebook")

if corr_df is None and features_df is None and scores_df is None:
    st.warning("Aucun résultat de notebook n'a été trouvé. Assurez-vous que les fichiers CSV existent dans `notebooks/outputs` et `data`.")
else:
    if corr_df is not None or features_df is not None:
        metric_cols = st.columns(3)
        metric_cols[0].metric("📈 Runs analysés", f"{len(scores_df) if scores_df is not None else 'N/A'}")
        metric_cols[1].metric("🔧 Features run-level", f"{len(features_df.columns) if features_df is not None else 'N/A'}")
        metric_cols[2].metric("🧠 Corrélations", f"{corr_df.shape[0] - 1 if corr_df is not None else 'N/A'}")

    st.markdown("---")
    left_col, right_col = st.columns([2, 3])

    with left_col:
        if corr_df is not None:
            st.subheader("Matrice de corrélation")
            corr_display = corr_df.copy()
            if "Unnamed: 0" in corr_display.columns:
                corr_display = corr_display.set_index("Unnamed: 0")
            st.dataframe(
                corr_display.style.background_gradient(cmap="coolwarm"),
                use_container_width=True
            )

        st.subheader("Images analytiques")
        for img_name, caption in [
            ("corr_heatmap.png", "Heatmap des corrélations"),
            ("corr_clustermap.png", "Clustermap des variables"),
            ("corr_with_duration_bar.png", "Corrélations avec la durée")
        ]:
            img_path = output_dir / img_name
            if img_path.exists():
                st.image(str(img_path), caption=caption, use_column_width=True)

    with right_col:
        if features_df is not None:
            st.subheader("Aperçu des features de run")
            st.write("Affichage des premières lignes du fichier `run_level_features.csv`.")
            st.dataframe(features_df.head(10), use_container_width=True)

        if scores_df is not None:
            st.subheader("Aperçu des scores")
            st.write("Voici quelques runs du fichier `run_scores.csv`.")
            st.dataframe(scores_df.head(10), use_container_width=True)

    with st.expander("Voir les détails des données brutes"):
        if corr_df is not None:
            st.markdown("**Matrice de corrélation**")
            st.dataframe(corr_display, use_container_width=True)
        if features_df is not None:
            st.markdown("**Features run-level**")
            st.dataframe(features_df, use_container_width=True)
        if scores_df is not None:
            st.markdown("**Scores des runs**")
            st.dataframe(scores_df, use_container_width=True)
