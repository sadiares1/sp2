from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "ml_models"
MODEL_DIR.mkdir(exist_ok=True)

DATA_FILES = sorted(BASE_DIR.glob("*SyntheticData.csv"))

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


def load_dataset() -> pd.DataFrame:
    if not DATA_FILES:
        raise FileNotFoundError("No synthetic CSV files were found in the api-django folder.")

    frames = []
    for path in DATA_FILES:
        frame = pd.read_csv(path)
        frame["source_file"] = path.name
        frames.append(frame)

    data = pd.concat(frames, ignore_index=True)
    data.columns = [str(column).strip() for column in data.columns]

    missing = [column for column in FEATURE_COLUMNS + ["final_germination_percentage", "viability_class", "regeneration_needed"] if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    return data


def normalize_targets(data: pd.DataFrame) -> pd.DataFrame:
    cleaned = data.copy()
    cleaned["viability_class"] = cleaned["viability_class"].astype(str).str.strip().str.lower()
    cleaned["regeneration_needed"] = cleaned["regeneration_needed"].astype(str).str.strip().str.lower()
    cleaned["regeneration_needed"] = cleaned["regeneration_needed"].map({"yes": 1, "no": 0}).fillna(0).astype(int)

    if "final_germination_percentage" in cleaned.columns:
        cleaned["final_germination_percentage"] = pd.to_numeric(
            cleaned["final_germination_percentage"], errors="coerce"
        )

    for column in NUMERIC_FEATURES:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    return cleaned


def build_preprocessor() -> ColumnTransformer:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )


def split_data(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    features = data[FEATURE_COLUMNS]
    viability_target = data["final_germination_percentage"]
    class_target = data["viability_class"]
    regen_target = data["regeneration_needed"]
    return features, viability_target, class_target, regen_target


def derive_viability_class(percentage: float) -> str:
    if percentage >= 80:
        return "high"
    if percentage >= 60:
        return "medium"
    return "low"


def train_models(features: pd.DataFrame, viability_target: pd.Series, class_target: pd.Series, regen_target: pd.Series) -> dict[str, Any]:
    X_train, X_test, y_train_reg, y_test_reg, y_train_class, y_test_class, y_train_regen, y_test_regen = train_test_split(
        features,
        viability_target,
        class_target,
        regen_target,
        test_size=0.2,
        random_state=42,
        stratify=class_target,
    )

    regressor = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("model", RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)),
        ]
    )
    regressor.fit(X_train, y_train_reg)

    class_candidates = sorted(class_target.dropna().astype(str).str.lower().unique().tolist())
    if len(class_candidates) < 2:
        class_candidates = ["high", "medium", "low"]

    class_model = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("model", RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)),
        ]
    )
    class_model.fit(X_train, y_train_class)

    regen_model = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("model", RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)),
        ]
    )
    regen_model.fit(X_train, y_train_regen)

    reg_predictions = regressor.predict(X_test)
    class_predictions = class_model.predict(X_test)
    regen_predictions = regen_model.predict(X_test)

    results = {
        "regressor": regressor,
        "class_model": class_model,
        "regen_model": regen_model,
        "regression_mae": float(mean_absolute_error(y_test_reg, reg_predictions)),
        "regression_r2": float(r2_score(y_test_reg, reg_predictions)),
        "class_accuracy": float(accuracy_score(y_test_class, class_predictions)),
        "regen_accuracy": float(accuracy_score(y_test_regen, regen_predictions)),
    }

    return results


def extract_feature_importance(model: Pipeline) -> list[dict[str, float]]:
    preprocessor = model.named_steps["preprocessor"]
    estimator = model.named_steps["model"]
    feature_names = list(preprocessor.get_feature_names_out())
    importances = estimator.feature_importances_

    ranked = sorted(zip(feature_names, importances), key=lambda item: item[1], reverse=True)
    return [{"feature": name, "importance": float(score)} for name, score in ranked]


