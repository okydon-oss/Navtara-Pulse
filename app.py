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

# Mobile-first styling
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1.0rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 0.9rem !important;
        padding-right: 0.9rem !important;
        max-width: 720px !important;
        margin: 0 auto !important;
    }
    
    h1 {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        text-align: center !important;
        margin-bottom: 0.2rem !important;
        letter-spacing: -0.5px;
    }
    h2 { font-size: 1.35rem !important; font-weight: 700 !important; }
    h3 { font-size: 1.15rem !important; font-weight: 700 !important; }
    p, span, div { font-size: 15px; }
    
    label { font-size: 14.5px !important; font-weight: 600 !important; }
    input, select { min-height: 46px !important; font-size: 15px !important; }
    
    .stButton > button {
        min-height: 48px !important;
        font-size: 15.5px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
    }

    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13.5px;
    }
    .badge-favorable { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
    .badge-caution { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
    .badge-neutral { background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; }

    .card-box {
        background: #ffffff;
        border: 1.2px solid #e2e8f0;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .remedy-card {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1.5px solid #fde68a;
        border-radius: 14px;
        padding: 14px;
        margin-top: 10px;
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
        "tagline": "Cosmic Timing • Shani Paya & Vahan • Numerology Engine",
        "native": "Native",
        "janma_star": "Janma Star",
        "moon_sign": "Moon Sign",
        "tab_matrix": "🗓️ 7-Day Matrix",
        "tab_oracle": "🔮 Today's Oracle & Remedy",
        "tab_shani": "🪐 Shani Charan & Vahan",
        "tab_numerology": "🔢 Numerology",
        "tab_planets": "🌌 Planets",
        "matrix_sub": "Daily Moon Transition Table (Next 7 Days)",
        "matrix_desc": "Calculated with Swiss Ephemeris Chitrapaksha Lahiri Ayanamsa.",
        "col_status": "Status",
        "col_time": "Day, Date & Time (IST)",
        "col_nak": "Nakshatra",
        "col_series": "Series / Tara",
        "col_vahan": "Shani Vahan",
        "oracle_title": "🔮 Today's Integrated Synthesis & Remedy",
        "oracle_desc": "Synthesized for {name} on {date}",
        "cur_nav": "Current Navtara",
        "cur_star": "Active Moon Star",
        "cur_pday": "Personal Day Number",
        "cur_paya": "Shani Paya",
        "cur_vahan": "Today's Shani Vahan",
        "cur_uday": "Universal Day Energy",
        "strategic_dir": "🎯 Daily Strategic Directives",
        "cosmic_rhythm": "Cosmic Rhythm",
        "saturn_mount": "Saturn's Daily Mount",
        "numerology_tone": "Numerological Tone",
        "remedy_title": "🪔 Prescribed Astro-Remedy for Today",
        "shani_title": "🪐 Shani Charan (Paya) & Vahan Analysis",
        "shani_caption": "Understanding Saturn's material foundation and behavioral speed.",
        "paya_head": "🥈 Shani Ka Paya",
        "transit_pos": "Transit Position",
        "vahan_head": "Today's Shani Vahan",
        "theme": "Behavioral Theme",
        "formula": "Formula",
        "all_vahans": "📖 View All 9 Vehicles of Saturn & Meanings",
        "num_title": "🔢 Personal Numerology Engine",
        "num_caption": "Derived via Vedic and Chaldean reduction methodology.",
        "mulank": "Mulank (Driver)",
        "mulank_help": "Calculated from your day of birth.",
        "bhagyank": "Bhagyank (Conductor)",
        "bhagyank_help": "Calculated from your full date of birth.",
        "namank": "Namank (Name)",
        "namank_help": "Calculated via Chaldean letter values.",
        "day_vib": "Day Number Vibration for {date}:",
        "universal_day": "Universal Day",
        "personal_day": "Your Personal Day",
        "core_num_info": "ℹ️ Understanding Your Core Numbers",
        "planets_title": "Sidereal Planetary Positions (Lahiri)",
        "col_planet": "Planet",
        "col_sign": "Sign",
        "col_deg": "Degrees",
        "save_profile": "💾 Save Profile",
        "profile_saved": "✅ Profile saved successfully!",
        "sidebar_head": "👤 Your Birth Profile",
        "sidebar_caption": "Saved automatically to your profile.",
        "full_name": "Full Name",
        "dob": "Date of Birth",
        "tob": "Time of Birth",
        "birth_place": "Birth Place / City",
        "select_nak": "Janma Nakshatra",
        "lang_select": "🌐 Language / भाषा"
    },
    "hi": {
        "title": "✨ नवतारा पल्स (Navtara Pulse)",
        "tagline": "काल निर्णय • शनि चरण व वाहन • अंक ज्योतिष इंजन",
        "native": "जातक",
        "janma_star": "जन्म नक्षत्र",
        "moon_sign": "चन्द्र राशि",
        "tab_matrix": "🗓️ 7-दिवसीय चक्र",
        "tab_oracle": "🔮 आज का फलादेश व उपाय",
        "tab_shani": "🪐 शनि चरण व वाहन",
        "tab_numerology": "🔢 अंक ज्योतिष",
        "tab_planets": "🌌 ग्रह स्थिति",
        "matrix_sub": "दैनिक चन्द्र गोचर सारणी (आगामी 7 दिन)",
        "matrix_desc": "स्विस एफिमेरिस चित्रपक्ष लाहिड़ी अयनांश द्वारा सटीक गणना।",
        "col_status": "स्थिति",
        "col_time": "दिन, दिनांक व समय (IST)",
        "col_nak": "नक्षत्र",
        "col_series": "तारा / श्रृंखला",
        "col_vahan": "शनि वाहन",
        "oracle_title": "🔮 आज का समग्र फलादेश एवं वैदिक उपाय",
        "oracle_desc": "{name} के लिए {date} का संश्लेषित विश्लेषण",
        "cur_nav": "वर्तमान नवतारा",
        "cur_star": "सक्रिय चन्द्र नक्षत्र",
        "cur_pday": "व्यक्तिगत दिन अंक",
        "cur_paya": "शनि पाया (चरण)",
        "cur_vahan": "आज का शनि वाहन",
        "cur_uday": "सार्वभौमिक दिन ऊर्जा",
        "strategic_dir": "🎯 आज की दैनिक रणनीतिक दिशानिर्देश",
        "cosmic_rhythm": "ब्रह्मांडीय ताल (नवतारा)",
        "saturn_mount": "शनिदेव का दैनिक वाहन",
        "numerology_tone": "अंक ज्योतिष प्रभाव",
        "remedy_title": "🪔 आज के लिए अनुशंसित ज्योतिषीय उपाय",
        "shani_title": "🪐 शनि चरण (पाया) एवं वाहन विश्लेषण",
        "shani_caption": "शनि के भौतिक आधार एवं मनोवैज्ञानिक गति का गहन विश्लेषण।",
        "paya_head": "शनि का पाया",
        "transit_pos": "गोचर स्थिति",
        "vahan_head": "आज का शनि वाहन",
        "theme": "व्यवहार एवं ऊर्जा",
        "formula": "गणना सूत्र",
        "all_vahans": "📖 शनि के सभी 9 वाहनों का विवरण देखें",
        "num_title": "🔢 व्यक्तिगत अंक ज्योतिष इंजन",
        "num_caption": "वैदिक एवं कीरो-खाल्डियन पद्धति द्वारा गणना।",
        "mulank": "मूलांक (ड्राइवर)",
        "mulank_help": "आपकी जन्म तिथि के दिन से प्राप्त।",
        "bhagyank": "भाग्यांक (कंडक्टर)",
        "bhagyank_help": "सम्पूर्ण जन्म तिथि के योग से प्राप्त।",
        "namank": "नामांक (नाम अंक)",
        "namank_help": "खाल्डियन अक्षर मूल्यों द्वारा गणना।",
        "day_vib": "{date} के लिए दिन अंक स्पंदन:",
        "universal_day": "सार्वभौमिक दिन",
        "personal_day": "आपका व्यक्तिगत दिन",
        "core_num_info": "ℹ️ अपने मूल अंकों को समझें",
        "planets_title": "निरयण ग्रह स्थिति (लाहिड़ी)",
        "col_planet": "ग्रह",
        "col_sign": "राशि",
        "col_deg": "अंश (डिग्री)",
        "save_profile": "💾 प्रोफ़ाइल सुरक्षित करें",
        "profile_saved": "✅ प्रोफ़ाइल सुरक्षित हो गई!",
        "sidebar_head": "👤 आपकी जन्म कुंडली प्रोफ़ाइल",
        "sidebar_caption": "आपकी प्रोफ़ाइल में स्वतः सुरक्षित होती है।",
        "full_name": "पूरा नाम",
        "dob": "जन्म तिथि",
        "tob": "जन्म समय",
        "birth_place": "जन्म स्थान / शहर",
        "select_nak": "जन्म नक्षत्र",
        "lang_select": "🌐 भाषा चुनें (Language)"
    },
    "mr": {
        "title": "✨ नवतारा पल्स (Navtara Pulse)",
        "tagline": "काल निर्णय • शनी चरण व वाहन • अंकशास्त्र इंजिन",
        "native": "जातक",
        "janma_star": "जन्म नक्षत्र",
        "moon_sign": "चंद्र राशी",
        "tab_matrix": "🗓️ ७-दिवसीय चक्र",
        "tab_oracle": "🔮 आजचे भविष्य व उपाय",
        "tab_shani": "🪐 शनी चरण व वाहन",
        "tab_numerology": "🔢 अंकशास्त्र",
        "tab_planets": "🌌 ग्रह स्थिती",
        "matrix_sub": "दैनिक चंद्र गोचर सारणी (पुढील ७ दिवस)",
        "matrix_desc": "स्विस एफिमेरिस चित्रपक्ष लाहिरी अयनांशानुसार अचूक गणना.",
        "col_status": "स्थिती",
        "col_time": "वार, दिनांक व वेळ (IST)",
        "col_nak": "नक्षत्र",
        "col_series": "तारा / मालिका",
        "col_vahan": "शनी वाहन",
        "oracle_title": "🔮 आजचे संश्लेषित भविष्य व उपाय",
        "oracle_desc": "{name} साठी {date} चे विश्लेषण",
        "cur_nav": "सद्य नवतारा",
        "cur_star": "सक्रिय चंद्र नक्षत्र",
        "cur_pday": "वैयक्तिक दिवस अंक",
        "cur_paya": "शनीचा पाया (चरण)",
        "cur_vahan": "आजचे शनी वाहन",
        "cur_uday": "सार्वत्रिक दिवस ऊर्जा",
        "strategic_dir": "🎯 आजच्या धोरणात्मक सूचना",
        "cosmic_rhythm": "नवतारा ऊर्जा",
        "saturn_mount": "शनीचे आजचे वाहन",
        "numerology_tone": "अंकशास्त्र प्रभाव",
        "remedy_title": "🪔 आजचे अनुशंसित ज्योतिषीय उपाय",
        "shani_title": "🪐 शनी चरण (पाया) आणि वाहन विश्लेषण",
        "shani_caption": "शनीचा भौतिक प्रभाव आणि गतीचे विश्लेषण.",
        "paya_head": "शनीचा पाया",
        "transit_pos": "गोचर स्थिती",
        "vahan_head": "आजचे शनी वाहन",
        "theme": "ऊर्जा व स्वभाव",
        "formula": "सूत्र",
        "all_vahans": "📖 शनीच्या सर्व ९ वाहनांची माहिती पहा",
        "num_title": "🔢 वैयक्तिक अंकशास्त्र इंजिन",
        "num_caption": "वैदिक व खाल्डियन पद्धतीने गणना.",
        "mulank": "मूलांक",
        "mulank_help": "तुमच्या जन्मतारखेच्या दिवसावरून.",
        "bhagyank": "भाग्यांक",
        "bhagyank_help": "पूर्ण जन्मतारखेच्या बेरीजेवरून.",
        "namank": "नामांक",
        "namank_help": "नावाच्या अक्षरांवरून.",
        "day_vib": "{date} साठी दिवस स्पंदन:",
        "universal_day": "सार्वत्रिक दिवस",
        "personal_day": "तुमचा वैयक्तिक दिवस",
        "core_num_info": "ℹ️ मूळ अंकांचे रहस्य",
        "planets_title": "निरयण ग्रह स्थिती (लाहिरी)",
        "col_planet": "ग्रह",
        "col_sign": "राशी",
        "col_deg": "अंश",
        "save_profile": "💾 माहिती सेव्ह करा",
        "profile_saved": "✅ माहिती सेव्ह झाली!",
        "sidebar_head": "👤 तुमची जन्मतपशील प्रोफाइल",
        "sidebar_caption": "माहिती सुरक्षित साठवली जाते.",
        "full_name": "पूर्ण नाव",
        "dob": "जन्म तारीख",
        "tob": "जन्म वेळ",
        "birth_place": "जन्म ठिकाण / शहर",
        "select_nak": "जन्म नक्षत्र",
        "lang_select": "🌐 भाषा निवडा (Language)"
    },
    "gu": {
        "title": "✨ નવતારા પલ્સ (Navtara Pulse)",
        "tagline": "સમય નિર્ણય • શનિ ચરણ અને વાહન • અંક જ્યોતિષ",
        "native": "જાતક",
        "janma_star": "જન્મ નક્ષત્ર",
        "moon_sign": "ચંદ્ર રાશિ",
        "tab_matrix": "🗓️ ૭-દિવસીય ચક્ર",
        "tab_oracle": "🔮 આજનું ભવિષ્ય અને ઉપાય",
        "tab_shani": "🪐 શનિ ચરણ અને વાહન",
        "tab_numerology": "🔢 અંકશાસ્ત્ર",
        "tab_planets": "🌌 ગ્રહ સ્થિતિ",
        "matrix_sub": "દૈનિક ચંદ્ર ગોચર કોષ્ટક (આગામી ૭ દિવસ)",
        "matrix_desc": "સ્વિસ એફિમેરિસ ચિત્રપક્ષ લાહિરી અયનાંશ દ્વારા સચોટ ગણતરી.",
        "col_status": "સ્થિતિ",
        "col_time": "વાર, તારીખ અને સમય (IST)",
        "col_nak": "નક્ષત્ર",
        "col_series": "તારા / શ્રેણી",
        "col_vahan": "શનિ વાહન",
        "oracle_title": "🔮 આજનું વિશ્લેષણ અને ઉપાય",
        "oracle_desc": "{name} માટે {date} નું વિશ્લેષણ",
        "cur_nav": "વર્તમાન નવતારા",
        "cur_star": "સક્રિય ચંદ્ર નક્ષત્ર",
        "cur_pday": "વ્યક્તિગત દિવસ અંક",
        "cur_paya": "શનિ પાયા (ચરણ)",
        "cur_vahan": "આજનું શનિ વાહન",
        "cur_uday": "સાર્વત્રિક દિવસ ઊર્જા",
        "strategic_dir": "🎯 આજની દૈનિક વ્યૂહાત્મક સલાહ",
        "cosmic_rhythm": "નવતારા ઊર્જા",
        "saturn_mount": "શનિદેવનું વાહન",
        "numerology_tone": "અંકશાસ્ત્ર પ્રભાવ",
        "remedy_title": "🪔 આજ માટે વિશેષ જ્યોતિષીય ઉપાય",
        "shani_title": "🪐 શનિ ચરણ (પાયા) અને વાહન વિશ્લેષણ",
        "shani_caption": "શનિના ભૌતિક આધાર અને ગતિશીલતાનું વિશ્લેષણ.",
        "paya_head": "શનિનો પાયો",
        "transit_pos": "ગોચર સ્થિતિ",
        "vahan_head": "આજનું શનિ વાહન",
        "theme": "ઊર્જા અને પ્રકૃતિ",
        "formula": "સૂત્ર",
        "all_vahans": "📖 શનિના તમામ ૯ વાહનોની માહિતી",
        "num_title": "🔢 વ્યક્તિગત અંકશાસ્ત્ર એન્જિન",
        "num_caption": "વૈદિક અને ખાલ્ડિયન પદ્ધતિ દ્વારા ગણતરી.",
        "mulank": "મૂળાંક",
        "mulank_help": "તમારી જન્મ તારીખના દિવસ પરથી.",
        "bhagyank": "ભાગ્યાંક",
        "bhagyank_help": "સંપૂર્ણ જન્મ તારીખના સરવાળા પરથી.",
        "namank": "નામાંક",
        "namank_help": "નામના અક્ષરો પરથી.",
        "day_vib": "{date} માટે દિવસ સ્પંદન:",
        "universal_day": "સાર્વત્રિક દિવસ",
        "personal_day": "તમારો વ્યક્તિગત દિવસ",
        "core_num_info": "ℹ️ મૂળ અંકો વિશે સમજો",
        "planets_title": "નિરાયણ ગ્રહ સ્થિતિ (લાહિરી)",
        "col_planet": "ગ્રહ",
        "col_sign": "રાશિ",
        "col_deg": "અંશ (ડિગ્રી)",
        "save_profile": "💾 પ્રોફાઇલ સાચવો",
        "profile_saved": "✅ પ્રોફાઇલ સફળતાપૂર્વક સાચવવામાં આવી!",
        "sidebar_head": "👤 તમારી જન્મ વિગતો",
        "sidebar_caption": "વિગતો આપમેળે સાચવવામાં આવે છે.",
        "full_name": "પૂરું નામ",
        "dob": "જન્મ તારીખ",
        "tob": "જન્મ સમય",
        "birth_place": "જન્મ સ્થળ / શહેર",
        "select_nak": "જન્મ નક્ષત્ર",
        "lang_select": "🌐 ભાષા પસંદ કરો (Language)"
    }
}

def t(key: str, lang: str = "en") -> str:
    """Helper function to fetch localized strings with fallback to English."""
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
        "Janma": "Self / Physical Vitality / Grounding & New Cycles",
        "Sampat": "Wealth / Financial Expansion / Material Acquisitions",
        "Vipat": "Obstacles / High Risk / Unforeseen Volatility",
        "Kshema": "Well-being / Comfort / Protection & Recovery",
        "Pratyari": "Resistance / Confrontation / Strategic Restraint",
        "Sadhana": "Achievement / Focused Effort / Peak Productivity",
        "Vadha": "Destruction / High Vulnerability / Complete Caution",
        "Mitra": "Friendship / Collaborative Harmony / Goodwill",
        "Ati-Mitra": "Supreme Support / Peak Auspicious Opportunity"
    },
    "hi": {
        "Janma": "स्व / शारीरिक स्वास्थ्य / नई शुरुआत एवं संतुलन",
        "Sampat": "धन / आर्थिक विस्तार / भौतिक लाभ एवं समृद्धि",
        "Vipat": "बाधाएं / जोखिम / अप्रत्याशित उतार-चढ़ाव (सावधानी)",
        "Kshema": "कल्याण / सुख-शांति / सुरक्षा एवं स्वास्थ्य लाभ",
        "Pratyari": "विरोध / मतभेद / वाद-विवाद से दूर रहने का समय",
        "Sadhana": "सिद्धि / लक्ष्य प्राप्ति / कार्य में पूर्ण सफलता",
        "Vadha": "हानि / संवेदनशीलता / पूर्ण संयम एवं शांति आवश्यक",
        "Mitra": "मित्रता / सौहार्दपूर्ण सहयोग / शुभ संपर्क",
        "Ati-Mitra": "अति शुभ / परम सहयोग / महत्वपूर्ण कार्यों के लिए श्रेष्ठ"
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
    1: {"name": "Ghoda (Horse) 🐴", "nature": "Speed & Quick Victory", "desc": "Swift movement, high stamina, victory over competitors, rapid task completion."},
    2: {"name": "Gadha (Donkey) 🫏", "nature": "Heavy Labor & Delays", "desc": "High physical workload with delayed recognition. Demands continuous patience."},
    3: {"name": "Siyar (Jackal) 🦊", "nature": "Alertness & Caution", "desc": "Warning against deceptive advice, unverified schemes, or hidden friction."},
    4: {"name": "Hathi (Elephant) 🐘", "nature": "Royalty & Prosperity", "desc": "Sudden prestige, luxury gains, recognition from seniors, and material comfort."},
    5: {"name": "Bail (Bull) 🐂", "nature": "Steady Persistence", "desc": "Gradual, rock-solid gains through steady discipline. Excellent for foundational building."},
    6: {"name": "Sher (Lion) 🦁", "nature": "Power & Authority", "desc": "Commanding respect, high confidence, decisive success in legal or competitive arenas."},
    7: {"name": "Kowwa (Crow) 🐦‍⬛", "nature": "Restlessness & Distraction", "desc": "Scattered mental energy, minor arguments, frequent movement. Practice silence."},
    8: {"name": "Mayur (Peacock) 🦚", "nature": "Joy & Aesthetic Warmth", "desc": "Heartwarming social news, creative flow, domestic warmth, and delightful meetings."},
    9: {"name": "Hans (Swan) 🦢", "nature": "Wisdom & Spiritual Peace", "desc": "Highest mental clarity, serene intuition, spiritual grace, and sound financial judgment."}
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
    if house_pos in [2, 5, 9]:
        paya_title = "Rajat Paya (Silver Feet / चाँदी का पाया) 🥈" if lang in ["hi", "mr", "gu"] else "Rajat Paya (Silver Feet) 🥈"
        status = "Most Auspicious & Protective (अति शुभ)" if lang in ["hi", "mr", "gu"] else "Most Auspicious & Protective"
        desc = "Brings wealth expansion, protective cushioning, domestic comfort, and clear resolutions."
        return paya_title, status, desc
    elif house_pos in [3, 7, 10]:
        paya_title = "Tamra Paya (Copper Feet / तांबे का पाया) 🥉" if lang in ["hi", "mr", "gu"] else "Tamra Paya (Copper Feet) 🥉"
        status = "Favorable & Progressive (शुभ फलदायी)" if lang in ["hi", "mr", "gu"] else "Favorable & Progressive"
        desc = "Brings steady rewards through hard work, continuous career growth, and strong vitality."
        return paya_title, status, desc
    elif house_pos in [1, 6, 11]:
        paya_title = "Swarna Paya (Gold Feet / सोने का पाया) 🥇" if lang in ["hi", "mr", "gu"] else "Swarna Paya (Gold Feet) 🥇"
        status = "Testing & High Expenditure (मध्यम/व्ययकारक)" if lang in ["hi", "mr", "gu"] else "Testing & High Expenditure"
        desc = "Tests humility and character. Financial turnover is high; caution against ego conflicts."
        return paya_title, status, desc
    else:  # 4, 8, 12
        paya_title = "Loha Paya (Iron Feet / लोहे का पाया) 🪙" if lang in ["hi", "mr", "gu"] else "Loha Paya (Iron Feet) 🪙"
        status = "Heavy Labor & High Caution (कठिन/सावधानी)" if lang in ["hi", "mr", "gu"] else "Heavy Labor & High Caution"
        desc = "Indicates karmic testing, project friction, joint fatigue. Requires routine discipline."
        return paya_title, status, desc

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
        1: ("Leadership & Initiative", "Ideal for launching plans, asserting self-confidence, and signing off on direct decisions."),
        2: ("Diplomacy & Harmony", "Favor teamwork, quiet negotiations, emotional balance, and attentive listening."),
        3: ("Creative Expression", "Excellent for brainstorming, persuasive communication, writing, and social meetings."),
        4: ("Discipline & Foundation", "Focus on structured execution, organizing paperwork, maintenance, and detailed follow-through."),
        5: ("Flexibility & Quick Change", "Expect quick changes in pace. Good for networking, sales, and agile problem solving."),
        6: ("Responsibility & Family", "Nurture domestic relationships, assist colleagues, and focus on health harmony."),
        7: ("Deep Introspection & Study", "Avoid noisy debates. Ideal for research, spiritual contemplation, and analytical audits."),
        8: ("Authority & Financial Prudence", "Handle monetary decisions, contracts, and long-range business planning with discipline."),
        9: ("Completion & Detachment", "Wrap up pending items, release past friction, forgive misunderstandings, and prepare for new cycles.")
    }
    return universal_day, personal_day, vibe_map.get(personal_day, ("Balanced Focus", "Proceed with standard awareness."))

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

