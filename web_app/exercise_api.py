# web_app/exercise_api.py
"""
Exercise database client.

Priority:
  1. ExerciseDB via RapidAPI  (set RAPIDAPI_KEY env var)
  2. Wger REST API            (completely free, no key)
  3. Local workout_splits.json fallback
"""

import os
import json
import requests
from typing import List, Dict, Optional
from functools import lru_cache
from shared.utils import resource_path

RAPIDAPI_KEY  = os.getenv("RAPIDAPI_KEY", "")
EXERCISEDB_HOST = "exercisedb.p.rapidapi.com"

WGER_BASE = "https://wger.de/api/v2"

# ─── ExerciseDB (RapidAPI) ────────────────────────────────────────────────────

@lru_cache(maxsize=64)
def _exercisedb_by_muscle(muscle: str, limit: int = 10) -> List[Dict]:
    """Fetch exercises from ExerciseDB filtered by target muscle."""
    if not RAPIDAPI_KEY:
        return []
    try:
        url = f"https://{EXERCISEDB_HOST}/exercises/target/{muscle.lower()}"
        response = requests.get(
            url,
            headers={
                "X-RapidAPI-Key":  RAPIDAPI_KEY,
                "X-RapidAPI-Host": EXERCISEDB_HOST,
            },
            params={"limit": limit, "offset": 0},
            timeout=8,
        )
        response.raise_for_status()
        raw = response.json()
        # Normalize to our schema
        return [
            {
                "name":               ex.get("name", "Unknown").title(),
                "sets":               3,
                "reps":               "10-12",
                "rest":               60,
                "required_equipment": [ex.get("equipment", "bodyweight").title()],
                "muscle_group":       ex.get("target", muscle).title(),
                "gif_url":            ex.get("gifUrl", ""),
                "secondary_muscles":  ex.get("secondaryMuscles", []),
                "instructions":       ex.get("instructions", []),
                "source":             "exercisedb",
            }
            for ex in raw[:limit]
        ]
    except Exception as e:
        print(f"[ExerciseDB] Error: {e}")
        return []


@lru_cache(maxsize=64)
def _exercisedb_search(name: str) -> Optional[Dict]:
    """Search ExerciseDB for a specific exercise by name."""
    if not RAPIDAPI_KEY:
        return None
    try:
        response = requests.get(
            f"https://{EXERCISEDB_HOST}/exercises/name/{name.lower()}",
            headers={
                "X-RapidAPI-Key":  RAPIDAPI_KEY,
                "X-RapidAPI-Host": EXERCISEDB_HOST,
            },
            timeout=8,
        )
        response.raise_for_status()
        results = response.json()
        if results:
            ex = results[0]
            return {
                "name":        ex.get("name", name).title(),
                "gif_url":     ex.get("gifUrl", ""),
                "muscle":      ex.get("target", ""),
                "equipment":   ex.get("equipment", ""),
                "instructions": ex.get("instructions", []),
                "source":      "exercisedb",
            }
    except Exception as e:
        print(f"[ExerciseDB search] Error: {e}")
    return None


# ─── Wger (free, no key) ──────────────────────────────────────────────────────

@lru_cache(maxsize=64)
def _wger_by_muscle(muscle_name: str, limit: int = 10) -> List[Dict]:
    """Fetch exercises from Wger's public REST API."""
    # Wger uses numeric category IDs ― map common names
    category_map = {
        "chest": 11, "back": 12, "biceps": 13, "triceps": 14,
        "legs": 10, "shoulders": 13, "core": 10, "quads": 10,
        "hamstrings": 10, "glutes": 10, "calves": 10, "arms": 13,
    }
    cat_id = category_map.get(muscle_name.lower())
    params = {"format": "json", "limit": limit, "language": 2}
    if cat_id:
        params["category"] = cat_id
    try:
        resp = requests.get(f"{WGER_BASE}/exercise/", params=params, timeout=8)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        exercises = []
        for ex in results:
            name_list = ex.get("translations", [])
            eng_name  = next((t["name"] for t in name_list if t.get("language") == 2), "")
            if not eng_name:
                continue
            exercises.append({
                "name":               eng_name.title(),
                "sets":               3,
                "reps":               "10-12",
                "rest":               60,
                "required_equipment": ["Bodyweight"],
                "muscle_group":       muscle_name.title(),
                "gif_url":            "",
                "source":             "wger",
            })
        return exercises
    except Exception as e:
        print(f"[Wger] Error: {e}")
        return []


# ─── Local fallback ───────────────────────────────────────────────────────────

def _local_by_muscle(muscle: str, limit: int = 10) -> List[Dict]:
    try:
        with open(resource_path("data/workout_splits.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        exs = data.get("exercises_by_muscle", {}).get(muscle, [])
        for ex in exs:
            ex.setdefault("gif_url", "")
            ex.setdefault("source", "local")
        return exs[:limit]
    except Exception:
        return []


# ─── Public API ───────────────────────────────────────────────────────────────

def get_exercises_by_muscle(muscle: str, limit: int = 10) -> List[Dict]:
    """
    Return exercises for a muscle group.
    Tries ExerciseDB → Wger → local data.
    """
    exs = _exercisedb_by_muscle(muscle, limit)
    if not exs:
        exs = _wger_by_muscle(muscle, limit)
    if not exs:
        exs = _local_by_muscle(muscle, limit)
    return exs


def get_exercise_detail(name: str) -> Optional[Dict]:
    """Look up a specific exercise and return its detail (including GIF)."""
    return _exercisedb_search(name)


def get_gif_url(exercise_name: str) -> str:
    """Return a GIF URL for the given exercise name, or empty string."""
    detail = get_exercise_detail(exercise_name)
    return detail.get("gif_url", "") if detail else ""
