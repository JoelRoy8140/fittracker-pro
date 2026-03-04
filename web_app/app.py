# web_app/app.py
"""
FitTracker Pro – main Streamlit application.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="FitTracker Pro",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from web_app.database import (
    init_db, get_latest_user, add_measurement, get_measurements,
    save_workout_plan, get_user_by_username,
)
from web_app.components.profile_setup    import profile_setup_component
from web_app.components.scanner_integration import body_scanner_component
from web_app.components.workout_planner  import workout_planner_component
from web_app.components.progress_tracker import progress_tracker_component
from web_app.components.theme            import inject_css
from web_app.components.auth             import auth_component
from web_app.components.reporting        import generate_workout_pdf, generate_progress_pdf

# ── DB init (runs once per process) ───────────────────────────────────────────
init_db()
inject_css()


# ─────────────────────────────────────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────────────────────────────────────

def dashboard_page():
    user = st.session_state.get("user") or get_latest_user()
    st.title("🎯 Fitness Dashboard")
    if not user:
        st.info("⚠️ No profile found – go to **Profile Setup** first.")
        return

    st.success(f"Welcome back, **{user.get('name', 'Athlete')}**! 🎉")
    measurements = get_measurements(user.get("id", 1))
    latest = measurements[0] if measurements else None

    c1, c2, c3 = st.columns(3)
    c1.metric("BMI",       f"{latest[3]:.1f}"  if latest else "—")
    c2.metric("Body Fat",  f"{latest[4]:.1f} %" if latest else "—")
    c3.metric("Weight",    f"{latest[5]:.1f} kg" if latest else "—")

    if measurements:
        try:
            df = pd.DataFrame(measurements,
                              columns=["id","user_id","date","bmi","body_fat","weight","measurements"])
            df["Date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            st.subheader("📋 Recent Measurements")
            st.dataframe(df[["Date","bmi","body_fat","weight"]]
                         .rename(columns={"bmi":"BMI","body_fat":"Body Fat %","weight":"Weight kg"}),
                         use_container_width=True)

            # PDF export
            pdf_bytes = generate_progress_pdf(user, measurements)
            st.download_button(
                "📥 Export Progress as PDF",
                data=pdf_bytes,
                file_name=f"progress_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.warning(f"Could not render measurements table: {e}")
    else:
        st.info("No measurements yet – try the **Body Scanner**.")


def profile_page():
    st.title("👤 Profile Setup")
    profile_setup_component()


def scanner_page():
    st.title("📸 Body & Face Scanner")
    user = st.session_state.get("user") or get_latest_user()
    if not user:
        st.warning("Create a profile first.")
        return
    body_scanner_component(user)


def workout_page():
    st.title("🏋️‍♂️ AI Workout Generator")
    workout_planner_component()

    # PDF download for the last generated plan
    plan = st.session_state.get("last_plan")
    if plan:
        user = st.session_state.get("user") or get_latest_user() or {}
        pdf_bytes = generate_workout_pdf(user, plan)
        st.download_button(
            "📥 Download Plan as PDF",
            data=pdf_bytes,
            file_name=f"workout_plan_{plan.get('date','today')}.pdf",
            mime="application/pdf",
        )


def progress_page():
    st.title("📈 Progress Tracker")
    progress_tracker_component()


# ─────────────────────────────────────────────────────────────────────────────
# ROUTING
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # ── Auth gate ─────────────────────────────────────────────────────────────
    if "user" not in st.session_state:
        auth_component()
        return

    user = st.session_state["user"]

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"## 💪 FitTracker Pro")
        st.markdown(f"**{user.get('name', 'Athlete')}**")
        st.caption(f"Goal: {user.get('goal','—')}")
        st.divider()

        page = st.radio("Navigate", [
            "🏠 Dashboard", "👤 Profile Setup",
            "📸 Body Scanner", "🏋️ AI Workout",
            "📈 Progress Tracker"
        ])

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # ── Dispatch ──────────────────────────────────────────────────────────────
    dispatch = {
        "🏠 Dashboard":     dashboard_page,
        "👤 Profile Setup": profile_page,
        "📸 Body Scanner":  scanner_page,
        "🏋️ AI Workout":    workout_page,
        "📈 Progress Tracker": progress_page,
    }
    dispatch[page]()


main()
