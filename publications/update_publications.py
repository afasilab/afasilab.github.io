#!/usr/bin/env python3
"""
update_publications.py
────────────────────────────────────────────────────────────────────────────
Скачивает публикации из двух профилей Google Scholar
  • Ruslan Afasizhev  (U7yVbHIAAAAJ)
  • Inna Afasizheva   (-ivXdnsAAAAJ)

▪ сохраняет JSON в  publications/gs_json/…
▪ перезаписывает блок  <section id="publications"> … </section>  в index.html

pip install "scholarly>=1.7.11"
────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json, re, sys
from datetime import datetime
from pathlib   import Path
from typing    import Dict, List, Tuple

from scholarly import scholarly


# ────────── пути ──────────
SCRIPT_DIR = Path(__file__).resolve().parent         # …/publications
REPO_DIR   = SCRIPT_DIR.parent                       # …/afasilab.github.io
INDEX_HTML = REPO_DIR / "index.html"

GS_DIR   = REPO_DIR / "publications" / "gs_json"
GS_DIR.mkdir(parents=True, exist_ok=True)

today     = datetime.today().strftime("%m-%d-%Y")
JSON_FILE = GS_DIR / f"publications_detailed_{today}.json"
# ─────────────────────────


AUTHOR_IDS: Dict[str, str] = {
    "Ruslan Afasizhev": "U7yVbHIAAAAJ",
    "Inna Afasizheva":  "-ivXdnsAAAAJ",
}


# ═════════════ helpers ═════════════
def fetch_author_pubs(author_id: str) -> List[dict]:
    """Собрать список публикаций автора по его ID."""
    base = scholarly.search_author_id(author_id)
    full = scholarly.fill(base, sections=["publications"])
    pubs: List[dict] = []
    for p in full["publications"]:
        filled = scholarly.fill(p)
        bib    = filled.get("bib", {})
        pubs.append(
            {
                "title":        bib.get("title", ""),
                "authors":      bib.get("author", ""),
                "year":         bib.get("pub_year", ""),
                "journal":      bib.get("journal", ""),
                "volume":       bib.get("volume", ""),
                "number":       bib.get("number", ""),
                "pages":        bib.get("pages", ""),
                "publisher":    bib.get("publisher", ""),
                "citation":     bib.get("citation", ""),
                "num_citations": filled.get("num_citations", 0),
                "pub_url":      filled.get("pub_url", ""),
            }
        )
    return pubs


def best_link(pub: dict) -> str:
    """Отдать DOI → PMID → fallback‐URL."""
    blob = f'{pub.get("citation","")} {pub.get("pub_url","")}'
    doi  = re.search(r"(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", blob)
    if doi:
        return f"https://doi.org/{doi.group(1)}"
    pmid = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d{4,9})", blob)
    if pmid:
        return f"https://pubmed.ncbi.nlm.nih.gov/{pmid.group(1)}/"
    return pub.get("pub_url", "")


def short_authors(auths: str, keep: int = 3) -> str:
    """Сократить длинный список авторов до «A, B, C et al.»."""
    names = [a.strip() for a in auths.split(" and ")]
    return (", ".join(names[:keep]) + " et al.") if len(names) > keep + 3 else ", ".join(names)
# ═══════════════════════════════════


# ────────── 1. собираем публикации ──────────
all_pubs: List[dict] = []
for name, aid in AUTHOR_IDS.items():
    print(f"📥  Fetching {name} …")
    try:
        all_pubs += fetch_author_pubs(aid)
    except Exception as e:                         # noqa: BLE001
        print(f"⚠️  {name}: {e}", file=sys.stderr)

uniq: Dict[Tuple[str, str], dict] = {}
for p in all_pubs:                                # дедупликация
    key = (p["title"].lower().strip(), p.get("year"))
    uniq.setdefault(key, p)

publications = [p for p in uniq.values() if p.get("year")]
publications.sort(key=lambda x: int(x["year"]), reverse=True)

print(f"🔢  Unique publications: {len(publications)}")

# ────────── 2. сохраняем JSON ──────────
JSON_FILE.write_text(json.dumps(publications, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"💾  Saved → {JSON_FILE.relative_to(REPO_DIR)}")

# ────────── 3. генерируем HTML ──────────
block_lines: List[str] = []
for p in publications:
    link = best_link(p)
    cite = (
        f'{short_authors(p["authors"])}. '
        f'<a href="{link}" target="_blank" class="ext">{p["title"]}</a>.'
    )
    if p["journal"]:
        cite += f' <em>{p["journal"]}</em>'
    if p["volume"]:
        cite += f', <strong>{p["volume"]}</strong>'
    if p["number"]:
        cite += f'({p["number"]})'
    if p["pages"]:
        cite += f', {p["pages"]}'
    cite += f', {p["year"]}.'
    block_lines.append(f'    <div class="pub-entry"><p>{cite}</p></div>')

new_section = (
    "<section id=\"publications\">\n"
    "  <h2>Publications</h2>\n"
    "  <div class=\"publications\">\n"
    + "\n".join(block_lines) + "\n"
    "  </div>\n"
    "</section>"
)

# ────────── 4. встраиваем в index.html ──────────
html_src = INDEX_HTML.read_text(encoding="utf-8")
updated  = re.sub(
    r'<section[^>]*id=["\']publications["\'][\s\S]*?</section>',
    new_section,
    html_src,
    flags=re.IGNORECASE | re.DOTALL,
)

if updated != html_src:
    INDEX_HTML.write_text(updated, encoding="utf-8")
    print("✅  index.html updated")
else:
    print("ℹ️  index.html уже содержит свежий блок – изменений нет")

# ────────── 5. CSS-подсказка ──────────
hint_css = """
/* publications */
.pub-entry       { margin:0 0 .9rem 0; line-height:1.45; }
.pub-entry p     { text-indent:-1.6em; padding-left:1.6em; }
.pub-entry a.ext::after{
  content:"↗"; font-size:.75em; margin-left:.15em;
  vertical-align:super; opacity:.6;
}
""".strip()

style_path = REPO_DIR / "css" / "styles.css"
if "pub-entry a.ext::after" not in style_path.read_text(encoding="utf-8"):
    print(
        f"""\nℹ️  Добавьте в css/styles.css для аккуратного вида ссылок:
{hint_css}
"""
    )
