import feedparser
import requests
import os
from datetime import datetime
from urllib.parse import urlparse
import re

WEBHOOK = "https://discord.com/api/webhooks/1483998601213644915/7v6QTNk39lpZ13U6x7_sYcHgAqQTLAC8BkzcM7xR8vNIzAyixA6X0c3m-TfZkiyLNfCB"
RSS = "https://www.reddit.com/r/TradingEdge/.rss"

def clean_content(text):
    # Remove links, trim
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    return text.strip()[:1900]  # Discord limit

def get_image(post_link):
    # Reddit post image (simple)
    if 'i.redd.it' in post_link:
        return post_link
    return None

def check_posts():
    feed = feedparser.parse(RSS)
    embeds = []
    
    for entry in feed.entries[:3]:  # 3 newest
        title = entry.title
        content = clean_content(entry.get('summary', ''))
        image = get_image(entry.link)
        
        embed = {
            "title": title[:256],
            "description": content,
            "color": 0xFF4500,  # Orange
            "timestamp": datetime.now().isoformat()
        }
        if image:
            embed["thumbnail"] = {"url": image}
        
        embeds.append(embed)
    
    if embeds:
        requests.post(WEBHOOK, json={
            "embeds": embeds,
            "username": "TradingEdge Bot"
        })
        print("✅ Posted", len(embeds), "posts")
    else:
        print("No new posts")

check_posts()
