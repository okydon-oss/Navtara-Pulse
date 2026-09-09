import os
import json
import datetime
import math
import streamlit as st

# Swiss Ephemeris import with fallback check
try:
    import swisseph as swe
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False

st.set_page_config(page_title="Navtara Pulse", page_icon="✨", layout="centered")

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

CITY_COORDS = {
    "chhatrapati sambhajinagar": (19.8762, 75.3433),
    "aurangabad": (19.8762, 75.3433),
    "mumbai": (19.0760, 72.8777),
    "pune": (18.5204, 73.8567),
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "ahmedabad": (23.0225, 72.5714),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "jaipur": (26.9124, 75.7873),
    "surat": (21.1702, 72.8311),
    "nagpur": (21.1458, 79.0882),
    "indore": (22.7196, 75.8577),
    "bhopal": (23.2599, 77.4126),
    "lucknow": (26.8467, 80.9462),
    "patna": (25.5941, 85.1376),
    "panvel": (18.9894, 73.1175),
    "thane": (19.2183, 72.9781),
    "nashik": (19.9975, 73.7898)
}

PROFILE_FILE = "user_profile.json"

TRANSLATIONS = {
    "en": {
        "app_title": "✨ Navtara Pulse",
        "app_subtitle": "Vedic Nakshatra Timing, Numerology & Shani Transit Intelligence",
        "lang_label": "🌐 Language / भाषा / भाषा / ભાષા",
        "edit_profile_expander": "✏️ Update / Edit Birth Details",
        "input_name": "Full Name",
        "input_dob": "Birth Date",
        "input_tob": "Birth Time",
        "input_place": "Birth Place (City)",
        "save_profile_btn": "💾 Save & Recompute Astrological Profile",
        "profile_saved_msg": "✅ Profile updated and recomputed with Swiss Ephemeris precision!",
        "sec1_title": "🌟 1. Navtara & Vedic Astrological Profile",
        "sec2_title": "🔢 2. Core Numerology Blueprint & Fixed Life Attributes",
        "sec3_title": "🪐 3. Shani Paya & Shani Gochar (Sade Sati / Dhaiya)",
        "janma_star_label": "Janma Nakshatra",
        "moon_rashi_label": "Moon Sign (Janma Rashi)",
        "lagna_label": "Lagna (Ascendant)",
        "nak_personality_title": "Core Personality & Behavioral Nature",
        "nak_remedies_title": "🪔 Vedic Remedies for Janma Nakshatra",
        "mulank_label": "Mulank (Driver)",
        "bhagyank_label": "Bhagyank (Conductor)",
        "namank_label": "Namank (Name No.)",
        "num_remedies_title": "🪔 Astro-Numerology Life Harmonizing Remedies",
        "transit_timeline_lbl": "Saturn Transit Window",
        "paya_impact_lbl": "Shani Paya Faction & Life Guidance",
        "sadesati_card_title": "Saturn Gochar (Sade Sati / Dhaiya Status)",
        "sadesati_timeline_lbl": "Transit Timeline & Phase",
        "sadesati_impact_lbl": "Sade Sati / Dhaiya Influence & Life Strategy",
        "shani_integrated_remedies": "🛡️ Combined Vedic Shani Protection Remedies",
        "btn_view_forecast": "🔮 View Predictions for Today & Next 7 Days ➔",
        "btn_back_profile": "⬅️ Back to Astrological Profile",
        "tab_today": "⚡ Today's Live Pulse",
        "tab_7days": "🗓️ 7-Day Moon Transition Matrix",
        "tab_planets": "🪐 Sidereal Lahiri Ephemeris",
        "active_navtara_title": "Active Navtara Energy Right Now",
        "shani_vahan_title": "Today's Saturn Vehicle (Shani Vahan)",
        "personal_day_title": "Personal Day Number Vibration",
        "three_directives_title": "🎯 Three Tactical Rules for Today",
        "matrix_table_title": "Daily Moon Transition Table (Next 7 Days)",
        "col_status": "Status",
        "col_timing": "Day, Date & Time to Day, Date & Time",
        "col_star": "Nakshatra Name",
        "col_series": "Navtara Series",
        "view_planets_btn": "🔭 Toggle Real-Time Sidereal Planetary Coordinates"
    },
    "hi": {
        "app_title": "✨ नवतारा पल्स",
        "app_subtitle": "वैदिक नक्षत्र गोचर, अंक ज्योतिष एवं शनि गोचर विश्लेषण",
        "lang_label": "🌐 भाषा चयन करें",
        "edit_profile_expander": "✏️ जन्म विवरण दर्ज अथवा संशोधित करें",
        "input_name": "पूरा नाम",
        "input_dob": "जन्म तिथि",
        "input_tob": "जन्म समय",
        "input_place": "जन्म स्थान (शहर)",
        "save_profile_btn": "💾 विवरण सहेजें एवं कुंडली पुनः गणना करें",
        "profile_saved_msg": "✅ जन्म विवरण सफलतापूर्वक सहेजा गया!",
        "sec1_title": "🌟 1. नवतारा एवं वैदिक जन्म कुंडली प्रोफाइल",
        "sec2_title": "🔢 2. अंक ज्योतिष रूपरेखा एवं मूल स्वभाव विश्लेषण",
        "sec3_title": "🪐 3. शनि पाया एवं शनि गोचर (साढ़े साती / ढैय्या प्रभाव)",
        "janma_star_label": "जन्म नक्षत्र",
        "moon_rashi_label": "जन्म राशि (चन्द्र राशि)",
        "lagna_label": "लग्न (Ascendant)",
        "nak_personality_title": "जन्म नक्षत्र आधारित मूल व्यक्तित्व व स्वभाव",
        "nak_remedies_title": "🪔 जन्म नक्षत्र शांति एवं वैदिक उपाय",
        "mulank_label": "मूलांक (Driver)",
        "bhagyank_label": "भाग्यांक (Conductor)",
        "namank_label": "नामांक (Name No.)",
        "num_remedies_title": "🪔 अंक ज्योतिषीय संतुलन एवं भाग्योदय उपाय",
        "transit_timeline_lbl": "शनि गोचर समयावधि",
        "paya_impact_lbl": "शनि पाया फल एवं जीवन मार्गदर्शन",
        "sadesati_card_title": "वर्तमान शनि गोचर (साढ़े साती / ढैय्या स्थिति)",
        "sadesati_timeline_lbl": "गोचर समयावधि एवं सक्रिय चरण",
        "sadesati_impact_lbl": "साढ़े साती / ढैय्या फलादेश एवं जीवन प्रभाव",
        "shani_integrated_remedies": "🛡️ शनि पाया व साढ़े साती सुरक्षात्मक वैदिक उपाय",
        "btn_view_forecast": "🔮 आज एवं आगामी 7 दिनों का फलादेश देखें ➔",
        "btn_back_profile": "⬅️ जन्म कुंडली प्रोफाइल पर वापस जाएं",
        "tab_today": "⚡ आज का सक्रिय गोचर",
        "tab_7days": "🗓️ 7 दिवसीय चन्द्र गोचर चक्र",
        "tab_planets": "🪐 प्रत्यक्ष ग्रह स्पष्ट (लाहिड़ी)",
        "active_navtara_title": "वर्तमान सक्रिय नवतारा स्थिति",
        "shani_vahan_title": "आज का शनि वाहन",
        "personal_day_title": "आज का व्यक्तिगत अंक (Personal Day)",
        "three_directives_title": "🎯 आज के लिए तीन स्वर्णिम नियम",
        "matrix_table_title": "दैनिक चन्द्र गोचर तालिका (आगामी 7 दिन)",
        "col_status": "स्थिति (Status)",
        "col_timing": "वार, दिनांक व समय से वार, दिनांक व समय तक",
        "col_star": "नक्षत्र नाम",
        "col_series": "नवतारा चक्र (Series)",
        "view_planets_btn": "🔭 प्रत्यक्ष ग्रह स्पष्ट स्थिति देखें"
    },
    "mr": {
        "app_title": "✨ नवतारा पल्स",
        "app_subtitle": "वैदिक नक्षत्र गोचर, अंकशास्त्र आणि शनी गोचर मार्गदर्शन",
        "lang_label": "🌐 भाषा निवडा",
        "edit_profile_expander": "✏️ जन्म तपशील संपादित करा",
        "input_name": "पूर्ण नाव",
        "input_dob": "जन्म तारीख",
        "input_tob": "जन्म वेळ",
        "input_place": "जन्म ठिकाण (शहर)",
        "save_profile_btn": "💾 जतन करा व कुंडली मोजा",
        "profile_saved_msg": "✅ तपशील यशस्वीरित्या जतन केला!",
        "sec1_title": "🌟 १. नवतारा व वैदिक जन्म कुंडली रूपरेषा",
        "sec2_title": "🔢 २. अंकशास्त्र ब्लूप्रिंट व स्थायी जीवन स्वभाव",
        "sec3_title": "🪐 ३. शनी पाया व शनी गोचर (साडेसाती / अडीचकी प्रभाव)",
        "janma_star_label": "जन्म नक्षत्र",
        "moon_rashi_label": "चंद्र राशी",
        "lagna_label": "लग्न (Ascendant)",
        "nak_personality_title": "जन्म नक्षत्र व्यक्तिमत्त्व व स्वभाव",
        "nak_remedies_title": "🪔 जन्म नक्षत्र शांती व वैदिक उपाय",
        "mulank_label": "मूलांक",
        "bhagyank_label": "भाग्यांक",
        "namank_label": "नामांक",
        "num_remedies_title": "🪔 अंकशास्त्र ऊर्जा समतोल व भाग्योदय उपाय",
        "transit_timeline_lbl": "शनी गोचर कालावधी",
        "paya_impact_lbl": "शनी पाया प्रभाव व जीवन फलादेश",
        "sadesati_card_title": "सद्य शनी गोचर (साडेसाती / ढैय्या स्थिती)",
        "sadesati_timeline_lbl": "गोचर कालावधी व सक्रिय टप्पा",
        "sadesati_impact_lbl": "साडेसाती / अडीचकी प्रभाव व जीवन फलादेश",
        "shani_integrated_remedies": "🛡️ शनी पाया व साडेसाती प्रतिबंधक वैदिक उपाय",
        "btn_view_forecast": "🔮 आजचे व पुढील ७ दिवसांचे भविष्य पहा ➔",
        "btn_back_profile": "⬅️ जन्म प्रोफाइलवर परत या",
        "tab_today": "⚡ आजचे सक्रिय नक्षत्र",
        "tab_7days": "🗓️ ७ दिवसांचे नक्षत्र संक्रमण",
        "tab_planets": "🪐 ग्रह स्थिती (लाहिरी)",
        "active_navtara_title": "सद्य सक्रिय नवतारा ऊर्जा",
        "shani_vahan_title": "आजचे शनी वाहन",
        "personal_day_title": "आजचा व्यक्तिगत अंक",
        "three_directives_title": "🎯 आजच्या दिवसाचे ३ महत्त्वाचे नियम",
        "matrix_table_title": "दैनिक चंद्र संक्रमण तक्ता (पुढील ७ दिवस)",
        "col_status": "स्थिती",
        "col_timing": "वार, दिनांक व वेळ ते वार, दिनांक व वेळ",
        "col_star": "नक्षत्र नाव",
        "col_series": "नवतारा चक्र",
        "view_planets_btn": "🔭 प्रत्यक्ष ग्रह स्थिती तपासा"
    },
    "gu": {
        "app_title": "✨ નવતારા પલ્સ",
        "app_subtitle": "વૈદિક નક્ષત્ર ગોચર, અંકશાસ્ત્ર અને શનિ ગોચર માર્ગદર્શન",
        "lang_label": "🌐 ભાષા પસંદ કરો",
        "edit_profile_expander": "✏️ જન્મ વિગત સુધારો",
        "input_name": "પૂરું નામ",
        "input_dob": "જન્મ તારીખ",
        "input_tob": "જન્મ સમય",
        "input_place": "જન્મ સ્થળ (શહેર)",
        "save_profile_btn": "💾 વિગત સાચવો અને ગણતરી કરો",
        "profile_saved_msg": "✅ વિગત સફળતાપૂર્વક સચવાઈ ગઈ!",
        "sec1_title": "🌟 ૧. નવતારા અને વૈદિક જન્મ કુંડળી રૂપરેખા",
        "sec2_title": "🔢 ૨. અંકશાસ્ત્ર બ્લૂપ્રિન્ટ અને મૂળ સ્વભાવ વિશ્લેષણ",
        "sec3_title": "🪐 ૩. શનિ પાયા અને શનિ ગોચર (સાડાસાતી / ઢૈય્યા પ્રભાવ)",
        "janma_star_label": "જન્મ નક્ષત્ર",
        "moon_rashi_label": "ચંદ્ર રાશિ",
        "lagna_label": "લગ્ન (Ascendant)",
        "nak_personality_title": "જન્મ નક્ષત્ર આધારિત વ્યક્તિત્વ અને સ્વભાવ",
        "nak_remedies_title": "🪔 જન્મ નક્ષત્ર શાંતિ અને વૈદિક ઉપાયો",
        "mulank_label": "મૂળાંક",
        "bhagyank_label": "ભાગ્યાંક",
        "namank_label": "નામાંક",
        "num_remedies_title": "🪔 અંકશાસ્ત્ર સંતુલન અને ભાગ્યોદય ઉપાયો",
        "transit_timeline_lbl": "શનિ ગોચર સમયગાળો",
        "paya_impact_lbl": "શનિ પાયા ફળ અને માર્ગદર્શન",
        "sadesati_card_title": "વર્તમાન શનિ ગોચર (સાડાસાતી / ઢૈય્યા સ્થિતિ)",
        "sadesati_timeline_lbl": "ગોચર સમયગાળો અને સક્રિય તબક્કો",
        "sadesati_impact_lbl": "સાડાસાતી / ઢૈય્યા ફળકથન અને જીવન પ્રભાવ",
        "shani_integrated_remedies": "🛡️ શનિ પાયા અને સાડાસાતી રક્ષાત્મક વૈદિક ઉપાયો",
        "btn_view_forecast": "🔮 આજનું અને આગામી ૭ દિવસનું ફળકથન જુઓ ➔",
        "btn_back_profile": "⬅️ જન્મ પ્રોફાઇલ પર પાછા જાઓ",
        "tab_today": "⚡ આજનું સક્રિય ગોચર",
        "tab_7days": "🗓️ ૭ દિવસનું ચંદ્ર ગોચર કોષ્ટક",
        "tab_planets": "🪐 ગ્રહ સ્થિતિ (લાહિરી)",
        "active_navtara_title": "હાલનું સક્રિય નવતારા ફળ",
        "shani_vahan_title": "આજનું શનિ વાહન",
        "personal_day_title": "આજનો વ્યક્તિગત અંક",
        "three_directives_title": "🎯 આજના ૩ સોનેરી નિયમો",
        "matrix_table_title": "દૈનિક ચંદ્ર ગોચર કોષ્ટક (આગામી ૭ દિવસ)",
        "col_status": "સ્થિતિ",
        "col_timing": "વાર, તારીખ અને સમય થી વાર, તારીખ અને સમય સુધી",
        "col_star": "નક્ષત્ર નામ",
        "col_series": "નવતારા શ્રેણી",
        "view_planets_btn": "🔭 વર્તમાન ગ્રહ સ્પષ્ટ સ્થિતિ જુઓ"
    }
}

