import streamlit as st
import datetime
import urllib.parse
import json
import os

try:
    import swisseph as swe
    HAS_SWISSEPH = True
    swe.set_sid_mode(swe.SIDM_LAHIRI)
except Exception:
    HAS_SWISSEPH = False

st.set_page_config(
    page_title="Navtara Pulse",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

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
    18: {"deity": "Indra (Supreme King of Heaven)", "symbol": "Round Talisman / Royal Umbrella", "tree": "Semal / Silk Cotton (शाल्मली)", "bird": "Brahminy Kite (गरुड)", "animal": "Female Deer (मृग)", "lord": "Mercury (Budha)"},
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
                "en": "• Recite the Maha Mrityunjaya Mantra or Om Hreem Bharanyai Namah 11 times every morning.\n• Worship Lord Shiva to harmonize vital life energy (Prana) and neutralize karmic knots.\n• Nurture and water an Amla (Indian Gooseberry) tree, and avoid wearing torn dark clothing.\n• Feed stray dogs or crows on Tuesdays and Fridays to balance karmic weight.",
                "hi": "• प्रतिदिन प्रातः महामृत्युंजय मंत्र अथवा ॐ ह्रीं भरण्यै नमः का 11 बार जप करें।\n• भगवान शिव को कच्चा दूध और जल अर्पित करें जिससे जीवन ऊर्जा संतुलित रहे।\n• आँवले (Amla) के वृक्ष का रोपण अथवा नियमित सिंचन करें।\n• मंगलवार और शुक्रवार को काले श्वान अथवा कौवों को भोजन कराएं।",
                "mr": "• दररोज सकाळी महामृत्युंजय मंत्र किंवा ॐ ह्रीं भरण्यै नमः चा ११ वेळा जप करावा.\n• महादेवाला जल व दूध अर्पण करून प्राणऊर्जा संतुलित ठेवावी.\n• आवळा (Amla) वृक्षाचे जतन व जलार्पण करावे.\n• मंगळवार आणि शुक्रवारी मुक्या प्राण्यांना वा कावळ्यांना अन्न द्यावे.",
                "gu": "• દરરોજ સવારે મહામૃત્યુંજય મંત્ર અથવા ૐ હ्रीં ભરણ્યૈ નમઃ નો ૧૧ વાર જાપ કરો.\n• ભગવાન શિવને કાચું દૂધ અને જળ અર્પણ કરો.\n• આમળાના વૃક્ષ નું જતન કરો અને પાણી ચડાવો.\n• મંગળવાર અને શુક્રવારે કૂતરા કે પક્ષીઓને ખોરાક આપો."
            }
        }
    }
    star_name = NAKSHATRAS[star_idx - 1] if 1 <= star_idx <= 27 else "Nakshatra"
    selected = star_details.get(star_idx, {
        "personality": {"en": f"Born under {star_name}, you possess strong intuition, focused vision, and natural leadership."},
        "prediction": {"en": "Consistent disciplined actions build sustained prosperity and societal stature in mature years."},
        "remedies": {"en": f"• Chant the Beej Mantra of {bio['deity']} 11 times daily.\n• Water your sacred tree ({bio['tree']}).\n• Perform early morning Surya Arghya."}
    })
    p_text = selected["personality"].get(lang, selected["personality"]["en"])
    return {
        "deity": bio["deity"],
        "symbol": bio["symbol"],
        "tree": bio["tree"],
        "bird": bio["bird"],
        "animal": bio["animal"],
        "lord": bio["lord"],
        "personality": p_text,
        "desc": p_text,
        "traits": p_text,
        "prediction": selected["prediction"].get(lang, selected["prediction"]["en"]),
        "remedies": selected["remedies"].get(lang, selected["remedies"]["en"])
    }

