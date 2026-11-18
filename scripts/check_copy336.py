#!/usr/bin/env python3
"""Checks that the built /zh-hant/best-markdown-viewer-mac/ carries Aria's #336 copy, and says where it differs.

Usage:
    python3 scripts/check_copy336.py [--root public]
    python3 scripts/check_copy336.py --self-test

scripts/copy336/approved.md is Aria's comment on #336 (pinned in sources.json). This reads it, and the built
public/zh-hant/best-markdown-viewer-mac/index.html and index.md, and fails unless the page holds, in its place:

  1 verbatim      every line of Aria's fenced copy (opening, scenarios, the two new tools, not-for list, FAQ),
                  title, h1 and description, as the text of one <h1>, <h2>, <h3>, <p> or <li>;
  2 filled        every {{placeholder}} filled the way scripts/copy336/data.py FILLS says, and no {{ left;
  3 cells         the two new table columns, cell by cell against Aria's table; a cell in CELLS_DIFFER has its
                  new value and not Aria's old one;
  4 removed       the sentences in REMOVED are not on the page, and the rest of their line is (or the whole
                  line is gone when drop_line says so);
  and: the held FAQ question (iPhone, waits for #337) and its link are not on the page; the two new tools
  link to their official pages and the Chrome extension's Web Store ID is stated; the eight old tools'
  paragraphs, bullets and table cells are the ones scripts/best228/data.py has (the MarsDawn price bullet
  is Aria's new one); every other locale's page does not carry any of this ticket's words.

Text is compared as visible text (tags stripped, entities decoded, whitespace collapsed) against the copy with
its Markdown marks removed. Never against the build's own rendering, which would share a mistake the build makes.
sources.json's sha256 pins approved.md, so a hand edit of it fails too.

--self-test plants one break of each kind in copies of the built page and its twin and fails unless each is caught.
"""
import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
from best228 import data as best  # noqa: E402
from copy336 import data  # noqa: E402

SITE = HERE.parent / "public"
PAGE = "zh-hant/best-markdown-viewer-mac"
OTHER_LOCALES = ["", "zh-hans", "ja", "de", "fr", "es", "ko"]
NEW_COLS = {"iPhone／iPad": "iphone-ipad", "只讀（不會誤改）": "read-only"}
CHROME_ID = "medapdbncneneejhbgcjceippjlfkmkg"


def ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def vis(fragment: str) -> str:
    return ws(html.unescape(re.sub(r"<[^>]+>", "", fragment)))


def plain_inline(md: str) -> str:
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    md = re.sub(r"\*\*(.+?)\*\*", r"\1", md)
    return md.replace("`", "")


def plain(md: str) -> str:
    return ws(plain_inline(re.sub(r"^(?:#{1,6} |- )", "", md.strip())))


def main_of(page: str) -> str:
    m = re.search(r"<main\b.*?</main>", page, re.S)
    return m.group(0) if m else ""


# ---------------------------------------------------------------- Aria's copy

def approved_text() -> str:
    return (HERE / "copy336" / "approved.md").read_text(encoding="utf-8")


def pin_problems(text: str) -> list:
    pin = json.loads((HERE / "copy336" / "sources.json").read_text(encoding="utf-8"))["comments"]["A"]
    got = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return [] if got == pin["vendored_sha256"] else [f"approved.md: sha256 {got} is not the pinned {pin['vendored_sha256']}"]


def fenced_blocks(text: str) -> list:
    """The ~~~markdown blocks of approved.md, each as a list of non-empty lines, in order."""
    return [[ln for ln in blk.split("\n") if ln.strip()] for blk in re.findall(r"~~~markdown\n(.*?)\n~~~", text, re.S)]


def aria_meta(text: str) -> dict:
    return {
        "title": re.search(r"- `<title>`：(.+)", text).group(1).strip(),
        "h1": re.search(r"- `<h1>`：(.+)", text).group(1).strip(),
        "description": re.search(r"### description\n\n> (.+)", text).group(1).strip(),
        "price": re.search(r"價格改成「(.+?)」", text).group(1),
    }


def aria_table(text: str) -> tuple:
    block = re.search(r"\| App \|.*?\n\n", text, re.S).group(0)
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in block.strip().split("\n")]
    return rows[0], [r for r in rows[2:]]


def fill(line: str) -> str:
    def one(m):
        key = m.group(1)
        if key not in data.FILLS:
            raise KeyError(f"placeholder {{{{{key}}}}} has no entry in copy336/data.py FILLS")
        return data.FILLS[key]
    return re.sub(r"\{\{(.+?)\}\}", one, line)


