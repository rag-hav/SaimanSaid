import re
import random
from urllib.parse import quote
from utils import doneQuotes, subQuotes

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
    footer = "\n\n***\n^^[Report error](<https://www.reddit.com/message/" +\
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

    if targetUserRegex := re.search(
        r'u/(\w+)',
        sourceComment.body,
            re.I):
        targetUsername = targetUserRegex.group(1)
        targetRedditor = reddit.redditor(targetUsername)
        try:
            targetRedditor.id
        except NotFound:
            return f"Sorry comrade, it looks like is no u/{targetUsername}" + \
                footer

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
        return f'Thankyou for your request comrade  \n\n&nbsp;\n  '\
            '\nu/{targetUsername} has said "Bhendi" a total of '\
            '{bcount} times!' + bhendiRank + footer
    else:
        return 'Sorry comrade. I did not find any username in your request. '\
            'You can call me properly by:  \n>BhendiCount! '\
            f'u/{sourceComment.author.name}' + footer


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
