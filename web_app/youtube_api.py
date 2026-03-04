# web_app/youtube_api.py
"""
Fetch exercise tutorial URLs.
Priority:
  1. YouTube Data API v3  (if YOUTUBE_API_KEY is set)
  2. DuckDuckGo image search fallback  (dynamic, no API key needed)
  3. Static dictionary fallback
"""

import os
import re
import requests
from typing import Optional

# ────────────────────────────────────────────────────────
# Static fallback table
# ────────────────────────────────────────────────────────
STATIC_EXERCISE_VIDEOS = {
    "Push-ups":          "https://www.youtube.com/watch?v=IODxDxX7oi4",
    "Squats":            "https://www.youtube.com/watch?v=aclHkVaku9U",
    "Bodyweight Squats": "https://www.youtube.com/watch?v=aclHkVaku9U",
    "Plank":             "https://www.youtube.com/watch?v=ASdvN_XEl_c",
    "Lunges":            "https://www.youtube.com/watch?v=QE7_owA_zR4",
    "Burpees":           "https://www.youtube.com/watch?v=dUuZA5b_V7Y",
    "Dumbbell Rows":     "https://www.youtube.com/watch?v=Vkjx0_5PdF8",
    "Deadlift":          "https://www.youtube.com/watch?v=ytGaGIn3SjE",
    "Pull-ups":          "https://www.youtube.com/watch?v=eGo4IYlbE5g",
    "Lateral Raises":    "https://www.youtube.com/watch?v=3VcKaXpzqRo",
    "Dumbbell Curls":    "https://www.youtube.com/watch?v=ykJmrZ5v0Oo",
    "Hammer Curls":      "https://www.youtube.com/watch?v=TwD-YGVP4Bk",
    "Hip Thrusts":       "https://www.youtube.com/watch?v=Zp26q4BY5HE",
    "Glute Bridges":     "https://www.youtube.com/watch?v=OUgsJ8-Vi0E",
}

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
API_KEY = os.getenv("YOUTUBE_API_KEY")


# ────────────────────────────────────────────────────────
# 1.  Official YouTube Data API
# ────────────────────────────────────────────────────────
def _youtube_api_search(exercise_name: str) -> Optional[str]:
    if not API_KEY:
        return None
    try:
        resp = requests.get(YOUTUBE_SEARCH_URL, params={
            "part": "snippet",
            "q": f"{exercise_name} exercise tutorial",
            "type": "video",
            "maxResults": 1,
            "key": API_KEY,
        }, timeout=5)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if items:
            return f"https://www.youtube.com/watch?v={items[0]['id']['videoId']}"
    except Exception:
        pass
    return None


# ────────────────────────────────────────────────────────
# 2.  DuckDuckGo image search (dynamic, no key needed)
# ────────────────────────────────────────────────────────
def _duckduckgo_image(exercise_name: str) -> Optional[str]:
    """
    Hits the DuckDuckGo Instant Answer API to grab a related thumbnail image
    when no YouTube video is available. Falls back to None if it fails.
    """
    try:
        query = f"{exercise_name} exercise how to"
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "ia": "images"},
            timeout=5,
            headers={"User-Agent": "FitTrackerPro/1.0"}
        )
        data = resp.json()
        # DuckDuckGo puts an Image field in the top result
        image = data.get("Image") or data.get("image")
        if image:
            return image
        # Try RelatedTopics
        for topic in data.get("RelatedTopics", []):
            img = topic.get("Icon", {}).get("URL")
            if img:
                return img
    except Exception:
        pass
    return None


# ────────────────────────────────────────────────────────
# 3.  Public entry point
# ────────────────────────────────────────────────────────
def get_youtube_video_url(exercise_name: str) -> Optional[str]:
    """Return a YouTube URL, or None if nothing found."""
    return (
        _youtube_api_search(exercise_name)
        or STATIC_EXERCISE_VIDEOS.get(exercise_name)
    )


def get_exercise_image(exercise_name: str) -> Optional[str]:
    """
    Return an image URL for the exercise.
    Tries DuckDuckGo first, then some known static thumbnails.
    """
    return _duckduckgo_image(exercise_name)
