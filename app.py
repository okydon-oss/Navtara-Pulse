import streamlit as st
import datetime
import urllib.parse
import json
import os
import math

try:
    from geopy.geocoders import Nominatim
    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False

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
    html { font-size: 16px; }
    @media (max-width: 640px) {
        html { font-size: 15.5px; }
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
    1: {"en": "Sun (Surya / सूर्य)", "hi": "सूर्य (Sun)"},
    2: {"en": "Moon (Chandra / चन्द्र)", "hi": "चन्द्र (Moon)"},
    3: {"en": "Jupiter (Brihaspati / गुरु)", "hi": "गुरु (Jupiter)"},
    4: {"en": "Rahu (North Node / राहु)", "hi": "राहु (Rahu)"},
    5: {"en": "Mercury (Budha / बुध)", "hi": "बुध (Mercury)"},
    6: {"en": "Venus (Shukra / शुक्र)", "hi": "शुक्र (Venus)"},
    7: {"en": "Ketu (South Node / केतु)", "hi": "केतु (Ketu)"},
    8: {"en": "Saturn (Shani / शनि)", "hi": "शनि (Saturn)"},
    9: {"en": "Mars (Mangal / मंगल)", "hi": "मंगल (Mars)"}
}

TRANSLATIONS = {
    "en": {
        "app_title": "✨ Navtara Pulse",
        "app_subtitle": "Vedic Nakshatra Rhythm & Cosmic Precision",
        "btn_about": "✨ About App",
        "btn_user_profile": "👤 User Profile",
        "btn_numerology": "🔢 Numerology",
        "btn_shani": "🪐 Shani & Sade Sati",
        "btn_live": "⚡ Live Prediction",
        "btn_forecast": "🗓️ 7 Days Prediction",
        "btn_mantra": "📿 Mantra Sadhana",
        "edit_details": "✏️ Edit Details",
        "save_details": "💾 Save Profile",
        "cancel": "Cancel",
        "name_label": "Full Name",
        "dob_label": "Birth Date",
        "tob_label": "Birth Time",
        "city_label": "Birth Location / City Name",
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
        "btn_shani": "🪐 शनि एवं साढ़े साती",
        "btn_live": "⚡ आज का फल",
        "btn_forecast": "🗓️ 7 दिवसीय फल",
        "btn_mantra": "📿 मंत्र साधना",
        "edit_details": "✏️ विवरण बदलें",
        "save_details": "💾 सुरक्षित करें",
        "cancel": "रद्द करें",
        "name_label": "पूरा नाम",
        "dob_label": "जन्म तिथि",
        "tob_label": "जन्म समय",
        "city_label": "जन्म स्थान का नाम",
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
    }
}

def t(key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))

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

