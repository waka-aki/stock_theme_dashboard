import { createClient } from "@/lib/supabase/server";
import { DashboardTable, type DashboardRow } from "@/components/dashboard-table";

type StockMetricsLatest = {
  code: string;
  fetched_at: string;
  price: number | null;
  market_cap: number | null;
  per: number | null;
  pbr: number | null;
  change_5bd: number | null;
  change_2w: number | null;
  change_1m: number | null;
  change_2m: number | null;
  change_3m: number | null;
};

export default async function DashboardPage() {
  const supabase = await createClient();

  const { data: watchlist, error: watchlistError } = await supabase
    .from("watchlist")
    .select("id, theme, code, name, note")
    .order("theme", { ascending: true })
    .order("code", { ascending: true });

  if (watchlistError) {
    return (
      <ErrorBanner message={`ウォッチリストの取得に失敗: ${watchlistError.message}`} />
    );
  }

  const codes = watchlist?.map((w) => w.code) ?? [];

  let metricsByCode = new Map<string, StockMetricsLatest>();
  let latestFetchedAt: string | null = null;

  if (codes.length > 0) {
    const { data: metrics, error: metricsError } = await supabase
      .from("stock_metrics_latest")
      .select("*")
      .in("code", codes);

    if (metricsError) {
      return (
        <ErrorBanner message={`株価データの取得に失敗: ${metricsError.message}`} />
      );
    }

    metricsByCode = new Map(
      (metrics ?? []).map((m: StockMetricsLatest) => [m.code, m]),
    );
    latestFetchedAt = (metrics ?? []).reduce<string | null>((acc, m) => {
      if (!m.fetched_at) return acc;
      return !acc || m.fetched_at > acc ? m.fetched_at : acc;
    }, null);
  }

  const rows: DashboardRow[] = (watchlist ?? []).map((w) => {
    const m = metricsByCode.get(w.code);
    return {
      id: w.id,
      theme: w.theme,
      code: w.code,
      name: w.name,
      note: w.note,
      price: m?.price ?? null,
      market_cap: m?.market_cap ?? null,
      per: m?.per ?? null,
      pbr: m?.pbr ?? null,
      change_5bd: m?.change_5bd ?? null,
      change_2w: m?.change_2w ?? null,
      change_1m: m?.change_1m ?? null,
      change_2m: m?.change_2m ?? null,
      change_3m: m?.change_3m ?? null,
    };
  });

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold">ダッシュボード</h1>
        {latestFetchedAt && (
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            最終更新: {latestFetchedAt}
          </p>
        )}
      </div>
      <DashboardTable rows={rows} />
    </div>
  );
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <p className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-600 dark:border-red-900 dark:bg-red-950 dark:text-red-400">
      {message}
    </p>
  );
}
