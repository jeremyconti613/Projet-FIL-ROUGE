import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from ui_theme import apply_isaac_theme, section, load_scores
from src.db import fetch_playerstates, fetch_stages, fetch_rooms

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
COLOR_A = "#b51919"
COLOR_B = "#d97b52"

st.set_page_config(
    page_title="Comparaison — Isaac Run Lab",
    page_icon="⚔️",
    layout="wide",
)
apply_isaac_theme()

st.markdown("# ⚔️ Comparaison de runs")
st.markdown("---")

df = load_scores()

if df is None:
    st.error(
        "⚠️ Fichier `data/run_scores.csv` introuvable. "
        "Exécute le notebook `scoring_runs.ipynb` pour générer les données."
    )
    st.stop()

# ── Sélection des 2 runs ────────────────────────────────────────────────────────
section("Sélection des runs", "🎮")

available_ids = sorted(df["run_id"].astype(int).tolist())

c1, c2 = st.columns(2)
run_a = c1.selectbox(
    "Run A", available_ids, index=0, format_func=lambda x: f"Run #{x}", key="run_a"
)
run_b = c2.selectbox(
    "Run B",
    available_ids,
    index=min(1, len(available_ids) - 1),
    format_func=lambda x: f"Run #{x}",
    key="run_b",
)

if run_a == run_b:
    st.warning("⚠️ Sélectionne deux runs différentes pour une comparaison utile.")

row_a = df[df["run_id"] == run_a].iloc[0]
row_b = df[df["run_id"] == run_b].iloc[0]

st.markdown("---")

# ── Bandeau de métriques finales ────────────────────────────────────────────────
section("Métriques finales", "📊")

m1, m2, m3, m4 = st.columns(4)
m1.metric(f"Score — Run #{run_b}", f"{row_b['score']:.1f}",
          delta=f"{row_b['score'] - row_a['score']:+.1f} vs #{run_a}")
m2.metric(f"Étages — Run #{run_b}", f"{int(row_b['nb_stages'])}",
          delta=f"{int(row_b['nb_stages'] - row_a['nb_stages']):+d} vs #{run_a}")
m3.metric(f"Clear rate — Run #{run_b}", f"{row_b['clear_rate'] * 100:.1f}%",
          delta=f"{(row_b['clear_rate'] - row_a['clear_rate']) * 100:+.1f} pts vs #{run_a}")
m4.metric(f"DPS proxy — Run #{run_b}", f"{row_b['dps_proxy']:.2f}",
          delta=f"{row_b['dps_proxy'] - row_a['dps_proxy']:+.2f} vs #{run_a}")

with st.expander("Voir toutes les métriques finales des 2 runs"):
    compare_df = pd.DataFrame({
        f"Run #{run_a}": row_a,
        f"Run #{run_b}": row_b,
    })
    st.dataframe(compare_df, use_container_width=True)

st.markdown("---")

# ── Chargement des relevés PlayerState / Stage / Room ───────────────────────────
section("Évolution détaillée (par étage ou par room)", "📈")

st.caption(
    "Comparaison de l'évolution des métriques, agrégée par étage ou par room "
    "— plus lisible et plus comparable entre 2 runs que le relevé brut par frame."
)


@st.cache_data(show_spinner="Chargement des PlayerStates…")
def load_series(run_id: int) -> pd.DataFrame:
    return fetch_playerstates(int(run_id))


