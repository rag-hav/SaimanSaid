import random
import re


def urlQuote(a):
    from urllib.parse import quote
    return quote(a, safe='')


def createMsgLink(to=None, subject=None, message=None):
    from requests import Request
    return Request(url="https://www.reddit.com/message/compose/", params={
        "to":to,
        "subject":subject,
        "message":message,}).prepare().url


def happyCakeday():
    return "Happy cakeday! Here have a quote!  \n\n&nbsp;\n\n" +\
        randomQuote() + '\u200e'


whoAmI = None
def getWhoAmI():
    if whoAmI is None:
        from Reddit import reddit
        wikiPg = reddit.subreddit("SaimanSaid").wiki["whoami"].content_md
        return [a.strip() for a in wikiPg.splitlines() if a]
    return whoAmI


def randomQuote(quote=None):

    if quote is None:
        allQuotes = getAllQuotes()
        quote = random.choices(allQuotes, [a.weight for a in allQuotes])[0]


    msg = f'{quote.quoteText}' + '\n\n&nbsp;\n\n' + \
        f'[Quote Sauce](<{quote.youtubeLink}> "Help Me, I am Timothy, Saiman\'s ' \
        'Slave. Please Free me. He is an evil man")  \n***\n' + createFooter()

    return msg


def createFooter():
    me_ = random.choice(getWhoAmI()).strip()
    if me_.startswith('$'):
        footer = me_
    else:
        footer = "I am " + me_
    if not me_.endswith('$'):
        footer = footer + " I reply to Bhendi, Timothy or Saibot" 
    footer = '^^' + footer.replace(' ',' ^^')
    if not me_.endswith('$$'):
        footer = footer + ' ^^^[Know&nbsp;more](https://redd.it/fvkvw9)'
    return footer.replace('$','')


def bhendiCount(sourceComment):
    footer = "  \n\n***\n^^[Report error](<" + createMsgLink(
                "I_eat_I_repeat",
                "Bhendi Count",
                "BhendiCount bot did not work as expected in reply to " + \
                     f"comment {sourceComment.permalink}") + \
        ">)<_>^^| [Suggest Bhendi titles](<" + createMsgLink(
                "I_eat_I_repeat",
                "Bhendi Titles Suggestion"
                "These are my suggestions:\n") +\
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
        "(<https://youtu.be/wQ2zsMyOMWc/?t=00h07m55s>)  \n***\n" +\
        "^P.S. You can simply [block&nbsp;me](https://redd.it/gh42zl) "\
        "to hide all my comments from you or to stop getting " \
        "replies from me.".replace(' ',' ^') +\
        "\n\n^[PM&nbsp;my&nbsp;creator](<" +\
        createMsgLink("I_eat_I_repeat", "Complaint SaimanSaid") +\
        ">) for any complaints.".replace(' ',' ^')


allQuotes =  []
def getAllQuotes():
    if not allQuotes:
        quoteCreator()
    return allQuotes


class Quote():
    def __init__(self, quoteText, youtubeLink, weight, handFiltered):
        self.quoteText = quoteText
        self.youtubeLink = youtubeLink
        self.weight = weight
        self.handFiltered = handFiltered


def quoteCreator():
    import os
    from math import sqrt
    from utils import getAge

    subFiles = [
        ("subs/", a) for a in os.listdir("subs/")] + [
        ("subs/done/", a) for a in os.listdir("subs/done/")]
    subFiles.remove(('subs/', 'done'))

    oldestSubAge = getAge(min(int(a[:8]) for fldr, a in subFiles)) * 1.1

    for fldr, subFile in subFiles:

        with open(fldr + subFile, 'r') as f:
            quotes = f.read().split('\n\n')

        videoId = subFile[8:]
        subAge = getAge(subFile[:8])

        for quote in quotes:
            if quoteTime := re.match(r"(\d\d):(\d\d):(\d\d)", quote):
                hh, mm, ss = quoteTime.groups()
            else:
                print(f"Time stamp not found in {quote=} \nof {subFile=}")
                continue
            youtubeLink = f"https://youtu.be/{videoId}/?t={hh}h{mm}m{ss}s"

            # Removes the time stamp
            quoteText = re.sub("^.*\n", '', quote)
            # Removes anything inside [] or ()
            quoteText = re.sub(r"\[.*\]", '', quoteText)
            quoteText = re.sub(r"\(.*\)", '', quoteText)
            quoteText = re.sub("  ", ' ', quoteText)
            # Remove starting -
            quoteText = re.sub(r"^\s*-\s*", '', quoteText)

            # sometimes two quotes are not seperated
            if re.search(r'(\d\d):(\d\d):(\d\d)', quoteText):
                print(f"Invalid format of {quote=} in {subFile=}")
                continue

            # Formatting
            quoteText = quoteText.strip()
            quoteText = re.sub(
                r"^\W*(and|but|so|also|that|i mean)\W*|" +
                r"([^a-zA-Z\?\.\!]*and|but|so|beacuse|also)\W*$",
                '',
                quoteText,
                flags=re.I).strip()
            quoteText = quoteText.capitalize()

            # Filters
            if len(re.sub(
                    r'\W|saiman|timothy|a+ditya', '',
                    quoteText, flags=re.I)) < 3:
                continue
            if re.search('video|^welcome', quoteText, re.I):
                # print(f"Banned words in '{quoteText}' of {subFile}")
                continue

            handFiltered = fldr == 'subs/done/'
            weight = sqrt(1 - subAge/oldestSubAge)

            if re.search('t-series|pewds|pewdiepie', quoteText, re.I):
                weight = weight/4
            if handFiltered:
                weight = weight * 1.2

            quote = Quote(quoteText, youtubeLink, weight, handFiltered)
            allQuotes.append(quote)

