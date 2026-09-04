import os
import json
import datetime
import streamlit as st

# Swiss Ephemeris import
try:
    import swisseph as swe
except ImportError:
    st.error("Missing library: Please make sure 'pyswisseph' is in your requirements.txt")
    st.stop()

# ---------------------------------------------------------
# CONFIG & CONSTANTS
# ---------------------------------------------------------
st.set_page_config(page_title="Navtara Pulse", page_icon="✨", layout="wide")

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
    "Janma": "Self / Physical Energy / Foundations",
    "Sampat": "Wealth / Financial Gains / Material Prosperity",
    "Vipat": "Obstacles / High Risk / Caution Required",
    "Kshema": "Well-being / Comfort / Protection",
    "Pratyari": "Conflict / Resistance / Differences of Opinion",
    "Sadhana": "Achievement / Focused Effort / Success",
    "Vadha": "Destruction / Vulnerability / Total Restraint",
    "Mitra": "Friendship / Favorable Assistance",
    "Ati-Mitra": "Supreme Support / Highest Success Rate"
}

PROFILE_FILE = "user_profile.json"

# ---------------------------------------------------------
# PERSISTENCE HELPERS
# ---------------------------------------------------------
def load_user_profile():
    defaults = {
        "name": "User",
        "dob": datetime.date(1990, 1, 1),
        "tob": datetime.time(12, 0),
        "place": "Chhatrapati Sambhajinagar, India",
        "lat": 19.8762,
        "lon": 75.3433,
        "tz_offset": 5.5,
        "nakshatra_idx": 1  # Bharani
    }
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                saved = json.load(f)
                if "dob" in saved:
                    saved["dob"] = datetime.date.fromisoformat(saved["dob"])
                if "tob" in saved:
                    saved["tob"] = datetime.time.fromisoformat(saved["tob"])
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_user_profile(data):
    try:
        data_to_save = data.copy()
        if isinstance(data_to_save.get("dob"), (datetime.date, datetime.datetime)):
            data_to_save["dob"] = data_to_save["dob"].isoformat()
        if isinstance(data_to_save.get("tob"), datetime.time):
            data_to_save["tob"] = data_to_save["tob"].isoformat()
        with open(PROFILE_FILE, "w") as f:
            json.dump(data_to_save, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return False

# ---------------------------------------------------------
# ASTRONOMICAL CALCULATIONS (SWISS EPHEMERIS)
# ---------------------------------------------------------
def dt_to_jd(utc_dt):
    hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0 + (utc_dt.microsecond / 1e6) / 3600.0
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)

def get_sidereal_lon(jd_ut, planet_id):
    """Calculates Lahiri sidereal longitude using Moshier analytical model."""
    res, _ = swe.calc_ut(jd_ut, planet_id, swe.FLG_MOSEPH)
    trop_lon = res[0]
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    return (trop_lon - ayanamsa) % 360.0

