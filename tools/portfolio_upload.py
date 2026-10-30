"""Encrypt the daily holdings files and publish them to the dashboard repo.

Runs on the Windows PC that produces the files. It reads ONLY
  <SOURCE_DIR>/sj_YYYYMMDD.json   and   <SOURCE_DIR>/reports/YYYY-MM-DD.md
and never opens sj.env or any other file. Each day is encrypted with
AES-256-GCM using a key derived from PORTFOLIO_PASSWORD (PBKDF2-SHA256), so the
public repository only ever holds ciphertext:

  data/portfolio/index.json        {v, kdf:{salt, iter}, check:{iv, ct}, days:[...]}
  data/portfolio/YYYY-MM-DD.json   {v, iv, ct}   plaintext = {date, sj, report}

Settings come from portfolio_upload.env next to this script (KEY=value lines):
  GITHUB_TOKEN        fine-grained token, Contents read/write on the repo only
  PORTFOLIO_PASSWORD  the password typed on the website
  SOURCE_DIR          folder holding sj_*.json and reports\\  (the "output" folder)
  REPO                optional, default yujie0212/tw-stock-dashboard
  DAYS                optional, how many recent days to keep in sync, default 30

Usage:
  python portfolio_upload.py              upload new or recently changed days
  python portfolio_upload.py --all        re-upload every day within DAYS
  python portfolio_upload.py --out DIR    write the encrypted files to DIR instead of GitHub
Requires: pip install cryptography
"""
import argparse
import base64
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITERATIONS = 600_000
CHECK_TEXT = b'"tw-portfolio"'
PREFIX = "data/portfolio/"
RECENT_DAYS = 3  # days whose files may still be rewritten (re-runs overwrite the same date)


def b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def derive(password: str, salt: bytes, iterations: int) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations)
    return kdf.derive(password.encode("utf-8"))


def seal(key: bytes, plain: bytes) -> dict:
    iv = os.urandom(12)
    return {"iv": b64(iv), "ct": b64(AESGCM(key).encrypt(iv, plain, None))}


def unseal(key: bytes, box: dict) -> bytes:
    return AESGCM(key).decrypt(base64.b64decode(box["iv"]), base64.b64decode(box["ct"]), None)


def load_settings(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"找不到設定檔 {path}")
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"')
    for need in ("PORTFOLIO_PASSWORD", "SOURCE_DIR"):
        if not out.get(need):
            sys.exit(f"設定檔缺少 {need}")
    return out


def local_days(source: Path, keep: int) -> dict:
    """date -> {"sj": Path|None, "report": Path|None} for the most recent `keep` dates."""
    days: dict = {}
    for f in source.glob("sj_*.json"):
        m = re.fullmatch(r"sj_(\d{4})(\d{2})(\d{2})\.json", f.name)
        if m:
            days.setdefault(f"{m[1]}-{m[2]}-{m[3]}", {"sj": None, "report": None})["sj"] = f
    reports = source / "reports"
    if reports.is_dir():
        for f in reports.glob("*.md"):
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", f.name):
                days.setdefault(f.stem, {"sj": None, "report": None})["report"] = f
    return {d: days[d] for d in sorted(days)[-keep:]}


