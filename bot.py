import feedparser
import requests
from datetime import datetime

WEBHOOK = "https://discord.com/api/webhooks/1483998601213644915/7v6QTNk39lpZ13U6x7_sYcHgAqQTLAC8BkzcM7xR8vNIzAyixA6X0c3m-TfZkiyLNfCB"
RSS = "https://www.reddit.com/r/TradingEdge/.rss"

def check_posts():
    feed = feedparser.parse(RSS)
    embeds = []

    for entry in feed.entries[:3]:
        embed = {
            "title": entry.title[:256],
            "url": entry.link,
            "color": 0xFF4500,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "footer": {"text": "r/TradingEdge"}
        }
        embeds.append(embed)

    if embeds:
        resp = requests.post(WEBHOOK, json={"embeds": embeds, "username": "🆕 TradingEdge Bot"})
        print(f"✅ Posted {len(embeds)} | {resp.status_code}")
    else:
        print("No new posts")

if __name__ == "__main__":
    check_posts()
