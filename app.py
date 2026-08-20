import streamlit as st
import datetime
import urllib.parse
import math

try:
    import requests
    import ephem
except ModuleNotFoundError as e:
    st.error(f"🚨 **Missing Library Error:** `{e.name}`")
    st.info("To fix this, open your terminal/command prompt and run:")
    st.code("pip install requests ephem", language="bash")
    st.stop()

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
    
    /* Unified Transit Card Top Block */
    .transit-card { 
        background-color: #e0f2fe; 
        color: #0f172a;
        padding: 16px; 
        border-radius: 12px 12px 0 0; 
        margin-bottom: 0px; 
        border-left: 6px solid #0284c7; 
        border-top: 1px solid #bae6fd;
        border-right: 1px solid #bae6fd;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); 
    }
    .transit-card h5 {
        color: #0369a1 !important;
        margin-top: 0;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 6px;
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
    .current-badge {
        background-color: #0284c7;
        color: white;
        font-size: 0.75rem;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    /* Seamless Expander Attachment to the Transit Card */
    div[data-testid="stExpander"] {
        border-top: none !important;
        border-top-left-radius: 0 !important;
        border-top-right-radius: 0 !important;
        border-bottom-left-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
        border-left: 6px solid #0284c7 !important;
        border-right: 1px solid #bae6fd !important;
        border-bottom: 1px solid #bae6fd !important;
        background-color: #f0f9ff !important;
        margin-bottom: 18px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stExpander"] summary {
        background-color: #dbeafe !important;
        color: #0369a1 !important;
        font-weight: 700 !important;
        border-radius: 0 !important;
        padding: 10px 14px !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: #bfdbfe !important;
        color: #0c4a6e !important;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        background-color: #f8fafc !important;
        padding: 14px !important;
        border-radius: 0 0 10px 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

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
    "Janma (Self / Body) ⚪",
    "Sampat (Wealth / Progress) 🟢",
    "Vipat (Obstacles / Delays) 🔴",
    "Kshema (Wellbeing / Comfort) 🟢",
    "Pratyari (Opposition / Tension) 🔴",
    "Sadhaka (Success / Achievement) 🟢",
    "Vadha (Risk / Danger) 🔴",
    "Mitra (Friend) 🟢",
    "Ati-Mitra (Best Friend) 🟢🟢"
]

num_lords = {
    1: "Sun (Surya)",
    2: "Moon (Chandra)",
    3: "Jupiter (Guru)",
    4: "Rahu",
    5: "Mercury (Budh)",
    6: "Venus (Shukra)",
    7: "Ketu",
    8: "Saturn (Shani)",
    9: "Mars (Mangal)"
}

lucky_numbers_map = {
    1: "1, 2, 3, 9",
    2: "1, 2, 5",
    3: "1, 2, 3, 9",
    4: "1, 4, 5, 6, 7",
    5: "1, 5, 6",
    6: "1, 5, 6, 7",
    7: "1, 4, 7",
    8: "3, 5, 6, 8",
    9: "1, 2, 3, 9"
}

# Detailed Personal Day Vibration Meanings (Main Card Text)
personal_day_meanings_en = {
    1: "New beginnings, leadership, and bold initiative. Drive new goals with focused confidence.",
    2: "Cooperation, emotional balance, and patience. Focus on active listening and harmonious teamwork.",
    3: "Creative self-expression, communication, and optimism. Share ideas and embrace social connections.",
    4: "Hard work, discipline, and practical foundation building. Organize tasks and avoid shortcut risks.",
    5: "Dynamic change, adaptability, and fast networking. Embrace quick decisions and versatile momentum.",
    6: "Responsibility, family harmony, and domestic wellness. Prioritize relationships and mutual care.",
    7: "Introspection, analytical study, and spiritual calm. Observe quietly before executing major shifts.",
    8: "Executive decision-making, financial strategy, and material ambition. Exercise authoritative focus.",
    9: "Completion of pending matters, clearing clutter, and letting go. Practice detachment and compassion."
}

personal_day_meanings_hi = {
    1: "नई शुरुआत, नेतृत्व और साहसिक पहल। केंद्रित आत्मविश्वास के साथ नए लक्ष्यों को आगे बढ़ाएं।",
    2: "सहयोग, भावनात्मक संतुलन और धैर्य। सक्रिय सुनने और सौहार्दपूर्ण टीम वर्क पर ध्यान केंद्रित करें।",
    3: "रचनात्मक अभिव्यक्ति, संवाद और नई आशा। विचारों को साझा करें और सामाजिक संवाद बढ़ाएं।",
    4: "कड़ी मेहनत, अनुशासन और व्यावहारिक आधार। कार्यों को व्यवस्थित करें और जल्दबाजी से बचें।",
    5: "गतिशील बदलाव, अनुकूलनशीलता और नेटवर्किंग। त्वरित निर्णयों और नई ऊर्जा का स्वागत करें।",
    6: "जिम्मेदारी, पारिवारिक सद्भाव और कल्याण। संबंधों और आपसी देखभाल को प्राथमिकता दें।",
    7: "आत्मनिरीक्षण, गहन विश्लेषण और आध्यात्मिक शांति। बदलाव से पहले शांत अवलोकन करें।",
    8: "कारोबारी निर्णय, वित्तीय योजना और महत्वाकांक्षा। रणनीतिक अनुशासन के साथ काम करें।",
    9: "अधूरे कार्यों का समापन, मानसिक स्पष्टता और क्षमाशीलता। नए चक्र के लिए जगह बनाएं।"
}

# Personal Day Numerology Nuances for Predictions
personal_day_aspects_en = {
    1: {"H": "Solar vitality is active; boost cardiovascular health and physical posture.", "C": "Leadership initiative; drive pending pitches.", "F": "Favorable for launching new revenue ideas.", "M": "Focused, independent, and decisive.", "R": "Lead relationships with warmth; avoid ego clashes.", "Remedy": ""},
    2: {"H": "Lunar influence; maintain fluid intake and emotional peace.", "C": "Collaborative diplomatic negotiations succeed.", "F": "Avoid emotional impulse purchases.", "M": "Empathetic, sensitive, and observant.", "R": "Deepen romantic bonding through sincere listening.", "Remedy": "✨ Numerology Tip: Drink water from a silver cup or practice quiet breathing for calm focus."},
    3: {"H": "Expansive energy; avoid overindulgent heavy meals.", "C": "Excellent for presentations, pitching, and teaching.", "F": "Good day for long-term growth investments.", "M": "Optimistic, joyful, and expressive.", "R": "Warm social gatherings and joyful family exchanges.", "Remedy": ""},
    4: {"H": "Rahu frequency; guard against sudden nervous fatigue.", "C": "Focus on routine audits; strictly avoid shortcut risks.", "F": "Maintain strict budgeting; avoid speculative trading.", "M": "Analytical, grounded, but prone to restlessness.", "R": "Be direct yet polite to prevent sudden miscommunications.", "Remedy": "✨ Numerology Remedy (Day 4): Keep your workspace tidy and chant 'Om Raam Rahave Namah' to calm mental flutter."},
    5: {"H": "Mercurial pace; take short walking breaks to release tension.", "C": "Fast progress in sales, digital work, and networking.", "F": "Opportunities for quick fluid transactions.", "M": "Quick-witted, versatile, and curious.", "R": "Fun, lively outings and spontaneous communication.", "Remedy": ""},
    6: {"H": "Venusian alignment; focus on skin, hydration, and relaxation.", "C": "Ideal for design, client relations, and aesthetic projects.", "F": "Favorable for family assets and aesthetic comforts.", "M": "Harmonious, peaceful, and balanced.", "R": "Heartwarming romantic closeness and family peace.", "Remedy": ""},
    7: {"H": "Ketu vibration; prioritize quiet rest and digestive ease.", "C": "Best for research, auditing, and deep technical study.", "F": "Review finances silently; do not execute hasty transfers.", "M": "Contemplative, highly intuitive, and quiet.", "R": "Seek intimate, meaningful talks over noisy crowds.", "Remedy": "✨ Numerology Remedy (Day 7): Spend 10 minutes in quiet meditation or chant 'Om Kem Ketave Namah'."},
    8: {"H": "Saturnian discipline; care for joint health and posture.", "C": "Command authoritative tasks and structured workloads.", "F": "Focus on debt management and solid long-term assets.", "M": "Pragmatic, cautious, and resilient.", "R": "Honor commitments faithfully; avoid being overly stern.", "Remedy": "✨ Numerology Remedy (Day 8): Light a sesame oil lamp or chant 'Om Sham Shanayscharaya Namah' for smooth progress."},
    9: {"H": "Martial energy; high stamina—avoid hasty movements.", "C": "Clear backlogs and finalize closing contracts.", "F": "Settle pending bills and clear outstanding dues.", "M": "Passionate, courageous, and ready for completion.", "R": "Practice patience, forgiveness, and let go of past grievances.", "Remedy": "✨ Numerology Remedy (Day 9): Channel high drive into physical exercise or chant 'Om Bhaumaya Namah'."}
}

# Base Navtara Details (including Relationships)
tara_details_en = {
    0: {
        "status": "Janma (1st Tara - Self) ⚪",
        "H": "Focus on self-care and balanced light diet. Body and digestion may feel sensitive today.",
        "C": "Maintain daily routine tasks. Avoid launching major new impulsive projects.",
        "F": "Keep finances stable. Avoid hasty or emotional buying.",
        "M": "Self-reflective, quiet, and calm mindset.",
        "Rel": "Maintain emotional balance in personal relationships; avoid demanding too much from loved ones.",
        "R": ""
    },
    1: {
        "status": "Sampat (2nd Tara - Wealth) 🟢",
        "H": "Energy levels are high. Great day for physical recovery and fitness.",
        "C": "Excellent day for professional growth, key business meetings, and new opportunities.",
        "F": "Highly favorable day for wealth accumulation, investments, and financial gains.",
        "M": "Positive, confident, and optimistic mindset.",
        "Rel": "Wonderful day for bonding, expressing appreciation, and deepening mutual trust in relationships.",
        "R": ""
    },
    2: {
        "status": "Vipat (3rd Tara - Obstacles) 🔴",
        "H": "Vulnerable day physically. Avoid excessive physical strain or high-risk activities.",
        "C": "Sudden hurdles or unexpected delays in projects may arise. Exercise patience.",
        "F": "Strictly avoid speculative investments, trading, or lending money today.",
        "M": "Prone to sudden anxiety, restlessness, or stress.",
        "Rel": "Potential for minor friction or misunderstandings; practice patience and gentle listening.",
        "R": "🛡️ Vedic Remedy (Vipat): Recite or listen to Hanuman Chalisa. Offer fresh water to green plants or birds. Postpone major risky commitments."
    },
    3: {
        "status": "Kshema (4th Tara - Wellbeing) 🟢",
        "H": "Good day for general wellbeing, healing, and physical comfort.",
        "C": "Smooth operations, effective teamwork, and steady ongoing progress.",
        "F": "Financial security and safe transactions are favored.",
        "M": "Peaceful, content, and emotionally balanced.",
        "Rel": "Warm, comforting interactions; excellent time for quality family moments and social harmony.",
        "R": ""
    },
    4: {
        "status": "Pratyari (5th Tara - Opposition) 🔴",
        "H": "Mental friction may manifest as fatigue. Ensure adequate sleep and hydration.",
        "C": "Friction or misunderstandings with colleagues or authority figures are possible.",
        "F": "Unexpected expenses or delayed payments can disrupt your budget.",
        "M": "Easily irritated or defensive. Practice mindfulness.",
        "Rel": "High chance of defensive reactions; practice silence (*Mouna*) during heated moments and give space.",
        "R": "🛡️ Vedic Remedy (Pratyari): Practice silence (Mouna) during arguments. Chant 'Om Sham Shanayscharaya Namah' or donate black sesame/oil."
    },
    5: {
        "status": "Sadhaka (6th Tara - Success) 🟢",
        "H": "Strong vitality and quick overcoming of minor health complaints.",
        "C": "Great achievements, breakthroughs, and successful completion of difficult goals.",
        "F": "Profitable ventures and realization of long-term financial plans.",
        "M": "Determined, highly focused, and intellectually sharp.",
        "Rel": "Achieve strong mutual understanding, resolve past issues, and build meaningful connections.",
        "R": ""
    },
    6: {
        "status": "Vadha (7th Tara - Danger) 🔴",
        "H": "Higher risk of fatigue, minor injury, or illness. Exercise caution while commuting.",
        "C": "Major blockages or opposition. Do not schedule crucial confrontations today.",
        "F": "Protect your assets. Avoid high-stakes financial commitments.",
        "M": "Overwhelmed, fearful, or defensive.",
        "Rel": "Sensitive day for personal ties; avoid major confrontations or bringing up past grievances.",
        "R": "🛡️ Vedic Remedy (Vadha): Chant Mahamrityunjaya Mantra or 'Om Namah Shivaya'. Offer water or milk to Lord Shiva."
    },
    7: {
        "status": "Mitra (8th Tara - Friend) 🟢",
        "H": "Improving health and supportive physical energy.",
        "C": "Expect cooperation from peers and joint success in group tasks.",
        "F": "Collaborative financial gains and steady wealth.",
        "M": "Happy, sociable, and emotionally supported.",
        "Rel": "Very supportive and friendly vibration; great day for social gatherings and romantic warmth.",
        "R": ""
    },
    8: {
        "status": "Ati-Mitra (9th Tara - Best Friend) 🟢🟢",
        "H": "Excellent physical vitality and vibrant energy.",
        "C": "High growth, ultimate success, and public recognition for your efforts.",
        "F": "Windfalls, bonuses, or highly favorable financial news.",
        "M": "Joyous, spiritually uplifted, and deeply fulfilled.",
        "Rel": "Deep emotional joy, heartwarming harmony, and full support from family and partners.",
        "R": ""
    }
}

translations = {
    "en": {
        "intro_title": "Unlocking the Wisdom of Vedic Astrology",
        "intro_desc": "In Vedic astrology and numerology, the Moon's transit through the 27 Nakshatras and daily numerical vibrations create a unique energy pattern relative to your birth profile. This app provides accurate, astronomical, and numerological insights into your health, career, finance, mindset, and relationships.",
        "profile_title": "👤 Birth Profile",
        "horoscope_title": "7-Day Horoscope Prediction & Life Guidance",
        "search_prompt": "🌍 Birth Place Name or 6-Digit Pincode",
        "generate_btn": "Generate Horoscope & Predictions",
        "expander_title": "✨ Click here to see the Prediction & Life Guidance ✨",
        "tara": tara_details_en
    },
    "hi": {
        "intro_title": "वैदिक ज्योतिष और अंकशास्त्र का ज्ञान",
        "intro_desc": "वैदिक ज्योतिष और अंकशास्त्र में, 27 नक्षत्रों में चंद्रमा का गोचर और दैनिक अंक कंपन आपके जन्म विवरण के सापेक्ष एक अनूठा ऊर्जा पैटर्न बनाते हैं। यह ऐप स्वास्थ्य, करियर, वित्त, मानसिकता और संबंधों में सटीक अंतर्दृष्टि प्रदान करता है।",
        "profile_title": "👤 जन्म विवरण",
        "horoscope_title": "7-दिवसीय राशिफल भविष्यवाणी और जीवन मार्गदर्शन",
        "search_prompt": "🌍 जन्म स्थान का नाम या 6-अंकीय पिनकोड",
        "generate_btn": "राशिफल और भविष्यवाणियां उत्पन्न करें",
        "expander_title": "✨ दैनिक भविष्यवाणी और जीवन मार्गदर्शन देखने के लिए यहां क्लिक करें ✨",
        "tara": tara_details_en 
    }
}
translations["mr"] = translations["hi"]
translations["gu"] = translations["hi"]

def reduce_to_single_digit(n: int) -> int:
    """Reduce any number to a single digit 1-9."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

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
    """Automatically determine UTC offset in hours based on place data."""
    if isinstance(place_obj, dict):
        addr = place_obj.get('address', {})
        country_code = addr.get('country_code', '').lower()
        if country_code == 'in':
            return 5.5
        lon = float(place_obj.get('lon', 0))
        if lon != 0:
            return round(lon / 15.0 * 2) / 2
    return 5.5

def get_moon_nakshatra_index(dt_utc):
    """Calculates exact Sidereal Moon Nakshatra index (0 to 26) using PyEphem + Lahiri Ayanamsa."""
    observer = ephem.Observer()
    observer.date = ephem.date(dt_utc)
    moon = ephem.Moon(observer)
    ecl = ephem.Ecliptic(moon)
    
    year = dt_utc.year + (dt_utc.month - 1) / 12.0
    ayanamsa = 23.85306 + (year - 2000.0) * 0.01397
    
    sidereal_lon = (math.degrees(ecl.lon) - ayanamsa) % 360
    nakshatra_index = int(sidereal_lon / 13.333333333333334) % 27
    return nakshatra_index

def calculate_7_day_transits(now_utc, utc_offset_hours, days=7):
    """
    Computes current and future transits anchored strictly to UTC time.
    Discards any past transit whose end time is before current local time.
    """
    now_local = now_utc + datetime.timedelta(hours=utc_offset_hours)
    current_nak = get_moon_nakshatra_index(now_utc)
    
    start_search_utc = now_utc
    for i in range(1, 200):
        test_utc = now_utc - datetime.timedelta(minutes=15 * i)
        if get_moon_nakshatra_index(test_utc) != current_nak:
            start_search_utc = test_utc + datetime.timedelta(minutes=15)
            break
            
    window_start_local = start_search_utc + datetime.timedelta(hours=utc_offset_hours)
    
    transits = []
    curr_nak = current_nak
    scan_limit_utc = now_utc + datetime.timedelta(days=days)
    
    total_steps = int((days + 3) * 24 * 4)
    for i in range(1, total_steps):
        test_utc = start_search_utc + datetime.timedelta(minutes=15 * i)
        test_nak = get_moon_nakshatra_index(test_utc)
        
        if test_nak != curr_nak:
            test_local = test_utc + datetime.timedelta(hours=utc_offset_hours)
            
            if test_local > now_local:
                transits.append({
                    "start": window_start_local,
                    "end": test_local,
                    "nak_index": curr_nak,
                    "is_current": (window_start_local <= now_local < test_local)
                })
            curr_nak = test_nak
            window_start_local = test_local
            
            if test_utc >= scan_limit_utc:
                break
                
    return transits

query_params = st.query_params
if 'profile_saved' not in st.session_state:
    st.session_state['profile_saved'] = 'saved' in query_params

st.title("🌙 Navtara Pulse")

lang_options = {"en": "English", "hi": "हिन्दी (Hindi)", "mr": "मराठी (Marathi)", "gu": "ગુજરાતી (Gujarati)"}
selected_lang_name = st.selectbox("🌐 Select Language", list(lang_options.values()), index=0)
lang_code = [k for k, v in lang_options.items() if v == selected_lang_name][0]
t = translations[lang_code]

st.markdown(f"### {t['intro_title']}")
st.write(t['intro_desc'])
st.divider()

st.header(t['profile_title'])

default_name = query_params.get('n', '')
default_date = datetime.datetime.strptime(query_params.get('d', '1995-01-01'), '%Y-%m-%d').date()
default_h = int(query_params.get('h', '0'))
default_m = int(query_params.get('m', '0'))
default_place = query_params.get('p', '')

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

# Auto-calculate UTC offset in background
utc_offset_val = get_utc_offset_hours(place_obj_data, place_query)

# Auto-calculate default Janma Nakshatra based on Date/Time
birth_local_dt = datetime.datetime.combine(birth_date, datetime.time(int(birth_hour), int(birth_minute)))
birth_utc_dt = birth_local_dt - datetime.timedelta(hours=utc_offset_val)
auto_janma_idx = get_moon_nakshatra_index(birth_utc_dt)

st.write("✨ **Janma Nakshatra (Birth Star)**")
selected_janma_nakshatra = st.selectbox(
    "Verify/Select your exact Kundli Birth Star:",
    nakshatra_list,
    index=auto_janma_idx,
    help="Auto-calculated based on birth date/time. You can adjust this if your Kundli mentions a specific star."
)

if selected_place_display:
    st.markdown(f"<div class='verified-badge'>📍 Birth Place: {selected_place_display}</div>", unsafe_allow_html=True)

if st.button(f"🔮 {t['generate_btn']}", type="primary", use_container_width=True):
    if len(place_query) < 3:
        st.error("⚠️ Please enter a valid Birth Place or Pincode to generate your predictions.")
    else:
        st.query_params['n'] = user_name
        st.query_params['d'] = str(birth_date)
        st.query_params['h'] = str(int(birth_hour))
        st.query_params['m'] = str(int(birth_minute))
        st.query_params['p'] = selected_place_display
        st.query_params['saved'] = 'true'
        st.session_state['profile_saved'] = True

if st.session_state.get('profile_saved'):
    st.divider()
    
    # 1. Vedic Nakshatra Details
    janma_index = nakshatra_list.index(selected_janma_nakshatra)
    janma_lord = nakshatra_lords[janma_index]
    
    # 2. Vedic Numerology Profile Calculation
    moolank = reduce_to_single_digit(birth_date.day)
    bhagyank = reduce_to_single_digit(birth_date.day + birth_date.month + birth_date.year)
    moolank_lord = num_lords.get(moolank, "")
    bhagyank_lord = num_lords.get(bhagyank, "")
    lucky_nums = lucky_numbers_map.get(moolank, "1, 3, 5, 6")
    
    st.success(f"🌟 **{user_name or 'User'}'s Janma Nakshatra:** {selected_janma_nakshatra} | **Nakshatra Lord:** {janma_lord}")
    
    # Numerology Summary Pill
    st.markdown(f"""
    <div style="background-color: #f1f5f9; color: #1e293b; padding: 12px 16px; border-radius: 10px; margin-top: -6px; margin-bottom: 16px; border: 1px solid #cbd5e1; font-size: 0.93rem;">
        🔢 <b>Numerology Profile:</b> Moolank (Driver): <b>{moolank} ({moolank_lord})</b> &nbsp;|&nbsp; Bhagyank (Conductor): <b>{bhagyank} ({bhagyank_lord})</b> &nbsp;|&nbsp; Lucky Numbers: <b>{lucky_nums}</b>
    </div>
    """, unsafe_allow_html=True)
    
    # Save & Install Mobile Instructions Banner
    st.markdown("""
    <div style="background-color: #1e1b4b; color: #ffffff; padding: 16px; border-radius: 12px; margin-top: 10px; margin-bottom: 20px;">
        <h5 style="color: #fbbf24; margin-top: 0; font-size: 1.05rem; font-weight: bold;">📱 Save & Install for 1-Click Mobile Access</h5>
        <p style="font-size: 0.9rem; color: #e2e8f0; margin-bottom: 8px;">
            Your birth profile details have been saved to this custom URL. To open this horoscope anytime without re-entering details:
        </p>
        <ul style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 0; padding-left: 20px;">
            <li><b>iPhone (Safari):</b> Tap the <b>Share</b> icon at the bottom ➔ select <b>"Add to Home Screen"</b>.</li>
            <li><b>Android (Chrome):</b> Tap the <b>three dots (⋮)</b> at top-right ➔ select <b>"Add to Home screen"</b> or <b>"Install App"</b>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.header(t['horoscope_title'])
    
    now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    transits = calculate_7_day_transits(now_utc, utc_offset_val)
    
    for transit in transits:
        nak_difference = (transit["nak_index"] - janma_index) % 27
        tara_index = nak_difference % 9
        
        tara_data = t["tara"][tara_index]
        tara_badge_name = navtara_names[tara_index]
        transit_nak_name = nakshatra_list[transit["nak_index"]]
        transit_nak_lord = nakshatra_lords[transit["nak_index"]]
        
        start_str = transit["start"].strftime('%a, %d %b %I:%M %p')
        end_str = transit["end"].strftime('%a, %d %b %I:%M %p')
        
        current_pill = "<span class='current-badge'>⚡ Active Now</span>" if transit.get("is_current") else ""
        
        # Calculate Daily Personal Day Number for the transit date
        t_date = transit["start"].date()
        p_day = reduce_to_single_digit(birth_date.day + birth_date.month + t_date.day + t_date.month + t_date.year)
        p_lord = num_lords.get(p_day, "")
        p_desc = (personal_day_meanings_hi if lang_code in ["hi", "mr", "gu"] else personal_day_meanings_en).get(p_day, "")
        num_aspects = personal_day_aspects_en.get(p_day, {})
        
        # Upper Portion: Moon Transit Metadata & Shifted Main-Card Numerology Section
        st.markdown(f"""
        <div class="transit-card">
            <h5><span>🕒 {start_str} ➔ {end_str}</span> {current_pill}</h5>
            <p><b>Status:</b> <span class='status-badge'>{tara_badge_name}</span></p>
            <p><b>Moon Nakshatra:</b> {transit_nak_name} (<b>Nakshatra Lord:</b> {transit_nak_lord})</p>
            <p style="margin-top: 6px; padding-top: 6px; border-top: 1px dashed #bae6fd;">
                🔢 <b>Numerology Vibration:</b> Personal Day <b>{p_day} ({p_lord})</b> — {p_desc}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Attached Lower Portion: Expanded Guidance with Health, Career, Finance, Mindset & Relationships
        with st.expander(t["expander_title"]):
            st.write(f"🩺 **Health:** {tara_data['H']} *(Numerology Focus: {num_aspects.get('H', '')})*")
            st.write(f"💼 **Career:** {tara_data['C']} *(Numerology Focus: {num_aspects.get('C', '')})*")
            st.write(f"💰 **Finance:** {tara_data['F']} *(Numerology Focus: {num_aspects.get('F', '')})*")
            st.write(f"🧘 **Mindset:** {tara_data['M']} *(Numerology Focus: {num_aspects.get('M', '')})*")
            st.write(f"❤️ **Relationships:** {tara_data.get('Rel', '')} *(Numerology Focus: {num_aspects.get('R', '')})*")
            
            # Show Navtara and/or Numerology Remedies if applicable
            if tara_data['R']:
                st.error(tara_data['R'])
            if num_aspects.get("Remedy", ""):
                st.info(num_aspects["Remedy"])

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
