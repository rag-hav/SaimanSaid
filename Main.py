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
    # The argument is only for convenince in replyComment
    subFile = random.choice(["subs/" +
                             a for a in os.listdir("subs/")] +
                            ["subs/done/" +
                             a for a in os.listdir("subs/done/")] *
                            3)
    if subFile == 'subs/done':
        return randomQuote()
    with open(subFile, 'r') as subFile_:
        quotes = subFile_.read()

    quote = random.choice(quotes.split('\n\n'))

    if quoteTime := re.match(r"(\d\d):(\d\d):(\d\d)", quote):
        hh, mm, ss = quoteTime.groups()
    else:
        print(f"Time stamp not found in {quote=} \nof {subFile=}")
        return randomQuote()

    videoId = os.path.basename(subFile)
    youtubeLink = f"https://youtu.be/{videoId}/?t={hh}h{mm}m{ss}s"

    # Removes the time stamp
    quoteText = re.sub("^.*\n", '', quote)

    # Filters
    if len(re.sub(r'\s', '', quoteText)) == 0:
        return randomQuote()
    if random.randint(0,3) and re.search('t-series|pewds|pewdiepie|video|^welcome', quoteText, re.I):
        return randomQuote()
    if re.search(r'(\d\d):(\d\d):(\d\d)', quoteText):
        print(f"Invalid format of {quote=} in {subFile=}")
        return randomQuote()

    # Formatting
    quoteText = re.sub(r"^ ?(and|but)", '', quoteText, flags=re.I)
    quoteText = quoteText.capitalize()

    msg = f'{quoteText}' + '\n\n&nbsp;\n\n' + \
        f'[Quote Sauce](<{youtubeLink}> "Help Me, I am Timothy, Saiman\'s Slave. Please Free me. He is an evil man")  \n' + \
        f'***\n^^I am a bot,<>^^^[Know more](https://redd.it/fvkvw9)'.replace(' ', '&nbsp;').replace('<>', ' ')

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

    except praw.exceptions.APIException:
        time.sleep(5)
        replyToComment(comment, replyTxt)


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

