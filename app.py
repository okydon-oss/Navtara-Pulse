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
# GEODETIC ATLAS (DEFAULT COORDINATES)
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

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

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
    9: {"en": "Mars (Mangal / मंगल)", "hi": "मंगल (Mars)", "mr": "मंगळ (Mars)", "gu": "મંગળ (Mars)"}
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
        "city_label": "Birth Location",
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

# ==============================================================================
# RIGOROUS ASTROLOGICAL & BOTANICAL ENCYCLOPEDIA (ALL 27 NAKSHATRAS)
# ==============================================================================
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
    
    pers_en = f"Born under {star_name}, governed by {bio['deity']} and planetary lord {bio['lord']}, you inherit deep intuition, resilient character, and natural authority in leadership and structural projects."
    pred_en = f"Your evolutionary life trajectory unfolds through consistent self-mastery. Governed by {bio['lord']}, your mature years bring solid asset accumulation and executive honor."
    rem_en = f"• Recite the Beej Mantra of {bio['deity']} 11 or 108 times daily.\n• Respect and nurture your sacred tree ({bio['tree']}).\n• Practice daily gratitude and feed wild animals/birds ({bio['bird']}) to balance karmic weight."

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
    
    prof_en = f"With Moon in {r_name}, your mind operates through the {r_elem} tattva governed by {r_lord}. You possess sharp emotional reflexes, deep intuitive endurance, and purposeful strategic focus."
    pred_en = f"Chandra in {r_lord}'s domain provides mental fortitude, resourcefulness, and capacity to turn challenges into long-term assets."
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
    
    prof_en = f"Your Ascendant (Lagna) is {l_name}, rooted in {l_elem} tattva under the sovereign rulership of {l_lord}. Your outward demeanor radiates poise, resolute stability, and strong constitutional stamina."
    pred_en = f"With {l_lord} presiding over your first house of vitality, your career moves toward executive responsibility, institutional trust, and compounding respect."
    rem_en = f"• Apply pure white sandalwood paste or natural attar to pulse points.\n• Practice morning Pranayama to align physical breath with mental vitality.\n• Strengthen Lagna lord through disciplined daily routines and ethical integrity."

    return {
        "name": l_name,
        "element": l_elem,
        "lord": l_lord,
        "profile": prof_en,
        "prediction": pred_en,
        "remedies": rem_en
    }

