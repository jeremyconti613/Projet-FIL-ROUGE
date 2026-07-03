import streamlit as st
from ui_theme import apply_isaac_theme, section, load_scores, floor_name, floor_icon, MAX_FLOOR, FLOOR_NAMES
from src.prediction import predict_final_floor

st.set_page_config(
    page_title="Prédiction — Isaac Run Lab",
    page_icon="🔮",
    layout="wide",
)
apply_isaac_theme()

st.markdown("# 🔮 Prédiction d'étage")
st.markdown("---")

# ── Info modèle ML ─────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="isaac-card" style="border-left: 4px solid #3a8c3a; padding: 12px 16px;">
    <p style="margin:0; font-size:0.9rem;"><strong>✅ Modèle ML entraîné</strong> — 
    GradientBoosting · R² = 0.951 · RMSE = 0.59 étages · 60 runs</p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Chargement des données ─────────────────────────────────────────────────────
df = load_scores()
if df is None:
    st.error(
        "⚠️ Fichier `data/run_scores.csv` introuvable. "
        "Exécute le notebook `scoring_runs.ipynb` pour générer les données."
    )
    st.stop()

available_ids = sorted(df["run_id"].astype(int).tolist())

# ── Formulaire de saisie ───────────────────────────────────────────────────────
section("Paramètres de la run", "🎮")

col_form, col_hint = st.columns([2, 1])

with col_form:
    run_id_input = st.number_input(
        "Run ID",
        min_value=1,
        max_value=999999,
        value=21,
        step=1,
        help="Identifiant de la run (colonne run_id dans run_scores.csv)",
    )

    # Slider avec noms d'étages
    floor_options = list(range(1, MAX_FLOOR + 1))
    floor_labels = [f"{n} — {floor_name(n)}" for n in floor_options]

    current_floor_label = st.select_slider(
        "Étage actuel de la run",
        options=floor_labels,
        value=floor_labels[2],  # Caves I par défaut
        help="Étage où se trouve le joueur au moment de la prédiction",
    )
    # Extraction du numéro d'étage depuis le label
    current_floor = int(current_floor_label.split(" — ")[0])

    predict_btn = st.button("🔮 Prédire l'étage final", use_container_width=True)

