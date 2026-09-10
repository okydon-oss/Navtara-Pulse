import streamlit as st
import datetime
import urllib.parse
import json
import os
import math

try:
    import swisseph as swe
    HAS_SWISSEPH = True
    swe.set_sid_mode(swe.SIDM_LAHIRI)
except Exception:
    HAS_SWISSEPH = False

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
    html {
        font-size: 16px;
    }
    @media (max-width: 640px) {
        html {
            font-size: 15.5px;
        }
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
        padding: 1rem 1.1rem;
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

# ==============================================================================
# GEODETIC ATLAS (CITY COORDINATE LOOKUP)
# ==============================================================================
CITY_COORDINATES = {
    "Delhi / New Delhi, India": (28.6139, 77.2090),
    "Mumbai, Maharashtra, India": (19.0760, 72.8777),
    "Chhatrapati Sambhajinagar (Aurangabad), Maharashtra, India": (19.8762, 75.3433),
    "Pune, Maharashtra, India": (18.5204, 73.8567),
    "Nagpur, Maharashtra, India": (21.1458, 79.0882),
    "Bengaluru, Karnataka, India": (12.9716, 77.5946),
    "Hyderabad, Telangana, India": (17.3850, 78.4867),
    "Chennai, Tamil Nadu, India": (13.0827, 80.2707),
    "Kolkata, West Bengal, India": (22.5726, 88.3639),
    "Ahmedabad, Gujarat, India": (23.0225, 72.5714),
    "Surat, Gujarat, India": (21.1702, 72.8311),
    "Jaipur, Rajasthan, India": (26.9124, 75.7873),
    "Lucknow, Uttar Pradesh, India": (26.8467, 80.9462),
    "Varanasi, Uttar Pradesh, India": (25.3176, 82.9739),
    "Patna, Bihar, India": (25.5941, 85.1376),
    "Bhopal, Madhya Pradesh, India": (23.2599, 77.4126),
    "Indore, Madhya Pradesh, India": (22.7196, 75.8577),
    "Chandigarh, India": (30.7333, 76.7794),
    "Dubai, UAE": (25.2048, 55.2708),
    "London, UK": (51.5074, -0.1278),
    "New York, USA": (40.7128, -74.0060),
    "San Francisco, USA": (37.7749, -122.4194),
    "Singapore": (1.3521, 103.8198),
    "Toronto, Canada": (43.6532, -79.3832)
}

def resolve_city_coordinates(city_name: str, fallback_lat: float = 28.6139, fallback_lon: float = 77.2090):
    c_clean = city_name.strip().lower()
    for name, coords in CITY_COORDINATES.items():
        if c_clean in name.lower() or any(part in name.lower() for part in c_clean.split(',')):
            return coords[0], coords[1]
    return fallback_lat, fallback_lon

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]
NAKHATRAS = NAKSHATRAS

RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

NAVTARA_NAMES = [
    ("Janma (Birth/Identity)", "🌱", "Sensitive & Foundational"),
    ("Sampat (Wealth/Gain)", "🟢", "Highly Auspicious & Material Abundance"),
    ("Vipat (Adversity/Friction)", "🔴", "Caution & Resistance"),
    ("Kshema (Well-being/Comfort)", "🟢", "Peace, Protection & Sustenance"),
    ("Pratyari (Obstacles/Delays)", "🔴", "High Resistance & Delays"),
    ("Sadhana (Accomplishment)", "🟢", "Success, Discipline & Mastery"),
    ("Vadha (Destruction/Loss)", "🔴", "Heavy Friction & Caution"),
    ("Mitra (Friendship/Allies)", "🟢", "Cordiality & Cooperative Harmony"),
    ("Ati-Mitra (Supreme Alliance)", "🟢", "Supreme Synergy & Deep Expansion")
]

SHANI_VAHANS = {
    1: {"name": "Gaja (Elephant / हस्ती)", "type": "Highly Auspicious (अति शुभ)", "speed": "Dignified & Steady", "desc": "Guaranteed wealth expansion, societal respect, sound health, and enduring peace."},
    2: {"name": "Ashwa (Horse / अश्व)", "type": "Progressive & Dynamic (शुभ)", "speed": "Rapid & Victorious", "desc": "Brisk progress, victory in competitive undertakings, and sudden career momentum."},
    3: {"name": "Simha (Lion / सिंह)", "type": "Victorious & Authoritative (शुभ)", "speed": "Commanding & Decisive", "desc": "Dominance over competitors, professional promotion, and clear leadership recognition."},
    4: {"name": "Gardabha (Donkey / गर्दभ)", "type": "Demanding & Heavy (कठिन)", "speed": "Slow & Laborious", "desc": "Heavy labor, delayed recognition, and testing of patient endurance."},
    5: {"name": "Kukkuta (Rooster / कुक्कुट)", "type": "Restless & Mixed (मिश्रित)", "speed": "Impulsive & Alert", "desc": "Sudden squabbles, mental restlessness, and unnecessary emotional volatility."},
    6: {"name": "Shvana (Dog / श्वान)", "type": "Vigilant & Challenging (संघर्षमय)", "speed": "Guarded & Suspicious", "desc": "Heightened anxiety, false accusations, and risk of misunderstandings."},
    7: {"name": "Jambuka (Jackal / जम्बुक)", "type": "Difficult & Testing (कठिन)", "speed": "Hesitant & Cautious", "desc": "Unexpected financial leaks, health dips, and domestic disharmony."},
    8: {"name": "Kaka (Crow / काक)", "type": "High Friction (अशुभ)", "speed": "Disruptive & Harsh", "desc": "Mental distress, family strife, and high risk of wasted expenditure."},
    9: {"name": "Mayura (Peacock / मयूर)", "type": "Auspicious & Graceful (शुभ)", "speed": "Harmonious & Joyful", "desc": "Artistic success, mental serenity, sudden fortune, and creative joy."}
}

CHALDEAN_MAP = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

NUM_PLANET_NAMES = {
    1: {"en": "Sun (Surya / सूर्य)", "hi": "सूर्य (Sun)", "mr": "सूर्य (Sun)", "gu": "સૂર્ય (Sun)"},
    2: {"en": "Moon (Chandra / चन्द्र)", "hi": "चन्द्र (Moon)", "mr": "चंद्र (Moon)", "gu": "ચંદ્ર (Moon)"},
    3: {"en": "Jupiter (Brihaspati / गुरु)", "hi": "गुरु (Jupiter)", "mr": "गुरू (Jupiter)", "gu": "ગુરુ (Jupiter)"},
    4: {"en": "Rahu (North Node / राहु)", "hi": "राहु (Rahu)", "mr": "राहू (Rahu)", "gu": "રાહુ (Rahu)"},
    5: {"en": "Mercury (Budha / बुध)", "hi": "बुध (Mercury)", "mr": "बुध (Mercury)", "gu": "બુધ (Mercury)"},
    6: {"en": "Venus (Shukra / शुक्र)", "hi": "शुक्र (Venus)", "mr": "शुक्र (Venus)", "gu": "શુક્ર (Venus)"},
    7: {"en": "Ketu (South Node / केतु)", "hi": "केतु (Ketu)", "mr": "કેતુ (Ketu)", "gu": "કેતુ (Ketu)"},
    8: {"en": "Saturn (Shani / शनि)", "hi": "शनि (Saturn)", "mr": "शनी (Saturn)", "gu": "શનિ (Saturn)"},
    9: {"en": "Mars (Mangal / मंगल)", "hi": "मंगल (Mars)", "mr": "મંગળ (Mars)", "gu": "મંગળ (Mars)"}
}

