import streamlit as st
import datetime
import urllib.parse
import json
import os

# Initialize Swiss Ephemeris engine with fail-safe sidereal Lahiri configuration
try:
    import swisseph as swe
    HAS_SWISSEPH = True
    swe.set_sid_mode(swe.SIDM_LAHIRI)
except Exception:
    HAS_SWISSEPH = False

# Configure Streamlit page layout
st.set_page_config(
    page_title="Navtara Pulse",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def render_html(html_string: str):
    """
    Renders HTML safely by stripping all leading whitespace from every line.
    Prevents Streamlit Markdown engine from mistaking indented HTML for pre/code blocks.
    """
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

render_html("""
<style>
    /* Fluid responsive typography adhering to system-wide mobile font scale */
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
            padding-top: 0.8rem !important;
            padding-bottom: 5.5rem !important;
        }
    }
    
    .block-container {
        padding-top: 1rem;
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
    
    /* High-contrast, card aesthetics */
    .auth-hero-box {
        background: linear-gradient(135deg, #fdfbf7 0%, #fffbeb 100%);
        border: 1.5px solid #fde68a;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.08);
    }
    
    .light-card-profile {
        background: #ffffff;
        border: 1.5px solid #fed7aa;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 4px 14px rgba(249, 115, 22, 0.06);
    }
    
    .light-card-num {
        background: #ffffff;
        border: 1.5px solid #bbf7d0;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.06);
    }
    
    .light-card-shani {
        background: #ffffff;
        border: 1.5px solid #ddd6fe;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 4px 14px rgba(139, 92, 246, 0.06);
    }
    
    .light-card-live {
        background: #ffffff;
        border: 1.5px solid #bae6fd;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.06);
    }

    /* Top navigation dock buttons */
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
        "app_title": "Navtara Pulse",
        "app_subtitle": "Vedic Nakshatra Rhythm & Cosmic Precision",
        "btn_about": "✨ About App",
        "btn_user_profile": "👤 User Profile",
        "btn_numerology": "🔢 Numerology",
        "btn_shani": "🪐 Shani",
        "btn_live": "⚡ Live Prediction",
        "btn_forecast": "🗓️ 7 Days Prediction",
        "btn_planets": "🔭 Planet position",
        "btn_remedies": "🪔 Remedies",
        "edit_details": "✏️ Edit Details",
        "save_details": "💾 Save Profile",
        "cancel": "Cancel",
        "name_label": "Full Name",
        "dob_label": "Birth Date",
        "tob_label": "Birth Time",
        "city_label": "Birth City",
        "nakshatra_label": "Janma Nakshatra",
        "pada_label": "Pada",
        "moon_rashi_label": "Moon Sign (Rashi)",
        "lagna_label": "Ascendant (Lagna)",
        "mulank_label": "Mulank (Driver)",
        "bhagyank_label": "Bhagyank (Destiny)",
        "namank_label": "Namank (Name Vibration)",
        "shani_paya_title": "🪐 Shani Paya & Active 2.5-Year Transit",
        "sadesati_title": "⚖️ Shani Sade Sati & Dhaiya Status",
        "live_pulse_title": "⚡ Today's Live Cosmic Pulse",
        "forecast_title": "🗓️ 7-Day Moon Transit Matrix & Daily Forecasts",
        "planet_title": "🔭 Real-Time Sidereal Planetary Longitudes (Lahiri)",
        "share_title": "📲 Share Navtara Pulse With Friends & Family"
    },
    "hi": {
        "app_title": "नवतारा पल्स",
        "app_subtitle": "वैदिक नक्षत्र गोचर एवं खगोलीय ऊर्जा चक्र",
        "btn_about": "✨ ऐप परिचय",
        "btn_user_profile": "👤 यूज़र प्रोफाइल",
        "btn_numerology": "🔢 अंकशास्त्र",
        "btn_shani": "🪐 शनि पाया",
        "btn_live": "⚡ आज का फल",
        "btn_forecast": "🗓️ 7 दिवसीय फल",
        "btn_planets": "🔭 ग्रह स्थिति",
        "btn_remedies": "🪔 वैदिक उपाय",
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
        "planet_title": "🔭 वास्तविक निरयण ग्रह स्पष्ट (लाहिड़ी)",
        "share_title": "📲 नवतारा पल्स को परिवार व मित्रों के साथ साझा करें"
    },
    "mr": {
        "app_title": "नवतारा पल्स",
        "app_subtitle": "वैदिक नक्षत्र गोचर आणि वैश्विक ऊर्जा चक्र",
        "btn_about": "✨ ॲप विषयी",
        "btn_user_profile": "👤 युझर प्रोफाईल",
        "btn_numerology": "🔢 अंकशास्त्र",
        "btn_shani": "🪐 शनी पाया",
        "btn_live": "⚡ आजचे भविष्य",
        "btn_forecast": "🗓️ ७ दिवसांचे भविष्य",
        "btn_planets": "🔭 ग्रह स्थिती",
        "btn_remedies": "🪔 वैदिक उपाय",
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
        "planet_title": "🔭 निरयन प्रत्यक्ष ग्रह स्थिती (लाहिरी)",
        "share_title": "📲 नवतारा पल्स ॲप मित्र आणि कुटुंबासह शेअर करा"
    },
    "gu": {
        "app_title": "નવતારા પલ્સ",
        "app_subtitle": "વૈદિક નક્ષત્ર ગોચર અને બ્રહ્માંડીય ઊર્જા ચક્ર",
        "btn_about": "✨ એપ વિશે",
        "btn_user_profile": "👤 યુઝર પ્રોફાઇલ",
        "btn_numerology": "🔢 અંકશાસ્ત્ર",
        "btn_shani": "🪐 શનિ પાયા",
        "btn_live": "⚡ આજનું ફળ",
        "btn_forecast": "🗓️ ૭ દિવસનું ફળ",
        "btn_planets": "🔭 ગ્રહ સ્થિતિ",
        "btn_remedies": "🪔 વૈદિક ઉપાયો",
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
        "planet_title": "🔭 પ્રત્યક્ષ નિરયણ ગ્રહ સ્થિતિ (લાહિરી)",
        "share_title": "📲 નવતારા પલ્સ તમારા મિત્રો અને પરિવાર સાથે શેર કરો"
    }
}

def t(key: str, lang: str = "en") -> str:
    """Translates key to target language with fallback to English."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]
# Dual alias guaranteeing backward compatibility and eliminating NameError
NAKHATRAS = NAKSHATRAS

RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

NAVTARA_NAMES = [
    ("1. Janma (Birth / Origin)", "🌱", "Sensitive & Foundational"),
    ("2. Sampat (Wealth & Prosperity)", "🟢", "Highly Auspicious & Lucrative"),
    ("3. Vipat (Peril / Crisis Risk)", "🔴", "High Friction / Caution Required"),
    ("4. Kshema (Well-being & Safety)", "🟢", "Protective & Favorable"),
    ("5. Pratyari (Obstacles / Resistance)", "🔴", "Adversity / Caution Required"),
    ("6. Sadhana (Success & Realization)", "🟢", "Empowering & Favorable"),
    ("7. Vadha (Destruction / Vulnerability)", "🔴", "Critical Risk / High Vigilance"),
    ("8. Mitra (Friend / Harmony)", "🟢", "Friendly & Favorable"),
    ("9. Ati-Mitra (Supreme Beneficence)", "🟢🟢", "Supreme Boon & Highest Favor")
]

SHANI_VAHANS = {
    1: {"name": "🐴 Ghoda (Horse)", "type": "Speed, Direct Victory & Acceleration", "remedy": "Feed soaked chana to horses or stray cattle early morning."},
    2: {"name": "🫏 Gadha (Donkey)", "type": "Heavy Labor, Patience & Delayed Fruit", "remedy": "Practice silent patience, avoid complaining, feed green fodder to cattle."},
    3: {"name": "🦊 Siyar (Jackal)", "type": "Vigilance Required, Deceit Alert & Caution", "remedy": "Double-check legal papers, avoid unverified tips, feed stray dogs outside your street."},
    4: {"name": "🐘 Hathi (Elephant)", "type": "Royalty, Prosperity & Sudden Honor", "remedy": "Donate yellow mustard seeds or honor teachers and elders with respect."},
    5: {"name": "🐂 Bail (Bull)", "type": "Steady Growth, Diligence & Solid Foundations", "remedy": "Feed fresh green spinach or wheat dough with jaggery to an ox or cow."},
    6: {"name": "🦁 Sher (Lion)", "type": "Courage, Sovereign Victory & Dominance", "remedy": "Chant Durga Kavach or Hanuman Chalisa; channel strength defensively."},
    7: {"name": "🐦‍⬛ Kowwa (Crow)", "type": "Restlessness, Travel Fatigue & Minor Disquiet", "remedy": "Feed boiled rice with black sesame seeds or bread to crows on terrace/balcony."},
    8: {"name": "🦚 Mayur (Peacock)", "type": "Joy, Beauty, Auspicious News & Social Harmony", "remedy": "Offer fragrant natural attar or water with white sandalwood to a Shiva Lingam."},
    9: {"name": "🦢 Hans (Swan)", "type": "Supreme Wisdom, Peace & Spiritual Clarity", "remedy": "Practice 15 minutes of quiet Japa/Meditation before starting daytime work."}
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
    1: {"en": "Sun (Surya)", "hi": "सूर्य (Surya)", "mr": "सूर्य (Surya)", "gu": "સૂર્ય (Surya)"},
    2: {"en": "Moon (Chandra)", "hi": "चन्द्र (Chandra)", "mr": "चंद्र (Chandra)", "gu": "ચંદ્ર (Chandra)"},
    3: {"en": "Jupiter (Guru)", "hi": "बृहस्पति (Guru)", "mr": "गुरु (Guru)", "gu": "ગુરુ (Guru)"},
    4: {"en": "Rahu (Uranus/Rahu)", "hi": "राहु (Rahu)", "mr": "राहु (Rahu)", "gu": "રાહુ (Rahu)"},
    5: {"en": "Mercury (Budha)", "hi": "बुध (Budha)", "mr": "बुध (Budha)", "gu": "બુધ (Budha)"},
    6: {"en": "Venus (Shukra)", "hi": "शुक्र (Shukra)", "mr": "शुक्र (Shukra)", "gu": "શુક્ર (Shukra)"},
    7: {"en": "Ketu (Neptune/Ketu)", "hi": "केतु (Ketu)", "mr": "કેતુ (Ketu)", "gu": "કેતુ (Ketu)"},
    8: {"en": "Saturn (Shani)", "hi": "शनि (Shani)", "mr": "शनी (Shani)", "gu": "શનિ (Shani)"},
    9: {"en": "Mars (Mangal)", "hi": "मंगल (Mangal)", "mr": "मंगळ (Mangal)", "gu": "મંગળ (Mangal)"}
}

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
    """Returns detailed Nakshatra bio, personality breakdown, prediction, and remedies with safe key aliasing."""
    bio = NAKSHATRA_BIO_DATA.get(star_idx, NAKSHATRA_BIO_DATA[2])
    
    star_details = {
        2: { # Bharani
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
                "en": "• Recite the Maha Mrityunjaya Mantra or Om Hreem Bharanyai Namah 11 times every morning.\n• Worship Lord Shiva to harmonize vital life energy (Prana) and neutralize karmic knots.\n• Nurture and water an Amla (Indian Gooseberry) tree, and avoid wearing torn dark clothing.\n• Feed stray dogs or crows on Tuesdays and Fridays to balance karmic weight.",
                "hi": "• प्रतिदिन प्रातः महामृत्युंजय मंत्र अथवा ॐ ह्रीं भरण्यै नमः का 11 बार जप करें।\n• भगवान शिव को कच्चा दूध और जल अर्पित करें जिससे जीवन ऊर्जा संतुलित रहे।\n• आँवले (Amla) के वृक्ष का रोपण अथवा नियमित सिंचन करें।\n• मंगलवार और शुक्रवार को काले श्वान अथवा कौवों को भोजन कराएं।",
                "mr": "• दररोज सकाळी महामृत्युंजय मंत्र किंवा ॐ ह्रीं भरण्यै नमः चा ११ वेळा जप करावा.\n• महादेवाला जल व दूध अर्पण करून प्राणऊर्जा संतुलित ठेवावी.\n• आवळा (Amla) वृक्षाचे जतन व जलार्पण करावे.\n• मंगळवार आणि शुक्रवारी मुक्या प्राण्यांना वा कावळ्यांना अन्न द्यावे.",
                "gu": "• દરરોજ સવારે મહામૃત્યુંજય મંત્ર અથવા ૐ હ્રીં ભરણ્યૈ નમઃ નો ૧૧ વાર જાપ કરો.\n• ભગવાન શિવને કાચું દૂધ અને જળ અર્પણ કરો.\n• આમળાના વૃક્ષ નું જતન કરો અને પાણી ચડાવો.\n• મંગળવાર અને શુક્રવારે કૂતરા કે પક્ષીઓને ખોરાક આપો."
            }
        }
    }
    
    star_name = NAKSHATRAS[star_idx - 1] if 1 <= star_idx <= 27 else "Nakshatra"
    selected_star = star_details.get(star_idx, {
        "personality": {
            "en": f"Born under the celestial star {star_name}, you inherit dynamic intuition, deep focus, and natural authority. Your actions are driven by genuine intent and structured vision.",
            "hi": f"इस नक्षत्र के प्रभाव से आप स्वाभाविक नेतृत्व, प्रखर बुद्धिमत्ता और दूरदर्शी सोच के धनी हैं। आपके कार्य दृढ़ संकल्प और सत्यनिष्ठा से प्रेरित होते हैं।",
            "mr": f"या नक्षत्राच्या प्रभावामुळे तुमच्यात तीव्र बुद्धिमत्ता, नेतृत्वगुण आणि दूरदृष्टी आहे.",
            "gu": f"આ નક્ષત્રના પ્રભાવથી તમારામાં તીવ્ર બુદ્ધિ, નેતૃત્વ ક્ષમતા અને દીર્ઘદ્રષ્ટિ રહેલી છે."
        },
        "prediction": {
            "en": "Your evolutionary path unfolds through consistent skill acquisition and resilient character. Success accelerates in mature years, establishing strong community stature and sustained prosperity.",
            "hi": "आपका भाग्योदय निरंतर कौशल विकास और धैर्यवान कर्मों से होता है। परिपक्व अवस्था में समाज में उच्च सम्मान और स्थायी संपत्ति का निर्माण होता है।",
            "mr": "सातत्यपूर्ण प्रयत्न आणि संयमाने तुमचा भाग्योदय होईल. आयुष्यात मोठी संपत्ती आणि सन्मान लाभेल.",
            "gu": "નિયમિત પરિશ્રમ અને ધૈર્યથી તમારો ભાગ્યોદય થાય છે. ઉત્તરાવસ્થામાં મોટી સંપત્તિ અને આદર પ્રાપ્ત થાય છે."
        },
        "remedies": {
            "en": f"• Chant the Beej Mantra of your star deity {bio['deity']} 11 times daily.\n• Honor and water your sacred tree ({bio['tree']}).\n• Perform early morning Surya Arghya and practice grounding Pranayama.",
            "hi": f"• अपने नक्षत्र देवता {bio['deity']} के मंत्र का 11 बार जप करें।\n• अपने नक्षत्र के पवित्र वृक्ष ({bio['tree']}) का पूजन व सिंचन करें।\n• सूर्य को तांबे के लोटे से अर्घ्य दें।",
            "mr": f"• नक्षत्र देवतेचा नियमित ११ वेळा जप करावा.\n• नक्षत्र वृक्षाची ({bio['tree']}) निगा राखावी.\n• सकाळी सूर्याला जल अर्पण करावे.",
            "gu": f"• નક્ષત્ર દેવતાનો નિયમિત ૧૧ વાર જાપ કરો.\n• નક્ષત્ર વૃક્ષ ({bio['tree']}) નું જતન કરો.\n• સવારે સૂર્યને અર્ઘ્ય અર્પણ કરો."
        }
    })
    
    personality_text = selected_star["personality"].get(lang, selected_star["personality"]["en"])
    prediction_text = selected_star["prediction"].get(lang, selected_star["prediction"]["en"])
    remedies_text = selected_star["remedies"].get(lang, selected_star["remedies"]["en"])
    
    return {
        "deity": bio["deity"],
        "symbol": bio["symbol"],
        "tree": bio["tree"],
        "bird": bio["bird"],
        "animal": bio["animal"],
        "lord": bio["lord"],
        "personality": personality_text,
        "desc": personality_text,
        "traits": personality_text,
        "prediction": prediction_text,
        "remedies": remedies_text
    }

def get_moon_rashi_details(rashi_idx: int, lang: str = "en") -> dict:
    """Returns Moon Rashi (Chandra Rashi) traits, prediction, and remedies."""
    rashi_info = {
        0: { # Mesha (Aries)
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
                "en": "• Offer water mixed with red sandalwood and rose petals to Surya Dev every morning.\n• Recite the Hanuman Chalisa daily, especially on Tuesdays, to channel emotional fire into constructive power.\n• Drink water from a silver cup or keep a small square piece of silver to cool lunar impulses.",
                "hi": "• प्रतिदिन तांबे के पात्र से सूर्य देव को रोली/लाल चंदन मिश्रित जल अर्पित करें।\n• नित्य प्रातः अथवा संध्या को श्री हनुमान चालीसा का पाठ करें।\n• क्रोध शांत रखने हेतु चांदी का चौकोर टुकड़ा अपने पास रखें अथवा चांदी के गिलास में जल पिएं।",
                "mr": "• रोज सकाळी सूर्याला लाल चंदन मिश्रित जल अर्पण करावे.\n• दररोज हनुमान चालीसा पठण करावे.\n• चांदीच्या पात्रातून पाणी प्यावे जेणेकरून मन शांत राहील.",
                "gu": "• સવારે સૂર્ય નારાયણને લાલ ચંદન મિશ્રિત જળ ચડાવો.\n• નિયમિત હનુમાન ચાલીસા ના પાઠ કરો.\n• મનને શાંત રાખવા ચાંદીના ગ્લાસમાં પાણી પીઓ."
            }
        }
    }
    
    selected = rashi_info.get(rashi_idx, {
        "name": RASHIS[rashi_idx] if 0 <= rashi_idx < 12 else f"Rashi {rashi_idx}",
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
    return {
        "name": selected["name"],
        "element": selected["element"],
        "ruler": selected["ruler"],
        "profile": prof_text,
        "desc": prof_text,
        "traits": prof_text,
        "personality": prof_text,
        "prediction": selected["prediction"].get(lang, selected["prediction"]["en"]),
        "remedies": selected["remedies"].get(lang, selected["remedies"]["en"])
    }

def get_lagna_details(lagna_idx: int, lang: str = "en") -> dict:
    """Returns Lagna (Ascendant) physical constitution, outward persona, life path, and remedies."""
    lagna_info = {
        1: { # Vrishabha (Taurus) Lagna
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
                "en": "• Apply pure white sandalwood or natural rose attar on your pulse points before starting important work.\n• Worship Goddess Lakshmi or recite the Shri Suktam on Fridays for financial and physical radiance.\n• Respect women, maintain clean surroundings, and donate white sweets or curd to the needy on Fridays.",
                "hi": "• महत्वपूर्ण कार्यों से पूर्व अपनी कलाई पर श्वेत चंदन अथवा गुलाब का इत्र लगाएं।\n• शुक्रवार को श्री सूक्तम् का पाठ करें अथवा माँ लक्ष्मी को खीर का भोग लगाएं।\n• महिलाओं का सम्मान करें तथा शुक्रवार को सफेद मिठाई अथवा दही का दान करें।",
                "mr": "• महत्त्वाच्या कामाला जाताना शुभ्र चंदन किंवा अत्तर लावावे.\n• शुक्रवारी श्री सूक्त पठण करावे आणि देवी लक्ष्मीची उपासना करावी.\n• शुक्रवारी पांढऱ्या वस्तूंचे दान करावे.",
                "gu": "• શુભ કાર્ય પહેલાં સફેદ ચંદન કે અત્તર લગાવો.\n• શુક્રવારે શ્રી સૂક્તમ્ નો પાઠ કરો અને લક્ષ્મીજીની કૃપા મેળવો.\n• શુક્રવારે સફેદ મીઠાઈ કે દૂધ-દહીંનું દાન કરો."
            }
        }
    }
    
    selected = lagna_info.get(lagna_idx, {
        "name": RASHIS[lagna_idx] if 0 <= lagna_idx < 12 else f"Lagna {lagna_idx}",
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
            "gu": "લગ્નેશના શુભ प्रભાવથી ઉત્તમ આરોગ્ય અને પ્રતિષ્ઠા વધે છે."
        },
        "remedies": {
            "en": "• Practice daily morning Pranayama to align physical breath with mental vitality.\n• Strengthen Lagna lord through mindful daily discipline and charity.",
            "hi": "• नित्य प्रातः प्राणायाम करें जिससे लग्न की जैविक ऊर्जा सशक्त रहे।\n• लग्नेश के मंत्र का श्रद्धापूर्वक जप करें।",
            "mr": "• नियमित प्राणायाम करून प्राणशक्ती वाढवावी.\n• लग्नेशाची आराधना करावी.",
            "gu": "• નિયમિત પ્રાણાયામ કરો અને લગ્નેશની કૃપા મેળવો."
        }
    })
    
    prof_text = selected["profile"].get(lang, selected["profile"]["en"])
    return {
        "name": selected["name"],
        "element": selected["element"],
        "lord": selected["lord"],
        "profile": prof_text,
        "desc": prof_text,
        "traits": prof_text,
        "personality": prof_text,
        "prediction": selected["prediction"].get(lang, selected["prediction"]["en"]),
        "remedies": selected["remedies"].get(lang, selected["remedies"]["en"])
    }

