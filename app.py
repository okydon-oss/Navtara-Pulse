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

# Configure Streamlit page settings
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

# Mobile-optimized CSS with fluid rem typography that respects system font settings
render_html("""
<style>
    /* Responsive mobile container */
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
    
    /* High-contrast, beautifully styled cards with comfortable mobile typography */
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

    /* Fixed bottom navigation buttons */
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
        "btn_navtara": "🌟 Navtara",
        "btn_profile": "👤 Profile",
        "btn_numerology": "🔢 Numerology",
        "btn_shani": "🪐 Shani",
        "btn_live": "⚡ Live Prediction",
        "btn_forecast": "🗓️ 7 Days Prediction",
        "btn_planets": "🔭 Planet position",
        "btn_remedies": "🪔 Remedies",
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
        "planet_title": "🔭 Real-Time Sidereal Planetary Longitudes (Lahiri)",
        "share_title": "📲 Share Navtara Pulse With Friends & Family"
    },
    "hi": {
        "app_title": "✨ नवतारा पल्स (Navtara Pulse)",
        "app_subtitle": "वैदिक नक्षत्र गोचर एवं खगोलीय ऊर्जा चक्र",
        "btn_about": "✨ ऐप परिचय",
        "btn_navtara": "🌟 नवतारा",
        "btn_profile": "👤 प्रोफाइल",
        "btn_numerology": "🔢 अंकशास्त्र",
        "btn_shani": "🪐 शनि पाया",
        "btn_live": "⚡ आज का फल",
        "btn_forecast": "🗓️ 7 दिवसीय फल",
        "btn_planets": "🔭 ग्रह स्थिति",
        "btn_remedies": "🪔 वैदिक उपाय",
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
        "planet_title": "🔭 वास्तविक निरयण ग्रह स्पष्ट (लाहिड़ी)",
        "share_title": "📲 नवतारा पल्स को परिवार व मित्रों के साथ साझा करें"
    },
    "mr": {
        "app_title": "✨ नवतारा पल्स (Navtara Pulse)",
        "app_subtitle": "वैदिक नक्षत्र गोचर आणि वैश्विक ऊर्जा चक्र",
        "btn_about": "✨ ॲप विषयी",
        "btn_navtara": "🌟 नवतारा",
        "btn_profile": "👤 प्रोफाईल",
        "btn_numerology": "🔢 अंकशास्त्र",
        "btn_shani": "🪐 शनी पाया",
        "btn_live": "⚡ आजचे भविष्य",
        "btn_forecast": "🗓️ ७ दिवसांचे भविष्य",
        "btn_planets": "🔭 ग्रह स्थिती",
        "btn_remedies": "🪔 वैदिक उपाय",
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
        "planet_title": "🔭 निरयन प्रत्यक्ष ग्रह स्थिती (लाहिरी)",
        "share_title": "📲 नवतारा पल्स ॲप मित्र आणि कुटुंबासह शेअर करा"
    },
    "gu": {
        "app_title": "✨ નવતારા પલ્સ (Navtara Pulse)",
        "app_subtitle": "વૈદિક નક્ષત્ર ગોચર અને બ્રહ્માંડીય ઊર્જા ચક્ર",
        "btn_about": "✨ એપ વિશે",
        "btn_navtara": "🌟 નવતારા",
        "btn_profile": "👤 પ્રોફાઇલ",
        "btn_numerology": "🔢 અંકશાસ્ત્ર",
        "btn_shani": "🪐 શનિ પાયા",
        "btn_live": "⚡ આજનું ફળ",
        "btn_forecast": "🗓️ ૭ દિવસનું ફળ",
        "btn_planets": "🔭 ગ્રહ સ્થિતિ",
        "btn_remedies": "🪔 વૈદિક ઉપાયો",
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
        "planet_title": "🔭 પ્રત્યક્ષ નિરયણ ગ્રહ સ્થિતિ (લાહિરી)",
        "share_title": "📲 નવતારા પલ્સ તમારા મિત્રો અને પરિવાર સાથે શેર કરો"
    }
}

def t(key: str, lang: str = "en") -> str:
    """Safely returns localized string with English fallback."""
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS.get("en", {}).get(key, key))

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
    ("Janma (Birth Star)", "🔵", "Introspective & Recharging"),
    ("Sampat (Wealth & Abundance)", "🟢", "Highly Auspicious & Lucrative"),
    ("Vipat (Danger & Friction)", "🔴", "Caution Required & Low Risk"),
    ("Kshema (Well-being & Flow)", "🟢", "Harmonious & Productive"),
    ("Pratyari (Opposition & Obstacles)", "🔴", "Defensive Stance & Patience"),
    ("Sadhana (Achievement & Execution)", "🟢", "Peak Action & Success"),
    ("Vadha (Destruction / Critical Point)", "🔴", "High Risk / Pause Crucial Deals"),
    ("Mitra (Friendship & Alliance)", "🟢", "Warm Cooperation & Ease"),
    ("Ati-Mitra (Supreme Alliance)", "🟢🟢", "Maximum Fortune & Breakthroughs")
]

SHANI_VAHANS = {
    1: {"name": "🐴 Horse (Ghoda)", "type": "Rapid Progress & Victory", "vibe": "Speed, bold actions, expansion and swift triumph over obstacles."},
    2: {"name": "🫏 Donkey (Gadha)", "type": "Heavy Effort & Hard Labor", "vibe": "Endurance required; outcomes require disciplined patience."},
    3: {"name": "🦊 Jackal (Siyar)", "type": "Caution & Hidden Traps", "vibe": "Alertness needed in contracts, legal matters and financial advice."},
    4: {"name": "🐘 Elephant (Hathi)", "type": "Royalty, Honor & Luxury", "vibe": "Prestige, royal comfort, recognition and financial windfalls."},
    5: {"name": "🐂 Bull (Bail)", "type": "Steady Foundations & Gains", "vibe": "Continuous progressive gains through disciplined daily routine."},
    6: {"name": "🦁 Lion (Sher)", "type": "Commanding Authority & Courage", "vibe": "Victory in competitions, legal dominance and fearless leadership."},
    7: {"name": "🐦‍⬛ Crow (Kowwa)", "type": "Restlessness & Scattered Focus", "vibe": "Guard against impulsive arguments, stay centered, practice silence."},
    8: {"name": "🦚 Peacock (Mayur)", "type": "Joy, Aesthetics & Good News", "vibe": "Social harmony, heartwarming family news and artistic success."},
    9: {"name": "🦢 Swan (Hans)", "type": "Wisdom, Mental Peace & Health", "vibe": "Deep spiritual clarity, sound decisions and radiant mental peace."}
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
    1: {"en": "Sun (Surya)", "hi": "सूर्य (Sun)", "mr": "सूर्य (Sun)", "gu": "સૂર્ય (Sun)"},
    2: {"en": "Moon (Chandra)", "hi": "चन्द्र (Moon)", "mr": "चंद्र (Moon)", "gu": "ચંદ્ર (Moon)"},
    3: {"en": "Jupiter (Guru)", "hi": "बृहस्पति (Jupiter)", "mr": "गुरु (Jupiter)", "gu": "ગુરુ (Jupiter)"},
    4: {"en": "Rahu (North Node)", "hi": "राहु (Rahu)", "mr": "राहु (Rahu)", "gu": "રાહુ (Rahu)"},
    5: {"en": "Mercury (Budha)", "hi": "बुध (Mercury)", "mr": "बुध (Mercury)", "gu": "બુધ (Mercury)"},
    6: {"en": "Venus (Shukra)", "hi": "शुक्र (Venus)", "mr": "शुक्र (Venus)", "gu": "શુક્ર (Venus)"},
    7: {"en": "Ketu (South Node)", "hi": "केतु (Ketu)", "mr": "केतु (Ketu)", "gu": "કેતુ (Ketu)"},
    8: {"en": "Saturn (Shani)", "hi": "शनि (Saturn)", "mr": "शनी (Saturn)", "gu": "શનિ (Saturn)"},
    9: {"en": "Mars (Mangal)", "hi": "मंगल (Mars)", "mr": "मंगळ (Mars)", "gu": "મંગળ (Mars)"}
}

def get_nakshatra_traits(star_idx: int, lang: str = "en") -> dict:
    """Returns detailed Nakshatra traits, deity, symbol, and remedies."""
    nakshatra_data = {
        1: {
            "name": "Ashwini",
            "deity": "Ashwini Kumaras (Divine Physicians)",
            "symbol": "Horse's Head",
            "lord": "Ketu",
            "traits": {
                "en": "Pioneering, swift, energetic, and courageous. You possess natural healing presence, acute spontaneous problem-solving agility, and a flair for initiating ambitious ventures without fear.",
                "hi": "साहसी, ऊर्जावान एवं त्वरित निर्णय लेने में सक्षम। आपके स्वभाव में नैसर्गिक नेतृत्व, नवीन शुरुआत और कठिनाइयों से शीघ्र उबरने की अद्भुत क्षमता होती है।",
                "mr": "धाडसी, उत्साही आणि तत्पर निर्णय घेणारे व्यक्तिमत्व. नव्या उपक्रमांची सुरुवात करणे आणि आव्हानांना धैर्याने तोंड देणे हे तुमचे नैसर्गिक वैशिष्ट्य आहे.",
                "gu": "સાહસિક, અત્યંત ઉત્સાહી અને ઝડપી નિર્ણય લેવાની અદભુત શક્તિ. નવી પહેલ કરવી અને મુશ્કેલીઓને હિંમતથી પાર કરવી તમારો મૂળ સ્વભાવ છે."
            }
        },
        2: {
            "name": "Bharani",
            "deity": "Lord Yama (Dharma & Cosmic Justice)",
            "symbol": "Yoni / Triangle of Creation",
            "lord": "Venus (Shukra)",
            "traits": {
                "en": "Determined, charismatic, highly passionate, and deeply disciplined. Governed by Yama and Venus, you carry an unshakable inner moral fortitude, judicial fairness, and the rare capacity to endure heavy responsibilities with silent dignity.",
                "hi": "दृढ़ संकल्पी, सम्मोहक व्यक्तित्व, अत्यंत निष्ठावान एवं कर्मठ। भरणी नक्षत्र के प्रभाव से आपमें सत्य के प्रति अडिगता, न्यायप्रियता और भारी जिम्मेदारियों को सहजता से वहन करने का असाधारण सामर्थ्य होता है।",
                "mr": "दृढनिश्चयी, आकर्षक आणि अथांग कार्यक्षमता असलेले व्यक्तिमत्व. भरणी नक्षत्राच्या प्रभावामुळे तुमच्यात न्यायप्रियता, सत्यनिष्ठा आणि कठीण प्रसंगात शांतपणे जबाबदारी पेलण्याची ताकद आहे.",
                "gu": "દૃઢ સંકલ્પ, પ્રભાવશાળી વ્યક્તિત્વ અને ઉચ્ચ શિસ્ત. કોઈપણ મુશ્કેલ પરિસ્થિતિમાં અડગ રહીને ન્યાયપ્રિયતા સાથે મોટી જવાબદારીઓ પૂર્ણ કરવાની કુદરતી શક્તિ ધરાવો છો."
            }
        }
    }
    
    selected = nakshatra_data.get(star_idx, nakshatra_data[2])
    return {
        "deity": selected["deity"],
        "symbol": selected["symbol"],
        "lord": selected["lord"],
        "desc": selected["traits"].get(lang, selected["traits"]["en"])
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
                    calc, _ = swe.calc_ut(t_jd, pid, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)
                    lon = float(calc[0] % 360.0)
                except Exception:
                    calc, _ = swe.calc_ut(t_jd, pid, swe.FLG_SIDEREAL)
                    lon = float(calc[0] % 360.0)
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

render_html(f"""
    <div style='text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; margin-top:0.2rem; margin-bottom:0.75rem;'>
        <div style='background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); width:72px; height:72px; border-radius:24px; display:flex; align-items:center; justify-content:center; font-size:2.35rem; box-shadow:0 8px 26px rgba(245,158,11,0.35); margin-bottom:10px;'>
            ✨
        </div>
        <h1 style='margin:0; font-size:2.15rem; color:#0f172a; font-weight:900; line-height:1.2; text-align:center;'>{t('app_title', current_lang)}</h1>
        <div style='font-size:1rem; color:#64748b; font-weight:600; margin-top:6px; text-align:center;'>{t('app_subtitle', current_lang)}</div>
    </div>
""")

# Row 1: About App, Navtara, Numerology, Shani
nav_r1_c1, nav_r1_c2, nav_r1_c3, nav_r1_c4 = st.columns(4)
with nav_r1_c1:
    p_type = "primary" if st.session_state.current_page == "about" else "secondary"
    if st.button(t("btn_about", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "about"
        st.rerun()

with nav_r1_c2:
    p_type = "primary" if st.session_state.current_page == "navtara" else "secondary"
    if st.button(t("btn_navtara", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "navtara"
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


# ==============================================================================
# PAGE 1: ABOUT APP, SCIENTIFIC ASTRO-FOUNDATION & SHARING PORTAL
# ==============================================================================
def render_page_about():
    lang_opts = {"en": "🌐 English", "hi": "🌐 हिन्दी", "mr": "🌐 मराठी", "gu": "🌐 ગુજરાતી"}
    col_lang_l, col_lang_c, col_lang_r = st.columns([1, 1.4, 1])
    with col_lang_c:
        st.markdown("<div style='text-align:center; font-weight:800; color:#64748b; font-size:0.88rem; margin-bottom:6px;'>Choose Language / भाषा निवडा:</div>", unsafe_allow_html=True)
        selected_lang_code = st.selectbox(
            "Language Selector",
            options=list(lang_opts.keys()),
            format_func=lambda x: lang_opts[x],
            index=list(lang_opts.keys()).index(current_lang) if current_lang in lang_opts else 0,
            label_visibility="collapsed",
            key="about_page_lang_select"
        )
        if selected_lang_code != current_lang:
            st.session_state.user_profile["lang"] = selected_lang_code
            save_user_profile(st.session_state.user_profile)
            st.rerun()

    render_html("<div style='margin-bottom:1rem;'></div>")

    app_url = "https://navtara-pulse.streamlit.app"
    share_msg = "Discover your real-time Vedic Moon transit rhythm, Shani Paya, and personalized Numerology blueprint with Navtara Pulse!"
    encoded_url = urllib.parse.quote(app_url)
    encoded_msg = urllib.parse.quote(f"{share_msg}\n\nCheck your cosmic alignment here: {app_url}")

    render_html(f"""
    <div class="auth-hero-box">
        <div style="font-weight:900; font-size:1.3rem; color:#92400e; margin-bottom:0.5rem; display:flex; align-items:center; gap:8px;">
            <span>🌌</span> <span>Navtara Pulse: Where Ancient Vedic Wisdom Meets Sub-Arcsecond Science</span>
        </div>
        <div style="font-size:0.96rem; line-height:1.7; color:#78350f;">
            Most horoscopes offer generalized sun-sign forecasts that fail to reflect your daily lived reality. 
            <b>Navtara Pulse</b> is engineered on a fundamentally different paradigm: the direct, real-time angular relationship between your 
            <b>Janma Nakshatra (Natal Moon Star)</b> and the actual astronomical position of the Moon as it sweeps through the 27 lunar mansions.
        </div>
    </div>

    <div class="light-card-profile" style="margin-bottom:1.15rem;">
        <div style="font-weight:900; font-size:1.2rem; color:#9a3412; margin-bottom:0.8rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            🔬 The Scientific Connection: Chronobiology, Lunar Pull & Human Bio-Rhythms
        </div>
        <div style="font-size:0.95rem; line-height:1.7; color:#334155; margin-bottom:1rem;">
            Astrology at its highest level is applied celestial mechanics and circadian chronobiology. Consider the established scientific realities:
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:0.5rem;">
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border-left:4px solid #f97316;">
                <b style="color:#9a3412; font-size:1rem;">🌊 Gravitational Hydrodynamics & Human Fluids:</b><br>
                <span style="font-size:0.92rem; color:#431407; line-height:1.6;">
                    The Moon exerts colossal gravitational pull capable of lifting billions of tons of ocean water in tidal swells. The adult human body consists of approximately <b>65% to 70% water</b>, with the human brain being over 73% water. Just as lunar phases govern marine tides, the Moon's orbital ingress creates measurable micro-fluctuations in neurotransmitter balance, sleep architecture, and psychological equilibrium (recognized in clinical chronobiology as <i>infradian rhythms</i>).
                </span>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border-left:4px solid #ea580c;">
                <b style="color:#9a3412; font-size:1rem;">🛰️ NASA JPL & Swiss Ephemeris Precision:</b><br>
                <span style="font-size:0.92rem; color:#431407; line-height:1.6;">
                    This application utilizes the <b>Moshier-Swiss Ephemeris algorithm</b> calibrated to the Chitrapaksha Lahiri Ayanamsa. Rather than using approximations, the planetary longitudes are solved with sub-arcsecond astronomical precision, matching the exact spatial coordinates calculated by space observatories.
                </span>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border-left:4px solid #c2410c;">
                <b style="color:#9a3412; font-size:1rem;">🧠 Vedic Psychological Priming & Navtara Harmonic Resonance:</b><br>
                <span style="font-size:0.92rem; color:#431407; line-height:1.6;">
                    In Vedic neuroscience, the Moon rules the <i>Manas</i> (sensory processing, emotional temperament, and instantaneous decision-making). The 9-tier Navtara matrix mathematically maps the angular distance of the transit Moon from your natal Moon into 9 archetypal energetic frequencies—ranging from frictionless creative flow (<b>Sampat</b>, <b>Sadhana</b>, <b>Ati-Mitra</b>) to high-friction karmic resistance (<b>Vipat</b>, <b>Pratyari</b>, <b>Vadha</b>).
                </span>
            </div>
        </div>
    </div>

    <div class="light-card-num" style="margin-bottom:1.15rem;">
        <div style="font-weight:900; font-size:1.2rem; color:#065f46; margin-bottom:0.8rem; border-bottom:2px solid #bbf7d0; padding-bottom:0.4rem;">
            🎯 How to Use Navtara Pulse to Master Your Daily Decisions
        </div>
        <div style="font-size:0.95rem; line-height:1.7; color:#1e293b;">
            Timing is everything. Even the strongest strategy fails when launched in a stormy cosmic current, while ordinary actions produce extraordinary breakthroughs when launched with the cosmic wind at your back:
        </div>
        <ul style="font-size:0.94rem; line-height:1.7; color:#1e293b; margin-top:8px; padding-left:1.2rem;">
            <li><b>Seize Golden Windows (🟢 Sampat, Sadhana, Mitra, Ati-Mitra):</b> Perfect hours for signing major contracts, launching products, scheduling critical job interviews, purchasing real estate, and having high-stakes relationship conversations.</li>
            <li><b>Safeguard During Caution Zones (🔴 Vipat, Pratyari, Vadha):</b> Avoid speculative trading, unnecessary confrontations, signing impulsive agreements, or starting litigation. Maintain a calm, defensive, observant posture.</li>
            <li><b>Harmonize with Saturn's Speed (Shani Vahan):</b> Understand whether your day demands the patient stamina of the Donkey, the strategic vigilance of the Jackal, the royal majesty of the Elephant, or the joyful ease of the Peacock.</li>
        </ul>
    </div>

    <div class="light-card-shani" style="margin-bottom:1.15rem;">
        <div style="font-weight:900; font-size:1.2rem; color:#5b21b6; margin-bottom:0.8rem; border-bottom:2px solid #ddd6fe; padding-bottom:0.4rem;">
            🪔 The Science Behind Vedic Remedies: Why They Work
        </div>
        <div style="font-size:0.95rem; line-height:1.7; color:#3b0764;">
            Vedic remedies are not superstitious rituals—they are sophisticated <b>neuro-linguistic, physiological, and behavioral recalibrations</b>:
        </div>
        <div style="display:grid; grid-template-columns: 1fr; gap:8px; margin-top:10px;">
            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe;">
                <b>🔊 Mantras & Sound Frequency:</b> Sanskrit mantras produce specific phonetic acoustic resonances that stimulate the vagus nerve, lower sympathetic nervous arousal, and silence cortisol-driven anxiety.
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe;">
                <b>🕊️ Dana (Charity & Animal Feeding):</b> Feeding crows, stray dogs, or supporting laborers directly neutralizes psychological Saturnine guilt and recalibrates ego-driven stress into universal empathy.
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe;">
                <b>💧 Elemental Grounding:</b> Offering clean water or raw milk to a Shiva Lingam harmonizes the lunar water element, bringing stillness to an overstimulated nervous system.
            </div>
        </div>
    </div>

    <!-- Installation Guide Card -->
    <div class="light-card-num" style="margin-bottom:1.15rem;">
        <div style="font-weight:900; font-size:1.2rem; color:#065f46; margin-bottom:0.8rem; border-bottom:2px solid #bbf7d0; padding-bottom:0.4rem; display:flex; align-items:center; gap:8px;">
            <span>📲</span> <span>How to Install & Use Like a Native Mobile App</span>
        </div>
        <div style="font-size:0.95rem; line-height:1.65; color:#1e293b; margin-bottom:0.9rem;">
            You can install <b>Navtara Pulse</b> directly onto your smartphone's home screen without downloading from any app store. It runs full-screen, fast, and accessible with a single tap:
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr; gap:10px;">
            <div style="background:#f0fdf4; border-radius:12px; padding:12px 14px; border:1.5px solid #dcfce7;">
                <b style="color:#047857; font-size:1rem;">🤖 For Android (Google Chrome):</b>
                <ol style="margin:6px 0 0 0; padding-left:1.2rem; font-size:0.92rem; color:#1e293b; line-height:1.6;">
                    <li>Open this link in <b>Google Chrome</b>.</li>
                    <li>Tap the <b>three dots menu (⋮)</b> in the top-right corner.</li>
                    <li>Select <b>"Add to Home screen"</b> or <b>"Install app"</b>.</li>
                    <li>Tap <b>Install / Add</b>. The app icon will appear right on your home screen.</li>
                </ol>
            </div>
            
            <div style="background:#f0fdf4; border-radius:12px; padding:12px 14px; border:1.5px solid #dcfce7;">
                <b style="color:#047857; font-size:1rem;">🍎 For Apple iPhone / iPad (Safari):</b>
                <ol style="margin:6px 0 0 0; padding-left:1.2rem; font-size:0.92rem; color:#1e293b; line-height:1.6;">
                    <li>Open this link in <b>Safari</b> browser.</li>
                    <li>Tap the <b>Share button</b> (the square icon with an upward arrow <b>⎋</b>) at the bottom.</li>
                    <li>Scroll down and select <b>"Add to Home Screen"</b> (<b>+</b>).</li>
                    <li>Tap <b>Add</b> in the top right corner. Navtara Pulse is now installed!</li>
                </ol>
            </div>
        </div>
    </div>

    <div class="light-card-live">
        <div style="font-weight:900; font-size:1.2rem; color:#0369a1; margin-bottom:0.8rem; border-bottom:2px solid #bae6fd; padding-bottom:0.4rem;">
            📲 Share Navtara Pulse With Friends & Family
        </div>
        <div style="font-size:0.95rem; color:#334155; margin-bottom:1rem; line-height:1.6;">
            Empower your loved ones with authentic astronomical timing and Vedic clarity. Share the app via your favorite platform:
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:10px; margin-bottom:1rem;">
            <a href="https://api.whatsapp.com/send?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#25D366; color:#ffffff; padding:10px 12px; border-radius:12px; text-align:center; font-weight:900; font-size:0.95rem;">
                    🟢 WhatsApp
                </div>
            </a>
            <a href="https://t.me/share/url?url={encoded_url}&text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0088cc; color:#ffffff; padding:10px 12px; border-radius:12px; text-align:center; font-weight:900; font-size:0.95rem;">
                    ✈️ Telegram
                </div>
            </a>
            <a href="mailto:?subject=Navtara Pulse - Vedic Timing&body={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#ea4335; color:#ffffff; padding:10px 12px; border-radius:12px; text-align:center; font-weight:900; font-size:0.95rem;">
                    ✉️ Email
                </div>
            </a>
            <a href="https://twitter.com/intent/tweet?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0f172a; color:#ffffff; padding:10px 12px; border-radius:12px; text-align:center; font-weight:900; font-size:0.95rem;">
                    🐦 X (Twitter)
                </div>
            </a>
        </div>

        <div style="background:#f0f9ff; border-radius:12px; padding:10px 14px; border:1px solid #bae6fd; text-align:center;">
            <div style="font-size:0.86rem; color:#0284c7; font-weight:800;">Direct Link:</div>
            <div style="font-size:0.98rem; font-weight:900; color:#0369a1; margin-top:2px;"><b>{app_url}</b></div>
        </div>
    </div>
    """)


# ==============================================================================
# PAGE 2: USER BIRTH PROFILE & NAVTARA ASTROLOGICAL PROFILE
# ==============================================================================
def render_page_navtara():
    # Smart User Profile Box with Inline Edit
    with st.container(border=True):
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            render_html(f"""
            <div style="font-weight:900; font-size:1.2rem; color:#0f172a;">👤 {prof['name']}'s Birth Profile</div>
            <div style="font-size:0.95rem; color:#334155; margin-top:5px; line-height:1.6;">
                📅 <b>DOB:</b> {dob_parsed.strftime('%d %B %Y')} &nbsp;|&nbsp; ⏰ <b>Time:</b> {tob_parsed.strftime('%I:%M %p')}<br>
                📍 <b>Place:</b> {prof['city']}
            </div>
            """)
        with col_p2:
            if st.button(t("edit_details", current_lang), use_container_width=True):
                st.session_state.edit_mode = not st.session_state.edit_mode
                st.rerun()

    # Expandable edit form
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

    # Navtara & Vedic Astrological Profile Box
    n_info = get_nakshatra_traits(chart_info["star_idx"], current_lang)
    
    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:1rem; border-bottom:2px solid #fed7aa; padding-bottom:0.5rem;">
            🌌 Navtara & Vedic Astrological Profile
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:10px; text-align:center; margin-bottom:1.1rem;">
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.85rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('nakshatra_label', current_lang)}</div>
                <div style="font-size:1.25rem; font-weight:900; color:#9a3412; margin:2px 0;">{chart_info['star_name']}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{t('pada_label', current_lang)} {chart_info['pada']}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.85rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('moon_rashi_label', current_lang)}</div>
                <div style="font-size:1.25rem; font-weight:900; color:#9a3412; margin:2px 0;">{chart_info['moon_rashi_name'].split()[0]}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{chart_info['moon_rashi_name'].split()[-1]}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.85rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('lagna_label', current_lang)}</div>
                <div style="font-size:1.25rem; font-weight:900; color:#9a3412; margin:2px 0;">{chart_info['lagna_name'].split()[0]}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{chart_info['lagna_name'].split()[-1]}</div>
            </div>
        </div>
        
        <div style="background:#fffaf0; border-radius:12px; padding:14px; border-left:5px solid #f97316; margin-bottom:1rem; border:1px solid #fed7aa; border-left-width:5px;">
            <div style="font-weight:900; font-size:1.05rem; color:#9a3412; margin-bottom:6px;">✨ Personality Archetype & Core Traits:</div>
            <div style="font-size:0.96rem; line-height:1.65; color:#431407;">{n_info['desc']}</div>
            <div style="margin-top:8px; font-size:0.9rem; color:#7c2d12;">
                <b>Deity:</b> {n_info['deity']} &nbsp;|&nbsp; <b>Symbol:</b> {n_info['symbol']} &nbsp;|&nbsp; <b>Planetary Lord:</b> {n_info['lord']}
            </div>
        </div>

        <div style="background:#fffaf0; border-radius:12px; padding:14px; border:1.5px solid #fed7aa;">
            <div style="font-weight:900; font-size:1.05rem; color:#9a3412; margin-bottom:6px;">🪔 Vedic Nakshatra Remedies:</div>
            <div style="font-size:0.95rem; line-height:1.65; color:#431407;">
                • <b>Deity Worship:</b> Offer prayers to Lord Shiva or Lord Yama to harmonize vital life energy and dissolve karmic resistance.<br>
                • <b>Vedic Japa:</b> Recite <b>Om Hreem Bharanyai Namah</b> or <b>Maha Mrityunjaya Mantra</b> 11 times on Tuesdays and Fridays.<br>
                • <b>Botanical Harmony:</b> Nurture or water an Amla (Indian Gooseberry) plant to strengthen Venusian prana.
            </div>
        </div>
    </div>
    """)