def get_lagna_lon(jd_ut, lat, lon):
    """Calculates sidereal Ascendant (Lagna)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    houses, ascmc = swe.houses(jd_ut, lat, lon, b'P')
    trop_asc = ascmc[0]
    return (trop_asc - ayanamsa) % 360.0

def lon_to_nakshatra(lon):
    nak_span = 360.0 / 27.0
    idx = int(lon / nak_span) % 27
    pada = int((lon % nak_span) / (nak_span / 4.0)) + 1
    return idx, pada

def lon_to_rashi(lon):
    rashi_idx = int(lon / 30.0) % 12
    deg_in_rashi = lon % 30.0
    return rashi_idx, deg_in_rashi

def calculate_navtara(birth_idx, transit_idx):
    offset = (transit_idx - birth_idx) % 27
    nav_idx = offset % 9
    series = (offset // 9) + 1
    return NAVTARA_NAMES[nav_idx], series

def get_birth_planetary_positions(birth_utc_dt, lat, lon):
    jd_ut = dt_to_jd(birth_utc_dt)
    planets = [
        ("Sun", swe.SUN),
        ("Moon", swe.MOON),
        ("Mars", swe.MARS),
        ("Mercury", swe.MERCURY),
        ("Jupiter", swe.JUPITER),
        ("Venus", swe.VENUS),
        ("Saturn", swe.SATURN),
        ("Rahu", swe.MEAN_NODE)
    ]
    positions = []
    
    # Lagna
    lagna_lon = get_lagna_lon(jd_ut, lat, lon)
    l_rashi, l_deg = lon_to_rashi(lagna_lon)
    l_nak, l_pada = lon_to_nakshatra(lagna_lon)
    positions.append({
        "Body": "Lagna (Ascendant)",
        "Longitude": f"{lagna_lon:.2f}°",
        "Rashi": RASHIS[l_rashi],
        "Rashi Deg": f"{l_deg:.2f}°",
        "Nakshatra": f"{NAKSHATRAS[l_nak]} (Pada {l_pada})"
    })
    
    # Planets
    for name, pid in planets:
        p_lon = get_sidereal_lon(jd_ut, pid)
        r_idx, r_deg = lon_to_rashi(p_lon)
        n_idx, pada = lon_to_nakshatra(p_lon)
        positions.append({
            "Body": name,
            "Longitude": f"{p_lon:.2f}°",
            "Rashi": RASHIS[r_idx],
            "Rashi Deg": f"{r_deg:.2f}°",
            "Nakshatra": f"{NAKSHATRAS[n_idx]} (Pada {pada})"
        })
        
    # Ketu (180 deg from Rahu)
    rahu_lon = get_sidereal_lon(jd_ut, swe.MEAN_NODE)
    ketu_lon = (rahu_lon + 180.0) % 360.0
    kr_idx, kr_deg = lon_to_rashi(ketu_lon)
    kn_idx, k_pada = lon_to_nakshatra(ketu_lon)
    positions.append({
        "Body": "Ketu",
        "Longitude": f"{ketu_lon:.2f}°",
        "Rashi": RASHIS[kr_idx],
        "Rashi Deg": f"{kr_deg:.2f}°",
        "Nakshatra": f"{NAKSHATRAS[kn_idx]} (Pada {k_pada})"
    })
    
    return positions, lagna_lon

def find_7day_transitions(start_utc_dt):
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
            # Binary search for boundary
            low = eval_time - step
            high = eval_time
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

def get_horoscope_for_navtara(navtara_name):
    predictions = {
        "Janma": "Focus on personal health, meditation, and physical revitalization. Avoid over-exerting yourself.",
        "Sampat": "Favorable day for financial inflows, investment evaluations, wealth planning, and resource growth.",
        "Vipat": "Potential for unexpected delays, equipment issues, or friction. Avoid taking speculative risks.",
        "Kshema": "Smooth, peaceful energy. Great for recovery, system maintenance, quality assurance, and family time.",
        "Pratyari": "Keep interactions diplomatic. Avoid confrontations or arguments with colleagues or competitors.",
        "Sadhana": "Productive and goal-driven. Ideal for technical problem-solving, focused research, and major achievements.",
        "Vadha": "Exercise maximum restraint. Postpone high-stakes meetings or travel; focus on peaceful, routine tasks.",
        "Mitra": "Friendly, collaborative vibes. Networking, joint agreements, and cooperative tasks yield positive results.",
        "Ati-Mitra": "Peak auspicious transit. Highest support for ambitious decisions, key meetings, and milestone launches."
    }
    return predictions.get(navtara_name, "Steady day for routine progress.")

# ---------------------------------------------------------
# SESSION STATE & SIDEBAR
# ---------------------------------------------------------
if "profile" not in st.session_state:
    st.session_state.profile = load_user_profile()

prof = st.session_state.profile

with st.sidebar:
    st.header("👤 Birth Details & Profile")
    st.caption("Settings are saved automatically to your profile.")
    
    name_input = st.text_input("Full Name", value=prof.get("name", "User"))
    dob_input = st.date_input(
        "Date of Birth",
        value=prof.get("dob", datetime.date(1990, 1, 1)),
        min_value=datetime.date(1930, 1, 1),
        max_value=datetime.date.today()
    )
    tob_input = st.time_input("Time of Birth", value=prof.get("tob", datetime.time(12, 0)))
    place_input = st.text_input("Birth Place", value=prof.get("place", "Chhatrapati Sambhajinagar, India"))
    
    lat_val = st.number_input("Latitude", value=float(prof.get("lat", 19.8762)), format="%.4f")
    lon_val = st.number_input("Longitude", value=float(prof.get("lon", 75.3433)), format="%.4f")
    
    selected_nak = st.selectbox(
        "Janma Nakshatra",
        NAKSHATRAS,
        index=prof.get("nakshatra_idx", 1)  # Default: Bharani
    )
    selected_nak_idx = NAKSHATRAS.index(selected_nak)
    
    if st.button("💾 Save Profile", use_container_width=True):
        new_prof = {
            "name": name_input,
            "dob": dob_input,
            "tob": tob_input,
            "place": place_input,
            "lat": lat_val,
            "lon": lon_val,
            "tz_offset": 5.5,
            "nakshatra_idx": selected_nak_idx
        }
        st.session_state.profile = new_prof
        if save_user_profile(new_prof):
            st.success("Details saved! They will load automatically on next launch.")

# ---------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------
janma_idx = prof.get("nakshatra_idx", 1)
user_name = prof.get("name", "User")
janma_name = NAKSHATRAS[janma_idx]

st.title(f"✨ Navtara Pulse: {user_name}")
st.markdown(f"**Janma Nakshatra:** `{janma_name}` (Index {janma_idx + 1}/27) | **Location:** `{prof.get('place')}`")

tab1, tab2, tab3 = st.tabs(["🗓️ 7-Day Navtara Matrix", "🔮 Daily Transit Horoscope", "🪐 Kundli & Planetary Positions"])

# ---------------------------------------------------------
# TAB 1: 7-DAY NAVTARA MATRIX
# ---------------------------------------------------------
with tab1:
    st.subheader("Daily Moon Transition Table (Next 7 Days)")
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    transitions = find_7day_transitions(now_utc)
    
    table_rows = []
    for t in transitions:
        nak_name = NAKSHATRAS[t["nak_idx"]]
        cat, series = calculate_navtara(janma_idx, t["nak_idx"])
        
        # Color coding indicators
        if cat in ["Vipat", "Pratyari", "Vadha"]:
            status = f"🔴 {cat}"
        elif cat == "Ati-Mitra":
            status = "🟢🟢 Ati-Mitra"
        elif cat == "Mitra":
            status = "🟢 Mitra"
        else:
            status = cat
            
        start_ist = t["start"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M IST)")
        end_ist = t["end"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M IST)")
        date_range = f"**{start_ist} – {end_ist}**"
        series_info = f"{cat} ({NAVTARA_DESCRIPTIONS.get(cat, '')}) — *Series {series}*"
        
        table_rows.append({
            "Status": status,
            "Day, Date & Time to Day, Date & Time": date_range,
            "Nakshatra Name": f"**{nak_name}**",
            "Navtara Series": series_info
        })
        
    st.table(table_rows)

# ---------------------------------------------------------
# TAB 2: DAILY TRANSIT HOROSCOPE
# ---------------------------------------------------------
with tab2:
    st.subheader("7-Day Transit Horoscope & Energy Forecast")
    st.caption("Actionable guidance tailored to your Janma Nakshatra for each upcoming window.")
    
    for idx, t in enumerate(transitions):
        nak_name = NAKSHATRAS[t["nak_idx"]]
        cat, series = calculate_navtara(janma_idx, t["nak_idx"])
        start_ist = t["start"].astimezone(ist_tz).strftime("%a, %d %b %H:%M")
        end_ist = t["end"].astimezone(ist_tz).strftime("%a, %d %b %H:%M IST")
        
        if cat in ["Vipat", "Pratyari", "Vadha"]:
            card_title = f"🔴 {cat} — Moon in {nak_name}"
        elif cat == "Ati-Mitra":
            card_title = f"🟢🟢 Ati-Mitra — Moon in {nak_name}"
        elif cat in ["Mitra", "Sampat"]:
            card_title = f"🟢 {cat} — Moon in {nak_name}"
        else:
            card_title = f"⚪ {cat} — Moon in {nak_name}"
            
        with st.expander(f"{card_title} ({start_ist} to {end_ist})", expanded=(idx < 2)):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"**Classification:** {cat}")
                st.markdown(f"**Navtara Cycle:** Series {series}")
                st.markdown(f"**Core Theme:** {NAVTARA_DESCRIPTIONS.get(cat, '')}")
            with c2:
                st.markdown("**Guidance:**")
                st.write(get_horoscope_for_navtara(cat))

# ---------------------------------------------------------
# TAB 3: KUNDLI & PLANETARY POSITIONS
# ---------------------------------------------------------
with tab3:
    st.subheader("Birth Kundli & Planetary Positions")
    
    # Calculate birth coordinates
    b_date = prof.get("dob", datetime.date(1990, 1, 1))
    b_time = prof.get("tob", datetime.time(12, 0))
    b_local = datetime.datetime.combine(b_date, b_time)
    b_utc = b_local - datetime.timedelta(hours=prof.get("tz_offset", 5.5))
    
    positions, lagna_lon = get_birth_planetary_positions(b_utc, prof.get("lat", 19.8762), prof.get("lon", 75.3433))
    
    col_chart, col_table = st.columns([1, 1])
    
    with col_chart:
        st.markdown("#### 🏛️ Rashi Chart Summary")
        lagna_rashi_idx, _ = lon_to_rashi(lagna_lon)
        st.info(f"**Lagna (Ascendant):** {RASHIS[lagna_rashi_idx]}")
        st.write("Planetary placements in your natal chart:")
        for pos in positions:
            st.markdown(f"- **{pos['Body']}**: {pos['Rashi']} at `{pos['Rashi Deg']}` ({pos['Nakshatra']})")
            
    with col_table:
        st.markdown("#### 📐 Ephemeris Coordinates Table")
        st.dataframe(positions, use_container_width=True)

st.markdown("---")
st.caption("Navtara Pulse Engine • Swiss Ephemeris Chitrapaksha Lahiri Sidereal Framework")
