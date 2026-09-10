import streamlit as st
import datetime
import urllib.parse
import json
import math

try:
    import swisseph as swe
    HAS_SWISSEPH = True
    swe.set_sid_mode(swe.SIDM_LAHIRI)
except Exception:
    HAS_SWISSEPH = False

try:
    from geopy.geocoders import Nominatim
    HAS_GEOPY = True
except Exception:
    HAS_GEOPY = False

st.set_page_config(
    page_title="Navtara Pulse",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

# STREAMLIT_CHUNK:Styling the layout...
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

# ==============================================================================
# DYNAMIC GEODETIC ATLAS (AUTOMATIC LOCATION LOOKUP FROM NAME)
# ==============================================================================
# STREAMLIT_CHUNK:Defining dynamic geocoder engine...
def get_location_coordinates(place_query: str):
    clean_q = place_query.strip()
    if not clean_q:
        return 28.6139, 77.2090 # Default Delhi
        
    if HAS_GEOPY:
        try:
            geolocator = Nominatim(user_agent="navtara_pulse_astro_app")
            location = geolocator.geocode(clean_q, timeout=4)
            if location:
                return float(location.latitude), float(location.longitude)
        except Exception:
            pass
            
    # Fallback heuristics
    q_low = clean_q.lower()
    if "mumbai" in q_low: return (19.0760, 72.8777)
    if "pune" in q_low: return (18.5204, 73.8567)
    if "delhi" in q_low: return (28.6139, 77.2090)
    if "bengaluru" in q_low or "bangalore" in q_low: return (12.9716, 77.5946)
    if "kolkata" in q_low: return (22.5726, 88.3639)
    if "chennai" in q_low: return (13.0827, 80.2707)
    if "hyderabad" in q_low: return (17.3850, 78.4867)
    if "nashik" in q_low: return (19.9975, 73.7898)
    if "nagpur" in q_low: return (21.1458, 79.0882)
    
    return 28.6139, 77.2090

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
    7: {"en": "Ketu (South Node / केतु)", "hi": "केतु (Ketu)", "mr": "केतू (Ketu)", "gu": "કેતુ (Ketu)"},
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
        "city_label": "Birth Place / Town / City",
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
        "city_label": "जन्म स्थान (शहर / गाँव)",
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
        "city_label": "जन्म ठिकाण (शहर)",
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
# ENCYCLOPEDIA (ALL 27 NAKSHATRAS)
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

NAKSHATRA_PROFILES = {
    1: ("Swift, dynamic initiator with pioneering healing instinct and executive courage.", "Cycles of rapid expansion followed by foundational testing; mature years bring institutional renown.", "• Chant Om Ashwibhyam Namah 11 times.\n• Donate barley or whole grains on Tuesdays.\n• Water a Strychnine (Kuchila) tree."),
    2: ("Enduring moral resilience, magnetic presence, and unyielding principles under intense pressure.", "Evolution through restructuring into creative authority and permanent asset mastery.", "• Recite Maha Mrityunjaya Mantra 11 times daily.\n• Water an Amla tree.\n• Feed stray dogs or crows on Tuesdays/Fridays."),
    3: ("Sharp intellect, transformative penetrating focus, and uncompromising truth-seeking nature.", "Command in technical, analytical, or executive leadership after early disciplined labor.", "• Offer red flowers to Surya Dev.\n• Water a Cluster Fig (Gular) tree.\n• Donate copper or jaggery on Sundays."),
    4: ("Artistic grace, magnetic charm, persistent material focus, and deep emotional sensitivity.", "Continuous compounding of tangible assets, creative triumph, and domestic fulfillment.", "• Offer raw milk on a Shiva Lingam on Mondays.\n• Water a Jamun tree.\n• Drink water from a silver cup."),
    5: ("Perpetual inquisitiveness, versatile mental agility, and keen aesthetic perception.", "Pioneering discoveries, communicative influence, and steady expansion across mid-career.", "• Chant Om Somaya Namah 11 times.\n• Water an Acacia Catechu (Khair) tree.\n• Donate green lentils or clothing on Wednesdays."),
    6: ("Transformative emotional depth, storm-like intellect, and resilience through crises.", "Major restructuring phases that unlock supreme spiritual insight and executive authority.", "• Chant Om Namah Shivaya 108 times.\n• Water an Agarwood tree.\n• Feed stray animals on Saturdays."),
    7: ("Philosophical wisdom, generous benevolence, and remarkable powers of renewal.", "Gradual compounding of respect, educational prestige, and ancestral prosperity.", "• Chant Om Brihaspataye Namah 19 times.\n• Water a sacred Bamboo tree.\n• Donate yellow chickpeas on Thursdays."),
    8: ("Nourishing discipline, enduring patience, and unwavering institutional integrity.", "Enduring respect, organizational sovereignty, and profound generational stability.", "• Water a sacred Peepal tree on Saturdays.\n• Chant Shani Beej Mantra 21 times.\n• Feed crows with mustard-oil roti."),
    9: ("Deep philosophical intuition, hypnotic mental acuity, and tactical cunning.", "Mastery over complex human systems, competitive triumph, and spiritual awakening.", "• Offer milk and water to Lord Shiva on Mondays.\n• Water a Nagkeshar tree.\n• Refrain from deceitful speech."),
    10: ("Regal dignity, ancestral lineage pride, and natural executive authority.", "Leadership in established organizations, ancestral blessings, and legacy assets.", "• Perform Pitru Tarpana or offer water to ancestors.\n• Water a Banyan (Bargad) tree.\n• Donate sesame on Amavasya."),
    11: ("Charismatic magnetism, refined taste in arts, and relentless pursuit of fortune.", "Harmonious material luxury, social prominence, and enduring partnership success.", "• Chant Om Shukraya Namah 16 times on Fridays.\n• Water a Palasa tree.\n• Donate white sweets to the needy."),
    12: ("Steadfast nobility, chivalric honor, and devotion to truth and societal contracts.", "Institutional governance, executive stability, and public honoring in mature years.", "• Offer water mixed with kumkum to morning Sun.\n• Water a Plaksha tree.\n• Feed bulls or red cows on Sundays."),
    13: ("Resourceful dexterity, sharp commercial acumen, and meticulous craftsmanship.", "Success in commercial enterprises, analytical professions, and sudden breakthroughs.", "• Chant Gayatri Mantra 24 times daily.\n• Water a Chameli (Jasmine) plant.\n• Respect mother figures and clean speech."),
    14: ("Architectural genius, vibrant charisma, and eye for sparkling aesthetic mastery.", "High recognition in design, engineering, or strategic infrastructure projects.", "• Recite Hanuman Chalisa on Tuesdays.\n• Water a Bilva (Bael) tree.\n• Keep a bright red handkerchief in pocket."),
    15: ("Dynamic adaptability, independent freedom-loving spirit, and subtle diplomatic skill.", "Rapid expansion in trade, cross-border ventures, and broad social networks.", "• Chant Rahu Beej Mantra 18 times at twilight.\n• Water an Arjuna tree.\n• Donate black blankets on Saturdays."),
    16: ("Intense goal focus, dual energies of alliance and fire, and unstoppable ambition.", "Pinnacle triumph over competitors and steady acquisition of commanding roles.", "• Chant Om Indragni Namah 11 times.\n• Water a Kaith (Wood Apple) tree.\n• Avoid interpersonal ego disputes."),
    17: ("Diplomatic loyalty, devotional warmth, and unshakeable alliance-building grace.", "Lifelong cordial alliances, international travel, and graceful mature prosperity.", "• Light a mustard oil lamp beneath Peepal on Saturday.\n• Water a Bakula tree.\n• Cultivate truthful friendships."),
    18: ("Commanding sovereignty, protective courage, and senior administrative stature.", "Executive supremacy, stewardship of large teams, and triumph in civic arenas.", "• Chant Vishnu Sahasranama on Wednesdays.\n• Water a Silk Cotton (Semal) tree.\n• Practice humble listening with subordinates."),
    19: ("Root-seeking inquiry, profound disillusionment with pretense, and transformative grit.", "Complete rebirth after early trials leading to profound self-mastery and wisdom.", "• Chant Om Ketave Namah 17 times at night.\n• Water a Sal tree.\n• Donate brown blankets or multi-color cloth."),
    20: ("Invincible optimism, emotional purity, and unstoppable perseverance toward victory.", "Creative mastery, celebrated public accomplishments, and enduring liquid wealth.", "• Chant Shri Suktam on Friday mornings.\n• Water an Ashoka tree.\n• Donate pure cow ghee to a temple."),
    21: ("Universal integrity, quiet dignity, and adherence to permanent cosmic laws.", "Gradual, unshakeable ascent to senior leadership and widespread societal trust.", "• Offer water in copper vessel to Aditya Hridaya Stotra.\n• Water a Jackfruit tree.\n• Honor elder mentors."),
    22: ("Scholarly listening acumen, preservation of tradition, and profound learning capacity.", "High educational distinction, public counsel roles, and spiritual tranquility.", "• Chant Om Namo Bhagavate Vasudevaya 108 times.\n• Water an Aak (Calotropis) plant.\n• Maintain strict truthfulness."),
    23: ("Elemental rhythm, musical or martial agility, and monumental resource mobilization.", "Wealth compounding, leadership in competitive sectors, and material victory.", "• Recite Kartikeya or Hanuman Stotra on Tuesdays.\n• Water a Shami tree.\n• Feed whole wheat dough to birds/animals."),
    24: ("Esoteric scientific curiosity, investigative mastery, and veil-piercing intuition.", "Breakthroughs in research, medical or technological systems, and hidden gains.", "• Chant Om Varunaya Namah 11 times.\n• Water a Kadamba tree.\n• Keep a pure silver square piece in wallet."),
    25: ("Fiery ascetic determination, visionary reformist drive, and immense mental force.", "Transformative executive authority and stewardship of radical breakthroughs.", "• Chant Rudra Gayatri Mantra 11 times.\n• Water a Neem or Mango tree.\n• Practice fasting or clean eating on Thursdays."),
    26: ("Serpentine wisdom of cosmic depths, calm benevolence, and meditative stamina.", "Unassailable peace, philosophical guidance, and solid generational wealth.", "• Chant Om Namah Shivaya 108 times facing East.\n• Water a Neem tree.\n• Feed black cows with green fodder on Saturdays."),
    27: ("Nourishing grace, safe guidance of journeys, and serene artistic completion.", "Prosperity in distant ventures, universal goodwill, and peaceful mature fulfillment.", "• Chant Budha Beej Mantra 19 times.\n• Water a Mahua tree.\n• Donate green fruits or educational books to children.")
}

def get_nakshatra_traits(star_idx: int, lang: str = "en") -> dict:
    bio = NAKSHATRA_BIO_DATA.get(star_idx, NAKSHATRA_BIO_DATA[2])
    p_archetype, p_pred, p_rem = NAKSHATRA_PROFILES.get(star_idx, NAKSHATRA_PROFILES[2])
    return {
        "deity": bio["deity"],
        "symbol": bio["symbol"],
        "tree": bio["tree"],
        "bird": bio["bird"],
        "animal": bio["animal"],
        "lord": bio["lord"],
        "personality": p_archetype,
        "prediction": p_pred,
        "remedies": p_rem
    }

RASHI_DETAILED_INFO = {
    0: ("Fire (Agni)", "Mars (Mangal)", "Dynamic pioneering engine, fearless initiative, and rapid intuitive decision-making reflexes.", "Command in competitive fields, technical systems, and executive roles; practice tactical calm to harness mental fire.", "• Offer water with red sandalwood to Surya Dev.\n• Recite Hanuman Chalisa on Tuesdays.\n• Drink water from a silver vessel to cool lunar impulses."),
    1: ("Earth (Prithvi)", "Venus (Shukra)", "Deliberate stability, refined aesthetic perception, immense perseverance, and strong financial pragmatism.", "Compounding tangible assets, real estate mastery, and comfortable executive longevity.", "• Recite Shri Suktam on Fridays.\n• Apply natural sandalwood attar.\n• Donate curd or white sweets on Fridays."),
    2: ("Air (Vayu)", "Mercury (Budha)", "Versatile communicative agility, multi-channel intellect, and razor-sharp analytical curiosity.", "Success in media, technology, commerce, and advisory domains through strategic versatility.", "• Chant Vishnu Sahasranama on Wednesdays.\n• Water a Tulsi plant daily.\n• Feed green fodder to cows."),
    3: ("Water (Jala)", "Moon (Chandra)", "Profound emotional empathy, protective loyalty, intuitive antennae, and rhythmic tenacity.", "Command over institutions, public leadership, and wealth accumulation through emotional intelligence.", "• Offer raw milk on Shiva Lingam on Mondays.\n• Respect mother figures.\n• Drink water from a silver cup."),
    4: ("Fire (Agni)", "Sun (Surya)", "Regal presence, natural sovereignty, magnanimous leadership, and uncompromising self-respect.", "Senior executive positions, administrative authority, and high societal distinction.", "• Recite Aditya Hridaya Stotra at sunrise.\n• Offer water in copper vessel to Sun.\n• Honor father figures and elders."),
    5: ("Earth (Prithvi)", "Mercury (Budha)", "Precision discernment, analytical rigor, structured problem-solving, and clean service ethics.", "Mastery over complex systems, organizational architecture, and financial auditing.", "• Chant Budha Beej Mantra on Wednesdays.\n• Donate green stationery or books to students.\n• Practice 10 minutes of daily mindfulness."),
    6: ("Air (Vayu)", "Venus (Shukra)", "Diplomatic equilibrium, refined justice, architectural balance, and partnership brilliance.", "Success in legal, negotiation, luxury commodities, and institutional governance.", "• Worship Goddess Lakshmi on Fridays.\n• Wear clean pressed pastel attire.\n• Maintain strict fairness in business agreements."),
    7: ("Water (Jala)", "Mars (Mangal)", "Penetrating investigative acumen, intense psychological depth, and unyielding transformative grit.", "Command over strategic operations, crisis management, and private compounding wealth.", "• Chant Kartikeya or Shiva Mantras on Tuesdays.\n• Donate jaggery and roasted chickpeas.\n• Guard against vengeful thoughts."),
    8: ("Fire (Agni)", "Jupiter (Guru)", "Expansive philosophical vision, legal and moral integrity, and inspiring pedagogical leadership.", "High institutional mentorship, cross-border ventures, and enduring reputational prestige.", "• Chant Guru Mantra on Thursdays.\n• Apply turmeric or yellow sandalwood tilak on forehead.\n• Water a Peepal tree without touching on Thursdays."),
    9: ("Earth (Prithvi)", "Saturn (Shani)", "Enduring tactical patience, monumental organizational grit, and structured pragmatic climbing.", "Sovereign institutional leadership, permanent asset foundations, and lasting mature authority.", "• Light mustard oil lamp under Peepal on Saturday.\n• Recite Hanuman Chalisa daily.\n• Respect and tip blue-collar workers."),
    10: ("Air (Vayu)", "Saturn (Shani)", "Universal visionary ideals, scientific detachment, systems reformation, and egalitarian ethics.", "Pioneering technological breakthroughs, social architecture, and non-linear prosperity.", "• Chant Shani Gayatri Mantra on Saturdays.\n• Donate black sesame or oil.\n• Keep electronic workspaces free of tangled cables."),
    11: ("Water (Jala)", "Jupiter (Guru)", "Oceanic subconscious intuition, compassionate wisdom, creative transcendence, and spiritual resonance.", "Success in counseling, foreign realms, creative arts, and profound inner peace.", "• Chant Om Namo Bhagavate Vasudevaya on Thursdays.\n• Feed fish with wheat dough on Thursdays.\n• Meditate for 15 minutes at twilight.")
}

def get_moon_rashi_details(rashi_idx: int, lang: str = "en") -> dict:
    elem, ruler, prof, pred, rem = RASHI_DETAILED_INFO.get(rashi_idx, RASHI_DETAILED_INFO[0])
    return {
        "name": RASHIS[rashi_idx],
        "element": elem,
        "ruler": ruler,
        "profile": prof,
        "prediction": pred,
        "remedies": rem
    }

LAGNA_DETAILED_INFO = {
    0: ("Fire (Agni)", "Mars (Mangal)", "Dynamic pioneering demeanor, physical courage, athletic constitution, and direct executive approach.", "Life trajectory driven by bold enterprise, technical leadership, and direct self-assertive victory.", "• Offer water with red sandalwood to Surya Dev.\n• Recite Hanuman Chalisa.\n• Maintain regular physical training."),
    1: ("Earth (Prithvi)", "Venus (Shukra)", "Calm poise, solid physical constitution, refined aesthetic voice, and unshakeable perseverance.", "Compound worldly assets, real estate mastery, and enduring administrative respect.", "• Apply pure white sandalwood paste.\n• Recite Shri Suktam on Fridays.\n• Respect women and keep clean surroundings."),
    2: ("Air (Vayu)", "Mercury (Budha)", "Expressive agility, youthful communicative demeanor, adaptable intellect, and versatile presence.", "Intellectual distinction, multi-disciplinary advisory roles, and dynamic commercial growth.", "• Chant Vishnu Sahasranama on Wednesdays.\n• Water a Tulsi plant.\n• Practice measured, clear speech."),
    3: ("Water (Jala)", "Moon (Chandra)", "Receptive intuitive countenance, nurturing presence, emotional depth, and responsive reflexes.", "Command over public affairs, institutional welfare, and enduring generational wealth.", "• Offer clean water to a Shiva Lingam on Mondays.\n• Respect maternal elders.\n• Drink water from a pure silver cup."),
    4: ("Fire (Agni)", "Sun (Surya)", "Commanding presence, royal posture, radiant vitality, and natural executive dignity.", "Administrative authority, prominent public standing, and honor in high governance.", "• Perform Surya Namaskar at sunrise.\n• Offer water in a copper vessel to Sun.\n• Cultivate magnanimity in leadership."),
    5: ("Earth (Prithvi)", "Mercury (Budha)", "Analytical precision, clean structured carriage, meticulous eye for detail, and discerning mind.", "Mastery over complex systems, organizational architecture, and financial integrity.", "• Chant Budha Beej Mantra on Wednesdays.\n• Maintain a clean workspace.\n• Practice evening pranayama."),
    6: ("Air (Vayu)", "Venus (Shukra)", "Harmonious facial symmetry, diplomatic composure, refined social grace, and balanced presence.", "Success in arbitration, diplomatic leadership, legal distinction, and luxury trade.", "• Worship Goddess Lakshmi on Fridays.\n• Apply natural rose attar.\n• Practice absolute balance in commitments."),
    7: ("Water (Jala)", "Mars (Mangal)", "Penetrating gaze, magnetic mysterious reserve, immense psychological stamina, and quiet resolve.", "Stewardship of crisis operations, strategic research, and transformative wealth building.", "• Recite Kartikeya or Hanuman Chalisa.\n• Practice honest transparency in speech.\n• Engage in rigorous physical discipline."),
    8: ("Fire (Agni)", "Jupiter (Guru)", "Tall visionary posture, benevolent optimism, scholarly presence, and philosophical demeanor.", "Senior advisory stature, legal and ethical stewardship, and public veneration.", "• Apply yellow sandalwood tilak on forehead.\n• Chant Guru Mantra on Thursdays.\n• Support educational causes."),
    9: ("Earth (Prithvi)", "Saturn (Shani)", "Sober pragmatic presence, austere self-discipline, steady constitutional stamina, and mature dignity.", "Permanent institutional foundations, administrative sovereignty, and compound authority.", "• Light a mustard oil lamp under Peepal on Saturdays.\n• Treat blue-collar workers with respect.\n• Maintain patient long-term planning."),
    10: ("Air (Vayu)", "Saturn (Shani)", "Independent cerebral poise, progressive visionary presence, and egalitarian demeanor.", "Pioneering technological breakthroughs, social systems reform, and original enterprise.", "• Chant Shani Gayatri Mantra on Saturdays.\n• Keep workspace uncluttered.\n• Donate to humanitarian causes."),
    11: ("Water (Jala)", "Jupiter (Guru)", "Gentle compassionate gaze, intuitive artistic sensibility, philosophical calm, and serene presence.", "Spiritual tranquility, cross-border achievements, creative distinction, and mature peace.", "• Chant Om Namo Bhagavate Vasudevaya on Thursdays.\n• Practice 15 minutes of quiet meditation.\n• Feed fish with whole wheat dough.")
}

def get_lagna_details(lagna_idx: int, lang: str = "en") -> dict:
    elem, lord, prof, pred, rem = LAGNA_DETAILED_INFO.get(lagna_idx, LAGNA_DETAILED_INFO[6])
    return {
        "name": RASHIS[lagna_idx],
        "element": elem,
        "lord": lord,
        "profile": prof,
        "prediction": pred,
        "remedies": rem
    }

# ==============================================================================
# TARA BALA COMPATIBILITY ENGINE
# ==============================================================================
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
        advice = "Differences in communication tempo or expectations can trigger misunderstandings. Ensure all commitments are formally written and expectations calibrated."
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

# ==============================================================================
# NUMEROLOGY & GEODESICS
# ==============================================================================
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
        "career_desc": f"The dynamic synthesis of Driver {mulank} ({p_m}) and Conductor {bhagyank} ({p_b}) creates an unstoppable powerhouse combination of strategic vision and courageous execution. You are naturally engineered for leadership, structural problem solving, and projects where you hold autonomy over key decisions.",
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
# RIGOROUS ASTRONOMICAL ENGINE
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
# USER PROFILE STORAGE MANAGEMENT (STRICT BLANK INITIALIZATION)
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
                if data.get("name") in ["Okesh", "User"]:
                    return blank_profile
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
    dob_parsed, tob_parsed, chart_info = None, None, None
    mulank, bhagyank, namank = None, None, None
    shani_paya_data, shani_sadesati_data = None, None

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
            🧬 Classical Sidereal Vedic Engine (Lahiri Ayanamsa)
        </div>
        <div style="font-size:0.96rem; line-height:1.75; color:#451a03; margin-bottom:0.8rem;">
            <b>Astronomical Precision & Kundali Alignment:</b><br>
            Navtara Pulse derives Local Sidereal Time (RAMC) and topocentric planetary horizons using true geographical coordinates and Swiss Ephemeris tables. All calculations—including Janma Nakshatra, Lagna, and Shani Sade Sati—dynamically compute from your exact birth profile.
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

            in_city_input = st.text_input(
                t("city_label", current_lang),
                value=prof.get("city", ""),
                placeholder="e.g. Delhi, Mumbai, Satara, London"
            )
            
            c_save, c_canc = st.columns([2, 1])
            with c_save:
                submitted = st.form_submit_button("✨ Save & Calculate Profile", type="primary", use_container_width=True)
            with c_canc:
                canceled = st.form_submit_button("Cancel", use_container_width=True)

            if submitted:
                if not new_name.strip():
                    st.error("Please provide your full name.")
                elif not in_city_input.strip():
                    st.error("Please provide your birth city or location.")
                else:
                    hr_24 = in_hour % 12
                    if in_ampm == "PM":
                        hr_24 += 12
                    final_tob_str = f"{hr_24:02d}:{in_minute:02d}"

                    resolved_lat, resolved_lon = get_location_coordinates(in_city_input)

                    st.session_state.user_profile.update({
                        "name": new_name.strip(),
                        "dob": new_dob.strftime("%Y-%m-%d"),
                        "tob": final_tob_str,
                        "city": in_city_input.strip(),
                        "lat": resolved_lat,
                        "lon": resolved_lon
                    })
                    save_user_profile(st.session_state.user_profile)
                    st.session_state.edit_mode = False
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
                <b>Core Archetype:</b> {n_info['personality']}
            </div>
            <div style="font-size:0.94rem; line-height:1.65; color:#431407; margin-bottom:8px;">
                <b>Life Trajectory:</b> {n_info['prediction']}
            </div>
            <div style="background:#ffffff; border-radius:8px; padding:10px; border-left:4px solid #f97316; font-size:0.92rem; color:#431407;">
                <b>🪔 Prescribed Remedies:</b><br>{n_info['remedies']}
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:14px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#065f46; margin-bottom:8px;">
                🌙 Moon Sign: {m_info['name']}
            </div>
            <div style="font-size:0.94rem; line-height:1.65; color:#14532d; margin-bottom:8px;">
                <b>Emotional Mindset:</b> {m_info['profile']}
            </div>
            <div style="font-size:0.94rem; line-height:1.65; color:#14532d; margin-bottom:8px;">
                <b>Strategic Outlook:</b> {m_info['prediction']}
            </div>
            <div style="background:#ffffff; border-radius:8px; padding:10px; border-left:4px solid #10b981; font-size:0.92rem; color:#14532d;">
                <b>🪔 Moon Remedies:</b><br>{m_info['remedies']}
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#5b21b6; margin-bottom:8px;">
                🌅 Ascendant (Lagna): {l_info['name']} at {chart_info['lagna_deg']}
            </div>
            <div style="font-size:0.94rem; line-height:1.65; color:#3b0764; margin-bottom:8px;">
                <b>Physical Constitution:</b> {l_info['profile']}
            </div>
            <div style="font-size:0.94rem; line-height:1.65; color:#3b0764; margin-bottom:8px;">
                <b>Executive Direction:</b> {l_info['prediction']}
            </div>
            <div style="background:#ffffff; border-radius:8px; padding:10px; border-left:4px solid #8b5cf6; font-size:0.92rem; color:#3b0764;">
                <b>🪔 Lagna Remedies:</b><br>{l_info['remedies']}
            </div>
        </div>

        <!-- SUBSECTION D: NAKSHATRA SOCIAL & BUSINESS SYNERGY MATRIX (TARA BALA) -->
        <div style="background:#ffffff; border-radius:14px; padding:14px; border:1.5px solid #fed7aa;">
            <div style="font-weight:900; font-size:1.1rem; color:#9a3412; margin-bottom:8px; border-bottom:1px solid #ffedd5; padding-bottom:4px;">
                🤝 Nakshatra Synergy & Compatibility Evaluator (Tara Bala)
            </div>
            <div style="font-size:0.92rem; color:#475569; margin-bottom:10px;">
                Select any colleague, business partner, or family member's Janma Nakshatra to evaluate mutual cosmic resonance:
            </div>
    """)

    partner_star_choice = st.selectbox(
        "Select Counterpart's Birth Star:",
        options=NAKSHATRAS,
        index=0,
        key="profile_partner_star_choice"
    )
    p_star_idx = NAKSHATRAS.index(partner_star_choice) + 1
    tara_res = get_tara_bala_info(chart_info['star_idx'], p_star_idx)

    bg_color = '#f0fdf4' if tara_res['is_allied'] else ('#fff1f2' if tara_res['is_friction'] else '#f8fafc')
    border_color = '#86efac' if tara_res['is_allied'] else ('#fecdd3' if tara_res['is_friction'] else '#e2e8f0')
    text_color = '#15803d' if tara_res['is_allied'] else ('#be123c' if tara_res['is_friction'] else '#0f172a')

    render_html(f"""
            <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:10px; padding:12px; margin-top:8px;">
                <div style="font-size:1.05rem; font-weight:800; color:{text_color};">
                    {tara_res['icon']} {tara_res['tara_name']} — {tara_res['quality']}
                </div>
                <div style="font-size:0.92rem; font-weight:700; color:#334155; margin-top:4px;">
                    Dynamic: {tara_res['relationship_tone']}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.5;">
                    {tara_res['advice']}
                </div>
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
    </div>
    """)


# ==============================================================================
# TAB 4: SHANI (DYNAMIC SADE SATI ENGINE BASED ON USER MOON SIGN)
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
        <div style="font-weight:900; font-size:1.3rem; color:#5b21b6; margin-bottom:1rem; border-bottom:2px solid #ddd6fe; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{t('shani_paya_title', current_lang)}</span>
            <span style="font-size:0.85rem; background:#ede9fe; color:#5b21b6; padding:4px 10px; border-radius:20px; font-weight:800;">Saturn in Pisces (Meena)</span>
        </div>
        
        <!-- DYNAMIC SHANI PAYA -->
        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #e9d5ff; margin-bottom:1.15rem;">
            <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">ACTIVE TRANSIT PAYA FOR YOUR {m_name.upper()} MOON</div>
            <div style="font-size:1.4rem; font-weight:900; color:#5b21b6; margin:4px 0;">{shani_paya_data['paya']}</div>
            <div style="font-size:0.95rem; color:#7c3aed; font-weight:800;">Status: {shani_paya_data['status']}</div>
            <div style="font-size:0.92rem; color:#475569; margin-top:3px;"><b>Active Timeline:</b> {shani_paya_data['timeline']}</div>
            <div style="font-size:0.95rem; line-height:1.7; color:#3b0764; margin-top:10px;">
                {shani_paya_data['desc']}
            </div>
        </div>

        <!-- DYNAMIC SADE SATI / DHAIYA STATUS -->
        <div style="background:#ffffff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:10px; border-bottom:1px solid #e9d5ff; padding-bottom:5px; display:flex; justify-content:space-between; align-items:center;">
                <span>⚖️ Sade Sati Status for {m_name} Moon</span>
                <span style="font-size:0.82rem; background:#ede9fe; color:#5b21b6; padding:3px 8px; border-radius:10px; font-weight:800;">{shani_sadesati_data['status_title'].split(':')[0]}</span>
            </div>
            
            <div style="background:{'#fef2f2' if shani_sadesati_data['phase_2_active'] else '#f5f3ff'}; border-radius:12px; padding:12px; border-left:5px solid {'#ef4444' if shani_sadesati_data['phase_2_active'] else '#9333ea'}; margin-bottom:12px;">
                <b style="color:{'#991b1b' if shani_sadesati_data['phase_2_active'] else '#5b21b6'}; font-size:1.05rem;">{shani_sadesati_data['status_title']}</b>
                <div style="font-size:0.9rem; color:#64748b; margin:2px 0 6px 0;"><b>Active Window:</b> {shani_sadesati_data['dates']}</div>
                <div style="font-size:0.94rem; line-height:1.65; color:#334155;">{shani_sadesati_data['impact']}</div>
            </div>

            <!-- DYNAMIC 3-PHASE ROADMAP TAILORED TO USER MOON SIGN -->
            <div style="font-weight:800; font-size:1rem; color:#475569; margin:14px 0 8px 0;">Complete 7.5-Year Sade Sati Trajectory for Your {m_name} Moon:</div>

            <div style="background:#faf5ff; border-radius:10px; padding:10px 12px; border-left:4px solid #a855f7; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#5b21b6;">Phase 1: Rising Phase (Saturn in {shani_sadesati_data['rashi_12th']} / 12th from Moon)</b>
                    {p1_active_tag}
                </div>
                <div style="font-size:0.88rem; color:#475569; margin-top:2px;">Restructuring subconscious habits, remote assignments, and elimination of unnecessary expenses.</div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:10px 12px; border-left:4px solid #ef4444; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#991b1b;">Phase 2: Peak Janma Shani (Saturn in {shani_sadesati_data['rashi_1st']} / Over Natal Moon)</b>
                    {p2_active_tag}
                </div>
                <div style="font-size:0.88rem; color:#475569; margin-top:2px;">Crucible of executive endurance, major life transformations, physical stamina, and spiritual maturity.</div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:10px 12px; border-left:4px solid #10b981;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#065f46;">Phase 3: Setting Phase (Saturn in {shani_sadesati_data['rashi_2nd']} / 2nd from Moon)</b>
                    {p3_active_tag}
                </div>
                <div style="font-size:0.88rem; color:#475569; margin-top:2px;">Consolidation of accumulated lessons, stabilization of speech and domestic finances, and permanent asset building.</div>
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe;">
            <div style="font-weight:900; font-size:1.05rem; color:#5b21b6; margin-bottom:6px;">🪔 Prescribed Remedies for Shani Alignment:</div>
            <div style="font-size:0.93rem; line-height:1.65; color:#3b0764;">
                • Chant the <b>Shani Beej Mantra</b> (<i>ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः</i>) 108 times on Saturday twilight facing West.<br>
                • Recite the <b>Hanuman Chalisa</b> daily to channel inner vitality and protect emotional equilibrium.<br>
                • Donate mustard oil, black sesame seeds, or blue cloth to laborers or the needy on Saturdays.
            </div>
        </div>
    </div>
    """)

    with st.container(border=True):
        st.markdown("**📿 Interactive Digital Japa Mala Counter (108 Beads)**")
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
            <div style="font-size:1.3rem; font-weight:900; color:#0369a1;">{icon} Navtara: {nav_name}</div>
            <div style="font-size:0.92rem; color:#0284c7; font-weight:700; margin-top:4px;">Current Transit Moon: {NAKSHATRAS[cur_star_idx-1]} ({quality})</div>
            <div style="font-size:0.88rem; color:#475569; margin-top:6px;">Window: {s_dt.strftime('%d %b %I:%M %p')} → {e_dt.strftime('%d %b %I:%M %p IST')}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <b>⏱️ Timing Windows for Today ({prof['city']}):</b><br>
            • 🌟 <b>Abhijit Muhurta:</b> {abhijit_s.strftime('%I:%M %p')} – {abhijit_e.strftime('%I:%M %p IST')} (Golden Window)<br>
            • ⚠️ <b>Rahu Kaal:</b> {rahu_s.strftime('%I:%M %p')} – {rahu_e.strftime('%I:%M %p IST')} (Avoid Signings)
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

    # 7-Day Visual Heatmap
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
    </div>
    """)


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
