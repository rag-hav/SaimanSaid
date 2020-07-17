from prawcore.exceptions import RequestException, ServerError
import re
from Reddit import reddit
import time
from utils import (
    SignalHandler,
    blockRedditor,
    cakedayCheck,
    commentCheck,
    downloadNewSubtitles,
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


signalHandler = SignalHandler()


def main():

    downloadNewSubtitles()
    updateKnowmore()

    commentCheckTime = 0
    inboxCheckTime = 0
    me = reddit.user.me()

    for comment in reddit.subreddit("SaimanSays").stream.comments():

        signalHandler.loopStart()

        if time.time() > inboxCheckTime:
            inboxCheck()
            inboxCheckTime = time.time() + 3600 * 12

        if time.time() > commentCheckTime:
            commentCheck()
            commentCheckTime = time.time() + 1800

        if comment.saved \
                or comment.author == me \
                or re.search(r"\bre+post\b", comment.body, re.I):
            continue

        if re.search(r"\b(chup|shut ?(the)? ?(fuck)? ?up|stop)\b",
                     comment.body, re.I) \
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

        elif re.search(r"!(ignore|block)", comment.body, re.I):
            if comment.parent.author == me:
                blockRedditor(comment.author)

        signalHandler.loopEnd()


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
            print("Program ended. It aint supposed to")
            break
