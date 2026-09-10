import streamlit as st
import datetime
import urllib.parse
import json
import os
import math

# Initialize Swiss Ephemeris engine with sidereal Lahiri configuration
try:
    import swisseph as swe
    HAS_SWISSEPH = True
    swe.set_sid_mode(swe.SIDM_LAHIRI)
except Exception:
    HAS_SWISSEPH = False

# Configure Streamlit page layout and viewport settings
st.set_page_config(
    page_title="Navtara Pulse",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Helper function to inject clean, responsive HTML without markdown code-block wrapping
def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

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
            padding-top: 0.9rem !important;
            padding-bottom: 5.5rem !important;
        }
    }
    
    .block-container {
        padding-top: 1.1rem;
        padding-bottom: 5.5rem;
        padding-left: 0.85rem;
        padding-right: 0.85rem;
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

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]
NAKHATRAS = NAKSHATRAS  # Robust backward-compatible alias

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
    ("Ati-Mitra (Supreme Alliance)", "🟢🟢", "Supreme Synergy & Deep Expansion")
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
        "city_label": "Birth City",
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
    
    star_details = {
        2: {
            "personality": {
                "en": "Governed by Lord Yama (Dharma, Truth, Cosmic Justice) and Venus (Shukra), you possess an unyielding inner moral compass, monumental resilience, and profound charismatic magnetism. You bear heavy responsibilities with quiet elegance. You do not compromise on principles and possess an innate capacity to withstand life's crucible transformations, turning challenges into stepping stones.",
                "hi": "धर्मराज यम और शुक्र के संयुक्त प्रभाव से आप असाधारण सत्यनिष्ठा, असीम मानसिक सहनशीलता और गहरे चुंबकीय व्यक्तित्व के धनी हैं। भारी से भारी संकट या उत्तरदायित्व को आप शांत भाव से वहन करते हैं। सिद्धांतों पर कभी समझौता नहीं करते और जीवन के कठिन संघर्षों को पार कर अभूतपूर्व सफलता प्राप्त करते हैं।",
                "mr": "धर्मराज यम आणि शुक्र यांच्या प्रभावामुळे तुमच्यात अफाट सहनशक्ती, तत्त्वनिष्ठा आणि नैसर्गिक प्रभावी व्यक्तिमत्व आहे. कितीही मोठे संकट किंवा जबाबदारी शांतपणे पेलणे हे तुमचे वैशिष्ट्य आहे. तत्वांवर तडजोड न करता कठीण प्रसंगांवर मात करून शिखरावर पोहोचण्याची तुमची क्षमता आहे.",
                "gu": "યમરાજ અને શુક્રના આશીર્વાદથી તમારામાં અદ્વિતીય સહનશક્તિ, સિદ્ધાંતપ્રિયતા અને આકર્ષક પ્રભાવ છે. ગમે તેવી મોટી મુશ્કેલી કે જવાબદારી પણ તમે શાંતિથી નિભાવી શકો છો. જીવનમાં સિદ્ધાંતો સાથે અડગ રહીને પ્રચંડ સફળતા મેળવો છો."
            },
            "prediction": {
                "en": "Your life path moves through powerful cycles of restructuring followed by enduring creative authority. Mid-career brings command over resources, high institutional trust, and executive leadership. While emotional intensity can trigger internal friction, your mature years bestow solid financial stability, ancestral blessings, and lasting respect.",
                "hi": "आपका जीवन चक्र गहन संरचनात्मक बदलावों के बाद स्थाई प्रतिष्ठा और समृद्धि की ओर अग्रसर रहता है। मध्य आयु में आपको महत्वपूर्ण संसाधन, उच्च प्रबंधकीय नियंत्रण और सामाजिक विश्वास प्राप्त होता है। भावुकता पर संयम रखने से जीवन में अकूत वित्तीय स्थिरता और मान-सम्मान की प्राप्ति होती है।",
                "mr": "तुमचा जीवनप्रवास मोठ्या स्थित्यंतरांनंतर स्थिर आणि सन्माननीय यशाकडे नेणारा आहे. आयुष्याच्या मध्यावर मोठी सत्ता, आर्थिक स्वावलंबन आणि प्रशासकीय नेतृत्व लाभेल. भावनांवर नियंत्रण ठेवल्यास दीर्घकालीन आर्थिक स्थैर्य व सामाजिक प्रतिष्ठा प्राप्त होईल.",
                "gu": "તમારો જીવનપથ મોટા પરિવર્તનો પછી સ્થિર અને સર્વોચ્ચ પ્રતિષ્ઠા તરફ આગળ વધે છે. જીવનના મધ્યભાગમાં પ્રભાવશાળી સત્તા, અધિકાર અને આર્થિક સમૃદ્ધિ પ્રાપ્ત થાય છે."
            },
            "remedies": {
                "en": "• Recite the **Maha Mrityunjaya Mantra** or **Om Hreem Bharanyai Namah** 11 times every morning.\n• Worship Lord Shiva or Lord Yama to harmonize vital life energy (*Prana*) and neutralize ancestral debts.\n• Nurture and water an **Amla (Indian Gooseberry)** tree, and avoid wearing torn black clothing.\n• Feed stray dogs or crows on Tuesdays and Fridays to balance karmic weight.",
                "hi": "• प्रतिदिन प्रातः **महामृत्युंजय मंत्र** अथवा **ॐ ह्रीं भरण्यै नमः** का 11 बार जप करें।\n• भगवान शिव को कच्चा दूध और जल अर्पित करें जिससे जीवन ऊर्जा संतुलित रहे।\n• **आँवले (Amla)** के वृक्ष का रोपण अथवा नियमित सिंचन करें।\n• मंगलवार और शुक्रवार को काले श्वान अथवा कौवों को भोजन कराएं।",
                "mr": "• दररोज सकाळी **महामृत्युंजय मंत्र** किंवा **ॐ ह्रीं भरण्यै नमः** चा ११ वेळा जप करावा.\n• महादेवाला जल व दूध अर्पण करून प्राणऊर्जा संतुलित ठेवावी.\n• **आवळा (Amla)** वृक्षाचे जतन व जलार्पण करावे.\n• मंगळवार आणि शुक्रवारी मुक्या प्राण्यांना वा कावळ्यांना अन्न द्यावे.",
                "gu": "• દરરોજ સવારે **મહામૃત્યુંજય મંત્ર** અથવા **ૐ હ્રીં ભરણ્યૈ નમઃ** નો ૧૧ વાર જાપ કરો.\n• ભગવાન શિવને કાચું દૂધ અને જળ અર્પણ કરો.\n• **આમળાના વૃક્ષ** નું જતન કરો અને પાણી ચડાવો.\n• મંગળવાર અને શુક્રવારે કૂતરા કે પક્ષીઓને ખોરાક આપો."
            }
        }
    }
    
    fallback_text = {
        "personality": {
            "en": f"Born under the celestial star {NAKSHATRAS[star_idx-1]}, you inherit dynamic intuition, deep focus, and natural authority.",
            "hi": f"इस नक्षत्र के प्रभाव से आप स्वाभाविक नेतृत्व, प्रखर बुद्धिमत्ता और दूरदर्शी सोच के धनी हैं।",
            "mr": f"या नक्षत्राच्या प्रभावामुळे तुमच्यात तीव्र बुद्धिमत्ता, नेतृत्वगुण आणि दूरदृष्टी आहे.",
            "gu": f"આ નક્ષત્રના પ્રભાવથી તમારામાં તીવ્ર બુદ્ધિ, નેતૃત્વ ક્ષમતા અને દીર્ઘદ્રષ્ટિ રહેલી છે."
        },
        "prediction": {
            "en": "Your evolutionary path unfolds through consistent skill acquisition and resilient character, resulting in mature stability.",
            "hi": "आपका भाग्योदय निरंतर कौशल विकास और धैर्यवान कर्मों से होता है।",
            "mr": "सातत्यपूर्ण प्रयत्न आणि संयमाने तुमचा भाग्योदय होईल.",
            "gu": "નિયમિત પરિશ્રમ અને ધૈર્યથી તમારો ભાગ્યોદય થાય છે."
        },
        "remedies": {
            "en": f"• Chant the Beej Mantra of deity {bio['deity']} 11 times daily.\n• Water your sacred tree ({bio['tree']}).",
            "hi": f"• अपने नक्षत्र देवता {bio['deity']} के मंत्र का जप करें।\n• पवित्र वृक्ष ({bio['tree']}) का सिंचन करें।",
            "mr": f"• नक्षत्र देवतेचा नियमित जप करावा.\n• नक्षत्र वृक्षाची ({bio['tree']}) निगा राखावी.",
            "gu": f"• નક્ષત્ર દેવતાનો નિયમિત જાપ કરો.\n• નક્ષત્ર વૃક્ષ ({bio['tree']}) નું જતન કરો."
        }
    }
    
    data = star_details.get(star_idx, fallback_text)
    pers = data["personality"].get(lang, data["personality"]["en"])
    pred = data["prediction"].get(lang, data["prediction"]["en"])
    rems = data["remedies"].get(lang, data["remedies"]["en"])
    
    return {
        "deity": bio["deity"],
        "symbol": bio["symbol"],
        "tree": bio["tree"],
        "bird": bio["bird"],
        "animal": bio["animal"],
        "lord": bio["lord"],
        "personality": pers,
        "desc": pers,
        "traits": pers,
        "prediction": pred,
        "remedies": rems
    }

