#!/usr/bin/env python3
"""
update_publications.py
-------------------------------------------
Собирает публикации сразу у двух профилей (Google Scholar) —
Ruslan Afasizhev и Inna Afasizheva,
записывает JSON и автоматически обновляет
секцию <section id="publications"> … </section> в index.html
-------------------------------------------
pip install scholarly==1.7.11   # версия ≥1.7 (лучше зафиксировать)
"""

import json, re
from datetime import datetime
from pathlib import Path

from scholarly import scholarly

# ---------- настройки ----------
AUTHOR_IDS = {
    "Ruslan Afasizhev": "U7yVbHIAAAAJ",
    "Inna Afasizheva": "ivXdnsAAAAJ&hl",  # https://scholar.google.com/citations?user=-ivXdnsAAAAJ&hl=en
}

BASE_DIR  = Path(__file__).resolve().parent        # …/afasilab.github.io
GS_DIR    = BASE_DIR / "publications" / "gs_json"
INDEX_HTML = BASE_DIR / "index.html"

GS_DIR.mkdir(parents=True, exist_ok=True)
today     = datetime.today().strftime("%m-%d-%Y")
json_file = GS_DIR / f"publications_detailed_{today}.json"
# ---------------------------------

def fetch_author_pubs(aid: str) -> list[dict]:
    """Вернуть список публикаций автора по Google-Scholar ID."""
    author_base = scholarly.search_author_id(aid)
    author_full = scholarly.fill(author_base, sections=["publications"])
    pubs = []
    for pub in author_full["publications"]:
        filled = scholarly.fill(pub)
        bib    = filled.get("bib", {})
        pubs.append(
            {
                "title":       bib.get("title", ""),
                "authors":     bib.get("author", ""),
                "year":        bib.get("pub_year", ""),
                "journal":     bib.get("journal", ""),
                "volume":      bib.get("volume", ""),
                "number":      bib.get("number", ""),
                "pages":       bib.get("pages", ""),
                "publisher":   bib.get("publisher", ""),
                "abstract":    bib.get("abstract", ""),
                "num_citations": filled.get("num_citations", 0),
                "pub_url":     filled.get("pub_url", ""),
            }
        )
    return pubs


# ---------- 1. собираем и объединяем ----------
all_pubs = []
for name, aid in AUTHOR_IDS.items():
    print(f"📥  Fetching publications for {name} …")
    all_pubs.extend(fetch_author_pubs(aid))

# дедупликация (по названию + году)
unique = {}
for p in all_pubs:
    key = (p["title"].lower().strip(), p.get("year"))
    if key not in unique:
        unique[key] = p
publications = list(unique.values())

# фильтр по году + сортировка
publications = [p for p in publications if p.get("year")]
publications.sort(key=lambda x: int(x["year"]), reverse=True)

# ---------- 2. сохраняем JSON ----------
with json_file.open("w", encoding="utf-8") as f:
    json.dump(publications, f, ensure_ascii=False, indent=2)
print(f"💾  Saved metadata → {json_file.relative_to(BASE_DIR)}")

# ---------- 3. генерируем HTML ----------
blocks = []
for p in publications:
    authors = p["authors"]
    title   = p["title"]
    journal = p["journal"]; volume = p["volume"]
    number  = p["number"];  pages  = p["pages"]
    year    = p["year"];    url    = p["pub_url"]

    cite = f"{authors}. {title}."
    if journal: cite += f" <em>{journal}</em>"
    if volume:  cite += f", <strong>{volume}</strong>"
    if number:  cite += f"({number})"
    if pages:   cite += f", {pages}"
    cite += f", {year}."

    blocks.append(
        f"""    <div class="pub-entry">
      <p>{cite}<br><em>(<a href="{url}" target="_blank">Link</a>)</em></p>
    </div>"""
    )

pub_section = f"""
<section id="publications">
  <h2>Publications</h2>
  <div class="publications">
{chr(10).join(blocks)}
  </div>
</section>
"""

# ---------- 4. вставляем в index.html ----------
html_text = INDEX_HTML.read_text(encoding="utf-8")
html_text = re.sub(
    r"<section id=\"publications\">[\\s\\S]*?</section>",
    pub_section,
    html_text,
    flags=re.DOTALL,
)
INDEX_HTML.write_text(html_text, encoding="utf-8")
print("✅ index.html updated with fresh publication list")
