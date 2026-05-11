import { createClient } from "@/lib/supabase/server";
import { AddWatchlistForm } from "@/components/add-watchlist-form";
import { WatchlistTable } from "@/components/watchlist-table";
import type { WatchlistEntry } from "@/components/watchlist-row";

export default async function WatchlistPage() {
  const supabase = await createClient();
  const { data, error } = await supabase
    .from("watchlist")
    .select("id, theme, code, name, note")
    .order("theme", { ascending: true })
    .order("code", { ascending: true });

  const entries: WatchlistEntry[] = data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Watchlist Editor</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          ダッシュボードに表示する銘柄を管理します。
        </p>
      </div>

      <AddWatchlistForm />

      {error ? (
        <p className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-600 dark:border-red-900 dark:bg-red-950 dark:text-red-400">
          銘柄の取得に失敗しました: {error.message}
        </p>
      ) : (
        <WatchlistTable entries={entries} />
      )}
    </div>
  );
}