def payload(date: str, files: dict) -> bytes:
    sj = json.loads(files["sj"].read_text(encoding="utf-8")) if files["sj"] else None
    if sj is not None:
        sj.pop("diag", None)  # debugging details are not needed on the site
    report = files["report"].read_text(encoding="utf-8") if files["report"] else None
    return json.dumps({"date": date, "sj": sj, "report": report}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class GitHub:
    def __init__(self, repo: str, token: str):
        self.base = f"https://api.github.com/repos/{repo}"
        self.token = token

    def call(self, method: str, path: str, body=None):
        req = urllib.request.Request(self.base + path, method=method,
                                     data=None if body is None else json.dumps(body).encode("utf-8"))
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise RuntimeError(f"GitHub {method} {path} 失敗：{e.code} {e.read()[:300]!r}") from None

    def read_json(self, path: str):
        meta = self.call("GET", f"/contents/{path}?ref=main")
        return None if meta is None else json.loads(base64.b64decode(meta["content"]))

    def listing(self, path: str) -> set:
        items = self.call("GET", f"/contents/{path}?ref=main") or []
        return {i["name"] for i in items if isinstance(i, dict)}

    def commit(self, files: dict, message: str) -> None:
        """One commit with all files; retried when the backend pushes in between."""
        for attempt in range(4):
            head = self.call("GET", "/git/ref/heads/main")["object"]["sha"]
            base_tree = self.call("GET", f"/git/commits/{head}")["tree"]["sha"]
            tree = self.call("POST", "/git/trees", {"base_tree": base_tree, "tree": [
                {"path": p, "mode": "100644", "type": "blob", "content": c} for p, c in files.items()]})
            new = self.call("POST", "/git/commits", {"message": message, "tree": tree["sha"], "parents": [head]})
            try:
                self.call("PATCH", "/git/refs/heads/main", {"sha": new["sha"]})
                return
            except RuntimeError:
                if attempt == 3:
                    raise
                time.sleep(2 * (attempt + 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=str(Path(__file__).with_name("portfolio_upload.env")))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", help="write files to this folder instead of GitHub")
    args = ap.parse_args()

    cfg = load_settings(Path(args.env))
    password, source = cfg["PORTFOLIO_PASSWORD"], Path(cfg["SOURCE_DIR"])
    keep = int(cfg.get("DAYS", "30"))
    gh = None if args.out else GitHub(cfg.get("REPO", "yujie0212/tw-stock-dashboard"), cfg.get("GITHUB_TOKEN", ""))
    if gh and not cfg.get("GITHUB_TOKEN"):
        sys.exit("設定檔缺少 GITHUB_TOKEN")

    if args.out:
        out_dir = Path(args.out)
        old = json.loads((out_dir / "index.json").read_text(encoding="utf-8")) if (out_dir / "index.json").exists() else None
        remote = {p.name for p in out_dir.glob("*.json")} if out_dir.exists() else set()
    else:
        old = gh.read_json(PREFIX + "index.json")
        remote = gh.listing(PREFIX.rstrip("/"))

    if old:
        salt, iterations = base64.b64decode(old["kdf"]["salt"]), int(old["kdf"]["iter"])
        key = derive(password, salt, iterations)
        try:
            unseal(key, old["check"])
        except Exception:
            sys.exit("密碼和網站上現有資料的密碼不同，已停止。要換密碼請先刪除 data/portfolio/ 再重新上傳。")
        check = old["check"]
    else:
        salt, iterations = os.urandom(16), ITERATIONS
        key = derive(password, salt, iterations)
        check = seal(key, CHECK_TEXT)

    days = local_days(source, keep)
    today = dt.date.today()
    files = {}
    for date, f in days.items():
        recent = (today - dt.date.fromisoformat(date)).days <= RECENT_DAYS
        if args.all or recent or f"{date}.json" not in remote:
            files[PREFIX + f"{date}.json"] = json.dumps({"v": 1, **seal(key, payload(date, f))})
    known = set(old["days"]) if old else set()
    manifest = {"v": 1, "kdf": {"name": "PBKDF2-SHA256", "salt": b64(salt), "iter": iterations}, "check": check,
                "days": sorted(known | set(days))}
    files[PREFIX + "index.json"] = json.dumps(manifest, indent=1)

    if args.out:
        out_dir.mkdir(parents=True, exist_ok=True)
        for path, content in files.items():
            (out_dir / path[len(PREFIX):]).write_text(content, encoding="utf-8")
        print(f"已寫入 {len(files) - 1} 天到 {out_dir}")
        return
    gh.commit(files, f"Portfolio data {max(days) if days else ''} (encrypted)")
    print(f"已上傳 {len(files) - 1} 天的加密持股資料")


if __name__ == "__main__":
    main()
