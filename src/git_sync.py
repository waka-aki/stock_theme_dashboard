import subprocess
from pathlib import Path


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def push_watchlist(repo_root: Path, relative_path: str = "data/watchlist.csv") -> tuple[bool, str]:
    diff = _run(["git", "diff", "--quiet", "--", relative_path], repo_root)
    staged = _run(["git", "diff", "--cached", "--quiet", "--", relative_path], repo_root)
    if diff.returncode == 0 and staged.returncode == 0:
        return True, "ローカルとリモートで watchlist.csv に差分なし。push はスキップしました。"

    add = _run(["git", "add", relative_path], repo_root)
    if add.returncode != 0:
        return False, f"git add 失敗: {add.stderr.strip() or add.stdout.strip()}"

    commit = _run(["git", "commit", "-m", "Update watchlist via dashboard"], repo_root)
    if commit.returncode != 0:
        message = (commit.stderr + commit.stdout).lower()
        if "nothing to commit" in message:
            return True, "コミット対象なし。push はスキップしました。"
        return False, f"git commit 失敗: {commit.stderr.strip() or commit.stdout.strip()}"

    push = _run(["git", "push"], repo_root)
    if push.returncode != 0:
        return False, f"git push 失敗: {push.stderr.strip() or push.stdout.strip()}"

    return True, "GitHub に push 完了。Actions が起動します。"
