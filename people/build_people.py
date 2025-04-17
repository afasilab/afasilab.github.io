from pathlib import Path

# ==== OUR TEAM DATA ====
people = [
    {
        "name": "Ruslan Afasizhev, PhD",
        "title": "Professor of Molecular & Cell Biology",
        "email": "ruslana@bu.edu",
        "phone": "617-358-3773",
        "image": "ruslan.jpeg",
        "bio": "Dr. Afasizhev leads research on mitochondrial RNA processing in Trypanosoma brucei. He has authored over 40 scientific publications and trained at HHMI UCLA. He is a member of the RNA Society and the American Society for Microbiology.",
        "links": {
            "Google Scholar": "https://scholar.google.com/citations?user=U7yVbHIAAAAJ",
            "LinkedIn": "https://www.linkedin.com/in/ruslan-afasizhev"
        }
    },
    {
        "name": "Inna Afasizheva, PhD",
        "title": "Associate Professor of Molecular & Cell Biology",
        "email": "innaaf@bu.edu",
        "phone": "617-358-4485",
        "image": "inna.jpeg",
        "bio": "Dr. Afasizheva’s research focuses on mitochondrial RNA processing in trypanosomes, emphasizing mechanisms of polyadenylation, uridylation, and roles of pentatricopeptide repeat proteins (PPRs).",
        "links": {}
    },
    {
        "name": "Takuma Suematsu, PhD",
        "title": "Research Assistant Professor of Molecular & Cell Biology",
        "email": "tsuemats@bu.edu",
        "phone": "617-358-4485",
        "image": "",  # No image provided
        "bio": "Dr. Suematsu specializes in molecular biology and RNA biology with a focus on the biochemistry of RNA processing in mitochondria. He earned his PhD from the University of Tokyo in 2008.",
        "links": {}
    }
]

# ==== HTML Creation ====
output = '<section id="people">\n  <h2>Our Team</h2>\n'

for person in people:
    output += f'  <div class="team-member">\n'
    if person["image"]:
        output += f'    <img src="people/team_images/{person["image"]}" alt="{person["name"]}" width="120"><br>\n'
    output += f'    <h3>{person["name"]}</h3>\n'
    output += f'    <p><strong>{person["title"]}</strong><br>\n'
    output += f'    <a href="mailto:{person["email"]}">{person["email"]}</a> | {person["phone"]}</p>\n'
    output += f'    <p>{person["bio"]}</p>\n'
    if person["links"]:
        output += '    <p>' + ' | '.join(f'<a href="{url}" target="_blank">{label}</a>' for label, url in person["links"].items()) + '</p>\n'
    output += '  </div>\n\n'

output += '</section>\n'

# ==== Save to people/team.html ====
team_path = Path("people/team.html")
team_path.parent.mkdir(parents=True, exist_ok=True)
team_path.write_text(output, encoding='utf-8')

print("✅ people/team.html is created successfully!")