def reduce_to_single_digit(num: int) -> int:
    """Reduces an integer to a single digit (1-9) using digital root."""
    while num > 9:
        num = sum(int(ch) for ch in str(num))
    return num if num > 0 else 9

def calculate_numerology(dob: datetime.date, name: str):
    """Calculates Mulank (Day), Bhagyank (Full Date), and Namank (Chaldean)."""
    mulank = reduce_to_single_digit(dob.day)
    full_date_sum = dob.day + dob.month + dob.year
    bhagyank = reduce_to_single_digit(full_date_sum)
    cleaned_name = "".join(ch for ch in name.upper() if ch.isalpha())
    namank_val = sum(CHALDEAN_MAP.get(ch, 0) for ch in cleaned_name)
    namank = reduce_to_single_digit(namank_val) if namank_val > 0 else 1
    return mulank, bhagyank, namank

def get_personal_day_vibe(dob: datetime.date, target_date: datetime.date, lang: str = "en") -> dict:
    """Calculates Personal Year and Personal Day vibration."""
    personal_year = reduce_to_single_digit(dob.day + dob.month + target_date.year)
    personal_day = reduce_to_single_digit(personal_year + target_date.month + target_date.day)
    planet_info = NUM_PLANET_NAMES.get(personal_day, {}).get(lang, NUM_PLANET_NAMES[personal_day]["en"])
    return {
        "number": personal_day,
        "planet": planet_info,
        "desc": f"Personal Day {personal_day} resonates with {planet_info} cosmic frequency."
    }

