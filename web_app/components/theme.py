# web_app/components/theme.py
import streamlit as st

def inject_css():
    """Global CSS: metric cards, mobile responsiveness, premium look."""
    st.markdown("""
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
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            font-weight: 600;
            transition: transform 0.15s, box-shadow 0.15s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(108,92,231,.4);
        }

        /* ── Tabs ── */
        [data-testid="stTabs"] [role="tab"] {
            font-weight: 600;
            color: #6C5CE7;
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

        /* ─────────────────────────────────────────
           MOBILE RESPONSIVE
        ───────────────────────────────────────── */
        @media (max-width: 768px) {
            /* Collapse columns to vertical on mobile */
            [data-testid="column"] {
                width: 100% !important;
                flex: 0 0 100% !important;
                max-width: 100% !important;
            }

            /* Sidebar hidden on mobile by default */
            [data-testid="stSidebar"] {
                display: none;
            }

            /* Larger tap targets */
            .stButton>button {
                width: 100%;
                padding: 0.75rem;
                font-size: 1rem;
            }

            /* Slightly larger body text */
            html, body {
                font-size: 14px;
            }

            /* Make metric cards bigger on mobile */
            [data-testid="stMetricValue"] {
                font-size: 1.3rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
