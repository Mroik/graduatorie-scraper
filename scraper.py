import hashlib
from os import mkdir, rename
import re

import requests
from bs4 import BeautifulSoup as bs
import pdfkit

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
        if resp.status_code != 200:
            continue
        hash_ = hashlib.md5(resp.content).hexdigest()
        with open(f"{DOWNLOADS}/{hash_ + '_' + links[x][0]}", "wb") as fd:
            fd.write(resp.content)
        scraped.append(f"{hash_ + '_' + links[x][0]}")
    return scraped


def generate_rankings(data):
    try:
        mkdir(DOWNLOADS)
    except FileExistsError:
        pass
    ris = "<html><body><table border='1px solid'><tr><td colspan=2><b>"
    students = []
    course_name = ""
    pub_date = ""
    soup = bs(data, "lxml")
    spans = soup.find_all("span")
    tbody = soup.find("tbody")

    # Find course name
    for span in spans:
        if span.string and "Corso " in span.string:
            course_name = re.findall("(?<=in ).*", span.string.strip())[0]
            ris += course_name + "</b></td></tr>"
            break

    # Find publish date
    for span in spans:
        if span.string and "Data di" in span.string:
            pub_date = re.findall("\\d+/\\d+/\\d+", span.string.strip())[0]
            pub_date = pub_date.replace("/", "-")

    # Scrape rankings
    for row in tbody.find_all("tr"):
        cols = row.find_all("td")
        students.append((int(cols[1].span.string.strip()), cols[0].a.string.strip()))

    # Sorting
    for x in range(len(students) - 1):
        for y in range(x + 1, len(students)):
            if students[x][0] > students[y][0]:
                temp = students[x]
                students[x] = students[y]
                students[y] = temp

    for student in students:
        ris += "<tr>"
        ris += f"<td>{student[0]}</td>"
        ris += f"<td>{student[1]}</td>"
        ris += "</tr>"
    ris += "</table></body></html>"
    filename = f"{course_name}_{pub_date}.pdf"
    pdfkit.from_string(ris, f"{DOWNLOADS}/" + filename, options={"--log-level": "none"})
    return filename


def scrape():
    sess = requests.Session()
    scraped = []
    rankings_generated = {}

    resp = sess.get(BASE_URL + ENTRY)
    links = find_links(resp.text)

    for link in links:
        resp = sess.get(BASE_URL + link)
        if resp.status_code != 200:
            continue
        pdf_links = find_pdf(resp.text)
        course_name = find_course(resp.text)
        rankings_generated[course_name] = generate_rankings(resp.text)
        scraped.append(((download_pdfs(sess, pdf_links)), course_name))
    return scraped, rankings_generated


def main():
    a, b = scrape()
    print(a)
    print("------")
    print(b)
    print("------")
    print("Done")


if __name__ == "__main__":
    main()
