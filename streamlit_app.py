import streamlit as st
import pandas as pd
from ui_theme import apply_isaac_theme, hero, section, load_scores, floor_name

st.set_page_config(
    page_title="Isaac Run Lab",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_isaac_theme()

# ── Hero ───────────────────────────────────────────────────────────────────────
hero(
    title="Isaac Run Lab",
    subtitle=(
        "Analyse et scoring de runs <em>The Binding of Isaac</em> — "
        "visualise tes performances, explore les corrélations, "
        "et prédit jusqu'où ira ta prochaine run."
    ),
)

# ── Chargement des données ─────────────────────────────────────────────────────
df = load_scores()

if df is None:
    st.error(
        "⚠️ Fichier `data/run_scores.csv` introuvable. "
        "Exécute le notebook `scoring_runs.ipynb` pour générer les données."
    )
    st.stop()

# ── Métriques globales ─────────────────────────────────────────────────────────
section("Vue d'ensemble", "📊")

best_run = df.loc[df["score"].idxmax()]
cols = st.columns(4)
cols[0].metric("Runs analysées", f"{len(df):,}")
cols[1].metric("Score moyen", f"{df['score'].mean():.1f} / 100")
cols[2].metric("Étage moyen atteint", f"{df['nb_stages'].mean():.1f}")
cols[3].metric(
    "Meilleure run",
    f"#{int(best_run['run_id'])} — {best_run['score']:.1f}",
    delta=f"Grade {best_run['grade']}",
)

st.markdown("---")

# ── Meilleures runs ────────────────────────────────────────────────────────────
section("Top runs", "🏆")

top_cols = st.columns([2, 1])

with top_cols[0]:
    top_n = st.slider("Nombre de runs à afficher", min_value=5, max_value=len(df), value=10, step=5)
    top_df = (
        df[["run_id", "score", "grade", "nb_stages",
            "clear_rate", "dps_proxy", "cluster_label", "anomaly_label"]]
        .sort_values("score", ascending=False)
        .head(top_n)
        .rename(columns={
            "run_id": "Run ID",
            "score": "Score",
            "grade": "Grade",
            "nb_stages": "Étages",
            "clear_rate": "Clear rate",
            "dps_proxy": "DPS proxy",
            "cluster_label": "Profil",
            "anomaly_label": "Statut",
        })
    )
    top_df["Clear rate"] = (top_df["Clear rate"] * 100).round(1).astype(str) + "%"
    top_df["DPS proxy"] = top_df["DPS proxy"].round(2)
    st.dataframe(top_df, use_container_width=True, hide_index=True)

with top_cols[1]:
    st.markdown("### Distribution des grades")
    grade_counts = df["grade"].value_counts().reindex(["S", "A", "B", "C", "D", "F"]).dropna()
    grade_df = grade_counts.reset_index()
    grade_df.columns = ["Grade", "Nombre"]
    st.dataframe(grade_df, use_container_width=True, hide_index=True)

    st.markdown("### Profils de runs")
    cluster_counts = df["cluster_label"].value_counts().reset_index()
    cluster_counts.columns = ["Profil", "Nombre"]
    st.dataframe(cluster_counts, use_container_width=True, hide_index=True)

st.markdown("---")

# ── Détail d'une run ───────────────────────────────────────────────────────────
section("Détail d'une run", "🔍")

available_ids = sorted(df["run_id"].astype(int).tolist())
run_id_input = st.selectbox(
    "Sélectionner une run",
    options=available_ids,
    format_func=lambda x: f"Run #{x}",
)

row = df[df["run_id"] == run_id_input]
if not row.empty:
    r = row.iloc[0]
    d1, d2, d3 = st.columns(3)
    d1.metric("Score", f"{r['score']:.1f}")
    d2.metric("Grade", str(r["grade"]))
    d3.metric("Étages atteints", int(r["nb_stages"]))

    d5, d6, d7, d8 = st.columns(4)
    d5.metric("Profil", str(r["cluster_label"]))
    d6.metric("Statut", str(r["anomaly_label"]))
    d7.metric("DPS proxy", f"{r['dps_proxy']:.2f}")
    d8.metric("Clear rate", f"{r['clear_rate'] * 100:.1f}%")

    with st.expander("Voir toutes les statistiques de la run"):
        detail = r.to_frame("Valeur").copy()
        st.dataframe(detail, use_container_width=True)
