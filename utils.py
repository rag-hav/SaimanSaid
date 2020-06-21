import re
import os
import sys

from Reddit import reddit

cakedayRedditors = []


class SignalHandler():

    def __init__(self):
        import signal
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


def commentCheck():
    for comment in reddit.user.me().comments.new():

        # Get Already wished redditors btw runs
        if re.search(r"^Happy cakeday", comment.body):
            cakedayRedditors.append(comment.parent().author)

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
                from quotes import randomQuote
                comment.edit(randomQuote() + '\u200e')
                print(f"Pulled a sneaky one on {comment.permalink}")


def inboxCheck():
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


def updateKnowmore():
    from quotes import getAllQuotes

    allQuotes = getAllQuotes()
    filteredQuotes, unfilteredQuotes = 0, 0
    for quote in allQuotes:
        if quote.handFiltered:
            filteredQuotes += 1
        else:
            unfilteredQuotes += 1

    Knowmore = reddit.submission("fvkvw9")
    srch = r"Currently, the bot has (\d+) filtered quotes and (\d+) "\
        r"unfiltered quotes in its database"
    oldFilteredQts, oldUnfilteredQts = re.search(
        srch, Knowmore.selftext).groups()

    if int(oldFilteredQts) != filteredQuotes or int(
            oldUnfilteredQts) != unfilteredQuotes:
        newBody = re.sub(
            srch,
            f"Currently, the bot has {filteredQuotes} filtered quotes "
            f"and {unfilteredQuotes} unfiltered quotes in its database",
            Knowmore.selftext)
        Knowmore.edit(newBody)
        print(f"Knowmore Updated: {filteredQuotes} done quotes "
              f"and {unfilteredQuotes} sub quotes")


def utcTime():
    from datetime import datetime
    return datetime.utcnow().timestamp()


def getAge(timestamp):
    # timestamp in format YYYYMMDD
    from datetime import date
    d = int(timestamp)
    return (date.today() - date(d // 10000, d // 100 % 100, d % 100)).days


def _processSubtitle(vId):
    # Checks if ydl has downloaded the subtitle and writes them to subs folder
    for file_ in os.listdir():
        if vId in file_:
            with open(file_, 'r') as f:
                subData = f.read()
            cleanSub = '\n\n'.join(a for a in subData.split('\n\n')[1:] if a)
            with open('subs/' + file_.split('.')[0], 'w') as f:
                f.write(cleanSub)
            print("Downloaded Subtitle for " + vId)
            os.remove(file_)


def downloadNewSubtitles():
    from youtube_dl import YoutubeDL

    playlist = 'https://www.youtube.com/playlist?list=UUy9cb7U-Asbhbum0ZXArvfQ'

    ydlOpts = {'ignoreerrors': True, 'no_warnings': True,
               'quiet': True, 'outtmpl': '%(upload_date)s%(id)s',
               'skip_download': True
               }

    with YoutubeDL(ydlOpts) as ydl:
        playlistRes = ydl.extract_info(playlist, download=False, process=False)

    if not playlistRes:
        print("Failed to download playlist, skipping new subtitle check")
        return

    # Youtubedl doesnt return the info dict if this option is passed
    ydlOpts['writesubtitles'] = True

    with YoutubeDL(ydlOpts) as ydl:
        for vid in playlistRes['entries']:
            for subFile in os.listdir("subs/") + os.listdir("subs/done/"):
                if vid['id'] in subFile:
                    if getAge(subFile[:8]) > 30:
                        return
                    break
            else:
                ydl.process_ie_result(vid, download=True)
                _processSubtitle(vid['id'])
