from pathlib import Path
import re

# Paths to files
index_path = Path("../index.html")
people_path = Path("people/team.html")

# Read the original files
html = index_path.read_text(encoding="utf-8")
team_html = people_path.read_text(encoding="utf-8")

# Replace old <section id="people"> with new one
html_updated = re.sub(
    r'<section id="people">.*?</section>',
    team_html,
    html,
    flags=re.DOTALL
)

# Write updated index.html
index_path.write_text(html_updated, encoding="utf-8")

print("✅ index.html updated with new people section!")
