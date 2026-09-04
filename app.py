import os
import json
import datetime
import streamlit as st

# Use Swiss Ephemeris (pyswisseph / pysweph)
try:
    import swisseph as swe
except ImportError:
    st.error("Missing library: Please ensure 'pyswisseph' is in your requirements.txt")
    st.stop()

# ---------------------------------------------------------
# CONSTANTS & DEFINITIONS
# ---------------------------------------------------------
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

NAVTARA_NAMES = [
    "Janma", "Sampat", "Vipat", "Kshema", "Pratyari",
    "Sadhana", "Vadha", "Mitra", "Ati-Mitra"
]

NAVTARA_DESCRIPTIONS = {
    "Janma": "Self / Body / New Cycles",
    "Sampat": "Wealth / Prosperity / Assets",
    "Vipat": "Obstacles / Caution / Danger",
    "Kshema": "Well-being / Protection / Comfort",
    "Pratyari": "Obstacles / Conflict / Opposition",
    "Sadhana": "Achievement / Focused Effort / Success",
    "Vadha": "Obstruction / High Risk / Restraint",
    "Mitra": "Friend / Favorable Alliances",
    "Ati-Mitra": "Great Friend / Highest Support"
}

PROFILE_FILE = "user_profile.json"

# ---------------------------------------------------------
# PROFILE PERSISTENCE HELPERS
# ---------------------------------------------------------
def load_user_profile():
    defaults = {
        "name": "User",
        "dob": datetime.date(1990, 1, 1),
        "tob": datetime.time(12, 0),
        "place": "Chhatrapati Sambhajinagar, India",
        "nakshatra_idx": 1  # Bharani (Index 1)
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

def save_user_profile(profile_data):
    try:
        data_to_save = profile_data.copy()
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
# ASTRONOMICAL COMPUTATIONS (SWISS EPHEMERIS)
# ---------------------------------------------------------
def get_sidereal_moon_lon(utc_dt):
    """Calculates sub-arcsecond Sidereal Moon longitude using Moshier Lahiri Ayanamsa."""
    # Convert datetime to Julian Day (UT)
    hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0 + (utc_dt.microsecond / 1e6) / 3600.0
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
    
    # 1. Geocentric Tropical Moon longitude (Moshier engine)
    res, _ = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_MOSEPH)
    trop_moon_lon = res[0]
    
    # 2. Lahiri Ayanamsa subtraction
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    
    sid_moon_lon = (trop_moon_lon - ayanamsa) % 360.0
    return sid_moon_lon

def get_nakshatra_from_lon(lon):
    nak_span = 360.0 / 27.0  # 13.333333333 degrees
    idx = int(lon / nak_span) % 27
    return idx

def calculate_navtara_category(birth_idx, transit_idx):
    """Computes Navtara category index (0 to 8) and Cycle/Series (1 to 3)."""
    offset = (transit_idx - birth_idx) % 27
    navtara_idx = offset % 9
    series = (offset // 9) + 1
    return NAVTARA_NAMES[navtara_idx], series

def find_exact_nakshatra_transitions(start_utc_dt, days=7):
    """Finds exact transition boundaries when the Moon crosses nakshatra spans."""
    nak_span = 360.0 / 27.0
    transitions = []
    
    current_time = start_utc_dt
    end_time = start_utc_dt + datetime.timedelta(days=days)
    
    cur_lon = get_sidereal_moon_lon(current_time)
    cur_nak = int(cur_lon / nak_span) % 27
    
    step = datetime.timedelta(minutes=30)
    eval_time = current_time
    
    interval_start = current_time
    active_nak = cur_nak
    
    while eval_time <= end_time:
        eval_time += step
        lon = get_sidereal_moon_lon(eval_time)
        nak = int(lon / nak_span) % 27
        
        if nak != active_nak:
            # Binary search refinement to 1-minute precision
            low = eval_time - step
            high = eval_time
            for _ in range(7):
                mid = low + (high - low) / 2
                mid_lon = get_sidereal_moon_lon(mid)
                mid_nak = int(mid_lon / nak_span) % 27
                if mid_nak == active_nak:
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

# ---------------------------------------------------------
# STREAMLIT UI CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Navtara Pulse", page_icon="✨", layout="wide")

if "profile" not in st.session_state:
    st.session_state.profile = load_user_profile()

prof = st.session_state.profile

# SIDEBAR: PERSISTENT PROFILE SETTINGS
with st.sidebar:
    st.header("👤 Your Birth Profile")
    st.caption("Saved details load automatically upon reopening.")
    
    name_input = st.text_input("Name", value=prof.get("name", "User"))
    dob_input = st.date_input(
        "Date of Birth",
        value=prof.get("dob", datetime.date(1990, 1, 1)),
        min_value=datetime.date(1930, 1, 1),
        max_value=datetime.date.today()
    )
    tob_input = st.time_input("Time of Birth", value=prof.get("tob", datetime.time(12, 0)))
    place_input = st.text_input("Birth Place / Location", value=prof.get("place", "Chhatrapati Sambhajinagar, India"))
    
    current_nak_idx = prof.get("nakshatra_idx", 1)  # Default: Bharani
    selected_nak = st.selectbox(
        "Janma Nakshatra",
        NAKSHATRAS,
        index=current_nak_idx
    )
    selected_nak_idx = NAKSHATRAS.index(selected_nak)
    
    if st.button("💾 Save Profile", use_container_width=True):
        new_prof = {
            "name": name_input,
            "dob": dob_input,
            "tob": tob_input,
            "place": place_input,
            "nakshatra_idx": selected_nak_idx
        }
        st.session_state.profile = new_prof
        if save_user_profile(new_prof):
            st.success("Profile saved permanently!")

# ---------------------------------------------------------
# MAIN VIEW: 7-DAY NAVTARA MATRIX
# ---------------------------------------------------------
janma_idx = prof.get("nakshatra_idx", 1)
user_name = prof.get("name", "User")
janma_name = NAKSHATRAS[janma_idx]

st.title("✨ Navtara Pulse")
st.subheader(f"7-Day Transit Matrix for {user_name} ({janma_name} Nakshatra)")

# Reference Time is Now (IST)
now_utc = datetime.datetime.now(datetime.timezone.utc)
transitions = find_exact_nakshatra_transitions(now_utc, days=7)

table_rows = []
ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

for t in transitions:
    nak_name = NAKSHATRAS[t["nak_idx"]]
    cat, series = calculate_navtara_category(janma_idx, t["nak_idx"])
    
    # Status formatting
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

st.markdown("### 🗓️ Daily Moon Transition Table")
st.table(table_rows)

st.markdown("---")
st.markdown("### 💡 Navtara Operational Rules")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🟢 Peak Opportunities")
    st.write("**Ati-Mitra (🟢🟢) & Sampat:** Best suited for high-stakes business decisions, financial transactions, signing agreements, and executing key plans.")

with col2:
    st.markdown("#### 🔴 Risk Windows")
    st.write("**Vipat, Pratyari, Vadha (🔴):** Exercise caution. Avoid initiating major structural modifications, heavy capital commitments, or entering unnecessary conflicts.")

with col3:
    st.markdown("#### ⚖️ Grounding & Achievement")
    st.write("**Kshema & Sadhana:** Ideal for health, system maintenance, deep research, disciplined learning, and completing pending tasks.")