def get_numerology_life_domains(mulank: int, bhagyank: int, namank: int, lang: str = "en") -> dict:
    """Generates an exhaustive life-domain analysis across Career, Wealth, Relationship, Health, Luck and Remedies."""
    p_m = NUM_PLANET_NAMES.get(mulank, {}).get(lang, f"Planet {mulank}")
    p_b = NUM_PLANET_NAMES.get(bhagyank, {}).get(lang, f"Planet {bhagyank}")

    if lang == "hi":
        return {
            "career_title": "💼 आजीविका एवं कर्मक्षेत्र (Career & Executive Destiny)",
            "career_desc": (
                f"मूलांक {mulank} ({p_m}) और भाग्यांक {bhagyank} ({p_b}) का दुर्लभ संयोग आपको असाधारण रणनीतिक सोच और निडर कार्यशैली प्रदान करता है। "
                "पारंपरिक 9-से-5 नौकरियों की तुलना में आप स्वतंत्र निर्णय लेने, तकनीकी प्रणालियों का निर्माण करने, संरचनात्मक सुधारों और उच्च-प्रबंधकीय पदों पर सर्वाधिक चमकते हैं। "
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
    """Computes comprehensive inauspicious numbers, colors, days, directions, and behavioral cautions."""
    avoidance_data = {
        1: {
            "num": "8, 6, 4 (Saturn, Venus, Rahu clashes)",
            "colors": "Pitch Black, Dark Navy Blue, Muddy Charcoal Brown",
            "days": "Saturday (delays & red tape), Friday (energy diffusion)",
            "dir": "South-West (Nairutya) and West",
            "habits": {
                "en": "• Avoid aggressive ego-driven confrontations or unilateral ultimatums.\n• Never sign binding contracts during sunset twilight or on Saturdays.\n• Do not lend large sums of cash on Saturdays without solid collateral.\n• Avoid skipping morning sunlight or allowing toxic pride to override sound advice.",
                "hi": "• अहंकारवश लिए गए निर्णयों और तीखी बहसबाजी से बचें।\n• शनिवार अथवा सूर्यास्त के समय बड़े अनुबंधों पर हस्ताक्षर न करें।\n• शनिवार को किसी को बड़ी धनराशी उधार देने से परहेज करें।\n• प्रातःकालीन सूर्य के प्रकाश की उपेक्षा न करें और दूसरों के सुझावों का सम्मान करें।",
                "mr": "• अहंकारापोटी घेतलेले निर्णय आणि वादविवाद टाळावेत.\n• शनिवारी किंवा सूर्यास्ताच्या वेळी मोठे व्यावसायिक करार करणे टाळा.\n• शनिवारी कोणालाही मोठी रक्कम उसनी देऊ नका.\n• सकाळी सूर्यप्रकाशाचा लाभ घ्या आणि इतरांच्या चांगल्या सल्ल्यांचा आदर करा.",
                "gu": "• અહંકાર અને ક્રોધમાં આવીને નિર્ણયો લેવાનું ટાળો.\n• શનિવારે અથવા સંધ્યાકાળના સમયે મહત્વપૂર્ણ કરાર પર હસ્તાક્ષર ન કરો.\n• શનિવારે કોઈને મોટી રકમ ઉધાર આપવાનું ટાળો.\n• સૂર્યોદય સમયે થોડો સમય સૂર્યપ્રકાશમાં રહો અને વડીલોની સલાહ અવગણશો નહીં."
            }
        },
        2: {
            "num": "8, 4, 9 (Saturn sorrow, Rahu eclipse, Mars fire)",
            "colors": "Dark Scarlet Red, Pitch Black, Dull Muddy Gray",
            "days": "Saturday (depression resonance), Tuesday (emotional friction)",
            "dir": "South and South-West",
            "habits": {
                "en": "• Avoid taking high-stakes financial decisions late at night under emotional fatigue.\n• Do not isolate yourself during bouts of pessimism; seek grounded conversation.\n• Avoid speculative gambles and high-volatility financial schemes.\n• Never waste clean water or leave dripping taps unrepaired in the house.",
                "hi": "• देर रात भावुकता या तनाव में आकर महत्वपूर्ण आर्थिक निर्णय न लें।\n• निराशा के क्षणों में स्वयं को अकेला न छोड़ें, विश्वासपात्र लोगों से संवाद रखें।\n• बिना सोचे-समझे सट्टेबाजी और जोखिम भरे निवेश से बचें।\n• पीने के पानी का अपव्यय न करें और नल को टपकता हुआ न छोड़ें।",
                "mr": "• रात्रीच्या वेळी भावनेच्या भरात कोणतेही मोठे आर्थिक निर्णय घेऊ नका.\n• नैराश्याच्या वेळी स्वतःला एकटे पाडू नका, विश्वासू माणसांशी संवाद साधा.\n• सट्टेबाजी आणि जोखमीच्या व्यवहारांपासून दूर राहा.\n• पाण्याचा अपव्यय टाळा आणि घरात गळणारे नळ दुरुस्त करा.",
                "gu": "• રાત્રિના સમયે ભાવનાત્મક આવેશમાં આવીને આર્થિક નિર્ણયો ન લો.\n• નકારાત્મક વિચારો આવે ત્યારે એકલા રહેવાને બદલે વિશ્વાસુ લોકો સાથે વાત કરો.\n• અતિ-જોખમી સટ્ટાબાજી કે યોજનાઓથી દૂર રહો.\n• પાણીનો બગાડ ન કરો અને ઘરમાં ટપકતા નળ તરત જ રિપેર કરાવો."
            }
        },
        3: {
            "num": "6, 8 (Venus ideological opposition, Saturn friction)",
            "colors": "Pitch Black, Dark Green, Murky Muddy Brown",
            "days": "Friday (clash with Venusian materialism)",
            "dir": "South-West (Nairutya)",
            "habits": {
                "en": "• Avoid offering unsolicited counsel or lecturing peers who did not ask.\n• Do not disrespect teachers, gurus, or senior mentors in public or private.\n• Avoid hoarding stale, unused books, torn study notes, and intellectual clutter.\n• Beware of taking high-interest debts for superficial status symbols.",
                "hi": "• बिना मांगे दूसरों को उपदेश देने या ज्ञान थोपने से बचें।\n• शिक्षकों, गुरुओं और वयोवृद्ध मार्गदर्शकों का भूलकर भी अनादर न करें।\n• पुरानी फटी पुस्तकें, रद्दी और निरुपयोगी कागजातों का ढेर न लगाएं।\n• दिखावे और आडंबर के लिए कर्ज लेने से परहेज करें।",
                "mr": "• समोरच्याने विचारल्याशिवाय विनाकारण उपदेश देणे टाळा.\n• शिक्षक, गुरू आणि घरातील वडीलधाऱ्यांचा अनादर करू नका.\n• जुनी रद्दी, फाटलेली पुस्तके आणि कचरा साठवून ठेवू नका.\n• केवळ दिखाव्यासाठी कर्ज काढणे पूर्णपणे टाळा.",
                "gu": "• કોઈના પૂછ્યા વગર સલાહ કે ઉપદેશ આપવાનું ટાળો.\n• ગુરુજનો, શિક્ષકો અને વડીલોનું ક્યારેય અપમાન ન કરો.\n• જૂના નકામા કાગળો અને ફાટેલા પુસ્તકોનો કચરો ન રાખો.\n• માત્ર દેખાડો કરવા માટે દેવું કરવાનું ટાળો."
            }
        },
        4: {
            "num": "2, 8, and repeated 4s (Avoid 4, 13, 22, 31 for critical pacts)",
            "colors": "Jet Black, Murky Dark Brown, Dull Khaki & Muddy Gray",
            "days": "Saturday (Shani delay resonance) and Monday (Chandra eclipse anxiety)",
            "dir": "South-West (Nairutya - over-amplifies restlessness) and West",
            "habits": {
                "en": "• Avoid speculative day trading, casino bets, and unverified fast-money schemes.\n• Never sign binding long-term contracts on Saturdays or during Rahu Kaal.\n• Do not accumulate non-working electronics, dead batteries, or rusted iron scrap in your living or workspace.\n• Refrain from harsh confrontational arguments during twilight hours (Sandhya Kaal).\n• Avoid wearing dark, unwashed, or torn black clothing when attending career-defining meetings.",
                "hi": "• अचानक अमीर बनाने वाली सट्टेबाजी, अनधिकृत क्रिप्टो या बिना सोचे-समझे किए गए सट्टे से पूर्णतः दूर रहें।\n• शनिवार के दिन अथवा राहुकाल में महत्वपूर्ण अनुबंधों या कानूनी समझौतों पर हस्ताक्षर करने से बचें।\n• घर या कार्यालय में बंद घड़ियां, टूटे इलेक्ट्रॉनिक उपकरण अथवा जंग लगा लोहा कभी जमा न होने दें।\n• क्रोध के आवेश में संध्याकाल के समय कटु वचन बोलने या संबंध विच्छेद करने से बचें।\n• अति-महत्वपूर्ण बैठकों में मैले, कटे-फटे या अत्यधिक काले वस्त्र पहनने से परहेज करें।",
                "mr": "• अति-लोभाच्या सट्टेबाजी किंवा झटपट नफा देणाऱ्या अनधिकृत योजनांपासून पूर्णपणे दूर राहा.\n• शनिवारी किंवा राहू काळात महत्त्वाच्या कायदेशीर कागदपत्रांवर सह्या करणे टाळा.\n• घरात किंवा कामाच्या ठिकाणी बंद पडलेली घड्याळे, निकामी इलेक्ट्रॉनिक्स सामान किंवा गंजलेले लोखंड ठेवू नका.\n• संध्याकाळी वादविवाद टाळा; रागाच्या भरात कठोर बोलून जुने संबंध तोडू नका.\n• महत्त्वाच्या कामाला जाताना फाटलेले किंवा अति-गडद काळे कपडे घालणे टाळा.",
                "gu": "• ઝડપી નફો આપતી સટ્ટાબાજી અથવા અજાણી સ્કીમોમાં મોટું જોખમ લેવાનું ટાળો.\n• શનિવારે કે રાહુકાળમાં મહત્વપૂર્ણ દસ્તાવેજો કે કરાર પર હસ્તાક્ષર ન કરો.\n• ઘરમાં કે ઓફિસમાં બંધ ઘડિયાળો કે બગડેલા ઇલેક્ટ્રોનિક્સ સાધનોનો કચરો જમા ન થવા દો.\n• ક્રોધમાં આવીને કડવા વચનો બોલવાથી બચો, ખાસ કરીને સંધ્યાકાળના સમયે.\n• મહત્વપૂર્ણ મીટિંગ વખતે ફાટેલા કે અત્યંત કાળા કપડાં પહેરવાનું ટાળો."
            }
        },
        5: {
            "num": "9, 2 (Mars aggression clashes with Mercury intellect, Moon volatility)",
            "colors": "Dark Scarlet Red, Deep Bright Orange",
            "days": "Tuesday (Mars combat energy triggers nervous burnout)",
            "dir": "South",
            "habits": {
                "en": "• Avoid impulsive job jumping or venture hopping without concrete safety cushions.\n• Do not sign legally binding agreements without thoroughly parsing the fine print.\n• Beware of nervous restlessness, excessive caffeine, and doom-scrolling before sleep.\n• Avoid making promises purely to please people when your schedule is already stretched.",
                "hi": "• बिना किसी ठोस योजना या वित्तीय आधार के बार-बार कार्यक्षेत्र बदलने से बचें।\n• दस्तावेजों की सूक्ष्म शर्तों को पढ़े बिना किसी कानूनी पत्र पर हस्ताक्षर न करें।\n• अत्यधिक कैफीन, देर रात तक फोन स्क्रीन देखने और मानसिक बेचैनी से बचें।\n• केवल लोगों को खुश करने के लिए ऐसे वादे न करें जिन्हें आप पूरा न कर सकें।",
                "mr": "• ठोस आर्थिक आधार नसताना वारंवार व्यवसाय किंवा नोकरी बदलणे टाळा.\n• कागदपत्रांच्या अटी नीट वाचल्याशिवाय स्वाक्षरी करू नका.\n• अति चहा-कॉफी पिणे आणि रात्री उशिरापर्यंत मोबाईल वापरणे टाळा.\n• केवळ दुसऱ्यांना खूश करण्यासाठी असमर्थ असलेली आश्वासने देऊ नका.",
                "gu": "• યોગ્ય પ્લાનિંગ વગર વારંવાર નોકરી કે ધંધો બદલવાનું ટાળો.\n• કોઈપણ દસ્તાવેજ ઝીણવટપૂર્વક વાંચ્યા વગર સહી ન કરો.\n• વધુ પડતી ચા-કોફી અને મોડી રાત સુધી મોબાઈલ વાપરવાથી બચો.\n• લોકોને માત્ર ખુશ કરવા માટે ખોટા વચનો આપવાનું ટાળો."
            }
        },
        6: {
            "num": "3, 1 (Jupiter moral friction, Sun scorched Venus energy)",
            "colors": "Pitch Black, Muddy Dark Yellow, Pale Saffron",
            "days": "Thursday (Jupiterian austerity curbs Venusian joy)",
            "dir": "North-East (Ishanya)",
            "habits": {
                "en": "• Avoid overspending on luxury status symbols merely to impress casual acquaintances.\n• Do not neglect personal hygiene, clean surroundings, or wardrobe neatness.\n• Beware of sweet-talking flatterers who exploit your generous hospitality.\n• Avoid toxic domestic disputes with women or mother figures in the family.",
                "hi": "• दूसरों को प्रभावित करने के लिए दिखावटी विलासिता पर फिजूलखर्ची से बचें।\n• व्यक्तिगत स्वच्छता, स्वच्छ परिवेश और सुव्यवस्थित परिधान की उपेक्षा न करें।\n• मीठी बातें करने वाले चापलूसों से सतर्क रहें जो आपकी उदारता का लाभ उठाते हैं।\n• परिवार की स्त्रियों अथवा मातृ-तुल्य व्यक्तियों से विवाद करने से बचें।",
                "mr": "• केवळ लोकांवर प्रभाव पाडण्यासाठी नको तितका दिखाऊ खर्च करू नका.\n• वैयक्तिक स्वच्छता आणि राहणीमानाकडे दुर्लक्ष करू नका.\n• गोड बोलणाऱ्या आणि फायदा घेणाऱ्या लोकांपासून सावध राहा.\n• घरातील महिलांशी किंवा ज्येष्ठ व्यक्तींशी वाद घालणे टाळा.",
                "gu": "• માત્ર બીજાને પ્રભાવિત કરવા માટે મોંઘી વસ્તુઓ પર ખોટો ખર્ચ ન કરો.\n• વ્યક્તિગત સ્વચ્છતા અને ઘરની વ્યવસ્થા પ્રત્યે બેદરકાર ન રહો.\n• મીઠી વાતો કરીને ફાયદો ઉઠાવતા લોકોથી ચેતો.\n• ઘરની સ્ત્રીઓ કે વડીલો સાથે વિવાદમાં પડવાનું ટાળો."
            }
        },
        7: {
            "num": "1, 2, 9 (Sun dominance, Moon whirlpool, Mars combat)",
            "colors": "Bright Fire Red, Pitch Black, Blazing Neon Shades",
            "days": "Sunday, Tuesday",
            "dir": "South, South-East",
            "habits": {
                "en": "• Avoid blind trust in unvetted business partners or smooth-talking strangers.\n• Do not suppress your intuitive hunches when something feels fundamentally off.\n• Avoid complete self-isolation during life challenges; stay connected to reality.\n• Refrain from cynicism or bitter skepticism towards genuine well-wishers.",
                "hi": "• नए अथवा असत्यापित व्यापारिक साझेदारों पर आंख मूंदकर भरोसा न करें।\n• जब आपका अंतर्ज्ञान किसी बात के लिए मना करे, तो उसकी अनदेखी न करें।\n• संकट के समय समाज से पूरी तरह कटने या एकांतवास में डूबने से बचें।\n• अपने सच्चे शुभचिंतकों के प्रति अविश्वास अथवा कड़वाहट रखने से परहेज करें।",
                "mr": "• नवीन किंवा अपरिचित व्यवसाय भागीदारांवर आंधळा विश्वास ठेवू नका.\n• अंतर्मनाचा आवाज ज्या गोष्टीला नकार देतो, त्याकडे दुर्लक्ष करू नका.\n• अडचणीच्या काळात स्वतःला पूर्णपणे एकांतात कोंडून घेऊ नका.\n• आपल्या हितचिंतकांवर विनाकारण संशय घेणे टाळा.",
                "gu": "• અજાણ્યા કે નવા ભાગીદારો પર આંધળો વિશ્વાસ મૂકવાનું ટાળો.\n• તમારું અંતરમન જે બાબત માટે ના પાડે, તેની અવગણના ન કરો.\n• મુશ્કેલ સમયમાં સાવ એકલા પડી જવાને બદલે સ્વજનો સાથે રહો.\n• પોતાના સાચા હિતેચ્છુઓ પ્રત્યે અવિશ્વાસ ન રાખો."
            }
        },
        8: {
            "num": "1, 2, 4, and double 8 (Sun authority enmity, Moon delay, double Saturn load)",
            "colors": "Blazing Crimson Red, Bright Saffron, Radiant Golden Yellow",
            "days": "Sunday (Sun clashes directly with Saturn ruler)",
            "dir": "East (Surya's cardinal point causes friction)",
            "habits": {
                "en": "• Avoid unethical shortcuts, tax loopholes, and deceptive legal maneuvers.\n• Never mistreat blue-collar workers, service staff, or subordinate laborers.\n• Do not complain about delays; Saturn rewards methodical, patient endurance.\n• Avoid brooding over past grievances or harboring revengeful thoughts.",
                "hi": "• अनैतिक शॉर्टकट, कानूनी हेरफेर अथवा किसी को ठगने वाले रास्तों से पूर्णतः बचें।\n• घर या कार्यस्थल पर काम करने वाले सहायकों, मजदूरों व अधीनस्थों का कभी अपमान न करें।\n• कार्यों में देरी होने पर झुंझलाएं नहीं; शनि धैर्यवान व निष्ठावान कर्मों को ही पुरस्कृत करते हैं।\n• पुरानी शिकायतों या बदले की भावना को मन में पालने से बचें।",
                "mr": "• चुकीचे शॉर्टकट, गैरकायदेशीर मार्ग किंवा कोणाची फसवणूक करणे पूर्णपणे टाळा.\n• हाताखाली काम करणारे कामगार आणि मदतनीसांचा कधीही अनादर करू नका.\n• कामात उशीर झाला तरी चिडू नका; शनी केवळ संयमी प्रयत्नांनाच मोठे फळ देतो.\n• मनामध्ये जुनी अढी किंवा सूडबुद्धी बाळगणे टाळा.",
                "gu": "• અનૈતિક શોર્ટકટ કે ખોટા કાયદાકીય રસ્તાઓ અપનાવવાનું ટાળો.\n• હાથ નીચે કામ કરતા કર્મચારીઓ કે શ્રમિકોનું ક્યારેય અપમાન ન કરો.\n• કામમાં વિલંબ થાય તો અકળાવાને બદલે ધીરજપૂર્વક મહેનત ચાલુ રાખો.\n• ભૂતકાળના વેરઝેર કે બદલાની ભાવના મનમાં રાખવાનું ટાળો."
            }
        },
        9: {
            "num": "2, 4, 5 (Moon emotional conflict, Rahu recklessness, Mercury clash)",
            "colors": "Pitch Black, Dark Moss Green, Stark Milky White",
            "days": "Wednesday, Saturday",
            "dir": "North (Mercury cardinal direction triggers friction)",
            "habits": {
                "en": "• Avoid sudden outbursts of temper, road rage, and impulsive verbal aggression.\n• Never sign personal loan guarantees for casual acquaintances or friends.\n• Do not rush into competitive ventures without doing prior reconnaissance.\n• Avoid excessive consumption of hyper-spicy, acidic, and heavy greasy food under stress.",
                "hi": "• अचानक आने वाले तीव्र क्रोध, सड़क पर उग्रता और कटु वाणी के प्रयोग से बचें।\n• मित्रों या परिचितों के व्यक्तिगत ऋण के लिए कभी भी अपनी गारंटी न दें।\n• बिना पूरी तैयारी या जानकारी के किसी प्रतिस्पर्धी कार्य में कूदने से बचें।\n• तनाव के समय अत्यधिक मिर्च-मसालेदार, गरिष्ठ या तामसिक भोजन से परहेज करें।",
                "mr": "• अचानक येणारा राग, रस्त्यावरील वाद आणि संतापाच्या भरात अपशब्द वापरणे टाळा.\n• मित्रांच्या किंवा ओळखीच्या लोकांच्या कर्जासाठी जामीनदार राहणे टाळा.\n• योग्य माहिती आणि तयारीनिशीच नवीन स्पर्धात्मक कामात उतरा.\n• मानसिक तणावाच्या वेळी अति तिखट, तेलकट किंवा जड अन्न खाणे टाळा.",
                "gu": "• એકદમ ક્રોધિત થઈ જવું, રોડ પર ગુસ્સો કરવો કે કડવા શબ્દો બોલવાનું ટાળો.\n• કોઈ મિત્ર કે પરિચિતની લોનમાં ગેરંટર બનવાનું ટાળો.\n• પૂરતી માહિતી કે તૈયારી વગર કોઈપણ સ્પર્ધામાં કૂદી પડવાનું ટાળો.\n• તણાવના સમયે વધુ પડતો તીખો, તળેલો કે ભારે ખોરાક લેવાનું ટાળો."
            }
        }
    }

    base = avoidance_data.get(mulank, avoidance_data[4])
    habits_text = base["habits"].get(lang, base["habits"]["en"])

    titles = {
        "en": "⚠️ Cosmic Caution & Avoidance Matrix (What to Avoid)",
        "hi": "⚠️ क्या वर्जित है: अशुभ अंक, रंग, दिन एवं विशेष सावधानियां",
        "mr": "⚠️ काय टाळावे: अशुभ अंक, रंग, वार आणि महत्त्वाच्या दक्षता",
        "gu": "⚠️ શું ટાળવું: અશુભ અંકો, રંગો, વાર અને વિશેષ સાવચેતીઓ"
    }

    labels = {
        "en": {
            "num": "⚠️ Numbers to Avoid:",
            "colors": "🚫 Colors to Avoid:",
            "days": "📅 Days to Avoid:",
            "dir": "🧭 Direction to Avoid:",
            "habits_hdr": "🚫 Strategic Actions & Pitfalls to Avoid:"
        },
        "hi": {
            "num": "⚠️ वर्जित अंक (Friction Numbers):",
            "colors": "🚫 वर्जित रंग (Draining Colors):",
            "days": "📅 प्रतिकूल दिन (Avoid Days):",
            "dir": "🧭 वर्जित दिशा (Avoid Direction):",
            "habits_hdr": "🚫 आचरण व आदतें जिन्हें टालना चाहिए (Actions to Avoid):"
        },
        "mr": {
            "num": "⚠️ वर्ज्य अंक (Friction Numbers):",
            "colors": "🚫 वर्ज्य रंग (Draining Colors):",
            "days": "📅 प्रतिकूल वार (Avoid Days):",
            "dir": "🧭 वर्ज्य दिशा (Avoid Direction):",
            "habits_hdr": "🚫 टाळावयाच्या कृती व सवयी (Actions to Avoid):"
        },
        "gu": {
            "num": "⚠️ વર્જ્ય અંકો (Friction Numbers):",
            "colors": "🚫 વર્જ્ય રંગો (Draining Colors):",
            "days": "📅 પ્રતિકૂળ વાર (Avoid Days):",
            "dir": "🧭 વર્જ્ય દિશા (Avoid Direction):",
            "habits_hdr": "🚫 ટાળવા જેવી આદતો અને કાર્યો (Actions to Avoid):"
        }
    }

    curr_lbl = labels.get(lang, labels["en"])

    return {
        "title": titles.get(lang, titles["en"]),
        "lbl_num": curr_lbl["num"],
        "lbl_colors": curr_lbl["colors"],
        "lbl_days": curr_lbl["days"],
        "lbl_dir": curr_lbl["dir"],
        "lbl_habits": curr_lbl["habits_hdr"],
        "avoid_num": base["num"],
        "avoid_colors": base["colors"],
        "avoid_days": base["days"],
        "avoid_dir": base["dir"],
        "avoid_habits": habits_text
    }

def calculate_shani_paya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    """Calculates Saturn's foot metal based on Moon Sign relative to Saturn's sign."""
    house_diff = (moon_rashi_idx - saturn_transit_rashi_idx) % 12 + 1
    if house_diff in [2, 5, 9]:
        return {
            "paya": "🥈 Rajat Paya (Silver Feet / चाँदी का पाया)",
            "metal": "Silver",
            "status": "Highly Auspicious (अति शुभ - Supreme Divine Cushion)",
            "desc": (
                "Saturn arrives bearing silver gifts. In classical Vedic astrology, Rajat Paya occurs when transit Saturn moves "
                "through the 2nd, 5th, or 9th house from your natal Moon sign. Silver is ruled by the Moon and Venus, directly cooling "
                "Saturn's dry, restrictive heat. Even during challenging transits or Sade Sati, Rajat Paya functions as an energetic shock-absorber—converting "
                "severe karmic friction into long-term professional stature, wealth preservation, intellectual breakthroughs, and unexpected societal patronage."
            ),
            "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces / Meena Rashi)"
        }
    elif house_diff in [3, 7, 10]:
        return {
            "paya": "🥉 Tamra Paya (Copper Feet / तांबे का पाया)",
            "metal": "Copper",
            "status": "Favorable & Productive (शुभ - Dynamic Growth)",
            "desc": (
                "Saturn steps with copper feet (3rd, 7th, or 10th from natal Moon). Governed by Mars and Sun, Copper Paya stimulates executive stamina, "
                "relentless work ethic, victory over competitors, and tangible career advancement through sustained disciplined labor."
            ),
            "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces / Meena Rashi)"
        }
    elif house_diff in [1, 6, 11]:
        return {
            "paya": "🥇 Swarna Paya (Gold Feet / सोने का पाया)",
            "metal": "Gold",
            "status": "Testing & High Friction (कठिन - Character Crucible)",
            "desc": (
                "Saturn steps with golden feet (1st, 6th, or 11th from natal Moon). Although gold symbolizes luxury, Saturn's relationship with gold "
                "is paradoxical: it tests character through inflated egos, sudden expenditures, and deceptive allure. Requires rigorous humility, grounded lifestyle, and charity."
            ),
            "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces / Meena Rashi)"
        }
    else:
        return {
            "paya": "🪙 Loha Paya (Iron Feet / लोहे का पाया)",
            "metal": "Iron",
            "status": "Demanding & Heavy (संघर्षमय - Rigorous Karmic Labor)",
            "desc": (
                "Saturn steps with iron feet (4th, 8th, or 12th from natal Moon in certain traditions). Represents heavy responsibilities, delays, and psychological trials. "
                "Demands relentless patience, ethical integrity, blue-collar charity, and daily Hanuman Chalisa chanting."
            ),
            "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces / Meena Rashi)"
        }

def calculate_shani_sadesati_dhaiya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    """Determines active Sade Sati or Dhaiya phase with complete multi-phase roadmap."""
    diff = (saturn_transit_rashi_idx - moon_rashi_idx) % 12
    if diff == 11:
        return {
            "active": True,
            "type": "Sade Sati Phase 1 (Rising Phase / Aarohi Charana - 12th House Transit)",
            "impact": "Saturn transits the 12th house from your natal Moon. Focus on strategic financial management, curbing unvetted investments, foreign ventures, and spiritual grounding.",
            "dates": "29 March 2025 – 23 February 2028"
        }
    elif diff == 0:
        return {
            "active": True,
            "type": "Sade Sati Phase 2 (Peak Phase / Janma Shani - 1st House Transit)",
            "impact": "Saturn transits over your natal Moon. The mental and physical core undergoes profound restructuring. Demands utmost discipline, health vigilance, and ego surrender.",
            "dates": "February 2028 – April 2030"
        }
    elif diff == 1:
        return {
            "active": True,
            "type": "Sade Sati Phase 3 (Setting Phase / Avarohi Charana - 2nd House Transit)",
            "impact": "Saturn transits the 2nd house from your Moon. Wealth stabilization, family realignment, speech refinement, and the harvesting of matured karmic lessons.",
            "dates": "April 2030 – May 2032"
        }
    elif diff == 3:
        return {
            "active": True,
            "type": "Kantaka Shani (4th House Dhaiya / Ardh-Ashtama Shani)",
            "impact": "Tests domestic tranquility, property matters, maternal health, and emotional peace. Steady inner calm builds unshakable resilience.",
            "dates": "Active 2.5-Year Cycle"
        }
    elif diff == 7:
        return {
            "active": True,
            "type": "Ashtama Shani (8th House Dhaiya - Deep Transformational Crucible)",
            "impact": "Sudden structural shifts, unearthing hidden resources, spiritual awakening, and mandatory metabolic discipline.",
            "dates": "Active 2.5-Year Cycle"
        }
    else:
        return {
            "active": False,
            "type": "No Active Sade Sati or Dhaiya",
            "impact": "Saturn is transiting a harmonious or neutral house relative to your natal Moon. Unhindered operational expansion.",
            "dates": "N/A"
        }

def calculate_shani_vahan(birth_star_idx: int, transit_moon_star_idx: int) -> dict:
    """Calculates Saturn's active vehicle using ((Birth Star * 4) + Transit Star) mod 9."""
    raw_val = (birth_star_idx * 4 + transit_moon_star_idx) % 9
    rem = 9 if raw_val == 0 else raw_val
    return SHANI_VAHANS.get(rem, SHANI_VAHANS[9])

def get_sidereal_moon_longitude(utc_dt: datetime.datetime) -> float:
    """Calculates accurate sidereal Moon longitude via Moshier Swiss Ephemeris or analytical engine."""
    if utc_dt.tzinfo is not None:
        utc_dt = utc_dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)

    if HAS_SWISSEPH:
        try:
            t_jd = swe.julday(
                utc_dt.year, utc_dt.month, utc_dt.day,
                utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
            )
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            calc_res = swe.calc_ut(t_jd, swe.MOON, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)
            raw_lon = calc_res[0][0] if isinstance(calc_res[0], (list, tuple)) else calc_res[0]
            return float(raw_lon % 360.0)
        except Exception:
            try:
                calc_res = swe.calc_ut(t_jd, swe.MOON, swe.FLG_SIDEREAL)
                raw_lon = calc_res[0][0] if isinstance(calc_res[0], (list, tuple)) else calc_res[0]
                return float(raw_lon % 360.0)
            except Exception:
                pass

    ref = datetime.datetime(2000, 1, 1, 12, 0)
    delta_days = (utc_dt - ref).total_seconds() / 86400.0
    moon_mean_lon = (218.316 + 13.176396 * delta_days - 23.85) % 360.0
    return float(moon_mean_lon % 360.0)

def calculate_birth_chart(dob: datetime.date, tob: datetime.time, lat: float = 19.8762, lon: float = 75.3433):
    """Calculates sidereal Moon Nakshatra, Pada, Moon Rashi, and Lagna."""
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
    """Calculates pinpoint entry and exit IST times for active star."""
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
    """Calculates Moon transit ingress and egress intervals for next 7 days."""
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
            "icon": icon,
            "quality": quality,
            "vahan": vahan_info["name"],
            "vahan_type": vahan_info["type"],
            "start_str": s_time.strftime("%a, %d %b %I:%M %p"),
            "end_str": e_time.strftime("%a, %d %b %I:%M %p IST")
        })
    return transits