def get_moon_rashi_details(rashi_idx: int, lang: str = "en") -> dict:
    rashi_info = {
        0: {
            "name": "Mesha (Aries / मेष)",
            "element": "Fire (Agni Tattva / अग्नि तत्व)",
            "ruler": "Mars (Mangal / मंगल)",
            "profile": {
                "en": "With Moon in Mesha (Aries), your mind functions like a high-voltage engine. You are bold, spontaneous, highly decisive, and driven by pioneering initiative. You do not wait for opportunities—you carve them. Mentally fearless, you refuse to be dominated, possessing rapid emotional recovery and instant problem-solving reflexes.",
                "hi": "चन्द्रमा के मेष राशि में होने से आपका मन अत्यंत तेजस्वी, साहसी और ऊर्जावान रहता है। आप त्वरित निर्णय लेने वाले, नए उपक्रमों की शुरुआत करने वाले और निडर स्वभाव के हैं। आप परिस्थितियों के आगे झुकते नहीं, अपितु संकटों का डटकर मुकाबला करते हैं।",
                "mr": "मेष राशीतील चंद्रामुळे तुमचे मन अत्यंत उत्साही, निर्भय आणि तत्पर असते. नवीन उपक्रम हाती घेणे आणि संकटांना न घाबरता सामोरे जाणे हा तुमचा मूळ स्वभाव आहे.",
                "gu": "મેષ રાશિમાં ચંદ્ર હોવાથી તમારું મન અત્યંત સાહસિક અને ઊર્જાવાન છે. ત્વરિત નિર્ણયો લેવા અને પડકારો સામે અડગ ઊભા રહેવું તમારો સ્વભાવ છે."
            },
            "prediction": {
                "en": "Chandra in Mars's fiery sign awards dynamic leadership, physical courage, and sudden breakthroughs in competitive fields, technology, or management. While sudden impatience or anger can cause momentary friction, practicing tactical calm turns your fiery impulse into an unstoppable asset.",
                "hi": "मंगल की अग्नि राशि में स्थित चन्द्र आपको प्रशासनिक नेतृत्व, प्रतिस्पर्धी परीक्षाओं और तकनीकी कार्यों में असाधारण विजय दिलाता है। केवल जल्दबाजी और क्रोध पर नियंत्रण रखने से आपका जीवन अत्यंत सफल और समृद्ध रहेगा।",
                "mr": "मंगळाच्या राशीतील चंद्र प्रशासकीय नेतृत्व आणि स्पर्धांमध्ये विजय मिळवून देतो. केवळ संयम बाळगल्यास अफाट संपत्ती व नावलौकिक प्राप्त होईल.",
                "gu": "મંગળની રાશિમાં ચંદ્ર હોવાથી વહીવટી અને સ્પર્ધાત્મક ક્ષેત્રોમાં ઉત્તમ સફળતા મળે છે. ક્રોધ પર સંયમ રાખવો હિતાવહ છે."
            },
            "remedies": {
                "en": "• Offer water mixed with red sandalwood and rose petals to Surya Dev every morning.\n• Recite the **Hanuman Chalisa** daily, especially on Tuesdays, to channel emotional fire into constructive power.\n• Wear a red coral or keep a small square piece of silver in your pocket to cool lunar impulses.",
                "hi": "• प्रतिदिन तांबे के पात्र से सूर्य देव को रोली/लाल चंदन मिश्रित जल अर्पित करें।\n• नित्य प्रातः अथवा संध्या को **श्री हनुमान चालीसा** का पाठ करें।\n• क्रोध शांत रखने हेतु चांदी का चौकोर टुकड़ा अपने पास रखें अथवा चांदी के गिलास में जल पिएं।",
                "mr": "• रोज सकाळी सूर्याला लाल चंदन मिश्रित जल अर्पण करावे.\n• दररोज **हनुमान चालीसा** पठण करावे.\n• चांदीच्या पात्रातून पाणी प्यावे जेणेकरून मन शांत राहील.",
                "gu": "• સવારે સૂર્ય નારાયણને લાલ ચંદન મિશ્રિત જળ ચડાવો.\n• નિયમિત **હનુમાન ચાલીસા** ના પાઠ કરો.\n• મનને શાંત રાખવા ચાંદીના ગ્લાસમાં પાણી પીઓ."
            }
        }
    }
    
    selected = rashi_info.get(rashi_idx, {
        "name": RASHIS[rashi_idx],
        "element": "Vedic Cosmic Element",
        "ruler": "Planetary Sovereign",
        "profile": {
            "en": "Your Moon sign governs emotional perception, psychological instinct, and subconscious behavioral responses.",
            "hi": "आपकी चन्द्र राशि आपके मानसिक संतुलन, भावनात्मक दृष्टिकोण और आंतरिक स्वभाव का निर्धारण करती है।",
            "mr": "तुमची चंद्र रास तुमचा भावनिक दृष्टिकोन आणि मानसिक स्वभाव दर्शवते.",
            "gu": "તમારી ચંદ્ર રાશિ તમારા માનસિક સ્વભાવ અને ભાવનાત્મક સંતુલનનું નિર્માણ કરે છે."
        },
        "prediction": {
            "en": "Favorable alignment creates mental stability and sound intuition in professional and domestic matters.",
            "hi": "चन्द्रमा का शुभ प्रभाव आपके जीवन में मानसिक शांति, स्थिर आय और पारिवारिक सुख में वृद्धि करता है।",
            "mr": "चंद्राचा प्रभाव मानसिक शांती आणि कौटुंबिक सुख समृद्धी प्रदान करतो.",
            "gu": "ચંદ્રનો પ્રભાવ માનસિક શાંતિ અને પારિવારિક સુખ આપે છે."
        },
        "remedies": {
            "en": "• Offer clean water to a Shiva Lingam on Mondays.\n• Respect mother figures and drink water from a silver cup.",
            "hi": "• सोमवार को शिवलिंग पर शुद्ध जल व कच्चा दूध अर्पित करें।\n• माता का चरण स्पर्श कर आशीर्वाद लें।",
            "mr": "• सोमवारी महादेवाला अभिषेक करावा व आईचा आशीर्वाद घ्यावा.",
            "gu": "• સોમવારે શિવલિંગ પર જળ ચડાવો અને માતાના આશીર્વાદ લો."
        }
    })
    
    prof_text = selected["profile"].get(lang, selected["profile"]["en"])
    pred_text = selected["prediction"].get(lang, selected["prediction"]["en"])
    rem_text = selected["remedies"].get(lang, selected["remedies"]["en"])
    
    return {
        "name": selected["name"],
        "element": selected["element"],
        "ruler": selected["ruler"],
        "profile": prof_text,
        "desc": prof_text,
        "prediction": pred_text,
        "remedies": rem_text
    }

