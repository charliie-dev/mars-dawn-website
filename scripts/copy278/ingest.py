#!/usr/bin/env python3
"""The /from-hackmd/ copy (website #278), carried by program from Aria's comments, never retyped.

source/ holds the two comments as posted: 6684344469 (en, zh-Hant, Ray approved in 6685109512) and
6685163599 (the other six; Aria checks ja, Ray's decision in 6685212059). data.py is generated from them:

    python3 -I -B scripts/copy278/ingest.py          # write data.py
    python3 -I -B scripts/copy278/ingest.py --check  # fail if data.py isn't what the sources give

The one sentence still marked 【待定，#300】 (the `:::` blocks) is left out of data.py in every locale,
with no place held for it. Aria's 6964983008 gives its words for en and zh-Hant, awaiting Ray's "#278 `:::` ok",
and has not translated the other six; when they are approved, add that comment to source/ and put the
sentence in where this file now drops it. Nothing else of 6964983008 changes the approved copy (its section 2
corrects Aria's notes, not the page text), and its optional rows (section 3) are not applied.
"""
import html
import pprint
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
SOURCES = {"6684344469-en-zh-hant.md": {"en": "en", "zh-Hant": "zh-hant"},
           "6685163599-six.md": {name: name for name in ("zh-hans", "ja", "ko", "de", "fr", "es")}}
PENDING = "【待定"


def block(text: str, heading: str) -> str:
    """The ```md block under `## heading`; the fence that ends it is the first one at column 0."""
    match = re.search(rf"^## {re.escape(heading)}\n+```md\n(.*?)^```$", text, re.S | re.M)
    if not match:
        raise SystemExit(f"no copy for {heading}")
    return match.group(1)


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def inline(text: str) -> str:
    """Markdown inline syntax to HTML; everything else is HTML-escaped and otherwise untouched."""
    out, pos = [], 0
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*\*([^*]+)\*\*", text):
        out.append(esc(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append(f'<a href="{html.escape(m.group(2), quote=True)}">{esc(m.group(1))}</a>')
        elif m.group(3) is not None:
            out.append(f"<code>{esc(m.group(3))}</code>")
        else:
            out.append(f"<strong>{inline(m.group(4))}</strong>")   # a bold phrase can hold a code span
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def cells(line: str) -> list:
    # strip(" ") and not strip(): fr and de copy carries U+00A0, which strip() would take off
    return [inline(cell.strip(" ")) for cell in line.strip(" ").removeprefix("|").removesuffix("|").split("|")]


def parse(md: str) -> dict:
    """Blocks, in order, as HTML-ready fields: ("h1"|"h2", text), ("p", html), ("ul", [html]), ("pre", text),
    ("table", head, rows), ("faq", heading, [(question, answer)]). The text of an h1 or h2 is plain, the rest is HTML (the FAQ's heading and questions are escaped)."""
    title = re.search(r"^Title: (.+)$", md, re.M).group(1)
    description = re.search(r"^Meta description: (.+)$", md, re.M).group(1)
    lines = md.split("\n")
    i = next(n for n, line in enumerate(lines) if line.startswith("# "))
    blocks, dropped = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip(" "):
            i += 1
        elif line.startswith("# "):
            blocks.append(("h1", line[2:]))
            i += 1
        elif line.startswith("### "):
            blocks.append(("h3", line[4:]))
            i += 1
        elif line.startswith("## "):
            blocks.append(("h2", line[3:]))
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            head, rule, *body = rows
            assert set(rule) <= set("|- "), rule
            blocks.append(("table", cells(head), [cells(row) for row in body]))
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(inline(lines[i][2:]))
                i += 1
            blocks.append(("ul", items))
        elif line.startswith("    "):
            code = []
            while i < len(lines) and (lines[i].startswith("    ") or not lines[i].strip(" ")):
                code.append(lines[i])
                i += 1
            while not code[-1].strip(" "):
                code.pop()
            blocks.append(("pre", "\n".join(row[4:] for row in code)))
        elif line.startswith(PENDING):
            dropped += 1   # the `:::` sentence: no paragraph, no placeholder
            i += 1
        else:
            blocks.append(("p", inline(line)))
            i += 1
    if dropped != 1:
        raise SystemExit(f"{title}: expected one {PENDING} line, found {dropped}")
    # the last h2 and what follows it are the FAQ: its heading, then h3, one paragraph, h3, one paragraph
    k = max(n for n, b in enumerate(blocks) if b[0] == "h2")
    faq = blocks[k + 1:]
    if len(faq) % 2 or any(b[0] != ("h3", "p")[n % 2] for n, b in enumerate(faq)):
        raise SystemExit(f"{title}: the questions aren't h3 and paragraph pairs")
    blocks[k:] = [("faq", esc(blocks[k][1]), [(esc(q[1]), a[1]) for q, a in zip(faq[::2], faq[1::2])])]
    return {"title": title, "description": description, "blocks": blocks}


def build() -> dict:
    data = {}
    for name, locales in SOURCES.items():
        text = (HERE / "source" / name).read_text(encoding="utf-8")
        for heading, locale in locales.items():
            data[locale] = parse(block(text, heading))
    if any(PENDING in repr(copy) for copy in data.values()):
        raise SystemExit(f"{PENDING} is still in the copy")
    return data


def main() -> int:
    source = ('"""Generated by ingest.py from source/. Do not edit: change the source and regenerate."""\n\nDATA = '
              + pprint.pformat(build(), width=120, sort_dicts=False) + "\n")
    target = HERE / "data.py"
    if "--check" in sys.argv:
        if target.read_text(encoding="utf-8") != source:
            print("data.py doesn't match source/")
            return 1
        print("data.py matches source/")
        return 0
    target.write_text(source, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
