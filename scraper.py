import hashlib

import requests
from bs4 import BeautifulSoup as bs
from os import mkdir

from cred import DOWNLOADS


BASE_URL = "https://studente.unimi.it/graduatorie/selezioneCorso/it/"
ENTRY = "P.html"


def find_pdf(data):
    ris = []
    soup = bs(data, "lxml")
    for row in soup.find_all("ul", class_="list-group"):
        ris.append([row.li.a.string.strip(), row.li.a["href"][18:]])
    return ris


def find_course(data):
    soup = bs(data, "lxml")
    for x in soup.find_all("span"):
        if x.string and "Corso" in x.string:
            return x.string.strip()


def find_links(data):
    links = []
    soup = bs(data, "lxml")
    tbody = soup.find("tbody")
    for tr in tbody.find_all("tr"):
        links.append(tr.td.a["href"])
    return links


def download_pdfs(sess, links):
    scraped = []
    try:
        mkdir(DOWNLOADS)
    except FileExistsError:
        pass
    for x in range(len(links)):
        resp = sess.get("https://studente.unimi.it/graduatorie/" + links[x][1])
        hash_ = hashlib.md5(resp.content).hexdigest()
        with open(f"{DOWNLOADS}/{hash_ + '_' + links[x][0]}", "wb") as fd:
            fd.write(resp.content)
        scraped.append(f"{hash_ + '_' + links[x][0]}")
    return scraped


def scrape():
    sess = requests.Session()
    scraped = []

    resp = sess.get(BASE_URL + ENTRY)
    links = find_links(resp.text)

    for link in links:
        resp = sess.get(BASE_URL + link)
        pdf_links = find_pdf(resp.text)
        scraped.append(((download_pdfs(sess, pdf_links)), find_course(resp.text)))
    return scraped


def main():
    scrape()
    print("Done")


if __name__ == "__main__":
    main()
