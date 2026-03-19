import feedparser
import requests
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

WEBHOOK = "https://discord.com/api/webhooks/1483998601213644915/7v6QTNk39lpZ13U6x7_sYcHgAqQTLAC8BkzcM7xR8vNIzAyixA6X0c3m-TfZkiyLNfCB"
RSS = "https://www.reddit.com/r/TradingEdge/.rss"

def clean_content(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Preserve structure: p → div, li → bullet
    for p in soup.find_all('p'):
        p.name = 'div'
    for li in soup.find_all('li'):
        li.name = 'div'
        li.insert(0, BeautifulSoup('• ', 'html.parser'))
    
    text = soup.get_text()
    
    # Perfect spacing + bullets
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    content = '\n\n'.join(lines)
    
    return content[:1900]

def get_image(entry):
    for media in entry.get('media_content', []):
        if media.get('medium') == 'image':
            return media['url']
    thumbs = entry.get('media_thumbnail', [])
    if thumbs:
        return thumbs[0]['url']
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
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "footer": {"text": "r/TradingEdge"}
        }
        if image:
            embed["thumbnail"] = {"url": image}
        
        embeds.append(embed)
    
    if embeds:
        data = {"embeds": embeds, "username": "🆕 TradingEdge Bot"}
        resp = requests.post(WEBHOOK, json=data)
        print(f"✅ Posted {len(embeds)} | {resp.status_code}")
    else:
        print("No new posts")

if __name__ == "__main__":
    check_posts()