def get_lagna_details(lagna_idx: int, lang: str = "en") -> dict:
    lagna_info = {
        1: {
            "name": "Vrishabha (Taurus / वृषभ लग्न)",
            "element": "Earth (Prithvi Tattva / पृथ्वी तत्व)",
            "lord": "Venus (Shukra / शुक्र)",
            "profile": {
                "en": "With Vrishabha (Taurus) Ascendant, your outward persona radiates calm dignity, refined aesthetic taste, unshakeable stability, and immense perseverance. You are structured, practical, and immune to superficial drama. Once committed to a goal or a person, your resolve is rock-solid. You appreciate quality, craftsmanship, wealth generation, and comfortable luxury.",
                "hi": "वृषभ लग्न के जातक होने के कारण आपका बाह्य व्यक्तित्व अत्यंत शालीन, स्थिर, गंभीर और प्रभावशाली होता है। आप दिखावे से दूर, ठोस धरातल पर कार्य करने वाले व्यक्ति हैं। एक बार जो संकल्प ले लेते हैं, उसे पूर्ण करके ही दम लेते हैं। आपमें आर्थिक दूरदर्शिता और कलात्मक सुरुचि कूट-कूट कर भरी होती है।",
                "mr": "वृषभ लग्नामुळे तुमचे व्यक्तिमत्त्व शांत, भारदस्त आणि अत्यंत व्यावहारिक असते. चंचलतेला तुमच्यात स्थान नाही. एकदा ठरवलेले ध्येय पूर्ण केल्याशिवाय तुम्ही थांबत नाही. संपत्ती निर्मिती आणि स्थैर्यावर तुमचा विशेष भर असतो.",
                "gu": "વૃષભ લગ્ન હોવાથી તમારું વ્યક્તિત્વ અત્યંત ગંભીર, સ્થિર અને પ્રભાવશાળી છે. કોઈ પણ કાર્યમાં ધૈર્ય અને દૃઢ સંકલ્પથી આગળ વધવું તમારો સ્વભાવ છે."
            },
            "prediction": {
                "en": "Governed by Shukra (Venus), your life trajectory is engineered for steady compounding wealth, physical vitality, executive longevity, and tangible asset accumulation (real estate, gold, luxury commodities). Obstacles in youth transform into supreme worldly stability as you approach mature years.",
                "hi": "शुक्र देव की छत्रछाया में आपका जीवन उत्तरोत्तर आर्थिक संपन्नता, अचल संपत्ति, वाहन सुख और सामाजिक प्रतिष्ठा की ओर अग्रसर रहता है। युवावस्था के संघर्ष आपको परिपक्व अवस्था में एक अटूट साम्राज्य स्थापित करने का सामर्थ्य देते हैं।",
                "mr": "शुक्राच्या प्रभावामुळे जीवनात स्थावर मालमत्ता, वाहने, ऐश्वर्य आणि दीर्घकालीन आर्थिक समृद्धीचे उत्तम योग आहेत.",
                "gu": "શુક્રના આશીર્વાદથી જીવનમાં ધીમે ધીમે પણ સ્થિર અને મોટી સંપત્તિ, વાહન સુખ અને ઉત્તમ પ્રતિષ્ઠા પ્રાપ્ત થાય છે."
            },
            "remedies": {
                "en": "• Apply pure white sandalwood or natural rose attar on your pulse points before starting important work.\n• Worship Goddess Lakshmi or recite the **Shri Suktam** on Fridays for financial and physical radiance.\n• Respect women, maintain clean surroundings, and donate white sweets or curd to the needy on Fridays.",
                "hi": "• महत्वपूर्ण कार्यों से पूर्व अपनी कलाई पर श्वेत चंदन अथवा गुलाब का इत्र लगाएं।\n• शुक्रवार को **श्री सूक्तम्** का पाठ करें अथवा माँ लक्ष्मी को खीर का भोग लगाएं।\n• महिलाओं का सम्मान करें तथा शुक्रवार को सफेद मिठाई अथवा दही का दान करें।",
                "mr": "• महत्त्वाच्या कामाला जाताना शुभ्र चंदन किंवा अत्तर लावावे.\n• शुक्रवारी **श्री सूक्त** पठण करावे आणि देवी लक्ष्मीची उपासना करावी.\n• शुक्रवारी पांढऱ्या वस्तूंचे दान करावे.",
                "gu": "• શુભ કાર્ય પહેલાં સફેદ ચંદન કે અત્તર લગાવો.\n• શુક્રવારે **શ્રી સૂક્તમ્** નો પાઠ કરો અને લક્ષ્મીજીની કૃપા મેળવો.\n• શુક્રવારે સફેદ મીઠાઈ કે દૂધ-દહીંનું દાન કરો."
            }
        }
    }
    
    selected = lagna_info.get(lagna_idx, {
        "name": RASHIS[lagna_idx],
        "element": "Vedic Lagna Tattva",
        "lord": "Ascendant Sovereign",
        "profile": {
            "en": "Your Lagna (Ascendant) defines physical vitality, constitution, outward persona, and behavioral approach to the world.",
            "hi": "आपका लग्न आपके शारीरिक स्वास्थ्य, बाह्य व्यक्तित्व और सांसारिक कार्यशैली का मूलाधार है।",
            "mr": "तुमचे लग्न तुमचे शारीरिक आरोग्य आणि बाह्य जगातील व्यक्तिमत्त्व ठरवते.",
            "gu": "તમારું લગ્ન તમારા શારીરિક સ્વાસ્થ્ય અને બાહ્ય વ્યક્તિત્વનો પાયો છે."
        },
        "prediction": {
            "en": "Lagna lord harmony guides health, executive ambition, and societal standing across life cycles.",
            "hi": "लग्नेश की शुभता से जीवन में आरोग्य, दीर्घायु और सामाजिक प्रभाव का विस्तार होता है।",
            "mr": "लग्नेश अनुकूल असल्यास उत्तम आरोग्य आणि सामाजिक प्रतिष्ठा लाभते.",
            "gu": "લગ્નેશના શુભ પ્રભાવથી ઉત્તમ આરોગ્ય અને પ્રતિષ્ઠા વધે છે."
        },
        "remedies": {
            "en": "• Practice daily morning Pranayama to align physical breath with mental vitality.\n• Strengthen Lagna lord through mindful daily discipline and charity.",
            "hi": "• नित्य प्रातः प्राणायाम करें जिससे लग्न की जैविक ऊर्जा सशक्त रहे।\n• लग्नेश के मंत्र का श्रद्धापूर्वक जप करें।",
            "mr": "• नियमित प्राणायाम करून प्राणशक्ती वाढवावी.\n• लग्नेशाची आराधना करावी.",
            "gu": "• નિયમિત પ્રાણાયામ કરો અને લગ્નેશની કૃપા મેળવો."
        }
    })
    
    prof_text = selected["profile"].get(lang, selected["profile"]["en"])
    pred_text = selected["prediction"].get(lang, selected["prediction"]["en"])
    rem_text = selected["remedies"].get(lang, selected["remedies"]["en"])
    
    return {
        "name": selected["name"],
        "element": selected["element"],
        "lord": selected["lord"],
        "profile": prof_text,
        "desc": prof_text,
        "prediction": pred_text,
        "remedies": rem_text
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

    if lang == "hi":
        return {
            "career_title": "💼 आजीविका एवं कर्मक्षेत्र (Career & Executive Destiny)",
            "career_desc": (
                f"मूलांक {mulank} ({p_m}) और भाग्यांक {bhagyank} ({p_b}) का दुर्लभ संयोग आपको असाधारण रणनीतिक सोच और निडर कार्यशैली प्रदान करता है। "
                "पारंपरिक नौकरियों की तुलना में आप स्वतंत्र निर्णय लेने, तकनीकी प्रणालियों का निर्माण करने, संरचनात्मक सुधारों और उच्च-प्रबंधकीय पदों पर सर्वाधिक चमकते हैं। "
                "आप संकट के समय सबसे शांत रहकर सटीक समाधान खोजते हैं।"
            ),
            "wealth_title": "💰 धन-सम्पदा एवं वित्तीय स्थिरता (Wealth & Asset Building)",
            "wealth_desc": (
                "राहु और मंगल के संयुक्त प्रभाव से आपके जीवन में अचानक वित्तीय विस्तार और गैर-पारंपरिक स्रोतों से धनलाभ के प्रबल अवसर बनते हैं। "
                "अस्थिर सट्टेबाजी से बचें; दीर्घकालिक अचल संपत्ति (Real Estate), ठोस भूमि, स्वर्ण और तकनीकी संपत्तियों में निवेश आपके लिए सर्वाधिक फलदायी रहेगा।"
            ),
            "rel_title": "❤️ संबंध एवं वैवाहिक सौहार्द (Relationships & Interpersonal Harmony)",
            "rel_desc": (
                "आप संबंधों में अत्यधिक निष्ठावान, समर्पित और दोहरेपन से मुक्त हैं। जो भी कहते हैं, सीधे हृदय से कहते हैं। "
                "कभी-कभी आपकी स्पष्टवादिता को लोग कठोरता समझ लेते हैं; इसलिए महत्वपूर्ण चर्चाओं के समय सौम्य वाणी और धैर्यपूर्ण श्रवण अभ्यास आपके दांपत्य व पारिवारिक संबंधों को अटूट बनाएगा।"
            ),
            "health_title": "🌿 स्वास्थ्य एवं जैविक ऊर्जा (Health, Vitality & Energy Flow)",
            "health_desc": (
                "आपके पास नैसर्गिक रूप से तीव्र ऊर्जा और सहनशक्ति है, किंतु अधिक सोचने या अनिद्रा से सिरदर्द या वायु-विकार हो सकता है। "
                "पर्याप्त जल पिएं, नियमित समय पर पौष्टिक भोजन लें और रात्रि को सोने से पूर्व 10 मिनट प्राणायाम करें।"
            ),
            "luck_title": "🍀 भाग्य सूचक तत्व (Harmonic Luck Matrix)",
            "lucky_num": "1, 3, 5, 9 (अत्यंत शुभ व पूरक)",
            "avoid_num": "2, 8 (संयम व सावधानी अपेक्षित)",
            "lucky_days": "रविवार, मंगलवार, गुरुवार",
            "lucky_colors": "केसरिया, पीला, हल्का नीला, गहरा लाल",
            "lucky_dir": "दक्षिण (South) एवं ईशान कोण (North-East)"
        }
    elif lang == "mr":
        return {
            "career_title": "💼 व्यवसाय व नोकरी (Career & Executive Trajectory)",
            "career_desc": (
                f"मूलांक {mulank} ({p_m}) आणि भाग्यांक {bhagyank} ({p_b}) यांचा संयोग तुम्हाला स्वतंत्र निर्णय घेण्याची अफाट ताकद आणि धाडसी नेतृत्व देतो. "
                "मोठ्या प्रकल्पांचे नियोजन, तांत्रिक किंवा व्यवस्थापकीय क्षेत्रात तुम्ही शीर्षस्थानी पोहोचू शकता."
            ),
            "wealth_title": "💰 आर्थिक संपदा व समृद्धी (Wealth & Long-term Investments)",
            "wealth_desc": (
                "जीवनात अचानक मोठे आर्थिक लाभ मिळण्याचे योग आहेत. अल्पकालीन सट्टेबाजी टाळा आणि स्थिर मालमत्ता, जमीन व सोन्यामध्ये दीर्घकालीन गुंतवणूक करा."
            ),
            "rel_title": "❤️ नातेसंबंध व कौटुंबिक सौख्य (Relationships & Family Bond)",
            "rel_desc": (
                "तुम्ही नात्यांमध्ये अत्यंत प्रामाणिक व सरळ आहात. संवाद साधताना वाणीत गोडवा आणि समोरच्या व्यक्तीचे ऐकून घेण्याची वृत्ती ठेवल्यास कौटुंबिक सुख अधिक वाढेल."
            ),
            "health_title": "🌿 आरोग्य व जीवनशैली (Health & Physical Energy)",
            "health_desc": (
                "प्रचंड शारीरिक क्षमता असली तरी कामाचा अतिताण टाळा. रोज सकाळी नियमित प्राणायाम आणि संतुलित आहार घेतल्यास ऊर्जा सदैव टिकून राहील."
            ),
            "luck_title": "🍀 भाग्यवान घटक (Lucky Attributes Chart)",
            "lucky_num": "१, ३, ५, ९ (अतिशय लाभदायक)",
            "avoid_num": "२, ८ (सावधगिरी बाळगा)",
            "lucky_days": "रविवार, मंगळवार, गुरुवार",
            "lucky_colors": "लाल, भगवा, पिवळा, आकाशी निळा",
            "lucky_dir": "दक्षिण आणि ईशान्य दिशा"
        }
    elif lang == "gu":
        return {
            "career_title": "💼 કારકિર્દી અને વ્યવસાય (Career & Professional Growth)",
            "career_desc": (
                f"મૂળાંક {mulank} ({p_m}) અને ભાગ્યાંક {bhagyank} ({p_b}) નો સમન્વય અદભુત આત્મવિશ્વાસ, કુશળ નેતૃત્વ અને ઝડપી સમસ્યા-નિવારણ ક્ષમતા બક્ષે છે."
            ),
            "wealth_title": "💰 ધન-સંપત્તિ અને નાણાકીય આયોજન (Wealth & Assets)",
            "wealth_desc": (
                "જીવનમાં આકસ્મિક આર્થિક પ્રગતિના ઉત્તમ યોગ બને છે. જમીન-મકાન અને લાંબા ગાળાના સુરક્ષિત રોકાણો તમારા માટે અત્યંત ફાયદાકારક સાબિત થશે."
            ),
            "rel_title": "❤️ સંબંધો અને પારિવારિક સુખ (Relationships & Family)",
            "rel_desc": (
                "તમે સંબંધોમાં અત્યંત વફાદાર અને નિખાલસ છો. બોલતી વખતે વાણીમાં નમ્રતા રાખવાથી પારિવારિક અને વ્યાવસાયિક સંબંધોમાં મીઠાશ જળવાઈ રહેશે."
            ),
            "health_title": "🌿 સ્વાસ્થ્ય અને જીવનશક્તિ (Health & Wellness)",
            "health_desc": (
                "શારીરિક ઊર્જા ઉત્તમ છે. પૂરતો આરામ, નિયમિત પ્રાણાયામ અને પૂરતા પ્રમાણમાં પાણી પીવું તમારા સ્વાસ્થ્ય માટે હિતાવહ રહેશે."
            ),
            "luck_title": "🍀 ભાગ્યશાળી તત્વો (Lucky Attributes Matrix)",
            "lucky_num": "૧, ૩, ૫, ૯ (શુભ)",
            "avoid_num": "૨, ૮ (સાવધાની જરૂરી)",
            "lucky_days": "રવિવાર, મંગળવાર, ગુરુવાર",
            "lucky_colors": "લાલ, કેસરી, સોનેરી, આછો વાદળી",
            "lucky_dir": "દક્ષિણ અને ઈશાન ખૂણો"
        }
    else:
        return {
            "career_title": "💼 Career Trajectory & Executive Ambition",
            "career_desc": (
                f"The dynamic synthesis of Driver {mulank} ({p_m}) and Conductor {bhagyank} ({p_b}) creates an unstoppable powerhouse combination of non-conformist strategic vision and courageous execution. "
                "You are naturally engineered for leadership, structural problem solving, complex systems architecture, and transformative projects where you hold autonomy over decisions."
            ),
            "wealth_title": "💰 Wealth Dynamics & Long-Term Financial Mastery",
            "wealth_desc": (
                "Rahu and Mars catalyze non-linear wealth opportunities and sudden capital liquidity. While wealth comes in large bursts, avoid volatile speculative gambling. "
                "Tangible hard assets—prime real estate, land parcels, gold bullion, and long-term tech holdings—provide your ultimate financial fortress."
            ),
            "rel_title": "❤️ Relationships, Marriage & Interpersonal Dynamics",
            "rel_desc": (
                "You are fiercely loyal, protective, and deeply authentic in personal relationships, with zero tolerance for pretense. "
                "Because you value truth above all, conscious verbal softness and active listening during emotionally charged moments will keep your relationships thriving and harmonious."
            ),
            "health_title": "🌿 Health, Vitality & Holistic Bio-Rhythms",
            "health_desc": (
                "You possess high innate endurance and resilience. However, your intense mental momentum can trigger restless sleep or metabolic heat. "
                "Prioritize deep hydration, structured recovery, and 10 minutes of grounding evening meditation or Pranayama."
            ),
            "luck_title": "🍀 Harmonic Lucky Attributes & Vibration Chart",
            "lucky_num": "1, 3, 5, 9 (Harmonic Synergy)",
            "avoid_num": "2, 8 (Friction / Demanding Karmic Energy)",
            "lucky_days": "Sunday, Tuesday, and Thursday",
            "lucky_colors": "Electric Blue, Slate Gray, Rich Coral Red, Golden Amber",
            "lucky_dir": "South and North-East (Ishanya)"
        }

def get_numerology_avoidance(mulank: int, bhagyank: int, lang: str = "en") -> dict:
    if lang == "hi":
        return {
            "avoid_title": "⚠️ अंकशास्त्रीय निषेध एवं सावधानियां (What to Avoid Matrix)",
            "avoid_numbers": "2, 8 (मानसिक अस्थिरता व विलंब कारक अंक)",
            "avoid_colors": "गहरा काला, स्लेटी भूरा, अत्यधिक गहरा नीला",
            "avoid_days": "शनिवार संध्या एवं सोमवार देर रात्रि (महत्वपूर्ण समझौतों के लिए)",
            "avoid_directions": "नैऋत्य कोण (South-West) में सिर रखकर न सोएं",
            "cautions": [
                "अपरिचितों के साथ मौखिक समझौतों अथवा बिना लिखित दस्तावेज के साझेदारी से बचें।",
                "क्रोध या अत्यधिक उत्साह में आकर तत्काल वित्तीय अथवा पारिवारिक निर्णय न लें।",
                "सट्टेबाजी, लॉटरी अथवा शेयर बाजार में त्वरित लाभ की लालच से पूर्णतः दूर रहें।",
                "कार्यस्थल पर बिखरे हुए अथवा टूटे हुए इलेक्ट्रॉनिक तारों व अनुपयोगी उपकरणों का जमावड़ा न रखें।",
                "शनिवार को चमड़े या लोहे की अनावश्यक वस्तुएं क्रय करने से परहेज करें।"
            ]
        }
    elif lang == "mr":
        return {
            "avoid_title": "⚠️ अंकशास्त्रीय सावधगिरी व काय टाळावे",
            "avoid_numbers": "२, ८ (मानसिक तणाव व कामात अडथळे आणणारे अंक)",
            "avoid_colors": "गडद काळा, तपकिरी, मळकट जांभळा",
            "avoid_days": "शनिवार आणि सोमवार (मोठ्या करारांसाठी)",
            "avoid_directions": "नैऋत्य दिशा (South-West)",
            "cautions": [
                "अनोळखी व्यक्तींसोबत विनादस्तऐवज आर्थिक व्यवहार करणे टाळा.",
                "अतिउत्साहात किंवा रागाच्या भरात कोणताही मोठा निर्णय घेऊ नका.",
                "सट्टा किंवा झटपट पैशांच्या प्रलोभनांपासून दूर राहा.",
                "घरात किंवा कार्यालयात तुटलेले विजेचे सामान जमा होऊ देऊ नका.",
                "शनिवारी लोखंड अथवा चामड्याच्या वस्तू खरेदी करणे टाळा."
            ]
        }
    elif lang == "gu":
        return {
            "avoid_title": "⚠️ અંકશાસ્ત્રીય સાવધાની અને શું ટાળવું",
            "avoid_numbers": "૨, ૮ (વિલંબ અને માનસિક દબાણ લાવનારા અંક)",
            "avoid_colors": "ઘેરો કાળો, કથ્થઈ રંગ",
            "avoid_days": "શનિવાર અને સોમવાર",
            "avoid_directions": "નૈઋત્ય ખૂણો (South-West)",
            "cautions": [
                "લેખિત પુરાવા વિના નાણાકીય લેવડદેવડ કરવી નહીં.",
                "ઉતાવળમાં કે ગુસ્સામાં આવીને જીવનના મહત્વના નિર્ણયો ન લો.",
                "સટ્ટાબાજી અને શોર્ટકટથી દૂર રહો.",
                "કાર્યાલયમાં જૂના બંધ પડેલા સાધનો રાખવા નહીં.",
                "શનિવારે ચામડા કે લોખંડની વસ્તુ ખરીદવાનું ટાળો."
            ]
        }
    else:
        return {
            "avoid_title": "⚠️ Cosmic Caution & Avoidance Matrix (What to Avoid)",
            "avoid_numbers": "2, 8 (Friction, delays & karmic tests)",
            "avoid_colors": "Pitch Black, Mud Brown, Dirty Dark Indigo (depletes vitality)",
            "avoid_days": "Saturday twilight & Monday late nights (for launching ventures)",
            "avoid_directions": "South-West (Nairruti) for head orientation during rest",
            "cautions": [
                "Avoid unwritten or casual handshake financial agreements; document every clause clearly.",
                "Never commit to capital investments or career shifts during impulsive anger or peak adrenaline.",
                "Strictly avoid speculative options trading, rapid-leverage gambles, or get-rich schemes.",
                "Eliminate tangled electronic cables, dead batteries, and non-functional gadgets from your workspace.",
                "Refrain from purchasing iron hardware, sharp cutlery, or real leather items on Saturdays."
            ]
        }

def calculate_shani_paya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    house_diff = (moon_rashi_idx - saturn_transit_rashi_idx) % 12 + 1
    if house_diff in [2, 5, 9]:
        return {
            "paya": "🥈 Rajat Paya (Silver Feet / चाँदी का पाया)",
            "metal": "Silver",
            "status": "Highly Auspicious (अति शुभ)",
            "desc": "Saturn arrives bearing silver gifts. Bestows financial liquidity, career elevation, relief from long-standing stress, and divine protection during Sade Sati.",
            "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces)"
        }
    elif house_diff in [3, 7, 10]:
        return {
            "paya": "🥉 Tamra Paya (Copper Feet / तांबे का पाया)",
            "metal": "Copper",
            "status": "Favorable (शुभ)",
            "desc": "Brings steady professional growth, success through hard work, balanced family relationships, and gradual financial gains.",
            "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces)"
        }
    elif house_diff in [1, 6, 11]:
        return {
            "paya": "🥇 Swarna Paya (Gold Feet / सोने का पाया)",
            "metal": "Gold",
            "status": "Testing & Demanding (कठिन)",
            "desc": "Tests character through ego challenges, high expenditures, and health concerns. Requires humility, discipline, and charity.",
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

def get_sidereal_moon_longitude(utc_dt: datetime.datetime) -> float:
    if utc_dt.tzinfo is not None:
        utc_dt = utc_dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)

    if HAS_SWISSEPH:
        try:
            t_jd = swe.julday(
                utc_dt.year, utc_dt.month, utc_dt.day,
                utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
            )
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            res = swe.calc_ut(t_jd, swe.MOON, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)
            res_val = res[0] if isinstance(res, (tuple, list)) else res
            lon = res_val[0] if isinstance(res_val, (tuple, list)) else res_val
            return float(lon % 360.0)
        except Exception:
            try:
                res = swe.calc_ut(t_jd, swe.MOON, swe.FLG_SIDEREAL)
                res_val = res[0] if isinstance(res, (tuple, list)) else res
                lon = res_val[0] if isinstance(res_val, (tuple, list)) else res_val
                return float(lon % 360.0)
            except Exception:
                pass

    ref = datetime.datetime(2000, 1, 1, 12, 0)
    delta_days = (utc_dt - ref).total_seconds() / 86400.0
    moon_mean_lon = (218.316 + 13.176396 * delta_days - 23.85) % 360.0
    return float(moon_mean_lon)

def calculate_birth_chart(dob: datetime.date, tob: datetime.time, lat: float = 19.8762, lon: float = 75.3433):
    ist_dt = datetime.datetime.combine(dob, tob)
    utc_dt = ist_dt - datetime.timedelta(hours=5, minutes=30)
    
    moon_lon = get_sidereal_moon_longitude(utc_dt)
    star_span = 360.0 / 27.0
    star_idx = max(1, min(27, int(moon_lon / star_span) + 1))
    rem_deg = moon_lon % star_span
    pada = max(1, min(4, int(rem_deg / (star_span / 4.0)) + 1))
    rashi_idx = max(0, min(11, int(moon_lon / 30.0)))

    lagna_idx = (rashi_idx + 1) % 12
    if HAS_SWISSEPH:
        try:
            t_jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                              utc_dt.hour + utc_dt.minute / 60.0)
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            cusps, ascmc = swe.houses(t_jd, lat, lon, b'P')
            ayanamsa = swe.get_ayanamsa_ut(t_jd)
            lagna_lon = (ascmc[0] - ayanamsa) % 360.0
            lagna_idx = max(0, min(11, int(lagna_lon / 30.0)))
        except Exception:
            lagna_idx = (rashi_idx + 1) % 12

    return {
        "star_idx": star_idx,
        "star_name": NAKSHATRAS[star_idx - 1],
        "pada": pada,
        "moon_rashi_idx": rashi_idx,
        "moon_rashi_name": RASHIS[rashi_idx],
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

def get_daily_micro_habit(transit_star_idx: int, navtara_offset: int):
    star_lord = NAKSHATRA_BIO_DATA.get(transit_star_idx, {}).get("lord", "Moon")
    
    palette_map = {
        "Sun": ("Amber Gold, Saffron & Warm Copper", "☀️ Surya Vitality", "Stand facing morning sunlight for 2 minutes while taking 7 deep belly breaths to activate solar metabolic drive."),
        "Moon": ("Pearl White, Cream & Silver Mist", "🌙 Chandra Serenity", "Drink a glass of fresh water stored in a silver vessel; splash cool water over eyes to soothe mental agitation."),
        "Mars": ("Coral Red, Vermilion & Crimson", "🔥 Mangal Courage", "Keep posture straight; stretch spine and calves for 2 minutes to discharge restlessness and channel focused physical resolve."),
        "Mercury": ("Emerald Green, Mint & Jade", "🌿 Budha Intellect", "Write down your top 3 priority decisions in green ink; wash face with rose water to sharpen synaptic communication."),
        "Jupiter": ("Bright Yellow, Golden Ochre & Turmeric", "✨ Brihaspati Wisdom", "Apply a faint dot of yellow sandalwood or pure saffron on wrists; honor mentors mentally before high-stakes talks."),
        "Venus": ("Pastel Pink, Silken White & Floral Lilac", "🌸 Shukra Harmony", "Apply natural sandalwood or rose attar to pulse points; cultivate aesthetic neatness in your immediate workstation."),
        "Saturn": ("Slate Gray, Deep Indigo & Midnight Navy", "🪐 Shani Discipline", "Practice silent conscious breathing (Mauna) for 2 minutes before speaking; stretch lower back to ground nervous energy."),
        "Rahu": ("Electric Blue, Smoky Charcoal & Metallic Silver", "⚡ Rahu Shield", "Tidy cluttered electronics, discard unneeded digital tabs, and avoid rash unverified commitments during twilight."),
        "Ketu": ("Earthy Khaki, Warm Sand & Smoked Hazel", "🕊️ Ketu Detachment", "Close eyes for 2 minutes of silent observation of breath at the eyebrow center (Ajna Chakra) to unhook from chaotic stimuli.")
    }
    
    lord_key = next((k for k in palette_map.keys() if k in star_lord), "Moon")
    color_name, archetype, habit_desc = palette_map[lord_key]
    
    if navtara_offset in [2, 4, 6]:
        caution_cue = "🔴 High-Friction Day Bio-Shield: Avoid harsh confrontation between 12:00 PM and 03:00 PM; drink warm water with a pinch of black salt."
    else:
        caution_cue = "🟢 Expansion Day Synergy: Wear this color prominently to amplify cognitive charisma and executive magnetism."
        
    return {
        "color": color_name,
        "lord": star_lord,
        "archetype": archetype,
        "habit": habit_desc,
        "caution_cue": caution_cue
    }

def get_nakshatra_synergy_data(user_star_idx: int):
    allied_stars = []
    friction_stars = []
    
    for i in range(1, 28):
        offset = (i - user_star_idx) % 9
        star_name = NAKSHATRAS[i - 1]
        if offset in [7, 8]:  # Mitra, Ati-Mitra
            allied_stars.append((star_name, NAVTARA_NAMES[offset][0].split('(')[0].strip()))
        elif offset in [2, 4, 6]:  # Vipat, Pratyari, Vadha
            friction_stars.append((star_name, NAVTARA_NAMES[offset][0].split('(')[0].strip()))
            
    return allied_stars, friction_stars

def calculate_partner_compatibility(user_star_idx: int, partner_star_idx: int):
    user_to_partner = (partner_star_idx - user_star_idx) % 9
    partner_to_user = (user_star_idx - partner_star_idx) % 9
    
    u_nav_name, u_icon, u_quality = NAVTARA_NAMES[user_to_partner]
    p_nav_name, p_icon, p_quality = NAVTARA_NAMES[partner_to_user]
    
    is_high_synergy = user_to_partner in [1, 3, 5, 7, 8] and partner_to_user in [1, 3, 5, 7, 8]
    is_karmic_friction = user_to_partner in [2, 4, 6] or partner_to_user in [2, 4, 6]
    
    if is_high_synergy:
        verdict = "🌟 High Mutual Synergy & Natural Alliance"
        verdict_color = "#15803d"
        verdict_bg = "#dcfce7"
        advice = "Natural mutual understanding, effortless communication, and collaborative expansion. Great for business partnerships, marriage, and long-term joint ventures."
    elif is_karmic_friction:
        verdict = "⚠️ Karmic Growth & High Caution Required"
        verdict_color = "#be123c"
        verdict_bg = "#ffe4e6"
        advice = "Prone to unspoken expectations, emotional friction, or administrative disputes. Document all agreements in writing, practice patient listening, and maintain clear boundaries."
    else:
        verdict = "⚖️ Dynamic & Growth-Oriented (Moderate Balance)"
        verdict_color = "#b45309"
        verdict_bg = "#fef3c7"
        advice = "Complementary strengths with occasional differences in operational pacing. Alignment thrives when roles and responsibilities are distinctly demarcated."
        
    return {
        "verdict": verdict,
        "color": verdict_color,
        "bg": verdict_bg,
        "user_perspective": f"{u_icon} {u_nav_name} ({u_quality})",
        "partner_perspective": f"{p_icon} {p_nav_name} ({p_quality})",
        "advice": advice
    }

def get_7_day_heatmap_and_power_day(transits: list):
    score_weights = {8: 10, 7: 9, 5: 8, 1: 8, 3: 7, 0: 5, 4: 4, 2: 3, 6: 2}
    
    best_day = None
    best_score = -1
    
    heatmap_items = []
    for tr in transits:
        off = tr["nav_offset"]
        score = score_weights.get(off, 5)
        if score > best_score:
            best_score = score
            best_day = tr
            
        if off in [7, 8]:
            bg = "#bbf7d0"; border = "#16a34a"; text = "#14532d"; badge = "🟢🟢 Peak"
        elif off in [1, 3, 5]:
            bg = "#dcfce7"; border = "#22c55e"; text = "#15803d"; badge = "🟢 Good"
        elif off == 0:
            bg = "#fef3c7"; border = "#eab308"; text = "#854d0e"; badge = "🟡 Focus"
        else:
            bg = "#fee2e2"; border = "#ef4444"; text = "#991b1b"; badge = "🔴 Guard"
            
        heatmap_items.append({
            "day": tr["date_str"].split(',')[0],
            "date": tr["date_str"].split(',')[1].strip(),
            "star": tr["star_name"][:5] + ".",
            "badge": badge,
            "bg": bg,
            "border": border,
            "text": text
        })
        
    return heatmap_items, best_day

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

PROFILE_FILE = "user_profile.json"

def load_user_profile():
    default_profile = {
        "name": "Okesh",
        "dob": "1984-01-13",
        "tob": "14:00",
        "city": "Chhatrapati Sambhajinagar, Maharashtra",
        "lat": 19.8762,
        "lon": 75.3433,
        "lang": "en"
    }
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**default_profile, **data}
        except Exception:
            return default_profile
    return default_profile

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

