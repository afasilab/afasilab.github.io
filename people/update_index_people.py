# from pathlib import Path
# import re

# # Paths to files
# index_path = Path("../index.html")
# people_path = Path("people/team.html")

# # Read the original files
# html = index_path.read_text(encoding="utf-8")
# team_html = people_path.read_text(encoding="utf-8")

# # Replace old <section id="people"> with new one
# html_updated = re.sub(
#     r'<section id="people">.*?</section>',
#     team_html,
#     html,
#     flags=re.DOTALL
# )

# # Write updated index.html
# index_path.write_text(html_updated, encoding="utf-8")

# print("✅ index.html updated with new people section!")

from pathlib import Path
import re

# Paths to files
index_path = Path("../index.html")
team_path = Path("people/team.html")

# Read files
index_html = index_path.read_text(encoding="utf-8")
team_html = team_path.read_text(encoding="utf-8")

# Check if <section id="people"> exists
if '<section id="people">' in index_html:
    # Replace existing people section
    updated_html = re.sub(
        r'<section id="people">.*?</section>',
        team_html,
        index_html,
        flags=re.DOTALL
    )
    print("🔄 Replaced existing <section id='people'>.")
else:
    # Insert after <section id="projects">
    updated_html = re.sub(
        r'(</section>\s*)(<!--.*?-->\s*)?(<section id="publications">)',
        f'</section>\n\n{team_html}\n\n\\3',
        index_html,
        count=1,
        flags=re.DOTALL
    )
    print("➕ Inserted <section id='people'> after 'Active Projects'.")

# Write to index.html
index_path.write_text(updated_html, encoding="utf-8")
print("✅ index.html updated successfully!")
