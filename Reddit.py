import praw
import os

reddit = praw.Reddit(
    client_id=str(os.getenv("SaimanSaid_CLIENT_ID")),
    client_secret=str(os.getenv("SaimanSaid_CLIENT_SECRET")),
    user_agent=str(os.getenv("SaimanSaid_USER_AGENT")),
    username=str(os.getenv("SaimanSaid_USERNAME")),
    password=str(os.getenv("SaimanSaid_PASSWORD")),
)
