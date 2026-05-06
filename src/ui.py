import pandas as pd
import plotly.express as px
import streamlit as st


CHANGE_COLUMNS = ["change_1d_pct", "change_5bd_pct", "change_25bd_pct", "change_75bd_pct"]


def format_pct(value: object) -> str:
    if pd.isna(value):
        return "-"
    return f"{float(value) * 100:.2f}%"


def format_number(value: object, digits: int = 2) -> str:
    if pd.isna(value):
        return "-"
    return f"{float(value):,.{digits}f}"


def format_market_cap(value: object) -> str:
    if pd.isna(value):
        return "-"
    oku_yen = float(value) / 100_000_000
    if oku_yen >= 10_000:
        return f"{oku_yen / 10_000:.2f}兆円"
    return f"{oku_yen:,.0f}億円"


def display_stock_table(df: pd.DataFrame) -> pd.DataFrame:
    formatted = df.copy()
    if "market_cap" in formatted.columns:
        formatted["market_cap"] = formatted["market_cap"].map(format_market_cap)
    for col in CHANGE_COLUMNS:
        if col in formatted.columns:
            formatted[col] = formatted[col].map(format_pct)
    for col in ["latest_price", "per", "pbr", "roe", "roic"]:
        if col in formatted.columns:
            if col == "roe":
                formatted[col] = formatted[col].map(format_pct)
            else:
                formatted[col] = formatted[col].map(format_number)
    return formatted.fillna("-")


def render_metric_cards(df: pd.DataFrame) -> None:
    cols = st.columns(5)
    metrics = [
        ("銘柄数", len(df), None),
        ("平均前日比", df["change_1d_pct"].mean(), "pct"),
        ("平均5営業日比", df["change_5bd_pct"].mean(), "pct"),
        ("平均25営業日比", df["change_25bd_pct"].mean(), "pct"),
        ("平均75営業日比", df["change_75bd_pct"].mean(), "pct"),
    ]
    for col, (label, value, kind) in zip(cols, metrics):
        col.metric(label, format_pct(value) if kind == "pct" else f"{value:,}")


def render_category_bar(summary: pd.DataFrame, metric: str = "change_25bd_pct") -> None:
    if summary.empty or metric not in summary.columns:
        st.info("グラフ表示に必要なデータがありません。")
        return
    chart_df = summary.sort_values(metric, ascending=False).copy()
    chart_df[f"{metric}_percent"] = chart_df[metric] * 100
    fig = px.bar(
        chart_df,
        x="category",
        y=f"{metric}_percent",
        color=f"{metric}_percent",
        color_continuous_scale=["#b91c1c", "#f8fafc", "#047857"],
        labels={f"{metric}_percent": "平均騰落率(%)", "category": "Category"},
    )
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)


def dataframe_with_pct(df: pd.DataFrame) -> pd.DataFrame:
    formatted = df.copy()
    for col in formatted.columns:
        if col.startswith("change_"):
            formatted[col] = formatted[col].map(format_pct)
    return formatted.fillna("-")


def render_data_quality(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("表示するデータがありません。")
        return

    failed = df[df["data_status"].ne("OK")].copy()
    st.subheader("取得失敗・注意が必要な銘柄")
    if failed.empty:
        st.success("重大な取得失敗はありません。")
    else:
        st.dataframe(failed[["category", "subcategory", "code", "name", "data_status"]], use_container_width=True)

    st.subheader("欠損項目")
    records = []
    check_columns = [
        "latest_price",
        "market_cap",
        "per",
        "pbr",
        "roe",
        "roic",
        "change_1d_pct",
        "change_5bd_pct",
        "change_25bd_pct",
        "change_75bd_pct",
    ]
    for _, row in df.iterrows():
        missing = [col for col in check_columns if col in df.columns and pd.isna(row[col])]
        if missing:
            records.append(
                {
                    "code": row["code"],
                    "name": row["name"],
                    "missing_items": ", ".join(missing),
                    "data_status": row["data_status"],
                }
            )
    st.dataframe(pd.DataFrame(records), use_container_width=True)