if "partner_star_idx" not in st.session_state:
    st.session_state.partner_star_idx = 1

prof = st.session_state.user_profile
current_lang = prof.get("lang", "en")

render_html(f"""
    <div style='text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; margin-top:0.2rem; margin-bottom:0.75rem;'>
        <div style='background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); width:76px; height:76px; border-radius:26px; display:flex; align-items:center; justify-content:center; font-size:2.45rem; box-shadow:0 8px 28px rgba(245,158,11,0.38); margin-bottom:10px;'>
            ✨
        </div>
        <h1 style='margin:0; font-size:2.15rem; color:#0f172a; font-weight:900; line-height:1.2; text-align:center;'>{t('app_title', current_lang)}</h1>
        <div style='font-size:1rem; color:#64748b; font-weight:600; margin-top:6px; text-align:center;'>{t('app_subtitle', current_lang)}</div>
    </div>
""")

# Top Navigation Dock (Balanced 2 Rows x 3 Columns)
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

try:
    dob_parsed = datetime.datetime.strptime(prof["dob"], "%Y-%m-%d").date()
except Exception:
    dob_parsed = datetime.date(1984, 1, 13)

try:
    tob_parsed = datetime.datetime.strptime(prof["tob"], "%H:%M").time()
except Exception:
    tob_parsed = datetime.time(14, 0)

