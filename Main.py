import os
import praw
import random
import re
import sys
import time
from pprint import pprint
# print((os.environ.get("praw_CLIENT_ID"),
# os.environ.get("praw_CLIENT_SECRET"),
# os.environ.get("praw_USER_AGENT"),
# os.environ.get("praw_USERNAME"),
# os.environ.get("praw_PASSWORD")))


def random_quote():
    subFile = random.choice(["subs/" +
                             a for a in os.listdir("subs/")] +
                            ["subs/done/" +
                             a for a in os.listdir("subs/done/")] *
                            5)
    with open(subFile, 'r') as subFile_:
        quotes = subFile_.read()
    quote = random.choice(quotes.split('\n\n'))
    quoteTime = re.match(r"(\d\d):(\d\d):(\d\d)", quote)
    hh, mm, ss = quoteTime.groups()
    if ss == '00':
        mm = str(int(mm) - 1)
        ss = '59'
    else:
        ss = str(int(ss) - 1)

    youtubeLink = f"https://youtu.be/{subFile[-15:-4]}/?t={hh}h{mm}m{ss}s"
    quoteText = re.sub("^.*\n", '', quote)

    msg = '>' + quoteText.replace('\n', '  \n>') + \
        f'\n\n&nbsp;\n\n[Source](<{youtubeLink}>"Did you expect the spanish inquisition")  \n'
    print(msg)
    return msg


def main():
    reddit = praw.Reddit(client_id=os.environ.get("praw_CLIENT_ID"),
                         client_secret=os.environ.get("praw_CLIENT_SECRET"),
                         user_agent=os.environ.get("praw_USER_AGENT"),
                         username=os.environ.get("praw_USERNAME"),
                         password=os.environ.get("praw_PASSWORD"))

    SaimanSays = reddit.subreddit("testingground4bots")
    for comment in SaimanSays.stream.comments():
        if re.search(r"TriggerWord", comment.body, re.I):
            comment.reply(random_quote())

random_quote()