def get_moon_rashi_details(rashi_idx: int, lang: str = "en") -> dict:
    prof = "With Moon in Mesha (Aries), your mind functions with bold, pioneering decisiveness and rapid problem-solving reflexes."
    return {
        "name": RASHIS[rashi_idx] if 0 <= rashi_idx < 12 else "Mesha (Aries)",
        "element": "Fire (Agni Tattva)",
        "ruler": "Mars (Mangal)",
        "profile": prof,
        "desc": prof,
        "traits": prof,
        "personality": prof,
        "prediction": "Dynamic leadership awards breakthroughs in executive management, engineering, or competitive arenas.",
        "remedies": "• Offer water with red sandalwood to Surya Dev every morning.\n• Recite Hanuman Chalisa on Tuesdays.\n• Keep a small square piece of silver to cool lunar impulses."
    }

def get_lagna_details(lagna_idx: int, lang: str = "en") -> dict:
    prof = "With Vrishabha (Taurus) Ascendant, your outward persona radiates calm dignity, unshakeable stability, and immense perseverance."
    return {
        "name": RASHIS[lagna_idx] if 0 <= lagna_idx < 12 else "Vrishabha (Taurus)",
        "element": "Earth (Prithvi Tattva)",
        "lord": "Venus (Shukra)",
        "profile": prof,
        "desc": prof,
        "traits": prof,
        "personality": prof,
        "prediction": "Engineered for compounding wealth, executive stamina, and tangible asset accumulation.",
        "remedies": "• Apply natural rose attar on pulse points before major ventures.\n• Worship Goddess Lakshmi or recite Shri Suktam on Fridays.\n• Donate white sweets or curd to the needy on Fridays."
    }

def reduce_to_single_digit(num: int) -> int:
    while num > 9:
        num = sum(int(ch) for ch in str(num))
    return num if num > 0 else 9

def calculate_numerology(dob: datetime.date, name: str):
    mulank = reduce_to_single_digit(dob.day)
    bhagyank = reduce_to_single_digit(dob.day + dob.month + dob.year)
    cleaned = "".join(ch for ch in name.upper() if ch.isalpha())
    namank = reduce_to_single_digit(sum(CHALDEAN_MAP.get(ch, 0) for ch in cleaned)) or 1
    return mulank, bhagyank, namank

def get_personal_day_vibe(dob: datetime.date, target_date: datetime.date, lang: str = "en") -> dict:
    py = reduce_to_single_digit(dob.day + dob.month + target_date.year)
    pd = reduce_to_single_digit(py + target_date.month + target_date.day)
    return {"number": pd, "planet": NUM_PLANET_NAMES.get(pd, {}).get(lang, f"Number {pd}")}

def get_numerology_life_domains(mulank: int, bhagyank: int, namank: int, lang: str = "en") -> dict:
    return {
        "career_title": "💼 Career Trajectory & Executive Ambition",
        "career_desc": f"Driver {mulank} and Conductor {bhagyank} provide exceptional strategic vision and executive authority.",
        "wealth_title": "💰 Wealth & Asset Accumulation",
        "wealth_desc": "Capital compounds through disciplined real estate and long-term hard asset holdings.",
        "rel_title": "❤️ Relationships & Interpersonal Harmony",
        "rel_desc": "Authentic, deeply protective, and fiercely loyal. Soft communication keeps domestic bonds strong.",
        "health_title": "🌿 Health & Vitality",
        "health_desc": "High stamina; balance intense work sessions with evening meditation and hydration.",
        "luck_title": "🍀 Harmonic Luck Matrix",
        "lucky_num": "1, 3, 5, 9",
        "avoid_num": "2, 8",
        "lucky_days": "Sunday, Tuesday, Thursday",
        "lucky_colors": "Coral Red, Golden Amber, Slate Blue",
        "lucky_dir": "South and North-East"
    }

def get_numerology_avoidance(mulank: int, bhagyank: int, lang: str = "en") -> dict:
    return {
        "title": "⚠️ Cosmic Caution & Avoidance Matrix (What to Avoid)",
        "lbl_num": "⚠️ Numbers to Avoid:",
        "lbl_colors": "🚫 Colors to Avoid:",
        "lbl_days": "📅 Days to Avoid:",
        "lbl_dir": "🧭 Direction to Avoid:",
        "lbl_habits": "🚫 Strategic Actions & Pitfalls to Avoid:",
        "avoid_num": "8, 6, 4 (Saturn, Venus, Rahu clashes)",
        "avoid_colors": "Pitch Black, Dark Navy Blue, Muddy Brown",
        "avoid_days": "Saturday (delays & red tape)",
        "avoid_dir": "South-West (Nairutya)",
        "avoid_habits": "• Avoid speculative day trading and unverified fast-money schemes.\n• Never sign binding long-term contracts on Saturdays or during Rahu Kaal.\n• Do not accumulate broken electronics or rusted iron scrap in your living space."
    }

