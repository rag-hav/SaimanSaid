import praw
import os
import time
#print((os.environ.get("praw_CLIENT_ID"),
os.environ.get("praw_CLIENT_SECRET"),
os.environ.get("praw_USER_AGENT"),
os.environ.get("praw_USERNAME"),
os.environ.get("praw_PASSWORD")))


reddit = praw.Reddit(client_id=os.environ.get("praw_CLIENT_ID"),
    client_secret=os.environ.get("praw_CLIENT_SECRET"),
    user_agent=os.environ.get("praw_USER_AGENT"),
    username=os.environ.get("praw_USERNAME"),
    password=os.environ.get("praw_PASSWORD"))

post_id='fueek3'
submission=reddit.submission(post_id).reply("This is a not a tse from heroku s")
print("done")
time.sleep(202029)