@st.cache_data(show_spinner="Chargement des étages/rooms…")
def load_structure(run_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    return fetch_stages(int(run_id)), fetch_rooms(int(run_id))


try:
    series_a = load_series(run_a)
    series_b = load_series(run_b)
    stages_a, rooms_a = load_structure(run_a)
    stages_b, rooms_b = load_structure(run_b)
except Exception as e:
    st.warning(
        "⚠️ Impossible de charger les données depuis Supabase "
        f"(base indisponible ou identifiants manquants dans `.env`). Détail : {e}"
    )
    st.stop()

if series_a.empty or series_b.empty:
    empty_runs = [f"#{r}" for r, s in [(run_a, series_a), (run_b, series_b)] if s.empty]
    st.warning(
        f"⚠️ Aucun relevé `PlayerState` trouvé pour la run {', '.join(empty_runs)}. "
        "L'évolution ne peut pas être affichée pour cette sélection."
    )
    st.stop()

# Colonnes candidates pour l'évolution (mêmes stats que src/features.py)
CANDIDATE_METRICS = [
    "Damage", "FireDelay", "ShotSpeed", "TearRange", "MoveSpeed", "Luck",
    "Hearts", "SoulHearts", "BlackHearts", "Coins", "Bombs", "Keys", "DamageTaken",
]
available_metrics = [
    c for c in CANDIDATE_METRICS
    if c in series_a.columns and c in series_b.columns
]

if not available_metrics:
    st.warning("⚠️ Aucune métrique temporelle exploitable trouvée dans `PlayerState`.")
    st.stop()

metric = st.selectbox("Métrique à comparer", available_metrics)

table_view = st.radio(
    "Niveau de détail",
    ["Par étage", "Par room (au sein d'un étage)"],
    horizontal=True,
    key="table_view",
)


def last_value_per_group(series: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Dernière valeur (par Frame) de value_col, pour chaque groupe (id_stage ou id_room)."""
    s = series[["Frame", group_col, value_col]].dropna(subset=[group_col])
    s[value_col] = pd.to_numeric(s[value_col], errors="coerce")
    return s.sort_values("Frame").groupby(group_col).last().reset_index()


def plot_curves(x_a, y_a, x_b, y_b, xlabel: str, title: str) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(x_a, y_a, color=COLOR_A, linewidth=2, marker="o", markersize=4, label=f"Run #{run_a}")
    ax.plot(x_b, y_b, color=COLOR_B, linewidth=2, marker="o", markersize=4, label=f"Run #{run_b}")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(metric)
    ax.set_title(title)
    ax.legend(facecolor="#241a17", edgecolor="#b51919", labelcolor="#e8dcc8")
    st.pyplot(fig, use_container_width=True)
    plt.close()


if table_view == "Par étage":
    if stages_a.empty and stages_b.empty:
        st.info("Aucune donnée d'étage disponible pour ces runs.")
    else:
        last_a = last_value_per_group(series_a, "id_stage", metric)
        last_b = last_value_per_group(series_b, "id_stage", metric)

        tbl_a = (
            stages_a[["id", "StageNumber", "StageName", "Curses"]]
            .merge(last_a, left_on="id", right_on="id_stage", how="left")
            .rename(columns={"StageName": f"Nom (Run #{run_a})", metric: f"{metric} (Run #{run_a})"})
            [["StageNumber", f"Nom (Run #{run_a})", f"{metric} (Run #{run_a})"]]
        )
        tbl_b = (
            stages_b[["id", "StageNumber", "StageName", "Curses"]]
            .merge(last_b, left_on="id", right_on="id_stage", how="left")
            .rename(columns={"StageName": f"Nom (Run #{run_b})", metric: f"{metric} (Run #{run_b})"})
            [["StageNumber", f"Nom (Run #{run_b})", f"{metric} (Run #{run_b})"]]
        )

        merged = tbl_a.merge(tbl_b, on="StageNumber", how="outer").sort_values("StageNumber")
        merged[f"Δ {metric}"] = (
            merged[f"{metric} (Run #{run_b})"] - merged[f"{metric} (Run #{run_a})"]
        )

        curve_a = merged.dropna(subset=[f"{metric} (Run #{run_a})"])
        curve_b = merged.dropna(subset=[f"{metric} (Run #{run_b})"])
        plot_curves(
            curve_a["StageNumber"], curve_a[f"{metric} (Run #{run_a})"],
            curve_b["StageNumber"], curve_b[f"{metric} (Run #{run_b})"],
            xlabel="Étage", title=f"Évolution de {metric} par étage",
        )

        merged = merged.rename(columns={"StageNumber": "Étage"})
        st.dataframe(merged, use_container_width=True, hide_index=True)

else:
    stage_numbers = sorted(
        set(stages_a["StageNumber"].tolist() if not stages_a.empty else [])
        | set(stages_b["StageNumber"].tolist() if not stages_b.empty else [])
    )
    if not stage_numbers:
        st.info("Aucun étage disponible pour ces runs.")
    else:
        selected_stage = st.selectbox("Étage à explorer", stage_numbers)

        room_tables = {}
        for run_label, stages_df, rooms_df, series_df in [
            (run_a, stages_a, rooms_a, series_a),
            (run_b, stages_b, rooms_b, series_b),
        ]:
            stage_row = stages_df[stages_df["StageNumber"] == selected_stage] if not stages_df.empty else pd.DataFrame()
            if stage_row.empty:
                room_tables[run_label] = pd.DataFrame()
                continue

            id_stage = stage_row.iloc[0]["id"]
            stage_rooms = rooms_df[rooms_df["id_stage"] == id_stage].sort_values("EnterFrame")
            last_by_room = last_value_per_group(series_df, "id_room", metric)

            room_tbl = (
                stage_rooms[["id", "RoomIndex", "RoomTypeName", "Cleared", "ClearDurationFrames"]]
                .merge(last_by_room, left_on="id", right_on="id_room", how="left")
                .rename(columns={"RoomTypeName": "Type de room"})
                [["RoomIndex", "Type de room", "Cleared", "ClearDurationFrames", metric]]
                .reset_index(drop=True)
            )
            room_tbl.insert(0, "Ordre de visite", range(1, len(room_tbl) + 1))
            room_tables[run_label] = room_tbl

        tbl_a, tbl_b = room_tables[run_a], room_tables[run_b]

        if tbl_a.empty and tbl_b.empty:
            st.info(f"Étage {selected_stage} non atteint par les 2 runs.")
        else:
            curve_a = tbl_a.dropna(subset=[metric]) if not tbl_a.empty else tbl_a
            curve_b = tbl_b.dropna(subset=[metric]) if not tbl_b.empty else tbl_b
            plot_curves(
                curve_a["Ordre de visite"] if not curve_a.empty else [],
                curve_a[metric] if not curve_a.empty else [],
                curve_b["Ordre de visite"] if not curve_b.empty else [],
                curve_b[metric] if not curve_b.empty else [],
                xlabel=f"Room visitée (ordre chronologique) — étage {selected_stage}",
                title=f"Évolution de {metric} par room",
            )

        room_cols = st.columns(2)
        for col, run_label, room_tbl in [(room_cols[0], run_a, tbl_a), (room_cols[1], run_b, tbl_b)]:
            with col:
                st.markdown(f"**Run #{run_label}**")
                if room_tbl.empty:
                    st.info(f"Étage {selected_stage} non atteint par cette run.")
                else:
                    st.dataframe(room_tbl, use_container_width=True, hide_index=True)

with st.expander("Voir les relevés bruts par frame (PlayerState)"):
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"**Run #{run_a}**")
        st.dataframe(series_a, use_container_width=True, hide_index=True)
    with d2:
        st.markdown(f"**Run #{run_b}**")
        st.dataframe(series_b, use_container_width=True, hide_index=True)