chart_info = calculate_birth_chart(dob_parsed, tob_parsed, prof.get("lat", 19.8762), prof.get("lon", 75.3433))
mulank, bhagyank, namank = calculate_numerology(dob_parsed, prof.get("name", "User"))

# Saturn in Pisces (Meena = index 11)
SATURN_TRANSIT_RASHI_IDX = 11
shani_paya_data = calculate_shani_paya(chart_info["moon_rashi_idx"], SATURN_TRANSIT_RASHI_IDX)
shani_sadesati_data = calculate_shani_sadesati_dhaiya(chart_info["moon_rashi_idx"], SATURN_TRANSIT_RASHI_IDX)

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
            The Moon exerts a massive gravitational pull that governs terrestrial tides and fluid circulation. The adult human body consists of approximately <b>70% water</b>. Just as lunar cycles dictate ocean tides, the Moon's orbital shifts modulate subtle intracellular fluids, cerebrospinal pressure, and endocrine secretions. In Vedic science, the Moon represents the conscious and subconscious mind (<i>"Chandro Manaso Jatah"</i>). When the Moon transits resonant or conflicting stellar zones, human focus, emotional equilibrium, and cognitive stamina experience measurable wave-like rhythms.
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#451a03; margin-bottom:1rem;">
            <b>2. Chronobiology & Infradian Circadian Rhythms:</b><br>
            Modern chronobiology establishes that biological life does not operate on a flat 24-hour clock; it is deeply synced to infradian (multi-day) and lunar bio-rhythms. The ancient Vedic <b>Navtara 9-fold grid</b> is the world's oldest precision chronobiological model. By indexing each day's sidereal Moon position against your natal birth star (Janma Nakshatra), it reveals your natural biorhythmic tides:
            <ul style="margin-top:6px; padding-left:1.3rem;">
                <li><b>Expansion Windows (Sampat, Sadhana, Mitra, Ati-Mitra):</b> Days of high synaptic alignment, optimal for vital negotiations, legal signings, high-stakes investments, and creative execution.</li>
                <li><b>Friction Shields (Vipat, Pratyari, Vadha):</b> Days when planetary resistance elevates cortisol, emotional reactivity, and communication errors. On these days, a defensive posture prevents costly missteps.</li>
            </ul>
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#451a03; margin-bottom:0.8rem;">
            <b>3. Sub-Arcsecond Ephemeris Precision:</b><br>
            Unlike popular astrology apps relying on generic calendar dates, <b>Navtara Pulse</b> integrates with the <b>Moshier Swiss Ephemeris</b> (pyswisseph)—the gold standard used by aerospace institutes and NASA JPL archives. Sidereal ingress and egress timestamps are calculated to true Lahiri Ayanamsa coordinates, giving you pinpoint accuracy for when cosmic windows open and close.
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

