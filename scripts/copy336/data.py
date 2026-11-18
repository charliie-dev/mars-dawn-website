"""zh-Hant copy for /zh-hant/best-markdown-viewer-mac/ (website #336): the page becomes "Markdown 閱讀器推薦".

Hand-kept, unlike scripts/best228/data.py (that one is generated and `ingest.py --check` fails on a hand
edit, so this module overrides it for zh-Hant only: merge() below). The words are Aria's, pinned in
approved.md (comment 6560244450 on #336, see sources.json), apart from four kinds of difference, each
listed here so scripts/check_copy336.py can hold the rendered page to them:

  FILLS    a {{placeholder}} in Aria's text, filled from an official page on CHECK_DATE;
  CELLS    a table cell whose value is not the one Aria pre-filled, because an official page says otherwise;
  REMOVED  a sentence of Aria's that conflicts with what is shipped or that no official page backs: it is
           left out and not rewritten (the PR lists it under 待決定);
  ADDED    text the ticket asks for that Aria's copy does not have: the source links of the two new tools.

Everything that says what MarsDawn does is Mac 1.2.2 and iOS 1.0.2 (shipped), nothing later.
Other locales are not touched: merge() is called for zh-hant only (build_pages.apply_best228)."""

CHECK_DATE = "2026-11-18"

_CHROME_STORE = "https://chromewebstore.google.com/detail/md-reader/medapdbncneneejhbgcjceippjlfkmkg"
_CHROME_SITE = "https://md-reader.github.io/"
_CHROME_PRICING = "https://md-reader.github.io/pricing"
_COLA_REPO = "https://github.com/marswaveai/ColaMD"
_COLA_SITE = "https://colamd.com/"

TITLE = "2026 Markdown 閱讀器推薦：Mac、iPhone 只看不改 · MarsDawn"
H1 = "2026 Markdown 閱讀器推薦：只想看、不想改，Mac 和 iPhone 怎麼選"
DESCRIPTION = ("Markdown 閱讀器推薦：只想讀、不想改的話，Mac 和 iPhone 各用哪一款。"
               "比較 10 款的價格、iPhone／iPad、唯讀、Mermaid、數學式和 PDF，依情境分組。")

INTRO_HTML = f"""<p>只想讀 Markdown、不想改的話，先看你在哪裡讀、讀的是什麼：</p>
  <ul>
    <li><strong>看 AI／agent 寫的計畫和報告</strong>：用 MarsDawn。agent 存檔時頁面會跟著更新，Mermaid 圖表和數學式都畫好。</li>
    <li><strong>在 iPhone 上看</strong>：MarsDawn 的 iPhone 版只能讀，不會誤改；Obsidian 能讀也能寫，但檔案要放在它的 vault 裡。</li>
    <li><strong>看完要交 PDF，而且要頁碼</strong>：用 Typora 或 Marked 3。</li>
  </ul>
  <p>市面上的比較文多半在比「編輯器」，比的是寫起來順不順手。這篇只比「讀」：打開後看到的是不是排好的頁面、會不會一不小心就改到檔案、手機上能不能看。以下 10 款依字母排序，每款都寫出適合誰、一個老實的缺點和價格。價格和功能的查證日期是 {CHECK_DATE}。</p>"""

# The "依情境挑" block, before the per-app sections. Aria's closing line "MarsDawn 也能輸出 PDF，但沒有頁碼。"
# is REMOVED[0].
SCENARIOS_HTML = """<h2 id="scenarios">依情境挑</h2>
<h3>看 AI／agent 產出的計畫</h3>
<p>agent 寫的檔案很長，會一直被改寫，裡面常常有表格和 Mermaid 圖表。挑的時候，看三件事：檔案被改了會不會自動更新、圖表畫不畫得出來、能不能從終端機直接打開。</p>
<ul>
  <li><strong>MarsDawn</strong>：agent 存檔時，開著的視窗會自動「從磁碟更新」，而且可以撤銷。<code>marsdawn open plan.md</code> 從終端機打開，也有給 agent 用的 skill。</li>
  <li><strong>ColaMD</strong>：免費開源，agent 改檔時畫面也會即時更新，Windows 和 Linux 也能用。</li>
</ul>
<h3>在手機上看</h3>
<ul>
  <li><strong>MarsDawn（iPhone／iPad）</strong>：只能讀，不能改，Mermaid、數學式和表格都畫好。和 Mac 版共用一次買斷。</li>
  <li><strong>Obsidian</strong>：有 iPhone 版，能讀也能寫。檔案要放在它的 vault 裡。</li>
</ul>
<h3>看完要交 PDF</h3>
<ul>
  <li><strong>Typora</strong>：輸出 PDF 時，頁首或頁尾可以加頁碼。</li>
  <li><strong>Marked 3</strong>：專門用來預覽和列印，PDF 有分頁和頁碼。</li>
</ul>"""

