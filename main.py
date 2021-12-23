from prawcore.exceptions import RequestException, ServerError
from Reddit import reddit
import time
from utils import (
    SignalHandler,
    commentCheck,
    downloadNewSubtitles,
    getActiveSubs,
    inboxCheck,
    processComment,
)


signalHandler = SignalHandler()


def main():

    downloadNewSubtitles()

    commentCheckTime = 0
    inboxCheckTime = 0
    me = reddit.user.me()

    for comment in reddit.subreddit(getActiveSubs()).stream.comments():

        signalHandler.loopStart()

        if time.time() > inboxCheckTime:
            inboxCheck()
            inboxCheckTime = time.time() + 3600 * 12

        if time.time() > commentCheckTime:
            commentCheck()
            commentCheckTime = time.time() + 1800

        if not (comment.saved or comment.author == me):
            processComment(comment)

        signalHandler.loopEnd()


if __name__ == "__main__":
    print("Starting the bot")
    while True:
        try:
            main()
        # Network Issues
        except (RequestException, ServerError) as e:
            print(e)
            time.sleep(60)
        else:
            print("Program ended. It aint supposed to")
            break