TRANSLATIONS = {
    "en": {
        "app_title": "✨ Navtara Pulse",
        "app_subtitle": "Vedic Nakshatra Rhythm & Cosmic Precision",
        "btn_about": "✨ About App",
        "btn_user_profile": "👤 User Profile",
        "btn_numerology": "🔢 Numerology",
        "btn_shani": "🪐 Shani",
        "btn_live": "⚡ Live Prediction",
        "btn_forecast": "🗓️ 7 Days Prediction",
        "btn_share": "📲 Share App",
        "edit_details": "✏️ Edit Details",
        "save_details": "💾 Save Profile",
        "cancel": "Cancel",
        "name_label": "Full Name",
        "dob_label": "Birth Date",
        "tob_label": "Birth Time",
        "city_label": "Birth Location / City",
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
        "btn_shani": "🪐 शनि पाया",
        "btn_live": "⚡ आज का फल",
        "btn_forecast": "🗓️ 7 दिवसीय फल",
        "btn_share": "📲 शेयर करें",
        "edit_details": "✏️ विवरण बदलें",
        "save_details": "💾 सुरक्षित करें",
        "cancel": "रद्द करें",
        "name_label": "पूरा नाम",
        "dob_label": "जन्म तिथि",
        "tob_label": "जन्म समय",
        "city_label": "जन्म स्थान",
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
    },
    "mr": {
        "app_title": "✨ नवतारा पल्स (Navtara Pulse)",
        "app_subtitle": "वैदिक नक्षत्र गोचर आणि वैश्विक ऊर्जा चक्र",
        "btn_about": "✨ ॲप विषयी",
        "btn_user_profile": "👤 युझर प्रोफाईल",
        "btn_numerology": "🔢 अंकशास्त्र",
        "btn_shani": "🪐 शनी पाया",
        "btn_live": "⚡ आजचे भविष्य",
        "btn_forecast": "🗓️ ७ दिवसांचे भविष्य",
        "btn_share": "📲 शेअर करा",
        "edit_details": "✏️ माहिती बदला",
        "save_details": "💾 सेव्ह करा",
        "cancel": "रद्द करा",
        "name_label": "पूर्ण नाव",
        "dob_label": "जन्म तारीख",
        "tob_label": "जन्म वेळ",
        "city_label": "जन्म ठिकाण",
        "nakshatra_label": "जन्म नक्षत्र",
        "pada_label": "चरण",
        "moon_rashi_label": "चंद्र रास",
        "lagna_label": "लग्न रास",
        "mulank_label": "मूलांक",
        "bhagyank_label": "भाग्यांक",
        "namank_label": "नामांक",
        "shani_paya_title": "🪐 चालू शनी पाया व २.५ वर्षांचे गोचर",
        "sadesati_title": "⚖️ शनी साडेसाती व ढिय्या स्थिती",
        "live_pulse_title": "⚡ आजचा थेट खगोलीय प्रभाव",
        "forecast_title": "🗓️ पुढील ७ दिवसांचे नक्षत्र संक्रमण व दैनिक मार्गदर्शन",
        "share_title": "📲 नवतारा पल्स ॲप मित्र आणि कुटुंबासह शेअर करा"
    },
    "gu": {
        "app_title": "✨ નવતારા પલ્સ (Navtara Pulse)",
        "app_subtitle": "વૈદિક નક્ષત્ર ગોચર અને બ્રહ્માંડીય ઊર્જા ચક્ર",
        "btn_about": "✨ એપ વિશે",
        "btn_user_profile": "👤 યુઝર પ્રોફાઇલ",
        "btn_numerology": "🔢 અંકશાસ્ત્ર",
        "btn_shani": "🪐 શનિ પાયા",
        "btn_live": "⚡ આજનું ફળ",
        "btn_forecast": "🗓️ ૭ દિવસનું ફળ",
        "btn_share": "📲 શેર કરો",
        "edit_details": "✏️ વિગત બદલો",
        "save_details": "💾 સેવ કરો",
        "cancel": "રદ કરો",
        "name_label": "પૂરું નામ",
        "dob_label": "જન્મ તારીખ",
        "tob_label": "જન્મ સમય",
        "city_label": "જન્મ સ્થળ",
        "nakshatra_label": "જન્મ નક્ષત્ર",
        "pada_label": "ચરણ",
        "moon_rashi_label": "ચંદ્ર રાશિ",
        "lagna_label": "લગ્ન રાશિ",
        "mulank_label": "મૂળાંક",
        "bhagyank_label": "ભાગ્યાંક",
        "namank_label": "નામાંક",
        "shani_paya_title": "🪐 વર્તમાન શનિ પાયા અને ૨.૫ વર્ષનું ગોચર",
        "sadesati_title": "⚖️ શનિ સાડાસાતી અને ઢૈય્યા સ્થિતિ",
        "live_pulse_title": "⚡ આજનો જીવંત નક્ષત્ર પ્રભાવ",
        "forecast_title": "🗓️ આગામી ૭ દિવસોનું નક્ષત્ર ગોચર અને દૈનિક માર્ગદર્શન",
        "share_title": "📲 નવતારા પલ્સ તમારા મિત્રો અને પરિવાર સાથે શેર કરો"
    }
}

def t(key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))

