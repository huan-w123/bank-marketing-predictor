import pandas as pd

NUMERIC_COLS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]

CATEGORICAL_COLS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]

TARGET_COL = "subscribe"
DROP_COLS = ["id"]


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df.drop(columns=[c for c in DROP_COLS if c in df.columns])


def get_feature_cols() -> list[str]:
    return NUMERIC_COLS + CATEGORICAL_COLS


def get_summary(df: pd.DataFrame) -> dict:
    n_rows, n_cols = df.shape
    num_feats = [c for c in NUMERIC_COLS if c in df.columns]
    cat_feats = [c for c in CATEGORICAL_COLS if c in df.columns]
    return {
        "n_rows": n_rows,
        "n_cols": n_cols,
        "num_features": num_feats,
        "cat_features": cat_feats,
        "numeric_summary": df[num_feats].describe().to_dict() if num_feats else {},
    }


def get_missing_info(df: pd.DataFrame) -> dict:
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    result = {}
    for col in df.columns:
        if missing[col] > 0:
            result[col] = {"count": int(missing[col]), "pct": float(missing_pct[col])}
    return result


def get_target_distribution(df: pd.DataFrame) -> dict:
    if TARGET_COL not in df.columns:
        return {}
    counts = df[TARGET_COL].value_counts().to_dict()
    pcts = (df[TARGET_COL].value_counts(normalize=True) * 100).round(2).to_dict()
    return {
        k: {"count": counts.get(k, 0), "pct": float(pcts.get(k, 0))} for k in counts
    }


def get_numeric_distribution(df: pd.DataFrame, feature: str) -> dict:
    if feature not in df.columns:
        return {}
    col = df[feature]
    return {
        "mean": float(col.mean()),
        "median": float(col.median()),
        "std": float(col.std()),
        "min": float(col.min()),
        "max": float(col.max()),
    }


def get_categorical_counts(df: pd.DataFrame, feature: str) -> dict:
    if feature not in df.columns:
        return {}
    counts = df[feature].value_counts().to_dict()
    return {str(k): int(v) for k, v in counts.items()}


def get_cross_tab(df: pd.DataFrame, feature: str) -> pd.DataFrame:
    if feature not in df.columns or TARGET_COL not in df.columns:
        return pd.DataFrame()
    return pd.crosstab(df[feature], df[TARGET_COL], normalize="index") * 100
