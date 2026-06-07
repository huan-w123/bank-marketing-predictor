import pandas as pd
import pytest

from src.analysis import (
    get_categorical_counts,
    get_cross_tab,
    get_feature_cols,
    get_missing_info,
    get_numeric_distribution,
    get_summary,
    get_target_distribution,
    load_data,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    data = {
        "age": [30, 45, 28, 52],
        "job": ["admin.", "blue-collar", "technician", "services"],
        "marital": ["married", "single", "divorced", "married"],
        "education": ["high.school", "university.degree", "basic.9y", "high.school"],
        "default": ["no", "no", "no", "yes"],
        "housing": ["yes", "yes", "no", "no"],
        "loan": ["no", "yes", "no", "yes"],
        "contact": ["cellular", "cellular", "telephone", "cellular"],
        "month": ["may", "jun", "jul", "aug"],
        "day_of_week": ["mon", "tue", "wed", "thu"],
        "duration": [100, 200, 150, 300],
        "campaign": [1, 2, 3, 1],
        "pdays": [999, 3, 999, 10],
        "previous": [0, 1, 0, 2],
        "poutcome": ["nonexistent", "failure", "nonexistent", "success"],
        "emp_var_rate": [1.4, -1.8, 1.4, -0.5],
        "cons_price_index": [92.0, 93.0, 94.0, 91.5],
        "cons_conf_index": [-36.0, -41.0, -35.0, -39.0],
        "lending_rate3m": [1.2, 2.0, 1.5, 3.0],
        "nr_employed": [5191.0, 4999.0, 5100.0, 5050.0],
        "subscribe": ["no", "yes", "no", "yes"],
    }
    return pd.DataFrame(data)


class TestLoadData:
    def test_load_csv(self, tmp_path):
        csv_path = tmp_path / "test.csv"
        pd.DataFrame(
            {"id": [1, 2], "age": [30, 40], "subscribe": ["no", "yes"]}
        ).to_csv(csv_path, index=False)
        df = load_data(str(csv_path))
        assert "id" not in df.columns
        assert "age" in df.columns
        assert len(df) == 2

    def test_load_no_id_column(self, tmp_path):
        csv_path = tmp_path / "test.csv"
        pd.DataFrame({"age": [30], "subscribe": ["no"]}).to_csv(csv_path, index=False)
        df = load_data(str(csv_path))
        assert len(df) == 1


class TestGetSummary:
    def test_returns_structure(self, sample_df):
        summary = get_summary(sample_df)
        assert summary["n_rows"] == 4
        assert "age" in summary["num_features"]


class TestGetMissingInfo:
    def test_no_missing(self, sample_df):
        info = get_missing_info(sample_df)
        assert info == {}

    def test_with_missing(self, sample_df):
        sample_df.loc[0, "age"] = None
        info = get_missing_info(sample_df)
        assert "age" in info
        assert info["age"]["count"] == 1


class TestGetTargetDistribution:
    def test_distribution(self, sample_df):
        dist = get_target_distribution(sample_df)
        assert "yes" in dist
        assert dist["yes"]["count"] == 2
        assert "no" in dist
        assert dist["no"]["count"] == 2


class TestGetNumericDistribution:
    def test_stats(self, sample_df):
        stats = get_numeric_distribution(sample_df, "age")
        assert "mean" in stats
        assert abs(stats["mean"] - 38.75) < 0.01

    def test_missing_feature(self, sample_df):
        assert get_numeric_distribution(sample_df, "nonexistent") == {}


class TestGetCategoricalCounts:
    def test_counts(self, sample_df):
        counts = get_categorical_counts(sample_df, "job")
        assert counts["admin."] == 1
        assert counts["blue-collar"] == 1


class TestGetCrossTab:
    def test_cross_tab(self, sample_df):
        ct = get_cross_tab(sample_df, "default")
        assert ct.shape[0] == 2  # no, yes


class TestGetFeatureCols:
    def test_returns_list(self):
        cols = get_feature_cols()
        assert isinstance(cols, list)
        assert "age" in cols
        assert "job" in cols
