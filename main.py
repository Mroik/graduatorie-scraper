import hashlib
import os
import json
from time import sleep

from telegram.ext import Updater
from telegram import Bot, Chat, InputMediaDocument
from telegram.error import BadRequest, RetryAfter

from cred import BOT_KEY, CHANNEL_NAME, DOWNLOADS
from scraper import scrape


updater = Updater(token=BOT_KEY)
scraped = []


def load_data():
    global scraped
    if DOWNLOADS not in os.listdir():
        os.mkdir(DOWNLOADS)
    if "data.json" in os.listdir(DOWNLOADS):
        with open(f"{DOWNLOADS}/data.json", "r") as fd:
            scraped = json.loads(fd.read())


def save_data():
    global scraped
    if DOWNLOADS not in os.listdir():
        os.mkdir(DOWNLOADS)
    with open(f"{DOWNLOADS}/data.json", "w") as fd:
        fd.write(json.dumps(scraped))


def get_data():
    data = []
    try:
        count = 0
        while True:
            temp, course = scrape(count)
            data.append((temp, course))
            count += 1
    except IndexError:
        return data


def main():
    load_data()

    updater.start_polling()
    bot: Bot = updater.bot
    chat: Chat = bot.get_chat(CHANNEL_NAME)

    data = get_data()
    for section in data:
        to_send = []
        for pdf in section[0]:
            if pdf in scraped:
                continue
            with open(f"{DOWNLOADS}/{pdf}", "rb") as fd:
                input_document = InputMediaDocument(fd, caption=section[1], filename=pdf[33:])
            to_send.append(input_document)
            scraped.append(pdf)
        if len(to_send) == 0:
            continue
        try:
            chat.send_media_group(to_send)  # Sometimes it raises a BadRequest not sure why
        except RetryAfter as e:
            # The data that was not sent will be sent next time
            sleep(e.retry_after + 2)
            for x in to_send:
                hash_ = hashlib.md5(x.media.input_file_content).hexdigest()
                scraped.remove(f"{hash_}_{x.media.filename}")
        except BadRequest:
            # The data that was not sent will be sent next time
            for x in to_send:
                hash_ = hashlib.md5(x.media.input_file_content).hexdigest()
                scraped.remove(f"{hash_}_{x.media.filename}")

    save_data()
    updater.stop()


if __name__ == "__main__":
    main()
