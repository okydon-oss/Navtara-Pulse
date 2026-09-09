import os
import json
import datetime
import math
import textwrap
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
        "lang_label": "🌐 Language Selection",
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
        "active_navtara_title": "Active Navtara Energy Right Now",
        "shani_vahan_title": "Today's Saturn Vehicle (Shani Vahan)",
        "personal_day_title": "Personal Day Number Vibration",
        "three_directives_title": "🎯 Three Tactical Rules for Today",
        "matrix_table_title": "Daily Moon Transition Table (Next 7 Days)",
        "col_status": "Status",
        "col_timing": "Day, Date & Time to Day, Date & Time",
        "col_star": "Nakshatra Name",
        "col_series": "Navtara Series",
        "view_planets_btn": "🔭 Toggle Real-Time Sidereal Planetary Coordinates",
        "auth_badge": "🔬 100% Precision Astronomical Engine",
        "auth_headline": "Why Navtara Pulse? Real Cosmic Timing, Zero Guesswork",
        "auth_body": "You don't need to know astrology to use this app. Just like ocean tides respond to the Moon, human mood, mental clarity, and decision outcomes flow in predictable 27-star rhythms. Navtara Pulse calculates NASA-grade Swiss Ephemeris coordinates to reveal your golden opportunity windows and high-friction blindspots in plain English.",
        "auth_benefit1": "🚀 <b>Strike at Peak Luck:</b> Know exact hours when the Moon enters your <i>Sampat</i> (Wealth) and <i>Ati-Mitra</i> (Best Support) stars for crucial deals, interviews, and purchases.",
        "auth_benefit2": "🛡️ <b>Shield from Friction:</b> Get early warnings before <i>Vipat</i> (Obstacles) or <i>Vadha</i> (Caution) periods start so you can sidestep arguments and risky gambles.",
        "auth_benefit3": "🎯 <b>Personalized Daily Blueprint:</b> Combines ancient 5,000-year-old Vedic Navtara, Saturn Transit speed, and Numerology into 3 actionable rules for your day.",
        "profile_card_title": "{name}'s Birth Profile",
        "btn_edit_details": "✏️ Edit Details",
        "btn_cancel_edit": "✕ Cancel",
        "new_user_title": "📝 User Profile & Birth Details",
        "today_transit_window": "Active Moon Transit Window",
        "today_detailed_pred_title": "🔮 In-Depth Cosmic Prediction for Today",
        "today_remedies_title": "🪔 Targeted Daily Vedic & Numerology Remedies",
        "timing_from": "Starts",
        "timing_to": "Ends"
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
        "active_navtara_title": "वर्तमान सक्रिय नवतारा स्थिति",
        "shani_vahan_title": "आज का शनि वाहन",
        "personal_day_title": "आज का व्यक्तिगत अंक (Personal Day)",
        "three_directives_title": "🎯 आज के लिए तीन स्वर्णिम नियम",
        "matrix_table_title": "दैनिक चन्द्र गोचर तालिका (आगामी 7 दिन)",
        "col_status": "स्थिति (Status)",
        "col_timing": "वार, दिनांक व समय से वार, दिनांक व समय तक",
        "col_star": "नक्षत्र नाम",
        "col_series": "नवतारा चक्र (Series)",
        "view_planets_btn": "🔭 प्रत्यक्ष ग्रह स्पष्ट स्थिति देखें",
        "auth_badge": "🔬 100% प्रामाणिक स्विस एफिमेरिस खगोलीय गणना",
        "auth_headline": "नवतारा पल्स क्यों? शुद्ध खगोलीय गणित, अंधविश्वास नहीं",
        "auth_body": "इस ऐप का लाभ लेने के लिए ज्योतिष का ज्ञान होना आवश्यक नहीं है। जैसे समुद्र की लहरें चन्द्रमा के गुरुत्वाकर्षण से संचालित होती हैं, वैसे ही मानव मन और ऊर्जा 27 नक्षत्रों के निश्चित चक्र से प्रभावित होती है। नवतारा पल्स नासा-मानक स्विस एफिमेरिस से आपकी व्यक्तिगत ऊर्जा का सटीक समय बताता है।",
        "auth_benefit1": "🚀 <b>शुभ समय का लाभ:</b> जानें कि कब चन्द्रमा आपके <i>सम्पत</i> (धन-लाभ) एवं <i>अति-मित्र</i> (सर्वोत्तम सफलता) नक्षत्र में है ताकि आप बड़े निर्णय और सौदे सही समय पर कर सकें।",
        "auth_benefit2": "🛡️ <b>कठिन समय से बचाव:</b> <i>विपत</i> (अड़चनें) अथवा <i>वध</i> (सावधानी) काल की अग्रिम जानकारी पाकर विवादों और जोखिम से स्वयं को सुरक्षित रखें।",
        "auth_benefit3": "🎯 <b>व्यक्तिगत दैनिक मार्गदर्शन:</b> 5,000 वर्ष प्राचीन वैदिक नवतारा, शनि गति और अंक ज्योतिष का संगम — आपके आज के दिन के 3 व्यावहारिक नियम।",
        "profile_card_title": "{name} का जन्म प्रोफाइल",
        "btn_edit_details": "✏️ विवरण बदलें",
        "btn_cancel_edit": "✕ निरस्त",
        "new_user_title": "📝 जन्म विवरण एवं प्रोफाइल",
        "today_transit_window": "वर्तमान चन्द्र नक्षत्र गोचर समयावधि",
        "today_detailed_pred_title": "🔮 आज का विस्तृत ज्योतिषीय फलादेश",
        "today_remedies_title": "🪔 आज के अचूक वैदिक एवं अंक ज्योतिषीय उपाय",
        "timing_from": "आरंभ",
        "timing_to": "समाप्ति"
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
        "active_navtara_title": "सद्य सक्रिय नवतारा ऊर्जा",
        "shani_vahan_title": "आजचे शनी वाहन",
        "personal_day_title": "आजचा व्यक्तिगत अंक",
        "three_directives_title": "🎯 आजच्या दिवसाचे ३ महत्त्वाचे नियम",
        "matrix_table_title": "दैनिक चंद्र संक्रमण तक्ता (पुढील ७ दिवस)",
        "col_status": "स्थिती",
        "col_timing": "वार, दिनांक व वेळ ते वार, दिनांक व वेळ",
        "col_star": "नक्षत्र नाव",
        "col_series": "नवतारा चक्र",
        "view_planets_btn": "🔭 प्रत्यक्ष ग्रह स्थिती तपासा",
        "auth_badge": "🔬 १००% वैज्ञानिक स्विस एफिमेरिस खगोलीय शुद्धता",
        "auth_headline": "नवतारा पल्स का? अचूक खगोलीय गणित, अंधश्रद्धा नाही",
        "auth_body": "या ॲपचा लाभ घेण्यासाठी ज्योतिषाचे ज्ञान असण्याची गरज नाही. ज्याप्रमाणे समुद्राच्या भरती-ओहोटी चंद्रावर अवलंबून असतात, त्याचप्रमाणे मानवी मन आणि निर्णय क्षमता २७ नक्षत्रांच्या भ्रमणावर आधारित असते. नवतारा पल्स नासा-मानक खगोलीय गणिताने तुमचा अनुकूल काळ दर्शवते.",
        "auth_benefit1": "🚀 <b>सुवर्ण संधीचा लाभ:</b> चंद्र तुमच्या <i>संपत</i> (धनलाभ) व <i>अति-मित्र</i> (सर्वोच्च यश) नक्षत्रात असताना महत्त्वाचे व्यवहार करा.",
        "auth_benefit2": "🛡️ <b>अडचणींपासून सावधगिरी:</b> <i>विपत</i> किंवा <i>वध</i> नक्षत्राची वेळ आधीच ओळखून वादविवाद आणि मोठे आर्थिक धोके टाळा.",
        "auth_benefit3": "🎯 <b>दैनिक कृती आराखडा:</b> ५,००० वर्षे प्राचीन वैदिक नवतारा, शनी गती आणि अंकशास्त्राचा संगम — तुमच्या दिवसासाठी ३ सुस्पष्ट नियम.",
        "profile_card_title": "{name} चे जन्म प्रोफाइल",
        "btn_edit_details": "✏️ तपशील बदला",
        "btn_cancel_edit": "✕ रद्द",
        "new_user_title": "📝 जन्म तपशील व प्रोफाइल",
        "today_transit_window": "सद्य चंद्र नक्षत्र गोचर कालावधी",
        "today_detailed_pred_title": "🔮 आजचे सविस्तर ज्योतिषीय फलादेश",
        "today_remedies_title": "🪔 आजचे अचूक वैदिक व अंकशास्त्र उपाय",
        "timing_from": "सुरुवात",
        "timing_to": "समाप्ती"
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
        "active_navtara_title": "હાલનું સક્રિય નવતારા ફળ",
        "shani_vahan_title": "આજનું શનિ વાહન",
        "personal_day_title": "આજનો વ્યક્તિગત અંક",
        "three_directives_title": "🎯 આજના ૩ સોનેરી નિયમો",
        "matrix_table_title": "દૈનિક ચંદ્ર ગોચર કોષ્ટક (આગામી ૭ દિવસ)",
        "col_status": "સ્થિતિ",
        "col_timing": "વાર, તારીખ અને સમય થી વાર, તારીખ અને સમય સુધી",
        "col_star": "નક્ષત્ર નામ",
        "col_series": "નવતારા શ્રેણી",
        "view_planets_btn": "🔭 વર્તમાન ગ્રહ સ્પષ્ટ સ્થિતિ જુઓ",
        "auth_badge": "🔬 ૧૦૦% શુદ્ધ સ્વિસ એફિમેરિસ ખગોળીય ગણતરી",
        "auth_headline": "નવતારા પલ્સ કેમ? શુદ્ધ ખગોળીય ગણિત, અંધશ્રદ્ધા મુક્ત",
        "auth_body": "આ એપ વાપરવા માટે જ્યોતિષ શીખવાની જરૂર નથી. જેમ સમુદ્રની ભરતી-ઓટ ચંદ્રથી પ્રભાવિત થાય છે, તેમ માનવ મન અને કાર્યક્ષમતા ૨૭ નક્ષત્રોના આધારે વહે છે. સ્વિસ એફિમેરિસ દ્વારા તમારી અંગત કુંડળી આધારિત શ્રેષ્ઠ અને સાવચેતીભર્યા કલાકો સરળ ભાષામાં જાણો.",
        "auth_benefit1": "🚀 <b>સુવર્ણ તક ઝડપો:</b> જાણો ક્યારે ચંદ્ર તમારા <i>સંપત</i> (ધનાગમન) અને <i>અતિ-મિત્ર</i> (સર્વોચ્ચ સાથ) નક્ષત્રમાં છે, જેથી મહત્વના કાર્યો સિદ્ધ થઈ શકે.",
        "auth_benefit2": "🛡️ <b>વિઘ્નોથી રક્ષણ:</b> <i>વિપત</i> કે <i>વધ</i> નક્ષત્રના સમયની અગાઉથી જાણ મેળવી વિવાદો અને મોટા આર્થિક જોખમો ટાળો.",
        "auth_benefit3": "🎯 <b>દૈનિક સરળ સૂત્રો:</b> ૫,૦૦૦ વર્ષ પ્રાચીન નવતારા, શનિ ગોચર અને અંકશાસ્ત્રનું અદભુત મિશ્રણ — તમારા દિવસ માટે ૩ નિર્ણાયક નિયમો.",
        "profile_card_title": "{name} ની જન્મ પ્રોફાઇલ",
        "btn_edit_details": "✏️ વિગત બદલો",
        "btn_cancel_edit": "✕ રદ કરો",
        "new_user_title": "📝 જન્મ વિગત અને પ્રોફાઇલ",
        "today_transit_window": "વર્તમાન ચંદ્ર નક્ષત્ર ગોચર સમયગાળો",
        "today_detailed_pred_title": "🔮 આજનું વિસ્તૃત જ્યોતિષીય ફળકથન",
        "today_remedies_title": "આજના સચોટ વૈદિક અને અંકશાસ્ત્ર ઉપાયો",
        "timing_from": "શરૂઆત",
        "timing_to": "સમાપ્તિ"
    }
}