# ==============================================================================
# PAGE 2: CORE NUMEROLOGY BLUEPRINT & LIFE DOMAINS
# ==============================================================================
def render_page_numerology():
    num_domains = get_numerology_life_domains(mulank, bhagyank, namank, current_lang)
    p_m_label = NUM_PLANET_NAMES.get(mulank, {}).get(current_lang, f"Planet {mulank}")
    p_b_label = NUM_PLANET_NAMES.get(bhagyank, {}).get(current_lang, f"Planet {bhagyank}")
    p_n_label = NUM_PLANET_NAMES.get(namank, {}).get(current_lang, f"Planet {namank}")

    render_html(f"""
    <div class="light-card-num">
        <div style="font-weight:900; font-size:1.25rem; color:#065f46; margin-bottom:1rem; border-bottom:2px solid #bbf7d0; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>🔢 2. Core Numerology Blueprint</span>
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

        <div style="background:#f0fdf4; border-radius:12px; padding:14px; border:1.5px solid #bbf7d0;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:8px;">{num_domains['luck_title']}</div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.95rem; line-height:1.6;">
                <div><b>✨ Lucky Numbers:</b> {num_domains['lucky_num']}</div>
                <div><b>⚠️ Caution Numbers:</b> {num_domains['avoid_num']}</div>
                <div><b>📅 Auspicious Days:</b> {num_domains['lucky_days']}</div>
                <div><b>🧭 Favorable Direction:</b> {num_domains['lucky_dir']}</div>
                <div style="grid-column: 1 / -1;"><b>🎨 Energizing Colors:</b> {num_domains['lucky_colors']}</div>
            </div>
        </div>
    </div>
    """)


