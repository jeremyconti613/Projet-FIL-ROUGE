"""
Script d'entraînement du modèle de prédiction d'étages.

Entraîne un modèle GradientBoostingRegressor sur les données de run_scores.csv
pour prédire nb_stages et sauvegarde le modèle en joblib.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from pathlib import Path

# Créer le dossier models s'il n'existe pas
MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODELS_DIR / "floor_predictor.joblib"
SCALER_PATH = MODELS_DIR / "feature_scaler.joblib"


def load_and_prepare_data(csv_path: str) -> tuple:
    """
    Charge les données de run_scores.csv et les prépare pour l'entraînement.
    
    Retourne
    --------
    X : features DataFrame
    y : target Series (nb_stages)
    feature_names : list of feature names
    """
    df = pd.read_csv(csv_path)
    
    # Exclure les colonnes qui ne sont pas des features utiles
    # ou qui pourraient créer du data leakage
    exclude_cols = {
        'run_id',           # identifiant
        'nb_stages',        # CIBLE
        'score',            # agrégat calculé après coup
        'rank',             # calculé après coup
        'grade',            # dérivé du score
        'raw_score',        # intermédiaire
        'anomaly',          # label calcul
        'anomaly_label',    # label calcul
        'cluster',          # label calcul
        'cluster_label',    # label calcul
    }
    
    available_features = [c for c in df.columns if c not in exclude_cols]
    
    # Vérifier que nb_stages existe
    if 'nb_stages' not in df.columns:
        raise ValueError("Colonne 'nb_stages' non trouvée dans le CSV")
    
    # Préparer X et y
    X = df[available_features].fillna(0)
    y = df['nb_stages']
    
    print(f"📊 Données chargées : {len(X)} runs, {len(available_features)} features")
    print(f"   Cible (nb_stages) : min={y.min()}, max={y.max()}, mean={y.mean():.2f}, std={y.std():.2f}")
    
    return X, y, available_features


def train_model(X: pd.DataFrame, y: pd.Series, feature_names: list) -> tuple:
    """
    Entraîne le modèle GradientBoostingRegressor.
    
    Retourne
    --------
    model : modèle entraîné
    scaler : StandardScaler entraîné
    metrics : dict avec les métriques d'évaluation
    """
    # Diviser train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scaler les features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Entraîner le modèle
    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=3,
        min_samples_leaf=1,
        random_state=42,
        subsample=0.8,
    )
    
    print("\n🎯 Entraînement du modèle GradientBoostingRegressor...")
    model.fit(X_train_scaled, y_train)
    
    # Évaluation
    y_pred = model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    # Cross-validation
    cv_scores = cross_val_score(
        GradientBoostingRegressor(
            n_estimators=100, learning_rate=0.1, max_depth=5,
            min_samples_split=3, min_samples_leaf=1, random_state=42, subsample=0.8,
        ),
        X_train_scaled, y_train, cv=5, scoring='r2'
    )
    
    metrics = {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'train_size': len(X_train),
        'test_size': len(X_test),
    }
    
    print(f"   ✓ R² Score : {r2:.4f}")
    print(f"   ✓ RMSE : {rmse:.4f} étages")
    print(f"   ✓ MAE : {mae:.4f} étages")
    print(f"   ✓ Cross-val (5-fold) : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    # Feature importance
    importances = model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    print(f"\n🔝 Top 10 features par importance :")
    for idx, row in feature_importance_df.head(10).iterrows():
        print(f"   {row['feature']:30s} : {row['importance']:.4f}")
    
    return model, scaler, metrics


def save_model(model, scaler):
    """Sauvegarde le modèle et le scaler."""
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"\n💾 Modèle sauvegardé : {MODEL_PATH}")
    print(f"   Scaler sauvegardé : {SCALER_PATH}")


if __name__ == "__main__":
    csv_path = Path(__file__).parent.parent / "data" / "run_scores.csv"
    
    if not csv_path.exists():
        print(f"❌ Fichier non trouvé : {csv_path}")
        exit(1)
    
    # Charger et préparer
    X, y, feature_names = load_and_prepare_data(str(csv_path))
    
    # Entraîner
    model, scaler, metrics = train_model(X, y, feature_names)
    
    # Sauvegarder
    save_model(model, scaler)
    
    print("\n✅ Modèle entraîné et sauvegardé avec succès !")
