import streamlit as st
import datetime
import urllib.parse
import math

# ==========================================
# DEPENDENCY CHECKER
# ==========================================
try:
    import requests
    import ephem
except ModuleNotFoundError as e:
    st.error(f"🚨 **Missing Library Error:** `{e.name}`")
    st.info("To fix this, open your terminal/command prompt and run:")
    st.code("pip install requests ephem", language="bash")
    st.stop()

# ==========================================
# 1. PAGE CONFIGURATION & CSS
# ==========================================
st.set_page_config(page_title="Navtara Pulse", page_icon="🌙", layout="centered")

st.markdown("""
    <style>
    /* Purple background for language selector */
    div[data-baseweb="select"] > div { 
        background-color: #6a0dad !important; 
        color: white !important; 
        border-radius: 8px; 
        font-weight: bold; 
    }
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    
    /* High-contrast Light Blue Transit Cards */
    .transit-card { 
        background-color: #e0f2fe; 
        color: #0f172a;
        padding: 16px; 
        border-radius: 12px 12px 0 0; 
        margin-bottom: 0px !important; 
        border-left: 6px solid #0284c7; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); 
    }
    .transit-card h5 {
        color: #0369a1 !important;
        margin-top: 0;
        font-weight: 700;
    }
    .transit-card p {
        color: #1e293b !important;
        margin-bottom: 4px;
        font-size: 0.95rem;
    }
    .verified-badge { 
        background-color: #16a34a; 
        color: white; 
        padding: 8px 12px; 
        border-radius: 6px; 
        font-weight: bold; 
        margin-top: 10px;
        margin-bottom: 15px; 
        display: block; 
        text-align: center; 
    }
    .status-badge { 
        font-weight: bold; 
        color: #0f172a; 
    }
    .cycle-badge { 
        font-size: 0.88em; 
        color: #475569; 
        font-weight: 600;
    }

    /* Glittering Yellow Animation Keyframes */
    @keyframes glitter {
        0% { background-position: 0% 50%; box-shadow: 0 0 12px #f59e0b, 0 0 22px #fbbf24; }
        50% { background-position: 100% 50%; box-shadow: 0 0 22px #f59e0b, 0 0 38px #fef08a, 0 0 12px #d97706; }
        100% { background-position: 0% 50%; box-shadow: 0 0 12px #f59e0b, 0 0 22px #fbbf24; }
    }

    /* Glittering Yellow Main Action Button */
    .glitter-btn div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #f59e0b 0%, #fef08a 25%, #fbbf24 50%, #d97706 75%, #f59e0b 100%) !important;
        background-size: 200% 200% !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        border: 2px solid #fef08a !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        animation: glitter 3s infinite ease-in-out !important;
        text-shadow: 0 1px 1px rgba(255,255,255,0.7) !important;
        width: 100% !important;
    }

    /* Seamless Glittering Yellow Expander Header Attached Below Blue Card */
    div[data-testid="stExpander"] {
        margin-top: -16px !important;
        margin-bottom: 20px !important;
        border: none !important;
    }
    div[data-testid="stExpander"] details {
        border: none !important;
    }
    div[data-testid="stExpander"] details summary {
        background: linear-gradient(135deg, #fef08a 0%, #f59e0b 50%, #fef08a 100%) !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        border-radius: 0 0 12px 12px !important;
        padding: 12px 16px !important;
        border: 2px solid #d97706 !important;
        border-top: none !important;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4) !important;
        animation: glitter 4s infinite ease-in-out !important;
    }
    div[data-testid="stExpander"] details summary:hover {
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.9) !important;
    }

    /* Mobile Save / PWA Banner Card */
    .install-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: 2px solid #818cf8;
        border-radius: 12px;
        padding: 16px;
        color: #f8fafc;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4);
    }
    .install-banner h4 {
        color: #fbbf24 !important;
        margin-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONSTANTS & LOCALIZATION
# ==========================================
nakshatra_list = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

nakshatra_lords = [
    "Ketu", "Venus (Shukra)", "Sun (Surya)", "Moon (Chandra)", "Mars (Mangal)", "Rahu",
    "Jupiter (Guru)", "Saturn (Shani)", "Mercury (Budh)",
    "Ketu", "Venus (Shukra)", "Sun (Surya)", "Moon (Chandra)", "Mars (Mangal)", "Rahu",
    "Jupiter (Guru)", "Saturn (Shani)", "Mercury (Budh)",
    "Ketu", "Venus (Shukra)", "Sun (Surya)", "Moon (Chandra)", "Mars (Mangal)", "Rahu",
    "Jupiter (Guru)", "Saturn (Shani)", "Mercury (Budh)"
]

navtara_names = [
    "Janma (Self / Body)",
    "Sampat (Wealth / Progress) 🟢",
    "Vipat (Obstacles / Delays) 🔴",
    "Kshema (Wellbeing / Comfort)",
    "Pratyari (Opposition / Tension) 🔴",
    "Sadhaka (Success / Achievement) 🟢",
    "Vadha (Risk / Danger) 🔴",
    "Mitra (Friend)",
    "Ati-Mitra (Best Friend) 🟢🟢"
]

cycles = {
    0: "1st Cycle (Janma Group)",
    1: "2nd Cycle (Anujanma Group)",
    2: "3rd Cycle (Trijanma Group)"
}

tara_details_en = {
    0: {
        "status": "Janma (1st Tara - Self)",
        "H": "Focus on self-care and balanced light diet. Body and digestion may feel sensitive today.",
        "C": "Maintain daily routine tasks. Avoid launching major new impulsive projects.",
        "F": "Keep finances stable. Avoid hasty or emotional buying.",
        "M": "Self-reflective, quiet, and calm mindset.",
        "R": ""
    },
    1: {
        "status": "Sampat (2nd Tara - Wealth) 🟢",
        "H": "Energy levels are high. Great day for physical recovery and fitness.",
        "C": "Excellent day for professional growth, key business meetings, and new opportunities.",
        "F": "Highly favorable day for wealth accumulation, investments, and financial gains.",
        "M": "Positive, confident, and optimistic mindset.",
        "R": ""
    },
    2: {
        "status": "Vipat (3rd Tara - Obstacles) 🔴",
        "H": "Vulnerable day physically. Avoid excessive physical strain or high-risk activities.",
        "C": "Sudden hurdles or unexpected delays in projects may arise. Exercise patience.",
        "F": "Strictly avoid speculative investments, trading, or lending money today.",
        "M": "Prone to sudden anxiety, restlessness, or stress.",
        "R": "🛡️ Vedic Remedy (Vipat): Recite or listen to Hanuman Chalisa. Offer fresh water to green plants or birds. Postpone major risky commitments."
    },
    3: {
        "status": "Kshema (4th Tara - Wellbeing)",
        "H": "Good day for general wellbeing, healing, and physical comfort.",
        "C": "Smooth operations, effective teamwork, and steady ongoing progress.",
        "F": "Financial security and safe transactions are favored.",
        "M": "Peaceful, content, and emotionally balanced.",
        "R": ""
    },
    4: {
        "status": "Pratyari (5th Tara - Opposition) 🔴",
        "H": "Mental friction may manifest as fatigue. Ensure adequate sleep and hydration.",
        "C": "Friction or misunderstandings with colleagues or authority figures are possible.",
        "F": "Unexpected expenses or delayed payments can disrupt your budget.",
        "M": "Easily irritated or defensive. Practice mindfulness.",
        "R": "🛡️ Vedic Remedy (Pratyari): Practice silence (Mouna) during arguments. Chant 'Om Sham Shanayscharaya Namah' or donate black sesame/oil."
    },
    5: {
        "status": "Sadhaka (6th Tara - Success) 🟢",
        "H": "Strong vitality and quick overcoming of minor health complaints.",
        "C": "Great achievements, breakthroughs, and successful completion of difficult goals.",
        "F": "Profitable ventures and realization of long-term financial plans.",
        "M": "Determined, highly focused, and intellectually sharp.",
        "R": ""
    },
    6: {
        "status": "Vadha (7th Tara - Danger) 🔴",
        "H": "Higher risk of fatigue, minor injury, or illness. Exercise caution while commuting.",
        "C": "Major blockages or opposition. Do not schedule crucial confrontations today.",
        "F": "Protect your assets. Avoid high-stakes financial commitments.",
        "M": "Overwhelmed, fearful, or defensive.",
        "R": "🛡️ Vedic Remedy (Vadha): Chant Mahamrityunjaya Mantra or 'Om Namah Shivaya'. Offer water or milk to Lord Shiva."
    },
    7: {
        "status": "Mitra (8th Tara - Friend)",
        "H": "Improving health and supportive physical energy.",
        "C": "Expect cooperation from peers and joint success in group tasks.",
        "F": "Collaborative financial gains and steady wealth.",
        "M": "Happy, sociable, and emotionally supported.",
        "R": ""
    },
    8: {
        "status": "Ati-Mitra (9th Tara - Best Friend) 🟢🟢",
        "H": "Excellent physical vitality and vibrant energy.",
        "C": "High growth, ultimate success, and public recognition for your efforts.",
        "F": "Windfalls, bonuses, or highly favorable financial news.",
        "M": "Joyous, spiritually uplifted, and deeply fulfilled.",
        "R": ""
    }
}

translations = {
    "en": {
        "intro_title": "Unlocking the Wisdom of Vedic Astrology",
        "intro_desc": "In Vedic astrology, the Moon's transit through the 27 Nakshatras creates a unique daily energy pattern relative to your birth star (Janma Nakshatra). This app provides accurate, astronomical insights into your daily Navtara Pulse, health, career, and financial guidance.",
        "profile_title": "👤 Birth Profiles Management",
        "horoscope_title": "7-Day Horoscope Prediction & Life Guidance",
        "search_prompt": "🌍 Birth Place Name or 6-Digit Pincode",
        "generate_btn": "✨ Click here to know the Horoscope & Predictions ✨",
        "tara": tara_details_en
    },
    "hi": {
        "intro_title": "वैदिक ज्योतिष के ज्ञान को अनलॉक करें",
        "intro_desc": "वैदिक ज्योतिष में, 27 नक्षत्रों के माध्यम से चंद्रमा का गोचर आपके जन्म नक्षत्र के सापेक्ष एक अनूठा दैनिक ऊर्जा पैटर्न बनाता है। यह ऐप आपके दैनिक नवतारा पल्स, स्वास्थ्य, करियर और वित्तीय मार्गदर्शन में सटीक अंतर्दृष्टि प्रदान करता है।",
        "profile_title": "👤 जन्म प्रोफाइल प्रबंधन",
        "horoscope_title": "7-दिवसीय राशिफल भविष्यवाणी और जीवन मार्गदर्शन",
        "search_prompt": "🌍 जन्म स्थान का नाम या 6-अंकीय पिनकोड",
        "generate_btn": "✨ राशिफल और भविष्यवाणियां जानने के लिए यहां क्लिक करें ✨",
        "tara": tara_details_en 
    }
}
translations["mr"] = translations["hi"]
translations["gu"] = translations["hi"]

# ==========================================
# 3. HELPER & ASTRONOMY FUNCTIONS
# ==========================================
@st.cache_data(show_spinner=False)
def search_places_online(query):
    """Fetch geocoding data from OpenStreetMap Nominatim API."""
    if len(query) < 3:
        return []
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=5"
    headers = {'User-Agent': 'NavtaraPulse/1.0'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

def get_utc_offset_hours(place_obj, place_query):
    """Automatically determine UTC offset in hours based on place data (no user input needed)."""
    if isinstance(place_obj, dict):
        addr = place_obj.get('address', {})
        country_code = addr.get('country_code', '').lower()
        if country_code == 'in':
            return 5.5
        lon = float(place_obj.get('lon', 0))
        if lon != 0:
            return round(lon / 15.0 * 2) / 2
    
    # Default fallback for Indian pincodes or place names
    return 5.5

def get_moon_nakshatra_index(dt_utc):
    """Calculates exact Sidereal Moon Nakshatra index (0 to 26) using PyEphem + Lahiri Ayanamsa."""
    observer = ephem.Observer()
    observer.date = ephem.date(dt_utc)
    moon = ephem.Moon(observer)
    ecl = ephem.Ecliptic(moon)
    
    # Lahiri Ayanamsa approximation
    year = dt_utc.year + (dt_utc.month - 1) / 12.0
    ayanamsa = 23.85306 + (year - 2000.0) * 0.01397
    
    sidereal_lon = (math.degrees(ecl.lon) - ayanamsa) % 360
    nakshatra_index = int(sidereal_lon / 13.333333333333334) % 27
    return nakshatra_index

def calculate_7_day_transits(start_local_dt, utc_offset_hours):
    """Calculates exact Moon transit time windows for the next 7 days in local time."""
    transits = []
    current_local = start_local_dt
    
    current_utc = current_local - datetime.timedelta(hours=utc_offset_hours)
    current_nak = get_moon_nakshatra_index(current_utc)
    window_start = current_local
    
    # Check at 15-minute intervals over 7 days
    for i in range(1, 7 * 96):
        test_local = start_local_dt + datetime.timedelta(minutes=15 * i)
        test_utc = test_local - datetime.timedelta(hours=utc_offset_hours)
        test_nak = get_moon_nakshatra_index(test_utc)
        
        if test_nak != current_nak:
            transits.append({
                "start": window_start,
                "end": test_local,
                "nak_index": current_nak
            })
            current_nak = test_nak
            window_start = test_local
            
    transits.append({
        "start": window_start,
        "end": start_local_dt + datetime.timedelta(days=7),
        "nak_index": current_nak
    })
    return transits

# ==========================================
# 4. MAIN APP LAYOUT & URL PARAMETERS
# ==========================================
query_params = st.query_params

# Initialize session state for multi-profile storage
if 'saved_profiles' not in st.session_state:
    st.session_state['saved_profiles'] = {}

if 'profile_saved' not in st.session_state:
    st.session_state['profile_saved'] = 'saved' in query_params

st.title("🌙 Navtara Pulse")

# Purple Highlighted Language Selector
lang_options = {"en": "English", "hi": "हिन्दी (Hindi)", "mr": "मराठी (Marathi)", "gu": "गुજરાતી (Gujarati)"}
selected_lang_name = st.selectbox("🌐 Select Language", list(lang_options.values()), index=0)
lang_code = [k for k, v in lang_options.items() if v == selected_lang_name][0]
t = translations[lang_code]

st.markdown(f"### {t['intro_title']}")
st.write(t['intro_desc'])
st.divider()

# ==========================================
# 5. MULTI-PROFILE MANAGEMENT & USER INPUT
# ==========================================
st.header(t['profile_title'])

# Profile Selector
profile_names = ["➕ Create New Profile"] + list(st.session_state['saved_profiles'].keys())
selected_profile_key = st.selectbox("📁 Select or Switch Saved Profile", profile_names, index=0)

if selected_profile_key != "➕ Create New Profile" and selected_profile_key in st.session_state['saved_profiles']:
    p = st.session_state['saved_profiles'][selected_profile_key]
    default_name = p.get('n', '')
    default_date = p.get('d', datetime.date(1995, 1, 1))
    default_h = p.get('h', 0)
    default_m = p.get('m', 0)
    default_place = p.get('p', '')
    default_nak_idx = p.get('nak_idx', 0)
else:
    default_name = query_params.get('n', '')
    default_date = datetime.datetime.strptime(query_params.get('d', '1995-01-01'), '%Y-%m-%d').date()
    default_h = int(query_params.get('h', '0'))
    default_m = int(query_params.get('m', '0'))
    default_place = query_params.get('p', '')
    default_nak_idx = None

col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("Name", value=default_name, placeholder="e.g. Rahul Sharma")
    birth_date = st.date_input("Date of Birth", min_value=datetime.date(1925, 1, 1), max_value=datetime.date.today(), value=default_date)

with col2:
    st.write("Time of Birth (24-Hour)")
    tc1, tc2 = st.columns(2)
    with tc1: 
        birth_hour = st.selectbox("HH", [f"{i:02d}" for i in range(24)], index=default_h)
    with tc2: 
        birth_minute = st.selectbox("MM", [f"{i:02d}" for i in range(60)], index=default_m)

# Unified Single Birth Place Search Box
st.write(t['search_prompt'])
place_query = st.text_input(
    "Search Location", 
    value=default_place, 
    placeholder="e.g. Ujjain, Mumbai, London, or 456001",
    label_visibility="collapsed"
)

selected_place_display = place_query
place_obj_data = None

if len(place_query) >= 3:
    places_list = search_places_online(place_query)
    if places_list:
        display_names = [p['display_name'] for p in places_list]
        selected_idx = st.selectbox("Select verified matching location from web:", range(len(display_names)), format_func=lambda x: display_names[x])
        selected_place_display = display_names[selected_idx]
        place_obj_data = places_list[selected_idx]

# Auto-calculate UTC offset in the background
utc_offset_val = get_utc_offset_hours(place_obj_data, place_query)

# Auto-calculate default Janma Nakshatra based on Date/Time
birth_local_dt = datetime.datetime.combine(birth_date, datetime.time(int(birth_hour), int(birth_minute)))
birth_utc_dt = birth_local_dt - datetime.timedelta(hours=utc_offset_val)
auto_janma_idx = get_moon_nakshatra_index(birth_utc_dt) if default_nak_idx is None else default_nak_idx

# Option to verify or adjust Janma Nakshatra directly from Kundli
st.write("✨ **Janma Nakshatra (Birth Star)**")
selected_janma_nakshatra = st.selectbox(
    "Verify/Select your exact Kundli Birth Star:",
    nakshatra_list,
    index=auto_janma_idx,
    help="Auto-calculated based on your birth date and time. You can adjust this if your official Kundli mentions a specific star."
)

# Display Verified Birth Place Badge right above the action button
if selected_place_display:
    st.markdown(f"<div class='verified-badge'>📍 Birth Place: {selected_place_display}</div>", unsafe_allow_html=True)

# Glittering Yellow Action Button Container
st.markdown("<div class='glitter-btn'>", unsafe_allow_html=True)
if st.button(t['generate_btn'], type="primary", use_container_width=True):
    if len(place_query) < 3:
        st.error("⚠️ Please enter a valid Birth Place or Pincode to generate your predictions.")
    else:
        # Save profile to session state
        profile_key_name = user_name or selected_place_display or "Saved Profile"
        st.session_state['saved_profiles'][profile_key_name] = {
            'n': user_name,
            'd': birth_date,
            'h': int(birth_hour),
            'm': int(birth_minute),
            'p': selected_place_display,
            'nak_idx': nakshatra_list.index(selected_janma_nakshatra)
        }
        
        st.query_params['n'] = user_name
        st.query_params['d'] = str(birth_date)
        st.query_params['h'] = str(int(birth_hour))
        st.query_params['m'] = str(int(birth_minute))
        st.query_params['p'] = selected_place_display
        st.query_params['saved'] = 'true'
        st.session_state['profile_saved'] = True
st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 6. RESULTS & HOROSCOPE SCHEDULE
# ==========================================
if st.session_state.get('profile_saved'):
    st.divider()
    
    # Exact Janma Nakshatra & Nakshatra Lord
    janma_index = nakshatra_list.index(selected_janma_nakshatra)
    janma_lord = nakshatra_lords[janma_index]
    
    st.success(f"🌟 **{user_name or 'User'}'s Janma Nakshatra:** {selected_janma_nakshatra} | **Nakshatra Lord:** {janma_lord}")
    
    # Save & Install Guidance Card for Mobile Access
    st.markdown("""
        <div class="install-banner">
            <h4>📱 Save & Install for 1-Click Mobile Access</h4>
            <p>Your birth profile details have been saved to this custom URL. To open this horoscope anytime without re-entering details:</p>
            <ul>
                <li><b>iPhone (Safari):</b> Tap the <i>Share</i> icon at the bottom ➔ select <b>"Add to Home Screen"</b>.</li>
                <li><b>Android (Chrome):</b> Tap the three dots (⋮) at top-right ➔ select <b>"Add to Home screen"</b> or <b>"Install App"</b>.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    st.header(t['horoscope_title'])
    
    # Generate exact 7-Day Moon Transits
    now_local = datetime.datetime.now()
    transits = calculate_7_day_transits(now_local, utc_offset_val)
    
    for transit in transits:
        # Astronomical Navtara Calculation
        nak_difference = (transit["nak_index"] - janma_index) % 27
        tara_index = nak_difference % 9
        cycle_group = cycles[nak_difference // 9]
        
        tara_data = t["tara"][tara_index]
        tara_badge_name = navtara_names[tara_index]
        transit_nak_name = nakshatra_list[transit["nak_index"]]
        transit_nak_lord = nakshatra_lords[transit["nak_index"]]
        
        start_str = transit["start"].strftime('%a, %d %b %I:%M %p')
        end_str = transit["end"].strftime('%a, %d %b %I:%M %p')
        
        # Light Blue High Contrast Card
        st.markdown(f"""
        <div class="transit-card">
            <h5>🕒 {start_str} ➔ {end_str}</h5>
            <p><b>Status:</b> <span class='status-badge'>{tara_badge_name}</span></p>
            <p><b>Moon Nakshatra:</b> {transit_nak_name} (<b>Nakshatra Lord:</b> {transit_nak_lord})</p>
            <p class='cycle-badge'><b>Navtara Series:</b> {cycle_group}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Glittering Yellow Expander
        with st.expander("✨ Click here to see the Prediction & Life Guidance ✨"):
            st.write(f"**Health:** {tara_data['H']}")
            st.write(f"**Career:** {tara_data['C']}")
            st.write(f"**Finance:** {tara_data['F']}")
            st.write(f"**Mindset:** {tara_data['M']}")
            if tara_data['R']:
                st.error(tara_data['R'])

# ==========================================
# 7. SHARE APP (Direct Link Payload)
# ==========================================
st.divider()
st.subheader("🔗 Share Navtara Pulse")
app_url = "https://navtara-pulse.streamlit.app"
share_text = urllib.parse.quote(f"Check out Navtara Pulse - Precision Moon Transit: {app_url}")

sc1, sc2, sc3 = st.columns(3)
with sc1: 
    st.link_button("💬 WhatsApp", f"https://api.whatsapp.com/send?text={share_text}", use_container_width=True)
with sc2: 
    st.link_button("✉️ Email", f"mailto:?subject=Navtara Pulse&body={share_text}", use_container_width=True)
with sc3: 
    st.link_button("✈️ Telegram", f"https://t.me/share/url?url={app_url}&text=Check out Navtara Pulse", use_container_width=True)
