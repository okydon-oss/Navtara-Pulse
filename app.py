import os
import json
import random
import datetime
import streamlit as st

# Dependency checking for Swiss Ephemeris
try:
    import swisseph as swe
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False
    st.error("🚨 **Missing Library Error:** `pyswisseph` is not installed in your environment.")
    st.warning("⚡ Add `pyswisseph` to your `requirements.txt` file in your repository.")
    st.info("If running locally on your computer, run:")
    st.code("pip install pyswisseph requests streamlit", language="bash")
    st.stop()

# Streamlit Page Config - 'centered' provides a natural mobile layout
st.set_page_config(
    page_title="Navtara Pulse",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Enhanced Responsive Styling with Larger, Clear Mobile Fonts
st.markdown("""
    <style>
    /* Hide Streamlit default headers & footers for native app feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Make block container adapt gracefully to mobile screens */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.8rem !important;
        padding-left: 1.1rem !important;
        padding-right: 1.1rem !important;
        max-width: 680px !important;
        margin: 0 auto !important;
    }
    
    /* Increased font size for labels and inputs for high legibility */
    label {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
    }
    
    input[type="text"], input[type="email"], select {
        font-size: 17px !important;
        min-height: 50px !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
    }
    
    /* Primary touch-friendly buttons with larger text */
    .stButton > button {
        font-size: 17px !important;
        font-weight: 700 !important;
        min-height: 52px !important;
        border-radius: 14px !important;
        width: 100% !important;
        transition: all 0.2s ease-in-out !important;
    }

    /* Headings with boosted readability */
    h1 {
        font-size: 1.95rem !important;
        font-weight: 800 !important;
        text-align: center !important;
        margin-bottom: 0.35rem !important;
        letter-spacing: -0.5px !important;
    }
    
    h2 {
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        margin-top: 0.5rem !important;
    }

    h3 {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
    }

    p, span, div {
        font-size: 15.5px;
    }

    /* Light, Catchy & Fresh Auth Container */
    .mobile-login-card-light {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #eff6ff 100%);
        padding: 24px 20px 20px 20px;
        border-radius: 22px;
        border: 1.5px solid #cbd5e1;
        box-shadow: 0 12px 28px -6px rgba(99, 102, 241, 0.14), 0 6px 14px -4px rgba(16, 185, 129, 0.08);
        margin-bottom: 1.3rem;
        text-align: center;
    }

    .hero-brand-container {
        text-align: center;
        padding-top: 0.2rem;
        margin-bottom: 1rem;
    }

    .brand-logo-emblem {
        width: 82px;
        height: 82px;
        margin: 0 auto 10px auto;
        border-radius: 24px;
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 25px -4px rgba(79, 70, 229, 0.4), 0 0 0 3px rgba(224, 231, 255, 0.8);
        animation: pulseGlow 3.5s ease-in-out infinite alternate;
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 8px 20px -4px rgba(79, 70, 229, 0.35), 0 0 0 3px rgba(224, 231, 255, 0.8); }
        100% { box-shadow: 0 14px 30px -2px rgba(236, 72, 153, 0.45), 0 0 0 4px rgba(254, 240, 138, 0.9); }
    }

    .hero-brand-container h1 {
        color: #0f172a !important;
        font-size: 2.15rem !important;
        font-weight: 900 !important;
        letter-spacing: -0.8px !important;
        margin-bottom: 2px !important;
        background: linear-gradient(120deg, #1e1b4b 0%, #4338ca 60%, #9333ea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-tagline {
        font-size: 1.02rem !important;
        font-weight: 700 !important;
        color: #4338ca !important;
        margin-bottom: 12px !important;
        letter-spacing: 0.2px;
    }

    /* Relatable Common-Man Value Card */
    .common-man-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 60%, #eef2ff 100%);
        border: 1.5px solid #c7d2fe;
        border-radius: 20px;
        padding: 20px 18px;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 24px -6px rgba(99, 102, 241, 0.12);
        text-align: left;
    }

    .common-man-card h4 {
        margin: 0 0 10px 0;
        font-size: 1.12rem;
        font-weight: 800;
        color: #1e1b4b;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .story-paragraph {
        font-size: 0.96rem;
        color: #334155;
        line-height: 1.55;
        margin-bottom: 14px;
    }

    .story-paragraph b {
        color: #0f172a;
    }

    .common-benefits-list {
        display: grid;
        grid-template-columns: 1fr;
        gap: 9px;
        margin-top: 10px;
    }

    .benefit-item {
        background: #ffffff;
        border: 1.2px solid #e2e8f0;
        border-radius: 12px;
        padding: 10px 12px;
        display: flex;
        align-items: flex-start;
        gap: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    }

    .benefit-icon {
        font-size: 1.25rem;
        line-height: 1;
        margin-top: 2px;
    }

    .benefit-text {
        font-size: 0.92rem;
        color: #334155;
        line-height: 1.4;
    }

    .benefit-text b {
        color: #1e293b;
        font-weight: 700;
    }

    .cosmic-pill-quote {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        border-radius: 0 10px 10px 0;
        padding: 9px 12px;
        font-size: 0.88rem;
        font-weight: 600;
        color: #166534;
        margin-top: 12px;
    }

    /* OTP Display Box */
    .otp-simulated-box {
        background: #f0fdf4;
        border: 2px dashed #22c55e;
        border-radius: 14px;
        padding: 14px;
        margin: 12px 0;
        text-align: center;
        color: #15803d;
        font-size: 1rem;
        font-weight: 700;
    }

    /* Google Brand Button */
    button[aria-label*="Google"] {
        background: #ffffff !important;
        color: #1f2937 !important;
        border: 1.8px solid #cbd5e1 !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.06) !important;
        font-weight: 700 !important;
    }
    button[aria-label*="Google"]::before {
        content: "";
        display: inline-block;
        width: 22px;
        height: 22px;
        margin-right: 10px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Cpath fill='%23EA4335' d='M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z'/%3E%3Cpath fill='%234285F4' d='M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z'/%3E%3Cpath fill='%23FBBC05' d='M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z'/%3E%3Cpath fill='%2334A853' d='M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: contain;
        vertical-align: middle;
    }

    /* WhatsApp Brand Button */
    button[aria-label*="WhatsApp"] {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%) !important;
        color: #ffffff !important;
        border: 1.8px solid #075E54 !important;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.28) !important;
        font-weight: 700 !important;
    }
    button[aria-label*="WhatsApp"]::before {
        content: "";
        display: inline-block;
        width: 22px;
        height: 22px;
        margin-right: 10px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 448 512'%3E%3Cpath fill='%23ffffff' d='M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.6z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: contain;
        vertical-align: middle;
    }

    /* Facebook Brand Button */
    button[aria-label*="Facebook"] {
        background: linear-gradient(135deg, #1877F2 0%, #0d65d9 100%) !important;
        color: #ffffff !important;
        border: 1.8px solid #0b4eb1 !important;
        box-shadow: 0 4px 12px rgba(24, 119, 242, 0.28) !important;
        font-weight: 700 !important;
    }
    button[aria-label*="Facebook"]::before {
        content: "";
        display: inline-block;
        width: 22px;
        height: 22px;
        margin-right: 10px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 448 512'%3E%3Cpath fill='%23ffffff' d='M400 32H48A48 48 0 0 0 0 80v352a48 48 0 0 0 48 48h137.25V327.69h-63V256h63v-54.64c0-62.15 37-96.48 93.67-96.48 27.14 0 55.52 4.84 55.52 4.84v61h-31.27c-30.81 0-40.42 19.12-40.42 38.74V256h68.78l-11 71.69h-57.78V480H400a48 48 0 0 0 48-48V80a48 48 0 0 0-48-48z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: contain;
        vertical-align: middle;
    }

    /* Email Brand Button */
    button[aria-label*="Email (OTP)"] {
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
        color: #ffffff !important;
        border: 1.8px solid #312e81 !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.28) !important;
        font-weight: 700 !important;
    }
    button[aria-label*="Email (OTP)"]::before {
        content: "";
        display: inline-block;
        width: 22px;
        height: 22px;
        margin-right: 10px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Cpath fill='%23ffffff' d='M48 64C21.5 64 0 85.5 0 112c0 15.1 7.1 29.3 19.2 38.4L236.8 313.6c11.4 8.5 27 8.5 38.4 0L492.8 150.4c12.1-9.1 19.2-23.3 19.2-38.4c0-26.5-21.5-48-48-48L48 64zM0 176L0 384c0 35.3 28.7 64 64 64l384 0c35.3 0 64-28.7 64-64l0-208L294.4 339.2c-22.8 17.1-54 17.1-76.8 0L0 176z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: contain;
        vertical-align: middle;
    }

    /* Active selection pill */
    .active-provider-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.88rem;
        font-weight: 700;
        margin-bottom: 12px;
    }

    /* Provider notification banner */
    .provider-banner {
        border-radius: 14px;
        padding: 12px 16px;
        font-size: 0.98rem;
        margin-bottom: 14px;
        font-weight: 700;
    }
    .provider-banner-email {
        background-color: #f8fafc;
        color: #334155;
        border: 1.5px solid #cbd5e1;
    }
    .provider-banner-google {
        background-color: #fef2f2;
        color: #991b1b;
        border: 1.5px solid #fca5a5;
    }
    .provider-banner-whatsapp {
        background-color: #f0fdf4;
        color: #166534;
        border: 1.5px solid #86efac;
    }
    .provider-banner-facebook {
        background-color: #eff6ff;
        color: #1e40af;
        border: 1.5px solid #93c5fd;
    }
    </style>
""", unsafe_allow_html=True)

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

NAVTARA_NAMES = [
    "Janma", "Sampat", "Vipat", "Kshema", "Pratyari",
    "Sadhana", "Vadha", "Mitra", "Ati-Mitra"
]

NAVTARA_DESCRIPTIONS = {
    "Janma": "Self / Physical Vitality / Grounding & New Cycles",
    "Sampat": "Wealth / Financial Inflow / Material Expansion",
    "Vipat": "Obstacles / High Risk / Unforeseen Difficulties",
    "Kshema": "Well-being / Comfort / Protection & Recovery",
    "Pratyari": "Conflict / Resistance / Disagreements",
    "Sadhana": "Achievement / Focused Effort / High Success",
    "Vadha": "Destruction / Vulnerability / Total Restraint",
    "Mitra": "Friendship / Collaborative Harmony / Assistance",
    "Ati-Mitra": "Supreme Support / Peak Auspicious Opportunity"
}

DB_FILE = "users_database.json"

def load_all_users() -> dict:
    """Reads the JSON database containing registered user accounts."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def get_user_profile(user_id: str, default_name: str = "User", auth_provider: str = "Email") -> dict:
    """Fetches user record from storage or instantiates default profile."""
    db = load_all_users()
    if user_id in db:
        record = db[user_id]
        if "dob" in record and isinstance(record["dob"], str):
            try:
                record["dob"] = datetime.date.fromisoformat(record["dob"])
            except ValueError:
                record["dob"] = datetime.date(1990, 1, 1)
        if "tob" in record and isinstance(record["tob"], str):
            try:
                record["tob"] = datetime.time.fromisoformat(record["tob"])
            except ValueError:
                record["tob"] = datetime.time(12, 0)
        return record

    return {
        "user_id": user_id,
        "name": default_name,
        "auth_provider": auth_provider,
        "dob": datetime.date(1990, 1, 1),
        "tob": datetime.time(12, 0),
        "place": "Chhatrapati Sambhajinagar, India",
        "lat": 19.8762,
        "lon": 75.3433,
        "tz_offset": 5.5,
        "nakshatra_idx": 1  # Bharani default
    }

def save_user_profile(user_id: str, profile_data: dict) -> bool:
    """Serializes user record to disk to persist Janma Nakshatra and birth details."""
    try:
        db = load_all_users()
        to_store = profile_data.copy()
        if isinstance(to_store.get("dob"), (datetime.date, datetime.datetime)):
            to_store["dob"] = to_store["dob"].isoformat()
        if isinstance(to_store.get("tob"), datetime.time):
            to_store["tob"] = to_store["tob"].isoformat()
        db[user_id] = to_store
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving user profile: {e}")
        return False

def dt_to_jd(utc_dt: datetime.datetime) -> float:
    """Converts a UTC datetime object to Julian Day number."""
    hour_decimal = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + utc_dt.second / 3600.0
        + (utc_dt.microsecond / 1e6) / 3600.0
    )
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)

def get_sidereal_lon(jd_ut: float, planet_id: int) -> float:
    """Computes sidereal longitude using Moshier engine with Chitrapaksha Lahiri Ayanamsa."""
    res, _ = swe.calc_ut(jd_ut, planet_id, swe.FLG_MOSEPH)
    trop_lon = res[0]
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    return (trop_lon - ayanamsa) % 360.0

def lon_to_nakshatra(lon: float):
    """Converts a sidereal longitude to nakshatra index (0-26) and pada (1-4)."""
    nak_span = 360.0 / 27.0
    idx = int(lon / nak_span) % 27
    pada = int((lon % nak_span) / (nak_span / 4.0)) + 1
    return idx, pada

def lon_to_rashi(lon: float):
    """Converts a longitude to rashi index (0-11) and degrees within sign."""
    return int(lon / 30.0) % 12, lon % 30.0

def calculate_navtara(birth_idx: int, transit_idx: int):
    """Calculates Navtara status name and series (1, 2, or 3)."""
    offset = (transit_idx - birth_idx) % 27
    return NAVTARA_NAMES[offset % 9], (offset // 9) + 1

def find_7day_transitions(start_utc_dt: datetime.datetime):
    """Locates exact Moon Nakshatra ingress and egress timestamps using binary search."""
    nak_span = 360.0 / 27.0
    transitions = []
    current_time = start_utc_dt
    end_time = start_utc_dt + datetime.timedelta(days=7)

    cur_lon = get_sidereal_lon(dt_to_jd(current_time), swe.MOON)
    active_nak = int(cur_lon / nak_span) % 27
    interval_start = current_time

    step = datetime.timedelta(minutes=30)
    eval_time = current_time

    while eval_time <= end_time:
        eval_time += step
        lon = get_sidereal_lon(dt_to_jd(eval_time), swe.MOON)
        nak = int(lon / nak_span) % 27

        if nak != active_nak:
            # Bisection refinement to 1-minute accuracy
            low, high = eval_time - step, eval_time
            for _ in range(7):
                mid = low + (high - low) / 2
                mid_lon = get_sidereal_lon(dt_to_jd(mid), swe.MOON)
                if int(mid_lon / nak_span) % 27 == active_nak:
                    low = mid
                else:
                    high = mid
            boundary = high
            transitions.append({
                "nak_idx": active_nak,
                "start": interval_start,
                "end": boundary
            })
            interval_start = boundary
            active_nak = nak

    transitions.append({
        "nak_idx": active_nak,
        "start": interval_start,
        "end": end_time
    })
    return transitions

if "user_info" not in st.session_state:
    st.session_state.user_info = None

# Active OTP verification tracking
if "pending_signup_otp" not in st.session_state:
    st.session_state.pending_signup_otp = None
if "pending_signup_data" not in st.session_state:
    st.session_state.pending_signup_data = None

if "pending_signin_otp" not in st.session_state:
    st.session_state.pending_signin_otp = None
if "pending_signin_id" not in st.session_state:
    st.session_state.pending_signin_id = None

if "signin_provider" not in st.session_state:
    st.session_state.signin_provider = "Google"
if "signup_provider" not in st.session_state:
    st.session_state.signup_provider = "Google"

# ---------------------------------------------------------
# AUTHENTICATION SCREEN (SIGN IN VS SIGN UP AS NEW USER)
# ---------------------------------------------------------
if not st.session_state.user_info:
    st.markdown("""
    <div class="hero-brand-container">
        <div class="brand-logo-emblem">
            <svg width="52" height="52" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- Outer Radiant Halo -->
                <circle cx="50" cy="50" r="44" stroke="url(#cosmicGrad)" stroke-width="2" stroke-dasharray="4 3" opacity="0.65"/>
                <!-- Crescent Moon Symbolizing Lunar Transit -->
                <path d="M56 22C41 22 29 34 29 49C29 64 41 76 56 76C46 76 38 67 38 53C38 39 47 25 56 22Z" fill="url(#goldGrad)" filter="drop-shadow(0 2px 6px rgba(245,158,11,0.5))"/>
                <!-- 9-Point Star Centerpiece Symbolizing 9 Navtara Pulses -->
                <path d="M56 36L58.5 45.5L68 47L59.5 51L61 60.5L53.5 54L45.5 59.5L48.5 50.5L41 45.5L50.5 45L56 36Z" fill="#ffffff"/>
                <!-- Center Core Pulse Indicator -->
                <circle cx="54" cy="49" r="3.5" fill="#f43f5e"/>
                <!-- Gradient Definitions -->
                <defs>
                    <linearGradient id="cosmicGrad" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#818cf8"/>
                        <stop offset="0.5" stop-color="#ec4899"/>
                        <stop offset="1" stop-color="#fbbf24"/>
                    </linearGradient>
                    <linearGradient id="goldGrad" x1="25" y1="20" x2="60" y2="80" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#fef08a"/>
                        <stop offset="0.4" stop-color="#fbbf24"/>
                        <stop offset="1" stop-color="#d97706"/>
                    </linearGradient>
                </defs>
            </svg>
        </div>
        <h1>Navtara Pulse</h1>
        <div class="hero-tagline">🧭 Your Personal Cosmic GPS & Daily Decision Timing Engine</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="common-man-card">
        <h4>✨ Why Every Decision Has a "Right Time"</h4>
        <div class="story-paragraph">
            Just as the <b>Moon's gravitational pull</b> commands the ocean tides, ancient Vedic astronomy discovered 
            that as the Moon glides across the <b>27 Nakshatras</b> every month, it creates invisible shifts in human energy, 
            mental clarity, and behavioral friction.
        </div>
        <div class="story-paragraph" style="margin-bottom: 8px;">
            <b>Navtara Pulse translates this 5,000-year-old cosmic rhythm into 3 simple daily advantages:</b>
        </div>
        <div class="common-benefits-list">
            <div class="benefit-item">
                <div class="benefit-icon">🛡️</div>
                <div class="benefit-text">
                    <b>Shield Your Wealth & Peace:</b> Know in advance which 24-hour windows are prone to unexpected delays, 
                    bad arguments, or financial traps (<i>Vipat, Pratyari, Vadha</i>) so you can hit pause and stay calm.
                </div>
            </div>
            <div class="benefit-item">
                <div class="benefit-icon">🚀</div>
                <div class="benefit-text">
                    <b>Catch Golden Windows:</b> Strike boldly when the Moon touches your peak auspicious cycles 
                    (<i>Sampat & Ati-Mitra</i>) for major purchases, interviews, financial deals, or ambitious launches.
                </div>
            </div>
            <div class="benefit-item">
                <div class="benefit-icon">💡</div>
                <div class="benefit-text">
                    <b>Zero Superstition, 100% Timing:</b> No complex rituals. Just pure astronomical planetary math 
                    tailored specifically to the exact star you were born under.
                </div>
            </div>
        </div>
        <div class="cosmic-pill-quote">
            🌱 <i>"Carry an umbrella before it rains, and set your sails when the golden wind blows."</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Clean Primary Mode Switch: Sign In vs Sign Up
    auth_mode = st.radio(
        "Authentication Mode",
        ["🔑 Existing User: Sign In", "✨ New User: Sign Up"],
        horizontal=True,
        label_visibility="collapsed"
    )

    db = load_all_users()

    # =========================================================
    # OPTION 1: EXISTING USER SIGN IN
    # =========================================================
    if "Sign In" in auth_mode:
        st.subheader("🔑 Sign In to Your Account")
        st.caption("Choose your account provider to access your saved birth parameters.")

        # 2x2 Brand Buttons Grid for Sign In
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("Google", key="btn_signin_google", use_container_width=True):
                st.session_state.signin_provider = "Google"
                st.rerun()
            if st.button("WhatsApp", key="btn_signin_wa", use_container_width=True):
                st.session_state.signin_provider = "WhatsApp"
                st.rerun()

        with btn_col2:
            if st.button("Facebook", key="btn_signin_fb", use_container_width=True):
                st.session_state.signin_provider = "Facebook"
                st.rerun()
            if st.button("Email (OTP)", key="btn_signin_email", use_container_width=True):
                st.session_state.signin_provider = "Email"
                st.rerun()

        method = st.session_state.signin_provider

        if method == "Google":
            st.markdown('<div class="provider-banner provider-banner-google">🔴 Sign In with your Google / Gmail Account</div>', unsafe_allow_html=True)
            google_email = st.text_input("Google Email Address", placeholder="e.g. username@gmail.com", key="signin_google_email")
            if st.button("🚀 Continue with Google", use_container_width=True, type="primary"):
                cleaned_id = google_email.strip().lower() if google_email else ""
                if not cleaned_id or "@" not in cleaned_id:
                    st.warning("⚠️ Please enter a valid Google email address.")
                elif cleaned_id not in db:
                    st.error("❌ No user details found for this Google account. Please use the 'Sign Up as New User' option to create an account.")
                else:
                    st.session_state.user_info = {
                        "user_id": cleaned_id,
                        "name": db[cleaned_id].get("name", cleaned_id.split("@")[0]),
                        "provider": "Google"
                    }
                    st.rerun()

        elif method == "WhatsApp":
            st.markdown('<div class="provider-banner provider-banner-whatsapp">🟢 Sign In with your WhatsApp Mobile Number</div>', unsafe_allow_html=True)
            wa_num = st.text_input("WhatsApp Mobile Number", placeholder="e.g. +91 98765 43210", key="signin_wa_num")
            if st.button("💬 Continue with WhatsApp", use_container_width=True, type="primary"):
                cleaned_id = wa_num.strip() if wa_num else ""
                if not cleaned_id or len(cleaned_id) < 8:
                    st.warning("⚠️ Please enter a valid registered mobile number.")
                elif cleaned_id not in db:
                    st.error("❌ No user details found for this WhatsApp number. Please use the 'Sign Up as New User' option to register.")
                else:
                    st.session_state.user_info = {
                        "user_id": cleaned_id,
                        "name": db[cleaned_id].get("name", "User"),
                        "provider": "WhatsApp"
                    }
                    st.rerun()

        elif method == "Facebook":
            st.markdown('<div class="provider-banner provider-banner-facebook">🔵 Sign In with your Facebook Account</div>', unsafe_allow_html=True)
            fb_id = st.text_input("Facebook Email or Mobile", placeholder="e.g. facebook.id@domain.com", key="signin_fb_id")
            if st.button("📘 Continue with Facebook", use_container_width=True, type="primary"):
                cleaned_id = fb_id.strip().lower() if fb_id else ""
                if not cleaned_id:
                    st.warning("⚠️ Please enter a valid Facebook email or ID.")
                elif cleaned_id not in db:
                    st.error("❌ No user details found for this Facebook account. Please use the 'Sign Up as New User' option.")
                else:
                    st.session_state.user_info = {
                        "user_id": cleaned_id,
                        "name": db[cleaned_id].get("name", "User"),
                        "provider": "Facebook"
                    }
                    st.rerun()

        else:  # Email (with OTP)
            st.markdown('<div class="provider-banner provider-banner-email">✉️ Sign In using your Registered Email & OTP</div>', unsafe_allow_html=True)
            login_email = st.text_input("Registered Email Address", placeholder="e.g. yourname@gmail.com", key="signin_email")

            if st.button("📨 Request Sign-In OTP", use_container_width=True, type="primary"):
                cleaned_id = login_email.strip().lower() if login_email else ""
                if not cleaned_id or "@" not in cleaned_id:
                    st.warning("⚠️ Please enter a valid registered email address.")
                elif cleaned_id not in db:
                    st.error("❌ No user details found for this email. Please use the 'Sign Up as New User' option to create your profile.")
                else:
                    otp_code = str(random.randint(100000, 999999))
                    st.session_state.pending_signin_otp = otp_code
                    st.session_state.pending_signin_id = cleaned_id
                    st.session_state.pending_signin_name = db[cleaned_id].get("name", "User")
                    st.rerun()

            if st.session_state.pending_signin_otp:
                st.markdown(f"""
                <div class="otp-simulated-box">
                    📩 Verification OTP sent to <b>{st.session_state.pending_signin_id}</b>:<br>
                    <span style="font-size: 1.4rem; letter-spacing: 4px; color: #166534;">{st.session_state.pending_signin_otp}</span>
                </div>
                """, unsafe_allow_html=True)

                entered_otp = st.text_input("Enter 6-digit OTP", placeholder="Enter OTP received", max_chars=6, key="signin_entered_otp")
                if st.button("✅ Verify OTP & Sign In", use_container_width=True, type="primary"):
                    if entered_otp.strip() == st.session_state.pending_signin_otp:
                        st.session_state.user_info = {
                            "user_id": st.session_state.pending_signin_id,
                            "name": st.session_state.pending_signin_name,
                            "provider": "Email"
                        }
                        st.session_state.pending_signin_otp = None
                        st.session_state.pending_signin_id = None
                        st.rerun()
                    else:
                        st.error("❌ Invalid OTP code entered. Please verify and try again.")

    # =========================================================
    # OPTION 2: NEW USER SIGN UP
    # =========================================================
    else:
        st.subheader("✨ Sign Up as New User")
        st.caption("Select your preferred registration method to create your profile.")

        # 2x2 Brand Buttons Grid for Sign Up
        signup_col1, signup_col2 = st.columns(2)
        with signup_col1:
            if st.button("Google", key="btn_signup_google", use_container_width=True):
                st.session_state.signup_provider = "Google"
                st.rerun()
            if st.button("WhatsApp", key="btn_signup_wa", use_container_width=True):
                st.session_state.signup_provider = "WhatsApp"
                st.rerun()

        with signup_col2:
            if st.button("Facebook", key="btn_signup_fb", use_container_width=True):
                st.session_state.signup_provider = "Facebook"
                st.rerun()
            if st.button("Email (OTP)", key="btn_signup_email", use_container_width=True):
                st.session_state.signup_provider = "Email"
                st.rerun()

        signup_method = st.session_state.signup_provider

        if signup_method == "Google":
            st.markdown('<div class="provider-banner provider-banner-google">🔴 Sign Up with Google / Gmail</div>', unsafe_allow_html=True)
            google_email = st.text_input("Gmail Address", placeholder="e.g. yourname@gmail.com", key="signup_g_email")
            google_name = st.text_input("Your Full Name", placeholder="e.g. Okesh Sharma", key="signup_g_name")

            if st.button("🚀 Complete Google Sign Up", use_container_width=True, type="primary"):
                cleaned_id = google_email.strip().lower() if google_email else ""
                cleaned_name = google_name.strip() if google_name else (cleaned_id.split("@")[0] if cleaned_id else "User")
                
                if not cleaned_id or "@" not in cleaned_id:
                    st.warning("⚠️ Please provide a valid Gmail address.")
                elif cleaned_id in db:
                    st.error(f"⚠️ An account with '{cleaned_id}' already exists! Please switch to 'Existing User: Sign In'.")
                else:
                    initial_profile = {
                        "user_id": cleaned_id,
                        "name": cleaned_name,
                        "auth_provider": "Google",
                        "dob": datetime.date(1990, 1, 1),
                        "tob": datetime.time(12, 0),
                        "place": "Chhatrapati Sambhajinagar, India",
                        "lat": 19.8762,
                        "lon": 75.3433,
                        "tz_offset": 5.5,
                        "nakshatra_idx": 1
                    }
                    save_user_profile(cleaned_id, initial_profile)
                    st.session_state.user_info = {
                        "user_id": cleaned_id,
                        "name": cleaned_name,
                        "provider": "Google"
                    }
                    st.rerun()

        elif signup_method == "WhatsApp":
            st.markdown('<div class="provider-banner provider-banner-whatsapp">🟢 Sign Up with WhatsApp Mobile</div>', unsafe_allow_html=True)
            wa_num = st.text_input("WhatsApp Number", placeholder="e.g. +91 98765 43210", key="signup_wa_num")
            wa_name = st.text_input("Your Full Name", placeholder="e.g. Okesh Sharma", key="signup_wa_name")

            if st.button("💬 Complete WhatsApp Sign Up", use_container_width=True, type="primary"):
                cleaned_id = wa_num.strip() if wa_num else ""
                cleaned_name = wa_name.strip() if wa_name else "User"

                if not cleaned_id or len(cleaned_id) < 8:
                    st.warning("⚠️ Please enter a valid mobile number.")
                elif cleaned_id in db:
                    st.error(f"⚠️ An account with mobile '{cleaned_id}' already exists! Please switch to 'Existing User: Sign In'.")
                else:
                    initial_profile = {
                        "user_id": cleaned_id,
                        "name": cleaned_name,
                        "auth_provider": "WhatsApp",
                        "dob": datetime.date(1990, 1, 1),
                        "tob": datetime.time(12, 0),
                        "place": "Chhatrapati Sambhajinagar, India",
                        "lat": 19.8762,
                        "lon": 75.3433,
                        "tz_offset": 5.5,
                        "nakshatra_idx": 1
                    }
                    save_user_profile(cleaned_id, initial_profile)
                    st.session_state.user_info = {
                        "user_id": cleaned_id,
                        "name": cleaned_name,
                        "provider": "WhatsApp"
                    }
                    st.rerun()

        elif signup_method == "Facebook":
            st.markdown('<div class="provider-banner provider-banner-facebook">🔵 Sign Up with Facebook Account</div>', unsafe_allow_html=True)
            fb_id = st.text_input("Facebook Email or Mobile", placeholder="e.g. facebook.id@domain.com", key="signup_fb_id")
            fb_name = st.text_input("Your Full Name", placeholder="e.g. Okesh Sharma", key="signup_fb_name")

            if st.button("📘 Complete Facebook Sign Up", use_container_width=True, type="primary"):
                cleaned_id = fb_id.strip().lower() if fb_id else ""
                cleaned_name = fb_name.strip() if fb_name else "User"

                if not cleaned_id:
                    st.warning("⚠️ Please enter your Facebook email or ID.")
                elif cleaned_id in db:
                    st.error(f"⚠️ An account with '{cleaned_id}' already exists! Please switch to 'Existing User: Sign In'.")
                else:
                    initial_profile = {
                        "user_id": cleaned_id,
                        "name": cleaned_name,
                        "auth_provider": "Facebook",
                        "dob": datetime.date(1990, 1, 1),
                        "tob": datetime.time(12, 0),
                        "place": "Chhatrapati Sambhajinagar, India",
                        "lat": 19.8762,
                        "lon": 75.3433,
                        "tz_offset": 5.5,
                        "nakshatra_idx": 1
                    }
                    save_user_profile(cleaned_id, initial_profile)
                    st.session_state.user_info = {
                        "user_id": cleaned_id,
                        "name": cleaned_name,
                        "provider": "Facebook"
                    }
                    st.rerun()

        else:  # Email (with OTP Verification)
            st.markdown('<div class="provider-banner provider-banner-email">✉️ Verify your Email with OTP</div>', unsafe_allow_html=True)
            signup_email = st.text_input("Email Address", placeholder="e.g. yourname@gmail.com", key="signup_email")
            signup_name = st.text_input("Your Full Name", placeholder="e.g. Okesh Sharma", key="signup_name")

            if st.button("📨 Send Verification OTP", use_container_width=True, type="primary"):
                cleaned_id = signup_email.strip().lower() if signup_email else ""
                cleaned_name = signup_name.strip() if signup_name else "User"
                
                if not cleaned_id or "@" not in cleaned_id:
                    st.warning("⚠️ Please provide a valid email address.")
                elif cleaned_id in db:
                    st.error(f"⚠️ An account with email '{cleaned_id}' already exists! Please switch to 'Existing User: Sign In'.")
                else:
                    otp_code = str(random.randint(100000, 999999))
                    st.session_state.pending_signup_otp = otp_code
                    st.session_state.pending_signup_data = {
                        "user_id": cleaned_id,
                        "name": cleaned_name,
                        "provider": "Email"
                    }
                    st.rerun()

            if st.session_state.pending_signup_otp:
                st.markdown(f"""
                <div class="otp-simulated-box">
                    📩 Verification OTP sent to <b>{st.session_state.pending_signup_data['user_id']}</b>:<br>
                    <span style="font-size: 1.4rem; letter-spacing: 4px; color: #166534;">{st.session_state.pending_signup_otp}</span>
                </div>
                """, unsafe_allow_html=True)

                entered_code = st.text_input("Enter 6-digit OTP", placeholder="Enter OTP received", max_chars=6, key="signup_entered_code")
                if st.button("✅ Verify OTP & Complete Sign Up", use_container_width=True, type="primary"):
                    if entered_code.strip() == st.session_state.pending_signup_otp:
                        new_user = st.session_state.pending_signup_data
                        # Initialize and save template profile
                        initial_profile = {
                            "user_id": new_user["user_id"],
                            "name": new_user["name"],
                            "auth_provider": "Email",
                            "dob": datetime.date(1990, 1, 1),
                            "tob": datetime.time(12, 0),
                            "place": "Chhatrapati Sambhajinagar, India",
                            "lat": 19.8762,
                            "lon": 75.3433,
                            "tz_offset": 5.5,
                            "nakshatra_idx": 1
                        }
                        save_user_profile(new_user["user_id"], initial_profile)
                        st.session_state.user_info = new_user
                        st.session_state.pending_signup_otp = None
                        st.session_state.pending_signup_data = None
                        st.rerun()
                    else:
                        st.error("❌ Invalid OTP entered. Please recheck the code.")

    st.stop()

# ---------------------------------------------------------
# LOGGED-IN MOBILE DASHBOARD
# ---------------------------------------------------------
user_id = st.session_state.user_info["user_id"]
user_display = st.session_state.user_info["name"]
auth_provider = st.session_state.user_info.get("provider", "Email")

if (
    "current_profile" not in st.session_state
    or st.session_state.current_profile.get("user_id") != user_id
):
    st.session_state.current_profile = get_user_profile(user_id, user_display, auth_provider)

prof = st.session_state.current_profile

# Sidebar Configuration for Profiles
with st.sidebar:
    provider_icon = "✉️" if auth_provider == "Email" else ("🔴" if auth_provider == "Google" else ("🟢" if auth_provider == "WhatsApp" else "🔵"))
    st.markdown(f"**Signed in via {auth_provider} {provider_icon}**")
    st.code(user_id, language=None)
    
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.user_info = None
        st.session_state.current_profile = None
        st.rerun()

    st.divider()
    st.header("👤 Your Birth Profile")
    st.caption(f"Linked permanently to your {auth_provider} account.")

    name_in = st.text_input("Full Name", value=prof.get("name", user_display))
    dob_in = st.date_input("Date of Birth", value=prof.get("dob", datetime.date(1990, 1, 1)))
    tob_in = st.time_input("Time of Birth", value=prof.get("tob", datetime.time(12, 0)))
    place_in = st.text_input("Birth Place / City", value=prof.get("place", "Chhatrapati Sambhajinagar, India"))

    lat_in = st.number_input("Latitude", value=float(prof.get("lat", 19.8762)), format="%.4f")
    lon_in = st.number_input("Longitude", value=float(prof.get("lon", 75.3433)), format="%.4f")

    selected_nak = st.selectbox(
        "Janma Nakshatra",
        NAKSHATRAS,
        index=prof.get("nakshatra_idx", 1)  # Default: Bharani (Index 1)
    )
    selected_nak_idx = NAKSHATRAS.index(selected_nak)

    if st.button("💾 Save Profile to Account", use_container_width=True, type="primary"):
        updated_prof = {
            "user_id": user_id,
            "name": name_in,
            "auth_provider": auth_provider,
            "dob": dob_in,
            "tob": tob_in,
            "place": place_in,
            "lat": lat_in,
            "lon": lon_in,
            "tz_offset": 5.5,
            "nakshatra_idx": selected_nak_idx
        }
        st.session_state.current_profile = updated_prof
        if save_user_profile(user_id, updated_prof):
            st.success("✅ Profile successfully saved to your account!")

janma_idx = prof.get("nakshatra_idx", 1)
janma_name = NAKSHATRAS[janma_idx]

st.markdown("<h1>✨ Navtara Pulse</h1>", unsafe_allow_html=True)
st.markdown(
    f"<p style='text-align: center; font-size: 1.05rem; margin-top: -6px;'>"
    f"Welcome, <b>{prof.get('name')}</b> ({auth_provider} {provider_icon})<br>"
    f"Janma Nakshatra: <b>{janma_name}</b> (<code>#{janma_idx + 1}/27</code>)"
    f"</p>",
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "🗓️ 7-Day Matrix",
    "🔮 Forecast",
    "🪐 Planetary"
])

