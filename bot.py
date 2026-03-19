for rss in rss_feeds:
    feed = feedparser.parse(rss)

    # Special handling for CanadianInvestor
    if "CanadianInvestor" in rss:
        if is_morning_run:
            continue  # skip completely in morning

        # Only take latest post
        entries = feed.entries[:1]

        for entry in entries:
            if not hasattr(entry, "published_parsed"):
                continue

            post_time_utc = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC"))
            post_time_est = post_time_utc.astimezone(EST)

            # Only same day
            if post_time_est.date() != today:
                continue

            embeds.append({
                "title": entry.title[:256],
                "url": entry.link,
                "color": 0xFF4500,
                "timestamp": post_time_est.isoformat(),
                "footer": {"text": "CanadianInvestor Daily Thread"}
            })

    else:
        # Existing TradingEdge logic (UNCHANGED)
        for entry in feed.entries:
            if not hasattr(entry, "published_parsed"):
                continue

            post_time_utc = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC"))
            post_time_est = post_time_utc.astimezone(EST)

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