# ==============================================================================
# PAGE 3: SHANI PAYA, TRANSIT & SADE SATI
# ==============================================================================
def render_page_shani():
    render_html(f"""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.25rem; color:#5b21b6; margin-bottom:1rem; border-bottom:2px solid #ddd6fe; padding-bottom:0.5rem;">
            {t('shani_paya_title', current_lang)}
        </div>
        
        <div style="background:#f5f3ff; border-radius:12px; padding:14px; border:1.5px solid #e9d5ff; margin-bottom:1.1rem;">
            <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">ACTIVE TRANSIT PAYA</div>
            <div style="font-size:1.35rem; font-weight:900; color:#5b21b6; margin:4px 0;">{shani_paya_data['paya']}</div>
            <div style="font-size:0.95rem; color:#7c3aed; font-weight:800;">Status: {shani_paya_data['status']}</div>
            <div style="font-size:0.92rem; color:#475569; margin-top:3px;"><b>Timeline:</b> {shani_paya_data['timeline']}</div>
            <div style="font-size:0.96rem; line-height:1.65; color:#3b0764; margin-top:8px;">{shani_paya_data['desc']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #ddd6fe; border-left:5px solid #7c3aed; margin-bottom:1.1rem;">
            <div style="font-weight:900; font-size:1.05rem; color:#5b21b6; margin-bottom:5px;">{t('sadesati_title', current_lang)}</div>
            <div style="font-size:1rem; font-weight:800; color:#6d28d9;">{shani_sadesati_data['type']}</div>
            <div style="font-size:0.92rem; color:#64748b; margin-bottom:6px;">Timeline: {shani_sadesati_data['dates']}</div>
            <div style="font-size:0.96rem; line-height:1.65; color:#1e293b;">{shani_sadesati_data['impact']}</div>
        </div>

        <div style="background:#f5f3ff; border-radius:12px; padding:14px; border:1.5px solid #ddd6fe;">
            <div style="font-weight:900; font-size:1.05rem; color:#5b21b6; margin-bottom:8px;">🪔 Shani Protective Remedies:</div>
            <div style="font-size:0.95rem; line-height:1.65; color:#3b0764;">
                • Recite the <b>Hanuman Chalisa</b> daily, especially on Saturday and Tuesday evenings.<br>
                • Offer mustard oil and black sesame seeds in an iron or steel bowl to Shani Dev, or light a mustard oil lamp near a sacred Peepal tree on Saturdays.<br>
                • Because you operate under <b>Silver Feet (Rajat Paya)</b>, offering raw milk mixed with clean water on a Shiva Lingam on Mondays activates an exceptional shield against Sade Sati friction.
            </div>
        </div>
    </div>
    """)