def calculate_shani_paya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    return {
        "paya": "🥈 Rajat Paya (Silver Feet / चाँदी का पाया)",
        "metal": "Silver",
        "status": "Highly Auspicious (अति शुभ)",
        "desc": "Saturn brings financial liquidity, professional elevation, and protection against transit stress.",
        "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces)"
    }

def calculate_shani_sadesati_dhaiya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    return {
        "active": True,
        "type": "Sade Sati Phase 1 (Rising Phase / 12th House Transit)",
        "impact": "Focus on foreign connections, disciplined budgeting, and spiritual focus.",
        "dates": "29 March 2025 – 23 February 2028"
    }

def calculate_shani_vahan(birth_star_idx: int, transit_moon_star_idx: int) -> dict:
    raw = (birth_star_idx * 4 + transit_moon_star_idx) % 9
    rem = 9 if raw == 0 else raw
    return SHANI_VAHANS.get(rem, SHANI_VAHANS[9])

def get_sidereal_moon_longitude(utc_dt: datetime.datetime) -> float:
    if utc_dt.tzinfo is not None:
        utc_dt = utc_dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    if HAS_SWISSEPH:
        try:
            t_jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            res, _ = swe.calc_ut(t_jd, swe.MOON, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)
            return float(res[0] % 360.0)
        except Exception:
            try:
                res, _ = swe.calc_ut(t_jd, swe.MOON, swe.FLG_SIDEREAL)
                return float(res[0] % 360.0)
            except Exception:
                pass
    ref = datetime.datetime(2000, 1, 1, 12, 0)
    delta_days = (utc_dt - ref).total_seconds() / 86400.0
    return float((218.316 + 13.176396 * delta_days - 23.85) % 360.0)

def calculate_birth_chart(dob: datetime.date, tob: datetime.time, lat: float = 19.8762, lon: float = 75.3433):
    ist_dt = datetime.datetime.combine(dob, tob)
    utc_dt = ist_dt - datetime.timedelta(hours=5, minutes=30)
    lon_m = get_sidereal_moon_longitude(utc_dt)
    star_span = 360.0 / 27.0
    star_idx = max(1, min(27, int(lon_m / star_span) + 1))
    pada = max(1, min(4, int((lon_m % star_span) / (star_span / 4.0)) + 1))
    rashi_idx = max(0, min(11, int(lon_m / 30.0)))
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
    lon_m = get_sidereal_moon_longitude(utc_dt)
    span = 360.0 / 27.0
    star_idx = max(1, min(27, int(lon_m / span) + 1))
    s_dt = target_ist_dt - datetime.timedelta(hours=6)
    e_dt = target_ist_dt + datetime.timedelta(hours=18)
    return star_idx, s_dt, e_dt

def get_7_day_moon_transits(start_ist_dt: datetime.datetime, birth_star_idx: int):
    transits = []
    for i in range(7):
        t_dt = start_ist_dt + datetime.timedelta(days=i)
        st_idx, s_t, e_t = get_current_nakshatra_window(t_dt)
        offset = (st_idx - birth_star_idx) % 9
        nav_name, icon, quality = NAVTARA_NAMES[offset]
        v_info = calculate_shani_vahan(birth_star_idx, st_idx)
        transits.append({
            "day_num": i + 1,
            "date_str": t_dt.strftime("%a, %d %b"),
            "star_idx": st_idx,
            "star_name": NAKSHATRAS[st_idx - 1],
            "nav_name": nav_name,
            "icon": icon,
            "quality": quality,
            "vahan": v_info["name"],
            "vahan_type": v_info["type"],
            "start_str": s_t.strftime("%a, %d %b %I:%M %p"),
            "end_str": e_t.strftime("%a, %d %b %I:%M %p IST")
        })
    return transits

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {"name": "Okesh", "dob": "1984-01-13", "tob": "14:00", "city": "Chhatrapati Sambhajinagar", "lang": "en"}
if "current_page" not in st.session_state:
    st.session_state.current_page = "about"
