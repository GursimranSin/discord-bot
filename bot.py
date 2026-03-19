import feedparser
import requests
from datetime import datetime, time
from zoneinfo import ZoneInfo
import os

WEBHOOK = os.environ.get("WEBHOOK_URL")

EST = ZoneInfo("America/New_York")

# RSS feeds
RSS_DEFAULT = [
    "https://www.reddit.com/r/TradingEdge/.rss"
]

RSS_PM_ONLY = [
    "https://www.reddit.com/r/CanadianInvestor/search.rss?q=daily+discussion+thread+for&restrict_sr=1&sort=new&t=day"
]

def check_posts():
    now_est = datetime.now(EST)
    today = now_est.date()

    # Time windows
    morning_start = datetime.combine(today, time(0, 0), EST)
    morning_end = datetime.combine(today, time(9, 0), EST)

    evening_start = datetime.combine(today, time(9, 0), EST)
    evening_end = datetime.combine(today, time(21, 0), EST)

    is_morning_run = now_est.hour < 12

    # Select RSS feeds
    if is_morning_run:
        rss_feeds = RSS_DEFAULT
    else:
        rss_feeds = RSS_DEFAULT + RSS_PM_ONLY

    embeds = []

    for rss in rss_feeds:
        feed = feedparser.parse(rss)

        for entry in feed.entries:
            if not hasattr(entry, "published_parsed"):
                continue

            post_time_utc = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC"))
            post_time_est = post_time_utc.astimezone(EST)

            # Only same day
            if post_time_est.date() != today:
                continue

            if is_morning_run:
                if not (morning_start <= post_time_est < morning_end):
                    continue
            else:
                if not (evening_start <= post_time_est < evening_end):
                    continue

            embeds.append({
                "title": entry.title[:256],
                "url": entry.link,
                "color": 0xFF4500,
                "timestamp": post_time_est.isoformat(),
                "footer": {"text": "Reddit Feed"}
            })

    if embeds:
        header = "📊 Morning Reddit Update (Before 9 AM EST)" if is_morning_run else "📊 Evening Reddit Update (9 AM – 9 PM EST)"
        requests.post(WEBHOOK, json={
            "content": header,
            "embeds": embeds,
            "username": "🆕 Trading Bot"
        })
        print(f"✅ Posted {len(embeds)} posts")
    else:
        print("No posts in this time window")

if __name__ == "__main__":
    check_posts()
