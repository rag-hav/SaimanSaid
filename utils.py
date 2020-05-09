from praw.exceptions import RedditAPIException
import re
import time
from datetime import datetime
from quotes import randomQuote, sizeDoneQuotes, sizeSubQuotes

utcTime = lambda : datetime.utcnow().timestamp()

cakedayRedditors = []

def cakedayCheck(comment):
    if comment.author in cakedayRedditors:
        # Already Wished
        return False

    createdUtc = comment.author.created_utc
    currentUtc = utcTime()
    while(createdUtc < currentUtc):
        createdUtc += 3600 * 24 * 365
        if currentUtc - createdUtc < 3600 * 24:
            cakedayRedditors.append(comment.author)
            return True
    return False


def myCommentCheck(reddit):
    for comment in reddit.user.me().comments.new():

        # Get Already wished redditors btw runs
        if re.search(r"^Happy cakeday", comment.body) and \
                comment.author not in cakedayRedditors:

            cakedayRedditors.append(comment.author)

        # Delete bad comnents
        if comment.score < -4:
            comment.delete()
            reddit.redditor("I_eat_I_repeat").message(
                "Comment deleted",
                comment.body +
                '\n\n' +
                comment.parent().permalink.replace(
                    "reddit",
                    "removeddit"))
            print("Deleted comment {comment.permalink}")

        # Pull a sneaky one
        elif comment.score < 0 \
                and "Quote Sauce" in comment.body\
                and "\u200e" not in comment.body\
                and utcTime() - comment.created_utc < 5000:
            comment.refresh()
            if len(comment.replies) == 0:
                comment.edit(randomQuote()+'\u200e')
                print(f"Pulled a sneaky one on {comment.id}")


def updateKnowmore(reddit):
    Knowmore = reddit.submission("fvkvw9")
    srch = r"Currently, the bot has (\d+) filtered quotes and (\d+) "\
        "unfiltered quotes in its database"
    oldDoneNum, oldSubNum = re.search(srch, Knowmore.selftext).groups()

    if int(oldDoneNum) != sizeDoneQuotes or int(oldSubNum) != sizeSubQuotes:
        newBody = re.sub(
            srch,
            f"Currently, the bot has {sizeDoneQuotes} filtered quotes "
            "and {sizeSubQuotes} unfiltered quotes in its database",
            Knowmore.selftext)
        Knowmore.edit(newBody)
        print(f"Knowmore Updated: {sizeDoneQuotes} done quotes "
              f"and {sizeSubQuotes} sub quotes")


def replyToComment(comment, replyTxt):
    '''Wrapper to handle API limit exception'''

    try:
        comment.reply(replyTxt)

    except RedditAPIException as exception:
        for subexception in exception.items:
            print(subexception.error_type)
            time.sleep(5)
            replyToComment(comment, replyTxt)
