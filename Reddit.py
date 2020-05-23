import praw
import os
    
reddit = praw.Reddit(
    client_id=os.getenv("SaimanSaid_CLIENT_ID"),
    client_secret=os.getenv("SaimanSaid_CLIENT_SECRET"),
    user_agent=os.getenv("SaimanSaid_USER_AGENT"),
    username=os.getenv("SaimanSaid_USERNAME"),
    password=os.getenv("SaimanSaid_PASSWORD"))
