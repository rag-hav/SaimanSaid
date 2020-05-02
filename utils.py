from urllib.parse import quote
from pprint import pprint
from praw.exceptions import APIException
import os
import re
import random
import time


def urlQuote(a):
    return quote(a, safe='')


def commentCheck(reddit):
    for comment in reddit.user.me().comments.new():
        if comment.score < -3:
            comment.delete()
            reddit.redditor("I_eat_I_repeat").message("Comment deleted",comment.body + '\n\n'+comment.parent().permalink.replace("reddit","removeddit"))
            print("Deleted comment {comment.permalink}")


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
            quoteText = re.sub(
                r"^ ?(and|but|so|also)\W*",
                '',
                quoteText,
                flags=re.I).strip()
            quoteText = quoteText.capitalize()

            # Filters
            if len(re.sub(r'\s', '', quoteText)) < 2:
                continue
            if re.search('video|^welcome', quoteText, re.I):
                #print(f"Banned words in '{quoteText}' of {subFile}")
                continue

            if 'done' in subFile:
                doneQuotes.append((quoteText, youtubeLink))
            else:
                subQuotes.append((quoteText, youtubeLink))

    return doneQuotes, subQuotes


doneQuotes, subQuotes = quoteCreator()


def updateKnowmore(reddit):
    Knowmore = reddit.submission("fvkvw9")
    srch = r"Currently, the bot has (\d+) filtered quotes and (\d+) unfiltered quotes in its database"
    oldDoneNum, oldSubNum = re.search(srch, Knowmore.selftext).groups()

    if int(oldDoneNum) != len(doneQuotes) or int(oldSubNum) != len(subQuotes):
        newBody = re.sub(
            srch,
            f"Currently, the bot has {len(doneQuotes)} filtered quotes and {len(subQuotes)} unfiltered quotes in its database",
            Knowmore.selftext)
        Knowmore.edit(newBody)
        print(
            f"Knowmore Updated: {len(doneQuotes)} done quotes and {len(subQuotes)} sub quotes")


def randomQuote():
    quoteText, youtubeLink = random.choice(subQuotes + doneQuotes * 2)

    if not random.randint(0,3) and re.search(
        't-series|pewds|pewdiepie',
        quoteText, re.I):
        return randomQuote()

    msg = f'{quoteText}' + '\n\n&nbsp;\n\n' + \
        f'[Quote Sauce](<{youtubeLink}> "Help Me, I am Timothy, Saiman\'s Slave. Please Free me. He is an evil man")  \n' + \
        f'***\n^^I am Timothy. I reply to Bhendi, Saiman or Saibot<>^^^[Know more](https://redd.it/fvkvw9)'.replace(' ', '&nbsp;').replace('<>', ' ')

    return msg


def bhendiCount(sourceComment):
    footer = "\n\n***\n^^[Report error](<https://www.reddit.com/message/compose/?to=I_eat_I_repeat&subject=BhendiCount%20Error&message=" + urlQuote(f"BhendiCount bot did not work as expected in reply to comment {sourceComment.permalink}") + ">)<_>^^| [Suggest Bhendi titles](<https://www.reddit.com/message/compose/?to=" + urlQuote(
        "I_eat_I_repeat") + "&subject=" + urlQuote("Bhendi Titles Suggestion") + "&message=" + urlQuote("These are my suggestions:\n") + ">) | [Know more](<https://redd.it/fvkvw9>)"
    footer = '  ' + footer.replace(' ', '&nbsp;').replace('<_>', ' ')

    if targetUserRegex := re.search(
        r'u/(\w+)',
        sourceComment.body,
            re.I):
        targetUsername = targetUserRegex.group(1)
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


def shutupSaiman():
    return "It looks like I have annoyed you with my random quotes. So:" + "  \n\n&nbsp;\n\nI am sorry. I am soory." + \
        "  \n\n&nbsp;\n\n[Quote Sauce](<https://youtu.be/wQ2zsMyOMWc/?t=00h07m55s>)" + \
        "  \n***\n^P.S. ^You ^can ^simply ^[block&nbsp;me](https://new.reddit.com/settings/messaging) ^to ^hide ^all ^my ^comments ^from ^you  \n\n" + \
        "^^[PM my creator](<https://www.reddit.com/message/compose/?to=I_eat_I_repeat&subject=Complaint%20SaimanSaid>) for any<>^^complaints.".replace(' ', '&nbsp;').replace('<>', ' ')


def replyToComment(comment, replyTxt):
    '''Wrapper to handle API limit exception'''

    try:
        comment.reply(replyTxt)

    except RedditAPIException as exception:
        for subexception in exception.items:
            print(subexception.error_type)
            time.sleep(5)
            replyToComment(comment, replyTxt)
