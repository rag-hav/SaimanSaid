import os
import praw
from prawcore.exceptions import *
import random
import re
import sys
import time
from urllib.parse import quote


def urlQuote(a):
    return quote(a, safe='')


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

    videoId = os.path.basename(subFile)
    youtubeLink = f"https://youtu.be/{videoId}/?t={hh}h{mm}m{ss}s"

    # Removes the first line
    quoteText = re.sub("^.*\n", '', quote)

    msg = f'{quoteText}' + '\n\n&nbsp;\n\n' + \
        f'[Quote Sauce](<{youtubeLink}> "Help Me, I am Timothy Saiman\'s Slave. Please Free me. He is an evil man")  \n' + \
        f'***\n^^I am a bot,<>^^^that replies to "Bhendi" or "Saiman" with a quote from Saiman [Know more](https://redd.it/fvkvw9)'.replace(' ', '&nbsp;').replace('<>', ' ')

    return msg


def bhendiCount(sourceComment):
    footer = "\n\n***\n^^[Report error](<https://www.reddit.com/message/compose/?to=I_eat_I_repeat&subject=BhendiCount%20Error&message=" + urlQuote(f"BhendiCount bot did not work as expected in reply to comment {sourceComment.permalink}") + ">)<_>^^| [Suggest Bhendi titles](<https://www.reddit.com/message/compose/?to=" + urlQuote(
        "I_eat_I_repeat") + "&subject=" + urlQuote("Bhendi Titles Suggestion") + "&message=" + urlQuote("These are my suggestions:\n") + ">) | [Know more](<https://redd.it/fvkvw9>)"
    footer = '  ' + footer.replace(' ', '&nbsp;').replace('<_>', ' ')

    targetUserRegex = re.search(r'u/(?P<user>\w+)', sourceComment.body, re.I)
    if targetUserRegex:
        targetUsername = targetUserRegex.group('user')
        targetRedditor = reddit.redditor(targetUsername)
        try:
            targetRedditor.id
        except NotFound:
            return f"Sorry comrade, it looks like is no u/{targetUsername}" + footer

        bcount = 0
        for comment in targetRedditor.comments.new(limit=None):
            if re.search(r'\bbhendi\b', comment.body, re.I):
                bcount += 1
        if bcount > 50:
            bhendiRank = "  \nHe is a Bhendi Bahgwan"
        elif bcount > 12:
            bhendiRank = "  \nHe is a Bhendi Bhashi"
        elif bcount > 5:
            bhendiRank = "  \nHe is a Bhendi Master"
        elif bcount > 0:
            bhendiRank = "  \nHe is a Bhendi Balak"
        else:
            bhendiRank = '  '
        return f'Thankyou for your request comrade  \n\n&nbsp;\n  \nu/{targetUsername} has said "Bhendi" a total of {bcount} times!' + bhendiRank + footer
    else:
        return f'Sorry comrade. I did not find any username in your request. You can call me properly by:  \n>BhendiCount! u/{sourceComment.author.name}' + footer


def replyToComment(comment, content):
    try:
        if content == 'randomQuote':
            comment.reply(randomQuote())

        elif content == 'bhendiCount':
            comment.reply(bhendiCount(comment))

        else:
            raise Exception()
    except praw.exceptions.APIException as e:
        if e.field == 'ratelimit':
            sleepTime, time_type = re.search(
                r'(\d+) ([ms])', e.message).groups()
            sleepTime = int(sleepTime)
            if time_type == 'm':
                sleepTime = sleepTime * 60 + 10

            t_print("RateLimit sleeping for", sleepTime)
            time.sleep(sleepTime + 5)
            replyToComment(comment)
        else:
            raise e


def main():
    global reddit
    reddit = praw.Reddit(
        client_id=os.environ.get("SaimanSaid_CLIENT_ID"),
        client_secret=os.environ.get("SaimanSaid_CLIENT_SECRET"),
        user_agent=os.environ.get("SaimanSaid_USER_AGENT"),
        username=os.environ.get("SaimanSaid_USERNAME"),
        password=os.environ.get("SaimanSaid_PASSWORD"))

    SaimanSays = reddit.subreddit("testingground4bots")
    me = reddit.user.me()

    for comment in SaimanSays.stream.comments():
        if comment.saved or comment.author == me:
            continue
        if re.search(
            r"\bSaiman\b|\bBhendi\b|\bSaimanSaid\b",
            comment.body,
                re.I):
            t_print(f"Replying to '{comment.id}' with random quote")
            replyToComment(comment, 'randomQuote')
            t_print("\tSuccess")
            comment.save()

        if re.search(r"\!bhendicount|bhendicount\!", comment.body, re.I):
            t_print(f"Replying to '{comment.id}' with bhendi count")
            replyToComment(comment, 'bhendiCount')
            t_print("\tSuccess")
            comment.save()


def infinite():
    '''Ensures that the bot can survive server down'''
    try:
        main()
    except RequestException as e:
        t_print(e)
        time.sleep(300)
        infinite()


def t_print(a):
    # print current time in string format always in IST
    print(time.ctime(time.mktime(time.gmtime()) + 19800) + ': ' + a)


t_print("Starting the bot")
reddit = None
infinite()