with tab1:
    st.subheader("Daily Moon Transition Table (Next 7 Days)")
    st.caption("Computed with Swiss Ephemeris Chitrapaksha Lahiri Ayanamsa.")

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    transitions = find_7day_transitions(now_utc)

    table_rows = []
    for t in transitions:
        nak_name = NAKSHATRAS[t["nak_idx"]]
        cat, series = calculate_navtara(janma_idx, t["nak_idx"])

        # Operational status symbols
        if cat in ["Vipat", "Pratyari", "Vadha"]:
            status_str = f"🔴 {cat}"
        elif cat == "Ati-Mitra":
            status_str = "🟢🟢 Ati-Mitra"
        elif cat in ["Mitra", "Sampat"]:
            status_str = f"🟢 {cat}"
        else:
            status_str = cat

        start_ist = t["start"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M)")
        end_ist = t["end"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M IST)")

        table_rows.append({
            "Status": status_str,
            "Time Range (IST)": f"{start_ist} – {end_ist}",
            "Nakshatra": f"{nak_name}",
            "Series": f"{cat} ({series})"
        })

    st.dataframe(table_rows, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("7-Day Energy Forecast & Guidance")
    st.caption("Strategic guidance tailored to your Janma Nakshatra.")

    guidance_map = {
        "Janma": "Focus on self-care, physical vitality, and routine grounding. Avoid starting high-strain structural tasks.",
        "Sampat": "Prime window for capital growth, investment evaluation, contract discussions, and financial planning.",
        "Vipat": "High-risk window. Avoid speculative trades, high-leverage positions, and unverified business commitments.",
        "Kshema": "Supportive and protective window. Excellent for health recovery, operational maintenance, and family time.",
        "Pratyari": "Keep communication gentle and diplomatic. Avoid arguments, confrontations, or aggressive negotiations.",
        "Sadhana": "Peak productivity window. Outstanding for completing complex research, technical challenges, and major milestones.",
        "Vadha": "Maximum caution window. Exercise restraint, keep physical strain low, and postpone high-stakes meetings.",
        "Mitra": "Friendly, cooperative energy. Ideal for networking, partnership building, and harmonious team collaboration.",
        "Ati-Mitra": "Supreme auspicious window. Highest support for ambitious launches, major milestones, and strategic decisions."
    }

    for idx, t in enumerate(transitions):
        nak_name = NAKSHATRAS[t["nak_idx"]]
        cat, series = calculate_navtara(janma_idx, t["nak_idx"])
        start_ist = t["start"].astimezone(ist_tz).strftime("%a, %d %b %H:%M")
        end_ist = t["end"].astimezone(ist_tz).strftime("%a, %d %b %H:%M IST")

        status_prefix = "🔴" if cat in ["Vipat", "Pratyari", "Vadha"] else ("🟢🟢" if cat == "Ati-Mitra" else ("🟢" if cat in ["Mitra", "Sampat"] else "⚪"))
        card_label = f"{status_prefix} {cat} — {nak_name} ({start_ist} to {end_ist})"

        with st.expander(card_label, expanded=(idx == 0)):
            st.markdown(f"**Navtara Category:** {cat} (Series {series})")
            st.markdown(f"**Core Archetype:** {NAVTARA_DESCRIPTIONS.get(cat, '')}")
            st.markdown(f"**Operational Directive:** {guidance_map.get(cat, 'Maintain steady, disciplined focus.')}")

with tab3:
    st.subheader("Sidereal Planetary Positions (Lahiri)")
    jd_now = dt_to_jd(now_utc)
    planets = [
        ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
        ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
        ("Venus", swe.VENUS), ("Saturn", swe.SATURN), ("Rahu", swe.MEAN_NODE)
    ]

    coords = []
    for name, pid in planets:
        lon = get_sidereal_lon(jd_now, pid)
        r_idx, r_deg = lon_to_rashi(lon)
        n_idx, pada = lon_to_nakshatra(lon)
        coords.append({
            "Planet": name,
            "Sign": RASHIS[r_idx].split(" ")[0],
            "Deg": f"{r_deg:.1f}°",
            "Nakshatra": f"{NAKSHATRAS[n_idx]} ({pada})"
        })

    rahu_lon = get_sidereal_lon(jd_now, swe.MEAN_NODE)
    ketu_lon = (rahu_lon + 180.0) % 360.0
    kr_idx, kr_deg = lon_to_rashi(ketu_lon)
    kn_idx, k_pada = lon_to_nakshatra(ketu_lon)
    coords.append({
        "Planet": "Ketu",
        "Sign": RASHIS[kr_idx].split(" ")[0],
        "Deg": f"{kr_deg:.1f}°",
        "Nakshatra": f"{NAKSHATRAS[kn_idx]} ({k_pada})"
    })

    st.dataframe(coords, use_container_width=True, hide_index=True)

st.divider()
st.caption("Navtara Pulse Engine • Swiss Ephemeris Lahiri Sidereal Framework")
