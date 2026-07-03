# src/prediction.py
#
# Modèle ML entraîné pour prédire l'étage final d'une run.
# Utilise un GradientBoostingRegressor entraîné sur les données de run_scores.csv.
#
# Modèle : GradientBoostingRegressor
#   R² Score : 0.9510
#   RMSE : 0.5877 étages
#   MAE : 0.3451 étages
#   CV Score : 0.8856 ± 0.0703
#
# Principales features utilisées :
#   1. nb_monsters (importance: 0.2325)
#   2. nb_rooms (importance: 0.2214)
#   3. clear_rate (importance: 0.1782)
#   4. nb_rooms_cleared (importance: 0.1416)
#   5. nb_passive_items (importance: 0.1088)

import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# Nombre maximum d'étages théorique dans Isaac (The Void inclus)
MAX_FLOOR = 13

# Charger le modèle et le scaler
_MODEL_PATH = Path(__file__).parent.parent / "models" / "floor_predictor.joblib"
_SCALER_PATH = Path(__file__).parent.parent / "models" / "feature_scaler.joblib"

try:
    _MODEL = joblib.load(_MODEL_PATH)
    _SCALER = joblib.load(_SCALER_PATH)
    _MODEL_LOADED = True
except Exception as e:
    print(f"⚠️  Impossible de charger le modèle : {e}")
    _MODEL_LOADED = False

# Distribution réelle de nb_stages dans run_scores.csv
# (utilisée pour l'estimation générique si le modèle n'est pas chargé)
_DEFAULT_MEAN_STAGES = 7.0
_DEFAULT_STD_STAGES = 2.0