# ALL 27 NAKSHATRAS EXPLICITLY DEFINED
NAKSHATRA_RICH_PROFILES = {
    1: {
        "core": "Pioneering initiator, rapid problem solver, intuitive healer, and swift executive.",
        "strengths": "Instant crisis responsiveness, fearless courage to break new ground, charismatic optimism, and high metabolic recovery speed.",
        "shadows": "Restlessness, impulsiveness, leaving half-finished projects when adrenaline wanes, and impatience with slower teammates.",
        "careers": "Emergency response, surgical/medical leadership, technological startups, aviation, high-speed project turnaround.",
        "prediction": "Dynamic early rise, with structural tests around age 28-30 leading to lasting executive distinction and institutional authority.",
        "remedies": "• Chant Om Ashwibhyam Namah 11 times every morning.\n• Feed green fodder to horses or cows on Tuesdays.\n• Plant and nurture a Strychnine (Kuchila) tree."
    },
    2: {
        "core": "Enduring moral resilience, deep magnetic charisma, uncompromising principles, and capacity to thrive under immense pressure.",
        "strengths": "Unshakeable loyalty, profound ability to manage high-stakes turnarounds, emotional fearlessness, and calm authority during restructuring.",
        "shadows": "All-or-nothing emotional intensity, stubborn resistance to compromise, holding emotional grudges, and taking on extreme burdens alone.",
        "careers": "Executive management, heavy industry, judicial leadership, forensic investigations, asset management, and creative transformation.",
        "prediction": "Major life transformations every 7-9 years. Obstacles faced in early career evolve into permanent asset ownership and executive authority in mature years.",
        "remedies": "• Recite the Maha Mrityunjaya Mantra 11 times daily.\n• Water an Amla tree regularly.\n• Feed stray dogs or crows on Tuesdays and Fridays to balance ancestral weight."
    },
    3: {
        "core": "Transformative intellect, razor-sharp discernment, and relentless pursuit of factual truth.",
        "strengths": "Uncompromising analytical clarity, piercing through superficial pretense, formidable debate skills, and courageous technical leadership.",
        "shadows": "Sharp or caustic speech during anger, hyper-critical perfectionism, and internal friction from suppressed irritation.",
        "careers": "Defense, metallurgy, software engineering, investigative journalism, precision manufacturing, and corporate auditing.",
        "prediction": "Early disciplined labor lays the foundation for formidable command and senior leadership in mid-to-late life.",
        "remedies": "• Offer water mixed with red sandalwood to Surya Dev.\n• Recite the Gayatri Mantra 24 times daily.\n• Nurture a Cluster Fig (Gular) tree."
    },
    4: {
        "core": "Creative charm, material refinement, persistent focus on asset compounding, and magnetic aesthetic taste.",
        "strengths": "Exceptional patience, capacity to cultivate tangible wealth, refined persuasive speech, and unwavering loyalty in long-term relationships.",
        "shadows": "Possessiveness, reluctance to adapt to sudden disruptions, and over-indulgence in sensory comfort.",
        "careers": "Luxury commodities, architecture, finance, agriculture, performing arts, and hospitality leadership.",
        "prediction": "Continuous compounding of assets across life, peaking in major material prosperity and domestic fulfillment after age 32.",
        "remedies": "• Offer raw milk on a Shiva Lingam on Mondays.\n• Water a Jamun tree regularly.\n• Drink clean water from a silver cup."
    },
    5: {
        "core": "Perpetual curiosity, versatile communicative intelligence, analytical agility, and restless exploratory spirit.",
        "strengths": "Brilliant research instincts, mental flexibility, networking ease, and ability to balance multiple complex projects.",
        "shadows": "Over-thinking, chronic second-guessing, mental restlessness, and susceptibility to sensory distractions.",
        "careers": "Telecommunications, market research, journalism, travel and logistics, software architecture, and advisory.",
        "prediction": "Dynamic exploratory phases during youth consolidate into senior consulting and strategic advisory roles by mid-career.",
        "remedies": "• Chant Om Somaya Namah 11 times on Wednesdays.\n• Water an Acacia Catechu (Khair) tree.\n• Donate green lentils or green clothing to students."
    },
    6: {
        "core": "Storm-like intellectual intensity, emotional depth, transformative breakthrough power, and crisis navigation.",
        "strengths": "Piercing through illusions, fearlessness during organizational crises, deep technological curiosity, and resilience.",
        "shadows": "Cynicism, destructive emotional outbursts, holding onto deep-seated grief, and creating self-imposed friction.",
        "careers": "Advanced technology, cybersecurity, data science, environmental engineering, psychotherapy, and investigative analysis.",
        "prediction": "Restructuring life crises forge exceptional wisdom, leading to radical breakthroughs and intellectual sovereignty in mature years.",
        "remedies": "• Chant Om Namah Shivaya 108 times at twilight.\n• Water an Agarwood tree.\n• Feed stray animals or birds on Saturdays."
    },
    7: {
        "core": "Benevolent wisdom, profound restorative resilience, pedagogical leadership, and philosophical balance.",
        "strengths": "Capacity to bounce back from any setback, inspiring optimism in teams, deep ethical grounding, and generous mentorship.",
        "shadows": "Over-idealism, taking on others' emotional problems, and hesitation to take tough disciplinary decisions.",
        "careers": "Higher education, jurisprudence, civil administration, counseling, publishing, and spiritual philanthropy.",
        "prediction": "Steady, compounding reputation. Life brings multiple opportunities for renewal, leading to lasting prestige and ancestral honor.",
        "remedies": "• Chant Om Brihaspataye Namah 19 times on Thursdays.\n• Water a sacred Bamboo tree.\n• Donate yellow chickpeas or turmeric to elders."
    },
    8: {
        "core": "Nourishing discipline, institutional loyalty, deep patience, and unshakeable ethical backbone.",
        "strengths": "Organizational stamina, ability to support large ecosystems, supreme reliability, and grounded crisis stewardship.",
        "shadows": "Rigid traditionalism, self-righteousness, and stubborn resistance to new methods.",
        "careers": "Public administration, institutional governance, social welfare, core manufacturing, banking, and executive mentorship.",
        "prediction": "Gradual, unstoppable ascent. The golden period begins after age 36, establishing permanent societal respect.",
        "remedies": "• Water a sacred Peepal tree on Saturdays without touching it.\n• Recite the Shani Beej Mantra 21 times.\n• Feed whole-wheat bread to crows."
    },
    9: {
        "core": "Hypnotic psychological insight, strategic shrewdness, deep esoteric intuition, and tactical mastery.",
        "strengths": "Ability to read unspoken intentions, razor-sharp intellect, independence, and formidable protective instincts.",
        "shadows": "Chronic suspicion, secretive behavior, venomous speech when betrayed, and emotional isolation.",
        "careers": "Diplomacy, strategic intelligence, corporate defense, pharmacology, psychoanalysis, and contract negotiation.",
        "prediction": "Early testing in interpersonal trusts evolves into supreme strategic acumen and mastery over complex systems.",
        "remedies": "• Offer milk and water to Lord Shiva on Mondays.\n• Water a Nagkeshar tree.\n• Maintain strict ethical honesty in speech."
    },
    10: {
        "core": "Ancestral authority, regal dignity, traditional pride, and executive commanding presence.",
        "strengths": "Natural leadership charisma, noble principles, respect for legacy and lineage, and protective stewardship of teams.",
        "shadows": "Ego sensitivity, resentment of subordinate feedback, and burden of high familial expectations.",
        "careers": "Corporate governance, politics, legacy business stewardship, heritage conservation, and senior civil service.",
        "prediction": "Strong generational blessings. Life brings executive authority and enduring family honor in mature years.",
        "remedies": "• Perform Pitru Tarpana or offer clean water facing South.\n• Water a sacred Banyan (Bargad) tree.\n• Donate black sesame seeds on Amavasya."
    },
    11: {
        "core": "Charismatic magnetism, social elegance, creative luxury orientation, and pursuit of prosperity.",
        "strengths": "Diplomatic warmth, natural aesthetic eye, relaxed confidence, and ability to manifest wealth and alliances.",
        "shadows": "Procrastination, indulgence in leisure, avoidance of harsh confrontational realities, and vanity.",
        "careers": "Creative direction, media production, luxury brand management, public relations, and high-end brokerage.",
        "prediction": "Fortunate social alliances and creative projects bring compounding financial comfort and celebrated status.",
        "remedies": "• Chant Om Shukraya Namah 16 times on Fridays.\n• Water a Palasa (Flame of the Forest) tree.\n• Donate white sweets or milk to the needy."
    },
    12: {
        "core": "Nobility of character, contractual fidelity, patronage of truth, and unyielding dependability.",
        "strengths": "Uncompromising integrity, strong alliance building, societal respect, and structured philanthropy.",
        "shadows": "Rigid insistence on social protocols, codependency in partnerships, and intolerance of informal behavior.",
        "careers": "Judiciary, corporate alliances, international trade contracts, governmental administration, and auditing.",
        "prediction": "Ascent into senior governance and institutional stewardship, marked by universal trust and civic honors.",
        "remedies": "• Offer water mixed with kumkum to the morning Sun.\n• Water a Plaksha tree.\n• Feed red cows or bulls on Sundays."
    },
    13: {
        "core": "Dexterous problem solver, commercial acumen, detailed analytical eye, and humorous intellect.",
        "strengths": "Meticulous craftsmanship, tactical agility, high hand-brain coordination, and commercial wit.",
        "shadows": "Nervous anxiety, over-critical tendencies, mood swings, and occasional manipulative cleverness under pressure.",
        "careers": "Accounting, engineering precision, data architecture, trade brokerage, manufacturing quality control, and writing.",
        "prediction": "Rapid career progression through technical skill and commercial brilliance, leading to financial independence.",
        "remedies": "• Chant the Gayatri Mantra 24 times at sunrise.\n• Water a Chameli (Jasmine) plant daily.\n• Keep speech clean and honor maternal figures."
    },
    14: {
        "core": "Architectural genius, vibrant charisma, sparkling aesthetic ambition, and mechanical insight.",
        "strengths": "Exceptional visual imagination, eye for proportion and design, charismatic presentation, and inventive drive.",
        "shadows": "Superficial vanity, restlessness, argumentative streak when creative vision is questioned, and financial extravagance.",
        "careers": "Architecture, civil infrastructure, automotive design, diamond/gem trading, fashion design, and branding.",
        "prediction": "Pioneering creative or technical creations gain widespread recognition, establishing lasting assets.",
        "remedies": "• Recite the Hanuman Chalisa on Tuesdays.\n• Water a Bilva (Bael Patra) tree.\n• Keep a clean red handkerchief in your pocket."
    },
    15: {
        "core": "Independent visionary, diplomatic agility, trade adaptability, and freedom-loving momentum.",
        "strengths": "Global perspective, exceptional networking, quick commercial instinct, and flexible adaptability to change.",
        "shadows": "Commitment hesitation, spreading energy too thin, and unpredictability in long-term partnerships.",
        "careers": "International commerce, aviation, software consulting, import-export, travel management, and media relations.",
        "prediction": "Major expansion through cross-border connections and innovative commercial systems, compounding wealth after age 30.",
        "remedies": "• Chant Rahu Beej Mantra 18 times at twilight on Saturdays.\n• Water an Arjuna tree.\n• Donate black blankets or mustard oil to the needy."
    },
    16: {
        "core": "Unstoppable ambition, dual energies of alliance and fire, competitive tenacity, and goal focus.",
        "strengths": "Relentless perseverance, formidable debate power, strategic alliance-building, and victory over adversaries.",
        "shadows": "Envy of competitors, burning bridges when goals shift, and exhaustion from ceaseless striving.",
        "careers": "Executive leadership, litigation, corporate acquisitions, industrial operations, and political strategy.",
        "prediction": "Late blooming triumph. Challenges faced in early career transform into undeniable executive authority in mature life.",
        "remedies": "• Chant Om Indragni Namah 11 times in the morning.\n• Water a Kaith (Wood Apple) tree.\n• Avoid interpersonal ego disputes and practice celebrating others' wins."
    },
    17: {
        "core": "Diplomatic loyalty, devotional warmth, alliance-building grace, and calm endurance under pressure.",
        "strengths": "Unshakeable friendship, organizational diplomacy, international appeal, and ability to unite divided groups.",
        "shadows": "Suppressing emotional hurt, vulnerability to being taken advantage of by selfish partners, and dietary neglect.",
        "careers": "Diplomacy, human resources, organizational development, international relations, corporate counseling, and music.",
        "prediction": "Long-standing loyal partnerships yield massive dividends. Mature years are blessed with peace, travel, and stable wealth.",
        "remedies": "• Light a mustard-oil lamp under a Peepal tree on Saturdays.\n• Water a Bakula tree.\n• Maintain truthful, authentic relationships."
    },
    18: {
        "core": "Commanding sovereignty, protective courage, senior executive stature, and fierce defensive instinct.",
        "strengths": "Natural executive poise, protective leadership over large teams, administrative capability, and battle-tested fortitude.",
        "shadows": "Authoritarian temper, isolation at the top, hypersensitivity to disrespect, and stubborn pride.",
        "careers": "Chief executive management, military/police command, corporate turnaround leadership, crisis administration.",
        "prediction": "Rapid ascension into high-responsibility executive offices. Demands humble listening to maintain long-term authority.",
        "remedies": "• Recite Vishnu Sahasranama on Wednesdays.\n• Water a Silk Cotton (Semal) tree.\n• Practice active, patient listening with subordinates."
    },
    19: {
        "core": "Root-seeking truth inquiry, disillusionment with pretense, transformative grit, and revolutionary insight.",
        "strengths": "Fearless examination of root causes, unmatched investigation, philosophical depth, and total self-reinvention.",
        "shadows": "Destructive anger, self-sabotaging cynicism, and emotional volatility when foundations feel shaky.",
        "careers": "Root-cause engineering, medical research, forensic pathology, mining, spiritual philosophy, and strategic intelligence.",
        "prediction": "Radical rebirth after early life trials. Reaches supreme spiritual and mental self-mastery in mid-to-late life.",
        "remedies": "• Chant Om Ketave Namah 17 times after sunset.\n• Water a Sal tree.\n• Donate multi-colored or brown blankets to the underprivileged."
    },
    20: {
        "core": "Invincible optimism, emotional purity, unstoppable perseverance, and magnetic victory drive.",
        "strengths": "Refusal to accept defeat, inspiring charisma, emotional intelligence, and high creative imagination.",
        "shadows": "Over-promising, stubborn refusal to admit errors, and emotional extravagance.",
        "careers": "Maritime industry, creative writing, corporate entertainment, legal advocacy, and large infrastructure projects.",
        "prediction": "Steadily rising career trajectory that achieves celebrated public triumphs and enduring liquid wealth.",
        "remedies": "• Chant Shri Suktam on Friday mornings.\n• Water an Ashoka tree.\n• Donate pure cow ghee to a temple."
    },
    21: {
        "core": "Universal integrity, quiet dignity, adherence to permanent cosmic laws, and institutional trustworthiness.",
        "strengths": "Universal respect, unassailable ethics, steady methodical climbing, and calming executive presence.",
        "shadows": "Excessive seriousness, melancholy under stress, and taking on the burdens of the entire organization.",
        "careers": "High judiciary, public auditing, institutional architecture, regulatory oversight, and research administration.",
        "prediction": "Flawless, permanent reputation. Gains senior statesman-like stature and generational respect.",
        "remedies": "• Recite Aditya Hridaya Stotra on Sundays.\n• Water a Jackfruit (Phanas) tree.\n• Honor elder mentors and uphold truthfulness in speech."
    },
    22: {
        "core": "Scholarly listening acumen, tradition preservation, high learning capacity, and public counsel grace.",
        "strengths": "Exceptional oral communication, deep erudition, encyclopedic memory, and natural advisory gift.",
        "shadows": "Susceptibility to gossip, rigid adherence to verbal forms, and cognitive fatigue from information overload.",
        "careers": "Education, corporate counsel, media broadcasting, audio engineering, linguistics, and strategic consulting.",
        "prediction": "High intellectual distinction. Life brings continuous learning and high advisory stature in civic or corporate spheres.",
        "remedies": "• Chant Om Namo Bhagavate Vasudevaya 108 times daily.\n• Water an Aak (Calotropis) plant.\n• Maintain strict truthfulness in daily conversation."
    },
    23: {
        "core": "Elemental rhythm, musical and martial agility, monumental resource mobilization, and wealth mastery.",
        "strengths": "Superb sense of timing, athletic physical coordination, capacity to mobilize large capital, and victory in competition.",
        "shadows": "Greed for recognition, harsh bluntness, and restlessness when confined to repetitive routines.",
        "careers": "Real estate development, financial trading, mining, percussion music, athletics, and industrial engineering.",
        "prediction": "Monumental capital compounding. Becomes the undisputed pillar of wealth and resource management in family and career.",
        "remedies": "• Recite Hanuman or Kartikeya Stotra on Tuesdays.\n• Water a Shami (Khejri) tree.\n• Feed whole-wheat bread to stray animals."
    },
    24: {
        "core": "Scientific curiosity, investigative veil-piercing intuition, philosophical detachment, and healing mastery.",
        "strengths": "Unconventional intellect, deep research breakthrough ability, medical intuition, and technological foresight.",
        "shadows": "Emotional alienation, cynicism, extreme solitude, and communication aloofness.",
        "careers": "Advanced medical technology, pharmacology, astronomy, esoteric research, telecommunications, and epidemiology.",
        "prediction": "Unlocks hidden scientific or commercial breakthroughs, gaining global recognition for original contributions.",
        "remedies": "• Chant Om Varunaya Namah 11 times facing North.\n• Water a Kadamba tree.\n• Keep a pure solid silver square in your pocket."
    },
    25: {
        "core": "Fiery ascetic determination, visionary reformist drive, immense mental force, and radical independence.",
        "strengths": "Absolute commitment to transformative visions, penetrating eloquence, courage to challenge dogmas, and intense focus.",
        "shadows": "Extreme mood swings, radical intolerance of mediocrity, and physical exhaustion from obsessive exertion.",
        "careers": "Revolutionary technology, high-stakes crisis leadership, metallurgy, criminal law, and social transformation.",
        "prediction": "Early tumultuous phases evolve into commanding visionary authority, leaving an indelible imprint on the field.",
        "remedies": "• Chant the Rudra Gayatri Mantra 11 times at sunrise.\n• Water a Neem or Mango tree.\n• Practice intermittent fasting or clean eating on Thursdays."
    },
    26: {
        "core": "Serpentine wisdom of cosmic depths, calm benevolence, meditative stamina, and unassailable peace.",
        "strengths": "Profound emotional containment, meditative stillness, deep philosophical guidance, and generational foresight.",
        "shadows": "Extreme inertia when unmotivated, social withdrawal, and reluctance to take aggressive physical action.",
        "careers": "Long-term asset custody, marine research, psychotherapy, charitable foundation stewardship, and philosophy.",
        "prediction": "Peaceful, compounding life trajectory. Reaches deep spiritual serenity and establishes permanent generational wealth.",
        "remedies": "• Chant Om Namah Shivaya 108 times facing East.\n• Water a sacred Neem tree.\n• Feed black cows with green grass on Saturdays."
    },
    27: {
        "core": "Nourishing grace, safe guidance of journeys, serene artistic completion, and universal goodwill.",
        "strengths": "Empathy, refined aesthetic and musical talent, traveler's luck, and gentle protective leadership.",
        "shadows": "Over-sensitivity, financial naivety, taking on others' debts, and difficulty setting firm operational boundaries.",
        "careers": "International travel and diplomacy, creative arts, animal welfare, maritime trade, and pediatric medicine.",
        "prediction": "Safe navigation through life's complex currents, concluding in high cultural honor, international respect, and serene fulfillment.",
        "remedies": "• Chant Budha Beej Mantra 19 times on Wednesdays.\n• Water a Mahua tree.\n• Donate educational books or green fruits to underprivileged children."
    }
}

def get_nakshatra_rich_data(star_idx: int):
    return NAKSHATRA_RICH_PROFILES.get(star_idx, NAKSHATRA_RICH_PROFILES[2])

