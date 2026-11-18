#!/usr/bin/env python3
"""Ingestion for website #383: /pdf/ becomes "Print & PDF" (列印與 PDF) in eight locales.

Every string this slice puts on the site comes from a pinned issue comment and is carried here by
program, never typed. Each comment is fetched by id with `gh api` and held to the sha256 and
`updated_at` in sources.json; a comment that changed stops the run.

- aria_en_zhhant, #383 6952823397 (Aria, 2026-11-17): Table A (30 cells for /pdf/) and Table B (link
  text across the site) for en and zh-Hant. The owner approved both on 2026-11-18 ("approval", 6953584073).
- aria_six, #383 6954520336 (Aria): the same two tables for zh-Hans, ja, ko, de, fr, es, translated from
  the approved pair, plus the one row Paula added ("paula", 6953647659): 標準 -> 文件 on the zh-Hant home page.
- daphne, #383 6951950154: the structure and the per-cell limits; only verified here, the limits are
  checked by scripts/check_copy383.py.

Writes scripts/copy383/data.py: TABLE_A[locale][key] = (current, proposed) for the 30 cells, and SRC_ROWS,
the source-code edits of Table B (file, current fragment, proposed fragment).

    python3 -I -B scripts/copy383/ingest.py           # verify the comments, write data.py
    python3 -I -B scripts/copy383/ingest.py --check   # verify, compare with data.py, write nothing

It needs gh, so it runs locally, never in CI.
"""
import argparse
import hashlib
import json
import pprint
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))
REPO = "redtear1115/mars-dawn-website"
LOCALES = ["en", "zh-Hant", "zh-Hans", "ja", "ko", "de", "fr", "es"]
KEYS = ["title", "meta", "h1", "lede", "fig_alt", "co1", "co2", "co3", "h2_steps", "step1", "step2", "step3",
        "h2_layouts", "opener", "cap_doc", "cap_hb", "cap_ho", "alt_doc", "alt_hb", "alt_ho", "h2_bul", "b1", "b2",
        "b3", "b_del", "b369", "ios", "close", "trait", "card"]
PENDING = ["fig_alt", "co1", "co2", "co3"]      # "待圖": they wait for the Print & Export panel photo
UNCHANGED = ["b2", "b3", "b369", "card"]        # current == proposed in the table
DELETED = ["b_del"]
NEW_MARK, DELETE_MARK, PENDING_MARK, KEEP_MARK = "（新增）", "（刪除）", "待圖", "（不動）"


class Stop(SystemExit):
    pass


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch(name: str) -> str:
    pinned = SOURCES["comments"][name]
    out = subprocess.run(["gh", "api", f"repos/{REPO}/issues/comments/{pinned['id']}"], capture_output=True, text=True)
    if out.returncode:
        raise Stop(f"gh api failed for comment {pinned['id']}: {out.stderr.strip()}")
    got = json.loads(out.stdout)
    digest = sha256(got["body"])
    if digest != pinned["sha256"] or got["updated_at"] != pinned["updated_at"]:
        raise Stop(f"comment {pinned['id']} differs from the pinned source: sha256 {digest} vs {pinned['sha256']}, "
                   f"updated_at {got['updated_at']} vs {pinned['updated_at']}")
    if f"/issues/{pinned['issue']}#" not in got["html_url"]:
        raise Stop(f"comment {pinned['id']} is not on #{pinned['issue']}: {got['html_url']}")
    print(f"verified #{pinned['issue']} comment {pinned['id']} ({name}): sha256 {digest[:12]} updated_at {got['updated_at']}")
    return got["body"]


def section(body: str, start: str, end: str = None) -> str:
    if body.count(start) != 1:
        raise Stop(f"{body.count(start)} sections {start!r}, expected 1")
    i = body.index(start) + len(start)
    j = body.index(end, i) if end else len(body)
    return body[i:j]


def cells(line: str) -> list:
    """The cells of one table row: split on a `|` that is not escaped and not inside backticks."""
    out, cur, in_code, i, s = [], "", False, 0, line[1:]
    while i < len(s):
        ch = s[i]
        if ch == "`":
            in_code = not in_code
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur += "|"
            i += 2
            continue
        if ch == "|" and not in_code:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
        i += 1
    return out


def unquote(cell: str) -> str:
    """One pair of backticks around the whole cell is table decoration, not part of the text."""
    return cell[1:-1] if len(cell) > 2 and cell.startswith("`") and cell.endswith("`") else cell