with col_hint:
    st.markdown("### Runs disponibles")
    st.caption(
        f"{len(available_ids)} runs dans le dataset. "
        "Renseigne un ID existant pour une prédiction personnalisée, "
        "ou un ID inconnu pour une estimation générique."
    )
    st.dataframe(
        df[["run_id", "score", "grade", "nb_stages"]]
        .sort_values("score", ascending=False)
        .rename(columns={"run_id": "ID", "score": "Score", "grade": "Grade", "nb_stages": "Étages"})
        .head(8),
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")

# ── Résultat ───────────────────────────────────────────────────────────────────
if predict_btn:
    section("Résultat de la prédiction", "🩸")

    result = predict_final_floor(int(run_id_input), current_floor, df)

    predicted = result["predicted_floor"]
    low = result["low"]
    high = result["high"]
    confidence = result["confidence"]

    # ── Affichage principal ────────────────────────────────────────────────────
    conf_color = {"Haute": "#3a8c3a", "Moyenne": "#c17c2a", "Basse": "#8c1a1a"}.get(confidence, "#8c1a1a")

    if result["found_in_data"]:
        st.success(f"✅ Run **#{int(run_id_input)}** trouvée dans le dataset.")
    else:
        st.warning(
            f"⚠️ Run **#{int(run_id_input)}** introuvable dans le dataset. "
            "Estimation générique appliquée."
        )

    # Carte principale
    st.markdown(
        f"""
<div class="isaac-card" style="text-align:center; padding: 24px;">
    <p style="color:#a08c7a; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px;">
        Run #{int(run_id_input)} — depuis l'étage {current_floor} ({floor_icon(current_floor)} {floor_name(current_floor)})
    </p>
    <p style="font-family:'VT323',monospace; font-size:1.2rem; color:#a08c7a; margin:4px 0;">
        atteindra l'étage
    </p>
    <p style="font-family:'VT323',monospace; font-size:4rem; color:#b51919;
              text-shadow: 2px 2px 0 #5c0a0a, 0 0 20px #b5191966; margin:0; line-height:1.1;">
        ~{predicted} / {MAX_FLOOR}
    </p>
    <p style="font-family:'VT323',monospace; font-size:1.6rem; color:#d97b52; margin:4px 0;">
        {floor_icon(predicted)} {floor_name(predicted)}
    </p>
    <p style="font-size:0.85rem; color:#a08c7a; margin-top:8px;">
        Intervalle : <strong style="color:#e8dcc8;">{low} — {high}</strong>
        &nbsp;|&nbsp;
        Confiance : <strong style="color:{conf_color};">{confidence}</strong>
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    # Barre de progression étage courant → étage prédit
    st.markdown("#### Progression estimée")

    prog_col1, prog_col2, prog_col3 = st.columns([1, 6, 1])
    with prog_col1:
        st.markdown(
            f"<div style='text-align:center; font-family:VT323,monospace; color:#a08c7a;'>"
            f"Étage<br><span style='font-size:1.5rem; color:#e8dcc8;'>{current_floor}</span></div>",
            unsafe_allow_html=True,
        )
    with prog_col2:
        # Barre de progression de current_floor à predicted, sur MAX_FLOOR
        progress_pct = predicted / MAX_FLOOR
        st.progress(progress_pct)
        st.caption(
            f"{floor_icon(current_floor)} {floor_name(current_floor)}  →  "
            f"{floor_icon(predicted)} {floor_name(predicted)}  "
            f"({predicted}/{MAX_FLOOR} étages)"
        )
    with prog_col3:
        st.markdown(
            f"<div style='text-align:center; font-family:VT323,monospace; color:#b51919;'>"
            f"Prédit<br><span style='font-size:1.5rem; color:#e8dcc8;'>{predicted}</span></div>",
            unsafe_allow_html=True,
        )

    # ── Détails de la run (si trouvée) ────────────────────────────────────────
    if result["found_in_data"]:
        st.markdown("---")
        section("Statistiques de la run", "📊")

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Score", f"{result['score']:.1f}")
        d2.metric("Grade", result["grade"])
        d3.metric("Étages réels", result["actual_nb_stages"])
        d4.metric("Profil", result["cluster_label"])

        # Comparaison prédit vs réel
        actual = result["actual_nb_stages"]
        if actual:
            diff = predicted - actual
            diff_str = (
                f"+{diff} étage{'s' if abs(diff) > 1 else ''} de plus que le réel"
                if diff > 0 else (
                    f"{diff} étage{'s' if abs(diff) > 1 else ''} de moins que le réel"
                    if diff < 0 else "égal au résultat réel 🎯"
                )
            )
            st.caption(
                f"ℹ️ Cette run est terminée — résultat réel : **{actual} étages**. "
                f"La prédiction est **{diff_str}**."
            )

    # ── Rationale ─────────────────────────────────────────────────────────────
    with st.expander("Voir l'explication de la prédiction"):
        st.markdown(f"**Prédiction :** {result['rationale']}")
        st.markdown(
            """
**Modèle utilisé :** GradientBoostingRegressor entraîné sur 60 runs

- **R² Score :** 0.951 (95% de la variance expliquée)
- **RMSE :** 0.59 étages (écart-type des erreurs)
- **MAE :** 0.35 étages (erreur absolue moyenne)
- **Cross-validation :** 0.8856 ± 0.0703

**Top features :**
1. Nombre de monstres (22.3%)
2. Nombre de salles (22.1%)
3. Taux de clear (17.8%)
4. Salles clairées (14.2%)
5. Items passifs (10.9%)

Voir `src/train_predictor.py` et `src/prediction.py` pour les détails.
            """
        )

else:
    # ── État initial — instructions ─────────────────────────────────────────
    st.markdown(
        """
<div class="isaac-card" style="text-align:center; padding:32px; opacity:0.7;">
    <p style="font-family:'VT323',monospace; font-size:2rem; color:#b51919;">
        🔮 En attente de prédiction
    </p>
    <p style="color:#a08c7a;">
        Renseigne un <strong style="color:#e8dcc8;">Run ID</strong> et un
        <strong style="color:#e8dcc8;">étage actuel</strong>, puis clique sur
        <em>Prédire l'étage final</em>.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )
