from winsound import Beep

from instagrapi import Client

from const import *
from helpers import *


def main():
    cl = Client()
    login(cl)
    like_follow_comment_by_hashtag(cl, popular_hashtags, comments)
    # unfollow_followers(cl, 10)
    Beep(frequency, duration)


if __name__ == "__main__":
    main()
