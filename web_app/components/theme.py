# web_app/components/theme.py
import streamlit as st

def inject_css():
    """Global CSS: metric cards, mobile responsiveness, premium look, PWA meta."""
    st.markdown("""
    <!-- PWA & Android meta tags -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#1a1a2e">

    <style>
        /* ── Google Font ── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ── Sidebar styling ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        }
        [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

        /* ── Metric cards ── */
        [data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: #6C5CE7 !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            color: #636e72 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* ── Button ── */
        .stButton>button {
            background: linear-gradient(135deg, #6C5CE7, #a29bfe);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: transform 0.15s, box-shadow 0.15s;
            /* Touch-friendly minimum target size */
            min-height: 44px;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(108,92,231,.4);
        }
        /* Touch: no hover transform (avoids stuck state on Android) */
        @media (hover: none) {
            .stButton>button:hover {
                transform: none;
                box-shadow: none;
            }
            .stButton>button:active {
                transform: scale(0.97);
                box-shadow: 0 2px 10px rgba(108,92,231,.4);
            }
        }

        /* ── Tabs ── */
        [data-testid="stTabs"] [role="tab"] {
            font-weight: 600;
            color: #6C5CE7;
            min-height: 44px;
            display: flex;
            align-items: center;
        }
        [aria-selected="true"] {
            border-bottom: 2px solid #6C5CE7 !important;
        }

        /* ── Cards / containers ── */
        .stContainer, [data-testid="stVerticalBlock"] > div {
            border-radius: 10px;
        }

        /* ── Progress bar ── */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #6C5CE7, #00B894);
        }

        /* ── Input fields: bigger for touch ── */
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stSelectbox"] select {
            min-height: 44px;
            font-size: 16px; /* prevents iOS/Android zoom-on-focus */
        }

        /* ── Slider thumb enlarged ── */
        [data-testid="stSlider"] [role="slider"] {
            width: 28px !important;
            height: 28px !important;
        }

        /* ─────────────────────────────────────────
           MOBILE / ANDROID RESPONSIVE
        ───────────────────────────────────────── */
        @media (max-width: 768px) {
            /* Collapse columns to vertical on mobile */
            [data-testid="column"] {
                width: 100% !important;
                flex: 0 0 100% !important;
                max-width: 100% !important;
            }

            /* Hide sidebar — replaced by bottom nav */
            [data-testid="stSidebar"],
            [data-testid="collapsedControl"] {
                display: none !important;
            }

            /* Expand main content to full width */
            .main .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 0.75rem !important;
                /* Leave space for bottom nav */
                padding-bottom: 80px !important;
                max-width: 100% !important;
            }

            /* Full-width buttons */
            .stButton>button {
                width: 100%;
                padding: 0.85rem;
                font-size: 1rem;
                border-radius: 12px;
            }

            /* Slightly larger body text */
            html, body {
                font-size: 15px;
            }

            /* Metric cards bigger on mobile */
            [data-testid="stMetricValue"] {
                font-size: 1.4rem !important;
            }

            /* Make inputs easier to tap */
            [data-testid="stTextInput"] input,
            [data-testid="stNumberInput"] input {
                font-size: 16px !important;
                height: 48px !important;
            }

            /* Tabs scrollable on small screens */
            [data-testid="stTabs"] > div:first-child {
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch !important;
                scrollbar-width: none;
            }

            /* Larger tab touch targets */
            [data-testid="stTabs"] [role="tab"] {
                padding: 0.6rem 1rem !important;
                white-space: nowrap;
            }

            /* File uploader better on mobile */
            [data-testid="stFileUploader"] {
                padding: 1.5rem !important;
            }

            /* Camera / image display full-width */
            [data-testid="stImage"] img {
                width: 100% !important;
                height: auto !important;
                border-radius: 12px;
            }

            /* Dataframes scrollable horizontally */
            [data-testid="stDataFrame"] {
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch !important;
            }

            /* Plotly charts full width */
            .js-plotly-plot {
                width: 100% !important;
            }

            /* Title sizing */
            h1 { font-size: 1.5rem !important; }
            h2 { font-size: 1.25rem !important; }
            h3 { font-size: 1.1rem !important; }
        }

        /* ── Android Bottom Navigation Bar ── */
        #android-bottom-nav {
            display: none; /* hidden on desktop */
        }
        @media (max-width: 768px) {
            #android-bottom-nav {
                display: flex !important;
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                border-top: 1px solid rgba(108,92,231,0.3);
                z-index: 9999;
                height: 64px;
                align-items: center;
                justify-content: space-around;
                padding: 0 0.25rem;
                box-shadow: 0 -4px 20px rgba(0,0,0,0.4);
            }
            .nav-btn {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                flex: 1;
                height: 100%;
                color: #a0a0b0;
                font-size: 0.6rem;
                font-weight: 600;
                letter-spacing: 0.03em;
                cursor: pointer;
                text-decoration: none;
                transition: color 0.15s;
                -webkit-tap-highlight-color: transparent;
                padding: 0.4rem;
                gap: 2px;
                border: none;
                background: transparent;
            }
            .nav-btn .nav-icon {
                font-size: 1.4rem;
                line-height: 1;
            }
            .nav-btn.active {
                color: #a29bfe;
            }
            .nav-btn:active {
                color: #6C5CE7;
                transform: scale(0.92);
            }
        }
    </style>
    """, unsafe_allow_html=True)


def inject_bottom_nav(current_page: str):
    """Inject the sticky bottom navigation bar for Android.
    
    Only visible on screens ≤768px.
    Uses anchor links to Streamlit sidebar radio buttons via JS click injection.
    """
    pages = [
        ("🏠", "Dashboard", "🏠 Dashboard"),
        ("📸", "Scanner", "📸 Body Scanner"),
        ("🏋️", "Workout", "🏋️ AI Workout"),
        ("📈", "Progress", "📈 Progress Tracker"),
        ("👤", "Profile", "👤 Profile Setup"),
    ]
    
    nav_html = '<div id="android-bottom-nav">'
    for icon, label, page_key in pages:
        active_class = "active" if current_page == page_key else ""
        # Use JS to click the sidebar radio button that matches the page
        js = f"""
            var radios = window.parent.document.querySelectorAll('[data-testid="stRadio"] label');
            for(var r of radios){{
                if(r.innerText.trim().startsWith('{icon}')){{
                    r.click(); break;
                }}
            }}
        """
        js_encoded = js.replace('"', '&quot;').replace('\n', ' ')
        nav_html += f'''
        <button class="nav-btn {active_class}" onclick="{js_encoded}" title="{label}">
            <span class="nav-icon">{icon}</span>
            <span>{label}</span>
        </button>'''
    
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)
