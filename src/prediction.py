# src/prediction.py
#
# PLACEHOLDER — heuristique provisoire pour prédire l'étage final d'une run.
# Cette logique est volontairement isolée ici pour être remplacée facilement
# par un vrai modèle entraîné (cf. `src/scoring.py` pour la pipeline sklearn).
#
# Limites de l'heuristique actuelle :
#   - La plupart des features de run_scores.csv sont des agrégats *fin de run*
#     (final_*, clear_rate, nb_rooms…) → les utiliser pour prédire nb_stages
#     crée une fuite de données (data leakage) dans un vrai contexte ML.
#   - Avec 40 runs, un modèle entraîné serait de toute façon peu fiable.
#   - Cette implémentation sert uniquement de démonstration UI.
#
# Pour remplacer par un vrai modèle :
#   1. Entraîner un RandomForestRegressor / GradientBoostingRegressor
#      sur des features *early-game* (snapshot PlayerState au frame ~1000)
#      avec nb_stages comme cible.
#   2. Sérialiser avec joblib.dump(model, "models/floor_predictor.joblib").
#   3. Remplacer predict_final_floor() par un appel model.predict().

import pandas as pd
import numpy as np

# Nombre maximum d'étages théorique dans Isaac (The Void inclus)
MAX_FLOOR = 13

# Distribution réelle de nb_stages dans run_scores.csv
# (utilisée pour calibrer l'estimation générique)
_DEFAULT_MEAN_STAGES = 7.0
_DEFAULT_STD_STAGES = 2.0


def predict_final_floor(
    run_id: int,
    current_floor: int,
    scores_df: pd.DataFrame,
) -> dict:
    """
    PLACEHOLDER heuristique — prédit l'étage final estimé d'une run Isaac.

    Paramètres
    ----------
    run_id        : identifiant de la run (colonne run_id dans run_scores.csv)
    current_floor : étage actuel renseigné par l'utilisateur (1..MAX_FLOOR)
    scores_df     : DataFrame chargé depuis data/run_scores.csv

    Retourne
    --------
    dict avec les clés :
        predicted_floor : int   — étage final prédit
        low             : int   — borne basse de l'intervalle de confiance
        high            : int   — borne haute
        confidence      : str   — "Haute" / "Moyenne" / "Basse"
        rationale       : str   — explication lisible
        found_in_data   : bool  — True si run_id trouvé dans le dataset
        actual_nb_stages: int | None — nb_stages réel (si trouvé)
        score           : float | None
        grade           : str | None
        cluster_label   : str | None
        anomaly_label   : str | None
        victory         : int | None
    """
    run_row = scores_df[scores_df["run_id"] == run_id]
    found = not run_row.empty

    if found:
        r = run_row.iloc[0]
        score = float(r.get("score", 50.0) or 50.0)
        clear_rate = float(r.get("clear_rate", 0.8) or 0.8)
        actual_nb_stages = int(r.get("nb_stages", 0) or 0)

        # Heuristique :
        #   On projette un "potentiel restant" basé sur score et clear_rate.
        #   Plus le score est élevé et le taux de clear bon, plus on pense
        #   que la run peut aller loin.
        #   facteur = nb d'étages supplémentaires possibles normalisé entre 0..1
        remaining_potential = (score / 100.0) * (0.6 + 0.4 * clear_rate)
        max_reachable = MAX_FLOOR
        predicted = int(
            round(current_floor + remaining_potential * (max_reachable - current_floor))
        )
        predicted = max(current_floor, min(MAX_FLOOR, predicted))

        # Intervalle de confiance (±2 étages, borné)
        spread = max(1, round(2.0 * (1.0 - clear_rate) + 1))
        low = max(current_floor, predicted - spread)
        high = min(MAX_FLOOR, predicted + spread)

        # Confiance
        if score >= 60 and clear_rate >= 0.9:
            confidence = "Haute"
        elif score >= 35 and clear_rate >= 0.7:
            confidence = "Moyenne"
        else:
            confidence = "Basse"

        rationale = (
            f"Run #{run_id} — score {score:.1f}/100, "
            f"clear rate {clear_rate * 100:.1f}%"
        )

        return {
            "predicted_floor": predicted,
            "low": low,
            "high": high,
            "confidence": confidence,
            "rationale": rationale,
            "found_in_data": True,
            "actual_nb_stages": actual_nb_stages,
            "score": score,
            "grade": str(r.get("grade", "?")),
            "cluster_label": str(r.get("cluster_label", "?")),
            "anomaly_label": str(r.get("anomaly_label", "Normal")),
            "victory": int(r.get("victory", 0) or 0),
        }

    else:
        # Run inconnue — estimation générique basée sur l'étage courant
        # et la distribution du dataset
        mean_stages = scores_df["nb_stages"].mean() if len(scores_df) > 0 else _DEFAULT_MEAN_STAGES
        std_stages = scores_df["nb_stages"].std() if len(scores_df) > 0 else _DEFAULT_STD_STAGES

        # On ne peut pas faire mieux que la moyenne du dataset
        predicted = int(round(max(current_floor, min(MAX_FLOOR, mean_stages))))
        spread = max(2, int(round(std_stages)))
        low = max(current_floor, predicted - spread)
        high = min(MAX_FLOOR, predicted + spread)

        return {
            "predicted_floor": predicted,
            "low": low,
            "high": high,
            "confidence": "Basse",
            "rationale": (
                f"Run #{run_id} introuvable dans le dataset. "
                f"Estimation générique basée sur {len(scores_df)} runs connues "
                f"(moyenne : {mean_stages:.1f} étages)."
            ),
            "found_in_data": False,
            "actual_nb_stages": None,
            "score": None,
            "grade": None,
            "cluster_label": None,
            "anomaly_label": None,
            "victory": None,
        }
