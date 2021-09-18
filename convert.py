import json
from cred import DOWNLOADS

with open(f"{DOWNLOADS}/data.json", "r") as fd:
    scraped = json.loads(fd.read())
with open(f"{DOWNLOADS}/data.json", "w") as fd:
    fd.write(json.dumps([scraped, []]))
