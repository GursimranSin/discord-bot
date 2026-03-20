import feedparser
import requests
from datetime import datetime, time
from zoneinfo import ZoneInfo
import os

# Use environment variable - required for GitHub Actions
WEBHOOK = os.getenv("WEBHOOK_URL")
if not WEBHOOK:
    raise RuntimeError("WEBHOOK_URL environment variable not set")

EST = ZoneInfo("America/New_York")

RSS_TRADINGEDGE = "https://www.reddit.com/r/TradingEdge/.rss"
RSS_CANADIAN = "https://www.reddit.com/r/CanadianInvestor/search.rss?q=daily+discussion+thread+for&restrict_sr=1&sort=new&t=day"

def check_posts():
    now_est = datetime.now(EST)
    today = now_est.date()
    
    print(f"Now EST: {now_est}")
    print(f"Today: {today}")

    # Determine run type
    is_morning_run = now_est.hour < 12
    print(f"Is morning run: {is_morning_run}")

    # Time windows (EST)
    morning_start = datetime.combine(today, time(0, 0), EST)
    morning_end = datetime.combine(today, time(9, 0), EST)

    evening_start = datetime.combine(today, time(9, 0), EST)
    evening_end = datetime.combine(today, time(21, 0), EST)

    embeds = []

    # =========================
    # 1. TradingEdge (time-based)
    # =========================
    print("Fetching TradingEdge RSS...")
    feed = feedparser.parse(RSS_TRADINGEDGE)
    print(f"TradingEdge entries: {len(feed.entries)}")

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
        print("Fetching CanadianInvestor RSS...")
        feed = feedparser.parse(RSS_CANADIAN)
        print(f"CanadianInvestor entries: {len(feed.entries)}")

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
            "Morning Reddit Update (Before 9 AM EST)"
            if is_morning_run
            else "Evening Reddit Update (9 AM – 9 PM EST)"
        )

        print(f"Sending {len(embeds)} embeds to Discord...")

        response = requests.post(WEBHOOK, json={
            "content": header,
            "embeds": embeds,
            "username": Trading Bot"
        })

        print(f"Discord response: {response.status_code} - {response.reason}")
        print(f"Response text: {response.text[:200]}...")  # First 200 chars
    else:
        print("No posts in this time window")

if __name__ == "__main__":
    check_posts()

