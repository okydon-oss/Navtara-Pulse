import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
import requests

# Streamlit Page Configuration
st.set_page_config(
    page_title="Navtara Pulse - Navtara & Daily Moon Transition Engine",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

I18N = {
    "hi": {
        "title": "Navtara Pulse",
        "subtitle": "सटीक नवतारा एवं दैनिक चंद्र गोचर राशिफल (Engine 3.0)",
        "intro_title": "वैदिक ज्योतिष के ज्ञान को अनलॉक करें",
        "intro_desc": "आज की व्यस्त जीवनशैली में, कई लोग नवतारा और वैदिक ज्योतिष से जुड़ी सटीक भविष्यवाणियों की प्राचीन अवधारणाओं से परिचित नहीं हो सकते हैं। यह ऐप एक मार्गदर्शक के रूप में कार्य करता है, जो आपको ज्योतिष द्वारा प्रदान किए जाने वाले गहन ज्ञान की खोज करने में मदद करता है। नक्षत्रों या चंद्र तारा-समूहों को समझकर, आप अपने व्यक्तित्व, जीवन पथ और संभावित चुनौतियों के बारे में मूल्यवान अंतर्दृष्टि प्राप्त कर सकते हैं।\n\nअपना व्यक्तिगत राशिफल देखने के लिए, बस अपना नाम, जन्म तिथि, जन्म समय और जन्म स्थान दर्ज करें। आइए हम सितारों के ज्ञान को उजागर करने में आपकी मदद करें!",
        "sidebar_header": "व्यक्तिगत जन्म विवरण",
        "name_label": "पूरा नाम",
        "dob_label": "जन्म तिथि",
        "time_label": "जन्म समय (24-घंटे का प्रारूप)",
        "place_label": "जन्म स्थान (शहर खोजें)",
        "calc_btn": "गोचर चक्र अपडेट करें",
        "current_moon": "आज का नक्षत्र",
        "navtara_status": "वर्तमान नवतारा स्थिति",
        "risk_index": "जोखिम स्तर",
        "golden_window": "अगला स्वर्णिम काल",
        "table_title": "7-दिवसीय चंद्रमा नक्षत्र गोचर तालिका",
        "table_desc": "आपकी जन्म तिथि व समय के आधार पर आगामी 7 दिनों का व्यक्तिगत नवतारा फलकथन",
        "chart_title": "7-दिवसीय अनुकूलता वक्र (Energy Score Index)",
        "briefing_title": "चयनित दिवस का विस्तृत दैनिक पूर्वानुमान व मार्गदर्शन",
        "health_pillar": "स्वास्थ्य, यात्रा व सुरक्षा",
        "fin_pillar": "धन, कर्ज व आर्थिक निर्णय",
        "career_pillar": "करियर, नौकरी व भाग्य",
        "mind_pillar": "मानसिक शांति व सुरक्षा कवच",
        "guide_title": "नवतारा चक्र सन्दर्भ निर्देशिका",
        "share_title": "📲 दोस्तों व परिजनों के साथ शेयर करें",
        "share_desc": "इस नवतारा चंद्र गोचर प्रेडिक्टर को अपने शुभचिंतकों के साथ साझा करें:",
        "footer": "Navtara Pulse © 2026 | वैदिक ज्योतिष के नवतारा सिद्धान्त एवं चंद्र गोचर गतियों पर आधारित।"
    },
    "en": {
        "title": "Navtara Pulse",
        "subtitle": "Precision Navtara & Daily Moon Transition Engine 3.0",
        "intro_title": "Unlocking the Wisdom of Vedic Astrology",
        "intro_desc": "In our fast-paced world, many people may not be familiar with ancient concepts like Navtara and accurate predictions rooted in Vedic astrology. This app serves as a guide, helping you explore the profound insights that astrology can offer. By understanding the Nakshatras, or lunar mansions, you can gain valuable knowledge about your personality, life path, and potential challenges.\n\nTo access your personalized horoscope, simply enter your name, date of birth, time of birth, and place of birth. Let us help you uncover the wisdom of the stars!",
        "sidebar_header": "Birth Details & Profile",
        "name_label": "Full Name",
        "dob_label": "Date of Birth",
        "time_label": "Time of Birth (24-Hour Format)",
        "place_label": "Place of Birth (Search City)",
        "calc_btn": "Recalculate Transits",
        "current_moon": "Current Moon Nakshatra",
        "navtara_status": "Active Navtara Status",
        "risk_index": "Risk Index Level",
        "golden_window": "Next Golden Window",
        "table_title": "7-Day Moon Transition Schedule",
        "table_desc": "Categorized 7-day Navtara forecast computed automatically from your birth details.",
        "chart_title": "7-Day Compatibility Index (Energy Score Curve)",
        "briefing_title": "Daily Prediction & Life Guidance",
        "health_pillar": "Health, Travel & Safety",
        "fin_pillar": "Money, Loans & Investments",
        "career_pillar": "Career, Job & Luck",
        "mind_pillar": "Mindset & Protection Shield",
        "guide_title": "Navtara Master Reference Guide",
        "share_title": "📲 Share with Friends & Family",
        "share_desc": "Send this personalized Moon Transit & Navtara forecast to your loved ones:",
        "footer": "Navtara Pulse © 2026 | Based on Vedic Astronomical Navtara principles & lunar transit speeds."
    },
    "mr": {
        "title": "Navtara Pulse",
        "subtitle": "अचूक नवतारा आणि दैनिक चंद्र गोचर राशीभविष्य 3.0",
        "intro_title": "वैदिक ज्योतिषाचे ज्ञान अनलॉक करा",
        "intro_desc": "आजच्या धावपळीच्या जगात, अनेक लोकांना नवतारा आणि वैदिक ज्योतिषावर आधारित अचूक भविष्यासारख्या प्राचीन संकल्पनांची माहिती नसते. हे ॲप तुम्हाला ज्योतिषातील सखोल ज्ञानाचा शोध घेण्यासाठी मार्गदर्शन करते. नक्षत्रांना समजून घेऊन, तुम्ही तुमचे व्यक्तित्व, जीवन प्रवास आणि संभाव्य आव्हानांबद्दल मौल्यवान माहिती मिळवू शकता.\n\nतुमचे वैयक्तिक राशीभविष्य पाहण्यासाठी, फक्त तुमचे नाव, जन्म तारीख, जन्म वेळ आणि जन्म ठिकाण प्रविष्ट करा. चला, ताऱ्यांचे ज्ञान उलगडण्यात आम्ही तुम्हाला मदत करतो!",
        "sidebar_header": "वैयक्तिक जन्म माहिती",
        "name_label": "पूर्ण नाव",
        "dob_label": "जन्म तारीख",
        "time_label": "जन्म वेळ",
        "place_label": "जन्म ठिकाण",
        "calc_btn": "गोचर चक्र अपडेट करा",
        "current_moon": "आजचे नक्षत्र",
        "navtara_status": "सध्याची नवतारा स्थिती",
        "risk_index": "जोखीम पातळी",
        "golden_window": "पुढील सुवर्ण काळ",
        "table_title": "७-दिवसीय चंद्र नक्षत्र गोचर तक्ता",
        "table_desc": "तुमच्या जन्म तपशिलांवर आधारित ७ दिवसांचे नवतारा राशीभविष्य",
        "chart_title": "७-दिवसीय अनुकूलता आलेख (Energy Score Index)",
        "briefing_title": "निवडलेल्या दिवसाचे सविस्तर दैनिक विश्लेषण",
        "health_pillar": "आरोग्य, प्रवास व सुरक्षा",
        "fin_pillar": "धन, कर्ज व आर्थिक निर्णय",
        "career_pillar": "करिअर, नोकरी व भाग्य",
        "mind_pillar": "मानसिक शांतता व संरक्षण",
        "guide_title": "नवतारा चक्र संदर्भ मार्गदर्शिका",
        "share_title": "📲 मित्र आणि नातेवाईकांसोबत शेअर करा",
        "share_desc": "हे नवतारा चंद्र गोचर प्रेडिक्टर तुमच्या जवळच्या लोकांशी शेअर करा:",
        "footer": "Navtara Pulse © 2026 | वैदिक ज्योतिष आणि चंद्र गोचर गतीवर आधारित."
    },
    "gu": {
        "title": "Navtara Pulse",
        "subtitle": "ચોક્કસ નવતારા અને દૈનિક ચંદ્ર ગોચર રાશિફળ 3.0",
        "intro_title": "વૈદિક જ્યોતિષના જ્ઞાનને અનાવૃત કરો",
        "intro_desc": "આજના ઝડપી યુગમાં, ઘણા લોકો નવતારા અને વૈદિક જ્યોતિષ પર આધારિત ચોક્કસ આગાહીઓ જેવી પ્રાચીન વિભાવનાઓથી અજાણ હોય છે. આ એપ તમને જ્યોતિષ દ્વારા મળતા ગહન જ્ઞાનનો સંગાથ આપવા માર્ગદર્શક તરીકે કામ કરે છે. નક્ષત્રોને સમજીને, તમે તમારા વ્યક્તિત્વ, જીવન માર્ગ અને સંભવિત પડકારો વિશે મૂલ્યવાન માહિતી મેળવી શકો છો.\n\nતમારું વ્યક્તિગત રાશિફળ જોવા માટે, બસ તમારું નામ, જન્મ તારીખ, જન્મ સમય અને જન્મ સ્થળ દાખલ કરો. ચાલો તારાઓના જ્ઞાનને સમજવામાં અમે તમારી મદદ કરીએ!",
        "sidebar_header": "વ્યક્તિગત જન્મ વિગતો",
        "name_label": "પૂરું નામ",
        "dob_label": "જન્મ તારીખ",
        "time_label": "જન્મ સમય",
        "place_label": "જન્મ સ્થળ",
        "calc_btn": "ગોચર ચક્ર ગણો",
        "current_moon": "આજનું નક્ષત્ર",
        "navtara_status": "વર્તમાન નવતારા સ્થિતિ",
        "risk_index": "જોખમ સ્તર",
        "golden_window": "આગામી ગોલ્ડન વિન્ડો",
        "table_title": "૭-દિવસીય ચંદ્ર નક્ષત્ર ગોચર કોષ્ટક",
        "table_desc": "તમારી જન્મ વિગતો આધારિત ૭ દિવસનું નવતારા વર્ગીકરણ",
        "chart_title": "૭-દિવસીય સફળતા ગ્રાફ (Energy Score Index)",
        "briefing_title": "પસંદ કરેલ દિવસનું દૈનિક વિશ્લેષણ",
        "health_pillar": "આરોગ્ય, મુસાફરી અને સુરક્ષા",
        "fin_pillar": "નાણાકીય, લોન અને રોકાણ",
        "career_pillar": "કરિયર, નોકરી અને ભાગ્ય",
        "mind_pillar": "માનસિક શાંતિ અને કવચ",
        "guide_title": "નવતારા ચક્ર સંદર્ભ ડિરેક્ટરી",
        "share_title": "📲 મિત્રો અને સગા-સંબંધીઓ સાથે શેર કરો",
        "share_desc": "આ નવતારા પ્રિડિક્ટર તમારા સ્નેહીજનો સાથે શેર કરો:",
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
        "desc": {"hi": "शरीर व मन का प्रभाव क्षेत्र। आलस्य या थकान हो सकती है।", "en": "Body & mind focus. Passivity or mild fatigue may occur."},
        "health": {"hi": "स्वास्थ्य सामान्य रहेगा। ड्राइविंग व लंबी यात्रा में जल्दबाजी न करें।", "en": "Health is fair. Drive carefully and avoid rushed travel."},
        "career": {"hi": "रूटीन काम निपटाएं। नई नौकरी या बड़े बदलाव में जल्दबाजी न करें।", "en": "Stick to routine tasks. Postpone job switches or big risks."},
        "fin": {"hi": "पैसों के लेन-देन में सतर्क रहें। कर्ज लेने या बड़ा निवेश टालें।", "en": "Avoid taking new loans or making speculative investments."},
        "mind": {"hi": "ध्यान, प्राणायाम व शांत मनोभाव से मानसिक स्थिरता मिलेगी।", "en": "Meditate or practice mindfulness to maintain emotional calm."}
    },
    {
        "index": 1, "code": "sampat", "symbol": "🟢", "status_type": "good", "score": 85,
        "name": {"hi": "सम्पत् (Sampat)", "en": "Sampat", "mr": "संपत्", "gu": "સંપત્"},
        "desc": {"hi": "धन लाभ, समृद्धि व आर्थिक प्रगति का शुभ समय।", "en": "Window of wealth, prosperity, and financial growth."},
        "health": {"hi": "ऊर्जावान महसूस करेंगे। छोटी-मोटी यात्राएं लाभदायक रहेंगी।", "en": "High energy level. Short business trips bring good rewards."},
        "career": {"hi": "नौकरी में पदोन्नति, नए अवसर व व्यापार में बड़ा लाभ।", "en": "Great day for job interviews, deals, and business expansion."},
        "fin": {"hi": "निवेश, बचत व नया वाहन/संपत्ति खरीदने के लिए उत्तम दिन।", "en": "Excellent time to invest, repay loans, or purchase assets."},
        "mind": {"hi": "पूर्ण आत्मविश्वास व मानसिक संतुष्टि बनी रहेगी।", "en": "Full confidence, mental clarity, and happiness."}
    },
    {
        "index": 2, "code": "vipat", "symbol": "🔴", "status_type": "danger", "score": 20,
        "name": {"hi": "विपत (Vipat)", "en": "Vipat", "mr": "विपत्", "gu": "વિપત્"},
        "desc": {"hi": "अचानक रुकावटें, चोट या वाद-विवाद का जोखिम।", "en": "High risk of unexpected hurdles, accidents, or arguments."},
        "health": {"hi": "वाहन सावधानी से चलाएं, दुर्घटना की आशंका। स्वास्थ्य का ध्यान रखें।", "en": "Drive carefully. High risk of minor accidents or fatigue."},
        "career": {"hi": "कार्यस्थल या ऑफिस में अधिकारियों से बहस से बचें। शांति रखें।", "en": "Avoid arguments with bosses or clients. Stay defensive."},
        "fin": {"hi": "धन हानि की संभावना। शेयर मार्केट, लॉटरी या नए कर्ज से बचें।", "en": "Risk of monetary loss. Avoid lending money or high-risk trades."},
        "mind": {"hi": "शांत चित्त रहें, सकारात्मक चिंतन करें व क्रोध से दूर रहें।", "en": "Practice peaceful reflection and keep anxious thoughts at bay."}
    },
    {
        "index": 3, "code": "kshema", "symbol": "🟢", "status_type": "good", "score": 80,
        "name": {"hi": "क्षेम (Kshema)", "en": "Kshema", "mr": "क्षेम", "gu": "ક્ષેમ"},
        "desc": {"hi": "सुरक्षा, पारिवारिक सुख व मन की शांति का काल।", "en": "Zone of health protection, safety, and domestic harmony."},
        "health": {"hi": "उत्तम स्वास्थ्य व तंदुरुस्ती। सुखद व सुरक्षित यात्रा।", "en": "Excellent health. Safe travel and peaceful family time."},
        "career": {"hi": "कार्यक्षेत्र में स्थायित्व, बॉस व साथियों से पूरा सहयोग।", "en": "Smooth progress at work. Good support from colleagues."},
        "fin": {"hi": "पुराने अटके पैसे वापस मिलेंगे। सुरक्षित एफडी/फंड्स में निवेश करें।", "en": "Good for long-term safe savings and recovering pending dues."},
        "mind": {"hi": "तनाव से पूरी मुक्ति व चिंता-रहित मन।", "en": "Relief from stress, peace of mind, and harmonious mood."}
    },
    {
        "index": 4, "code": "pratyari", "symbol": "🔴", "status_type": "danger", "score": 25,
        "name": {"hi": "प्रत्यरि (Pratyari)", "en": "Pratyari", "mr": "प्रत्यरि", "gu": "પ્રત્યરિ"},
        "desc": {"hi": "विरोधी सक्रिय, संवाद में गलतफहमी व रुकावट का खतरा।", "en": "Risk of opposition, misunderstandings, and minor delays."},
        "health": {"hi": "मानसिक तनाव या सिरदर्द। ड्राइविंग करते समय सतर्क रहें।", "en": "Watch out for stress-induced fatigue. Avoid harsh driving."},
        "career": {"hi": "ऑफिस पॉलिटिक्स से दूर रहें। कोई महत्वपूर्ण फैसला आज न लें।", "en": "Stay away from office gossip and delay key legal decisions."},
        "fin": {"hi": "अनावश्यक खर्चे बढ़ सकते हैं। क्रेडिट कार्ड या लोन लेने से बचें।", "en": "Risk of unexpected expenses. Refrain from taking debt."},
        "mind": {"hi": "संयम बरतें, प्रतिक्रिया देने में जल्दबाजी न करें व शांत रहें।", "en": "Maintain patience, refrain from quick reactions, and stay calm."}
    },
    {
        "index": 5, "code": "saadhaka", "symbol": "🟢", "status_type": "good", "score": 90,
        "name": {"hi": "साधक (Saadhaka)", "en": "Saadhaka", "mr": "साधक", "gu": "સાધક"},
        "desc": {"hi": "इच्छापूर्ति, सफलता, परीक्षा व कठिन कार्यों में विजय।", "en": "Success in complex goals, competitive exams, and tasks."},
        "health": {"hi": "शारीरिक ऊर्जा भरपूर। यात्रा सफल व मंगलमय रहेगी।", "en": "High stamina and vitality. Profitable business travel."},
        "career": {"hi": "नौकरी में बड़ी सफलता, इंटरव्यू में चयन व नया प्रोजेक्ट।", "en": "Victory in interviews, new job offers, and career growth."},
        "fin": {"hi": "आर्थिक स्थिति मजबूत होगी। नए सौदे व निवेश लाभदायक रहेंगे।", "en": "Strong financial gains, smart investment returns."},
        "mind": {"hi": "उच्च इच्छाशक्ति, तीक्ष्ण बुद्धि और नेतृत्व क्षमता।", "en": "High determination, sharp intellect, and spiritual power."}
    },
    {
        "index": 6, "code": "vadha", "symbol": "🔴", "status_type": "danger", "score": 15,
        "name": {"hi": "वध (Vadha)", "en": "Vadha", "mr": "वध", "gu": "વધ"},
        "desc": {"hi": "अत्यधिक संवेदनशील समय। भारी तनाव व संकट का जोखिम।", "en": "Highly vulnerable window. Risk of heavy stress or injury."},
        "health": {"hi": "स्वास्थ्य का विशेष ध्यान रखें। दुर्घटना से बचने हेतु यात्रा टालें।", "en": "Take extra health precautions. Postpone non-essential travel."},
        "career": {"hi": "नौकरी या व्यापार में 100% रक्षात्मक रहें। नया रिस्क न लें।", "en": "Be 100% cautious at work. Do not make risky career moves."},
        "fin": {"hi": "धन का बड़ा नुकसान संभव। ट्रेडिंग या जुआ/सट्टा से दूर रहें।", "en": "High risk of heavy losses. Strict NO to speculative bets."},
        "mind": {"hi": "मौन व आत्म-चिंतन का सहारा लें, तनावपूर्ण विचारों से दूर रहें।", "en": "Seek quiet meditation and maintain defensive composure."}
    },
    {
        "index": 7, "code": "mitra", "symbol": "🟢", "status_type": "good", "score": 85,
        "name": {"hi": "मित्र (Mitra)", "en": "Mitra", "mr": "मित्र", "gu": "મિત્ર"},
        "desc": {"hi": "मित्रों का सहयोग, सुखद संबंध व सकारात्मक समाचार।", "en": "Support from friends, harmonious relationships, and joy."},
        "health": {"hi": "उत्कृष्ट स्वास्थ्य। दोस्तों व परिवार के साथ यात्रा का आनंद।", "en": "Great health and enjoyable leisure trips with friends."},
        "career": {"hi": "सहकर्मियों व पार्टनरशिप से लाभ। नई डील्स फाइनल होंगी।", "en": "Good networking, successful team meetings, and partnerships."},
        "fin": {"hi": "आर्थिक लेन-देन शुभ रहेगा। आर्थिक मदद आसानी से मिलेगी।", "en": "Favorable day for financial discussions and steady gains."},
        "mind": {"hi": "प्रसन्नचित्त मन, आनंद और भावनात्मक संतुलन।", "en": "Joyful mood, happiness, and emotional balance."}
    },
    {
        "index": 8, "code": "ati_mitra", "symbol": "🟢🟢", "status_type": "golden", "score": 100,
        "name": {"hi": "अति-मित्र (Ati-Mitra)", "en": "Ati-Mitra", "mr": "अति-मित्र", "gu": "અતિ-मित्र"},
        "desc": {"hi": "सर्वोच्च स्वर्णिम काल (Golden Window)! हर कार्य में सफलता।", "en": "Supreme Golden Power Window for major breakthroughs!"},
        "health": {"hi": "उत्कृष्ट आरोग्य व आरोग्य लाभ। दूरगामी यात्राएं अति-शुभ।", "en": "Peak vitality and excellent health. Highly favorable travel."},
        "career": {"hi": "भाग्य का पूर्ण साथ। नई नौकरी, प्रमोशन व बड़ी व्यावसायिक जीत।", "en": "Maximum luck! Promotions, contract sign-offs, and victories."},
        "fin": {"hi": "बड़ा धन लाभ, लॉटरी/शेयर में फायदा व संपत्ति डील फाइनल।", "en": "Golden time to invest, buy property, or close profitable deals."},
        "mind": {"hi": "सर्वोच्च मानसिक स्पष्टता, आनंद व आध्यात्मिक संतुष्टि।", "en": "Supreme intellectual clarity, bliss, and supreme luck."}
    }
]

def compute_janma_nakshatra(dob, birth_time):
    """Automatically computes Janma Nakshatra index (1-27) based on DOB and Time."""
    birth_datetime = datetime.datetime.combine(dob, birth_time)
    base_epoch = datetime.datetime(2026, 8, 19, 10, 0, 0) # Swati #15 (index 14)
    diff_hours = (birth_datetime - base_epoch).total_seconds() / 3600.0
    nak_idx = (14 + int(diff_hours // 24.5)) % 27
    if nak_idx < 0:
        nak_idx += 27
    return NAKSHATRAS[nak_idx]["id"]

def calculate_navtara(janma_id, transit_id):
    """Calculates Navtara category object based on Janma and Transit Nakshatra IDs."""
    diff = (transit_id - janma_id + 27) % 9
    return NAVTARA_TYPES[diff]

def get_loc(obj, lang):
    """Returns localized string from dictionary with fallbacks."""
    if isinstance(obj, dict):
        return obj.get(lang, obj.get('hi', obj.get('en', '')))
    return str(obj)

def generate_7day_transits(janma_id, start_date):
    """Generates 7-day Moon transit schedule from start date."""
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
            "date_short": cursor_time.strftime('%a, %d %b'),
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

    # Language Switcher (English set as Default)
    lang_choice = st.selectbox(
        "🌐 Language / भाषा Select:",
        options=["en", "hi", "mr", "gu"],
        format_func=lambda x: {"en": "English", "hi": "हिन्दी (Hindi)", "mr": "मराठी (Marathi)", "gu": "ગુજરાતી (Gujarati)"}[x]
    )
    t = I18N[lang_choice]

    st.markdown("---")
    st.subheader(t["sidebar_header"])

    user_name = st.text_input(t["name_label"], value="माय प्रोफाइल")
    user_dob = st.date_input(t["dob_label"], value=datetime.date.today())
    
    # 24-Hour HH:MM Clock Selection Widget
    now_time = datetime.datetime.now().time()
    st.markdown(f"**⏰ {t['time_label']}:**")
    col_h, col_m = st.columns(2)
    with col_h:
        hour_opts = [f"{h:02d}" for h in range(24)]
        selected_hour = st.selectbox("HH (Hour)", options=hour_opts, index=now_time.hour)
    with col_m:
        min_opts = [f"{m:02d}" for m in range(60)]
        selected_minute = st.selectbox("MM (Minute)", options=min_opts, index=now_time.minute)

    user_time = datetime.time(int(selected_hour), int(selected_minute))

    # City / Birth Place Internet Lookup (3+ letters query)
    st.markdown(f"**📍 {t['place_label']}:**")
    place_query = st.text_input(
        "Type 3+ letters to search any city/town worldwide (Internet Lookup):", 
        value="Ujjain"
    )

    user_place = place_query.strip()

    # Internet lookup for typing 3+ letters
    if len(place_query.strip()) >= 3:
        try:
            headers = {"User-Agent": "NavtaraPulse/3.0 (AstroApp)"}
            params = {"q": place_query.strip(), "format": "json", "limit": 5}
            response = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers, timeout=2)
            if response.status_code == 200:
                results = response.json()
                if results:
                    online_cities = [r["display_name"] for r in results]
                    selected_online_place = st.selectbox("🌐 Select matched location from internet:", options=online_cities)
                    if selected_online_place:
                        user_place = selected_online_place.split(",")[0] + ", " + selected_online_place.split(",")[-1]
        except Exception:
            pass # Gracefully fall back to entered place_query if offline

    st.caption(f"📍 Active Location: **{user_place}**")

    # Compute Janma Nakshatra automatically based on DOB & Time
    selected_janma_id = compute_janma_nakshatra(user_dob, user_time)
    computed_janma_nak = NAKSHATRAS[selected_janma_id - 1]
    janma_name_str = get_loc(computed_janma_nak["name"], lang_choice)

    st.success(f"⭐ **Calculated Janma Nakshatra:**\n**{janma_name_str}** ({computed_janma_nak['rashi']})\n\n⏰ Birth Time: **{selected_hour}:{selected_minute}** (24h)")

    # Forecast start date defaults automatically to today
    forecast_start_date = datetime.date.today()

transits = generate_7day_transits(selected_janma_id, forecast_start_date)

st.title(f"🌙 {t['title']}")
st.caption(f"{t['subtitle']} | Place: {user_place} | Janma Star: {janma_name_str}")

# Localized Introductory Text
st.markdown(f"""
### **{t['intro_title']}**

{t['intro_desc']}
""")

st.markdown("---")

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

# Optimized Table Format to avoid horizontal scroll on mobile/desktop
table_data = []
for tr in transits:
    nak_n = get_loc(tr["nakshatra"]["name"], lang_choice).split(" ")[0]
    nav_n = get_loc(tr["navtara"]["name"], lang_choice)
    desc_n = get_loc(tr["navtara"]["desc"], lang_choice)
    
    table_data.append({
        "Day & Date": f"D{tr['day']} ({tr['date_short']})",
        "Moon Nakshatra": f"{nak_n}",
        "Navtara Category": f"{tr['navtara']['symbol']} {nav_n}",
        "General Forecast Summary": desc_n
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
        format_func=lambda x: f"Day {x+1}: {transits[x]['date_short']} - {get_loc(transits[x]['nakshatra']['name'], lang_choice)}"
    )
    
    sel_t = transits[selected_day_idx]
    sel_nav = sel_t["navtara"]
    sel_nav_name = get_loc(sel_nav["name"], lang_choice)
    
    st.info(f"**Selected Navtara:** {sel_nav['symbol']} **{sel_nav_name}** | Moon Star: **{get_loc(sel_t['nakshatra']['name'], lang_choice)}** ({sel_t['nakshatra']['lord']})")
    
    st.markdown(f"**🩺 {t['health_pillar']}:** {get_loc(sel_nav['health'], lang_choice)}")
    st.markdown(f"**💼 {t['career_pillar']}:** {get_loc(sel_nav['career'], lang_choice)}")
    st.markdown(f"**💰 {t['fin_pillar']}:** {get_loc(sel_nav['fin'], lang_choice)}")
    st.markdown(f"**🛡️ {t['mind_pillar']}:** {get_loc(sel_nav['mind'], lang_choice)}")

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

# Social Sharing Section
st.markdown("---")
st.subheader(t["share_title"])
st.caption(t["share_desc"])

share_text = f"🌙 Check out my 7-Day Moon Transit & Navtara Forecast on Navtara Pulse! Current Star: {today_nak_name} ({today_nav_name}). Try Navtara Pulse app now!"
encoded_share_text = share_text.replace(" ", "%20")

col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_share_text}"
    st.link_button("💬 Share on WhatsApp", whatsapp_url, use_container_width=True)

with col_s2:
    email_url = f"mailto:?subject=Navtara Pulse Forecast&body={encoded_share_text}"
    st.link_button("✉️ Share via Email", email_url, use_container_width=True)

with col_s3:
    telegram_url = f"https://t.me/share/url?url=https://navtara-pulse.streamlit.app&text={encoded_share_text}"
    st.link_button("✈️ Share on Telegram", telegram_url, use_container_width=True)

st.markdown("---")
st.caption(t["footer"])
