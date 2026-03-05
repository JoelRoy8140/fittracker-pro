# web_app/components/workout_planner.py
"""
Full-featured Workout Planner UI.
Supports split selection (Full Body / PPL / Upper-Lower / Bro Split),
displays per-day workout cards with YouTube video links or exercise images.
"""

import streamlit as st
import json
from web_app.workout_generator import generate_workout_plan, SPLIT_TYPES
from web_app.youtube_api import get_youtube_video_url, get_exercise_image
from web_app.database import save_workout_plan, get_latest_user, get_workout_plans


def workout_planner_component():
    """Main entry called from app.py."""
    user = st.session_state.get("user") or get_latest_user()
    if not user:
        st.warning("Please complete your profile before generating a workout.")
        return

    st.subheader("🏋️‍♂️ AI Workout Plan Generator")

    # ── Check for Auto-Generate from Scanner ─────────────────────────────────
    auto_generate = False
    body_metrics = None
    if st.session_state.get("generate_from_scan"):
        auto_generate = True
        body_metrics = st.session_state.get("last_body_scan")
        # Consume the flag so it doesn't loop
        del st.session_state["generate_from_scan"]

    # ── Controls ──────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        split_type = st.selectbox(
            "Workout Split",
            SPLIT_TYPES,
            help="How to organise muscle groups across the week"
        )
    with col2:
        duration = st.slider("Session Duration (min)", 15, 120, 45, step=5)
    with col3:
        intensity = st.select_slider(
            "Intensity",
            options=["Beginner", "Intermediate", "Advanced"],
            value="Intermediate"
        )

    generate_clicked = st.button("🚀 Generate My Weekly Plan", use_container_width=True)

    if generate_clicked or auto_generate:
        with st.spinner("Building your personalised plan…"):
            if auto_generate and body_metrics:
                st.info("🧠 Using live body scan data for hyper-personalised hyper-generation...")
                from web_app.ai_recommendations import get_body_workout_recommendation
                plan = get_body_workout_recommendation(body_metrics, user)
                # Fallback to general if AI fails totally
                if not plan or not plan.get("week"):
                    plan = generate_workout_plan(user, duration_minutes=duration, split_type=split_type)
            else:
                # Default behavior
                plan = generate_workout_plan(
                    user,
                    duration_minutes=duration,
                    split_type=split_type
                )
                
            st.session_state["last_plan"] = plan

            try:
                user_id = user.get("id") or 1
                save_workout_plan(user_id, plan)
            except Exception:
                pass

    # ── Display plan stored in session ────────────────────────────────────────
    plan = st.session_state.get("last_plan")
    if plan:
        _render_plan(plan)

    # ── Past plans accordion ──────────────────────────────────────────────────
    with st.expander("📂 Previous Plans"):
        user_id = (st.session_state.get("user") or {}).get("id") or 1
        rows = get_workout_plans(user_id)
        if not rows:
            st.info("No saved plans yet.")
        for row in rows[:5]:
            try:
                p = json.loads(row[2])
                with st.container():
                    st.markdown(f"**{p.get('split','Plan')}** — {p.get('date','')}")
                    st.caption(f"{p.get('duration_minutes', '?')} min | {len(p.get('exercises', []))} exercises")
                    st.divider()
            except Exception:
                pass


# ── Internal helpers ──────────────────────────────────────────────────────────

def _render_plan(plan: dict):
    st.success(f"✅ **{plan['split']} Plan** — {plan['date']}")

    week = plan.get("week", {})
    if not week:
        # Legacy flat format
        _render_exercise_list(plan.get("exercises", []))
        return

    tabs = st.tabs(list(week.keys()))
    for tab, (day_name, day_data) in zip(tabs, week.items()):
        with tab:
            st.markdown(f"**Focus:** {day_data['focus']}")
            st.markdown(f"**Muscle Groups:** {', '.join(day_data.get('muscle_groups', []))}")
            st.divider()
            _render_exercise_list(day_data.get("exercises", []))


def _render_exercise_list(exercises: list):
    if not exercises:
        st.info("No exercises for this day.")
        return

    from web_app.exercise_api import get_gif_url
    from web_app.youtube_api import get_youtube_video_url, get_exercise_image

    for i, ex in enumerate(exercises, 1):
        with st.container():
            col_name, col_sets, col_reps, col_rest, col_media = st.columns([3, 1, 1, 1, 2])
            with col_name:
                st.markdown(f"**{i}. {ex['name']}**")
                if ex.get("required_equipment"):
                    st.caption("🏋️ " + ", ".join(ex["required_equipment"]))
                # Show step-by-step instructions if present (from ExerciseDB or AI)
                if ex.get("instructions"):
                    with st.expander("📋 Instructions"):
                        for j, step in enumerate(ex["instructions"][:5], 1):
                            st.markdown(f"{j}. {step}")
                if ex.get("why"):
                    st.caption(f"💡 {ex['why']}")
            with col_sets:
                st.metric("Sets", ex.get("sets", "—"))
            with col_reps:
                st.metric("Reps", str(ex.get("reps", "—")))
            with col_rest:
                st.metric("Rest", f"{ex.get('rest', 60)}s")
            with col_media:
                # Priority: ExerciseDB GIF > YouTube link > DuckDuckGo image
                gif = ex.get("gif_url") or get_gif_url(ex["name"])
                if gif:
                    st.image(gif, width=160, caption="Exercise Demo")
                else:
                    video = get_youtube_video_url(ex["name"])
                    if video:
                        st.markdown(f"[📺 Watch Tutorial]({video})")
                    else:
                        img = get_exercise_image(ex["name"])
                        if img:
                            st.image(img, width=140)
                        else:
                            st.caption("No media found")
            st.divider()