NAKSHATRA_BIO_DATA = {
    1: {"deity": "Ashwini Kumaras (Celestial Healers)", "symbol": "Horse's Head", "tree": "Kuchila / Strychnine (विषमुष्टी)", "bird": "Shikra / Wild Hawk", "animal": "Horse (Ashwa / अश्व)", "lord": "Ketu"},
    2: {"deity": "Lord Yama (Dharma & Cosmic Justice)", "symbol": "Yoni / Creative Triangle", "tree": "Amla / Indian Gooseberry (धात्री)", "bird": "Crow (काक)", "animal": "Elephant (Gaja / गज)", "lord": "Venus (Shukra)"},
    3: {"deity": "Agni (God of Fire & Transformation)", "symbol": "Razor / Flame / Knife", "tree": "Gular / Cluster Fig (उदुम्बर)", "bird": "Peacock (मयूर)", "animal": "Sheep / Ram (मेष)", "lord": "Sun (Surya)"},
    4: {"deity": "Prajapati / Lord Brahma (Creator)", "symbol": "Chariot / Cart / Temple", "tree": "Jamun / Black Plum (जम्बू)", "bird": "Owl (उलूक)", "animal": "Serpent (Sarpa / सर्प)", "lord": "Moon (Chandra)"},
    5: {"deity": "Soma (God of Nectar & Vitality)", "symbol": "Deer's Head", "tree": "Khair / Acacia Catechu (खदिर)", "bird": "Batar / Francolin", "animal": "Serpent (Sarpa / सर्प)", "lord": "Mars (Mangal)"},
    6: {"deity": "Rudra (Storm & Destructive Transformation)", "symbol": "Teardrop / Diamond / Jewel", "tree": "Agarwood / Krishna Agaru (अगरु)", "bird": "Andal / Red-wattled Lapwing", "animal": "Dog (Shwana / श्वान)", "lord": "Rahu"},
    7: {"deity": "Aditi (Cosmic Mother of Gods)", "symbol": "Bow and Quiver of Arrows", "tree": "Vamsha / Sacred Bamboo (वंश)", "bird": "Swan (Hamsa / हंस)", "animal": "Cat (Marjara / मार्जार)", "lord": "Jupiter (Guru)"},
    8: {"deity": "Brihaspati (Guru of the Devatas)", "symbol": "Cow's Udder / Lotus / Wheel", "tree": "Peepal / Sacred Fig (अश्वत्थ)", "bird": "Sea Crow / जलकाक", "animal": "Goat / Sheep (Aja / अज)", "lord": "Saturn (Shani)"},
    9: {"deity": "Nagas (Divine Serpent Guardians)", "symbol": "Coiled Serpent", "tree": "Nagkeshar / Ashoka (नागकेशर)", "bird": "Small Owl (उलूक)", "animal": "Cat (Marjara / मार्जार)", "lord": "Mercury (Budha)"},
    10: {"deity": "Pitris (Sacred Ancestors & Lineage)", "symbol": "Royal Throne / Palanquin", "tree": "Banyan / Bargad (वटवृक्ष)", "bird": "Male Eagle (चील)", "animal": "Rat (Mushaka / मूषक)", "lord": "Ketu"},
    11: {"deity": "Bhaga (God of Fortune & Prosperity)", "symbol": "Front Legs of Couch / Hammock", "tree": "Palasa / Flame of Forest (पलाश)", "bird": "Falcon (शिशुक)", "animal": "Female Rat (मूषक)", "lord": "Venus (Shukra)"},
    12: {"deity": "Aryaman (God of Honor, Vows & Truth)", "symbol": "Back Legs of Couch / Bed", "tree": "Plaksha / Rudraksha (प्लक्ष)", "bird": "Beetle / Crow", "animal": "Bull / Cow (वृषभ)", "lord": "Sun (Surya)"},
    13: {"deity": "Savitur (Solar Awakening & Energy)", "symbol": "Open Hand / Palm Blessing", "tree": "Chameli / Wild Jasmine (चमेली)", "bird": "Vulture / Hawk", "animal": "Female Buffalo (महिषी)", "lord": "Moon (Chandra)"},
    14: {"deity": "Vishwakarma (Divine Cosmic Architect)", "symbol": "Bright Pearl / Polished Gem", "tree": "Bilva / Bael Patra (बिल्व)", "bird": "Woodpecker (काष्ठकूट)", "animal": "Female Tiger (व्याघ्र)", "lord": "Mars (Mangal)"},
    15: {"deity": "Vayu (God of Cosmic Wind & Breath)", "symbol": "Young Sprout swaying in Wind / Coral", "tree": "Arjuna (अर्जुन वृक्ष)", "bird": "Pigeon / Sparrow (कपोत)", "animal": "Male Buffalo (महिष)", "lord": "Rahu"},
    16: {"deity": "Indragni (Alliance of Power & Fire)", "symbol": "Triumphal Arch / Potter's Wheel", "tree": "Wood Apple / Kaith (कपित्थ)", "bird": "Red Falcon (श्येन)", "animal": "Male Tiger (व्याघ्र)", "lord": "Jupiter (Guru)"},
    17: {"deity": "Mitra (God of Friendship & Devotion)", "symbol": "Staff / Lotus / Arc of Victory", "tree": "Bakula / Maulsari (बकुल)", "bird": "Nightingale / Peacock", "animal": "Female Deer (मृग)", "lord": "Saturn (Shani)"},
    18: {"deity": "Indra (Supreme King of Heaven)", "symbol": "Round Talisman / Royal Umbrella", "tree": "Semal / Silk Cotton (शाल्मली)", "bird": "Brahminy Kite (गरुड)", "animal": "Male Deer (मृग)", "lord": "Mercury (Budha)"},
    19: {"deity": "Nirriti (Goddess of Root Realities)", "symbol": "Tied Bundle of Roots / Elephant Goad", "tree": "Sal / Sarjaka (शाल वृक्ष)", "bird": "Red Vulture (गीध)", "animal": "Male Dog (श्वान)", "lord": "Ketu"},
    20: {"deity": "Apah (Divine Waters of Invincibility)", "symbol": "Winnowing Basket / Fan", "tree": "Ashoka / Rattan (अशोक)", "bird": "Francolin / Hawk", "animal": "Male Monkey (वानर)", "lord": "Venus (Shukra)"},
    21: {"deity": "Vishwadevas (Universal Cosmic Laws)", "symbol": "Elephant's Tusk / Small Cot", "tree": "Jackfruit / Phanas (पनस)", "bird": "Stork / सारस", "animal": "Male Mongoose (नकुल)", "lord": "Sun (Surya)"},
    22: {"deity": "Lord Vishnu (Cosmic Preserver)", "symbol": "Three Footprints / Ear of Listening", "tree": "Aak / Rui / Calotropis (मदार)", "bird": "Francolin / Kapinjala", "animal": "Female Monkey (वानर)", "lord": "Moon (Chandra)"},
    23: {"deity": "Eight Vasus (Elemental Energy Lords)", "symbol": "Mridangam / Drum / Flute", "tree": "Shami / Khejri (शमी वृक्ष)", "bird": "Golden Bee / Peacock", "animal": "Female Lion (सिंह)", "lord": "Mars (Mangal)"},
    24: {"deity": "Varuna (God of Cosmic Oceans & Truth)", "symbol": "Hundred Healers / Empty Circle", "tree": "Kadamba (कदम्ब)", "bird": "Raven / Koel (काक)", "animal": "Female Horse (अश्व)", "lord": "Rahu"},
    25: {"deity": "Aja Ekapada (One-Footed Cosmic Fire)", "symbol": "Two Front Legs of Bed / Crossed Swords", "tree": "Mango / Neem (आम्र/निम्ब)", "bird": "Avocet / Peacock", "animal": "Male Lion (सिंह)", "lord": "Jupiter (Guru)"},
    26: {"deity": "Ahirbudhnya (Serpent of Deep Depths)", "symbol": "Two Back Legs of Bed / Serpent in Water", "tree": "Neem / Pithari (निम्ब)", "bird": "Kotwal / Rainbird", "animal": "Female Cow (गौ)", "lord": "Saturn (Shani)"},
    27: {"deity": "Pushan (Nourisher of Safe Journeys)", "symbol": "Pair of Fish / Small Drum", "tree": "Mahua (मधूक)", "bird": "Demoiselle Crane / Sparrow", "animal": "Female Elephant (हस्तिनी)", "lord": "Mercury (Budha)"}
}

def get_nakshatra_traits(star_idx: int, lang: str = "en") -> dict:
    bio = NAKSHATRA_BIO_DATA.get(star_idx, NAKSHATRA_BIO_DATA[2])
    star_name = NAKSHATRAS[star_idx - 1]
    
    pers_en = f"Born under {star_name}, governed by {bio['deity']} and planetary lord {bio['lord']}, you inherit acute intuitive foresight, exceptional endurance, and principled leadership."
    pred_en = f"Your evolutionary trajectory moves through cyclical refinement into established institutional authority and enduring financial stability."
    rem_en = f"• Recite the Beej Mantra of {bio['deity']} 11 times every morning.\n• Water and nurture your sacred tree ({bio['tree']}).\n• Practice daily gratitude and feed wild birds ({bio['bird']}) to balance karmic weight."

    return {
        "deity": bio["deity"],
        "symbol": bio["symbol"],
        "tree": bio["tree"],
        "bird": bio["bird"],
        "animal": bio["animal"],
        "lord": bio["lord"],
        "personality": pers_en,
        "prediction": pred_en,
        "remedies": rem_en
    }

def get_moon_rashi_details(rashi_idx: int, lang: str = "en") -> dict:
    r_name = RASHIS[rashi_idx]
    lords = ["Mars (Mangal)", "Venus (Shukra)", "Mercury (Budha)", "Moon (Chandra)",
             "Sun (Surya)", "Mercury (Budha)", "Venus (Shukra)", "Mars (Mangal)",
             "Jupiter (Guru)", "Saturn (Shani)", "Saturn (Shani)", "Jupiter (Guru)"]
    elements = ["Fire (Agni)", "Earth (Prithvi)", "Air (Vayu)", "Water (Jala)",
                "Fire (Agni)", "Earth (Prithvi)", "Air (Vayu)", "Water (Jala)",
                "Fire (Agni)", "Earth (Prithvi)", "Air (Vayu)", "Water (Jala)"]
    
    r_lord = lords[rashi_idx]
    r_elem = elements[rashi_idx]
    
    prof_en = f"With Moon in {r_name}, your mind operates through the {r_elem} tattva under {r_lord}. You possess sharp emotional stamina and deep focus."
    pred_en = f"Chandra in {r_lord}'s domain bestows strategic patience, executive resourcefulness, and capacity to turn challenges into lasting assets."
    rem_en = f"• Offer clean water or milk to a Shiva Lingam on Mondays.\n• Respect mother figures and drink water from a pure silver cup.\n• Meditate for 10 minutes at twilight to ground lunar tides."

    return {
        "name": r_name,
        "element": r_elem,
        "ruler": r_lord,
        "profile": prof_en,
        "prediction": pred_en,
        "remedies": rem_en
    }

def get_lagna_details(lagna_idx: int, lang: str = "en") -> dict:
    l_name = RASHIS[lagna_idx]
    lords = ["Mars (Mangal)", "Venus (Shukra)", "Mercury (Budha)", "Moon (Chandra)",
             "Sun (Surya)", "Mercury (Budha)", "Venus (Shukra)", "Mars (Mangal)",
             "Jupiter (Guru)", "Saturn (Shani)", "Saturn (Shani)", "Jupiter (Guru)"]
    elements = ["Fire (Agni)", "Earth (Prithvi)", "Air (Vayu)", "Water (Jala)",
                "Fire (Agni)", "Earth (Prithvi)", "Air (Vayu)", "Water (Jala)",
                "Fire (Agni)", "Earth (Prithvi)", "Air (Vayu)", "Water (Jala)"]
    
    l_lord = lords[lagna_idx]
    l_elem = elements[lagna_idx]
    
    prof_en = f"Your Ascendant (Lagna) is {l_name}, rooted in {l_elem} tattva under the sovereign lordship of {l_lord}. Your outward demeanor radiates poise, diplomacy, and balanced presence."
    pred_en = f"With {l_lord} presiding over your first house of vitality, your life trajectory aligns with professional distinction, institutional trust, and compounding respect."
    rem_en = f"• Apply pure white sandalwood paste or natural attar to pulse points.\n• Practice morning Pranayama to align physical breath with mental vitality.\n• Strengthen Lagna lord through disciplined daily routines and ethical integrity."

    return {
        "name": l_name,
        "element": l_elem,
        "lord": l_lord,
        "profile": prof_en,
        "prediction": pred_en,
        "remedies": rem_en
    }

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