def expected_lines(text: str) -> tuple:
    """(lines that must be elements of the page, in order; plain texts that must not be on it)."""
    want, absent = [], []
    blocks = fenced_blocks(text)
    assert len(blocks) == 5, f"approved.md has {len(blocks)} fenced blocks, want 5 (opening, scenarios, tools, not-for, faq)"
    held_faq = False
    for block in blocks:
        h2 = ""
        for ln in block:
            if ln.startswith("## "):
                h2 = plain(ln)
            if ln.startswith("### ") and plain(ln) in ("iPhone 怎麼看 .md 檔？",):
                held_faq = True
                absent.append(plain(ln))
                continue
            if ln.startswith("### "):
                held_faq = False
            if held_faq:
                continue
            line = plain(fill(ln))
            dropped = False
            for rem in data.REMOVED:
                sent = plain(rem["sentence"])
                only = rem.get("only_after")
                if only and h2 != only:
                    continue
                if sent in plain(ln) or sent == plain(ln):
                    if not only:  # a rule for one section is held to that section below
                        absent.append(sent)
                    if rem["drop_line"]:
                        dropped = True
                    else:
                        line = ws(plain(fill(ln)).replace(sent, ""))
            if not dropped:
                want.append(line)
    return want, absent


# ---------------------------------------------------------------- the page