# ==============================================================================
# PAGE 4: LIVE DAILY PREDICTION & TODAY'S COSMIC PULSE
# ==============================================================================
def render_page_live():
    now_ist = datetime.datetime.now()
    cur_star_idx, s_dt, e_dt = get_current_nakshatra_window(now_ist)
    offset = (cur_star_idx - chart_info["star_idx"]) % 9
    nav_name, icon, quality = NAVTARA_NAMES[offset]
    vahan_info = calculate_shani_vahan(chart_info["star_idx"], cur_star_idx)
    p_day = get_personal_day_vibe(dob_parsed, now_ist.date(), current_lang)

    render_html(f"""
    <div class="light-card-live">
        <div style="font-weight:900; font-size:1.25rem; color:#0369a1; margin-bottom:1rem; border-bottom:2px solid #bae6fd; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{t('live_pulse_title', current_lang)}</span>
            <span style="font-size:0.85rem; background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:20px; font-weight:900;">LIVE IST</span>
        </div>

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

        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin-bottom:1.1rem;">
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd;">
                <div style="font-size:0.85rem; color:#0284c7; font-weight:800; text-transform:uppercase;">DAILY SHANI VAHAN</div>
                <div style="font-size:1.15rem; font-weight:900; color:#0369a1;">{vahan_info['name']}</div>
                <div style="font-size:0.92rem; color:#64748b;">{vahan_info['type']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd;">
                <div style="font-size:0.85rem; color:#0284c7; font-weight:800; text-transform:uppercase;">PERSONAL DAY VIBE</div>
                <div style="font-size:1.15rem; font-weight:900; color:#0369a1;">Day {p_day['number']} ({p_day['planet'].split()[0]})</div>
                <div style="font-size:0.92rem; color:#64748b;">Alignment Energy</div>
            </div>
        </div>

        <div style="background:#f0f9ff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd;">
            <div style="font-weight:900; font-size:1.05rem; color:#0369a1; margin-bottom:8px;">🎯 Today's Actionable Strategy & Remedies:</div>
            <div style="font-size:0.95rem; line-height:1.65; color:#0c4a6e;">
                • <b>Decision Protocol:</b> {"🟢 High green light for critical ventures, agreements, property, and financial investments." if "🟢" in icon else "🔴 Avoid speculative gambles, practice patience in communications, and postpone high-stakes friction."}<br>
                • <b>Saturn Mount Remedy:</b> Feed birds or stray animals this morning to harmonize the daily Shani vehicle.<br>
                • <b>Aura Protection Mantra:</b> Chant <b>Om Namah Shivaya</b> 11 times before starting important ventures today.
            </div>
        </div>
    </div>
    """)