# ALL 12 MOON SIGNS EXPLICITLY DEFINED
RASHI_RICH_PROFILES = {
    0: {
        "element": "Fire (Agni Tattva)",
        "ruler": "Mars (Mangal)",
        "psychology": "Bold, direct, and action-oriented. Mind works like a high-voltage engine that thrives on challenges rather than routine comfort.",
        "instincts": "Fast emotional recovery, instant decision-making reflexes, and zero tolerance for bureaucratic delays. Needs physical outlets to dissipate stress.",
        "relations": "Fiercely protective, passionate, and open. Expects total honesty and can be impatient with passive-aggressive behavior.",
        "health": "Prone to excess metabolic heat (Pitta), headaches, or restless sleep when physical energy is underutilized. Thrives on vigorous daily exercise.",
        "outlook": "Natural pioneer. Bestows courage to build independent ventures and break industry conventions.",
        "remedies": "• Offer water with red sandalwood to the morning Sun.\n• Recite Hanuman Chalisa on Tuesdays.\n• Drink water from a pure silver cup to soothe lunar impulses."
    },
    1: {
        "element": "Earth (Prithvi Tattva)",
        "ruler": "Venus (Shukra)",
        "psychology": "Deliberate, grounded, and emotionally stable. Prioritizes enduring security, comfort, and sensory beauty.",
        "instincts": "Methodical contemplation before committing. Unshakeable perseverance that outlasts temporary storms.",
        "relations": "Deeply loyal, affectionate, and protective. Takes time to trust, but once committed, remains permanent.",
        "health": "Strong constitutional stamina; watch for sluggish metabolism (Kapha) and throat/thyroid care.",
        "outlook": "Master of compound growth, accumulating tangible assets and establishing permanent domestic comfort.",
        "remedies": "• Recite Shri Suktam on Fridays.\n• Apply natural sandalwood attar.\n• Donate white sweets or curd to the needy on Fridays."
    },
    2: {
        "element": "Air (Vayu Tattva)",
        "ruler": "Mercury (Budha)",
        "psychology": "Versatile communicative agility, multi-channel intellect, and insatiable curiosity.",
        "instincts": "Processes emotions through intellectual analysis and dialogue. Highly adaptable in shifting environments.",
        "relations": "Engaging, conversational, and mentally stimulating. Needs intellectual parity in close partnerships.",
        "health": "Sensitive nervous system; susceptible to mental restlessness and shallow breathing. Needs daily meditation.",
        "outlook": "Thrives in media, commerce, information networks, and high-speed multi-disciplinary ventures.",
        "remedies": "• Chant Vishnu Sahasranama on Wednesdays.\n• Water a Tulsi plant daily.\n• Feed green fodder to cows."
    },
    3: {
        "element": "Water (Jala Tattva)",
        "ruler": "Moon (Chandra)",
        "psychology": "Deep emotional empathy, maternal protectiveness, profound subconscious intuition, and rhythmic tenacity.",
        "instincts": "Intuitive antennae sense unspoken atmospheric shifts instantly. Highly protective of loved ones.",
        "relations": "Fiercely nurturing, affectionate, and sentimental. Requires emotional safety and genuine loyalty.",
        "health": "Subject to fluid balance shifts and digestive sensitivity under emotional stress. Hydration is vital.",
        "outlook": "Commands public trust, excels in managing organizations through emotional intelligence and legacy assets.",
        "remedies": "• Offer raw milk on a Shiva Lingam on Mondays.\n• Respect mother figures.\n• Drink water from a silver cup."
    },
    4: {
        "element": "Fire (Agni Tattva)",
        "ruler": "Sun (Surya)",
        "psychology": "Regal dignity, magnanimous generosity, natural executive pride, and commanding emotional presence.",
        "instincts": "Responds with noble authority. Needs admiration and respect; deeply hurt by petty disrespect.",
        "relations": "Devoted, warm-hearted, and protective leader in family and team matters.",
        "health": "High vitality, strong heart rate; must manage blood pressure and avoid over-heating.",
        "outlook": "Attains senior governance, public standing, and institutional authority through charismatic leadership.",
        "remedies": "• Recite Aditya Hridaya Stotra at sunrise.\n• Offer water in a copper vessel to Sun.\n• Honor father figures and mentors."
    },
    5: {
        "element": "Earth (Prithvi Tattva)",
        "ruler": "Mercury (Budha)",
        "psychology": "Analytical precision, structured discernment, service-oriented mindset, and continuous optimization.",
        "instincts": "Emotional calm achieved through practical problem-solving and structured order.",
        "relations": "Thoughtful, dependable, and quietly supportive. Shows love through practical acts of care.",
        "health": "Sensitive digestive tract and gut health. Requires clean nutrition and regular meal hours.",
        "outlook": "Mastery over complex operational systems, corporate auditing, engineering, and quality excellence.",
        "remedies": "• Chant Budha Beej Mantra on Wednesdays.\n• Donate stationery or books to students.\n• Practice 10 minutes of daily mindfulness."
    },
    6: {
        "element": "Air (Vayu Tattva)",
        "ruler": "Venus (Shukra)",
        "psychology": "Diplomatic equilibrium, refined justice, social harmony, and architectural aesthetic balance.",
        "instincts": "Naturally balances competing perspectives. Dislikes crude conflict and seeks elegant arbitration.",
        "relations": "Charming, accommodating, and fair-minded. Thrives in partnership and shared accomplishments.",
        "health": "Kidney and lower back balance; needs pure hydration and avoidance of toxic emotional environments.",
        "outlook": "Success in legal, commercial alliances, luxury commodities, and institutional negotiation.",
        "remedies": "• Worship Goddess Lakshmi on Fridays.\n• Wear clean, pressed pastel attire.\n• Maintain strict fairness in all business contracts."
    },
    7: {
        "element": "Water (Jala Tattva)",
        "ruler": "Mars (Mangal)",
        "psychology": "Penetrating psychological depth, intense emotional stamina, and unyielding transformative grit.",
        "instincts": "Hyper-vigilant radar. Pierces straight through superficial facades; calm in emergencies.",
        "relations": "Intensely loyal and private. Expects absolute devotion and never forgets a breach of trust.",
        "health": "Strong recovery power; guard against chronic stress accumulation and reproductive/colon health.",
        "outlook": "Mastery in strategic turnaround, crisis operations, deep investigations, and private wealth building.",
        "remedies": "• Chant Kartikeya or Shiva Mantras on Tuesdays.\n• Donate jaggery and roasted chickpeas.\n• Guard against holding grudges."
    },
    8: {
        "element": "Fire (Agni Tattva)",
        "ruler": "Jupiter (Guru)",
        "psychology": "Expansive philosophical vision, legal and moral integrity, optimism, and inspiring pedagogical drive.",
        "instincts": "Interprets setbacks as educational milestones. Thrives on exploration, truth, and freedom.",
        "relations": "Generous, honest, and jovial. Values intellectual companionship and mutual independence.",
        "health": "Active metabolism; needs liver support, regular physical workouts, and avoidance of rich foods.",
        "outlook": "High institutional respect, foreign linkages, legal distinction, and enduring reputational prestige.",
        "remedies": "• Chant Guru Mantra on Thursdays.\n• Apply turmeric or yellow sandalwood tilak on forehead.\n• Water a Peepal tree on Thursdays."
    },
    9: {
        "element": "Earth (Prithvi Tattva)",
        "ruler": "Saturn (Shani)",
        "psychology": "Tactical patience, monumental organizational grit, sobriety, and long-range pragmatic climbing.",
        "instincts": "Emotions are contained and controlled. Evaluates decisions through duty, legacy, and long-term durability.",
        "relations": "Extremely dependable, solemn, and protective. Expresses care through providing material foundations.",
        "health": "Joints, knees, and bone health; requires consistent warm hydration and physical movement.",
        "outlook": "Sovereign executive leadership, permanent asset foundations, and lasting mature authority.",
        "remedies": "• Light a mustard-oil lamp under a Peepal tree on Saturdays.\n• Recite Hanuman Chalisa daily.\n• Respect and tip service workers."
    },
    10: {
        "element": "Air (Vayu Tattva)",
        "ruler": "Saturn (Shani)",
        "psychology": "Universal visionary ideals, scientific detachment, systems reformation, and egalitarian ethics.",
        "instincts": "Processes emotions with objective intellectual perspective. Values humanity over individual ego.",
        "relations": "Friendly, loyal, and broad-minded. Respects personal space and avoids possessive clinginess.",
        "health": "Circulatory system and nervous energy; needs restful sleep away from digital screens.",
        "outlook": "Pioneering technological breakthroughs, social systems reform, and original non-linear enterprise.",
        "remedies": "• Chant Shani Gayatri Mantra on Saturdays.\n• Donate black sesame or oil.\n• Keep electronic workspaces free of tangled cables."
    },
    11: {
        "element": "Water (Jala Tattva)",
        "ruler": "Jupiter (Guru)",
        "psychology": "Oceanic subconscious intuition, compassionate wisdom, creative transcendence, and profound emotional depth.",
        "instincts": "Absorbs ambient environmental emotions like a sponge. Exceptional gut instinct that foresees outcomes long before analytical models detect them.",
        "relations": "Deeply devoted, empathetic, and romantic. Needs quiet emotional sanctuary and mutual respect without harsh critical cynicism.",
        "health": "Sensitive lymphatic system and fluid balance (Kapha-Vata balance). Vulnerable to psychosomatic fatigue; requires grounding routines and clean hydration.",
        "outlook": "Unmatched creative imagination and spiritual wisdom. Excels in multi-disciplinary advisory, consulting, and cross-border initiatives.",
        "remedies": "• Chant Om Namo Bhagavate Vasudevaya 108 times on Thursdays.\n• Feed whole wheat dough balls to fish or water birds on Thursdays.\n• Practice 10 minutes of silent meditation at twilight."
    }
}

def get_rashi_rich_data(rashi_idx: int):
    return RASHI_RICH_PROFILES.get(rashi_idx, RASHI_RICH_PROFILES[0])

