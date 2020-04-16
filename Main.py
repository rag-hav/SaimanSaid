import os
import praw
from prawcore.exceptions import RequestException, ServerError
import re
import time

def main():

    SaimanSays = reddit.subreddit("SaimanSays")
    me = reddit.user.me()

    for comment in SaimanSays.stream.comments():
        if comment.saved or comment.author == me:
            continue
        if re.search(r"\bre+post\b", comment.body, re.I):
            continue

        if re.match(
            r"chup|shut ?up|block",
            comment.body,
                re.I) and comment.parent().author == me:
            print(f"Replying to '{comment.id}' with shutupSaiman")
            replyToComment(comment, shutupSaiman())
            print("\tSuccess")
            comment.save()
            continue

        if re.search(
            r"\bSaiman\b|\bBhe+ndi\b|\bSaiman-?Said\b",
            comment.body,
                re.I):
            print(f"Replying to '{comment.id}' with random quote")
            replyToComment(comment, randomQuote())
            print("\tSuccess")
            comment.save()
            continue

        if re.search(r"bhendicount", comment.body, re.I):
            print(f"Replying to '{comment.id}' with bhendi count")
            replyToComment(comment, bhendiCount(comment))
            print("\tSuccess")
            comment.save()
            continue


reddit = praw.Reddit(
    client_id=os.environ.get("SaimanSaid_CLIENT_ID"),
    client_secret=os.environ.get("SaimanSaid_CLIENT_SECRET"),
    user_agent=os.environ.get("SaimanSaid_USER_AGENT"),
    username=os.environ.get("SaimanSaid_USERNAME"),
    password=os.environ.get("SaimanSaid_PASSWORD"))

if __name__ == "__main__":
    print("Starting the bot")
    while(True):
        try:
            main()
        #Network Issues
        except (RequestException, ServerError) as e:
            print(e)
            time.sleep(60)
        except KeyboardInterrupt:
            print("Killing all operations; Over and Out")
            break

