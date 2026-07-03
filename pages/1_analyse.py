import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from ui_theme import apply_isaac_theme, section, load_scores
from src.db import fetch_all

matplotlib.rcParams.update({
    "figure.facecolor": "#141010",
    "axes.facecolor": "#1c1414",
    "axes.edgecolor": "#b5191955",
    "axes.labelcolor": "#e8dcc8",
    "xtick.color": "#a08c7a",
    "ytick.color": "#a08c7a",
    "text.color": "#e8dcc8",
    "grid.color": "#b5191922",
    "grid.linestyle": "--",
})

ISAAC_PALETTE = ["#b51919", "#c9362e", "#d97b52", "#a08c7a", "#e8dcc8", "#8c1a1a"]
CMAP_ISAAC = "RdYlBu_r"

st.set_page_config(
    page_title="Analyse — Isaac Run Lab",
    page_icon="📈",
    layout="wide",
)
apply_isaac_theme()

st.markdown("# 📈 Analyse des runs")
st.markdown("---")

df = load_scores()

if df is None:
    st.error(
        "⚠️ Fichier `data/run_scores.csv` introuvable. "
        "Exécute le notebook `scoring_runs.ipynb` pour générer les données."
    )
    st.stop()

# ── Métriques ──────────────────────────────────────────────────────────────────
cols = st.columns(3)
cols[0].metric("Runs", f"{len(df):,}")
cols[1].metric("Score moyen", f"{df['score'].mean():.1f}")
cols[2].metric("Étage max atteint", f"{int(df['nb_stages'].max())}")

st.markdown("---")

# ── Onglets d'analyse ──────────────────────────────────────────────────────────
tab_dist, tab_stages, tab_corr, tab_custom = st.tabs([
    "🎲 Distribution des scores",
    "🗺️ Étages atteints",
    "🔗 Corrélations",
    "🔬 Exploration",
])

# ── 1. Distribution des scores ─────────────────────────────────────────────────
with tab_dist:
    section("Distribution des scores", "🎲")
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.histplot(df["score"], bins=15, kde=True, ax=ax,
                     color="#b51919", edgecolor="#5c0a0a", alpha=0.8)
        ax.set_xlabel("Score (/100)")
        ax.set_ylabel("Nombre de runs")
        ax.set_title("Distribution des scores de run")
        ax.axvline(df["score"].mean(), color="#d97b52", linestyle="--",
                   linewidth=1.5, label=f"Moyenne : {df['score'].mean():.1f}")
        ax.legend(facecolor="#241a17", edgecolor="#b51919", labelcolor="#e8dcc8")
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with c2:
        fig, ax = plt.subplots(figsize=(7, 4))
        grade_order = [g for g in ["S", "A", "B", "C", "D", "F"] if g in df["grade"].values]
        grade_counts = df["grade"].value_counts().reindex(grade_order).fillna(0)
        bars = ax.bar(grade_counts.index, grade_counts.values,
                      color=["#b51919", "#c9362e", "#d97b52", "#a08c7a", "#6b5c52", "#3a2e2b"],
                      edgecolor="#5c0a0a")
        ax.set_xlabel("Grade")
        ax.set_ylabel("Nombre de runs")
        ax.set_title("Répartition par grade")
        for bar, val in zip(bars, grade_counts.values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                        int(val), ha="center", va="bottom", color="#e8dcc8", fontsize=10)
        st.pyplot(fig, use_container_width=True)
        plt.close()

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.scatter(df["duration"], df["score"],
               c=df["score"], cmap=CMAP_ISAAC, alpha=0.8, edgecolors="#5c0a0a", s=70)
    ax.set_xlabel("Durée (frames)")
    ax.set_ylabel("Score")
    ax.set_title("Durée vs Score")
    st.pyplot(fig, use_container_width=True)
    plt.close()