def table_of(h: str) -> tuple:
    head = [vis(c) for c in re.findall(r"<th scope=\"col\"[^>]*>(.*?)</th>", h, re.S)]
    ids = re.findall(r"<th scope=\"col\" id=\"(col-[^\"]+)\"", h)
    rows = {}
    for m in re.finditer(r"<tr id=\"cmp-[^\"]+\"><th scope=\"row\">(.*?)</th>(.*?)</tr>", h, re.S):
        rows[vis(m.group(1))] = [vis(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", m.group(2), re.S)]
    return head, ids, rows


def md_table_of(md: str) -> tuple:
    lines = [ln for ln in md.split("\n") if ln.startswith("| ")]
    cells = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    return cells[0], {r[0]: r[1:] for r in cells[1:]}


def sections(main: str) -> dict:
    parts = re.split(r"(?=<h2\b)", main)
    out = {}
    for part in parts:
        m = re.match(r"<h2\b[^>]*>(.*?)</h2>", part, re.S)
        if m:
            out[vis(m.group(1))] = part
    return out


def page_problems(h: str, md: str, text: str, absent_extra=()) -> list:
    out = []
    main = main_of(h)
    meta = aria_meta(text)
    want, absent = expected_lines(text)

    # 1-2 verbatim and filled: each line is the text of one element, in order
    els = [(m.start(), vis(m.group(2))) for m in re.finditer(r"<(h[1-3]|p|li)\b[^>]*>(.*?)</\1>", main, re.S)]
    pos = 0
    for line in want:
        if re.match(r"\| ", line):
            continue
        hit = next((i for i in range(pos, len(els)) if els[i][1] == line), None)
        if hit is None:
            anywhere = any(t == line for _, t in els)
            out.append(f"html: {'out of order' if anywhere else 'missing'}: {line[:70]}")
        else:
            pos = hit + 1
    md_plain = ws(" ".join(plain_inline(ln) for ln in md.split("\n")))
    pos = 0
    for line in want:
        i = md_plain.find(line, pos)
        if i < 0:
            out.append(f"md: {'out of order' if line in md_plain else 'missing'}: {line[:70]}")
        else:
            pos = i + len(line)

    # title, h1, description, MarsDawn's price bullet
    for key, pat in (("title", r"<title>(.*?)</title>"), ("description", r'<meta name="description" content="([^"]*)"')):
        m = re.search(pat, h, re.S)
        if not m or html.unescape(m.group(1)).strip() != meta[key]:
            out.append(f"html: {key} is not Aria's: {m.group(1) if m else None}")
    m = re.search(r"<h1\b[^>]*>(.*?)</h1>", main, re.S)
    if not m or vis(m.group(1)) != meta["h1"]:
        out.append(f"html: h1 is not Aria's: {vis(m.group(1)) if m else None}")
    if not md.startswith("# " + meta["h1"] + "\n"):
        out.append("md: first line is not Aria's h1")
    price = "價格：" + meta["price"]
    if not any(t == price for _, t in els):
        out.append("html: MarsDawn's price bullet is not Aria's")
    for need, where in (("Markdown 閱讀器推薦", meta["title"]), ("iPhone", meta["title"]),
                        ("Markdown 閱讀器推薦", meta["h1"]), ("iPhone", meta["h1"])):
        if need not in where:
            out.append(f"copy: {need} is not in {where}")
    first = meta["description"].split("。")[0]
    if "閱讀器" not in first or "推薦" not in first:
        out.append("copy: description's first sentence lacks 閱讀器 or 推薦")

    # 4 removed, and held
    htext, mtext = vis(main), md_plain
    for a in list(absent) + list(data.ABSENT) + list(absent_extra):
        if a and (a in htext or a in mtext or a in main or a in md):
            out.append(f"held/removed text is on the page: {a[:60]}")
    secs = sections(main)
    chrome = secs.get("Chrome 的 Markdown Reader 擴充功能", "")
    if "價格：免費" in vis(chrome) or "iPhone 上的 Chrome" in vis(chrome):
        out.append("html: a removed sentence is back in the Chrome section")

    # 3 cells
    head, ids, rows = table_of(h)
    arow_head, arows = aria_table(text)
    old_head = best.DATA["zh-hant"]["head"]
    for col, cid in NEW_COLS.items():
        if col not in head:
            out.append(f"html: column {col} missing")
        if f"col-{cid}" not in ids:
            out.append(f"html: column id col-{cid} missing")
    if [c for c in head if c not in NEW_COLS] != old_head:
        out.append("html: the old columns are not the eight-tool page's, in order")
    differ = {(r, c): (old, new) for r, c, old, new in data.CELLS_DIFFER}
    for arow in arows:
        name = arow[0]
        cells = rows.get(name)
        if cells is None:
            out.append(f"html: table row {name} missing")
            continue
        for k, col in enumerate(arow_head[1:], start=1):
            want_cell = fill(arow[k])
            if (name, col) in differ:
                old, new = differ[(name, col)]
                if old != arow[k]:
                    out.append(f"copy336 CELLS_DIFFER: {name}/{col} old value is not Aria's ({arow[k]!r})")
                want_cell = new
            got = cells[head.index(col) - 1] if col in head else None
            if got != want_cell:
                out.append(f"html: cell {name}/{col} is {got!r}, want {want_cell!r}")
            if (name, col) in differ and got == arow[k]:
                out.append(f"html: cell {name}/{col} still has Aria's value")
    mhead, mrows = md_table_of(md)
    if mhead != head:
        out.append("md: table head is not the page's")
    for name, cells in rows.items():
        if mrows.get(name) != cells:
            out.append(f"md: table row {name} is not the page's")
    if rows.get("MarsDawn", [""] * 9)[head.index("自動重新載入") - 1:][:1] != ["有，可撤銷"]:
        out.append("html: MarsDawn's 自動重新載入 is not 有，可撤銷")

    # the eight old tools stay as best228 has them
    old = best.DATA["zh-hant"]
    for app in old["apps"]:
        sec = secs.get(app["name"])
        if sec is None:
            out.append(f"html: old tool {app['name']} lost its section")
            continue
        ts = [vis(m.group(2)) for m in re.finditer(r"<(p|li)\b[^>]*>(.*?)</\1>", sec, re.S)]
        for t in [vis(app["para"])] + [vis(b) for b in app["bullets"] if not (app["slug"] == "marsdawn" and b.startswith("價格："))]:
            if t not in ts:
                out.append(f"html: old text of {app['name']} changed: {t[:50]}")
    for row in old["rows"]:
        got = rows.get(row[0])
        if got is None:
            out.append(f"html: old row {row[0]} lost")
        elif [c for col, c in zip(head[1:], got) if col not in NEW_COLS] != [vis(c) for c in row[1:]]:
            out.append(f"html: old cells of {row[0]} changed")
    faq = re.search(r'<section class="faq">(.*?)</section>', h, re.S)
    faq_h3 = [vis(x) for x in re.findall(r"<h3>(.*?)</h3>", faq.group(1), re.S)] if faq else []
    if faq_h3 != ["Mac 預設能開 .md 嗎？"] + [q for q, _ in old["faq"]]:
        out.append(f"html: FAQ questions are {faq_h3}")

    # sources of the two new tools
    colamd = secs.get("ColaMD", "")
    if CHROME_ID not in vis(chrome) or f"chromewebstore.google.com/detail/md-reader/{CHROME_ID}" not in chrome:
        out.append("html: the Chrome section does not name the extension's ID and Web Store page")
    if "https://github.com/marswaveai/ColaMD" not in colamd or "https://colamd.com/" not in colamd:
        out.append("html: the ColaMD section lacks its official links")
    if vis(main).count(data.CHECK_DATE) < 3:
        out.append(f"html: the check date {data.CHECK_DATE} is not in the opening and both new tools' sections")
    return out


def site_problems(root: Path) -> list:
    text = approved_text()
    out = pin_problems(text)
    page = root / PAGE
    if not (page / "index.html").is_file() or not (page / "index.md").is_file():
        return out + [f"{PAGE}: index.html or index.md is not built"]
    out += page_problems((page / "index.html").read_text(encoding="utf-8"), (page / "index.md").read_text(encoding="utf-8"), text)
    for loc in OTHER_LOCALES:
        f = root / loc / "best-markdown-viewer-mac" / "index.html"
        if not f.is_file():
            out.append(f"{f.relative_to(root)}: missing")
            continue
        body = f.read_text(encoding="utf-8")
        for needle in ("Markdown 閱讀器推薦", "ColaMD", CHROME_ID):
            if needle in body:
                out.append(f"{f.relative_to(root)}: carries {needle!r}, which belongs to zh-hant only")
    return out


# ---------------------------------------------------------------- self-test

def self_test(root: Path) -> int:
    text = approved_text()
    page = root / PAGE
    h = (page / "index.html").read_text(encoding="utf-8")
    md = (page / "index.md").read_text(encoding="utf-8")
    if page_problems(h, md, text):
        print("self-test: the built page already has problems; plants prove little")
        return 1
    caught = missed = 0

    def plant(what, hh=None, mm=None, tt=None, extra=()):
        nonlocal caught, missed
        if page_problems(hh if hh is not None else h, mm if mm is not None else md,
                         tt if tt is not None else text, extra):
            caught += 1
        else:
            print(f"self-test: {what} was NOT caught")
            missed += 1

    def sub(s, old, new):
        assert old in s, f"self-test: cannot plant, {old!r} is not there"
        return s.replace(old, new, 1)

    plant("a verbatim line changed (html)", hh=sub(h, "看三件事", "看兩件事"))
    plant("a verbatim line changed (md)", mm=sub(md, "看三件事", "看兩件事"))
    plant("a placeholder left in", hh=sub(h, "查證日期是 " + data.CHECK_DATE, "查證日期是 {{查證日期}}"))
    plant("a filled value changed", hh=sub(h, "Mermaid 圖表和數學式（KaTeX）都內建。", "Mermaid 圖表和數學式都內建。"))
    plant("a removed sentence back (R1)", hh=sub(h, "<li><strong>Marked 3</strong>：專門用來預覽和列印，PDF 有分頁和頁碼。</li>",
                                                    "<li><strong>Marked 3</strong>：專門用來預覽和列印，PDF 有分頁和頁碼。</li>\n<p>MarsDawn 也能輸出 PDF，但沒有頁碼。</p>"))
    plant("a removed sentence back (R3)", hh=sub(h, "才能讀本機檔案。", "才能讀本機檔案。iPhone 上的 Chrome 不能裝擴充功能。"))
    plant("a differing cell has Aria's value", hh=sub(h, "<td data-col=\"read-only\">未記載，官方稱是編輯器</td>", "<td data-col=\"read-only\">無，原始碼可以直接改</td>"))
    plant("a cell of the two new columns changed", hh=sub(h, "<td data-col=\"iphone-ipad\">有，只能讀</td>", "<td data-col=\"iphone-ipad\">有</td>"))
    plant("an old cell changed", hh=sub(h, "<td data-col=\"price\">一次 USD 4.99</td>", "<td data-col=\"price\">一次 USD 5.99</td>"))
    plant("an old paragraph changed", hh=sub(h, "快速查看擴充功能：在 Finder", "快速查看擴充功能：在 Finder 裡"))
    plant("the held iPhone FAQ is on the page", hh=sub(h, "<h3>Mac 預設能開 .md 嗎？</h3>", "<h3>iPhone 怎麼看 .md 檔？</h3>\n<p>x</p>\n<h3>Mac 預設能開 .md 嗎？</h3>"))
    plant("a link to the #337 page", mm=md + "\n[x](/zh-hant/view-markdown-on-iphone/)\n")
    plant("the Chrome ID is gone", hh=h.replace(CHROME_ID, "xxxx"))
    plant("the ColaMD link is gone", hh=h.replace("https://github.com/marswaveai/ColaMD", "https://example.com"))
    plant("MarsDawn's price is the old one", hh=sub(h, "價格：免費下載，試用 14 天，之後 USD 4.99 一次買斷。", "價格：免費下載，試用 14 天，之後一次 USD 4.99。"))
    plant("the title lost iPhone", hh=sub(h, "Mac、iPhone 只看不改", "Mac 只看不改"))
    # the pin: a changed approved.md text is the pin's problem, not the page's
    if not pin_problems(text + "x\n"):
        print("self-test: a changed approved.md was NOT caught by the pin")
        missed += 1
    else:
        caught += 1
    print(f"self-test: {caught} caught, {missed} missed")
    return 1 if missed else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(SITE))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    root = Path(args.root)
    if args.self_test:
        return self_test(root)
    problems = site_problems(root)
    for p in problems:
        print(p)
    if problems:
        print(f"{len(problems)} problems")
        return 1
    print("ok: #336 copy on /zh-hant/best-markdown-viewer-mac/ (html and md): verbatim lines, filled placeholders, "
          f"{len(data.CELLS_DIFFER)} table cells that differ from Aria's, {len(data.REMOVED)} removed sentences, "
          "old tools unchanged, held iPhone FAQ absent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