def table_a(block: str, locale: str) -> dict:
    out = {}
    for line in block.split("\n"):
        if not line.startswith("| `pdf."):
            continue
        c = cells(line)
        if len(c) != 3:
            raise Stop(f"A {locale}: row with {len(c)} cells: {line[:80]}")
        ident = c[0].split("`")[1]
        prefix, loc, key = ident.split(".")
        if loc != locale:
            raise Stop(f"A {locale}: row {ident} is for another locale")
        now, new = unquote(c[1]), c[2]
        out[key] = (now, now if new == KEEP_MARK else new)   # the six-locale table says （不動） instead of repeating it
    if sorted(out) != sorted(KEYS):
        raise Stop(f"A {locale}: keys {sorted(set(KEYS) ^ set(out))} differ from the 30 expected")
    for key in UNCHANGED:
        if out[key][0] != out[key][1]:
            raise Stop(f"A {locale} {key}: marked unchanged but current != proposed")
    for key in PENDING:
        if out[key][1] != PENDING_MARK:
            raise Stop(f"A {locale} {key}: expected {PENDING_MARK}, got {out[key][1]!r}")
    if out["b_del"][1] != DELETE_MARK:
        raise Stop(f"A {locale} b_del: expected {DELETE_MARK}")
    return out


def parse_table_a(b_enzh: str, b_six: str) -> dict:
    a1 = section(b_enzh, "## 表 A", "## 表 B")
    a2 = section(b_six, "## 表 A", "## 表 B")
    data = {"en": table_a(section(a1, "### en\n", "### zh-Hant"), "en"),
            "zh-Hant": table_a(section(a1, "### zh-Hant\n"), "zh-Hant")}
    order = ["zh-Hans", "ja", "ko", "de", "fr", "es"]
    for i, locale in enumerate(order):
        end = f"### {order[i + 1]}\n" if i + 1 < len(order) else None
        data[locale] = table_a(section(a2, f"### {locale}\n", end), locale)
    return data


def src_rows(body: str, start: str, end: str = None) -> list:
    rows = []
    for line in section(body, start, end).split("\n"):
        if not line.startswith("| `src."):
            continue
        c = cells(line)
        ident = c[0].split("`")[1]
        path = re.search(r"`(scripts/[\w/.]+\.py):(\d+)", c[0])
        if not path:
            raise Stop(f"{ident}: no file in {c[0]!r}")
        now, new = unquote(c[1]), unquote(c[2])
        rows.append({"id": ident, "file": path.group(1), "line": path.group(2), "current": now, "proposed": new})
    return rows


def parse_src_rows(b_enzh: str, b_six: str) -> list:
    rows = src_rows(b_enzh, "### 要改的原始碼\n", "### 建置出來的位置")
    rows += src_rows(b_six, "### 要改的原始碼（每語 6 條，共 36 條）\n", "### 建置出來的位置")
    rows += src_rows(b_six, "### 追加：zh-Hant 首頁比較表", "### 不改的位置")
    if len(rows) != 12 + 36 + 1:
        raise Stop(f"{len(rows)} source rows, expected 49")
    return rows


def build() -> tuple:
    for name in ("daphne", "approval", "paula"):
        fetch(name)
    b_enzh, b_six = fetch("aria_en_zhhant"), fetch("aria_six")
    return parse_table_a(b_enzh, b_six), parse_src_rows(b_enzh, b_six)


def render(a: dict, rows: list) -> str:
    pins = {k: {f: v[f] for f in ("issue", "id", "sha256", "updated_at")} for k, v in SOURCES["comments"].items()}
    return ('"""Generated by scripts/copy383/ingest.py from the pinned comments in sources.json. Do not edit by hand.\n\n'
            "TABLE_A[locale][key] = (current, proposed): the 30 cells of Table A for /pdf/. Markdown **bold** and\n"
            "[text](url) are as the table has them. SRC_ROWS: the source-code edits of Table B and the one row\n"
            'Paula added (file, the fragment now, the fragment proposed)."""\n\n'
            f"SOURCES = {pprint.pformat(pins, width=110, sort_dicts=True)}\n\n"
            f"TABLE_A = {pprint.pformat(a, width=110, sort_dicts=True)}\n\n"
            f"SRC_ROWS = {pprint.pformat(rows, width=110, sort_dicts=False)}\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    a, rows = build()
    text = render(a, rows)
    target = HERE / "data.py"
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != text:
            print("data.py differs from what the pinned comments give", file=sys.stderr)
            return 1
        print("data.py matches the pinned comments")
        return 0
    target.write_text(text, encoding="utf-8")
    print(f"wrote {target.relative_to(HERE.parent.parent)}: {len(LOCALES)} locales x {len(KEYS)} cells, {len(rows)} source rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