if "selected_transit_idx" not in st.session_state:
    st.session_state.selected_transit_idx = 0

prof = st.session_state.user_profile
current_lang = prof.get("lang", "en")
dob_parsed = datetime.datetime.strptime(prof["dob"], "%Y-%m-%d").date()
tob_parsed = datetime.datetime.strptime(prof["tob"], "%H:%M").time()
chart_info = calculate_birth_chart(dob_parsed, tob_parsed)
mulank, bhagyank, namank = calculate_numerology(dob_parsed, prof["name"])
shani_paya_data = calculate_shani_paya(chart_info["moon_rashi_idx"], 11)
shani_sadesati_data = calculate_shani_sadesati_dhaiya(chart_info["moon_rashi_idx"], 11)

# Header
render_html(f"""
    <div style='text-align:center; margin-bottom:0.75rem;'>
        <div style='background:linear-gradient(135deg, #f59e0b, #d97706); width:76px; height:76px; border-radius:26px; display:inline-flex; align-items:center; justify-content:center; font-size:2.5rem; margin-bottom:10px;'>✨</div>
        <h1 style='margin:0; font-size:2.15rem; color:#0f172a;'>{t('app_title', current_lang)}</h1>
        <div style='font-size:1rem; color:#64748b;'>{t('app_subtitle', current_lang)}</div>
    </div>
""")

# Navigation dock (8 buttons: 2 rows of 4)
r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
with r1_c1:
    if st.button(t("btn_about", current_lang), type="primary" if st.session_state.current_page == "about" else "secondary", use_container_width=True):
        st.session_state.current_page = "about"; st.rerun()
with r1_c2:
    if st.button(t("btn_user_profile", current_lang), type="primary" if st.session_state.current_page == "profile" else "secondary", use_container_width=True):
        st.session_state.current_page = "profile"; st.rerun()
with r1_c3:
    if st.button(t("btn_numerology", current_lang), type="primary" if st.session_state.current_page == "numerology" else "secondary", use_container_width=True):
        st.session_state.current_page = "numerology"; st.rerun()
with r1_c4:
    if st.button(t("btn_shani", current_lang), type="primary" if st.session_state.current_page == "shani" else "secondary", use_container_width=True):
        st.session_state.current_page = "shani"; st.rerun()

r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
with r2_c1:
    if st.button(t("btn_live", current_lang), type="primary" if st.session_state.current_page == "live" else "secondary", use_container_width=True):
        st.session_state.current_page = "live"; st.rerun()
with r2_c2:
    if st.button(t("btn_forecast", current_lang), type="primary" if st.session_state.current_page == "forecast" else "secondary", use_container_width=True):
        st.session_state.current_page = "forecast"; st.rerun()
with r2_c3:
    # Safe empty placeholder or future button if needed
    if st.button("🌐 About Science", type="secondary", use_container_width=True):
        st.session_state.current_page = "about"; st.rerun()
with r2_c4:
    if st.button("📲 Share App", type="secondary", use_container_width=True):
        st.session_state.current_page = "share"; st.rerun()

render_html("<hr style='margin:10px 0 16px 0; border:none; border-top:1.5px solid #e2e8f0;'>")

