import os
import json
import datetime
import streamlit as st

# Swiss Ephemeris astronomical library import
try:
    import swisseph as swe
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False
    st.error("🚨 **Missing Library Error:** `pyswisseph` is not installed in your environment.")
    st.warning("⚡ Add `pyswisseph` to your `requirements.txt` file in your repository.")
    st.info("If running locally on your computer, run:")
    st.code("pip install pyswisseph streamlit", language="bash")
    st.stop()

st.set_page_config(
    page_title="Navtara Pulse",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Hide Streamlit default headers & footers for native app feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Make block container adapt gracefully to mobile screens */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 680px !important;
        margin: 0 auto !important;
    }
    
    /* Legible inputs and labels for mobile touch screens */
    label {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
    }
    
    input[type="text"], select {
        font-size: 16px !important;
        min-height: 48px !important;
        border-radius: 12px !important;
        padding: 8px 12px !important;
    }
    
    /* Touch-friendly full-width action buttons */
    .stButton > button {
        font-size: 16px !important;
        font-weight: 700 !important;
        min-height: 50px !important;
        border-radius: 14px !important;
        width: 100% !important;
        transition: all 0.2s ease-in-out !important;
    }

    h1 {
        font-size: 2.05rem !important;
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

    /* Hero Brand & Emblem Styles */
    .hero-brand-container {
        text-align: center;
        padding-top: 0.2rem;
        margin-bottom: 0.8rem;
    }

    .brand-logo-emblem {
        width: 74px;
        height: 74px;
        margin: 0 auto 10px auto;
        border-radius: 22px;
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
        margin-bottom: 8px !important;
        letter-spacing: 0.2px;
    }

    /* Active Native Status Banner */
    .user-status-card {
        background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
        border: 1.5px solid #bfdbfe;
        border-radius: 16px;
        padding: 14px 16px;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08);
        text-align: center;
    }

    .user-status-card b {
        color: #1e1b4b;
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

PROFILE_FILE = "user_profile.json"

def load_user_profile() -> dict:
    """Loads saved birth profile from local storage or returns sensible defaults."""
    defaults = {
        "name": "Okesh",
        "dob": datetime.date(1984, 1, 13),
        "tob": datetime.time(14, 0),
        "place": "Chhatrapati Sambhajinagar, India",
        "lat": 19.8762,
        "lon": 75.3433,
        "tz_offset": 5.5,
        "nakshatra_idx": 1  # Default: Bharani (Index 1)
    }
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                saved = json.load(f)
                if "dob" in saved and isinstance(saved["dob"], str):
                    try:
                        saved["dob"] = datetime.date.fromisoformat(saved["dob"])
                    except ValueError:
                        pass
                if "tob" in saved and isinstance(saved["tob"], str):
                    try:
                        saved["tob"] = datetime.time.fromisoformat(saved["tob"])
                    except ValueError:
                        pass
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_user_profile(profile_data: dict) -> bool:
    """Saves user birth parameters to user_profile.json."""
    try:
        to_store = profile_data.copy()
        if isinstance(to_store.get("dob"), (datetime.date, datetime.datetime)):
            to_store["dob"] = to_store["dob"].isoformat()
        if isinstance(to_store.get("tob"), datetime.time):
            to_store["tob"] = to_store["tob"].isoformat()
        with open(PROFILE_FILE, "w") as f:
            json.dump(to_store, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return False

def dt_to_jd(utc_dt: datetime.datetime) -> float:
    hour_decimal = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + utc_dt.second / 3600.0
        + (utc_dt.microsecond / 1e6) / 3600.0
    )
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)

def get_sidereal_lon(jd_ut: float, planet_id: int) -> float:
    """Calculates sub-arcsecond Sidereal longitude using Moshier Lahiri Ayanamsa."""
    res, _ = swe.calc_ut(jd_ut, planet_id, swe.FLG_MOSEPH)
    trop_lon = res[0]
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    return (trop_lon - ayanamsa) % 360.0

