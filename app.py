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

# Helper function to inject clean HTML without triggering Markdown code block formatting
def render_html(html_string: str):
    """
    Renders HTML safely by stripping all leading whitespace from every line.
    Prevents Streamlit Markdown engine from mistaking indented HTML for <pre><code> blocks.
    """
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

render_html("""
<style>
    /* Responsive mobile container with fluid typography */
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
    
    /* Themed content cards */
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

    /* Tactile navigation buttons */
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
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))

NAKHATRAS = [
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
    """Returns detailed Nakshatra bio, personality breakdown, prediction, and remedies."""
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
    
    star_name = NAKHATRAS[star_idx - 1] if 1 <= star_idx <= 27 else "Nakshatra"
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
    
    return {
        "deity": bio["deity"],
        "symbol": bio["symbol"],
        "tree": bio["tree"],
        "bird": bio["bird"],
        "animal": bio["animal"],
        "lord": bio["lord"],
        "personality": selected_star["personality"].get(lang, selected_star["personality"]["en"]),
        "prediction": selected_star["prediction"].get(lang, selected_star["prediction"]["en"]),
        "remedies": selected_star["remedies"].get(lang, selected_star["remedies"]["en"])
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
    
    return {
        "name": selected["name"],
        "element": selected["element"],
        "ruler": selected["ruler"],
        "profile": selected["profile"].get(lang, selected["profile"]["en"]),
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
            "gu": "લગ્નેશના શુભ પ્રભાવથી ઉત્તમ આરોગ્ય અને પ્રતિષ્ઠા વધે છે."
        },
        "remedies": {
            "en": "• Practice daily morning Pranayama to align physical breath with mental vitality.\n• Strengthen Lagna lord through mindful daily discipline and charity.",
            "hi": "• नित्य प्रातः प्राणायाम करें जिससे लग्न की जैविक ऊर्जा सशक्त रहे।\n• लग्नेश के मंत्र का श्रद्धापूर्वक जप करें।",
            "mr": "• नियमित प्राणायाम करून प्राणशक्ती वाढवावी.\n• लग्नेशाची आराधना करावी.",
            "gu": "• નિયમિત પ્રાણાયામ કરો અને લગ્નેશની કૃપા મેળવો."
        }
    })
    
    return {
        "name": selected["name"],
        "element": selected["element"],
        "lord": selected["lord"],
        "profile": selected["profile"].get(lang, selected["profile"]["en"]),
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
    planet_info = NUM_PLANET_NAMES.get(personal_day, {}).get(lang, f"Number {personal_day}")
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

def calculate_shani_paya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    """Calculates Saturn's foot metal based on Moon Sign relative to Saturn's sign."""
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
    """Determines active Sade Sati or Dhaiya phase."""
    diff = (saturn_transit_rashi_idx - moon_rashi_idx) % 12
    if diff == 11:
        return {
            "active": True,
            "type": "Sade Sati Phase 1 (Rising Phase / 12th House Transit)",
            "impact": "Saturn transits the 12th from your Moon. Focus on strategic budgeting, foreign avenues, spiritual grounding, and avoiding mental overthinking.",
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
    moon_mean_lon = (218.316 + 13.176396 * delta_days - 23.85) % 360.0
    return float(moon_mean_lon)

def calculate_birth_chart(dob: datetime.date, tob: datetime.time, lat: float = 19.8762, lon: float = 75.3433):
    """Calculates sidereal Moon Nakshatra, Pada, Moon Rashi, and Lagna."""
    ist_dt = datetime.datetime.combine(dob, tob)
    utc_dt = ist_dt - datetime.timedelta(hours=5, minutes=30)
    
    moon_lon = get_sidereal_moon_longitude(utc_
