import os
import random
import logging

from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from instagrapi.exceptions import MediaUnavailable


load_dotenv()

logging.basicConfig(
    filename="log.log",
    level=logging.INFO,
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)


def login(cl: Client) -> None:
    username = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")
    session = cl.load_settings("session.json")

    login_via_session = False
    login_via_pw = False

    # Check if session is valid
    if session:
        try:
            cl.set_settings(session)
            cl.login(username, password)

            try:
                cl.get_timeline_feed()
            except LoginRequired:
                logging.error(
                    "Session is invalid, need to login via username and password"
                )

                old_session = cl.get_settings()

                # use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])

                cl.login(username, password)
            login_via_session = True

        except Exception as e:
            logging.error("Couldn't login user using session information: %s" % e)

    # If session is not valid login via username and password
    if not login_via_session:
        try:
            print(
                "Attempting to login via username and password. username: %s" % username
            )
            if cl.login(username, password):
                login_via_pw = True
        except Exception as e:
            logging.error("Couldn't login user using username and password: %s" % e)

    # Raise exception if session and username and password are not valid
    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")


def like_follow_comment_by_hashtag(
    cl: Client,
    hashtags: str,
    comments: list,
    comment: bool = False,
    follow: bool = False,
) -> None:
    for hashtag in hashtags[:]:
        medias = cl.hashtag_medias_recent(hashtag, 20)
        try:
            for i, media in enumerate(medias, 1):
                cl.media_like(media.id)
                print(f"Liked post number {i} of hashtag {hashtag}")
                cl.delay_range = [6, 11]

                if follow:
                    if i % 5 == 0:
                        cl.user_follow(media.user.pk)
                        print(f"Followed user: {media.user.username}")
                        cl.delay_range = [4, 10]

                if comment:
                    if i % 4 == 0:
                        random_comment = random.choice(comments)
                        cl.media_comment(media.id, random_comment)
                        print(f"Commented on post number {i} of hashtag {hashtag}")
                        cl.delay_range = [2, 6]

        except MediaUnavailable:
            print("Media Unavailable!!!")


def unfollow_followers(cl: Client, amount: int) -> None:
    count = 0
    followers = cl.user_following(cl.user_id)

    for user_id in followers.keys():
        if count < amount:
            cl.user_unfollow(user_id)
            print(f"Unfollowed users: {count}")
            cl.delay_range = [1, 3]
            count += 1
