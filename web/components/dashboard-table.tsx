"use client";

import { useMemo, useState } from "react";
import {
  formatMarketCap,
  formatPercent,
  formatPrice,
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
  change_1bd: number | null;
  change_2bd: number | null;
  change_3bd: number | null;
  change_5bd: number | null;
  change_2w: number | null;
  change_1m: number | null;
  change_2m: number | null;
  change_3m: number | null;
};

type SortKey = keyof DashboardRow;
type SortDir = "asc" | "desc";

type Column = {
  key: SortKey;
  label: string;
  align: "left" | "right";
  sortable: boolean;
};

const COLUMNS: Column[] = [
  { key: "theme", label: "テーマ", align: "left", sortable: true },
  { key: "code", label: "コード", align: "left", sortable: true },
  { key: "name", label: "銘柄名", align: "left", sortable: true },
  { key: "price", label: "株価", align: "right", sortable: true },
  { key: "market_cap", label: "時価総額(yf)", align: "right", sortable: true },
  { key: "change_1bd", label: "1日", align: "right", sortable: true },
  { key: "change_2bd", label: "2日", align: "right", sortable: true },
  { key: "change_3bd", label: "3日", align: "right", sortable: true },
  { key: "change_5bd", label: "5日", align: "right", sortable: true },
  { key: "change_2w", label: "2週", align: "right", sortable: true },
  { key: "change_1m", label: "1ヶ月", align: "right", sortable: true },
  { key: "change_2m", label: "2ヶ月", align: "right", sortable: true },
  { key: "change_3m", label: "3ヶ月", align: "right", sortable: true },
  { key: "note", label: "メモ", align: "left", sortable: false },
];

export function DashboardTable({ rows }: { rows: DashboardRow[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("theme");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const sortedRows = useMemo(
    () => [...rows].sort(makeComparator(sortKey, sortDir)),
    [rows, sortKey, sortDir],
  );

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

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
      <table className="w-full min-w-[1400px] bg-white dark:bg-zinc-950">
        <thead className="bg-zinc-50 text-xs uppercase tracking-wide text-zinc-600 dark:bg-zinc-900 dark:text-zinc-400">
          <tr>
            {COLUMNS.map((col) => (
              <HeaderCell
                key={col.key}
                column={col}
                isActive={sortKey === col.key}
                direction={sortDir}
                onSort={handleSort}
              />
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedRows.map((row) => (
            <tr
              key={row.id}
              className="border-t border-zinc-200 dark:border-zinc-800"
            >
              <td className="whitespace-nowrap px-3 py-2 text-sm">
                {row.theme}
              </td>
              <td className="whitespace-nowrap px-3 py-2 font-mono text-sm">
                {row.code}
              </td>
              <td className="whitespace-nowrap px-3 py-2 text-sm">
                {row.name}
              </td>
              <td className="whitespace-nowrap px-3 py-2 text-right font-mono text-sm">
                {formatPrice(row.price)}
              </td>
              <td className="whitespace-nowrap px-3 py-2 text-right font-mono text-sm">
                {formatMarketCap(row.market_cap)}
              </td>
              <PercentCell value={row.change_1bd} />
              <PercentCell value={row.change_2bd} />
              <PercentCell value={row.change_3bd} />
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
  );
}

function HeaderCell({
  column,
  isActive,
  direction,
  onSort,
}: {
  column: Column;
  isActive: boolean;
  direction: SortDir;
  onSort: (key: SortKey) => void;
}) {
  const alignClass = column.align === "right" ? "text-right" : "text-left";

  if (!column.sortable) {
    return (
      <th
        className={`whitespace-nowrap px-3 py-2 font-medium ${alignClass}`}
      >
        {column.label}
      </th>
    );
  }

  const arrow = isActive ? (direction === "asc" ? "↑" : "↓") : "";

  return (
    <th className={`whitespace-nowrap px-3 py-2 ${alignClass}`}>
      <button
        type="button"
        onClick={() => onSort(column.key)}
        className={`flex w-full items-center gap-1 font-medium hover:text-zinc-900 dark:hover:text-zinc-100 ${
          column.align === "right" ? "justify-end" : "justify-start"
        } ${isActive ? "text-zinc-900 dark:text-zinc-100" : ""}`}
      >
        <span>{column.label}</span>
        <span className="w-3 text-xs">{arrow}</span>
      </button>
    </th>
  );
}

function PercentCell({ value }: { value: number | null }) {
  return (
    <td
      className={`whitespace-nowrap px-3 py-2 text-right font-mono text-sm ${percentClass(value)}`}
    >
      {formatPercent(value)}
    </td>
  );
}

function makeComparator(key: SortKey, dir: SortDir) {
  const factor = dir === "asc" ? 1 : -1;
  return (a: DashboardRow, b: DashboardRow): number => {
    const primary = compareValues(a[key], b[key]) * factor;
    if (primary !== 0) return primary;
    if (key === "code") return 0;
    return String(a.code).localeCompare(String(b.code));
  };
}

function compareValues(
  a: string | number | null,
  b: string | number | null,
): number {
  if (a == null && b == null) return 0;
  if (a == null) return 1;
  if (b == null) return -1;
  if (typeof a === "number" && typeof b === "number") return a - b;
  return String(a).localeCompare(String(b), "ja");
}
