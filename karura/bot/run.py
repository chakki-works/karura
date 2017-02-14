import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from slackbot.bot import Bot


def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
