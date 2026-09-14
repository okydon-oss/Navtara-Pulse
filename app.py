import streamlit as st
import datetime
import urllib.parse
import json
import os
import math

# Geocoding engine imports
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False

# Swiss Ephemeris imports
try:
    import swisseph as swe
    HAS_SWISSEPH = True
    swe.set_sid_mode(swe.SIDM_LAHIRI)
except Exception:
    HAS_SWISSEPH = False

# Import data banks from databanks.py
from databanks import (
    NAKSHATRAS,
    RASHIS,
    NAVTARA_NAMES,
    SHANI_VAHANS,
    CHALDEAN_MAP,
    NUM_PLANET_NAMES,
    CITY_COORDINATES,
    NAKSHATRA_BIO_DATA,
    NAKSHATRA_RICH_PROFILES,
    RASHI_RICH_PROFILES,
    LAGNA_RICH_PROFILES,
    SHANI_PAYA_ENCYCLOPEDIA,
    SADE_SATI_PHASE_ENCYCLOPEDIA,
    DHAIYA_ENCYCLOPEDIA,
    get_nakshatra_rich_data,
    get_rashi_rich_data,
    get_lagna_rich_data
    NAVAGRAHA_BEEJ_MANTRAS,
    NAKSHATRA_BEEJ_MANTRAS
)

# Configure Streamlit page settings
st.set_page_config(
    page_title="Navtara Pulse",
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
        "app_subtitle": "Vedic Nakshatra Rhythm & Cosmic Precision",
        "btn_about": "✨ About App",
        "btn_user_profile": "👤 User Profile",
        "btn_numerology": "🔢 Numerology",
        "btn_shani": "🪐 Shani & Sade Sati",
        "btn_live": "⚡ Live Prediction",
        "btn_forecast": "🗓️ 7 Days Prediction",
        "btn_mantra": "📿 Mantra Sadhana",
        "edit_details": "✏️ Edit Details",
        "save_details": "💾 Save Profile",
        "cancel": "Cancel",
        "name_label": "Full Name",
        "dob_label": "Birth Date",
        "tob_label": "Birth Time",
        "city_label": "Birth Location / City Name",
        "nakshatra_label": "Janma Nakshatra",
        "pada_label": "Pada (Quarter)",
        "moon_rashi_label": "Moon Sign (Rashi)",
        "lagna_label": "Ascendant (Lagna)",
        "mulank_label": "Mulank (Driver)",
        "bhagyank_label": "Bhagyank (Destiny)",
        "namank_label": "Namank (Name Vibration)",
        "shani_paya_title": "🪐 Shani Paya & Active 2.5-Year Transit",
        "sadesati_title": "⚖️ Shani Sade Sati & Dhaiya Status",
        "live_pulse_title": "⚡ Today's Live Cosmic Pulse",
        "forecast_title": "🗓️ 7-Day Moon Transit Matrix & Daily Forecasts",
        "share_title": "📲 Share Navtara Pulse With Friends & Family"
    },
    "hi": {
        "app_title": "✨ नवतारा पल्स (Navtara Pulse)",
        "app_subtitle": "वैदिक नक्षत्र गोचर एवं खगोलीय ऊर्जा चक्र",
        "btn_about": "✨ ऐप परिचय",
        "btn_user_profile": "👤 यूज़र प्रोफाइल",
        "btn_numerology": "🔢 अंकशास्त्र",
        "btn_shani": "🪐 शनि एवं साढ़े साती",
        "btn_live": "⚡ आज का फल",
        "btn_forecast": "🗓️ 7 दिवसीय फल",
        "btn_mantra": "📿 मंत्र साधना",
        "edit_details": "✏️ विवरण बदलें",
        "save_details": "💾 सुरक्षित करें",
        "cancel": "रद्द करें",
        "name_label": "पूरा नाम",
        "dob_label": "जन्म तिथि",
        "tob_label": "जन्म समय",
        "city_label": "जन्म स्थान का नाम",
        "nakshatra_label": "जन्म नक्षत्र",
        "pada_label": "चरण",
        "moon_rashi_label": "चन्द्र राशि",
        "lagna_label": "लग्न राशि",
        "mulank_label": "मूलांक (Driver)",
        "bhagyank_label": "भाग्यांक (Conductor)",
        "namank_label": "नामांक (Name Vibration)",
        "shani_paya_title": "🪐 वर्तमान शनि पाया एवं 2.5 वर्षीय गोचर",
        "sadesati_title": "⚖️ शनि साढ़े साती एवं ढैय्या स्थिति",
        "live_pulse_title": "⚡ आज का दैनिक खगोलीय प्रवाह",
        "forecast_title": "🗓️ आगामी 7 दिनों का नक्षत्र गोचर एवं दैनिक फल",
        "share_title": "📲 नवतारा पल्स को परिवार व मित्रों के साथ साझा करें"
    }
}

def t(key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))

# DYNAMIC LOCATION RESOLVER (Handles ANY city, town, village or direct coordinates)
def resolve_location_name(place_query: str):
    if not place_query or not place_query.strip():
        return 28.6139, 77.2090, "New Delhi, India"
    
    clean_q = place_query.strip()
    
    # 1. Direct Decimal Coordinates Check (e.g. "19.8762, 75.3433")
    if "," in clean_q:
        parts = clean_q.split(",")
        if len(parts) == 2:
            try:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                    return lat, lon, clean_q
            except ValueError:
                pass

    # 2. Fast Offline Cache Check
    for name, coords in CITY_COORDINATES.items():
        if clean_q.lower() in name.lower() or any(part.strip().lower() in name.lower() for part in clean_q.split(',')):
            return coords[0], coords[1], name

    # 3. Dynamic Global Search via OpenStreetMap (Nominatim)
    if HAS_GEOPY:
        try:
            geolocator = Nominatim(user_agent="navtara_pulse_dynamic_geocoder", timeout=6)
            loc = geolocator.geocode(clean_q, language="en")
            if loc:
                return float(loc.latitude), float(loc.longitude), loc.address
        except Exception:
            pass

    # Safe emergency fallback
    return 28.6139, 77.2090, clean_q

def get_tara_bala_info(user_star_idx: int, partner_star_idx: int):
    offset = (partner_star_idx - user_star_idx) % 9
    tara_name, icon, quality = NAVTARA_NAMES[offset]
    is_allied = offset in [1, 3, 5, 7, 8]
    is_friction = offset in [2, 4, 6]
    
    if is_allied:
        relationship_tone = "High Harmonic Resonance (Constructive Growth & Mutual Trust)"
        advice = "Partnership naturally expands capital, strategic execution, and emotional ease. Communication flows with minimal resistance."
    elif is_friction:
        relationship_tone = "Testing & High Friction (Demands Clear Boundaries & Patience)"
        advice = "Differences in communication tempo or expectations can trigger misunderstandings. Ensure all commitments are formally written."
    else:
        relationship_tone = "Mirror / Foundational Synergy (Intense Alignment & Reflective Growth)"
        advice = "High mutual identification. Both individuals share foundational biorhythms; great for long-term loyalty if ego boundaries remain healthy."

    return {
        "tara_name": tara_name,
        "icon": icon,
        "quality": quality,
        "is_allied": is_allied,
        "is_friction": is_friction,
        "relationship_tone": relationship_tone,
        "advice": advice
    }

def get_julian_day(utc_dt: datetime.datetime) -> float:
    y = utc_dt.year
    m = utc_dt.month
    d = utc_dt.day + (utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0) / 24.0
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5

def get_approx_lahiri_ayanamsa(jd: float) -> float:
    t_val = (jd - 2451545.0) / 36525.0
    return 23.85848 + 1.396042 * t_val + 0.000308 * (t_val ** 2)

def calculate_sidereal_ascendant(utc_dt: datetime.datetime, lat: float, lon: float) -> float:
    jd = get_julian_day(utc_dt)
    if HAS_SWISSEPH:
        try:
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            ayanamsa = swe.get_ayanamsa_ut(jd)
            cusps, ascmc = swe.houses(jd, lat, lon, b'P')
            return float((ascmc[0] - ayanamsa) % 360.0)
        except Exception:
            pass

    t_val = (jd - 2451545.0) / 36525.0
    gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * (t_val**2) - (t_val**3) / 38710000.0) % 360.0
    lst = (gmst + lon) % 360.0
    eps = 23.439291 - 0.0130042 * t_val
    
    eps_rad = math.radians(eps)
    lat_rad = math.radians(lat)
    lst_rad = math.radians(lst)
    
    y = math.cos(lst_rad)
    x = - (math.sin(lst_rad) * math.cos(eps_rad) + math.tan(lat_rad) * math.sin(eps_rad))
    tropical_asc = math.degrees(math.atan2(y, x)) % 360.0
    
    ayanamsa = get_approx_lahiri_ayanamsa(jd)
    return float((tropical_asc - ayanamsa) % 360.0)

def get_sidereal_moon_longitude(utc_dt: datetime.datetime) -> float:
    if utc_dt.tzinfo is not None:
        utc_dt = utc_dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)

    jd = get_julian_day(utc_dt)
    if HAS_SWISSEPH:
        try:
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            res = swe.calc_ut(jd, swe.MOON, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)
            res_val = res[0] if isinstance(res, (tuple, list)) else res
            lon = res_val[0] if isinstance(res_val, (tuple, list)) else res_val
            return float(lon % 360.0)
        except Exception:
            try:
                res = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
                res_val = res[0] if isinstance(res, (tuple, list)) else res
                lon = res_val[0] if isinstance(res_val, (tuple, list)) else res_val
                return float(lon % 360.0)
            except Exception:
                pass

    d = jd - 2451545.0
    moon_mean_lon = (218.316 + 13.176396 * d) % 360.0
    sun_mean_lon = (280.466 + 0.9856474 * d) % 360.0
    sun_mean_anom = math.radians((357.528 + 0.9856003 * d) % 360.0)
    moon_mean_anom = math.radians((134.963 + 13.064993 * d) % 360.0)
    
    evec = 1.274 * math.sin(2 * math.radians(moon_mean_lon - sun_mean_lon) - moon_mean_anom)
    eq_center = 6.289 * math.sin(moon_mean_anom)
    var = 0.658 * math.sin(2 * math.radians(moon_mean_lon - sun_mean_lon))
    tropical_moon = (moon_mean_lon + eq_center + evec + var) % 360.0
    
    ayanamsa = get_approx_lahiri_ayanamsa(jd)
    return float((tropical_moon - ayanamsa) % 360.0)

