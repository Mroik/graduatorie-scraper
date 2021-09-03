import datetime

import requests
import re
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs


BASE_URL = "https://studente.unimi.it/ammissioni/g/graduatoriaprogrammati/"
ENTRY = "checkLogin.asp"

sess = requests.Session()


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


def main():
    # TODO Remove logging [DEBUG]
    data = sess.get(BASE_URL + ENTRY).text
    links, buttons = find_updater_links(data)  # buttons[0] => next, buttons[1] => previous
    ids = get_ids(data)

    stamp = datetime.datetime.now().timestamp() * 1000
    resp = sess.get(
        BASE_URL + links[0] + "&_=" + str(stamp),
        headers={
            "Wicket-Ajax": "true",
            "Wicket-Ajax-BaseURL": "g/graduatoriaprogrammati/checkLogin.asp?0",
            "X-Requested-With": "XMLHttpRequest"
        }
    )
    with open("part1.txt", "w") as fd:
        fd.write(resp.text)

    old_ids = ids
    ids = get_ids(resp.text)  # Every time an update is called the IDs change

    resp = sess.post(
        BASE_URL + buttons[0],
        headers={
            "Wicket-Ajax": "true",
            "Wicket-Ajax-BaseURL": "g/graduatoriaprogrammati/checkLogin.asp?0",
            "Wicket-FocusedElementId": f"{int(old_ids[0]) + 8}"
        },
        data={
            f"id{int(old_ids[0]) + 7}_hf_0": "",
            "buttons:next": "1"
        }
    )
    with open("part2.txt", "w") as fd:
        fd.write(resp.text)

    pdfs = find_pdf(resp.text)
    for x in pdfs:
        resp = sess.get(BASE_URL + x[1])
        with open(x[0], "wb") as fd:
            fd.write(resp.content)


if __name__ == "__main__":
    main()