def predict_final_floor(
    run_id: int,
    current_floor: int,
    scores_df: pd.DataFrame,
) -> dict:
    """
    Prédit l'étage final estimé d'une run Isaac avec le modèle ML entraîné.

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
    if not _MODEL_LOADED:
        return _fallback_prediction(run_id, current_floor, scores_df)
    
    run_row = scores_df[scores_df["run_id"] == run_id]
    found = not run_row.empty

    if found:
        r = run_row.iloc[0]
        actual_nb_stages = int(r.get("nb_stages", 0) or 0)
        score = float(r.get("score", 50.0) or 50.0)
        
        # Préparer les features pour le modèle
        feature_cols = _SCALER.get_feature_names_out() if hasattr(_SCALER, 'get_feature_names_out') else None
        
        # Récupérer toutes les features pour la run
        exclude_cols = {
            'run_id', 'nb_stages', 'score', 'rank', 'grade', 'raw_score',
            'anomaly', 'anomaly_label', 'cluster', 'cluster_label',
        }
        available_features = [c for c in scores_df.columns if c not in exclude_cols]
        
        # Préparer les données d'entrée pour le modèle
        X_input = scores_df[scores_df["run_id"] == run_id][available_features].fillna(0)
        if len(X_input) > 0:
            X_scaled = _SCALER.transform(X_input)
            predicted_stages = float(_MODEL.predict(X_scaled)[0])
        else:
            predicted_stages = current_floor
        
        # Cliper la prédiction entre current_floor et MAX_FLOOR
        predicted_stages = max(current_floor, min(MAX_FLOOR, predicted_stages))
        predicted = int(round(predicted_stages))
        
        # Intervalle de confiance basé sur RMSE du modèle (0.5877)
        # ±1.96 * RMSE ≈ ±1.15 étages (95% CI)
        spread = max(1, int(round(1.96 * 0.5877)))  # ~1 étage
        low = max(current_floor, predicted - spread)
        high = min(MAX_FLOOR, predicted + spread)
        
        # Confiance basée sur score et anomaly
        anomaly = str(r.get("anomaly_label", "Normal"))
        if score >= 70 and anomaly == "Normal":
            confidence = "Haute"
        elif score >= 50 or anomaly != "Normal":
            confidence = "Moyenne"
        else:
            confidence = "Basse"

        rationale = (
            f"Run #{run_id} — score {score:.1f}/100. "
            f"Prédiction ML : {predicted_stages:.1f} étages "
            f"(R² = 0.951, RMSE = 0.59 étages)"
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
        # Run inconnue — utiliser le modèle avec des features moyennes
        return _predict_unknown_run(current_floor, scores_df)


def _predict_unknown_run(current_floor: int, scores_df: pd.DataFrame) -> dict:
    """Prédit pour une run inconnue en utilisant les features moyennes du dataset."""
    if not _MODEL_LOADED or len(scores_df) == 0:
        return _fallback_prediction(-1, current_floor, scores_df)
    
    # Utiliser les features moyennes du dataset
    exclude_cols = {
        'run_id', 'nb_stages', 'score', 'rank', 'grade', 'raw_score',
        'anomaly', 'anomaly_label', 'cluster', 'cluster_label',
    }
    available_features = [c for c in scores_df.columns if c not in exclude_cols]
    
    # Calculer les moyennes
    X_mean = scores_df[available_features].fillna(0).mean().values.reshape(1, -1)
    
    try:
        X_scaled = _SCALER.transform(X_mean)
        predicted_stages = float(_MODEL.predict(X_scaled)[0])
    except Exception:
        predicted_stages = scores_df["nb_stages"].mean() if len(scores_df) > 0 else _DEFAULT_MEAN_STAGES
    
    predicted_stages = max(current_floor, min(MAX_FLOOR, predicted_stages))
    predicted = int(round(predicted_stages))
    
    spread = 2
    low = max(current_floor, predicted - spread)
    high = min(MAX_FLOOR, predicted + spread)
    
    mean_stages = scores_df["nb_stages"].mean() if len(scores_df) > 0 else _DEFAULT_MEAN_STAGES
    
    return {
        "predicted_floor": predicted,
        "low": low,
        "high": high,
        "confidence": "Basse",
        "rationale": (
            f"Run inconnue. Prédiction basée sur les features moyennes du dataset "
            f"({len(scores_df)} runs). Résultat : {predicted_stages:.1f} étages en moyenne."
        ),
        "found_in_data": False,
        "actual_nb_stages": None,
        "score": None,
        "grade": None,
        "cluster_label": None,
        "anomaly_label": None,
        "victory": None,
    }


def _fallback_prediction(run_id: int, current_floor: int, scores_df: pd.DataFrame) -> dict:
    """Estimation générique basée sur le dataset quand le modèle n'est pas disponible."""
    run_row = scores_df[scores_df["run_id"] == run_id] if run_id > 0 else pd.DataFrame()
    found = not run_row.empty

    if found:
        r = run_row.iloc[0]
        score = float(r.get("score", 50.0) or 50.0)
        clear_rate = float(r.get("clear_rate", 0.8) or 0.8)
        actual_nb_stages = int(r.get("nb_stages", 0) or 0)

        # Heuristique simple basée sur score et clear_rate
        remaining_potential = (score / 100.0) * (0.6 + 0.4 * clear_rate)
        predicted = int(
            round(current_floor + remaining_potential * (MAX_FLOOR - current_floor))
        )
        predicted = max(current_floor, min(MAX_FLOOR, predicted))

        spread = max(1, round(2.0 * (1.0 - clear_rate) + 1))
        low = max(current_floor, predicted - spread)
        high = min(MAX_FLOOR, predicted + spread)

        if score >= 60 and clear_rate >= 0.9:
            confidence = "Haute"
        elif score >= 35 and clear_rate >= 0.7:
            confidence = "Moyenne"
        else:
            confidence = "Basse"

        rationale = (
            f"Run #{run_id} — score {score:.1f}/100, clear rate {clear_rate * 100:.1f}%. "
            f"⚠️ Modèle ML indisponible, heuristique utilisée."
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
        # Run inconnue — estimation générique
        mean_stages = scores_df["nb_stages"].mean() if len(scores_df) > 0 else _DEFAULT_MEAN_STAGES
        std_stages = scores_df["nb_stages"].std() if len(scores_df) > 0 else _DEFAULT_STD_STAGES

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
                f"Run #{run_id} introuvable. Estimation générique basée sur {len(scores_df)} runs "
                f"(moyenne : {mean_stages:.1f} étages). ⚠️ Modèle ML indisponible."
            ),
            "found_in_data": False,
            "actual_nb_stages": None,
            "score": None,
            "grade": None,
            "cluster_label": None,
            "anomaly_label": None,
            "victory": None,
        }
