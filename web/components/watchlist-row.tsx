"use client";

import { useActionState, useEffect, useState, useTransition } from "react";
import {
  deleteWatchlistEntry,
  updateWatchlistEntry,
  type WatchlistActionState,
} from "@/app/(app)/watchlist/actions";

export type WatchlistEntry = {
  id: string;
  theme: string;
  code: string;
  name: string;
  note: string | null;
};

const initialState: WatchlistActionState = null;

export function WatchlistRow({ entry }: { entry: WatchlistEntry }) {
  const [isEditing, setIsEditing] = useState(false);

  const updateAction = updateWatchlistEntry.bind(null, entry.id);
  const [state, formAction, pending] = useActionState(
    updateAction,
    initialState,
  );

  const [isDeleting, startDelete] = useTransition();

  useEffect(() => {
    if (state?.success) setIsEditing(false);
  }, [state]);

  function handleDelete() {
    if (!confirm(`「${entry.name}」(${entry.code}) を削除しますか?`)) return;
    startDelete(async () => {
      await deleteWatchlistEntry(entry.id);
    });
  }

  if (isEditing) {
    return (
      <tr className="border-t border-zinc-200 dark:border-zinc-800">
        <td colSpan={5} className="px-3 py-3">
          <form action={formAction} className="space-y-2">
            <div className="grid grid-cols-1 gap-2 md:grid-cols-4">
              <EditField name="theme" defaultValue={entry.theme} required />
              <EditField name="code" defaultValue={entry.code} required />
              <EditField name="name" defaultValue={entry.name} required />
              <EditField name="note" defaultValue={entry.note ?? ""} />
            </div>
            {state?.error && (
              <p className="text-sm text-red-600 dark:text-red-400">
                {state.error}
              </p>
            )}
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="rounded-md border border-zinc-300 px-3 py-1 text-sm hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900"
              >
                キャンセル
              </button>
              <button
                type="submit"
                disabled={pending}
                className="rounded-md bg-zinc-900 px-3 py-1 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
              >
                {pending ? "保存中..." : "保存"}
              </button>
            </div>
          </form>
        </td>
      </tr>
    );
  }

  return (
    <tr className="border-t border-zinc-200 dark:border-zinc-800">
      <td className="px-3 py-2 text-sm">{entry.theme}</td>
      <td className="px-3 py-2 font-mono text-sm">{entry.code}</td>
      <td className="px-3 py-2 text-sm">{entry.name}</td>
      <td className="px-3 py-2 text-sm text-zinc-600 dark:text-zinc-400">
        {entry.note}
      </td>
      <td className="px-3 py-2 text-right text-sm">
        <div className="flex justify-end gap-2">
          <button
            onClick={() => setIsEditing(true)}
            className="rounded-md border border-zinc-300 px-2 py-1 hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900"
          >
            編集
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="rounded-md border border-red-300 px-2 py-1 text-red-600 hover:bg-red-50 disabled:opacity-50 dark:border-red-900 dark:text-red-400 dark:hover:bg-red-950"
          >
            {isDeleting ? "削除中..." : "削除"}
          </button>
        </div>
      </td>
    </tr>
  );
}

function EditField({
  name,
  defaultValue,
  required,
}: {
  name: string;
  defaultValue: string;
  required?: boolean;
}) {
  return (
    <input
      type="text"
      name={name}
      defaultValue={defaultValue}
      required={required}
      className="w-full rounded-md border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-900"
    />
  );
}
