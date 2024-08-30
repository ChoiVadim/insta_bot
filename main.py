import os
from winsound import Beep

from dotenv import load_dotenv

from const import *
from helpers import InstagramBot

load_dotenv()


def main() -> None:
    with InstagramBot(
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
    ) as my_bot:

        my_bot.like_follow_comment_by_hashtag(
            hashtags=popular_hashtags,
            comments=comments,
        )

    Beep(frequency, duration)


if __name__ == "__main__":
    main()
