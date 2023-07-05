import praw
from .reddit_scraper import RedditScraper


# Authenticate with Reddit API using praw.ini
reddit = praw.Reddit("ytbot")

# Initialize RedditScraper instance 
scraper = RedditScraper(reddit)