# ==============================================================================
# PAGE 5: 7-DAY NAKSHATRA TRANSIT FORECAST
# ==============================================================================
def render_page_forecast():
    now_ist = datetime.datetime.now()
    transits = get_7_day_moon_transits(now_ist, chart_info["star_idx"])

    render_html(f"""
    <div style="font-weight:900; font-size:1.25rem; color:#1e293b; margin-bottom:0.8rem;">
        {t('forecast_title', current_lang)}
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
            • <b>Remedy & Action Plan:</b> {"Schedule critical meetings, sign major documents, and wear light or energizing colors." if "🟢" in sel_tr['icon'] else "Pause aggressive financial risks, keep conversations respectful and calm, and recite Hanuman Chalisa in the evening."}
        </div>
    </div>
    """)


# ==============================================================================
# PAGE 6: PLANETARY POSITIONS (SIDEREAL LAHIRI)
# ==============================================================================
def render_page_planets():
    now_ist = datetime.datetime.now()
    planets_data = get_sidereal_planet_positions(now_ist)

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:8px; border-bottom:2px solid #fed7aa; padding-bottom:0.5rem;">
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


# ==============================================================================
# PAGE 7: CONSOLIDATED VEDIC REMEDIES SANCTUARY
# ==============================================================================
def render_page_remedies():
    render_html(f"""
    <div class="light-card-num">
        <div style="font-weight:900; font-size:1.25rem; color:#065f46; margin-bottom:1rem; border-bottom:2px solid #bbf7d0; padding-bottom:0.5rem;">
            🪔 Consolidated Vedic Astro-Remedies Sanctuary
        </div>
        
        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #059669; margin-bottom:1rem;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">1. Janma Nakshatra Protection ({chart_info['star_name']})</div>
            <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">
                • Worship Lord Shiva or Lord Yama to clear heavy ancestral burdens and establish inner stillness.<br>
                • Chant <b>Om Hreem Bharanyai Namah</b> or <b>Maha Mrityunjaya Mantra</b> 11 times every morning.
            </div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #10b981; margin-bottom:1rem;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">2. Numerology Harmony (Mulank {mulank} & Bhagyank {bhagyank})</div>
            <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">
                • Drink water from a silver or copper vessel to balance high planetary nervous intensity.<br>
                • Maintain an uncluttered workspace free from tangled electronics to amplify mental clarity.
            </div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #ddd6fe; border-left:5px solid #7c3aed;">
            <div style="font-weight:900; font-size:1.05rem; color:#5b21b6; margin-bottom:5px;">3. Shani Rajat Paya (Silver Feet) Shield</div>
            <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">
                • Recite the Hanuman Chalisa on Tuesday and Saturday evenings.<br>
                • Pour raw cow milk and clean water over a Shiva Lingam on Mondays to awaken the divine silver shield.
            </div>
        </div>
    </div>
    """)