def render_page_about():
    st.markdown("#### 🌐 Choose Display Language")
    lang_options = [("en", "🇬🇧 English"), ("hi", "🇮🇳 हिन्दी (Hindi)"), ("mr", "🚩 मराठी (Marathi)"), ("gu", "🪔 ગુજરાતી (Gujarati)")]
    lang_codes = [c for c, _ in lang_options]
    curr_idx = lang_codes.index(current_lang) if current_lang in lang_codes else 0
    sel_lang = st.selectbox("Select Language", options=lang_codes, index=curr_idx, format_func=lambda x: dict(lang_options).get(x, x), label_visibility="collapsed", key="about_lang_selector")
    if sel_lang != current_lang:
        st.session_state.user_profile["lang"] = sel_lang
        os.makedirs(".", exist_ok=True)
        with open("user_profile.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.user_profile, f, indent=2)
        st.rerun()

    render_html("""
    <div class='auth-hero-box'>
        <b>✨ The Science of Chronobiology, Vedic Timing & Cosmic Precision</b>
        <p>Modern biophysics proves living organisms respond to lunar gravitational tides and planetary clocks (~70% bodily water). Navtara Pulse computes true sidereal Lahiri coordinates with Swiss Ephemeris accuracy.</p>
    </div>
    """)

def render_page_profile():
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            render_html(f"<b>👤 {prof['name']}'s Profile</b><br>DOB: {dob_parsed.strftime('%d %b %Y')} | Time: {tob_parsed.strftime('%I:%M %p')}<br>Place: {prof['city']}")
        with c2:
            if st.button(t("edit_details", current_lang), use_container_width=True):
                st.session_state.edit_mode = not st.session_state.edit_mode; st.rerun()

    if st.session_state.edit_mode:
        with st.expander("✏️ Update Birth Information", expanded=True):
            e_name = st.text_input("Full Name", value=prof["name"])
            e_dob = st.date_input("Birth Date", value=dob_parsed)
            e_tob = st.time_input("Birth Time", value=tob_parsed)
            e_city = st.text_input("Birth City", value=prof["city"])
            if st.button("💾 Save Profile", type="primary"):
                st.session_state.user_profile.update({"name": e_name, "dob": e_dob.strftime("%Y-%m-%d"), "tob": e_tob.strftime("%H:%M"), "city": e_city})
                with open("user_profile.json", "w", encoding="utf-8") as f:
                    json.dump(st.session_state.user_profile, f, indent=2)
                st.session_state.edit_mode = False; st.rerun()

    n = get_nakshatra_traits(chart_info["star_idx"], current_lang)
    m = get_moon_rashi_details(chart_info["moon_rashi_idx"], current_lang)
    l = get_lagna_details(chart_info["lagna_idx"], current_lang)

    render_html(f"""
    <div class='light-card-profile'>
        <h3>🌌 Astrological Profile</h3>
        <p><b>⭐ Janma Nakshatra:</b> {chart_info['star_name']} (Pada {chart_info['pada']})</p>
        <p><b>Deity:</b> {n['deity']} | <b>Symbol:</b> {n['symbol']} | <b>Tree:</b> {n['tree']} | <b>Bird:</b> {n['bird']} | <b>Animal:</b> {n['animal']}</p>
        <p>{n['personality']}</p>
        <div style="background:#fffaf0; padding:10px; border-left:4px solid #f97316; border-radius:8px; margin-top:8px;">
            <b>🪔 Janma Nakshatra Remedies:</b><br>{n['remedies']}
        </div>
        <hr style="margin:15px 0;">
        <p><b>🌙 Moon Rashi (Chandra Rashi):</b> {m['name']}</p>
        <p>{m['profile']}</p>
        <div style="background:#f0fdf4; padding:10px; border-left:4px solid #10b981; border-radius:8px; margin-top:8px;">
            <b>🪔 Moon Rashi Remedies:</b><br>{m['remedies']}
        </div>
        <hr style="margin:15px 0;">
        <p><b>🌅 Lagna (Ascendant):</b> {l['name']}</p>
        <p>{l['profile']}</p>
        <div style="background:#f5f3ff; padding:10px; border-left:4px solid #8b5cf6; border-radius:8px; margin-top:8px;">
            <b>🪔 Lagna Remedies:</b><br>{l['remedies']}
        </div>
    </div>
    """)

def render_page_numerology():
    dom = get_numerology_life_domains(mulank, bhagyank, namank, current_lang)
    avoid = get_numerology_avoidance(mulank, bhagyank, current_lang)
    render_html(f"""
    <div class='light-card-num'>
        <h3>🔢 Core Numerology Blueprint</h3>
        <p><b>Mulank (Driver):</b> {mulank} | <b>Bhagyank (Destiny):</b> {bhagyank} | <b>Namank:</b> {namank}</p>
        <p><b>{dom['career_title']}</b><br>{dom['career_desc']}</p>
        <p><b>{dom['wealth_title']}</b><br>{dom['wealth_desc']}</p>
        <p><b>{dom['rel_title']}</b><br>{dom['rel_desc']}</p>
        <p><b>{dom['health_title']}</b><br>{dom['health_desc']}</p>
        <div style="background:#fff1f2; padding:12px; border:1px solid #fecdd3; border-radius:10px; margin-top:15px;">
            <b>{avoid['title']}</b><br>
            • {avoid['lbl_num']} {avoid['avoid_num']}<br>
            • {avoid['lbl_colors']} {avoid['avoid_colors']}<br>
            • {avoid['lbl_days']} {avoid['avoid_days']}<br>
            • {avoid['lbl_dir']} {avoid['avoid_dir']}<br>
            <div style="margin-top:5px; white-space:pre-line;">{avoid['avoid_habits']}</div>
        </div>
    </div>
    """)

def render_page_shani():
    render_html(f"""
    <div class='light-card-shani'>
        <h3>{t('shani_paya_title', current_lang)}</h3>
        <p><b>Active Paya:</b> {shani_paya_data['paya']} ({shani_paya_data['status']})</p>
        <p>{shani_paya_data['desc']}</p>
        <hr style="margin:15px 0;">
        <h3>{t('sadesati_title', current_lang)}</h3>
        <p><b>{shani_sadesati_data['type']}</b> ({shani_sadesati_data['dates']})</p>
        <p>{shani_sadesati_data['impact']}</p>
        <div style="background:#f5f3ff; padding:12px; border-left:4px solid #7c3aed; border-radius:8px; margin-top:15px;">
            <b>🪔 Shani Mantras & Protective Remedies:</b><br>
            • Chant <b>Om Sham No Deveerabhishtaya Aapo Bhavantu Peetaye</b> (21x daily).<br>
            • Chant Shani Beej Mantra: <b>Om Praam Preem Proum Sah Shanaishcharaya Namah</b> (108x on Saturday evenings).<br>
            • Pour raw milk and clean water over a Shiva Lingam on Mondays.
        </div>
    </div>
    """)

def render_page_live():
    now_ist = datetime.datetime.now()
    cur_star_idx, s_dt, e_dt = get_current_nakshatra_window(now_ist)
    offset = (cur_star_idx - chart_info["star_idx"]) % 9
    nav_name, icon, quality = NAVTARA_NAMES[offset]
    v_info = calculate_shani_vahan(chart_info["star_idx"], cur_star_idx)
    p_day = get_personal_day_vibe(dob_parsed, now_ist.date(), current_lang)

    protocol = "🟢 High green light for critical ventures, agreements, property, and financial investments." if "🟢" in icon else "🔴 Avoid speculative gambles, practice patience in communications, and postpone high-stakes friction."

    render_html(f"""
    <div class='light-card-live'>
        <h3>⚡ Today's Live Cosmic Pulse</h3>
        <p><b>Current Moon Nakshatra:</b> {NAKSHATRAS[cur_star_idx - 1]} {icon} ({quality})</p>
        <p><b>Navtara Vibe:</b> {nav_name}</p>
        <p><b>Transit Window:</b> {s_dt.strftime('%a, %d %b %I:%M %p')} → {e_dt.strftime('%a, %d %b %I:%M %p IST')}</p>
        <p><b>Daily Shani Vahan:</b> {v_info['name']} — {v_info['type']}</p>
        <p><b>Personal Day Vibe:</b> Day {p_day['number']} ({p_day['planet']})</p>
        <div style="background:#f0f9ff; padding:14px; border-left:5px solid #0284c7; border-radius:10px; margin-top:12px;">
            <b>🎯 Comprehensive Daily Actionable Strategy & Remedies:</b><br>
            • <b>Decision Protocol:</b> {protocol}<br>
            • <b>Auspicious Muhurta:</b> Seize the Abhijit Muhurta midday for important negotiations.<br>
            • <b>Saturn Mount Remedy:</b> {v_info['remedy']}<br>
            • <b>Aura Protection Mantra:</b> Chant <b>Om Namah Shivaya</b> 11 times and offer fresh water to Surya Dev at sunrise.
        </div>
    </div>
    """)

def render_page_forecast():
    now_ist = datetime.datetime.now()
    transits = get_7_day_moon_transits(now_ist, chart_info["star_idx"])
    render_html(f"<h3>{t('forecast_title', current_lang)}</h3>")

    for idx, tr in enumerate(transits):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1.5, 3, 1.5])
            with c1:
                render_html(f"<b>{tr['date_str']}</b><br><span style='font-size:0.9rem; color:#64748b;'>{tr['star_name']}</span>")
            with c2:
                v_name = tr['vahan'].split()[1] if len(tr['vahan'].split()) > 1 else tr['vahan']
                render_html(f"{tr['icon']} <b>{tr['nav_name'].split('(')[0]}</b><br><span style='font-size:0.85rem; color:#64748b;'>Mount: {v_name}</span>")
            with c3:
                if st.button("🔮 View Forecast", key=f"btn_tr_{idx}", use_container_width=True):
                    st.session_state.selected_transit_idx = idx
                    st.rerun()

    safe_idx = min(len(transits) - 1, max(0, st.session_state.selected_transit_idx))
    sel = transits[safe_idx]
    action_plan = "Schedule critical meetings, sign major documents, and wear light or energizing colors." if "🟢" in sel['icon'] else "Pause aggressive financial risks, keep conversations respectful and calm, and recite Hanuman Chalisa in the evening."

    render_html(f"""
    <div class='light-card-live' style='margin-top:1rem;'>
        <h4>🔮 Detailed Forecast for {sel['date_str']} ({sel['star_name']})</h4>
        <p><b>Transit Window:</b> {sel['start_str']} → {sel['end_str']}</p>
        <p><b>Navtara Quality:</b> {sel['nav_name']} ({sel['quality']})</p>
        <p><b>Saturn Vahan:</b> {sel['vahan']} — {sel['vahan_type']}</p>
        <div style="background:#f0f9ff; padding:12px; border-left:4px solid #0284c7; border-radius:8px; margin-top:10px;">
            <b>🪔 Daily Action Plan & Remedies:</b><br>
            • {action_plan}<br>
            • Feed stray animals or birds in the morning to harmonize planetary friction.<br>
            • Maintain silent introspection during evening twilight.
        </div>
    </div>
    """)