# The two new tools, alphabetical, so they come before MacDown 3000. The last bullet of each is ADDED: the
# page has to say which Chrome extension this is (the Web Store has several of the same name) and where
# each fact on the page can be checked.
NEW_APPS = [
    {
        "slug": "chrome-markdown-reader",
        "name": "Chrome 的 Markdown Reader 擴充功能",
        "para": ("裝在 Chrome 裡的擴充功能。把 .md 檔拖進瀏覽器，就會顯示排好的頁面，旁邊有目錄。"
                 "Mermaid 圖表和數學式（KaTeX）都內建。"),
        "bullets": [
            "適合：不想多裝一個 App、本來就整天開著 Chrome 的人。",
            "缺點：要先在擴充功能設定裡打開「允許存取檔案網址」，才能讀本機檔案。",
            (f"是哪一個：Chrome 線上應用程式商店裡的「Markdown Reader」（ID <code>medapdbncneneejhbgcjceippjlfkmkg</code>，"
             f"開發者網站 md-reader.github.io）。官方頁面：<a href=\"{_CHROME_STORE}\">商店頁</a>、"
             f"<a href=\"{_CHROME_SITE}\">官網</a>、<a href=\"{_CHROME_PRICING}\">價格頁</a>。查證日期 {CHECK_DATE}。"),
        ],
    },
    {
        "slug": "colamd",
        "name": "ColaMD",
        "para": "免費開源（MIT）的 Markdown 編輯器，用 Electron 做的，macOS、Windows、Linux 都能用。agent 改檔時，畫面會即時更新，不用重新打開。",
        "bullets": [
            "適合：要在 Windows 或 Linux 上看 agent 寫的檔案的人。",
            "缺點：是所見即所得的編輯器，打開後就能直接改，沒有只讀模式。Mermaid 圖表和數學式（KaTeX）都內建。",
            "價格：免費。",
            (f"官方頁面：<a href=\"{_COLA_REPO}\">GitHub</a>、<a href=\"{_COLA_SITE}\">官網</a>。查證日期 {CHECK_DATE}。"),
        ],
    },
]

# Table: the two new columns go after 價格; the two new rows are alphabetical (first). Each entry is
# (row label, iPhone／iPad, 只讀（不會誤改）) for the eight tools that were already on the page, whose other
# cells stay exactly as best228/data.py has them.
NEW_COLS = ("iphone-ipad", "read-only")
NEW_HEAD = ("iPhone／iPad", "只讀（不會誤改）")
OLD_ROW_CELLS = {
    "MacDown 3000": ("無", "未記載，官方稱是編輯器"),
    "Marked 3": ("無", "有，本身就是預覽器"),
    "MarkEdit": ("無", "未記載，官方稱是編輯器"),
    "MarsDawn": ("有，只能讀", "Mac：預覽窗格不能改，原始碼窗格可以改；iPhone／iPad：只能讀"),
    "Obsidian": ("有，能讀也能寫", "有，閱讀檢視"),
    "QLMarkdown": ("無", "有，只在 Finder 預覽"),
    "Typora": ("無", "未記載，官方稱是編輯器"),
    "VS Code": ("無", "有，預覽分頁"),
}
# Whole rows of the two new tools, in the order of the page's columns (after the "App" cell):
# price, iPhone／iPad, 只讀, Mermaid, 數學式, PDF, 自動重新載入, 命令列開到指定行, 快速查看, 架構.
NEW_ROWS = {
    "Chrome Markdown Reader": ["免費，另有 Pro 訂閱", "無", "有", "有", "KaTeX", "未記載", "有", "未記載", "未記載", "瀏覽器擴充功能"],
    "ColaMD": ["免費（MIT）", "無", "無，打開就是編輯", "有", "KaTeX", "有", "有", "未記載", "未記載", "Electron"],
}

NOTFOR = [
    "想在 iPhone 或 iPad 上改檔案。MarsDawn 的 iPhone、iPad 版只能讀；要在手機上寫，Obsidian 可以。",
    "用 Windows 或 Linux。MarsDawn 只有 Mac、iPhone 和 iPad 版；ColaMD 三個平台都有。",
    "你在經營互相連結的個人筆記庫。Obsidian 就是為此打造的。",
    "你只想在 Finder 預覽。QLMarkdown 免費。",
]

