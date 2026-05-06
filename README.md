# 日本株テーマ別株式ダッシュボード

自分で分類した日本株のテーマ別ウォッチリストを、Streamlitで一覧確認するためのローカル用ダッシュボードです。株価、時価総額、PER、PBR、ROE、ROIC、短期・中期の騰落率を1画面で整理します。

このダッシュボードは投資助言ではありません。銘柄監視・情報整理を目的としたツールです。

## ディレクトリ構成

```text
stock_theme_dashboard/
  app.py
  requirements.txt
  README.md
  .env.example
  data/
    watchlist.csv
  src/
    __init__.py
    config.py
    data_loader.py
    git_sync.py
    metrics.py
    ui.py
    providers/
      __init__.py
      base.py
      yfinance_provider.py
```

## セットアップ方法

既存の `stock_list` 仮想環境を使います。

```bash
source stock_list/bin/activate
pip install -r stock_theme_dashboard/requirements.txt
```

必要に応じて `.env.example` を `.env` にコピーし、キャッシュTTLなどを変更できます。

## 実行方法

```bash
streamlit run app.py
```

ブラウザでStreamlitのローカルURLを開くとダッシュボードを操作できます。

## GitHub Actionsでの定時更新

株価データはGitHub Actionsで平日17:30（JST）に自動更新できます。ワークフローは `.github/workflows/update-dashboard-data.yml` にあります。

Actionsでは以下を実行します。

- `data/watchlist.csv` を読み込む
- yfinanceから株価・指標を取得する
- `data/dashboard_data.csv` を更新する
- 変更があればGitHub Actions botでコミットする

手動で同じ更新を実行したい場合は、GitHubのActions画面から `Update dashboard data` を選び、`Run workflow` を押してください。

取得結果は `data/dashboard_data.csv` に保存されます。アプリはこの保存済みデータを優先して表示します。`watchlist.csv` を編集した場合は、古い保存済みデータを使わずに再取得します。

アプリ内の `Watchlist Editor` で銘柄やセクターを編集できます。保存ボタンを押すと、ローカルの `data/watchlist.csv` を更新したうえで自動的に GitHub へ push します。push をトリガに上記ワークフローが走り、`dashboard_data.csv` が即時に更新されます。

push にはローカルの git 認証情報（PAT もしくは SSH キー）が必要です。push に失敗した場合はターミナルで `git push` を手動実行してください。

## watchlist.csv の編集方法

`data/watchlist.csv` は以下の列で管理します。

```csv
category,subcategory,code,name,note
半導体,製造装置,8035,東京エレクトロン,
```

`code` は4桁の日本株コードを入力してください。yfinanceで取得する際はアプリ側で自動的に `.T` を付けます。

## Watchlist Editor の使い方

アプリ内の `Watchlist Editor` タブで `data/watchlist.csv` を編集できます。

- 銘柄の追加・削除
- category / subcategory / code / name / note の変更
- 保存前のバリデーション
- 確認チェックボックスを入れた後の保存
- 保存後のキャッシュクリアとダッシュボード反映

保存ボタンを押すまではCSVは書き換えられません。

## 注意点

yfinanceでは日本株のファンダメンタルデータが欠損することがあります。PER、PBR、ROE、時価総額が取得できない場合は欠損値として表示します。

ROICはyfinanceから安定取得しにくいため、現時点では `NaN` としています。将来的に手入力CSVやJ-Quants APIから補完する想定です。

## 将来的な拡張案

- J-Quants API対応
- ROIC計算
- ニュース取得
- 株価チャート追加
- GitHub Actionsによる自動更新
- 決算発表日や適時開示の取得
- セクターごとのヒートマップ表示
