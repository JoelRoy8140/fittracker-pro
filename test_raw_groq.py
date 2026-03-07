import os
import json
os.environ["GROQ_API_KEY"] = "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"

from web_app.ai_recommendations import get_body_workout_recommendation

body_metrics = {"bmi": 24, "body_fat": 15, "waist_hip_ratio": 0.85, "shoulder_width_px": 200}
user_profile = {"name": "Test User", "age": 25, "gender": "Male", "goal": "Muscle gain", "activity_level": "Active", "equipment": ["Dumbbells", "Bodyweight"]}

try:
    res = get_body_workout_recommendation(body_metrics, user_profile)
    with open("raw_llm_output2.txt", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
except Exception as e:
    with open("raw_llm_output2.txt", "w", encoding="utf-8") as f:
        f.write("ERROR: " + str(e))
