"""Check the supplied PR ticket versions against live remote branch names."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


RELEASE = re.compile(r"release/v?([0-9]+)\.([0-9]+)\.([0-9]+)")


def check_versions(data, branches):
    if not isinstance(data, dict):
        raise ValueError("輸入必須是 JSON object")
    base = data.get("base")
    if not isinstance(base, str) or base not in branches:
        raise ValueError("base 必須是存在遠端的完整分支")
    match = RELEASE.fullmatch(base)
    if base == "main":
        versions = [
            tuple(map(int, m.groups()))
            for branch in branches
            if (m := RELEASE.fullmatch(branch))
        ]
        if not versions:
            raise ValueError("沒有遠端 release 分支，無法推導 main 版本")
        major, minor, _ = max(versions)
        expected = f"{major}.{minor + 1}.0"
    elif match:
        expected = ".".join(match.groups())
    else:
        raise ValueError("只允許 main 或 release/[v]X.Y.Z")
    tickets = data.get("tickets")
    head = data.get("head", "")
    if tickets == [] and isinstance(head, str) and re.fullmatch(r"(?:chore|refactor)(?:/.+)?", head):
        return {"base": base, "expected": expected, "tickets": [], "ticket_check": "skipped"}
    if not isinstance(tickets, list) or not tickets:
        raise ValueError("缺少本次 PR 關聯票")
    seen = set()
    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("每張票必須是 object")
        key = ticket.get("key")
        if not isinstance(key, str) or not key.strip() or key != key.strip():
            raise ValueError("票號必須是非空且無前後空白的字串")
        if key in seen:
            raise ValueError(f"{key}: 重複票號，請先去重")
        seen.add(key)
        versions = ticket.get("fixVersions")
        if not isinstance(versions, list) or len(versions) != 1:
            raise ValueError(f"{key}: 必須恰好一個修正版本")
        actual = versions[0]
        if not isinstance(actual, str):
            raise ValueError(f"{key}: 修正版本必須是字串")
        normalized = actual.strip()
        if normalized.startswith("v"):
            normalized = normalized[1:]
        if not normalized.startswith(expected):
            raise ValueError(f"{key}: {actual!r} 不符合目標 {expected}*")
    return {"base": base, "expected": expected, "tickets": sorted(seen)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--remote", default="origin")
    args = parser.parse_args()
    try:
        if not args.remote or args.remote.startswith("-"):
            raise ValueError("remote 不可為空或選項")
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = subprocess.run(
            ["git", "ls-remote", "--heads", args.remote],
            capture_output=True, text=True, check=True, timeout=30,
        )
        branches = {
            line.split("\t", 1)[1].removeprefix("refs/heads/")
            for line in result.stdout.splitlines()
            if "\trefs/heads/" in line
        }
        print(json.dumps(check_versions(data, branches), ensure_ascii=False))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