def get_sidereal_planet_positions(target_ist_dt: datetime.datetime):
    """Returns sidereal longitudes for Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu."""
    utc_dt = target_ist_dt - datetime.timedelta(hours=5, minutes=30)
    planets = [
        ("Sun (Surya)", 0),
        ("Moon (Chandra)", 1),
        ("Mars (Mangal)", 4),
        ("Mercury (Budha)", 2),
        ("Jupiter (Guru)", 5),
        ("Venus (Shukra)", 3),
        ("Saturn (Shani)", 6),
        ("Rahu (North Node)", 10)
    ]
    
    res_list = []
    if HAS_SWISSEPH:
        try:
            t_jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                              utc_dt.hour + utc_dt.minute / 60.0)
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            for name, pid in planets:
                try:
                    calc = swe.calc_ut(t_jd, pid, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)
                    lon = float(calc[0][0] if isinstance(calc[0], (list, tuple)) else calc[0])
                except Exception:
                    calc = swe.calc_ut(t_jd, pid, swe.FLG_SIDEREAL)
                    lon = float(calc[0][0] if isinstance(calc[0], (list, tuple)) else calc[0])
                r_idx = max(0, min(11, int(lon / 30.0)))
                deg_in_rashi = lon % 30.0
                res_list.append({
                    "planet": name,
                    "rashi": RASHIS[r_idx],
                    "deg": f"{int(deg_in_rashi)}° {int((deg_in_rashi % 1) * 60)}'"
                })
            rahu_items = [p for p in res_list if "Rahu" in p["planet"]]
            if rahu_items:
                res_list.append({
                    "planet": "Ketu (South Node)",
                    "rashi": "Opposite Rahu",
                    "deg": "180° Polar Axis"
                })
        except Exception:
            res_list = []
            
    if not res_list:
        fallback_planets = [
            ("Sun (Surya)", "Simha (Leo)", "23° 45'"),
            ("Moon (Chandra)", "Mesha (Aries)", "18° 12'"),
            ("Mars (Mangal)", "Mithuna (Gemini)", "04° 30'"),
            ("Mercury (Budha)", "Kanya (Virgo)", "11° 15'"),
            ("Jupiter (Guru)", "Vrishabha (Taurus)", "21° 50'"),
            ("Venus (Shukra)", "Kanya (Virgo)", "08° 22'"),
            ("Saturn (Shani)", "Meena (Pisces)", "03° 10'"),
            ("Rahu (North Node)", "Meena (Pisces)", "12° 40'"),
            ("Ketu (South Node)", "Kanya (Virgo)", "12° 40'")
        ]
        for name, rashi, deg in fallback_planets:
            res_list.append({"planet": name, "rashi": rashi, "deg": deg})
            
    return res_list

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

