import time
import threading
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VIRAL_TOPICS = []

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_TRENDS_URL = "https://api.twitter.com/1.1/trends/place.json"

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
INSTAGRAM_GRAPH_URL = "https://graph.facebook.com/v17.0"

INSTAGRAM_HASHTAGS = [
    "roblox", "violencedistrict", "vd", "valorant", "mlbb",
    "pubgmobile", "genshinimpact", "dota2", "fortnite", "gaming", "esports"
]

def fetch_twitter_trends(woeid=1, limit=10):
    print("📡 Fetching Twitter trends...")
    try:
        headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
        resp = requests.get(f"{TWITTER_TRENDS_URL}?id={woeid}", headers=headers)
        data = resp.json()

        if not isinstance(data, list) or "trends" not in data[0]:
            print("⚠️ Format data Twitter tidak sesuai.")
            return []

        trends = data[0]["trends"]
        trend_names = [t["name"].lower() for t in trends if t.get("name")]
        print(f"✅ Twitter trends fetched: {trend_names[:5]}")
        return trend_names[:limit]

    except Exception as e:
        print("❗ Error ambil data Twitter:", e)
        return []

def get_hashtag_id(hashtag):
    url = f"{INSTAGRAM_GRAPH_URL}/ig_hashtag_search"
    params = {
        "user_id": INSTAGRAM_ACCOUNT_ID,
        "q": hashtag,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if "data" in data and len(data["data"]) > 0:
        return data["data"][0]["id"]
    return None

def count_hashtag_activity(hashtag_id):
    url = f"{INSTAGRAM_GRAPH_URL}/{hashtag_id}/recent_media"
    params = {
        "user_id": INSTAGRAM_ACCOUNT_ID,
        "fields": "id,like_count,comments_count",
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if "data" not in data:
        return 0
    score = sum(
        item.get("like_count", 0) + item.get("comments_count", 0) + 1
        for item in data["data"]
    )
    return score

def fetch_instagram_trends(limit=5):
    print("📸 Fetching Instagram hashtag activity...")
    scores = {}
    for tag in INSTAGRAM_HASHTAGS:
        tag_id = get_hashtag_id(tag)
        if tag_id:
            score = count_hashtag_activity(tag_id)
            scores[tag] = score
            print(f" - #{tag}: {score}")
        else:
            scores[tag] = 0

    sorted_tags = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    trending_tags = [t for t, _ in sorted_tags[:limit]]
    print(f"✅ Instagram trending tags: {trending_tags}")
    return trending_tags

def fetch_viral_topics():
    global VIRAL_TOPICS
    print(f"\n🕓 Fetching viral topics at {datetime.now().strftime('%H:%M:%S')}")
    try:
        twitter_topics = fetch_twitter_trends()
        instagram_topics = fetch_instagram_trends()
        combined = list(dict.fromkeys(twitter_topics + instagram_topics))
        VIRAL_TOPICS = combined[:15]
        print("🔥 Combined viral topics:", VIRAL_TOPICS)
    except Exception as e:
        print("❗ Gagal ambil topik viral:", e)
        VIRAL_TOPICS = ["roblox", "valorant", "mlbb", "genshin", "pubg", "dota2"]
        print("⚠️ Using fallback topics:", VIRAL_TOPICS)

def start_trending_loop(interval_seconds=3600):
    def loop():
        while True:
            fetch_viral_topics()
            time.sleep(interval_seconds)
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
