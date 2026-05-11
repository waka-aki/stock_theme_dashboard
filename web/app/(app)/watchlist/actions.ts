"use server";

import { revalidatePath } from "next/cache";
import { createClient } from "@/lib/supabase/server";

export type WatchlistActionState = {
  error?: string;
  success?: boolean;
} | null;

const CODE_PATTERN = /^\d{4}$/;

function readField(formData: FormData, key: string): string {
  return String(formData.get(key) ?? "").trim();
}

export async function createWatchlistEntry(
  _prevState: WatchlistActionState,
  formData: FormData,
): Promise<WatchlistActionState> {
  const theme = readField(formData, "theme");
  const code = readField(formData, "code");
  const name = readField(formData, "name");
  const note = readField(formData, "note");

  if (!theme || !code || !name) {
    return { error: "テーマ、コード、銘柄名は必須です。" };
  }
  if (!CODE_PATTERN.test(code)) {
    return { error: "コードは4桁の数字で入力してください。" };
  }

  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { error: "ログインしてください。" };

  const { error } = await supabase.from("watchlist").insert({
    user_id: user.id,
    theme,
    code,
    name,
    note: note || null,
  });

  if (error) {
    if (error.code === "23505") {
      return { error: "そのコードはすでに登録済みです。" };
    }
    return { error: error.message };
  }

  revalidatePath("/watchlist");
  revalidatePath("/");
  return { success: true };
}

export async function updateWatchlistEntry(
  id: string,
  _prevState: WatchlistActionState,
  formData: FormData,
): Promise<WatchlistActionState> {
  const theme = readField(formData, "theme");
  const code = readField(formData, "code");
  const name = readField(formData, "name");
  const note = readField(formData, "note");

  if (!theme || !code || !name) {
    return { error: "テーマ、コード、銘柄名は必須です。" };
  }
  if (!CODE_PATTERN.test(code)) {
    return { error: "コードは4桁の数字で入力してください。" };
  }

  const supabase = await createClient();
  const { error } = await supabase
    .from("watchlist")
    .update({ theme, code, name, note: note || null })
    .eq("id", id);

  if (error) {
    if (error.code === "23505") {
      return { error: "そのコードはすでに登録済みです。" };
    }
    return { error: error.message };
  }

  revalidatePath("/watchlist");
  revalidatePath("/");
  return { success: true };
}

export async function deleteWatchlistEntry(id: string): Promise<void> {
  const supabase = await createClient();
  await supabase.from("watchlist").delete().eq("id", id);
  revalidatePath("/watchlist");
  revalidatePath("/");
}
