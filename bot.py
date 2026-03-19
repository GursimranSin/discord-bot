import feedparser
import requests
from datetime import datetime, time
from zoneinfo import ZoneInfo
import os

WEBHOOK = os.environ.get("WEBHOOK_URL")
RSS = "https://www.reddit.com/r/TradingEdge/.rss"

EST = ZoneInfo("America/New_York")

def check_posts():
    feed = feedparser.parse(RSS)
    embeds = []

    now_est = datetime.now(EST)
    today = now_est.date()

    # Define time windows in EST
    morning_start = datetime.combine(today, time(0, 0), EST)
    morning_end = datetime.combine(today, time(9, 0), EST)

    evening_start = datetime.combine(today, time(9, 0), EST)
    evening_end = datetime.combine(today, time(21, 0), EST)

    is_morning_run = now_est.hour < 12  # safe detection

    for entry in feed.entries:
        if not hasattr(entry, "published_parsed"):
            continue

        post_time_utc = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC"))
        post_time_est = post_time_utc.astimezone(EST)

        # Ensure same day (EST)
        if post_time_est.date() != today:
            continue

        if is_morning_run:
            if morning_start <= post_time_est < morning_end:
                embeds.append({
                    "title": entry.title[:256],
                    "url": entry.link,
                    "color": 0xFF4500,
                    "timestamp": post_time_est.isoformat(),
                    "footer": {"text": "r/TradingEdge"}
                })
        else:
            if evening_start <= post_time_est < evening_end:
                embeds.append({
                    "title": entry.title[:256],
                    "url": entry.link,
                    "color": 0xFF4500,
                    "timestamp": post_time_est.isoformat(),
                    "footer": {"text": "r/TradingEdge"}
                })

    if embeds:
        header = "📊 Morning Reddit Update (Before 9 AM EST)" if is_morning_run else "📊 Evening Reddit Update (9 AM – 9 PM EST)"
        requests.post(WEBHOOK, json={
            "content": header,
            "embeds": embeds,
            "username": "🆕 TradingEdge Bot"
        })
        print(f"✅ Posted {len(embeds)} posts")
    else:
        print("No posts in this time window")

if __name__ == "__main__":
    check_posts()
