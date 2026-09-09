import os
import json
import datetime
import urllib.parse
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

st.set_page_config(
    page_title="Navtara Pulse",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for cards, badges, and table elements
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .status-badge-danger {
        color: #ef4444 !important;
        font-weight: 800;
    }
    .status-badge-golden {
        color: #10b981 !important;
        font-weight: 800;
    }
    .login-container {
        background-color: #1e1b4b;
        color: #ffffff;
        padding: 24px;
        border-radius: 14px;
        border: 1px solid #4338ca;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .transit-card {
        background-color: #0f172a;
        color: #f8fafc;
        padding: 16px;
        border-radius: 10px;
        border-left: 5px solid #6366f1;
        margin-bottom: 12px;
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
    """Reads the JSON database containing user profiles keyed by email address."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def get_user_profile(user_email: str, default_name: str = "User"):
    """Fetches user record from disk or creates default template."""
    db = load_all_users()
    if user_email in db:
        record = db[user_email]
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
        "email": user_email,
        "name": default_name,
        "dob": datetime.date(1990, 1, 1),
        "tob": datetime.time(12, 0),
        "place": "Chhatrapati Sambhajinagar, India",
        "lat": 19.8762,
        "lon": 75.3433,
        "tz_offset": 5.5,
        "nakshatra_idx": 1  # Bharani default
    }

def save_user_profile(user_email: str, profile_data: dict) -> bool:
    """Serializes and saves the user record to JSON storage."""
    try:
        db = load_all_users()
        to_store = profile_data.copy()
        if isinstance(to_store.get("dob"), (datetime.date, datetime.datetime)):
            to_store["dob"] = to_store["dob"].isoformat()
        if isinstance(to_store.get("tob"), datetime.time):
            to_store["tob"] = to_store["tob"].isoformat()
        db[user_email] = to_store
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

if not st.session_state.user_info:
    st.markdown("<h1 style='text-align: center;'>✨ Navtara Pulse</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Precision Vedic Moon Transit & Navtara Timing Engine</p>", unsafe_allow_html=True)
    st.divider()

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("""
        <div class="login-container">
            <h3 style="margin-top: 0; color: #fbbf24;">🔐 User Sign-In</h3>
            <p style="color: #cbd5e1; font-size: 0.95rem;">
                Sign in with your email or Google Account. Your Janma Nakshatra and birth parameters will be permanently saved to your profile.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        login_email = st.text_input("Email / Gmail Address", placeholder="e.g. yourname@gmail.com")
        display_name = st.text_input("Your Full Name", placeholder="e.g. Okesh Sharma")

        if st.button("🚀 Continue to Navtara Pulse", use_container_width=True, type="primary"):
            if login_email and "@" in login_email:
                cleaned_email = login_email.strip().lower()
                cleaned_name = display_name.strip() if display_name else cleaned_email.split("@")[0]
                st.session_state.user_info = {
                    "email": cleaned_email,
                    "name": cleaned_name
                }
                st.rerun()
            else:
                st.warning("⚠️ Please provide a valid email address.")
    st.stop()

user_email = st.session_state.user_info["email"]
user_display = st.session_state.user_info["name"]

if (
    "current_profile" not in st.session_state
    or st.session_state.current_profile.get("email") != user_email
):
    st.session_state.current_profile = get_user_profile(user_email, user_display)

prof = st.session_state.current_profile

with st.sidebar:
    st.markdown(f"**Logged in as:** `{user_email}`")
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.user_info = None
        st.session_state.current_profile = None
        st.rerun()

    st.divider()
    st.header("👤 Your Birth Profile")
    st.caption("Saved birth settings load automatically upon signing in.")

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
            "email": user_email,
            "name": name_in,
            "dob": dob_in,
            "tob": tob_in,
            "place": place_in,
            "lat": lat_in,
            "lon": lon_in,
            "tz_offset": 5.5,
            "nakshatra_idx": selected_nak_idx
        }
        st.session_state.current_profile = updated_prof
        if save_user_profile(user_email, updated_prof):
            st.success("✅ Profile successfully saved to your account!")

janma_idx = prof.get("nakshatra_idx", 1)
janma_name = NAKSHATRAS[janma_idx]

st.title("✨ Navtara Pulse")
st.markdown(
    f"Welcome, **{prof.get('name')}** | Janma Nakshatra: **{janma_name}** (`Index {janma_idx + 1}/27`) | Location: **{prof.get('place')}**"
)

tab1, tab2, tab3 = st.tabs([
    "🗓️ 7-Day Navtara Matrix",
    "🔮 Energy Forecast & Guidance",
    "🪐 Planetary Positions"
])

with tab1:
    st.subheader("Daily Moon Transition Table (Next 7 Days)")
    st.caption("Continuous lunar transits computed with Swiss Ephemeris Chitrapaksha Lahiri Ayanamsa.")

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

        start_ist = t["start"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M IST)")
        end_ist = t["end"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M IST)")

        table_rows.append({
            "Status": status_str,
            "Day, Date & Time to Day, Date & Time": f"**{start_ist} – {end_ist}**",
            "Nakshatra Name": f"**{nak_name}**",
            "Navtara Series": f"{cat} ({NAVTARA_DESCRIPTIONS.get(cat, '')}) — *Series {series}*"
        })

    st.table(table_rows)

with tab2:
    st.subheader("7-Day Transit Energy Forecast & Life Strategy")
    st.caption("Strategic guidance tailored to your Janma Nakshatra for each upcoming window.")

    guidance_map = {
        "Janma": "Focus on self-care, physical vitality, and routine grounding. Avoid starting high-strain structural tasks.",
        "Sampat": "Prime window for capital growth, investment evaluation, contract discussions, and financial planning.",
        "Vipat": "High-risk window. Avoid speculative trades, high-leverage positions, and unverified business commitments.",
        "Kshema": "Supportive and protective window. Excellent for health recovery, operational maintenance, and family time.",
        "Pratyari": "Keep communication gentle and diplomatic. Avoid arguments, confrontations, or aggressive sales negotiations.",
        "Sadhana": "Peak productivity window. Outstanding for completing complex research, technical challenges, and major milestones.",
        "Vadha": "Maximum caution window. Exercise restraint, keep physical strain low, and postpone non-essential high-stakes meetings.",
        "Mitra": "Friendly, cooperative energy. Ideal for networking, partnership building, and harmonious team collaboration.",
        "Ati-Mitra": "Supreme auspicious window. Highest support for ambitious launches, major milestones, and strategic decisions."
    }

    for idx, t in enumerate(transitions):
        nak_name = NAKSHATRAS[t["nak_idx"]]
        cat, series = calculate_navtara(janma_idx, t["nak_idx"])
        start_ist = t["start"].astimezone(ist_tz).strftime("%a, %d %b %H:%M")
        end_ist = t["end"].astimezone(ist_tz).strftime("%a, %d %b %H:%M IST")

        status_prefix = "🔴" if cat in ["Vipat", "Pratyari", "Vadha"] else ("🟢🟢" if cat == "Ati-Mitra" else ("🟢" if cat in ["Mitra", "Sampat"] else "⚪"))
        card_label = f"{status_prefix} {cat} — Moon in {nak_name} ({start_ist} to {end_ist})"

        with st.expander(card_label, expanded=(idx < 2)):
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.markdown(f"**Navtara Category:** {cat}")
                st.markdown(f"**Cycle Series:** Series {series}")
                st.markdown(f"**Core Archetype:** {NAVTARA_DESCRIPTIONS.get(cat, '')}")
            with col_b:
                st.markdown("**Operational Directive:**")
                st.write(guidance_map.get(cat, "Maintain steady, disciplined focus on ongoing priorities."))

with tab3:
    st.subheader("Current Sidereal Planetary Positions (Lahiri Ayanamsa)")
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
            "Planetary Body": name,
            "Sidereal Longitude": f"{lon:.2f}°",
            "Zodiac Sign (Rashi)": RASHIS[r_idx],
            "Degrees in Sign": f"{r_deg:.2f}°",
            "Nakshatra Placement": f"{NAKSHATRAS[n_idx]} (Pada {pada})"
        })

    # Ketu placement (180 degrees from Rahu)
    rahu_lon = get_sidereal_lon(jd_now, swe.MEAN_NODE)
    ketu_lon = (rahu_lon + 180.0) % 360.0
    kr_idx, kr_deg = lon_to_rashi(ketu_lon)
    kn_idx, k_pada = lon_to_nakshatra(ketu_lon)
    coords.append({
        "Planetary Body": "Ketu",
        "Sidereal Longitude": f"{ketu_lon:.2f}°",
        "Zodiac Sign (Rashi)": RASHIS[kr_idx],
        "Degrees in Sign": f"{kr_deg:.2f}°",
        "Nakshatra Placement": f"{NAKSHATRAS[kn_idx]} (Pada {k_pada})"
    })

    st.dataframe(coords, use_container_width=True)

st.divider()
st.caption("Navtara Pulse Engine • Powered by Swiss Ephemeris Chitrapaksha Lahiri Sidereal Astronomical Framework")
