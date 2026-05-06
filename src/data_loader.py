from pathlib import Path
import re

import pandas as pd


WATCHLIST_COLUMNS = ["category", "subcategory", "code", "name", "note"]


def normalize_code(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    digits = re.sub(r"\D", "", text)
    return digits.zfill(4) if digits else ""


def load_watchlist(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=WATCHLIST_COLUMNS)

    df = pd.read_csv(path, dtype=str).fillna("")
    for column in WATCHLIST_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[WATCHLIST_COLUMNS].copy()
    df["code"] = df["code"].map(normalize_code)
    return df


def load_dashboard_snapshot(path: Path, watchlist_path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    if watchlist_path.exists() and path.stat().st_mtime < watchlist_path.stat().st_mtime:
        return None

    df = pd.read_csv(path, dtype={"code": str})
    if "code" in df.columns:
        df["code"] = df["code"].map(normalize_code)
    for column in ["category", "subcategory", "name", "data_status"]:
        if column in df.columns:
            df[column] = df[column].fillna("")
    return df


def save_dashboard_snapshot(df: pd.DataFrame, path: Path) -> None:
    output = df.copy()
    if "code" in output.columns:
        output["code"] = output["code"].map(normalize_code)

    path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(path, index=False, encoding="utf-8")


def validate_watchlist(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required_columns = ["category", "code", "name"]

    for column in WATCHLIST_COLUMNS:
        if column not in df.columns:
            errors.append(f"{column} 列がありません。")

    if errors:
        return errors

    normalized = df.copy().fillna("")
    normalized["code"] = normalized["code"].map(normalize_code)

    for index, row in normalized.iterrows():
        row_no = index + 1
        for column in required_columns:
            if str(row[column]).strip() == "":
                errors.append(f"{row_no}行目: {column} が空です。")
        if not re.fullmatch(r"\d{4}", str(row["code"]).strip()):
            errors.append(f"{row_no}行目: code は4桁の数字にしてください。")

    duplicated = normalized["code"][normalized["code"].duplicated() & normalized["code"].ne("")]
    if not duplicated.empty:
        codes = ", ".join(sorted(duplicated.unique()))
        errors.append(f"重複する code があります: {codes}")

    return errors


def save_watchlist(df: pd.DataFrame, path: Path) -> None:
    errors = validate_watchlist(df)
    if errors:
        raise ValueError("\n".join(errors))

    output = df.copy().fillna("")
    for column in WATCHLIST_COLUMNS:
        if column not in output.columns:
            output[column] = ""
    output = output[WATCHLIST_COLUMNS]
    output["code"] = output["code"].map(normalize_code)

    path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(path, index=False, encoding="utf-8")
