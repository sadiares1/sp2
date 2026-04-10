from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import time

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score
from sklearn.model_selection import KFold, StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.inspection import permutation_importance


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "ml_models"
MODEL_DIR.mkdir(exist_ok=True)

DATA_FILES = sorted(BASE_DIR.glob("*SyntheticData_updated.csv"))

NUMERIC_FEATURES = [
    "storage_temperature",
    "storage_relative_humidity",
    "storage_duration_months",
    "seed_moisture_content",
    "initial_viability",
    "germination_temperature",
    "germination_relative_humidity",
    "remaining_seed_stock",
]

CATEGORICAL_FEATURES = [
    "species",
    "packaging_type",
    "dormancy_type",
    "drying_method",
]

FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


# -------------------------------
# DATA LOADING
# -------------------------------
def load_dataset() -> pd.DataFrame:
    if not DATA_FILES:
        raise FileNotFoundError("No synthetic CSV files found.")

    frames = []
    for path in DATA_FILES:
        df = pd.read_csv(path)
        df["source_file"] = path.name
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)
    data.columns = [c.strip() for c in data.columns]
    return data


# -------------------------------
# CLEANING
# -------------------------------
def normalize_targets(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()

    data["viability_class"] = data["viability_class"].astype(str).str.lower().str.strip()
    data["regeneration_needed"] = (
        data["regeneration_needed"].astype(str).str.lower().map({"yes": 1, "no": 0}).fillna(0)
    )

    for col in NUMERIC_FEATURES + ["final_germination_percentage"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    return data


# -------------------------------
# PREPROCESSOR
# -------------------------------
def build_preprocessor():
    return ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), NUMERIC_FEATURES),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), CATEGORICAL_FEATURES)
    ])


# -------------------------------
# VALIDATION
# -------------------------------
def validate_input(sample: dict):
    if not (0 <= sample["initial_viability"] <= 100):
        raise ValueError("initial_viability must be 0–100")

    if not (0 <= sample["storage_relative_humidity"] <= 100):
        raise ValueError("humidity must be 0–100")


# -------------------------------
# MODEL TRAINING
# -------------------------------
def train_models(X, y_reg, y_class, y_regen):
    log("Starting train/test split (80/20).")
    split_start = time.time()

    X_train, X_test, y_train_reg, y_test_reg, y_train_class, y_test_class, y_train_regen, y_test_regen = train_test_split(
        X, y_reg, y_class, y_regen, test_size=0.2, random_state=42, stratify=y_class
    )
    log(f"Completed split in {time.time() - split_start:.2f}s.")

    # ✅ FIXED: no nested parallelism
    regressor = Pipeline([
        ("pre", build_preprocessor()),
        ("model", RandomForestRegressor(n_estimators=200, n_jobs=1, random_state=42))
    ])

    log("Starting 5-fold cross-validation (regression).")
    cv_start = time.time()
    reg_cv = cross_validate(
        regressor,
        X,
        y_reg,
        cv=5,
        scoring={"r2": "r2"},
        n_jobs=-1
    )
    log(f"Completed regression CV in {time.time() - cv_start:.2f}s.")

    log("Fitting regression model on training split.")
    reg_fit_start = time.time()
    regressor.fit(X_train, y_train_reg)
    log(f"Completed regression fit in {time.time() - reg_fit_start:.2f}s.")

    # classifiers
    classifier = Pipeline([
        ("pre", build_preprocessor()),
        ("model", RandomForestClassifier(n_estimators=200, n_jobs=1, random_state=42))
    ])

    log("Fitting viability-class classifier on training split.")
    class_fit_start = time.time()
    classifier.fit(X_train, y_train_class)
    log(f"Completed viability-class fit in {time.time() - class_fit_start:.2f}s.")

    regen_model = Pipeline([
        ("pre", build_preprocessor()),
        ("model", RandomForestClassifier(n_estimators=200, n_jobs=1, random_state=42))
    ])

    log("Fitting regeneration classifier on training split.")
    regen_fit_start = time.time()
    regen_model.fit(X_train, y_train_regen)
    log(f"Completed regeneration fit in {time.time() - regen_fit_start:.2f}s.")

    # evaluation
    test_r2 = r2_score(y_test_reg, regressor.predict(X_test))
    cv_r2 = reg_cv["test_r2"].mean()

    return {
        "regressor": regressor,
        "classifier": classifier,
        "regen": regen_model,
        "cv_r2": cv_r2,
        "test_r2": test_r2
    }


# -------------------------------
# PERMUTATION IMPORTANCE
# -------------------------------
def get_permutation_importance(model, X, y):
    r = permutation_importance(model, X, y, n_repeats=5, random_state=42, n_jobs=-1)
    return sorted(zip(X.columns, r.importances_mean), key=lambda x: x[1], reverse=True)


# -------------------------------
# TIME PREDICTION (🔥 CORE FEATURE)
# -------------------------------
def predict_timeline(sample: dict, artifacts):
    log("Starting timeline prediction for 1, 5, 10, 15, 20, 30, 40, 50 years.")
    validate_input(sample)

    model = artifacts["regressor"]
    class_model = artifacts["classifier"]

    timeline = []

    for year in [1, 5, 10, 15, 20, 30, 40, 50]:
        temp = sample.copy()
        temp["storage_duration_months"] = year * 12

        df = pd.DataFrame([temp])

        viability = float(model.predict(df)[0])
        viability = max(0, min(100, viability))

        regen_flag = viability < 50

        timeline.append({
            "year": year,
            "viability": round(viability, 2),
            "regeneration_needed": regen_flag
        })

        log(f"Predicted year {year}.")

    return timeline


# -------------------------------
# MODEL VERSIONING
# -------------------------------
def save_model_versioned(model, name):
    timestamp = int(time.time())
    path = MODEL_DIR / f"{name}_{timestamp}.joblib"
    joblib.dump(model, path)
    return path


# -------------------------------
# MAIN
# -------------------------------
def main():
    overall_start = time.time()
    log("Script started.")

    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", help="JSON input")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    log("Loading and normalizing dataset.")
    data = normalize_targets(load_dataset())
    log(f"Dataset ready with {len(data)} rows.")

    X = data[FEATURE_COLUMNS]
    y_reg = data["final_germination_percentage"]
    y_class = data["viability_class"]
    y_regen = data["regeneration_needed"]

    log("Training models.")
    artifacts = train_models(X, y_reg, y_class, y_regen)

    print("\nModel Performance")
    print(f"CV R2: {artifacts['cv_r2']:.4f}")
    print(f"Test R2: {artifacts['test_r2']:.4f}")

    if abs(artifacts["cv_r2"] - artifacts["test_r2"]) > 0.1:
        print("⚠️ Possible overfitting detected")

    log("Preparing sample input.")
    sample = json.loads(args.sample) if args.sample else X.iloc[0].to_dict()

    timeline = predict_timeline(sample, artifacts)

    print("\n📊 Prediction Timeline")
    print(json.dumps(timeline, indent=2))

    if args.save:
        log("Saving model artifacts.")
        save_model_versioned(artifacts["regressor"], "rf_regressor")
        save_model_versioned(artifacts["classifier"], "rf_classifier")
        save_model_versioned(artifacts["regen"], "rf_regen")

    log(f"Script finished in {time.time() - overall_start:.2f}s.")


if __name__ == "__main__":
    main()