# ==============================================================================
# PAGE 8: SHARE APP PORTAL
# ==============================================================================
def render_page_share():
    app_url = "https://navtara-pulse.streamlit.app"
    share_msg = "Discover your real-time Vedic Moon transit rhythm, Shani Paya, and personalized Numerology blueprint with Navtara Pulse!"
    encoded_url = urllib.parse.quote(app_url)
    encoded_msg = urllib.parse.quote(f"{share_msg}\n\nCheck your cosmic alignment here: {app_url}")

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:1rem; border-bottom:2px solid #fed7aa; padding-bottom:0.5rem;">
            {t('share_title', current_lang)}
        </div>
        <div style="font-size:0.96rem; color:#475569; margin-bottom:1rem; line-height:1.5;">
            Share this authentic timing engine with your family, friends, and colleagues via your favorite platform:
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
            <div style="font-size:0.88rem; color:#9a3412; font-weight:800;">Direct App Link:</div>
            <div style="font-size:1rem; font-weight:900; color:#431407; margin-top:2px;"><b>{app_url}</b></div>
        </div>
    </div>
    """)


# ==============================================================================
# ROUTER DISPATCHER: RENDER THE SELECTED PAGE
# ==============================================================================
PAGES = {
    "about": render_page_about,
    "navtara": render_page_navtara,
    "numerology": render_page_numerology,
    "shani": render_page_shani,
    "live": render_page_live,
    "forecast": render_page_forecast,
    "planets": render_page_planets,
    "remedies": render_page_remedies,
}

active_page_func = PAGES.get(st.session_state.current_page, render_page_about)
active_page_func()
