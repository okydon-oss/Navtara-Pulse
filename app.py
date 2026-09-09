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

# Configure page settings
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
        padding-top: 1rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 720px !important;
        margin: 0 auto !important;
    }

    /* Top branding and single language selection bar */
    .brand-header {
        text-align: center;
        margin-bottom: 12px;
    }
    .brand-title {
        font-size: 26px;
        font-weight: 800;
        color: #3b2d54;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .brand-subtitle {
        font-size: 13.5px;
        color: #6b5b7b;
        margin-top: 3px;
        margin-bottom: 14px;
        font-weight: 500;
    }

    /* Light catchy card designs */
    .light-card-profile {
        background: linear-gradient(135deg, #fbf7f4 0%, #fef4e8 100%);
        border: 1.5px solid #fed7aa;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(251, 146, 60, 0.08);
    }

    .light-card-num {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
        border: 1.5px solid #a7f3d0;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08);
    }

    .light-card-paya {
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
        border: 1.5px solid #ddd6fe;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.08);
    }

    .light-card-live {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1.5px solid #fde68a;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.10);
    }

    .remedy-highlight-box {
        background: #ffffff;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 12px 14px;
        margin-top: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }

    .badge-danger {
        background: #fee2e2;
        color: #991b1b;
        padding: 3px 9px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .badge-favorable {
        background: #dcfce7;
        color: #166534;
        padding: 3px 9px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .badge-super {
        background: #dbeafe;
        color: #1e40af;
        padding: 3px 9px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }

    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 15.5px !important;
        transition: all 0.2s ease;
    }
    </style>
""", unsafe_allow_html=True)

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "mr": "मराठी (Marathi)",
    "gu": "ગુજરાતી (Gujarati)"
}

TRANSLATIONS = {
    "en": {
        "app_title": "✨ Navtara Pulse",
        "app_tagline": "Precision Vedic Moon Transit • Shani Charan & Vahan • Numerology Blueprint",
        "select_lang": "🌐 Select Language",
        "profile_heading": "👤 Native Astrological Profile",
        "edit_profile_expander": "✏️ Update / Edit Birth Details",
        "input_name": "Full Name",
        "input_dob": "Date of Birth",
        "input_tob": "Time of Birth",
        "input_place": "Birth Place (City, Country)",
        "input_nakshatra": "Janma Nakshatra (Birth Star)",
        "save_profile_btn": "💾 Save Profile Details",
        "profile_saved_msg": "✅ Profile updated and saved successfully!",
        "birth_details_sub": "Birth Information",
        "janma_star_label": "Janma Nakshatra",
        "moon_rashi_label": "Moon Sign (Janma Rashi)",
        "nak_personality_title": "🌟 Janma Nakshatra Personality & Core Traits",
        "num_title": "🔢 Core Numerology Blueprint & Fixed Life Attributes",
        "mulank_label": "Mulank (Driver)",
        "bhagyank_label": "Bhagyank (Conductor)",
        "namank_label": "Namank (Name Vibration)",
        "fixed_prediction_title": "✨ Fixed Numerology Life Path Analysis",
        "paya_card_title": "🪐 Ongoing Shani Paya (Saturn's Pillar & Charan)",
        "transit_timeline_lbl": "Current Transit Timeline",
        "paya_impact_lbl": "Foundational Life Impact & Predictions",
        "paya_remedies_lbl": "🪔 Shani Paya Protective Vedic Remedies",
        "btn_view_forecast": "🔮 View Predictions for Today & Next 7 Days ➔",
        "btn_back_profile": "⬅️ Back to Native Profile",
        "forecast_page_title": "🔮 Cosmic Synthesis & Navtara Transit Directives",
        "today_card_title": "🌟 Today's Active Cosmic Synthesis",
        "current_active_nak": "Current Moon Nakshatra",
        "current_tara": "Active Navtara",
        "saturn_vahan_lbl": "Today's Shani Vahan",
        "personal_day_lbl": "Today's Personal Day Vibration",
        "today_directives": "🎯 Integrated 3-Pillar Directives for Today",
        "today_remedies_lbl": "🪔 Prescribed Daily Multi-Layer Remedies",
        "navtara_matrix_title": "🗓️ 7-Day Moon Transition & Daily Forecast",
        "matrix_instruction": "Click any day below to expand and view full predictions and remedies for that specific window.",
        "col_status": "Status",
        "col_window": "Window (IST)",
        "col_nak": "Moon Star",
        "col_series": "Navtara Series",
        "col_vahan": "Shani Vahan",
        "planets_btn": "🌌 View Sidereal Planetary Positions (Lahiri)",
        "planets_hide_btn": "🔼 Hide Planetary Positions",
        "window_lbl": "Active Window",
        "series_lbl": "Series",
        "predictions_lbl": "Detailed Forecast",
        "remedies_lbl": "Prescribed Remedies for this Day"
    },
    "hi": {
        "app_title": "✨ नवतारा पल्स (Navtara Pulse)",
        "app_tagline": "सटीक वैदिक चन्द्र गोचर • शनि चरण व वाहन • अंक ज्योतिष रूपरेखा",
        "select_lang": "🌐 भाषा का चयन करें",
        "profile_heading": "👤 जातक जन्म कुंडली एवं ज्योतिषीय आधार",
        "edit_profile_expander": "✏️ जन्म विवरण दर्ज या संशोधित करें",
        "input_name": "पूरा नाम",
        "input_dob": "जन्म तिथि",
        "input_tob": "जन्म समय",
        "input_place": "जन्म स्थान (शहर, देश)",
        "input_nakshatra": "जन्म नक्षत्र",
        "save_profile_btn": "💾 जन्म विवरण सुरक्षित करें",
        "profile_saved_msg": "✅ विवरण सफलतापूर्वक सुरक्षित कर लिया गया!",
        "birth_details_sub": "जन्म विवरण",
        "janma_star_label": "जन्म नक्षत्र",
        "moon_rashi_label": "चन्द्र राशि",
        "nak_personality_title": "🌟 जन्म नक्षत्र व्यक्तित्व एवं मूल स्वभाव",
        "num_title": "🔢 अंक ज्योतिष चक्र एवं मूल स्वभाव विश्लेषण",
        "mulank_label": "मूलांक (स्वभाव)",
        "bhagyank_label": "भाग्यांक (भाग्य पथ)",
        "namank_label": "नामांक (पहचान स्पंदन)",
        "fixed_prediction_title": "✨ आजीवन अंक ज्योतिषीय फलादेश एवं स्वभाव",
        "paya_card_title": "🪐 वर्तमान शनि पाया (चरण फल व आधार)",
        "transit_timeline_lbl": "वर्तमान गोचर समयावधि (Timeline)",
        "paya_impact_lbl": "शनि पाया प्रभाव एवं जीवन पर परिणाम",
        "paya_remedies_lbl": "🪔 शनि पाया शांति एवं सुरक्षात्मक वैदिक उपाय",
        "btn_view_forecast": "🔮 आज का और अगले 7 दिनों का फलादेश देखें ➔",
        "btn_back_profile": "⬅️ जातक प्रोफ़ाइल पर वापस जाएं",
        "forecast_page_title": "🔮 ब्रह्मांडीय नवतारा गोचर एवं दैनिक फलादेश",
        "today_card_title": "🌟 आज का सक्रिय त्रि-स्तंभीय ब्रह्मांडीय समन्वय",
        "current_active_nak": "सक्रिय चन्द्र नक्षत्र",
        "current_tara": "वर्तमान नवतारा स्थिति",
        "saturn_vahan_lbl": "आज का शनि वाहन",
        "personal_day_lbl": "व्यक्तिगत दिन अंक स्पंदन",
        "today_directives": "🎯 आज के लिए एकीकृत ज्योतिषीय निर्देश",
        "today_remedies_lbl": "🪔 आज के अनुशंसित त्रि-स्तरीय वैदिक उपाय",
        "navtara_matrix_title": "🗓️ 7-दिवसीय चन्द्र गोचर व दैनिक तालिका",
        "matrix_instruction": "विस्तृत फलादेश और उपाय देखने के लिए नीचे दिए गए किसी भी दिन पर क्लिक करें।",
        "col_status": "स्थिति",
        "col_window": "समयावधि (IST)",
        "col_nak": "चन्द्र नक्षत्र",
        "col_series": "नवतारा चक्र",
        "col_vahan": "शनि वाहन",
        "planets_btn": "🌌 स्पष्ट निरयण ग्रह स्थितियां देखें (लाहिड़ी)",
        "planets_hide_btn": "🔼 ग्रह स्थिति बंद करें",
        "window_lbl": "सक्रिय समय",
        "series_lbl": "श्रृंखला",
        "predictions_lbl": "विस्तृत फलादेश",
        "remedies_lbl": "इस दिन के विशेष उपाय"
    },
    "mr": {
        "app_title": "✨ नवतारा पल्स (Navtara Pulse)",
        "app_tagline": "अचूक वैदिक चंद्र गोचर • शनी चरण व वाहन • अंकशास्त्र विश्लेषण",
        "select_lang": "🌐 भाषा निवडा",
        "profile_heading": "👤 जातक जन्म कुंडली व ज्योतिषीय पाया",
        "edit_profile_expander": "✏️ जन्म तपशील भरा किंवा बदला",
        "input_name": "पूर्ण नाव",
        "input_dob": "जन्म तारीख",
        "input_tob": "जन्म वेळ",
        "input_place": "जन्म ठिकाण (शहर, देश)",
        "input_nakshatra": "जन्म नक्षत्र",
        "save_profile_btn": "💾 जन्म तपशील सेव्ह करा",
        "profile_saved_msg": "✅ माहिती यशस्वीरित्या सेव्ह केली गेली!",
        "birth_details_sub": "जन्म माहिती",
        "janma_star_label": "जन्म नक्षत्र",
        "moon_rashi_label": "चंद्र रास",
        "nak_personality_title": "🌟 जन्म नक्षत्र व्यक्तिमत्त्व व स्वभाव वैशिष्ट्ये",
        "num_title": "🔢 अंकशास्त्र रूपरेषा व स्थायी स्वभाव फळ",
        "mulank_label": "मूलांक (स्वभाव)",
        "bhagyank_label": "भाग्यांक (भाग्य मार्ग)",
        "namank_label": "नामांक (नावाचा प्रभाव)",
        "fixed_prediction_title": "✨ जीवनप्रवासाचे अंकशास्त्रीय फलादेश",
        "paya_card_title": "🪐 सद्य शनीचा पाया (चरण प्रभाव व फळ)",
        "transit_timeline_lbl": "सध्याचा गोचर कालावधी (Timeline)",
        "paya_impact_lbl": "शनी पाया प्रभाव व जीवन फल",
        "paya_remedies_lbl": "🪔 शनी पाया शांतता व संरक्षक वैदिक उपाय",
        "btn_view_forecast": "🔮 आजचे आणि पुढील ७ दिवसांचे भविष्य पहा ➔",
        "btn_back_profile": "⬅️ जातक कुंडलीवर परत जा",
        "forecast_page_title": "🔮 वैश्विक नवतारा गोचर व दैनंदिन फलादेश",
        "today_card_title": "🌟 आजचे सक्रिय त्रिकोणीय वैश्विक मार्गदर्शन",
        "current_active_nak": "सद्य चंद्र नक्षत्र",
        "current_tara": "सक्रिय नवतारा",
        "saturn_vahan_lbl": "आजचे शनी वाहन",
        "personal_day_lbl": "आजचा वैयक्तिक दिवस अंक",
        "today_directives": "🎯 आजच्या कृतीसाठी मुख्य दिशा व फलादेश",
        "today_remedies_lbl": "🪔 आजचे त्रि-स्तरीय अनुशंसित उपाय",
        "navtara_matrix_title": "🗓️ ७-दिवसीय चंद्र गोचर व दैनिक वेळापत्रक",
        "matrix_instruction": "सविस्तर फलादेश आणि उपाय पाहण्यासाठी खालील कोणत्याही दिवसावर क्लिक करा.",
        "col_status": "स्थिती",
        "col_window": "कालावधी (IST)",
        "col_nak": "चंद्र नक्षत्र",
        "col_series": "नवतारा चक्र",
        "col_vahan": "शनी वाहन",
        "planets_btn": "🌌 ग्रह स्थिती पहा (लाहिरी अयन)",
        "planets_hide_btn": "🔼 ग्रह स्थिती लपवा",
        "window_lbl": "सक्रिय वेळ",
        "series_lbl": "मालिका",
        "predictions_lbl": "सविस्तर फलादेश",
        "remedies_lbl": "या दिवसासाठी विशेष उपाय"
    },
    "gu": {
        "app_title": "✨ નવતારા પલ્સ (Navtara Pulse)",
        "app_tagline": "સચોટ વૈદિક ચંદ્ર ગોચર • શનિ ચરણ અને વાહન • અંકશાસ્ત્ર વિશ્લેષણ",
        "select_lang": "🌐 ભાષા પસંદ કરો",
        "profile_heading": "👤 જાતક જન્મ વિગતો અને જ્યોતિષીય પાયો",
        "edit_profile_expander": "✏️ જન્મ વિગતો દાખલ કરો અથવા સુધારો",
        "input_name": "પૂરું નામ",
        "input_dob": "જન્મ તારીખ",
        "input_tob": "જન્મ સમય",
        "input_place": "જન્મ સ્થળ (શહેર, દેશ)",
        "input_nakshatra": "જન્મ નક્ષત્ર",
        "save_profile_btn": "💾 જન્મ વિગતો સાચવો",
        "profile_saved_msg": "✅ વિગતો સફળતાપૂર્વક સાચવવામાં આવી!",
        "birth_details_sub": "જન્મ વિગતો",
        "janma_star_label": "જન્મ નક્ષત્ર",
        "moon_rashi_label": "ચંદ્ર રાશિ",
        "nak_personality_title": "🌟 જન્મ નક્ષત્ર વ્યક્તિત્વ અને મૂળ સ્વભાવ",
        "num_title": "🔢 અંકશાસ્ત્ર રૂપરેખા અને મૂળ સ્વભાવ ફળ",
        "mulank_label": "મૂળાંક (સ્વભાવ)",
        "bhagyank_label": "ભાગ્યાંક (ભાગ્ય પથ)",
        "namank_label": "નામાંક (નામ સ્પંદન)",
        "fixed_prediction_title": "✨ આજીવન અંકશાસ્ત્ર ફલાદેશ અને સ્વભાવ",
        "paya_card_title": "🪐 વર્તમાન શનિ પાયા (ચરણ ફળ અને પ્રભાવ)",
        "transit_timeline_lbl": "વર્તમાન ગોચર સમયગાળો (Timeline)",
        "paya_impact_lbl": "શનિ પાયા પ્રભાવ અને જીવન ફળ",
        "paya_remedies_lbl": "🪔 શનિ પાયા શાંતિ અને સુરક્ષાત્મક વૈદિક ઉપાયો",
        "btn_view_forecast": "🔮 આજનું અને આગામી ૭ દિવસનું ફલાદેશ જુઓ ➔",
        "btn_back_profile": "⬅️ જાતક પ્રોફાઇલ પર પાછા જાઓ",
        "forecast_page_title": "🔮 બ્રહ્માંડીય નવતારા ગોચર અને દૈનિક ફલાદેશ",
        "today_card_title": "🌟 આજનો સક્રિય ત્રિ-સ્તરીય બ્રહ્માંડીય સમન્વય",
        "current_active_nak": "સક્રિય ચંદ્ર નક્ષત્ર",
        "current_tara": "વર્તમાન નવતારા સ્થિતિ",
        "saturn_vahan_lbl": "આજનું શનિ વાહન",
        "personal_day_lbl": "વ્યક્તિગત દિવસ અંક સ્પંદન",
        "today_directives": "🎯 આજના કાર્ય માટે મુખ્ય માર્ગદર્શન",
        "today_remedies_lbl": "🪔 આજના ત્રિ-સ્તરીય સૂચવેલા ઉપાયો",
        "navtara_matrix_title": "🗓️ ૭-દિવસીય ચંદ્ર ગોચર અને દૈનિક કોષ્ટક",
        "matrix_instruction": "વિગતવાર ફલાદેશ અને ઉપાયો જોવા માટે નીચે આપેલા કોઈપણ દિવસ પર ક્લિક કરો.",
        "col_status": "સ્થિતિ",
        "col_window": "સમયગાળો (IST)",
        "col_nak": "ચંદ્ર નક્ષત્ર",
        "col_series": "નવતારા ચક્ર",
        "col_vahan": "શનિ વાહન",
        "planets_btn": "🌌 સ્પષ્ટ નિરયણ ગ્રહ સ્થિતિ જુઓ (લાહિરી)",
        "planets_hide_btn": "🔼 ગ્રહ સ્થિતિ છુપાવો",
        "window_lbl": "સક્રિય સમય",
        "series_lbl": "શ્રેણી",
        "predictions_lbl": "વિગતવાર ફલાદેશ",
        "remedies_lbl": "આ દિવસ માટેના વિશેષ ઉપાયો"
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
        "Janma": "Self, physical energy, vital forces, beginning of a cycle.",
        "Sampat": "Wealth, assets, material prosperity, financial gains.",
        "Vipat": "Obstacles, danger, financial setbacks, accidents. High caution.",
        "Kshema": "Well-being, safety, prosperity, comfort, recovery.",
        "Pratyari": "Obstacles, enmity, disputes, opposition, disagreements.",
        "Sadhana": "Success through effort, achievements, spiritual fulfillment.",
        "Vadha": "Severe distress, destruction, extreme loss, heavy friction.",
        "Mitra": "Friendship, harmony, helpful alliances, cordial contacts.",
        "Ati-Mitra": "Great friend, peak auspiciousness, extreme gains, mutual joy."
    },
    "hi": {
        "Janma": "जन्म तारा: शारीरिक ऊर्जा, आत्म-विकास, नए संकल्प।",
        "Sampat": "सम्पत तारा: धन, समृद्धि, व्यापार लाभ और भौतिक संपन्नता।",
        "Vipat": "विपत तारा: संकट, अचानक बाधा, जोखिम से बचाव आवश्यक।",
        "Kshema": "क्षेम तारा: कल्याण, पारिवारिक शांति, सुरक्षा व आरोग्य।",
        "Pratyari": "प्रत्यरि तारा: वाद-विवाद, प्रतिद्वंद्विता, शत्रुता से सावधान रहें।",
        "Sadhana": "साधना तारा: संकल्प सिद्धि, परिश्रम का फल, लक्ष्य प्राप्ति।",
        "Vadha": "वध तारा: उच्च जोखिम, कष्ट, महत्वपूर्ण कार्यों का त्याग आवश्यक।",
        "Mitra": "मित्र तारा: सौहार्द, सहयोग, लाभ व सुखद संबंध।",
        "Ati-Mitra": "अति-मित्र तारा: परम कल्याणकारी, सर्वोच्च सफलता, अति शुभ समय।"
    },
    "mr": {
        "Janma": "जन्म तारा: शारीरिक ऊर्जा, आत्म-विकास, नवी सुरुवात.",
        "Sampat": "संपत तारा: संपत्ती, भरभराट, आर्थिक लाभ व समृद्धी.",
        "Vipat": "विपत तारा: संकट, अचानक विघ्ने, सावधगिरी बाळगावी.",
        "Kshema": "क्षेम तारा: कल्याण, सुरक्षितता, आरोग्य व शांतता.",
        "Pratyari": "प्रत्यरी तारा: वादविवाद, विरोध, मतभेद यांपासून दूर राहा.",
        "Sadhana": "साधना तारा: कामात यश, ध्येयपूर्ती व सिद्धिदायक काळ.",
        "Vadha": "वध तारा: अत्यंत अडचणींचा काळ, मोठे निर्णय पुढे ढकलावेत.",
        "Mitra": "मित्र तारा: सलोखा, सहकार्य, यश व हितकारक संबंध.",
        "Ati-Mitra": "अति-मित्र तारा: सर्वोच्च शुभ, कार्यसिद्धी व प्रचंड लाभ."
    },
    "gu": {
        "Janma": "જન્મ તારા: શારીરિક ઊર્જા, આત્મ-વિકાસ, નવી શરૂઆત.",
        "Sampat": "સંપત તારા: સંપત્તિ, આર્થિક પ્રગતિ અને સ્થિરતા.",
        "Vipat": "વિપત તારા: મુશ્કેલીઓ, અણધાર્યા વિલંબ, ભારે સાવચેતી જરૂરી.",
        "Kshema": "ક્ષેમ તારા: કલ્યાણ, રક્ષણ, સુખ-શાંતિ અને સ્વાસ્થ્ય લાભ.",
        "Pratyari": "પ્રત્યરિ તારા: વિરોધ, વાદ-વિવાદ અને અવરોધોથી સાવધાન.",
        "Sadhana": "સાધના તારા: સિદ્ધિ, સખત મહેનતનું શુભ ફળ અને સફળતા.",
        "Vadha": "વધ તારા: જોખમ, નુકસાન, અતિ સંયમ અને શાંતિ રાખવી.",
        "Mitra": "મિત્ર તારા: મિત્રતા, મદદ, સહયોગ અને સાનુકૂળ પરિસ્થિતિ.",
        "Ati-Mitra": "અતિ-મિત્ર તારા: શ્રેષ્ઠ સહયોગ, પરમ શુભ અને ઉત્તમ પરિણામો."
    }
}

SHANI_VAHANS = {
    "en": {
        1: {"name": "🐴 Ghoda (Horse)", "desc": "Speed, rapid progress, physical energy, and swift victory over hurdles."},
        2: {"name": "🫏 Gadha (Donkey)", "desc": "Heavy effort, hard labor, perseverance required, delayed appreciation."},
        3: {"name": "🦊 Siyar (Jackal)", "desc": "Deceit, caution advised, watch out for misdirection and hidden adversaries."},
        4: {"name": "🐘 Hathi (Elephant)", "desc": "Royalty, prestige, elevation in status, wealth, and authority."},
        5: {"name": "🐂 Bail (Bull)", "desc": "Steady, continuous progress through discipline and consistent routine."},
        6: {"name": "🦁 Sher (Lion)", "desc": "Courage, supreme confidence, victory in competitions, fearless leadership."},
        7: {"name": "🐦‍⬛ Kowwa (Crow)", "desc": "Restlessness, minor disagreements, travel, scattered focus; keep calm."},
        8: {"name": "🦚 Mayur (Peacock)", "desc": "Joy, artistic harmony, heartwarming news, domestic celebration."},
        9: {"name": "🦢 Hans (Swan)", "desc": "Wisdom, tranquility, mental peace, spiritual and financial stability."}
    },
    "hi": {
        1: {"name": "🐴 घोड़ा (Horse)", "desc": "तीव्र प्रगति, ऊर्जा, त्वरित विजय और साहसिक निर्णय लेने का समय।"},
        2: {"name": "🫏 गधा (Donkey)", "desc": "कठिन परिश्रम, अत्यधिक भागदौड़; धैर्य और निष्ठा से कार्य करते रहें।"},
        3: {"name": "🦊 सियार (Jackal)", "desc": "सतर्कता आवश्यक; छल-कपट या भ्रामक सलाह से सावधान रहें।"},
        4: {"name": "🐘 हाथी (Elephant)", "desc": "राजसी सम्मान, धन लाभ, पद-प्रतिष्ठा और वरिष्ठों का सहयोग।"},
        5: {"name": "🐂 बैल (Bull)", "desc": "स्थिर व निरंतर प्रगति; नियमित अनुशासन से सफलता प्राप्त होगी।"},
        6: {"name": "🦁 सिंह (Lion)", "desc": "अदम्य साहस, प्रतियोगिता में विजय और नेतृत्व क्षमता का विस्तार।"},
        7: {"name": "🐦‍⬛ कौआ (Crow)", "desc": "मानसिक चंचलता, अनावश्यक वाद-विवाद या यात्रा; वाणी पर संयम रखें।"},
        8: {"name": "🦚 मयूर (Peacock)", "desc": "प्रसन्नता, रचनात्मक सफलता, शुभ समाचार और संबंधों में मधुरता।"},
        9: {"name": "🦢 हंस (Swan)", "desc": "मानसिक शांति, विवेक, आध्यात्मिक उन्नति और स्थायी सुख-समृद्धि।"}
    },
    "mr": {
        1: {"name": "🐴 घोडा (Horse)", "desc": "जलद प्रगती, उत्साह, त्वरेने यश आणि धाडसी पावले उचलण्याचा काळ."},
        2: {"name": "🫏 गाढव (Donkey)", "desc": "कठोर परिश्रम, जास्तीची धावपळ; संयम बाळगून काम करत राहा."},
        3: {"name": "🦊 कोल्हा (Jackal)", "desc": "सावधगिरी आवश्यक; फसवणूक किंवा चुकीच्या सल्ल्यापासून सावध राहा."},
        4: {"name": "🐘 हत्ती (Elephant)", "desc": "राजमान्यता, सन्मान, आर्थिक वृद्धी आणि वरिष्ठांचे मोलाचे सहकार्य."},
        5: {"name": "🐂 बैल (Bull)", "desc": "स्थिर व संथ प्रगती; नियमित शिस्तीने दीर्घकालीन यश मिळेल."},
        6: {"name": "🦁 सिंह (Lion)", "desc": "प्रचंड आत्मविश्वास, संकटांवर मात आणि नेतृत्व गुणांचा विकास."},
        7: {"name": "🐦‍⬛ कावळा (Crow)", "desc": "मानसिक अस्वस्थता, किरकोळ वाद किंवा प्रवास; संवादात शांतता राखा."},
        8: {"name": "🦚 मोर (Peacock)", "desc": "आनंद, कौटुंबिक सौख्य, शुभ वार्ता आणि मनसोक्त समाधान."},
        9: {"name": "🦢 हंस (Swan)", "desc": "मानसिक शांतता, विवेक, आध्यात्मिक उन्नती आणि समाधानकारक स्थैर्य."}
    },
    "gu": {
        1: {"name": "🐴 ઘોડો (Horse)", "desc": "ઝડપી પ્રગતિ, ઉત્સાહ, વિજય અને સાહસિક નિર્ણયો માટે ઉત્તમ સમય."},
        2: {"name": "🫏 ગધેડો (Donkey)", "desc": "સખત મહેનત અને દોડધામ; ધીરજ રાખીને કામ પૂર્ણ કરવા પર ધ્યાન આપો."},
        3: {"name": "🦊 શિયાળ (Jackal)", "desc": "સાવધાની જરૂરી; છેતરપિંડી કે ગેરમાર્ગે દોરતી સલાહથી બચવું."},
        4: {"name": "🐘 હાથી (Elephant)", "desc": "રાજસી માન-સન્માન, ધનલાભ, પદ-પ્રતિષ્ઠા અને સમૃદ્ધિની પ્રાપ્તિ."},
        5: {"name": "🐂 બળદ (Bull)", "desc": "સ્થિર અને ધીમી પણ મક્કમ પ્રગતિ; નિયમિતતા લાભ કરાવશે."},
        6: {"name": "🦁 સિંહ (Lion)", "desc": "અડગ હિંમત, હરીફો પર વિજય અને પ્રભાવશાળી નેતૃત્વ."},
        7: {"name": "🐦‍⬛ કાગડો (Crow)", "desc": "મનની ચંચળતા, નાની બાબતોમાં વિવાદ કે મુસાફરી; વાણીમાં સંયમ રાખવો."},
        8: {"name": "🦚 મોર (Peacock)", "desc": "આનંદ, સર્જનાત્મક સફળતા, પારિવારિક સુખ અને શુભ સમાચાર."},
        9: {"name": "🦢 હંસ (Swan)", "desc": "માનસિક શાંતિ, ઊંડો વિવેક, આધ્યાત્મિક જ્ઞાન અને સ્થિર સુખ."}
    }
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

NAKSHATRA_TRAITS = {
    0: {  # Ashwini
        "en": "Pioneering, swift, energetic, and naturally inclined towards healing and adventure. Possesses a strong desire for independence and quick execution.",
        "hi": "स्फूर्तिवान, साहसी, त्वरित निर्णय लेने वाले एवं प्राकृतिक आरोग्य प्रदाता। स्वतंत्रता प्रिय और किसी भी कार्य को तत्परता से आरंभ करने में कुशल।",
        "mr": "उत्साही, धाडसी, तत्पर आणि स्वतंत्र विचारांचे. नवीन संकल्पनांना त्वरित मूर्त रूप देण्याची जन्मजात क्षमता.",
        "gu": "ઉત્સાહી, સાહસિક, ઝડપી નિર્ણયો લેનાર અને કુદરતી ઉપચારક. નવીન કાર્યોની ઝડપી શરૂઆત કરવામાં માહિર."
    },
    1: {  # Bharani
        "en": "Governed by Venus and Yama. High personal magnetism, courageous, uncompromising truth-seeker, capable of handling immense responsibility and radical transformations.",
        "hi": "शुक्र एवं यम के प्रभाव से युक्त। चुंबकीय व्यक्तित्व, सत्यप्रिय, साहसी एवं गंभीर उत्तरदायित्व निभाने में दक्ष। जीवन में बड़े रूपांतरणों से गुजरकर दृढ़ता प्राप्त करते हैं।",
        "mr": "शुक्र व यम यांच्या प्रभावाखाली. आकर्षक व्यक्तिमत्त्व, स्पष्टवक्ते, निष्ठावान आणि कठीण प्रसंगांना आत्मविश्वासाने सामोरे जाणारे.",
        "gu": "શુક્ર અને યમનું આધિપત્ય. આકર્ષક, સત્યવાદી, સાહસી અને અતિ મહત્વની જવાબદારીઓ સુપેરે નિભાવનાર દ્રઢ વ્યક્તિત્વ."
    },
    2: {  # Krittika
        "en": "Sharp intellect, heroic willpower, direct and purifying presence. Natural leader with a fiery determination to cut through deception.",
        "hi": "तीक्ष्ण बुद्धि, प्रखर इच्छाशक्ति एवं तेजवान व्यक्तित्व। सत्य के प्रति निष्ठावान, नेतृत्व क्षमता से परिपूर्ण और अन्याय का दृढ़ विरोध करने वाले।",
        "mr": "तीक्ष्ण बुद्धिमत्ता, प्रखर नेतृत्व आणि निडर स्वभाव. सत्याची बाजू ठामपणे मांडणारे आणि शिस्तप्रिय.",
        "gu": "તેજસ્વી બુદ્ધિ, અડગ મનોબળ અને નેતૃત્વ ગુણ. સત્ય માટે અડગ રહેનાર અને શિસ્તબદ્ધ વ્યક્તિત્વ."
    },
    3: {  # Rohini
        "en": "Charming, artistic, grounded, and emotionally nurturing. Possesses exceptional aesthetic vision, persuasive speech, and high creative elegance.",
        "hi": "आकर्षक, कलाप्रेमी, स्नेही और पोषणकर्ता। उच्च सौंदर्य दृष्टि, मधुर वाणी एवं पारिवारिक व भौतिक समृद्धि को आकर्षित करने वाले।",
        "mr": "कलाप्रेमी, आकर्षक, भावनिक समतोल आणि समृद्धी आकर्षित करणारे. मधुर संभाषण आणि सर्जनशीलता हे मूळ गुण.",
        "gu": "કળાપ્રેમી, આકર્ષક, સૌમ્ય અને સર્જનાત્મક. મધુર વાણી અને સૌંદર્ય પ્રત્યે ઊંડો પ્રેમ ધરાવતું વ્યક્તિત્વ."
    },
    4: {  # Mrigashira
        "en": "Inquisitive, perceptive, gentle, and a perpetual seeker of knowledge and truth. Highly adaptable, communicative, and socially charming.",
        "hi": "जिज्ञासु, शोधक प्रवृत्ति, सौम्य और निरंतर ज्ञान पिपासु। अनुकूलनशील, स्पष्ट वक्ता और संवेदनशील व्यक्तित्व।",
        "mr": "जिज्ञासू, संशोधक वृत्ती, मनमिळाऊ आणि सदैव ज्ञानप्राप्तीची आवड बाळगणारे. उत्तम संवादकौशल्य.",
        "gu": "જિજ્ઞાસુ, સંશોધક સ્વભાવ, નમ્ર અને ઉત્તમ સંવાદક. સતત નવી બાબતો શીખવાની ધગશ ધરાવનાર."
    },
    5: {  # Ardra
        "en": "Sharp analytical power, intense emotional depth, resilient in crises. Excels in cutting-edge research, technology, and transformative problem-solving.",
        "hi": "तीक्ष्ण विश्लेषणात्मक क्षमता, आंतरिक गहराई एवं संकटों से उबरने में सक्षम। तकनीक, अनुसंधान एवं जटिल समस्याओं के समाधान में कुशल।",
        "mr": "सखोल विश्लेषक, आव्हानांवर मात करणारे आणि संकटसमयी संयम राखणारे. तंत्रज्ञान व संशोधनात आघाडीवर.",
        "gu": "ઊંડા વિશ્લેષક, પડકારો સામે મક્કમ રહેનાર અને સંશોધનમાં અગ્રેસર. મુશ્કેલ પરિસ્થિતિઓમાં પણ અડગ."
    },
    6: {  # Punarvasu
        "en": "Benevolent, optimistic, resilient, and spiritually grounded. Possesses the unique ability to renew oneself and bounce back from any setback.",
        "hi": "उदार, आशावादी, सात्विक एवं आध्यात्मिक दृष्टि। जीवन के उतार-चढ़ावों से पुनः उठ खड़े होने और सबको साथ लेकर चलने की अद्भुत क्षमता।",
        "mr": "सकारात्मक, परोपकारी, शांत आणि पुनरुत्थानाची विलक्षण ताकद बाळगणारे. अध्यात्म आणि नीतिमूल्यांची आवड.",
        "gu": "ઉદાર, આશાવાદી, પુનરાગમનની અદભુત ક્ષમતા અને આધ્યાત્મિક વિચારો ધરાવનાર વ્યક્તિત્વ."
    },
    7: {  # Pushya
        "en": "Nurturing, ethically steadfast, disciplined, and deeply wise. Known as the king of Nakshatras; grants dependable guidance, patience, and lasting prosperity.",
        "hi": "पोषणकर्ता, धर्मपरायण, अनुशासित एवं परम विवेकशील। नक्षत्रों का राजा; विश्वसनीय मित्र, धैर्यवान मार्गदर्शक एवं स्थायी प्रगति प्रदाता।",
        "mr": "सर्वश्रेष्ठ नक्षत्र, मार्गदर्शक, संयमी आणि अत्यंत प्रामाणिक. कुटुंब व समाजासाठी आधारस्तंभ.",
        "gu": "પોષક, ધાર્મિક, અનુશાસિત અને જ્ઞાની. નક્ષત્રોનો રાજા; ધીરજવાન સલાહકાર અને સ્થિર પ્રગતિ કરનાર."
    },
    8: {  # Ashlesha
        "en": "Deeply intuitive, strategic, protective, and mentally formidable. Possesses penetrating psychological insight and formidable defensive resilience.",
        "hi": "गहन अंतर्दृष्टि, कूटनीतिक दक्षता, सतर्क और रणनीतिक विचारक। मानवीय मनोविज्ञान को समझने और अपनी सीमाओं की रक्षा करने में अद्वितीय।",
        "mr": "तीव्र अंतर्ज्ञान, मुत्सद्दी, सावध आणि धोरणी. मानवी स्वभाव चटकन ओळखण्याची क्षमता.",
        "gu": "ઊંડી આંતરસૂઝ, વ્યૂહાત્મક વિચારક અને રક્ષણાત્મક સ્વભાવ. લોકોના મનની વાત તુરંત પારખી લેનાર."
    },
    9: {  # Magha
        "en": "Dignified, regal, commanding, and connected to ancestral roots. Naturally authoritative with high self-respect and strong moral duty.",
        "hi": "राजसी स्वभाव, स्वाभिमानी, गौरवशाली एवं पैतृक संस्कारों से युक्त। स्वाभाविक नेतृत्व, मर्यादा का पालन और सामाजिक सम्मान के धनी।",
        "mr": "राजेशाही रुबाब, स्वाभिमानी, पूर्वजांच्या परंपरेचा अभिमान बाळगणारे आणि प्रभावी नेतृत्व करणारे.",
        "gu": "રાજસી પ્રભાવ, સ્વાભિમાની, નેતૃત્વ ગુણોથી ભરપૂર અને કુળપરંપરાને જાળવનાર આદરણીય વ્યક્તિત્વ."
    },
    10: {  # Purva Phalguni
        "en": "Warm, charismatic, artistic, and generous. Enjoys refined pleasures, social gatherings, harmonious partnerships, and creative endeavors.",
        "hi": "उदार, आकर्षक, कलाप्रिय एवं स्नेहमयी। जीवन का आनंद लेने, संबंधों को संजोने और रचनात्मक कार्यों में विशेष रुचि रखने वाले।",
        "mr": "आनंदी, कलाप्रेमी, उदार आणि मैत्रीपूर्ण संबंध जपणारे. सामाजिक प्रतिष्ठा आणि सौंदर्यदृष्टीचे धनी.",
        "gu": "આનંદી, આકર્ષક, કળાપ્રેમી અને ઉદાર. સંબંધોમાં મધુરતા અને જીવનનો ઉત્સાહ જાળવનાર."
    },
    11: {  # Uttara Phalguni
        "en": "Steadfast, trustworthy, philanthropic, and honorable. Excels in establishing enduring agreements, structured leadership, and service to society.",
        "hi": "सदाचारी, सत्यनिष्ठ, परोपकारी एवं सम्मानित। दीर्घकालिक मित्रताओं, वचनबद्धता और न्यायपूर्ण नेतृत्व के लिए जाने जाते हैं।",
        "mr": "विश्वासू, कर्तव्यदक्ष, परोपकारी आणि न्यायाची चाड असणारे. दिलेल्या शब्दाला जागणारे व्यक्तिमत्त्व.",
        "gu": "વિશ્વાસુ, કર્તવ્યનિષ્ઠ, પરોપકારી અને વચનપાલક. સ્થિર અને ન્યાયપૂર્ણ નેતૃત્વ કરનાર."
    },
    12: {  # Hasta
        "en": "Skillful, resourceful, dexterous, and intellectually witty. Possesses the golden touch for detailed craft, negotiations, and systematic work.",
        "hi": "दक्ष, कार्यकुशल, बुद्धिमान एवं व्यावहारिक। हस्तकला, योजना निर्माण, व्यापार एवं समाधानपरक कार्यों में अद्वितीय निपुणता।",
        "mr": "कलाकुशल, व्यवहारी, चतुर आणि अचूक नियोजन करणारे. कोणत्याही समस्येवर त्वरित तोडगा काढणारे.",
        "gu": "કુશળ, વ્યવહારુ, બુદ્ધિશાળી અને આયોજનબદ્ધ. કાર્યોમાં ચોકસાઈ અને રચનાત્મકતા લાવનાર."
    },
    13: {  # Chitra
        "en": "Brilliant architect, aesthetic visionary, magnetic, and perfectionist. Driven by a desire to structure, build, and adorn the world with beauty.",
        "hi": "सौंदर्यदृष्टा, सृजनशील, आकर्षक एवं वास्तुकार बुद्धि। हर कार्य में पूर्णता और सुंदरता लाने वाले; स्वतंत्र और आत्मविश्वासी।",
        "mr": "सर्जनशील, आकर्षक, परिपूर्णतेची आवड आणि उत्तम सौंदर्यदृष्टी बाळगणारे स्वतंत्र व्यक्तिमत्त्व.",
        "gu": "સર્જનાત્મક, કળાપારખુ, આકર્ષક અને પરફેક્શનિસ્ટ. કાર્યોને સુંદર અને વ્યવસ્થિત રૂપ આપનાર."
    },
    14: {  # Swati
        "en": "Independent, diplomatic, flexible, and visionary. Values freedom, excels in business networking, fair trade, and graceful communication.",
        "hi": "स्वतंत्र, कूटनीतिज्ञ, लचीले और दूरदर्शी। स्वतंत्रता प्रिय, निष्पक्ष व्यापार, संवाद और सामाजिक संबंधों में कुशल।",
        "mr": "स्वतंत्र विचारांचे, मुत्सद्दी, लवचिक आणि दूरगामी विचार करणारे. उत्तम व्यावसायिक कौशल्य.",
        "gu": "સ્વતંત્ર, મુત્સદ્દી, દૂરંદેશી અને અનુકૂલનશીલ. વ્યવસાયિક સંબંધો અને સંવાદમાં નિપુણ."
    },
    15: {  # Vishakha
        "en": "Ambitious, single-minded, goal-oriented, and intensely determined. Focuses relentless energy until objectives are fully conquered.",
        "hi": "महत्वाकांक्षी, एकाग्रचित्त, लक्ष्य-उन्मुख एवं अथक परिश्रमी। जिस कार्य का संकल्प लेते हैं, उसे पूर्ण करके ही दम लेते हैं।",
        "mr": "ध्येयवेडे, चिकाटी असलेले, महत्त्वाकांक्षी आणि एकाग्र. ठरवलेले उद्दिष्ट साध्य करणारे खंबीर व्यक्तिमत्त्व.",
        "gu": "મહત્વાકાંક્ષી, અડગ, લક્ષ્ય-કેન્દ્રી અને પરિશ્રમી. ધારેલું કામ પૂરું કરીને જ જંપનાર."
    },
    16: {  # Anuradha
        "en": "Devoted, collaborative, friendly, and spiritually sensitive. Capable of uniting diverse groups and thriving even in distant lands.",
        "hi": "मैत्रीपूर्ण, निष्ठावान, आध्यात्मिक एवं सहयोगशील। विपरीत परिस्थितियों में भी सामंजस्य बनाने और विदेशी संपर्कों से लाभ पाने में दक्ष।",
        "mr": "मित्रता जपणारे, प्रामाणिक, आध्यात्मिक आणि सहकार्याची भावना असणारे. सर्वांना एकत्र आणण्याची हातोटी.",
        "gu": "મૈત્રીપૂર્ણ, વફાદાર, સંવેદનશીલ અને આધ્યાત્મિક. પ્રતિકૂળતામાં પણ સંતુલન જાળવી રાખનાર."
    },
    17: {  # Jyeshtha
        "en": "Protective, elder-like authority, formidable courage, and perceptive. Natural defender of family and high-stakes interests.",
        "hi": "रक्षक, वरिष्ठता का भाव, अदम्य साहसी और सतर्क। परिवार और सहयोगियों के सुरक्षा कवच, अधिकारपूर्ण नेतृत्व के धनी।",
        "mr": "ज्येष्ठता, धीरोदात्त, कुटुंबवत्सल आणि संकटात आधार देणारे प्रभावी व्यक्तिमत्त्व.",
        "gu": "રક્ષક, વડીલ જેવી પરિપક્વતા, સાહસી અને પરિસ્થિતિ પર કાબૂ મેળવવાની ઉત્તમ ક્ષમતા ધરાવનાર."
    },
    18: {  # Mula
        "en": "Profound, truth-seeking, radical investigator, penetrating the very root of matters. Capable of fearless transformation and philosophical depth.",
        "hi": "गहन अन्वेषक, सत्यनिष्ठ, मूल कारणों तक पहुँचने वाले। निर्भीक, पारंपरिक सीमाओं से परे सोचने वाले और दार्शनिक दृष्टि संपन्न।",
        "mr": "सखोल विचारवंत, मूळापर्यंत जाणारे आणि निर्भय. तत्त्वज्ञान आणि संशोधनात विशेष गती.",
        "gu": "ઊંડા અભ્યાસુ, સત્યશોધક, નિર્ભીક અને મૂળ સુધી જઈને સમસ્યાઓનો ઉકેલ લાવનાર દ્રષ્ટા."
    },
    19: {  # Purva Ashadha
        "en": "Invincible spirit, charismatic orator, optimistic, and proud. Inspires loyalty, wins debates, and thrives in challenging journeys.",
        "hi": "अपराजेय संकल्प, प्रभावशाली वक्ता, आशावादी और स्वाभिमानी। दूसरों को प्रेरित करने और जनसमर्थन प्राप्त करने में निपुण।",
        "mr": "अजिंक्य इच्छाशक्ती, प्रभावी वक्ते, आशावादी आणि स्वाभिमानी. संकटातही आत्मविश्वास न गमावणारे.",
        "gu": "અપરાજય મનોબળ, પ્રભાવશાળી વક્તા, આશાવાદી અને સ્વાભિમાની. લોકોને પ્રેરણા આપનાર."
    },
    20: {  # Uttara Ashadha
        "en": "Virtuous, patient, enduring, and victorious through righteousness. Known for unwavering integrity, modesty, and universal respect.",
        "hi": "धैर्यवान, सत्यप्रिय, नीतिवान एवं दीर्घकालिक विजयी। उच्च चारित्रिक निष्ठा, विनम्रता और समाज में स्थायी सम्मान प्राप्त करने वाले।",
        "mr": "संयमी, चारित्र्यसंपन्न, न्यायप्रिय आणि खात्रीशीर यश मिळवणारे. समाजात आदराचे स्थान असणारे व्यक्तिमत्त्व.",
        "gu": "સંયમી, નીતિવાન, ધૈર્યવાન અને સત્યના માર્ગે વિજય મેળવનાર. સમાજમાં આદરણીય સ્થાન પ્રાપ્ત કરનાર."
    },
    21: {  # Shravana
        "en": "Attentive listener, scholarly, wise, and devoted to oral tradition and learning. Possesses remarkable memory and organizational acumen.",
        "hi": "उत्तम श्रोता, विद्वान, विद्यानुरागी एवं विवेकशील। गहन स्मरणशक्ति, संगठनात्मक कौशल और सुसंस्कृत आचरण के प्रतीक।",
        "mr": "उत्कृष्ट श्रोता, अभ्यासू, सुसंस्कृत आणि उत्तम स्मरणशक्ती असलेले. ज्ञान संपादन आणि प्रसारात आघाडीवर.",
        "gu": "સારો શ્રોતા, વિદ્વાન, સ્મરણશક્તિમાં તેજ અને જ્ઞાનપ્રિય. વ્યવસ્થિત અને સન્માનનીય જીવનશૈલી ધરાવનાર."
    },
    22: {  # Dhanishta
        "en": "Rhythmic, prosperous, courageous, and philanthropic. Naturally inclined towards music, real estate, community leadership, and wealth creation.",
        "hi": "समृद्धिदायक, साहसी, संगीत व कला प्रेमी एवं उदार। सामाजिक नेतृत्व, अचल संपत्ति निर्माण और मान-सम्मान के धनी।",
        "mr": "उदार, संगीत व कलाप्रेमी, संपत्ती व कीर्ती संपादन करणारे आणि समाजात सन्मान मिळवणारे.",
        "gu": "ધનવાન, સાહસિક, સંગીતપ્રેમી અને ઉદાર. રિયલ એસ્ટેટ, વ્યવસાય અને નેતૃત્વમાં આગળ વધનાર."
    },
    23: {  # Shatabhisha
        "en": "Visionary, secretive, independent healer, and philosophical thinker. Unravels deep scientific, occult, or astronomical enigmas.",
        "hi": "दूरदर्शी, रहस्यमयी, स्वतंत्र विचारक एवं शोधक। गूढ़ विज्ञान, आरोग्य विद्या और जीवन की सूक्ष्म गुत्थियों को सुलझाने में कुशल।",
        "mr": "दूरदृष्टी असलेले, गूढ ज्ञान व विज्ञानाची आवड असणारे आणि स्वतंत्र वृत्तीचे संशोधक.",
        "gu": "દૂરંદેશી, રહસ્યમયી, સ્વતંત્ર વિચારક અને ગૂઢ વિદ્યા તેમજ વિજ્ઞાનમાં ઊંડો રસ ધરાવનાર."
    },
    24: {  # Purva Bhadrapada
        "en": "Passionate, philosophically intense, transformative, and sincere. Dedicated to lofty ideals and unyielding in times of profound change.",
        "hi": "गंभीर, दार्शनिक, तपस्वी स्वभाव और आदर्शवादी। उच्च सिद्धांतों के प्रति समर्पित, निष्कपट और आंतरिक रूपांतरण के संवाहक।",
        "mr": "तत्त्वनिष्ठ, तीव्र वैचारिक क्षमता आणि अंतर्मुख. आदर्श मूल्यांसाठी सर्वस्व पणाला लावणारे.",
        "gu": "તત્વચિંતક, ગંભીર, આદર્શવાદી અને પરિવર્તનશીલ. પોતાના સિદ્ધાંતો માટે અડગ રહેનાર."
    },
    25: {  # Uttara Bhadrapada
        "en": "Serene, wise, compassionate, and self-controlled. Possesses deep psychic stability, generosity, and mastery over human passions.",
        "hi": "शांत, विवेकी, करुणामयी और आत्म-नियंत्रित। गहन मानसिक स्थिरता, परोपकार और आध्यात्मिक ज्ञान से संपन्न संतुलित व्यक्तित्व।",
        "mr": "शांत, संयमी, दयाळू आणि आध्यात्मिक परिपक्वता असलेले. समाधानाचा आणि स्थिरतेचा मार्ग निवडणारे.",
        "gu": "શાંત, દયાળુ, સંયમી અને આધ્યાત્મિક જ્ઞાનથી સમૃદ્ધ. બીજાનું ભલું કરવાની સતત ભાવના રાખનાર."
    },
    26: {  # Revati
        "en": "Gentle, compassionate, highly intuitive, and artistic. Safe protector of wayfarers, deeply empathetic, and spiritually liberated.",
        "hi": "सौम्य, दयालु, कलात्मक और परम अंतर्ज्ञानी। दूसरों के प्रति असीम संवेदना, सुरक्षित मार्गदर्शक और आध्यात्मिक मोक्ष के अभिलाषी।",
        "mr": "अत्यंत दयाळू, संवेदनशील, कल्पक आणि आध्यात्मिक प्रवृत्तीचे. सर्वांना प्रेम व मार्गदर्शन देणारे.",
        "gu": "સૌમ્ય, પરોપકારી, કળાપ્રેમી અને ઊંડી આંતરસૂઝ ધરાવનાર. સૌનું કલ્યાણ ઈચ્છનાર પવિત્ર હૃદય."
    }
}

def calculate_birth_chart(dob: datetime.date, tob: datetime.time, tz_offset_hours: float = 5.5):
    """Calculates Moon Nakshatra, Pada, and Moon Rashi from DOB and TOB using Swiss Ephemeris Lahiri."""
    birth_dt_local = datetime.datetime.combine(dob, tob)
    birth_dt_utc = birth_dt_local - datetime.timedelta(hours=tz_offset_hours)
    jd_birth = dt_to_jd(birth_dt_utc)
    moon_lon = get_sidereal_lon(jd_birth, swe.MOON)
    nak_idx, pada = lon_to_nakshatra(moon_lon)
    rashi_idx, rashi_deg = lon_to_rashi(moon_lon)
    return nak_idx, pada, rashi_idx, rashi_deg

def get_nakshatra_description(nak_idx: int, lang: str = "en") -> str:
    traits_dict = NAKSHATRA_TRAITS.get(nak_idx, NAKSHATRA_TRAITS[1])
    return traits_dict.get(lang, traits_dict.get("en", ""))

PROFILE_FILE = "user_profile.json"

def load_user_profile() -> dict:
    defaults = {
        "name": "Okesh",
        "dob": datetime.date(1984, 1, 13),
        "tob": datetime.time(14, 0),
        "place": "Chhatrapati Sambhajinagar, India",
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
        if lang == "hi":
            name = "रजत पाया (Silver Feet / चाँदी का पाया) 🥈"
            grade = "परम शुभ एवं रक्षक पाया (अति शुभ फलदायी)"
            desc = ("मेष चन्द्र राशि के जातकों के लिए प्रथम चरण की साढ़े साती चल रही है, परंतु शनि देव रजत (चाँदी) के पाए पर विराजमान होकर "
                    "आए हैं। यह पाया एक दिव्य सुरक्षा कवच की भाँति कार्य करता है। यह आर्थिक संकटों से सुरक्षा, परिवार में सुख, ऋणमुक्ति "
                    "और वरिष्ठों का आशीर्वाद सुनिश्चित करता है।")
            remedies = [
                "अपनी जेब या पर्स में शुद्ध चाँदी का चौकोर टुकड़ा रखें या अनामिका में चाँदी का छल्ला धारण करें।",
                "प्रत्येक सोमवार को शिवलिंग पर जल में कच्चा दूध एवं सफेद तिल मिलाकर अर्पण करें।",
                "घर के सेवादारों, कर्मचारियों और श्रमिकों के साथ सम्मानजनक व्यवहार रखें।"
            ]
        elif lang == "mr":
            name = "रजत पाया (Silver Feet / चांदीचा पाया) 🥈"
            grade = "अत्यंत शुभ व संरक्षक पाया (उत्तम फलदायी)"
            desc = ("मेष राशीच्या जातकांसाठी साडेसातीचा प्रथम टप्पा सुरू आहे, मात्र शनी महाराजांचे आगमन चांदीच्या पायाने झाले आहे. "
                    "हा पाया संकटात ढाल बनून कार्य करतो. आर्थिक स्थैर्य, कौटुंबिक सौख्य, जुनी कर्जे फिटणे आणि वरिष्ठांचे मोलाचे सहकार्य प्राप्त होते.")
            remedies = [
                "पर्समध्ये चांदीचा छोटा चौकोनी तुकडा ठेवा किंवा अनामिकेत चांदीची अंगठी घाला.",
                "दर सोमवारी शिवलिंगावर दुधमिश्रित जल आणि पांढरे तीळ अर्पण करा.",
                "कष्टकरी, कामगार आणि मदतनीसांचा आदर राखा व कामात प्रामाणिकपणा ठेवा."
            ]
        elif lang == "gu":
            name = "રજત પાયા (Silver Feet / ચાંદીનો પાયો) 🥈"
            grade = "અતિ શુભ અને સુરક્ષા આપનાર પાયો"
            desc = ("મેષ ચંદ્ર રાશિના જાતકો માટે સાડાસાતીનો પ્રથમ તબક્કો ચાલી રહ્યો છે, પરંતુ શનિ મહારાજ ચાંદીના પાયે પધાર્યા છે. "
                    "આ પાયો આશીર્વાદ સમાન છે જે નાણાકીય રક્ષણ, પરિવારમાં સુખ-શાંતિ, જૂના દેવામાંથી મુક્તિ અને વડીલોનો સહયોગ લાવે છે.")
            remedies = [
                "પર્સમાં શુદ્ધ ચાંદીનો ચોરસ ટુકડો રાખો અથવા અનામિકા આંગળીમાં ચાંદીની વીંટી પહેરો.",
                "દર સોમવારે શિવલિંગ પર દૂધ-મિશ્રિત જળ અને સફેદ તલ અર્પણ કરો.",
                "શ્રમિકો અને મદદનીશો સાથે સારો વ્યવહાર રાખો અને ઈમાનદારી જાળવો."
            ]
        else:
            name = "Rajat Paya (Silver Feet) 🥈"
            grade = "Most Auspicious & Highly Protective"
            desc = ("Saturn arrives bearing silver gifts. For Aries Moon natives navigating Sade Sati phase 1, "
                    "this Silver Paya acts as a celestial shock absorber. It shields finances, expands family happiness, "
                    "clears past debts, and ensures steady support from mentors.")
            remedies = [
                "Wear a pure silver ring or keep a small square piece of silver in your wallet.",
                "Offer fresh milk mixed with water and white sesame seeds to a Shiva Lingam on Mondays.",
                "Respect domestic helpers, service workers, and maintain strict integrity in all agreements."
            ]
        return name, grade, desc, remedies, transit_timeline

    elif house_pos in [3, 7, 10]:
        name = "Tamra Paya (Copper Feet) 🥉" if lang == "en" else "ताम्र पाया (तांबे का पाया) 🥉"
        grade = "Favorable & Progressive" if lang == "en" else "शुभ व उन्नतिकारक"
        desc = "Saturn awards steady growth for disciplined, focused effort." if lang == "en" else "निरंतर परिश्रम और अनुशासन से उत्तम प्रगति एवं यश की प्राप्ति।"
        remedies = ["Offer water to rising Sun from a copper vessel."] if lang == "en" else ["तांबे के लोटे से सूर्य देव को अर्घ्य दें।"]
        return name, grade, desc, remedies, transit_timeline

    elif house_pos in [1, 6, 11]:
        name = "Swarna Paya (Gold Feet) 🥇" if lang == "en" else "स्वर्ण पाया (सोने का पाया) 🥇"
        grade = "Challenging / Test of Humility" if lang == "en" else "मध्यम / विनम्रता की परीक्षा"
        desc = "Expenses remain high; requires strict discipline against speculation." if lang == "en" else "व्यय अधिक रह सकता है; अहंकार व सट्टेबाजी से बचना आवश्यक है।"
        remedies = ["Recite Dasharatha Shani Stotra on Saturdays."] if lang == "en" else ["शनिवार को दशरथ कृत शनि स्तोत्र का पाठ करें।"]
        return name, grade, desc, remedies, transit_timeline

    else:
        name = "Loha Paya (Iron Feet) 🪙" if lang == "en" else "लौह पाया (लोहे का पाया) 🪙"
        grade = "Demanding / High Caution & Labor" if lang == "en" else "कठिन / श्रमसाध्य एवं सावधानी योग्य"
        desc = "Requires persistence, careful health habits, and systematic patience." if lang == "en" else "धैर्य, कठोर श्रम और स्वास्थ्य के प्रति विशेष सावधानी अपेक्षित है।"
        remedies = ["Light a mustard oil lamp near Peepal tree on Saturdays."] if lang == "en" else ["शनिवार की संध्या पीपल के वृक्ष के नीचे सरसों के तेल का दीपक जलाएं।"]
        return name, grade, desc, remedies, transit_timeline

def calculate_shani_vahan(birth_nak_1based: int, transit_moon_nak_1based: int, lang: str = "en"):
    rem = ((birth_nak_1based * 4) + transit_moon_nak_1based) % 9
    rem = 9 if rem == 0 else rem
    lang_dict = SHANI_VAHANS.get(lang, SHANI_VAHANS["en"])
    vahan_info = lang_dict.get(rem, SHANI_VAHANS["en"][rem])
    return rem, vahan_info

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

def get_fixed_numerology_prediction(mulank: int, bhagyank: int, lang: str = "en") -> str:
    if lang == "hi":
        return (f"**मूलांक {mulank} (राहु/स्थिर बुद्धि) एवं भाग्यांक {bhagyank} (मंगल/ऊर्जा) का समन्वय:** "
                f"आप एक साहसी, मौलिक और व्यवस्थित विचारक हैं। आप किसी भी कार्य की गहराई तक पहुँचकर उसे सुचारू रूप देने में दक्ष हैं। "
                f"राहु और मंगल का प्रभाव आपको तकनीकी, योजनागत और रणनीतिक कार्यों में असाधारण सफलता दिलाता है। "
                f"जीवन में धैर्य बनाए रखने और आवेशपूर्ण निर्णयों से बचने पर भाग्य का पूर्ण सहयोग प्राप्त होता है।")
    elif lang == "mr":
        return (f"**मूलांक {mulank} (राहु/दूरदृष्टी) आणि भाग्यांक {bhagyank} (मंगळ/ऊर्जा) योग:** "
                f"आपण दृढनिश्चयी, स्वतंत्र विचारांचे आणि सूक्ष्म नियोजन करणारे आहात. "
                f"राहु व मंगळ यांच्या प्रभावामुळे कठीण आव्हाने पेलण्याची व धोरणात्मक निर्णय घेण्याची प्रचंड क्षमता लाभलेली आहे. "
                f"घाईगडबडीत निर्णय घेणे टाळून शिस्तबद्ध मार्ग निवडल्यास जीवनात उत्तुंग यश व स्थैर्य लाभते.")
    elif lang == "gu":
        return (f"**મૂળાંક {mulank} (રાહુ/વિશ્લેષણ) અને ભાગ્યાંક {bhagyank} (મંગળ/પરાક્રમ) સમન્વય:** "
                f"તમે એક મક્કમ, સ્વતંત્ર અને ઊંડો વિચાર ધરાવનાર વ્યક્તિત્વ છો. મુશ્કેલ પરિસ્થિતિઓમાં પણ યોગ્ય રસ્તો કાઢવાની તમારી ક્ષમતા ઉત્કૃષ્ટ છે. "
                f"ધૈર્ય અને નિયમિત આયોજન તમને વ્યાવસાયિક તેમજ વ્યક્તિગત જીવનમાં મોટી ઊંચાઈઓ પ્રદાન કરશે.")
    else:
        return (f"**Mulank {mulank} (Rahu Insight) & Bhagyank {bhagyank} (Mars Drive) Synergy:** "
                f"You are naturally endowed with sharp analytical prowess, strategic patience, and relentless execution power. "
                f"You excel in solving complex systems and navigating structural challenges. Channeling high willpower while avoiding "
                f"impulsive emotional confrontation ensures steady, lasting ascension in career and wealth.")

def get_personal_day_vibe(mulank: int, target_date: datetime.date, lang: str = "en"):
    day_sum = target_date.day + target_date.month + target_date.year
    universal_day = reduce_single_digit(day_sum)
    personal_day = reduce_single_digit(mulank + universal_day)

    vibe_map_en = {
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

    vibe_map_hi = {
        1: ("नेतृत्व एवं निर्णायक शुरुआत", "नई योजनाओं को शुरू करने, आत्मविश्वास बढ़ाने और महत्वपूर्ण अनुबंधों के लिए श्रेष्ठ दिन।", "हल्के लाल या सुनहरे रंग का प्रयोग करें; 11 बार गायत्री मंत्र का जप करें।"),
        2: ("सौहार्द, शांति व कूटनीति", "टीमवर्क, शांतिपूर्ण वार्ता, भावनात्मक संतुलन और दूसरों की बात सुनने का दिन।", "चाँदी के पात्र से जल पिएं; 5 मिनट शांत बैठकर ध्यान करें।"),
        3: ("रचनात्मकता एवं ज्ञान का प्रसार", "योजनाओं के विचार-विमर्श, प्रभावी संवाद और मित्रों से मिलने के लिए उत्तम दिन।", "माथे पर केसर या चंदन का तिलक लगाएं; ज्ञानवर्धक कार्य करें।"),
        4: ("अनुशासन एवं व्यवस्थित कार्य", "दस्तावेजों को व्यवस्थित करने, अधूरी योजनाओं को पूर्ण करने और धैर्यपूर्वक काम करने का दिन।", "पक्षियों को बाजरा या साबुत अनाज डालें; जल्दबाजी से बचें।"),
        5: ("सक्रियता, संपर्क एवं त्वरित हल", "तेज गति से कार्य, नेटवर्किंग, संवाद और व्यापारिक सौदों के लिए अनुकूल समय।", "हल्के हरे वस्त्र पहनें; गाय को हरा चारा या हरी मूंग दाल खिलाएं।"),
        6: ("पारिवारिक सौहार्द एवं सामंजस्य", "रिश्तों में मधुरता, परिजनों का सहयोग और स्वास्थ्य संतुलन पर ध्यान देने का दिन।", "सुगंधित इत्र का प्रयोग करें; परिवार के प्रति कृतज्ञता व्यक्त करें।"),
        7: ("गंभीर चिंतन एवं आंतरिक स्पष्टता", "गहन अध्ययन, आध्यात्मिक चिंतन और आत्म-मूल्यांकन के लिए श्रेष्ठ; वाद-विवाद से बचें।", "15 मिनट एकांत में मौन रहें; किसी भी सट्टेबाजी से दूर रहें।"),
        8: ("स्थायित्व, सत्ता व वित्तीय सतर्कता", "वित्तीय योजनाएं, दीर्घकालिक अनुबंध और गंभीरता से काम करने का दिन।", "'ॐ शं शनैश्चराय नमः' का 21 बार जप करें; अधीनस्थों के प्रति विनम्र रहें।"),
        9: ("पूर्णता, क्षमाशीलता एवं नवीन संकल्प", "पुराने विवादों को सुलझाने, अटके काम पूरे करने और मन को हल्का करने का दिन।", "ज़रूरतमंद को भोजन या वस्त्र दान करें; मन में शांति रखें।")
    }

    vibe_map = vibe_map_hi if lang in ["hi", "mr", "gu"] else vibe_map_en
    title, desc, remedy = vibe_map.get(personal_day, ("समतोल एवं सजगता", "शांत मन से दैनिक कार्य संपन्न करें।", "ईश्वर का स्मरण करें।"))
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

if "current_page" not in st.session_state:
    st.session_state.current_page = "profile"

if "show_planets" not in st.session_state:
    st.session_state.show_planets = False

prof = st.session_state.profile
current_lang = prof.get("language", "en")

st.markdown(f"""
<div class="brand-header">
    <div class="brand-title">{t("app_title", current_lang)}</div>
    <div class="brand-subtitle">{t("app_tagline", current_lang)}</div>
</div>
""", unsafe_allow_html=True)

# Single clean language selector dropdown at the top
lang_codes = list(SUPPORTED_LANGUAGES.keys())
lang_labels = list(SUPPORTED_LANGUAGES.values())
curr_lang_idx = lang_codes.index(current_lang) if current_lang in lang_codes else 0

col_sel_left, col_sel_right = st.columns([1, 2])
with col_sel_left:
    st.markdown(f"**{t('select_lang', current_lang)}:**")
with col_sel_right:
    chosen_label = st.selectbox(
        "Application Language",
        lang_labels,
        index=curr_lang_idx,
        label_visibility="collapsed"
    )
    chosen_code = lang_codes[lang_labels.index(chosen_label)]
    if chosen_code != current_lang:
        prof["language"] = chosen_code
        st.session_state.profile = prof
        save_user_profile(prof)
        st.rerun()

st.markdown("<hr style='margin: 10px 0 16px 0; border: none; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)

user_name = prof.get("name", "Okesh")
user_dob = prof.get("dob", datetime.date(1984, 1, 13))
user_tob = prof.get("tob", datetime.time(14, 0))
user_place = prof.get("place", "Chhatrapati Sambhajinagar, India")

# Calculate Janma Nakshatra and Pada automatically from Birth Date and Time
janma_idx, janma_pada, natal_moon_rashi_idx, natal_rashi_deg = calculate_birth_chart(user_dob, user_tob)
janma_name = NAKSHATRAS[janma_idx]
nak_personality_desc = get_nakshatra_description(janma_idx, current_lang)

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

paya_name, paya_status, paya_desc, paya_remedies, paya_timeline = calculate_shani_paya(
    natal_moon_rashi_idx, saturn_rashi_idx, current_lang
)
today_vahan_num, today_vahan = calculate_shani_vahan(
    janma_idx + 1, cur_moon_nak_idx + 1, current_lang
)
cur_nav_cat, cur_nav_series = calculate_navtara(janma_idx, cur_moon_nak_idx)
u_day, p_day, p_title, p_desc, num_remedy = get_personal_day_vibe(mulank, now_ist.date(), current_lang)

# ==============================================================================
# PAGE 1: NATIVE ASTROLOGICAL PROFILE & FOUNDATIONAL ANALYSIS
# ==============================================================================
if st.session_state.current_page == "profile":
    with st.expander(t("edit_profile_expander", current_lang), expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            in_name = st.text_input(t("input_name", current_lang), value=user_name)
            in_dob = st.date_input(t("input_dob", current_lang), value=user_dob)
        with c2:
            in_tob = st.time_input(t("input_tob", current_lang), value=user_tob)
            in_place = st.text_input(t("input_place", current_lang), value=user_place)

        st.caption("ℹ️ *Janma Nakshatra, Pada, and Moon Sign are automatically calculated from your birth date and time using the Swiss Ephemeris engine.*")

        if st.button(t("save_profile_btn", current_lang), use_container_width=True, type="primary"):
            updated_data = {
                "name": in_name,
                "dob": in_dob,
                "tob": in_tob,
                "place": in_place,
                "language": current_lang
            }
            st.session_state.profile = updated_data
            if save_user_profile(updated_data):
                st.success(t("profile_saved_msg", current_lang))
                st.rerun()

    st.markdown(f"""
    <div class="light-card-profile">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h3 style="margin:0; font-size:1.35rem; font-weight:800; color:#431407;">👤 {user_name}</h3>
                <div style="font-size:13.5px; color:#78350f; margin-top:3px;">
                    🎂 {user_dob.strftime('%d %B %Y')} • ⏰ {user_tob.strftime('%H:%M')} • 📍 {user_place}
                </div>
            </div>
            <div>
                <span class="badge-favorable" style="font-size:13px; padding:6px 12px;">
                    {RASHIS[natal_moon_rashi_idx].split(' ')[0]}
                </span>
            </div>
        </div>
        <div style="display:flex; gap:8px; margin-top:12px; flex-wrap:wrap;">
            <span style="background:#ffedd5; color:#9a3412; padding:5px 11px; border-radius:8px; font-size:13px; font-weight:700;">
                🌟 {t('janma_star_label', current_lang)}: {janma_name} (#{janma_idx + 1}, Pada {janma_pada})
            </span>
            <span style="background:#ffedd5; color:#9a3412; padding:5px 11px; border-radius:8px; font-size:13px; font-weight:700;">
                🪐 {t('moon_rashi_label', current_lang)}: {RASHIS[natal_moon_rashi_idx].split(' ')[0]}
            </span>
        </div>
        <div style="margin-top:14px; background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #fed7aa;">
            <div style="font-weight:700; font-size:13.5px; color:#9a3412; margin-bottom:4px;">
                {t('nak_personality_title', current_lang)}:
            </div>
            <div style="font-size:13px; line-height:1.55; color:#431407;">
                {nak_personality_desc}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="light-card-num">
        <div style="font-weight:800; font-size:15px; color:#064e3b; margin-bottom:10px;">
            {t('num_title', current_lang)}
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; text-align:center; margin-bottom:12px;">
            <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                <div style="font-size:12px; color:#047857; font-weight:600;">{t('mulank_label', current_lang)}</div>
                <div style="font-size:24px; font-weight:900; color:#065f46;">{mulank}</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                <div style="font-size:12px; color:#047857; font-weight:600;">{t('bhagyank_label', current_lang)}</div>
                <div style="font-size:24px; font-weight:900; color:#065f46;">{bhagyank}</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                <div style="font-size:12px; color:#047857; font-weight:600;">{t('namank_label', current_lang)}</div>
                <div style="font-size:24px; font-weight:900; color:#065f46;">{namank}</div>
            </div>
        </div>
        <div style="font-size:13.5px; line-height:1.55; color:#064e3b; background:#ffffff; border-radius:10px; padding:12px; border:1px solid #bbf7d0;">
            {get_fixed_numerology_prediction(mulank, bhagyank, current_lang)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="light-card-paya">
        <div style="font-weight:800; font-size:15.5px; color:#3b0764; margin-bottom:4px;">
            {paya_name}
        </div>
        <div style="font-size:12.5px; font-weight:700; color:#6b21a8; margin-bottom:8px;">
            ✦ {paya_status}
        </div>
        <div style="font-size:13px; font-weight:600; color:#4c1d95; margin-bottom:10px; background:#ffffff; padding:8px 12px; border-radius:8px; border:1px solid #e9d5ff;">
            ⏳ <b>{t('transit_timeline_lbl', current_lang)}:</b> {paya_timeline}
        </div>
        <div style="font-size:13.5px; line-height:1.55; color:#3b0764; margin-bottom:12px;">
            <b>{t('paya_impact_lbl', current_lang)}:</b><br>{paya_desc}
        </div>
        <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #e9d5ff;">
            <div style="font-weight:700; font-size:13.5px; color:#581c87; margin-bottom:6px;">
                {t('paya_remedies_lbl', current_lang)}:
            </div>
    """, unsafe_allow_html=True)
    for r in paya_remedies:
        st.markdown(f"<div style='font-size:13px; color:#4c1d95; margin-bottom:4px;'>• {r}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    if st.button(t("btn_view_forecast", current_lang), use_container_width=True, type="primary"):
        st.session_state.current_page = "forecast"
        st.rerun()

# ==============================================================================
# PAGE 2: TRANSIT PREDICTIONS, 7-DAY MATRIX, REMEDIES & PLANETS
# ==============================================================================
elif st.session_state.current_page == "forecast":
    if st.button(t("btn_back_profile", current_lang), use_container_width=False):
        st.session_state.current_page = "profile"
        st.rerun()

    # Active Navtara description lookup
    lang_desc_dict = NAVTARA_DESCRIPTIONS.get(current_lang, NAVTARA_DESCRIPTIONS["en"])
    active_tara_desc = lang_desc_dict.get(cur_nav_cat, "")

    # Badge styling
    if cur_nav_cat in ["Vipat", "Pratyari", "Vadha"]:
        tara_badge_class = "badge-danger"
    elif cur_nav_cat == "Ati-Mitra":
        tara_badge_class = "badge-super"
    else:
        tara_badge_class = "badge-favorable"

    st.markdown(f"""
    <div class="light-card-live">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-size:16px; font-weight:800; color:#78350f;">
                {t('today_card_title', current_lang)}
            </span>
            <span class="{tara_badge_class}">
                {cur_nav_cat} ({t('series_lbl', current_lang)} {cur_nav_series})
            </span>
        </div>
        <div style="font-size:13px; color:#92400e; margin-bottom:10px;">
            📅 <b>{now_ist.strftime('%A, %d %B %Y')}</b> | {t('current_active_nak', current_lang)}: <b>{NAKSHATRAS[cur_moon_nak_idx]}</b>
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size:13px; margin-bottom:10px; background:#ffffff; padding:10px; border-radius:10px; border:1px solid #fde68a;">
            <div>🪐 <b>{t('saturn_vahan_lbl', current_lang)}:</b><br>{today_vahan['name']}</div>
            <div>🔢 <b>{t('personal_day_lbl', current_lang)}:</b><br>Day {p_day} ({p_title})</div>
        </div>
        <div style="font-size:13.5px; line-height:1.55; color:#451a03; margin-top:8px;">
            <b>1. Navtara Rhythm ({cur_nav_cat}):</b> {active_tara_desc}<br>
            <b>2. Shani Vahan Pulse:</b> {today_vahan['desc']}<br>
            <b>3. Personal Day {p_day} Vibration:</b> {p_desc}
        </div>
        <div class="remedy-highlight-box">
            <div style="font-weight:700; color:#92400e; font-size:13.5px; margin-bottom:4px;">
                {t('today_remedies_lbl', current_lang)}:
            </div>
            <div style="font-size:13px; color:#1e293b; line-height:1.5;">
                • <b>Navtara:</b> {'पक्षियों/पशुओं को अन्न डालें; बड़े अनुबंधों को टालें।' if cur_nav_cat in ['Vadha', 'Vipat'] else ('संवाद में संयम रखें; विवाद से बचें।' if cur_nav_cat == 'Pratyari' else 'शुभ व उत्पादक कार्यों को गति दें; वयोवृद्धों का आशीर्वाद लें।')}<br>
                • <b>अंक ज्योतिष (Day {p_day}):</b> {num_remedy}<br>
                • <b>शनि वाहन:</b> {'कौवों या पक्षियों को छत पर भीगा हुआ अनाज दें।' if 'कौआ' in today_vahan['name'] or 'Crow' in today_vahan['name'] else 'हनुमान चालीसा का पाठ करें एवं धैर्यपूर्वक कार्य करें।'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader(t("navtara_matrix_title", current_lang))
    st.caption(t("matrix_instruction", current_lang))

    transitions = find_7day_transitions(now_utc)

    for idx, tr in enumerate(transitions):
        nak_name = NAKSHATRAS[tr["nak_idx"]]
        cat, series = calculate_navtara(janma_idx, tr["nak_idx"])
        s_dt = tr["start"].astimezone(ist_tz)
        e_dt = tr["end"].astimezone(ist_tz)
        _, v_info = calculate_shani_vahan(janma_idx + 1, tr["nak_idx"] + 1, current_lang)
        _, d_num, d_title, d_desc, d_rem = get_personal_day_vibe(mulank, s_dt.date(), current_lang)

        cat_desc = lang_desc_dict.get(cat, "")

        # Status icon
        if cat in ["Vipat", "Pratyari", "Vadha"]:
            icon = "🔴"
        elif cat == "Ati-Mitra":
            icon = "🟢🟢"
        else:
            icon = "🟢"

        expander_label = f"{icon} {s_dt.strftime('%a, %d %b')}: {nak_name} ({cat} - {t('series_lbl', current_lang)} {series})"

        with st.expander(expander_label, expanded=(idx == 0)):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**⏰ {t('window_lbl', current_lang)}:** `{s_dt.strftime('%d %b %H:%M')} – {e_dt.strftime('%d %b %H:%M IST')}`")
                st.markdown(f"**🪐 {t('saturn_vahan_lbl', current_lang)}:** `{v_info['name']}`")
            with col_b:
                st.markdown(f"**✨ {t('current_tara', current_lang)}:** `{cat}` ({cat_desc})")
                st.markdown(f"**🔢 {t('personal_day_lbl', current_lang)}:** `Day {d_num} - {d_title}`")

            st.markdown(f"""
            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; margin-top:8px; border:1px solid #fed7aa; font-size:13px; color:#431407;">
                <b>🎯 {t('predictions_lbl', current_lang)}:</b> {d_desc}<br>
                <b>🪐 Shani Mount Note:</b> {v_info['desc']}
            </div>
            <div style="background:#f0fdf4; border-radius:8px; padding:10px 12px; margin-top:6px; border:1px solid #bbf7d0; font-size:13px; color:#064e3b;">
                <b>🪔 {t('remedies_lbl', current_lang)}:</b><br>
                • <b>Navtara:</b> {'गौ माता या पक्षियों को अन्न खिलाएं; संयम रखें।' if cat in ['Vadha', 'Vipat'] else ('वाद-विवाद से दूर रहें।' if cat == 'Pratyari' else 'महत्वपूर्ण कार्यों का शुभारंभ करें; बड़ों का सम्मान करें।')}<br>
                • <b>Numerology:</b> {d_rem}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:24px 0 16px 0; border:none; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)

    if not st.session_state.show_planets:
        if st.button(t("planets_btn", current_lang), use_container_width=True):
            st.session_state.show_planets = True
            st.rerun()
    else:
        if st.button(t("planets_hide_btn", current_lang), use_container_width=True):
            st.session_state.show_planets = False
            st.rerun()

        st.markdown("### 🌌 Sidereal Planetary Positions (Chitrapaksha Lahiri)")
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
                "Rashi": RASHIS[r_idx].split(" ")[0],
                "Degrees": f"{r_deg:.2f}°",
                "Nakshatra": f"{NAKSHATRAS[n_idx]} (Pada {pada})"
            })

        rahu_lon = get_sidereal_lon(jd_now, swe.MEAN_NODE)
        ketu_lon = (rahu_lon + 180.0) % 360.0
        kr_idx, kr_deg = lon_to_rashi(ketu_lon)
        kn_idx, k_pada = lon_to_nakshatra(ketu_lon)
        coords.append({
            "Planet": "Ketu",
            "Rashi": RASHIS[kr_idx].split(" ")[0],
            "Degrees": f"{kr_deg:.2f}°",
            "Nakshatra": f"{NAKSHATRAS[kn_idx]} (Pada {k_pada})"
        })

        st.dataframe(coords, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    if st.button(t("btn_back_profile", current_lang) + " ↺", use_container_width=True):
        st.session_state.current_page = "profile"
        st.rerun()

st.markdown("<div style='text-align:center; font-size:12px; color:#94a3b8; margin-top:24px;'>Navtara Pulse • Swiss Ephemeris Chitrapaksha Lahiri Engine</div>", unsafe_allow_html=True)