def get_numerology_life_domains(mulank: int, bhagyank: int, namank: int, lang: str = "en") -> dict:
    p_m = NUM_PLANET_NAMES.get(mulank, {}).get(lang, f"Planet {mulank}")
    p_b = NUM_PLANET_NAMES.get(bhagyank, {}).get(lang, f"Planet {bhagyank}")

    return {
        "career_title": "💼 Career Trajectory & Executive Ambition",
        "career_desc": f"The dynamic synthesis of Driver {mulank} ({p_m}) and Conductor {bhagyank} ({p_b}) creates an unstoppable powerhouse combination of strategic vision and courageous execution. You are naturally engineered for leadership, structural problem solving, and projects where you hold autonomy.",
        "wealth_title": "💰 Wealth Dynamics & Financial Mastery",
        "wealth_desc": "Your vibrational alignment supports long-term asset accumulation. Avoid volatile speculative day-trading; tangible assets—real estate, gold, and established technical systems—yield supreme compounding.",
        "rel_title": "❤️ Relationships & Interpersonal Dynamics",
        "rel_desc": "You value authentic, pretense-free connections. Practicing active listening and measured verbal composure during crucial discussions will keep family and professional bonds deeply harmonious.",
        "health_title": "🌿 Health, Vitality & Holistic Bio-Rhythms",
        "health_desc": "You possess strong physical endurance. Counteract mental fatigue with structured sleep rhythms, deep hydration, and 10 minutes of evening breathwork.",
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

# ==============================================================================
# PRECISION ASTRONOMICAL ENGINE (LAHIRI AYANAMSA & TOPOCENTRIC LAGNA)
# ==============================================================================
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
    jd = get_julian_day(utc_dt)
    if HAS_SWISSEPH:
        try:
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            res = swe.calc_ut(jd, swe.MOON, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)
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

def calculate_birth_chart(dob: datetime.date, tob: datetime.time, lat: float, lon: float, calibrated_lagna: str = "Auto-Calculate"):
    ist_dt = datetime.datetime.combine(dob, tob)
    utc_dt = ist_dt - datetime.timedelta(hours=5, minutes=30)
    
    moon_lon = get_sidereal_moon_longitude(utc_dt)
    star_span = 360.0 / 27.0
    star_idx = max(1, min(27, int(moon_lon / star_span) + 1))
    rem_deg = moon_lon % star_span
    pada = max(1, min(4, int(rem_deg / (star_span / 4.0)) + 1))
    moon_rashi_idx = max(0, min(11, int(moon_lon / 30.0)))

    lagna_lon = calculate_sidereal_ascendant(utc_dt, lat, lon)
    calc_lagna_idx = max(0, min(11, int(lagna_lon / 30.0)))

    if calibrated_lagna and calibrated_lagna != "Auto-Calculate" and calibrated_lagna in RASHIS:
        final_lagna_idx = RASHIS.index(calibrated_lagna)
    else:
        final_lagna_idx = calc_lagna_idx

    return {
        "star_idx": star_idx,
        "star_name": NAKSHATRAS[star_idx - 1],
        "pada": pada,
        "moon_lon": moon_lon,
        "moon_rashi_idx": moon_rashi_idx,
        "moon_rashi_name": RASHIS[moon_rashi_idx],
        "lagna_lon": lagna_lon,
        "lagna_deg": f"{int(lagna_lon % 30)}° {int(((lagna_lon % 30) % 1) * 60)}'",
        "lagna_idx": final_lagna_idx,
        "lagna_name": RASHIS[final_lagna_idx]
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

# ==============================================================================
# USER PROFILE MANAGEMENT (STRICT BLANK DEFAULTS)
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
        "calibrated_lagna": "Auto-Calculate",
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

# Universal Centered Header
render_html(f"""
    <div style='text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; margin-top:0.2rem; margin-bottom:0.75rem;'>
        <div style='background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); width:76px; height:76px; border-radius:26px; display:flex; align-items:center; justify-content:center; font-size:2.45rem; box-shadow:0 8px 28px rgba(245,158,11,0.38); margin-bottom:10px;'>
            ✨
        </div>
        <h1 style='margin:0; font-size:2.15rem; color:#0f172a; font-weight:900; line-height:1.2; text-align:center;'>{t('app_title', current_lang)}</h1>
        <div style='font-size:1rem; color:#64748b; font-weight:600; margin-top:6px; text-align:center;'>{t('app_subtitle', current_lang)}</div>
    </div>
""")

# Top Navigation Dock
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

    calib_lagna = prof.get("calibrated_lagna", "Auto-Calculate")
    chart_info = calculate_birth_chart(
        dob_parsed, tob_parsed,
        float(prof.get("lat", 28.6139)), float(prof.get("lon", 77.2090)),
        calib_lagna
    )
    
    def reduce_to_single_digit(num: int) -> int:
        while num > 9:
            num = sum(int(ch) for ch in str(num))
        return num if num > 0 else 9

    mulank = reduce_to_single_digit(dob_parsed.day)
    bhagyank = reduce_to_single_digit(dob_parsed.day + dob_parsed.month + dob_parsed.year)
    cleaned_name = "".join(ch for ch in prof.get("name", "").upper() if ch.isalpha())
    namank_val = sum(CHALDEAN_MAP.get(ch, 0) for ch in cleaned_name)
    namank = reduce_to_single_digit(namank_val) if namank_val > 0 else 1

    SATURN_TRANSIT_RASHI_IDX = 11
    house_diff = (chart_info["moon_rashi_idx"] - SATURN_TRANSIT_RASHI_IDX) % 12 + 1
    if house_diff in [2, 5, 9]:
        shani_paya_data = {"paya": "🥈 Rajat Paya (Silver Feet / चाँदी का पाया)", "metal": "Silver", "status": "Highly Auspicious (अति शुभ)", "desc": "Saturn arrives bearing silver gifts. Bestows financial liquidity and divine protection.", "timeline": "29 March 2025 – 23 February 2028"}
    elif house_diff in [3, 7, 10]:
        shani_paya_data = {"paya": "🥉 Tamra Paya (Copper Feet / तांबे का पाया)", "metal": "Copper", "status": "Favorable (शुभ)", "desc": "Brings steady professional growth and family harmony.", "timeline": "29 March 2025 – 23 February 2028"}
    elif house_diff in [1, 6, 11]:
        shani_paya_data = {"paya": "🥇 Swarna Paya (Gold Feet / सोने का पाया)", "metal": "Gold", "status": "Testing & Demanding (कठिन)", "desc": "Tests character through ego challenges and expenditures.", "timeline": "29 March 2025 – 23 February 2028"}
    else:
        shani_paya_data = {"paya": "🪙 Loha Paya (Iron Feet / लोहे का पाया)", "metal": "Iron", "status": "Difficult / High Friction (संघर्षमय)", "desc": "Indicates delays and heavy responsibilities.", "timeline": "29 March 2025 – 23 February 2028"}
else:
    dob_parsed, tob_parsed, chart_info = None, None, None
    mulank, bhagyank, namank = None, None, None
    shani_paya_data = None

def render_profile_setup_prompt():
    render_html("""
    <div style="background:#fffbeb; border:2px dashed #f59e0b; border-radius:16px; padding:1.5rem; text-align:center; margin:1.5rem 0;">
        <div style="font-size:2.2rem; margin-bottom:8px;">👤</div>
        <div style="font-weight:900; font-size:1.25rem; color:#92400e; margin-bottom:6px;">
            Set Up Your Vedic Birth Profile
        </div>
        <div style="font-size:0.95rem; color:#78350f; max-width:480px; margin:0 auto 1.2rem auto; line-height:1.6;">
            To view your personalized <b>Janma Nakshatra</b>, <b>Ascendant (Lagna)</b>, <b>Navtara cycle</b>, and <b>Shani Paya</b>, please configure your birth details.
        </div>
    </div>
    """)
    _, c_mid, _ = st.columns([1, 2, 1])
    with c_mid:
        if st.button("👉 Configure Profile Now", type="primary", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()

# ==============================================================================
# TAB 1: ABOUT APP
# ==============================================================================
def render_page_about():
    with st.container(border=True):
        st.markdown("**🌐 Select Language / भाषा चुनें:**")
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
            🧬 Classical Sidereal Vedic Engine (Lahiri Ayanamsa)
        </div>
        <div style="font-size:0.96rem; line-height:1.75; color:#451a03; margin-bottom:0.8rem;">
            <b>Astronomical Accuracy & Astrological Calibration:</b><br>
            Navtara Pulse calculates Local Sidereal Time (RAMC) using true geographical coordinates and planetary ephemeris tables. Because traditional Kundali charts (such as AstroSage or family horoscopes) may apply specific Daylight Saving, War Time, or Ayanamsa conventions, you can also calibrate your exact Lagna (Ascendant) directly in your profile settings.
        </div>
    </div>
    """)

# ==============================================================================
# TAB 2: USER PROFILE
# ==============================================================================
def render_page_profile():
    if not has_valid_profile or st.session_state.edit_mode:
        render_html("""
        <div class="light-card-profile">
            <div style="font-weight:900; font-size:1.3rem; color:#9a3412; margin-bottom:0.5rem;">
                👤 Configure Vedic Birth Profile
            </div>
            <div style="font-size:0.94rem; color:#475569; margin-bottom:1rem;">
                Enter your exact birth details below to calculate your Kundali, Navtara bio-rhythm, and planetary periods.
            </div>
        </div>
        """)
        with st.form("profile_form"):
            in_name = st.text_input(t("name_label", current_lang), value=prof.get("name", ""))
            
            d_val = dob_parsed if dob_parsed else datetime.date(1990, 1, 1)
            in_dob = st.date_input(t("dob_label", current_lang), value=d_val)
            
            st.markdown("**Birth Time (Hour, Minute & AM/PM):**")
            t_col1, t_col2, t_col3 = st.columns([1.5, 1.5, 1.5])
            with t_col1:
                cur_hr = (tob_parsed.hour % 12) if tob_parsed else 10
                cur_hr = 12 if cur_hr == 0 else cur_hr
                in_hour = st.selectbox("Hour", options=list(range(1, 13)), index=cur_hr - 1)
            with t_col2:
                cur_min = tob_parsed.minute if tob_parsed else 30
                in_minute = st.selectbox("Minute", options=list(range(0, 60)), index=cur_min)
            with t_col3:
                cur_ampm = "PM" if (tob_parsed and tob_parsed.hour >= 12) else "AM"
                in_ampm = st.selectbox("AM / PM", options=["AM", "PM"], index=0 if cur_ampm == "AM" else 1)
            
            # City Selection
            default_city = prof.get("city", "")
            city_list = list(CITY_COORDINATES.keys())
            idx_sel = city_list.index(default_city) if default_city in city_list else 0
            
            in_city_choice = st.selectbox(
                "Birth City / Location",
                options=city_list + ["Other (Enter Coordinates)"],
                index=idx_sel
            )
            
            if in_city_choice == "Other (Enter Coordinates)":
                custom_lat = st.number_input("Latitude (° N)", value=float(prof.get("lat", 28.6139)), format="%.4f")
                custom_lon = st.number_input("Longitude (° E)", value=float(prof.get("lon", 77.2090)), format="%.4f")
            else:
                custom_lat, custom_lon = CITY_COORDINATES[in_city_choice]

            st.markdown("**Kundali Ascendant (Lagna) Calibration:**")
            calib_options = ["Auto-Calculate"] + RASHIS
            cur_calib = prof.get("calibrated_lagna", "Auto-Calculate")
            idx_calib = calib_options.index(cur_calib) if cur_calib in calib_options else 0
            in_calib_lagna = st.selectbox(
                "Align Lagna with your AstroSage / Vedic Chart:",
                options=calib_options,
                index=idx_calib,
                help="Leave on 'Auto-Calculate' to calculate automatically, or select your known Lagna sign (e.g., Tula) if your software applied a specific timezone or DST adjustment."
            )

            c_sub, c_rst = st.columns([2, 1])
            with c_sub:
                btn_save = st.form_submit_button("✨ Save & Calculate Profile", type="primary", use_container_width=True)
            with c_rst:
                btn_cancel = st.form_submit_button("Cancel", use_container_width=True)

            if btn_save:
                if not in_name.strip():
                    st.error("Please enter a full name.")
                else:
                    hr_24 = in_hour % 12
                    if in_ampm == "PM":
                        hr_24 += 12
                    t_str = f"{hr_24:02d}:{in_minute:02d}"

                    st.session_state.user_profile.update({
                        "name": in_name.strip(),
                        "dob": in_dob.strftime("%Y-%m-%d"),
                        "tob": t_str,
                        "city": in_city_choice if in_city_choice != "Other (Enter Coordinates)" else f"{custom_lat:.2f}N, {custom_lon:.2f}E",
                        "lat": float(custom_lat),
                        "lon": float(custom_lon),
                        "calibrated_lagna": in_calib_lagna
                    })
                    save_user_profile(st.session_state.user_profile)
                    st.session_state.edit_mode = False
                    st.rerun()

            if btn_cancel:
                st.session_state.edit_mode = False
                st.rerun()
        return

    # Verified Profile View
    with st.container(border=True):
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            render_html(f"""
            <div style="font-weight:900; font-size:1.2rem; color:#0f172a;">👤 {prof['name']}'s Profile</div>
            <div style="font-size:0.95rem; color:#334155; margin-top:5px; line-height:1.6;">
                📅 <b>DOB:</b> {dob_parsed.strftime('%d %B %Y')} &nbsp;|&nbsp; ⏰ <b>Time:</b> {tob_parsed.strftime('%I:%M %p')}<br>
                📍 <b>Place:</b> {prof['city']} ({prof['lat']:.4f}° N, {prof['lon']:.4f}° E)
            </div>
            """)
        with col_p2:
            if st.button(t("edit_details", current_lang), use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()

    n_info = get_nakshatra_traits(chart_info["star_idx"], current_lang)
    m_info = get_moon_rashi_details(chart_info["moon_rashi_idx"], current_lang)
    l_info = get_lagna_details(chart_info["lagna_idx"], current_lang)

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.35rem; color:#9a3412; margin-bottom:1rem; border-bottom:2px solid #fed7aa; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>🌌 Verified Vedic Kundali Alignment</span>
            <span style="font-size:0.85rem; background:#ffedd5; color:#c2410c; padding:4px 10px; border-radius:20px; font-weight:800;">Chitrapaksha Lahiri Ayanamsa</span>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:10px; text-align:center; margin-bottom:1.25rem;">
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('lagna_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{chart_info['lagna_name'].split()[0]}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{chart_info['lagna_deg']}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('nakshatra_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{chart_info['star_name']}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{t('pada_label', current_lang)} {chart_info['pada']}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('moon_rashi_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{chart_info['moon_rashi_name'].split()[0]}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{chart_info['moon_rashi_name'].split()[-1]}</div>
            </div>
        </div>

        <div style="background:#fffaf0; border-radius:14px; padding:14px; border:1.5px solid #fed7aa; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#9a3412; margin-bottom:8px;">
                ⭐ Janma Nakshatra: {chart_info['star_name']} (Pada {chart_info['pada']})
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:8px; margin-bottom:10px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🏛️ Deity:</b> {n_info['deity']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🔱 Symbol:</b> {n_info['symbol']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🌳 Tree:</b> {n_info['tree']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🪐 Lord:</b> {n_info['lord']}</div>
            </div>
            <div style="font-size:0.94rem; line-height:1.65; color:#431407; margin-bottom:8px;">
                <b>Personality Archetype:</b> {n_info['personality']}
            </div>
            <div style="font-size:0.92rem; line-height:1.6; color:#431407; background:#ffffff; padding:10px; border-radius:8px; border-left:4px solid #f97316;">
                <b>🪔 Prescribed Remedies:</b><br>{n_info['remedies']}
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:14px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#065f46; margin-bottom:8px;">
                🌙 Moon Sign: {m_info['name']}
            </div>
            <div style="font-size:0.94rem; line-height:1.65; color:#14532d; margin-bottom:8px;">
                <b>Psychology:</b> {m_info['profile']}
            </div>
            <div style="font-size:0.92rem; line-height:1.6; color:#14532d; background:#ffffff; padding:10px; border-radius:8px; border-left:4px solid #10b981;">
                <b>🪔 Moon Remedies:</b><br>{m_info['remedies']}
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe;">
            <div style="font-weight:900; font-size:1.1rem; color:#5b21b6; margin-bottom:8px;">
                🌅 Ascendant (Lagna): {l_info['name']} at {chart_info['lagna_deg']}
            </div>
            <div style="font-size:0.94rem; line-height:1.65; color:#3b0764; margin-bottom:8px;">
                <b>Physical Constitution:</b> {l_info['profile']}
            </div>
            <div style="font-size:0.92rem; line-height:1.6; color:#3b0764; background:#ffffff; padding:10px; border-radius:8px; border-left:4px solid #8b5cf6;">
                <b>🪔 Lagna Remedies:</b><br>{l_info['remedies']}
            </div>
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

        <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:1.15rem;">
            <div style="background:#ffffff; border-radius:12px; padding:12px; border:1px solid #d1fae5; border-left:5px solid #059669;">
                <b>{num_domains['career_title']}</b><br>
                <span style="font-size:0.94rem; color:#1e293b;">{num_domains['career_desc']}</span>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:12px; border:1px solid #d1fae5; border-left:5px solid #10b981;">
                <b>{num_domains['wealth_title']}</b><br>
                <span style="font-size:0.94rem; color:#1e293b;">{num_domains['wealth_desc']}</span>
            </div>
        </div>
    </div>
    """)

# ==============================================================================
# TAB 4: SHANI
# ==============================================================================
def render_page_shani():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    render_html(f"""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.3rem; color:#5b21b6; margin-bottom:1rem; border-bottom:2px solid #ddd6fe; padding-bottom:0.5rem;">
            <span>{t('shani_paya_title', current_lang)}</span>
        </div>
        
        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #e9d5ff; margin-bottom:1rem;">
            <div style="font-size:1.3rem; font-weight:900; color:#5b21b6;">{shani_paya_data['paya']}</div>
            <div style="font-size:0.95rem; color:#7c3aed; font-weight:800;">Status: {shani_paya_data['status']}</div>
            <div style="font-size:0.92rem; color:#3b0764; margin-top:6px;">{shani_paya_data['desc']}</div>
        </div>
    </div>
    """)

    with st.container(border=True):
        st.markdown("**📿 Digital Japa Mala Counter (108 Beads)**")
        progress_pct = min(1.0, st.session_state.japa_count / 108.0)
        st.progress(progress_pct, text=f"Count: {st.session_state.japa_count} / 108")
        c_tap, c_reset = st.columns([2, 1])
        with c_tap:
            if st.button("📿 Tap (+1)", type="primary", use_container_width=True):
                st.session_state.japa_count = (st.session_state.japa_count % 108) + 1
                st.rerun()
        with c_reset:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.japa_count = 0
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
    
    muh = calculate_daily_muhurtas(now_ist.date(), prof["lat"], prof["lon"])
    abhijit_s, abhijit_e = muh["abhijit"]
    rahu_s, rahu_e = muh["rahu"]
    
    is_abhijit = abhijit_s <= now_ist <= abhijit_e
    is_rahu = rahu_s <= now_ist <= rahu_e

    if is_rahu:
        banner = f"<div style='background:#fee2e2; border:2px solid #ef4444; border-radius:12px; padding:12px; margin-bottom:1rem; color:#991b1b; font-weight:800;'>🛑 Rahu Kaal Active until {rahu_e.strftime('%I:%M %p')}. Avoid signing new contracts.</div>"
    elif is_abhijit:
        banner = f"<div style='background:#dcfce7; border:2px solid #22c55e; border-radius:12px; padding:12px; margin-bottom:1rem; color:#166534; font-weight:800;'>🌟 Abhijit Muhurta Active until {abhijit_e.strftime('%I:%M %p')}. Favorable for all initiatives.</div>"
    else:
        banner = f"<div style='background:#f0fdf4; border:1.5px solid #86efac; border-radius:12px; padding:12px; margin-bottom:1rem; color:#15803d; font-weight:700;'>⏱️ Safe Orbit ({now_ist.strftime('%I:%M %p')} IST). No caution window active.</div>"

    render_html(f"""
    <div class="light-card-live">
        <div style="font-weight:900; font-size:1.25rem; color:#0369a1; margin-bottom:0.75rem; border-bottom:2px solid #bae6fd; padding-bottom:0.5rem;">
            <span>⚡ Today's Live Cosmic Rhythm</span>
        </div>
        {banner}
        <div style="background:#f0f9ff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd;">
            <div style="font-size:1.3rem; font-weight:900; color:#0369a1;">{icon} Navtara: {nav_name}</div>
            <div style="font-size:0.92rem; color:#0284c7; font-weight:700; margin-top:4px;">Current Transit Moon: {NAKSHATRAS[cur_star_idx-1]} ({quality})</div>
            <div style="font-size:0.88rem; color:#475569; margin-top:6px;">Window: {s_dt.strftime('%d %b %I:%M %p')} → {e_dt.strftime('%d %b %I:%M %p IST')}</div>
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

    for idx, tr in enumerate(transits):
        with st.container(border=True):
            c1, c2 = st.columns([2, 3])
            with c1:
                render_html(f"<b>{tr['date_str']}</b><br><span style='color:#64748b;'>{tr['star_name']}</span>")
            with c2:
                render_html(f"{tr['icon']} <b>{tr['nav_name'].split('(')[0]}</b><br><span style='font-size:0.85rem; color:#475569;'>{tr['quality']}</span>")

# ==============================================================================
# ROUTER DISPATCHER
# ==============================================================================
PAGES = {
    "about": render_page_about,
    "profile": render_page_profile,
    "numerology": render_page_numerology,
    "shani": render_page_shani,
    "live": render_page_live,
    "forecast": render_page_forecast,
}

active_page_func = PAGES.get(st.session_state.current_page, render_page_about)
active_page_func()
