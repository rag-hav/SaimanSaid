import re
import os
import random
from urllib.parse import quote

def urlQuote(a): return quote(a, safe='')


def happyCakeday():
    return "Happy cakeday! Here is a quote just for you  \n\n&nbsp;\n\n" +\
        randomQuote()


def matMaan():
    return "mat maan  \n\n***\n" +\
           "^^(I am dddisco dancerr tu tu)".replace(" ", "&nbsp;") +\
           " ^^tudu"


def randomQuote():
    quoteText, youtubeLink = random.choice(subQuotes + doneQuotes * 2)

    if not random.randint(0, 3) and re.search(
        't-series|pewds|pewdiepie',
            quoteText, re.I):
        return randomQuote()

    msg = f'{quoteText}' + '\n\n&nbsp;\n\n' + \
        f'[Quote Sauce](<{youtubeLink}> "Help Me, I am Timothy, Saiman\'s ' \
        'Slave. Please Free me. He is an evil man")  \n' + \
        f'***\n^^I am Timothy. I reply to Bhendi, Saiman or Saibot'.replace(
            ' ', '&nbsp;') + \
        ' ^^^[Know&nbsp;more](https://redd.it/fvkvw9)'

    return msg


def bhendiCount(sourceComment):
    footer = "  \n\n***\n^^[Report error](<https://www.reddit.com/message/" +\
        "compose/?to=I_eat_I_repeat&subject=BhendiCount%20Error&message=" +\
        urlQuote("BhendiCount bot did not work as expected in reply to " +
                 f"comment {sourceComment.permalink}") + \
        ">)<_>^^| [Suggest Bhendi titles](<https://www.reddit.com/"\
        "message/compose/?to=" +\
        urlQuote("I_eat_I_repeat") + "&subject=" + \
        urlQuote("Bhendi Titles Suggestion") + "&message=" +\
        urlQuote("These are my suggestions:\n") + \
        ">) | [Know more](<https://redd.it/fvkvw9>)"
    footer = '  ' + footer.replace(' ', '&nbsp;').replace('<_>', ' ')

    if targetUserRegex := re.search(r'u/(\w+)', sourceComment.body, re.I):
        targetUsername = targetUserRegex.group(1)
        targetRedditor = reddit.redditor(targetUsername)
    else:
        targetRedditor = sourceComment.parent().author

    try:
        targetRedditor.id
    except NotFound:
        return f"I didn't find any u/{targetUsername}" + footer

    bcount = 0
    for comment in targetRedditor.comments.new(limit=None):
        if re.search(r'\bbhendi\b', comment.body, re.I):
            bcount += 1

    bhendiRank = "  \nHe has been awarded the title of "
    if bcount > 50:
        bhendiRank += "Bhendi Bahgwan"
    elif bcount > 12:
        bhendiRank += "Bhendi Bhashi"
    elif bcount > 5:
        bhendiRank += "Bhendi Master"
    elif bcount > 0:
        bhendiRank += "Bhendi Balak"
    else:
        bhendiRank = ''

    return f'Thankyou for your request comrade  \n\n&nbsp;\n  '\
        '\nu/{targetUsername} has said "Bhendi" a total of '\
        '{bcount} times!' + bhendiRank + footer


def shutupSaiman():
    return "It looks like I have annoyed you with my random quotes. So:" +\
        "  \n\n&nbsp;\n\nI am sorry. I am soory." + \
        "  \n\n&nbsp;\n\n[Quote Sauce]"\
        "(<https://youtu.be/wQ2zsMyOMWc/?t=00h07m55s>)" + \
        "  \n***\n^P.S. ^You ^can ^simply ^[block&nbsp;me]"\
        "(https://new.reddit.com/settings/messaging) ^to ^hide ^all "\
        "^my ^comments ^from ^you  \n\n" + \
        "^^[PM&nbsp;my&nbsp;creator](<https://www.reddit.com/message/compose/"\
        "?to=I_eat_I_repeat&subject=Complaint%20SaimanSaid>)&nbsp;"\
        "for&nbsp;any ^^complaints."


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

sizeDoneQuotes, sizeSubQuotes = len(doneQuotes), len(subQuotes)
