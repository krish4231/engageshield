"""
ML Training Pipeline for EngageShield.
Trains an XGBoost classifier on synthetic engagement data.

Usage:
    python -m ml.train_model
"""

import json
import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.detection.ml_engine.features import extract_features, FEATURE_NAMES
from ml.data.synthetic_generator import SyntheticDataGenerator


def train_model(output_path: str = "ml/models/xgboost_model.joblib"):
    """Full training pipeline."""
    print("=" * 60)
    print("EngageShield ML Training Pipeline")
    print("=" * 60)

    # 1. Generate training data
    print("\n[1/5] Generating synthetic training data...")
    gen = SyntheticDataGenerator(seed=42)
    data = gen.generate(
        num_normal_users=500,
        num_bot_users=150,
        num_coordinated_groups=5,
        coord_group_size=20,
    )
    labels = data["labels"]
    engagements = data["engagements"]
    print(f"  Generated {len(engagements)} engagements from {len(labels)} users")

    # 2. Extract features per user
    print("\n[2/5] Extracting features...")
    user_engagements = {}
    for eng in engagements:
        uid = eng["source_user_id"]
        if uid not in user_engagements:
            user_engagements[uid] = []
        user_engagements[uid].append(eng)

    X_data = []
    y_data = []
    for uid, user_engs in user_engagements.items():
        features = extract_features(user_engs, uid)
        feature_vector = [features.get(f, 0) for f in FEATURE_NAMES]
        X_data.append(feature_vector)
        y_data.append(1 if labels.get(uid) == "fake" else 0)

    X = np.array(X_data)
    y = np.array(y_data)
    print(f"  Feature matrix: {X.shape}")
    print(f"  Class distribution: {sum(y == 0)} legitimate, {sum(y == 1)} fake")

    # 3. Split data
    print("\n[3/5] Splitting data (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {X_train.shape[0]} samples")
    print(f"  Test: {X_test.shape[0]} samples")

    # 4. Train model
    print("\n[4/5] Training XGBoost classifier...")
    try:
        from xgboost import XGBClassifier
        model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="logloss",
            use_label_encoder=False,
        )
    except ImportError:
        print("  XGBoost not available, falling back to Random Forest...")
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
        )

    model.fit(X_train, y_train)

    # 5. Evaluate
    print("\n[5/5] Evaluating model...")
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Fake"]))

    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  TN={cm[0][0]}  FP={cm[0][1]}")
    print(f"  FN={cm[1][0]}  TP={cm[1][1]}")

    auc = roc_auc_score(y_test, y_proba)
    print(f"\nROC AUC Score: {auc:.4f}")

    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="f1")
    print(f"Cross-validation F1: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")

    # Feature importances
    if hasattr(model, 'feature_importances_'):
        print("\nFeature Importances:")
        importances = list(zip(FEATURE_NAMES, model.feature_importances_))
        importances.sort(key=lambda x: x[1], reverse=True)
        for name, imp in importances:
            bar = "█" * int(imp * 50)
            print(f"  {name:30s} {imp:.4f} {bar}")

    # Save model
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(model, output_path)
    print(f"\nModel saved to {output_path}")
    print("=" * 60)

    return model


if __name__ == "__main__":
    train_model()