def predict(sample: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    frame = pd.DataFrame([sample])
    frame = frame.reindex(columns=FEATURE_COLUMNS)

    regressor = artifacts["regressor"]
    class_model = artifacts["class_model"]
    regen_model = artifacts["regen_model"]

    predicted_viability = float(regressor.predict(frame)[0])
    predicted_viability = max(0.0, min(100.0, predicted_viability))

    class_probabilities = class_model.predict_proba(frame)[0]
    class_index = int(class_probabilities.argmax())
    class_prediction = str(class_model.named_steps["model"].classes_[class_index]).lower()
    class_confidence = float(class_probabilities[class_index])

    regen_probabilities = regen_model.predict_proba(frame)[0]
    regen_index = int(regen_probabilities.argmax())
    regen_prediction = int(regen_model.named_steps["model"].classes_[regen_index])
    regen_confidence = float(regen_probabilities[regen_index])

    confidence_score = round((class_confidence + regen_confidence) / 2.0, 4)

    return {
        "predicted_viability_percentage": round(predicted_viability, 2),
        "viability_class": class_prediction if class_prediction in {"high", "medium", "low"} else derive_viability_class(predicted_viability),
        "confidence_score": confidence_score,
        "regeneration_decision": "yes" if regen_prediction == 1 else "no",
    }


def default_sample(data: pd.DataFrame) -> dict[str, Any]:
    sample = {}
    for column in NUMERIC_FEATURES:
        sample[column] = float(pd.to_numeric(data[column], errors="coerce").dropna().median())
    for column in CATEGORICAL_FEATURES:
        sample[column] = data[column].dropna().astype(str).mode().iat[0]
    return sample


def parse_sample_argument(sample_arg: str | None, data: pd.DataFrame) -> dict[str, Any]:
    if not sample_arg:
        return default_sample(data)

    path = Path(sample_arg)
    if path.exists() and path.suffix.lower() == ".csv":
        sample_df = pd.read_csv(path)
        if sample_df.empty:
            raise ValueError("The sample CSV is empty.")
        return sample_df.iloc[0][FEATURE_COLUMNS].to_dict()

    return json.loads(sample_arg)


def save_artifacts(artifacts: dict[str, Any]) -> None:
    joblib.dump(artifacts["regressor"], MODEL_DIR / "random_forest_viability_regressor.joblib")
    joblib.dump(artifacts["class_model"], MODEL_DIR / "random_forest_viability_class.joblib")
    joblib.dump(artifacts["regen_model"], MODEL_DIR / "random_forest_regeneration.joblib")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Random Forest models for seed viability prediction.")
    parser.add_argument(
        "--sample",
        help="Optional JSON string or path to a CSV file with one row of input features.",
    )
    parser.add_argument(
        "--save-models",
        action="store_true",
        help="Save trained models under api-django/ml_models/.",
    )
    args = parser.parse_args()

    data = normalize_targets(load_dataset())
    features, viability_target, class_target, regen_target = split_data(data)

    artifacts = train_models(features, viability_target, class_target, regen_target)
    feature_importance = extract_feature_importance(artifacts["regressor"])

    sample = parse_sample_argument(args.sample, data)
    prediction = predict(sample, artifacts)

    if args.save_models:
        save_artifacts(artifacts)

    print("Training metrics")
    print(f"  Viability MAE: {artifacts['regression_mae']:.4f}")
    print(f"  Viability R2: {artifacts['regression_r2']:.4f}")
    print(f"  Viability class accuracy: {artifacts['class_accuracy']:.4f}")
    print(f"  Regeneration accuracy: {artifacts['regen_accuracy']:.4f}")
    print()
    print("Prediction")
    print(json.dumps(prediction, indent=2))
    print()
    print("Top feature importance")
    for item in feature_importance[:10]:
        print(f"  {item['feature']}: {item['importance']:.6f}")


if __name__ == "__main__":
    main()