# Aria's FAQ has two new questions; only this one goes on the page. The iPhone one waits for #337 (its
# page is not live, and its answer needs Ray's device check): PR 後續.
FAQ_FIRST = [
    ("Mac 預設能開 .md 嗎？",
     "能打開，但通常是用「文字編輯」，看到的是 <code>#</code> 和 <code>**</code> 這些記號，不是排好的頁面。"
     "換成 Markdown 閱讀器再設成預設 App，之後雙擊就會在那裡打開。"
     "做法請看 <a href=\"/zh-hant/view-markdown-on-mac/\">Mac 怎麼開 md 檔</a>。"),
]

MARSDAWN_PRICE = "價格：免費下載，試用 14 天，之後 USD 4.99 一次買斷。同一個 Apple 帳號，一次購買，Mac、iPhone、iPad 都能用。"

# --- what differs from approved.md (read by scripts/check_copy336.py) ----------------------------------------

# {{placeholder}} in approved.md -> the text that stands in its place, and why it is true (source, CHECK_DATE).
FILLS = {
    "查證日期": CHECK_DATE,
    "Mermaid／數學式：待查證": "Mermaid 圖表和數學式（KaTeX）都內建。",
    "Mermaid／數學式：主程式未內建，有第三方延伸版本；待查證": "Mermaid 圖表和數學式（KaTeX）都內建。",
    "待查證": "無",  # the MarkEdit iPhone／iPad table cell
}

# Table cells whose final value is not the one in Aria's table: (row, column, Aria's value, final value).
CELLS_DIFFER = [
    ("Chrome Markdown Reader", "iPhone／iPad", "無（iOS 版 Chrome 不支援擴充功能）", "無"),
    ("MacDown 3000", "只讀（不會誤改）", "無，原始碼可以直接改", "未記載，官方稱是編輯器"),
    ("MarkEdit", "只讀（不會誤改）", "無", "未記載，官方稱是編輯器"),
    ("Typora", "只讀（不會誤改）", "無，打開就是編輯", "未記載，官方稱是編輯器"),
]

# Sentences of Aria's that are not on the page. `where` is a line of approved.md that holds it, `drop_line`
# says the whole line goes (a bullet that would be left empty or would say the same thing by implication).
REMOVED = [
    {"id": "R1", "sentence": "MarsDawn 也能輸出 PDF，但沒有頁碼。", "drop_line": True},
    {"id": "R2", "sentence": "PDF 一定要有頁碼。Typora 與 Marked 3 能加，MarsDawn 不能。", "drop_line": True},
    {"id": "R3", "sentence": "iPhone 上的 Chrome 不能裝擴充功能。", "drop_line": False},
    {"id": "R4", "sentence": "- 價格：免費。", "drop_line": True, "only_after": "Chrome 的 Markdown Reader 擴充功能"},
]

# Text of Aria's that must not be on the page at all (the held FAQ question, and the old title it replaces).
ABSENT = ["iPhone 怎麼看 .md 檔？", "view-markdown-on-iphone", "{{", "}}", "Co-authored-by"]


def merge(base: dict) -> dict:
    """best228's zh-hant dict with this ticket's copy on top. Old apps, their rows and the other FAQ stay as
    they are; only the table gains two columns."""
    d = dict(base)
    d["title"], d["h1"], d["description"] = TITLE, H1, DESCRIPTION
    d["intro_html"], d["scenarios_html"] = INTRO_HTML, SCENARIOS_HTML
    apps = [dict(a) for a in base["apps"]]
    for app in apps:
        if app["slug"] == "marsdawn":
            bullets = list(app["bullets"])
            assert bullets[2].startswith("價格："), bullets[2]
            bullets[2] = MARSDAWN_PRICE
            app["bullets"] = bullets
    d["apps"] = NEW_APPS + apps
    # table: App, 價格, +2 new, then the old cells from 價格's successor on
    d["head"] = [base["head"][0], base["head"][1], *NEW_HEAD, *base["head"][2:]]
    d["cols"] = [base["cols"][0], *NEW_COLS, *base["cols"][1:]]
    rows = []
    for row in base["rows"]:
        extra = OLD_ROW_CELLS[row[0]]
        rows.append([row[0], row[1], *extra, *row[2:]])
    new_rows = [[name, *cells] for name, cells in NEW_ROWS.items()]
    d["rows"] = new_rows + rows
    d["notfor"] = NOTFOR
    d["faq"] = FAQ_FIRST + [list(q) for q in base["faq"]]
    return d
