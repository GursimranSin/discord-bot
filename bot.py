import feedparser
import requests
import os
from datetime import datetime

WEBHOOK = "https://discord.com/api/webhooks/1483998601213644915/7v6QTNk39lpZ13U6x7_sYcHgAqQTLAC8BkzcM7xR8vNIzAyixA6X0c3m-TfZkiyLNfCB"
RSS = "https://www.reddit.com/r/TradingEdge/.rss"

def check_posts():
    feed = feedparser.parse(RSS)
    new_posts = []
    for entry in feed.entries[:5]:  # Last 5 posts
        new_posts.append(f"**{entry.title}**\n{entry.link}\n{entry.published}")
    
    if new_posts:
        requests.post(WEBHOOK, json={
            "content": f"**🆕 r/TradingEdge Updates** ({datetime.now().strftime('%H:%M')})\n\n" + "\n\n".join(new_posts[:3])
        })
        print("Posted!")
    else:
        print("No new posts")

check_posts()  # Run once
