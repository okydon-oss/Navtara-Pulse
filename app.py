import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
import plotly.express as px

# Streamlit Page Setup
st.set_page_config(
    page_title="Navtara Pulse - Navtara & Daily Moon Transition Engine",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

I18N = {
    "hi": {
        "title": "Navtara Pulse",
        "subtitle": "सटीक नवतारा एवं दैनिक चंद्र गोचर प्रेडिक्टर (Engine 3.0)",
        "sidebar_header": "व्यक्तिगत विवरण एवं प्रोफाइल",
        "quick_presets": "त्वरित प्रोफाइल (Presets):",
        "name_label": "पूरा नाम",
        "dob_label": "जन्म तिथि",
        "time_label": "जन्म समय",
        "place_label": "जन्म स्थान",
        "nakshatra_label": "जन्म नक्षत्र (Janma Nakshatra)",
        "start_date_label": "पूर्वानुमान प्रारंभ तिथि",
        "calc_btn": "गोचर चक्र जनरेट करें",
        "current_moon": "आज का नक्षत्र",
        "navtara_status": "वर्तमान नवतारा स्थिति",
        "risk_index": "जोखिम स्तर",
        "golden_window": "अगला स्वर्णिम काल",
        "table_title": "7-दिवसीय चंद्रमा नक्षत्र गोचर तालिका",
        "table_desc": "आपके चुने गए जन्म नक्षत्र के आधार पर 7 दिनों का नवतारा वर्गीकरण",
        "chart_title": "7-दिवसीय अनुकूलता वक्र (Energy Score Index)",
        "briefing_title": "चयनित दिवस का विस्तृत कार्यकारी विश्लेषण",
        "ops_pillar": "ऑपरेशन्स व प्लांट्स",
        "fin_pillar": "वित्तीय व पोर्टफोलियो",
        "mind_pillar": "रुद्राक्ष व रक्षा कवच",
        "guide_title": "नवतारा चक्र सन्दर्भ निर्देशिका",
        "footer": "Navtara Pulse © 2026 | वैदिक ज्योतिष के नवतारा सिद्धान्त एवं चंद्र गोचर गतियों पर आधारित।"
    },
    "en": {
        "title": "Navtara Pulse",
        "subtitle": "Precision Navtara & Daily Moon Transition Engine 3.0",
        "sidebar_header": "Profile & Birth Details",
        "quick_presets": "Quick Presets:",
        "name_label": "Full Name",
        "dob_label": "Date of Birth",
        "time_label": "Time of Birth",
        "place_label": "Place of Birth",
        "nakshatra_label": "Janma Nakshatra",
        "start_date_label": "Forecast Start Date",
        "calc_btn": "Calculate Transits",
        "current_moon": "Current Moon Nakshatra",
        "navtara_status": "Active Navtara Status",
        "risk_index": "Risk Index Level",
        "golden_window": "Next Golden Window",
        "table_title": "7-Day Moon Transition Schedule",
        "table_desc": "Categorized Navtara series for 7 days relative to your birth constellation.",
        "chart_title": "7-Day Compatibility Index (Energy Score Curve)",
        "briefing_title": "Executive Day Analysis & Strategic Action Plan",
        "ops_pillar": "Operations & Facilities",
        "fin_pillar": "Finance & Portfolio",
        "mind_pillar": "Mindset & Protection Shield",
        "guide_title": "Navtara Master Reference Guide",
        "footer": "Navtara Pulse © 2026 | Based on Vedic Astronomical Navtara principles & lunar transit speeds."
    },
    "mr": {
        "title": "Navtara Pulse",
        "subtitle": "अचूक नवतारा आणि दैनिक चंद्र गोचर इंजिन 3.0",
        "sidebar_header": "वैयक्तिक माहिती व जन्म नक्षत्र",
        "quick_presets": "द्रुत प्रोफाईल:",
        "name_label": "पूर्ण नाव",
        "dob_label": "जन्म तारीख",
        "time_label": "जन्म वेळ",
        "place_label": "जन्म ठिकाण",
        "nakshatra_label": "जन्म नक्षत्र",
        "start_date_label": "पूर्वानुमान प्रारंभ",
        "calc_btn": "गोचर चक्र जनरेट करा",
        "current_moon": "आजचे नक्षत्र",
        "navtara_status": "सध्याची नवतारा स्थिती",
        "risk_index": "जोखीम पातळी",
        "golden_window": "पुढील सुवर्ण काळ",
        "table_title": "७-दिवसीय चंद्र नक्षत्र गोचर तक्ता",
        "table_desc": "तुमच्या जन्म नक्षत्रावर आधारित ७ दिवसांचे नवतारा वर्गीकरण",
        "chart_title": "७-दिवसीय अनुकूलता आलेख (Energy Score Index)",
        "briefing_title": "निवडलेल्या दिवसाचे सविस्तर विश्लेषण",
        "ops_pillar": "ऑपरेशन्स व प्लांट्स",
        "fin_pillar": "आर्थिक व गुंतवणूक",
        "mind_pillar": "मानसिकता व संरक्षण",
        "guide_title": "नवतारा चक्र संदर्भ मार्गदर्शिका",
        "footer": "Navtara Pulse © 2026 | वैदिक ज्योतिष आणि चंद्र गोचर गतीवर आधारित."
    },
    "gu": {
        "title": "Navtara Pulse",
        "subtitle": "ચોક્કસ નવતારા અને દૈનિક ચંદ્ર ગોચર પ્રિડિક્ટર 3.0",
        "sidebar_header": "વ્યક્તિગત વિગત અને જન્મ નક્ષત્ર",
        "quick_presets": "ઝડપી પ્રોફાઇલ:",
        "name_label": "પૂરું નામ",
        "dob_label": "જન્મ તારીખ",
        "time_label": "જન્મ સમય",
        "place_label": "જન્મ સ્થળ",
        "nakshatra_label": "જન્મ નક્ષત્ર",
        "start_date_label": "આગાહી પ્રારંભ",
        "calc_btn": "ગોચર ચક્ર ગણો",
        "current_moon": "આજનું નક્ષત્ર",
        "navtara_status": "વર્તમાન નવતારા સ્થિતિ",
        "risk_index": "જોખમ સ્તર",
        "golden_window": "આગામી ગોલ્ડન વિન્ડો",
        "table_title": "૭-દિવસીય ચંદ્ર નક્ષત્ર ગોચર કોષ્ટક",
        "table_desc": "તમારા જન્મ નક્ષત્ર આધારિત ૭ દિવસનું નવતારા વર્ગીકરણ",
        "chart_title": "૭-દિવસીય સફળતા ગ્રાફ (Energy Score Index)",
        "briefing_title": "પસંદ કરેલ દિવસનું વિગતવાર વિશ્લેષણ",
        "ops_pillar": "ઓપરેશન્સ અને પ્લાન્ટ્સ",
        "fin_pillar": "નાણાકીય અને પોર્ટફોલિયો",
        "mind_pillar": "માનસિક સ્થિરતા અને કવચ",
        "guide_title": "નવતારા ચક્ર સંદર્ભ ડિરેક્ટરી",
        "footer": "Navtara Pulse © 2026 | વૈદિક જ્યોતિષ અને ચંદ્ર ગોચરની ગતિ પર આધારિત."
    }
}

NAKSHATRAS = [
    {"id": 1, "name": {"hi": "अश्विनी (Ashwini)", "en": "Ashwini", "mr": "अश्विनी", "gu": "અશ્વિની"}, "lord": "केतु (Ketu)", "rashi": "मेष (Aries)"},
    {"id": 2, "name": {"hi": "भरणी (Bharani)", "en": "Bharani", "mr": "भरणी", "gu": "ભરણી"}, "lord": "शुक्र (Venus)", "rashi": "मेष (Aries)"},
    {"id": 3, "name": {"hi": "कृत्तिका (Krittika)", "en": "Krittika", "mr": "कृत्तिका", "gu": "કૃતિકા"}, "lord": "सूर्य (Sun)", "rashi": "मेष/वृषभ"},
    {"id": 4, "name": {"hi": "रोहिणी (Rohini)", "en": "Rohini", "mr": "रोहिणी", "gu": "રોહિણી"}, "lord": "चंद्रमा (Moon)", "rashi": "वृषभ (Taurus)"},
    {"id": 5, "name": {"hi": "मृगशिरा (Mrigashira)", "en": "Mrigashira", "mr": "मृगशीर्ष", "gu": "મૃગશીર્ષ"}, "lord": "मंगल (Mars)", "rashi": "वृषभ/मिथुन"},
    {"id": 6, "name": {"hi": "आर्द्रा (Ardra)", "en": "Ardra", "mr": "आर्द्र", "gu": "આર્દ્રા"}, "lord": "राहु (Rahu)", "rashi": "मिथुन (Gemini)"},
    {"id": 7, "name": {"hi": "पुनर्वसु (Punarvasu)", "en": "Punarvasu", "mr": "पुनर्वसू", "gu": "પુનર્વસુ"}, "lord": "गुरु (Jupiter)", "rashi": "मिथुन/कर्क"},
    {"id": 8, "name": {"hi": "पुष्य (Pushya)", "en": "Pushya", "mr": "पुष्य", "gu": "પુષ્ય"}, "lord": "शनि (Saturn)", "rashi": "कर्क (Cancer)"},
    {"id": 9, "name": {"hi": "आश्लेषा (Ashlesha)", "en": "Ashlesha", "mr": "आश्लेषा", "gu": "આશ્લેષા"}, "lord": "बुध (Mercury)", "rashi": "कर्क (Cancer)"},
    {"id": 10, "name": {"hi": "मघा (Magha)", "en": "Magha", "mr": "मघा", "gu": "મઘા"}, "lord": "केतु (Ketu)", "rashi": "सिंह (Leo)"},
    {"id": 11, "name": {"hi": "पूर्वाफाल्गुनी (P. Phalguni)", "en": "Purva Phalguni", "mr": "पूर्वा फाल्गुनी", "gu": "પૂર્વા ફાલ્ગુની"}, "lord": "शुक्र (Venus)", "rashi": "सिंह (Leo)"},
    {"id": 12, "name": {"hi": "उत्तराफाल्गुनी (U. Phalguni)", "en": "Uttara Phalguni", "mr": "उत्तरा फाल्गुनी", "gu": "ઉત્તરા ફાલ્ગુની"}, "lord": "सूर्य (Sun)", "rashi": "सिंह/कन्या"},
    {"id": 13, "name": {"hi": "हस्त (Hasta)", "en": "Hasta", "mr": "हस्त", "gu": "હસ્ત"}, "lord": "चंद्रमा (Moon)", "rashi": "कन्या (Virgo)"},
    {"id": 14, "name": {"hi": "चित्रा (Chitra)", "en": "Chitra", "mr": "चित्रा", "gu": "ચિત્રા"}, "lord": "मंगल (Mars)", "rashi": "कन्या/तुला"},
    {"id": 15, "name": {"hi": "स्वाती (Swati)", "en": "Swati", "mr": "स्वाती", "gu": "સ્વાતિ"}, "lord": "राहु (Rahu)", "rashi": "तुला (Libra)"},
    {"id": 16, "name": {"hi": "विशाखा (Vishakha)", "en": "Vishakha", "mr": "विशाखा", "gu": "વિશાખા"}, "lord": "गुरु (Jupiter)", "rashi": "तुला/वृश्चिक"},
    {"id": 17, "name": {"hi": "अनुराधा (Anuradha)", "en": "Anuradha", "mr": "अनुराधा", "gu": "અનુરાધા"}, "lord": "शनि (Saturn)", "rashi": "वृश्चिक (Scorpio)"},
    {"id": 18, "name": {"hi": "ज्येष्ठा (Jyeshtha)", "en": "Jyeshtha", "mr": "ज्येष्ठा", "gu": "જ્યેષ્ઠા"}, "lord": "बुध (Mercury)", "rashi": "वृश्चिक (Scorpio)"},
    {"id": 19, "name": {"hi": "मूल (Mula)", "en": "Mula", "mr": "मूळ", "gu": "મૂળ"}, "lord": "केतु (Ketu)", "rashi": "धनु (Sagittarius)"},
    {"id": 20, "name": {"hi": "पूर्वाषाढ़ा (P. Ashadha)", "en": "Purva Ashadha", "mr": "पूर्वाषाढा", "gu": "પૂર્વાષાઢા"}, "lord": "शुक्र (Venus)", "rashi": "धनु (Sagittarius)"},
    {"id": 21, "name": {"hi": "उत्तराषाढ़ा (U. Ashadha)", "en": "Uttara Ashadha", "mr": "उत्तराषाढा", "gu": "ઉત્તરાષાઢા"}, "lord": "सूर्य (Sun)", "rashi": "धनु/मकर"},
    {"id": 22, "name": {"hi": "श्रवण (Shravana)", "en": "Shravana", "mr": "श्रवण", "gu": "શ્રવણ"}, "lord": "चंद्रमा (Moon)", "rashi": "मकर (Capricorn)"},
    {"id": 23, "name": {"hi": "धनिष्ठा (Dhanishta)", "en": "Dhanishta", "mr": "धनिष्ठा", "gu": "ધનિષ્ઠા"}, "lord": "मंगल (Mars)", "rashi": "मकर/कुंभ"},
    {"id": 24, "name": {"hi": "शतभिषा (Shatabhisha)", "en": "Shatabhisha", "mr": "शततारका", "gu": "શતભિષા"}, "lord": "राहु (Rahu)", "rashi": "कुंभ (Aquarius)"},
    {"id": 25, "name": {"hi": "पूर्वाभाद्रपद (P. Bhadrapada)", "en": "Purva Bhadrapada", "mr": "पूर्वा भाद्रपदा", "gu": "પૂર્વા ભાદ્રપદ"}, "lord": "गुरु (Jupiter)", "rashi": "कुंभ/मीन"},
    {"id": 26, "name": {"hi": "उत्तराभाद्रपद (U. Bhadrapada)", "en": "Uttara Bhadrapada", "mr": "उत्तरा भाद्रपदा", "gu": "ઉત્તરા ભાદ્રપદ"}, "lord": "शनि (Saturn)", "rashi": "मीन (Pisces)"},
    {"id": 27, "name": {"hi": "रेवती (Revati)", "en": "Revati", "mr": "रेवती", "gu": "રેવતી"}, "lord": "बुध (Mercury)", "rashi": "मीन (Pisces)"}
]

NAVTARA_TYPES = [
    {
        "index": 0, "code": "janma", "symbol": "⚪", "status_type": "neutral", "score": 40,
        "name": {"hi": "जन्म (Janma)", "en": "Janma", "mr": "जन्म", "gu": "જન્મ"},
        "desc": {"hi": "शरीर व मन का प्रभाव क्षेत्र। स्वाभविक पैसिविटी या सुस्ती आ सकती है।", "en": "Focus on body & mind. Passivity or fatigue may occur."},
        "ops": {"hi": "रूटीन कार्य निपटाएं। नए आक्रामक बदलावों को टालें।", "en": "Complete routine tasks. Postpone aggressive structural shifts."},
        "fin": {"hi": "इंडेक्स और पोर्टफोलियो को केवल ऑब्जर्व करें, नया ट्रेड न लें।", "en": "Observe portfolio trends. Avoid heavy speculative trades."},
        "mind": {"hi": "6-7-8-9 मुखी ब्रेसलेट का स्पर्श कर शांत रहें।", "en": "Touch 6-7-8-9 Mukhi Rudraksha bracelet to stay calm."}
    },
    {
        "index": 1, "code": "sampat", "symbol": "🟢", "status_type": "good", "score": 85,
        "name": {"hi": "सम्पत् (Sampat)", "en": "Sampat", "mr": "संपत्", "gu": "સંપત્"},
        "desc": {"hi": "धन, संपत्ति और व्यावसायिक लाभ की अनुकूल विंडो।", "en": "Window of wealth, prosperity, and asset allocation."},
        "ops": {"hi": "3-Bucket strategy के अनुकूल आवंटन निष्पादित करें।", "en": "Allocate resources strategically according to plan."},
        "fin": {"hi": "MFI & RSI चार्ट्स देखकर री-बैलेंसिंग का समय।", "en": "Analyze MFI & RSI charts; rebalance leveraged ETFs."},
        "mind": {"hi": "आर्थिक स्पष्टता व पूर्ण आत्मविश्वास।", "en": "Enhanced mental clarity and financial confidence."}
    },
    {
        "index": 2, "code": "vipat", "symbol": "🔴", "status_type": "danger", "score": 20,
        "name": {"hi": "विपत (Vipat)", "en": "Vipat", "mr": "विपत्", "gu": "વિપત્"},
        "desc": {"hi": "अचानक विघ्न, विवाद व तकनीकी डेटा विचलन का जोखिम।", "en": "High risk of sudden impediments and technical errors."},
        "ops": {"hi": "6 प्लांट्स में सर्वर, लैब डेटा या वेंडर विवाद पर शांत रहें।", "en": "Stay defensive during plant server delays or lab deviations."},
        "fin": {"hi": "नो-ट्रेड जोन। पैनिक में कोई शेयर न बेचें।", "en": "Strict No-Trade Zone. Avoid panic selling or leverage exposure."},
        "mind": {"hi": "7 मुखी (शनि) दाने का स्पर्श कर ॐ नमः शिवाय का जाप करें।", "en": "Touch 7 Mukhi (Saturn) bead and chant Om Namah Shivaya."}
    },
    {
        "index": 3, "code": "kshema", "symbol": "🟢", "status_type": "good", "score": 80,
        "name": {"hi": "क्षेम (Kshema)", "en": "Kshema", "mr": "क्षेम", "gu": "ક્ષેમ"},
        "desc": {"hi": "सुरक्षा, कल्याण व सुचारू ऑपरेशन्स ज़ोन।", "en": "Zone of safety, protection, and operational harmony."},
        "ops": {"hi": "पेंडिंग ऑडिट फाइलों व CAPA क्लीयरेंस को स्वीकृत करें।", "en": "Approve pending audit files and CAPA clearances safely."},
        "fin": {"hi": "सुरक्षित एसेट्स लॉक करने के लिए उत्तम समय।", "en": "Ideal window to lock capital into safe-haven assets."},
        "mind": {"hi": "तनाव से मुक्ति व पूर्ण एकाग्रता।", "en": "Relief from anxiety and excellent concentration."}
    },
    {
        "index": 4, "code": "pratyari", "symbol": "🔴", "status_type": "danger", "score": 25,
        "name": {"hi": "प्रत्यरि (Pratyari)", "en": "Pratyari", "mr": "प्रत्यरि", "gu": "પ્રત્યરિ"},
        "desc": {"hi": "बाधाएं, वैचारिक मतभेद व संवाद में भ्रम का जोखिम।", "en": "Risk of friction, miscommunication, and opposition."},
        "ops": {"hi": "सहकर्मियों व बाहरी ऑडिटर्स से तीखी बहस से बचें।", "en": "Avoid heated debates with external auditors or partners."},
        "fin": {"hi": "ऑप्शन ट्रेडिंग व हाई-रिस्क ट्रेड्स से दूर रहें।", "en": "Refrain from option trading or high-leverage positions."},
        "mind": {"hi": "8 मुखी (राहु) दाने के स्पर्श से नर्वस सिस्टम रिलैक्स रखें।", "en": "Touch 8 Mukhi (Rahu) bead to soothe nervous excitation."}
    },
    {
        "index": 5, "code": "saadhaka", "symbol": "🟢", "status_type": "good", "score": 90,
        "name": {"hi": "साधक (Saadhaka)", "en": "Saadhaka", "mr": "साधक", "gu": "સાધક"},
        "desc": {"hi": "साधना, कठिन लक्ष्यों में विजय व उच्च सिद्धि।", "en": "Achievement of complex goals, victory, and high focus."},
        "ops": {"hi": "जटिल तकनीकी समस्याओं का समाधान तेजी से निकालें।", "en": "Solve intricate technical issues and complex workflows."},
        "fin": {"hi": "वित्तीय योजनाओं व पोर्टफोलियो री-बैलेंसिंग को एग्जीक्यूट करें।", "en": "Execute long-term financial shifts and portfolio rebalancing."},
        "mind": {"hi": "उच्च मानसिक ऊर्जा और नेतृत्व गुण।", "en": "High mental stamina and authoritative leadership."}
    },
    {
        "index": 6, "code": "vadha", "symbol": "🔴", "status_type": "danger", "score": 15,
        "name": {"hi": "वध (Vadha)", "en": "Vadha", "mr": "वध", "gu": "વધ"},
        "desc": {"hi": "अत्यधिक संवेदनशील। भारी तनाव व बाधा का जोखिम।", "en": "Extremely vulnerable window. Risk of heavy stress."},
        "ops": {"hi": "100% डिफेंसिव मोड। कोई भी बड़ा रणनीतिक ऐलान न करें।", "en": "100% Defensive Mode. Do not announce strategic decisions."},
        "fin": {"hi": "टर्मिनल बंद रखें। केवल पैसिव होल्डिंग जारी रखें।", "en": "Close trading terminal. Maintain passive holdings only."},
        "mind": {"hi": "पीपल सेवा या महामृत्युंजय मंत्र का ध्यान करें।", "en": "Chant Mahamrityunjaya mantra or keep quiet meditation."}
    },
    {
        "index": 7, "code": "mitra", "symbol": "🟢", "status_type": "good", "score": 85,
        "name": {"hi": "मित्र (Mitra)", "en": "Mitra", "mr": "मित्र", "gu": "મિત્ર"},
        "desc": {"hi": "अनुकूलता, सामंजस्य व सकारात्मक परिणाम।", "en": "Harmonious relationship building, trust, and smooth flow."},
        "ops": {"hi": "टीम मीटिंग्स व वेंडर टॉक के लिए आदर्श दिन।", "en": "Ideal day for high-level team alignment & vendor reviews."},
        "fin": {"hi": "वित्तीय सलाहकारों से परामर्श व सुरक्षित निवेश।", "en": "Consult advisors and enter steady, calculated positions."},
        "mind": {"hi": "प्रसन्नचित्त मन व भावनात्मक संतुलन।", "en": "Joyful mood, balanced emotional state."}
    },
    {
        "index": 8, "code": "ati_mitra", "symbol": "🟢🟢", "status_type": "golden", "score": 100,
        "name": {"hi": "अति-मित्र (Ati-Mitra)", "en": "Ati-Mitra", "mr": "अति-मित्र", "gu": "અતિ-મિત્ર"},
        "desc": {"hi": "सर्वोच्च स्वर्णिम पावर विंडो (Golden Window)।", "en": "Supreme Golden Power Window for major breakthroughs."},
        "ops": {"hi": "मास्टर एग्जीक्यूशन, बड़े प्रोजेक्ट्स का शुभारंभ व साइन-ऑफ।", "en": "Master execution, major project launches, and sign-offs."},
        "fin": {"hi": "TQQQ/FNGU व एसेट एलोकेशन को लॉक करने का गोल्डन टाइम।", "en": "Golden opportunity to lock major asset allocations."},
        "mind": {"hi": "सर्वोच्च तार्किक व आध्यात्मिक स्पष्टता।", "en": "Supreme intellectual clarity and spiritual alignment."}
    }
]

def calculate_navtara(janma_id, transit_id):
    diff = (transit_id - janma_id + 27) % 9
    return NAVTARA_TYPES[diff]

def get_loc(obj, lang):
    if isinstance(obj, dict):
        return obj.get(lang, obj.get('hi', obj.get('en', '')))
    return str(obj)

def generate_7day_transits(janma_id, start_date):
    base_epoch = datetime.datetime(2026, 8, 19, 10, 0, 0)
    start_datetime = datetime.datetime.combine(start_date, datetime.time(9, 0))
    diff_hours = (start_datetime - base_epoch).total_seconds() / 3600.0
    
    current_nak_idx = (14 + int(diff_hours // 24.5)) % 27
    if current_nak_idx < 0:
        current_nak_idx += 27
        
    transits = []
    cursor_time = start_datetime

    for i in range(7):
        nak = NAKSHATRAS[current_nak_idx]
        nav = calculate_navtara(janma_id, nak["id"])
        
        end_time = cursor_time + datetime.timedelta(hours=24.5)
        
        transits.append({
            "day": i + 1,
            "start_time": cursor_time,
            "end_time": end_time,
            "time_range": f"{cursor_time.strftime('%a, %d %b %I:%M %p')} to {end_time.strftime('%a, %d %b %I:%M %p')}",
            "nakshatra": nak,
            "navtara": nav
        })
        current_nak_idx = (current_nak_idx + 1) % 27
        cursor_time = end_time

    return transits

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/moon.png", width=64)
    st.title("Navtara Pulse")
    st.caption("Engine 3.0 | Streamlit Edition")

    # Language Switcher
    lang_choice = st.selectbox(
        "🌐 Language / भाषा Select:",
        options=["hi", "en", "mr", "gu"],
        format_func=lambda x: {"hi": "हिन्दी (Hindi)", "en": "English", "mr": "मराठी (Marathi)", "gu": "ગુજરાતી (Gujarati)"}[x]
    )
    t = I18N[lang_choice]

    st.markdown("---")
    st.subheader(t["sidebar_header"])

    # Quick Presets Buttons
    st.write(t["quick_presets"])
    col_p1, col_p2, col_p3 = st.columns(3)
    preset_selected = None
    if col_p1.button("भरणी"):
        preset_selected = 2
    if col_p2.button("अश्विनी"):
        preset_selected = 1
    if col_p3.button("कृत्तिका"):
        preset_selected = 3

    user_name = st.text_input(t["name_label"], value="माय प्रोफाइल")
    
    # Set default Birth Date to Today
    user_dob = st.date_input(t["dob_label"], value=datetime.date.today())
    
    # Set default Birth Time to Current Time
    now_time = datetime.datetime.now().time()
    user_time = st.time_input(t["time_label"], value=datetime.time(now_time.hour, now_time.minute))

    # Set default Birth Place to Ujjain
    user_place = st.text_input(t["place_label"], value="उज्जैन (Ujjain)")

    # Nakshatra Selector
    nak_options = [f"{n['id']}. {get_loc(n['name'], lang_choice)} [{n['lord']}]" for n in NAKSHATRAS]
    default_nak_index = (preset_selected - 1) if preset_selected else 1
    selected_nak_str = st.selectbox(t["nakshatra_label"], nak_options, index=default_nak_index)
    selected_janma_id = int(selected_nak_str.split(".")[0])

    forecast_start_date = st.date_input(t["start_date_label"], value=datetime.date.today())

transits = generate_7day_transits(selected_janma_id, forecast_start_date)

st.title(f"🌙 {t['title']}")
st.caption(f"{t['subtitle']} | Place: {user_place}")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

today_t = transits[0]
today_nak_name = get_loc(today_t["nakshatra"]["name"], lang_choice)
today_nav_name = get_loc(today_t["navtara"]["name"], lang_choice)

with col_m1:
    st.metric(label=t["current_moon"], value=today_nak_name, delta=today_t["nakshatra"]["rashi"])

with col_m2:
    status_label = f"{today_t['navtara']['symbol']} {today_nav_name}"
    st.metric(label=t["navtara_status"], value=status_label)

with col_m3:
    risk_text = "HIGH RISK 🔴" if today_t["navtara"]["status_type"] == "danger" else ("GOLDEN 🟢🟢" if today_t["navtara"]["status_type"] == "golden" else "Favorable 🟢")
    st.metric(label=t["risk_index"], value=risk_text, delta_color="off")

with col_m4:
    golden_day = next((tr for tr in transits if tr["navtara"]["code"] in ["ati_mitra", "saadhaka"]), None)
    if golden_day:
        g_name = get_loc(golden_day["navtara"]["name"], lang_choice)
        g_nak = get_loc(golden_day["nakshatra"]["name"], lang_choice)
        st.metric(label=t["golden_window"], value=f"{g_name}", delta=f"Day {golden_day['day']} ({g_nak})")
    else:
        st.metric(label=t["golden_window"], value="Sampat / Mitra")

st.markdown("---")

st.subheader(f"📋 {t['table_title']}")
st.caption(t["table_desc"])

table_data = []
for tr in transits:
    nak_n = get_loc(tr["nakshatra"]["name"], lang_choice)
    nav_n = get_loc(tr["navtara"]["name"], lang_choice)
    desc_n = get_loc(tr["navtara"]["desc"], lang_choice)
    
    table_data.append({
        "Day": f"Day {tr['day']}",
        "Status": tr["navtara"]["symbol"],
        "Time Range": tr["time_range"],
        "Nakshatra": f"{nak_n} ({tr['nakshatra']['rashi']})",
        "Navtara Series": nav_n,
        "Lord": tr["nakshatra"]["lord"],
        "Summary": desc_n
    })

df_transits = pd.DataFrame(table_data)
st.dataframe(df_transits, use_container_width=True, hide_index=True)

st.markdown("---")

col_chart, col_brief = st.columns([1, 1])

with col_chart:
    st.subheader(f"📈 {t['chart_title']}")
    
    chart_days = [f"D{tr['day']}: {get_loc(tr['nakshatra']['name'], lang_choice).split(' ')[0]}" for tr in transits]
    chart_scores = [tr["navtara"]["score"] for tr in transits]
    chart_colors = ['#f43f5e' if tr["navtara"]["status_type"] == 'danger' else ('#f59e0b' if tr["navtara"]["status_type"] == 'golden' else '#10b981') for tr in transits]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart_days,
        y=chart_scores,
        mode='lines+markers',
        line=dict(color='#6366f1', width=3),
        marker=dict(size=12, color=chart_colors),
        text=[get_loc(tr["navtara"]["name"], lang_choice) for tr in transits],
        hovertemplate='<b>%{x}</b><br>Score: %{y}/100<br>Status: %{text}<extra></extra>'
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(range=[0, 110], gridcolor='rgba(255,255,255,0.1)'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        font=dict(color='#ffffff')
    )
    st.plotly_chart(fig, use_container_width=True)

with col_brief:
    st.subheader(f"💼 {t['briefing_title']}")
    
    selected_day_idx = st.selectbox(
        "Select Day to Inspect Details:",
        options=range(7),
        format_func=lambda x: f"Day {x+1}: {transits[x]['time_range'].split(' to ')[0]} - {get_loc(transits[x]['nakshatra']['name'], lang_choice)}"
    )
    
    sel_t = transits[selected_day_idx]
    sel_nav = sel_t["navtara"]
    sel_nav_name = get_loc(sel_nav["name"], lang_choice)
    
    st.info(f"**Selected Navtara:** {sel_nav['symbol']} **{sel_nav_name}** | Ruling Lord: **{sel_t['nakshatra']['lord']}**")
    
    st.markdown(f"**🏭 {t['ops_pillar']}:** {get_loc(sel_nav['ops'], lang_choice)}")
    st.markdown(f"**📊 {t['fin_pillar']}:** {get_loc(sel_nav['fin'], lang_choice)}")
    st.markdown(f"**🧘 {t['mind_pillar']}:** {get_loc(sel_nav['mind'], lang_choice)}")

st.markdown("---")

with st.expander(f"📚 {t['guide_title']} (Click to Expand)", expanded=False):
    guide_cols = st.columns(3)
    for idx, nav_item in enumerate(NAVTARA_TYPES):
        col_target = guide_cols[idx % 3]
        nav_n = get_loc(nav_item["name"], lang_choice)
        desc_n = get_loc(nav_item["desc"], lang_choice)
        
        with col_target:
            st.markdown(f"**{nav_item['index']+1}. {nav_n} ({nav_item['symbol']})**")
            st.caption(desc_n)

st.markdown("---")
st.caption(t["footer"])
