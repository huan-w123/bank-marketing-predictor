import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analysis import (
    CATEGORICAL_COLS,
    NUMERIC_COLS,
    TARGET_COL,
    get_categorical_counts,
    get_cross_tab,
    get_missing_info,
    get_numeric_distribution,
    get_summary,
    get_target_distribution,
    load_data,
)
from src.predict import predict
from src.train import load_pipeline, train_pipeline

st.set_page_config(page_title="银行营销数据分析与预测", page_icon="📊", layout="wide")

DATA_PATH = os.path.join("data", "train.csv")
MODEL_PATH = os.path.join("models", "pipeline.joblib")


@st.cache_data
def load_df(path: str) -> pd.DataFrame:
    return load_data(path)


@st.cache_resource
def get_pipeline(df: pd.DataFrame):
    pipeline, metrics = train_pipeline(df)
    return pipeline, metrics


def render_analysis_page(df: pd.DataFrame):
    st.title("📊 数据分析看板")

    summary = get_summary(df)
    missing = get_missing_info(df)
    target_dist = get_target_distribution(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("总行数", f"{summary['n_rows']:,}")
    col2.metric("特征数", summary["n_cols"])
    col3.metric("缺失字段", len(missing) if missing else "无")

    with st.expander("数据摘要", expanded=False):
        st.dataframe(df.describe(), use_container_width=True)

    if missing:
        with st.expander(f"⚠️ 缺失值信息（{len(missing)} 个字段）"):
            st.json(missing)

    st.subheader("目标变量分布")
    if target_dist:
        fig = go.Figure()
        labels = list(target_dist.keys())
        counts = [target_dist[k]["count"] for k in labels]
        pcts = [target_dist[k]["pct"] for k in labels]
        fig.add_trace(
            go.Bar(
                x=labels, y=counts, text=[f"{p}%" for p in pcts], textposition="auto"
            )
        )
        fig.update_layout(xaxis_title="是否认购", yaxis_title="人数")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("特征分布探索")
    col_left, col_right = st.columns([1, 3])

    with col_left:
        feature_type = st.radio("特征类型", ["数值特征", "类别特征"], key="feat_type")
        if feature_type == "数值特征":
            selected = st.selectbox("选择数值特征", NUMERIC_COLS, key="num_feat")
        else:
            selected = st.selectbox("选择类别特征", CATEGORICAL_COLS, key="cat_feat")

    with col_right:
        if selected:
            if feature_type == "数值特征":
                dist = get_numeric_distribution(df, selected)
                if dist:
                    cols = st.columns(5)
                    cols[0].metric("均值", f"{dist['mean']:.2f}")
                    cols[1].metric("中位数", f"{dist['median']:.2f}")
                    cols[2].metric("标准差", f"{dist['std']:.2f}")
                    cols[3].metric("最小值", f"{dist['min']:.2f}")
                    cols[4].metric("最大值", f"{dist['max']:.2f}")

                fig = px.histogram(
                    df,
                    x=selected,
                    color=df[TARGET_COL] if TARGET_COL in df.columns else None,
                    marginal="box",
                    nbins=40,
                    opacity=0.7,
                    title=f"{selected} 分布（按认购着色）",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                counts = get_categorical_counts(df, selected)
                if counts:
                    fig = px.bar(
                        x=list(counts.keys()),
                        y=list(counts.values()),
                        title=f"{selected} 各类别计数",
                        labels={"x": selected, "y": "人数"},
                    )
                    st.plotly_chart(fig, use_container_width=True)

                ct = get_cross_tab(df, selected)
                if not ct.empty:
                    st.subheader(f"{selected} × 认购 交叉分析 (%)")
                    fig_ct = px.imshow(
                        ct,
                        text_auto=".1f",
                        aspect="auto",
                        labels={"color": "占比 (%)"},
                        title=f"{selected} 各取值对应的认购比例",
                    )
                    st.plotly_chart(fig_ct, use_container_width=True)


def render_prediction_page(pipeline):
    st.title("🔮 在线预测")

    st.markdown("输入客户特征信息，预测该客户是否会认购定期存款。")

    with st.form("prediction_form"):
        col_a, col_b, col_c = st.columns(3)

        inputs = {}
        with col_a:
            inputs["age"] = st.number_input(
                "年龄", min_value=17, max_value=100, value=35, step=1
            )
            inputs["job"] = st.selectbox(
                "职业",
                [
                    "admin.",
                    "blue-collar",
                    "technician",
                    "services",
                    "management",
                    "entrepreneur",
                    "self-employed",
                    "housemaid",
                    "unemployed",
                    "student",
                    "retired",
                ],
            )
            inputs["marital"] = st.selectbox(
                "婚姻状况", ["married", "single", "divorced"]
            )
            inputs["education"] = st.selectbox(
                "教育程度",
                [
                    "high.school",
                    "university.degree",
                    "basic.9y",
                    "professional.course",
                    "illiterate",
                ],
            )
            inputs["default"] = st.selectbox("是否有信贷违约", ["no", "yes"])
            inputs["housing"] = st.selectbox("是否有住房贷款", ["no", "yes"])
            inputs["loan"] = st.selectbox("是否有个人贷款", ["no", "yes"])

        with col_b:
            inputs["contact"] = st.selectbox("联系方式", ["cellular", "telephone"])
            inputs["month"] = st.selectbox(
                "最后联系月份",
                [
                    "jan",
                    "feb",
                    "mar",
                    "apr",
                    "may",
                    "jun",
                    "jul",
                    "aug",
                    "sep",
                    "oct",
                    "nov",
                    "dec",
                ],
            )
            inputs["day_of_week"] = st.selectbox(
                "最后联系星期", ["mon", "tue", "wed", "thu", "fri"]
            )
            inputs["duration"] = st.number_input(
                "通话时长（秒）", min_value=0, max_value=6000, value=300, step=1
            )
            inputs["campaign"] = st.number_input(
                "本次营销联系次数", min_value=1, max_value=50, value=1, step=1
            )
            inputs["pdays"] = st.number_input(
                "上次联系距今天数（999=未联系过）",
                min_value=0,
                max_value=999,
                value=999,
                step=1,
            )
            inputs["previous"] = st.number_input(
                "本次营销前联系次数", min_value=0, max_value=10, value=0, step=1
            )

        with col_c:
            inputs["poutcome"] = st.selectbox(
                "上次营销结果", ["nonexistent", "failure", "success"]
            )
            inputs["emp_var_rate"] = st.number_input(
                "就业变化率",
                min_value=-5.0,
                max_value=5.0,
                value=1.4,
                step=0.1,
                format="%.1f",
            )
            inputs["cons_price_index"] = st.number_input(
                "消费者物价指数",
                min_value=80.0,
                max_value=110.0,
                value=93.0,
                step=0.1,
                format="%.2f",
            )
            inputs["cons_conf_index"] = st.number_input(
                "消费者信心指数",
                min_value=-60.0,
                max_value=0.0,
                value=-36.0,
                step=0.1,
                format="%.2f",
            )
            inputs["lending_rate3m"] = st.number_input(
                "3个月拆借利率",
                min_value=0.0,
                max_value=10.0,
                value=1.5,
                step=0.1,
                format="%.2f",
            )
            inputs["nr_employed"] = st.number_input(
                "就业人数",
                min_value=4500.0,
                max_value=6000.0,
                value=5100.0,
                step=0.1,
                format="%.1f",
            )

        submitted = st.form_submit_button(
            "🔍 预测", type="primary", use_container_width=True
        )

    if submitted:
        result = predict(pipeline, inputs)
        if result["success"]:
            color = "green" if result["prediction"] == "会认购" else "red"
            st.markdown(
                f"### 预测结果：:<span style='color:{color}'>{result['prediction']}</span>",
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2)
            c1.metric("置信度", f"{result['confidence']:.2%}")
            c2.metric("认购概率", f"{result['subscribe_probability']:.2%}")

            prob = result["subscribe_probability"]
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=prob * 100,
                    title={"text": "认购概率 (%)"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 50], "color": "lightgray"},
                            {"range": [50, 100], "color": "lightgreen"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 2},
                            "value": 50,
                        },
                    },
                )
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("输入校验失败，请修正以下问题：")
            for err in result["errors"]:
                st.warning(f"- {err}")


def main():
    st.sidebar.title("导航")
    page = st.sidebar.radio("选择页面", ["📊 数据分析", "🔮 在线预测"])

    df = load_df(DATA_PATH)

    if page == "📊 数据分析":
        render_analysis_page(df)
    else:
        if os.path.exists(MODEL_PATH):
            pipeline = load_pipeline(MODEL_PATH)
            st.sidebar.success("✅ 已加载训练好的模型")
        else:
            with st.spinner("模型尚未训练，正在自动训练中..."):
                pipeline, metrics = get_pipeline(df)
                from src.train import save_pipeline

                os.makedirs("models", exist_ok=True)
                save_pipeline(pipeline, MODEL_PATH)
            st.sidebar.success(f"✅ 模型训练完成（AUC: {metrics['auc']:.3f}）")
        render_prediction_page(pipeline)


if __name__ == "__main__":
    main()
