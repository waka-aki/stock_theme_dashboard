# 日本株テーマ別株式ダッシュボード

自分で分類した日本株のテーマ別ウォッチリストを、Webブラウザから一覧確認・編集できるダッシュボードです。株価、時価総額、PER、PBR、短期・中期の騰落率を1画面で整理します。

このダッシュボードは投資助言ではありません。銘柄監視・情報整理を目的としたツールです。

## アーキテクチャ

```text
[ブラウザ]
    ↓ HTTPS
[Vercel: Next.js + TypeScript] ─── SDK ──→ [Supabase]
                                             ├ Auth (Email/Password)
                                             └ Postgres
                                                  ↑ upsert
[GitHub Actions: Python + yfinance] ─────────────┘
   平日 17:30 JST に定期実行
```

3コンポーネントで構成します。

- **Next.js (Vercel)**: ブラウザUI。ダッシュボード表示と銘柄編集
- **Supabase**: 認証とDB（Postgres）
- **GitHub Actions (Python)**: yfinanceで株価・指標を取得し、Supabaseへ書き込み

## ディレクトリ構成

```text
stock_theme_dashboard/
├── web/                          # Next.js（Vercel デプロイ対象）
│   ├── app/
│   │   ├── (auth)/
│   │   │   └── login/page.tsx
│   │   ├── (app)/
│   │   │   ├── page.tsx          # / = ダッシュボード
│   │   │   └── watchlist/page.tsx
│   │   └── layout.tsx
│   ├── middleware.ts             # 未ログイン時のリダイレクト
│   ├── components/
│   │   ├── ui/                   # shadcn/ui
│   │   ├── dashboard-table.tsx
│   │   └── watchlist-editor.tsx
│   ├── lib/supabase/
│   │   ├── client.ts
│   │   └── server.ts
│   ├── package.json
│   └── tsconfig.json
├── jobs/                         # 定期取得ジョブ
│   ├── fetch_metrics.py
│   └── requirements.txt
├── supabase/
│   └── migrations/
│       └── 0001_init.sql
├── .github/workflows/
│   └── update-metrics.yml
├── .env.example
└── README.md
```

## DBスキーマ

```sql
-- 銘柄ウォッチリスト
create table watchlist (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid references auth.users not null,
  theme       text not null,
  code        text not null,        -- 4桁日本株コード
  name        text not null,
  note        text,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now(),
  unique (user_id, code)
);

-- 日次の株価・指標履歴
create table stock_metrics (
  code        text not null,
  fetched_at  date not null,
  price       numeric,
  market_cap  numeric,
  per         numeric,
  pbr         numeric,
  change_5bd  numeric,  -- 5営業日（取引日ベース）
  change_2w   numeric,  -- 2週間（カレンダー）
  change_1m   numeric,  -- 1か月（カレンダー）
  change_2m   numeric,  -- 2か月（カレンダー）
  change_3m   numeric,  -- 3か月（カレンダー）
  primary key (code, fetched_at)
);

-- 最新値を取り出すビュー（ダッシュボード表示用）
create view stock_metrics_latest as
  select distinct on (code) *
  from stock_metrics
  order by code, fetched_at desc;

-- RLS
alter table watchlist enable row level security;
create policy "own rows" on watchlist
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

alter table stock_metrics enable row level security;
create policy "read all" on stock_metrics for select using (true);
```

## ページ構成

| Path | 内容 |
|------|------|
| `/login` | Supabase Auth でログイン |
| `/` | ダッシュボード（テーマ別の株価表） |
| `/watchlist` | 銘柄の追加・編集・削除 |

## セットアップ

### Supabase

1. https://supabase.com で新規プロジェクトを作成
2. SQL Editor で `supabase/migrations/0001_init.sql` を実行
3. Authentication → Email で自分用ユーザーを作成
4. プロジェクトの URL / anon key / service_role key を控える

### Web (Next.js)

```bash
cd web
npm install
cp ../.env.example .env.local
# .env.local を編集して Supabase の URL と anon key を設定
npm run dev
```

ブラウザで `http://localhost:3000` を開きます。

### Vercel デプロイ

1. リポジトリを GitHub へ push
2. Vercel で New Project → ルートに `web` ディレクトリを指定
3. 環境変数 `NEXT_PUBLIC_SUPABASE_URL` と `NEXT_PUBLIC_SUPABASE_ANON_KEY` を設定
4. デプロイ

### 定期取得ジョブ

GitHub Repository の Settings → Secrets で以下を設定します。

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

ワークフロー `.github/workflows/update-metrics.yml` が平日 17:30 JST に自動実行されます。手動実行も Actions タブから可能です。

## 環境変数

| 名前 | 設定場所 | 用途 |
|------|----------|------|
| `NEXT_PUBLIC_SUPABASE_URL` | Vercel / `.env.local` | フロントから接続 |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Vercel / `.env.local` | フロントから接続（RLSで保護） |
| `SUPABASE_URL` | GitHub Secrets | ジョブから接続 |
| `SUPABASE_SERVICE_ROLE_KEY` | GitHub Secrets | RLS を無視してジョブから書き込み |

## 銘柄の追加

`/watchlist` ページからブラウザ上で追加・編集・削除できます。CSVファイルの直接編集は不要です。

入力する `code` は4桁の日本株コードです。yfinance への問い合わせ時にジョブ側で `.T` を自動付与します。

## 実装ロードマップ

| Phase | 内容 |
|-------|------|
| 1 | Supabase プロジェクト作成、DBスキーマ反映 |
| 2 | Next.js 初期化、Vercel デプロイ（空画面でOK） |
| 3 | Supabase Auth ログイン |
| 4 | ダッシュボード表（`stock_metrics_latest` ビュー使用） |
| 5 | Watchlist Editor |
| 6 | yfinance ジョブ + GitHub Actions 化 |
| 7 | 任意: ソート、フィルタ、銘柄チャート、ニュース |

## 注意点

- yfinance では日本株のファンダメンタルデータが欠損することがあります。PER、PBR、時価総額が取得できない場合は欠損値として表示します。
- yfinance を公開サービスで利用することは規約上グレーな領域があるため、Supabase Auth で本人のみアクセスできる構成を維持します。

## 将来的な拡張案

- J-Quants API 対応
- ニュース取得
- 銘柄ごとの株価チャート（保存済み `stock_metrics` 履歴を使用）
- 決算発表日や適時開示の取得
- セクターごとのヒートマップ表示
