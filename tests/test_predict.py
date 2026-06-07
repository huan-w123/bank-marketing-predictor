import pandas as pd
import numpy as np
import pytest

from src.predict import predict, validate_input
from src.train import build_pipeline


@pytest.fixture
def valid_input() -> dict:
    return {
        "age": 35,
        "job": "admin.",
        "marital": "married",
        "education": "high.school",
        "default": "no",
        "housing": "yes",
        "loan": "no",
        "contact": "cellular",
        "month": "may",
        "day_of_week": "mon",
        "duration": 500,
        "campaign": 2,
        "pdays": 999,
        "previous": 0,
        "poutcome": "nonexistent",
        "emp_var_rate": 1.4,
        "cons_price_index": 93.0,
        "cons_conf_index": -36.0,
        "lending_rate3m": 1.5,
        "nr_employed": 5100.0,
    }


@pytest.fixture
def fitted_pipeline():
    np.random.seed(42)
    n = 100
    df = pd.DataFrame(
        {
            "age": np.random.randint(18, 90, n),
            "job": np.random.choice(
                ["admin.", "blue-collar", "technician", "services", "management"], n
            ),
            "marital": np.random.choice(["married", "single", "divorced"], n),
            "education": np.random.choice(
                ["high.school", "university.degree", "basic.9y", "professional.course"],
                n,
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
            "subscribe": np.random.choice(["no", "yes"], n),
        }
    )
    pipe = build_pipeline()
    pipe.fit(df.drop(columns=["subscribe"]), (df["subscribe"] == "yes").astype(int))
    return pipe


class TestValidateInput:
    def test_valid_input_passes(self, valid_input):
        assert validate_input(valid_input) == []

    def test_missing_field(self):
        errors = validate_input({"age": 30})
        assert len(errors) > 0
        assert any("job" in e for e in errors)

    def test_out_of_range(self, valid_input):
        valid_input["age"] = -5
        errors = validate_input(valid_input)
        assert len(errors) > 0
        assert any("age" in e for e in errors)

    def test_empty_string_numeric(self, valid_input):
        valid_input["age"] = ""
        errors = validate_input(valid_input)
        assert len(errors) > 0

    def test_non_numeric_value(self, valid_input):
        valid_input["age"] = "abc"
        errors = validate_input(valid_input)
        assert len(errors) > 0
        assert any("age" in e for e in errors)


class TestPredict:
    def test_successful_prediction(self, fitted_pipeline, valid_input):
        result = predict(fitted_pipeline, valid_input)
        assert result["success"] is True
        assert result["prediction"] in ("会认购", "不会认购")
        assert 0 <= result["confidence"] <= 1

    def test_validation_error(self, fitted_pipeline):
        result = predict(fitted_pipeline, {"age": 30})
        assert result["success"] is False
        assert len(result["errors"]) > 0

    def test_prediction_structure(self, fitted_pipeline, valid_input):
        result = predict(fitted_pipeline, valid_input)
        assert "subscribe_probability" in result
        assert isinstance(result["confidence"], float)
