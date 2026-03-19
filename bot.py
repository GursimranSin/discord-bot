import feedparser
import requests
import os
from datetime import datetime
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup

WEBHOOK = "https://discord.com/api/webhooks/1483998601213644915/7v6QTNk39lpZ13U6x7_sYcHgAqQTLAC8BkzcM7xR8vNIzAyixA6X0c3m-TfZkiyLNfCB"
RSS = "https://www.reddit.com/r/TradingEdge/new/.rss"

def clean_content(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text[:1900]

def get_image(entry):
    # Check media enclosures first
    for media in entry.get('media_content', []):
        if media.get('medium') == 'image':
            return media['url']
    # Check thumbnails
    thumbnails = entry.get('media_thumbnail', [])
    if thumbnails:
        return thumbnails[0]['url']
    # Reddit image post
    if 'i.redd.it' in entry.link:
        return entry.link
    return None

def check_posts():
    feed = feedparser.parse(RSS)
    embeds = []
    
    for entry in feed.entries[:3]:
        title = entry.title[:256]
        content = clean_content(entry.get('summary', ''))
        image = get_image(entry)
        
        embed = {
            "title": title,
            "description": content,
            "color": 0xFF4500,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        if image:
            embed["thumbnail"] = {"url": image}
        
        embeds.append(embed)
    
    if embeds:
        requests.post(WEBHOOK, json={
            "embeds": embeds,
            "username": "🆕 TradingEdge Bot"
        })
        print(f"✅ Posted {len(embeds)} posts")
    else:
        print("No new posts")

if __name__ == "__main__":
    check_posts()
