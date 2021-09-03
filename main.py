import botogram

from cred import BOT_KEY, CHANNEL_NAME
from scraper import scrape


bot = botogram.create(BOT_KEY)
scraped = []


@bot.timer(86400)
def check_grad(bot, shared):
    chan = botogram.channel(CHANNEL_NAME, BOT_KEY)
    try:
        count = 0
        while True:
            temp = scrape(count)
            for x in temp:
                if x not in scraped:
                    chan.send_file(path=x)
                    scraped.append(x)
            count += 1
    except IndexError:
        pass


def main():
    bot.run()


if __name__ == "__main__":
    main()
