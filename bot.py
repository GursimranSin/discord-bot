import feedparser
import requests
from datetime import datetime
from bs4 import BeautifulSoup

WEBHOOK = "https://discord.com/api/webhooks/1483998601213644915/7v6QTNk39lpZ13U6x7_sYcHgAqQTLAC8BkzcM7xR8vNIzAyixA6X0c3m-TfZkiyLNfCB"
RSS = "https://www.reddit.com/r/TradingEdge/.rss"

CHUNK_SIZE = 1900  # Safe limit per embed description

def clean_content(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    
    for p in soup.find_all('p'):
        p.insert_after(soup.new_string('\n'))
    for li in soup.find_all('li'):
        li.insert(0, soup.new_string('• '))
        li.insert_after(soup.new_string('\n'))
    
    text = soup.get_text()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    content = '\n\n'.join(lines)
    
    return content  # No truncation — we'll chunk instead

def split_chunks(text, size=CHUNK_SIZE):
    chunks = []
    while len(text) > size:
        cut = text.rfind('\n', 0, size)  # Cut at last newline before limit
        if cut == -1:
            cut = size  # No newline found, hard cut
        chunks.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        chunks.append(text)
    return chunks

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
        chunks = split_chunks(content)

        for i, chunk in enumerate(chunks):
            embed = {
                "description": chunk,
                "color": 0xFF4500,
                "footer": {"text": f"r/TradingEdge • Part {i+1}/{len(chunks)}"}
            }
            # Only first chunk gets the title, timestamp, and thumbnail
            if i == 0:
                embed["title"] = title
                embed["timestamp"] = datetime.utcnow().isoformat() + 'Z'
                if image:
                    embed["thumbnail"] = {"url": image}

            embeds.append(embed)

        # Discord allows max 10 embeds per message — flush if getting close
        if len(embeds) >= 9:
            requests.post(WEBHOOK, json={"embeds": embeds, "username": "🆕 TradingEdge Bot"})
            embeds = []

    if embeds:
        data = {"embeds": embeds, "username": "🆕 TradingEdge Bot"}
        resp = requests.post(WEBHOOK, json=data)
        print(f"✅ Posted | {resp.status_code}")
    else:
        print("No new posts")

if __name__ == "__main__":
    check_posts()