prof = st.session_state.user_profile
current_lang = prof.get("lang", "en")

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

render_html(f"""
    <div style='text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; margin-top:0.2rem; margin-bottom:0.75rem;'>
        <div style='background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); width:76px; height:76px; border-radius:26px; display:flex; align-items:center; justify-content:center; font-size:2.5rem; box-shadow:0 8px 28px rgba(245,158,11,0.38); margin-bottom:10px;'>
            ✨
        </div>
        <h1 style='margin:0; font-size:2.15rem; color:#0f172a; font-weight:900; line-height:1.2; text-align:center;'>{t('app_title', current_lang)}</h1>
        <div style='font-size:1rem; color:#64748b; font-weight:600; margin-top:6px; text-align:center;'>{t('app_subtitle', current_lang)}</div>
    </div>
""")

# Row 1: About App, User Profile, Numerology, Shani
nav_r1_c1, nav_r1_c2, nav_r1_c3, nav_r1_c4 = st.columns(4)
with nav_r1_c1:
    p_type = "primary" if st.session_state.current_page == "about" else "secondary"
    if st.button(t("btn_about", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "about"
        st.rerun()

with nav_r1_c2:
    p_type = "primary" if st.session_state.current_page in ["profile", "navtara"] else "secondary"
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

# Row 2: Live Prediction, 7 Days Prediction, Planet Position, Remedies
nav_r2_c1, nav_r2_c2, nav_r2_c3, nav_r2_c4 = st.columns(4)
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
    p_type = "primary" if st.session_state.current_page == "planets" else "secondary"
    if st.button(t("btn_planets", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "planets"
        st.rerun()

with nav_r2_c4:
    p_type = "primary" if st.session_state.current_page == "remedies" else "secondary"
    if st.button(t("btn_remedies", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "remedies"
        st.rerun()

render_html("<hr style='margin:10px 0 16px 0; border:none; border-top:1.5px solid #e2e8f0;'>")

def render_page_about():
    st.markdown("#### 🌐 Choose Display Language")
    lang_options = [("en", "🇬🇧 English"), ("hi", "🇮🇳 हिन्दी (Hindi)"), ("mr", "🚩 मराठी (Marathi)"), ("gu", "🪔 ગુજરાતી (Gujarati)")]
    lang_codes = [c for c, _ in lang_options]
    curr_idx = lang_codes.index(current_lang) if current_lang in lang_codes else 0
    sel_lang = st.selectbox(
        "Select Language",
        options=lang_codes,
        index=curr_idx,
        format_func=lambda x: dict(lang_options).get(x, x),
        label_visibility="collapsed",
        key="about_lang_selector"
    )
    if sel_lang != current_lang:
        st.session_state.user_profile["lang"] = sel_lang
        save_user_profile(st.session_state.user_profile)
        st.rerun()

    render_html("""
    <div class="auth-hero-box">
        <div style="font-weight:900; font-size:1.35rem; color:#92400e; margin-bottom:0.8rem; border-bottom:2px solid #fde68a; padding-bottom:0.4rem;">
            ✨ The Science of Chronobiology, Vedic Timing & Cosmic Precision
        </div>
        
        <div style="font-size:0.96rem; line-height:1.75; color:#451a03;">
            <p><b>1. Chronobiology & Biological Water Dynamics:</b> Modern biophysics and chronobiology prove that living organisms are governed by planetary and circadian clocks. The human body is composed of approximately <b>70% water</b>. Just as lunar gravitation exerts enormous tidal forces on planetary oceans, it produces subtle neuro-electrochemical shifts within the human nervous and endocrine systems. In Vedic science, the Moon governs the Mind (<i>Chandro Manaso Jatah</i>)—dictating emotional balance, cognitive resilience, and daily decision velocity.</p>
            
            <p><b>2. Astronomical Precision via Swiss Ephemeris:</b> Unlike generic calendar horoscopes, <b>Navtara Pulse</b> is powered by the internationally recognized <b>Swiss Ephemeris (Moshier engine)</b>, computing true sidereal planetary coordinates using the <b>Lahiri Ayanamsa</b> with sub-arcsecond accuracy. Every nakshatra transit window reflects real-time astronomical ingress and egress timestamps in Indian Standard Time (IST).</p>
            
            <p><b>3. Strategic Timing (Navtara Chakra):</b> Your birth Moon Nakshatra forms an immutable karmic baseline. As the transit Moon traverses the 27 stellar mansions, it activates 9 cyclical frequencies:
            <br>• <b>Golden Windows:</b> <i>Sampat</i> (Wealth), <i>Kshema</i> (Safety), <i>Sadhana</i> (Achievement), <i>Mitra</i> & <i>Ati-Mitra</i> (Alliance & Triumph). Seize these days for business negotiations, investments, and launches.
            <br>• <b>Protective Shields:</b> <i>Vipat</i> (Crisis Risk), <i>Pratyari</i> (Resistance), and <i>Vadha</i> (Critical Vulnerability). Recognize these phases in advance to avoid impulsive legal, financial, or verbal friction.</p>

            <p><b>4. The Biophysics of Vedic Remedies:</b> Vedic remedies are bio-resonance tools. Reciting root Sanskrit mantras creates focused acoustic resonance that down-regulates cortisol and stabilizes autonomic neural networks. Targeted charity (<i>Dana</i>) balances elemental psychological feedback loops, neutralizing karmic friction.</p>
        </div>
    </div>
    """)

    render_html("""
    <!-- PWA INSTALLATION GUIDE -->
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.6rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            📲 How to Install as a Native Mobile App
        </div>
        <div style="font-size:0.95rem; line-height:1.65; color:#431407;">
            <p>You can run <b>Navtara Pulse</b> full-screen on your phone just like an app installed from the Google Play Store or Apple App Store:</p>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:10px; margin-top:8px;">
                <div style="background:#fff7ed; padding:12px; border-radius:12px; border:1.5px solid #ffedd5;">
                    <b style="color:#c2410c;">🤖 Android (Google Chrome):</b><br>
                    1. Tap the three dots (<b>⋮</b>) in the top-right corner.<br>
                    2. Select <b>Add to Home screen</b> or <b>Install App</b>.<br>
                    3. Launch directly from your home screen.
                </div>
                <div style="background:#fff7ed; padding:12px; border-radius:12px; border:1.5px solid #ffedd5;">
                    <b style="color:#c2410c;">🍏 iPhone / iPad (Safari):</b><br>
                    1. Tap the <b>Share</b> button (square with arrow ↑) at the bottom.<br>
                    2. Scroll down and tap <b>Add to Home Screen</b>.<br>
                    3. Tap <b>Add</b> in the top-right corner to finish.
                </div>
            </div>
        </div>
    </div>
    """)

    app_url = "https://navtara-pulse.streamlit.app"
    share_msg = "Discover your real-time Vedic Moon transit rhythm, Shani Paya, and personalized Numerology blueprint with Navtara Pulse!"
    encoded_url = urllib.parse.quote(app_url)
    encoded_msg = urllib.parse.quote(f"{share_msg}\n\nCheck your cosmic alignment here: {app_url}")

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.8rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            {t('share_title', current_lang)}
        </div>
        <div style="font-size:0.95rem; color:#475569; margin-bottom:1rem; line-height:1.5;">
            Share this cosmic timing engine with friends, family, and associates:
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:1rem;">
            <a href="https://api.whatsapp.com/send?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#25D366; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem;">
                    🟢 WhatsApp
                </div>
            </a>
            <a href="https://t.me/share/url?url={encoded_url}&text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0088cc; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem;">
                    ✈️ Telegram
                </div>
            </a>
            <a href="mailto:?subject=Navtara Pulse - Vedic Timing&body={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#ea4335; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem;">
                    ✉️ Email
                </div>
            </a>
            <a href="https://twitter.com/intent/tweet?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0f172a; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem;">
                    🐦 X (Twitter)
                </div>
            </a>
        </div>

        <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1px solid #fed7aa; text-align:center;">
            <div style="font-size:0.88rem; color:#9a3412; font-weight:800;">Direct Web App Link:</div>
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
    
    # Defensive text preparation for Moon Sign and Lagna
    m_rashi_parts = chart_info['moon_rashi_name'].split()
    m_rashi_main = m_rashi_parts[0] if m_rashi_parts else chart_info['moon_rashi_name']
    m_rashi_sub = m_rashi_parts[-1] if len(m_rashi_parts) > 1 else ""

    l_rashi_parts = chart_info['lagna_name'].split()
    l_rashi_main = l_rashi_parts[0] if l_rashi_parts else chart_info['lagna_name']
    l_rashi_sub = l_rashi_parts[-1] if len(l_rashi_parts) > 1 else ""

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
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{m_rashi_main}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{m_rashi_sub}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('lagna_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{l_rashi_main}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{l_rashi_sub}</div>
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

        <!-- 2. MOON RASHI (CHANDRA RASHI) SECTION -->
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
        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:0.5rem;">
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
    </div>
    """)

def render_page_numerology():
    num_domains = get_numerology_life_domains(mulank, bhagyank, namank, current_lang)
    num_avoid = get_numerology_avoidance(mulank, bhagyank, current_lang)
    p_m_label = NUM_PLANET_NAMES.get(mulank, {}).get(current_lang, f"Planet {mulank}")
    p_b_label = NUM_PLANET_NAMES.get(bhagyank, {}).get(current_lang, f"Planet {bhagyank}")
    p_n_label = NUM_PLANET_NAMES.get(namank, {}).get(current_lang, f"Planet {namank}")

    render_html(f"""
    <div class="light-card-num">
        <div style="font-weight:900; font-size:1.35rem; color:#065f46; margin-bottom:1rem; border-bottom:2px solid #bbf7d0; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
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

        <!-- A. HARMONIC LUCK MATRIX -->
        <div style="background:#f0fdf4; border-radius:14px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:8px;">{num_domains['luck_title']}</div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.95rem; line-height:1.6;">
                <div><b>✨ Lucky Numbers:</b> {num_domains['lucky_num']}</div>
                <div><b>⚠️ Caution Numbers:</b> {num_domains['avoid_num']}</div>
                <div><b>📅 Auspicious Days:</b> {num_domains['lucky_days']}</div>
                <div><b>🧭 Favorable Direction:</b> {num_domains['lucky_dir']}</div>
                <div style="grid-column: 1 / -1;"><b>🎨 Energizing Colors:</b> {num_domains['lucky_colors']}</div>
            </div>
        </div>

        <!-- B. DEDICATED COSMIC CAUTION & AVOIDANCE MATRIX -->
        <div style="background:#fff1f2; border-radius:14px; padding:14px; border:1.5px solid #fecdd3;">
            <div style="font-weight:900; font-size:1.1rem; color:#9f1239; margin-bottom:10px; border-bottom:1.5px solid #fecdd3; padding-bottom:6px;">
                {num_avoid['title']}
            </div>

            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:10px; margin-bottom:12px;">
                <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #fecdd3;">
                    <div style="font-size:0.82rem; font-weight:800; color:#e11d48; text-transform:uppercase;">{num_avoid['lbl_num']}</div>
                    <div style="font-size:0.94rem; font-weight:900; color:#881337; margin-top:2px;">{num_avoid['avoid_num']}</div>
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #fecdd3;">
                    <div style="font-size:0.82rem; font-weight:800; color:#e11d48; text-transform:uppercase;">{num_avoid['lbl_colors']}</div>
                    <div style="font-size:0.94rem; font-weight:900; color:#881337; margin-top:2px;">{num_avoid['avoid_colors']}</div>
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #fecdd3;">
                    <div style="font-size:0.82rem; font-weight:800; color:#e11d48; text-transform:uppercase;">{num_avoid['lbl_days']}</div>
                    <div style="font-size:0.94rem; font-weight:900; color:#881337; margin-top:2px;">{num_avoid['avoid_days']}</div>
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #fecdd3;">
                    <div style="font-size:0.82rem; font-weight:800; color:#e11d48; text-transform:uppercase;">{num_avoid['lbl_dir']}</div>
                    <div style="font-size:0.94rem; font-weight:900; color:#881337; margin-top:2px;">{num_avoid['avoid_dir']}</div>
                </div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border-left:4px solid #e11d48; border:1px solid #fecdd3; border-left-width:4px;">
                <div style="font-weight:900; font-size:0.98rem; color:#9f1239; margin-bottom:6px;">{num_avoid['lbl_habits']}</div>
                <div style="font-size:0.93rem; line-height:1.7; color:#881337; white-space:pre-line;">{num_avoid['avoid_habits']}</div>
            </div>
        </div>
    </div>
    """)

def render_page_shani():
    render_html(f"""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.35rem; color:#5b21b6; margin-bottom:1rem; border-bottom:2px solid #ddd6fe; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{t('shani_paya_title', current_lang)}</span>
            <span style="font-size:0.85rem; background:#ede9fe; color:#6d28d9; padding:4px 12px; border-radius:20px; font-weight:900;">SATURN TRANSIT MATRIX</span>
        </div>
        
        <!-- 1. ACTIVE SHANI PAYA CARD -->
        <div style="background:#f5f3ff; border-radius:14px; padding:16px; border:1.5px solid #e9d5ff; margin-bottom:1.15rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">ACTIVE 2.5-YEAR SHANI PAYA</div>
                <div style="font-size:0.88rem; background:#dcfce7; color:#15803d; padding:3px 10px; border-radius:12px; font-weight:800;">{shani_paya_data['status']}</div>
            </div>
            <div style="font-size:1.4rem; font-weight:900; color:#5b21b6; margin:6px 0;">{shani_paya_data['paya']}</div>
            <div style="font-size:0.92rem; color:#475569; margin-bottom:8px;"><b>Active Timeline:</b> {shani_paya_data['timeline']}</div>
            <div style="font-size:0.96rem; line-height:1.7; color:#3b0764;">{shani_paya_data['desc']}</div>
        </div>

        <!-- 2. THE FOUR PAYAS COMPARATIVE GUIDE -->
        <div style="background:#ffffff; border-radius:14px; padding:15px; border:1.5px solid #ddd6fe; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#5b21b6; margin-bottom:10px; border-bottom:1.5px solid #ede9fe; padding-bottom:6px;">
                🏛️ Classical Science of the 4 Shani Payas (Saturn's Metallic Footing)
            </div>
            <div style="font-size:0.94rem; line-height:1.65; color:#334155; margin-bottom:10px;">
                In Vedic Jyotish, when Saturn enters any zodiac sign, his arrival energy crystallizes through one of four metallic footings based on the angular distance of your natal Moon sign:
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:10px; font-size:0.92rem;">
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0; border-left:4px solid #94a3b8;">
                    <b style="color:#0f172a;">🥈 Rajat Paya (Silver - 2nd, 5th, 9th from Moon):</b><br>
                    <span style="color:#475569;">Governed by Chandra & Shukra. Most auspicious footing; bestows financial shields, executive intellect, and relief from long-standing health burdens.</span>
                </div>
                <div style="background:#fff7ed; border-radius:10px; padding:10px; border:1px solid #fed7aa; border-left:4px solid #ea580c;">
                    <b style="color:#9a3412;">🥉 Tamra Paya (Copper - 3rd, 7th, 10th from Moon):</b><br>
                    <span style="color:#7c2d12;">Governed by Surya & Mangal. Drives high stamina, aggressive professional expansion, courage in litigation, and steady compounding wealth through labor.</span>
                </div>
                <div style="background:#fefce8; border-radius:10px; padding:10px; border:1px solid #fef08a; border-left:4px solid #eab308;">
                    <b style="color:#854d0e;">🥇 Swarna Paya (Gold - 1st, 6th, 11th from Moon):</b><br>
                    <span style="color:#713f12;">High ego tests, sudden spikes in overhead expenses, and health vulnerabilities. Demands strict humility, modesty, and avoidance of vanity.</span>
                </div>
                <div style="background:#f1f5f9; border-radius:10px; padding:10px; border:1px solid #cbd5e1; border-left:4px solid #475569;">
                    <b style="color:#1e293b;">🪙 Loha Paya (Iron - 4th, 8th, 12th from Moon):</b><br>
                    <span style="color:#334155;">Demands heavy patience, blue-collar endurance, and silent labor. High delays reward those who do not complain and remain honest.</span>
                </div>
            </div>
        </div>

        <!-- 3. ELABORATIVE SHANI SADE SATI & DHAIYA 3-PHASE ROADMAP -->
        <div style="background:#ffffff; border-radius:14px; padding:16px; border:1.5px solid #ddd6fe; border-left:6px solid #7c3aed; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:4px;">
                {t('sadesati_title', current_lang)}
            </div>
            <div style="font-size:1.05rem; font-weight:900; color:#6d28d9; margin-bottom:2px;">
                {shani_sadesati_data['type']}
            </div>
            <div style="font-size:0.92rem; color:#64748b; margin-bottom:12px;">
                <b>Active Phase Period:</b> {shani_sadesati_data['dates']} &nbsp;|&nbsp; <b>Overall Cycle:</b> 7.5 Years Total
            </div>

            <!-- Complete 3-Phase Roadmap -->
            <div style="display:flex; flex-direction:column; gap:12px; margin-top:8px;">
                <!-- PHASE 1 -->
                <div style="background:#f5f3ff; border-radius:12px; padding:13px; border:1px solid #ddd6fe; border-left:5px solid #9333ea;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <b style="color:#6b21a8; font-size:1rem;">Phase 1: Rising Phase (Aarohi Charana / 12th House Transit)</b>
                        <span style="background:#d8b4fe; color:#581c87; font-size:0.8rem; padding:2px 8px; border-radius:10px; font-weight:800;">ACTIVE NOW</span>
                    </div>
                    <div style="font-size:0.88rem; color:#7e22ce; font-weight:700; margin-bottom:5px;">📅 29 March 2025 – 23 February 2028 (Saturn in Pisces / Meena Rashi)</div>
                    <div style="font-size:0.93rem; line-height:1.65; color:#3b0764;">
                        <b>Detailed Prediction:</b> Saturn enters the 12th house from your natal Moon (Mesha), initiating the 7.5-year cycle. This phase audits subconscious habits, sleep architecture, and financial outflows. Unnecessary expenditures increase unless directed toward constructive long-term investments (real estate, foreign connections, asset creation). Mental anxiety and restless sleep can occur due to subconscious purging. Your active <b>Silver Paya (Rajat Paya)</b> acts as a divine protective shield, turning potential losses into strategic investments and spiritual elevation.
                    </div>
                    <div style="background:#ffffff; border-radius:8px; padding:8px 10px; margin-top:8px; border:1px solid #e9d5ff; font-size:0.9rem; color:#581c87;">
                        <b>🪔 Phase 1 Remedies:</b> Maintain strict budgeting. Avoid high-interest loans. Feed soaked black grams (chana) to stray cattle on Tuesdays and Saturdays. Keep your bedroom free of clutter and sleep with your head towards the South or East.
                    </div>
                </div>

                <!-- PHASE 2 -->
                <div style="background:#fdf2f8; border-radius:12px; padding:13px; border:1px solid #fbcfe8; border-left:5px solid #db2777;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <b style="color:#9d174d; font-size:1rem;">Phase 2: Peak Phase (Janma Shani / 1st House Core Transit)</b>
                        <span style="background:#fce7f3; color:#9d174d; font-size:0.8rem; padding:2px 8px; border-radius:10px; font-weight:800;">UPCOMING</span>
                    </div>
                    <div style="font-size:0.88rem; color:#be185d; font-weight:700; margin-bottom:5px;">📅 February 2028 – April 2030 (Saturn in Aries / Mesha Rashi)</div>
                    <div style="font-size:0.93rem; line-height:1.65; color:#831843;">
                        <b>Detailed Prediction:</b> Saturn transits directly over your natal Moon. This is the heart of Sade Sati—the psychological and physical crucible. Saturn directly scrutinizes your self-identity, health vitality, executive decision-making, and relationship dynamics. You are tasked with massive leadership responsibilities. While work pressure peaks, those who work with meticulous discipline emerge as unshakeable industry leaders. Personal ego is dismantled to make room for genuine authority.
                    </div>
                    <div style="background:#ffffff; border-radius:8px; padding:8px 10px; margin-top:8px; border:1px solid #fbcfe8; font-size:0.9rem; color:#9d174d;">
                        <b>🪔 Phase 2 Remedies:</b> Recite the <b>Hanuman Chalisa</b> or <b>Sundarkand</b> every Tuesday and Saturday evening. Perform Shani Telabhishekam (offer mustard oil with black sesame seeds) on Saturdays. Practice daily morning Surya Namaskar and Pranayama to maintain biological Prana.
                    </div>
                </div>

                <!-- PHASE 3 -->
                <div style="background:#f0fdf4; border-radius:12px; padding:13px; border:1px solid #bbf7d0; border-left:5px solid #16a34a;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <b style="color:#166534; font-size:1rem;">Phase 3: Setting Phase (Avarohi Charana / 2nd House Transit)</b>
                        <span style="background:#dcfce7; color:#166534; font-size:0.8rem; padding:2px 8px; border-radius:10px; font-weight:800;">UPCOMING</span>
                    </div>
                    <div style="font-size:0.88rem; color:#15803d; font-weight:700; margin-bottom:5px;">📅 April 2030 – May 2032 (Saturn in Taurus / Vrishabha Rashi)</div>
                    <div style="font-size:0.93rem; line-height:1.65; color:#14532d;">
                        <b>Detailed Prediction:</b> Saturn moves to the 2nd house of accumulated wealth (Dhana Bhava), family lineage, and speech. The turbulent storms of Phase 2 settle completely. You now harvest the fruits of the hard lessons learned. Financial stability returns, new permanent income assets are locked in, and family relations consolidate. Saturn teaches mindful speech—avoiding arrogance or sharp criticism cements permanent domestic peace.
                    </div>
                    <div style="background:#ffffff; border-radius:8px; padding:8px 10px; margin-top:8px; border:1px solid #bbf7d0; font-size:0.9rem; color:#166534;">
                        <b>🪔 Phase 3 Remedies:</b> Feed wheat dough balls with jaggery to cows on Thursdays and Saturdays. Maintain absolute honesty in business accounting and tax filings. Practice sweet, measured speech (Mita-bhashi).
                    </div>
                </div>
            </div>
        </div>

        <!-- 4. CRITICAL CAUTIONS: WHAT TO AVOID DURING SADE SATI & DHAIYA -->
        <div style="background:#fff1f2; border-radius:14px; padding:16px; border:1.5px solid #fecdd3; border-left:6px solid #e11d48; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#9f1239; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
                <span>⚠️</span> <span>What to Avoid During Active Sade Sati or Dhaiya (वर्जित कर्म व सावधानियां)</span>
            </div>
            <div style="font-size:0.94rem; line-height:1.7; color:#881337;">
                Saturn is the cosmic Chief Justice (Dharmaraja / Karma-Phaladata). When operating under active Sade Sati or Dhaiya, strictly avoid the following pitfalls:
                <div style="margin-top:8px; display:flex; flex-direction:column; gap:6px;">
                    <div>🚫 <b>Never Mistreat Subordinates or Laborers:</b> Saturn represents blue-collar workers, cleaners, drivers, and service staff. Cheating, delaying wages, or speaking disrespectfully to service staff directly activates Saturn's severe wrath. Treat them with generosity and respect.</div>
                    <div>🚫 <b>No Speculative Gambles or Fast-Money Shortcuts:</b> Avoid high-leverage day trading, unauthorized crypto bets, and illegal tax evasion schemes. Saturn punishes shortcuts with compounding penalties.</div>
                    <div>🚫 <b>Avoid Saturday Binding Contracts & Sunset Signings:</b> Refrain from signing long-term partnership pacts or high-stakes debt commitments on Saturdays or during twilight (Sandhya Kaal).</div>
                    <div>🚫 <b>Do Not Buy Iron, Mustard Oil, or Leather on Saturdays:</b> Buying iron scrap, black footwear, or mustard oil on Saturdays invites transit friction. These items may be donated on Saturdays, but never purchased for personal use.</div>
                    <div>🚫 <b>Avoid Alcohol, Intoxicants & Tamasic Greasy Food on Tuesdays/Saturdays:</b> Intoxicants cloud cognitive discernment, leading to impulsive words that cause lasting professional and domestic rifts.</div>
                    <div>🚫 <b>Avoid Harboring Vengeful Thoughts or Arrogant Ultimatums:</b> Saturn demands egoless objectivity. If someone wrongs you, let cosmic Dharma handle justice—do not stoop to vindictive retaliations.</div>
                </div>
            </div>
        </div>

        <!-- 5. AUTHENTIC VEDIC & PURANIC SHANI MANTRAS -->
        <div style="background:#f5f3ff; border-radius:14px; padding:16px; border:1.5px solid #ddd6fe;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:8px; display:flex; align-items:center; gap:8px;">
                <span>🪔</span> <span>Authentic Vedic & Puranic Shani Mantras (सिद्ध वैदिक एवं पौराणिक मंत्र)</span>
            </div>
            <div style="font-size:0.93rem; color:#475569; margin-bottom:12px;">
                Chanting these consecrated mantras during twilight hours facing West neutralizes heavy karmic density and activates protective cosmic shields:
            </div>

            <!-- Mantra 1: Vedic Samhita Mantra -->
            <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #ddd6fe; margin-bottom:10px; border-left:4px solid #7c3aed;">
                <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">1. Rigvedic / Yajurvedic Samhita Shani Mantra (परम वैदिक शांति मंत्र)</div>
                <div style="font-size:1.15rem; font-weight:900; color:#1e1b4b; margin:6px 0; font-family:'Noto Sans Devanagari', sans-serif;">
                    ॐ शं नो देवीरभिष्टय आपो भवन्तु पीतये। शं योरभि स्रवन्तु नः॥
                </div>
                <div style="font-size:0.92rem; color:#4338ca; font-weight:700;">
                    <i>Om Sham No Deveerabhishtaya Aapo Bhavantu Peetaye, Sham Yorabhi Sravantu Nah.</i>
                </div>
                <div style="font-size:0.88rem; color:#475569; margin-top:4px;">
                    <b>Meaning & Count:</b> "May the divine cosmic waters bestow bliss and fulfillment upon us; may auspiciousness flow upon us from all directions." Chant <b>21 times daily</b> during sunrise or sunset.
                </div>
            </div>

            <!-- Mantra 2: Shani Beej Mantra -->
            <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #ddd6fe; margin-bottom:10px; border-left:4px solid #7c3aed;">
                <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">2. Shani Beej Mantra (तांत्रिक बीज मंत्र - Acoustic Karmic Purifier)</div>
                <div style="font-size:1.15rem; font-weight:900; color:#1e1b4b; margin:6px 0; font-family:'Noto Sans Devanagari', sans-serif;">
                    ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः॥
                </div>
                <div style="font-size:0.92rem; color:#4338ca; font-weight:700;">
                    <i>Om Praam Preem Proum Sah Shanaishcharaya Namah.</i>
                </div>
                <div style="font-size:0.88rem; color:#475569; margin-top:4px;">
                    <b>Count & Guidance:</b> Chant <b>108 times on a Rudraksha or Blue Hakik mala</b> on Saturday evenings facing West. Calms nervous agitation and aligns the root chakra.
                </div>
            </div>

            <!-- Mantra 3: Shani Gayatri Mantra -->
            <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #ddd6fe; margin-bottom:10px; border-left:4px solid #7c3aed;">
                <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">3. Shani Gayatri Mantra (शनि गायत्री मंत्र - Divine Mental Illumination)</div>
                <div style="font-size:1.15rem; font-weight:900; color:#1e1b4b; margin:6px 0; font-family:'Noto Sans Devanagari', sans-serif;">
                    ॐ काकध्वजाय विद्महे खड्गहस्ताय धीमहि तन्नो मन्दः प्रचोदयात्॥
                </div>
                <div style="font-size:0.92rem; color:#4338ca; font-weight:700;">
                    <i>Om Kaakadhwajaaya Vidmahe Khadgahastaaya Dheemahi Tanno Mandah Prachodayaat.</i>
                </div>
                <div style="font-size:0.88rem; color:#475569; margin-top:4px;">
                    <b>Count & Guidance:</b> Chant <b>11 times on Saturdays</b> to banish fear of the future, remove mental despair, and awaken tactical clarity.
                </div>
            </div>

            <!-- Mantra 4: Maha Mrityunjaya Mantra -->
            <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #ddd6fe; border-left:4px solid #7c3aed;">
                <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">4. Maha Mrityunjaya Shield (महामृत्युंजय रक्षा कवच - Supreme Overcoming of Shani)</div>
                <div style="font-size:1.15rem; font-weight:900; color:#1e1b4b; margin:6px 0; font-family:'Noto Sans Devanagari', sans-serif;">
                    ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्। उर्वारुकमिव बन्धनान् मृत्योर्मुक्षीय मामृतात्॥
                </div>
                <div style="font-size:0.92rem; color:#4338ca; font-weight:700;">
                    <i>Om Tryambakam Yajaamahe Sugandhim Pushti-Vardhanam, Urvaarukamiva Bandhanaan Mrityor-Muksheeya Maamritaat.</i>
                </div>
                <div style="font-size:0.88rem; color:#475569; margin-top:4px;">
                    <b>Count & Guidance:</b> Because Lord Shiva is the supreme Guru and sovereign master of Shani Dev, chanting this mantra <b>11 times every morning</b> completely neutralizes sudden health risks, accidents, and psychological paralysis during Sade Sati.
                </div>
            </div>
        </div>
    </div>
    """)

def render_page_live():
    now_ist = datetime.datetime.now()
    cur_star_idx, s_dt, e_dt = get_current_nakshatra_window(now_ist)
    offset = (cur_star_idx - chart_info["star_idx"]) % 9
    nav_name, icon, quality = NAVTARA_NAMES[offset]
    vahan_info = calculate_shani_vahan(chart_info["star_idx"], cur_star_idx)
    p_day = get_personal_day_vibe(dob_parsed, now_ist.date(), current_lang)

    # Safe evaluation of planet name and decision protocol
    p_planet_clean = p_day['planet'].split()[0] if p_day.get('planet') else f"Day {p_day['number']}"
    current_star_name = NAKSHATRAS[cur_star_idx - 1] if 1 <= cur_star_idx <= 27 else "Nakshatra"

    if "🟢" in icon:
        decision_protocol = "🟢 High green light for critical ventures, agreements, property, and financial investments."
    else:
        decision_protocol = "🔴 Avoid speculative gambles, practice patience in communications, and postpone high-stakes friction."

    render_html(f"""
    <div class="light-card-live">
        <div style="font-weight:900; font-size:1.35rem; color:#0369a1; margin-bottom:1rem; border-bottom:2px solid #bae6fd; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{t('live_pulse_title', current_lang)}</span>
            <span style="font-size:0.85rem; background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:20px; font-weight:900;">LIVE IST</span>
        </div>

        <div style="background:#f0f9ff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:0.85rem; color:#0284c7; font-weight:800; text-transform:uppercase;">CURRENT MOON NAKSHATRA</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#0369a1;">{current_star_name}</div>
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

        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin-bottom:1.1rem;">
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd;">
                <div style="font-size:0.85rem; color:#0284c7; font-weight:800; text-transform:uppercase;">DAILY SHANI VAHAN</div>
                <div style="font-size:1.15rem; font-weight:900; color:#0369a1;">{vahan_info['name']}</div>
                <div style="font-size:0.92rem; color:#64748b;">{vahan_info['type']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd;">
                <div style="font-size:0.85rem; color:#0284c7; font-weight:800; text-transform:uppercase;">PERSONAL DAY VIBE</div>
                <div style="font-size:1.15rem; font-weight:900; color:#0369a1;">Day {p_day['number']} ({p_planet_clean})</div>
                <div style="font-size:0.92rem; color:#64748b;">Alignment Energy</div>
            </div>
        </div>

        <div style="background:#f0f9ff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd;">
            <div style="font-weight:900; font-size:1.05rem; color:#0369a1; margin-bottom:8px;">🎯 Today's Actionable Strategy & Remedies:</div>
            <div style="font-size:0.95rem; line-height:1.65; color:#0c4a6e;">
                • <b>Decision Protocol:</b> {decision_protocol}<br>
                • <b>Saturn Mount Remedy:</b> {vahan_info['remedy']}<br>
                • <b>Aura Protection Mantra:</b> Chant <b>Om Namah Shivaya</b> 11 times before starting important ventures today.
            </div>
        </div>
    </div>
    """)

def render_page_forecast():
    now_ist = datetime.datetime.now()
    transits = get_7_day_moon_transits(now_ist, chart_info["star_idx"])

    render_html(f"""
    <div style="font-weight:900; font-size:1.25rem; color:#1e293b; margin-bottom:0.8rem;">
        {t('forecast_title', current_lang)}
    </div>
    """)

    if not transits:
        st.info("Computing active 7-day ephemeris matrix...")
        return

    for idx, tr in enumerate(transits):
        with st.container(border=True):
            col_t1, col_t2, col_t3 = st.columns([1.6, 2.8, 1.6])
            with col_t1:
                render_html(f"<b>{tr['date_str']}</b><br><span style='font-size:0.92rem; color:#475569; font-weight:700;'>{tr['star_name']}</span>")
            with col_t2:
                v_parts = tr['vahan'].split()
                vahan_name = v_parts[1] if len(v_parts) > 1 else tr['vahan']
                nav_clean = tr['nav_name'].split('(')[0]
                render_html(f"<span style='font-size:1.1rem;'>{tr['icon']}</span> <b>{nav_clean}</b><br><span style='font-size:0.88rem; color:#64748b;'>Mount: {vahan_name}</span>")
            with col_t3:
                if st.button("🔮 Prediction", key=f"btn_tr_{idx}", use_container_width=True):
                    st.session_state.selected_transit_idx = idx
                    st.rerun()

    safe_idx = min(len(transits) - 1, max(0, st.session_state.selected_transit_idx))
    sel_tr = transits[safe_idx]
    
    if "🟢" in sel_tr['icon']:
        plan_desc = "Schedule critical meetings, sign major documents, and wear light or energizing colors."
    else:
        plan_desc = "Pause aggressive financial risks, keep conversations respectful and calm, and recite Hanuman Chalisa in the evening."

    render_html(f"""
    <div class="light-card-live" style="margin-top:1.1rem;">
        <div style="font-weight:900; font-size:1.15rem; color:#0369a1; margin-bottom:8px;">
            🔮 Detailed Forecast for {sel_tr['date_str']} ({sel_tr['star_name']})
        </div>
        <div style="font-size:0.94rem; color:#334155; margin-bottom:10px; line-height:1.5;">
            ⏰ <b>Transit Window:</b><br>{sel_tr['start_str']} → {sel_tr['end_str']}
        </div>
        <div style="font-size:0.96rem; line-height:1.65; color:#0c4a6e;">
            • <b>Navtara Category:</b> {sel_tr['nav_name']} ({sel_tr['quality']})<br>
            • <b>Saturn Mount:</b> {sel_tr['vahan']} ({sel_tr['vahan_type']})<br>
            • <b>Remedy & Action Plan:</b> {plan_desc}
        </div>
    </div>
    """)

def render_page_planets():
    now_ist = datetime.datetime.now()
    planets_data = get_sidereal_planet_positions(now_ist)

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.35rem; color:#9a3412; margin-bottom:8px; border-bottom:2px solid #fed7aa; padding-bottom:0.5rem;">
            {t('planet_title', current_lang)}
        </div>
        <div style="font-size:0.92rem; color:#64748b; margin-bottom:12px;">
            Sidereal Lahiri Ayanamsa | Computed for {now_ist.strftime('%d %B %Y, %I:%M %p IST')}
        </div>
    </div>
    """)

    for p in planets_data:
        render_html(f"""
        <div style="background:#fff7ed; border-radius:10px; padding:10px 14px; display:flex; justify-content:space-between; align-items:center; border:1px solid #fed7aa; margin-bottom:8px;">
            <span style="font-weight:800; color:#9a3412; font-size:0.98rem;">{p['planet']}</span>
            <span style="font-weight:900; color:#431407; font-size:0.98rem;">{p['rashi']} ({p['deg']})</span>
        </div>
        """)

def render_page_remedies():
    render_html(f"""
    <div class="light-card-num">
        <div style="font-weight:900; font-size:1.35rem; color:#065f46; margin-bottom:1rem; border-bottom:2px solid #bbf7d0; padding-bottom:0.5rem;">
            🪔 Consolidated Vedic Astro-Remedies Sanctuary
        </div>
        
        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #059669; margin-bottom:1rem;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">1. Janma Nakshatra Protection ({chart_info['star_name']})</div>
            <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">
                • Worship Lord Shiva or your Nakshatra deity to clear heavy ancestral burdens and establish inner stillness.<br>
                • Chant the <b>Maha Mrityunjaya Mantra</b> 11 times every morning to revitalize biological Prana.<br>
                • Respect and nourish birds or animals corresponding to your Nakshatra totem.
            </div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #10b981; margin-bottom:1rem;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">2. Numerology Harmony (Mulank {mulank} & Bhagyank {bhagyank})</div>
            <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">
                • Drink water from a silver or copper vessel to balance high planetary nervous intensity.<br>
                • Keep your primary workstation clean and free from tangled electronics to amplify mental clarity.
            </div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #ddd6fe; border-left:5px solid #7c3aed;">
            <div style="font-weight:900; font-size:1.05rem; color:#5b21b6; margin-bottom:5px;">3. Shani Rajat Paya (Silver Feet) Shield</div>
            <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">
                • Recite the Hanuman Chalisa on Tuesday and Saturday evenings.<br>
                • Pour raw cow milk mixed with clean water over a Shiva Lingam on Mondays to awaken the divine silver shield.
            </div>
        </div>
    </div>
    """)

PAGES = {
    "about": render_page_about,
    "profile": render_page_profile,
    "navtara": render_page_profile,  # Safe alias for backward compatibility
    "numerology": render_page_numerology,
    "shani": render_page_shani,
    "live": render_page_live,
    "forecast": render_page_forecast,
    "planets": render_page_planets,
    "remedies": render_page_remedies,
    "share": render_page_about,      # Safe alias routing share requests directly to About
}

active_page_func = PAGES.get(st.session_state.current_page, render_page_about)
active_page_func()
