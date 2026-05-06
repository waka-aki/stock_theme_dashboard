import pandas as pd
import streamlit as st

from src.config import CACHE_TTL_SECONDS, DASHBOARD_DATA_PATH, WATCHLIST_PATH
from src.data_loader import (
    WATCHLIST_COLUMNS,
    load_dashboard_snapshot,
    load_watchlist,
    save_dashboard_snapshot,
    save_watchlist,
    validate_watchlist,
)
from src.metrics import CHANGE_WINDOWS, category_return_summary, subcategory_summary
from src.providers.yfinance_provider import build_dashboard_data
from src.ui import (
    dataframe_with_pct,
    display_stock_table,
    render_category_bar,
    render_data_quality,
    render_metric_cards,
)


st.set_page_config(page_title="日本株テーマ別ダッシュボード", layout="wide")


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def get_watchlist() -> pd.DataFrame:
    return load_watchlist(WATCHLIST_PATH)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def get_dashboard_data(watchlist_records: list[dict[str, str]], force_refresh: bool = False) -> pd.DataFrame:
    if not force_refresh:
        snapshot = load_dashboard_snapshot(DASHBOARD_DATA_PATH, WATCHLIST_PATH)
        if snapshot is not None:
            return snapshot

    watchlist = pd.DataFrame(watchlist_records)
    dashboard_data = build_dashboard_data(watchlist)
    save_dashboard_snapshot(dashboard_data, DASHBOARD_DATA_PATH)
    return dashboard_data


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    categories = sorted(df["category"].dropna().unique().tolist())
    selected_categories = st.sidebar.multiselect("category", categories, default=categories)

    category_filtered = df[df["category"].isin(selected_categories)] if selected_categories else df.copy()
    subcategories = sorted(category_filtered["subcategory"].dropna().unique().tolist())
    selected_subcategories = st.sidebar.multiselect("subcategory", subcategories, default=subcategories)

    search_text = st.sidebar.text_input("銘柄名・銘柄コードの検索", "")
    sort_options = [
        "category",
        "subcategory",
        "code",
        "name",
        "latest_price",
        "market_cap",
        "per",
        "pbr",
        "roe",
        "roic",
        *CHANGE_WINDOWS.keys(),
    ]
    sort_by = st.sidebar.selectbox("並び替え対象", sort_options, index=sort_options.index("change_25bd_pct"))
    ascending = st.sidebar.radio("並び順", ["降順", "昇順"], horizontal=True) == "昇順"

    filtered = category_filtered
    if selected_subcategories:
        filtered = filtered[filtered["subcategory"].isin(selected_subcategories)]
    if search_text.strip():
        keyword = search_text.strip()
        mask = filtered["name"].str.contains(keyword, case=False, na=False) | filtered["code"].str.contains(keyword, na=False)
        filtered = filtered[mask]

    return filtered.sort_values(sort_by, ascending=ascending, na_position="last")


def render_dashboard_tab(df: pd.DataFrame) -> None:
    render_metric_cards(df)
    st.divider()

    summary = category_return_summary(df)
    st.subheader("Categoryごとの平均騰落率")
    st.dataframe(dataframe_with_pct(summary), use_container_width=True)

    st.subheader("資金流入の見え方")
    metric = st.selectbox(
        "グラフ指標",
        ["change_1d_pct", "change_5bd_pct", "change_25bd_pct", "change_75bd_pct"],
        index=2,
    )
    render_category_bar(summary, metric)


def render_stock_table_tab(df: pd.DataFrame) -> None:
    display_columns = [
        "category",
        "subcategory",
        "code",
        "name",
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
    visible = df[display_columns].copy()
    st.dataframe(display_stock_table(visible), use_container_width=True, height=520)
    st.download_button(
        "CSVダウンロード",
        data=visible.to_csv(index=False).encode("utf-8-sig"),
        file_name="stock_theme_dashboard.csv",
        mime="text/csv",
    )


def render_category_summary_tab(df: pd.DataFrame) -> None:
    summary = subcategory_summary(df)
    st.dataframe(dataframe_with_pct(summary), use_container_width=True, height=560)


def render_watchlist_editor_tab() -> None:
    st.caption("保存ボタンを押すまで CSV は書き換えません。")
    current = load_watchlist(WATCHLIST_PATH)
    edited = st.data_editor(
        current,
        num_rows="dynamic",
        use_container_width=True,
        column_order=WATCHLIST_COLUMNS,
        hide_index=True,
    )

    errors = validate_watchlist(edited)
    if errors:
        st.warning("\n".join(errors))

    confirm = st.checkbox("内容を確認し、watchlist.csv を上書き保存する")
    if st.button("保存", type="primary", disabled=not confirm):
        try:
            save_watchlist(edited, WATCHLIST_PATH)
            st.cache_data.clear()
            st.success("watchlist.csv を保存しました。")
        except Exception as exc:
            st.error(f"保存に失敗しました: {exc}")


def main() -> None:
    st.title("日本株テーマ別株式ダッシュボード")
    st.caption("銘柄監視・情報整理用のローカルダッシュボードです。売買判断や自動売買機能は含みません。")

    watchlist = get_watchlist()
    if watchlist.empty:
        st.warning("watchlist.csv に銘柄がありません。Watchlist Editor で追加してください。")
        dashboard_data = pd.DataFrame()
    else:
        force_refresh = st.sidebar.button("データ更新", type="primary")
        if force_refresh:
            st.cache_data.clear()
        with st.spinner("yfinanceからデータを取得しています..."):
            dashboard_data = get_dashboard_data(watchlist.to_dict("records"), force_refresh=force_refresh)

    if dashboard_data.empty:
        tabs = st.tabs(["Watchlist Editor"])
        with tabs[0]:
            render_watchlist_editor_tab()
        return

    filtered = filter_data(dashboard_data)

    tab_dashboard, tab_table, tab_summary, tab_quality, tab_editor = st.tabs(
        ["Dashboard", "Stock Table", "Category Summary", "Data Quality", "Watchlist Editor"]
    )

    with tab_dashboard:
        render_dashboard_tab(filtered)
    with tab_table:
        render_stock_table_tab(filtered)
    with tab_summary:
        render_category_summary_tab(filtered)
    with tab_quality:
        render_data_quality(dashboard_data)
    with tab_editor:
        render_watchlist_editor_tab()


if __name__ == "__main__":
    main()
