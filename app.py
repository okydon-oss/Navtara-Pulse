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
    st.info("To fix this, open your terminal and run: `pip install requests ephem`")
    st.stop()

# ==========================================
# 1. PAGE CONFIGURATION & CSS
# ==========================================
st.set_page_config(page_title="Navtara Pulse", page_icon="🌙", layout="centered")

st.markdown("""
    <style>
    /* Purple background for language selector */
    div[data-baseweb="select"] > div { background-color: #6a0dad !important; color: white !important; border-radius: 8px; font-weight: bold; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    
    /* Responsive Transit Cards */
    .transit-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #6a0dad; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .verified-badge { background-color: #4CAF50; color: white; padding: 8px 12px; border-radius: 5px; font-weight: bold; margin-bottom: 15px; display: inline-block; width: 100%; text-align: center; }
    .status-badge { font-weight: bold; color: #ffcc00; }
    .cycle-badge { font-size: 0.9em; color: #aaaaaa; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. COMPLETE PREDICTION & LANGUAGE DICTIONARY
# ==========================================
# Full dictionaries providing actual details for the 9 Navtara categories.
tara_details_en = {
    0: {"name": "Janma", "status": "Janma (Self)", "H": "Focus on self-care. Your body and digestion may feel sensitive today.", "C": "Maintain your daily routine. Avoid launching major new projects.", "F": "Keep finances stable. Avoid impulsive buying.", "M": "Self-reflective, quiet, and calm.", "R": ""},
    1: {"name": "Sampat", "status": "Sampat (Wealth) 🟢", "H": "Energy levels are high. Great day for recovery and healing.", "C": "Excellent for professional growth, meetings, and new opportunities.", "F": "Highly favorable day for investments and financial gains.", "M": "Positive, confident, and outgoing.", "R": ""},
    2: {"name": "Vipat", "status": "Vipat (Obstacles) 🔴", "H": "Vulnerable day. Strictly avoid physical strain or risky activities.", "C": "Sudden hurdles or unexpected delays in projects may occur.", "F": "Strictly avoid speculative investments or lending money.", "M": "Prone to sudden anxiety or stress.", "R": "🛡️ Remedy: Recite Hanuman Chalisa. Offer water to plants or birds. Postpone major risky commitments."},
    3: {"name": "Kshema", "status": "Kshema (Wellbeing)", "H": "Good day for general wellbeing and physical comfort.", "C": "Smooth operations, teamwork, and steady progress.", "F": "Financial security and safe transactions are favored.", "M": "Peaceful, content, and emotionally balanced.", "R": ""},
    4: {"name": "Pratyari", "status": "Pratyari (Opposition) 🔴", "H": "Mental stress may manifest physically. Ensure you rest well.", "C": "Friction with colleagues or authority is highly possible.", "F": "Unexpected expenses or delayed payments can frustrate you.", "M": "Easily irritated or frustrated.", "R": "🛡️ Remedy: Practice absolute silence during tense arguments. Chant 'Om Sham Shanayscharaya Namah' or donate sesame oil."},
    5: {"name": "Sadhaka", "status": "Sadhaka (Success) 🟢", "H": "Strong vitality and quick overcoming of minor ailments.", "C": "Great achievements and successful completion of difficult tasks.", "F": "Profitable ventures and realization of long-term financial goals.", "M": "Determined, highly focused, and sharp.", "R": ""},
    6: {"name": "Vadha", "status": "Vadha (Danger) 🔴", "H": "High risk of injury or sudden illness. Be extremely cautious driving.", "C": "Major blockages. Do not schedule important meetings today.", "F": "Protect your current assets. High chance of financial loss.", "M": "Overwhelmed, fearful, or highly pessimistic.", "R": "🛡️ Remedy: Chant Mahamrityunjaya mantra or 'Om Namah Shivaya'. Offer milk/water to Lord Shiva. Avoid unnecessary travel."},
    7: {"name": "Mitra", "status": "Mitra (Friend)", "H": "Improving health and supportive physical energy.", "C": "Expect help from peers and cooperative success at the workplace.", "F": "Collaborative financial gains and stable wealth.", "M": "Happy, sociable, and emotionally supported.", "R": ""},
    8: {"name": "Ati-Mitra", "status": "Ati-Mitra (Best Friend) 🟢🟢", "H": "Excellent physical vitality and vibrant energy.", "C": "High growth, ultimate success, and public recognition.", "F": "Windfalls, bonuses, or highly favorable financial news.", "M": "Joyous, spiritually uplifted, and deeply fulfilled.", "R": ""}
}

translations = {
    "en": {
        "intro_title": "Unlocking the Wisdom of Vedic Astrology",
        "intro_desc": "Explore the profound insights that astrology can offer. By understanding the Nakshatras and your Navtara Pulse, you gain valuable knowledge about your daily life path, energy levels, and potential challenges.",
        "profile_title": "👤 Your Birth Profile",
        "horoscope_title": "7-Day Horoscope Prediction & Life Guidance",
        "search_prompt": "🌍 Birth Place Name or 6-Digit Pincode",
        "save_btn": "💾 Save Profile Changes",
        "tara": tara_details_en
    },
    "hi": {
        "intro_title": "वैदिक ज्योतिष के ज्ञान को अनलॉक करें",
        "intro_desc": "नक्षत्रों और नवतारा को समझकर, आप अपने दैनिक जीवन, ऊर्जा और संभावित चुनौतियों के बारे में मूल्यवान ज्ञान प्राप्त कर सकते हैं।",
        "profile_title": "👤 आपकी जन्म कुंडली प्रोफ़ाइल",
        "horoscope_title": "7-दिवसीय राशिफल भविष्यवाणी और जीवन मार्गदर्शन",
        "search_prompt": "🌍 जन्म स्थान का नाम या 6-अंकीय पिनकोड",
        "save_btn": "💾 प्रोफ़ाइल सहेजें",
        "tara": tara_details_en # (For brevity, UI is translated, predictions use English base. You can translate tara_details_en to Hindi here)
    }
}
# Map MR and GU to UI translations
translations["mr"] = translations["hi"]
translations["gu"] = translations["hi"]

nakshatra_list = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

cycles = {
    0: "1st Cycle (Janma Group)",
    1: "2nd Cycle (Anujanma Group)",
    2: "3rd Cycle (Trijanma Group)"
}

# ==========================================
# 3. HELPER & ASTRONOMY FUNCTIONS
# ==========================================
@st.cache_data(show_spinner=False)
def search_places_online(query):
    if len(query) < 3: return []
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=5"
    try:
        res = requests.get(url, headers={'User-Agent': 'NavtaraPulse/1.0'}, timeout=5)
        if res.status_code == 200:
            return [r['display_name'] for r in res.json()]
    except: pass
    return []

def get_moon_nakshatra_index(dt_obj):
    observer = ephem.Observer()
    observer.date = ephem.date(dt_obj)
    moon = ephem.Moon(observer)
    sidereal_lon = (math.degrees(moon.hlon) - 24.1) % 360
    return int(sidereal_lon / 13.3333) % 27

def calculate_7_day_transits(start_dt):
    transits = []
    current_dt = start_dt
    current_nak = get_moon_nakshatra_index(current_dt)
    window_start = current_dt
    
    for i in range(1, 7 * 48): # 30 min intervals for 7 days
        test_dt = start_dt + datetime.timedelta(minutes=30 * i)
        test_nak = get_moon_nakshatra_index(test_dt)
        if test_nak != current_nak:
            transits.append({"start": window_start, "end": test_dt, "nak_index": current_nak})
            current_nak = test_nak
            window_start = test_dt
            
    transits.append({"start": window_start, "end": start_dt + datetime.timedelta(days=7), "nak_index": current_nak})
    return transits

# ==========================================
# 4. MAIN APP LAYOUT & URL STATE
# ==========================================
# URL Persistence: Read parameters from URL if they exist
query_params = st.query_params
if 'profile_saved' not in st.session_state:
    st.session_state['profile_saved'] = 'saved' in query_params

st.title("🌙 Navtara Pulse")

# Purple Highlighted Language Selector
lang_options = {"en": "English", "hi": "हिन्दी (Hindi)", "mr": "मराठी (Marathi)", "gu": "ગુજરાતી (Gujarati)"}
selected_lang_name = st.selectbox("🌐 Select Language", list(lang_options.values()), index=0)
lang_code = [k for k, v in lang_options.items() if v == selected_lang_name][0]
t = translations[lang_code]

st.markdown(f"### {t['intro_title']}")
st.write(t['intro_desc'])
st.divider()

# ==========================================
# 5. UNIFIED USER PROFILE WINDOW
# ==========================================
st.header(t['profile_title'])

# Load defaults from URL Query Params if available
default_name = query_params.get('n', '')
default_date = datetime.datetime.strptime(query_params.get('d', '1995-01-01'), '%Y-%m-%d').date()
default_h = int(query_params.get('h', '0'))
default_m = int(query_params.get('m', '0'))
default_place = query_params.get('p', '')

col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("Name", value=default_name)
    birth_date = st.date_input("Date of Birth", min_value=datetime.date(1925, 1, 1), max_value=datetime.date.today(), value=default_date)

with col2:
    st.write("Time of Birth (24-Hour)")
    tc1, tc2 = st.columns(2)
    with tc1: birth_hour = st.selectbox("HH", [f"{i:02d}" for i in range(24)], index=default_h)
    with tc2: birth_minute = st.selectbox("MM", [f"{i:02d}" for i in range(60)], index=default_m)

st.write(t['search_prompt'])
place_query = st.text_input("Type 3 letters or a pincode to search...", value=default_place)
selected_place = default_place

if len(place_query) >= 3 and place_query != default_place:
    with st.spinner("Searching online..."):
        places = search_places_online(place_query)
        if places:
            selected_place = st.selectbox("Select matching location:", places)

if selected_place:
    st.markdown(f"<div class='verified-badge'>📍 Verified Birth Place: {selected_place}</div>", unsafe_allow_html=True)

if st.button(t['save_btn'], use_container_width=True):
    if not selected_place:
        st.error("Please search and select a verified birthplace.")
    else:
        # Save to session and URL parameters for persistent bookmarking!
        st.query_params['n'] = user_name
        st.query_params['d'] = str(birth_date)
        st.query_params['h'] = str(int(birth_hour))
        st.query_params['m'] = str(int(birth_minute))
        st.query_params['p'] = selected_place
        st.query_params['saved'] = 'true'
        st.session_state['profile_saved'] = True
        st.success("Profile Saved! You can now bookmark this URL to save your details permanently.")

# ==========================================
# 6. RESULTS & COMBINED TABLE
# ==========================================
if st.session_state.get('profile_saved'):
    st.divider()
    
    # Accurate Astronomical Calculation
    birth_dt = datetime.datetime.combine(birth_date, datetime.time(int(birth_hour), int(birth_minute)))
    janma_index = get_moon_nakshatra_index(birth_dt)
    janma_nakshatra = nakshatra_list[janma_index]
    
    st.success(f"🌟 **{user_name}'s Janma Nakshatra:** {janma_nakshatra}")
    st.header(t['horoscope_title'])
    
    now = datetime.datetime.now()
    transits = calculate_7_day_transits(now)
    
    for transit in transits:
        # Calculate Navtara Series and Cycle logic
        nak_difference = (transit["nak_index"] - janma_index) % 27
        tara_index = nak_difference % 9
        cycle_group = cycles[nak_difference // 9] 
        
        tara_data = t["tara"][tara_index]
        moon_nakshatra = nakshatra_list[transit["nak_index"]]
        
        start_str = transit["start"].strftime('%a, %d %b %I:%M %p')
        end_str = transit["end"].strftime('%a, %d %b %I:%M %p')
        
        # Responsive UI Card rendering all details
        st.markdown(f"""
        <div class="transit-card">
            <h5 style='margin-top:0; color: #ffffff;'>🕒 {start_str} ➔ {end_str}</h5>
            <p style='margin-bottom:5px;'>
                <span class='status-badge'>Status: {tara_data['status']}</span> <br/>
                <b>Moon Nakshatra:</b> {moon_nakshatra} <br/>
                <span class='cycle-badge'>Navtara Series: {cycle_group}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Unified Dropdown for Predictions & Guidance
        with st.expander("🔮 Daily Prediction & Life Guidance"):
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
with sc1: st.link_button("💬 WhatsApp", f"https://api.whatsapp.com/send?text={share_text}", use_container_width=True)
with sc2: st.link_button("✉️ Email", f"mailto:?subject=Navtara Pulse&body={share_text}", use_container_width=True)
with sc3: st.link_button("✈️ Telegram", f"https://t.me/share/url?url={app_url}&text=Check out Navtara Pulse", use_container_width=True)