def calculate_birth_chart(dob: datetime.date, tob: datetime.time, lat: float, lon: float):
    ist_dt = datetime.datetime.combine(dob, tob)
    utc_dt = ist_dt - datetime.timedelta(hours=5, minutes=30)
    
    moon_lon = get_sidereal_moon_longitude(utc_dt)
    star_span = 360.0 / 27.0
    star_idx = max(1, min(27, int(moon_lon / star_span) + 1))
    rem_deg = moon_lon % star_span
    pada = max(1, min(4, int(rem_deg / (star_span / 4.0)) + 1))
    moon_rashi_idx = max(0, min(11, int(moon_lon / 30.0)))

    lagna_lon = calculate_sidereal_ascendant(utc_dt, lat, lon)
    lagna_idx = max(0, min(11, int(lagna_lon / 30.0)))

    return {
        "star_idx": star_idx,
        "star_name": NAKSHATRAS[star_idx - 1],
        "pada": pada,
        "moon_lon": moon_lon,
        "moon_rashi_idx": moon_rashi_idx,
        "moon_rashi_name": RASHIS[moon_rashi_idx],
        "lagna_lon": lagna_lon,
        "lagna_deg": f"{int(lagna_lon % 30)}° {int(((lagna_lon % 30) % 1) * 60)}'",
        "lagna_idx": lagna_idx,
        "lagna_name": RASHIS[lagna_idx]
    }

def calculate_shani_paya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    house_diff = (moon_rashi_idx - saturn_transit_rashi_idx) % 12 + 1
    m_name = RASHIS[moon_rashi_idx].split()[0]
    
    if house_diff in [2, 5, 9]:
        metal = "Silver"
    elif house_diff in [3, 7, 10]:
        metal = "Copper"
    elif house_diff in [1, 6, 11]:
        metal = "Gold"
    else:
        metal = "Iron"

    ency = SHANI_PAYA_ENCYCLOPEDIA[metal]
    
    return {
        "paya": ency["title"],
        "metal": metal,
        "status": ency["grade"],
        "tone": ency["tone"],
        "houses": ency["houses"],
        "health": ency["health"],
        "wealth": ency["wealth"],
        "family": ency["family"],
        "loan": ency["loan"],
        "partner": ency["partner"],
        "luck": ency["luck"],
        "career": ency["career"],
        "protocol": ency["protocol"],
        "desc": f"Saturn is currently transiting the {house_diff}th house relative to your {m_name} Moon, arriving on {metal} Feet.",
        "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces / Meena Rashi)"
    }

