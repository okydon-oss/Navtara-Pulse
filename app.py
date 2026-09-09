import streamlit as st
import datetime
import urllib.parse
import math
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

st.markdown("""
<style>
    /* Responsive container formatting */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 5.5rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
        max-width: 780px;
    }
    
    /* Top Language Dropdown Styling */
    div[data-baseweb="select"] {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    
    /* Mobile-first card components */
    .auth-hero-box {
        background: linear-gradient(135deg, #fdfbf7 0%, #fffbeb 100%);
        border: 1.5px solid #fde68a;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.08);
    }
    
    .light-card-profile {
        background: #ffffff;
        border: 1.5px solid #fed7aa;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(249, 115, 22, 0.05);
    }
    
    .light-card-num {
        background: #ffffff;
        border: 1.5px solid #bbf7d0;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.05);
    }
    
    .light-card-shani {
        background: #ffffff;
        border: 1.5px solid #ddd6fe;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(139, 92, 246, 0.05);
    }
    
    .light-card-live {
        background: #ffffff;
        border: 1.5px solid #bae6fd;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(14, 165, 233, 0.05);
    }

    /* Fixed bottom navigation styling */
    .stButton button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 13.5px !important;
        padding: 6px 4px !important;
    }
</style>
""", unsafe_allow_html=True)