# ALL 12 LAGNAS (ASCENDANTS) EXPLICITLY DEFINED
LAGNA_RICH_PROFILES = {
    0: {
        "element": "Fire (Agni Tattva)",
        "lord": "Mars (Mangal)",
        "constitution": "High Pitta metabolic intensity, athletic constitution, energetic posture, and physical resilience.",
        "persona": "Direct, confident, bold executive poise, and quick initiative in crisis.",
        "life_arc": "Pioneering entrepreneurship, rapid leadership breakthroughs, and triumph through direct personal courage.",
        "remedies": "• Offer water with red sandalwood to Surya Dev.\n• Recite Hanuman Chalisa daily.\n• Engage in structured physical conditioning."
    },
    1: {
        "element": "Earth (Prithvi Tattva)",
        "lord": "Venus (Shukra)",
        "constitution": "Solid, robust physical stamina, calm facial symmetry, deep voice, and resilient physical health.",
        "persona": "Composed, patient, immovable dignity, and diplomatic aesthetic grace in negotiation.",
        "life_arc": "Compounding permanent tangible wealth, real estate dominion, and enduring executive longevity.",
        "remedies": "• Apply pure white sandalwood paste.\n• Recite Shri Suktam on Fridays.\n• Respect women and keep clean surroundings."
    },
    2: {
        "element": "Air (Vayu Tattva)",
        "lord": "Mercury (Budha)",
        "constitution": "Quick reflexes, expressive carriage, youthful demeanor, and high metabolic speed.",
        "persona": "Articulate, witty, adaptable communicator, and versatile multi-channel strategist.",
        "life_arc": "Commercial triumphs, intellectual distinction, and influence in media, trade, and advisory.",
        "remedies": "• Chant Vishnu Sahasranama on Wednesdays.\n• Water a Tulsi plant daily.\n• Practice measured, clear speech."
    },
    3: {
        "element": "Water (Jala Tattva)",
        "lord": "Moon (Chandra)",
        "constitution": "Gentle, receptive demeanor, sensitive lymphatic and digestive system, and rhythmic stamina.",
        "persona": "Empathetic, nurturing executive presence with sharp intuitive radar.",
        "life_arc": "Command over public institutions, communal trust, and compounding generational assets.",
        "remedies": "• Offer clean water to a Shiva Lingam on Mondays.\n• Respect maternal elders.\n• Drink water from a pure silver cup."
    },
    4: {
        "element": "Fire (Agni Tattva)",
        "lord": "Sun (Surya)",
        "constitution": "Broad chest, regal posture, radiant vitality, strong heart, and commanding demeanor.",
        "persona": "Natural sovereignty, magnanimous leadership, and uncompromising executive dignity.",
        "life_arc": "Administrative authority, prominent public standing, and honors in high governance.",
        "remedies": "• Perform Surya Namaskar at sunrise.\n• Offer water in a copper vessel to Sun.\n• Cultivate magnanimity in leadership."
    },
    5: {
        "element": "Earth (Prithvi Tattva)",
        "lord": "Mercury (Budha)",
        "constitution": "Clean, structured carriage, precise fine-motor dexterity, and sensitive digestive constitution.",
        "persona": "Analytical precision, clean structured communication, and meticulously prepared poise.",
        "life_arc": "Mastery over complex systems, organizational architecture, and financial auditing.",
        "remedies": "• Chant Budha Beej Mantra on Wednesdays.\n• Maintain a clean workspace.\n• Practice evening pranayama."
    },
    6: {
        "element": "Air (Vayu Tattva)",
        "lord": "Venus (Shukra)",
        "constitution": "Balanced Vata-Kapha constitution. Refined aesthetic posture, balanced symmetry, and magnetic social poise.",
        "persona": "Diplomatic composure, natural arbiter of justice, graceful in high-stakes negotiations, and calm under public pressure.",
        "life_arc": "Ascendant lord Shukra guides the life toward institutional balance, legal and commercial distinction, high societal networks, and luxury asset compounding.",
        "remedies": "• Apply pure white sandalwood paste or natural attar on wrists before important meetings.\n• Worship Goddess Lakshmi or recite Shri Suktam on Fridays.\n• Maintain clean, clutter-free surroundings and pristine personal elegance."
    },
    7: {
        "element": "Water (Jala Tattva)",
        "lord": "Mars (Mangal)",
        "constitution": "High Pitta-Kapha metabolic intensity. Powerful stamina, penetrating gaze, and immense physical and mental recovery power.",
        "persona": "Mysterious reserve, authoritative quiet resolve, intense self-command, and zero fear in navigating high-stakes crises.",
        "life_arc": "Life moves through profound evolutionary transformations. Early challenges forge an impenetrable executive fortress, granting control over complex resources in mature years.",
        "remedies": "• Recite the Hanuman Chalisa or Kartikeya Stotra on Tuesdays.\n• Maintain strict ethical transparency in all agreements.\n• Practice grounding breathwork (Nadi Shodhana) to channel internal fire."
    },
    8: {
        "element": "Fire (Agni Tattva)",
        "lord": "Jupiter (Guru)",
        "constitution": "Tall visionary posture, benevolent athletic build, strong liver, and dignified presence.",
        "persona": "Inspiring optimism, scholarly presence, moral integrity, and natural mentorship grace.",
        "life_arc": "Senior institutional leadership, global travel, judicial authority, and profound societal respect.",
        "remedies": "• Apply yellow sandalwood tilak on forehead.\n• Chant Guru Mantra on Thursdays.\n• Support educational causes."
    },
    9: {
        "element": "Earth (Prithvi Tattva)",
        "lord": "Saturn (Shani)",
        "constitution": "Austere constitution, steady bone and joint stamina, dignified mature presence.",
        "persona": "Sober pragmatic presence, disciplined reserve, unshakeable reliability, and executive gravity.",
        "life_arc": "Permanent institutional foundations, administrative sovereignty, and compound authority.",
        "remedies": "• Light a mustard-oil lamp under Peepal on Saturdays.\n• Treat blue-collar workers with respect.\n• Maintain patient long-term planning."
    },
    10: {
        "element": "Air (Vayu Tattva)",
        "lord": "Saturn (Shani)",
        "constitution": "Cerebral poise, progressive demeanor, nervous system sensitivity, and open physical posture.",
        "persona": "Egalitarian visionary, scientific detachment, reformist courage, and intellectual independence.",
        "life_arc": "Pioneering technological breakthroughs, social systems reform, and original enterprise.",
        "remedies": "• Chant Shani Gayatri Mantra on Saturdays.\n• Keep workspace uncluttered.\n• Donate to humanitarian causes."
    },
    11: {
        "element": "Water (Jala Tattva)",
        "lord": "Jupiter (Guru)",
        "constitution": "Gentle compassionate gaze, intuitive artistic sensibility, fluid balance, and calm demeanor.",
        "persona": "Philosophical calm, profound empathy, reflective listening, and transcendent perspective.",
        "life_arc": "Spiritual tranquility, cross-border achievements, creative distinction, and mature peace.",
        "remedies": "• Chant Om Namo Bhagavate Vasudevaya on Thursdays.\n• Practice 15 minutes of quiet meditation.\n• Feed fish with whole wheat dough."
    }
}

def get_lagna_rich_data(lagna_idx: int):
    return LAGNA_RICH_PROFILES.get(lagna_idx, LAGNA_RICH_PROFILES[6])

# ==============================================================================
# EXHAUSTIVE SHANI PAYA ENCYCLOPEDIA (DOMAINS: HEALTH, WEALTH, FAMILY, LOAN, PARTNER, LUCK, CAREER)
# ==============================================================================
SHANI_PAYA_ENCYCLOPEDIA = {
    "Silver": {
        "title": "🥈 Rajat Paya (Silver Feet / चाँदी का पाया)",
        "grade": "Supreme Auspiciousness (अति शुभ फलदायी)",
        "tone": "Divine Cushion, Financial Liquidity & Reputational Growth",
        "houses": "2nd, 5th, or 9th house from natal Moon",
        "health": "Robust physical vitality, restful sleep patterns, strong immunity, and quick recuperation from minor illnesses.",
        "wealth": "Exceptional capital expansion, stabilization of liquid cash flow, recovery of long-pending debts, and lucrative property compounding.",
        "family": "Harmonious domestic environment, supportive spouse, celebration of auspicious family events, and peace with children.",
        "loan": "Seamless debt clearance, easy approvals for restructuring loans at lower interest rates, and immunity against heavy liabilities.",
        "partner": "Highly cooperative business partners and devoted life partner; commercial agreements flow smoothly with mutual trust.",
        "luck": "Favorable wind in long-term ventures, unexpected windfall gains, and strong alignment of mentors and destiny.",
        "career": "Steady executive advancement, elevation in institutional rank, favorable rapport with senior leadership, and public recognition.",
        "protocol": "Wear a solid pure silver square or ring on the little finger, offer raw cow's milk mixed with water on a Shiva Lingam on Mondays."
    },
    "Copper": {
        "title": "🥉 Tamra Paya (Copper Feet / तांबे का पाया)",
        "grade": "Favorable & Productive (शुभ फलदायी)",
        "tone": "Laborious Progress, Competitive Mastery & Sustained Effort",
        "houses": "3rd, 7th, or 10th house from natal Moon",
        "health": "Good stamina driven by focused effort; watch out for elevated metabolic heat (Pitta) and muscular tension from overwork.",
        "wealth": "Wealth grows steadily through direct exertion, disciplined commercial ventures, and enterprise expansion rather than lottery windfalls.",
        "family": "Supportive domestic sphere where hard work is appreciated; requires conscious time-allocation to prevent work-life imbalance.",
        "loan": "Loans are successfully utilized for productive asset creation (e.g., machinery or real estate) with reliable repayment streams.",
        "partner": "Business partnerships thrive through shared ambition and grit; spouse acts as a strong operational sounding board.",
        "luck": "Luck favors the diligent. Persistence through competitive hurdles unlocks major triumphs.",
        "career": "Dominance over competitors, successful project turnarounds, expansion of client networks, and triumph in challenging negotiations.",
        "protocol": "Drink water stored overnight in a pure copper vessel, donate jaggery and roasted chickpeas on Tuesdays, maintain strict truthfulness."
    },
    "Gold": {
        "title": "🥇 Swarna Paya (Gold Feet / सोने का पाया)",
        "grade": "Testing & Demanding (कठिन एवं संघर्षमय)",
        "tone": "Ego Restructuring, Expense Spikes & Need for Extreme Prudence",
        "houses": "1st, 6th, or 11th house from natal Moon",
        "health": "Nervous exhaustion, occasional sleep disruption, and sensitivity to stress; requires strict adherence to restorative sleep and breathwork.",
        "wealth": "Unforeseen expenses, family commitments consuming cash reserves, and slow returns on speculative ventures. Demands strict budgetary austerity.",
        "family": "Ego clashes or communication friction with relatives; requires active listening and emotional humility to maintain peace.",
        "loan": "Avoid taking new unsecured loans or lending money to peers. Refinance existing liabilities with caution.",
        "partner": "Partnerships undergo stress due to ego friction or misaligned expectations. Keep all agreements transparent and documented.",
        "luck": "Luck requires careful navigation; avoid unhedged shortcuts or speculative gambling.",
        "career": "Ego disputes with seniors or partners, misunderstandings regarding credit, and heightened professional scrutiny.",
        "protocol": "Avoid excessive yellow gold jewelry; wear clean silver; donate yellow lentils or turmeric to temple priests on Thursdays; cultivate humility."
    },
    "Iron": {
        "title": "🪙 Loha Paya (Iron Feet / लोहे का पाया)",
        "grade": "Heavy Crucible & High Friction (अति कठिन / संघर्षमय)",
        "tone": "Karmic Weight, Heavy Responsibilities & Constitutional Testing",
        "houses": "4th, 8th, or 12th house from natal Moon",
        "health": "Prone to joint stiffness, lower back vulnerability, and sluggish digestion. Demands regular walking, clean diet, and early bedtime.",
        "wealth": "Sudden financial leaks, legal or administrative hurdles, and stalled asset liquidity. Strictly avoid leveraged bets or lending money.",
        "family": "Heavy family responsibilities testing your patience; domestic harmony requires conscious emotional restraint and quiet tolerance.",
        "loan": "High risk of debt entanglement if living beyond means. Strict moratorium on new liabilities is mandatory.",
        "partner": "Business and personal partners may face external pressures; maintain clear boundaries and avoid joint financial risks.",
        "luck": "Testing phase where destiny rewards patient endurance rather than aggressive gambles.",
        "career": "Strenuous workloads, organizational restructuring, delays in promotions, and demanding subordinate management.",
        "protocol": "Light a mustard-oil lamp under a sacred Peepal tree every Saturday evening; feed black dogs or crows; donate iron items or black sesame."
    }
}