def lon_to_nakshatra(lon: float):
    nak_span = 360.0 / 27.0
    idx = int(lon / nak_span) % 27
    pada = int((lon % nak_span) / (nak_span / 4.0)) + 1
    return idx, pada

def lon_to_rashi(lon: float):
    return int(lon / 30.0) % 12, lon % 30.0

def calculate_navtara(birth_idx: int, transit_idx: int):
    offset = (transit_idx - birth_idx) % 27
    return NAVTARA_NAMES[offset % 9], (offset // 9) + 1

def find_7day_transitions(start_utc_dt: datetime.datetime):
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
            # Binary search refinement to 1-minute precision
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

if "profile" not in st.session_state:
    st.session_state.profile = load_user_profile()

prof = st.session_state.profile

with st.sidebar:
    st.header("👤 Your Birth Profile")
    st.caption("Customize your details here. They are saved automatically.")

    name_in = st.text_input("Full Name", value=prof.get("name", "Okesh"))
    dob_in = st.date_input("Date of Birth", value=prof.get("dob", datetime.date(1984, 1, 13)))
    tob_in = st.time_input("Time of Birth", value=prof.get("tob", datetime.time(14, 0)))
    place_in = st.text_input("Birth Place / City", value=prof.get("place", "Chhatrapati Sambhajinagar, India"))

    lat_in = st.number_input("Latitude", value=float(prof.get("lat", 19.8762)), format="%.4f")
    lon_in = st.number_input("Longitude", value=float(prof.get("lon", 75.3433)), format="%.4f")

    selected_nak = st.selectbox(
        "Janma Nakshatra",
        NAKSHATRAS,
        index=prof.get("nakshatra_idx", 1)  # Default: Bharani (Index 1)
    )
    selected_nak_idx = NAKSHATRAS.index(selected_nak)

    if st.button("💾 Save Profile", use_container_width=True, type="primary"):
        updated_prof = {
            "name": name_in,
            "dob": dob_in,
            "tob": tob_in,
            "place": place_in,
            "lat": lat_in,
            "lon": lon_in,
            "tz_offset": 5.5,
            "nakshatra_idx": selected_nak_idx
        }
        st.session_state.profile = updated_prof
        if save_user_profile(updated_prof):
            st.success("✅ Profile successfully saved!")

janma_idx = prof.get("nakshatra_idx", 1)
janma_name = NAKSHATRAS[janma_idx]

st.markdown("""
<div class="hero-brand-container">
    <div class="brand-logo-emblem">
        <svg width="46" height="46" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="44" stroke="url(#cosmicGrad)" stroke-width="2" stroke-dasharray="4 3" opacity="0.65"/>
            <path d="M56 22C41 22 29 34 29 49C29 64 41 76 56 76C46 76 38 67 38 53C38 39 47 25 56 22Z" fill="url(#goldGrad)" filter="drop-shadow(0 2px 6px rgba(245,158,11,0.5))"/>
            <path d="M56 36L58.5 45.5L68 47L59.5 51L61 60.5L53.5 54L45.5 59.5L48.5 50.5L41 45.5L50.5 45L56 36Z" fill="#ffffff"/>
            <circle cx="54" cy="49" r="3.5" fill="#f43f5e"/>
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

st.markdown(f"""
<div class="user-status-card">
    Welcome, <b>{prof.get('name', 'User')}</b><br>
    Janma Nakshatra: <b>{janma_name}</b> (<code>#{janma_idx + 1}/27</code>) • Location: <b>{prof.get('place')}</b>
</div>
""", unsafe_allow_html=True)

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
            "Day, Date & Time Range (IST)": f"{start_ist} – {end_ist}",
            "Nakshatra Name": f"{nak_name}",
            "Navtara Series": f"{cat} ({series})"
        })

    st.dataframe(table_rows, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("7-Day Energy Forecast & Guidance")
    st.caption(f"Actionable strategies tailored for {janma_name} natives.")

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
