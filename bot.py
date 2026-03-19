import feedparser
import requests
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

WEBHOOK = "https://discord.com/api/webhooks/1483998601213644915/7v6QTNk39lpZ13U6x7_sYcHgAqQTLAC8BkzcM7xR8vNIzAyixA6X0c3m-TfZkiyLNfCB"
RSS = "https://www.reddit.com/r/TradingEdge/.rss"

def clean_content(html_text):
    if not html_text:
        return "No content available"
    
    soup = BeautifulSoup(html_text, 'html.parser')
    for p in soup.find_all('p'):
        p.name = 'div'
    for li in soup.find_all('li'):
        li.name = 'div'
        li.insert(0, BeautifulSoup('• ', 'html.parser'))
    
    text = soup.get_text().strip()
    if not text:
        return "Content parsing failed"
    
    content = re.sub(r'\n+', '\n\n', text)
    return content

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
    print("Fetching RSS...")
    feed = feedparser.parse(RSS)
    print(f"Found {len(feed.entries)} posts")
    
    if not feed.entries:
        requests.post(WEBHOOK, json={"content": "❌ No posts in r/TradingEdge RSS"})
        return
    
    embeds = []
    for i, entry in enumerate(feed.entries[:3]):
        title = entry.title[:256] or f"Post {i+1}"
        summary = entry.get('summary', '')
        content = clean_content(summary)
        print(f"Post {i+1}: {len(content)} chars")
        
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
    
    data = {"embeds": embeds, "username": "🆕 TradingEdge Bot"}
    resp = requests.post(WEBHOOK, json=data)
    print(f"Discord response: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    check_posts()
