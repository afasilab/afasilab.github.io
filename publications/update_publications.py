#!/usr/bin/env python3
"""
update_publications.py
-------------------------------------------
Скачивает публикации сразу из двух профилей Google Scholar
(Ruslan Afasizhev, Inna Afasizheva), сохраняет метаданные
в JSON и обновляет блок <section id="publications"> … </section>
в корневом index.html.
-------------------------------------------
pip install "scholarly>=1.7.11"
"""

import json
import re
from datetime import datetime
from pathlib import Path

from scholarly import scholarly

# ──────────────── настройки путей ────────────────
SCRIPT_DIR = Path(__file__).resolve().parent          # …/publications
REPO_DIR   = SCRIPT_DIR.parent                       # …/afasilab.github.io
INDEX_HTML = REPO_DIR / "index.html"

GS_DIR     = REPO_DIR / "publications" / "gs_json"
GS_DIR.mkdir(parents=True, exist_ok=True)

today        = datetime.today().strftime("%m-%d-%Y")
JSON_FILE    = GS_DIR / f"publications_detailed_{today}.json"

AUTHOR_IDS = {
    "Ruslan Afasizhev": "U7yVbHIAAAAJ",
    "Inna Afasizheva":  "-ivXdnsAAAAJ",
}
# ────────────────────────────────────────────────


def fetch_author_pubs(author_id: str) -> list[dict]:
    """Вернуть список публикаций автора по его Google-Scholar ID."""
    base = scholarly.search_author_id(author_id)
    full = scholarly.fill(base, sections=["publications"])
    pubs = []
    for pub in full["publications"]:
        filled = scholarly.fill(pub)
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
                "abstract":     bib.get("abstract", ""),
                "num_citations": filled.get("num_citations", 0),
                "pub_url":      filled.get("pub_url", ""),
            }
        )
    return pubs


# ──────────────── 1. собираем все публикации ────────────────
all_pubs = []
for name, aid in AUTHOR_IDS.items():
    print(f"📥  Fetching publications for {name} …")
    all_pubs.extend(fetch_author_pubs(aid))

# дедупликация (title + year)
uniq: dict[tuple[str, str], dict] = {}
for p in all_pubs:
    key = (p["title"].lower().strip(), p.get("year"))
    uniq.setdefault(key, p)
publications = list(uniq.values())

# отбрасываем записи без года и сортируем
publications = [p for p in publications if p.get("year")]
publications.sort(key=lambda x: int(x["year"]), reverse=True)

print(f"🔢  Total unique publications: {len(publications)}")

# ──────────────── 2. сохраняем JSON ────────────────
with JSON_FILE.open("w", encoding="utf-8") as f:
    json.dump(publications, f, ensure_ascii=False, indent=2)
print(f"💾  Saved metadata → {JSON_FILE.relative_to(REPO_DIR)}")

# ──────────────── 3. генерируем HTML блок ────────────────
blocks = []
for p in publications:
    cite = f'{p["authors"]}. {p["title"]}.'
    if p["journal"]:
        cite += f' <em>{p["journal"]}</em>'
    if p["volume"]:
        cite += f', <strong>{p["volume"]}</strong>'
    if p["number"]:
        cite += f'({p["number"]})'
    if p["pages"]:
        cite += f', {p["pages"]}'
    cite += f', {p["year"]}.'

    url  = p["pub_url"]
    blocks.append(
        f'''    <div class="pub-entry">
      <p>{cite}<br><em>(<a href="{url}" target="_blank">Link</a>)</em></p>
    </div>'''
    )

new_section = (
    "<section id=\"publications\">\n"
    "  <h2>Publications</h2>\n"
    "  <div class=\"publications\">\n"
    f"{chr(10).join(blocks)}\n"
    "  </div>\n"
    "</section>"
)

# ──────────────── 4. вставляем в index.html ────────────────
html = INDEX_HTML.read_text(encoding="utf-8")

pattern = r"<section[^>]*id=[\"']publications[\"'][\s\S]*?</section>"
updated = re.sub(pattern, new_section, html, flags=re.IGNORECASE | re.DOTALL)

if updated != html:
    INDEX_HTML.write_text(updated, encoding="utf-8")
    print("✅ index.html updated with fresh publication list")
else:
    print("ℹ️  index.html already up-to-date — no changes made")
