# app.py - Main Streamlit Application Entry Point
import streamlit as st
import datetime

# Import data banks and calculation routines from databanks.py
import databanks as db
from databanks import *

# Import modular views (Pattern B)
from views.about import render_page_about
from views.profile import render_page_profile
from views.numerology import render_page_numerology
from views.shani import render_page_shani
from views.live import render_page_live
from views.forecast import render_page_forecast
from views.monthly import render_page_monthly
from views.dasha import render_page_dasha
from views.mantra import render_page_mantra

# ==============================================================================
# EARLY LANGUAGE DETECTION & PAGE CONFIG
# ==============================================================================
init_lang = st.query_params.get("lang", "en")
app_page_title = "✨ नवतारा पल्स" if init_lang == "hi" else "✨ Navtara Pulse"

st.set_page_config(
    page_title=app_page_title,
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Helper function to inject clean HTML safely
def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

# Mobile-optimized CSS styling
render_html("""
<style>
    html { font-size: 16px; }
    @media (max-width: 640px) {
        html { font-size: 15.5px; }
        .block-container {
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
            padding-top: 1rem !important;
            padding-bottom: 5.5rem !important;
        }
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 5.5rem;
        padding-left: 0.9rem;
        padding-right: 0.9rem;
        max-width: 780px;
    }
    div[data-baseweb="select"] {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }
    .auth-hero-box {
        background: linear-gradient(135deg, #fdfbf7 0%, #fffbeb 100%);
        border: 1.5px solid #fde68a;
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 2px 10px rgba(245, 158, 11, 0.08);
    }
    .light-card-profile {
        background: #ffffff;
        border: 1.5px solid #fed7aa;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 3px 12px rgba(249, 115, 22, 0.06);
    }
    .light-card-num {
        background: #ffffff;
        border: 1.5px solid #bbf7d0;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 3px 12px rgba(16, 185, 129, 0.06);
    }
    .light-card-shani {
        background: #ffffff;
        border: 1.5px solid #ddd6fe;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 3px 12px rgba(139, 92, 246, 0.06);
    }
    .light-card-live {
        background: #ffffff;
        border: 1.5px solid #bae6fd;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 3px 12px rgba(14, 165, 233, 0.06);
    }
    .stButton button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        padding: 8px 6px !important;
        transition: all 0.2s ease-in-out;
    }
</style>
""")

TRANSLATIONS = {
    "en": {
        "app_title": "✨ Navtara Pulse",
        "btn_about": "✨ About App",
        "btn_user_profile": "👤 User Profile",
        "btn_numerology": "🔢 Numerology",
        "btn_shani": "🪐 Shani & Sade Sati",
        "btn_live": "⚡ Daily Horoscope",
        "btn_forecast": "🗓️ Weekly Horoscope",
        "btn_monthly": "📅 Monthly Horoscope",
        "btn_dasha": "⏳ Dasha Timeline",
        "btn_mantra": "📿 Mantra Sadhana",
    },
    "hi": {
        "app_title": "✨ नवतारा पल्स (Navtara Pulse)",
        "btn_about": "✨ ऐप परिचय",
        "btn_user_profile": "👤 यूज़र प्रोफाइल",
        "btn_numerology": "🔢 अंकशास्त्र",
        "btn_shani": "🪐 शनि एवं साढ़े साती",
        "btn_live": "⚡ आज का फल",
        "btn_forecast": "🗓️ 7 दिवसीय फल",
        "btn_monthly": "📅 मासिक राशिफल",
        "btn_dasha": "⏳ दशा समयरेखा",
        "btn_mantra": "📿 मंत्र साधना",
    }
}

def t(key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))

client_params = st.query_params

if "user_profile" not in st.session_state:
    if client_params.get("name") and client_params.get("dob") and client_params.get("tob"):
        st.session_state.user_profile = {
            "name": client_params.get("name", ""),
            "dob": client_params.get("dob", ""),
            "tob": client_params.get("tob", ""),
            "city": client_params.get("city", ""),
            "lat": float(client_params.get("lat", 28.6139)),
            "lon": float(client_params.get("lon", 77.2090)),
            "lang": client_params.get("lang", "en")
        }
    else:
        st.session_state.user_profile = {
            "name": "",
            "dob": "",
            "tob": "",
            "city": "",
            "lat": 28.6139,
            "lon": 77.2090,
            "lang": "en"
        }

if "current_page" not in st.session_state:
    st.session_state.current_page = "about"

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "selected_transit_idx" not in st.session_state:
    st.session_state.selected_transit_idx = 0

if "japa_count" not in st.session_state:
    st.session_state.japa_count = 0

if "mala_rounds" not in st.session_state:
    st.session_state.mala_rounds = 0

prof = st.session_state.user_profile
current_lang = prof.get("lang", "en")

# Universal Centered Header with your preferred Catchy Tagline
app_subtitle_text = "कृत्रिम बुद्धि (AI) से परे, आचार्यों के अनुभव की सटीकता" if current_lang == "hi" else "Beyond Artificial Intelligence, the precision of acharyas' experience"

