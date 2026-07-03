# src/scoring.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans


def compute_scores(df_features: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Calcule un score normalisé entre 0 et 100 pour chaque run
    à partir des features et de la configuration de pondération.
    """
    df        = df_features.copy()
    config    = {c: cfg for c, cfg in config.items() if c != "victory"}
    available = [c for c in config.keys() if c in df.columns]
    missing   = [c for c in config.keys() if c not in df.columns]

    if missing:
        print(f"⚠️  Colonnes absentes ignorées : {missing}")

    df_feat = df[available].fillna(0)

    scaler  = MinMaxScaler()
    df_norm = pd.DataFrame(
        scaler.fit_transform(df_feat),
        columns=available,
        index=df.index
    )

    total_weight = sum(config[c]["weight"] for c in available)
    score        = pd.Series(0.0, index=df.index)

    for col in available:
        direction = config[col]["direction"]
        weight    = config[col]["weight"]
        col_vals  = df_norm[col]

        if direction == -1:
            col_vals = 1 - col_vals

        score += col_vals * weight

    df["raw_score"] = score
    df["score"]     = (score / total_weight * 100).round(2)
    df["rank"]      = df["score"].rank(ascending=False, method="min").astype(int)
    df["grade"]     = pd.cut(
        df["score"],
        bins=[0, 20, 40, 60, 75, 90, 100],
        labels=["F", "D", "C", "B", "A", "S"],
        include_lowest=True
    )

    return df.sort_values("score", ascending=False)


def ml_enrichment(
    df_scored: pd.DataFrame,
    config: dict,
    n_clusters: int = 4
) -> pd.DataFrame:
    """
    Enrichit le scoring avec :
    - Isolation Forest : détection de runs exceptionnelles
    - KMeans           : regroupement en profils de runs
    """
    feature_cols = [c for c in config.keys() if c in df_scored.columns]
    df_ml        = df_scored[feature_cols].fillna(0)

    scaler = StandardScaler()
    X      = scaler.fit_transform(df_ml)

    # Isolation Forest
    iso                      = IsolationForest(contamination=0.05, random_state=42)
    df_scored["anomaly"]     = iso.fit_predict(X)
    df_scored["anomaly_label"] = df_scored["anomaly"].map({
        1: "Normal", -1: "⚡ Exceptionnelle"
    })

    # KMeans
    kmeans               = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_scored["cluster"] = kmeans.fit_predict(X)

    cluster_scores = (
        df_scored.groupby("cluster")["score"]
        .mean()
        .sort_values(ascending=False)
    )
    cluster_labels = {
        cid: label for cid, label in zip(
            cluster_scores.index,
            ["🏆 Elite", "⭐ Solide", "📈 Moyenne", "💀 Difficile"][:n_clusters]
        )
    }
    df_scored["cluster_label"] = df_scored["cluster"].map(cluster_labels)

    print("\n🔍 Répartition des clusters :")
    print(
        df_scored
        .groupby("cluster_label")["score"]
        .agg(["count", "mean", "min", "max"])
        .round(2)
    )

    return df_scored


def print_run_report(df_scored: pd.DataFrame, run_id: int) -> None:
    """Affiche un rapport détaillé pour une run spécifique."""
    row = df_scored[df_scored["run_id"] == run_id]

    if row.empty:
        print(f"❌ Run {run_id} introuvable.")
        return

    r = row.iloc[0]
    print(f"""
╔══════════════════════════════════════════╗
║         RAPPORT DE RUN #{run_id:<6}          ║
╠══════════════════════════════════════════╣
║  Score        : {r['score']:.1f}/100  [{r['grade']}]
║  Classement   : #{int(r['rank'])} / {len(df_scored)}
║  Profil       : {r.get('cluster_label', 'N/A')}
║  Statut       : {r.get('anomaly_label', 'Normal')}
╠══════════════════════════════════════════╣
║  Victoire     : {'✅' if r.get('victory') else '❌'}
║  Stages       : {int(r.get('nb_stages', 0))}
║  Rooms clear  : {r.get('clear_rate', 0) * 100:.1f}%
║  DPS proxy    : {r.get('dps_proxy', 0):.2f}
║  Dégâts reçus : {int(r.get('total_damage_taken', 0))}
║  Items passifs: {int(r.get('nb_passive_items', 0))} (qualité moy: {r.get('avg_passive_quality', 0):.1f})
║  Malédictions : {int(r.get('nb_curses', 0))}
╚══════════════════════════════════════════╝
    """)