def get_daily_remedy(navtara_cat: str, vahan_name: str, day_name: str, lang: str = "en"):
    remedies = []
    
    if "Sat" in day_name:
        remedies.append("शनिवार: शाम को पीपल के वृक्ष के पास सरसों के तेल का दीपक प्रज्वलित करें अथवा काले तिल का दान करें।" if lang in ["hi", "mr", "gu"] else "Saturday: Offer mustard oil diya near a Peepal tree or donate black sesame to cultivate Saturn's grounding peace.")
    elif "Tue" in day_name:
        remedies.append("मंगलवार: आत्मविश्वास एवं सुरक्षा के लिए हनुमान चालीसा का २ बार पाठ करें।" if lang in ["hi", "mr", "gu"] else "Tuesday: Recite the Hanuman Chalisa twice to dissolve friction and bolster internal stamina.")
    elif "Sun" in day_name:
        remedies.append("रविवार: तांबे के लोटे से सूर्यदेव को जल (अर्घ्य) अर्पित करें।" if lang in ["hi", "mr", "gu"] else "Sunday: Offer Arghya (clean water in copper vessel) to the rising Sun to nourish vitality.")
    elif "Mon" in day_name:
        remedies.append("सोमवार: मन को शांत रखने के लिए पर्याप्त जल पिएं और ओम नमः शिवाय का जप करें।" if lang in ["hi", "mr", "gu"] else "Monday: Keep your mind calm with deep hydration; avoid impulsive emotional reactions.")
    else:
        remedies.append("दिन की शुरुआत ५ मिनट शांत प्राणायाम अथवा इष्ट मंत्र जप से करें।" if lang in ["hi", "mr", "gu"] else "Begin your day with 5 minutes of focused conscious breathing or Japa before taking phone calls.")
        
    if navtara_cat in ["Vadha", "Vipat"]:
        remedies.append("नवतारा चेतावनी: पक्षियों या गाय को हरा चारा अथवा दाना खिलाएं। जोखिम भरे वित्तीय निर्णय न लें।" if lang in ["hi", "mr", "gu"] else "Navtara Caution: Feed stray birds or cattle with whole grains. Avoid signing high-risk financial commitments.")
    elif navtara_cat == "Pratyari":
        remedies.append("प्रत्यरि तारा: वाणी पर संयम रखें और अनावश्यक वाद-विवाद से बचें।" if lang in ["hi", "mr", "gu"] else "Pratyari Star: Practice diplomatic silence. Avoid entering into avoidable debates or counter-arguments.")
    elif navtara_cat in ["Sampat", "Ati-Mitra"]:
        remedies.append("अति-मित्र/सम्पत: किसी जरूरतमंद को फल अथवा मिष्ठान्न बांटें और बड़ों का आशीर्वाद लें।" if lang in ["hi", "mr", "gu"] else "Auspicious Tara: Share sweets or fresh fruit with someone in need; express gratitude to elders.")
    else:
        remedies.append("अपने आवश्यक कार्यों को एकाग्रता के साथ पूरा करें।" if lang in ["hi", "mr", "gu"] else "Focus diligently on completing one pending task with full attention to harness steady momentum.")

    if "Crow" in vahan_name or "Kowwa" in vahan_name:
        remedies.append("कौआ वाहन: मानसिक चंचलता को शांत करने हेतु कौवों या पक्षियों को भीगे हुए अनाज या रोटी खिलाएं।" if lang in ["hi", "mr", "gu"] else "Crow Vahan: Feed crows or birds some soaked grains or bread on your terrace to settle mental restlessness.")
    elif "Jackal" in vahan_name or "Siyar" in vahan_name:
        remedies.append("सियार वाहन: लेन-देन के विवरण की दोबारा जांच करें और किसी बहकावे में न आएं।" if lang in ["hi", "mr", "gu"] else "Jackal Vahan: Double-check transaction details and avoid speculation or unverified claims.")
    elif "Donkey" in vahan_name or "Gadha" in vahan_name:
        remedies.append("गधा वाहन: अधिक कार्यभार से बचने हेतु काम के बीच में छोटे-छोटे विश्राम लें।" if lang in ["hi", "mr", "gu"] else "Donkey Vahan: Take regular short breaks during heavy physical or mental labor to prevent burnout.")

    return remedies