def calculate_shani_sadesati_dhaiya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    diff = (saturn_transit_rashi_idx - moon_rashi_idx) % 12
    m_name = RASHIS[moon_rashi_idx].split()[0]

    rashi_12th = RASHIS[(moon_rashi_idx - 1) % 12].split()[0]
    rashi_1st = m_name
    rashi_2nd = RASHIS[(moon_rashi_idx + 1) % 12].split()[0]

    if diff == 11:
        p_info = SADE_SATI_PHASE_ENCYCLOPEDIA[1]
        return {
            "active": True,
            "status_title": p_info["phase_name"],
            "phase_num": 1,
            "focus": p_info["focus"],
            "health": p_info["health"],
            "wealth": p_info["wealth"],
            "family": p_info["family"],
            "loan": p_info["loan"],
            "partner": p_info["partner"],
            "luck": p_info["luck"],
            "career": p_info["career"],
            "remedy": p_info["remedy"],
            "impact": f"Saturn currently transits your 12th house in {RASHIS[saturn_transit_rashi_idx].split()[0]} relative to your {m_name} Moon.",
            "dates": "Active Phase (29 March 2025 – 23 February 2028)",
            "phase_1_active": True, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 0:
        p_info = SADE_SATI_PHASE_ENCYCLOPEDIA[2]
        return {
            "active": True,
            "status_title": p_info["phase_name"],
            "phase_num": 2,
            "focus": p_info["focus"],
            "health": p_info["health"],
            "wealth": p_info["wealth"],
            "family": p_info["family"],
            "loan": p_info["loan"],
            "partner": p_info["partner"],
            "luck": p_info["luck"],
            "career": p_info["career"],
            "remedy": p_info["remedy"],
            "impact": f"Saturn transits directly over your natal Moon in {m_name} (Janma Shani). Character crucible and endurance test.",
            "dates": "Active Peak Phase (29 March 2025 – 23 February 2028)",
            "phase_1_active": False, "phase_2_active": True, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 1:
        p_info = SADE_SATI_PHASE_ENCYCLOPEDIA[3]
        return {
            "active": True,
            "status_title": p_info["phase_name"],
            "phase_num": 3,
            "focus": p_info["focus"],
            "health": p_info["health"],
            "wealth": p_info["wealth"],
            "family": p_info["family"],
            "loan": p_info["loan"],
            "partner": p_info["partner"],
            "luck": p_info["luck"],
            "career": p_info["career"],
            "remedy": p_info["remedy"],
            "impact": f"Saturn transits the 2nd house from your {m_name} Moon. Financial recovery and asset consolidation phase.",
            "dates": "Active Concluding Phase (29 March 2025 – 23 February 2028)",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": True,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 3:
        dh_info = DHAIYA_ENCYCLOPEDIA[4]
        return {
            "active": True,
            "status_title": dh_info["name"],
            "phase_num": 4,
            "focus": dh_info["focus"],
            "health": dh_info["health"],
            "wealth": dh_info["wealth"],
            "family": dh_info["family"],
            "loan": dh_info["loan"],
            "partner": dh_info["partner"],
            "luck": dh_info["luck"],
            "career": dh_info["career"],
            "remedy": dh_info["remedy"],
            "impact": f"Saturn transits your 4th house from {m_name} Moon.",
            "dates": "Active 2.5-Year Dhaiya (2025 – 2028)",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 7:
        dh_info = DHAIYA_ENCYCLOPEDIA[8]
        return {
            "active": True,
            "status_title": dh_info["name"],
            "phase_num": 8,
            "focus": dh_info["focus"],
            "health": dh_info["health"],
            "wealth": dh_info["wealth"],
            "family": dh_info["family"],
            "loan": dh_info["loan"],
            "partner": dh_info["partner"],
            "luck": dh_info["luck"],
            "career": dh_info["career"],
            "remedy": dh_info["remedy"],
            "impact": f"Saturn transits your 8th house from {m_name} Moon.",
            "dates": "Active 2.5-Year Dhaiya (2025 – 2028)",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    else:
        return {
            "active": False,
            "status_title": "No Active Sade Sati or Dhaiya",
            "phase_num": 0,
            "focus": "Unimpeded Progress & Expansion",
            "health": "Standard biological stamina.",
            "wealth": "Standard financial liquidity based on active Dasha periods.",
            "family": "Harmonious domestic relations.",
            "loan": "Normal credit management.",
            "partner": "Stable partnership dynamics.",
            "luck": "Favorable planetary support.",
            "career": "Constructive career growth with minimal Saturnic friction.",
            "remedy": "Continue daily prayers and ethical business practices.",
            "impact": f"Saturn is currently in Pisces, placing it in an auspicious or neutral house relative to your {m_name} Moon.",
            "dates": "No Current Friction Cycle",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }

def calculate_shani_vahan(birth_star_idx: int, transit_moon_star_idx: int) -> dict:
    raw_val = (birth_star_idx * 4 + transit_moon_star_idx) % 9
    rem = 9 if raw_val == 0 else raw_val
    return SHANI_VAHANS.get(rem, SHANI_VAHANS[9])

def reduce_to_single_digit(num: int) -> int:
    while num > 9:
        num = sum(int(ch) for ch in str(num))
    return num if num > 0 else 9

def calculate_numerology(dob: datetime.date, name: str):
    mulank = reduce_to_single_digit(dob.day)
    full_date_sum = dob.day + dob.month + dob.year
    bhagyank = reduce_to_single_digit(full_date_sum)
    cleaned_name = "".join(ch for ch in name.upper() if ch.isalpha())
    namank_val = sum(CHALDEAN_MAP.get(ch, 0) for ch in cleaned_name)
    namank = reduce_to_single_digit(namank_val) if namank_val > 0 else 1
    return mulank, bhagyank, namank

def get_personal_day_vibe(dob: datetime.date, target_date: datetime.date, lang: str = "en") -> dict:
    personal_year = reduce_to_single_digit(dob.day + dob.month + target_date.year)
    personal_day = reduce_to_single_digit(personal_year + target_date.month + target_date.day)
    planet_info = NUM_PLANET_NAMES.get(personal_day, {}).get(lang, f"Number {personal_day}")
    return {
        "number": personal_day,
        "planet": planet_info,
        "desc": f"Personal Day {personal_day} resonates with {planet_info} cosmic frequency."
    }

def get_numerology_life_domains(mulank: int, bhagyank: int, namank: int, lang: str = "en") -> dict:
    p_m = NUM_PLANET_NAMES.get(mulank, {}).get(lang, f"Planet {mulank}")
    p_b = NUM_PLANET_NAMES.get(bhagyank, {}).get(lang, f"Planet {bhagyank}")
    return {
        "career_title": "💼 Career Trajectory & Executive Ambition",
        "career_desc": f"The dynamic synthesis of Driver {mulank} ({p_m}) and Conductor {bhagyank} ({p_b}) creates a powerhouse combination of strategic vision and courageous execution.",
        "wealth_title": "💰 Wealth Dynamics & Financial Mastery",
        "wealth_desc": "Your vibrational alignment supports structured compounding and tangible asset security. Avoid volatile speculative gambling.",
        "rel_title": "❤️ Relationships & Interpersonal Dynamics",
        "rel_desc": "You value authentic, pretense-free connections. Practicing active listening during critical discussions will keep family and professional bonds deeply harmonious.",
        "health_title": "🌿 Health, Vitality & Holistic Bio-Rhythms",
        "health_desc": "You possess strong physical endurance. Balance mental momentum with regular hydration, structured rest, and evening breathwork.",
        "luck_title": "🍀 Harmonic Lucky Attributes",
        "lucky_num": f"{mulank}, {bhagyank}, {(mulank + bhagyank) % 9 or 9}",
        "avoid_num": "2, 8 (Exercise tactful patience)",
        "lucky_days": "Tuesday, Thursday, and Sunday",
        "lucky_colors": "Electric Blue, Slate Gray, Rich Amber Gold",
        "lucky_dir": "South and North-East"
    }

def get_numerology_avoidance(mulank: int, bhagyank: int, lang: str = "en") -> dict:
    return {
        "avoid_title": "⚠️ Cosmic Caution & Avoidance Matrix",
        "avoid_numbers": "2, 8 (Challenging karmic tests)",
        "avoid_colors": "Pitch Black, Mud Brown, Dirty Dark Indigo",
        "avoid_days": "Saturday twilight & Monday late nights (for high-stakes launches)",
        "avoid_directions": "South-West during rest",
        "cautions": [
            "Avoid verbal agreements without clearly documented written contracts.",
            "Never commit to capital investments or legal deeds during sudden anger or peak haste.",
            "Strictly avoid speculative options trading and get-rich-quick shortcuts.",
            "Eliminate tangled electronic cables and broken appliances from your primary workspace.",
            "Refrain from purchasing iron hardware or heavy scrap on Saturdays."
        ]
    }

def calculate_sun_times(date_obj: datetime.date, lat: float, lon: float):
    day_of_year = date_obj.timetuple().tm_yday
    decl = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    lat_rad = math.radians(lat)
    decl_rad = math.radians(decl)
    
    cos_ha = -math.tan(lat_rad) * math.tan(decl_rad)
    cos_ha = max(-1.0, min(1.0, cos_ha))
    ha_deg = math.degrees(math.acos(cos_ha))
    
    b = math.radians((360 / 365) * (day_of_year - 81))
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    
    time_corr = 4 * (lon - 82.5) + eot
    solar_noon_minutes = 720 - time_corr
    half_day_minutes = (ha_deg / 15.0) * 60.0
    
    sr_minutes = solar_noon_minutes - half_day_minutes
    ss_minutes = solar_noon_minutes + half_day_minutes
    
    base_dt = datetime.datetime.combine(date_obj, datetime.time.min)
    return base_dt + datetime.timedelta(minutes=sr_minutes), base_dt + datetime.timedelta(minutes=ss_minutes)

def calculate_daily_muhurtas(date_obj: datetime.date, lat: float, lon: float):
    sunrise, sunset = calculate_sun_times(date_obj, lat, lon)
    day_duration = (sunset - sunrise).total_seconds()
    
    muhurta_duration = day_duration / 15.0
    abhijit_start = sunrise + datetime.timedelta(seconds=7 * muhurta_duration)
    abhijit_end = sunrise + datetime.timedelta(seconds=8 * muhurta_duration)
    
    eighth_part = day_duration / 8.0
    wday = date_obj.weekday()
    rahu_parts = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}
    yamaganda_parts = {0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6, 6: 5}
    
    r_idx = rahu_parts.get(wday, 6)
    rahu_start = sunrise + datetime.timedelta(seconds=(r_idx - 1) * eighth_part)
    rahu_end = sunrise + datetime.timedelta(seconds=r_idx * eighth_part)
    
    y_idx = yamaganda_parts.get(wday, 1)
    yama_start = sunrise + datetime.timedelta(seconds=(y_idx - 1) * eighth_part)
    yama_end = sunrise + datetime.timedelta(seconds=y_idx * eighth_part)
    
    brahma_start = sunrise - datetime.timedelta(minutes=96)
    brahma_end = sunrise - datetime.timedelta(minutes=48)
    
    return {
        "sunrise": sunrise,
        "sunset": sunset,
        "abhijit": (abhijit_start, abhijit_end),
        "rahu": (rahu_start, rahu_end),
        "yamaganda": (yama_start, yama_end),
        "brahma": (brahma_start, brahma_end)
    }

def get_current_nakshatra_window(target_ist_dt: datetime.datetime):
    utc_dt = target_ist_dt - datetime.timedelta(hours=5, minutes=30)
    current_lon = get_sidereal_moon_longitude(utc_dt)
    span = 360.0 / 27.0
    star_idx = max(1, min(27, int(current_lon / span) + 1))
    start_lon = (star_idx - 1) * span

    deg_from_start = (current_lon - start_lon) % span
    deg_to_end = span - deg_from_start

    hours_since_start = max(0.1, deg_from_start / 0.55)
    hours_to_end = max(0.1, deg_to_end / 0.55)

    start_dt = target_ist_dt - datetime.timedelta(hours=hours_since_start)
    end_dt = target_ist_dt + datetime.timedelta(hours=hours_to_end)

    return star_idx, start_dt, end_dt

def get_7_day_moon_transits(start_ist_dt: datetime.datetime, birth_star_idx: int):
    transits = []
    curr_t = start_ist_dt
    for i in range(7):
        target_t = curr_t + datetime.timedelta(days=i)
        star_idx, s_time, e_time = get_current_nakshatra_window(target_t)
        
        offset = (star_idx - birth_star_idx) % 9
        nav_name, icon, quality = NAVTARA_NAMES[offset]
        vahan_rem = (birth_star_idx * 4 + star_idx) % 9
        vahan_rem = 9 if vahan_rem == 0 else vahan_rem
        vahan_info = SHANI_VAHANS.get(vahan_rem, SHANI_VAHANS[9])
        
        transits.append({
            "day_num": i + 1,
            "date": target_t.date(),
            "date_str": target_t.strftime("%a, %d %b"),
            "star_idx": star_idx,
            "star_name": NAKSHATRAS[star_idx - 1],
            "nav_name": nav_name,
            "nav_offset": offset,
            "icon": icon,
            "quality": quality,
            "vahan": vahan_info["name"],
            "vahan_type": vahan_info["type"],
            "start_str": s_time.strftime("%a, %d %b %I:%M %p"),
            "end_str": e_time.strftime("%a, %d %b %I:%M %p IST")
        })
    return transits

def get_detailed_day_insights(offset: int, vahan_dict: dict, current_star_name: str, p_day: dict):
    is_positive = offset in [1, 3, 5, 7, 8]
    is_extreme_friction = offset in [2, 4, 6]

    theme_map = {
        0: ("Identity Renewal & Foundation (Janma)", "Mind feels intensely sensitive, reflective, and connected to root desires. Vital for self-evaluation rather than high-stakes friction.", "Focus on foundational planning, health diagnostics, routine execution, and self-care.", "Avoid impulsive career shifts, major loans, or initiating confrontational meetings."),
        1: ("Accelerated Wealth & Liquidity (Sampat)", "High financial synchronicity. Cosmic doors open for asset acquisition, high-ticket proposals, and capital expansion.", "Sign partnership deeds, initiate investments, submit proposals, and collect receivables.", "Avoid complacency; strike while the cosmic window is open."),
        2: ("Friction Shield & Crisis Deflection (Vipat)", "Elevated environmental resistance. Unforeseen delays, technological glitches, and administrative roadblocks.", "Conduct defensive administrative checks, review error margins, and maintain low profile.", "Strictly avoid speculative bets, aggressive confrontations, or signing irreversible contracts."),
        3: ("Peace, Health & Structural Security (Kshema)", "Sustaining, healing vibrational flow. Excellent for domestic harmony, property matters, and emotional equilibrium.", "Finalize contracts, purchase durable goods, enjoy family gatherings, and resolve old disputes.", "Avoid over-exhaustion; maintain balanced dietary and rest rhythms."),
        4: ("Overcoming Roadblocks & Opposition (Pratyari)", "Testing of diplomatic acumen. Hidden opposition, critical auditors, or challenging counterparties may emerge.", "Gather airtight evidence, exercise extreme tactical patience, and listen twice as much as you speak.", "Avoid losing temper in official communications; do not escalate legal friction."),
        5: ("Strategic Mastery & Manifestation (Sadhana)", "Golden window for high-order accomplishments. Mental faculties are razor sharp for complex engineering, strategy, and execution.", "Launch critical campaigns, undertake complex technical projects, negotiate promotions, and study.", "Do not waste this high-frequency window on superficial trivialities."),
        6: ("High Friction Zone & Defensive Prudence (Vadha)", "Heaviest energetic friction. Physical vitality and mental stamina feel vulnerable to depletion.", "Keep a minimalist agenda, practice quiet perseverance, and double-check all critical data.", "Do not drive long distances late at night; postpone major financial commitments."),
        7: ("Cooperative Harmony & Alliance Building (Mitra)", "Pleasurable, cordial cosmic atmosphere. High responsiveness from peers, mentors, and prospective partners.", "Network with key decision-makers, resolve estrangements, host important discussions, and socialize.", "Avoid being overly accommodating; ensure business boundaries remain firm."),
        8: ("Supreme Synergy & Pinnacle Triumph (Ati-Mitra)", "Peak celestial resonance. The rarest, most fruitful timing window for long-term victories and monumental leaps.", "Pitch high-value clients, launch new business verticals, close major property deals, and celebrate.", "Do not doubt yourself; step forward with unwavering confidence.")
    }

    theme_title, theme_desc, opportunities, hazards = theme_map.get(offset, theme_map[0])

    if is_positive:
        remedy_mantra = "ॐ नमो भगवते वासुदेवाय (Om Namo Bhagavate Vasudevaya) - 11 times in morning facing East."
        remedy_charity = "Offer sweet yellow fruits or milk sweets to elders, mentors, or temples to seal cosmic prosperity."
        remedy_action = "Wear light, vibrant shades (Coral Red, Amber Gold, or Electric White) to broadcast peak resonance."
    elif is_extreme_friction:
        remedy_mantra = "ॐ नमः शिवाय (Om Namah Shivaya) or Maha Mrityunjaya Mantra - 108 times at twilight facing North."
        remedy_charity = "Feed stray dogs, crows, or donate dark grains/black sesame to pacify planetary friction."
        remedy_action = "Apply white sandalwood paste to forehead/wrists; maintain 15 minutes of silent mindfulness (Mauna) before sunset."
    else:
        remedy_mantra = "ॐ सूर्याय नमः (Om Suryaya Namah) - Offer pure water in a copper vessel to morning Sun."
        remedy_charity = "Feed green grass or fresh spinach to cows to enhance cellular vitality and grounding."
        remedy_action = "Drink warm water from a silver cup; strictly abstain from fast food and erratic sleep patterns."

    return {
        "theme_title": theme_title,
        "theme_desc": theme_desc,
        "opportunities": opportunities,
        "hazards": hazards,
        "remedy_mantra": remedy_mantra,
        "remedy_charity": remedy_charity,
        "remedy_action": remedy_action
    }

# ==============================================================================
# CLIENT-SIDE BROWSER MEMORY (URL QUERY PARAMS + SESSION STATE)
# ==============================================================================
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

# Universal Centered Header on ALL tabs
render_html(f"""
    <div style='text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; margin-top:0.2rem; margin-bottom:0.75rem;'>
        <div style='background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); width:76px; height:76px; border-radius:26px; display:flex; align-items:center; justify-content:center; font-size:2.45rem; box-shadow:0 8px 28px rgba(245,158,11,0.38); margin-bottom:10px;'>
            ✨
        </div>
        <h1 style='margin:0; font-size:2.15rem; color:#0f172a; font-weight:900; line-height:1.2; text-align:center;'>{t('app_title', current_lang)}</h1>
        <div style='font-size:1rem; color:#64748b; font-weight:600; margin-top:6px; text-align:center;'>{t('app_subtitle', current_lang)}</div>
    </div>
""")

# Top Navigation Dock (4 + 3 Grid)
nav_r1_c1, nav_r1_c2, nav_r1_c3, nav_r1_c4 = st.columns(4)
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

with nav_r1_c4:
    p_type = "primary" if st.session_state.current_page == "shani" else "secondary"
    if st.button(t("btn_shani", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "shani"
        st.rerun()

nav_r2_c1, nav_r2_c2, nav_r2_c3 = st.columns(3)
with nav_r2_c1:
    p_type = "primary" if st.session_state.current_page == "live" else "secondary"
    if st.button(t("btn_live", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "live"
        st.rerun()

with nav_r2_c2:
    p_type = "primary" if st.session_state.current_page == "forecast" else "secondary"
    if st.button(t("btn_forecast", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "forecast"
        st.rerun()

with nav_r2_c3:
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
else:
    dob_parsed, tob_parsed, chart_info = None, None, None
    mulank, bhagyank, namank = None, None, None
    shani_paya_data, shani_sadesati_data = None, None
    u_lat, u_lon = 28.6139, 77.2090

def render_profile_setup_prompt():
    render_html("""
    <div style="background:#fffbeb; border:2px dashed #f59e0b; border-radius:16px; padding:1.5rem; text-align:center; margin:1.5rem 0;">
        <div style="font-size:2.2rem; margin-bottom:8px;">👤</div>
        <div style="font-weight:900; font-size:1.25rem; color:#92400e; margin-bottom:6px;">
            Set Up Your Vedic Birth Profile
        </div>
        <div style="font-size:0.95rem; color:#78350f; max-width:480px; margin:0 auto 1.2rem auto; line-height:1.6;">
            To calculate your authentic <b>Janma Nakshatra</b>, <b>Ascendant (Lagna)</b>, <b>Navtara cycle</b>, and <b>Shani Sade Sati phase</b>, please enter your birth details in the User Profile tab.
        </div>
    </div>
    """)
    _, c_mid, _ = st.columns([1, 2, 1])
    with c_mid:
        if st.button("👉 Configure Profile Now", type="primary", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()

# ==============================================================================
# POST-SUBMISSION ONBOARDING SCREEN: ADD TO HOME SCREEN
# ==============================================================================
def render_page_install_guide():
    render_html("""
    <div class="auth-hero-box" style="text-align:center; border:2px solid #f59e0b; background:#fffbeb;">
        <div style="font-size:2.6rem; margin-bottom:8px;">📱</div>
        <div style="font-weight:900; font-size:1.45rem; color:#92400e; margin-bottom:6px;">
            Save to Home Screen on Your Device
        </div>
        <div style="font-size:0.98rem; color:#78350f; line-height:1.6; margin-bottom:12px;">
            Your astrological profile & coordinates are now securely loaded in your device's browser bar. 
            <b>Add Navtara Pulse to your Home Screen now</b> so your profile opens automatically every day without typing anything again!
        </div>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.18rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:1.5px solid #fed7aa; padding-bottom:0.3rem;">
            🤖 For Android (Google Chrome)
        </div>
        <ol style="margin-top:5px; margin-bottom:6px; padding-left:1.3rem; font-size:0.95rem; color:#431407; line-height:1.75;">
            <li>Tap the <b>three vertical dots menu (⋮)</b> in the top-right corner of Chrome.</li>
            <li>Select <b>"Install app"</b> or <b>"Add to Home screen"</b>.</li>
            <li>Tap <b>"Install"</b>. The app icon is saved to your phone with your profile intact!</li>
        </ol>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.18rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:1.5px solid #fed7aa; padding-bottom:0.3rem;">
            🍏 For iPhone / iOS (Safari Browser)
        </div>
        <ol style="margin-top:5px; margin-bottom:6px; padding-left:1.3rem; font-size:0.95rem; color:#431407; line-height:1.75;">
            <li>Tap the <b>Share icon</b> (square with an upward arrow) at the bottom of Safari.</li>
            <li>Scroll down and tap <b>"Add to Home Screen"</b>.</li>
            <li>Tap <b>"Add"</b> in the top right. Launch directly anytime as a native full-screen app!</li>
        </ol>
    </div>
    """)

    st.write("")
    c_btn1, c_btn2 = st.columns([1, 1])
    with c_btn1:
        if st.button("⚡ Proceed to Today's Prediction", type="primary", use_container_width=True):
            st.session_state.current_page = "live"
            st.rerun()
    with c_btn2:
        if st.button("👤 View Astrological Profile", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()

# ==============================================================================
# TAB 1: ABOUT APP
# ==============================================================================
def render_page_about():
    with st.container(border=True):
        st.markdown("**🌐 Select Language / भाषा चुनें:**")
        lang_col1, _ = st.columns([2, 1])
        with lang_col1:
            lang_options = {"en": "English", "hi": "हिन्दी (Hindi)"}
            selected_lang_code = st.selectbox(
                "App Language",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
                index=list(lang_options.keys()).index(current_lang if current_lang in lang_options else "en"),
                label_visibility="collapsed"
            )
            if selected_lang_code != current_lang:
                st.session_state.user_profile["lang"] = selected_lang_code
                st.query_params["lang"] = selected_lang_code
                st.rerun()

    render_html("""
    <div class="auth-hero-box">
        <div style="font-weight:900; font-size:1.35rem; color:#92400e; margin-bottom:0.75rem; border-bottom:1.5px solid #fde68a; padding-bottom:0.4rem;">
            🧬 Navtara Pulse: Precision Chronobiology & Vedic Timing Engine
        </div>
        <div style="font-size:0.98rem; line-height:1.8; color:#451a03; margin-bottom:0.8rem;">
            <b>Navtara Pulse</b> bridges ancient Sidereal Jyotish with modern chronobiology. It is an algorithmic decision-support compass designed to answer one crucial question: <b>"Is today mathematically aligned for aggressive action, or does it demand strategic defense?"</b><br>
            By mapping the Moon's real-time transit through the 27 lunar mansions (Nakshatras) against your natal birth frequency, the app calculates your personalized 9-fold bio-rhythm, pinpointing exact windows of peak influence, effortless execution, and friction avoidance.
        </div>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            🔬 The Scientific Logic: Gravitational Hydrodynamics & Bio-Rhythms
        </div>
        
        <div style="font-size:0.96rem; line-height:1.75; color:#334155; margin-bottom:1rem;">
            <b>1. Lunar Tidal Hydrodynamics & Neuro-Endocrine Flow:</b><br>
            The adult human brain and body are composed of approximately <b>70% water and electrolytic fluids</b>. Chronobiology confirms that lunar periodicity modulates circadian gene expression, sleep architecture (REM cycles), cerebrospinal fluid pressure, and neuro-transmitter output. In classical Vedic science, the Moon governs the mind (<i>"Chandro Manaso Jatah"</i>). When the celestial Moon aligns harmoniously with your natal Moon's electro-magnetic horizon, neural processing operates at peak cognitive clarity.
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#334155; margin-bottom:1rem;">
            <b>2. The 9-Fold Mathematical Resonance Grid (27 = 9 × 3):</b><br>
            The zodiac is divided into 27 Nakshatras of 13° 20' each. The Vedic <b>Navtara Chakra</b> is an infradian mathematical model that groups these 27 stars into 3 repeating cycles of 9 qualitative energetic frequencies (Taras). Every single day, the Moon activates one of these 9 energetic chambers for your unique neural wiring:
            <ul style="margin-top:6px; padding-left:1.3rem;">
                <li><b>Expansion Windows (Sampat, Sadhana, Mitra, Ati-Mitra):</b> Characterized by high environmental receptivity and synaptic coherence. Ideal for high-stakes business negotiations, signing contracts, strategic investing, and key launches.</li>
                <li><b>Friction Shields (Vipat, Pratyari, Vadha):</b> Characterized by elevated resistance, biochemical fatigue, and communication misfires. On these days, defensive prudence and patient review prevent costly missteps.</li>
                <li><b>Foundational & Consolidation Days (Janma, Kshema):</b> Optimal for internal diagnostics, physical recuperation, and team alignment.</li>
            </ul>
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#334155;">
            <b>3. Sub-Arcsecond Planetary Ephemeris (Swiss Ephemeris):</b><br>
            Unlike conventional astrology apps that rely on generic sun signs or flat 24-hour sunrise assumptions, <b>Navtara Pulse</b> incorporates the <b>Moshier Swiss Ephemeris</b> (pyswisseph) with true topocentric Chitrapaksha Lahiri Ayanamsa. Ingress and egress timestamps are calculated down to the exact second for your geographical horizon.
        </div>
    </div>
    """)

    app_url = "https://navtara-pulse.streamlit.app"
    share_msg = "Track your real-time Vedic Moon transit rhythm, Shani Paya, and personalized timing blueprint with Navtara Pulse!"
    encoded_url = urllib.parse.quote(app_url)
    encoded_msg = urllib.parse.quote(f"{share_msg}\n\nCheck your cosmic alignment here: {app_url}")

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            {t('share_title', current_lang)}
        </div>
        <div style="font-size:0.95rem; color:#475569; margin-bottom:0.85rem;">
            Share this authentic Vedic chronobiology tool with your family, friends, and colleagues:
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:1rem;">
            <a href="https://api.whatsapp.com/send?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#25D366; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(37,211,102,0.2);">
                    🟢 WhatsApp
                </div>
            </a>
            <a href="https://t.me/share/url?url={encoded_url}&text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0088cc; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(0,136,204,0.2);">
                    ✈️ Telegram
                </div>
            </a>
            <a href="mailto:?subject=Navtara Pulse - Vedic Timing&body={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#ea4335; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(234,67,53,0.2);">
                    ✉️ Email
                </div>
            </a>
            <a href="https://twitter.com/intent/tweet?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0f172a; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(15,23,42,0.2);">
                    🐦 X (Twitter)
                </div>
            </a>
        </div>
    </div>
    """)

# ==============================================================================
# TAB 2: USER PROFILE
# ==============================================================================
def render_page_profile():
    global u_lat, u_lon
    if not has_valid_profile or st.session_state.edit_mode:
        render_html("""
        <div class="light-card-profile">
            <div style="font-weight:900; font-size:1.3rem; color:#9a3412; margin-bottom:0.5rem;">
                👤 Configure Vedic Birth Profile
            </div>
            <div style="font-size:0.94rem; color:#475569; margin-bottom:1rem;">
                Please enter your birth details to generate your authentic Vedic chart, Lagna, Janma Nakshatra, and Sade Sati status.
            </div>
        </div>
        """)
        with st.form("create_profile_form"):
            new_name = st.text_input(t("name_label", current_lang), value=prof.get("name", ""), placeholder="e.g. Rahul Sharma")
            d_init = dob_parsed if dob_parsed else datetime.date(1990, 1, 1)
            new_dob = st.date_input(t("dob_label", current_lang), value=d_init)
            
            st.markdown("**Birth Time (Hour, Minute & AM/PM):**")
            t_col1, t_col2, t_col3 = st.columns([1.5, 1.5, 1.5])
            with t_col1:
                init_hr = (tob_parsed.hour % 12) if tob_parsed else 10
                init_hr = 12 if init_hr == 0 else init_hr
                in_hour = st.selectbox("Hour", options=list(range(1, 13)), index=init_hr - 1)
            with t_col2:
                init_min = tob_parsed.minute if tob_parsed else 43
                in_minute = st.selectbox("Minute", options=list(range(0, 60)), index=init_min)
            with t_col3:
                init_ampm = "PM" if (tob_parsed and tob_parsed.hour >= 12) else "AM"
                in_ampm = st.selectbox("AM / PM", options=["AM", "PM"], index=1 if init_ampm == "PM" else 0)

            new_city_query = st.text_input(t("city_label", current_lang), value=prof.get("city", ""), placeholder="e.g. Panvel, Aurangabad, Mumbai, London, New York")

            c_save, c_canc = st.columns([2, 1])
            with c_save:
                submitted = st.form_submit_button("✨ Save & Calculate Profile", type="primary", use_container_width=True)
            with c_canc:
                canceled = st.form_submit_button("Cancel", use_container_width=True)

            if submitted:
                if not new_name.strip():
                    st.error("Please provide your full name.")
                elif not new_city_query.strip():
                    st.error("Please provide a birth location name.")
                else:
                    hr_24 = in_hour % 12
                    if in_ampm == "PM":
                        hr_24 += 12
                    final_tob_str = f"{hr_24:02d}:{in_minute:02d}"

                    # DYNAMIC GEOCODING SEARCH
                    with st.spinner("Searching coordinates for your location..."):
                        resolved_lat, resolved_lon, resolved_name = resolve_location_name(new_city_query)

                    st.session_state.user_profile.update({
                        "name": new_name.strip(),
                        "dob": new_dob.strftime("%Y-%m-%d"),
                        "tob": final_tob_str,
                        "city": new_city_query.strip(),
                        "lat": resolved_lat,
                        "lon": resolved_lon
                    })
                    
                    st.query_params.update({
                        "name": new_name.strip(),
                        "dob": new_dob.strftime("%Y-%m-%d"),
                        "tob": final_tob_str,
                        "city": new_city_query.strip(),
                        "lat": f"{resolved_lat:.4f}",
                        "lon": f"{resolved_lon:.4f}"
                    })

                    st.session_state.edit_mode = False
                    st.session_state.current_page = "install_guide"
                    st.rerun()
            
            if canceled:
                st.session_state.edit_mode = False
                st.rerun()
        return

    with st.container(border=True):
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            render_html(f"""
            <div style="font-weight:900; font-size:1.2rem; color:#0f172a;">👤 {prof['name']}'s Profile</div>
            <div style="font-size:0.95rem; color:#334155; margin-top:5px; line-height:1.6;">
                📅 <b>DOB:</b> {dob_parsed.strftime('%d %B %Y')} &nbsp;|&nbsp; ⏰ <b>Time:</b> {tob_parsed.strftime('%I:%M %p')}<br>
                📍 <b>Place:</b> {prof['city']} ({u_lat:.4f}° N, {u_lon:.4f}° E)
            </div>
            """)
        with col_p2:
            if st.button(t("edit_details", current_lang), use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()

    bio_nak = NAKSHATRA_BIO_DATA.get(chart_info["star_idx"], NAKSHATRA_BIO_DATA[2])
    n_data = get_nakshatra_rich_data(chart_info["star_idx"])
    m_data = get_rashi_rich_data(chart_info["moon_rashi_idx"])
    l_data = get_lagna_rich_data(chart_info["lagna_idx"])
    
    moon_parts = chart_info['moon_rashi_name'].split()
    moon_p1 = moon_parts[0] if moon_parts else chart_info['moon_rashi_name']
    moon_p2 = moon_parts[-1] if len(moon_parts) > 1 else ""

    lagna_parts = chart_info['lagna_name'].split()
    lagna_p1 = lagna_parts[0] if lagna_parts else chart_info['lagna_name']
    lagna_p2 = lagna_parts[-1] if len(lagna_parts) > 1 else ""

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.35rem; color:#9a3412; margin-bottom:1rem; border-bottom:2px solid #fed7aa; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>🌌 Verified Vedic Kundali Alignment</span>
            <span style="font-size:0.85rem; background:#ffedd5; color:#c2410c; padding:4px 10px; border-radius:20px; font-weight:800;">Chitrapaksha Lahiri Ayanamsa</span>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:10px; text-align:center; margin-bottom:1.25rem;">
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('lagna_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{lagna_p1}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{chart_info['lagna_deg']}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('nakshatra_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{chart_info['star_name']}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{t('pada_label', current_lang)} {chart_info['pada']}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('moon_rashi_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{moon_p1}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{moon_p2}</div>
            </div>
        </div>

        <div style="background:#fffaf0; border-radius:14px; padding:14px; border:1.5px solid #fed7aa; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#9a3412; margin-bottom:8px;">
                ⭐ Janma Nakshatra: {chart_info['star_name']} (Pada {chart_info['pada']})
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:8px; margin-bottom:12px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🏛️ Deity:</b> {bio_nak['deity']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🔱 Symbol:</b> {bio_nak['symbol']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🌳 Sacred Tree:</b> {bio_nak['tree']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🦅 Sacred Bird:</b> {bio_nak['bird']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🦁 Yoni Animal:</b> {bio_nak['animal']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🪐 Planetary Lord:</b> {bio_nak['lord']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #fed7aa; margin-bottom:8px;">
                <b style="color:#9a3412; font-size:0.96rem;">🧠 Core Cognitive & Behavioral Archetype:</b>
                <div style="font-size:0.92rem; line-height:1.65; color:#431407; margin-top:2px;">{n_data['core']}</div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:8px;">
                <div style="background:#f0fdf4; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                    <b style="color:#15803d; font-size:0.92rem;">✨ Superpowers & Natural Assets:</b>
                    <div style="font-size:0.89rem; line-height:1.55; color:#14532d; margin-top:2px;">{n_data['strengths']}</div>
                </div>
                <div style="background:#fff1f2; border-radius:10px; padding:10px; border:1px solid #fecdd3;">
                    <b style="color:#be123c; font-size:0.92rem;">⚠️ Karmic Shadows & Blind Spots:</b>
                    <div style="font-size:0.89rem; line-height:1.55; color:#881337; margin-top:2px;">{n_data['shadows']}</div>
                </div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #fed7aa; margin-bottom:8px; font-size:0.91rem; color:#431407;">
                <b>💼 Peak Vocational & Executive Fields:</b><br>{n_data['careers']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #fed7aa; margin-bottom:8px; font-size:0.91rem; color:#431407;">
                <b>🔮 Evolutionary Life Path Trajectory:</b><br>{n_data['prediction']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #f97316; font-size:0.91rem; color:#431407;">
                <b>🪔 Prescribed Vedic Nakshatra Remedies:</b><br>{n_data['remedies']}
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:14px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#065f46; margin-bottom:8px;">
                🌙 Moon Sign (Chandra Rashi): {chart_info['moon_rashi_name']}
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:10px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>🔥 Element:</b> {m_data['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>🪐 Rashi Sovereign:</b> {m_data['ruler']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>🧠 Emotional Mindset & Subconscious Processing:</b><br>{m_data['psychology']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>⚡ Stress Reflexes & Primal Coping Instincts:</b><br>{m_data['instincts']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>❤️ Interpersonal Blueprint & Relationship Style:</b><br>{m_data['relations']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>🌿 Bio-Rhythms & Physiological Vitality:</b><br>{m_data['health']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #10b981; font-size:0.91rem; color:#14532d;">
                <b>🪔 Prescribed Lunar Remedies:</b><br>{m_data['remedies']}
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:8px;">
                🌅 Ascendant (Lagna): {chart_info['lagna_name']} at {chart_info['lagna_deg']}
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:10px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>🌍 Lagna Tattva:</b> {l_data['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>👑 Ascendant Lord:</b> {l_data['lord']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>🛡️ Physical Constitution, Vitality & Posture (Prakriti):</b><br>{l_data['constitution']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>👔 Outward Persona & Negotiating Presence:</b><br>{l_data['persona']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>🚀 Evolutionary Life Arc & Asset Compounding:</b><br>{l_data['life_arc']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #8b5cf6; font-size:0.91rem; color:#3b0764;">
                <b>🪔 Prescribed Ascendant Remedies:</b><br>{l_data['remedies']}
            </div>
        </div>
    </div>
    """)

    # Tara Bala Widget
    with st.container(border=True):
        st.markdown("**🤝 Nakshatra Synergy & Compatibility Evaluator (Tara Bala)**")
        partner_star_choice = st.selectbox("Select Counterpart's Birth Star:", options=NAKSHATRAS, index=0)
        p_star_idx = NAKSHATRAS.index(partner_star_choice) + 1
        tara_res = get_tara_bala_info(chart_info['star_idx'], p_star_idx)
        
        box_bg = '#f0fdf4' if tara_res['is_allied'] else ('#fff1f2' if tara_res['is_friction'] else '#f8fafc')
        box_border = '#86efac' if tara_res['is_allied'] else ('#fecdd3' if tara_res['is_friction'] else '#e2e8f0')
        box_color = '#15803d' if tara_res['is_allied'] else ('#be123c' if tara_res['is_friction'] else '#0f172a')
        
        render_html(f"""
        <div style="background:{box_bg}; border:1.5px solid {box_border}; border-radius:12px; padding:12px; margin-top:8px;">
            <div style="font-size:1.05rem; font-weight:800; color:{box_color};">
                {tara_res['icon']} {tara_res['tara_name']} — {tara_res['quality']}
            </div>
            <div style="font-size:0.92rem; font-weight:700; color:#334155; margin-top:4px;">
                Dynamic: {tara_res['relationship_tone']}
            </div>
            <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.5;">
                {tara_res['advice']}
            </div>
        </div>
        """)

# ==============================================================================
# TAB 3: NUMEROLOGY
# ==============================================================================
def render_page_numerology():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    num_domains = get_numerology_life_domains(mulank, bhagyank, namank, current_lang)
    avoid_data = get_numerology_avoidance(mulank, bhagyank, current_lang)
    p_m_label = NUM_PLANET_NAMES.get(mulank, {}).get(current_lang, f"Planet {mulank}")
    p_b_label = NUM_PLANET_NAMES.get(bhagyank, {}).get(current_lang, f"Planet {bhagyank}")
    p_n_label = NUM_PLANET_NAMES.get(namank, {}).get(current_lang, f"Planet {namank}")

    cautions_html = "".join(f"<li style='margin-bottom:5px;'>{c}</li>" for c in avoid_data['cautions'])

    render_html(f"""
    <div class="light-card-num">
        <div style="font-weight:900; font-size:1.25rem; color:#065f46; margin-bottom:1rem; border-bottom:2px solid #bbf7d0; padding-bottom:0.5rem;">
            <span>🔢 Core Numerology Blueprint</span>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:10px; text-align:center; margin-bottom:1.15rem;">
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900;">{t('mulank_label', current_lang)}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46;">{mulank}</div>
                <div style="font-size:0.88rem; color:#059669; font-weight:800;">{p_m_label}</div>
            </div>
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900;">{t('bhagyank_label', current_lang)}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46;">{bhagyank}</div>
                <div style="font-size:0.88rem; color:#059669; font-weight:800;">{p_b_label}</div>
            </div>
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900;">{t('namank_label', current_lang)}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46;">{namank}</div>
                <div style="font-size:0.88rem; color:#059669; font-weight:800;">{p_n_label}</div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr; gap:12px; margin-bottom:1.15rem;">
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #059669;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['career_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['career_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #10b981;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['wealth_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['wealth_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #14b8a6;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['rel_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['rel_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #0d9488;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['health_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['health_desc']}</div>
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:12px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:8px;">{num_domains['luck_title']}</div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.95rem; line-height:1.6;">
                <div><b>✨ Lucky Numbers:</b> {num_domains['lucky_num']}</div>
                <div><b>⚠️ Caution Numbers:</b> {num_domains['avoid_num']}</div>
                <div><b>📅 Auspicious Days:</b> {num_domains['lucky_days']}</div>
                <div><b>🧭 Favorable Direction:</b> {num_domains['lucky_dir']}</div>
                <div style="grid-column: 1 / -1;"><b>🎨 Energizing Colors:</b> {num_domains['lucky_colors']}</div>
            </div>
        </div>

        <div style="background:#fff1f2; border-radius:12px; padding:14px; border:1.5px solid #fecdd3; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.08rem; color:#9f1239; margin-bottom:8px;">{avoid_data['avoid_title']}</div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.93rem; line-height:1.6; margin-bottom:10px;">
                <div><b>🚫 Numbers to Avoid:</b> {avoid_data['avoid_numbers']}</div>
                <div><b>🎨 Colors to Avoid:</b> {avoid_data['avoid_colors']}</div>
                <div><b>📅 Unfavorable Days:</b> {avoid_data['avoid_days']}</div>
                <div><b>🧭 Direction to Avoid:</b> {avoid_data['avoid_directions']}</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border-left:4px solid #e11d48;">
                <b style="color:#9f1239; font-size:0.95rem;">⚠️ Critical Behavioral & Strategic Don'ts:</b>
                <ul style="margin:4px 0 0 0; padding-left:1.2rem; font-size:0.92rem; color:#881337; line-height:1.6;">
                    {cautions_html}
                </ul>
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:12px; padding:14px; border:1.5px solid #bbf7d0;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:6px;">🪔 Numerology Harmony & Grounding Remedies:</div>
            <div style="font-size:0.94rem; line-height:1.65; color:#14532d;">
                • <b>Metal Vessel Grounding:</b> Drink water from a pure silver or copper vessel to pacify nervous restlessness and enhance bio-electrical harmony.<br>
                • <b>Digital & Workspace Bio-Shield:</b> Remove tangled charging cables, broken electronic gadgets, and inactive clocks from your workspace.<br>
                • <b>Name Resonance (Namank):</b> Use green or blue ink when writing or endorsing important planning documents to harmonize your {namank} name vibration.
            </div>
        </div>
    </div>
    """)

# ==============================================================================
# TAB 4: SHANI & SADE SATI (EXHAUSTIVE 7-DOMAIN MATRIX)
# ==============================================================================
def render_page_shani():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    m_name = chart_info['moon_rashi_name'].split()[0]
    p1_active_tag = '<span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW</span>' if shani_sadesati_data['phase_1_active'] else ''
    p2_active_tag = '<span style="font-size:0.82rem; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW (PEAK)</span>' if shani_sadesati_data['phase_2_active'] else ''
    p3_active_tag = '<span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW</span>' if shani_sadesati_data['phase_3_active'] else ''

    render_html(f"""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.35rem; color:#5b21b6; margin-bottom:1rem; border-bottom:2px solid #ddd6fe; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>🪐 Shani Paya & Sade Sati Exhaustive Life-Domain Matrix</span>
            <span style="font-size:0.85rem; background:#ede9fe; color:#5b21b6; padding:4px 10px; border-radius:20px; font-weight:800;">Saturn in Pisces (Meena)</span>
        </div>
        
        <!-- SHANI PAYA IN-DEPTH MATRIX -->
        <div style="background:#f5f3ff; border-radius:14px; padding:16px; border:1.5px solid #e9d5ff; margin-bottom:1.25rem;">
            <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">ACTIVE TRANSIT PAYA FOR YOUR {m_name.upper()} MOON</div>
            <div style="font-size:1.45rem; font-weight:900; color:#5b21b6; margin:4px 0;">{shani_paya_data['paya']}</div>
            <div style="font-size:0.98rem; color:#7c3aed; font-weight:800;">Grade: {shani_paya_data['status']} | Dynamic: {shani_paya_data['tone']}</div>
            <div style="font-size:0.92rem; color:#475569; margin-top:3px;"><b>Active Timeline:</b> {shani_paya_data['timeline']}</div>
            
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1px solid #ddd6fe; margin-top:12px; font-size:0.93rem; color:#3b0764; line-height:1.7;">
                <b>🏛️ Classical Foundation:</b> {shani_paya_data['desc']}<br>
                <b>🧭 Operating Houses:</b> Saturn activates the {shani_paya_data['houses']} house axis relative to your natal Moon.
            </div>

            <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-top:12px;">
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #f97316; font-size:0.91rem; color:#7c2d12; line-height:1.6;">
                    <b>🌿 1. Health & Vitality Impact:</b><br>{shani_paya_data['health']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #10b981; font-size:0.91rem; color:#14532d; line-height:1.6;">
                    <b>💰 2. Wealth & Cash Flow Dynamics:</b><br>{shani_paya_data['wealth']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #8b5cf6; font-size:0.91rem; color:#3b0764; line-height:1.6;">
                    <b>👨‍👩‍👧‍👦 3. Family & Domestic Harmony:</b><br>{shani_paya_data['family']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #e11d48; font-size:0.91rem; color:#881337; line-height:1.6;">
                    <b>📉 4. Loans & Liabilities Management:</b><br>{shani_paya_data['loan']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #065f46; font-size:0.91rem; color:#065f46; line-height:1.6;">
                    <b>🤝 5. Partnerships & Business Alliances:</b><br>{shani_paya_data['partner']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #d97706; font-size:0.91rem; color:#78350f; line-height:1.6;">
                    <b>🍀 6. Luck & Destiny Alignment:</b><br>{shani_paya_data['luck']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #0284c7; font-size:0.91rem; color:#0369a1; line-height:1.6;">
                    <b>💼 7. Career, Authority & Executive Standing:</b><br>{shani_paya_data['career']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #475569; font-size:0.91rem; color:#0f172a; line-height:1.6;">
                    <b>🪔 8. Targeted Elemental Countermeasures:</b><br>{shani_paya_data['protocol']}
                </div>
            </div>
        </div>

        <!-- SADE SATI / DHAIYA EXHAUSTIVE MATRIX -->
        <div style="background:#ffffff; border-radius:14px; padding:16px; border:1.5px solid #ddd6fe; margin-bottom:1.25rem;">
            <div style="font-weight:900; font-size:1.2rem; color:#5b21b6; margin-bottom:10px; border-bottom:1px solid #e9d5ff; padding-bottom:5px; display:flex; justify-content:space-between; align-items:center;">
                <span>⚖️ Active Sade Sati / Dhaiya Life-Domain Breakdown for {m_name} Moon</span>
                <span style="font-size:0.82rem; background:#ede9fe; color:#5b21b6; padding:3px 8px; border-radius:10px; font-weight:800;">{shani_sadesati_data['status_title'].split(':')[0]}</span>
            </div>
            
            <div style="background:{'#fef2f2' if shani_sadesati_data['phase_2_active'] else '#f5f3ff'}; border-radius:12px; padding:14px; border-left:5px solid {'#ef4444' if shani_sadesati_data['phase_2_active'] else '#9333ea'}; margin-bottom:14px;">
                <b style="color:{'#991b1b' if shani_sadesati_data['phase_2_active'] else '#5b21b6'}; font-size:1.1rem;">{shani_sadesati_data['status_title']}</b>
                <div style="font-size:0.92rem; color:#64748b; margin:3px 0 8px 0;"><b>Active Window:</b> {shani_sadesati_data['dates']} | <b>Core Focus:</b> {shani_sadesati_data['focus']}</div>
                <div style="font-size:0.95rem; line-height:1.7; color:#334155;">{shani_sadesati_data['impact']}</div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:14px;">
                <div style="background:#fff7ed; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#7c2d12; border-left:4px solid #f97316;">
                    <b>🌿 1. Health & Vitality Impact:</b><br>{shani_sadesati_data['health']}
                </div>
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; border-left:4px solid #10b981; font-size:0.91rem; color:#14532d; border-left:4px solid #10b981;">
                    <b>💰 2. Wealth & Cash Flow Dynamics:</b><br>{shani_sadesati_data['wealth']}
                </div>
                <div style="background:#faf5ff; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#3b0764; border-left:4px solid #8b5cf6;">
                    <b>👨‍👩‍👧‍👦 3. Family & Domestic Harmony:</b><br>{shani_sadesati_data['family']}
                </div>
                <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#881337; border-left:4px solid #e11d48;">
                    <b>📉 4. Loans & Liabilities Management:</b><br>{shani_sadesati_data['loan']}
                </div>
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#065f46; border-left:4px solid #065f46;">
                    <b>🤝 5. Partnerships & Business Alliances:</b><br>{shani_sadesati_data['partner']}
                </div>
                <div style="background:#fffbeb; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#78350f; border-left:4px solid #d97706;">
                    <b>🍀 6. Luck & Destiny Alignment:</b><br>{shani_sadesati_data['luck']}
                </div>
                <div style="background:#f0f9ff; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#0369a1; border-left:4px solid #0284c7;">
                    <b>💼 7. Career, Authority & Executive Standing:</b><br>{shani_sadesati_data['career']}
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#0f172a; border-left:4px solid #475569;">
                    <b>🪔 8. Prescribed Remedial Protocol:</b><br>{shani_sadesati_data['remedy']}
                </div>
            </div>

            <div style="font-weight:900; font-size:1.05rem; color:#475569; margin:16px 0 8px 0; border-top:1px solid #e9d5ff; padding-top:10px;">
                Complete 7.5-Year Sade Sati Evolutionary Blueprint for {m_name} Moon:
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #a855f7; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#5b21b6; font-size:0.96rem;">Phase 1: Rising Phase (Saturn in {shani_sadesati_data['rashi_12th']} / 12th from Moon)</b>
                    {p1_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>Core Dynamic:</b> Subconscious restructuring, elimination of toxic habits, and mental detachment.<br>
                    • <b>Financial & Career:</b> Spikes in expenses related to travel, relocation, or healthcare; work happens behind the scenes.<br>
                    • <b>Karmic Mastery:</b> Shedding psychological baggage and preparing for the core transit.
                </div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #ef4444; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#991b1b; font-size:0.96rem;">Phase 2: Peak Janma Shani (Saturn in {shani_sadesati_data['rashi_1st']} / Over Natal Moon)</b>
                    {p2_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>Core Dynamic:</b> Crucible of character and endurance. Dissolves false pride and tests emotional truth.<br>
                    • <b>Financial & Career:</b> Maximum administrative burden, heavy decision-making stress, and executive solitude.<br>
                    • <b>Karmic Mastery:</b> Cultivating emotional resilience, physical discipline, and enduring maturity.
                </div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #10b981; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#065f46; font-size:0.96rem;">Phase 3: Setting Phase (Saturn in {shani_sadesati_data['rashi_2nd']} / 2nd from Moon)</b>
                    {p3_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>Core Dynamic:</b> Lifting of psychological pressure, consolidation of hard-won wisdom, and stabilizing family harmony.<br>
                    • <b>Financial & Career:</b> Wealth recovery, acquisition of durable assets, disciplined speech, and delayed recognition.<br>
                    • <b>Karmic Mastery:</b> Transforming lessons into lasting institutional stability and financial security.
                </div>
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe;">
            <div style="font-weight:900; font-size:1.05rem; color:#5b21b6; margin-bottom:6px;">🪔 Prescribed Remedies for Planetary Neutralization:</div>
            <div style="font-size:0.93rem; line-height:1.7; color:#3b0764;">
                • <b>Mantra Japa:</b> Recite the <b>Shani Beej Mantra</b> (ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः) 108 times at twilight on Saturdays facing West.<br>
                • <b>Vitality Shield:</b> Recite the <b>Hanuman Chalisa</b> daily to boost pranic fire, disperse lethargy, and protect mental peace.<br>
                • <b>Charity & Service:</b> Donate mustard oil, black sesame seeds, or dark blankets to laborers, sweepers, or elderly persons on Saturdays.<br>
                • <b>Behavioral Grounding:</b> Practice absolute punctuality, avoid harsh speech, and avoid shortcuts in contractual agreements.
            </div>
        </div>
    </div>
    """)

    st.write("")
    if st.button("📿 Open Dedicated Digital Japa Counter", type="primary", use_container_width=True):
        st.session_state.current_page = "mantra"
        st.rerun()

# ==============================================================================
# TAB 5: LIVE PREDICTION
# ==============================================================================
def render_page_live():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    now_ist = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
    now_ist = now_ist.replace(tzinfo=None)

    cur_star_idx, s_dt, e_dt = get_current_nakshatra_window(now_ist)
    offset = (cur_star_idx - chart_info["star_idx"]) % 9
    nav_name, icon, quality = NAVTARA_NAMES[offset]
    vahan_info = calculate_shani_vahan(chart_info["star_idx"], cur_star_idx)
    p_day = get_personal_day_vibe(dob_parsed, now_ist.date(), current_lang)

    insights = get_detailed_day_insights(offset, vahan_info, NAKSHATRAS[cur_star_idx - 1], p_day)

    muhurtas = calculate_daily_muhurtas(now_ist.date(), u_lat, u_lon)
    abhijit_s, abhijit_e = muhurtas["abhijit"]
    rahu_s, rahu_e = muhurtas["rahu"]
    yama_s, yama_e = muhurtas["yamaganda"]

    is_abhijit = abhijit_s <= now_ist <= abhijit_e
    is_rahu = rahu_s <= now_ist <= rahu_e
    is_yama = yama_s <= now_ist <= yama_e

    now_time_str = now_ist.strftime('%I:%M %p')

    if is_rahu:
        status_banner = f"""
        <div style="background:#fee2e2; border:2px solid #ef4444; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#b91c1c; font-size:1.02rem;">🔴 CAUTION WINDOW ACTIVE: Rahu Kaal in Operation ({now_time_str} IST)</b>
                <div style="font-size:0.88rem; color:#7f1d1d; margin-top:2px;">Pause new contract signing, travel departures, and major capital moves until {rahu_e.strftime('%I:%M %p')}.</div>
            </div>
            <span style="font-size:1.8rem;">🛑</span>
        </div>
        """
    elif is_yama:
        status_banner = f"""
        <div style="background:#fee2e2; border:2px solid #ef4444; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#b91c1c; font-size:1.02rem;">🔴 CAUTION WINDOW ACTIVE: Yamaganda in Operation ({now_time_str} IST)</b>
                <div style="font-size:0.88rem; color:#7f1d1d; margin-top:2px;">Avoid launching crucial ventures or final legal settlements until {yama_e.strftime('%I:%M %p')}.</div>
            </div>
            <span style="font-size:1.8rem;">⚠️</span>
        </div>
        """
    elif is_abhijit:
        status_banner = f"""
        <div style="background:#dcfce7; border:2px solid #22c55e; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#15803d; font-size:1.02rem;">🟢 GOLDEN ACTION WINDOW ACTIVE: Abhijit Muhurta ({now_time_str} IST)</b>
                <div style="font-size:0.88rem; color:#14532d; margin-top:2px;">Supreme cosmic victory window. Highly auspicious for approvals, launches, and decisions until {abhijit_e.strftime('%I:%M %p')}.</div>
            </div>
            <span style="font-size:1.8rem;">🌟</span>
        </div>
        """
    else:
        status_banner = f"""
        <div style="background:#f0fdf4; border:1.5px solid #86efac; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#166534; font-size:0.98rem;">🟢 SAFE TO ACT: Standard Favorable Orbit ({now_time_str} IST)</b>
                <div style="font-size:0.86rem; color:#15803d; margin-top:2px;">No planetary friction windows currently active. Next Abhijit: {abhijit_s.strftime('%I:%M %p')} | Rahu Kaal: {rahu_s.strftime('%I:%M %p')}</div>
            </div>
            <span style="font-size:1.6rem;">⏱️</span>
        </div>
        """

    render_html(f"""
    <div class="light-card-live">
        <div style="font-weight:900; font-size:1.25rem; color:#0369a1; margin-bottom:1rem; border-bottom:2px solid #bae6fd; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{t('live_pulse_title', current_lang)}</span>
            <span style="font-size:0.85rem; background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:20px; font-weight:900;">LIVE IST</span>
        </div>

        {status_banner}

        <div style="background:#f0f9ff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:0.85rem; color:#0284c7; font-weight:800; text-transform:uppercase;">CURRENT MOON NAKSHATRA</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#0369a1;">{NAKSHATRAS[cur_star_idx - 1]}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.8rem;">{icon}</div>
                    <div style="font-size:0.88rem; font-weight:900; color:#0369a1;">{quality}</div>
                </div>
            </div>
            <div style="font-size:1.05rem; font-weight:900; color:#0284c7; margin-top:8px;">Navtara: {nav_name}</div>
            <div style="font-size:0.92rem; color:#334155; margin-top:6px; line-height:1.5;">
                ⏳ <b>Active Moon Transit Window:</b><br>
                {s_dt.strftime('%a, %d %b %I:%M %p')} → {e_dt.strftime('%a, %d %b %I:%M %p IST')}
            </div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <b>⏱️ Timing Windows for Today ({prof['city']}):</b><br>
            • 🌟 <b>Abhijit Muhurta:</b> {abhijit_s.strftime('%I:%M %p')} – {abhijit_e.strftime('%I:%M %p IST')} (Golden Window)<br>
            • ⚠️ <b>Rahu Kaal:</b> {rahu_s.strftime('%I:%M %p')} – {rahu_e.strftime('%I:%M %p IST')} (Avoid Signings)
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#0369a1; margin-bottom:10px; border-bottom:1px solid #e0f2fe; padding-bottom:5px;">
                📋 Practical Action Green Light Checklist
            </div>
            
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.92rem;">
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>💼 Career & Execution:</b><br>
                    <span style="color:#0f172a;">{'🟢 Green Light: Take bold action in Abhijit window' if offset in [1,3,5,7,8] else '🔴 Hold Back: Avoid starting disputes or high-stakes requests'}</span>
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>💰 Wealth & Financials:</b><br>
                    <span style="color:#0f172a;">{'🟢 Favorable: Execute capital transfers & investments' if offset in [1,3,5,7,8] else '🔴 Cautious: Strictly avoid speculative leverage & loans'}</span>
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>🏠 Domestic & Relations:</b><br>
                    <span style="color:#0f172a;">{'🟢 Harmonious: Excellent for family discussions' if offset in [1,3,5,7,8] else '🟡 Sensitive: Practice calm listening; avoid debates'}</span>
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>🌿 Health & Energy:</b><br>
                    <span style="color:#0f172a;">{'🟢 High Vitality: Great for workouts & physical tasks' if offset in [1,3,5,7,8] else '🔴 Prone to Fatigue: Rest well and hydrate deeply'}</span>
                </div>
            </div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#0369a1; margin-bottom:8px; border-bottom:1px solid #e0f2fe; padding-bottom:5px;">
                🧠 Cognitive & Strategic Archetype: {insights['theme_title']}
            </div>
            <div style="font-size:0.95rem; line-height:1.7; color:#1e293b; margin-bottom:12px;">
                {insights['theme_desc']}
            </div>

            <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; border-left:4px solid #16a34a; margin-bottom:10px;">
                <b style="color:#15803d; font-size:0.95rem;">🚀 Prime Opportunities & Protocols:</b>
                <div style="font-size:0.92rem; line-height:1.6; color:#166534; margin-top:2px;">{insights['opportunities']}</div>
            </div>

            <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; border-left:4px solid #e11d48;">
                <b style="color:#be123c; font-size:0.95rem;">⚠️ Potential Hazards & Red Flags:</b>
                <div style="font-size:0.92rem; line-height:1.6; color:#9f1239; margin-top:2px;">{insights['hazards']}</div>
            </div>
        </div>

        <div style="background:#f0f9ff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd;">
            <div style="font-weight:900; font-size:1.1rem; color:#0369a1; margin-bottom:8px; border-bottom:1px solid #bae6fd; padding-bottom:5px;">
                🪔 Targeted Daily Cosmic Remedies:
            </div>
            <div style="font-size:0.94rem; line-height:1.7; color:#0c4a6e;">
                • <b>Aura Protection Mantra:</b> {insights['remedy_mantra']}<br>
                • <b>Elemental Harmony & Donation:</b> {insights['remedy_charity']}<br>
                • <b>Behavioral & Color Calibration:</b> {insights['remedy_action']}
            </div>
        </div>
    </div>
    """)

# ==============================================================================
# TAB 6: 7 DAYS PREDICTION
# ==============================================================================
def render_page_forecast():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    now_ist = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
    now_ist = now_ist.replace(tzinfo=None)

    transits = get_7_day_moon_transits(now_ist, chart_info["star_idx"])

    render_html(f"""
    <div style="font-weight:900; font-size:1.25rem; color:#1e293b; margin-bottom:0.8rem;">
        {t('forecast_title', current_lang)}
    </div>
    """)

    pill_elements = []
    for tr in transits:
        off = tr["nav_offset"]
        if off in [1, 8]:
            bg, fg, label = "#dcfce7", "#15803d", "Peak 🟢🟢"
        elif off in [3, 5, 7]:
            bg, fg, label = "#f0fdf4", "#166534", "Good 🟢"
        elif off == 0:
            bg, fg, label = "#fef9c3", "#854d0e", "Focus 🟡"
        else:
            bg, fg, label = "#fee2e2", "#b91c1c", "Guard 🔴"
        pill_elements.append(f"""
        <div style="background:{bg}; color:{fg}; padding:8px 6px; border-radius:10px; text-align:center; font-size:0.8rem; font-weight:800; border:1px solid rgba(0,0,0,0.06);">
            <div>{tr['date_str'].split(',')[0]}</div>
            <div style="font-size:0.86rem; margin:2px 0;">{label.split()[1]}</div>
            <div style="font-size:0.75rem;">{tr['star_name'][:4]}</div>
        </div>
        """)
    pills_html = "".join(pill_elements)

    render_html(f"""
    <div style="display:grid; grid-template-columns: repeat(7, 1fr); gap:6px; margin-bottom:1rem;">
        {pills_html}
    </div>
    """)

    for idx, tr in enumerate(transits):
        with st.container(border=True):
            col_t1, col_t2, col_t3 = st.columns([1.6, 2.8, 1.6])
            with col_t1:
                render_html(f"<b>{tr['date_str']}</b><br><span style='font-size:0.92rem; color:#475569; font-weight:700;'>{tr['star_name']}</span>")
            with col_t2:
                vahan_name = tr['vahan'].split()[1] if len(tr['vahan'].split()) > 1 else tr['vahan']
                render_html(f"<span style='font-size:1.1rem;'>{tr['icon']}</span> <b>{tr['nav_name'].split('(')[0]}</b><br><span style='font-size:0.88rem; color:#64748b;'>Mount: {vahan_name}</span>")
            with col_t3:
                if st.button("🔮 View", key=f"btn_tr_{idx}", use_container_width=True):
                    st.session_state.selected_transit_idx = idx
                    st.rerun()

    safe_idx = min(len(transits) - 1, max(0, st.session_state.selected_transit_idx))
    sel_tr = transits[safe_idx]
    
    sel_p_day = get_personal_day_vibe(dob_parsed, sel_tr['date'], current_lang)
    v_info = calculate_shani_vahan(chart_info["star_idx"], sel_tr["star_idx"])
    sel_insights = get_detailed_day_insights(sel_tr["nav_offset"], v_info, sel_tr['star_name'], sel_p_day)
    sel_muh = calculate_daily_muhurtas(sel_tr['date'], u_lat, u_lon)

    render_html(f"""
    <div class="light-card-live" style="margin-top:1.1rem;">
        <div style="font-weight:900; font-size:1.25rem; color:#0369a1; margin-bottom:8px; border-bottom:1.5px solid #bae6fd; padding-bottom:5px;">
            🔮 Detailed Transit Forecast: {sel_tr['date_str']} ({sel_tr['star_name']})
        </div>
        
        <div style="font-size:0.94rem; color:#334155; margin-bottom:10px; line-height:1.5;">
            ⏰ <b>Transit Window:</b> {sel_tr['start_str']} → {sel_tr['end_str']}<br>
            🧭 <b>Navtara Classification:</b> {sel_tr['nav_name']} ({sel_tr['quality']})<br>
            🪐 <b>Saturn Mount (Vahan):</b> {v_info['name']} — <i>{v_info['speed']} ({v_info['type']})</i>
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bae6fd; margin-bottom:10px; font-size:0.91rem;">
            <b>⏱️ Key Timing Windows for {sel_tr['date_str']}:</b><br>
            • 🌟 <b>Abhijit Muhurta:</b> {sel_muh['abhijit'][0].strftime('%I:%M %p')} – {sel_muh['abhijit'][1].strftime('%I:%M %p IST')} (Golden Period)<br>
            • ⚠️ <b>Rahu Kaal:</b> {sel_muh['rahu'][0].strftime('%I:%M %p')} – {sel_muh['rahu'][1].strftime('%I:%M %p IST')} (Avoid Signings)
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #bae6fd; margin-bottom:12px;">
            <b style="color:#0369a1; font-size:1rem;">🎯 Cosmic Archetype: {sel_insights['theme_title']}</b>
            <div style="font-size:0.94rem; line-height:1.65; color:#1e293b; margin-top:4px;">
                {sel_insights['theme_desc']}
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr; gap:8px; margin-bottom:12px;">
            <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; border-left:4px solid #16a34a;">
                <b style="color:#15803d; font-size:0.92rem;">🟢 Favorable Initiatives & Green Lights:</b>
                <div style="font-size:0.91rem; line-height:1.6; color:#166534; margin-top:2px;">{sel_insights['opportunities']}</div>
            </div>
            <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; border-left:4px solid #e11d48;">
                <b style="color:#be123c; font-size:0.92rem;">🔴 Hazards, Caution & Red Lights:</b>
                <div style="font-size:0.91rem; line-height:1.6; color:#9f1239; margin-top:2px;">{sel_insights['hazards']}</div>
            </div>
        </div>

        <div style="background:#f0f9ff; border-radius:10px; padding:12px; border:1px solid #bae6fd;">
            <b style="color:#0369a1; font-size:0.98rem;">🪔 Prescribed Daily Remedies for this Window:</b>
            <div style="font-size:0.92rem; line-height:1.65; color:#0c4a6e; margin-top:4px;">
                • <b>Mantra Japa:</b> {sel_insights['remedy_mantra']}<br>
                • <b>Elemental Donation:</b> {sel_insights['remedy_charity']}<br>
                • <b>Personal Protocol:</b> {sel_insights['remedy_action']}
            </div>
        </div>
    </div>
    """)

# ==============================================================================
# TAB 7: DEDICATED MANTRA SADHANA & DIGITAL JAPA MALA COUNTER
# ==============================================================================
def render_page_mantra():
    render_html("""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.35rem; color:#5b21b6; margin-bottom:0.4rem;">
            📿 Japa Sadhana & Vedic Mantra Sanctuary
        </div>
        <div style="font-size:0.95rem; color:#475569; line-height:1.6;">
            Select from Supreme Classical Mantras, the 9 Navagraha Planetary Beej Mantras, 
            or your personalized Birth Nakshatra Beej Mantra to chant with the 108-bead digital Mala counter.
        </div>
    </div>
    """)

    # 1. Base Classical Protection Mantras
    classical_mantras = {
        "Maha Mrityunjaya Mantra (Supreme Protection)": {
            "sanskrit": "ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्।\nउर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय मामृतात्॥",
            "translit": "Om Tryambakam Yajamahe Sugandhim Pushti-Vardhanam |\nUrvarukamiva Bandhanan-Mrityor-Mukshiya Maamritat ||",
            "meaning": "We meditate on the Three-Eyed Lord Shiva, who permeates and nourishes all beings. May He liberate us from the bonds of fear and death into immortality.",
            "rules": "• Best chanted at dawn or dusk facing East or North.\n• Use a Rudraksha Mala.\n• Pacifies severe transit friction (Vipat, Vadha) and shields cellular vitality."
        },
        "Gayatri Mantra (Solar Illumination)": {
            "sanskrit": "ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात्॥",
            "translit": "Om Bhur Bhuvah Swah Tat Savitur Varenyam Bhargo Devasya Dheemahi Dhiyo Yo Nah Prachodayat ||",
            "meaning": "We meditate upon the supreme divine brilliance of the Sun who illuminates the inner cosmos. May that divine light awaken and inspire our intellect.",
            "rules": "• Best chanted during Brahma Muhurta or at sunrise facing East.\n• Use a Tulsi or Sandalwood Mala.\n• Enhances mental clarity, vitality, and cellular healing."
        },
        "Vishnu Sahasranama Shloka (Aura Shield)": {
            "sanskrit": "ॐ नमो भगवते वासुदेवाय॥",
            "translit": "Om Namo Bhagavate Vasudevaya ||",
            "meaning": "Salutations to the Supreme Preserver of the Cosmos who dwells within all living hearts.",
            "rules": "• Chant in the morning facing East.\n• Harmonizes favorable transits (Sampat, Sadhana, Ati-Mitra).\n• Brings peace to the home and liquid capital stability."
        }
    }

    category = st.radio(
        "**Select Mantra Category:**",
        options=["Classical & Protection", "9 Navagraha Beej Mantras", "27 Nakshatra Beej Mantras"],
        horizontal=True
    )

    if category == "Classical & Protection":
        mantra_choice = st.selectbox("Choose Classical Mantra:", list(classical_mantras.keys()))
        m_info = classical_mantras[mantra_choice]
    elif category == "9 Navagraha Beej Mantras":
        from databanks import NAVAGRAHA_BEEJ_MANTRAS
        mantra_choice = st.selectbox("Choose Planetary Beej Mantra:", list(NAVAGRAHA_BEEJ_MANTRAS.keys()))
        m_info = NAVAGRAHA_BEEJ_MANTRAS[mantra_choice]
    else:
        from databanks import NAKSHATRA_BEEJ_MANTRAS
        nak_options = {idx: data["name"] for idx, data in NAKSHATRA_BEEJ_MANTRAS.items()}
        
        # Pre-select user's Janma Nakshatra if chart is loaded
        default_idx = (chart_info["star_idx"] - 1) if chart_info else 0
        selected_star_idx = st.selectbox(
            "Choose Nakshatra Beej Mantra:",
            options=list(nak_options.keys()),
            format_func=lambda x: nak_options[x],
            index=default_idx
        )
        m_info = NAKSHATRA_BEEJ_MANTRAS[selected_star_idx]

    # Render Card
    render_html(f"""
    <div style="background:#ffffff; border:1.5px solid #ddd6fe; border-radius:14px; padding:18px; margin:14px 0; box-shadow:0 3px 12px rgba(139,92,246,0.06);">
        <div style="font-size:1.4rem; font-weight:900; color:#1e1b4b; text-align:center; font-family:serif; line-height:1.6; white-space:pre-line;">
            {m_info['sanskrit']}
        </div>
        <div style="font-size:0.95rem; color:#6d28d9; text-align:center; font-style:italic; margin-top:8px; line-height:1.5; white-space:pre-line;">
            {m_info['translit']}
        </div>
        <hr style="margin:14px 0; border:none; border-top:1px solid #ede9fe;">
        <div style="font-size:0.93rem; color:#334155; line-height:1.7;">
            <b>📜 Meaning:</b> {m_info['meaning']}<br><br>
            <b>🧘 Sadhana Guidelines:</b><br>{m_info['rules'].replace(chr(10), '<br>')}
        </div>
    </div>
    """)

    # Interactive 108-Bead Mala Counter
    with st.container(border=True):
        st.markdown(f"### 📿 Digital Mala: **{st.session_state.japa_count} / 108** Beads")
        progress_val = min(1.0, st.session_state.japa_count / 108.0)
        st.progress(progress_val, text=f"Mala Progress: {int(progress_val * 100)}% | Completed Malas: {st.session_state.mala_rounds}")

        col_tap, col_reset = st.columns([2, 1])
        with col_tap:
            if st.button("📿 Tap Bead (+1)", type="primary", use_container_width=True):
                st.session_state.japa_count += 1
                if st.session_state.japa_count >= 108:
                    st.session_state.japa_count = 0
                    st.session_state.mala_rounds += 1
                    st.balloons()
                    st.success("🎉 Om Shanti! You completed 1 full Mala (108 Chants). May the vibration bring peace and protection!")
                st.rerun()
        with col_reset:
            if st.button("🔄 Reset Counter", use_container_width=True):
                st.session_state.japa_count = 0
                st.session_state.mala_rounds = 0
                st.rerun()

# ==============================================================================
# ROUTER DISPATCHER: RENDER THE SELECTED PAGE
# ==============================================================================
PAGES = {
    "about": render_page_about,
    "profile": render_page_profile,
    "numerology": render_page_numerology,
    "shani": render_page_shani,
    "live": render_page_live,
    "forecast": render_page_forecast,
    "mantra": render_page_mantra,
    "install_guide": render_page_install_guide,
}

active_page_func = PAGES.get(st.session_state.current_page, render_page_about)
active_page_func()
