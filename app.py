import os
import json
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

# Mobile-Optimized & Light Catchy CSS Styling
st.markdown("""
    <style>
    /* Hide Streamlit default headers & footers for native app feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Make block container adapt gracefully to mobile screens */
    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 650px !important;
        margin: 0 auto !important;
    }
    
    /* Prevent auto-zooming on mobile inputs & ensure touch-friendly size */
    input[type="text"], input[type="email"], select {
        font-size: 16px !important;
        min-height: 46px !important;
        border-radius: 10px !important;
    }
    
    /* Primary buttons touch-friendly */
    .stButton > button {
        font-size: 16px !important;
        font-weight: 600 !important;
        min-height: 48px !important;
        border-radius: 12px !important;
        width: 100% !important;
    }

    /* Headings scaling */
    h1 {
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        text-align: center !important;
        margin-bottom: 0.25rem !important;
    }
    
    h2 {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
    }

    /* Light, Catchy & Fresh Mobile Login Card */
    .mobile-login-card-light {
        background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 45%, #eff6ff 100%);
        padding: 22px 18px 18px 18px;
        border-radius: 20px;
        border: 1.5px solid #cbd5e1;
        box-shadow: 0 12px 28px -6px rgba(99, 102, 241, 0.16), 0 6px 12px -4px rgba(16, 185, 129, 0.1);
        margin-bottom: 1.25rem;
        text-align: center;
    }

    .mobile-login-card-light h3 {
        color: #0f172a !important;
        margin-top: 0 !important;
        margin-bottom: 6px !important;
        font-size: 1.28rem !important;
        font-weight: 800 !important;
    }

    .mobile-login-card-light p {
        color: #475569 !important;
        font-size: 0.90rem !important;
        line-height: 1.45 !important;
        margin-bottom: 12px !important;
    }

    /* Social Badge Chips */
    .social-pills-wrap {
        display: flex;
        justify-content: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 6px;
    }

    .social-badge-google {
        background: #ffffff;
        color: #dc2626;
        border: 1px solid #fca5a5;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .social-badge-whatsapp {
        background: #ecfdf5;
        color: #059669;
        border: 1px solid #6ee7b7;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .social-badge-facebook {
        background: #eff6ff;
        color: #2563eb;
        border: 1px solid #93c5fd;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Provider notification banner */
    .provider-banner {
        border-radius: 12px;
        padding: 10px 14px;
        font-size: 0.88rem;
        margin-bottom: 12px;
        font-weight: 600;
    }
    .provider-banner-google {
        background-color: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    .provider-banner-whatsapp {
        background-color: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    .provider-banner-facebook {
        background-color: #eff6ff;
        color: #1e40af;
        border: 1px solid #bfdbfe;
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

def load_all_users():
    """Reads the JSON database containing user profiles keyed by identifier."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def get_user_profile(user_id: str, default_name: str = "User", auth_provider: str = "Google"):
    """Fetches user record from disk or creates default template."""
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
    """Serializes and saves the user record to JSON storage."""
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

# Session State Auth Setup
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ---------------------------------------------------------
# AUTHENTICATION SCREEN (LIGHT & CATCHY + GOOGLE / WHATSAPP / FACEBOOK)
# ---------------------------------------------------------
if not st.session_state.user_info:
    st.markdown("<h1>✨ Navtara Pulse</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; margin-top: -6px; font-size: 0.92rem;'>Precision Vedic Moon Transit & Navtara Timing Engine</p>", unsafe_allow_html=True)
    st.write("")

    # Light, catchy and welcoming card
    st.markdown("""
    <div class="mobile-login-card-light">
        <h3>🌟 Welcome to Navtara Pulse</h3>
        <p>
            Choose your preferred sign-in method to sync and permanently save your Janma Nakshatra and birth parameters.
        </p>
        <div class="social-pills-wrap">
            <span class="social-badge-google">🔴 Google</span>
            <span class="social-badge-whatsapp">🟢 WhatsApp</span>
            <span class="social-badge-facebook">🔵 Facebook</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Multi-Provider Selector
    auth_choice = st.radio(
        "Select Sign-in Method",
        ["Google", "WhatsApp", "Facebook"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if auth_choice == "Google":
        st.markdown('<div class="provider-banner provider-banner-google">🔴 Sign in with your Google / Gmail Account</div>', unsafe_allow_html=True)
        login_input = st.text_input("Gmail Address", placeholder="e.g. yourname@gmail.com")
        display_name = st.text_input("Your Full Name", placeholder="e.g. Okesh Sharma")
        btn_label = "🚀 Continue with Google"
        btn_color = "primary"

    elif auth_choice == "WhatsApp":
        st.markdown('<div class="provider-banner provider-banner-whatsapp">🟢 Sign in with your WhatsApp Mobile Number</div>', unsafe_allow_html=True)
        login_input = st.text_input("WhatsApp Mobile Number", placeholder="e.g. +91 98765 43210")
        display_name = st.text_input("Your Full Name", placeholder="e.g. Okesh Sharma")
        btn_label = "💬 Continue with WhatsApp"
        btn_color = "primary"

    else:  # Facebook
        st.markdown('<div class="provider-banner provider-banner-facebook">🔵 Sign in with your Facebook Account</div>', unsafe_allow_html=True)
        login_input = st.text_input("Facebook Email or Mobile", placeholder="e.g. facebook.id@domain.com")
        display_name = st.text_input("Your Full Name", placeholder="e.g. Okesh Sharma")
        btn_label = "📘 Continue with Facebook"
        btn_color = "primary"

    st.write("")
    if st.button(btn_label, use_container_width=True, type=btn_color):
        cleaned_id = login_input.strip().lower() if login_input else ""
        if cleaned_id:
            cleaned_name = display_name.strip() if display_name else cleaned_id.split("@")[0]
            st.session_state.user_info = {
                "user_id": cleaned_id,
                "name": cleaned_name,
                "provider": auth_choice
            }
            st.rerun()
        else:
            st.warning(f"⚠️ Please enter a valid {auth_choice} credential to continue.")
    st.stop()

# ---------------------------------------------------------
# LOGGED-IN MOBILE DASHBOARD
# ---------------------------------------------------------
user_id = st.session_state.user_info["user_id"]
user_display = st.session_state.user_info["name"]
auth_provider = st.session_state.user_info.get("provider", "Google")

if (
    "current_profile" not in st.session_state
    or st.session_state.current_profile.get("user_id") != user_id
):
    st.session_state.current_profile = get_user_profile(user_id, user_display, auth_provider)

prof = st.session_state.current_profile

# Sidebar Configuration for Profiles
with st.sidebar:
    provider_icon = "🔴" if auth_provider == "Google" else ("🟢" if auth_provider == "WhatsApp" else "🔵")
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
    f"<p style='text-align: center; font-size: 0.95rem; margin-top: -6px;'>"
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