if "profile" not in st.session_state:
    st.session_state.profile = load_user_profile()

prof = st.session_state.profile
current_lang = prof.get("language", "en")

with st.sidebar:
    st.header(t("sidebar_head", current_lang))
    st.caption(t("sidebar_caption", current_lang))

    # Prominent Language Selector
    lang_codes = list(SUPPORTED_LANGUAGES.keys())
    lang_labels = list(SUPPORTED_LANGUAGES.values())
    curr_lang_idx = lang_codes.index(current_lang) if current_lang in lang_codes else 0

    selected_lang_label = st.selectbox(
        t("lang_select", current_lang),
        lang_labels,
        index=curr_lang_idx
    )
    selected_lang_code = lang_codes[lang_labels.index(selected_lang_label)]

    if selected_lang_code != current_lang:
        prof["language"] = selected_lang_code
        st.session_state.profile = prof
        save_user_profile(prof)
        st.rerun()

    st.divider()

    name_in = st.text_input(t("full_name", current_lang), value=prof.get("name", "Okesh"))
    dob_in = st.date_input(t("dob", current_lang), value=prof.get("dob", datetime.date(1984, 1, 13)))
    tob_in = st.time_input(t("tob", current_lang), value=prof.get("tob", datetime.time(14, 0)))
    place_in = st.text_input(t("birth_place", current_lang), value=prof.get("place", "Chhatrapati Sambhajinagar, India"))

    selected_nak = st.selectbox(
        t("select_nak", current_lang),
        NAKSHATRAS,
        index=prof.get("nakshatra_idx", 1)  # Default: Bharani
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
            "language": selected_lang_code
        }
        st.session_state.profile = updated_prof
        if save_user_profile(updated_prof):
            st.success(t("profile_saved", current_lang))

