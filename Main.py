from prawcore.exceptions import RequestException, ServerError
import os
import praw
import re
import time
from utils import (
    cakedayCheck,
    commentCheck,
    inboxCheck,
    replyToComment,
    updateKnowmore,
)
from quotes import (
    bhendiCount,
    happyCakeday,
    matMaan,
    randomQuote,
    shutupSaiman,
)


def main():

    commentCheckTime = time.time()
    inboxCheckTime =  time.time()
    me = reddit.user.me()

    for comment in reddit.subreddit("SaimanSays").stream.comments():

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
                    "Shutup Saiman", comment.permalink)
            inboxCheckTime = time.time() + 3600
            comment.save()

        elif re.match(r"(lol )?(xd )?m[ae]in? k(ai|e)se maa?n lu\?*",
                      comment.body, re.I):
            comment.refresh()
            for reply in comment.replies:
                if re.search(r"mat+ ma+n+", reply.body, re.I):
                    break
            else:
                print(f"Replying to '{comment.permalink}' with mat mann")
                replyToComment(comment, matMaan())
                comment.save()

        elif cakedayCheck(comment):
            print(f"Replying to '{comment.permalink}' with Cakeday")
            replyToComment(comment, happyCakeday())
            comment.save()

        elif re.search(
            r"\bBhe+ndi\b|\bSaiman-?Said(bot)?\b|\bSai ?-?bot\b",
                comment.body, re.I):
            print(f"Replying to '{comment.permalink}' with random quote")
            replyToComment(comment, randomQuote())
            comment.save()

        elif re.search(r"bhendicount", comment.body, re.I):
            print(f"Replying to '{comment.permalink}' with bhendi count")
            replyToComment(comment, bhendiCount(comment))
            comment.save()


reddit = praw.Reddit(
    client_id=os.environ.get("SaimanSaid_CLIENT_ID"),
    client_secret=os.environ.get("SaimanSaid_CLIENT_SECRET"),
    user_agent=os.environ.get("SaimanSaid_USER_AGENT"),
    username=os.environ.get("SaimanSaid_USERNAME"),
    password=os.environ.get("SaimanSaid_PASSWORD"))

if __name__ == "__main__":
    print("Starting the bot")
    updateKnowmore(reddit)
    while(True):
        try:
            main()
        # Network Issues
        except (RequestException, ServerError) as e:
            print(e)
            time.sleep(60)
        except KeyboardInterrupt:
            print("Killing all operations; Over and Out")
            break
        else:
            raise "Program Finished, It really shouldn't"
            break
