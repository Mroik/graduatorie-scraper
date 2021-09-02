import requests
import re
from datetime import datetime as dt


BASE_URL = "https://studente.unimi.it/ammissioni/g/graduatoriaprogrammati/"
ENTRY = "checkLogin.asp"

sess = requests.Session()


def find_programmes(data):
    return re.findall("(?<=Wicket\.Ajax\.ajax\({\"u\":\"\./).+?(?=\",)", data)


def main():
    data = sess.get(BASE_URL + ENTRY).text
    programs = find_programmes(data)
    with open("part1.txt", "w") as fd:
        fd.write(data)

    data = sess.get(BASE_URL + programs[0] + "&_=" + str(int(dt.now().timestamp()*1000)))
    with open("part2.txt", "w") as fd:
        fd.write(data.text)

    data = sess.post(
            BASE_URL + programs[-2],
            data={
                "id8_hf_0": "",  # id is original + 7
                "buttons:next": 1
            }
    )
    with open("part3.txt", "w") as fd:
        fd.write(data.text)


if __name__ == "__main__":
    main()
