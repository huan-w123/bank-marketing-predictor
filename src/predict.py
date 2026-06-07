import pandas as pd
from sklearn.pipeline import Pipeline

from src.analysis import CATEGORICAL_COLS, get_feature_cols

REQUIRED_FIELDS = get_feature_cols()

FIELD_RANGES = {
    "age": (17, 100),
    "duration": (0, 6000),
    "campaign": (1, 50),
    "pdays": (0, 999),
    "previous": (0, 10),
    "emp_var_rate": (-5.0, 5.0),
    "cons_price_index": (80.0, 110.0),
    "cons_conf_index": (-60.0, 0.0),
    "lending_rate3m": (0.0, 10.0),
    "nr_employed": (4500.0, 6000.0),
}


def validate_input(input_data: dict) -> list[str]:
    errors = []
    for field in REQUIRED_FIELDS:
        if (
            field not in input_data
            or input_data[field] is None
            or str(input_data[field]).strip() == ""
        ):
            errors.append(f"缺少必填字段: {field}")
            continue
        if field in FIELD_RANGES:
            try:
                val = float(input_data[field])
                lo, hi = FIELD_RANGES[field]
                if val < lo or val > hi:
                    errors.append(f"{field} 值 {val} 超出合理范围 [{lo}, {hi}]")
            except (ValueError, TypeError):
                errors.append(f"{field} 不是有效数值: {input_data[field]}")
        elif field in CATEGORICAL_COLS:
            if (
                not isinstance(input_data[field], str)
                or input_data[field].strip() == ""
            ):
                errors.append(f"{field} 需要文本值")
    return errors


def predict(pipeline: Pipeline, input_data: dict) -> dict:
    errors = validate_input(input_data)
    if errors:
        return {"success": False, "errors": errors}

    df = pd.DataFrame([input_data])[get_feature_cols()]
    proba = pipeline.predict_proba(df)[0]
    pred_class = pipeline.predict(df)[0]
    label = "会认购" if pred_class == 1 else "不会认购"
    confidence = float(max(proba))

    return {
        "success": True,
        "prediction": label,
        "confidence": round(confidence, 4),
        "subscribe_probability": round(float(proba[1]), 4),
    }
