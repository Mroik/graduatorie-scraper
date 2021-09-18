import os
import re
import json
from time import sleep

from telegram.ext import Updater
from telegram import Bot, Chat, InputMediaDocument
from telegram.error import BadRequest, RetryAfter

from cred import BOT_KEY, CHANNEL_NAME, DOWNLOADS
from scraper import scrape


updater = Updater(token=BOT_KEY)
scraped = []
rankings_generated = []


def load_data():
    global scraped
    global rankings_generated
    if DOWNLOADS not in os.listdir():
        os.mkdir(DOWNLOADS)
    if "data.json" in os.listdir(DOWNLOADS):
        with open(f"{DOWNLOADS}/data.json", "r") as fd:
            data = json.loads(fd.read())
            scraped = data[0]
            rankings_generated = data[1]


def save_data():
    global scraped
    global rankings_generated
    if DOWNLOADS not in os.listdir():
        os.mkdir(DOWNLOADS)
    with open(f"{DOWNLOADS}/data.json", "w") as fd:
        fd.write(json.dumps([scraped, rankings_generated]))


def generate_caption(caption):
    caption = "📜 " + caption + "\n\n▶️ @studenti_unimi | studentiunimi.it"
    exp = re.compile(r"(?:\(CLASSE*\s)(\w+-\w+)", re.IGNORECASE)
    matches = exp.findall(caption)
    if len(matches) > 0:
        match = matches[0]
        caption = caption.replace(match, f"#{match.replace('-', '_')}")
    return caption


def main():
    try:
        os.mkdir(DOWNLOADS)
    except FileExistsError:
        pass

    load_data()
    bot: Bot = updater.bot
    chat: Chat = bot.get_chat(CHANNEL_NAME)

    docs, rankings = scrape()
    for section in docs:
        to_send = []
        for pdf in section[0]:
            if pdf not in scraped:
                to_send.append(pdf)
        send_group = []
        for pdf in to_send:
            with open(f"{DOWNLOADS}/{pdf}", "rb") as fd:
                input_document = InputMediaDocument(
                    fd,
                    # attach caption only to the last element in the group
                    caption=generate_caption(section[1]) if len(send_group) == len(to_send)-1 else None,
                    filename=pdf[33:],
                )
            send_group.append(input_document)
            scraped.append(pdf)

        if rankings[section[1]] not in rankings_generated:
            with open(f"{DOWNLOADS}/{rankings[section[1]]}", "rb") as fd:
                send_group.append(InputMediaDocument(
                    fd,
                    filename=rankings[section[1]]
                ))
            rankings_generated.append(rankings[section[1]])

        print("Sending", section[1])
        if len(send_group) == 0:
            continue
        while True:
            try:
                chat.send_media_group(send_group)  # Sometimes it raises a BadRequest not sure why
                break
            except RetryAfter as e:
                sleep(e.retry_after + 2)
            except BadRequest:
                sleep(10)

    save_data()


if __name__ == "__main__":
    main()
