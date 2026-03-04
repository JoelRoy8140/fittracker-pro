# web_app/workout_generator.py
"""
Generates personalised workout plans based on:
 - user profile (goal, equipment, activity level)
 - chosen split (Full Body / Push-Pull-Legs / Upper-Lower / Bro Split)
 - session duration in minutes
"""

import json, random, os
from typing import Dict, List, Any
from datetime import datetime
from shared.utils import resource_path

TEMPLATE_PATH  = resource_path(os.path.join("data", "workout_templates.json"))
SPLITS_PATH    = resource_path(os.path.join("data", "workout_splits.json"))

SPLIT_TYPES = ["Full Body", "Push/Pull/Legs", "Upper/Lower", "Bro Split"]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _load_splits() -> Dict:
    with open(SPLITS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_templates() -> List[Dict]:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Public alias kept for backward-compat
def load_templates() -> List[Dict]:
    return _load_templates()


def _equipment_ok(exercise: Dict, user_equipment: List[str]) -> bool:
    """Return True if the user has all required equipment (Bodyweight is free)."""
    required = exercise.get("required_equipment", [])
    for item in required:
        if item == "Bodyweight":
            continue
        if item not in user_equipment:
            return False
    return True


def _pick_exercises(muscle_groups: List[str],
                    all_exercises: Dict[str, List],
                    user_equipment: List[str],
                    per_muscle: int = 2) -> List[Dict]:
    chosen = []
    for muscle in muscle_groups:
        pool = [e for e in all_exercises.get(muscle, [])
                if _equipment_ok(e, user_equipment)]
        random.shuffle(pool)
        chosen.extend(pool[:per_muscle])
    return chosen


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def generate_workout_plan(user_profile: Dict[str, Any],
                          duration_minutes: int = 45,
                          split_type: str = "Full Body") -> Dict[str, Any]:
    """
    Returns:
    {
        "split": "Push/Pull/Legs",
        "week": {
            "Push Day": { "focus": "...", "exercises": [...] },
            ...
        },
        "date": "YYYY-MM-DD"
    }
    """
    splits_data = _load_splits()
    all_exercises_by_muscle = splits_data["exercises_by_muscle"]
    splits_config = splits_data["splits"]

    equipment = user_profile.get("equipment", []) or []
    # Always add Bodyweight
    if "Bodyweight" not in equipment:
        equipment.append("Bodyweight")

    # Pick split configuration
    split_config = splits_config.get(split_type, splits_config["Full Body"])
    
    week_plan = {}
    for day_name, day_info in split_config["days"].items():
        muscle_groups = day_info["muscle_groups"]
        description   = day_info["description"]
        
        # Approximate per_muscle count from duration and number of muscle groups
        per_muscle = max(1, duration_minutes // (len(muscle_groups) * 8))

        exercises = _pick_exercises(muscle_groups, all_exercises_by_muscle,
                                    equipment, per_muscle=per_muscle)

        week_plan[day_name] = {
            "focus": description,
            "muscle_groups": muscle_groups,
            "exercises": exercises,
        }

    return {
        "split":  split_type,
        "date":   datetime.now().strftime("%Y-%m-%d"),
        "week":   week_plan,
        # Flat exercise list for code that expects the old format
        "exercises": [ex for day in week_plan.values()
                      for ex in day["exercises"]],
        "focus":  split_type,
        "duration_minutes": duration_minutes,
    }
