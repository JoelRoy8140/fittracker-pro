# web_app/components/scanner_integration.py
"""
Dual-tab scanner:
 • Body Scan  — MediaPipe Pose + AI-powered workout recommendations
 • Face Scan  — MediaPipe Face Mesh + AI-powered facial exercises
"""

import streamlit as st
import cv2, numpy as np
from PIL import Image


# ─── Lazy MediaPipe loaders ───────────────────────────────────────────────────

def _get_pose():
    import mediapipe as mp
    return (
        mp.solutions.pose.Pose(static_image_mode=True, model_complexity=1,
                               min_detection_confidence=0.5),
        mp.solutions.drawing_utils,
        mp.solutions.pose,
    )

def _get_face_mesh():
    import mediapipe as mp
    return (
        mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1,
                                        refine_landmarks=True,
                                        min_detection_confidence=0.5),
        mp.solutions.drawing_utils,
        mp.solutions.drawing_styles,
        mp.solutions.face_mesh,
    )


# ─── Analysis functions ───────────────────────────────────────────────────────

def _analyse_body(frame_rgb, user_data):
    pose, drawing, mp_pose = _get_pose()
    results = pose.process(frame_rgb)
    pose.close()
    if not results.pose_landmarks:
        return None
    lm = results.pose_landmarks.landmark
    h, w = frame_rgb.shape[:2]
    def px(idx):
        p = lm[idx]; return int(p.x*w), int(p.y*h)
    l_sh, r_sh = px(mp_pose.PoseLandmark.LEFT_SHOULDER), px(mp_pose.PoseLandmark.RIGHT_SHOULDER)
    l_hi, r_hi = px(mp_pose.PoseLandmark.LEFT_HIP),      px(mp_pose.PoseLandmark.RIGHT_HIP)
    sh_w = abs(l_sh[0]-r_sh[0])
    hi_w = abs(l_hi[0]-r_hi[0])
    import mediapipe as mp
    ann = frame_rgb.copy()
    mp.solutions.drawing_utils.draw_landmarks(ann, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    wt = user_data.get("weight") or 70
    ht = user_data.get("height") or 170
    age = user_data.get("age") or 25
    gender = (user_data.get("gender") or "Male").strip().capitalize()
    bmi = round(wt / ((ht/100)**2), 1)
    bf  = round((1.20*bmi)+(0.23*age)-(10.8 if gender=="Male" else 0)-5.4, 1)
    return {"annotated_image": ann, "bmi": bmi,
            "body_fat": max(0, bf), "shoulder_width_px": sh_w,
            "hip_width_px": hi_w,
            "waist_hip_ratio": round(sh_w/max(hi_w,1), 2)}


def _analyse_face(frame_rgb):
    face_mesh, drawing, styles, mp_face = _get_face_mesh()
    results = face_mesh.process(frame_rgb)
    face_mesh.close()
    if not results.multi_face_landmarks:
        return None
    h, w = frame_rgb.shape[:2]
    lm = results.multi_face_landmarks[0].landmark
    def xy(i): p=lm[i]; return int(p.x*w), int(p.y*h)
    r_ch, l_ch = xy(234), xy(454)
    r_jw, l_jw = xy(172), xy(397)
    top, chin  = xy(10),  xy(152)
    ch_w = abs(r_ch[0]-l_ch[0])
    jw_w = abs(r_jw[0]-l_jw[0])
    fh   = abs(top[1]-chin[1])
    wtoh = round(ch_w / max(fh, 1), 3)
    ctoj = round(ch_w / max(jw_w, 1), 3)
    score = max(0, min(100, int((wtoh-0.6)/0.5*100)))
    cats  = [(20,"Very Lean"),(40,"Lean"),(60,"Average"),(80,"Above Average")]
    cat   = next((c for s,c in cats if score<s), "High")
    import mediapipe as mp
    ann = frame_rgb.copy()
    for fl in results.multi_face_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(
            ann, fl, mp.solutions.face_mesh.FACEMESH_TESSELATION,
            None, mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style())
        mp.solutions.drawing_utils.draw_landmarks(
            ann, fl, mp.solutions.face_mesh.FACEMESH_CONTOURS,
            None, mp.solutions.drawing_styles.get_default_face_mesh_contours_style())
    return {"annotated_image": ann, "cheek_width_px": ch_w,
            "jaw_width_px": jw_w, "face_height_px": fh,
            "cheek_to_jaw_ratio": ctoj, "face_width_to_height": wtoh,
            "face_fat_score": score, "face_fat_category": cat}


# ─── UI helpers ───────────────────────────────────────────────────────────────

def _render_body_ai(body_result, user_data):
    """Show AI-generated workout plan from scan metrics."""
    st.markdown("---")
    st.subheader("🤖 AI Workout Recommendation")
    with st.spinner("Generating personalised plan from your scan…"):
        from web_app.ai_recommendations import get_body_workout_recommendation
        plan = get_body_workout_recommendation(body_result, user_data)

    badge = "🟢 AI" if plan.get("source") == "gemini" else "⚡ Smart Plan"
    st.info(f"{badge} — {plan.get('ai_reasoning', '')}")

    if plan.get("nutrition_tip"):
        st.success(f"🥗 **Nutrition tip:** {plan['nutrition_tip']}")
    if plan.get("weekly_cardio"):
        st.info(f"🏃 **Cardio:** {plan['weekly_cardio']}")

    week = plan.get("week", {})
    if week:
        tabs = st.tabs(list(week.keys()))
        for tab, (day, data) in zip(tabs, week.items()):
            with tab:
                st.caption(data.get("focus", ""))
                for ex in data.get("exercises", []):
                    col1, col2 = st.columns([3,1])
                    with col1:
                        st.markdown(f"**{ex.get('name','—')}**")
                        if ex.get("why"):
                            st.caption(f"💡 {ex['why']}")
                    with col2:
                        st.metric("Sets×Reps", f"{ex.get('sets',3)}×{ex.get('reps','12')}")
                    # Try to show GIF
                    from web_app.exercise_api import get_gif_url
                    gif = get_gif_url(ex.get("name",""))
                    if gif:
                        st.image(gif, width=200)
                    st.divider()

    # Save to session for PDF export
    if week:
        st.session_state["last_plan"] = plan

    st.markdown("---")
    if st.button("🚀 Build Custom AI Plan from Scan", key="btn_body_plan", use_container_width=True):
        st.session_state["nav_route"] = "🏋️ AI Workout"
        st.session_state["generate_from_scan"] = True
        st.rerun()


def _render_facial_ai(face_result):
    """Show AI-generated facial exercise plan from face scan metrics."""
    st.markdown("---")
    st.subheader("🤖 AI Facial Exercise Plan")
    with st.spinner("Generating facial exercise plan…"):
        from web_app.ai_recommendations import get_facial_exercise_recommendation
        plan = get_facial_exercise_recommendation(face_result)

    badge = "🟢 AI" if plan.get("source") == "gemini" else "⚡ Smart Plan"
    st.info(f"{badge} — {plan.get('ai_reasoning', '')}")
    st.markdown(f"**Primary concern:** {plan.get('primary_concern','')}")
    st.caption(f"📅 {plan.get('daily_routine','')}")
    st.caption(f"⏳ {plan.get('expected_results','')}")

    exercises = plan.get("exercises", [])
    for i, ex in enumerate(exercises, 1):
        with st.expander(f"{i}. {ex.get('name', ex.get('id','Exercise'))} — {ex.get('target', '')}"):
            col1, col2 = st.columns([1,2])
            with col1:
                st.metric("Reps", ex.get("reps","—"))
                st.metric("Duration", ex.get("duration","—"))
            with col2:
                steps = ex.get("instructions", [])
                for j, step in enumerate(steps, 1):
                    st.markdown(f"{j}. {step}")
            if ex.get("why") or ex.get("benefits"):
                st.success(f"✅ {ex.get('why') or ex.get('benefits','')}")

    tips = plan.get("lifestyle_tips", [])
    if tips:
        st.markdown("**💡 Lifestyle Tips:**")
        for t in tips:
            st.markdown(f"- {t}")

    st.markdown("---")
    if st.button("🚀 Build Custom AI Plan from Scan", key="btn_face_plan", use_container_width=True):
        st.session_state["nav_route"] = "🏋️ AI Workout"
        st.session_state["generate_from_scan"] = True
        st.rerun()



# ─── Main public component ────────────────────────────────────────────────────

def body_scanner_component(user_data: dict):
    tab_body, tab_face = st.tabs(["🏋️ Body Scan", "😊 Face Fat Scan"])

    # ── BODY TAB ─────────────────────────────────────────────────────────────
    with tab_body:
        st.info("📸 Stand 2–3 m away so your whole body is visible.")
        cam = st.camera_input("Capture for Body Scan", key="body_cam")
        if cam:
            img = Image.open(cam).convert("RGB")
            frame_rgb = np.array(img)
            with st.spinner("Analysing body posture…"):
                result = _analyse_body(frame_rgb, user_data)
            if result:
                st.image(result["annotated_image"], caption="Pose Detected", use_column_width=True)
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("BMI",              f"{result['bmi']:.1f}")
                c2.metric("Body Fat %",       f"{result['body_fat']:.1f}%")
                c3.metric("Shoulder Width",   f"{result['shoulder_width_px']}px")
                c4.metric("Waist-Hip Ratio",  result["waist_hip_ratio"])
                st.session_state["last_body_scan"] = result
                # AI recommendations
                _render_body_ai(result, user_data)
            else:
                st.error("❌ No full body detected. Make sure your entire body is in frame.")

    # ── FACE TAB ─────────────────────────────────────────────────────────────
    with tab_face:
        st.info("📸 Look straight at the camera in good lighting.")
        cam_f = st.camera_input("Capture for Face Scan", key="face_cam")
        if cam_f:
            img = Image.open(cam_f).convert("RGB")
            frame_rgb = np.array(img)
            with st.spinner("Analysing facial structure…"):
                result = _analyse_face(frame_rgb)
            if result:
                st.image(result["annotated_image"], caption="Face Mesh Detected", use_column_width=True)
                c1,c2,c3 = st.columns(3)
                c1.metric("Face Fat Score",  f"{result['face_fat_score']}/100")
                c2.metric("Category",         result["face_fat_category"])
                c3.metric("Cheek/Jaw Ratio",  result["cheek_to_jaw_ratio"])
                st.session_state["last_face_scan"] = result
                # AI facial exercises
                _render_facial_ai(result)
            else:
                st.error("❌ No face detected. Ensure face is well-lit and clearly visible.")