def calculate_shani_paya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    house_diff = (moon_rashi_idx - saturn_transit_rashi_idx) % 12 + 1
    if house_diff in [2, 5, 9]:
        return {
            "paya": "🥈 Rajat Paya (Silver Feet / चाँदी का पाया)",
            "metal": "Silver",
            "status": "Highly Auspicious (अति शुभ)",
            "desc": "Saturn arrives bearing silver gifts. Bestows financial liquidity, career elevation, and divine protection during Sade Sati.",
            "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces)"
        }
    elif house_diff in [3, 7, 10]:
        return {
            "paya": "🥉 Tamra Paya (Copper Feet / तांबे का पाया)",
            "metal": "Copper",
            "status": "Favorable (शुभ)",
            "desc": "Brings steady professional growth, success through patient labor, and balanced family relationships.",
            "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces)"
        }
    elif house_diff in [1, 6, 11]:
        return {
            "paya": "🥇 Swarna Paya (Gold Feet / सोने का पाया)",
            "metal": "Gold",
            "status": "Testing & Demanding (कठिन)",
            "desc": "Tests character through ego challenges, high expenditures, and health concerns. Requires humility and charity.",
            "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces)"
        }
    else:
        return {
            "paya": "🪙 Loha Paya (Iron Feet / लोहे का पाया)",
            "metal": "Iron",
            "status": "Difficult / High Friction (संघर्षमय)",
            "desc": "Indicates delays, mental fatigue, and heavy responsibilities. Requires patient endurance and regular Hanuman Chalisa chanting.",
            "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces)"
        }

def calculate_shani_sadesati_dhaiya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    diff = (saturn_transit_rashi_idx - moon_rashi_idx) % 12
    if diff == 11:
        return {
            "active": True,
            "type": "Sade Sati Phase 1 (Rising Phase / 12th House Transit)",
            "impact": "Saturn transits the 12th house from your Moon. Focus on strategic budgeting, foreign avenues, spiritual grounding, and avoiding mental overthinking.",
            "dates": "29 March 2025 – 23 February 2028"
        }
    elif diff == 0:
        return {
            "active": True,
            "type": "Sade Sati Phase 2 (Peak Phase / 1st House Janma Transit)",
            "impact": "Saturn transits your natal Moon. Deep personal restructuring, high responsibilities, and major life decisions.",
            "dates": "February 2028 – April 2030"
        }
    elif diff == 1:
        return {
            "active": True,
            "type": "Sade Sati Phase 3 (Setting Phase / 2nd House Transit)",
            "impact": "Saturn transits the 2nd from Moon. Financial realignment, family consolidation, and long-term asset stabilization.",
            "dates": "April 2030 – May 2032"
        }
    elif diff == 3:
        return {
            "active": True,
            "type": "Kantaka Shani (4th House Dhaiya)",
            "impact": "Tests domestic peace and work-life balance. Steady focus brings long-term rewards.",
            "dates": "Active 2.5-Year Cycle"
        }
    elif diff == 7:
        return {
            "active": True,
            "type": "Ashtama Shani (8th House Dhaiya)",
            "impact": "Sudden transformations, spiritual deepening, and rigorous health discipline.",
            "dates": "Active 2.5-Year Cycle"
        }
    else:
        return {
            "active": False,
            "type": "No Active Sade Sati or Dhaiya",
            "impact": "Saturn is transiting a neutral/favorable house relative to your Moon. Unobstructed progress.",
            "dates": "N/A"
        }

def calculate_shani_vahan(birth_star_idx: int, transit_moon_star_idx: int) -> dict:
    raw_val = (birth_star_idx * 4 + transit_moon_star_idx) % 9
    rem = 9 if raw_val == 0 else raw_val
    return SHANI_VAHANS.get(rem, SHANI_VAHANS[9])

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
    
    # Sidereal Moon
    moon_lon = get_sidereal_moon_longitude(utc_dt)
    star_span = 360.0 / 27.0
    star_idx = max(1, min(27, int(moon_lon / star_span) + 1))
    rem_deg = moon_lon % star_span
    pada = max(1, min(4, int(rem_deg / (star_span / 4.0)) + 1))
    moon_rashi_idx = max(0, min(11, int(moon_lon / 30.0)))

    # Exact Topocentric Sidereal Lagna
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

# ==============================================================================
# PRECISION SOLAR & MUHURTA CALCULATION ENGINE
# ==============================================================================
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
    sunrise_dt = base_dt + datetime.timedelta(minutes=sr_minutes)
    sunset_dt = base_dt + datetime.timedelta(minutes=ss_minutes)
    solar_noon_dt = base_dt + datetime.timedelta(minutes=solar_noon_minutes)
    
    return sunrise_dt, sunset_dt, solar_noon_dt

def calculate_daily_muhurtas(date_obj: datetime.date, lat: float, lon: float):
    sunrise, sunset, noon = calculate_sun_times(date_obj, lat, lon)
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

def get_7_day_moon_transits(start_ist_dt: datetime.datetime, birth_star_idx: int):
    transits = []
    curr_t = start_ist_dt
    for i in range(7):
        target_t = curr_t + datetime.timedelta(days=i)
        star_idx, s_time, e_time = get_current_nakshatra_window(target_t)
        
        offset = (star_idx - birth_star_idx) % 9
        nav_name, icon, quality = NAVTARA_NAMES[offset]
        vahan_info = calculate_shani_vahan(birth_star_idx, star_idx)
        
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

# ==============================================================================
# USER PROFILE STORAGE MANAGEMENT (DEFAULT: STRICTLY BLANK)
# ==============================================================================
PROFILE_FILE = "user_profile.json"

def load_user_profile():
    blank_profile = {
        "name": "",
        "dob": "",
        "tob": "",
        "city": "",
        "lat": 28.6139,
        "lon": 77.2090,
        "lang": "en"
    }
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure no old hardcoded mock names survive
                if data.get("name") in ["Okesh", "User"]:
                    data["name"] = ""
                    data["dob"] = ""
                    data["tob"] = ""
                    data["city"] = ""
                return {**blank_profile, **data}
        except Exception:
            return blank_profile
    return blank_profile

def save_user_profile(data):
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

if "user_profile" not in st.session_state:
    st.session_state.user_profile = load_user_profile()

if "current_page" not in st.session_state:
    st.session_state.current_page = "about"

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "selected_transit_idx" not in st.session_state:
    st.session_state.selected_transit_idx = 0

if "japa_count" not in st.session_state:
    st.session_state.japa_count = 0

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

# Top Navigation Dock (Clean 2 Rows of 3 Buttons)
# Row 1: About App, User Profile, Numerology
nav_r1_c1, nav_r1_c2, nav_r1_c3 = st.columns(3)
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

