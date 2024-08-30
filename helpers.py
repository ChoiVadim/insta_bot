import random
import logging

import colorama
from instagrapi import Client  # type: ignore
from instagrapi.exceptions import LoginRequired  # type: ignore
from instagrapi.exceptions import MediaUnavailable  # type: ignore


logging.basicConfig(
    filename="log.log",
    level=logging.INFO,
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)


def progress_bar(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=80,
    fill="█",
    printEnd="\r",
):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)

    print(
        colorama.Fore.YELLOW + f"\r{prefix} |{bar}| {percent}% {suffix}",
        end=printEnd,
    )

    if iteration == total:
        print(
            colorama.Fore.GREEN + f"\r{prefix} |{bar}| {percent}% {suffix}",
            end=printEnd,
        )
        print(colorama.Fore.RESET)


class InstagramBot:
    def __init__(self, username: str | None, password: str | None) -> None:
        self.cl = Client()
        self.username = username
        self.password = password
        self.session = self.cl.load_settings("session.json")
        self.is_logged_in = False

    def login(self) -> None:
        login_via_session = False
        login_via_pw = False

        # Check if session is valid
        if self.session:
            try:
                self.cl.set_settings(self.session)
                self.cl.login(self.username, self.password)

                try:
                    self.cl.get_timeline_feed()
                except LoginRequired:
                    logging.error(
                        "Session is invalid, need to login via username and password"
                    )

                    old_session = self.cl.get_settings()

                    # use the same device uuids across logins
                    self.cl.set_settings({})
                    self.cl.set_uuids(old_session["uuids"])

                    self.cl.login(self.username, self.password)
                login_via_session = True

            except Exception as e:
                logging.error("Couldn't login user using session information: %s" % e)

        # If session is not valid login via username and password
        if not login_via_session:
            try:
                print(
                    "Attempting to login via username and password. username: %s"
                    % self.username
                )
                if self.cl.login(self.username, self.password):
                    login_via_pw = True
            except Exception as e:
                logging.error("Couldn't login user using username and password: %s" % e)

        # Raise exception if session and username and password are not valid
        if not login_via_pw and not login_via_session:
            raise Exception("Couldn't login user with either password or session")

    def like_follow_comment_by_hashtag(
        self,
        hashtags: list[str],
        comments: list[str],
        comment: bool = False,
        follow: bool = False,
    ) -> None:
        count = 1
        total = len(hashtags) * 20

        for hashtag in hashtags:
            medias = self.cl.hashtag_medias_recent(hashtag, 20)
            try:
                for i, media in enumerate(medias, 1):
                    self.cl.media_like(media.id)
                    progress_bar(
                        count,
                        total,
                        prefix=f"{count}/{total}",
                        suffix=f"Processing hashtag: {hashtag:<20}",
                    )
                    self.cl.delay_range = [6, 11]

                    if follow:
                        if i % 5 == 0:
                            self.cl.user_follow(media.user.pk)
                            print(f"Followed user: {media.user.username}")
                            self.cl.delay_range = [4, 10]

                    if comment:
                        if i % 4 == 0:
                            random_comment = random.choice(comments)
                            self.cl.media_comment(media.id, random_comment)
                            print(f"Commented on post number {i} of hashtag {hashtag}")
                            self.cl.delay_range = [2, 6]

                    count += 1

            except MediaUnavailable:
                print("Media Unavailable!!!")

            except KeyboardInterrupt:
                pass

    def unfollow_followers(self, amount: int) -> None:
        count = 0
        followers = self.cl.user_following(self.cl.user_id)

        for user_id in followers.keys():
            if count < amount:
                self.cl.user_unfollow(user_id)
                print(f"Unfollowed users: {count}")
                self.cl.delay_range = [1, 3]
                count += 1

    def __exit__(self, type, value, traceback) -> None:
        print(colorama.Fore.RESET)
        print("Ending...")

    def __enter__(self) -> Client:
        print("Starting...")
        self.login()
        return self