janma_idx = prof.get("nakshatra_idx", 1)
janma_name = NAKSHATRAS[janma_idx]
user_dob = prof.get("dob", datetime.date(1984, 1, 13))
user_name = prof.get("name", "Okesh")

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

paya_name, paya_status, paya_desc = calculate_shani_paya(natal_moon_rashi_idx, saturn_rashi_idx, current_lang)
today_vahan_num, today_vahan = calculate_shani_vahan(janma_idx + 1, cur_moon_nak_idx + 1)
cur_nav_cat, cur_nav_series = calculate_navtara(janma_idx, cur_moon_nak_idx)

st.markdown(f"""
<div style="text-align: center; margin-bottom: 12px;">
    <h1>{t("title", current_lang)}</h1>
    <div style="color: #4f46e5; font-weight: 700; font-size: 15px;">{t("tagline", current_lang)}</div>
    <div style="margin-top: 6px; font-size: 14.5px; color: #475569;">
        {t("native", current_lang)}: <b>{user_name}</b> | {t("janma_star", current_lang)}: <b>{janma_name}</b> (<code>#{janma_idx+1}</code>) | {t("moon_sign", current_lang)}: <b>{RASHIS[natal_moon_rashi_idx].split(' ')[0]}</b>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    t("tab_matrix", current_lang),
    t("tab_oracle", current_lang),
    t("tab_shani", current_lang),
    t("tab_numerology", current_lang),
    t("tab_planets", current_lang)
])

with tab1:
    st.subheader(t("matrix_sub", current_lang))
    st.caption(t("matrix_desc", current_lang))

    transitions = find_7day_transitions(now_utc)
    table_rows = []

    for tr in transitions:
        nak_name = NAKSHATRAS[tr["nak_idx"]]
        cat, series = calculate_navtara(janma_idx, tr["nak_idx"])

        if cat in ["Vipat", "Pratyari", "Vadha"]:
            status_str = f"🔴 {cat}"
        elif cat == "Ati-Mitra":
            status_str = "🟢🟢 Ati-Mitra"
        elif cat in ["Mitra", "Sampat"]:
            status_str = f"🟢 {cat}"
        else:
            status_str = cat

        start_ist = tr["start"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M)")
        end_ist = tr["end"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M IST)")

        _, vahan_info = calculate_shani_vahan(janma_idx + 1, tr["nak_idx"] + 1)

        table_rows.append({
            t("col_status", current_lang): status_str,
            t("col_time", current_lang): f"{start_ist} – {end_ist}",
            t("col_nak", current_lang): nak_name,
            t("col_series", current_lang): f"{cat} ({series})",
            t("col_vahan", current_lang): vahan_info["name"].split(" ")[0]
        })

    st.dataframe(table_rows, use_container_width=True, hide_index=True)

with tab2:
    st.subheader(t("oracle_title", current_lang))
    st.caption(t("oracle_desc", current_lang).format(name=user_name, date=now_ist.strftime('%A, %d %B %Y')))

    u_day, p_day, (p_title, p_desc) = get_personal_day_vibe(mulank, now_ist.date())

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{t('cur_nav', current_lang)}:** `{cur_nav_cat} (Series {cur_nav_series})`")
        st.markdown(f"**{t('cur_star', current_lang)}:** `{NAKSHATRAS[cur_moon_nak_idx]}`")
        st.markdown(f"**{t('cur_pday', current_lang)}:** `{p_day}` ({p_title})")
    with c2:
        st.markdown(f"**{t('cur_paya', current_lang)}:** `{paya_name.split(' ')[0]} {paya_name.split(' ')[1]}`")
        st.markdown(f"**{t('cur_vahan', current_lang)}:** `{today_vahan['name']}`")
        st.markdown(f"**{t('cur_uday', current_lang)}:** `{u_day}`")

    st.markdown("---")

    nav_desc_map = NAVTARA_DESCRIPTIONS.get(current_lang, NAVTARA_DESCRIPTIONS["en"])
    st.markdown(f"### {t('strategic_dir', current_lang)}")
    st.write(f"**1. {t('cosmic_rhythm', current_lang)} ({cur_nav_cat}):** {nav_desc_map.get(cur_nav_cat, '')}")
    st.write(f"**2. {t('saturn_mount', current_lang)} ({today_vahan['name']}):** {today_vahan['desc']}")
    st.write(f"**3. {t('numerology_tone', current_lang)} (Day {p_day}):** {p_desc}")

    st.markdown(f"""<div class="remedy-card">
        <h4 style="margin-top: 0; color: #92400e;">{t('remedy_title', current_lang)}</h4>
    """, unsafe_allow_html=True)
    
    daily_remedies = get_daily_remedy(cur_nav_cat, today_vahan["name"], now_ist.strftime("%a"), current_lang)
    for idx, rem in enumerate(daily_remedies, 1):
        st.markdown(f"• **Step {idx}:** {rem}")
        
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.subheader(t("shani_title", current_lang))
    st.caption(t("shani_caption", current_lang))

    sat_rashi_name = RASHIS[saturn_rashi_idx].split(" ")[0]
    moon_rashi_name = RASHIS[natal_moon_rashi_idx].split(" ")[0]

    st.markdown(f"""
    <div class="card-box">
        <h3 style="margin-top:0; color:#1e1b4b;">{paya_name}</h3>
        <p><b>{t('transit_pos', current_lang)}:</b> Saturn in <b>{sat_rashi_name}</b>, your Janma Rashi is <b>{moon_rashi_name}</b>.</p>
        <p><b>Status:</b> <span class="status-badge badge-favorable">{paya_status}</span></p>
        <p>{paya_desc}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card-box">
        <h3 style="margin-top:0; color:#1e1b4b;">{today_vahan['name']}</h3>
        <p><b>{t('theme', current_lang)}:</b> <i>{today_vahan['nature']}</i></p>
        <p>{today_vahan['desc']}</p>
        <p><b>{t('formula', current_lang)}:</b> <code>((Birth Star #{janma_idx+1} × 4) + Today's Moon Star #{cur_moon_nak_idx+1}) mod 9 = Remainder {today_vahan_num}</code></p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(t("all_vahans", current_lang)):
        v_rows = []
        for num, vdata in SHANI_VAHANS.items():
            v_rows.append({
                "Index": num,
                "Vehicle": vdata["name"],
                "Key Energy": vdata["nature"],
                "Impact": vdata["desc"]
            })
        st.dataframe(v_rows, use_container_width=True, hide_index=True)

with tab4:
    st.subheader(t("num_title", current_lang))
    st.caption(t("num_caption", current_lang))

    num_col1, num_col2, num_col3 = st.columns(3)
    with num_col1:
        st.metric(label=t("mulank", current_lang), value=mulank, help=t("mulank_help", current_lang))
    with num_col2:
        st.metric(label=t("bhagyank", current_lang), value=bhagyank, help=t("bhagyank_help", current_lang))
    with num_col3:
        st.metric(label=t("namank", current_lang), value=namank, help=t("namank_help", current_lang))

    st.markdown("---")
    date_vib_title = t("day_vib", current_lang).format(date=now_ist.strftime('%d %b %Y'))
    st.markdown(f"**{date_vib_title}**")
    st.info(f"**{t('universal_day', current_lang)}:** {u_day} | **{t('personal_day', current_lang)}:** {p_day} — **{p_title}**\n\n{p_desc}")

    with st.expander(t("core_num_info", current_lang)):
        st.markdown(f"""
        - **{t('mulank', current_lang)} {mulank}:** Represents your core behavioral nature, innate desires, and spontaneous reactions.
        - **{t('bhagyank', current_lang)} {bhagyank}:** Dictates life path, career direction, karmic trajectory, and maturity cycles after age 32.
        - **{t('namank', current_lang)} {namank}:** Represents your public identity, social attraction, and professional resonance.
        """)

with tab5:
    st.subheader(t("planets_title", current_lang))
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
            t("col_planet", current_lang): name,
            t("col_sign", current_lang): RASHIS[r_idx].split(" ")[0],
            t("col_deg", current_lang): f"{r_deg:.2f}°",
            t("col_nak", current_lang): f"{NAKSHATRAS[n_idx]} (Pada {pada})"
        })

    rahu_lon = get_sidereal_lon(jd_now, swe.MEAN_NODE)
    ketu_lon = (rahu_lon + 180.0) % 360.0
    kr_idx, kr_deg = lon_to_rashi(ketu_lon)
    kn_idx, k_pada = lon_to_nakshatra(ketu_lon)
    coords.append({
        t("col_planet", current_lang): "Ketu",
        t("col_sign", current_lang): RASHIS[kr_idx].split(" ")[0],
        t("col_deg", current_lang): f"{kr_deg:.2f}°",
        t("col_nak", current_lang): f"{NAKSHATRAS[kn_idx]} (Pada {k_pada})"
    })

    st.dataframe(coords, use_container_width=True, hide_index=True)

st.divider()
st.caption("Navtara Pulse Engine • Swiss Ephemeris Chitrapaksha Lahiri Framework • All rights reserved.")
