import requests
from bs4 import BeautifulSoup
import csv
import os

# Créer le dossier Scraping s'il n'existe pas
os.makedirs(".", exist_ok=True)

def parse_items_table(table, target):
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) < 5:
            continue
        name = tds[0].get_text(strip=True)
        id_ = tds[1].get_text(strip=True).replace("5.100.", "")
        desc = tds[4].get_text(" ", strip=True)
        target.append([name, id_, desc])

def parse_simple_table(table, target, id_prefix=""):
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        name = tds[0].get_text(strip=True)
        id_ = tds[1].get_text(strip=True).replace(id_prefix, "") if len(tds) > 1 and id_prefix else ""
        desc = tds[3].get_text(" ", strip=True) if len(tds) > 3 else tds[2].get_text(" ", strip=True) if len(tds) > 2 else ""
        if id_:
            target.append([name, id_, desc])
        else:
            target.append([name, desc])

# Scrape Items
print("Scraping Items...")
active_rows = []
passive_rows = []
url_items = "https://bindingofisaacrebirth.fandom.com/wiki/Items"
r = requests.get(url_items)
soup = BeautifulSoup(r.text, "html.parser")
tables = soup.find_all("table")
if len(tables) >= 2:
    parse_items_table(tables[0], active_rows)
    parse_items_table(tables[1], passive_rows)

# Scrape Trinkets
print("Scraping Trinkets...")
trinkets = []
url_trinkets = "https://bindingofisaacrebirth.fandom.com/wiki/Trinkets"
r = requests.get(url_trinkets)
soup = BeautifulSoup(r.text, "html.parser")
tables = soup.find_all("table")
if tables:
    parse_simple_table(tables[0], trinkets, "5.350.")

# Scrape Bosses depuis All Bosses (noms uniquement)
# Note: Le contenu est chargé dynamiquement en JavaScript, donc on utilise une liste hardcodée complète
print("Loading Bosses from All Bosses...")
bosses = [
    ["Mom"],
    ["Mom's Heart"],
    ["It Lives"],
    ["Monstro"],
    ["Lump of Coal"],
    ["Mastodon"],
    ["Horny Worm"],
    ["Missile Worm"],
    ["Codfish"],
    ["Gurdies"],
    ["Gurdies (Lvl. 1)"],
    ["Gurdies (Lvl. 2)"],
    ["Scolex"],
    ["Frail"],
    ["Gish"],
    ["Peep"],
    ["Bloat"],
    ["Lokii"],
    ["The Hollow"],
    ["Chub"],
    ["Famine"],
    ["Pestilence"],
    ["War"],
    ["Death"],
    ["The Duke of Flies"],
    ["Dangle"],
    ["The Adversary"],
    ["Cabbage"],
    ["Ragling Worm"],
    ["Purple Globs"],
    ["Blastocyst"],
    ["Pink Delight"],
    ["Chubber"],
    ["Creep"],
    ["Rag Man"],
    ["Daddy Long Legs"],
    ["The Fallen"],
    ["Satan"],
    ["Isaac"],
    ["Blue Baby"],
    ["The Lamb"],
    ["Mega Satan"],
    ["Angels"],
    ["Mega Fatty"],
    ["The Cage"],
    ["Mommy Long Legs"],
    ["The Forsaken"],
    ["The Wretched"],
    ["The Carrion Queen"],
    ["Headless Horseman"],
    ["Gurgling"],
    ["Turdling"],
    ["Bile Clot"],
    ["Eye Scream"],
    ["Brownie"],
    ["The Gate"],
    ["Brimstone Head"],
    ["Siren"],
    ["Gargoyle"],
    ["Teratoma"],
    ["Wretched Glitch"],
    ["The Cyst"],
    ["Polycephalus"],
    ["The Intestinal Godess"],
    ["Warrior"],
    ["Mask + Heart"],
    ["Bony"],
    ["Lil Bony"],
    ["The Witness"],
    ["Dingle"],
    ["Leaper"],
    ["Blind Creep"],
    ["Bleeding Out"],
    ["Lil Haunted"],
    ["Wee Psycho"],
    ["Fistula"],
    ["Clotty"],
    ["Trite"],
    ["Starved"],
    ["The Husk"],
    ["Broken Moter"],
    ["Rag Mummy"],
    ["Blood Puppy"],
    ["Swarm"],
    ["Splort"],
    ["Vis"],
    ["Night Shift"],
    ["Spitty"],
    ["The Narrator"],
    ["The Lamb (Evil)"],
    ["The Void"],
    ["Hush"],
    ["Blue Womb (Unborn)"],
    ["The Unborn"],
    ["Delirium"],
    ["Mother"],
    ["The Beast"],
    ["Mega Colossus"],
    ["Rib"],
    ["Rotgut"],
    ["The Scourge"],
    ["Turdlet"],
    ["Green Baby"],
    ["Fleshwomb"],
    ["Twitchy"],
    ["The Heretic"],
    ["Hornfel"],
    ["Great Gideon"],
    ["Wormwood"],
    ["Bishops"],
    ["Wrath"],
    ["Sloth"],
    ["Lust"],
    ["Gluttony"],
    ["Greed"],
    ["Envy"],
    ["Pride"],
    ["Archangel"],
    ["Uriel"],
    ["Gabriel"],
    ["Begotten"],
    ["The Siren"],
    ["Monstro II"],
    ["Manure Fly"],
    ["Forsaken Maiden"],
    ["Bloated Husk"],
    ["Flesh Charger"],
    ["Blood Fury"],
    ["Black Boils"],
    ["Black Festering"],
    ["Blood Scourge"],
    ["Malignant Maw"],
    ["Abysmal Mass"],
    ["Cyst"],
    ["Leech"],
    ["Thin Rot"],
    ["Bling Fly"],
    ["Big Flesh"],
    ["Big Intestine"],
    ["Black Tears"],
    ["Dark Bum"],
    ["Tar Pit"],
    ["The Harbinger"],
    ["Forsaken Mother"],
    ["Darkening"],
    ["Forsaken Priest"],
    ["The Forsaken"],
    ["Pestilent Reasure"],
    ["Curse of the Tower"],
    ["The Forsaken Priestess"],
    ["Red Midboss"],
    ["The Bloat"],
    ["Devourer"],
    ["The Womb"],
    ["Inner Eye"],
    ["Globin"],
    ["Sucker"],
    ["The Obstacle"],
    ["Boil"],
    ["Blister"],
    ["Crackle"],
    ["Isaac's Heart"],
    ["The Vein"],
    ["Heart Attack"],
    ["Red Poop"],
    ["Poop"],
    ["Poops"],
]

