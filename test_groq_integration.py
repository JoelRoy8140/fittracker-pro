import os
from streamlit import secrets

# Setup environment to use the key directly for testing
os.environ["GROQ_API_KEY"] = "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"

from web_app.ai_recommendations import get_body_workout_recommendation

body_metrics = {"bmi": 24, "body_fat": 15, "waist_hip_ratio": 0.85, "shoulder_width_px": 200}
user_profile = {"name": "Test User", "age": 25, "gender": "Male", "goal": "Muscle gain", "activity_level": "Active", "equipment": ["Dumbbells", "Bodyweight"]}

print("Testing get_body_workout_recommendation with Groq...")
res = get_body_workout_recommendation(body_metrics, user_profile)
print(res)
print("Test completed.")
