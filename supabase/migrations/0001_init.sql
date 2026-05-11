-- 日本株テーマ別ダッシュボード 初期スキーマ
-- Supabase の SQL Editor で実行してください。

-- =========================================================
-- 1. 銘柄ウォッチリスト
-- =========================================================
create table watchlist (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid references auth.users not null,
  theme       text not null,
  code        text not null,
  name        text not null,
  note        text,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  unique (user_id, code)
);

create index watchlist_user_id_idx on watchlist (user_id);

-- updated_at を自動更新するトリガー
create or replace function set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger watchlist_set_updated_at
  before update on watchlist
  for each row execute function set_updated_at();

-- =========================================================
-- 2. 日次の株価・指標履歴
-- =========================================================
create table stock_metrics (
  code        text not null,
  fetched_at  date not null,
  price       numeric,
  market_cap  numeric,
  per         numeric,
  pbr         numeric,
  change_5bd  numeric,   -- 5営業日（取引日ベース）
  change_2w   numeric,   -- 2週間（カレンダー）
  change_1m   numeric,   -- 1か月（カレンダー）
  change_2m   numeric,   -- 2か月（カレンダー）
  change_3m   numeric,   -- 3か月（カレンダー）
  primary key (code, fetched_at)
);

create index stock_metrics_fetched_at_idx on stock_metrics (fetched_at desc);

-- =========================================================
-- 3. 最新値ビュー（ダッシュボード表示用）
-- =========================================================
create view stock_metrics_latest as
  select distinct on (code) *
  from stock_metrics
  order by code, fetched_at desc;

-- =========================================================
-- 4. Row Level Security
-- =========================================================

-- watchlist: 本人のみ全操作可能
alter table watchlist enable row level security;

create policy "watchlist_select_own"
  on watchlist for select
  using (auth.uid() = user_id);

create policy "watchlist_insert_own"
  on watchlist for insert
  with check (auth.uid() = user_id);

create policy "watchlist_update_own"
  on watchlist for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "watchlist_delete_own"
  on watchlist for delete
  using (auth.uid() = user_id);

-- stock_metrics: 認証済みユーザーが読み取り可能（公開情報のため）
-- 書き込みは service_role キー経由（GitHub Actions）のみ。RLSをバイパスできるので INSERT/UPDATE ポリシーは不要。
alter table stock_metrics enable row level security;

create policy "stock_metrics_select_authenticated"
  on stock_metrics for select
  to authenticated
  using (true);