# ==============================================================================
# EXHAUSTIVE SADE SATI & DHAIYA MATRIX (DOMAINS: HEALTH, WEALTH, FAMILY, LOAN, PARTNER, LUCK, CAREER)
# ==============================================================================
SADE_SATI_PHASE_ENCYCLOPEDIA = {
    1: {
        "phase_name": "Phase 1: Rising Phase (Aarohi Charana / 12th House Transit)",
        "focus": "Subconscious Cleansing, Isolation, Expense Spikes & Detachment",
        "health": "Sleep fragmentation, eye strain, joint fatigue in feet/ankles, and vulnerability to psychosomatic stress.",
        "wealth": "High unbudgeted expenditures, investments in foreign affairs or healthcare, and necessity to plug financial leaks. Not favorable for speculative risks.",
        "family": "Temporary physical separation from family due to travel or relocation; emotional introspection may cause temporary distance.",
        "loan": "Potential outflow for settling past obligations or medical/travel expenses. Avoid taking fresh unhedged credit.",
        "partner": "Partners may be absorbed in their own challenges; maintain transparent dialogue to prevent miscommunication.",
        "luck": "External luck is muted in favor of inner spiritual and psychological preparation.",
        "career": "Relocation, foreign assignments, working behind the scenes, or navigating corporate restructuring. Recognition may feel delayed despite intense efforts.",
        "remedy": "Recite Maha Mrityunjaya Mantra 108 times at twilight; donate dark blankets to homeless individuals; avoid major financial commitments during late night hours."
    },
    2: {
        "phase_name": "Phase 2: Peak Janma Shani (Core Transit / 1st House Over Natal Moon)",
        "focus": "Identity Rebirth, Character Crucible, Physical Endurance & Leadership",
        "health": "Demands strict physical discipline, spinal and joint care, adequate hydration, and emotional containment to prevent burnout.",
        "wealth": "Cash flow requires meticulous cash-reserve management. Assets are restructured into solid, unshakeable foundations rather than liquid luxuries.",
        "family": "Testing phase for domestic harmony; patience and ego surrender prevent domestic friction from escalating.",
        "loan": "Strictly avoid speculative loans or signing surety for others. Manage existing debt conservatively.",
        "partner": "Intense testing ground for marital and business partnerships. Mutual commitment is forged through shared adversity.",
        "luck": "Destiny places heavy responsibilities on your shoulders; rewards come strictly through unyielding integrity.",
        "career": "Massive increase in executive responsibilities. You become the reliable pillar managing crises, yet must endure high scrutiny and professional solitude.",
        "remedy": "Chant Shani Beej Mantra 108 times on Saturdays; offer water with blue flowers to Lord Shiva; treat factory workers and subordinates with deep respect."
    },
    3: {
        "phase_name": "Phase 3: Setting Phase (Avarohi Charana / 2nd House Transit)",
        "focus": "Asset Consolidation, Speech Discipline, Family Healing & Permanent Rewards",
        "health": "Teeth, throat, vocal cord, and dietary adjustments. Restoring nutritional balance and cellular vitality.",
        "wealth": "Recovery of financial momentum, accumulation of permanent tangible wealth, stabilization of family estates, and steady cash-flow turnaround.",
        "family": "Reconciliation, celebration of family milestones, and peaceful domestic bonding.",
        "loan": "Debts are steadily paid off, leaving you with clean balance sheets and strengthened creditworthiness.",
        "partner": "Business and life partners bring renewed stability, shared financial planning, and mutual growth.",
        "luck": "Cosmic headwinds turn into favorable tailwinds as past efforts begin to bear tangible fruit.",
        "career": "Consolidation of executive authority, reaping the enduring benefits of hard labor endured during Phase 1 & 2, and achieving long-term respect.",
        "remedy": "Practice strict honesty and avoid harsh speech; drink water from a silver cup; donate whole black urad dal and mustard oil on Saturdays."
    }
}

DHAIYA_ENCYCLOPEDIA = {
    4: {
        "name": "Kantaka Shani (4th House Dhaiya / Ardhashtama Shani)",
        "focus": "Domestic Equilibrium, Property Challenges & Work-Life Balance",
        "health": "Chest, respiratory, and heart-rate balance under domestic or work pressure.",
        "wealth": "Focus on property maintenance expenses and consolidating real estate holdings.",
        "family": "Emotional friction at home, restlessness regarding living arrangements, and attention needed toward maternal health.",
        "loan": "Manage property-related mortgages or home loans with prudent budgeting.",
        "partner": "Domestic stress can spill into partnership dynamics; practice conscious patience.",
        "luck": "Shifts focus from external expansion to securing foundational base and home front.",
        "career": "Strenuous workplace politics, change of department or relocation, and balancing heavy domestic needs with professional demands.",
        "remedy": "Serve and respect your mother; light a mustard-oil lamp under a Peepal tree on Saturdays; keep living space clean and clutter-free."
    },
    8: {
        "name": "Ashtama Shani (8th House Dhaiya / High Friction)",
        "focus": "Deep Transformation, Crisis Mitigation, Health Vigilance & Karmic Debts",
        "health": "Avoid fatigue, check chronic symptoms, and maintain daily walking discipline.",
        "wealth": "Avoid unhedged market leverage, speculative schemes, and unsecured loans.",
        "family": "Elevated vulnerability to stress; keep family communications transparent and calm.",
        "loan": "High caution required against sudden financial commitments or guarantor obligations.",
        "partner": "Unforeseen partner issues require calm mediation and legal/financial prudence.",
        "luck": "Testing cycle requiring spiritual introspection and risk minimization.",
        "career": "Unexpected obstacles in career progression, legal or tax audits, and necessity for absolute transparency in business contracts.",
        "remedy": "Recite Hanuman Chalisa twice daily; avoid risky driving late at night; strictly abstain from speculative financial gambling."
    }
}

def calculate_shani_paya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    house_diff = (moon_rashi_idx - saturn_transit_rashi_idx) % 12 + 1
    m_name = RASHIS[moon_rashi_idx].split()[0]
    
    if house_diff in [2, 5, 9]:
        metal = "Silver"
    elif house_diff in [3, 7, 10]:
        metal = "Copper"
    elif house_diff in [1, 6, 11]:
        metal = "Gold"
    else:
        metal = "Iron"

    ency = SHANI_PAYA_ENCYCLOPEDIA[metal]
    
    return {
        "paya": ency["title"],
        "metal": metal,
        "status": ency["grade"],
        "tone": ency["tone"],
        "houses": ency["houses"],
        "psychology": ency["psychology"],
        "health": ency["health"],
        "wealth": ency["wealth"],
        "family": ency["family"],
        "loan": ency["loan"],
        "partner": ency["partner"],
        "luck": ency["luck"],
        "career": ency["career"],
        "protocol": ency["protocol"],
        "desc": f"Saturn is currently transiting the {house_diff}th house relative to your {m_name} Moon, arriving on {metal} Feet ({ency['title'].split('(')[1].split('/')[0].strip()}).",
        "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces / Meena Rashi)"
    }

