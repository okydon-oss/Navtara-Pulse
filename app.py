import streamlit as st
import datetime
import urllib.parse
import math

# ==========================================
# DEPENDENCY CHECKER
# ==========================================
try:
    import requests
    import ephem
except ModuleNotFoundError as e:
    st.error(f"🚨 **Missing Library Error:** `{e.name}`")
    st.info("To fix this, open your terminal/command prompt and run:")
    st.code("pip install requests ephem", language="bash")
    st.stop()

# ==========================================
# 1. PAGE CONFIGURATION & CSS
# ==========================================
st.set_page_config(page_title="Navtara Pulse", page_icon="🌙", layout="centered")

st.markdown("""
    <style>
    /* Purple background for language selector */
    div[data-baseweb="select"] > div { 
        background-color: #6a0dad !important; 
        color: white !important; 
        border-radius: 8px; 
        font-weight: bold; 
    }
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    
    /* Red Border & Glowing Highlight for Missing Input Fields */
    .missing-field div[data-baseweb="input"], 
    .missing-field div[data-baseweb="select"] > div,
    .missing-field input {
        border: 2px solid #ef4444 !important;
        border-radius: 8px !important;
        background-color: #fef2f2 !important;
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.35) !important;
    }
    .missing-field-warning {
        color: #dc2626 !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        margin-top: 4px;
        display: block;
    }

    /* Unified Transit Card Top Block */
    .transit-card { 
        background-color: #e0f2fe; 
        color: #0f172a;
        padding: 16px; 
        border-radius: 12px 12px 0 0; 
        margin-bottom: 0px; 
        border-left: 6px solid #0284c7; 
        border-top: 1px solid #bae6fd;
        border-right: 1px solid #bae6fd;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); 
    }
    .transit-card h5 {
        color: #0369a1 !important;
        margin-top: 0;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 6px;
    }
    .transit-card p {
        color: #1e293b !important;
        margin-bottom: 4px;
        font-size: 0.95rem;
    }
    /* Plain Birth Place Badge */
    .verified-badge { 
        background-color: #f1f5f9; 
        color: #1e293b; 
        padding: 8px 12px; 
        border-radius: 8px; 
        font-weight: 600; 
        border: 1px solid #cbd5e1;
        margin-top: 10px;
        margin-bottom: 15px; 
        display: block; 
        text-align: center; 
    }
    .status-badge { 
        font-weight: bold; 
        color: #0f172a; 
    }
    .current-badge {
        background-color: #0284c7;
        color: white;
        font-size: 0.75rem;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    /* Yellow Glittering Consolidated Primary Button */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #f59e0b 0%, #fef08a 50%, #d97706 100%) !important;
        color: #1e1b4b !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        border: 2px solid #f59e0b !important;
        border-radius: 10px !important;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.6);
        animation: glitter 2s infinite ease-in-out;
        transition: all 0.3s ease;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(245, 158, 11, 0.9);
        background: linear-gradient(135deg, #fbbf24 0%, #ffffff 50%, #f59e0b 100%) !important;
    }
    /* Disabled state for primary button */
    div[data-testid="stButton"] > button[kind="primary"]:disabled {
        background: #e2e8f0 !important;
        color: #94a3b8 !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: none !important;
        animation: none !important;
        cursor: not-allowed !important;
        transform: none !important;
    }

    @keyframes glitter {
        0%, 100% { box-shadow: 0 0 12px rgba(245, 158, 11, 0.5), 0 0 20px rgba(251, 191, 36, 0.4); }
        50% { box-shadow: 0 0 22px rgba(245, 158, 11, 0.9), 0 0 35px rgba(251, 191, 36, 0.8); }
    }

    /* Eye-Catching Yellow Glittering Expander Summary Bar */
    div[data-testid="stExpander"] {
        border-top: none !important;
        border-top-left-radius: 0 !important;
        border-top-right-radius: 0 !important;
        border-bottom-left-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
        border-left: 6px solid #d97706 !important;
        border-right: 1px solid #fef08a !important;
        border-bottom: 1px solid #fef08a !important;
        background-color: #fffbeb !important;
        margin-bottom: 18px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stExpander"] summary {
        background: linear-gradient(135deg, #f59e0b 0%, #fef08a 50%, #d97706 100%) !important;
        color: #1e1b4b !important;
        font-weight: 800 !important;
        font-size: 0.98rem !important;
        border-radius: 0 !important;
        padding: 12px 16px !important;
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.5);
        animation: glitter 2s infinite ease-in-out;
        transition: all 0.3s ease;
    }
    div[data-testid="stExpander"] summary:hover {
        background: linear-gradient(135deg, #fbbf24 0%, #ffffff 50%, #f59e0b 100%) !important;
        color: #0f172a !important;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        background-color: #ffffff !important;
        padding: 16px !important;
        border-radius: 0 0 10px 10px !important;
        border-top: 1px solid #fef08a !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONSTANTS & MULTILINGUAL DICTIONARIES
# ==========================================
nakshatra_list = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

nakshatra_lords_map = {
    "en": ["Ketu", "Venus (Shukra)", "Sun (Surya)", "Moon (Chandra)", "Mars (Mangal)", "Rahu", "Jupiter (Guru)", "Saturn (Shani)", "Mercury (Budh)"] * 3,
    "hi": ["केतु", "शुक्र", "सूर्य", "चंद्र", "मंगल", "राहु", "गुरु", "शनि", "बुध"] * 3,
    "mr": ["केतू", "शुक्र", "सूर्य", "चंद्र", "मंगळ", "राहु", "गुरु", "शनि", "बुध"] * 3,
    "gu": ["કેતુ", "શુક્ર", "સૂર્ય", "ચંદ્ર", "મંગળ", "રાહુ", "ગુરુ", "શનિ", "બુધ"] * 3
}

rashi_list_map = {
    "en": ["Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)", "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)", "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"],
    "hi": ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"],
    "mr": ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तूळ", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"],
    "gu": ["મેષ", "વૃષભ", "મિથુન", "કર્ક", "સિંહ", "કન્યા", "તુલા", "વૃશ્ચિક", "ધન", "મકર", "કુંભ", "મીન"]
}

lagna_list_map = rashi_list_map

navtara_names_map = {
    "en": ["Janma (Self / Body) ⚪", "Sampat (Wealth / Progress) 🟢", "Vipat (Obstacles / Delays) 🔴", "Kshema (Wellbeing / Comfort) 🟢", "Pratyari (Opposition / Tension) 🔴", "Sadhaka (Success / Achievement) 🟢", "Vadha (Risk / Danger) 🔴", "Mitra (Friend) 🟢", "Ati-Mitra (Best Friend) 🟢🟢"],
    "hi": ["जन्म (शरीर / स्वयं) ⚪", "सम्पत् (धन / प्रगति) 🟢", "विपत (बाधा / विलंब) 🔴", "क्षेम (कल्याण / सुख) 🟢", "प्रत्यरि (विरोध / तनाव) 🔴", "साधक (सफलता / सिद्धि) 🟢", "वध (जोखिम / संकट) 🔴", "मित्र (मित्र) 🟢", "अति-मित्र (परम मित्र) 🟢🟢"],
    "mr": ["जन्म (शरीर / स्वतः) ⚪", "संपत् (संपत्ती / प्रगती) 🟢", "विपत् (अडथळे / विलंब) 🔴", "क्षेम (कल्याण / सुख) 🟢", "प्रत्यरि (विरोध / ताण) 🔴", "साधक (यश / सिद्धी) 🟢", "वध (धोका / संकट) 🔴", "मित्र (मित्र) 🟢", "अति-मित्र (परम मित्र) 🟢🟢"],
    "gu": ["જન્મ (શરીર / સ્વયં) ⚪", "સંપત્ (ધન / પ્રગતિ) 🟢", "વિપત્ (અડચણ / વિલંબ) 🔴", "ક્ષેમ (કલ્યાણ / સુખ) 🟢", "પ્રત્યરિ (વિરોધ / તણાવ) 🔴", "સાધક (સફળતા / સિદ્ધિ) 🟢", "વધ (જોખમ / સંકટ) 🔴", "મિત્ર (મિત્ર) 🟢", "અતિ-મિત્ર (પરમ મિત્ર) 🟢🟢"]
}

num_lords_map = {
    "en": {1: "Sun (Surya)", 2: "Moon (Chandra)", 3: "Jupiter (Guru)", 4: "Rahu", 5: "Mercury (Budh)", 6: "Venus (Shukra)", 7: "Ketu", 8: "Saturn (Shani)", 9: "Mars (Mangal)"},
    "hi": {1: "सूर्य", 2: "चंद्र", 3: "गुरु", 4: "राहु", 5: "बुध", 6: "शुक्र", 7: "केतु", 8: "शनि", 9: "मंगल"},
    "mr": {1: "सूर्य", 2: "चंद्र", 3: "गुरु", 4: "राहु", 5: "बुध", 6: "शुक्र", 7: "केतु", 8: "शनि", 9: "मंगळ"},
    "gu": {1: "સૂર્ય", 2: "ચંદ્ર", 3: "ગુરુ", 4: "રાહુ", 5: "બુધ", 6: "શુક્ર", 7: "કેતુ", 8: "શનિ", 9: "મંગળ"}
}

lucky_numbers_map = {
    1: "1, 2, 3, 9", 2: "1, 2, 5", 3: "1, 2, 3, 9", 4: "1, 4, 5, 6, 7",
    5: "1, 5, 6", 6: "1, 5, 6, 7", 7: "1, 4, 7", 8: "3, 5, 6, 8", 9: "1, 2, 3, 9"
}

personal_day_meanings = {
    "en": {
        1: "Good day to launch new goals, lead projects, and pitch ideas. Avoid hesitating or relying on others.",
        2: "Good day for teamwork, smooth negotiations, and active listening. Avoid emotional impulse buying or arguments.",
        3: "Good day for meetings, creative tasks, and social networking. Avoid overpromising or heavy overindulgence.",
        4: "Good day to organize, complete routine audits, and clean your workspace. Avoid taking shortcuts or making speculative bets.",
        5: "Good day for fast networking, sales pitches, and quick decisions. Avoid being rigid or losing focus.",
        6: "Good day for family discussions, relationship bonding, and self-care. Avoid unnecessary arguments or neglecting home ties.",
        7: "Good day for quiet study, deep research, and mental rest. Avoid launching major public changes or making hasty big decisions.",
        8: "Good day for financial planning, debt management, and structured work. Avoid being overly stern or rushing big tasks.",
        9: "Good day to finish pending backlogs, clear clutter, and forgive old grievances. Avoid launching brand-new long-term commitments."
    },
    "hi": {
        1: "लक्ष्य शुरू करने, नेतृत्व करने और विचार प्रस्तुत करने के लिए अच्छा दिन। संकोच से बचें।",
        2: "टीम कार्य, कूटनीति और सक्रिय सुनने के लिए अच्छा दिन। भावनात्मक खरीदारी से बचें।",
        3: "बैठकों, रचनात्मक कार्यों और नेटवर्किंग के लिए अच्छा दिन। वादों में अतिरंजना से बचें।",
        4: "संगठित होने, ऑडिट पूरा करने और कार्यक्षेत्र व्यवस्थित करने के लिए अच्छा दिन। शॉर्टकट से बचें।",
        5: "त्वरित नेटवर्किंग, बिक्री और निर्णयों के लिए अच्छा दिन। कठोरता से बचें।",
        6: "पारिवारिक चर्चा, संबंधों और आत्म-देखभाल के लिए अच्छा दिन। अनावश्यक विवादों से बचें।",
        7: "शांत अध्ययन, गहन शोध और मानसिक विश्राम के लिए अच्छा दिन। जल्दबाजी के निर्णयों से बचें।",
        8: "वित्तीय योजना, ऋण प्रबंधन और संरचित कार्य के लिए अच्छा दिन। अति कठोरता से बचें।",
        9: "अधूरे कार्यों को पूरा करने, अव्यवस्था दूर करने और माफ करने के लिए अच्छा दिन। नई शुरुआत से बचें।"
    },
    "mr": {
        1: "नवीन ध्येये सुरू करण्यासाठी आणि नेतृत्व करण्यासाठी उत्तम दिवस. संकोच टाळा.",
        2: "संघकार्य, मुत्सद्देगिरी आणि ऐकून घेण्यासाठी चांगला दिवस. भावनिक खरेदी टाळा.",
        3: "बैठका, सर्जनशील कामे आणि नेटवर्किंगसाठी उत्तम दिवस. अति-वचनांपासून दूर राहा.",
        4: "कामकाज व्यवस्थित करण्यासाठी आणि ऑडिट पूर्ण करण्यासाठी योग्य दिवस. शॉर्टकट टाळा.",
        5: "जलद निर्णय, विक्री आणि नेटवर्किंगसाठी उत्तम दिवस. आग्रही असणे टाळा.",
        6: "कौटुंबिक चर्चा, नातेसंबंध आणि स्वतःची काळजी घेण्यासाठी चांगला दिवस. वाद टाळा.",
        7: "शांत अभ्यास, सखोल संशोधन आणि मानसिक विश्रांतीसाठी उत्तम दिवस. घाईघाईने निर्णय टाळा.",
        8: "आर्थिक नियोजन, कर्ज व्यवस्थापन आणि शिस्तबद्ध कामासाठी उत्तम दिवस.",
        9: "प्रलंबित कामे पूर्ण करण्यासाठी आणि जुने मतभेद सोडवण्यासाठी उत्तम दिवस."
    },
    "gu": {
        1: "નવા લક્ષ્યો શરૂ કરવા અને નેતૃત્વ કરવા માટે ઉત્તમ દિવસ. અચકાશો નહીં.",
        2: "ટીમ વર્ક, મુત્સદ્દીગીરી અને સાંભળવા માટે સારો દિવસ. ભાવનાત્મક ખરીદી ટાળો.",
        3: "મીટિંગ્સ, સર્જનાત્મક કાર્યો અને નેટવર્કિંગ માટે ઉત્તમ દિવસ. અતિશયોક્તિ ટાળો.",
        4: "કામ વ્યવસ્થિત કરવા અને ઓડિટ પૂર્ણ કરવા માટે સારો દિવસ. શોર્ટકટ ટાળો.",
        5: "ઝડપી નિર્ણયો, વેચાણ અને નેટવર્કિંગ માટે ઉત્તમ દિવસ. જિદ્દી બનવાનું ટાળો.",
        6: "પારિવારિક ચર્ચા, સંબંધો અને સ્વ-સંભાળ માટે સારો દિવસ. બિનજરૂરી વિવાદ ટાળો.",
        7: "શાંત અભ્યાસ, ઊંડા સંશોધન અને માનસિક આરામ માટે ઉત્તમ દિવસ. ઉતાવળા નિર્ણયો ટાળો.",
        8: "નાણાકીય આયોજન, દેવા સંચાલન आणि શિસ્તબદ્ધ કામ માટે ઉત્તમ દિવસ.",
        9: "અધૂરા કામો પૂર્ણ કરવા અને જૂના ભેદભાવ ભૂલી જવા માટે ઉત્તમ દિવસ."
    }
}

vahan_map = {
    "en": {
        1: {"name": "Ghoda (Horse) 🐴", "symbolism": "Speed & Rapid Progress", "H": "High physical stamina; guard against overexertion.", "C": "Swift career expansion and quick victory over competitors.", "F": "Fast fluid liquidity and profitable deal momentum.", "M": "Energetic, brave, and proactive mindset.", "R": "Dynamic communication; avoid rushing partner decisions.", "Remedy": "🏇 Shani Vahan Remedy: Feed soaked black chana (chickpeas) to horses or workers on Saturdays."},
        2: {"name": "Gadha (Donkey) 🫏", "symbolism": "Heavy Labor & Patience", "H": "Physical tiredness or joint strain; ensure adequate rest.", "C": "Heavy workload requiring patience; steady effort yields results.", "F": "Strict budgeting required; focus on routine earnings.", "M": "Resilient stamina against stress.", "R": "Practice gentle listening to prevent domestic friction.", "Remedy": "🫏 Shani Vahan Remedy: Serve aged workers or donate footwear to the underprivileged."},
        3: {"name": "Siyar (Jackal) 🦊", "symbolism": "Caution & High Vigilance", "H": "Nervous fatigue; stay hydrated and composed.", "C": "Beware of misleading advice; double-check all documents.", "F": "High risk of financial scams; avoid unverified schemes.", "M": "Alert, observant, but guard against overthinking.", "R": "Be direct and transparent in speech.", "Remedy": "🦊 Shani Vahan Remedy: Feed stray animals or birds with chapati/bread on Saturday evenings."},
        4: {"name": "Hathi (Elephant) 🐘", "symbolism": "Royalty & Financial Gains", "H": "Robust health, dignified energy, and physical stability.", "C": "Recognition from authority, promotions, and elevated prestige.", "F": "Financial windfalls, luxury acquisitions, and asset stability.", "M": "Dignified, generous, confident, and peaceful.", "R": "Generous presence in family and social ties.", "Remedy": "🐘 Shani Vahan Remedy: Respect mentors/teachers and offer mustard oil or sesame seeds in charity."},
        5: {"name": "Bail (Bull) 🐂", "symbolism": "Steady Persistence & Growth", "H": "Solid stamina; maintain neck and joint flexibility.", "C": "Methodical progress in core tasks; ideal for groundwork.", "F": "Steady accumulation through real estate or long-term assets.", "M": "Grounded, persistent, patient, and focused.", "R": "Dependable, committed, and stable bonding.", "Remedy": "🐂 Shani Vahan Remedy: Feed green fodder or jaggery to black bulls or cows on Saturdays."},
        6: {"name": "Sher (Lion) 🦁", "symbolism": "Power & Leadership Courage", "H": "Strong confidence; keep cardiovascular stress low.", "C": "Commanding leadership authority; triumph in challenges.", "F": "Strong capital protection and negotiation leverage.", "M": "Bold, fearless, authoritative, and decisive.", "R": "Protect loved ones warmly; guard against dominating tone.", "Remedy": "🦁 Shani Vahan Remedy: Recite Hanuman Chalisa or offer red flowers to Lord Hanuman or Lord Shiva."},
        7: {"name": "Kowwa (Crow) 🐦‍⬛", "symbolism": "Restlessness & Scattered Focus", "H": "Restless nerves or light sleep; practice calming breathwork.", "C": "Frequent travel, scattered attention, or unexpected delays.", "F": "Flustered small expenses; avoid impulsive online purchases.", "M": "Anxious mindset; practice silence (Mouna) and meditation.", "R": "Avoid impatient retorts or arguments with close family.", "Remedy": "🐦‍⬛ Shani Vahan Remedy: Feed crows or stray birds with grains or bread every morning."},
        8: {"name": "Mayur (Peacock) 🦚", "symbolism": "Joy & Creative Breakthroughs", "H": "Vibrant vitality, aesthetic radiance, and emotional warmth.", "C": "Creative breakthroughs, social applause, and team harmony.", "F": "Heartwarming financial gains and pleasant surprises.", "M": "Joyous, optimistic, creative, and socially uplifted.", "R": "Romantic warmth, heartwarming family news, and social joy.", "Remedy": "🦚 Shani Vahan Remedy: Keep a peacock feather at your desk or chant 'Om Sham Shanayscharaya Namah'."},
        9: {"name": "Hans (Swan) 🦢", "symbolism": "Supreme Wisdom & Peace", "H": "Peaceful vitality, mental composure, and holistic health.", "C": "Wise decision-making, excellent judgment, and peer respect.", "F": "Strong financial security, debt clearance, and prudent investments.", "M": "Deep spiritual clarity, tranquil, and intuitive.", "R": "Pure, soul-nourishing harmony and mutual respect.", "Remedy": "🦢 Shani Vahan Remedy: Practice quiet meditation; offer milk or fresh water to birds or Lord Shiva."}
    }
}
vahan_map["hi"] = vahan_map["en"]
vahan_map["mr"] = vahan_map["en"]
vahan_map["gu"] = vahan_map["en"]

translations = {
    "en": {
        "intro_title": "Unlocking the Wisdom of Vedic Astrology",
        "intro_desc": "In Vedic astrology and numerology, the Moon's transit through the 27 Nakshatras and daily numerical vibrations create a unique energy pattern relative to your birth profile. This app provides accurate, astronomical, and numerological insights into your health, career, finance, mindset, and relationships.",
        "profile_title": "👤 Birth Profile",
        "horoscope_title": "7-Day Horoscope Prediction & Life Guidance",
        "search_prompt": "🌍 Birth Place Name or 6-Digit Pincode",
        "generate_btn": "Save Profile & Generate Predictions",
        "expander_title": "✨ Click here to see the Prediction & Life Guidance ✨",
        "name_label": "Name", "dob_label": "Date of Birth", "tob_label": "Time of Birth (24-Hour)",
        "birth_place_label": "Birth Place",
        "mobile_banner_title": "📱 Save & Install for 1-Click Mobile Access",
        "mobile_banner_desc": "Your birth profile details have been saved to this custom URL. To open this horoscope anytime without re-entering details:",
        "mobile_banner_ios": "iPhone (Safari): Tap the Share icon ➔ select 'Add to Home Screen'.",
        "mobile_banner_android": "Android (Chrome): Tap the three dots (⋮) ➔ select 'Add to Home screen' or 'Install App'.",
        "navtara_head": "🌙 Navtara Transit:", "num_head": "🔢 Numerology Vibration:", "vahan_head": "🪐 Shani Vahan:",
        "health_head": "🩺 Health:", "career_head": "💼 Career:", "finance_head": "💰 Finance:", "mindset_head": "🧘 Mindset:", "rel_head": "❤️ Relationships:",
        "share_title": "🔗 Share Navtara Pulse",
        "warning_name": "⚠️ Name is required", "warning_dob": "⚠️ Date of Birth is required",
        "warning_hh": "⚠️ Hour (HH) is required", "warning_mm": "⚠️ Minute (MM) is required",
        "warning_place": "⚠️ Birth Place or 6-digit Pincode is required"
    },
    "hi": {
        "intro_title": "वैदिक ज्योतिष और अंकशास्त्र का ज्ञान",
        "intro_desc": "वैदिक ज्योतिष और अंकशास्त्र में, 27 नक्षत्रों में चंद्रमा का गोचर और दैनिक अंक कंपन आपके जन्म विवरण के सापेक्ष एक अनूठा ऊर्जा पैटर्न बनाते हैं। यह ऐप स्वास्थ्य, करियर, वित्त, मानसिकता और संबंधों में सटीक अंतर्दृष्टि प्रदान करता है।",
        "profile_title": "👤 जन्म विवरण",
        "horoscope_title": "7-दिवसीय राशिफल भविष्यवाणी और जीवन मार्गदर्शन",
        "search_prompt": "🌍 जन्म स्थान का नाम या 6-अंकीय पिनकोड",
        "generate_btn": "प्रोफाइल सहेजें और भविष्यवाणियां उत्पन्न करें",
        "expander_title": "✨ दैनिक भविष्यवाणी और जीवन मार्गदर्शन देखने के लिए यहां क्लिक करें ✨",
        "name_label": "नाम", "dob_label": "जन्म तिथि", "tob_label": "जन्म समय (24-घंटे)",
        "birth_place_label": "जन्म स्थान",
        "mobile_banner_title": "📱 1-क्लिक मोबाइल एक्सेस के लिए सहेजें और इंस्टॉल करें",
        "mobile_banner_desc": "आपके जन्म विवरण इस URL में सहेजे गए हैं। बिना दोबारा विवरण भरे कभी भी देखने के लिए:",
        "mobile_banner_ios": "iPhone (Safari): शेयर (Share) आइकन ➔ 'Add to Home Screen' चुनें।",
        "mobile_banner_android": "Android (Chrome): तीन बिंदु (⋮) ➔ 'Add to Home screen' या 'Install App' चुनें।",
        "navtara_head": "🌙 नवतारा गोचर:", "num_head": "🔢 अंकशास्त्र कंपन:", "vahan_head": "🪐 शनि वाहन:",
        "health_head": "🩺 स्वास्थ्य:", "career_head": "💼 करियर:", "finance_head": "💰 वित्त:", "mindset_head": "🧘 मानसिकता:", "rel_head": "❤️ संबंध:",
        "share_title": "🔗 नवतारा पल्स शेयर करें",
        "warning_name": "⚠️ नाम आवश्यक है", "warning_dob": "⚠️ जन्म तिथि आवश्यक है",
        "warning_hh": "⚠️ घंटा (HH) आवश्यक है", "warning_mm": "⚠️ मिनट (MM) आवश्यक है",
        "warning_place": "⚠️ जन्म स्थान या 6-अंकीय पिनकोड आवश्यक है"
    },
    "mr": {
        "intro_title": "वैदिक ज्योतिष आणि अंकशास्त्राचे ज्ञान",
        "intro_desc": "वैदिक ज्योतिष आणि अंकशास्त्रामध्ये, २७ नक्षत्रांमधील चंद्राचे भ्रमण आणि दैनंदिन अंक तुमच्या जन्म तपशिलाच्या संदर्भात ऊर्जा निर्माण करतात. हे ॲप आरोग्य, करिअर, वित्त, मानसिकता आणि नातेसंबंधांबद्दल अचूक मार्गदर्शन प्रदान करते.",
        "profile_title": "👤 जन्म तपशील",
        "horoscope_title": "७-दिवसीय राशीभविष्य आणि जीवन मार्गदर्शन",
        "search_prompt": "🌍 जन्मस्थानाचे नाव किंवा ६-अंकी पिनकोड",
        "generate_btn": "प्रोफाइल सेव्ह करा आणि भविष्यानुमान जनरेट करा",
        "expander_title": "✨ दैनिक राशीभविष्य आणि जीवन मार्गदर्शन पाहण्यासाठी येथे क्लिक करा ✨",
        "name_label": "नाव", "dob_label": "जन्म तारीख", "tob_label": "जन्म वेळ (२४-तास)",
        "birth_place_label": "जन्म स्थान",
        "mobile_banner_title": "📱 १-क्लिक मोबाईल प्रवेशासाठी सेव्ह करा आणि इंस्टॉल करा",
        "mobile_banner_desc": "तुमचे जन्म तपशील या URL मध्ये सेव्ह केले आहेत. पुन्हा न भरता पाहण्यासाठी:",
        "mobile_banner_ios": "iPhone (Safari): शेअर (Share) ➔ 'Add to Home Screen' निवडा.",
        "mobile_banner_android": "Android (Chrome): तीन ठिपके (⋮) ➔ 'Add to Home screen' किंवा 'Install App' निवडा.",
        "navtara_head": "🌙 नवतारा गोचर:", "num_head": "🔢 अंकशास्त्र कंपन:", "vahan_head": "🪐 शनि वाहन:",
        "health_head": "🩺 आरोग्य:", "career_head": "💼 करिअर:", "finance_head": "💰 वित्त:", "mindset_head": "🧘 मानसिकता:", "rel_head": "❤️ संबंध:",
        "share_title": "🔗 नवतारा पल्स शेअर करा",
        "warning_name": "⚠️ नाव आवश्यक आहे", "warning_dob": "⚠️ जन्म तारीख आवश्यक आहे",
        "warning_hh": "⚠️ तास (HH) आवश्यक आहे", "warning_mm": "⚠️ मिनिट (MM) आवश्यक आहे",
        "warning_place": "⚠️ जन्मस्थान किंवा ६-अंकी पिनकोड आवश्यक आहे"
    },
    "gu": {
        "intro_title": "વૈદિક જ્યોતિષ અને અંકશાસ્ત્રનું જ્ઞાન",
        "intro_desc": "વૈદિક જ્યોતિષ અને અંકશાસ્ત્રમાં, ૨૭ નક્ષત્રોમાં ચંદ્રનું ભ્રમણ અને દૈનિક અંક કંપન તમારી જન્મ વિગતો અનુસાર અનન્ય ઊર્જા કંપન બનાવે છે. આ એપ આરોગ્ય, કારકિર્દી, નાણાં, માનસિકતા અને સંબંધોમાં સચોટ માર્ગદર્શન પૂરું પાડે છે.",
        "profile_title": "👤 જન્મ વિગતો",
        "horoscope_title": "૭-દિવસીય રાશીફળ અને જીવન માર્ગદર્શન",
        "search_prompt": "🌍 જન્મ સ્થાનનું નામ અથવા ૬-અંકનો પિનકોડ",
        "generate_btn": "પ્રોફાઇલ સાચવો અને આગાહીઓ જનરેટ કરો",
        "expander_title": "✨ દૈનિક રાશીફળ અને જીવન માર્ગદર્શન જોવા માટે અહીં ક્લિક કરો ✨",
        "name_label": "નામ", "dob_label": "જન્મ તારીખ", "tob_label": "જન્મ સમય (૨૪-કલાક)",
        "birth_place_label": "જન્મ સ્થાન",
        "mobile_banner_title": "📱 ૧-ક્લિક મોબાઇલ ઍક્સેસ માટે સાચવો અને ઇન્સ્ટોલ કરો",
        "mobile_banner_desc": "તમારી જન્મ વિગતો આ URL માં સાચવેલ છે. ફરીથી દાખલ કર્યા વગર જોવા માટે:",
        "mobile_banner_ios": "iPhone (Safari): શેર (Share) ➔ 'Add to Home Screen' પસંદ કરો.",
        "mobile_banner_android": "Android (Chrome): ત્રણ ટપકાં (⋮) ➔ 'Add to Home screen' અથવા 'Install App' પસંદ કરો.",
        "navtara_head": "🌙 નવતારા ગોચર:", "num_head": "🔢 અંકશાસ્ત્ર કંપન:", "vahan_head": "🪐 શનિ વાહન:",
        "health_head": "🩺 આરોગ્ય:", "career_head": "💼 કારકિર્દી:", "finance_head": "💰 નાણાં:", "mindset_head": "🧘 માનસિકતા:", "rel_head": "❤️ સંબંધો:",
        "share_title": "🔗 નવતારા પલ્સ શેર કરો",
        "warning_name": "⚠️ નામ જરૂરી છે", "warning_dob": "⚠️ જન્મ તારીખ જરૂરી છે",
        "warning_hh": "⚠️ કલાક (HH) જરૂરી છે", "warning_mm": "⚠️ મિનિટ (MM) જરૂરી છે",
        "warning_place": "⚠️ જન્મ સ્થાન અથવા ૬-અંકનો પિનકોડ જરૂરી છે"
    }
}

# ==========================================
# 3. HELPER & ASTRONOMY FUNCTIONS
# ==========================================
def reduce_to_single_digit(n: int) -> int:
    """Reduce any number to a single digit 1-9."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

@st.cache_data(show_spinner=False)
def search_places_online(query):
    """Fetch geocoding data from OpenStreetMap Nominatim API."""
    if len(query) < 3:
        return []
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=5"
    headers = {'User-Agent': 'NavtaraPulse/1.0'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

def get_utc_offset_hours(place_obj, place_query):
    """Automatically determine UTC offset in hours based on place data."""
    if isinstance(place_obj, dict):
        addr = place_obj.get('address', {})
        country_code = addr.get('country_code', '').lower()
        if country_code == 'in':
            return 5.5
        lon = float(place_obj.get('lon', 0))
        if lon != 0:
            return round(lon / 15.0 * 2) / 2
    return 5.5

def get_moon_and_kundli_indices(dt_utc, place_obj=None):
    """Calculates exact Sidereal Moon Nakshatra, Rashi, and Lagna indices using PyEphem + Lahiri Ayanamsa."""
    observer = ephem.Observer()
    observer.date = ephem.date(dt_utc)
    
    if isinstance(place_obj, dict):
        lat = float(place_obj.get('lat', 0))
        lon = float(place_obj.get('lon', 0))
        if lat != 0 or lon != 0:
            observer.lat = str(lat)
            observer.lon = str(lon)
            
    moon = ephem.Moon(observer)
    ecl = ephem.Ecliptic(moon)
    
    year = dt_utc.year + (dt_utc.month - 1) / 12.0
    ayanamsa = 23.85306 + (year - 2000.0) * 0.01397
    
    sidereal_moon_lon = (math.degrees(ecl.lon) - ayanamsa) % 360
    nakshatra_index = int(sidereal_moon_lon / 13.333333333333334) % 27
    rashi_index = int(sidereal_moon_lon / 30.0) % 12
    
    try:
        lst_deg = math.degrees(observer.sidereal_time())
        lat_rad = math.radians(float(observer.lat))
        eps = math.radians(23.439)
        lst_rad = math.radians(lst_deg)
        
        num = math.cos(lst_rad)
        den = -math.sin(lst_rad) * math.cos(eps) - math.tan(lat_rad) * math.sin(eps)
        asc_deg = math.degrees(math.atan2(num, den)) % 360
        sidereal_lagna_lon = (asc_deg - ayanamsa) % 360
        lagna_index = int(sidereal_lagna_lon / 30.0) % 12
    except:
        lagna_index = (rashi_index + 2) % 12
        
    return nakshatra_index, rashi_index, lagna_index

def calculate_7_day_transits(now_utc, utc_offset_hours, days=7):
    """
    Computes current and future transits anchored strictly to UTC time.
    Discards any past transit whose end time is before current local time.
    """
    now_local = now_utc + datetime.timedelta(hours=utc_offset_hours)
    current_nak, _, _ = get_moon_and_kundli_indices(now_utc)
    
    start_search_utc = now_utc
    for i in range(1, 200):
        test_utc = now_utc - datetime.timedelta(minutes=15 * i)
        test_nak, _, _ = get_moon_and_kundli_indices(test_utc)
        if test_nak != current_nak:
            start_search_utc = test_utc + datetime.timedelta(minutes=15)
            break
            
    window_start_local = start_search_utc + datetime.timedelta(hours=utc_offset_hours)
    
    transits = []
    curr_nak = current_nak
    scan_limit_utc = now_utc + datetime.timedelta(days=days)
    
    total_steps = int((days + 3) * 24 * 4)
    for i in range(1, total_steps):
        test_utc = start_search_utc + datetime.timedelta(minutes=15 * i)
        test_nak, _, _ = get_moon_and_kundli_indices(test_utc)
        
        if test_nak != curr_nak:
            test_local = test_utc + datetime.timedelta(hours=utc_offset_hours)
            
            if test_local > now_local:
                transits.append({
                    "start": window_start_local,
                    "end": test_local,
                    "nak_index": curr_nak,
                    "is_current": (window_start_local <= now_local < test_local)
                })
            curr_nak = test_nak
            window_start_local = test_local
            
            if test_utc >= scan_limit_utc:
                break
                
    return transits

# ==========================================
# 4. MAIN APP LAYOUT & URL PARAMETERS
# ==========================================
query_params = st.query_params

if 'profile_generated' not in st.session_state:
    st.session_state['profile_generated'] = (query_params.get('saved') == 'true')

st.title("🌙 Navtara Pulse")

# Purple Highlighted Language Selector
lang_options = {"en": "English", "hi": "हिन्दी (Hindi)", "mr": "मराठी (Marathi)", "gu": "ગુજરાતી (Gujarati)"}
selected_lang_name = st.selectbox("🌐 Select Language", list(lang_options.values()), index=0)
lang_code = [k for k, v in lang_options.items() if v == selected_lang_name][0]
t = translations[lang_code]

st.markdown(f"### {t['intro_title']}")
st.write(t['intro_desc'])
st.divider()

# ==========================================
# 5. UNIFIED USER PROFILE INPUT WINDOW
# ==========================================
st.header(t['profile_title'])

default_name = query_params.get('n', '')
default_date_str = query_params.get('d', '')
if default_date_str:
    try:
        default_date = datetime.datetime.strptime(default_date_str, '%Y-%m-%d').date()
    except:
        default_date = None
else:
    default_date = None

hh_param = query_params.get('h')
hh_index = int(hh_param) + 1 if (hh_param is not None and hh_param.isdigit() and int(hh_param) < 24) else 0

mm_param = query_params.get('m')
mm_index = int(mm_param) + 1 if (mm_param is not None and mm_param.isdigit() and int(mm_param) < 60) else 0

default_place = query_params.get('p', '')

col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input(t['name_label'], value=default_name, placeholder="e.g. Rahul Sharma")
    is_name_valid = bool(user_name.strip())
    if not is_name_valid:
        st.markdown(f'<span class="missing-field-warning">{t["warning_name"]}</span>', unsafe_allow_html=True)

    birth_date = st.date_input(t['dob_label'], min_value=datetime.date(1925, 1, 1), max_value=datetime.date.today(), value=default_date)
    is_dob_valid = birth_date is not None
    if not is_dob_valid:
        st.markdown(f'<span class="missing-field-warning">{t["warning_dob"]}</span>', unsafe_allow_html=True)

with col2:
    st.write(t['tob_label'])
    tc1, tc2 = st.columns(2)
    hh_options = ["--"] + [f"{i:02d}" for i in range(24)]
    mm_options = ["--"] + [f"{i:02d}" for i in range(60)]

    with tc1: 
        birth_hour = st.selectbox("HH", hh_options, index=hh_index)
        is_hh_valid = birth_hour != "--"
        if not is_hh_valid:
            st.markdown(f'<span class="missing-field-warning">{t["warning_hh"]}</span>', unsafe_allow_html=True)

    with tc2: 
        birth_minute = st.selectbox("MM", mm_options, index=mm_index)
        is_mm_valid = birth_minute != "--"
        if not is_mm_valid:
            st.markdown(f'<span class="missing-field-warning">{t["warning_mm"]}</span>', unsafe_allow_html=True)

# Unified Single Birth Place Search Box
st.write(t['search_prompt'])
place_query = st.text_input(
    "Search Location", 
    value=default_place, 
    placeholder="e.g. Ujjain, Mumbai, London, or 456001",
    label_visibility="collapsed"
)

is_place_valid = len(place_query.strip()) >= 3
if not is_place_valid:
    st.markdown(f'<span class="missing-field-warning">{t["warning_place"]}</span>', unsafe_allow_html=True)

selected_place_display = place_query
place_obj_data = None

if len(place_query) >= 3:
    places_list = search_places_online(place_query)
    if places_list:
        display_names = [p['display_name'] for p in places_list]
        selected_idx = st.selectbox("Select verified matching location from web:", range(len(display_names)), format_func=lambda x: display_names[x])
        selected_place_display = display_names[selected_idx]
        place_obj_data = places_list[selected_idx]

# Auto-calculate UTC offset in background
utc_offset_val = get_utc_offset_hours(place_obj_data, place_query)

# Auto-calculate fixed Kundali Parameters based on Date/Time/Location
if is_dob_valid and is_hh_valid and is_mm_valid:
    birth_local_dt = datetime.datetime.combine(birth_date, datetime.time(int(birth_hour), int(birth_minute)))
    birth_utc_dt = birth_local_dt - datetime.timedelta(hours=utc_offset_val)
    auto_janma_idx, auto_rashi_idx, auto_lagna_idx = get_moon_and_kundli_indices(birth_utc_dt, place_obj_data)
else:
    auto_janma_idx, auto_rashi_idx, auto_lagna_idx = 0, 0, 0

# Plain Birth Place Badge
if selected_place_display and is_place_valid:
    st.markdown(f"<div class='verified-badge'>📍 {t['birth_place_label']}: {selected_place_display}</div>", unsafe_allow_html=True)

# Form Validation Check
is_form_valid = is_name_valid and is_dob_valid and is_hh_valid and is_mm_valid and is_place_valid

submit_clicked = st.button(
    f"💾 {t['generate_btn']}", 
    type="primary", 
    use_container_width=True,
    disabled=not is_form_valid
)

if not is_form_valid:
    st.caption("⚠️ Please enter all required birth details highlighted above to enable predictions.")

if submit_clicked:
    st.query_params['n'] = user_name
    st.query_params['d'] = str(birth_date)
    st.query_params['h'] = str(int(birth_hour))
    st.query_params['m'] = str(int(birth_minute))
    st.query_params['p'] = selected_place_display
    st.query_params['saved'] = 'true'
    st.session_state['profile_generated'] = True
    st.toast("✅ Profile saved & horoscope generated!", icon="🎉")

# ==========================================
# 6. CONSOLIDATED PROFILE & HOROSCOPE
# ==========================================
if st.session_state.get('profile_generated') and is_form_valid:
    st.divider()
    
    # 1. Fixed Astrological Kundli Parameters
    janma_nakshatra_name = nakshatra_list[auto_janma_idx]
    janma_lord = nakshatra_lords_map[lang_code][auto_janma_idx]
    janma_rashi_name = rashi_list_map[lang_code][auto_rashi_idx]
    janma_lagna_name = lagna_list_map[lang_code][auto_lagna_idx]
    janma_traits = nakshatra_traits_map.get(janma_nakshatra_name, "Balanced vitality, strong intuition, and steady growth.")
    
    # 2. Vedic Numerology Profile Calculation
    moolank = reduce_to_single_digit(birth_date.day)
    bhagyank = reduce_to_single_digit(birth_date.day + birth_date.month + birth_date.year)
    moolank_lord = num_lords_map[lang_code].get(moolank, "")
    bhagyank_lord = num_lords_map[lang_code].get(bhagyank, "")
    moolank_trait = moolank_traits_map.get(moolank, "Leadership and steady focus.")
    bhagyank_trait = moolank_traits_map.get(bhagyank, "Long-term purpose and natural path.")
    lucky_nums = lucky_numbers_map.get(moolank, "1, 3, 5, 6")
    
    # 3. Shani Paya (Saturn's Feet) Calculation (Saturn in Pisces / Meena Rashi = Index 11)
    saturn_transit_rashi_idx = 11  # Pisces (Meena)
    house_from_saturn = (auto_rashi_idx - saturn_transit_rashi_idx) % 12 + 1
    
    paya_map = {
        2: {"name": "Rajat Paya (Silver Feet / चाँदी का पाया) 🥈", "metal": "Silver", "grade": "Most Auspicious & Protective (अति शुभ)", "desc": "Acts as a divine protective shield. Cushioning transit friction, bringing financial expansion, debt clearance, and steady career growth."},
        5: {"name": "Rajat Paya (Silver Feet / चाँदी का पाया) 🥈", "metal": "Silver", "grade": "Most Auspicious & Protective (अति शुभ)", "desc": "Acts as a divine protective shield. Cushioning transit friction, bringing financial expansion, debt clearance, and steady career growth."},
        9: {"name": "Rajat Paya (Silver Feet / चाँदी का पाया) 🥈", "metal": "Silver", "grade": "Most Auspicious & Protective (अति शुभ)", "desc": "Acts as a divine protective shield. Cushioning transit friction, bringing financial expansion, debt clearance, and steady career growth."},
        3: {"name": "Tamra Paya (Copper Feet / तांबे का पाया) 🥉", "metal": "Copper", "grade": "Favorable & Productive (शुभ एवं फलदायी)", "desc": "Brings rewards for honest hard work, steady business growth, positive support from elders/mentors, and strong physical stamina."},
        7: {"name": "Tamra Paya (Copper Feet / तांबे का पाया) 🥉", "metal": "Copper", "grade": "Favorable & Productive (शुभ एवं फलदायी)", "desc": "Brings rewards for honest hard work, steady business growth, positive support from elders/mentors, and strong physical stamina."},
        10: {"name": "Tamra Paya (Copper Feet / तांबे का पाया) 🥉", "metal": "Copper", "grade": "Favorable & Productive (शुभ एवं फलदायी)", "desc": "Brings rewards for honest hard work, steady business growth, positive support from elders/mentors, and strong physical stamina."},
        1: {"name": "Swarna Paya (Gold Feet / सोने का पाया) 🥇", "metal": "Gold", "grade": "Testing / Mixed Results (मध्यम एवं सचेत)", "desc": "Brings prestige alongside high personal/family expenses and workload. Requires strict budget discipline, humility, and avoiding ego clashes."},
        6: {"name": "Swarna Paya (Gold Feet / सोने का पाया) 🥇", "metal": "Gold", "grade": "Testing / Mixed Results (मध्यम एवं सचेत)", "desc": "Brings prestige alongside high personal/family expenses and workload. Requires strict budget discipline, humility, and avoiding ego clashes."},
        11: {"name": "Swarna Paya (Gold Feet / सोने का पाया) 🥇", "metal": "Gold", "grade": "Testing / Mixed Results (मध्यम एवं सचेत)", "desc": "Brings prestige alongside high personal/family expenses and workload. Requires strict budget discipline, humility, and avoiding ego clashes."},
        4: {"name": "Loha Paya (Iron Feet / लोहे का पाया) 🪙", "metal": "Iron", "grade": "Requires Discipline & Caution (कठिन एवं धैर्य)", "desc": "Brings delays in key projects, physical fatigue or joint strain. Best managed through routine hard work, avoiding speculative bets, and reciting Hanuman Chalisa daily."},
        8: {"name": "Loha Paya (Iron Feet / लोहे का पाया) 🪙", "metal": "Iron", "grade": "Requires Discipline & Caution (कठिन एवं धैर्य)", "desc": "Brings delays in key projects, physical fatigue or joint strain. Best managed through routine hard work, avoiding speculative bets, and reciting Hanuman Chalisa daily."},
        12: {"name": "Loha Paya (Iron Feet / लोहे का पाया) 🪙", "metal": "Iron", "grade": "Requires Discipline & Caution (कठिन एवं धैर्य)", "desc": "Brings delays in key projects, physical fatigue or joint strain. Best managed through routine hard work, avoiding speculative bets, and reciting Hanuman Chalisa daily."}
    }
    active_paya = paya_map.get(house_from_saturn, paya_map[2])
    
    clean_name = user_name.strip()
    profile_display_name = f"{clean_name}'s Profile" if clean_name else "User's Profile"

    # Single Consolidated Light Green Profile Box
    st.markdown(f"""
    <div style="background-color: #f0fdf4; color: #166534; padding: 18px 20px; border-radius: 12px; border: 1.5px solid #86efac; margin-top: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
        <h4 style="color: #15803d; margin-top: 0; margin-bottom: 12px; font-weight: 800; font-size: 1.18rem; display: flex; align-items: center; gap: 8px;">
            🌿 {profile_display_name}
        </h4>
        <div style="font-size: 0.94rem; color: #14532d; line-height: 1.6;">
            <p style="margin-bottom: 6px;">
                ⭐ <b>Janma Nakshatra:</b> {janma_nakshatra_name} &nbsp;|&nbsp; 
                <b>Lord:</b> {janma_lord} &nbsp;|&nbsp; 
                <b>Rashi:</b> {janma_rashi_name} &nbsp;|&nbsp; 
                <b>Lagna:</b> {janma_lagna_name}
            </p>
            <p style="margin-bottom: 12px; padding-left: 10px; border-left: 3.5px solid #22c55e; color: #166534; font-size: 0.91rem;">
                ✨ <b>Traits:</b> {janma_traits}
            </p>
            <hr style="border: 0; border-top: 1px dashed #a7f3d0; margin: 10px 0;">
            <p style="margin-bottom: 6px; margin-top: 10px;">
                🔢 <b>Numerology:</b> Moolank: <b>{moolank} ({moolank_lord})</b> &nbsp;|&nbsp; Bhagyank: <b>{bhagyank} ({bhagyank_lord})</b> &nbsp;|&nbsp; Lucky Numbers: <b>{lucky_nums}</b>
            </p>
            <p style="margin-bottom: 12px; padding-left: 10px; border-left: 3.5px solid #22c55e; color: #166534; font-size: 0.91rem;">
                💡 <b>Traits:</b> Moolank {moolank} brings {moolank_trait} Bhagyank {bhagyank} emphasizes {bhagyank_trait}
            </p>
            <hr style="border: 0; border-top: 1px dashed #a7f3d0; margin: 10px 0;">
            <p style="margin-bottom: 6px; margin-top: 10px;">
                🪐 <b>Shani Paya (Saturn's Feet):</b>
            </p>
            <div style="background-color: #ffffff; padding: 12px 14px; border-radius: 8px; border: 1px solid #bbf7d0; color: #14532d; font-size: 0.9rem; margin-top: 6px;">
                <p style="margin-bottom: 4px;">
                    📌 <b>Transit:</b> Saturn in <b>Meena Rashi (Pisces)</b> &nbsp;|&nbsp; <b>Duration:</b> <span style="background-color: #dcfce7; padding: 2px 8px; border-radius: 6px; font-weight: 700; color: #15803d;">March 2025 – June 2027</span>
                </p>
                <p style="margin-bottom: 4px;">
                    🦵 <b>Active Paya:</b> <b>{active_paya['name']}</b>
                </p>
                <p style="margin-bottom: 0px; color: #166534; padding-left: 8px; border-left: 3px solid #16a34a; margin-top: 6px;">
                    🔮 <b>Impact:</b> <b>[{active_paya['grade']}]</b> {active_paya['desc']}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Save & Install Mobile Instructions Banner
    st.markdown(f"""
    <div style="background-color: #1e1b4b; color: #ffffff; padding: 16px; border-radius: 12px; margin-top: 10px; margin-bottom: 20px;">
        <h5 style="color: #fbbf24; margin-top: 0; font-size: 1.05rem; font-weight: bold;">{t['mobile_banner_title']}</h5>
        <p style="font-size: 0.9rem; color: #e2e8f0; margin-bottom: 8px;">
            {t['mobile_banner_desc']}
        </p>
        <ul style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 0; padding-left: 20px;">
            <li>{t['mobile_banner_ios']}</li>
            <li>{t['mobile_banner_android']}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.header(t['horoscope_title'])
    
    now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    transits = calculate_7_day_transits(now_utc, utc_offset_val)
    
    for transit in transits:
        nak_difference = (transit["nak_index"] - auto_janma_idx) % 27
        tara_index = nak_difference % 9
        
        tara_data = t["tara"][tara_index]
        tara_badge_name = navtara_names_map[lang_code][tara_index]
        transit_nak_name = nakshatra_list[transit["nak_index"]]
        transit_nak_lord = nakshatra_lords_map[lang_code][transit["nak_index"]]
        
        start_str = transit["start"].strftime('%a, %d %b %I:%M %p')
        end_str = transit["end"].strftime('%a, %d %b %I:%M %p')
        
        current_pill = f"<span class='current-badge'>{t['active_now']}</span>" if transit.get("is_current") else ""
        
        # Calculate Daily Personal Day Number for the transit date
        t_date = transit["start"].date()
        p_day = reduce_to_single_digit(birth_date.day + birth_date.month + t_date.day + t_date.month + t_date.year)
        p_lord = num_lords_map[lang_code].get(p_day, "")
        p_desc = personal_day_meanings[lang_code].get(p_day, "")
        num_aspects = personal_day_aspects_en.get(p_day, {})
        
        # Calculate Daily Shani Vahan
        janma_nak_num = auto_janma_idx + 1
        transit_nak_num = transit["nak_index"] + 1
        vahan_rem = ((janma_nak_num * 4) + transit_nak_num) % 9
        if vahan_rem == 0: vahan_rem = 9
        vahan_info = vahan_map[lang_code].get(vahan_rem, vahan_map[lang_code][9])
        
        # Upper Portion: Day Card with 3 Explicit Headings
        st.markdown(f"""
        <div class="transit-card">
            <h5><span>🕒 {start_str} ➔ {end_str}</span> {current_pill}</h5>
            <p><b>{t['navtara_head']}</b> Status: <span class='status-badge'>{tara_badge_name}</span> | <b>Moon Nakshatra:</b> {transit_nak_name} (<b>Lord:</b> {transit_nak_lord})</p>
            <p style="margin-top: 6px; padding-top: 6px; border-top: 1px dashed #bae6fd;">
                <b>{t['num_head']}</b> Personal Day <b>{p_day} ({p_lord})</b> — {p_desc}
            </p>
            <p style="margin-top: 6px; padding-top: 6px; border-top: 1px dashed #bae6fd;">
                <b>{t['vahan_head']}</b> <b>{vahan_info['name']}</b> — <i>{vahan_info['symbolism']}</i>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Attached Lower Portion: Yellow Glittering Expander Bar
        with st.expander(t["expander_title"]):
            st.write(f"{t['health_head']} {tara_data['H']} *(Numerology: {num_aspects.get('H', '')})* *(Shani Vahan: {vahan_info['H']})*")
            st.write(f"{t['career_head']} {tara_data['C']} *(Numerology: {num_aspects.get('C', '')})* *(Shani Vahan: {vahan_info['C']})*")
            st.write(f"{t['finance_head']} {tara_data['F']} *(Numerology: {num_aspects.get('F', '')})* *(Shani Vahan: {vahan_info['F']})*")
            st.write(f"{t['mindset_head']} {tara_data['M']} *(Numerology: {num_aspects.get('M', '')})* *(Shani Vahan: {vahan_info['M']})*")
            st.write(f"{t['rel_head']} {tara_data.get('Rel', '')} *(Numerology: {num_aspects.get('R', '')})* *(Shani Vahan: {vahan_info['R']})*")
            
            # Show Navtara, Numerology, and Shani Vahan Remedies
            if tara_data['R']:
                st.error(tara_data['R'])
            if num_aspects.get("Remedy", ""):
                st.info(num_aspects["Remedy"])
            if vahan_info.get("Remedy", ""):
                st.warning(vahan_info["Remedy"])

# ==========================================
# 7. SHARE APP (Direct Link Payload)
# ==========================================
st.divider()
st.subheader(t['share_title'])
app_url = "https://navtara-pulse.streamlit.app"
share_text = urllib.parse.quote(f"Check out Navtara Pulse - Precision Moon Transit: {app_url}")

sc1, sc2, sc3 = st.columns(3)
with sc1: 
    st.link_button("💬 WhatsApp", f"https://api.whatsapp.com/send?text={share_text}", use_container_width=True)
with sc2: 
    st.link_button("✉️ Email", f"mailto:?subject=Navtara Pulse&body={share_text}", use_container_width=True)
with sc3: 
    st.link_button("✈️ Telegram", f"https://t.me/share/url?url={app_url}&text=Check out Navtara Pulse", use_container_width=True)
