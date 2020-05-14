from datetime import datetime
import re
import sys
import signal
from quotes import randomQuote, sizeDoneQuotes, sizeSubQuotes

cakedayRedditors = []


class SignalHandler():

    def __init__(self):
        signal.signal(signal.SIGINT, self._signalHandler)
        signal.signal(signal.SIGTERM, self._signalHandler)
        self.exitCondition = False
        self.inLoop = False

    def _signalHandler(self, signal, frame):
        print(f"RECIEVED SIGNAL: {signal}, Bye")
        if not self.inLoop:
            sys.exit(0)
        else:
            self.exitCondition = True

    def loopEnd(self):
        self.inLoop = False

        if self.exitCondition:
            sys.exit(0)

    def loopStart(self):
        self.inLoop = True


def cakedayCheck(comment):
    if comment.author in cakedayRedditors:
        # Already Wished
        return False

    createdUtc = comment.author.created_utc + 3600 * 24 * 365
    currentUtc = utcTime()

    while(currentUtc > createdUtc):
        if currentUtc - createdUtc < 3600 * 24:
            cakedayRedditors.append(comment.author)
            return True
        createdUtc += 3600 * 24 * 365
    return False


def commentCheck(reddit):
    for comment in reddit.user.me().comments.new():

        # Get Already wished redditors btw runs
        if re.search(r"^Happy cakeday", comment.body) and \
                comment.author not in cakedayRedditors:

            cakedayRedditors.append(comment.author)

        # Delete bad comnents
        if comment.score < -4:
            parentId = comment.parent().permalink.replace(
                    "reddit", "removeddit")
            comment.delete()
            reddit.redditor("I_eat_I_repeat").message(
                    "Comment deleted",
                    comment.body + '\n\n' + parentId)
            print("Deleted comment {parentId}")

        # Pull a sneaky one
        elif comment.score < 0 \
                and "Quote Sauce" in comment.body\
                and "\u200e" not in comment.body\
                and utcTime() - comment.created_utc < 5000:
            comment.refresh()
            if len(comment.replies) == 0:
                comment.edit(randomQuote() + '\u200e')
                print(f"Pulled a sneaky one on {comment.permalink}")


def inboxCheck(reddit):
    for msg in reddit.inbox.messages():
        if msg.subject == "Block me":
            msg.reply("Okay done")
            print("User Blocked: " + msg.author.name)
            reddit.redditor("I_eat_I_repeat").message(
                "User Blocked", 'u/' + msg.author.name)
            msg.author.block()


def replyToComment(comment, replyTxt):

    replyComment = comment.reply(replyTxt)
    comment.save()
    print("\tSuccess: " + replyComment.id)


def updateKnowmore(reddit):
    Knowmore = reddit.submission("fvkvw9")
    srch = r"Currently, the bot has (\d+) filtered quotes and (\d+) "\
        r"unfiltered quotes in its database"
    oldDoneNum, oldSubNum = re.search(srch, Knowmore.selftext).groups()

    if int(oldDoneNum) != sizeDoneQuotes or int(oldSubNum) != sizeSubQuotes:
        newBody = re.sub(
            srch,
            f"Currently, the bot has {sizeDoneQuotes} filtered quotes "
            f"and {sizeSubQuotes} unfiltered quotes in its database",
            Knowmore.selftext)
        Knowmore.edit(newBody)
        print(f"Knowmore Updated: {sizeDoneQuotes} done quotes "
              f"and {sizeSubQuotes} sub quotes")


def utcTime(): return datetime.utcnow().timestamp()