def t(key: str, lang: str = "en") -> str:
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))

st.markdown("""
<style>
    .light-card-profile {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1.5px solid #fde68a;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.08);
    }
    .light-card-num {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border: 1.5px solid #a7f3d0;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.08);
    }
    .light-card-paya {
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
        border: 1.5px solid #ddd6fe;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.08);
    }
    .badge-favorable {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #86efac;
        padding: 3px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
    }
    .badge-danger {
        background-color: #fee2e2;
        color: #b91c1c;
        border: 1px solid #fca5a5;
        padding: 3px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

NAKSHATRA_DETAILS = {
    0: {"lord": "Ketu", "deity": "Ashwini Kumaras", "tree": "Kuchila", "mantra": "Om Ashwibhyam Namah"},
    1: {"lord": "Shukra (Venus)", "deity": "Yama", "tree": "Amla", "mantra": "Om Yamaya Namah"},
    2: {"lord": "Surya (Sun)", "deity": "Agni", "tree": "Gular", "mantra": "Om Agnaye Namah"},
    3: {"lord": "Chandra (Moon)", "deity": "Brahma", "tree": "Jamun", "mantra": "Om Brahmane Namah"},
    4: {"lord": "Mangal (Mars)", "deity": "Soma", "tree": "Khair", "mantra": "Om Somaya Namah"},
    5: {"lord": "Rahu", "deity": "Rudra", "tree": "Pakar", "mantra": "Om Rudraya Namah"},
    6: {"lord": "Guru (Jupiter)", "deity": "Aditi", "tree": "Bamboo", "mantra": "Om Aditaye Namah"},
    7: {"lord": "Shani (Saturn)", "deity": "Brihaspati", "tree": "Peepal", "mantra": "Om Brihaspataye Namah"},
    8: {"lord": "Budha (Mercury)", "deity": "Nagas", "tree": "Nagkesar", "mantra": "Om Sarpabhyo Namah"},
    9: {"lord": "Ketu", "deity": "Pitris", "tree": "Banyan", "mantra": "Om Pitribhyo Namah"},
    10: {"lord": "Shukra (Venus)", "deity": "Bhaga", "tree": "Palash", "mantra": "Om Bhagaya Namah"},
    11: {"lord": "Surya (Sun)", "deity": "Aryaman", "tree": "Rudraksha", "mantra": "Om Aryamne Namah"},
    12: {"lord": "Chandra (Moon)", "deity": "Savitr", "tree": "Chameli", "mantra": "Om Savitre Namah"},
    13: {"lord": "Mangal (Mars)", "deity": "Tvashtar", "tree": "Bilva", "mantra": "Om Tvashtre Namah"},
    14: {"lord": "Rahu", "deity": "Vayu", "tree": "Arjuna", "mantra": "Om Vayave Namah"},
    15: {"lord": "Guru (Jupiter)", "deity": "Indra-Agni", "tree": "Vikankata", "mantra": "Om Indragnibhyam Namah"},
    16: {"lord": "Shani (Saturn)", "deity": "Mitra", "tree": "Bakul", "mantra": "Om Mitraya Namah"},
    17: {"lord": "Budha (Mercury)", "deity": "Indra", "tree": "Pine", "mantra": "Om Indraya Namah"},
    18: {"lord": "Ketu", "deity": "Nirriti", "tree": "Sal", "mantra": "Om Nirritaye Namah"},
    19: {"lord": "Shukra (Venus)", "deity": "Apas", "tree": "Ashoka", "mantra": "Om Adbhyo Namah"},
    20: {"lord": "Surya (Sun)", "deity": "Vishvadevas", "tree": "Jackfruit", "mantra": "Om Vishvedevabhyo Namah"},
    21: {"lord": "Chandra (Moon)", "deity": "Vishnu", "tree": "Arka", "mantra": "Om Vishnave Namah"},
    22: {"lord": "Mangal (Mars)", "deity": "Ashta Vasus", "tree": "Shami", "mantra": "Om Vasubhyo Namah"},
    23: {"lord": "Rahu", "deity": "Varuna", "tree": "Kadamba", "mantra": "Om Varunaya Namah"},
    24: {"lord": "Guru (Jupiter)", "deity": "Aja Ekapada", "tree": "Mango", "mantra": "Om Ajaikapade Namah"},
    25: {"lord": "Shani (Saturn)", "deity": "Ahirbudhnya", "tree": "Neem", "mantra": "Om Ahirbudhnyaya Namah"},
    26: {"lord": "Budha (Mercury)", "deity": "Pushan", "tree": "Mahua", "mantra": "Om Pushne Namah"}
}

NAKSHATRA_TRAITS = {
    1: {  # Bharani
        "en": "Natives born under Bharani exhibit immense willpower, courage, and an unshakeable sense of justice. Ruled by Venus and presiding deity Yama (God of Dharma), Bharani represents the womb of creation—symbolizing transformation through intense life experiences. You possess sharp intuition, artistic taste, fierce loyalty, and a natural tendency to safeguard those you care for. You dislike superficial pretense and perform best in demanding endeavors where authenticity and strategic resilience are rewarded.",
        "hi": "भरणी नक्षत्र में जन्मे जातक अदम्य इच्छाशक्ति, अद्वितीय साहस और न्यायप्रियता से युक्त होते हैं। इसके स्वामी शुक्र एवं अधिष्ठाता देवता यम (धर्मराज) हैं। भरणी सृजन का प्रतीक है, जो जीवन में बड़े कायाकल्प और रूपांतरण को दर्शाता है। आपके भीतर गहन अंतर्दृष्टि, कलात्मक अभिरुचि, स्पष्टवादिता और नेतृत्व का स्वाभाविक गुण होता है। आप दिखावे से दूर रहकर निष्ठावान संबंधों को महत्व देते हैं और चुनौतीपूर्ण परिस्थितियों में दृढ़ता से विजयी होते हैं।",
        "mr": "भरणी नक्षत्रात जन्मलेल्या व्यक्तींमध्ये विलक्षण इच्छाशक्ती, धैर्य आणि न्यायप्रिय वृत्ती असते. या नक्षत्राचे स्वामी शुक्र आणि आराध्य दैवत यमराज आहेत. भरणी नक्षत्र हे नवनिर्मिती आणि मोठ्या परिवर्तनाचे प्रतीक मानले जाते. तुमच्यामध्ये तीव्र अंतर्ज्ञान, कलात्मक दृष्टी, निर्भीड स्वभाव आणि स्वतःच्या तत्त्वांवर ठाम राहण्याची वृत्ती असते. तुम्ही बाह्य दिखावा नाकारून प्रामाणिक परिश्रमावर विश्वास ठेवता आणि संघर्षातून मोठी प्रगती साधता.",
        "gu": "ભરણી નક્ષત્રમાં જન્મેલા જાતકો અતૂટ ઇચ્છાશક્તિ, સાહસ અને ન્યાયપ્રિયતા માટે જાણીતા છે. આ નક્ષત્રના સ્વામી શુક્ર અને અધિષ્ઠાતા દેવ યમરાજ છે. ભરણી સર્જન અને જીવનના ઊંડા પરિવર્તનનું પ્રતીક છે. તમારી પાસે તીવ્ર આંતરજ્ઞાન, કલાત્મક સૂઝબૂઝ અને મુશ્કેલ સમયમાં પણ અડગ રહેવાની ક્ષમતા હોય છે. તમે દંભથી દૂર રહીને સત્ય અને નિષ્ઠાવાન સંબંધોને સર્વોચ્ચ પ્રાથમિકતા આપો છો."
    }
}

def get_nakshatra_description(nak_idx: int, lang: str = "en") -> str:
    traits = NAKSHATRA_TRAITS.get(nak_idx, NAKSHATRA_TRAITS.get(1))
    return traits.get(lang, traits.get("en", "Dynamic, energetic, focused, and intuitive personality with strong spiritual depth."))

def get_nakshatra_remedy(nak_idx: int, lang: str = "en") -> list:
    details = NAKSHATRA_DETAILS.get(nak_idx, NAKSHATRA_DETAILS[1])
    deity = details["deity"]
    lord = details["lord"]
    mantra = details["mantra"]
    tree = details["tree"]

    if lang == "hi":
        return [
            f"**नक्षत्र आराध्य देव:** भगवान {deity} एवं नक्षत्र स्वामी {lord} की नित्य आराधना करें।",
            f"**बीज मंत्र जप:** प्रतिदिन अथवा जन्म नक्षत्र के दिन `{mantra}` का 108 बार शांत मन से जप करें।",
            f"**पवित्र वृक्ष संरक्षण:** {tree} के पौधे का संवर्धन करें या उसे नियमित जल अर्पित करें।",
            "**सात्विक दान:** शुक्रवार को श्वेत वस्त्र, चावल, दूध अथवा मिश्री का जरूरतमंदों को दान करें।"
        ]
    elif lang == "mr":
        return [
            f"**नक्षत्र आराध्य दैवत:** {deity} आणि नक्षत्र स्वामी {lord} यांचे नित्य स्मरण व नामस्मरण करा.",
            f"**बीज मंत्र जप:** दररोज किंवा जन्म नक्षत्राच्या दिवशी `{mantra}` चा १०८ वेळा शांतपणे जप करा.",
            f"**पवित्र वृक्ष सेवा:** {tree} वृक्षाचे संवर्धन करा किंवा त्याला जल अर्पण करा.",
            "**सात्विक दान:** शुक्रवारी गरजूंना पांढरे वस्त्र अथवा दुधाचे पदार्थ दान करून पुण्य संपादन करा."
        ]
    elif lang == "gu":
        return [
            f"**નક્ષત્ર આરાધ્ય દેવ:** {deity} અને નક્ષત્ર સ્વામી {lord} ની નિયમિત ભક્તિ કરો.",
            f"**બીજ મંત્ર જાપ:** દરરોજ અથવા જન્મ નક્ષત્રના દિવસે `{mantra}` નો ૧૦૮ વખત જાપ કરવો.",
            f"**પવિત્ર વૃક્ષ સેવન:** {tree} ના વૃક્ષનું જતન કરો અથવા તેને જળ અર્પણ કરવું.",
            "**કલ્યાણકારી દાન:** શુક્રવારે જરૂરિયાતમંદોને સફેદ વસ્ત્ર, અન્ન કે સાકરનું દાન કરવું."
        ]
    else:
        return [
            f"**Nakshatra Deity Worship:** Offer prayers to {deity} and honor planetary ruler {lord}.",
            f"**Sacred Japa:** Recite `{mantra}` 108 times daily or on Moon transit over your birth star.",
            f"**Sacred Plant Connection:** Honor, plant, or water the {tree} to harmonize stellar frequencies.",
            "**Sattvic Charity:** Donate white grains, milk sweets, or clothes to harmonize Venusian currents."
        ]

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

def resolve_coords(place_str: str):
    normalized = place_str.lower().split(",")[0].strip()
    return CITY_COORDS.get(normalized, (19.8762, 75.3433))

def calculate_lagna(jd_birth_ut: float, lat: float, lon: float):
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayanamsa = swe.get_ayanamsa_ut(jd_birth_ut)
    houses, ascmc = swe.houses(jd_birth_ut, lat, lon, b'P')
    ascendant_sidereal = (ascmc[0] - ayanamsa) % 360.0
    rashi_idx = int(ascendant_sidereal / 30.0) % 12
    deg = ascendant_sidereal % 30.0
    return rashi_idx, deg

def calculate_birth_chart(dob: datetime.date, tob: datetime.time, place_str: str = "", tz_offset_hours: float = 5.5):
    birth_dt_local = datetime.datetime.combine(dob, tob)
    birth_dt_utc = birth_dt_local - datetime.timedelta(hours=tz_offset_hours)
    jd_birth = dt_to_jd(birth_dt_utc)
    moon_lon = get_sidereal_lon(jd_birth, swe.MOON)
    nak_idx, pada = lon_to_nakshatra(moon_lon)
    rashi_idx, rashi_deg = lon_to_rashi(moon_lon)
    lat, lon = resolve_coords(place_str)
    lagna_rashi_idx, lagna_deg = calculate_lagna(jd_birth, lat, lon)
    return nak_idx, pada, rashi_idx, rashi_deg, lagna_rashi_idx, lagna_deg

def reduce_to_single_digit(n: int) -> int:
    while n > 9 and n not in [11, 22, 33]:
        n = sum(int(d) for d in str(n))
    if n in [11, 22, 33]:
        n = sum(int(d) for d in str(n))
    return n

def calculate_numerology(dob: datetime.date, name: str):
    mulank = reduce_to_single_digit(dob.day)
    full_date_sum = dob.day + dob.month + dob.year
    bhagyank = reduce_to_single_digit(full_date_sum)
    cleaned_name = "".join(ch for ch in name.upper() if ch.isalpha())
    namank_val = sum(CHALDEAN_MAP.get(ch, 0) for ch in cleaned_name)
    namank = reduce_to_single_digit(namank_val) if namank_val > 0 else 1
    return mulank, bhagyank, namank

def get_fixed_numerology_prediction(mulank: int, bhagyank: int, lang: str = "en") -> str:
    if lang == "hi":
        return (
            f"**मूलांक {mulank} (राहु) + भाग्यांक {bhagyank} (मंगल) अद्वितीय विश्लेषण:**\n"
            "राहु और मंगल का संयोग आपको अत्यंत कुशाग्र, खोजी और साहसी व्यक्तित्व प्रदान करता है। "
            "आप स्थापित लीक से हटकर नए रास्ते तलाशने में सक्षम हैं। मूलांक 4 आपको विश्लेषणात्मक दृष्टि और दूरदर्शिता देता है, "
            "जबकि भाग्यांक 9 आपके भीतर अदम्य ऊर्जा, मानवीय संवेदना और कर्मठता भरता है। अत्यधिक जल्दबाजी या आवेश से बचें; "
            "धैर्यपूर्वक की गई योजनाएं आपको स्थायी यश एवं आर्थिक स्थिरता प्रदान करेंगी।"
        )
    elif lang == "mr":
        return (
            f"**मूलांक {mulank} (राहु) + भाग्यांक {bhagyank} (मंगळ) सखोल व्यक्तिमत्त्व:**\n"
            "राहु आणि मंगळ यांचा हा संयोग तुम्हाला तीक्ष्ण बुद्धिमत्ता, संशोधक दृष्टी आणि अफाट धैर्य प्रदान करतो. "
            "मूलांक ४ मुळे तुमच्यात पद्धतशीर काम करण्याची क्षमता येते, तर भाग्यांक ९ मुळे दृढ निश्चय आणि नेतृत्व कौशल्य लाभते. "
            "कोणत्याही कामात संयम बाळगल्यास तुम्हाला मोठे यश आणि आर्थिक प्रगती निश्चित मिळते."
        )
    elif lang == "gu":
        return (
            f"**મૂળાંક {mulank} (રાહુ) + ભાગ્યાંક {bhagyank} (મંગળ) વિશ્લેષણ:**\n"
            "રાહુ અને મંગળનો આ સમન્વય અદભુત આત્મવિશ્વાસ, ઊર્જા અને નવીન વિચારોનું સર્જન કરે છે. "
            "મૂળાંક ૪ વિશ્લેષણાત્મક શક્તિ આપે છે અને ભાગ્યાંક ૯ લક્ષ્યપ્રાપ્તિ માટે પ્રબળ ઉત્સાહ પૂરો પાડે છે. "
            "શાંતિ અને દીર્ઘદ્રષ્ટિથી કામ લેવાથી જીવનમાં અપેક્ષિત માન-સન્માન અને પ્રગતિ પ્રાપ્ત થશે."
        )
    else:
        return (
            f"**Driver {mulank} (Rahu) + Conductor {bhagyank} (Mars) Synthesis:**\n"
            "The electrifying combination of Rahu (analytical innovator) and Mars (warrior executor) endows you with "
            "unorthodox brilliance, relentless drive, and strong leadership instincts. You naturally identify structural "
            "loopholes and execute strategic solutions. Balancing impulsive enthusiasm with disciplined routine unlocks "
            "massive professional expansion and authoritative influence."
        )

def get_numerology_remedies(mulank: int, bhagyank: int, lang: str = "en") -> list:
    if lang == "hi":
        return [
            f"**अनुकूल शुभ रंग:** मूलांक {mulank} (राहु) व भाग्यांक {bhagyank} (मंगल) हेतु नीला, हल्का धूसर और गहरा लाल रंग श्रेष्ठ हैं।",
            "**वैदिक मंत्र जप:** प्रतिदिन 'गायत्री मंत्र' का 11 बार शांतिपूर्वक स्मरण करें।",
            "**आहार एवं जीवनशैली:** मंगलवार और शनिवार को सात्विक भोजन ग्रहण करें तथा तांबे अथवा चाँदी के पात्र से जल पिएं।",
            "**ग्रह शांति दान:** शनिवार को श्वान (कुत्ते) को रोटी खिलाएं तथा मंगलवार को गुड़ या लाल मसूर की दाल का दान करें।"
        ]
    elif lang == "mr":
        return [
            f"**शुभ रंग:** मूलांक {mulank} आणि भाग्यांक {bhagyank} साठी आकाशी निळा, लाल व चॉकलेटी रंग लाभदायक ठरतील.",
            "**वैदिक मंत्र:** दररोज गायत्री मंत्र व 'ॐ अं अंगारकाय नमः' चा जप करा.",
            "**सात्विक दिनचर्या:** मंगळवार व शनिवारी सात्विक आहार ठेवा; तांब्याच्या भांड्यातील पाणी प्या.",
            "**पुण्य कार्य:** शनिवारी मुक्या प्राण्यांना अन्न द्या व मंगळवारी गुळाचे दान करा."
        ]
    elif lang == "gu":
        return [
            f"**અનુકૂળ રંગો:** મૂળાંક {mulank} અને ભાગ્યાંક {bhagyank} માટે વાદળી, કેસરી અને લાલ રંગ શુભ રહેશે.",
            "**મંત્ર ઉપાસના:** ગાયત્રી મંત્ર તેમજ હનુમાન ચાલીસાનો નિત્ય પાઠ કરવો.",
            "**જીવનશૈલી:** મંગળવાર અને શનિવારે સાત્વિક ભોજન લેવું; તાંબાના પાત્રમાંથી જળ પીવું.",
            "**દાન પુણ્ય:** શનિવારે પક્ષીઓ/પ્રાણીઓને ચણ નાખવું અને મંગળવારે ગોળનું દાન કરવું."
        ]
    else:
        return [
            f"**Harmonizing Colors:** Integrate tones aligned with Driver {mulank} (Electric Blue, Slate Gray) and Conductor {bhagyank} (Warm Coral, Red).",
            "**Vedic Japa:** Chant the Gayatri Mantra 11 times daily to balance analytical fire with mental clarity.",
            "**Astro-Nutrition:** Keep Tuesdays and Saturdays light; hydrate from a copper or silver vessel.",
            "**Charity on Key Days:** Feed stray dogs on Saturdays (Rahu pacification) and donate red lentils or jaggery on Tuesdays."
        ]

def calculate_shani_paya(natal_moon_rashi_idx: int, saturn_rashi_idx: int, lang: str = "en"):
    house_from_saturn = ((natal_moon_rashi_idx - saturn_rashi_idx) % 12) + 1
    timeline_str = "29 March 2025 – 23 February 2028 (Meena / Pisces Transit)"

    if house_from_saturn in [2, 5, 9]:
        name = "Rajat Paya (Silver Feet / चाँदी का पाया)" if lang == "en" else "रजत पाया (चाँदी का पाया)"
        status = "Highly Auspicious & Protective (अति शुभ)" if lang == "en" else "अत्यंत शुभ एवं कल्याणकारी"
        desc = (
            "Saturn enters your chart on Silver Feet. This is the most benevolent metallic footing of Saturn. "
            "It cushions karmic debts, safeguards family finances, fosters intellectual breakthroughs, and brings "
            "support from authority figures and mentors throughout the Pisces transit."
        ) if lang == "en" else (
            "शनि देव आपकी जन्म राशि से रजत (चाँदी के) पाए पर गोचर कर रहे हैं। यह ज्योतिष में सबसे शुभ पाया माना जाता है। "
            "यह गोचर आर्थिक सुदृढ़ता, पद-प्रतिष्ठा में वृद्धि, पारिवारिक सुरक्षा और बौद्धिक निर्णयों में बड़ी सफलता प्रदान करता है।"
        )
        remedies = [
            "Maintain a small solid silver coin or square piece in your wallet or safe." if lang == "en" else "अपनी तिजोरी अथवा बटुए में चाँदी का एक ठोस चौकोर टुकड़ा अथवा सिक्का रखें।",
            "Offer pure milk mixed with water on a Shiva Lingam on Mondays." if lang == "en" else "सोमवार को शिवलिंग पर जल में थोड़ा कच्चा दूध मिलाकर अर्पित करें।"
        ]
    elif house_from_saturn in [3, 7, 10]:
        name = "Tamra Paya (Copper Feet / तांबे का पाया)" if lang == "en" else "ताम्र पाया (तांबे का पाया)"
        status = "Favorable & Progressive (शुभ)" if lang == "en" else "शुभ एवं प्रगतिशील"
        desc = "Steady gains through hard work and consistent efforts." if lang == "en" else "कठिन परिश्रम से स्थिर लाभ और मान-सम्मान की प्राप्ति।"
        remedies = ["Donate copper utensils or jaggery on Tuesdays." if lang == "en" else "मंगलवार को तांबे के बर्तन अथवा गुड़ का दान करें।"]
    elif house_from_saturn in [1, 6, 11]:
        name = "Swarna Paya (Gold Feet / सोने का पाया)" if lang == "en" else "स्वर्ण पाया (सोने का पाया)"
        status = "Testing / High Expenditure (मध्यम)" if lang == "en" else "संघर्षशील एवं व्ययकारी"
        desc = "Financial volatility; requires careful budgeting and ego control." if lang == "en" else "अनावश्यक व्यय पर नियंत्रण रखें और अहंकार से बचें।"
        remedies = ["Perform daily Hanuman Chalisa recitation." if lang == "en" else "प्रतिदिन हनुमान चालीसा का पाठ करें।"]
    else:
        name = "Loha Paya (Iron Feet / लोहे का पाया)" if lang == "en" else "लोह पाया (लोहे का पाया)"
        status = "Demanding / Caution Needed (सतर्कता)" if lang == "en" else "चुनौतीपूर्ण एवं सतर्कता योग्य"
        desc = "Hard labor, delay in projects, demands peak physical discipline." if lang == "en" else "परिश्रम अधिक फल विलंब से; धैर्य और संयम बनाए रखें।"
        remedies = ["Light a mustard oil lamp under a Peepal tree on Saturdays." if lang == "en" else "शनिवार को पीपल के वृक्ष पर सरसों के तेल का दीपक लगाएं।"]

    return name, status, desc, remedies, timeline_str

def calculate_shani_sadesati_dhaiya(moon_rashi_idx: int, saturn_rashi_idx: int, lang: str = "en"):
    house_from_moon = ((saturn_rashi_idx - moon_rashi_idx) % 12) + 1
    timeline_str = "29 March 2025 – 23 February 2028 (Meena / Pisces Transit)"

    if house_from_moon == 12:
        is_active = True
        status_type = "Sade Sati Phase 1 (Rising / चढ़ती साढ़े साती)" if lang == "en" else "साढ़े साती प्रथम चरण (आरंभिक / लग्न चरण)"
        impact_en = (
            "Saturn transits the 12th house from your natal Moon sign. Known as the Rising Phase of Sade Sati. "
            "It prompts deep inner introspection, expenditure restructuring, overseas or long-distance shifts, "
            "and detachment from non-essential commitments. While expenses and travel increase, operating with "
            "disciplined routines turns this into a period of massive long-term spiritual and professional restructuring."
        )
        impact_hi = (
            "शनि देव आपकी चन्द्र राशि से द्वादश (12वें) भाव में गोचर कर रहे हैं। यह साढ़े साती का प्रथम (आरंभिक) चरण कहलाता है। "
            "यह चरण जीवन में अनावश्यक व्यय पर नियंत्रण, दूरगामी योजनाओं, विदेश या सुदूर संपर्कों और आध्यात्मिक चिंतन का विस्तार करता है। "
            "आर्थिक मामलों में अत्यधिक सतर्कता और स्वास्थ्य व निद्रा का ध्यान रखें। अनुशासित दिनचर्या से यह समय जीवन को सुदृढ़ आधार देता है।"
        )
        impact_mr = (
            "शनी महाराज आपल्या चंद्र राशीपासून १२ व्या भावात गोचर करत आहेत. हा साडेसातीचा प्रथम (चढती साडेसाती) टप्पा आहे. "
            "या काळात खर्च वाढू शकतो, कामाच्या निमित्ताने प्रवास होतात व जीवनशैलीत मोठे बदल घडून येतात. "
            "आर्थिक व्यवहारात सावधगिरी बाळगा आणि आरोग्याकडे लक्ष द्या. प्रामाणिक परिश्रमाने मोठी प्रगती साध्य होते."
        )
        impact_gu = (
            "શનિ દેવ તમારી ચંદ્ર રાશિથી ૧૨મા ભાવમાં ગોચર કરી રહ્યા છે. આ સાડાસાતીનો પ્રથમ તબક્કો છે. "
            "આ સમયગાળામાં ખર્ચ પર અંકુશ રાખવો, લાંબા ગાળાનું આયોજન કરવું અને બિનજરૂરી દોડધામથી બચવું હિતાવહ છે. "
            "ધૈર્ય અને આધ્યાત્મિક સાધનાથી મુશ્કેલ કાર્યો પણ સરળતાથી પાર પડી શકે છે."
        )
        remedies = [
            "Light a mustard oil lamp beneath a Peepal tree on Saturday evenings and perform 7 circumambulations." if lang == "en" else "शनिवार की संध्या पीपल के वृक्ष के नीचे सरसों के तेल का दीपक प्रज्वलित करें एवं 7 परिक्रमा करें।",
            "Recite the Hanuman Chalisa and Dasharatha Shani Stotra daily with pure devotion." if lang == "en" else "नित्य 'हनुमान चालीसा' एवं 'दशरथ कृत शनि स्तोत्र' का पाठ करें।",
            "Serve domestic helpers, sanitation workers, and donate black sesame or footwear on Saturdays." if lang == "en" else "श्रमिकों, सफाई कर्मियों एवं दिव्यांगजनों की निःस्वार्थ सेवा करें एवं काले तिल अथवा जूते दान करें।",
            "Wear an iron ring crafted from a horse-shoe on your middle finger on a Saturday." if lang == "en" else "शनिवार को विधिपूर्वक मध्यमा अंगुली में लोहे या काले घोड़े की नाल का छल्ला धारण करें।"
        ]
        impact_txt = impact_hi if lang == "hi" else (impact_mr if lang == "mr" else (impact_gu if lang == "gu" else impact_en))
        return is_active, status_type, timeline_str, impact_txt, remedies

    elif house_from_moon == 1:
        is_active = True
        status_type = "Sade Sati Phase 2 (Peak / मध्य चरण)" if lang == "en" else "साढ़े साती द्वितीय चरण (शिखर काल)"
        desc = "Saturn transits directly over your natal Moon. Demands peak patience, emotional resilience, and steady focus." if lang == "en" else "शनि का चन्द्र राशि पर प्रत्यक्ष गोचर; मानसिक धैर्य, कड़ी मेहनत और व्यक्तिगत रूपांतरण का मुख्य काल।"
        remedies = ["Recite Maha Mrityunjaya Mantra daily." if lang == "en" else "प्रतिदिन महामृत्युंजय मंत्र का 108 बार जप करें।"]
        return is_active, status_type, timeline_str, desc, remedies

    elif house_from_moon == 2:
        is_active = True
        status_type = "Sade Sati Phase 3 (Setting / उतरती साढ़े साती)" if lang == "en" else "साढ़े साती तृतीय चरण (उतरती साढ़े साती)"
        desc = "Saturn moves into the 2nd house from natal Moon. Finances, speech, and family stabilization period." if lang == "en" else "शनि चन्द्र से दूसरे भाव में; वाणी पर संयम, पारिवारिक सामंजस्य और वित्तीय स्थिरता लाने का समय।"
        remedies = ["Donate food to needy elders on Saturdays." if lang == "en" else "शनिवार को वृद्धजनों को भोजन कराएं।"]
        return is_active, status_type, timeline_str, desc, remedies

    elif house_from_moon == 4:
        is_active = True
        status_type = "Kantaka Shani (4th House Dhaiya / छोटी पनौती)" if lang == "en" else "कंटक शनि ढैय्या (चतुर्थ भाव ढैय्या)"
        desc = "Saturn transits 4th from Moon. Focus on domestic harmony and maternal health." if lang == "en" else "शनि चन्द्र से चौथे भाव में; गृह शांति एवं माता के स्वास्थ्य पर ध्यान दें।"
        remedies = ["Offer blue flowers to Lord Shiva on Saturdays." if lang == "en" else "शनिवार को शिवलिंग पर नीले फूल अर्पित करें।"]
        return is_active, status_type, timeline_str, desc, remedies

    elif house_from_moon == 8:
        is_active = True
        status_type = "Ashtama Shani (8th House Dhaiya / अष्टम ढैय्या)" if lang == "en" else "अष्टम शनि ढैय्या (अष्टम भाव गोचर)"
        desc = "Saturn transits 8th from Moon. Extreme prudence required in investments and health." if lang == "en" else "शनि चन्द्र से आठवें भाव में; जोखिम भरे कार्यों से बचें और स्वास्थ्य का विशेष ध्यान रखें।"
        remedies = ["Chant 'Om Sham Shanicharaya Namah' 108 times daily." if lang == "en" else "प्रतिदिन 'ॐ शं शनैश्चराय नमः' का 108 बार जप करें।"]
        return is_active, status_type, timeline_str, desc, remedies

    else:
        is_active = False
        status_type = "No Sade Sati / Dhaiya Active" if lang == "en" else "साढ़े साती अथवा ढैय्या का प्रभाव नहीं है"
        desc = f"Saturn is currently in house {house_from_moon} from your natal Moon sign. You are completely free from Sade Sati and Dhaiya cycles!" if lang == "en" else f"शनि देव आपकी चन्द्र राशि से {house_from_moon}वें भाव में गोचर कर रहे हैं। आप साढ़े साती व ढैय्या के प्रभाव से पूर्णतः मुक्त हैं!"
        remedies = ["Maintain disciplined routines and assist service workers." if lang == "en" else "नियमित कर्मठता बनाए रखें और जरूरतमंदों का सहयोग करें।"]
        return is_active, status_type, timeline_str, desc, remedies

SHANI_VAHAN_DATA = {
    1: {"name": "🐴 Horse (Ghoda)", "nature": "Speed, Victory & Expansion", "advice": "Swift career progress and goal completion."},
    2: {"name": "🫏 Donkey (Gadha)", "nature": "Heavy Effort & Delayed Gains", "advice": "Avoid shortcuts; focus on systematic routine."},
    3: {"name": "🦊 Jackal (Siyar)", "nature": "Caution & Deceit Alert", "advice": "Be alert against hidden opposition or scams."},
    4: {"name": "🐘 Elephant (Hathi)", "nature": "Royalty, Honor & Luxury", "advice": "Auspicious gains and recognition from elders."},
    5: {"name": "🐂 Bull (Bail)", "nature": "Gradual & Steady Gains", "advice": "Disciplined persistence yields solid results."},
    6: {"name": "🦁 Lion (Sher)", "nature": "Power, Courage & Authority", "advice": "Excellent for competitive courage and leadership."},
    7: {"name": "🐦‍⬛ Crow (Kowwa)", "nature": "Restlessness & Minor Friction", "advice": "Practice silence (Mouna); avoid hasty arguments."},
    8: {"name": "🦚 Peacock (Mayur)", "nature": "Joy, Growth & Harmony", "advice": "Brings heartwarming news and relationship warmth."},
    9: {"name": "🦢 Swan (Hans)", "nature": "Peace, Wisdom & Clarity", "advice": "Supreme harmony and calm mental lucidity."}
}

def calculate_shani_vahan(birth_nak_idx1: int, transit_nak_idx1: int, lang: str = "en"):
    vahan_num = ((birth_nak_idx1 * 4) + transit_nak_idx1) % 9
    if vahan_num == 0:
        vahan_num = 9
    v_data = SHANI_VAHAN_DATA.get(vahan_num, SHANI_VAHAN_DATA[9])
    return vahan_num, f"{v_data['name']} — {v_data['nature']}"

def calculate_navtara(birth_idx: int, transit_idx: int):
    offset = (transit_idx - birth_idx) % 27
    cat = NAVTARA_NAMES[offset % 9]
    series = (offset // 9) + 1
    return cat, series

def get_personal_day_vibe(mulank: int, target_date: datetime.date, lang: str = "en"):
    u_day = target_date.day + target_date.month + target_date.year
    u_reduced = reduce_to_single_digit(u_day)
    p_day = reduce_to_single_digit(mulank + u_reduced)
    title = f"Vibration of Day {p_day}"
    desc = "Favorable for focused execution and strategic harmony."
    remedy = "Offer water to the rising Sun and take deep conscious breaths."
    return u_reduced, p_day, title, desc, remedy

def load_user_profile():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                data = json.load(f)
                if "dob" in data and isinstance(data["dob"], str):
                    data["dob"] = datetime.date.fromisoformat(data["dob"])
                if "tob" in data and isinstance(data["tob"], str):
                    data["tob"] = datetime.time.fromisoformat(data["tob"])
                return data
        except Exception:
            pass
    return {
        "name": "Okesh",
        "dob": datetime.date(1984, 1, 13),
        "tob": datetime.time(14, 0),
        "place": "Chhatrapati Sambhajinagar, India",
        "language": "en"
    }

def save_user_profile(data: dict):
    try:
        to_store = data.copy()
        if isinstance(to_store.get("dob"), (datetime.date, datetime.datetime)):
            to_store["dob"] = to_store["dob"].isoformat()
        if isinstance(to_store.get("tob"), datetime.time):
            to_store["tob"] = to_store["tob"].isoformat()
        with open(PROFILE_FILE, "w") as f:
            json.dump(to_store, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Save error: {e}")
        return False

if "profile" not in st.session_state:
    st.session_state.profile = load_user_profile()

if "current_page" not in st.session_state:
    st.session_state.current_page = "profile"

prof = st.session_state.profile
saved_lang = prof.get("language", "en")

# Top header and single language selector
col_top_l, col_top_r = st.columns([3, 2])
with col_top_l:
    st.markdown("<h2 style='margin:0; font-weight:900; color:#1e1b4b;'>✨ Navtara Pulse</h2>", unsafe_allow_html=True)
    st.caption(t("app_subtitle", saved_lang))

with col_top_r:
    lang_opts = ["en", "hi", "mr", "gu"]
    lang_labels = {"en": "English", "hi": "हिन्दी (Hindi)", "mr": "मराठी (Marathi)", "gu": "ગુજરાતી (Gujarati)"}
    curr_idx = lang_opts.index(saved_lang) if saved_lang in lang_opts else 0
    selected_lang = st.selectbox(
        t("lang_label", saved_lang),
        options=lang_opts,
        index=curr_idx,
        format_func=lambda x: lang_labels[x],
        label_visibility="collapsed"
    )

if selected_lang != saved_lang:
    prof["language"] = selected_lang
    st.session_state.profile = prof
    save_user_profile(prof)
    st.rerun()

current_lang = selected_lang

user_name = prof.get("name", "Okesh")
user_dob = prof.get("dob", datetime.date(1984, 1, 13))
user_tob = prof.get("tob", datetime.time(14, 0))
user_place = prof.get("place", "Chhatrapati Sambhajinagar, India")

# Calculate Janma Nakshatra, Pada, Moon Rashi, and Lagna (Ascendant)
janma_idx, janma_pada, natal_moon_rashi_idx, natal_rashi_deg, lagna_rashi_idx, lagna_deg = calculate_birth_chart(
    user_dob, user_tob, user_place
)
janma_name = NAKSHATRAS[janma_idx]
nak_personality_desc = get_nakshatra_description(janma_idx, current_lang)
nak_remedies = get_nakshatra_remedy(janma_idx, current_lang)

mulank, bhagyank, namank = calculate_numerology(user_dob, user_name)
num_remedies_list = get_numerology_remedies(mulank, bhagyank, current_lang)

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
is_ss_active, ss_status, ss_timeline, ss_impact, ss_remedies = calculate_shani_sadesati_dhaiya(
    natal_moon_rashi_idx, saturn_rashi_idx, current_lang
)

today_vahan_num, today_vahan = calculate_shani_vahan(
    janma_idx + 1, cur_moon_nak_idx + 1, current_lang
)
cur_nav_cat, cur_nav_series = calculate_navtara(janma_idx, cur_moon_nak_idx)
u_day, p_day, p_title, p_desc, num_remedy = get_personal_day_vibe(mulank, now_ist.date(), current_lang)

if st.session_state.current_page == "profile":
    with st.expander(t("edit_profile_expander", current_lang), expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            in_name = st.text_input(t("input_name", current_lang), value=user_name)
            in_dob = st.date_input(t("input_dob", current_lang), value=user_dob)
        with c2:
            in_tob = st.time_input(t("input_tob", current_lang), value=user_tob)
            in_place = st.text_input(t("input_place", current_lang), value=user_place)

        st.caption("ℹ️ *Janma Nakshatra, Pada, Moon Sign, and Lagna are calculated automatically from birth date, time, and place using Swiss Ephemeris.*")

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

    # -------------------------------------------------------------------------
    # SUBSECTION 1: NAVTARA & VEDIC ASTROLOGICAL PROFILE
    # -------------------------------------------------------------------------
    st.markdown(f"""
    <div class="light-card-profile">
        <div style="font-weight:800; font-size:16px; color:#78350f; margin-bottom:12px; border-bottom:1.5px solid #fed7aa; padding-bottom:6px;">
            {t('sec1_title', current_lang)}
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h3 style="margin:0; font-size:1.35rem; font-weight:800; color:#431407;">👤 {user_name}</h3>
                <div style="font-size:13.5px; color:#78350f; margin-top:3px;">
                    🎂 {user_dob.strftime('%d %B %Y')} • ⏰ {user_tob.strftime('%H:%M')} • 📍 {user_place}
                </div>
            </div>
            <div>
                <span class="badge-favorable" style="font-size:13px; padding:6px 12px;">
                    🌙 {RASHIS[natal_moon_rashi_idx].split(' ')[0]}
                </span>
            </div>
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:8px; margin-top:14px; text-align:center;">
            <div style="background:#ffffff; border-radius:10px; padding:10px 8px; border:1px solid #fed7aa;">
                <div style="font-size:11.5px; color:#9a3412; font-weight:700;">{t('janma_star_label', current_lang)}</div>
                <div style="font-size:14.5px; font-weight:800; color:#431407; margin-top:2px;">{janma_name}</div>
                <div style="font-size:11px; color:#b45309;">(#{janma_idx + 1} • Pada {janma_pada})</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px 8px; border:1px solid #fed7aa;">
                <div style="font-size:11.5px; color:#9a3412; font-weight:700;">{t('moon_rashi_label', current_lang)}</div>
                <div style="font-size:14.5px; font-weight:800; color:#431407; margin-top:2px;">{RASHIS[natal_moon_rashi_idx].split(' ')[0]}</div>
                <div style="font-size:11px; color:#b45309;">{natal_rashi_deg:.2f}° Sidereal</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px 8px; border:1px solid #fed7aa;">
                <div style="font-size:11.5px; color:#9a3412; font-weight:700;">{t('lagna_label', current_lang)}</div>
                <div style="font-size:14.5px; font-weight:800; color:#431407; margin-top:2px;">{RASHIS[lagna_rashi_idx].split(' ')[0]}</div>
                <div style="font-size:11px; color:#b45309;">{lagna_deg:.2f}° Ascendant</div>
            </div>
        </div>

        <div style="margin-top:12px; background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #fed7aa;">
            <div style="font-weight:700; font-size:13.5px; color:#9a3412; margin-bottom:4px;">
                {t('nak_personality_title', current_lang)} ({janma_name}):
            </div>
            <div style="font-size:13px; line-height:1.6; color:#431407;">
                {nak_personality_desc}
            </div>
        </div>

        <div style="margin-top:10px; background:#fff7ed; border-radius:10px; padding:12px 14px; border:1px solid #ffedd5;">
            <div style="font-weight:700; font-size:13.5px; color:#c2410c; margin-bottom:6px;">
                {t('nak_remedies_title', current_lang)}:
            </div>
    """, unsafe_allow_html=True)
    for nr in nak_remedies:
        st.markdown(f"<div style='font-size:12.8px; color:#7c2d12; margin-bottom:3px;'>• {nr}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SUBSECTION 2: CORE NUMEROLOGY BLUEPRINT & FIXED LIFE ATTRIBUTES
    # -------------------------------------------------------------------------
    st.markdown(f"""
    <div class="light-card-num">
        <div style="font-weight:800; font-size:16px; color:#064e3b; margin-bottom:12px; border-bottom:1.5px solid #a7f3d0; padding-bottom:6px;">
            {t('sec2_title', current_lang)}
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; text-align:center; margin-bottom:12px;">
            <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                <div style="font-size:12px; color:#047857; font-weight:700;">{t('mulank_label', current_lang)}</div>
                <div style="font-size:26px; font-weight:900; color:#065f46;">{mulank}</div>
                <div style="font-size:11px; color:#059669;">Rahu / Driver</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                <div style="font-size:12px; color:#047857; font-weight:700;">{t('bhagyank_label', current_lang)}</div>
                <div style="font-size:26px; font-weight:900; color:#065f46;">{bhagyank}</div>
                <div style="font-size:11px; color:#059669;">Mars / Conductor</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                <div style="font-size:12px; color:#047857; font-weight:700;">{t('namank_label', current_lang)}</div>
                <div style="font-size:26px; font-weight:900; color:#065f46;">{namank}</div>
                <div style="font-size:11px; color:#059669;">Chaldean Vibration</div>
            </div>
        </div>
        <div style="font-size:13.5px; line-height:1.6; color:#064e3b; background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #bbf7d0;">
            {get_fixed_numerology_prediction(mulank, bhagyank, current_lang)}
        </div>
        <div style="margin-top:10px; background:#f0fdf4; border-radius:10px; padding:12px 14px; border:1px solid #dcfce7;">
            <div style="font-weight:700; font-size:13.5px; color:#047857; margin-bottom:6px;">
                {t('num_remedies_title', current_lang)}:
            </div>
    """, unsafe_allow_html=True)
    for rem_num in num_remedies_list:
        st.markdown(f"<div style='font-size:12.8px; color:#065f46; margin-bottom:3px;'>• {rem_num}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SUBSECTION 3: SHANI PAYA & SHANI GOCHAR (SADE SATI / DHAIYA)
    # -------------------------------------------------------------------------
    sadesati_badge = "<span class='badge-danger' style='font-size:12px;'>⚠️ " + ss_status + "</span>" if is_ss_active else "<span class='badge-favorable' style='font-size:12px;'>✅ Favorable Shani Transit</span>"

    st.markdown(f"""
    <div class="light-card-paya">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1.5px solid #ddd6fe; padding-bottom:6px;">
            <span style="font-weight:800; font-size:16px; color:#3b0764;">
                {t('sec3_title', current_lang)}
            </span>
            {sadesati_badge}
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #e9d5ff; margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-weight:800; font-size:15px; color:#3b0764;">
                    {paya_name}
                </div>
                <div style="font-size:12px; font-weight:700; color:#6b21a8;">
                    ✦ {paya_status}
                </div>
            </div>
            <div style="font-size:12.5px; font-weight:600; color:#581c87; margin-top:4px;">
                ⏳ <b>{t('transit_timeline_lbl', current_lang)}:</b> {paya_timeline}
            </div>
            <div style="font-size:13px; line-height:1.55; color:#3b0764; margin-top:6px;">
                <b>{t('paya_impact_lbl', current_lang)}:</b><br>{paya_desc}
            </div>
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #e9d5ff; margin-bottom:10px;">
            <div style="font-weight:800; font-size:14.5px; color:#4c1d95; margin-bottom:4px;">
                🪐 {t('sadesati_card_title', current_lang)}:
            </div>
            <div style="font-size:12.5px; font-weight:600; color:#6b21a8; margin-bottom:6px;">
                ⏳ <b>{t('sadesati_timeline_lbl', current_lang)}:</b> {ss_status} ({ss_timeline})
            </div>
            <div style="font-size:13px; line-height:1.55; color:#2e1065;">
                <b>{t('sadesati_impact_lbl', current_lang)}:</b><br>{ss_impact}
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:10px; padding:12px 14px; border:1px solid #ddd6fe;">
            <div style="font-weight:700; font-size:13.5px; color:#581c87; margin-bottom:6px;">
                {t('shani_integrated_remedies', current_lang)}:
            </div>
    """, unsafe_allow_html=True)
    all_shani_remedies = paya_remedies + [r for r in ss_remedies if r not in paya_remedies]
    for sr in all_shani_remedies:
        st.markdown(f"<div style='font-size:12.8px; color:#4c1d95; margin-bottom:3px;'>• {sr}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    if st.button(t("btn_view_forecast", current_lang), use_container_width=True, type="primary"):
        st.session_state.current_page = "forecast"
        st.rerun()

elif st.session_state.current_page == "forecast":
    if st.button(t("btn_back_profile", current_lang), use_container_width=True):
        st.session_state.current_page = "profile"
        st.rerun()

    tab_today, tab_7day = st.tabs([t("tab_today", current_lang), t("tab_7days", current_lang)])

    # TAB 1: TODAY'S LIVE SYNTHESIS
    with tab_today:
        st.markdown(f"""
        <div style="background:#f8fafc; border:1.5px solid #e2e8f0; border-radius:14px; padding:16px; margin-bottom:14px;">
            <div style="font-weight:800; font-size:15px; color:#1e293b; margin-bottom:10px;">
                ⚡ {t('active_navtara_title', current_lang)}
            </div>
            <div style="font-size:20px; font-weight:900; color:#0f172a;">
                {cur_nav_cat} (Series {cur_nav_series})
            </div>
            <div style="font-size:13.5px; color:#475569; margin-top:4px;">
                Moon transiting in <b>{NAKSHATRAS[cur_moon_nak_idx]}</b> | Natal: <b>{janma_name}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c_vahan, c_pday = st.columns(2)
        with c_vahan:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:12px;">
                <div style="font-size:11.5px; color:#64748b; font-weight:700;">{t('shani_vahan_title', current_lang)}</div>
                <div style="font-size:15px; font-weight:800; color:#1e293b; margin-top:2px;">{today_vahan.split('—')[0]}</div>
                <div style="font-size:11.5px; color:#475569;">{today_vahan.split('—')[1] if '—' in today_vahan else ''}</div>
            </div>
            """, unsafe_allow_html=True)

        with c_pday:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:12px;">
                <div style="font-size:11.5px; color:#64748b; font-weight:700;">{t('personal_day_title', current_lang)}</div>
                <div style="font-size:15px; font-weight:800; color:#1e293b; margin-top:2px;">Day {p_day} Vibration</div>
                <div style="font-size:11.5px; color:#475569;">Driver {mulank} + Universal {u_day}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top:14px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px; padding:14px;">
            <div style="font-weight:800; font-size:14px; color:#1e40af; margin-bottom:8px;">
                {t('three_directives_title', current_lang)}:
            </div>
            <div style="font-size:13px; color:#1e3a8a; line-height:1.6;">
                1. <b>Navtara Strategy ({cur_nav_cat}):</b> Align high-stakes actions to favorable windows and observe diplomatic restraint during friction zones.<br>
                2. <b>Saturn Vahan Pace ({today_vahan.split('—')[0]}):</b> Follow methodical discipline, avoiding hasty short-cuts or impulsive escalations.<br>
                3. <b>Personal Day Alignment ({p_day}):</b> Channel focused energy into personal productivity and core long-term priorities.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # TAB 2: 7-DAY TRANSITION MATRIX WITH INTERACTIVE EXPANDERS
    with tab_7day:
        st.subheader(t("matrix_table_title", current_lang))
        
        # Calculate continuous 7-day Moon transit transitions
        nak_span = 360.0 / 27.0
        start_time = now_utc
        end_time = now_utc + datetime.timedelta(days=7)
        cur_lon = get_sidereal_lon(dt_to_jd(start_time), swe.MOON)
        active_nak = int(cur_lon / nak_span) % 27
        interval_start = start_time
        step = datetime.timedelta(minutes=30)
        eval_time = start_time
        transitions = []

        while eval_time <= end_time:
            eval_time += step
            lon = get_sidereal_lon(dt_to_jd(eval_time), swe.MOON)
            nak = int(lon / nak_span) % 27
            if nak != active_nak:
                low, high = eval_time - step, eval_time
                for _ in range(7):
                    mid = low + (high - low) / 2
                    if int(get_sidereal_lon(dt_to_jd(mid), swe.MOON) / nak_span) % 27 == active_nak:
                        low = mid
                    else:
                        high = mid
                boundary = high
                transitions.append({"nak_idx": active_nak, "start": interval_start, "end": boundary})
                interval_start = boundary
                active_nak = nak
        transitions.append({"nak_idx": active_nak, "start": interval_start, "end": end_time})

        matrix_rows = []
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

            s_ist = tr["start"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M IST)")
            e_ist = tr["end"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M IST)")

            matrix_rows.append({
                t("col_status", current_lang): status_str,
                t("col_timing", current_lang): f"**{s_ist} – {e_ist}**",
                t("col_star", current_lang): f"**{nak_name}**",
                t("col_series", current_lang): f"{cat} — *Series {series}*"
            })

        st.table(matrix_rows)

        st.markdown("---")
        st.markdown(f"#### 🔍 Daily Actionable Predictions & Targeted Remedies")

        for idx, tr in enumerate(transitions):
            nak_name = NAKSHATRAS[tr["nak_idx"]]
            cat, series = calculate_navtara(janma_idx, tr["nak_idx"])
            s_ist = tr["start"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M)")
            e_ist = tr["end"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M IST)")
            
            _, d_vahan = calculate_shani_vahan(janma_idx + 1, tr["nak_idx"] + 1, current_lang)
            _, d_pday, _, _, d_remedy = get_personal_day_vibe(mulank, tr["start"].astimezone(ist_tz).date(), current_lang)

            with st.expander(f"{s_ist} to {e_ist} • {cat} ({nak_name})", expanded=(idx == 0)):
                st.markdown(f"**Navtara Status:** {cat} (Series {series})")
                st.markdown(f"**Saturn Mount (Vahan):** {d_vahan}")
                st.markdown(f"**Personal Day Number:** Day {d_pday}")
                st.markdown(f"**Action Strategy:** {'Exercise protective restraint and delay high-stakes contracts.' if cat in ['Vipat', 'Pratyari', 'Vadha'] else 'Excellent window for key executions, purchases, and negotiations.'}")
                st.markdown(f"**Remedy for Window:** {d_remedy}")

    # OPTIONAL BOTTOM EXPANDER: PLANETARY POSITIONS
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    with st.expander(t("view_planets_btn", current_lang), expanded=False):
        planets_list = [
            ("Sun (Surya)", swe.SUN), ("Moon (Chandra)", swe.MOON),
            ("Mars (Mangal)", swe.MARS), ("Mercury (Budha)", swe.MERCURY),
            ("Jupiter (Guru)", swe.JUPITER), ("Venus (Shukra)", swe.VENUS),
            ("Saturn (Shani)", swe.SATURN), ("Rahu (North Node)", swe.MEAN_NODE)
        ]
        coords_data = []
        for p_name, p_id in planets_list:
            lon_p = get_sidereal_lon(jd_now, p_id)
            r_idx, r_deg = lon_to_rashi(lon_p)
            n_idx, n_pada = lon_to_nakshatra(lon_p)
            coords_data.append({
                "Graha": p_name,
                "Longitude": f"{lon_p:.2f}°",
                "Rashi": RASHIS[r_idx],
                "Nakshatra": f"{NAKSHATRAS[n_idx]} (Pada {n_pada})"
            })
        st.dataframe(coords_data, use_container_width=True)
