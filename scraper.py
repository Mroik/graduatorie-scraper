import os
import hashlib
import re

import requests
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs

from cred import DOWNLOADS


BASE_URL = "https://studente.unimi.it/ammissioni/g/graduatoriaprogrammati/"
ENTRY = "checkLogin.asp"


def find_updater_links(data):
    ris = re.findall("(?<=Wicket\.Ajax\.ajax\({\"u\":\"\./).+?(?=\",)", data)
    return ris[:-2], ris[-2:]


def get_ids(data):
    ris = []
    soup = bs(data, "lxml")
    table = soup.find("table", class_="content-table")
    for row in table.find_all("tr"):
        col = row.find("td")
        if col is None:
            continue
        ris.append(col.get("id")[2:])
    return ris


def find_pdf(data):
    ris = []
    soup = bs(data, "lxml")
    for row in soup.find_all("ul", class_="list-group"):
        ris.append((row.li.a.string.strip(), row.li.a["href"][2:]))
    return ris


def find_course(data):
    soup = bs(data, "lxml")
    spans = soup.find_all("span")
    for x in spans:
        if x.string and "Corso" in x.string:
            return x.string.strip()


def scrape(count):
    sess = requests.Session()
    scraped = []

    data = sess.get(BASE_URL + ENTRY).text
    links, buttons = find_updater_links(data)  # buttons[0] => next, buttons[1] => previous
    ids = get_ids(data)

    stamp = dt.now().timestamp() * 1000
    resp = sess.get(
        BASE_URL + links[count] + "&_=" + str(stamp),
        headers={
            "Wicket-Ajax": "true",
            "Wicket-Ajax-BaseURL": "g/graduatoriaprogrammati/checkLogin.asp?0",
            "X-Requested-With": "XMLHttpRequest"
        }
    )

    old_ids = ids
    ids = get_ids(resp.text)  # Every time an update is called the IDs change

    resp = sess.post(
        BASE_URL + buttons[0],
        headers={
            "Wicket-Ajax": "true",
            "Wicket-Ajax-BaseURL": "g/graduatoriaprogrammati/checkLogin.asp?0",
            "Wicket-FocusedElementId": "{:x}".format(int(old_ids[count], 16) + len(ids) + 1)
        },
        data={
            "id{:x}_hf_0".format(int(old_ids[count], 16) + len(ids)): "",
            "buttons:next": "1"
        }
    )

    pdfs = find_pdf(resp.text)
    course = find_course(resp.text)
    for x in pdfs:
        resp = sess.get(BASE_URL + x[1])
        hash_ = str(hashlib.md5(resp.content).hexdigest())
        with open(f"{DOWNLOADS}/{hash_ + '_' + x[0]}", "wb") as fd:
            fd.write(resp.content)
        scraped.append(hash_ + "_" + x[0])
    return scraped, course


def main():
    count = 0
    try:
        while True:
            scrape(count)
            count += 1
    except IndexError:
        return


if __name__ == "__main__":
    main()