def t(key: str, lang: str = "en") -> str:
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))

st.markdown("""
<style>
    .auth-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 50%, #fef3c7 100%);
        border: 1.5px solid #bae6fd;
        border-radius: 16px;
        padding: 18px 20px;
        margin-top: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.08);
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.profile-card-content) {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
    }
    .user-profile-bar {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1.5px solid #cbd5e1;
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 18px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
    }
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
            f"<b>नक्षत्र आराध्य देव:</b> भगवान {deity} एवं नक्षत्र स्वामी {lord} की नित्य आराधना करें।",
            f"<b>बीज मंत्र जप:</b> प्रतिदिन अथवा जन्म नक्षत्र के दिन <code>{mantra}</code> का 108 बार शांत मन से जप करें।",
            f"<b>पवित्र वृक्ष संरक्षण:</b> {tree} के पौधे का संवर्धन करें या उसे नियमित जल अर्पित करें।",
            "<b>सात्विक दान:</b> शुक्रवार को श्वेत वस्त्र, चावल, दूध अथवा मिश्री का जरूरतमंदों को दान करें।"
        ]
    elif lang == "mr":
        return [
            f"<b>नक्षत्र आराध्य दैवत:</b> {deity} आणि नक्षत्र स्वामी {lord} यांचे नित्य स्मरण व नामस्मरण करा.",
            f"<b>बीज मंत्र जप:</b> दररोज किंवा जन्म नक्षत्राच्या दिवशी <code>{mantra}</code> चा १०८ वेळा शांतपणे जप करा.",
            f"<b>पवित्र वृक्ष सेवा:</b> {tree} वृक्षाचे संवर्धन करा किंवा त्याला जल अर्पण करा.",
            "<b>सात्विक दान:</b> शुक्रवारी गरजूंना पांढरे वस्त्र अथवा दुधाचे पदार्थ दान करून पुण्य संपादन करा."
        ]
    elif lang == "gu":
        return [
            f"<b>નક્ષત્ર આરાધ્ય દેવ:</b> {deity} અને નક્ષત્ર સ્વામી {lord} ની નિયમિત ભક્તિ કરો.",
            f"<b>બીજ મંત્ર જાપ:</b> દરરોજ અથવા જન્મ નક્ષત્રના દિવસે <code>{mantra}</code> નો ૧૦૮ વખત જાપ કરવો.",
            f"<b>પવિત્ર વૃક્ષ સેવન:</b> {tree} ના વૃક્ષનું જતન કરો અથવા તેને જળ અર્પણ કરવું.",
            "<b>કલ્યાણકારી દાન:</b> શુક્રવારે જરૂરિયાતમંદોને સફેદ વસ્ત્ર, અન્ન કે સાકરનું દાન કરવું."
        ]
    else:
        return [
            f"<b>Nakshatra Deity Worship:</b> Offer prayers to {deity} and honor planetary ruler {lord}.",
            f"<b>Sacred Japa:</b> Recite <code>{mantra}</code> 108 times daily or on Moon transit over your birth star.",
            f"<b>Sacred Plant Connection:</b> Honor, plant, or water the {tree} to harmonize stellar frequencies.",
            "<b>Sattvic Charity:</b> Donate white grains, milk sweets, or clothes to harmonize Venusian currents."
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
            f"<b>मूलांक {mulank} (राहु) + भाग्यांक {bhagyank} (मंगल) अद्वितीय विश्लेषण:</b><br>"
            "राहु और मंगल का संयोग आपको अत्यंत कुशाग्र, खोजी और साहसी व्यक्तित्व प्रदान करता है। "
            "आप स्थापित लीक से हटकर नए रास्ते तलाशने में सक्षम हैं। मूलांक 4 आपको विश्लेषणात्मक दृष्टि और दूरदर्शिता देता है, "
            "जबकि भाग्यांक 9 आपके भीतर अदम्य ऊर्जा, मानवीय संवेदना और कर्मठता भरता है। अत्यधिक जल्दबाजी या आवेश से बचें; "
            "धैर्यपूर्वक की गई योजनाएं आपको स्थायी यश एवं आर्थिक स्थिरता प्रदान करेंगी।"
        )
    elif lang == "mr":
        return (
            f"<b>मूलांक {mulank} (राहु) + भाग्यांक {bhagyank} (मंगळ) सखोल व्यक्तिमत्त्व:</b><br>"
            "राहु आणि मंगळ यांचा हा संयोग तुम्हाला तीक्ष्ण बुद्धिमत्ता, संशोधक दृष्टी आणि अफाट धैर्य प्रदान करतो। "
            "मूलांक ४ मुळे तुमच्यात पद्धतशीर काम करण्याची क्षमता येते, तर भाग्यांक ९ मुळे दृढ निश्चय आणि नेतृत्व कौशल्य लाभते। "
            "कोणत्याही कामात संयम बाळगल्यास तुम्हाला मोठे यश आणि आर्थिक प्रगती निश्चित मिळते।"
        )
    elif lang == "gu":
        return (
            f"<b>મૂળાંક {mulank} (રાહુ) + ભાગ્યાંક {bhagyank} (મંગળ) વિશ્લેષણ:</b><br>"
            "રાહુ અને મંગળનો આ સમન્વય અદભુત આત્મવિશ્વાસ, ઊર્જા અને નવીન વિચારોનું સર્જન કરે છે। "
            "મૂળાંક ૪ વિશ્લેષણાત્મક શક્તિ આપે છે અને ભાગ્યાંક ૯ લક્ષ્યપ્રાપ્તિ માટે પ્રબળ ઉત્સાહ પૂરો પાડે છે। "
            "શાંતિ અને દીર્ઘદ્રષ્ટિથી કામ લેવાથી જીવનમાં અપેક્ષિત માન-સન્માન અને પ્રગતિ પ્રાપ્ત થશે।"
        )
    else:
        return (
            f"<b>Driver {mulank} (Rahu) + Conductor {bhagyank} (Mars) Synthesis:</b><br>"
            "The electrifying combination of Rahu (analytical innovator) and Mars (warrior executor) endows you with "
            "unorthodox brilliance, relentless drive, and strong leadership instincts. You naturally identify structural "
            "loopholes and execute strategic solutions. Balancing impulsive enthusiasm with disciplined routine unlocks "
            "massive professional expansion and authoritative influence."
        )

def get_numerology_remedies(mulank: int, bhagyank: int, lang: str = "en") -> list:
    if lang == "hi":
        return [
            f"<b>अनुकूल शुभ रंग:</b> मूलांक {mulank} (राहु) व भाग्यांक {bhagyank} (मंगल) हेतु नीला, हल्का धूसर और गहरा लाल रंग श्रेष्ठ हैं।",
            "<b>वैदिक मंत्र जप:</b> प्रतिदिन 'गायत्री मंत्र' का 11 बार शांतिपूर्वक स्मरण करें।",
            "<b>आहार एवं जीवनशैली:</b> मंगलवार और शनिवार को सात्विक भोजन ग्रहण करें तथा तांबे अथवा चाँदी के पात्र से जल पिएं।",
            "<b>ग्रह शांति दान:</b> शनिवार को श्वान (कुत्ते) को रोटी खिलाएं तथा मंगलवार को गुड़ या लाल मसूर की दाल का दान करें।"
        ]
    elif lang == "mr":
        return [
            f"<b>शुभ रंग:</b> मूलांक {mulank} आणि भाग्यांक {bhagyank} साठी आकाशी निळा, लाल व चॉकलेटी रंग लाभदायक ठरतील।",
            "<b>वैदिक मंत्र:</b> दररोज गायत्री मंत्र व 'ॐ अं अंगारकाय नमः' चा जप करा।",
            "<b>सात्विक दिनचर्या:</b> मंगळवार व शनिवारी सात्विक आहार ठेवा; तांब्याच्या भांड्यातील पाणी प्या।",
            "<b>पुण्य कार्य:</b> शनिवारी मुक्या प्राण्यांना अन्न द्या व मंगळवारी गुळाचे दान करा।"
        ]
    elif lang == "gu":
        return [
            f"<b>અનુકૂળ રંગો:</b> મૂળાંક {mulank} અને ભાગ્યાંક {bhagyank} માટે વાદળી, કેસરી અને લાલ રંગ શુભ રહેશે।",
            "<b>મંત્ર ઉપાસના:</b> ગાયત્રી મંત્ર તેમજ હનુમાન ચાલીસાનો નિત્ય પાઠ કરવો।",
            "<b>જીવનશૈલી:</b> મંગળવાર અને શનિવારે સાત્વિક ભોજન લેવું; તાંબાના પાત્રમાંથી જળ પીવું।",
            "<b>દાન પુણ્ય:</b> શનિવારે પક્ષીઓ/પ્રાણીઓને ચણ નાખવું અને મંગળવારે ગોળનું દાન કરવું।"
        ]
    else:
        return [
            f"<b>Harmonizing Colors:</b> Integrate tones aligned with Driver {mulank} (Electric Blue, Slate Gray) and Conductor {bhagyank} (Warm Coral, Red).",
            "<b>Vedic Japa:</b> Chant the Gayatri Mantra 11 times daily to balance analytical fire with mental clarity.",
            "<b>Astro-Nutrition:</b> Keep Tuesdays and Saturdays light; hydrate from a copper or silver vessel.",
            "<b>Charity on Key Days:</b> Feed stray dogs on Saturdays (Rahu pacification) and donate red lentils or jaggery on Tuesdays."
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
            "शनी महाराज आपल्या चंद्र राशीपासून १२ व्या भावात गोचर करत आहेत। हा साडेसातीचा प्रथम (चढती साडेसाती) टप्पा आहे। "
            "या काळात खर्च वाढू शकतो, कामाच्या निमित्ताने प्रवास होतात व जीवनशैलीत मोठे बदल घडून येतात। "
            "आर्थिक व्यवहारात सावधगिरी बाळगा आणि आरोग्याकडे लक्ष द्या। प्रामाणिक परिश्रमाने मोठी प्रगती साध्य होते।"
        )
        impact_gu = (
            "શનિ દેવ તમારી ચંદ્ર રાશિથી ૧૨મા ભાવમાં ગોચર કરી રહ્યા છે। આ સાડાસાતીનો પ્રથમ તબક્કો છે। "
            "આ સમયગાળામાં ખર્ચ પર અંકુશ રાખવો, લાંબા ગાળાનું આયોજન કરવું અને બિનજરૂરી દોડધામથી બચવું હિતાવહ છે। "
            "ધૈર્ય અને આધ્યાત્મિક સાધનાથી મુશ્કેલ કાર્યો પણ સરળતાથી પાર પડી શકે છે।"
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

def get_current_nakshatra_window(current_utc: datetime.datetime):
    """Computes exact start and end timeline of the current active Moon Nakshatra using bisection search."""
    nak_span = 360.0 / 27.0
    cur_lon = get_sidereal_lon(dt_to_jd(current_utc), swe.MOON)
    active_nak = int(cur_lon / nak_span) % 27
    step = datetime.timedelta(minutes=30)
    
    # Backtrack to find exact entry time
    t_back = current_utc
    start_boundary = current_utc - datetime.timedelta(hours=12)
    for _ in range(65):
        prev_t = t_back - step
        if int(get_sidereal_lon(dt_to_jd(prev_t), swe.MOON) / nak_span) % 27 != active_nak:
            low, high = prev_t, t_back
            for _ in range(8):
                mid = low + (high - low) / 2
                if int(get_sidereal_lon(dt_to_jd(mid), swe.MOON) / nak_span) % 27 == active_nak:
                    high = mid
                else:
                    low = mid
            start_boundary = high
            break
        t_back = prev_t

    # Step forward to find exact exit time
    t_fwd = current_utc
    end_boundary = current_utc + datetime.timedelta(hours=12)
    for _ in range(65):
        next_t = t_fwd + step
        if int(get_sidereal_lon(dt_to_jd(next_t), swe.MOON) / nak_span) % 27 != active_nak:
            low, high = t_fwd, next_t
            for _ in range(8):
                mid = low + (high - low) / 2
                if int(get_sidereal_lon(dt_to_jd(mid), swe.MOON) / nak_span) % 27 == active_nak:
                    low = mid
                else:
                    high = mid
            end_boundary = high
            break
        t_fwd = next_t

    return active_nak, start_boundary, end_boundary

def get_detailed_today_forecast(cat: str, series: int, transit_nak: str, janma_nak: str, vahan_name: str, p_day: int, lang: str = "en"):
    """Synthesizes an in-depth, structured tactical forecast for the day."""
    if lang == "hi":
        nature_dict = {
            "Janma": "शारीरिक ऊर्जा, नवीन विचार व आत्म-निरीक्षण का दिन। किसी भी नए कार्य की सुदृढ़ योजना बनाएं।",
            "Sampat": "धनार्जन, वित्तीय सौदों, निवेश और मूल्यवान चर्चाओं के लिए अत्यधिक अनुकूल एवं शुभ समय।",
            "Vipat": "अचानक विघ्न, अप्रत्याशित विलंब और मानसिक तनाव की संभावना। जोखिम भरे निर्णयों और विवाद से बचें।",
            "Kshema": "कल्याण, आरोग्य, पारिवारिक सुख एवं पूर्व-नियोजित कार्यों की सुगम सिद्धि का शुभ काल।",
            "Pratyari": "वैचारिक मतभेद, प्रतिस्पर्धा अथवा विरोध की स्थिति बन सकती है। कूटनीतिक संयम बनाए रखें।",
            "Sadhana": "लक्ष्य-प्राप्ति, कठिन परिश्रम और रणनीतिक प्रयासों में सफलता का स्वर्णिम अवसर।",
            "Vadha": "अति-सतर्कता का काल। संवेदनशील बातचीत, नया अनुबंध अथवा भारी आर्थिक जोखिम पूर्णतः टालें।",
            "Mitra": "सहयोग, सौहार्द, मित्रता और अनुबंधों में पारस्परिक विश्वास व लाभ प्राप्त होगा।",
            "Ati-Mitra": "सर्वोत्तम भाग्यशाली समय! अटके हुए कार्यों को गति दें; उच्चाधिकारियों का पूर्ण सहयोग मिलेगा।"
        }
        summary = nature_dict.get(cat, "संतुलित एवं सामान्य दिन।")
        return {
            "mind": f"चन्द्रमा का <b>{transit_nak}</b> में गोचर आपकी जन्म राशि के अनुसार <b>{cat} (चक्र {series})</b> ऊर्जा सक्रिय कर रहा है। मन में {summary}",
            "career": f"<b>व्यापार व कर्मक्षेत्र:</b> शनि के {vahan_name} के प्रभाव से जल्दबाजी के स्थान पर धैर्यपूर्ण योजना बनाएं। वित्तीय मामलों में व्यवस्थित कदम उठाएं।",
            "advice": f"<b>आज का व्यक्तिगत अंक {p_day}:</b> दिन के अंक की ऊर्जा एकाग्रता और संकल्पशक्ति को बढ़ाती है। किसी भी विवाद में न उलझें।"
        }
    elif lang == "mr":
        nature_dict = {
            "Janma": "नवीन ऊर्जा आणि आत्मपरीक्षणाचा काळ. महत्त्वाची पूर्वतयारी करण्यासाठी अनुकूल दिवस.",
            "Sampat": "धनलाभ, आर्थिक निर्णय, खरेदी आणि व्यावसायिक प्रगतीसाठी अत्यंत फलदायी काळ.",
            "Vipat": "अडचणी व कामात अनपेक्षित विलंब संभवतो. वादविवाद व आर्थिक जोखीम टाळणे श्रेयस्कर.",
            "Kshema": "आरोग्य, सुख-समाधान आणि शांततेचा दिवस. कामात सुलभता जाणवेल.",
            "Pratyari": "विरोध किंवा मतभेदांची शक्यता. बोलण्यावर संयम ठेवा आणि सबुरीने घ्या.",
            "Sadhana": "ध्येयपूर्ती, अभ्यास आणि नियोजनबद्ध कामात मोठे यश मिळवणारा दिवस.",
            "Vadha": "अत्यंत सावधगिरीचा काळ. महत्त्वाचे निर्णय आणि आर्थिक सौदे पुढे ढकलावेत.",
            "Mitra": "मित्र आणि सहकाऱ्यांचे सहकार्य लाभेल. संवाद आणि भागीदारीसाठी उत्तम.",
            "Ati-Mitra": "सर्वोच्च यशाचा अनुकूल काळ! महत्त्वाच्या कामांना गती द्या."
        }
        summary = nature_dict.get(cat, "संतुलित दिवस.")
        return {
            "mind": f"चंद्राचे <b>{transit_nak}</b> नक्षत्रातील भ्रमण <b>{cat} (चक्र {series})</b> प्रभाव दर्शवत आहे. {summary}",
            "career": f"<b>व्यवसाय व नोकरी:</b> शनीच्या {vahan_name} प्रभावाने शिस्तबद्ध रीतीने काम पूर्ण करा.",
            "advice": f"<b>वैयक्तिक अंक {p_day}:</b> धोरणात्मक दृष्टिकोन ठेवा आणि उद्दिष्ट निश्चित करा."
        }
    elif lang == "gu":
        nature_dict = {
            "Janma": "સ્વ-ચિંતન અને નવી યોજનાઓ ઘડવાનો સમય. સ્વાસ્થ્યનું ધ્યાન રાખવું.",
            "Sampat": "ધનલાભ, આર્થિક રોકાણ અને શુભ કાર્યો માટે ઉત્તમ અનુકૂળ સમયગાળો.",
            "Vipat": "અણધારી મુશ્કેલીઓ કે વિલંબ થઈ શકે છે. જોખમી નિર્ણયો ટાળવા.",
            "Kshema": "શાંતિ, આરોગ્ય અને પારિવારિક સુખ માટે અત્યંત શુભ સમય.",
            "Pratyari": "મતભેદ કે અવરોધ આવી શકે છે. વાણી અને વર્તનમાં નમ્રતા રાખવી.",
            "Sadhana": "મહેનતનું ફળ મળશે અને લક્ષ્ય તરફ આગળ વધવાનો શ્રેષ્ઠ અવસર.",
            "Vadha": "સાવચેતી રાખવી જરૂરી છે. કાનૂની કે આર્થિક વિવાદોથી દૂર રહેવું.",
            "Mitra": "મિત્રો અને સ્નેહીઓનો સાથ મળશે. પરસ્પર લાભદાયી વાટાઘાટો થશે.",
            "Ati-Mitra": "સર્વોચ્ચ શુભ ફળદાયી સમય! મહત્વના કામો હાથ ધરવા માટે શ્રેષ્ઠ."
        }
        summary = nature_dict.get(cat, "સામાન્ય દિવસ.")
        return {
            "mind": f"ચંદ્રનું <b>{transit_nak}</b> માં ગોચર <b>{cat} (શ્રેણી {series})</b> ઊર્જા લાવી રહ્યું છે. {summary}",
            "career": f"<b>કાર્યક્ષેત્ર:</b> શનિના {vahan_name} પ્રભાવ હેઠળ ધૈર્યથી આયોજન કરવું.",
            "advice": f"<b>વ્યક્તિગત અંક {p_day}:</b> સંતુલિત અને વિચારપૂર્વકના પગલાં સફળતા અપાવશે."
        }
    else:
        nature_dict = {
            "Janma": "Focus on personal vitality, introspection, and physical grounding. Plan and refine rather than rush.",
            "Sampat": "Highly auspicious for wealth accumulation, deal signings, high-value purchases, and financial growth.",
            "Vipat": "High-friction zone. Delays and sudden hurdles possible. Postpone aggressive moves and avoid speculation.",
            "Kshema": "Harmonious and protective. Favors health recovery, domestic peace, and smooth execution of routine affairs.",
            "Pratyari": "Potential resistance, opposing views, or competitive friction. Maintain diplomatic neutrality.",
            "Sadhana": "Peak accomplishment window. Dedicated effort yields tangible breakthroughs and strategic success.",
            "Vadha": "Vulnerable window requiring peak restraint. Avoid signing binding agreements, confrontations, or financial risk.",
            "Mitra": "Favorable camaraderie, networking, and helpful collaborations. Builds goodwill and fruitful alliances.",
            "Ati-Mitra": "Supreme golden window! Optimal support from superiors, mentors, and the universe for critical milestones."
        }
        summary = nature_dict.get(cat, "Balanced and steady progress.")
        return {
            "mind": f"The Moon transiting in <b>{transit_nak}</b> activates your <b>{cat} (Series {series})</b> star relative to your natal {janma_nak}. {summary}",
            "career": f"<b>Professional & Financial Focus:</b> Under Saturn's {vahan_name}, prioritize methodological persistence over hasty gambles. Lock down loose ends before committing capital.",
            "advice": f"<b>Personal Day {p_day} Vibration:</b> Channels focused mental clarity into your top priorities. Avoid scatter and preserve your energy."
        }

def get_today_actionable_remedies(cat: str, vahan_num: int, p_day: int, lang: str = "en") -> list:
    """Generates targeted Vedic and Numerology remedies tailored to today's cosmic pulse."""
    remedies = []
    if lang == "hi":
        if cat in ["Vipat", "Pratyari", "Vadha"]:
            remedies.append("🛡️ <b>नवतारा कवच उपाय:</b> संकट नाशक 'हनुमान चालीसा' का दो बार पाठ करें अथवा <code>ॐ नमः शिवाय</code> का 108 बार मानसिक जप करें।")
            remedies.append("🕊️ <b>शान्ति दान:</b> आज काले तिल अथवा जल में थोड़ा कच्चा दूध मिलाकर शिवलिंग पर अर्पित करें।")
        else:
            remedies.append("🌟 <b>नवतारा संवर्धन उपाय:</b> अनुकूल समय का लाभ लेने हेतु प्रातः सूर्य देव को तांबे के लोटे से अर्घ्य दें एवं 'गायत्री मंत्र' का जप करें।")
            remedies.append("🌿 <b>शुभ संकल्प:</b> किसी नए कार्य के आरंभ से पूर्व इष्टदेव का स्मरण कर मिश्री या गुड़ ग्रहण करें।")
        
        if vahan_num in [2, 3, 7]:  # Donkey, Jackal, Crow
            remedies.append("🐦‍⬛ <b>शनि वाहन शान्ति:</b> पक्षियों को जल व दाना दें अथवा काले श्वान को रोटी खिलाएं; कटु वाणी से बचें।")
        else:
            remedies.append("🪐 <b>शनि कृपा उपाय:</b> शाम के समय पीपल के समीप अथवा घर के मंदिर में सरसों या तिल के तेल का दीपक लगाएं।")
        remedies.append(f"🔢 <b>अंक ज्योतिष उपाय (Day {p_day}):</b> आज हल्का श्वेत अथवा हल्का पीला/नीला वस्त्र धारण करें और अनावश्यक तर्क-वितर्क से दूर रहें।")
    elif lang == "mr":
        if cat in ["Vipat", "Pratyari", "Vadha"]:
            remedies.append("🛡️ <b>नवतारा सुरक्षा उपाय:</b> मारुती स्तोत्र किंवा हनुमान चालीसा म्हणा; <code>ॐ नमः शिवाय</code> चा १०८ वेळा जप करा.")
            remedies.append("🕊️ <b>सात्विक दान:</b> मुक्या प्राण्यांना अन्न द्या किंवा शिवलिंगावर जलाभिषेक करा.")
        else:
            remedies.append("🌟 <b>शुभ नवतारा वृद्धी:</b> सकाळी सूर्याला तांब्याच्या पात्रातून जल अर्पण करा आणि गायत्री मंत्राचा जप करा.")
            remedies.append("🌿 <b>यशस्वी सुरुवात:</b> कामास सुरुवात करताना गूळ खाऊन व देवाचे स्मरण करून पुढे जा.")
        remedies.append("🪐 <b>शनी वाहन शांती:</b> संध्याकाळी तिळाच्या किंवा मोहरीच्या तेलाचा दिवा लावा; गरजू व्यक्तीला मदत करा.")
        remedies.append(f"🔢 <b>अंकशास्त्र उपाय (दिवस {p_day}):</b> आकाशी निळा किंवा पांढरा रंग वापरा आणि मानसिक शांतता ठेवा.")
    elif lang == "gu":
        if cat in ["Vipat", "Pratyari", "Vadha"]:
            remedies.append("🛡️ <b>નવતારા રક્ષા ઉપાય:</b> હનુમાન ચાલીસાનો પાઠ કરવો અને શાંત મનથી <code>ૐ નમઃ શિવાય</code> જાપ કરવો.")
            remedies.append("🕊️ <b>પુણ્ય દાન:</b> પક્ષીઓને ચણ નાખવું અને શિવલિંગ પર જળાભિષેક કરવો.")
        else:
            remedies.append("🌟 <b>શુભ ફળ વૃદ્ધિ:</b> સવારે સૂર્ય નારાયણને જળ અર્પણ કરી ગાયત્રી મંત્ર કરવો.")
            remedies.append("🌿 <b>મંગલ શરૂઆત:</b> શુભ કાર્ય પહેલાં ગોળ-પાણી ગ્રહણ કરી ઈષ્ટદેવનું સ્મરણ કરવું.")
        remedies.append("🪐 <b>શનિ વાહન ઉપાય:</b> સાંજે દીવો પ્રગટાવવો અને વડીલોના આશીર્વાદ લેવા.")
        remedies.append(f"🔢 <b>અંકશાસ્ત્ર ઉપાય (અંક {p_day}):</b> સફેદ અથવા આછો વાદળી રંગ અનુકૂળ રહેશે; શાંતિ જાળવવી.")
    else:
        if cat in ["Vipat", "Pratyari", "Vadha"]:
            remedies.append("🛡️ <b>Navtara Shield Remedy:</b> Recite the <i>Hanuman Chalisa</i> or chant <code>Om Namah Shivaya</code> 108 times to dissolve friction.")
            remedies.append("🕊️ <b>Karmic Neutralizer:</b> Offer fresh water or milk on a Shiva Lingam; avoid lending money or signing unvetted deals today.")
        else:
            remedies.append("🌟 <b>Navtara Expansion Remedy:</b> Offer water to the rising Sun and chant the Gayatri Mantra 11 times to magnify favorable opportunities.")
            remedies.append("🌿 <b>Golden Hour Karma:</b> Share a portion of food or sweets with someone in need before starting your primary task.")
        
        if vahan_num in [2, 3, 7]:  # Donkey, Jackal, Crow
            remedies.append("🐦‍⬛ <b>Saturn Mount Pacifier:</b> Feed grains or bread to crows/birds this morning; practice conscious silence (Mouna) during tense debates.")
        else:
            remedies.append("🪐 <b>Saturn Benevolence:</b> Light a mustard or sesame oil lamp in the evening and express gratitude to service workers.")
        remedies.append(f"🔢 <b>Personal Day {p_day} Harmonizer:</b> Wear white, light blue, or cream tones; stay hydrated from a copper or glass vessel.")
    return remedies

def load_user_profile():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                data = json.load(f)
                if "dob" in data and isinstance(data["dob"], str):
                    data["dob"] = datetime.date.fromisoformat(data["dob"])
                if "tob" in data and isinstance(data["tob"], str):
                    data["tob"] = datetime.time.fromisoformat(data["tob"])
                data["is_existing_user"] = True
                return data
        except Exception:
            pass
    return {
        "name": "Okesh",
        "dob": datetime.date(1984, 1, 13),
        "tob": datetime.time(14, 0),
        "place": "Chhatrapati Sambhajinagar, India",
        "language": "en",
        "is_existing_user": False
    }

def save_user_profile(data: dict):
    try:
        to_store = data.copy()
        to_store["is_existing_user"] = True
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

if "editing_profile" not in st.session_state:
    st.session_state.editing_profile = False

prof = st.session_state.profile
saved_lang = prof.get("language", "en")

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

auth_card_html = f"""<div class="auth-card">
<div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;">
    <span style="font-weight:900; font-size:16px; color:#0f172a;">
        {t('auth_headline', current_lang)}
    </span>
    <span style="background:#0284c7; color:#ffffff; padding:3px 10px; border-radius:20px; font-size:11.5px; font-weight:700;">
        {t('auth_badge', current_lang)}
    </span>
</div>
<div style="font-size:13.5px; line-height:1.6; color:#334155; margin-top:8px;">
    {t('auth_body', current_lang)}
</div>
<div style="display:grid; grid-template-columns:1fr; gap:8px; margin-top:12px;">
    <div style="background:#ffffff; border-radius:10px; padding:9px 12px; border:1px solid #bae6fd; font-size:13px; color:#0f172a;">
        {t('auth_benefit1', current_lang)}
    </div>
    <div style="background:#ffffff; border-radius:10px; padding:9px 12px; border:1px solid #fecaca; font-size:13px; color:#0f172a;">
        {t('auth_benefit2', current_lang)}
    </div>
    <div style="background:#ffffff; border-radius:10px; padding:9px 12px; border:1px solid #bbf7d0; font-size:13px; color:#0f172a;">
        {t('auth_benefit3', current_lang)}
    </div>
</div>
</div>"""
st.markdown(auth_card_html, unsafe_allow_html=True)

user_name = prof.get("name", "Okesh")
user_dob = prof.get("dob", datetime.date(1984, 1, 13))
user_tob = prof.get("tob", datetime.time(14, 0))
user_place = prof.get("place", "Chhatrapati Sambhajinagar, India")
is_existing = prof.get("is_existing_user", True)

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
    # Check if user is actively editing OR is a new user without saved profile
    if st.session_state.editing_profile or not is_existing:
        box_header = t("new_user_title", current_lang) if not is_existing else t("edit_profile_expander", current_lang)
        with st.container(border=True):
            st.markdown(f"""
            <div style="font-weight:800; font-size:15px; color:#0369a1; margin-bottom:12px;">{box_header}</div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                in_name = st.text_input(t("input_name", current_lang), value=user_name)
                in_dob = st.date_input(t("input_dob", current_lang), value=user_dob)
            with c2:
                in_tob = st.time_input(t("input_tob", current_lang), value=user_tob)
                in_place = st.text_input(t("input_place", current_lang), value=user_place)

            st.caption("ℹ️ *Janma Nakshatra, Pada, Moon Sign, and Lagna are calculated automatically from birth date, time, and place using Swiss Ephemeris.*")

            c_save, c_cancel = st.columns([2, 1])
            with c_save:
                if st.button(t("save_profile_btn", current_lang), use_container_width=True, type="primary"):
                    updated_data = {
                        "name": in_name,
                        "dob": in_dob,
                        "tob": in_tob,
                        "place": in_place,
                        "language": current_lang,
                        "is_existing_user": True
                    }
                    st.session_state.profile = updated_data
                    st.session_state.editing_profile = False
                    if save_user_profile(updated_data):
                        st.success(t("profile_saved_msg", current_lang))
                        st.rerun()
            with c_cancel:
                if is_existing and st.button(t("btn_cancel_edit", current_lang), use_container_width=True):
                    st.session_state.editing_profile = False
                    st.rerun()

    else:
        # Existing User Card: Profile info on left/middle, Edit button inside the profile box on the very right side
        profile_title = t("profile_card_title", current_lang).format(name=user_name)
        with st.container(border=True):
            col_prof_info, col_prof_btn = st.columns([3.2, 1.2])
            with col_prof_info:
                st.markdown(f"""
                <div class="profile-card-content">
                    <div style="font-weight:800; font-size:16px; color:#0f172a; margin-bottom:6px;">
                    👤 {profile_title}
                    </div>
                    <div style="font-size:13.5px; color:#475569; display:flex; flex-wrap:wrap; gap:12px;">
                    <span>🎂 <b>{user_dob.strftime('%d %B %Y')}</b></span>
                    <span>⏰ <b>{user_tob.strftime('%H:%M')}</b></span>
                    <span>📍 <b>{user_place}</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_prof_btn:
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                if st.button(t("btn_edit_details", current_lang), use_container_width=True):
                    st.session_state.editing_profile = True
                    st.rerun()

        st.markdown("<div style='margin-bottom:14px;'></div>", unsafe_allow_html=True)

    nak_remedies_rendered = "".join([f"<div style='font-size:12.8px; color:#7c2d12; margin-bottom:4px;'>• {nr}</div>" for nr in nak_remedies])
    sec1_html = f"""<div class="light-card-profile">
<div style="border-bottom:1.5px solid #fed7aa; padding-bottom:8px; margin-bottom:12px;">
    <span style="font-weight:800; font-size:16px; color:#78350f;">
        {t('sec1_title', current_lang)}
    </span>
</div>

<div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:8px; margin-top:6px; text-align:center;">
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
{nak_remedies_rendered}
</div>
</div>"""
    st.markdown(sec1_html, unsafe_allow_html=True)

    num_remedies_rendered = "".join([f"<div style='font-size:12.8px; color:#065f46; margin-bottom:4px;'>• {r}</div>" for r in num_remedies_list])
    sec2_html = f"""<div class="light-card-num">
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
{num_remedies_rendered}
</div>
</div>"""
    st.markdown(sec2_html, unsafe_allow_html=True)

    sadesati_badge = "<span class='badge-danger' style='font-size:12px;'>⚠️ " + ss_status + "</span>" if is_ss_active else "<span class='badge-favorable' style='font-size:12px;'>✅ Favorable Shani Transit</span>"
    all_shani_remedies = paya_remedies + [r for r in ss_remedies if r not in paya_remedies]
    shani_remedies_rendered = "".join([f"<div style='font-size:12.8px; color:#4c1d95; margin-bottom:4px;'>• {sr}</div>" for sr in all_shani_remedies])

    sec3_html = f"""<div class="light-card-paya">
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
{shani_remedies_rendered}
</div>
</div>"""
    st.markdown(sec3_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    if st.button(t("btn_view_forecast", current_lang), use_container_width=True, type="primary"):
        st.session_state.current_page = "forecast"
        st.rerun()

elif st.session_state.current_page == "forecast":
    if st.button(t("btn_back_profile", current_lang), use_container_width=True):
        st.session_state.current_page = "profile"
        st.rerun()

    tab_today, tab_7day = st.tabs([t("tab_today", current_lang), t("tab_7days", current_lang)])

    with tab_today:
        active_nak_idx, t_start_utc, t_end_utc = get_current_nakshatra_window(now_utc)
        start_ist_str = t_start_utc.astimezone(ist_tz).strftime("%A, %d %b %Y (%I:%M %p IST)")
        end_ist_str = t_end_utc.astimezone(ist_tz).strftime("%A, %d %b %Y (%I:%M %p IST)")

        status_badge = (
            "<span style='background:#fee2e2; color:#b91c1c; border:1px solid #fca5a5; padding:4px 12px; border-radius:20px; font-weight:800; font-size:12px;'>🔴 Caution / High Friction</span>"
            if cur_nav_cat in ["Vipat", "Pratyari", "Vadha"] else
            "<span style='background:#dcfce7; color:#15803d; border:1px solid #86efac; padding:4px 12px; border-radius:20px; font-weight:800; font-size:12px;'>🟢 Peak Favorable Cosmic Flow</span>"
        )

        pulse_html = f"""<div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border:1.5px solid #cbd5e1; border-radius:16px; padding:18px 20px; margin-bottom:14px; box-shadow:0 4px 14px rgba(15, 23, 42, 0.05);">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; border-bottom:1.5px solid #e2e8f0; padding-bottom:10px; margin-bottom:12px;">
    <div>
        <div style="font-weight:800; font-size:16px; color:#0f172a;">
            ⚡ {t('active_navtara_title', current_lang)}: <span style="color:#0284c7;">{cur_nav_cat}</span>
        </div>
        <div style="font-size:12px; color:#64748b; font-weight:600; margin-top:2px;">
            Navtara Cycle: <b>Series {cur_nav_series}</b> | Transiting: <b>{NAKSHATRAS[cur_moon_nak_idx]}</b> | Janma: <b>{janma_name}</b>
        </div>
    </div>
    {status_badge}
</div>

<div style="background:#f0f9ff; border:1.5px solid #bae6fd; border-radius:12px; padding:12px 14px; margin-top:8px;">
    <div style="font-weight:800; font-size:13px; color:#0369a1; display:flex; align-items:center; gap:6px;">
        ⏱️ {t('today_transit_window', current_lang)}
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:8px; font-size:12.8px;">
        <div style="background:#ffffff; border:1px solid #e0f2fe; border-radius:8px; padding:8px 10px;">
            <span style="color:#0284c7; font-weight:700; font-size:11px; display:block;">▶️ {t('timing_from', current_lang)}:</span>
            <span style="color:#0f172a; font-weight:800;">{start_ist_str}</span>
        </div>
        <div style="background:#ffffff; border:1px solid #e0f2fe; border-radius:8px; padding:8px 10px;">
            <span style="color:#0284c7; font-weight:700; font-size:11px; display:block;">⏹️ {t('timing_to', current_lang)}:</span>
            <span style="color:#0f172a; font-weight:800;">{end_ist_str}</span>
        </div>
    </div>
</div>
</div>"""
        st.markdown(pulse_html, unsafe_allow_html=True)

        c_vahan, c_pday = st.columns(2)
        with c_vahan:
            vahan_card_html = f"""<div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:12px;">
<div style="font-size:11.5px; color:#64748b; font-weight:700;">{t('shani_vahan_title', current_lang)}</div>
<div style="font-size:15px; font-weight:800; color:#1e293b; margin-top:2px;">{today_vahan.split('—')[0]}</div>
<div style="font-size:11.5px; color:#475569;">{today_vahan.split('—')[1] if '—' in today_vahan else ''}</div>
</div>"""
            st.markdown(vahan_card_html, unsafe_allow_html=True)

        with c_pday:
            pday_card_html = f"""<div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:12px;">
<div style="font-size:11.5px; color:#64748b; font-weight:700;">{t('personal_day_title', current_lang)}</div>
<div style="font-size:15px; font-weight:800; color:#1e293b; margin-top:2px;">Day {p_day} Vibration</div>
<div style="font-size:11.5px; color:#475569;">Driver {mulank} + Universal {u_day}</div>
</div>"""
            st.markdown(pday_card_html, unsafe_allow_html=True)

        today_pred = get_detailed_today_forecast(
            cur_nav_cat, cur_nav_series, NAKSHATRAS[cur_moon_nak_idx], janma_name,
            today_vahan.split('—')[0], p_day, current_lang
        )
        
        pred_card_html = f"""<div style="background:#ffffff; border:1.5px solid #fed7aa; border-radius:14px; padding:16px 18px; margin-top:14px; box-shadow:0 2px 10px rgba(249, 115, 22, 0.05);">
<div style="font-weight:800; font-size:15px; color:#9a3412; margin-bottom:10px; border-bottom:1.5px solid #ffedd5; padding-bottom:6px;">
    {t('today_detailed_pred_title', current_lang)}
</div>
<div style="font-size:13.2px; line-height:1.65; color:#431407; margin-bottom:8px;">
    {today_pred['mind']}
</div>
<div style="background:#fff7ed; border-radius:10px; padding:10px 12px; font-size:13px; color:#7c2d12; line-height:1.6; margin-bottom:8px; border:1px solid #ffedd5;">
    {today_pred['career']}
</div>
<div style="background:#fffbeb; border-radius:10px; padding:10px 12px; font-size:13px; color:#78350f; line-height:1.6; border:1px solid #fef3c7;">
    {today_pred['advice']}
</div>
</div>"""
        st.markdown(pred_card_html, unsafe_allow_html=True)

        today_remedies = get_today_actionable_remedies(cur_nav_cat, today_vahan_num, p_day, current_lang)
        remedies_items_html = "".join([f"<div style='font-size:13px; color:#064e3b; margin-bottom:6px; line-height:1.5;'>{rm}</div>" for rm in today_remedies])
        
        remedies_card_html = f"""<div style="background:#f0fdf4; border:1.5px solid #bbf7d0; border-radius:14px; padding:16px 18px; margin-top:14px; box-shadow:0 2px 10px rgba(22, 163, 74, 0.05);">
<div style="font-weight:800; font-size:15px; color:#065f46; margin-bottom:10px; border-bottom:1.5px solid #dcfce7; padding-bottom:6px;">
    {t('today_remedies_title', current_lang)}
</div>
<div>
    {remedies_items_html}
</div>
</div>"""
        st.markdown(remedies_card_html, unsafe_allow_html=True)

    with tab_7day:
        st.subheader(t("matrix_table_title", current_lang))
        
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
        st.markdown("#### 🔍 Daily Actionable Predictions & Targeted Remedies")

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
