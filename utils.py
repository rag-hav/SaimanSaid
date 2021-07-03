import re
import os
import sys
from datetime import datetime, date

from prawcore.exceptions import NotFound
from praw.exceptions import RedditAPIException

from Reddit import reddit

cakedayRedditors = []


def utcTime():
    return datetime.utcnow().timestamp()


class SignalHandler():

    def __init__(self):
        import signal
        signal.signal(signal.SIGINT, self._signalHandler)
        signal.signal(signal.SIGTERM, self._signalHandler)
        self.exitWhenLoopEnds = False
        self.inLoop = False

    def _signalHandler(self, signal, frame):
        print(f"RECIEVED SIGNAL: {signal}, Bye")
        if not self.inLoop:
            sys.exit(0)
        else:
            self.exitWhenLoopEnds = True

    def loopEnd(self):
        self.inLoop = False

        if self.exitWhenLoopEnds:
            sys.exit(0)

    def loopStart(self):
        self.inLoop = True


def cakedayCheck(comment):
    if comment.author in cakedayRedditors:
        return False

    try:
        created = comment.author.created_utc
        timeDiff = datetime.utcnow() - datetime.fromtimestamp(created)
        res = timeDiff.days % 365 == 0

    except NotFound:
        try:
            res = bool(comment.__dict__.get("author_cakeday"))
        except:
            return False

    if res:
        cakedayRedditors.append(comment.author)
        return True
    return False


def commentCheck():
    print("Checking old comments")
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


def blockRedditor(redditor):
    print("User Blocked: " + redditor.name)
    reddit.redditor("I_eat_I_repeat").message(
        "User Blocked", 'u/' + redditor.name)
    redditor.block()


def inboxCheck():
    print("Checking Inbox")
    for msg in reddit.inbox.messages():
        if msg.subject == "Block me":
            msg.reply("Okay done")
            blockRedditor(msg.author)


def replyToComment(comment, replyTxt):

    try:
        replyComment = comment.reply(replyTxt)
        comment.save()
        print("\tSuccess: " + replyComment.id)
    except RedditAPIException as e:
        print(e)


def getAge(timestamp):
    # timestamp in format YYYYMMDD
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
    print("Checking for new subtitles")
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


def getActiveSubs():
    wikiPg = reddit.subreddit("SaimanSaid").wiki["activesubs"].content_md
    return "+".join([a.strip() for a in wikiPg.splitlines() if a])
