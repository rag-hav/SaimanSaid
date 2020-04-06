import os
import praw
from prawcore.exceptions import *
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


def randomQuote():
    subFile = random.choice(["subs/" +
                             a for a in os.listdir("subs/")] +
                            ["subs/done/" +
                             a for a in os.listdir("subs/done/")] *
                            5)
    with open(subFile, 'r') as subFile_:
        quotes = subFile_.read()
    quote = random.choice(quotes.split('\n\n'))
    quoteTime = re.match(r"(\d\d):(\d\d):(\d\d)", quote)
    try:
        hh, mm, ss = quoteTime.groups()
    except AttributeError:
        return randomQuote()

    youtubeLink = f"https://youtu.be/{subFile}/?t={hh}h{mm}m{ss}s"

    quoteText = re.sub("^.*\n", '', quote)

    msg = f'{quoteText}' + '\n\n&nbsp;\n\n' + \
        f'[Quote Sauce](<{youtubeLink}> "Did you expect the spanish inquisition")  \n' + \
        '***\n^^I ^^am ^^a ^^bot, ^^contact ^^u/I_eat_I_repeat ^^^to ^^^report ^^^any ^^^(error.&#x2005;[About](/redd.it/fvkvw9)) '

    return msg


def getReplyedIds():
    if not os.path.isfile('replyedIds'):
        print('No History file present')
        return []
    with open('replyedIds', 'r') as fileObj:
        ids_text = fileObj.read()
    return(ids_text.split())


def writeReplyedId(Id):
    with open('replyedIds', 'a') as fileObj:
        fileObj.write(Id + '\n')


def replyToComment(comment):
    try:
        comment.reply(randomQuote())
    except praw.exceptions.APIException as e:
        if e.field == 'ratelimit':
            sleepTime, time_type = re.search(
                r'(\d+) ([ms])', e.message).groups()
            sleepTime = int(sleepTime)
            if time_type == 'm':
                sleepTime = sleepTime * 60 + 10

            print("RateLimit sleeping for", sleepTime)
            time.sleep(sleepTime + 5)
            replyToComment(comment)
        else:
            raise e


def main():
    reddit = praw.Reddit(client_id=os.environ.get("praw_CLIENT_ID"),
                         client_secret=os.environ.get("praw_CLIENT_SECRET"),
                         user_agent=os.environ.get("praw_USER_AGENT"),
                         username=os.environ.get("praw_USERNAME"),
                         password=os.environ.get("praw_PASSWORD"))

    SaimanSays = reddit.subreddit("SaimanSays")
    replyedIds = getReplyedIds()
    for comment in SaimanSays.stream.comments():
        if comment.id not in replyedIds and re.search(
                r"Bhendi", comment.body, re.I):

            print(f"Replying to '{comment.id}'")
            replyToComment(comment)
            print("Success")
            writeReplyedId(comment.id)

def infinite():
    try:
        main()
    except RequestException as e:
        print(e)
        time.sleep(300)
        infinite()

infinite()