def render_page_profile():
    with st.container(border=True):
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            render_html(f"""
            <div style="font-weight:900; font-size:1.2rem; color:#0f172a;">👤 {prof['name']}'s Profile</div>
            <div style="font-size:0.95rem; color:#334155; margin-top:5px; line-height:1.6;">
                📅 <b>DOB:</b> {dob_parsed.strftime('%d %B %Y')} &nbsp;|&nbsp; ⏰ <b>Time:</b> {tob_parsed.strftime('%I:%M %p')}<br>
                📍 <b>Place:</b> {prof['city']}
            </div>
            """)
        with col_p2:
            if st.button(t("edit_details", current_lang), use_container_width=True):
                st.session_state.edit_mode = not st.session_state.edit_mode
                st.rerun()

    if st.session_state.edit_mode:
        with st.expander("✏️ Update Birth Information", expanded=True):
            e_name = st.text_input(t("name_label", current_lang), value=prof["name"])
            e_dob = st.date_input(t("dob_label", current_lang), value=dob_parsed)
            e_tob = st.time_input(t("tob_label", current_lang), value=tob_parsed)
            e_city = st.text_input(t("city_label", current_lang), value=prof["city"])
            
            c_save, c_canc = st.columns(2)
            with c_save:
                if st.button(t("save_details", current_lang), type="primary", use_container_width=True):
                    st.session_state.user_profile.update({
                        "name": e_name,
                        "dob": e_dob.strftime("%Y-%m-%d"),
                        "tob": e_tob.strftime("%H:%M"),
                        "city": e_city
                    })
                    save_user_profile(st.session_state.user_profile)
                    st.session_state.edit_mode = False
                    st.rerun()
            with c_canc:
                if st.button(t("cancel", current_lang), use_container_width=True):
                    st.session_state.edit_mode = False
                    st.rerun()

    n_info = get_nakshatra_traits(chart_info["star_idx"], current_lang)
    m_info = get_moon_rashi_details(chart_info["moon_rashi_idx"], current_lang)
    l_info = get_lagna_details(chart_info["lagna_idx"], current_lang)
    
    allied_stars, friction_stars = get_nakshatra_synergy_data(chart_info["star_idx"])
    allied_str = ", ".join([s[0] for s in allied_stars[:5]])
    friction_str = ", ".join([s[0] for s in friction_stars[:5]])

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
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('nakshatra_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{chart_info['star_name']}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{t('pada_label', current_lang)} {chart_info['pada']}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('moon_rashi_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{moon_p1}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{moon_p2}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('lagna_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{lagna_p1}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{lagna_p2}</div>
            </div>
        </div>

        <!-- 1. JANMA NAKSHATRA SECTION -->
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

        <!-- 2. MOON RASHI SECTION -->
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

        <!-- 3. LAGNA (ASCENDANT) SECTION -->
        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
                <span>🌅</span> <span>3. Lagna (Ascendant): {l_info['name']}</span>
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

        <!-- 4. NAKSHATRA SOCIAL & BUSINESS SYNERGY MATRIX -->
        <div style="background:#fdf4ff; border-radius:14px; padding:14px; border:1.5px solid #f0abfc;">
            <div style="font-weight:900; font-size:1.18rem; color:#86198f; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                <span>🤝</span> <span>4. Nakshatra Social & Business Synergy Matrix</span>
            </div>
            <div style="font-size:0.92rem; color:#4a044e; margin-bottom:10px; line-height:1.5;">
                Cosmic resonance mapping based on your <b>Janma Nakshatra ({chart_info['star_name']})</b>. Evaluate co-founders, partners, and key alliances:
            </div>
            
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:10px; margin-bottom:14px;">
                <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #f0abfc; border-left:4px solid #a21caf;">
                    <b style="color:#86198f; font-size:0.94rem;">🌟 Allied Stars (Mitra & Ati-Mitra):</b>
                    <div style="font-size:0.88rem; color:#4a044e; margin-top:4px; line-height:1.6;">
                        • <b>Key Allied Stars:</b> {allied_str}<br>
                        <i style="color:#701a75;">(Natural allies who bring high support, ease, and mutual growth)</i>
                    </div>
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #fecdd3; border-left:4px solid #e11d48;">
                    <b style="color:#9f1239; font-size:0.94rem;">⚠️ Friction Stars (Vipat & Vadha):</b>
                    <div style="font-size:0.88rem; color:#881337; margin-top:4px; line-height:1.6;">
                        • <b>Key Friction Stars:</b> {friction_str}<br>
                        <i style="color:#9f1239;">(Require clear written terms, conscious patience, and low ego)</i>
                    </div>
                </div>
            </div>
            
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1px solid #f0abfc;">
                <b style="color:#86198f; font-size:0.95rem;">🔍 Interactive Partner / Colleague Synergy Checker:</b>
                <div style="font-size:0.88rem; color:#64748b; margin:2px 0 8px 0;">Select a partner's, spouse's, or colleague's Janma Nakshatra to inspect mutual compatibility:</div>
            </div>
        </div>
    </div>
    """)

    # Interactive partner selectbox right below profile card
    with st.container():
        synergy_col1, synergy_col2 = st.columns([2, 3])
        with synergy_col1:
            sel_partner_star = st.selectbox(
                "Select Colleague / Partner Nakshatra:",
                options=NAKSHATRAS,
                index=st.session_state.partner_star_idx - 1,
                key="profile_partner_star_select"
            )
            partner_idx = NAKSHATRAS.index(sel_partner_star) + 1
            st.session_state.partner_star_idx = partner_idx
            
        with synergy_col2:
            syn_result = calculate_partner_compatibility(chart_info["star_idx"], partner_idx)
            render_html(f"""
            <div style="background:{syn_result['bg']}; border:1.5px solid {syn_result['color']}; border-radius:10px; padding:10px 12px; margin-top:6px;">
                <b style="color:{syn_result['color']}; font-size:0.95rem;">{syn_result['verdict']}</b>
                <div style="font-size:0.86rem; color:#1e293b; margin-top:4px; line-height:1.5;">
                    <b>Your view of them:</b> {syn_result['user_perspective']}<br>
                    <b>Their view of you:</b> {syn_result['partner_perspective']}
                </div>
                <div style="font-size:0.85rem; color:#334155; margin-top:5px; font-style:italic;">
                    💡 {syn_result['advice']}
                </div>
            </div>
            """)

def render_page_numerology():
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

        <!-- Numerology Avoidance Matrix -->
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

        <!-- Dedicated Numerology Remedies Card -->
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

def render_page_shani():
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
                In classical Vedic transit science (<i>Gochara Shastra</i>), the arrival of Saturn into a zodiac sign is evaluated through the house distance from your natal Moon sign. Because Saturn entered Pisces (the 12th house relative to your Aries Moon), it arrives on <b>Silver Feet (Rajat Paya)</b>. Silver is governed by Moon and Venus. It serves as a celestial shock absorber, cooling Saturn's natural dry friction. Even though you are traversing the initial phase of Sade Sati, the silver footing ensures that financial avenues remain open, ancestral protection guards your health, and reputation remains intact through testing times.
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
                    <b>Detailed Prediction:</b> Saturn transits through your 12th house of expenditures, foreign linkages, subconscious shedding, and solitude. You will experience a major restructuring of personal priorities. Unnecessary social obligations will fade. You may feel drawn toward spiritual contemplation, research, or cross-border/distant business endeavors. Watch out for sudden unexpected capital expenses or disrupted sleep cycles. Because Saturn is on Silver Feet, financial outflow converts into productive long-term assets rather than net waste.
                </div>
                <div style="margin-top:8px; font-size:0.92rem; color:#4c1d95; background:#ffffff; padding:8px 10px; border-radius:8px; border:1px solid #e9d5ff;">
                    <b>🪔 Phase 1 Remedies:</b> Offer raw cow milk mixed with water on a Shiva Lingam on Mondays. Donate black sesame seeds and mustard oil on Saturdays. Keep a silver coin or square piece of pure silver in your wallet.
                </div>
            </div>

            <div style="background:#f8fafc; border-radius:12px; padding:12px; border-left:5px solid #64748b; margin-bottom:12px;">
                <div style="font-weight:900; font-size:1rem; color:#1e293b;">Phase 2: Peak Phase (Janma Shani - 1st House Transit)</div>
                <div style="font-size:0.9rem; color:#64748b; margin:2px 0 6px 0;"><b>Timeline:</b> 23 February 2028 – 17 April 2030 (Mesha / Aries)</div>
                <div style="font-size:0.93rem; line-height:1.65; color:#334155;">
                    <b>Detailed Prediction:</b> Saturn transits directly over your natal Moon in Aries (Janma Rashi). This represents the crucible of self-mastery. You will shoulder immense executive duties, high professional accountability, and significant structural shifts in career or health. Mental resilience will be tested. It demands absolute ego surrender, physical stamina, and unwavering patience. Those who avoid haste during Phase 2 emerge as formidable institutional authorities.
                </div>
                <div style="margin-top:8px; font-size:0.92rem; color:#1e293b; background:#ffffff; padding:8px 10px; border-radius:8px; border:1px solid #e2e8f0;">
                    <b>🪔 Phase 2 Remedies:</b> Recite the <b>Hanuman Chalisa</b> twice daily (morning & evening). Light a mustard oil lamp (Diya) beneath a sacred Peepal tree every Saturday evening without looking back.
                </div>
            </div>

            <div style="background:#f8fafc; border-radius:12px; padding:12px; border-left:5px solid #64748b;">
                <div style="font-weight:900; font-size:1rem; color:#1e293b;">Phase 3: Setting Phase (Avarohi Charana - 2nd House Transit)</div>
                <div style="font-size:0.9rem; color:#64748b; margin:2px 0 6px 0;"><b>Timeline:</b> 17 April 2030 – 31 May 2032 (Vrishabha / Taurus)</div>
                <div style="font-size:0.93rem; line-height:1.65; color:#334155;">
                    <b>Detailed Prediction:</b> Saturn transits your 2nd house of accumulated wealth, family lineages, speech, and material sustenance. As Sade Sati draws to a close, the hard lessons of the preceding 5 years crystallize into permanent assets, financial consolidation, and family maturity. Speech must remain measured to avoid domestic misunderstandings. Financial rewards for earlier patience manifest solidly during this concluding phase.
                </div>
                <div style="margin-top:8px; font-size:0.92rem; color:#1e293b; background:#ffffff; padding:8px 10px; border-radius:8px; border:1px solid #e2e8f0;">
                    <b>🪔 Phase 3 Remedies:</b> Feed whole wheat flour dough balls (Peda) mixed with black sesame to black cows or fish on Saturdays. Practice mindful silence (Mauna) for 15 minutes before sunset.
                </div>
            </div>
        </div>

        <div style="background:#fff1f2; border-radius:14px; padding:14px; border:1.5px solid #fecdd3; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#9f1239; margin-bottom:8px;">
                ⚠️ Critical Cautions: What to Avoid During Sade Sati
            </div>
            <ul style="margin:0; padding-left:1.25rem; font-size:0.93rem; line-height:1.7; color:#881337;">
                <li><b>Never Mistreat Subordinates:</b> Shani represents the working class, blue-collar staff, cleaners, and laborers. Disrespecting or delaying payment to laborers incurs swift Saturnic karmic penalty.</li>
                <li><b>Avoid Speculative Leverage:</b> Do not engage in debt-fueled day trading, short-selling, or unverified speculative schemes. Shani demands slow, honest compounding.</li>
                <li><b>No Saturday Contracts or Iron Purchases:</b> Do not sign high-stakes real estate contracts, register new partnership deeds, or buy iron, steel cutlery, or real leather items on Saturdays.</li>
                <li><b>Strictly Avoid Intoxicants & Tamasic Habits:</b> Consumption of excessive alcohol, smoking, or deceitful speech severely destabilizes Shani's protective aura.</li>
                <li><b>Never Retaliate With Malice:</b> Shani is the lord of cosmic justice (Nyayakaraka). When wronged, remain dignified and allow cosmic law to handle the outcome.</li>
            </ul>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:10px; border-bottom:1px solid #e9d5ff; padding-bottom:5px;">
                🪔 Authentic Vedic & Puranic Shani Mantras (With Meaning & Count)
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #ddd6fe; margin-bottom:10px;">
                <b style="color:#5b21b6; font-size:0.98rem;">1. Vedic Samhita Shani Mantra (Rigveda / Yajurveda):</b>
                <div style="font-family:serif; font-size:1.05rem; font-weight:700; color:#1e1b4b; margin:6px 0; line-height:1.6;">
                    ॐ शं नो देवीरभिष्टय आपो भवन्तु पीतये। शं योरभि स्रवन्तु नः॥
                </div>
                <div style="font-size:0.88rem; color:#475569; font-style:italic;">
                    <b>Transliteration:</b> Om Sham No Deviir-Abhishtaye Aapo Bhavantu Piitaye | Sham Yor-Abhi Sravantu Nah ||
                </div>
                <div style="font-size:0.9rem; color:#3b0764; margin-top:4px; line-height:1.5;">
                    <b>Meaning & Prescription:</b> "May the divine waters and cosmic energies be propitious for our fulfillment and blessings. May they flow peacefully for our well-being." Chant 11 times on Saturday mornings facing East.
                </div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #ddd6fe; margin-bottom:10px;">
                <b style="color:#5b21b6; font-size:0.98rem;">2. Shani Beej Mantra (Tantrik Vibration):</b>
                <div style="font-family:serif; font-size:1.15rem; font-weight:800; color:#1e1b4b; margin:6px 0;">
                    ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः॥
                </div>
                <div style="font-size:0.88rem; color:#475569; font-style:italic;">
                    <b>Transliteration:</b> Om Praam Preem Proum Sah Shanaishcharaya Namah ||
                </div>
                <div style="font-size:0.9rem; color:#3b0764; margin-top:4px; line-height:1.5;">
                    <b>Meaning & Prescription:</b> The primordial seed vibration that pacifies acute friction, alleviates chronic delays, and shields physical health. Chant 108 times using a Rudraksha or Blue Sandalwood Mala in the evening facing West.
                </div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #ddd6fe;">
                <b style="color:#5b21b6; font-size:0.98rem;">3. Shani Gayatri Mantra (Solar-Saturnic Harmony):</b>
                <div style="font-family:serif; font-size:1.05rem; font-weight:700; color:#1e1b4b; margin:6px 0; line-height:1.6;">
                    ॐ सूर्यपुत्राय विद्महे मृत्युरूपाय धीमहि। तन्नो सौरिः प्रचोदयात्॥
                </div>
                <div style="font-size:0.88rem; color:#475569; font-style:italic;">
                    <b>Transliteration:</b> Om Suryaputraya Vidmahe Mrityuroopaya Dheemahi | Tanno Saurih Prachodayat ||
                </div>
                <div style="font-size:0.9rem; color:#3b0764; margin-top:4px; line-height:1.5;">
                    <b>Meaning & Prescription:</b> Awakes the righteous, disciplined wisdom of Saturn. Chanting 21 times on Saturday evenings dissolves anxiety and fear of the unknown.
                </div>
            </div>
        </div>
    </div>
    """)

    # Interactive Japa Mala Counter Widget
    render_html("""
    <div style="background:#ffffff; border:1.5px solid #ddd6fe; border-radius:16px; padding:1.15rem; margin-top:1.15rem; box-shadow:0 3px 12px rgba(139,92,246,0.06);">
        <div style="font-weight:900; font-size:1.18rem; color:#5b21b6; margin-bottom:4px; display:flex; justify-content:space-between; align-items:center;">
            <span>📿 Interactive Japa Mala Counter (108 Chants)</span>
            <span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">Digital Sadhana</span>
        </div>
        <div style="font-size:0.88rem; color:#64748b; margin-bottom:10px;">
            Tap to count your daily <b>Shani Beej Mantra (ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः)</b> or Maha Mrityunjaya chants directly on screen:
        </div>
    </div>
    """)

    with st.container():
        j_col1, j_col2, j_col3 = st.columns([1.5, 1.2, 1.2])
        with j_col1:
            curr_bead = st.session_state.japa_count
            pct = min(100, int((curr_bead / 108.0) * 100))
            render_html(f"""
            <div style="background:#f5f3ff; border-radius:12px; padding:12px 14px; text-align:center; border:1.5px solid #ddd6fe;">
                <div style="font-size:0.82rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">BEADS COMPLETED</div>
                <div style="font-size:2.2rem; font-weight:900; color:#5b21b6; line-height:1.1;">{curr_bead} <span style="font-size:1.1rem; color:#a78bfa;">/ 108</span></div>
                <div style="font-size:0.82rem; color:#7c3aed; font-weight:700; margin-top:2px;">Mala Progress: {pct}%</div>
            </div>
            """)
        with j_col2:
            if st.button("📿 Tap Bead (+1)", type="primary", use_container_width=True, key="btn_japa_add"):
                if st.session_state.japa_count < 108:
                    st.session_state.japa_count += 1
                else:
                    st.session_state.japa_count = 1
                st.rerun()
        with j_col3:
            if st.button("🔄 Reset Mala", type="secondary", use_container_width=True, key="btn_japa_reset"):
                st.session_state.japa_count = 0
                st.rerun()

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

def render_page_live():
    now_ist = datetime.datetime.now()
    cur_star_idx, s_dt, e_dt = get_current_nakshatra_window(now_ist)
    offset = (cur_star_idx - chart_info["star_idx"]) % 9
    nav_name, icon, quality = NAVTARA_NAMES[offset]
    vahan_info = calculate_shani_vahan(chart_info["star_idx"], cur_star_idx)
    p_day = get_personal_day_vibe(dob_parsed, now_ist.date(), current_lang)

    insights = get_detailed_day_insights(offset, vahan_info, NAKSHATRAS[cur_star_idx - 1], p_day)
    micro_habit = get_daily_micro_habit(cur_star_idx, offset)

    u_lat = prof.get("lat", 19.8762)
    u_lon = prof.get("lon", 75.3433)
    muhurtas = calculate_daily_muhurtas(now_ist.date(), u_lat, u_lon)
    
    abhijit_s, abhijit_e = muhurtas["abhijit"]
    rahu_s, rahu_e = muhurtas["rahu"]
    yama_s, yama_e = muhurtas["yamaganda"]
    brahma_s, brahma_e = muhurtas["brahma"]

    is_abhijit = abhijit_s <= now_ist <= abhijit_e
    is_rahu = rahu_s <= now_ist <= rahu_e
    is_yama = yama_s <= now_ist <= yama_e

    if is_rahu:
        status_banner = f"""
        <div style="background:#fee2e2; border:2px solid #ef4444; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#b91c1c; font-size:1.02rem;">🔴 CAUTION WINDOW ACTIVE: Rahu Kaal in Operation</b>
                <div style="font-size:0.88rem; color:#7f1d1d; margin-top:2px;">Pause new contract signing, travel departures, and major transactions until {rahu_e.strftime('%I:%M %p')}.</div>
            </div>
            <span style="font-size:1.8rem;">🛑</span>
        </div>
        """
    elif is_yama:
        status_banner = f"""
        <div style="background:#fee2e2; border:2px solid #ef4444; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#b91c1c; font-size:1.02rem;">🔴 CAUTION WINDOW ACTIVE: Yamaganda in Operation</b>
                <div style="font-size:0.88rem; color:#7f1d1d; margin-top:2px;">Avoid launching crucial ventures or financial agreements until {yama_e.strftime('%I:%M %p')}.</div>
            </div>
            <span style="font-size:1.8rem;">⚠️</span>
        </div>
        """
    elif is_abhijit:
        status_banner = f"""
        <div style="background:#dcfce7; border:2px solid #22c55e; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#15803d; font-size:1.02rem;">🟢 GOLDEN ACTION WINDOW ACTIVE: Abhijit Muhurta</b>
                <div style="font-size:0.88rem; color:#14532d; margin-top:2px;">Supreme cosmic victory window. Highly auspicious for approvals, launches, and decisions until {abhijit_e.strftime('%I:%M %p')}.</div>
            </div>
            <span style="font-size:1.8rem;">🌟</span>
        </div>
        """
    else:
        status_banner = f"""
        <div style="background:#f0fdf4; border:1.5px solid #86efac; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#166534; font-size:0.98rem;">🟢 SAFE TO ACT: Standard Favorable Orbit</b>
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

        <!-- ATTIRE COLOR OF THE DAY & BIO-SHIELD -->
        <div style="background:#f8fafc; border-radius:12px; padding:14px; border:1.5px solid #cbd5e1; margin-bottom:1.1rem;">
            <div style="font-weight:900; font-size:1.08rem; color:#0f172a; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                <span>🎨 Attire Color of the Day & 2-Minute Bio-Shield</span>
                <span style="font-size:0.8rem; background:#e2e8f0; color:#334155; padding:2px 8px; border-radius:10px; font-weight:800;">{micro_habit['archetype']}</span>
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.92rem;">
                <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #e2e8f0;">
                    <b style="color:#0284c7;">👔 Harmonizing Attire Color:</b><br>
                    <span style="font-weight:800; color:#0f172a; font-size:0.96rem;">{micro_habit['color']}</span><br>
                    <span style="font-size:0.84rem; color:#64748b;">(Resonates with {micro_habit['lord']} frequency)</span>
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #e2e8f0;">
                    <b style="color:#059669;">🌿 2-Minute Grounding Habit:</b><br>
                    <span style="color:#1e293b; font-size:0.88rem; line-height:1.5;">{micro_habit['habit']}</span>
                </div>
            </div>
            <div style="font-size:0.85rem; color:#475569; margin-top:8px; font-style:italic;">
                {micro_habit['caution_cue']}
            </div>
        </div>

        <!-- PRECISION MUHURTA TIMING WINDOWS -->
        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#0369a1; margin-bottom:10px; border-bottom:1px solid #e0f2fe; padding-bottom:5px; display:flex; justify-content:space-between; align-items:center;">
                <span>⏱️ Precision Timing Windows for Today</span>
                <span style="font-size:0.8rem; color:#0284c7; background:#e0f2fe; padding:2px 8px; border-radius:12px; font-weight:800;">{prof['city'].split(',')[0]} Solar Geometry</span>
            </div>

            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:10px; margin-bottom:10px;">
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; border:1px solid #86efac;">
                    <b style="color:#166534; font-size:0.95rem;">🌟 Golden Auspicious Windows:</b>
                    <div style="font-size:0.92rem; color:#14532d; margin-top:5px; line-height:1.6;">
                        • <b>Abhijit Muhurta:</b><br>
                        <span style="font-size:1.05rem; font-weight:900; color:#15803d;">{abhijit_s.strftime('%I:%M %p')} – {abhijit_e.strftime('%I:%M %p IST')}</span><br>
                        <i style="font-size:0.84rem; color:#166534;">(Supreme window for agreements, launches & investments)</i>
                    </div>
                    <div style="font-size:0.92rem; color:#14532d; margin-top:8px; line-height:1.6;">
                        • <b>Brahma Muhurta:</b><br>
                        <span style="font-weight:800; color:#15803d;">{brahma_s.strftime('%I:%M %p')} – {brahma_e.strftime('%I:%M %p IST')}</span><br>
                        <i style="font-size:0.84rem; color:#166534;">(Peak sattvic time for meditation & spiritual grounding)</i>
                    </div>
                </div>

                <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; border:1px solid #fecdd3;">
                    <b style="color:#9f1239; font-size:0.95rem;">⚠️ Caution & Inauspicious Windows:</b>
                    <div style="font-size:0.92rem; color:#881337; margin-top:5px; line-height:1.6;">
                        • <b>Rahu Kaal (Avoid Signings):</b><br>
                        <span style="font-size:1.05rem; font-weight:900; color:#be123c;">{rahu_s.strftime('%I:%M %p')} – {rahu_e.strftime('%I:%M %p IST')}</span><br>
                        <i style="font-size:0.84rem; color:#9f1239;">(Pause high-risk trades, signing deeds & departures)</i>
                    </div>
                    <div style="font-size:0.92rem; color:#881337; margin-top:8px; line-height:1.6;">
                        • <b>Yamaganda (Delays):</b><br>
                        <span style="font-weight:800; color:#be123c;">{yama_s.strftime('%I:%M %p')} – {yama_e.strftime('%I:%M %p IST')}</span><br>
                        <i style="font-size:0.84rem; color:#9f1239;">(Avoid starting brand-new critical ventures)</i>
                    </div>
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

def render_page_forecast():
    now_ist = datetime.datetime.now()
    transits = get_7_day_moon_transits(now_ist, chart_info["star_idx"])
    heatmap_items, power_day = get_7_day_heatmap_and_power_day(transits)

    render_html(f"""
    <div style="font-weight:900; font-size:1.25rem; color:#1e293b; margin-bottom:0.8rem;">
        {t('forecast_title', current_lang)}
    </div>
    """)

    heatmap_cards_html = "".join([
        f"""<div style="background:{h['bg']}; border:1.5px solid {h['border']}; border-radius:10px; padding:8px 6px; text-align:center; min-width:68px; flex:1;">
            <div style="font-size:0.78rem; font-weight:800; color:{h['text']};">{h['day']}</div>
            <div style="font-size:0.86rem; font-weight:900; color:#0f172a;">{h['date']}</div>
            <div style="font-size:0.75rem; color:#475569; margin:2px 0;">{h['star']}</div>
            <div style="font-size:0.72rem; font-weight:800; color:{h['text']};">{h['badge']}</div>
        </div>""" for h in heatmap_items
    ])

    v_pname = power_day['vahan'].split()[1] if len(power_day['vahan'].split()) > 1 else power_day['vahan']
    render_html(f"""
    <!-- 7-Day Visual Energy Heatmap Strip -->
    <div style="background:#ffffff; border-radius:14px; padding:12px; border:1.5px solid #e2e8f0; margin-bottom:12px; box-shadow:0 2px 8px rgba(0,0,0,0.03);">
        <div style="font-weight:900; font-size:0.95rem; color:#334155; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <span>📊 Weekly Transit Energy Heatmap</span>
            <span style="font-size:0.8rem; color:#64748b;">(7-Day Glance)</span>
        </div>
        <div style="display:flex; gap:6px; overflow-x:auto; padding-bottom:4px;">
            {heatmap_cards_html}
        </div>
    </div>

    <!-- Power Day of the Week Banner -->
    <div style="background:linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border:2px solid #22c55e; border-radius:14px; padding:12px 14px; margin-bottom:16px; box-shadow:0 4px 12px rgba(34,197,94,0.12);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <b style="color:#15803d; font-size:1.05rem;">🌟 Power Day of the Week: {power_day['date_str']}</b>
            <span style="font-size:0.82rem; background:#22c55e; color:#ffffff; padding:3px 8px; border-radius:12px; font-weight:800;">PEAK VIBRATION</span>
        </div>
        <div style="font-size:0.92rem; color:#14532d; margin-top:4px; line-height:1.5;">
            Moon transits <b>{power_day['star_name']}</b> activating <b>{power_day['nav_name']}</b> (Mount: {v_pname}). This is your highest-leverage window this week for high-stakes agreements, capital investments, key negotiations, and major career initiatives.
        </div>
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

    u_lat = prof.get("lat", 19.8762)
    u_lon = prof.get("lon", 75.3433)
    sel_muh = calculate_daily_muhurtas(sel_tr['date'], u_lat, u_lon)

    render_html(f"""
    <div class="light-card-live" style="margin-top:1.1rem;">
        <div style="font-weight:900; font-size:1.25rem; color:#0369a1; margin-bottom:8px; border-bottom:1.5px solid #bae6fd; padding-bottom:5px;">
            🔮 Detailed Transit Forecast: {sel_tr['date_str']} ({sel_tr['star_name']})
        </div>
        
        <div style="font-size:0.94rem; color:#334155; margin-bottom:12px; line-height:1.5;">
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
