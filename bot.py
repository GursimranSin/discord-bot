import feedparser
import requests
from datetime import datetime, time
from zoneinfo import ZoneInfo
import os

WEBHOOK = "https://discord.com/api/webhooks/1483998601213644915/7v6QTNk39lpZ13U6x7_sYcHgAqQTLAC8BkzcM7xR8vNIzAyixA6X0c3m-TfZkiyLNfCB";

EST = ZoneInfo("America/New_York")

RSS_TRADINGEDGE = "https://www.reddit.com/r/TradingEdge/.rss"
RSS_CANADIAN = "https://www.reddit.com/r/CanadianInvestor/search.rss?q=daily+discussion+thread+for&restrict_sr=1&sort=new&t=day"

def check_posts():
    now_est = datetime.now(EST)
    today = now_est.date()

    # Determine run type
    is_morning_run = now_est.hour < 12

    # Time windows (EST)
    morning_start = datetime.combine(today, time(0, 0), EST)
    morning_end = datetime.combine(today, time(9, 0), EST)

    evening_start = datetime.combine(today, time(9, 0), EST)
    evening_end = datetime.combine(today, time(21, 0), EST)

    embeds = []

    # =========================
    # 1. TradingEdge (time-based)
    # =========================
    feed = feedparser.parse(RSS_TRADINGEDGE)

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
            "footer": {"text": "TradingEdge"}
        })

    # =========================
    # 2. CanadianInvestor (PM only, ignore time window)
    # =========================
    if not is_morning_run:
        feed = feedparser.parse(RSS_CANADIAN)

        if feed.entries:
            entry = feed.entries[0]  # only latest daily thread

            if hasattr(entry, "published_parsed"):
                post_time_utc = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC"))
                post_time_est = post_time_utc.astimezone(EST)

                # Only same day
                if post_time_est.date() == today:
                    embeds.append({
                        "title": entry.title[:256],
                        "url": entry.link,
                        "color": 0x00AAFF,
                        "timestamp": post_time_est.isoformat(),
                        "footer": {"text": "CanadianInvestor Daily Thread"}
                    })

    # =========================
    # Send to Discord
    # =========================
    if embeds:
        header = (
            "📊 Morning Reddit Update (Before 9 AM EST)"
            if is_morning_run
            else "📊 Evening Reddit Update (9 AM – 9 PM EST)"
        )

        response = requests.post(WEBHOOK, json={
            "content": header,
            "embeds": embeds,
            "username": "🆕 Trading Bot"
        })

        print(f"✅ Posted {len(embeds)} posts | Status: {response.status_code}")
    else:
        print("No posts in this time window")

if __name__ == "__main__":
    check_posts()
