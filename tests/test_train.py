import pandas as pd
import numpy as np
import pytest

from src.train import (
    build_pipeline,
    evaluate_pipeline,
    load_pipeline,
    save_pipeline,
    split_data,
    train_pipeline,
)


@pytest.fixture
def train_df() -> pd.DataFrame:
    np.random.seed(42)
    n = 200
    data = {
        "age": np.random.randint(18, 90, n),
        "job": np.random.choice(
            ["admin.", "blue-collar", "technician", "services", "management"], n
        ),
        "marital": np.random.choice(["married", "single", "divorced"], n),
        "education": np.random.choice(
            ["high.school", "university.degree", "basic.9y", "professional.course"], n
        ),
        "default": np.random.choice(["no", "yes"], n),
        "housing": np.random.choice(["no", "yes"], n),
        "loan": np.random.choice(["no", "yes"], n),
        "contact": np.random.choice(["cellular", "telephone"], n),
        "month": np.random.choice(["may", "jun", "jul", "aug", "sep"], n),
        "day_of_week": np.random.choice(["mon", "tue", "wed", "thu", "fri"], n),
        "duration": np.random.randint(50, 4000, n),
        "campaign": np.random.randint(1, 15, n),
        "pdays": np.random.choice([999, 3, 5, 10], n),
        "previous": np.random.randint(0, 5, n),
        "poutcome": np.random.choice(["nonexistent", "failure", "success"], n),
        "emp_var_rate": np.random.uniform(-3, 3, n),
        "cons_price_index": np.random.uniform(90, 100, n),
        "cons_conf_index": np.random.uniform(-50, -30, n),
        "lending_rate3m": np.random.uniform(0.5, 5, n),
        "nr_employed": np.random.uniform(4900, 5300, n),
    }
    df = pd.DataFrame(data)
    df["subscribe"] = np.where(
        (df["duration"] > 1500) & (df["poutcome"] == "success")
        | (np.random.random(n) < 0.15),
        "yes",
        "no",
    )
    return df


class TestSplitData:
    def test_split_sizes(self, train_df):
        X_train, X_test, y_train, y_test = split_data(train_df)
        assert len(X_train) + len(X_test) == len(train_df)
        assert len(y_train) + len(y_test) == len(train_df)
        assert len(X_test) / len(train_df) == pytest.approx(0.2, abs=0.05)

    def test_stratify_preserves_ratio(self, train_df):
        X_train, X_test, y_train, y_test = split_data(train_df)
        orig_ratio = (train_df["subscribe"] == "yes").mean()
        train_ratio = y_train.mean()
        assert abs(train_ratio - orig_ratio) < 0.15


class TestBuildPipeline:
    def test_pipeline_structure(self):
        pipe = build_pipeline()
        assert "preprocessor" in pipe.named_steps
        assert "classifier" in pipe.named_steps


class TestTrainPipeline:
    def test_returns_pipeline_and_metrics(self, train_df):
        pipeline, metrics = train_pipeline(train_df)
        assert pipeline is not None
        assert "auc" in metrics
        assert metrics["auc"] > 0.5

    def test_auc_above_threshold(self, train_df):
        _, metrics = train_pipeline(train_df)
        assert metrics["auc"] >= 0.55


class TestEvaluatePipeline:
    def test_returns_dict(self, train_df):
        X_train, X_test, y_train, y_test = split_data(train_df)
        pipe = build_pipeline()
        pipe.fit(X_train, y_train)
        metrics = evaluate_pipeline(pipe, X_test, y_test)
        assert "auc" in metrics
        assert "classification_report" in metrics


class TestSaveLoad:
    def test_roundtrip(self, train_df, tmp_path):
        pipe = build_pipeline()
        X = train_df.drop(columns=["subscribe"])
        y = (train_df["subscribe"] == "yes").astype(int)
        pipe.fit(X, y)

        path = tmp_path / "model.joblib"
        save_pipeline(pipe, str(path))
        loaded = load_pipeline(str(path))

        pred_orig = pipe.predict(X.head(3))
        pred_loaded = loaded.predict(X.head(3))
        assert (pred_orig == pred_loaded).all()
