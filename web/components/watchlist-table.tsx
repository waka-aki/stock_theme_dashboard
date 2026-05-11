import { WatchlistRow, type WatchlistEntry } from "./watchlist-row";

export function WatchlistTable({ entries }: { entries: WatchlistEntry[] }) {
  if (entries.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-zinc-300 bg-zinc-50 p-6 text-center text-sm text-zinc-600 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-400">
        まだ銘柄が登録されていません。上のフォームから追加してください。
      </p>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-zinc-200 dark:border-zinc-800">
      <table className="w-full bg-white dark:bg-zinc-950">
        <thead className="bg-zinc-50 text-left text-xs uppercase tracking-wide text-zinc-600 dark:bg-zinc-900 dark:text-zinc-400">
          <tr>
            <th className="px-3 py-2 font-medium">テーマ</th>
            <th className="px-3 py-2 font-medium">コード</th>
            <th className="px-3 py-2 font-medium">銘柄名</th>
            <th className="px-3 py-2 font-medium">メモ</th>
            <th className="px-3 py-2 text-right font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <WatchlistRow key={entry.id} entry={entry} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