def calculate_shani_sadesati_dhaiya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    diff = (saturn_transit_rashi_idx - moon_rashi_idx) % 12
    m_name = RASHIS[moon_rashi_idx].split()[0]

    rashi_12th = RASHIS[(moon_rashi_idx - 1) % 12].split()[0]
    rashi_1st = m_name
    rashi_2nd = RASHIS[(moon_rashi_idx + 1) % 12].split()[0]

    if diff == 11:
        p_info = SADE_SATI_PHASE_ENCYCLOPEDIA[1]
        return {
            "active": True,
            "status_title": p_info["phase_name"],
            "phase_num": 1,
            "focus": p_info["focus"],
            "health": p_info["health"],
            "wealth": p_info["wealth"],
            "family": p_info["family"],
            "loan": p_info["loan"],
            "partner": p_info["partner"],
            "luck": p_info["luck"],
            "career": p_info["career"],
            "mental": p_info["mental"],
            "remedy": p_info["remedy"],
            "impact": f"Saturn currently transits your 12th house in {RASHIS[saturn_transit_rashi_idx].split()[0]} relative to your {m_name} Moon. Prompts deep restructuring of personal priorities, elimination of wasteful financial habits, and subconscious purification.",
            "dates": "Active Phase (29 March 2025 – 23 February 2028)",
            "phase_1_active": True, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 0:
        p_info = SADE_SATI_PHASE_ENCYCLOPEDIA[2]
        return {
            "active": True,
            "status_title": p_info["phase_name"],
            "phase_num": 2,
            "focus": p_info["focus"],
            "health": p_info["health"],
            "wealth": p_info["wealth"],
            "family": p_info["family"],
            "loan": p_info["loan"],
            "partner": p_info["partner"],
            "luck": p_info["luck"],
            "career": p_info["career"],
            "mental": p_info["mental"],
            "remedy": p_info["remedy"],
            "impact": f"Saturn transits directly over your natal Moon in {m_name} (Janma Shani). This is the supreme crucible of character, requiring physical stamina, ego dissolution, leadership responsibility, and unwavering moral grounding.",
            "dates": "Active Peak Phase (29 March 2025 – 23 February 2028)",
            "phase_1_active": False, "phase_2_active": True, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 1:
        p_info = SADE_SATI_PHASE_ENCYCLOPEDIA[3]
        return {
            "active": True,
            "status_title": p_info["phase_name"],
            "phase_num": 3,
            "focus": p_info["focus"],
            "health": p_info["health"],
            "wealth": p_info["wealth"],
            "family": p_info["family"],
            "loan": p_info["loan"],
            "partner": p_info["partner"],
            "luck": p_info["luck"],
            "career": p_info["career"],
            "mental": p_info["mental"],
            "remedy": p_info["remedy"],
            "impact": f"Saturn transits the 2nd house from your {m_name} Moon in {RASHIS[saturn_transit_rashi_idx].split()[0]}. As Sade Sati draws toward conclusion, hard lessons solidify into permanent wealth consolidation, stabilized speech, and generational assets.",
            "dates": "Active Concluding Phase (29 March 2025 – 23 February 2028)",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": True,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 3:
        dh_info = DHAIYA_ENCYCLOPEDIA[4]
        return {
            "active": True,
            "status_title": dh_info["name"],
            "phase_num": 4,
            "focus": dh_info["focus"],
            "health": dh_info["health"],
            "wealth": "Focus on property maintenance and real estate asset consolidation.",
            "family": dh_info["family"],
            "loan": "Manage property-related mortgages or home loans with prudent budgeting.",
            "partner": dh_info["partner"],
            "luck": "Shifts focus from external expansion to securing foundational base and home front.",
            "career": dh_info["career"],
            "mental": dh_info["mental"],
            "remedy": dh_info["remedy"],
            "impact": f"Saturn transits your 4th house from {m_name} Moon in {RASHIS[saturn_transit_rashi_idx].split()[0]}. Focus on home stability, vehicle care, maternal health, and inner peace.",
            "dates": "Active 2.5-Year Dhaiya (2025 – 2028)",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 7:
        dh_info = DHAIYA_ENCYCLOPEDIA[8]
        return {
            "active": True,
            "status_title": dh_info["name"],
            "phase_num": 8,
            "focus": dh_info["focus"],
            "health": dh_info["health"],
            "wealth": "Avoid unhedged market leverage, speculative schemes, and unsecured loans.",
            "family": dh_info["family"],
            "loan": "High caution required against sudden financial commitments or guarantor obligations.",
            "partner": dh_info["partner"],
            "luck": "Testing cycle requiring spiritual introspection and risk minimization.",
            "career": dh_info["career"],
            "mental": dh_info["mental"],
            "remedy": dh_info["remedy"],
            "impact": f"Saturn transits your 8th house from {m_name} Moon in {RASHIS[saturn_transit_rashi_idx].split()[0]}. Demands disciplined health habits, careful driving, transparent financial ethics, and spiritual introspection.",
            "dates": "Active 2.5-Year Dhaiya (2025 – 2028)",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    else:
        return {
            "active": False,
            "status_title": "No Active Sade Sati or Dhaiya",
            "phase_num": 0,
            "focus": "Unimpeded Progress & Expansion",
            "health": "Standard biological stamina.",
            "wealth": "Standard financial liquidity based on active Dasha periods.",
            "family": "Harmonious domestic relations.",
            "loan": "Normal credit management.",
            "partner": "Stable partnership dynamics.",
            "luck": "Favorable planetary support.",
            "career": "Constructive career growth with minimal Saturnic friction.",
            "mental": "Mental clarity is high; favorable for launching new enterprises.",
            "remedy": "Continue daily prayers and ethical business practices.",
            "impact": f"Saturn is currently in Pisces ({RASHIS[saturn_transit_rashi_idx].split()[0]}), placing it in an auspicious or neutral {((saturn_transit_rashi_idx - moon_rashi_idx) % 12) + 1}th house relative to your {m_name} Moon.",
            "dates": "No Current Friction Cycle",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }

def calculate_shani_vahan(birth_star_idx: int, transit_moon_star_idx: int) -> dict:
    raw_val = (birth_star_idx * 4 + transit_moon_star_idx) % 9
    rem = 9 if raw_val == 0 else raw_val
    return SHANI_VAHANS.get(rem, SHANI_VAHANS[9])

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
# CLIENT-SIDE BROWSER MEMORY (URL QUERY PARAMS + SESSION STATE)
# ==============================================================================
client_params = st.query_params

if "user_profile" not in st.session_state:
    if client_params.get("name") and client_params.get("dob") and client_params.get("tob"):
        st.session_state.user_profile = {
            "name": client_params.get("name", ""),
            "dob": client_params.get("dob", ""),
            "tob": client_params.get("tob", ""),
            "city": client_params.get("city", ""),
            "lat": float(client_params.get("lat", 28.6139)),
            "lon": float(client_params.get("lon", 77.2090)),
            "lang": client_params.get("lang", "en")
        }
    else:
        st.session_state.user_profile = {
            "name": "",
            "dob": "",
            "tob": "",
            "city": "",
            "lat": 28.6139,
            "lon": 77.2090,
            "lang": "en"
        }

if "current_page" not in st.session_state:
    st.session_state.current_page = "about"

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "selected_transit_idx" not in st.session_state:
    st.session_state.selected_transit_idx = 0

if "japa_count" not in st.session_state:
    st.session_state.japa_count = 0

if "mala_rounds" not in st.session_state:
    st.session_state.mala_rounds = 0

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

# Top Navigation Dock (4 + 3 Grid)
nav_r1_c1, nav_r1_c2, nav_r1_c3, nav_r1_c4 = st.columns(4)
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

with nav_r1_c4:
    p_type = "primary" if st.session_state.current_page == "shani" else "secondary"
    if st.button(t("btn_shani", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "shani"
        st.rerun()

nav_r2_c1, nav_r2_c2, nav_r2_c3 = st.columns(3)
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
    p_type = "primary" if st.session_state.current_page == "mantra" else "secondary"
    if st.button(t("btn_mantra", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "mantra"
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
    u_lat, u_lon = 28.6139, 77.2090

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
# POST-SUBMISSION ONBOARDING SCREEN: ADD TO HOME SCREEN
# ==============================================================================
def render_page_install_guide():
    render_html("""
    <div class="auth-hero-box" style="text-align:center; border:2px solid #f59e0b; background:#fffbeb;">
        <div style="font-size:2.6rem; margin-bottom:8px;">📱</div>
        <div style="font-weight:900; font-size:1.45rem; color:#92400e; margin-bottom:6px;">
            Save to Home Screen on Your Device
        </div>
        <div style="font-size:0.98rem; color:#78350f; line-height:1.6; margin-bottom:12px;">
            Your astrological profile & coordinates are now securely loaded in your device's browser bar. 
            <b>Add Navtara Pulse to your Home Screen now</b> so your profile opens automatically every day without typing anything again!
        </div>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.18rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:1.5px solid #fed7aa; padding-bottom:0.3rem;">
            🤖 For Android (Google Chrome)
        </div>
        <ol style="margin-top:5px; margin-bottom:6px; padding-left:1.3rem; font-size:0.95rem; color:#431407; line-height:1.75;">
            <li>Tap the <b>three vertical dots menu (⋮)</b> in the top-right corner of Chrome.</li>
            <li>Select <b>"Install app"</b> or <b>"Add to Home screen"</b>.</li>
            <li>Tap <b>"Install"</b>. The app icon is saved to your phone with your profile intact!</li>
        </ol>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.18rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:1.5px solid #fed7aa; padding-bottom:0.3rem;">
            🍏 For iPhone / iOS (Safari Browser)
        </div>
        <ol style="margin-top:5px; margin-bottom:6px; padding-left:1.3rem; font-size:0.95rem; color:#431407; line-height:1.75;">
            <li>Tap the <b>Share icon</b> (square with an upward arrow) at the bottom of Safari.</li>
            <li>Scroll down and tap <b>"Add to Home Screen"</b>.</li>
            <li>Tap <b>"Add"</b> in the top right. Launch directly anytime as a native full-screen app!</li>
        </ol>
    </div>
    """)

    st.write("")
    c_btn1, c_btn2 = st.columns([1, 1])
    with c_btn1:
        if st.button("⚡ Proceed to Today's Prediction", type="primary", use_container_width=True):
            st.session_state.current_page = "live"
            st.rerun()
    with c_btn2:
        if st.button("👤 View Astrological Profile", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()

# ==============================================================================
# TAB 1: ABOUT APP
# ==============================================================================
def render_page_about():
    with st.container(border=True):
        st.markdown("**🌐 Select Language / भाषा चुनें:**")
        lang_col1, _ = st.columns([2, 1])
        with lang_col1:
            lang_options = {"en": "English", "hi": "हिन्दी (Hindi)"}
            selected_lang_code = st.selectbox(
                "App Language",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
                index=list(lang_options.keys()).index(current_lang if current_lang in lang_options else "en"),
                label_visibility="collapsed"
            )
            if selected_lang_code != current_lang:
                st.session_state.user_profile["lang"] = selected_lang_code
                st.query_params["lang"] = selected_lang_code
                st.rerun()

    render_html("""
    <div class="auth-hero-box">
        <div style="font-weight:900; font-size:1.35rem; color:#92400e; margin-bottom:0.75rem; border-bottom:1.5px solid #fde68a; padding-bottom:0.4rem;">
            🧬 Navtara Pulse: Precision Chronobiology & Vedic Timing Engine
        </div>
        <div style="font-size:0.98rem; line-height:1.8; color:#451a03; margin-bottom:0.8rem;">
            <b>Navtara Pulse</b> bridges ancient Sidereal Jyotish with modern chronobiology. It is an algorithmic decision-support compass designed to answer one crucial question: <b>"Is today mathematically aligned for aggressive action, or does it demand strategic defense?"</b><br>
            By mapping the Moon's real-time transit through the 27 lunar mansions (Nakshatras) against your natal birth frequency, the app calculates your personalized 9-fold bio-rhythm, pinpointing exact windows of peak influence, effortless execution, and friction avoidance.
        </div>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            🔬 The Scientific Logic: Gravitational Hydrodynamics & Bio-Rhythms
        </div>
        
        <div style="font-size:0.96rem; line-height:1.75; color:#334155; margin-bottom:1rem;">
            <b>1. Lunar Tidal Hydrodynamics & Neuro-Endocrine Flow:</b><br>
            The adult human brain and body are composed of approximately <b>70% water and electrolytic fluids</b>. Chronobiology confirms that lunar periodicity modulates circadian gene expression, sleep architecture (REM cycles), cerebrospinal fluid pressure, and neuro-transmitter output. In classical Vedic science, the Moon governs the mind (<i>"Chandro Manaso Jatah"</i>). When the celestial Moon aligns harmoniously with your natal Moon's electro-magnetic horizon, neural processing operates at peak cognitive clarity.
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#334155; margin-bottom:1rem;">
            <b>2. The 9-Fold Mathematical Resonance Grid (27 = 9 × 3):</b><br>
            The zodiac is divided into 27 Nakshatras of 13° 20' each. The Vedic <b>Navtara Chakra</b> is an infradian mathematical model that groups these 27 stars into 3 repeating cycles of 9 qualitative energetic frequencies (Taras). Every single day, the Moon activates one of these 9 energetic chambers for your unique neural wiring:
            <ul style="margin-top:6px; padding-left:1.3rem;">
                <li><b>Expansion Windows (Sampat, Sadhana, Mitra, Ati-Mitra):</b> Characterized by high environmental receptivity and synaptic coherence. Ideal for high-stakes business negotiations, signing contracts, strategic investing, and key launches.</li>
                <li><b>Friction Shields (Vipat, Pratyari, Vadha):</b> Characterized by elevated resistance, biochemical fatigue, and communication misfires. On these days, defensive prudence and patient review prevent costly missteps.</li>
                <li><b>Foundational & Consolidation Days (Janma, Kshema):</b> Optimal for internal diagnostics, physical recuperation, and team alignment.</li>
            </ul>
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#334155;">
            <b>3. Sub-Arcsecond Planetary Ephemeris (Swiss Ephemeris):</b><br>
            Unlike conventional astrology apps that rely on generic sun signs or flat 24-hour sunrise assumptions, <b>Navtara Pulse</b> incorporates the <b>Moshier Swiss Ephemeris</b> (pyswisseph) with true topocentric Chitrapaksha Lahiri Ayanamsa. Ingress and egress timestamps are calculated down to the exact second for your geographical horizon.
        </div>
    </div>

    <div class="light-card-num">
        <div style="font-weight:900; font-size:1.25rem; color:#065f46; margin-bottom:0.75rem; border-bottom:2px solid #bbf7d0; padding-bottom:0.4rem;">
            🎯 How Navtara Pulse Empowers You in Daily Life
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:0.5rem;">
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1px solid #bbf7d0; border-left:5px solid #059669;">
                <b style="color:#065f46; font-size:1rem;">💼 Strategic Career & Business Execution:</b><br>
                <span style="font-size:0.93rem; color:#1e293b; line-height:1.6;">
                    Never schedule critical client pitches, salary reviews, or investor meetings blind. Aligning major professional leaps with your <b>Sadhana (Accomplishment)</b> or <b>Ati-Mitra (Supreme Alliance)</b> days drastically increases closing velocity and reduces friction.
                </span>
            </div>
            
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1px solid #bbf7d0; border-left:5px solid #10b981;">
                <b style="color:#065f46; font-size:1rem;">💰 Financial Preservation & Capital Timing:</b><br>
                <span style="font-size:0.93rem; color:#1e293b; line-height:1.6;">
                    Shield yourself from impulsive capital deployment. Executing asset purchases during <b>Sampat (Wealth)</b> days supports long-term appreciation, while strictly holding back on <b>Vipat (Friction)</b> and <b>Vadha (Loss)</b> days prevents unforced financial errors.
                </span>
            </div>

            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1px solid #bbf7d0; border-left:5px solid #14b8a6;">
                <b style="color:#065f46; font-size:1rem;">❤️ Emotional Composure & Relationship Harmony:</b><br>
                <span style="font-size:0.93rem; color:#1e293b; line-height:1.6;">
                    Knowing when you or your partner are traversing high-sensitivity transit days allows you to practice proactive patience, avoid unnecessary arguments, and cultivate deeper empathy.
                </span>
            </div>

            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1px solid #bbf7d0; border-left:5px solid #0d9488;">
                <b style="color:#065f46; font-size:1rem;">🌿 Bio-Energy Shielding & Burnout Prevention:</b><br>
                <span style="font-size:0.93rem; color:#1e293b; line-height:1.6;">
                    Pace your vital energy. Schedule intensive athletic workouts on high-vitality days and prioritize meditation, restorative sleep, and grounding breathwork when biological resistance peaks.
                </span>
            </div>
        </div>
    </div>
    """)

    app_url = "https://navtara-pulse.streamlit.app"
    share_msg = "Track your real-time Vedic Moon transit rhythm, Shani Paya, and personalized timing blueprint with Navtara Pulse!"
    encoded_url = urllib.parse.quote(app_url)
    encoded_msg = urllib.parse.quote(f"{share_msg}\n\nCheck your cosmic alignment here: {app_url}")

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            {t('share_title', current_lang)}
        </div>
        <div style="font-size:0.95rem; color:#475569; margin-bottom:0.85rem;">
            Share this authentic Vedic chronobiology tool with your family, friends, and colleagues:
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
            <div style="font-size:0.88rem; color:#9a3412; font-weight:800;">Direct Web App Link:</div>
            <div style="font-size:1.05rem; font-weight:900; color:#431407; margin-top:2px;"><b>{app_url}</b></div>
        </div>
    </div>
    """)

# ==============================================================================
# TAB 2: USER PROFILE
# ==============================================================================
def render_page_profile():
    global u_lat, u_lon
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

            new_city_query = st.text_input(t("city_label", current_lang), value=prof.get("city", ""), placeholder="e.g. Delhi, Mumbai, Pune, London, New York")

            c_save, c_canc = st.columns([2, 1])
            with c_save:
                submitted = st.form_submit_button("✨ Save & Calculate Profile", type="primary", use_container_width=True)
            with c_canc:
                canceled = st.form_submit_button("Cancel", use_container_width=True)

            if submitted:
                if not new_name.strip():
                    st.error("Please provide your full name.")
                elif not new_city_query.strip():
                    st.error("Please provide a birth location name.")
                else:
                    hr_24 = in_hour % 12
                    if in_ampm == "PM":
                        hr_24 += 12
                    final_tob_str = f"{hr_24:02d}:{in_minute:02d}"

                    resolved_lat, resolved_lon = resolve_location_name(new_city_query)

                    st.session_state.user_profile.update({
                        "name": new_name.strip(),
                        "dob": new_dob.strftime("%Y-%m-%d"),
                        "tob": final_tob_str,
                        "city": new_city_query.strip(),
                        "lat": resolved_lat,
                        "lon": resolved_lon
                    })
                    
                    st.query_params["name"] = new_name.strip()
                    st.query_params["dob"] = new_dob.strftime("%Y-%m-%d")
                    st.query_params["tob"] = final_tob_str
                    st.query_params["city"] = new_city_query.strip()
                    st.query_params["lat"] = f"{resolved_lat:.4f}"
                    st.query_params["lon"] = f"{resolved_lon:.4f}"

                    st.session_state.edit_mode = False
                    st.session_state.current_page = "install_guide"
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

    bio_nak = NAKSHATRA_BIO_DATA.get(chart_info["star_idx"], NAKSHATRA_BIO_DATA[2])
    n_data = get_nakshatra_rich_data(chart_info["star_idx"])
    m_data = get_rashi_rich_data(chart_info["moon_rashi_idx"])
    l_data = get_lagna_rich_data(chart_info["lagna_idx"])
    
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
            <div style="font-weight:900; font-size:1.15rem; color:#9a3412; margin-bottom:8px;">
                ⭐ Janma Nakshatra: {chart_info['star_name']} (Pada {chart_info['pada']})
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:8px; margin-bottom:12px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🏛️ Deity:</b> {bio_nak['deity']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🔱 Symbol:</b> {bio_nak['symbol']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🌳 Sacred Tree:</b> {bio_nak['tree']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🦅 Sacred Bird:</b> {bio_nak['bird']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🦁 Yoni Animal:</b> {bio_nak['animal']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🪐 Planetary Lord:</b> {bio_nak['lord']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #fed7aa; margin-bottom:8px;">
                <b style="color:#9a3412; font-size:0.96rem;">🧠 Core Cognitive & Behavioral Archetype:</b>
                <div style="font-size:0.92rem; line-height:1.65; color:#431407; margin-top:2px;">{n_data['core']}</div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:8px;">
                <div style="background:#f0fdf4; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                    <b style="color:#15803d; font-size:0.92rem;">✨ Superpowers & Natural Assets:</b>
                    <div style="font-size:0.89rem; line-height:1.55; color:#14532d; margin-top:2px;">{n_data['strengths']}</div>
                </div>
                <div style="background:#fff1f2; border-radius:10px; padding:10px; border:1px solid #fecdd3;">
                    <b style="color:#be123c; font-size:0.92rem;">⚠️ Karmic Shadows & Blind Spots:</b>
                    <div style="font-size:0.89rem; line-height:1.55; color:#881337; margin-top:2px;">{n_data['shadows']}</div>
                </div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #fed7aa; margin-bottom:8px; font-size:0.91rem; color:#431407;">
                <b>💼 Peak Vocational & Executive Fields:</b><br>{n_data['careers']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #fed7aa; margin-bottom:8px; font-size:0.91rem; color:#431407;">
                <b>🔮 Evolutionary Life Path Trajectory:</b><br>{n_data['prediction']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #f97316; font-size:0.91rem; color:#431407;">
                <b>🪔 Prescribed Vedic Nakshatra Remedies:</b><br>{n_data['remedies']}
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:14px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#065f46; margin-bottom:8px;">
                🌙 Moon Sign (Chandra Rashi): {chart_info['moon_rashi_name']}
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:10px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>🔥 Element:</b> {m_data['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>🪐 Rashi Sovereign:</b> {m_data['ruler']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>🧠 Emotional Mindset & Subconscious Processing:</b><br>{m_data['psychology']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>⚡ Stress Reflexes & Primal Coping Instincts:</b><br>{m_data['instincts']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>❤️ Interpersonal Blueprint & Relationship Style:</b><br>{m_data['relations']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>🌿 Bio-Rhythms & Physiological Vitality:</b><br>{m_data['health']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #10b981; font-size:0.91rem; color:#14532d;">
                <b>🪔 Prescribed Lunar Remedies:</b><br>{m_data['remedies']}
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:8px;">
                🌅 Ascendant (Lagna): {chart_info['lagna_name']} at {chart_info['lagna_deg']}
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:10px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>🌍 Lagna Tattva:</b> {l_data['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>👑 Ascendant Lord:</b> {l_data['lord']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>🛡️ Physical Constitution, Vitality & Posture (Prakriti):</b><br>{l_data['constitution']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>👔 Outward Persona & Negotiating Presence:</b><br>{l_data['persona']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>🚀 Evolutionary Life Arc & Asset Compounding:</b><br>{l_data['life_arc']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #8b5cf6; font-size:0.91rem; color:#3b0764;">
                <b>🪔 Prescribed Ascendant Remedies:</b><br>{l_data['remedies']}
            </div>
        </div>
    </div>
    """)

    # Tara Bala Widget
    with st.container(border=True):
        st.markdown("**🤝 Nakshatra Synergy & Compatibility Evaluator (Tara Bala)**")
        partner_star_choice = st.selectbox("Select Counterpart's Birth Star:", options=NAKSHATRAS, index=0)
        p_star_idx = NAKSHATRAS.index(partner_star_choice) + 1
        tara_res = get_tara_bala_info(chart_info['star_idx'], p_star_idx)
        
        box_bg = '#f0fdf4' if tara_res['is_allied'] else ('#fff1f2' if tara_res['is_friction'] else '#f8fafc')
        box_border = '#86efac' if tara_res['is_allied'] else ('#fecdd3' if tara_res['is_friction'] else '#e2e8f0')
        box_color = '#15803d' if tara_res['is_allied'] else ('#be123c' if tara_res['is_friction'] else '#0f172a')
        
        render_html(f"""
        <div style="background:{box_bg}; border:1.5px solid {box_border}; border-radius:12px; padding:12px; margin-top:8px;">
            <div style="font-size:1.05rem; font-weight:800; color:{box_color};">
                {tara_res['icon']} {tara_res['tara_name']} — {tara_res['quality']}
            </div>
            <div style="font-size:0.92rem; font-weight:700; color:#334155; margin-top:4px;">
                Dynamic: {tara_res['relationship_tone']}
            </div>
            <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.5;">
                {tara_res['advice']}
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
                • <b>Metal Vessel Grounding:</b> Drink water from a pure silver or copper vessel to pacify nervous restlessness and enhance bio-electrical harmony.<br>
                • <b>Digital & Workspace Bio-Shield:</b> Remove tangled charging cables, broken electronic gadgets, and inactive clocks from your workspace.<br>
                • <b>Name Resonance (Namank):</b> Use green or blue ink when writing or endorsing important planning documents to harmonize your {namank} name vibration.
            </div>
        </div>
    </div>
    """)

# ==============================================================================
# TAB 4: SHANI & SADE SATI (EXHAUSTIVE LIFE-DOMAIN BREAKDOWN)
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
        <div style="font-weight:900; font-size:1.35rem; color:#5b21b6; margin-bottom:1rem; border-bottom:2px solid #ddd6fe; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>🪐 Shani Paya & Sade Sati Exhaustive Life-Domain Matrix</span>
            <span style="font-size:0.85rem; background:#ede9fe; color:#5b21b6; padding:4px 10px; border-radius:20px; font-weight:800;">Saturn in Pisces (Meena)</span>
        </div>
        
        <!-- SHANI PAYA IN-DEPTH MATRIX -->
        <div style="background:#f5f3ff; border-radius:14px; padding:16px; border:1.5px solid #e9d5ff; margin-bottom:1.25rem;">
            <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">ACTIVE TRANSIT PAYA FOR YOUR {m_name.upper()} MOON</div>
            <div style="font-size:1.45rem; font-weight:900; color:#5b21b6; margin:4px 0;">{shani_paya_data['paya']}</div>
            <div style="font-size:0.98rem; color:#7c3aed; font-weight:800;">Grade: {shani_paya_data['status']} | Dynamic: {shani_paya_data['tone']}</div>
            <div style="font-size:0.92rem; color:#475569; margin-top:3px;"><b>Active Timeline:</b> {shani_paya_data['timeline']}</div>
            
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1px solid #ddd6fe; margin-top:12px; font-size:0.93rem; color:#3b0764; line-height:1.7;">
                <b>🏛️ Classical Foundation:</b> {shani_paya_data['desc']}<br>
                <b>🧭 Operating Houses:</b> Saturn activates the {shani_paya_data['houses']} house axis relative to your natal Moon.
            </div>

            <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-top:12px;">
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #f97316; font-size:0.91rem; color:#7c2d12; line-height:1.6;">
                    <b>🌿 1. Health & Vitality Impact:</b><br>{shani_paya_data['health']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #10b981; font-size:0.91rem; color:#14532d; line-height:1.6;">
                    <b>💰 2. Wealth & Cash Flow Dynamics:</b><br>{shani_paya_data['wealth']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #8b5cf6; font-size:0.91rem; color:#3b0764; line-height:1.6;">
                    <b>👨‍👩‍👧‍👦 3. Family & Domestic Harmony:</b><br>{shani_paya_data['family']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #e11d48; font-size:0.91rem; color:#881337; line-height:1.6;">
                    <b>📉 4. Loans & Liabilities Management:</b><br>{shani_paya_data['loan']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #065f46; font-size:0.91rem; color:#065f46; line-height:1.6;">
                    <b>🤝 5. Partnerships & Business Alliances:</b><br>{shani_paya_data['partner']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #d97706; font-size:0.91rem; color:#78350f; line-height:1.6;">
                    <b>🍀 6. Luck & Destiny Alignment:</b><br>{shani_paya_data['luck']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #0284c7; font-size:0.91rem; color:#0369a1; line-height:1.6;">
                    <b>💼 7. Career, Authority & Executive Standing:</b><br>{shani_paya_data['career']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #475569; font-size:0.91rem; color:#0f172a; line-height:1.6;">
                    <b>🪔 8. Targeted Elemental Countermeasures:</b><br>{shani_paya_data['protocol']}
                </div>
            </div>
        </div>

        <!-- SADE SATI / DHAIYA EXHAUSTIVE MATRIX -->
        <div style="background:#ffffff; border-radius:14px; padding:16px; border:1.5px solid #ddd6fe; margin-bottom:1.25rem;">
            <div style="font-weight:900; font-size:1.2rem; color:#5b21b6; margin-bottom:10px; border-bottom:1px solid #e9d5ff; padding-bottom:5px; display:flex; justify-content:space-between; align-items:center;">
                <span>⚖️ Active Sade Sati / Dhaiya Life-Domain Breakdown for {m_name} Moon</span>
                <span style="font-size:0.82rem; background:#ede9fe; color:#5b21b6; padding:3px 8px; border-radius:10px; font-weight:800;">{shani_sadesati_data['status_title'].split(':')[0]}</span>
            </div>
            
            <div style="background:{'#fef2f2' if shani_sadesati_data['phase_2_active'] else '#f5f3ff'}; border-radius:12px; padding:14px; border-left:5px solid {'#ef4444' if shani_sadesati_data['phase_2_active'] else '#9333ea'}; margin-bottom:14px;">
                <b style="color:{'#991b1b' if shani_sadesati_data['phase_2_active'] else '#5b21b6'}; font-size:1.1rem;">{shani_sadesati_data['status_title']}</b>
                <div style="font-size:0.92rem; color:#64748b; margin:3px 0 8px 0;"><b>Active Window:</b> {shani_sadesati_data['dates']} | <b>Core Focus:</b> {shani_sadesati_data['focus']}</div>
                <div style="font-size:0.95rem; line-height:1.7; color:#334155;">{shani_sadesati_data['impact']}</div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:14px;">
                <div style="background:#fff7ed; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#7c2d12; border-left:4px solid #f97316;">
                    <b>🌿 1. Health & Vitality Impact:</b><br>{shani_sadesati_data['health']}
                </div>
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#14532d; border-left:4px solid #10b981;">
                    <b>💰 2. Wealth & Cash Flow Dynamics:</b><br>{shani_sadesati_data['wealth']}
                </div>
                <div style="background:#faf5ff; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#3b0764; border-left:4px solid #8b5cf6;">
                    <b>👨‍👩‍👧‍👦 3. Family & Domestic Harmony:</b><br>{shani_sadesati_data['family']}
                </div>
                <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#881337; border-left:4px solid #e11d48;">
                    <b>📉 4. Loans & Liabilities Management:</b><br>{shani_sadesati_data['loan']}
                </div>
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#065f46; border-left:4px solid #065f46;">
                    <b>🤝 5. Partnerships & Business Alliances:</b><br>{shani_sadesati_data['partner']}
                </div>
                <div style="background:#fffbeb; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#78350f; border-left:4px solid #d97706;">
                    <b>🍀 6. Luck & Destiny Alignment:</b><br>{shani_sadesati_data['luck']}
                </div>
                <div style="background:#f0f9ff; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#0369a1; border-left:4px solid #0284c7;">
                    <b>💼 7. Career, Authority & Executive Standing:</b><br>{shani_sadesati_data['career']}
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#0f172a; border-left:4px solid #475569;">
                    <b>🪔 8. Prescribed Remedial Protocol:</b><br>{shani_sadesati_data['remedy']}
                </div>
            </div>

            <div style="font-weight:900; font-size:1.05rem; color:#475569; margin:16px 0 8px 0; border-top:1px solid #e9d5ff; padding-top:10px;">
                Complete 7.5-Year Sade Sati Evolutionary Blueprint for {m_name} Moon:
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #a855f7; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#5b21b6; font-size:0.96rem;">Phase 1: Rising Phase (Saturn in {shani_sadesati_data['rashi_12th']} / 12th from Moon)</b>
                    {p1_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>Core Dynamic:</b> Subconscious restructuring, elimination of toxic habits, and mental detachment.<br>
                    • <b>Financial & Career:</b> Spikes in expenses related to travel, relocation, or healthcare; work happens behind the scenes.<br>
                    • <b>Karmic Mastery:</b> Shedding psychological baggage and preparing for the core transit.
                </div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #ef4444; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#991b1b; font-size:0.96rem;">Phase 2: Peak Janma Shani (Saturn in {shani_sadesati_data['rashi_1st']} / Over Natal Moon)</b>
                    {p2_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>Core Dynamic:</b> Crucible of character and endurance. Dissolves false pride and tests emotional truth.<br>
                    • <b>Financial & Career:</b> Maximum administrative burden, heavy decision-making stress, and executive solitude.<br>
                    • <b>Karmic Mastery:</b> Cultivating emotional resilience, physical discipline, and enduring maturity.
                </div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #10b981; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#065f46; font-size:0.96rem;">Phase 3: Setting Phase (Saturn in {shani_sadesati_data['rashi_2nd']} / 2nd from Moon)</b>
                    {p3_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>Core Dynamic:</b> Lifting of psychological pressure, consolidation of hard-won wisdom, and stabilizing family harmony.<br>
                    • <b>Financial & Career:</b> Wealth recovery, acquisition of durable assets, disciplined speech, and delayed recognition.<br>
                    • <b>Karmic Mastery:</b> Transforming lessons into lasting institutional stability and financial security.
                </div>
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe;">
            <div style="font-weight:900; font-size:1.05rem; color:#5b21b6; margin-bottom:6px;">🪔 Prescribed Remedies for Planetary Neutralization:</div>
            <div style="font-size:0.93rem; line-height:1.7; color:#3b0764;">
                • <b>Mantra Japa:</b> Recite the <b>Shani Beej Mantra</b> (ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः) 108 times at twilight on Saturdays facing West.<br>
                • <b>Vitality Shield:</b> Recite the <b>Hanuman Chalisa</b> daily to boost pranic fire, disperse lethargy, and protect mental peace.<br>
                • <b>Charity & Service:</b> Donate mustard oil, black sesame seeds, or dark blankets to laborers, sweepers, or elderly persons on Saturdays.<br>
                • <b>Behavioral Grounding:</b> Practice absolute punctuality, avoid harsh speech, and avoid shortcuts in contractual agreements.
            </div>
        </div>
    </div>
    """)

    st.write("")
    if st.button("📿 Open Dedicated Digital Japa Counter", type="primary", use_container_width=True):
        st.session_state.current_page = "mantra"
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

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <b>⏱️ Timing Windows for Today ({prof['city']}):</b><br>
            • 🌟 <b>Abhijit Muhurta:</b> {abhijit_s.strftime('%I:%M %p')} – {abhijit_e.strftime('%I:%M %p IST')} (Golden Window)<br>
            • ⚠️ <b>Rahu Kaal:</b> {rahu_s.strftime('%I:%M %p')} – {rahu_e.strftime('%I:%M %p IST')} (Avoid Signings)
        </div>

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
# TAB 7: DEDICATED MANTRA SADHANA & DIGITAL JAPA MALA COUNTER
# ==============================================================================
def render_page_mantra():
    render_html("""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.3rem; color:#5b21b6; margin-bottom:0.4rem;">
            📿 Japa Sadhana & Vedic Mantra Sanctuary
        </div>
        <div style="font-size:0.93rem; color:#475569; line-height:1.6;">
            Select a personalized planetary, star, or transit mantra to view its authentic Sanskrit verse, 
            meaning, and chant with the 108-bead interactive digital Mala counter.
        </div>
    </div>
    """)

    mantra_catalog = {
        "Maha Mrityunjaya Mantra (Supreme Protection)": {
            "sanskrit": "ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्।\nउर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय मामृतात्॥",
            "translit": "Om Tryambakam Yajamahe Sugandhim Pushti-Vardhanam |\nUrvarukamiva Bandhanan-Mrityor-Mukshiya Maamritat ||",
            "meaning": "We meditate on the Three-Eyed Lord Shiva, who permeates and nourishes all beings. May He liberate us from the bonds of fear and death into immortality.",
            "rules": "• Best chanted at dawn or dusk facing East or North.\n• Use a Rudraksha Mala.\n• Pacifies severe transit friction (Vipat, Vadha) and shields cellular vitality."
        },
        "Shani Beej Mantra (Saturn Pacification)": {
            "sanskrit": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः॥",
            "translit": "Om Praam Preem Proum Sah Shanaishcharaya Namah ||",
            "meaning": "Salutations to Lord Saturn, the dispenser of karmic justice. Pacifies delays, chronic exhaustion, and aligns personal discipline during Sade Sati / Dhaiya.",
            "rules": "• Best chanted at twilight facing West on Saturdays.\n• Use a dark Rudraksha or black tourmaline mala.\n• Sit on an indigo or wool asana."
        },
        "Gayatri Mantra (Solar Illumination)": {
            "sanskrit": "ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात्॥",
            "translit": "Om Bhur Bhuvah Swah Tat Savitur Varenyam Bhargo Devasya Dheemahi Dhiyo Yo Nah Prachodayat ||",
            "meaning": "We meditate upon the supreme divine brilliance of the Sun who illuminates the inner cosmos. May that divine light awaken and inspire our intellect.",
            "rules": "• Best chanted during Brahma Muhurta or at sunrise facing East.\n• Use a Tulsi or Sandalwood Mala.\n• Enhances mental clarity, vitality, and cellular healing."
        },
        "Vishnu Sahasranama Shloka (Aura Shield)": {
            "sanskrit": "ॐ नमो भगवते वासुदेवाय॥",
            "translit": "Om Namo Bhagavate Vasudevaya ||",
            "meaning": "Salutations to the Supreme Preserver of the Cosmos who dwells within all living hearts.",
            "rules": "• Chant in the morning facing East.\n• Harmonizes favorable transits (Sampat, Sadhana, Ati-Mitra).\n• Brings peace to the home and liquid capital stability."
        }
    }

    if has_valid_profile:
        bio_nak = NAKSHATRA_BIO_DATA.get(chart_info["star_idx"], NAKSHATRA_BIO_DATA[2])
        deity_name = bio_nak["deity"].split()[0]
        nak_key = f"Janma Nakshatra Mantra ({chart_info['star_name']})"
        mantra_catalog[nak_key] = {
            "sanskrit": f"ॐ {deity_name} नमः॥",
            "translit": f"Om {deity_name} Namah ||",
            "meaning": f"Directly harmonizes the natal electromagnetic bio-frequency of your birth star governed by {bio_nak['deity']}.",
            "rules": f"• Chant 11, 27, or 108 times daily in the morning.\n• Protects and waters the sacred Nakshatra tree ({bio_nak['tree']}).\n• Enhances natural intuition and executive luck."
        }

    selected_mantra = st.selectbox("Select Mantra to Chant:", options=list(mantra_catalog.keys()))
    m_info = mantra_catalog[selected_mantra]

    render_html(f"""
    <div style="background:#ffffff; border:1.5px solid #ddd6fe; border-radius:14px; padding:16px; margin:14px 0; box-shadow:0 3px 12px rgba(139,92,246,0.06);">
        <div style="font-size:1.35rem; font-weight:900; color:#1e1b4b; text-align:center; font-family:serif; line-height:1.6; white-space:pre-line;">
            {m_info['sanskrit']}
        </div>
        <div style="font-size:0.93rem; color:#6d28d9; text-align:center; font-style:italic; margin-top:8px; line-height:1.5; white-space:pre-line;">
            {m_info['translit']}
        </div>
        <hr style="margin:12px 0; border:none; border-top:1px solid #ede9fe;">
        <div style="font-size:0.92rem; color:#334155; line-height:1.65;">
            <b>📜 Meaning:</b> {m_info['meaning']}<br><br>
            <b>🧘 Sadhana Guidelines:</b><br>{m_info['rules'].replace(chr(10), '<br>')}
        </div>
    </div>
    """)

    # Interactive 108-Bead Mala Counter
    with st.container(border=True):
        st.markdown(f"### 📿 Digital Mala: **{st.session_state.japa_count} / 108** Beads")
        progress_val = min(1.0, st.session_state.japa_count / 108.0)
        st.progress(progress_val, text=f"Mala Progress: {int(progress_val * 100)}% | Completed Malas: {st.session_state.mala_rounds}")

        col_tap, col_reset = st.columns([2, 1])
        with col_tap:
            if st.button("📿 Tap Bead (+1)", type="primary", use_container_width=True):
                st.session_state.japa_count += 1
                if st.session_state.japa_count >= 108:
                    st.session_state.japa_count = 0
                    st.session_state.mala_rounds += 1
                    st.balloons()
                    st.success("🎉 Om Shanti! You have completed 1 full Mala (108 Chants). May the vibration bring peace and protection!")
                st.rerun()
        with col_reset:
            if st.button("🔄 Reset Counter", use_container_width=True):
                st.session_state.japa_count = 0
                st.session_state.mala_rounds = 0
                st.rerun()

# ==============================================================================
# ROUTER DISPATCHER: RENDER THE SELECTED PAGE
# ==============================================================================
PAGES = {
    "about": render_page_about,
    "profile": render_page_profile,
    "numerology": render_page_numerology,
    "shani": render_page_shani,
    "live": render_page_live,
    "forecast": render_page_forecast,
    "mantra": render_page_mantra,
    "install_guide": render_page_install_guide,
}

active_page_func = PAGES.get(st.session_state.current_page, render_page_about)
active_page_func()
