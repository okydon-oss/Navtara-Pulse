import os
import json
import datetime
import streamlit as st

# Swiss Ephemeris astronomical calculation library
try:
    import swisseph as swe
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False
    st.error("🚨 Missing Library: `pyswisseph` is not installed. Please add `pyswisseph` to `requirements.txt`.")
    st.stop()

st.set_page_config(
    page_title="Navtara Pulse",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 0.9rem !important;
        padding-right: 0.9rem !important;
        max-width: 740px !important;
        margin: 0 auto !important;
    }
    
    .top-lang-bar {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 8px 12px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .hero-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        color: #ffffff;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 14px rgba(30, 27, 75, 0.15);
    }

    .profile-card {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }

    .paya-banner {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1.5px solid #86efac;
        border-radius: 12px;
        padding: 14px;
        margin-top: 10px;
        color: #14532d;
    }

    .num-banner {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 1.5px solid #93c5fd;
        border-radius: 12px;
        padding: 12px;
        margin-top: 10px;
        color: #1e3a8a;
    }

    .active-live-card {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1.5px solid #fde68a;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 3px 10px rgba(245, 158, 11, 0.08);
    }

    .remedy-box {
        background: #ffffff;
        border: 1.2px solid #fcd34d;
        border-radius: 10px;
        padding: 12px;
        margin-top: 10px;
    }

    .badge-danger { background: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 6px; font-weight: 700; }
    .badge-favorable { background: #dcfce7; color: #166534; padding: 3px 8px; border-radius: 6px; font-weight: 700; }
    .badge-neutral { background: #f1f5f9; color: #334155; padding: 3px 8px; border-radius: 6px; font-weight: 700; }

    .stButton > button {
        min-height: 46px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "mr": "मराठी (Marathi)",
    "gu": "ગુજરાતી (Gujarati)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)",
    "kn": "ಕನ್ನಡ (Kannada)",
    "bn": "বাংলা (Bengali)",
    "es": "Español (Spanish)",
    "fr": "Français (French)",
    "de": "Deutsch (German)"
}

TRANSLATIONS = {
    "en": {
        "title": "✨ Navtara Pulse",
        "tagline": "Real-time Cosmic Timing • Shani Charan & Vahan • Numerology Synthesis",
        "select_lang": "🌐 Select Language / भाषा चुनें",
        "profile_heading": "👤 Native Profile & Astrological Foundation",
        "native": "Native Name",
        "janma_nak": "Janma Nakshatra",
        "moon_sign": "Moon Sign (Janma Rashi)",
        "shani_paya_title": "🪐 Ongoing Shani Paya (Foundational Charan)",
        "transit_period": "Current Transit Timeline",
        "paya_desc_title": "Paya Interpretation & Life Impact",
        "paya_remedy_title": "🪔 Shani Paya Protective Remedies",
        "num_profile_title": "🔢 Core Numerology Blueprint",
        "mulank": "Mulank (Driver)",
        "bhagyank": "Bhagyank (Conductor)",
        "namank": "Namank (Name)",
        "live_synthesis_head": "🔮 Active Cosmic Synthesis & Directives for Today",
        "active_tara": "Current Active Navtara",
        "active_moon_star": "Moon Ingress Star",
        "active_timing": "Active Window",
        "active_vahan": "Today's Shani Vahan",
        "active_pday": "Today's Personal Day",
        "integrated_predictions": "🎯 Integrated Astrological Predictions for Today",
        "todays_remedies": "🪔 Prescribed Daily Multi-Layer Remedies",
        "tab_matrix": "🗓️ 7-Day Moon Transition & Daily Forecast",
        "tab_shani": "🪐 Shani Charan & Vahan Guide",
        "tab_numerology": "🔢 Numerology Engine",
        "tab_planets": "🌌 Planetary Positions",
        "day_forecast_expander": "View Daily Forecast & Prescribed Remedies",
        "col_status": "Status",
        "col_time": "Window (IST)",
        "col_nak": "Moon Star",
        "col_navtara": "Navtara Series",
        "save_profile": "💾 Save Profile",
        "profile_saved": "✅ Profile updated successfully!",
        "sidebar_head": "⚙️ Update Birth Profile"
    },
    "hi": {
        "title": "✨ नवतारा पल्स (Navtara Pulse)",
        "tagline": "सटीक काल निर्णय • शनि चरण व वाहन • अंक ज्योतिष समन्वय",
        "select_lang": "🌐 भाषा चुनें (Select Language)",
        "profile_heading": "👤 जातक जन्म विवरण एवं ज्योतिषीय आधार",
        "native": "जातक का नाम",
        "janma_nak": "जन्म नक्षत्र",
        "moon_sign": "चन्द्र राशि",
        "shani_paya_title": "🪐 वर्तमान शनि पाया (चरण फल)",
        "transit_period": "गोचर समयावधि (Timeline)",
        "paya_desc_title": "शनि पाया प्रभाव एवं फल",
        "paya_remedy_title": "🪔 शनि पाया सुरक्षा उपाय",
        "num_profile_title": "🔢 मूल अंक ज्योतिष रूपरेखा",
        "mulank": "मूलांक (स्वभाव)",
        "bhagyank": "भाग्यांक (भाग्य)",
        "namank": "नामांक (पहचान)",
        "live_synthesis_head": "🔮 आज का सक्रिय ब्रह्मांडीय फलादेश एवं निर्देश",
        "active_tara": "सक्रिय नवतारा",
        "active_moon_star": "गोचर चन्द्र नक्षत्र",
        "active_timing": "सक्रिय समय",
        "active_vahan": "आज का शनि वाहन",
        "active_pday": "व्यक्तिगत दिन अंक",
        "integrated_predictions": "🎯 आज का समग्र त्रिकोणीय फलादेश",
        "todays_remedies": "🪔 आज के त्रि-स्तरीय वैदिक उपाय",
        "tab_matrix": "🗓️ 7-दिवसीय चन्द्र गोचर व दैनिक भविष्य",
        "tab_shani": "🪐 शनि चरण व वाहन संदर्शिका",
        "tab_numerology": "🔢 अंक ज्योतिष चक्र",
        "tab_planets": "🌌 ग्रह स्थिति (लाहिड़ी)",
        "day_forecast_expander": "आज का विस्तृत फलादेश एवं उपाय देखें",
        "col_status": "स्थिति",
        "col_time": "समयावधि (IST)",
        "col_nak": "चन्द्र नक्षत्र",
        "col_navtara": "नवतारा श्रृंखला",
        "save_profile": "💾 प्रोफ़ाइल सुरक्षित करें",
        "profile_saved": "✅ प्रोफ़ाइल सफलतापूर्वक सुरक्षित हुई!",
        "sidebar_head": "⚙️ जन्म विवरण सम्पादित करें"
    },
    "mr": {
        "title": "✨ नवतारा पल्स (Navtara Pulse)",
        "tagline": "अचूक काल निर्णय • शनी चरण व वाहन • अंकशास्त्र समन्वय",
        "select_lang": "🌐 भाषा निवडा (Language)",
        "profile_heading": "👤 जातक जन्म कुंडली व ज्योतिषीय पाया",
        "native": "जातकाचे नाव",
        "janma_nak": "जन्म नक्षत्र",
        "moon_sign": "चंद्र राशी",
        "shani_paya_title": "🪐 सध्याचा शनीचा पाया (चरण प्रभाव)",
        "transit_period": "गोचर कालमर्यादा (Timeline)",
        "paya_desc_title": "पाया प्रभाव व फळ",
        "paya_remedy_title": "🪔 शनी पाया शांतता उपाय",
        "num_profile_title": "🔢 अंकशास्त्र रूपरेषा",
        "mulank": "मूलांक",
        "bhagyank": "भाग्यांक",
        "namank": "नामांक",
        "live_synthesis_head": "🔮 आजचे सक्रिय वैश्विक भविष्य व उपाय",
        "active_tara": "सद्य नवतारा",
        "active_moon_star": "गोचर चंद्र नक्षत्र",
        "active_timing": "सक्रिय वेळ",
        "active_vahan": "आजचे शनी वाहन",
        "active_pday": "वैयक्तिक दिवस अंक",
        "integrated_predictions": "🎯 आजच्या धोरणात्मक भविष्य सूचना",
        "todays_remedies": "🪔 आजचे अनुशंसित त्रि-स्तरीय उपाय",
        "tab_matrix": "🗓️ ७-दिवसीय चंद्र गोचर व दैनंदिन भविष्य",
        "tab_shani": "🪐 शनी चरण व वाहन माहिती",
        "tab_numerology": "🔢 अंकशास्त्र विश्लेषण",
        "tab_planets": "🌌 ग्रह स्थिती",
        "day_forecast_expander": "या दिवसाचे फलादेश व उपाय पहा",
        "col_status": "स्थिती",
        "col_time": "कालावधी (IST)",
        "col_nak": "चंद्र नक्षत्र",
        "col_navtara": "नवतारा मालिका",
        "save_profile": "💾 माहिती सेव्ह करा",
        "profile_saved": "✅ माहिती सेव्ह झाली!",
        "sidebar_head": "⚙️ जन्म तपशील बदला"
    },
    "gu": {
        "title": "✨ નવતારા પલ્સ (Navtara Pulse)",
        "tagline": "સચોટ સમય નિર્ણય • શનિ ચરણ અને વાહન • અંક જ્યોતિષ",
        "select_lang": "🌐 ભાષા પસંદ કરો (Language)",
        "profile_heading": "👤 જાતક જન્મ વિગતો અને જ્યોતિષીય પાયો",
        "native": "જાતકનું નામ",
        "janma_nak": "જન્મ નક્ષત્ર",
        "moon_sign": "ચંદ્ર રાશિ",
        "shani_paya_title": "🪐 વર્તમાન શનિ પાયા (ચરણ ફળ)",
        "transit_period": "ગોચર સમયગાળો (Timeline)",
        "paya_desc_title": "પાયા પ્રભાવ અને ફળ",
        "paya_remedy_title": "🪔 શનિ પાયા શાંતિ ઉપાય",
        "num_profile_title": "🔢 અંકશાસ્ત્ર રૂપરેખા",
        "mulank": "મૂળાંક",
        "bhagyank": "ભાગ્યાંક",
        "namank": "નામાંક",
        "live_synthesis_head": "🔮 આજનું સક્રિય ભવિષ્ય અને માર્ગદર્શન",
        "active_tara": "સક્રિય નવતારા",
        "active_moon_star": "ગોચર ચંદ્ર નક્ષત્ર",
        "active_timing": "સક્રિય સમય",
        "active_vahan": "આજનું શનિ વાહન",
        "active_pday": "વ્યક્તિગત દિવસ અંક",
        "integrated_predictions": "🎯 આજનું ત્રિકોણીય ભવિષ્ય વિશ્લેષણ",
        "todays_remedies": "🪔 આજ માટે વિશેષ ઉપાયો",
        "tab_matrix": "🗓️ ૭-દિવસીય ચંદ્ર ગોચર અને દૈનિક ભવિષ્ય",
        "tab_shani": "🪐 શનિ ચરણ અને વાહન માર્ગદર્શિકા",
        "tab_numerology": "🔢 અંકશાસ્ત્ર ચક્ર",
        "tab_planets": "🌌 ગ્રહ સ્થિતિ",
        "day_forecast_expander": "આ દિવસનું ભવિષ્ય અને ઉપાય જુઓ",
        "col_status": "સ્થિતિ",
        "col_time": "સમયગાળો (IST)",
        "col_nak": "ચંદ્ર નક્ષત્ર",
        "col_navtara": "નવતારા શ્રેણી",
        "save_profile": "💾 પ્રોફાઇલ સાચવો",
        "profile_saved": "✅ પ્રોફાઇલ સાચવવામાં આવી!",
        "sidebar_head": "⚙️ જન્મ વિગતો સુધારો"
    }
}

def t(key: str, lang: str = "en") -> str:
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

NAVTARA_NAMES = [
    "Janma", "Sampat", "Vipat", "Kshema", "Pratyari",
    "Sadhana", "Vadha", "Mitra", "Ati-Mitra"
]

NAVTARA_DESCRIPTIONS = {
    "en": {
        "Janma": "Self / Physical Vitality / Grounding & New Beginnings",
        "Sampat": "Wealth / Material Expansion / Positive Financial Inflows",
        "Vipat": "Obstacles / High Friction / High-risk Caution Required",
        "Kshema": "Well-being / Comfort / Protection & Easy Progress",
        "Pratyari": "Resistance / Confrontations / Diplomatic Restraint Needed",
        "Sadhana": "Achievement / Focused Productivity / Milestone Success",
        "Vadha": "Destruction / High Vulnerability / Complete Postponement",
        "Mitra": "Friendship / Collaborative Harmony / Beneficial Help",
        "Ati-Mitra": "Supreme Support / Peak Auspicious Opportunity"
    },
    "hi": {
        "Janma": "स्व / शारीरिक स्वास्थ्य / नई शुरुआत एवं संतुलन",
        "Sampat": "धन / आर्थिक विस्तार / भौतिक लाभ एवं समृद्धि",
        "Vipat": "बाधाएं / अप्रत्याशित जोखिम / अत्यधिक सावधानी का समय",
        "Kshema": "कल्याण / सुख-शांति / सुरक्षा एवं स्वास्थ्य लाभ",
        "Pratyari": "विरोध / मतभेद / वाद-विवाद से दूर रहने का समय",
        "Sadhana": "सिद्धि / लक्ष्य प्राप्ति / कार्य में पूर्ण सफलता",
        "Vadha": "हानि / संवेदनशीलता / पूर्ण संयम एवं शांति आवश्यक",
        "Mitra": "मित्रता / सौहार्दपूर्ण सहयोग / शुभ संपर्क",
        "Ati-Mitra": "अति शुभ / परम सहयोग / महत्वपूर्ण निर्णयों के लिए श्रेष्ठ"
    },
    "mr": {
        "Janma": "स्व / शारीरिक स्वास्थ्य / नवीन सुरुवात व समतोल",
        "Sampat": "संपत्ती / आर्थिक प्रगती / लाभ व ऐश्वर्य",
        "Vipat": "अडचणी / संकट / अनपेक्षित चढ-उतार (सावध राहा)",
        "Kshema": "कल्याण / सुख-समाधान / सुरक्षा व आरोग्य लाभ",
        "Pratyari": "विरोध / मतभेद / वादापासून दूर राहण्याची गरज",
        "Sadhana": "साधना / उद्दिष्ट पूर्ती / कामात मोठे यश",
        "Vadha": "नुकसान / संवेदनशीलता / पूर्ण संयम बाळगा",
        "Mitra": "मित्रत्व / अनुकूल सहकार्य / शुभ संबंध",
        "Ati-Mitra": "अति शुभ / सर्वोच्च सहकार्य / महत्त्वाच्या निर्णयांसाठी उत्तम"
    },
    "gu": {
        "Janma": "સ્વ / શારીરિક સ્વાસ્થ્ય / નવી શરૂઆત અને સંતુલન",
        "Sampat": "ધન / આર્થિક પ્રગતિ / લાભ અને સમૃદ્ધિ",
        "Vipat": "અડચણો / જોખમ / સાવધાની રાખવાનો સમય",
        "Kshema": "કલ્યાણ / સુખ-શાંતિ / સુરક્ષા અને સ્વાસ્થ્ય લાભ",
        "Pratyari": "વિરોધ / મતભેદ / વિવાદોથી દૂર રહેવાની જરૂર",
        "Sadhana": "સાધના / સિદ્ધિ / કાર્યમાં ઉત્કૃષ્ટ સફળતા",
        "Vadha": "હાનિ / સંવેદનશીલતા / શાંતિ અને સંયમ જરૂરી",
        "Mitra": "મિત્રતા / સાનુકૂળ સહયોગ / શુભ સંબંધો",
        "Ati-Mitra": "અતિ શુભ / ઉત્તમ સહયોગ / મહત્વના કાર્યો માટે શ્રેષ્ઠ"
    }
}

SHANI_VAHANS = {
    1: {"name": "Ghoda (Horse) 🐴", "nature": "Speed & Quick Victory", "desc": "Swift movement, high stamina, triumph over rivals, and fast closure of pending tasks."},
    2: {"name": "Gadha (Donkey) 🫏", "nature": "Heavy Labor & Fatigue", "desc": "High physical and mental workload with delayed applause. Requires continuous patience and pacing."},
    3: {"name": "Siyar (Jackal) 🦊", "nature": "Vigilance & Risk Alert", "desc": "Alertness required against deceptive terms, speculation, or hidden office politics."},
    4: {"name": "Hathi (Elephant) 🐘", "nature": "Royalty & Prosperity", "desc": "Prestige, unexpected recognition, material comfort, luxury gains, and supportive superiors."},
    5: {"name": "Bail (Bull) 🐂", "nature": "Steady Persistence", "desc": "Gradual, rock-solid gains achieved through methodical discipline and structured effort."},
    6: {"name": "Sher (Lion) 🦁", "nature": "Power & Decisive Courage", "desc": "Commanding executive presence, success in competitive debates, legal or contractual triumphs."},
    7: {"name": "Kowwa (Crow) 🐦‍⬛", "nature": "Restlessness & Wander", "desc": "Scattered focus, restlessness, domestic irritation, or frequent travel. Cultivate silence."},
    8: {"name": "Mayur (Peacock) 🦚", "nature": "Joy & Aesthetic Warmth", "desc": "Delightful meetings, artistic breakthroughs, heartwarming social interactions, and warmth."},
    9: {"name": "Hans (Swan) 🦢", "nature": "Wisdom & Deep Peace", "desc": "Serene intuition, highest mental clarity, spiritual discernment, and sound financial strategy."}
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

PROFILE_FILE = "user_profile.json"

def load_user_profile() -> dict:
    defaults = {
        "name": "Okesh",
        "dob": datetime.date(1984, 1, 13),
        "tob": datetime.time(14, 0),
        "place": "Chhatrapati Sambhajinagar, India",
        "lat": 19.8762,
        "lon": 75.3433,
        "tz_offset": 5.5,
        "nakshatra_idx": 1,  # Bharani (#2)
        "language": "en"
    }
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                saved = json.load(f)
                if "dob" in saved and isinstance(saved["dob"], str):
                    saved["dob"] = datetime.date.fromisoformat(saved["dob"])
                if "tob" in saved and isinstance(saved["tob"], str):
                    saved["tob"] = datetime.time.fromisoformat(saved["tob"])
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_user_profile(profile_data: dict) -> bool:
    try:
        to_store = profile_data.copy()
        if isinstance(to_store.get("dob"), (datetime.date, datetime.datetime)):
            to_store["dob"] = to_store["dob"].isoformat()
        if isinstance(to_store.get("tob"), datetime.time):
            to_store["tob"] = to_store["tob"].isoformat()
        with open(PROFILE_FILE, "w") as f:
            json.dump(to_store, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return False

def dt_to_jd(utc_dt: datetime.datetime) -> float:
    hour_dec = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0 + (utc_dt.microsecond / 1e6) / 3600.0
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)

def get_sidereal_lon(jd_ut: float, planet_id: int) -> float:
    res, _ = swe.calc_ut(jd_ut, planet_id, swe.FLG_MOSEPH)
    trop_lon = res[0]
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    return (trop_lon - ayanamsa) % 360.0

def lon_to_nakshatra(lon: float):
    nak_span = 360.0 / 27.0
    idx = int(lon / nak_span) % 27
    pada = int((lon % nak_span) / (nak_span / 4.0)) + 1
    return idx, pada

def lon_to_rashi(lon: float):
    return int(lon / 30.0) % 12, lon % 30.0

def calculate_navtara(birth_idx: int, transit_idx: int):
    offset = (transit_idx - birth_idx) % 27
    return NAVTARA_NAMES[offset % 9], (offset // 9) + 1

def calculate_shani_paya(moon_rashi_idx: int, saturn_rashi_idx: int, lang: str = "en"):
    house_pos = ((moon_rashi_idx - saturn_rashi_idx) % 12) + 1
    transit_timeline = "29 March 2025 – 23 February 2028 (Meena / Pisces Transit)"
    
    if house_pos in [2, 5, 9]:
        paya_name = "Rajat Paya (Silver Feet / चाँदी का पाया) 🥈"
        grade = "Most Auspicious & Highly Protective (अति शुभ)"
        desc = ("Saturn arrives bearing silver gifts. For Aries Moon natives navigating Sade Sati phase 1, "
                "this Silver Paya acts as a celestial shock absorber. It shields finances, expands family happiness, "
                "clears past debts, and ensures steady support from mentors.")
        remedies = [
            "Wear a pure silver ring or keep a small square piece of silver in your wallet.",
            "Offer fresh milk mixed with water and white sesame seeds to a Shiva Lingam on Mondays.",
            "Respect domestic helpers, service workers, and maintain strict integrity in all agreements."
        ]
        return paya_name, grade, desc, remedies, transit_timeline
    elif house_pos in [3, 7, 10]:
        paya_name = "Tamra Paya (Copper Feet / तांबे का पाया) 🥉"
        grade = "Favorable & Progressive (शुभ फलदायी)"
        desc = ("Saturn awards consistent rewards for disciplined effort. Promotes stamina, career ascension, "
                "healthy business deals, and reliable physical vigor.")
        remedies = [
            "Offer clean water from a copper vessel (Arghya) to the morning rising Sun.",
            "Donate whole wheat or copper utensils to workers or underprivileged individuals.",
            "Maintain consistent daily physical exercise to honor Saturn's call for disciplined strength."
        ]
        return paya_name, grade, desc, remedies, transit_timeline
    elif house_pos in [1, 6, 11]:
        paya_name = "Swarna Paya (Gold Feet / सोने का पाया) 🥇"
        grade = "Challenging / Test of Humility (मध्यम व व्ययकारक)"
        desc = ("Though gold represents wealth, Saturn walking on gold feet tests ego and humility. "
                "Money turnover is high; caution is needed against impulsive investments or pride-driven clashes.")
        remedies = [
            "Feed black dogs or stray animals on Saturdays with bread coated in mustard oil.",
            "Avoid speculative gambling, lottery, or quick-return schemes.",
            "Recite Dasharatha Shani Stotra on Saturday evenings after sunset."
        ]
        return paya_name, grade, desc, remedies, transit_timeline
    else:  # 4, 8, 12
        paya_name = "Loha Paya (Iron Feet / लोहे का पाया) 🪙"
        grade = "Demanding / High Caution & Labor (कठिन व श्रमसाध्य)"
        desc = ("Indicates karmic scrutiny, heavy workload, and joint or fatigue sensitivity. Teaches "
                "resilience and patience. Shortcuts must be strictly avoided.")
        remedies = [
            "Light a mustard oil diya near a Peepal tree every Saturday evening.",
            "Recite the Hanuman Chalisa twice daily to ignite courage and dissolve mental fatigue.",
            "Donate black sesame seeds, iron pans (Tawa), or black umbrellas to laborers."
        ]
        return paya_name, grade, desc, remedies, transit_timeline

def calculate_shani_vahan(birth_nak_1based: int, transit_moon_nak_1based: int):
    rem = ((birth_nak_1based * 4) + transit_moon_nak_1based) % 9
    rem = 9 if rem == 0 else rem
    return rem, SHANI_VAHANS[rem]

def reduce_single_digit(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

def calculate_numerology(dob: datetime.date, name: str):
    mulank = reduce_single_digit(dob.day)
    total_dob = dob.day + dob.month + dob.year
    bhagyank = reduce_single_digit(total_dob)
    clean_name = "".join(ch for ch in name.upper() if ch.isalpha())
    name_sum = sum(CHALDEAN_MAP.get(ch, 0) for ch in clean_name)
    namank = reduce_single_digit(name_sum) if name_sum > 0 else 1
    return mulank, bhagyank, namank

def get_personal_day_vibe(mulank: int, target_date: datetime.date):
    day_sum = target_date.day + target_date.month + target_date.year
    universal_day = reduce_single_digit(day_sum)
    personal_day = reduce_single_digit(mulank + universal_day)
    
    vibe_map = {
        1: ("Leadership & Decisive Action", "Ideal for launching plans, asserting self-confidence, and signing off on direct initiatives.", "Wear shades of red or gold; chant the Gayatri Mantra 11 times."),
        2: ("Diplomacy & Harmonious Listening", "Favor teamwork, quiet negotiations, emotional balance, and attentive listening.", "Drink water from a silver cup; practice 5 minutes of mindful meditation."),
        3: ("Creative Expression & Social Flow", "Excellent for brainstorming, persuasive communication, writing, and client meetings.", "Apply a small saffron or sandalwood tilak; share knowledge with others."),
        4: ("Discipline & Structural Grounding", "Focus on structured execution, organizing paperwork, maintenance, and detailed follow-through.", "Avoid rushing; feed birds with mixed millet or whole grains."),
        5: ("Flexibility & Quick Problem-Solving", "Expect quick changes in tempo. Good for networking, sales, and agile problem solving.", "Wear light green; donate green gram (Moong) or green vegetables."),
        6: ("Responsibility & Domestic Warmth", "Nurture domestic relationships, assist colleagues, and focus on health harmony.", "Keep a pleasant fragrance or perfume; express appreciation to your partner/family."),
        7: ("Deep Introspection & Analytical Audit", "Avoid noisy debates. Ideal for research, spiritual contemplation, and analytical audits.", "Spend 15 minutes in silent contemplation; avoid impulsive financial speculation."),
        8: ("Authority & Financial Prudence", "Handle monetary decisions, contracts, and long-range business planning with discipline.", "Recite 'Om Sham Shanicharaya Namah' 21 times; avoid arrogance with subordinates."),
        9: ("Completion & Graceful Detachment", "Wrap up pending items, release past friction, forgive misunderstandings, and prepare for new cycles.", "Donate old clothes or food to someone in need; clear physical clutter.")
    }
    title, desc, remedy = vibe_map.get(personal_day, ("Balanced Awareness", "Proceed with standard mindfulness.", "Maintain peaceful balance."))
    return universal_day, personal_day, title, desc, remedy

def find_7day_transitions(start_utc_dt: datetime.datetime):
    nak_span = 360.0 / 27.0
    transitions = []
    current_time = start_utc_dt
    end_time = start_utc_dt + datetime.timedelta(days=7)

    cur_lon = get_sidereal_lon(dt_to_jd(current_time), swe.MOON)
    active_nak = int(cur_lon / nak_span) % 27
    interval_start = current_time

    step = datetime.timedelta(minutes=30)
    eval_time = current_time

    while eval_time <= end_time:
        eval_time += step
        lon = get_sidereal_lon(dt_to_jd(eval_time), swe.MOON)
        nak = int(lon / nak_span) % 27

        if nak != active_nak:
            low, high = eval_time - step, eval_time
            for _ in range(7):
                mid = low + (high - low) / 2
                mid_lon = get_sidereal_lon(dt_to_jd(mid), swe.MOON)
                if int(mid_lon / nak_span) % 27 == active_nak:
                    low = mid
                else:
                    high = mid
            boundary = high
            transitions.append({
                "nak_idx": active_nak,
                "start": interval_start,
                "end": boundary
            })
            interval_start = boundary
            active_nak = nak

    transitions.append({
        "nak_idx": active_nak,
        "start": interval_start,
        "end": end_time
    })
    return transitions

if "profile" not in st.session_state:
    st.session_state.profile = load_user_profile()

prof = st.session_state.profile
current_lang = prof.get("language", "en")

st.markdown(f"""
<div class="top-lang-bar">
    <div style="font-weight: 700; color: #1e1b4b; font-size: 14.5px;">
        ✨ <b>Navtara Pulse Engine</b>
    </div>
    <div style="font-size: 13.5px; color: #64748b;">
        {t("select_lang", current_lang)}
    </div>
</div>
""", unsafe_allow_html=True)

lang_codes = list(SUPPORTED_LANGUAGES.keys())
lang_labels = list(SUPPORTED_LANGUAGES.values())
curr_lang_idx = lang_codes.index(current_lang) if current_lang in lang_codes else 0

col_lang_left, col_lang_right = st.columns([1, 2])
with col_lang_left:
    st.markdown(f"**{t('select_lang', current_lang)}:**")
with col_lang_right:
    selected_lang_label = st.selectbox(
        "App Language",
        lang_labels,
        index=curr_lang_idx,
        label_visibility="collapsed"
    )
    selected_lang_code = lang_codes[lang_labels.index(selected_lang_label)]

    if selected_lang_code != current_lang:
        prof["language"] = selected_lang_code
        st.session_state.profile = prof
        save_user_profile(prof)
        st.rerun()

janma_idx = prof.get("nakshatra_idx", 1)  # Bharani
janma_name = NAKSHATRAS[janma_idx]
user_dob = prof.get("dob", datetime.date(1984, 1, 13))
user_name = prof.get("name", "Okesh")
user_place = prof.get("place", "Chhatrapati Sambhajinagar, India")

mulank, bhagyank, namank = calculate_numerology(user_dob, user_name)

now_utc = datetime.datetime.now(datetime.timezone.utc)
ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
now_ist = now_utc.astimezone(ist_tz)
jd_now = dt_to_jd(now_utc)

saturn_lon = get_sidereal_lon(jd_now, swe.SATURN)
saturn_rashi_idx, _ = lon_to_rashi(saturn_lon)
moon_lon = get_sidereal_lon(jd_now, swe.MOON)
cur_moon_rashi_idx, _ = lon_to_rashi(moon_lon)
cur_moon_nak_idx, _ = lon_to_nakshatra(moon_lon)

natal_moon_rashi_idx = int((janma_idx * (360.0 / 27.0)) / 30.0) % 12

paya_name, paya_status, paya_desc, paya_remedies, paya_timeline = calculate_shani_paya(natal_moon_rashi_idx, saturn_rashi_idx, current_lang)
today_vahan_num, today_vahan = calculate_shani_vahan(janma_idx + 1, cur_moon_nak_idx + 1)
cur_nav_cat, cur_nav_series = calculate_navtara(janma_idx, cur_moon_nak_idx)
u_day, p_day, p_title, p_desc, num_remedy = get_personal_day_vibe(mulank, now_ist.date())

st.markdown(f"""
<div class="hero-box">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h2 style="margin:0; font-size:1.45rem; font-weight:800; color:#ffffff;">{user_name}</h2>
            <div style="font-size:13.5px; color:#cbd5e1; margin-top:2px;">📍 {user_place} | 🎂 {user_dob.strftime('%d %B %Y')}</div>
        </div>
        <div style="text-align:right;">
            <span style="background:#4338ca; padding:4px 10px; border-radius:8px; font-weight:700; font-size:13px;">
                {RASHIS[natal_moon_rashi_idx].split(' ')[0]} Rashi
            </span>
        </div>
    </div>
    <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
        <span style="background:rgba(255,255,255,0.12); padding:4px 9px; border-radius:7px; font-size:12.5px;">
            🌟 <b>Janma Star:</b> {janma_name} (#{janma_idx+1})
        </span>
        <span style="background:rgba(255,255,255,0.12); padding:4px 9px; border-radius:7px; font-size:12.5px;">
            🪐 <b>Saturn Transit:</b> {RASHIS[saturn_rashi_idx].split(' ')[0]}
        </span>
        <span style="background:rgba(255,255,255,0.12); padding:4px 9px; border-radius:7px; font-size:12.5px;">
            🔢 <b>Driver / Conductor:</b> {mulank} / {bhagyank}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander(f"🪐 {t('shani_paya_title', current_lang)}: {paya_name}", expanded=True):
    st.markdown(f"""
    <div class="paya-banner">
        <div style="font-weight:800; font-size:15px; margin-bottom:4px;">
            {paya_name} — <span style="text-decoration: underline;">{paya_status}</span>
        </div>
        <div style="font-size:13px; font-weight:600; margin-bottom:8px;">
            ⏳ <b>{t('transit_period', current_lang)}:</b> {paya_timeline}
        </div>
        <div style="font-size:13.5px; line-height:1.5;">
            {paya_desc}
        </div>
        <div style="margin-top:10px; font-weight:700; font-size:13.5px;">
            {t('paya_remedy_title', current_lang)}:
        </div>
    </div>
    """, unsafe_allow_html=True)
    for r in paya_remedies:
        st.markdown(f"• {r}")

with st.expander(f"🔢 {t('num_profile_title', current_lang)}", expanded=False):
    num_c1, num_c2, num_c3 = st.columns(3)
    with num_c1:
        st.metric(label=t("mulank", current_lang), value=mulank, help="Born on day 13 -> 1+3 = 4 (Rahu)")
    with num_c2:
        st.metric(label=t("bhagyank", current_lang), value=bhagyank, help="Total full date of birth reduction (Life Path)")
    with num_c3:
        st.metric(label=t("namank", current_lang), value=namank, help="Chaldean reduction of your official name")
    
    st.markdown(f"""
    <div class="num-banner">
        <b>• {t('mulank', current_lang)} {mulank}:</b> Governs your direct temperament, instincts, and execution velocity.<br>
        <b>• {t('bhagyank', current_lang)} {bhagyank}:</b> Dictates karmic milestones, career elevation, and life trajectory.<br>
        <b>• {t('namank', current_lang)} {namank}:</b> Defines social attraction, business resonance, and public reputation.
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="active-live-card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:16px; font-weight:800; color:#92400e;">
            {t('live_synthesis_head', current_lang)}
        </span>
        <span class="{'badge-danger' if cur_nav_cat in ['Vadha', 'Vipat', 'Pratyari'] else 'badge-favorable'}">
            {cur_nav_cat} (Series {cur_nav_series})
        </span>
    </div>
    <div style="font-size:13px; color:#78350f; margin-top:4px; margin-bottom:10px;">
        📅 <b>{now_ist.strftime('%A, %d %B %Y')}</b> | Active Moon in <b>{NAKSHATRAS[cur_moon_nak_idx]}</b>
    </div>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size:13.5px; margin-bottom:10px;">
        <div>🪐 <b>{t('active_vahan', current_lang)}:</b> {today_vahan['name']}</div>
        <div>🔢 <b>{t('active_pday', current_lang)}:</b> Day {p_day} ({p_title})</div>
    </div>
    <hr style="border:none; border-top:1px dashed #fcd34d; margin:10px 0;">
    <div style="font-size:14px; line-height:1.5; color:#451a03;">
        <b>1. Navtara Flow ({cur_nav_cat}):</b> {NAVTARA_DESCRIPTIONS.get(current_lang, NAVTARA_DESCRIPTIONS['en']).get(cur_nav_cat, '')}<br>
        <b>2. Saturn's Daily Mount ({today_vahan['name']}):</b> {today_vahan['desc']}<br>
        <b>3. Numerological Tone (Day {p_day}):</b> {p_desc}
    </div>
    <div class="remedy-box">
        <div style="font-weight:700; color:#92400e; font-size:13.5px; margin-bottom:4px;">
            {t('todays_remedies', current_lang)}:
        </div>
        <div style="font-size:13.5px; color:#1e293b;">
            • <b>Navtara Remedy:</b> {'Feed cattle or birds with soaked grain; defer speculative contracts.' if cur_nav_cat in ['Vadha', 'Vipat'] else ('Maintain diplomatic silence; avoid non-essential debates.' if cur_nav_cat == 'Pratyari' else 'Share fresh fruit or sweets; express gratitude to elders.')}<br>
            • <b>Numerology Remedy (Day {p_day}):</b> {num_remedy}<br>
            • <b>Shani Vahan Remedy:</b> {'Feed crows or stray birds soaked grains on your terrace to calm restlessness.' if 'Crow' in today_vahan['name'] else ('Double check documents and agreements against unverified advice.' if 'Jackal' in today_vahan['name'] else 'Light a mustard oil lamp or recite Hanuman Chalisa to maintain grounding stamina.')}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    t("tab_matrix", current_lang),
    t("tab_shani", current_lang),
    t("tab_numerology", current_lang),
    t("tab_planets", current_lang)
])

with tab1:
    st.subheader(t("tab_matrix", current_lang))
    transitions = find_7day_transitions(now_utc)
    
    # Overview Table
    overview_rows = []
    for tr in transitions:
        nak_name = NAKSHATRAS[tr["nak_idx"]]
        cat, series = calculate_navtara(janma_idx, tr["nak_idx"])
        status_badge = f"🔴 {cat}" if cat in ["Vipat", "Pratyari", "Vadha"] else ("🟢🟢 Ati-Mitra" if cat == "Ati-Mitra" else ("🟢 " + cat if cat in ["Mitra", "Sampat"] else cat))
        
        s_ist = tr["start"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M)")
        e_ist = tr["end"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M IST)")
        _, v_info = calculate_shani_vahan(janma_idx + 1, tr["nak_idx"] + 1)
        
        overview_rows.append({
            t("col_status", current_lang): status_badge,
            t("col_time", current_lang): f"{s_ist} – {e_ist}",
            t("col_nak", current_lang): nak_name,
            t("col_navtara", current_lang): f"{cat} ({series})",
            "Shani Vahan": v_info["name"].split(" ")[0]
        })
        
    st.dataframe(overview_rows, use_container_width=True, hide_index=True)
    st.markdown("---")
    
    # Detailed Day-by-Day Expanders with tailored predictions and remedies
    st.markdown("### 📋 Daily Expandable Predictions & Remedial Guidance")
    for idx, tr in enumerate(transitions):
        nak_name = NAKSHATRAS[tr["nak_idx"]]
        cat, series = calculate_navtara(janma_idx, tr["nak_idx"])
        s_dt = tr["start"].astimezone(ist_tz)
        e_dt = tr["end"].astimezone(ist_tz)
        _, v_info = calculate_shani_vahan(janma_idx + 1, tr["nak_idx"] + 1)
        _, day_num, day_t, day_d, day_rem = get_personal_day_vibe(mulank, s_dt.date())

        cat_badge = "🔴" if cat in ["Vipat", "Pratyari", "Vadha"] else ("🟢🟢" if cat == "Ati-Mitra" else "🟢")
        expander_title = f"{cat_badge} {s_dt.strftime('%A, %d %b')}: Moon in {nak_name} ({cat} - Series {series})"

        with st.expander(expander_title, expanded=(idx == 0)):
            c_left, c_right = st.columns([1, 1])
            with c_left:
                st.markdown(f"**⏰ Time Window:** `{s_dt.strftime('%d %b %H:%M')} to {e_dt.strftime('%d %b %H:%M IST')}`")
                st.markdown(f"**🪐 Saturn Vahan:** `{v_info['name']}` ({v_info['nature']})")
                st.markdown(f"**🔢 Personal Day:** `Day {day_num}` ({day_t})")
            with c_right:
                st.markdown(f"**✨ Navtara Essence:** {NAVTARA_DESCRIPTIONS.get(current_lang, NAVTARA_DESCRIPTIONS['en']).get(cat, '')}")
                st.markdown(f"**🎯 Day Tone:** {day_d}")

            st.markdown(f"""
            <div style="background:#f8fafc; border-left:4px solid #f59e0b; padding:10px; border-radius:6px; margin-top:8px;">
                <b>🪔 Prescribed Remedies for this Window:</b><br>
                1. <b>Navtara:</b> {'Feed cows/birds; hold off on high-stakes litigation or contracts.' if cat in ['Vadha', 'Vipat'] else ('Maintain disciplined silence in heated situations.' if cat == 'Pratyari' else 'Execute priority projects; offer thanks to elders/mentors.')}<br>
                2. <b>Numerology:</b> {day_rem}<br>
                3. <b>Shani Mount:</b> {v_info['desc']}
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.subheader(t("tab_shani", current_lang))
    
    st.markdown(f"""
    <div class="profile-card">
        <h3 style="margin-top:0; color:#1e1b4b;">{paya_name}</h3>
        <p><b>Current Transit:</b> Saturn transits <b>{RASHIS[saturn_rashi_idx].split(' ')[0]}</b>, your Moon sign is <b>{RASHIS[natal_moon_rashi_idx].split(' ')[0]}</b>.</p>
        <p><b>Foundational Status:</b> <span class="badge-favorable">{paya_status}</span></p>
        <p>{paya_desc}</p>
        <p><b>Timeline:</b> {paya_timeline}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📖 The 9 Sacred Vehicles (Vahans) of Saturn")
    v_table = []
    for k, v in SHANI_VAHANS.items():
        v_table.append({
            "Rem": k,
            "Vehicle": v["name"],
            "Nature & Speed": v["nature"],
            "Psychological Impact": v["desc"]
        })
    st.dataframe(v_table, use_container_width=True, hide_index=True)

with tab3:
    st.subheader(t("tab_numerology", current_lang))
    st.caption("Derived via Vedic and Chaldean reduction methodology.")
    
    n1, n2, n3 = st.columns(3)
    with n1:
        st.metric(label=t("mulank", current_lang), value=mulank, help="Born on day 13 -> 1+3 = 4")
    with n2:
        st.metric(label=t("bhagyank", current_lang), value=bhagyank, help="Full Date of Birth Sum -> 1+3+1+1+9+8+4 = 27 -> 9")
    with n3:
        st.metric(label=t("namank", current_lang), value=namank, help="Chaldean Name Letter Value Sum")
        
    st.markdown("---")
    st.markdown(f"**Day Number Vibration for {now_ist.strftime('%A, %d %B %Y')}:**")
    st.info(f"**Universal Day:** {u_day} | **Personal Day:** {p_day} — **{p_title}**\n\n{p_desc}\n\n**Remedy:** {num_remedy}")

with tab4:
    st.subheader(t("tab_planets", current_lang))
    st.caption("Computed with Swiss Ephemeris Chitrapaksha Lahiri Ayanamsa.")
    
    planets = [
        ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
        ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
        ("Venus", swe.VENUS), ("Saturn", swe.SATURN), ("Rahu", swe.MEAN_NODE)
    ]
    coords = []
    for name, pid in planets:
        lon = get_sidereal_lon(jd_now, pid)
        r_idx, r_deg = lon_to_rashi(lon)
        n_idx, pada = lon_to_nakshatra(lon)
        coords.append({
            "Planet": name,
            "Sign / Rashi": RASHIS[r_idx].split(" ")[0],
            "Degrees": f"{r_deg:.2f}°",
            "Nakshatra": f"{NAKSHATRAS[n_idx]} (Pada {pada})"
        })

    rahu_lon = get_sidereal_lon(jd_now, swe.MEAN_NODE)
    ketu_lon = (rahu_lon + 180.0) % 360.0
    kr_idx, kr_deg = lon_to_rashi(ketu_lon)
    kn_idx, k_pada = lon_to_nakshatra(ketu_lon)
    coords.append({
        "Planet": "Ketu",
        "Sign / Rashi": RASHIS[kr_idx].split(" ")[0],
        "Degrees": f"{kr_deg:.2f}°",
        "Nakshatra": f"{NAKSHATRAS[kn_idx]} (Pada {k_pada})"
    })

    st.dataframe(coords, use_container_width=True, hide_index=True)

with st.sidebar:
    st.header(t("sidebar_head", current_lang))
    st.caption("Update birth parameters to adjust calculations.")
    
    name_in = st.text_input("Name", value=prof.get("name", "Okesh"))
    dob_in = st.date_input("Date of Birth", value=prof.get("dob", datetime.date(1984, 1, 13)))
    tob_in = st.time_input("Time of Birth", value=prof.get("tob", datetime.time(14, 0)))
    place_in = st.text_input("Birth Place", value=prof.get("place", "Chhatrapati Sambhajinagar, India"))
    
    selected_nak = st.selectbox(
        "Janma Nakshatra",
        NAKSHATRAS,
        index=prof.get("nakshatra_idx", 1)  # Bharani
    )
    selected_nak_idx = NAKSHATRAS.index(selected_nak)
    
    if st.button(t("save_profile", current_lang), use_container_width=True, type="primary"):
        updated_prof = {
            "name": name_in,
            "dob": dob_in,
            "tob": tob_in,
            "place": place_in,
            "lat": prof.get("lat", 19.8762),
            "lon": prof.get("lon", 75.3433),
            "tz_offset": 5.5,
            "nakshatra_idx": selected_nak_idx,
            "language": current_lang
        }
        st.session_state.profile = updated_prof
        if save_user_profile(updated_prof):
            st.success(t("profile_saved", current_lang))
            st.rerun()

st.divider()
st.caption("Navtara Pulse • Swiss Ephemeris Chitrapaksha Lahiri Engine • All rights reserved.")