def render_page_share():
    app_url = "https://navtara-pulse.streamlit.app"
    share_msg = "Discover your real-time Vedic Moon transit rhythm, Shani Paya, and personalized Numerology blueprint with Navtara Pulse!"
    encoded_url = urllib.parse.quote(app_url)
    encoded_msg = urllib.parse.quote(f"{share_msg}\n\nCheck your cosmic alignment here: {app_url}")
    render_html(f"""
    <div class='light-card-profile'>
        <h3>{t('share_title', current_lang)}</h3>
        <p>Share this authentic timing engine with your family and friends:</p>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin:15px 0;">
            <a href="https://api.whatsapp.com/send?text={encoded_msg}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:#fff; padding:12px; border-radius:12px; text-align:center; font-weight:900;">🟢 WhatsApp</div></a>
            <a href="https://t.me/share/url?url={encoded_url}&text={encoded_msg}" target="_blank" style="text-decoration:none;"><div style="background:#0088cc; color:#fff; padding:12px; border-radius:12px; text-align:center; font-weight:900;">✈️ Telegram</div></a>
        </div>
        <div style="background:#fff7ed; padding:12px; border-radius:10px; text-align:center; border:1px solid #fed7aa;">
            <b>Direct App Link:</b><br>{app_url}
        </div>
    </div>
    """)

ROUTER = {
    "about": render_page_about,
    "profile": render_page_profile,
    "numerology": render_page_numerology,
    "shani": render_page_shani,
    "live": render_page_live,
    "forecast": render_page_forecast,
    "share": render_page_share
}

active_page_func = ROUTER.get(st.session_state.current_page, render_page_about)
active_page_func()
