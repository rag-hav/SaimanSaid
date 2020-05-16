from prawcore.exceptions import RequestException, ServerError
import os
import praw
import re
import signal
import sys
import time
from utils import (
    SignalHandler,
    cakedayCheck,
    commentCheck,
    inboxCheck,
    replyToComment,
    updateKnowmore,
)
from quotes import (
    bhendiCount,
    happyCakeday,
    randomQuote,
    shutupSaiman,
)


def main():

    signalHandler = SignalHandler()
    updateKnowmore(reddit)

    commentCheckTime = 0
    inboxCheckTime = 0
    me = reddit.user.me()

    for comment in reddit.subreddit("SaimanSays").stream.comments():

        signalHandler.loopStart()

        if time.time() > inboxCheckTime:
            inboxCheck(reddit)
            inboxCheckTime = time.time() + 3600 * 12

        if time.time() > commentCheckTime:
            commentCheck(reddit)
            commentCheckTime = time.time() + 1800

        if comment.saved \
                or comment.author == me \
                or re.search(r"\bre+post\b", comment.body, re.I):
            continue

        if re.search(r"chup|shut ?up|block|stop", comment.body, re.I) \
                and comment.parent().author == me:
            print(f"Replying to '{comment.permalink}' with shutupSaiman")
            replyToComment(comment, shutupSaiman())

            reddit.redditor("I_eat_I_repeat").message(
                "Sent a Shutup Saiman", comment.permalink)
            inboxCheckTime = time.time() + 3600

        elif cakedayCheck(comment):
            print(f"Replying to '{comment.permalink}' with Cakeday")
            replyToComment(comment, happyCakeday())

        elif re.search(
            r"\bBh[ei]+ndi\b|\bSai(man)?-?(Said| ?bot)\b|\bTimothy\b",
                comment.body, re.I):
            print(f"Replying to '{comment.permalink}' with random quote")
            replyToComment(comment, randomQuote())

        elif re.search(r"bhendicount", comment.body, re.I):
            print(f"Replying to '{comment.permalink}' with bhendi count")
            replyToComment(comment, bhendiCount(comment))

        signalHandler.loopEnd()



reddit = praw.Reddit(
    client_id=os.getenv("SaimanSaid_CLIENT_ID"),
    client_secret=os.getenv("SaimanSaid_CLIENT_SECRET"),
    user_agent=os.getenv("SaimanSaid_USER_AGENT"),
    username=os.getenv("SaimanSaid_USERNAME"),
    password=os.getenv("SaimanSaid_PASSWORD"))


if __name__ == "__main__":
    print("Starting the bot")
    while(True):
        try:
            main()
        # Network Issues
        except (RequestException, ServerError) as e:
            print(e)
            time.sleep(60)
        else:
            raise "Program Finished Abnormally"
            break