render_html(f"""
    <div style='text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; margin-top:0.2rem; margin-bottom:0.75rem;'>
        <div style='background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); width:76px; height:76px; border-radius:26px; display:flex; align-items:center; justify-content:center; font-size:2.45rem; box-shadow:0 8px 28px rgba(245,158,11,0.38); margin-bottom:10px;'>
            ✨
        </div>
        <h1 style='margin:0; font-size:2.15rem; color:#0f172a; font-weight:900; line-height:1.2; text-align:center;'>{t('app_title', current_lang)}</h1>
        <div style='font-size:0.95rem; color:#b45309; font-weight:800; margin-top:6px; text-align:center; background:#fffbeb; padding:4px 14px; border-radius:20px; border:1px solid #fde68a;'>{app_subtitle_text}</div>
    </div>
""")

# Top Navigation Dock (3x3 Grid) - Fully Localized Dynamic Titles
nav_r1_c1, nav_r1_c2, nav_r1_c3 = st.columns(3)
with nav_r1_c1:
    p_type = "primary" if st.session_state.current_page == "about" else "secondary"
    if st.button(t("btn_about", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "about"
        st.rerun()
with nav_r1_c2:
    p_type = "primary" if st.session_state.current_page == "profile" else "secondary"
    if st.button(t("btn_user_profile", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "profile"
        st.rerun()
with nav_r1_c3:
    p_type = "primary" if st.session_state.current_page == "numerology" else "secondary"
    if st.button(t("btn_numerology", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "numerology"
        st.rerun()

nav_r2_c1, nav_r2_c2, nav_r2_c3 = st.columns(3)
with nav_r2_c1:
    p_type = "primary" if st.session_state.current_page == "shani" else "secondary"
    if st.button(t("btn_shani", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "shani"
        st.rerun()
with nav_r2_c2:
    p_type = "primary" if st.session_state.current_page == "live" else "secondary"
    if st.button(t("btn_live", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "live"
        st.rerun()
with nav_r2_c3:
    p_type = "primary" if st.session_state.current_page == "forecast" else "secondary"
    if st.button(t("btn_forecast", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "forecast"
        st.rerun()

nav_r3_c1, nav_r3_c2, nav_r3_c3 = st.columns(3)
with nav_r3_c1:
    p_type = "primary" if st.session_state.current_page == "monthly" else "secondary"
    if st.button(t("btn_monthly", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "monthly"
        st.rerun()
with nav_r3_c2:
    p_type = "primary" if st.session_state.current_page == "dasha" else "secondary"
    if st.button(t("btn_dasha", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "dasha"
        st.rerun()
with nav_r3_c3:
    p_type = "primary" if st.session_state.current_page == "mantra" else "secondary"
    if st.button(t("btn_mantra", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "mantra"
        st.rerun()
        
render_html("<hr style='margin:10px 0 16px 0; border:none; border-top:1.5px solid #e2e8f0;'>")

has_valid_profile = bool(prof.get("name") and prof.get("dob") and prof.get("tob"))

if has_valid_profile:
    try:
        dob_parsed = datetime.datetime.strptime(prof["dob"], "%Y-%m-%d").date()
    except Exception:
        dob_parsed = datetime.date(1990, 1, 1)

    try:
        tob_parsed = datetime.datetime.strptime(prof["tob"], "%H:%M").time()
    except Exception:
        tob_parsed = datetime.time(12, 0)

    u_lat = float(prof.get("lat", 28.6139))
    u_lon = float(prof.get("lon", 77.2090))
    chart_info = calculate_birth_chart(dob_parsed, tob_parsed, u_lat, u_lon)
    mulank, bhagyank, namank = calculate_numerology(dob_parsed, prof.get("name", "User"))

    SATURN_TRANSIT_RASHI_IDX = 11  # Saturn in Pisces (Meena)
    shani_paya_data = calculate_shani_paya(chart_info["moon_rashi_idx"], SATURN_TRANSIT_RASHI_IDX)
    shani_sadesati_data = calculate_shani_sadesati_dhaiya(chart_info["moon_rashi_idx"], SATURN_TRANSIT_RASHI_IDX)

    st.session_state["has_valid_profile"] = True
    st.session_state["chart_info"] = chart_info
    st.session_state["dob_parsed"] = dob_parsed
    st.session_state["tob_parsed"] = tob_parsed
    st.session_state["mulank"] = mulank
    st.session_state["bhagyank"] = bhagyank
    st.session_state["namank"] = namank
    st.session_state["shani_paya_data"] = shani_paya_data
    st.session_state["shani_sadesati_data"] = shani_sadesati_data
else:
    dob_parsed, tob_parsed, chart_info = None, None, None
    mulank, bhagyank, namank = None, None, None
    shani_paya_data, shani_sadesati_data = None, None
    u_lat, u_lon = 28.6139, 77.2090
    st.session_state["has_valid_profile"] = False

# ==============================================================================
# ROUTER DISPATCHER
# ==============================================================================
PAGES = {
    "about": render_page_about,
    "profile": render_page_profile,
    "numerology": render_page_numerology,
    "shani": render_page_shani,
    "live": render_page_live,
    "forecast": render_page_forecast,
    "monthly": render_page_monthly,
    "dasha": render_page_dasha,
    "mantra": render_page_mantra,
}

active_page_func = PAGES.get(st.session_state.current_page, render_page_about)
active_page_func()
