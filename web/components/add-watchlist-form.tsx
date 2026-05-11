"use client";

import { useActionState, useEffect, useRef } from "react";
import {
  createWatchlistEntry,
  type WatchlistActionState,
} from "@/app/(app)/watchlist/actions";

const initialState: WatchlistActionState = null;

export function AddWatchlistForm() {
  const [state, formAction, pending] = useActionState(
    createWatchlistEntry,
    initialState,
  );
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (state?.success && formRef.current) {
      formRef.current.reset();
    }
  }, [state]);

  return (
    <form
      ref={formRef}
      action={formAction}
      className="space-y-3 rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950"
    >
      <h2 className="text-sm font-semibold">銘柄を追加</h2>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <Field label="テーマ" name="theme" placeholder="例: 半導体" required />
        <Field label="コード" name="code" placeholder="4桁" required />
        <Field label="銘柄名" name="name" placeholder="例: トヨタ自動車" required />
        <Field label="メモ" name="note" placeholder="任意" />
      </div>
      {state?.error && (
        <p className="text-sm text-red-600 dark:text-red-400">{state.error}</p>
      )}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={pending}
          className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
        >
          {pending ? "追加中..." : "追加"}
        </button>
      </div>
    </form>
  );
}

function Field({
  label,
  name,
  placeholder,
  required,
}: {
  label: string;
  name: string;
  placeholder?: string;
  required?: boolean;
}) {
  return (
    <label className="space-y-1 text-sm">
      <span className="block font-medium">
        {label}
        {required && <span className="text-red-500"> *</span>}
      </span>
      <input
        type="text"
        name={name}
        placeholder={placeholder}
        required={required}
        className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
      />
    </label>
  );
}
