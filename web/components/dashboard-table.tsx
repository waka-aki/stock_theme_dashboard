import {
  formatMarketCap,
  formatPercent,
  formatPrice,
  formatRatio,
  percentClass,
} from "@/lib/format";

export type DashboardRow = {
  id: string;
  theme: string;
  code: string;
  name: string;
  note: string | null;
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

export function DashboardTable({ rows }: { rows: DashboardRow[] }) {
  if (rows.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-zinc-300 bg-zinc-50 p-6 text-center text-sm text-zinc-600 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-400">
        ウォッチリストが空です。{" "}
        <a href="/watchlist" className="underline">
          /watchlist
        </a>{" "}
        から銘柄を追加してください。
      </p>
    );
  }

  const groups = groupByTheme(rows);

  return (
    <div className="space-y-6">
      {groups.map(({ theme, rows: groupRows }) => (
        <section key={theme}>
          <h2 className="mb-2 text-lg font-semibold">{theme}</h2>
          <div className="overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
            <table className="w-full min-w-[960px] bg-white dark:bg-zinc-950">
              <thead className="bg-zinc-50 text-left text-xs uppercase tracking-wide text-zinc-600 dark:bg-zinc-900 dark:text-zinc-400">
                <tr>
                  <th className="px-3 py-2 font-medium">コード</th>
                  <th className="px-3 py-2 font-medium">銘柄名</th>
                  <th className="px-3 py-2 text-right font-medium">株価</th>
                  <th className="px-3 py-2 text-right font-medium">時価総額</th>
                  <th className="px-3 py-2 text-right font-medium">PER</th>
                  <th className="px-3 py-2 text-right font-medium">PBR</th>
                  <th className="px-3 py-2 text-right font-medium">5日</th>
                  <th className="px-3 py-2 text-right font-medium">2週</th>
                  <th className="px-3 py-2 text-right font-medium">1ヶ月</th>
                  <th className="px-3 py-2 text-right font-medium">2ヶ月</th>
                  <th className="px-3 py-2 text-right font-medium">3ヶ月</th>
                  <th className="px-3 py-2 font-medium">メモ</th>
                </tr>
              </thead>
              <tbody>
                {groupRows.map((row) => (
                  <tr
                    key={row.id}
                    className="border-t border-zinc-200 dark:border-zinc-800"
                  >
                    <td className="px-3 py-2 font-mono text-sm">{row.code}</td>
                    <td className="px-3 py-2 text-sm">{row.name}</td>
                    <td className="px-3 py-2 text-right font-mono text-sm">
                      {formatPrice(row.price)}
                    </td>
                    <td className="px-3 py-2 text-right font-mono text-sm">
                      {formatMarketCap(row.market_cap)}
                    </td>
                    <td className="px-3 py-2 text-right font-mono text-sm">
                      {formatRatio(row.per)}
                    </td>
                    <td className="px-3 py-2 text-right font-mono text-sm">
                      {formatRatio(row.pbr)}
                    </td>
                    <PercentCell value={row.change_5bd} />
                    <PercentCell value={row.change_2w} />
                    <PercentCell value={row.change_1m} />
                    <PercentCell value={row.change_2m} />
                    <PercentCell value={row.change_3m} />
                    <td className="px-3 py-2 text-sm text-zinc-600 dark:text-zinc-400">
                      {row.note}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ))}
    </div>
  );
}

function PercentCell({ value }: { value: number | null }) {
  return (
    <td
      className={`px-3 py-2 text-right font-mono text-sm ${percentClass(value)}`}
    >
      {formatPercent(value)}
    </td>
  );
}

function groupByTheme(rows: DashboardRow[]): Array<{
  theme: string;
  rows: DashboardRow[];
}> {
  const map = new Map<string, DashboardRow[]>();
  for (const row of rows) {
    const list = map.get(row.theme);
    if (list) list.push(row);
    else map.set(row.theme, [row]);
  }
  return Array.from(map.entries()).map(([theme, rows]) => ({ theme, rows }));
}
