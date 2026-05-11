const OKU = 100_000_000;
const CHO = 1_000_000_000_000;

export function formatPrice(n: number | null | undefined): string {
  if (n == null) return "—";
  return `¥${n.toLocaleString("ja-JP", { maximumFractionDigits: 1 })}`;
}

export function formatMarketCap(n: number | null | undefined): string {
  if (n == null) return "—";
  if (n >= CHO) return `${(n / CHO).toFixed(2)}兆`;
  if (n >= OKU) return `${Math.round(n / OKU).toLocaleString("ja-JP")}億`;
  return n.toLocaleString("ja-JP");
}

export function formatRatio(n: number | null | undefined): string {
  if (n == null) return "—";
  return n.toFixed(2);
}

export function formatPercent(n: number | null | undefined): string {
  if (n == null) return "—";
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(2)}%`;
}

// 日本株の慣例: 赤=上昇 / 緑=下落。Western 風に逆転したい場合はこの2行を入れ替え。
const UP_CLASS = "text-red-600 dark:text-red-400";
const DOWN_CLASS = "text-green-600 dark:text-green-400";

export function percentClass(n: number | null | undefined): string {
  if (n == null || n === 0) return "text-zinc-500 dark:text-zinc-500";
  return n > 0 ? UP_CLASS : DOWN_CLASS;
}