# Row 2: Shani, Live Prediction, 7 Days Prediction
nav_r2_c1, nav_r2_c2, nav_r2_c3 = st.columns(3)
with nav_r2_c1:
    p_type = "primary" if st.session_state.current_page == "shani" else "secondary"
    if st.button(t("btn_shani", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "shani"
        st.rerun()

with nav_r2_c2:
    p_type = "primary" if st.session_state.current_page == "live" else "secondary"
    if st.button(t("btn_live", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "live"
        st.rerun()

with nav_r2_c3:
    p_type = "primary" if st.session_state.current_page == "forecast" else "secondary"
    if st.button(t("btn_forecast", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "forecast"
        st.rerun()

render_html("<hr style='margin:10px 0 16px 0; border:none; border-top:1.5px solid #e2e8f0;'>")

# Profile Presence Validation
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
    dob_parsed = None
    tob_parsed = None
    chart_info = None
    mulank, bhagyank, namank = None, None, None
    shani_paya_data = None
    shani_sadesati_data = None

def render_profile_setup_prompt():
    render_html("""
    <div style="background:#fffbeb; border:2px dashed #f59e0b; border-radius:16px; padding:1.5rem; text-align:center; margin:1.5rem 0;">
        <div style="font-size:2.2rem; margin-bottom:8px;">👤</div>
        <div style="font-weight:900; font-size:1.25rem; color:#92400e; margin-bottom:6px;">
            Set Up Your Vedic Birth Profile
        </div>
        <div style="font-size:0.95rem; color:#78350f; max-width:480px; margin:0 auto 1.2rem auto; line-height:1.6;">
            To calculate your personalized <b>Janma Nakshatra</b>, <b>Ascendant (Lagna)</b>, <b>Navtara cycle</b>, and <b>Shani Paya</b>, please enter your birth details in the User Profile tab.
        </div>
    </div>
    """)
    _, c_mid, _ = st.columns([1, 2, 1])
    with c_mid:
        if st.button("👉 Go to User Profile Setup", type="primary", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()


# ==============================================================================
# PAGE 1: ABOUT APP
# ==============================================================================
def render_page_about():
    with st.container(border=True):
        st.markdown("**🌐 Select Language / भाषा चुनें / भाषा निवडा / ભાષા પસંદ કરો:**")
        lang_col1, _ = st.columns([2, 1])
        with lang_col1:
            lang_options = {"en": "English", "hi": "हिन्दी (Hindi)", "mr": "मराठी (Marathi)", "gu": "ગુજરાતી (Gujarati)"}
            selected_lang_code = st.selectbox(
                "App Language",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
                index=list(lang_options.keys()).index(current_lang),
                label_visibility="collapsed"
            )
            if selected_lang_code != current_lang:
                st.session_state.user_profile["lang"] = selected_lang_code
                save_user_profile(st.session_state.user_profile)
                st.rerun()

    render_html("""
    <div class="auth-hero-box">
        <div style="font-weight:900; font-size:1.3rem; color:#92400e; margin-bottom:0.75rem; border-bottom:1.5px solid #fde68a; padding-bottom:0.4rem;">
            🧬 The Authentic Science Behind Vedic Timing & Navtara
        </div>
        
        <div style="font-size:0.96rem; line-height:1.75; color:#451a03; margin-bottom:1rem;">
            <b>1. Lunar Tidal Hydrodynamics & Human Physiology:</b><br>
            The Moon exerts a massive gravitational pull that governs terrestrial tides and fluid circulation. The adult human body consists of approximately <b>70% water</b>. In Vedic science, the Moon represents the conscious and subconscious mind (<i>"Chandro Manaso Jatah"</i>). When the Moon transits resonant or conflicting stellar zones, human focus, emotional equilibrium, and cognitive stamina experience measurable wave-like rhythms.
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#451a03; margin-bottom:1rem;">
            <b>2. Chronobiology & Infradian Circadian Rhythms:</b><br>
            Modern chronobiology establishes that biological life does not operate on a flat 24-hour clock; it is deeply synced to infradian (multi-day) and lunar bio-rhythms. The ancient Vedic <b>Navtara 9-fold grid</b> indexes each day's sidereal Moon position against your natal birth star (Janma Nakshatra) to map expansion and caution windows.
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#451a03; margin-bottom:0.8rem;">
            <b>3. Sub-Arcsecond Ephemeris Precision:</b><br>
            <b>Navtara Pulse</b> integrates with the <b>Moshier Swiss Ephemeris</b> (pyswisseph) and true Lahiri Ayanamsa coordinates, giving you pinpoint accuracy for when cosmic windows open and close across any geographical horizon.
        </div>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            📲 How to Install & Use Like a Native Mobile App
        </div>
        <div style="font-size:0.96rem; line-height:1.7; color:#334155; margin-bottom:1rem;">
            You can install <b>Navtara Pulse</b> directly onto your smartphone's home screen without downloading anything from an app store. It works instantly as a fast Progressive Web App (PWA):
        </div>
        
        <div style="background:#fff7ed; border-radius:12px; padding:12px 14px; border:1px solid #fed7aa; margin-bottom:10px;">
            <b style="color:#9a3412; font-size:1rem;">🤖 For Android Users (Google Chrome):</b>
            <ol style="margin-top:5px; margin-bottom:2px; padding-left:1.3rem; font-size:0.94rem; color:#431407; line-height:1.6;">
                <li>Tap the three vertical dots menu (<b>⋮</b>) in the top-right corner of Chrome.</li>
                <li>Select <b>"Install app"</b> or <b>"Add to Home screen"</b>.</li>
                <li>Tap <b>"Install"</b>. The app icon will appear alongside your native applications.</li>
            </ol>
        </div>

        <div style="background:#fff7ed; border-radius:12px; padding:12px 14px; border:1px solid #fed7aa;">
            <b style="color:#9a3412; font-size:1rem;">🍏 For iPhone / iOS Users (Safari Browser):</b>
            <ol style="margin-top:5px; margin-bottom:2px; padding-left:1.3rem; font-size:0.94rem; color:#431407; line-height:1.6;">
                <li>Open this link in <b>Safari</b> and tap the <b>Share icon</b> (square with an arrow pointing upward).</li>
                <li>Scroll down the menu and tap <b>"Add to Home Screen"</b>.</li>
                <li>Tap <b>"Add"</b> in the top right. The app will launch in full-screen native mode.</li>
            </ol>
        </div>
    </div>
    """)

    app_url = "https://navtara-pulse.streamlit.app"
    share_msg = "Track your real-time Vedic Moon transit rhythm, Shani Paya, and personalized Numerology blueprint with Navtara Pulse!"
    encoded_url = urllib.parse.quote(app_url)
    encoded_msg = urllib.parse.quote(f"{share_msg}\n\nCheck your cosmic alignment here: {app_url}")

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            {t('share_title', current_lang)}
        </div>
        <div style="font-size:0.95rem; color:#475569; margin-bottom:0.85rem;">
            Share this authentic Vedic timing companion with your family, friends, and colleagues:
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

        <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1px solid #fed7aa; text-align:center;">
            <div style="font-size:0.88rem; color:#9a3412; font-weight:800;">Direct Web App URL:</div>
            <div style="font-size:1rem; font-weight:900; color:#431407; margin-top:2px;"><b>{app_url}</b></div>
        </div>
    </div>
    """)


# ==============================================================================
# PAGE 2: USER PROFILE & ASTROLOGICAL PROFILE
# ==============================================================================
def render_page_profile():
    if not has_valid_profile or st.session_state.edit_mode:
        render_html("""
        <div class="light-card-profile">
            <div style="font-weight:900; font-size:1.3rem; color:#9a3412; margin-bottom:0.5rem;">
                👤 Configure Vedic Birth Profile
            </div>
            <div style="font-size:0.94rem; color:#475569; margin-bottom:1rem;">
                Please enter your birth details to generate your authentic Vedic chart, Lagna, Janma Nakshatra, and customized timing rhythm.
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

            # City Selection with Coordinate Autocomplete
            city_options = list(CITY_COORDINATES.keys()) + ["Other (Enter City & Coordinates)"]
            cur_city = prof.get("city", "")
            city_idx = city_options.index(cur_city) if cur_city in city_options else 0
            
            sel_city = st.selectbox(t("city_label", current_lang), options=city_options, index=city_idx)
            
            if sel_city == "Other (Enter City & Coordinates)":
                c_name_in = st.text_input("City Name:", value=prof.get("city", ""))
                c_lat_in = st.number_input("Latitude (° N):", value=float(prof.get("lat", 28.6139)), format="%.4f")
                c_lon_in = st.number_input("Longitude (° E):", value=float(prof.get("lon", 77.2090)), format="%.4f")
                final_city = c_name_in or "Custom Location"
                final_lat = float(c_lat_in)
                final_lon = float(c_lon_in)
            else:
                final_city = sel_city
                final_lat, final_lon = CITY_COORDINATES[sel_city]
            
            c_save, c_canc = st.columns([2, 1])
            with c_save:
                submitted = st.form_submit_button("✨ Save & Calculate Profile", type="primary", use_container_width=True)
            with c_canc:
                canceled = st.form_submit_button("Cancel", use_container_width=True)

            if submitted:
                if not new_name.strip():
                    st.error("Please provide your full name.")
                else:
                    hr_24 = in_hour % 12
                    if in_ampm == "PM":
                        hr_24 += 12
                    final_tob_str = f"{hr_24:02d}:{in_minute:02d}"

                    st.session_state.user_profile.update({
                        "name": new_name.strip(),
                        "dob": new_dob.strftime("%Y-%m-%d"),
                        "tob": final_tob_str,
                        "city": final_city,
                        "lat": final_lat,
                        "lon": final_lon
                    })
                    save_user_profile(st.session_state.user_profile)
                    st.session_state.edit_mode = False
                    st.rerun()
            
            if canceled:
                st.session_state.edit_mode = False
                st.rerun()
        return

    # Profile exists: display profile summary with edit/clear options
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

    n_info = get_nakshatra_traits(chart_info["star_idx"], current_lang)
    m_info = get_moon_rashi_details(chart_info["moon_rashi_idx"], current_lang)
    l_info = get_lagna_details(chart_info["lagna_idx"], current_lang)
    
    moon_parts = chart_info['moon_rashi_name'].split()
    moon_p1 = moon_parts[0] if moon_parts else chart_info['moon_rashi_name']
    moon_p2 = moon_parts[-1] if len(moon_parts) > 1 else ""

    lagna_parts = chart_info['lagna_name'].split()
    lagna_p1 = lagna_parts[0] if lagna_parts else chart_info['lagna_name']
    lagna_p2 = lagna_parts[-1] if len(lagna_parts) > 1 else ""

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.35rem; color:#9a3412; margin-bottom:1rem; border-bottom:2px solid #fed7aa; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>🌌 Astrological Profile</span>
            <span style="font-size:0.85rem; background:#ffedd5; color:#c2410c; padding:4px 10px; border-radius:20px; font-weight:800;">Vedic Lahiri Ayanamsa</span>
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

        <!-- SUBSECTION A: JANMA NAKSHATRA BIO & REMEDIES -->
        <div style="background:#fffaf0; border-radius:14px; padding:14px; border:1.5px solid #fed7aa; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#9a3412; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
                <span>⭐</span> <span>1. Janma Nakshatra: {chart_info['star_name']} (Pada {chart_info['pada']})</span>
            </div>
            
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:8px; margin-bottom:12px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🏛️ Deity:</b> {n_info['deity']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🔱 Symbol:</b> {n_info['symbol']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🌳 Tree (Vriksha):</b> {n_info['tree']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🦅 Bird (Pakshi):</b> {n_info['bird']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🦁 Animal (Yoni):</b> {n_info['animal']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🪐 Planetary Lord:</b> {n_info['lord']}</div>
            </div>

            <div style="margin-bottom:10px;">
                <b style="color:#9a3412; font-size:0.98rem;">🧬 Core Personality Archetype:</b>
                <div style="font-size:0.94rem; line-height:1.65; color:#431407; margin-top:3px;">{n_info['personality']}</div>
            </div>
            
            <div style="margin-bottom:10px;">
                <b style="color:#9a3412; font-size:0.98rem;">🔮 Evolutionary Life Path Prediction:</b>
                <div style="font-size:0.94rem; line-height:1.65; color:#431407; margin-top:3px;">{n_info['prediction']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #f97316; margin-top:10px;">
                <b style="color:#9a3412; font-size:0.98rem;">🪔 Janma Nakshatra Remedies:</b>
                <div style="font-size:0.92rem; line-height:1.65; color:#431407; margin-top:4px; white-space:pre-line;">{n_info['remedies']}</div>
            </div>
        </div>

        <!-- SUBSECTION B: MOON RASHI BIO & REMEDIES -->
        <div style="background:#f0fdf4; border-radius:14px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#065f46; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
                <span>🌙</span> <span>2. Moon Rashi (Chandra Rashi): {m_info['name']}</span>
            </div>

            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:8px; margin-bottom:12px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>🔥 Element:</b> {m_info['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>🪐 Rashi Sovereign:</b> {m_info['ruler']}</div>
            </div>

            <div style="margin-bottom:10px;">
                <b style="color:#065f46; font-size:0.98rem;">🧠 Psychological Temperament & Emotional Mindset:</b>
                <div style="font-size:0.94rem; line-height:1.65; color:#14532d; margin-top:3px;">{m_info['profile']}</div>
            </div>

            <div style="margin-bottom:10px;">
                <b style="color:#065f46; font-size:0.98rem;">🔮 Moon Sign Life Outlook & Strategic Prediction:</b>
                <div style="font-size:0.94rem; line-height:1.65; color:#14532d; margin-top:3px;">{m_info['prediction']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #10b981; margin-top:10px;">
                <b style="color:#065f46; font-size:0.98rem;">🪔 Moon Rashi Remedies:</b>
                <div style="font-size:0.92rem; line-height:1.65; color:#14532d; margin-top:4px; white-space:pre-line;">{m_info['remedies']}</div>
            </div>
        </div>

        <!-- SUBSECTION C: LAGNA BIO & REMEDIES -->
        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:0.5rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
                <span>🌅</span> <span>3. Lagna (Ascendant): {l_info['name']} ({chart_info['lagna_deg']})</span>
            </div>

            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:8px; margin-bottom:12px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>🌍 Lagna Tattva:</b> {l_info['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>👑 Lagna Lord:</b> {l_info['lord']}</div>
            </div>

            <div style="margin-bottom:10px;">
                <b style="color:#5b21b6; font-size:0.98rem;">🛡️ Physical Vitality & Outward Persona:</b>
                <div style="font-size:0.94rem; line-height:1.65; color:#3b0764; margin-top:3px;">{l_info['profile']}</div>
            </div>

            <div style="margin-bottom:10px;">
                <b style="color:#5b21b6; font-size:0.98rem;">🔮 Life Direction & Societal Stature Prediction:</b>
                <div style="font-size:0.94rem; line-height:1.65; color:#3b0764; margin-top:3px;">{l_info['prediction']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #8b5cf6; margin-top:10px;">
                <b style="color:#5b21b6; font-size:0.98rem;">🪔 Lagna Remedies:</b>
                <div style="font-size:0.92rem; line-height:1.65; color:#3b0764; margin-top:4px; white-space:pre-line;">{l_info['remedies']}</div>
            </div>
        </div>

    </div>
    """)


# ==============================================================================
# PAGE 3: NUMEROLOGY
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
        <div style="font-weight:900; font-size:1.25rem; color:#065f46; margin-bottom:1rem; border-bottom:2px solid #bbf7d0; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>🔢 Core Numerology Blueprint</span>
            <span style="font-size:0.85rem; background:#d1fae5; color:#065f46; padding:4px 10px; border-radius:20px; font-weight:800;">Vedic & Chaldean</span>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:10px; text-align:center; margin-bottom:1.15rem;">
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900; text-transform:uppercase;">{t('mulank_label', current_lang)}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46; margin:2px 0;">{mulank}</div>
                <div style="font-size:0.9rem; color:#059669; font-weight:800;">{p_m_label}</div>
            </div>
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900; text-transform:uppercase;">{t('bhagyank_label', current_lang)}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46; margin:2px 0;">{bhagyank}</div>
                <div style="font-size:0.9rem; color:#059669; font-weight:800;">{p_b_label}</div>
            </div>
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900; text-transform:uppercase;">{t('namank_label', current_lang)}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46; margin:2px 0;">{namank}</div>
                <div style="font-size:0.9rem; color:#059669; font-weight:800;">{p_n_label}</div>
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
                • <b>Metal Vessel Grounding:</b> Drink water from a pure silver or copper vessel to pacify Rahu-Mars nervous restlessness and enhance bio-electrical harmony.<br>
                • <b>Digital & Workspace Bio-Shield:</b> Remove tangled charging cables, broken electronic gadgets, and inactive clocks from your study/office desk to unblock Mercury-Rahu frequencies.<br>
                • <b>Name Resonance (Namank):</b> Use green or blue ink when writing or endorsing important planning documents to harmonize your {namank} name vibration.
            </div>
        </div>
    </div>
    """)


# ==============================================================================
# PAGE 4: SHANI
# ==============================================================================
def render_page_shani():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    render_html(f"""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.3rem; color:#5b21b6; margin-bottom:1rem; border-bottom:2px solid #ddd6fe; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{t('shani_paya_title', current_lang)}</span>
            <span style="font-size:0.85rem; background:#ede9fe; color:#5b21b6; padding:4px 10px; border-radius:20px; font-weight:800;">Saturn in Pisces (Meena)</span>
        </div>
        
        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #e9d5ff; margin-bottom:1.15rem;">
            <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">ACTIVE TRANSIT PAYA & FOOTING MECHANICS</div>
            <div style="font-size:1.4rem; font-weight:900; color:#5b21b6; margin:4px 0;">{shani_paya_data['paya']}</div>
            <div style="font-size:0.95rem; color:#7c3aed; font-weight:800;">Status: {shani_paya_data['status']}</div>
            <div style="font-size:0.92rem; color:#475569; margin-top:3px;"><b>Active Timeline:</b> {shani_paya_data['timeline']}</div>
            
            <div style="font-size:0.95rem; line-height:1.7; color:#3b0764; margin-top:10px;">
                <b>Why Rajat Paya (Silver Feet) is Highly Auspicious:</b><br>
                In classical Vedic transit science (<i>Gochara Shastra</i>), the arrival of Saturn into a zodiac sign is evaluated through the house distance from your natal Moon sign. Silver footing ensures that financial avenues remain open, ancestral protection guards your health, and reputation remains intact through testing times.
            </div>
            
            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-top:10px; font-size:0.9rem; color:#475569;">
                <b>The 4 Classical Shani Payas:</b><br>
                • <b>🥈 Rajat (Silver - Houses 2, 5, 9):</b> Highly Auspicious | Financial gains, honor & peace.<br>
                • <b>🥉 Tamra (Copper - Houses 3, 7, 10):</b> Favorable | Success through patient labor & family harmony.<br>
                • <b>🥇 Swarna (Gold - Houses 1, 6, 11):</b> Testing | High expenditures, ego conflicts & mental worries.<br>
                • <b>🪙 Loha (Iron - Houses 4, 8, 12):</b> Demanding | Physical stress, delays & heavy karmic debts.
            </div>
        </div>

        <div style="background:#ffffff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:10px; border-bottom:1px solid #e9d5ff; padding-bottom:5px;">
                ⚖️ Complete 3-Phase Sade Sati Matrix (7.5 Years Roadmap)
            </div>

            <div style="background:#faf5ff; border-radius:12px; padding:12px; border-left:5px solid #9333ea; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:900; font-size:1rem; color:#5b21b6;">Phase 1: Rising Phase (Aarohi Charana - 12th House Transit)</span>
                    <span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW</span>
                </div>
                <div style="font-size:0.9rem; color:#64748b; margin:2px 0 6px 0;"><b>Timeline:</b> 29 March 2025 – 23 February 2028 (Meena / Pisces)</div>
                <div style="font-size:0.93rem; line-height:1.65; color:#3b0764;">
                    <b>Detailed Prediction:</b> Saturn transits through your 12th house of expenditures, foreign linkages, subconscious shedding, and solitude. Restructure personal priorities and eliminate wasteful overhead. Financial outflow converts into productive assets under Silver feet.
                </div>
                <div style="margin-top:8px; font-size:0.92rem; color:#4c1d95; background:#ffffff; padding:8px 10px; border-radius:8px; border:1px solid #e9d5ff;">
                    <b>🪔 Phase 1 Remedies:</b> Offer raw cow milk mixed with water on a Shiva Lingam on Mondays. Donate black sesame seeds and mustard oil on Saturdays. Keep a silver coin in your wallet.
                </div>
            </div>

            <div style="background:#f8fafc; border-radius:12px; padding:12px; border-left:5px solid #64748b; margin-bottom:12px;">
                <div style="font-weight:900; font-size:1rem; color:#1e293b;">Phase 2: Peak Phase (Janma Shani - 1st House Transit)</div>
                <div style="font-size:0.9rem; color:#64748b; margin:2px 0 6px 0;"><b>Timeline:</b> 23 February 2028 – 17 April 2030</div>
                <div style="font-size:0.93rem; line-height:1.65; color:#334155;">
                    <b>Detailed Prediction:</b> Saturn transits directly over your natal Moon. Crucible of self-mastery demanding absolute ego surrender, physical stamina, and unwavering patience.
                </div>
                <div style="margin-top:8px; font-size:0.92rem; color:#1e293b; background:#ffffff; padding:8px 10px; border-radius:8px; border:1px solid #e2e8f0;">
                    <b>🪔 Phase 2 Remedies:</b> Recite the <b>Hanuman Chalisa</b> twice daily. Light a mustard oil lamp beneath a Peepal tree every Saturday evening.
                </div>
            </div>

            <div style="background:#f8fafc; border-radius:12px; padding:12px; border-left:5px solid #64748b;">
                <div style="font-weight:900; font-size:1rem; color:#1e293b;">Phase 3: Setting Phase (Avarohi Charana - 2nd House Transit)</div>
                <div style="font-size:0.9rem; color:#64748b; margin:2px 0 6px 0;"><b>Timeline:</b> 17 April 2030 – 31 May 2032</div>
                <div style="font-size:0.93rem; line-height:1.65; color:#334155;">
                    <b>Detailed Prediction:</b> Saturn transits the 2nd house of accumulated wealth and family. Lessons crystallize into permanent assets, financial consolidation, and family maturity.
                </div>
                <div style="margin-top:8px; font-size:0.92rem; color:#1e293b; background:#ffffff; padding:8px 10px; border-radius:8px; border:1px solid #e2e8f0;">
                    <b>🪔 Phase 3 Remedies:</b> Feed whole wheat flour dough balls mixed with black sesame to black cows or fish on Saturdays.
                </div>
            </div>
        </div>

        <div style="background:#fff1f2; border-radius:14px; padding:14px; border:1.5px solid #fecdd3; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#9f1239; margin-bottom:8px;">
                ⚠️ Critical Cautions: What to Avoid During Sade Sati
            </div>
            <ul style="margin:0; padding-left:1.25rem; font-size:0.93rem; line-height:1.7; color:#881337;">
                <li><b>Never Mistreat Subordinates:</b> Disrespecting or delaying payment to blue-collar laborers incurs swift Saturnic karmic penalty.</li>
                <li><b>Avoid Speculative Leverage:</b> Do not engage in debt-fueled day trading or unverified speculative schemes.</li>
                <li><b>No Saturday Contracts or Iron Purchases:</b> Do not sign high-stakes contracts or buy iron/leather on Saturdays.</li>
                <li><b>Strictly Avoid Intoxicants:</b> Substance abuse or deceitful speech severely destabilizes Shani's protective aura.</li>
            </ul>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:10px; border-bottom:1px solid #e9d5ff; padding-bottom:5px;">
                🪔 Authentic Vedic & Puranic Shani Mantras
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #ddd6fe; margin-bottom:10px;">
                <b style="color:#5b21b6; font-size:0.98rem;">1. Vedic Samhita Shani Mantra:</b>
                <div style="font-family:serif; font-size:1.05rem; font-weight:700; color:#1e1b4b; margin:6px 0; line-height:1.6;">
                    ॐ शं नो देवीरभिष्टय आपो भवन्तु पीतये। शं योरभि स्रवन्तु नः॥
                </div>
                <div style="font-size:0.88rem; color:#475569; font-style:italic;">
                    <b>Transliteration:</b> Om Sham No Deviir-Abhishtaye Aapo Bhavantu Piitaye | Sham Yor-Abhi Sravantu Nah ||
                </div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #ddd6fe; margin-bottom:10px;">
                <b style="color:#5b21b6; font-size:0.98rem;">2. Shani Beej Mantra:</b>
                <div style="font-family:serif; font-size:1.15rem; font-weight:800; color:#1e1b4b; margin:6px 0;">
                    ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः॥
                </div>
                <div style="font-size:0.88rem; color:#475569; font-style:italic;">
                    <b>Transliteration:</b> Om Praam Preem Proum Sah Shanaishcharaya Namah ||
                </div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #ddd6fe;">
                <b style="color:#5b21b6; font-size:0.98rem;">3. Shani Gayatri Mantra:</b>
                <div style="font-family:serif; font-size:1.05rem; font-weight:700; color:#1e1b4b; margin:6px 0; line-height:1.6;">
                    ॐ सूर्यपुत्राय विद्महे मृत्युरूपाय धीमहि। तन्नो सौरिः प्रचोदयात्॥
                </div>
                <div style="font-size:0.88rem; color:#475569; font-style:italic;">
                    <b>Transliteration:</b> Om Suryaputraya Vidmahe Mrityuroopaya Dheemahi | Tanno Saurih Prachodayat ||
                </div>
            </div>
        </div>
    </div>
    """)

    # Interactive Digital Japa Mala Counter (1 to 108 Beads)
    with st.container(border=True):
        st.markdown("**📿 Interactive Digital Japa Mala Counter (108 Beads)**")
        progress_pct = min(1.0, st.session_state.japa_count / 108.0)
        st.progress(progress_pct, text=f"Bead Count: {st.session_state.japa_count} / 108 ({int(progress_pct * 100)}%)")
        
        c_tap, c_reset = st.columns([2, 1])
        with c_tap:
            if st.button("📿 Tap Bead (+1)", type="primary", use_container_width=True):
                st.session_state.japa_count += 1
                if st.session_state.japa_count > 108:
                    st.session_state.japa_count = 1
                st.rerun()
        with c_reset:
            if st.button("🔄 Reset Mala", use_container_width=True):
                st.session_state.japa_count = 0
                st.rerun()


# ==============================================================================
# DETAILED PREDICTION & REMEDIES ENGINE
# ==============================================================================
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
# PAGE 5: LIVE DAILY PREDICTION (FEATURING PRECISION MUHURTA ENGINE)
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

    # Compute live precision Muhurtas for active user coordinates
    muhurtas = calculate_daily_muhurtas(now_ist.date(), u_lat, u_lon)
    
    abhijit_s, abhijit_e = muhurtas["abhijit"]
    rahu_s, rahu_e = muhurtas["rahu"]
    yama_s, yama_e = muhurtas["yamaganda"]
    brahma_s, brahma_e = muhurtas["brahma"]

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
        upcoming_notes = []
        if now_ist < abhijit_s:
            upcoming_notes.append(f"Next Abhijit: {abhijit_s.strftime('%I:%M %p')}")
        if now_ist < rahu_s:
            upcoming_notes.append(f"Rahu Kaal: {rahu_s.strftime('%I:%M %p')}")
        
        note_str = " | ".join(upcoming_notes) if upcoming_notes else "All major caution and golden windows for today have concluded."

        status_banner = f"""
        <div style="background:#f0fdf4; border:1.5px solid #86efac; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#166534; font-size:0.98rem;">🟢 SAFE TO ACT: Standard Favorable Orbit ({now_time_str} IST)</b>
                <div style="font-size:0.86rem; color:#15803d; margin-top:2px;">No planetary friction windows currently active. {note_str}</div>
            </div>
            <span style="font-size:1.6rem;">⏱️</span>
        </div>
        """

    golden_items = []
    if now_ist <= abhijit_e:
        status_tag = "ACTIVE NOW" if is_abhijit else "Upcoming"
        golden_items.append(f"""
        <div style="margin-bottom:8px;">
            • <b>Abhijit Muhurta ({status_tag}):</b><br>
            <span style="font-size:1.05rem; font-weight:900; color:#15803d;">{abhijit_s.strftime('%I:%M %p')} – {abhijit_e.strftime('%I:%M %p IST')}</span><br>
            <i style="font-size:0.84rem; color:#166534;">(Supreme window for agreements, launches & investments)</i>
        </div>
        """)
    if now_ist <= brahma_e:
        golden_items.append(f"""
        <div style="margin-bottom:8px;">
            • <b>Brahma Muhurta:</b><br>
            <span style="font-weight:800; color:#15803d;">{brahma_s.strftime('%I:%M %p')} – {brahma_e.strftime('%I:%M %p IST')}</span><br>
            <i style="font-size:0.84rem; color:#166534;">(Peak sattvic time for meditation & spiritual grounding)</i>
        </div>
        """)
    
    if not golden_items:
        golden_html = "<div style='font-size:0.9rem; color:#166534; font-style:italic;'>Today's morning & midday golden windows (Brahma & Abhijit) have concluded for the day.</div>"
    else:
        golden_html = "".join(golden_items)

    caution_items = []
    if now_ist <= rahu_e:
        status_tag = "ACTIVE NOW" if is_rahu else "Upcoming"
        caution_items.append(f"""
        <div style="margin-bottom:8px;">
            • <b>Rahu Kaal ({status_tag}):</b><br>
            <span style="font-size:1.05rem; font-weight:900; color:#be123c;">{rahu_s.strftime('%I:%M %p')} – {rahu_e.strftime('%I:%M %p IST')}</span><br>
            <i style="font-size:0.84rem; color:#9f1239;">(Pause high-risk trades, signing deeds & departures)</i>
        </div>
        """)
    if now_ist <= yama_e:
        status_tag = "ACTIVE NOW" if is_yama else "Upcoming"
        caution_items.append(f"""
        <div style="margin-bottom:8px;">
            • <b>Yamaganda ({status_tag}):</b><br>
            <span style="font-weight:800; color:#be123c;">{yama_s.strftime('%I:%M %p')} – {yama_e.strftime('%I:%M %p IST')}</span><br>
            <i style="font-size:0.84rem; color:#9f1239;">(Avoid starting brand-new critical ventures)</i>
        </div>
        """)

    if not caution_items:
        caution_html = "<div style='font-size:0.9rem; color:#9f1239; font-style:italic;'>🟢 Clear Cosmic Highway: Today's Rahu Kaal and Yamaganda periods have ended.</div>"
    else:
        caution_html = "".join(caution_items)

    render_html(f"""
    <div class="light-card-live">
        <div style="font-weight:900; font-size:1.25rem; color:#0369a1; margin-bottom:1rem; border-bottom:2px solid #bae6fd; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{t('live_pulse_title', current_lang)}</span>
            <span style="font-size:0.85rem; background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:20px; font-weight:900;">LIVE IST</span>
        </div>

        {status_banner}

        <!-- TRANSIT HEADER -->
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

        <!-- PRECISION MUHURTA TIMING WINDOWS (WITH DYNAMIC EXPIRATION) -->
        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#0369a1; margin-bottom:10px; border-bottom:1px solid #e0f2fe; padding-bottom:5px; display:flex; justify-content:space-between; align-items:center;">
                <span>⏱️ Active & Upcoming Timing Windows</span>
                <span style="font-size:0.8rem; color:#0284c7; background:#e0f2fe; padding:2px 8px; border-radius:12px; font-weight:800;">Real-Time IST</span>
            </div>

            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:10px; margin-bottom:10px;">
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; border:1px solid #86efac;">
                    <b style="color:#166534; font-size:0.95rem;">🌟 Golden Auspicious Windows:</b>
                    <div style="margin-top:6px;">{golden_html}</div>
                </div>
                <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; border:1px solid #fecdd3;">
                    <b style="color:#9f1239; font-size:0.95rem;">⚠️ Caution & Inauspicious Windows:</b>
                    <div style="margin-top:6px;">{caution_html}</div>
                </div>
            </div>
            
            <div style="font-size:0.85rem; color:#64748b; text-align:right;">
                🌅 Sunrise: <b>{muhurtas['sunrise'].strftime('%I:%M %p')}</b> &nbsp;|&nbsp; 🌇 Sunset: <b>{muhurtas['sunset'].strftime('%I:%M %p IST')}</b>
            </div>
        </div>

        <!-- DUAL METRICS -->
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin-bottom:1.1rem;">
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd;">
                <div style="font-size:0.85rem; color:#0284c7; font-weight:800; text-transform:uppercase;">DAILY SHANI VAHAN</div>
                <div style="font-size:1.15rem; font-weight:900; color:#0369a1;">{vahan_info['name']}</div>
                <div style="font-size:0.88rem; color:#64748b;"><b>Type:</b> {vahan_info['type']} ({vahan_info['speed']})</div>
                <div style="font-size:0.88rem; color:#0369a1; margin-top:4px;">{vahan_info['desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd;">
                <div style="font-size:0.85rem; color:#0284c7; font-weight:800; text-transform:uppercase;">PERSONAL DAY VIBRATION</div>
                <div style="font-size:1.15rem; font-weight:900; color:#0369a1;">Day {p_day['number']} ({p_day['planet'].split()[0]})</div>
                <div style="font-size:0.88rem; color:#64748b;"><b>Planetary Tone:</b> {p_day['planet']}</div>
                <div style="font-size:0.88rem; color:#0369a1; margin-top:4px;">{p_day['desc']}</div>
            </div>
        </div>

        <!-- 4-DOMAIN ACTION QUICK CHECKLIST -->
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

        <!-- IN-DEPTH COGNITIVE & STRATEGIC THEME -->
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

        <!-- COMPREHENSIVE ACTIONABLE REMEDIES -->
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
# PAGE 6: 7-DAY NAKSHATRA TRANSIT FORECAST
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

    # 7-Day Visual Energy Heatmap Strip
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
# ROUTER DISPATCHER: RENDER THE SELECTED PAGE
# ==============================================================================
PAGES = {
    "about": render_page_about,
    "profile": render_page_profile,
    "navtara": render_page_profile,
    "numerology": render_page_numerology,
    "shani": render_page_shani,
    "live": render_page_live,
    "forecast": render_page_forecast,
}

active_page_func = PAGES.get(st.session_state.current_page, render_page_about)
active_page_func()