# ── 2. Étages atteints ─────────────────────────────────────────────────────────
with tab_stages:
    section("Étages atteints", "🗺️")

    from ui_theme import FLOOR_NAMES

    fig, ax = plt.subplots(figsize=(10, 4))
    stage_counts = df["nb_stages"].value_counts().sort_index()
    bars = ax.bar(
        [FLOOR_NAMES.get(s, str(s)) for s in stage_counts.index],
        stage_counts.values,
        color="#b51919", edgecolor="#5c0a0a", alpha=0.85,
    )
    ax.set_xlabel("Étage final atteint")
    ax.set_ylabel("Nombre de runs")
    ax.set_title("Distribution des étages finals")
    plt.xticks(rotation=35, ha="right", fontsize=8)
    for bar, val in zip(bars, stage_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                int(val), ha="center", va="bottom", color="#e8dcc8", fontsize=9)
    st.pyplot(fig, use_container_width=True)
    plt.close()



    # Scatter nb_stages vs score
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.scatter(df["nb_stages"], df["score"], c="#b51919", alpha=0.8,
               edgecolors="#5c0a0a", s=80)
    ax.set_xlabel("Étages atteints (nb_stages)")
    ax.set_ylabel("Score")
    ax.set_title("Étages atteints vs Score")
    # Ligne de tendance
    z = np.polyfit(df["nb_stages"], df["score"], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df["nb_stages"].min(), df["nb_stages"].max(), 100)
    ax.plot(x_line, p(x_line), "--", color="#d97b52", linewidth=1.5, label="Tendance")
    ax.legend(facecolor="#241a17", edgecolor="#b51919", labelcolor="#e8dcc8")
    st.pyplot(fig, use_container_width=True)
    plt.close()

# ── 3. Corrélations ────────────────────────────────────────────────────────────
with tab_corr:
    section("Matrice de corrélation", "🔗")

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    # Exclure les colonnes trop bruitées ou de faible intérêt
    exclude = ["anomaly", "cluster", "rank", "raw_score"]
    corr_cols = [c for c in numeric_cols if c not in exclude]

    default_cols = [
        "score", "nb_stages", "clear_rate", "dps_proxy",
        "total_damage_taken", "nb_passive_items", "avg_passive_quality",
    ]
    default_cols = [c for c in default_cols if c in corr_cols]

    selected = st.multiselect(
        "Colonnes à inclure dans la heatmap",
        options=corr_cols,
        default=default_cols,
    )

    if len(selected) >= 2:
        corr = df[selected].corr()
        fig, ax = plt.subplots(figsize=(max(8, len(selected)), max(6, len(selected) - 1)))
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
        sns.heatmap(
            corr, annot=True, fmt=".2f", cmap=CMAP_ISAAC,
            ax=ax, linewidths=0.5, linecolor="#141010",
            vmin=-1, vmax=1,
        )
        ax.set_title("Corrélations entre métriques")
        st.pyplot(fig, use_container_width=True)
        plt.close()
    else:
        st.info("Sélectionne au moins 2 colonnes pour afficher la heatmap.")

# ── 4. Exploration libre ───────────────────────────────────────────────────────
with tab_custom:
    section("Exploration libre", "🔬")

    numeric_cols_clean = [c for c in df.select_dtypes(include=np.number).columns
                          if c not in ["anomaly", "cluster"]]

    col_a = st.selectbox("Axe X", numeric_cols_clean,
                         index=numeric_cols_clean.index("nb_stages") if "nb_stages" in numeric_cols_clean else 0)
    col_b = st.selectbox("Axe Y", numeric_cols_clean,
                         index=numeric_cols_clean.index("score") if "score" in numeric_cols_clean else 1)

    if col_a != col_b:
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.scatter(df[col_a], df[col_b], c="#b51919", alpha=0.8,
                   edgecolors="#5c0a0a", s=80)
        ax.set_xlabel(col_a)
        ax.set_ylabel(col_b)
        title = f"{col_b} vs {col_a}"
        ax.set_title(title)
        st.pyplot(fig, use_container_width=True)
        plt.close()

        corr_val = df[[col_a, col_b]].corr().iloc[0, 1]
        st.caption(f"Corrélation de Pearson entre **{col_a}** et **{col_b}** : `{corr_val:.3f}`")
    else:
        st.info("Sélectionne deux colonnes différentes.")

    st.markdown("---")
    with st.expander("Afficher les données brutes"):
        st.dataframe(df, use_container_width=True, hide_index=True)

