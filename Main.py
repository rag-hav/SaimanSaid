from prawcore.exceptions import RequestException, ServerError
import os
import praw
import re
import time
from utils import (
    cakedayCheck,
    myCommentCheck,
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

    lastCommentCheckTime = 0
    SaimanSays = reddit.subreddit("SaimanSays")
    me = reddit.user.me()

    for comment in SaimanSays.stream.comments():

        if time.time() - lastCommentCheckTime > 1800:
            myCommentCheck(reddit)
            lastCommentCheckTime = time.time()

        if comment.saved \
                or comment.author == me \
                or re.search(r"\bre+post\b", comment.body, re.I):
            continue

        if re.search(r"chup|shut ?up|block", comment.body,
                     re.I) and comment.parent().author == me:
            print(f"Replying to '{comment.id}' with shutupSaiman")
            replyToComment(comment, shutupSaiman())
            print("\tSuccess")
            comment.save()

        elif re.match(r"(lol )?(xd )?m[ae]in? k(ai|e)se maa?n lu\?*",
                      comment.body, re.I):
            comment.refresh()
            for reply in comment.replies:
                if re.search(r"mat+ ma+n+", reply.body, re.I):
                    break
            else:
                print(f"Replying to '{comment.id}' with mat mann")
                replyToComment(comment, matMaan())
                print("\tSuccess")
                comment.save()

        elif cakedayCheck(comment):
            print(f"Replying to '{comment.id}' with Cakeday")
            replyToComment(comment, happyCakeday())
            print("\tSuccess")
            comment.save()

        elif re.search(
            r"\bSaiman\b|\bBhe+ndi\b|\bSaiman-?Said\b|\bSai ?-?bot\b",
                comment.body, re.I):
            print(f"Replying to '{comment.id}' with random quote")
            replyToComment(comment, randomQuote())
            print("\tSuccess")
            comment.save()

        elif re.search(r"bhendicount", comment.body, re.I):
            print(f"Replying to '{comment.id}' with bhendi count")
            replyToComment(comment, bhendiCount(comment))
            print("\tSuccess")
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
