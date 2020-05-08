from praw.exceptions import RedditAPIException
import re
import os
import time
from datetime import datetime

cakedayRedditors = []


def cakedayCheck(comment):
    if comment.author in cakedayRedditors:
        # Already Wished
        return False

    createdUtc = comment.author.created_utc
    currentUtc = datetime.utcnow().timestamp()
    while(createdUtc < currentUtc):
        if currentUtc - createdUtc < 3600 * 24:
            cakedayRedditors.append(comment.author)
            return True
        createdUtc += 3600 * 24 * 365
    return False


def myCommentCheck(reddit):
    for comment in reddit.user.me().comments.new():

        # Get Already wished redditors btw runs
        if re.search(r"^Happy cakeday", comment.body) and \
                comment.author not in cakedayRedditors:

            cakedayRedditors.append(comment.author)

        if comment.score < -3:
            comment.delete()
            reddit.redditor("I_eat_I_repeat").message(
                "Comment deleted",
                comment.body +
                '\n\n' +
                comment.parent().permalink.replace(
                    "reddit",
                    "removeddit"))
            print("Deleted comment {comment.permalink}")


def updateKnowmore(reddit):
    Knowmore = reddit.submission("fvkvw9")
    srch = r"Currently, the bot has (\d+) filtered quotes and (\d+) "\
        "unfiltered quotes in its database"
    oldDoneNum, oldSubNum = re.search(srch, Knowmore.selftext).groups()

    if int(oldDoneNum) != len(doneQuotes) or int(oldSubNum) != len(subQuotes):
        newBody = re.sub(
            srch,
            f"Currently, the bot has {len(doneQuotes)} filtered quotes "
            "and {len(subQuotes)} unfiltered quotes in its database",
            Knowmore.selftext)
        Knowmore.edit(newBody)
        print(f"Knowmore Updated: {len(doneQuotes)} done quotes "
              f"and {len(subQuotes)} sub quotes")


def replyToComment(comment, replyTxt):
    '''Wrapper to handle API limit exception'''

    try:
        comment.reply(replyTxt)

    except RedditAPIException as exception:
        for subexception in exception.items:
            print(subexception.error_type)
            time.sleep(5)
            replyToComment(comment, replyTxt)


def quoteCreator():
    doneQuotes, subQuotes = [], []
    subFiles = [
        "subs/" + a for a in os.listdir("subs/")] + [
        "subs/done/" + a for a in os.listdir("subs/done/")]

    for subFile in subFiles:
        if subFile == 'subs/done':
            continue
        quotes = open(subFile, 'r').read().split('\n\n')
        for quote in quotes:
            if quoteTime := re.match(r"(\d\d):(\d\d):(\d\d)", quote):
                hh, mm, ss = quoteTime.groups()
            else:

                print(f"Time stamp not found in {quote=} \nof {subFile=}")
                continue

            videoId = os.path.basename(subFile)[3:]
            youtubeLink = f"https://youtu.be/{videoId}/?t={hh}h{mm}m{ss}s"

            # Removes the time stamp
            quoteText = re.sub("^.*\n", '', quote)
            # Removes anything inside [] or ()
            quoteText = re.sub(r"[\[\(].*[\]\)]", '', quoteText)
            quoteText = re.sub("  ", ' ', quoteText)

            # sometimes two quotes are not seperated
            if re.search(r'(\d\d):(\d\d):(\d\d)', quoteText):
                print(f"Invalid format of {quote=} in {subFile=}")
                continue

            # Formatting
            quoteText = quoteText.strip()
            quoteText = re.sub(
                r"^(and|but|so|also)\W*|" +
                r"([^a-zA-Z\?\.\!]*and|but|so|also)\W*$",
                '',
                quoteText,
                flags=re.I).strip()
            quoteText = quoteText.capitalize()

            # Filters
            if len(re.sub(r'\s', '', quoteText)) < 2:
                continue
            if re.search('video|^welcome', quoteText, re.I):
                # print(f"Banned words in '{quoteText}' of {subFile}")
                continue

            if 'done' in subFile:
                doneQuotes.append((quoteText, youtubeLink))
            else:
                subQuotes.append((quoteText, youtubeLink))

    return doneQuotes, subQuotes


doneQuotes, subQuotes = quoteCreator()