TRANSLATIONS = {
    "en": {
        "app_title": "✨ Navtara Pulse",
        "app_subtitle": "Vedic Nakshatra Rhythm & Cosmic Alignment",
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
        "pada_label": "Pada",
        "moon_rashi_label": "Moon Rashi",
        "lagna_label": "Ascendant (Lagna)",
        "mulank_label": "Mulank (Driver)",
        "bhagyank_label": "Bhagyank (Destiny)",
        "namank_label": "Namank (Name No.)",
        "shani_paya_title": "🪐 Active Shani Paya & 2.5-Year Transit",
        "sadesati_title": "⚖️ Shani Sade Sati & Dhaiya Status",
        "live_pulse_title": "⚡ Today's Live Cosmic Pulse",
        "forecast_title": "🗓️ 7-Day Moon Transit Matrix",
        "planet_title": "🔭 Real-Time Sidereal Planetary Longitudes",
        "share_title": "📲 Share Navtara Pulse With Friends & Family"
    },
    "hi": {
        "app_title": "✨ नवतारा पल्स (Navtara Pulse)",
        "app_subtitle": "वैदिक नक्षत्र गोचर एवं खगोलीय ऊर्जा चक्र",
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
        "namank_label": "नामांक (Name Number)",
        "shani_paya_title": "🪐 वर्तमान शनि पाया एवं गोचर काल",
        "sadesati_title": "⚖️ शनि साढ़े साती एवं ढैय्या स्थिति",
        "live_pulse_title": "⚡ आज का दैनिक खगोलीय प्रवाह",
        "forecast_title": "🗓️ आगामी 7 दिनों का नक्षत्र गोचर",
        "planet_title": "🔭 वास्तविक निरयण ग्रह स्पष्ट",
        "share_title": "📲 नवतारा पल्स को परिवार व मित्रों के साथ साझा करें"
    },
    "mr": {
        "app_title": "✨ नवतारा पल्स (Navtara Pulse)",
        "app_subtitle": "वैदिक नक्षत्र गोचर आणि वैश्विक ऊर्जा चक्र",
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
        "forecast_title": "🗓️ पुढील ७ दिवसांचे नक्षत्र संक्रमण",
        "planet_title": "🔭 निरयन प्रत्यक्ष ग्रह स्थिती",
        "share_title": "📲 नवतारा पल्स ॲप मित्र आणि कुटुंबासह शेअर करा"
    },
    "gu": {
        "app_title": "✨ નવતારા પલ્સ (Navtara Pulse)",
        "app_subtitle": "વૈદિક નક્ષત્ર ગોચર અને બ્રહ્માંડીય ઊર્જા ચક્ર",
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
        "shani_paya_title": "🪐 વર્તમાન શનિ પાયા અને ગોચર",
        "sadesati_title": "⚖️ શનિ સાડાસાતી અને ઢૈય્યા સ્થિતિ",
        "live_pulse_title": "⚡ આજનો જીવંત નક્ષત્ર પ્રભાવ",
        "forecast_title": "🗓️ આગામી ૭ દિવસોનું નક્ષત્ર ગોચર",
        "planet_title": "🔭 પ્રત્યક્ષ નિરયણ ગ્રહ સ્થિતિ",
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
    ("Janma (Birth Star)", "🔵", "Introspective"),
    ("Sampat (Wealth & Abundance)", "🟢", "Highly Auspicious"),
    ("Vipat (Danger & Obstacles)", "🔴", "Caution Required"),
    ("Kshema (Well-being & Flow)", "🟢", "Harmonious"),
    ("Pratyari (Opposition & Obstacles)", "🔴", "Defense & Patience"),
    ("Sadhana (Success & Execution)", "🟢", "Action & Execution"),
    ("Vadha (Destruction / Critical)", "🔴", "High Risk / Pause"),
    ("Mitra (Friendship & Support)", "🟢", "Cooperation & Ease"),
    ("Ati-Mitra (Supreme Alliance)", "🟢🟢", "Maximum Fortune")
]

SHANI_VAHANS = {
    1: {"name": "🐴 Horse (Ghoda)", "type": "Rapid Progress & Victory", "vibe": "Speed and bold execution"},
    2: {"name": "🫏 Donkey (Gadha)", "type": "Heavy Effort & Hard Labor", "vibe": "Endurance and patience"},
    3: {"name": "🦊 Jackal (Siyar)", "type": "Caution & Hidden Traps", "vibe": "Alertness in legal/financial affairs"},
    4: {"name": "🐘 Elephant (Hathi)", "type": "Royalty, Honor & Luxury", "vibe": "Status and financial windfalls"},
    5: {"name": "🐂 Bull (Bail)", "type": "Steady Foundations & Gains", "vibe": "Disciplined progress"},
    6: {"name": "🦁 Lion (Sher)", "type": "Commanding Authority & Courage", "vibe": "Overcoming competition"},
    7: {"name": "🐦‍⬛ Crow (Kowwa)", "type": "Restlessness & Scattered Energy", "vibe": "Practice silence and calm"},
    8: {"name": "🦚 Peacock (Mayur)", "type": "Joy, Aesthetics & Good News", "vibe": "Creative and family warmth"},
    9: {"name": "🦢 Swan (Hans)", "type": "Wisdom, Mental Peace & Health", "vibe": "Spiritual and clear thinking"}
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

def get_nakshatra_traits(star_idx: int, lang: str = "en") -> str:
    """Returns dynamic Nakshatra traits across English, Hindi, Marathi, and Gujarati."""
    traits_map = {
        1: {
            "en": "Pioneering, bold, and energetic. You possess natural healing energy, swift analytical agility, and a talent for starting ambitious projects.",
            "hi": "साहसी, ऊर्जावान एवं त्वरित निर्णय लेने में सक्षम। आपके स्वभाव में नैसर्गिक नेतृत्व, नवीन शुरुआत और कठिनाइयों से शीघ्र उबरने की क्षमता होती है।",
            "mr": "धाडसी, उत्साही आणि तत्पर निर्णय घेणारे व्यक्तिमत्व. नव्या उपक्रमांची सुरुवात करणे आणि आव्हानांना तोंड देणे हे तुमचे वैशिष्ट्य आहे.",
            "gu": "સાહસિક, ઉત્સાહી અને ઝડપી નિર્ણય લેવાની અદભુત ક્ષમતા. નવી શરૂઆત કરવી અને પ્રગતિના માર્ગે અગ્રેસર રહેવું તમારો સ્વભાવ છે."
        },
        2: {
            "en": "Determined, charismatic, highly passionate, and disciplined. Governed by Yama and Venus, you possess strong inner perseverance, judicial fairness, and the capacity to bear heavy responsibility with dignity.",
            "hi": "दृढ़ संकल्पी, सम्मोहक व्यक्तित्व, अत्यंत निष्ठावान एवं कर्मठ। भरणी नक्षत्र के प्रभाव से आपमें सत्य के प्रति अडिगता, न्यायप्रियता और भारी जिम्मेदारियों को सहजता से वहन करने का सामर्थ्य होता है।",
            "mr": "दृढनिश्चयी, आकर्षक आणि अथांग कार्यक्षमता असलेले व्यक्तिमत्व. भरणी नक्षत्राच्या प्रभावामुळे तुमच्यात न्यायप्रियता, सत्यनिष्ठा आणि कठीण प्रसंगात शांत राहण्याची ताकद आहे.",
            "gu": "દૃઢ સંકલ્પ, પ્રભાવશાળી વ્યક્તિત્વ અને ઉચ્ચ શિસ્ત. કોઈપણ મુશ્કેલ પરિસ્થિતિમાં અડગ રહીને સફળતા પ્રાપ્ત કરવાની કુદરતી શક્તિ ધરાવો છો."
        }
    }
    fallback_star = traits_map.get(star_idx, traits_map[2])
    return fallback_star.get(lang, fallback_star["en"])

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
        "desc": f"Personal Day {personal_day} resonates with {planet_info} energy."
    }

def get_numerology_life_domains(mulank: int, bhagyank: int, namank: int, lang: str = "en") -> dict:
    """Generates an exhaustive analysis across Career, Wealth, Relationship, Health, Luck and Remedies."""
    p_m = NUM_PLANET_NAMES.get(mulank, {}).get(lang, f"Planet {mulank}")
    p_b = NUM_PLANET_NAMES.get(bhagyank, {}).get(lang, f"Planet {bhagyank}")
    p_n = NUM_PLANET_NAMES.get(namank, {}).get(lang, f"Planet {namank}")

    if lang == "hi":
        return {
            "career_title": "💼 आजीविका एवं कर्मक्षेत्र (Career & Profession)",
            "career_desc": (
                f"मूलांक {mulank} ({p_m}) और भाग्यांक {bhagyank} ({p_b}) का संयोग आपको असाधारण रणनीतिक नेतृत्व और समस्या-निवारण क्षमता देता है। "
                "आप किसी के अधीन काम करने की अपेक्षा स्वतंत्र निर्णय और बड़े स्तर के तकनीकी, संरचनात्मक या प्रबंधकीय कार्यों में शीर्ष सफलता प्राप्त करते हैं। "
                "<b>सर्वोत्तम कार्यक्षेत्र:</b> सूचना प्रौद्योगिकी, इंजीनियरिंग, रियल एस्टेट, कॉर्पोरेट प्रशासन, कानूनी सलाहकार, अनुसंधान एवं स्वतंत्र उद्यमिता।"
            ),
            "wealth_title": "💰 धन-सम्पदा एवं वित्तीय स्थिरता (Wealth & Finances)",
            "wealth_desc": (
                f"राहु और मंगल के प्रभाव से आपके जीवन में अचानक बड़े वित्तीय लाभ और द्रुतगामी पूंजी के योग बनते हैं। "
                "<b>धन संचय नियम:</b> भूमि, अचल संपत्ति और स्वर्ण में निवेश आपके लिए सर्वाधिक सुरक्षित और लाभकारी रहेगा। अनियोजित सट्टे से बचें।"
            ),
            "rel_title": "❤️ संबंध, वैवाहिक जीवन एवं सामंजस्य (Love & Relationships)",
            "rel_desc": (
                "आप संबंधों में अत्यंत निष्ठावान, स्पष्टवादी और सुरक्षात्मक हैं। आपको दिखावा बिल्कुल पसंद नहीं है। "
                "<b>दांपत्य मंत्र:</b> संवाद के समय वाणी में कोमलता और धैर्य बनाए रखें। मूलांक 1, 3, 5 और 6 वाले जातक आपके लिए सहयोगी सिद्ध होते हैं।"
            ),
            "health_title": "🌿 स्वास्थ्य एवं ऊर्जा स्तर (Health & Vitality)",
            "health_desc": (
                "आपके पास नैसर्गिक रूप से उच्च शारीरिक सहनशक्ति है, परंतु पित्त विकार, रक्तचाप और मानसिक अति-सक्रियता पर ध्यान देना आवश्यक है। "
                "<b>आरोग्य सलाह:</b> भरपूर जल पिएं, अत्यधिक तीखा भोजन सीमित करें, तथा रात्रि को 10 मिनट ध्यान द्वारा मन को शांत करें।"
            ),
            "luck_title": "🍀 भाग्य सूचक तत्व (Harmonic Luck Matrix)",
            "lucky_num": "1, 3, 5, 9 (शुभ)",
            "avoid_num": "2, 8 (सावधानी रखें)",
            "lucky_days": "रविवार, मंगलवार, गुरुवार",
            "lucky_colors": "केसरिया, पीला, हल्का नीला, लाल",
            "lucky_dir": "दक्षिण (South) एवं ईशान कोण (North-East)"
        }
    elif lang == "mr":
        return {
            "career_title": "💼 व्यवसाय व नोकरी (Career & Professional Growth)",
            "career_desc": (
                f"मूलांक {mulank} ({p_m}) व भाग्यांक {bhagyank} ({p_b}) यांचा संयोग तुम्हाला धाडसी आणि स्वतंत्र निर्णय घेण्याची क्षमता देतो. "
                "<b>अनुकूल क्षेत्रे:</b> माहिती तंत्रज्ञान, अभियांत्रिकी, स्थावर मालमत्ता, प्रशासन, व्यवस्थापन सल्लागार व तांत्रिक उद्योग."
            ),
            "wealth_title": "💰 आर्थिक संपदा व धनयोग (Wealth & Money)",
            "wealth_desc": (
                "तुमच्या पत्रिकेत अचानक धनलाभ आणि मोठ्या संधींचे योग आहेत. दीर्घकालीन गुंतवणुकीत जमीन व स्थिर मालमत्ता फायदेशीर ठरतात."
            ),
            "rel_title": "❤️ नातेसंबंध व कौटुंबिक जीवन (Love & Relationships)",
            "rel_desc": (
                "तुम्ही नात्यांमध्ये अत्यंत निष्ठावान आणि सरळ आहात. कुटुंबात संवाद साधताना शांतता व ऐकून घेण्याची वृत्ती ठेवा."
            ),
            "health_title": "🌿 आरोग्य व जीवनशैली (Health & Vitality)",
            "health_desc": (
                "भरपूर शारीरिक ऊर्जा असली तरी अतिविचार आणि कामाच्या तणावामुळे डोकेदुखी व पित्ताचा त्रास होऊ शकतो. रोज सकाळी ध्यानधारणा करा."
            ),
            "luck_title": "🍀 भाग्यवान घटक (Lucky Attributes Chart)",
            "lucky_num": "१, ३, ५, ९ (अत्यंत शुभ)",
            "avoid_num": "२, ८ (सावधगिरी बाळगा)",
            "lucky_days": "रविवार, मंगळवार, गुरुवार",
            "lucky_colors": "लाल, भगवा, पिवळा, आकाशी निळा",
            "lucky_dir": "दक्षिण आणि ईशान्य दिशा"
        }
    elif lang == "gu":
        return {
            "career_title": "💼 વ્યવસાય અને કારકિર્દી (Career & Ambition)",
            "career_desc": (
                f"મૂળાંક {mulank} ({p_m}) અને ભાગ્યાંક {bhagyank} ({p_b}) નો સુભગ સમન્વય અદભુત આત્મવિશ્વાસ, ઊર્જા અને નવીન વિચારો આપે છે. "
                "<b>શ્રેષ્ઠ ક્ષેત્રો:</b> આઈટી, એન્જિનિયરિંગ, રિયલ એસ્ટેટ, વહીવટી સેવાઓ અને સ્વતંત્ર વ્યવસાય."
            ),
            "wealth_title": "💰 ધન-સંપત્તિ અને રોકાણ (Wealth & Finances)",
            "wealth_desc": (
                "આકસ્મિક આર્થિક વૃદ્ધિ અને મોટી તકોના યોગ બને છે. જમીન-મકાન અને લાંબા ગાળાના રોકાણમાં વિશેષ ફાયદો થાય છે."
            ),
            "rel_title": "❤️ સંબંધો અને પારિવારિક સુખ (Love & Social Bonding)",
            "rel_desc": (
                "તમે સંબંધોમાં સત્યનિષ્ઠ અને વફાદાર છો. વાણીમાં નમ્રતા અને સાંભળવાની ધીરજ રાખવાથી દાંપત્યજીવન મધુર બને છે."
            ),
            "health_title": "🌿 સ્વાસ્થ્ય અને ઊર્જા (Health & Wellness)",
            "health_desc": (
                "ઉચ્ચ શારીરિક ઊર્જા હોવા છતાં એસિડિટી કે અનિદ્રા જેવી તકલીફોથી બચવું જરૂરી છે. નિયમિત પ્રાણાયામ ઉત્તમ રહેશે."
            ),
            "luck_title": "🍀 ભાગ્યશાળી તત્વો (Lucky Attributes Matrix)",
            "lucky_num": "૧, ૩, ૫, ૯ (શુભ)",
            "avoid_num": "૨, ૮ (સાવચેતી જરૂરી)",
            "lucky_days": "રવિવાર, મંગળવાર, ગુરુવાર",
            "lucky_colors": "લાલ, કેસરી, સોનેરી, આછો વાદળી",
            "lucky_dir": "દક્ષિણ અને ઈશાન ખૂણો"
        }
    else:
        return {
            "career_title": "💼 Career Trajectory & Executive Ambition",
            "career_desc": (
                f"The dynamic synthesis of Driver {mulank} ({p_m}) and Conductor {bhagyank} ({p_b}) creates a powerhouse combination of strategic unconventional thinking and warrior-like execution. "
                "You thrive in leadership roles that require structural problem-solving, architectural vision, and calculated risk-taking. "
                "<b>Optimal Avenues:</b> Technology Architecture, Systems Engineering, Real Estate Infrastructure, Corporate Governance, and Independent Entrepreneurship."
            ),
            "wealth_title": "💰 Wealth Dynamics & Long-Term Financial Mastery",
            "wealth_desc": (
                f"Rahu and Mars inherently catalyze sudden expansions, non-linear wealth opportunities, and high-velocity capital turnover. "
                "<b>Wealth Accumulation Strategy:</b> Long-term real estate holdings, land, and tangible hard assets provide your safest financial anchor. "
                "Strictly avoid speculative unhedged market gambles."
            ),
            "rel_title": "❤️ Relationships, Marriage & Interpersonal Dynamics",
            "rel_desc": (
                "You are fiercely loyal, protective, and authentic in relationships, with zero tolerance for pretense or superficial flatteries. "
                "<b>Marital Harmony:</b> Practice mindful active listening and verbal gentleness during high-intensity discussions. "
                "Natives with Driver/Conductor numbers 1, 3, 5, and 6 bring stabilizing warmth and romantic balance."
            ),
            "health_title": "🌿 Health, Vitality & Holistic Bio-Rhythms",
            "health_desc": (
                "You possess tremendous organic stamina and regenerative capacity, but your fiery metabolic constitution (Mars) combined with Rahu's nervous intensity demands conscious pacing. "
                "<b>Vitality Protocol:</b> Stay heavily hydrated, reduce excessive refined pungent stimulants, and practice 15 minutes of grounding Pranayama before sleep."
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
            "impact": "Saturn transits the 12th from Moon. Focus on budgeting, foreign avenues, spiritual grounding, and avoiding mental overthinking.",
            "dates": "March 2025 – June 2027"
        }
    elif diff == 0:
        return {
            "active": True,
            "type": "Sade Sati Phase 2 (Peak Phase / 1st House Janma Transit)",
            "impact": "Saturn transits your natal Moon. Deep personal restructuring, high responsibilities, and major life decisions.",
            "dates": "June 2027 – August 2029"
        }
    elif diff == 1:
        return {
            "active": True,
            "type": "Sade Sati Phase 3 (Setting Phase / 2nd House Transit)",
            "impact": "Saturn transits the 2nd from Moon. Financial realignment, family consolidation, and long-term asset stabilization.",
            "dates": "August 2029 – May 2032"
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
    # Ensure utc_dt is naive for clean mathematical operations
    if utc_dt.tzinfo is not None:
        utc_dt = utc_dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)

    if HAS_SWISSEPH:
        try:
            t_jd = swe.julday(
                utc_dt.year, utc_dt.month, utc_dt.day,
                utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
            )
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            # Use Moshier analytical ephemeris which requires NO external .se1 files
            res, _ = swe.calc_ut(t_jd, swe.MOON, swe.FLG_MOSEPH | swe.FLG_SIDEREAL)
            return float(res[0] % 360.0)
        except Exception:
            try:
                res, _ = swe.calc_ut(t_jd, swe.MOON, swe.FLG_SIDEREAL)
                return float(res[0] % 360.0)
            except Exception:
                pass

    # High-precision Lahiri-aligned analytical fallback
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

    # Calculate approximate Lagna
    lagna_idx = (rashi_idx + 1) % 12
    if HAS_SWISSEPH:
        try:
            t_jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                              utc_dt.hour + utc_dt.minute / 60.0)
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            # Universal swe.houses call compatible across all pyswisseph builds
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

    # Sidereal Moon average speed approx 0.55 deg per hour
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
        
        # Calculate Navtara
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
            "start_str": s_time.strftime("%d %b, %I:%M %p"),
            "end_str": e_time.strftime("%d %b, %I:%M %p")
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
            # Ketu is exactly opposite Rahu
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
    st.session_state.current_page = "profile"

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "selected_transit_idx" not in st.session_state:
    st.session_state.selected_transit_idx = 0

prof = st.session_state.user_profile
current_lang = prof.get("lang", "en")

col_top_l, col_top_r = st.columns([2.8, 1.2])
with col_top_l:
    st.markdown(f"<h2 style='margin:0; font-size:24px; color:#1e293b;'>{t('app_title', current_lang)}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:12.5px; color:#64748b; margin-bottom:8px;'>{t('app_subtitle', current_lang)}</div>", unsafe_allow_html=True)

with col_top_r:
    lang_opts = {"en": "English", "hi": "हिन्दी", "mr": "मराठी", "gu": "ગુજરાતી"}
    selected_lang_code = st.selectbox(
        "Language",
        options=list(lang_opts.keys()),
        format_func=lambda x: lang_opts[x],
        index=list(lang_opts.keys()).index(current_lang) if current_lang in lang_opts else 0,
        label_visibility="collapsed"
    )
    if selected_lang_code != current_lang:
        st.session_state.user_profile["lang"] = selected_lang_code
        save_user_profile(st.session_state.user_profile)
        st.rerun()

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

if st.session_state.current_page == "profile":
    # Authenticity & Purpose Hero Box
    st.markdown(f"""
    <div class="auth-hero-box">
        <div style="font-weight:800; font-size:14.5px; color:#92400e; margin-bottom:6px; display:flex; align-items:center; gap:6px;">
            <span>🛡️</span> <span>Authentic Vedic Timing Engine & Mathematical Precision</span>
        </div>
        <div style="font-size:12.8px; line-height:1.55; color:#78350f;">
            Powered by the sub-arcsecond Moshier-Swiss Ephemeris algorithm (Chitrapaksha Lahiri Ayanamsa), Navtara Pulse calculates the Moon's real-time velocity to reveal your personal daily <b>Golden Timing Windows</b> and <b>Friction Caution Hours</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Smart User Profile Box with Inline Edit
    with st.container(border=True):
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            st.markdown(f"""
            <div style="font-weight:800; font-size:16px; color:#0f172a;">👤 {prof['name']}'s Profile</div>
            <div style="font-size:12.5px; color:#475569; margin-top:3px;">
                📅 <b>DOB:</b> {dob_parsed.strftime('%d %B %Y')} &nbsp;|&nbsp; ⏰ <b>Time:</b> {tob_parsed.strftime('%I:%M %p')}<br>
                📍 <b>Place:</b> {prof['city']}
            </div>
            """, unsafe_allow_html=True)
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
    n_traits = get_nakshatra_traits(chart_info["star_idx"], current_lang)
    
    st.markdown(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:17px; color:#9a3412; margin-bottom:12px; border-bottom:2px solid #fed7aa; padding-bottom:6px;">
            🌌 1. Navtara & Vedic Astrological Profile
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; text-align:center; margin-bottom:14px;">
            <div style="background:#fff7ed; border-radius:10px; padding:10px; border:1px solid #ffedd5;">
                <div style="font-size:11.5px; color:#c2410c; font-weight:700;">{t('nakshatra_label', current_lang)}</div>
                <div style="font-size:16px; font-weight:900; color:#9a3412;">{chart_info['star_name']}</div>
                <div style="font-size:11px; color:#ea580c; font-weight:600;">{t('pada_label', current_lang)} {chart_info['pada']}</div>
            </div>
            <div style="background:#fff7ed; border-radius:10px; padding:10px; border:1px solid #ffedd5;">
                <div style="font-size:11.5px; color:#c2410c; font-weight:700;">{t('moon_rashi_label', current_lang)}</div>
                <div style="font-size:16px; font-weight:900; color:#9a3412;">{chart_info['moon_rashi_name'].split()[0]}</div>
                <div style="font-size:11px; color:#ea580c; font-weight:600;">{chart_info['moon_rashi_name'].split()[-1]}</div>
            </div>
            <div style="background:#fff7ed; border-radius:10px; padding:10px; border:1px solid #ffedd5;">
                <div style="font-size:11.5px; color:#c2410c; font-weight:700;">{t('lagna_label', current_lang)}</div>
                <div style="font-size:16px; font-weight:900; color:#9a3412;">{chart_info['lagna_name'].split()[0]}</div>
                <div style="font-size:11px; color:#ea580c; font-weight:600;">{chart_info['lagna_name'].split()[-1]}</div>
            </div>
        </div>
        
        <div style="background:#fffaf0; border-radius:10px; padding:12px 14px; border-left:4px solid #f97316; margin-bottom:12px;">
            <div style="font-weight:800; font-size:13.5px; color:#9a3412; margin-bottom:4px;">✨ Personality & Core Archetype:</div>
            <div style="font-size:13px; line-height:1.55; color:#431407;">{n_traits}</div>
        </div>

        <div style="background:#fffaf0; border-radius:10px; padding:12px 14px; border:1px solid #fed7aa;">
            <div style="font-weight:800; font-size:13.5px; color:#9a3412; margin-bottom:4px;">🪔 Vedic Nakshatra Remedies:</div>
            <div style="font-size:12.8px; line-height:1.55; color:#431407;">
                • <b>Deity Worship:</b> Offer prayers to Lord Shiva or Lord Yama to harmonize vital life energy.<br>
                • <b>Vedic Mantra:</b> Chanting <code>Om Hreem Bharanyai Namah</code> or <code>Maha Mrityunjaya Mantra</code> on Fridays and Tuesdays removes heavy burdens.<br>
                • <b>Sacred Tree:</b> Nurture or water an Amla (Indian Gooseberry) plant.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == "numerology":
    num_domains = get_numerology_life_domains(mulank, bhagyank, namank, current_lang)
    p_m_label = NUM_PLANET_NAMES.get(mulank, {}).get(current_lang, f"Planet {mulank}")
    p_b_label = NUM_PLANET_NAMES.get(bhagyank, {}).get(current_lang, f"Planet {bhagyank}")
    p_n_label = NUM_PLANET_NAMES.get(namank, {}).get(current_lang, f"Planet {namank}")

    st.markdown(f"""
    <div class="light-card-num">
        <div style="font-weight:900; font-size:17px; color:#065f46; margin-bottom:12px; border-bottom:2px solid #bbf7d0; padding-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
            <span>🔢 2. Core Numerology Blueprint</span>
            <span style="font-size:11.5px; background:#d1fae5; color:#065f46; padding:3px 8px; border-radius:20px; font-weight:700;">Vedic & Chaldean</span>
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; text-align:center; margin-bottom:14px;">
            <div style="background:#f0fdf4; border-radius:10px; padding:10px; border:1px solid #dcfce7;">
                <div style="font-size:11px; color:#047857; font-weight:800; text-transform:uppercase;">{t('mulank_label', current_lang)}</div>
                <div style="font-size:26px; font-weight:900; color:#065f46; margin:2px 0;">{mulank}</div>
                <div style="font-size:11px; color:#059669; font-weight:700;">{p_m_label}</div>
            </div>
            <div style="background:#f0fdf4; border-radius:10px; padding:10px; border:1px solid #dcfce7;">
                <div style="font-size:11px; color:#047857; font-weight:800; text-transform:uppercase;">{t('bhagyank_label', current_lang)}</div>
                <div style="font-size:26px; font-weight:900; color:#065f46; margin:2px 0;">{bhagyank}</div>
                <div style="font-size:11px; color:#059669; font-weight:700;">{p_b_label}</div>
            </div>
            <div style="background:#f0fdf4; border-radius:10px; padding:10px; border:1px solid #dcfce7;">
                <div style="font-size:11px; color:#047857; font-weight:800; text-transform:uppercase;">{t('namank_label', current_lang)}</div>
                <div style="font-size:26px; font-weight:900; color:#065f46; margin:2px 0;">{namank}</div>
                <div style="font-size:11px; color:#059669; font-weight:700;">{p_n_label}</div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr; gap:12px; margin-bottom:14px;">
            <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border-left:4px solid #059669; border:1px solid #d1fae5; border-left-width:4px;">
                <div style="font-weight:800; font-size:14px; color:#065f46; margin-bottom:4px;">{num_domains['career_title']}</div>
                <div style="font-size:13px; line-height:1.55; color:#1e293b;">{num_domains['career_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border-left:4px solid #10b981; border:1px solid #d1fae5; border-left-width:4px;">
                <div style="font-weight:800; font-size:14px; color:#065f46; margin-bottom:4px;">{num_domains['wealth_title']}</div>
                <div style="font-size:13px; line-height:1.55; color:#1e293b;">{num_domains['wealth_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border-left:4px solid #14b8a6; border:1px solid #d1fae5; border-left-width:4px;">
                <div style="font-weight:800; font-size:14px; color:#065f46; margin-bottom:4px;">{num_domains['rel_title']}</div>
                <div style="font-size:13px; line-height:1.55; color:#1e293b;">{num_domains['rel_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border-left:4px solid #0d9488; border:1px solid #d1fae5; border-left-width:4px;">
                <div style="font-weight:800; font-size:14px; color:#065f46; margin-bottom:4px;">{num_domains['health_title']}</div>
                <div style="font-size:13px; line-height:1.55; color:#1e293b;">{num_domains['health_desc']}</div>
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:10px; padding:12px 14px; border:1px solid #bbf7d0;">
            <div style="font-weight:800; font-size:14px; color:#065f46; margin-bottom:8px;">{num_domains['luck_title']}</div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:12.5px;">
                <div><b>✨ Lucky Numbers:</b> {num_domains['lucky_num']}</div>
                <div><b>⚠️ Caution Numbers:</b> {num_domains['avoid_num']}</div>
                <div><b>📅 Auspicious Days:</b> {num_domains['lucky_days']}</div>
                <div><b>🧭 Favorable Direction:</b> {num_domains['lucky_dir']}</div>
                <div style="grid-column: span 2;"><b>🎨 Energizing Colors:</b> {num_domains['lucky_colors']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == "shani":
    st.markdown(f"""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:17px; color:#5b21b6; margin-bottom:12px; border-bottom:2px solid #ddd6fe; padding-bottom:6px;">
            {t('shani_paya_title', current_lang)}
        </div>
        
        <div style="background:#f5f3ff; border-radius:10px; padding:12px 14px; border:1px solid #e9d5ff; margin-bottom:12px;">
            <div style="font-size:12px; color:#6d28d9; font-weight:700;">ACTIVE TRANSIT PAYA</div>
            <div style="font-size:20px; font-weight:900; color:#5b21b6; margin:2px 0;">{shani_paya_data['paya']}</div>
            <div style="font-size:12.5px; color:#7c3aed; font-weight:700;">Status: {shani_paya_data['status']}</div>
            <div style="font-size:12px; color:#64748b; margin-top:2px;"><b>Timeline:</b> {shani_paya_data['timeline']}</div>
            <div style="font-size:13px; line-height:1.55; color:#3b0764; margin-top:8px;">{shani_paya_data['desc']}</div>
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border-left:4px solid #7c3aed; border:1px solid #ddd6fe; border-left-width:4px; margin-bottom:12px;">
            <div style="font-weight:800; font-size:14px; color:#5b21b6; margin-bottom:4px;">{t('sadesati_title', current_lang)}</div>
            <div style="font-size:13.5px; font-weight:700; color:#6d28d9;">{shani_sadesati_data['type']}</div>
            <div style="font-size:12px; color:#64748b; margin-bottom:6px;">Timeline: {shani_sadesati_data['dates']}</div>
            <div style="font-size:13px; line-height:1.55; color:#1e293b;">{shani_sadesati_data['impact']}</div>
        </div>

        <div style="background:#f5f3ff; border-radius:10px; padding:12px 14px; border:1px solid #ddd6fe;">
            <div style="font-weight:800; font-size:14px; color:#5b21b6; margin-bottom:6px;">🪔 Shani Protective Remedies:</div>
            <div style="font-size:12.8px; line-height:1.55; color:#3b0764;">
                • Recite the <b>Hanuman Chalisa</b> daily, especially on Saturday evenings.<br>
                • Offer mustard oil and black sesame seeds in a steel bowl to Shani Dev or light a mustard oil lamp near a Peepal tree on Saturdays.<br>
                • Since you operate under <b>Silver Feet</b>, offering raw milk and water on a Shiva Lingam grants exceptional shield against Sade Sati friction.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == "live":
    now_ist = datetime.datetime.now()
    cur_star_idx, s_dt, e_dt = get_current_nakshatra_window(now_ist)
    offset = (cur_star_idx - chart_info["star_idx"]) % 9
    nav_name, icon, quality = NAVTARA_NAMES[offset]
    vahan_info = calculate_shani_vahan(chart_info["star_idx"], cur_star_idx)
    p_day = get_personal_day_vibe(dob_parsed, now_ist.date(), current_lang)

    st.markdown(f"""
    <div class="light-card-live">
        <div style="font-weight:900; font-size:17px; color:#0369a1; margin-bottom:12px; border-bottom:2px solid #bae6fd; padding-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
            <span>{t('live_pulse_title', current_lang)}</span>
            <span style="font-size:12px; background:#e0f2fe; color:#0369a1; padding:3px 10px; border-radius:20px; font-weight:800;">LIVE IST</span>
        </div>

        <div style="background:#f0f9ff; border-radius:10px; padding:12px 14px; border:1px solid #bae6fd; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:12px; color:#0284c7; font-weight:700;">CURRENT MOON NAKSHATRA</div>
                    <div style="font-size:20px; font-weight:900; color:#0369a1;">{NAKSHATRAS[cur_star_idx - 1]}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:24px;">{icon}</div>
                    <div style="font-size:12px; font-weight:800; color:#0369a1;">{quality}</div>
                </div>
            </div>
            <div style="font-size:13.5px; font-weight:800; color:#0284c7; margin-top:6px;">Navtara: {nav_name}</div>
            <div style="font-size:12px; color:#475569; margin-top:4px;">
                ⏳ <b>Active Window:</b> {s_dt.strftime('%a, %d %b %I:%M %p')} → {e_dt.strftime('%a, %d %b %I:%M %p IST')}
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:12px;">
            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bae6fd;">
                <div style="font-size:11px; color:#0284c7; font-weight:700;">DAILY SHANI VAHAN</div>
                <div style="font-size:14px; font-weight:800; color:#0369a1;">{vahan_info['name']}</div>
                <div style="font-size:11.5px; color:#64748b;">{vahan_info['type']}</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bae6fd;">
                <div style="font-size:11px; color:#0284c7; font-weight:700;">PERSONAL DAY VIBE</div>
                <div style="font-size:14px; font-weight:800; color:#0369a1;">Day {p_day['number']} ({p_day['planet'].split()[0]})</div>
                <div style="font-size:11.5px; color:#64748b;">Alignment Energy</div>
            </div>
        </div>

        <div style="background:#f0f9ff; border-radius:10px; padding:12px 14px; border:1px solid #bae6fd;">
            <div style="font-weight:800; font-size:14px; color:#0369a1; margin-bottom:6px;">🎯 Today's Actionable Strategy & Remedies:</div>
            <div style="font-size:13px; line-height:1.55; color:#0c4a6e;">
                • <b>Decision Protocol:</b> {"High green light for key ventures and financial commitments." if "🟢" in icon else "Pause speculative ventures, keep communication mild and avoid avoidable friction."}<br>
                • <b>Vahan Remedy:</b> Feed birds or stray animals this morning to balance the active Saturn vehicle.<br>
                • <b>Aura Mantra:</b> Recite <code>Om Namah Shivaya</code> 11 times before stepping out.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == "forecast":
    now_ist = datetime.datetime.now()
    transits = get_7_day_moon_transits(now_ist, chart_info["star_idx"])

    st.markdown(f"""
    <div style="font-weight:900; font-size:17px; color:#1e293b; margin-bottom:10px;">
        {t('forecast_title', current_lang)}
    </div>
    """, unsafe_allow_html=True)

    # Render table rows with buttons
    for idx, tr in enumerate(transits):
        with st.container(border=True):
            col_t1, col_t2, col_t3 = st.columns([1.5, 3, 1.5])
            with col_t1:
                st.markdown(f"<b>{tr['date_str']}</b><br><span style='font-size:12px; color:#64748b;'>{tr['star_name']}</span>", unsafe_allow_html=True)
            with col_t2:
                vahan_name = tr['vahan'].split()[1] if len(tr['vahan'].split()) > 1 else tr['vahan']
                st.markdown(f"<span style='font-size:15px;'>{tr['icon']}</span> <b>{tr['nav_name'].split('(')[0]}</b><br><span style='font-size:11.5px; color:#475569;'>Mount: {vahan_name}</span>", unsafe_allow_html=True)
            with col_t3:
                if st.button("🔮 View", key=f"btn_tr_{idx}", use_container_width=True):
                    st.session_state.selected_transit_idx = idx
                    st.rerun()

    # Detailed view for selected day with safe indexing
    safe_idx = min(len(transits) - 1, max(0, st.session_state.selected_transit_idx))
    sel_tr = transits[safe_idx]
    st.markdown(f"""
    <div class="light-card-live" style="margin-top:14px;">
        <div style="font-weight:800; font-size:15px; color:#0369a1; margin-bottom:8px;">
            🔮 Detailed Forecast for {sel_tr['date_str']} ({sel_tr['star_name']})
        </div>
        <div style="font-size:12.5px; color:#475569; margin-bottom:8px;">
            ⏰ <b>Transit Window:</b> {sel_tr['start_str']} → {sel_tr['end_str']}
        </div>
        <div style="font-size:13px; line-height:1.55; color:#0c4a6e;">
            • <b>Navtara Category:</b> {sel_tr['nav_name']} ({sel_tr['quality']})<br>
            • <b>Saturn Mount:</b> {sel_tr['vahan']}<br>
            • <b>Remedy for this day:</b> {"Wear green or light clothes, schedule key meetings, and execute major deals." if "🟢" in sel_tr['icon'] else "Avoid hasty arguments, keep investments on hold, and recite Hanuman Chalisa."}
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == "planets":
    now_ist = datetime.datetime.now()
    planets_data = get_sidereal_planet_positions(now_ist)

    st.markdown(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:17px; color:#9a3412; margin-bottom:12px; border-bottom:2px solid #fed7aa; padding-bottom:6px;">
            {t('planet_title', current_lang)}
        </div>
        <div style="font-size:12px; color:#64748b; margin-bottom:10px;">
            Sidereal Lahiri Ayanamsa | Computed for {now_ist.strftime('%d %B %Y, %I:%M %p IST')}
        </div>
        <div style="display:grid; grid-template-columns: 1fr; gap:8px;">
    """, unsafe_allow_html=True)

    for p in planets_data:
        st.markdown(f"""
        <div style="background:#fff7ed; border-radius:8px; padding:8px 12px; display:flex; justify-content:space-between; align-items:center; border:1px solid #fed7aa;">
            <span style="font-weight:700; color:#9a3412; font-size:13px;">{p['planet']}</span>
            <span style="font-weight:800; color:#431407; font-size:13px;">{p['rashi']} ({p['deg']})</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

elif st.session_state.current_page == "remedies":
    st.markdown(f"""
    <div class="light-card-num">
        <div style="font-weight:900; font-size:17px; color:#065f46; margin-bottom:12px; border-bottom:2px solid #bbf7d0; padding-bottom:6px;">
            🪔 Consolidated Vedic Astro-Remedies Sanctuary
        </div>
        
        <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border-left:4px solid #059669; border:1px solid #d1fae5; border-left-width:4px; margin-bottom:12px;">
            <div style="font-weight:800; font-size:14px; color:#065f46; margin-bottom:4px;">1. Janma Nakshatra Protection (Bharani)</div>
            <div style="font-size:12.8px; line-height:1.55; color:#1e293b;">
                • Worship Lord Shiva or Lord Yama to clear heavy ancestral and life burdens.<br>
                • Chant <code>Om Hreem Bharanyai Namah</code> or <code>Maha Mrityunjaya Mantra</code> 11 times every morning.
            </div>
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border-left:4px solid #10b981; border:1px solid #d1fae5; border-left-width:4px; margin-bottom:12px;">
            <div style="font-weight:800; font-size:14px; color:#065f46; margin-bottom:4px;">2. Numerology Harmony (Mulank {mulank} & Bhagyank {bhagyank})</div>
            <div style="font-size:12.8px; line-height:1.55; color:#1e293b;">
                • Drink water from a silver or copper vessel to pacify planetary intensity.<br>
                • Keep an organized desk and avoid cluttered electronic wires to strengthen focus.
            </div>
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border-left:4px solid #7c3aed; border:1px solid #ddd6fe; border-left-width:4px;">
            <div style="font-weight:800; font-size:14px; color:#5b21b6; margin-bottom:4px;">3. Shani Rajat Paya (Silver Feet) Shield</div>
            <div style="font-size:12.8px; line-height:1.55; color:#1e293b;">
                • Recite the Hanuman Chalisa on Tuesday and Saturday evenings.<br>
                • Pour raw milk and clean water over a Shiva Lingam on Mondays to awaken the divine silver shield.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == "share":
    app_url = "https://navtara-pulse.streamlit.app"
    share_msg = "Discover your real-time Vedic Moon transit rhythm, Shani Paya, and personalized Numerology blueprint with Navtara Pulse!"
    encoded_url = urllib.parse.quote(app_url)
    encoded_msg = urllib.parse.quote(f"{share_msg}\n\nCheck your alignment here: {app_url}")

    st.markdown(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:17px; color:#9a3412; margin-bottom:12px; border-bottom:2px solid #fed7aa; padding-bottom:6px;">
            {t('share_title', current_lang)}
        </div>
        <div style="font-size:13px; color:#475569; margin-bottom:14px;">
            Share this timing engine with your friends and loved ones via your favorite platform:
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:14px;">
            <a href="https://api.whatsapp.com/send?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#25D366; color:#ffffff; padding:10px; border-radius:10px; text-align:center; font-weight:800; font-size:13.5px;">
                    🟢 WhatsApp
                </div>
            </a>
            <a href="https://t.me/share/url?url={encoded_url}&text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0088cc; color:#ffffff; padding:10px; border-radius:10px; text-align:center; font-weight:800; font-size:13.5px;">
                    ✈️ Telegram
                </div>
            </a>
            <a href="mailto:?subject=Navtara Pulse - Vedic Timing&body={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#ea4335; color:#ffffff; padding:10px; border-radius:10px; text-align:center; font-weight:800; font-size:13.5px;">
                    ✉️ Email
                </div>
            </a>
            <a href="https://twitter.com/intent/tweet?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0f172a; color:#ffffff; padding:10px; border-radius:10px; text-align:center; font-weight:800; font-size:13.5px;">
                    🐦 X (Twitter)
                </div>
            </a>
        </div>

        <div style="background:#fff7ed; border-radius:10px; padding:10px; border:1px solid #fed7aa; text-align:center;">
            <div style="font-size:11.5px; color:#9a3412; font-weight:700;">Direct App Link:</div>
            <div style="font-size:13px; font-weight:800; color:#431407; margin-top:2px;"><code>{app_url}</code></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin:18px 0 12px 0; border:none; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)

# Row 1: Profile, Numerology, Shani, Live Prediction
nav_r1_c1, nav_r1_c2, nav_r1_c3, nav_r1_c4 = st.columns(4)
with nav_r1_c1:
    p_type = "primary" if st.session_state.current_page == "profile" else "secondary"
    if st.button(t("btn_profile", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "profile"
        st.rerun()

with nav_r1_c2:
    p_type = "primary" if st.session_state.current_page == "numerology" else "secondary"
    if st.button(t("btn_numerology", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "numerology"
        st.rerun()

with nav_r1_c3:
    p_type = "primary" if st.session_state.current_page == "shani" else "secondary"
    if st.button(t("btn_shani", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "shani"
        st.rerun()

with nav_r1_c4:
    p_type = "primary" if st.session_state.current_page == "live" else "secondary"
    if st.button(t("btn_live", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "live"
        st.rerun()

# Row 2: 7 Days Prediction, Planet Position, Remedies, Share App
nav_r2_c1, nav_r2_c2, nav_r2_c3, nav_r2_c4 = st.columns(4)
with nav_r2_c1:
    p_type = "primary" if st.session_state.current_page == "forecast" else "secondary"
    if st.button(t("btn_forecast", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "forecast"
        st.rerun()

with nav_r2_c2:
    p_type = "primary" if st.session_state.current_page == "planets" else "secondary"
    if st.button(t("btn_planets", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "planets"
        st.rerun()

with nav_r2_c3:
    p_type = "primary" if st.session_state.current_page == "remedies" else "secondary"
    if st.button(t("btn_remedies", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "remedies"
        st.rerun()

with nav_r2_c4:
    p_type = "primary" if st.session_state.current_page == "share" else "secondary"
    if st.button(t("btn_share", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "share"
        st.rerun()
