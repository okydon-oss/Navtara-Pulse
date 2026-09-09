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

    .mobile-login-card-light h3 {
        color: #0f172a !important;
        margin-top: 0 !important;
        margin-bottom: 8px !important;
        font-size: 1.35rem !important;
        font-weight: 800 !important;
    }

    .mobile-login-card-light p {
        color: #475569 !important;
        font-size: 1.02rem !important;
        line-height: 1.5 !important;
        margin-bottom: 4px !important;
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

# ---------------------------------------------------------
# AUTHENTICATION SCREEN (SIGN IN VS SIGN UP AS NEW USER)
# ---------------------------------------------------------
if not st.session_state.user_info:
    st.markdown("<h1>✨ Navtara Pulse</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; margin-top: -6px; font-size: 1.05rem; font-weight: 500;'>Precision Vedic Moon Transit & Navtara Timing Engine</p>", unsafe_allow_html=True)
    st.write("")

    # Light, catchy welcoming card
    st.markdown("""
    <div class="mobile-login-card-light">
        <h3>🌟 Welcome to Navtara Pulse</h3>
        <p>
            Track your 27-Nakshatra Navtara cycles and protect key financial and personal decisions.
        </p>
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
        st.caption("Access your saved Janma Nakshatra and birth parameters.")

        method = st.selectbox(
            "Select Sign-In Method",
            ["Email (with OTP)", "Google", "WhatsApp", "Facebook"],
            index=0
        )

        if method == "Email (with OTP)":
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

        elif method == "Google":
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

        else:  # Facebook
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

    # =========================================================
    # OPTION 2: NEW USER SIGN UP
    # =========================================================
    else:
        st.subheader("✨ Sign Up as New User")
        st.caption("Create a new profile to sync your Janma Nakshatra calculations.")

        signup_method = st.selectbox(
            "Select Registration Method",
            ["Email (with OTP Verification)", "Sign Up via Google", "Sign Up via WhatsApp", "Sign Up via Facebook"],
            index=0
        )

        if signup_method == "Email (with OTP Verification)":
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

        elif signup_method == "Sign Up via Google":
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

        elif signup_method == "Sign Up via WhatsApp":
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

        else:  # Facebook
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
