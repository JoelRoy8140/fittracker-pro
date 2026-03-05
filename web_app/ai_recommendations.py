# web_app/ai_recommendations.py
"""
Google Gemini-powered AI recommendations.

Functions
---------
get_body_workout_recommendation(body_metrics, user_profile)
    → Returns a personalised workout plan as a dict, tailored to scan results.

get_facial_exercise_recommendation(face_metrics)
    → Returns tailored facial exercises based on face fat scan data.

Both functions fall back gracefully to rule-based logic when no API key is set.
"""

import os
import json
import re
from typing import Dict, Any, List

import streamlit as st

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
try:
    if "GEMINI_API_KEY" in st.secrets:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass


# ─── Gemini helper ────────────────────────────────────────────────────────────

def _call_gemini(prompt: str) -> str:
    """Call Gemini and return the raw text response."""
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


def _extract_json(text: str) -> Any:
    """Pull the first JSON block out of a Gemini response."""
    # Try to find ```json ... ``` block
    match = re.search(r"```json\s*([\s\S]+?)\s*```", text)
    if match:
        return json.loads(match.group(1))
    # Fallback: try parsing whole response
    return json.loads(text)


# ─── Body Workout Recommendation ─────────────────────────────────────────────

def get_body_workout_recommendation(
    body_metrics: Dict[str, Any],
    user_profile: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Given body scan metrics and user profile, returns a personalized workout plan.

    Parameters
    ----------
    body_metrics : dict
        Keys: bmi, body_fat, shoulder_width_px, waist_hip_ratio, etc.
    user_profile : dict
        Keys: name, age, gender, goal, activity_level, equipment, etc.

    Returns
    -------
    dict  — workout plan with 'ai_reasoning' and 'week' structure.
    """
    if not GEMINI_API_KEY:
        return _rule_based_body_plan(body_metrics, user_profile)

    prompt = f"""
You are an elite, professional strength and conditioning coach with access to a massive 
exercise database (similar to Muscle & Strength). Your job is to generate a HIGHLY dynamic, 
non-repetitive, and deeply personalized weekly workout plan based on the user's live body scan metrics.

## User Profile
- Name: {user_profile.get('name', 'User')}
- Age: {user_profile.get('age', 25)}
- Gender: {user_profile.get('gender', 'Not specified')}
- Goal: {user_profile.get('goal', 'General fitness')}
- Activity Level: {user_profile.get('activity_level', 'Beginner')}
- Available Equipment: {user_profile.get('equipment', ['Bodyweight'])}

## LIVE Body Scan Results
- BMI: {body_metrics.get('bmi', 'Unknown')}
- Body Fat %: {body_metrics.get('body_fat', 'Unknown')}%
- Shoulder/Hip Ratio: {body_metrics.get('waist_hip_ratio', 'Unknown')}

## Crucial Coaching Mandates:
1. DO NOT give generic, boring workouts (e.g., just "Pushups" or "Squats"). Use highly specific variations! 
   (e.g., "Incline Dumbbell Bench Press", "Cable Crossover (Low to High)", "Bulgarian Split Squats", "Decline Barbell Bench Press").
2. Explicitly tailor the `ai_reasoning` to their EXACT BMI and Body Fat %. Tell them why this routine is scientifically built for their current body composition.
3. Ensure the workout is physically possible with their `Available Equipment`.
4. Provide a structured weekly split based on their goal (e.g., Push/Pull/Legs, Upper/Lower, or Bro Split).

Return ONLY a JSON object with this exact structure (no markdown formatting outside the JSON, just the JSON string, but you can use markdown formatting inside the JSON values):

{{
  "ai_reasoning": "A 3-sentence deep dive into why this specific protocol matches their {body_metrics.get('bmi', 'BMI')} BMI and {body_metrics.get('body_fat', 'body fat')}% Body Fat.",
  "focus_areas": ["list", "of", "priority", "muscle", "groups"],
  "split_type": "The exact split name you chose",
  "week": {{
    "Day 1: Heavy Push (Chest/Shoulders/Triceps)": {{
      "focus": "Hypertrophy for anterior chain",
      "exercises": [
        {{
          "name": "Incline Dumbbell Bench Press",
          "sets": 4,
          "reps": "8-10",
          "rest": 90,
          "why": "Why this specific variation is chosen over a flat barbell bench for this user."
        }}
      ]
    }}
  }},
  "nutrition_tip": "One highly actionable diet tip mapped to their Body Fat %.",
  "weekly_cardio": "Exact cardio prescription (e.g., '30 mins LISS post-workout' or 'HIIT 2x a week')."
}}
"""

    try:
        raw = _call_gemini(prompt)
        plan = _extract_json(raw)
        plan["source"] = "gemini"
        return plan
    except Exception as e:
        print(f"[Gemini body] Error: {e}")
        fallback = _rule_based_body_plan(body_metrics, user_profile)
        fallback["ai_error"] = str(e)
        return fallback


# ─── Facial Exercise Recommendation ──────────────────────────────────────────

def get_facial_exercise_recommendation(face_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given face fat scan metrics, returns tailored facial exercises.

    Parameters
    ----------
    face_metrics : dict
        Keys: face_fat_score, face_fat_category, cheek_to_jaw_ratio, etc.

    Returns
    -------
    dict with 'ai_reasoning', 'exercises' list, 'daily_routine', 'lifestyle_tips'
    """
    if not GEMINI_API_KEY:
        return _rule_based_facial_plan(face_metrics)

    prompt = f"""
You are a certified facial fitness and wellness expert.

## Face Scan Results
- Face Fat Score: {face_metrics.get('face_fat_score', 50)}/100
- Category: {face_metrics.get('face_fat_category', 'Average')}
- Cheek-to-Jaw Ratio: {face_metrics.get('cheek_to_jaw_ratio', 1.0)}
- Face Width-to-Height Ratio: {face_metrics.get('face_width_to_height', 0.7)}

## Instructions
Based on these metrics, recommend specific facial exercises.
Return ONLY a JSON object:
{{
  "ai_reasoning": "2 sentence explanation of what the metrics indicate and the plan",
  "primary_concern": "main area to target (e.g., Cheeks, Jawline, Double Chin)",
  "exercises": [
    {{
      "name": "Exercise Name",
      "target": "Target area",
      "reps": "20 reps",
      "duration": "1 minute",
      "instructions": ["step 1", "step 2", "step 3"],
      "why": "Why this targets their specific concern"
    }}
  ],
  "daily_routine": "When and how to do the exercises (morning / evening, etc.)",
  "lifestyle_tips": ["tip 1", "tip 2"],
  "expected_results": "Realistic results timeframe"
}}
Recommend 4-6 exercises. Prioritize based on the fat score and ratio.
"""

    try:
        raw = _call_gemini(prompt)
        plan = _extract_json(raw)
        plan["source"] = "gemini"
        return plan
    except Exception as e:
        print(f"[Gemini facial] Error: {e}")
        fallback = _rule_based_facial_plan(face_metrics)
        fallback["ai_error"] = str(e)
        return fallback


# ─── Rule-Based Fallbacks ─────────────────────────────────────────────────────

def _rule_based_body_plan(body_metrics: Dict, user_profile: Dict) -> Dict:
    """Simple rule-based plan when Gemini is unavailable."""
    bmi      = body_metrics.get("bmi", 22)
    body_fat = body_metrics.get("body_fat", 20)
    goal     = user_profile.get("goal", "General fitness")

    if bmi > 27 or body_fat > 25:
        split = "Full Body"
        focus = ["Cardio", "Core", "Legs", "Full Body"]
        reasoning = (
            f"Your BMI of {bmi} and body fat of {body_fat}% suggest prioritising "
            "fat-burning workouts with compound movements and cardio."
        )
    elif bmi < 18.5:
        split = "Bro Split"
        focus = ["Chest", "Back", "Shoulders", "Arms"]
        reasoning = (
            "With a lower BMI, hypertrophy-focused training will help "
            "build lean muscle mass effectively."
        )
    else:
        split = "Push/Pull/Legs"
        focus = ["Chest", "Back", "Legs", "Shoulders"]
        reasoning = (
            "Your metrics indicate a balanced physique. Push/Pull/Legs "
            "provides efficient stimulus for muscle growth and maintenance."
        )

    return {
        "source":        "rule_based",
        "ai_reasoning":  reasoning,
        "focus_areas":   focus,
        "split_type":    split,
        "nutrition_tip": "Aim for 1.6–2.2g of protein per kg of bodyweight.",
        "weekly_cardio": "3×30 min moderate cardio (cycling, brisk walking, swimming).",
        "week": {},
    }


def _rule_based_facial_plan(face_metrics: Dict) -> Dict:
    """Curated facial exercises based on face fat score."""
    score    = face_metrics.get("face_fat_score", 50)
    category = face_metrics.get("face_fat_category", "Average")

    # Load local library
    exercises_library: List[Dict] = []
    try:
        from shared.utils import resource_path
        with open(resource_path("data/facial_exercises.json"), "r") as f:
            exercises_library = json.load(f)
    except Exception:
        pass

    # Filter exercises appropriate for the score
    recommended = [
        ex for ex in exercises_library
        if ex.get("fat_score_min", 0) <= score <= ex.get("fat_score_max", 100)
    ]

    # Ensure we always have exercises
    if not recommended:
        recommended = exercises_library[:5]

    # Sort by most relevant (higher min = more targeted)
    recommended.sort(key=lambda x: x.get("fat_score_min", 0), reverse=True)
    recommended = recommended[:6]

    if score < 30:
        concern = "Maintaining lean facial structure"
        tip = "Focus on jaw definition and cheekbone exercises."
    elif score < 60:
        concern = "Moderate cheek and jawline toning"
        tip = "Consistency is key — do exercises daily for 4 weeks."
    else:
        concern = "Reducing face fat and defining jawline"
        tip = "Combine facial exercises with overall fat loss through cardio."

    return {
        "source":          "rule_based",
        "ai_reasoning":    f"Your face fat score of {score}/100 ({category}) suggests {concern.lower()}.",
        "primary_concern": concern,
        "exercises":       recommended,
        "daily_routine":   "Do this routine every morning after washing your face, and again before bed.",
        "lifestyle_tips":  [
            tip,
            "Stay well hydrated — drink 2–3L of water daily.",
            "Reduce sodium intake to minimise facial bloating.",
            "Get 7–8 hours of sleep; poor sleep causes facial puffiness.",
        ],
        "expected_results": "Visible toning in 3–4 weeks with daily practice.",
    }
