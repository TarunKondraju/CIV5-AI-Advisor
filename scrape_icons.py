import os
import json
import urllib.request
import urllib.parse
import re

ICONS_DIR = "icons"
if not os.path.exists(ICONS_DIR):
    os.makedirs(ICONS_DIR)

print("Fetching Category Members from Civilization Wiki...")
api_url = "https://civilization.fandom.com/api.php?action=query&list=categorymembers&cmtitle=Category:Civilization_icons_(Civ5)&cmlimit=100&format=json"

req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())

members = data['query']['categorymembers']
print(f"Found {len(members)} items in the category.")

for m in members:
    title = m['title']
    if title.startswith("File:") and ".png" in title:
        civ_name = title.replace("File:", "").replace(" (Civ5).png", "").replace(".png", "")
        
        encoded_title = urllib.parse.quote(title)
        img_api = f"https://civilization.fandom.com/api.php?action=query&titles={encoded_title}&prop=imageinfo&iiprop=url&format=json"
        
        try:
            img_req = urllib.request.Request(img_api, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(img_req) as img_resp:
                img_data = json.loads(img_resp.read().decode())
                pages = img_data['query']['pages']
                for page_id, page_info in pages.items():
                    if 'imageinfo' in page_info:
                        img_url = page_info['imageinfo'][0]['url']
                        filepath = os.path.join(ICONS_DIR, f"{civ_name}.png")
                        urllib.request.urlretrieve(img_url, filepath)
                        print(f"✅ Downloaded {civ_name}.png")
        except Exception as e:
            print(f"❌ Failed to download {civ_name}: {e}")

print("Done downloading icons!")