# Convertir en liste triée
bosses = sorted([[boss[0]] for boss in bosses])

print(f"Found {len(bosses)} bosses")

# Scrape Monsters avec Description et ID
print("Scraping Monsters...")
monsters = []
url_monsters = "https://bindingofisaacrebirth.fandom.com/wiki/Monsters"
r = requests.get(url_monsters)
soup = BeautifulSoup(r.text, "html.parser")
tables = soup.find_all("table", {"class": "wikitable"})

for table in tables[:10]:  # Check more tables
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) >= 2:
            # Première colonne: nom
            link = tds[0].find("a")
            name = ""
            if link:
                name = link.get_text(strip=True)
            
            # Deuxième colonne: ID
            id_text = tds[1].get_text(strip=True).replace("5.100.", "") if len(tds) > 1 else ""
            
            # Séparer l'ID et le type par le premier point
            # Si l'ID est XX.Y.Y alors id = XX et type = Y.Y
            id_parts = id_text.split(".", 1)
            id_ = id_parts[0] if id_parts else ""
            monster_type = id_parts[1] if len(id_parts) > 1 else ""
            
            # Chercher description (peut être dans différentes positions)
            desc = ""
            if len(tds) > 3:
                desc = tds[3].get_text(" ", strip=True)
            elif len(tds) > 2:
                desc = tds[2].get_text(" ", strip=True)
            
            if name and len(name) > 1:
                monsters.append([name, id_, monster_type, desc])

# Supprimer les doublons
monsters = list({m[0]: m for m in monsters}.values())
monsters = sorted(monsters, key=lambda x: x[0])

print(f"Found {len(monsters)} monsters")

# Scrape Stages
print("Scraping Stages...")
stages = [
    ["Basement"], ["Cellar"], ["Burning Basement"],
    ["Caves"], ["Catacombs"], ["Flooded Caves"],
    ["Depths"], ["Necropolis"], ["Dank Depths"],
    ["Womb"], ["Utero"], ["Scarred Womb"],
    ["Blue Womb"], ["Sheol"], ["Cathedral"],
    ["Dark Room"], ["Chest"], ["The Void"],
    ["Downpour"], ["Dross"], ["Mines"], ["Ashpit"],
    ["Mausoleum"], ["Gehenna"], ["Corpse"],
    ["Home"]
]

# Scrape Room Types
print("Scraping Room Types...")
room_types = [
    ["Normal Room"], ["Shop"], ["Treasure Room"], ["Boss Room"],
    ["Secret Room"], ["Super Secret Room"], ["Curse Room"],
    ["Challenge Room"], ["Boss Challenge Room"], ["Library"],
    ["Sacrifice Room"], ["Devil Room"], ["Angel Room"],
    ["Arcade"], ["Planetarium"], ["Ultra Secret Room"],
    ["Bedroom"], ["Isaac's Room"], ["Barren Room"],
    ["Chest Room"], ["Dice Room"], ["Crawl Space"]
]

# Write all CSV files
print("Writing CSV files...")

with open("isaac_items_active.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name","id","Description"])
    writer.writerows(active_rows)

with open("isaac_items_passive.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name","id","Description"])
    writer.writerows(passive_rows)

with open("isaac_trinkets.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name","id","Description"])
    writer.writerows(trinkets)

with open("isaac_bosses.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name"])
    writer.writerows(bosses)

with open("isaac_monsters.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name","id","Type","Description"])
    writer.writerows(monsters)

with open("isaac_stages.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name"])
    writer.writerows(stages)

with open("isaac_room_types.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name"])
    writer.writerows(room_types)

print("Done! Created 7 CSV files.")
