<div align="center">

<img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit&logoColor=white" />
<img src="https://img.shields.io/badge/MediaPipe-0.10.9-green?logo=google&logoColor=white" />
<img src="https://img.shields.io/badge/Gemini_AI-Integrated-purple?logo=google&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-yellow" />

# 💪 FitTracker Pro

**An AI-powered fitness tracking web application** featuring real-time body & face fat scanning, AI-personalised workout plans, 1300+ exercise database integration, PDF reports, and user authentication.

[🚀 Features](#-features) • [📸 Screenshots](#-screenshots) • [⚙️ Setup](#%EF%B8%8F-setup) • [🔧 Configuration](#-configuration) • [📁 Project Structure](#-project-structure)

</div>

---

## 🚀 Features

### 🔐 User Authentication

- Secure login & registration with **bcrypt** password hashing
- Session-based routing — all pages protected behind login
- Per-user data isolation

### 📸 AI Body Scanner

- **Real-time MediaPipe Pose estimation** from webcam
- Calculates: **BMI**, **Body Fat %**, **Shoulder Width**, **Waist-Hip Ratio**
- After scan → instantly generates a **personalised workout plan** (via Gemini AI or rule-based fallback)

### 😊 Face Fat Scanner _(unique feature)_

- **MediaPipe Face Mesh** (468 facial landmarks)
- Calculates: Cheek/Jaw ratio, Face Width-to-Height ratio → **0–100 Face Fat Score**
- After scan → generates a **tailored facial exercise plan** with step-by-step instructions
- Categories: Very Lean → Lean → Average → Above Average → High

### 🏋️ AI Workout Plan Generator

- **4 Split Types:** Full Body, Push/Pull/Legs, Upper/Lower, Bro Split
- Choose session duration (15–120 min) and intensity (Beginner → Advanced)
- Equipment-aware filtering
- Per-day tabbed layout with exercise cards

### 📺 Exercise Media — 3-layer fallback

1. **ExerciseDB** (RapidAPI) — 1300+ exercises with animated GIFs
2. **YouTube** tutorial links (static + API)
3. **DuckDuckGo** real-time image search (no key needed)

### 🤖 Google Gemini AI Integration

- Body scan metrics → fully custom workout plan with AI reasoning per exercise
- Face scan metrics → personalised facial exercises with targeted justifications
- Graceful rule-based fallback when no API key is set

### 📄 PDF Export

- Download your **Workout Plan** or **Progress Report** as a styled A4 PDF
- Generated with ReportLab — coloured headers, per-day exercise tables

### 📈 Progress Tracker

- BMI & Body Fat % history charts over time
- Measurement comparison table
- Export to PDF

### 📱 Mobile Responsive

- CSS media queries at 768px — stacked columns, hidden sidebar
- Inter font, gradient sidebar, animated buttons

---

## 📸 Screenshots

> After cloning and running the app, you will see:
>
> - **Login/Register page** on first visit
> - **Dashboard** with your latest metrics
> - **Body Scanner** with live AI recommendations after each scan
> - **Face Fat Scanner** with facial exercise plan
> - **Workout Generator** with split selection and exercise GIFs

---

## ⚙️ Setup

### Prerequisites

- Python 3.11+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/fittracker-pro.git
cd fittracker-pro
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run web_app/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔧 Configuration

All configuration is via **environment variables** — no API key is required to run the app, everything falls back gracefully.

| Variable          | Description                                | Where to get it                                                                                            | Free?        |
| ----------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------ |
| `GEMINI_API_KEY`  | Google Gemini AI for smart recommendations | [aistudio.google.com/apikey](https://aistudio.google.com/apikey)                                           | ✅ Yes       |
| `RAPIDAPI_KEY`    | ExerciseDB — 1300+ exercises with GIFs     | [rapidapi.com/exercisedb](https://rapidapi.com/justin-thewebsite-justin-thewebsite-default/api/exercisedb) | ✅ Free tier |
| `YOUTUBE_API_KEY` | YouTube Data API for tutorial search       | [console.cloud.google.com](https://console.cloud.google.com)                                               | ✅ Free tier |

### Setting environment variables

**Windows (PowerShell):**

```powershell
$env:GEMINI_API_KEY = "your-key-here"
$env:RAPIDAPI_KEY   = "your-key-here"
streamlit run web_app/app.py
```

**macOS/Linux:**

```bash
export GEMINI_API_KEY="your-key-here"
export RAPIDAPI_KEY="your-key-here"
streamlit run web_app/app.py
```

### Without any API keys

The app runs fully in offline mode:

- Rule-based AI recommendations using body metrics
- Local exercise library (60+ exercises across all muscle groups)
- Static YouTube links for common exercises
- DuckDuckGo image fallback for exercise demos

---

## 📁 Project Structure

```
fitness-tracker/
├── web_app/
│   ├── app.py                    # Main Streamlit application & routing
│   ├── database.py               # SQLite ORM (users, measurements, plans)
│   ├── workout_generator.py      # Split-based workout plan generator
│   ├── exercise_api.py           # ExerciseDB → Wger → local fallback
│   ├── ai_recommendations.py     # Gemini AI for body + face recommendations
│   ├── youtube_api.py            # YouTube + DuckDuckGo media fetcher
│   └── components/
│       ├── auth.py               # Login / Register UI
│       ├── profile_setup.py      # User profile form
│       ├── scanner_integration.py # Body + Face Fat scanner UI
│       ├── workout_planner.py    # Workout planner UI with splits
│       ├── progress_tracker.py   # Charts & history UI
│       ├── reporting.py          # PDF generation (ReportLab)
│       └── theme.py              # Global CSS + mobile responsiveness
├── shared/
│   ├── body_measurements.py      # MediaPipe Pose scanner class
│   ├── calculations.py           # BMI, body fat formulae
│   └── utils.py                  # Resource path helper, JSON utils
├── data/
│   ├── workout_templates.json    # General workout templates
│   ├── workout_splits.json       # Exercises by muscle for all 4 splits
│   └── facial_exercises.json     # Curated facial exercise library
└── requirements.txt
```

---

## 📦 Requirements

Key packages used:

| Package               | Purpose                             |
| --------------------- | ----------------------------------- |
| `streamlit`           | Web UI framework                    |
| `mediapipe==0.10.9`   | Pose & Face Mesh landmark detection |
| `opencv-python`       | Image processing                    |
| `Pillow`              | Image handling                      |
| `bcrypt`              | Secure password hashing             |
| `google-generativeai` | Gemini AI integration               |
| `reportlab`           | PDF generation                      |
| `requests`            | HTTP API calls                      |
| `plotly`              | Interactive progress charts         |
| `pandas`              | Data manipulation                   |

Install all with: `pip install -r requirements.txt`

---

## 🧠 How the AI Works

### Body-Scan Workout Recommendation

1. Body scanner extracts **BMI**, **Body Fat %** and **Shoulder-Hip Ratio**
2. These metrics are sent to **Gemini 1.5 Flash** with a structured prompt
3. Gemini returns a JSON workout plan with per-exercise reasoning
4. ExerciseDB fetches animated GIFs for each exercise
5. _Fallback:_ Rule-based logic selects the optimal split (PPL for normal BMI, Full Body for high BMI, etc.)

### Face-Scan Facial Exercise Recommendation

1. Face Mesh extracts **468 landmarks** → calculates cheek/jaw ratio and face width-to-height ratio
2. A **0–100 Face Fat Score** is computed from these ratios
3. Gemini generates a personalised **6-exercise facial routine** targeting the specific concern areas
4. _Fallback:_ Exercises from `facial_exercises.json` are filtered by fat score range

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create your branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'Add some feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Made with ❤️ using Python, Streamlit & MediaPipe
</div>
