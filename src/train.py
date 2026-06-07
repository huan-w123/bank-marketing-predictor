import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.analysis import CATEGORICAL_COLS, NUMERIC_COLS, TARGET_COL, get_feature_cols

RANDOM_SEED = 42
TEST_SIZE = 0.2
AUC_THRESHOLD = 0.80


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_COLS),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_COLS,
            ),
        ],
        remainder="drop",
    )


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    random_state=RANDOM_SEED,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def split_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    X = df[get_feature_cols()]
    y = (df[TARGET_COL] == "yes").astype(int)
    return train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_SEED
    )


def train_pipeline(df: pd.DataFrame) -> tuple[Pipeline, dict]:
    X_train, X_test, y_train, y_test = split_data(df)
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    metrics = evaluate_pipeline(pipeline, X_test, y_test)
    return pipeline, metrics


def evaluate_pipeline(
    pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series
) -> dict:
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_proba)
    report = classification_report(
        y_test, y_pred, target_names=["no", "yes"], output_dict=True
    )
    return {"auc": float(auc), "classification_report": report}


def save_pipeline(pipeline: Pipeline, path: str) -> None:
    joblib.dump(pipeline, path)


def load_pipeline(path: str) -> Pipeline:
    return joblib.load(path)
