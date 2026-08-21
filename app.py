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

    /* Dasha Card Styling */
    .dasha-card {
        background-color: #fefce8;
        color: #1e1b4b;
        padding: 18px;
        border-radius: 12px 12px 0 0;
        border-left: 6px solid #d97706;
        border-top: 1px solid #fef08a;
        border-right: 1px solid #fef08a;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-top: 25px;
    }
    .dasha-card h4 {
        color: #92400e !important;
        margin-top: 0;
        margin-bottom: 12px;
        font-weight: 800;
        font-size: 1.15rem;
    }
    .dasha-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 10px;
        margin-top: 10px;
    }
    .dasha-item {
        background-color: #ffffff;
        border: 1px solid #fde047;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    .dasha-item .title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #854d0e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .dasha-item .planet {
        font-size: 1rem;
        font-weight: 800;
        color: #1e1b4b;
        margin: 4px 0;
    }
    .dasha-item .dates {
        font-size: 0.73rem;
        color: #475569;
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
# 2. CONSTANTS & LOCALIZATION
# ==========================================
nakshatra_list = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

nakshatra_lords = [
    "Ketu", "Venus (Shukra)", "Sun (Surya)", "Moon (Chandra)", "Mars (Mangal)", "Rahu",
    "Jupiter (Guru)", "Saturn (Shani)", "Mercury (Budh)",
    "Ketu", "Venus (Shukra)", "Sun (Surya)", "Moon (Chandra)", "Mars (Mangal)", "Rahu",
    "Jupiter (Guru)", "Saturn (Shani)", "Mercury (Budh)",
    "Ketu", "Venus (Shukra)", "Sun (Surya)", "Moon (Chandra)", "Mars (Mangal)", "Rahu",
    "Jupiter (Guru)", "Saturn (Shani)", "Mercury (Budh)"
]

rashi_list = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

lagna_list = rashi_list

navtara_names = [
    "Janma (Self / Body) ⚪",
    "Sampat (Wealth / Progress) 🟢",
    "Vipat (Obstacles / Delays) 🔴",
    "Kshema (Wellbeing / Comfort) 🟢",
    "Pratyari (Opposition / Tension) 🔴",
    "Sadhaka (Success / Achievement) 🟢",
    "Vadha (Risk / Danger) 🔴",
    "Mitra (Friend) 🟢",
    "Ati-Mitra (Best Friend) 🟢🟢"
]

dasha_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
dasha_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]

dasha_names_map = {
    "en": {"Ketu": "Ketu", "Venus": "Venus (Shukra)", "Sun": "Sun (Surya)", "Moon": "Moon (Chandra)", "Mars": "Mars (Mangal)", "Rahu": "Rahu", "Jupiter": "Jupiter (Guru)", "Saturn": "Saturn (Shani)", "Mercury": "Mercury (Budh)"},
    "hi": {"Ketu": "केतु", "Venus": "शुक्र", "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Rahu": "राहु", "Jupiter": "गुरु", "Saturn": "शनि", "Mercury": "बुध"},
    "mr": {"Ketu": "केतू", "Venus": "शुक्र", "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगळ", "Rahu": "राहु", "Jupiter": "गुरु", "Saturn": "शनि", "Mercury": "बुध"},
    "gu": {"Ketu": "કેતુ", "Venus": "શુક્ર", "Sun": "સૂર્ય", "Moon": "ચંદ્ર", "Mars": "મંગળ", "Rahu": "રાહુ", "Jupiter": "ગુરુ", "Saturn": "શનિ", "Mercury": "બુધ"}
}

dasha_predictions = {
    "en": {
        "Ketu": {"H": "Prone to sudden nervous exhaustion or skin allergy; maintain spiritual peace.", "C": "Deep analytical focus; research and technical tasks yield breakthroughs.", "F": "Silent financial restructuring; avoid speculative bets.", "M": "Intuitive, detached, and contemplative.", "R": "Seek quiet quality time; avoid unnecessary arguments.", "Remedy": "🕉️ Ketu Remedy: Feed stray dogs with bread/roti and recite 'Om Kem Ketave Namah'."},
        "Venus": {"H": "Radiant physical vitality and comfort; ensure balanced diet.", "C": "Creative success, design breakthroughs, and smooth client negotiations.", "F": "Prosperous period; favorable for asset expansion and luxury comfort.", "M": "Harmonious, charming, artistic, and peaceful.", "R": "Heartwarming romantic closeness and family joy.", "Remedy": "🌸 Venus Remedy: Offer white flowers to Goddess Lakshmi and donate ghee/rice on Fridays."},
        "Sun": {"H": "High solar stamina and confidence; care for cardiovascular health and posture.", "C": "Elevated leadership authority, government recognition, and promotion.", "F": "Strong capital growth and support from mentors/senior officials.", "M": "Commanding, dignified, bold, and decisive.", "R": "Lead ties with warmth; guard against ego friction.", "Remedy": "☀️ Sun Remedy: Offer fresh water (Arghya) to the rising Sun daily and recite Aditya Hrudayam."},
        "Moon": {"H": "Fluid vitality; maintain adequate hydration and mental peace.", "C": "High public networking, marketing success, and intuitive decision-making.", "F": "Steady financial liquidity and prosperous deal flows.", "M": "Empathetic, sensitive, imaginative, and observant.", "R": "Deep emotional bonding and nurturing family atmosphere.", "Remedy": "🌙 Moon Remedy: Drink water from a silver cup and respect mother/elder matriarchs."},
        "Mars": {"H": "High muscular stamina; avoid hasty movements or heat exhaustion.", "C": "Courageous execution, competitive victories, and swift goal completion.", "F": "Profitable real estate dealings and active capital accumulation.", "M": "Passionate, brave, dynamic, and goal-driven.", "R": "Express feelings directly; maintain patience during discussions.", "Remedy": "🔥 Mars Remedy: Recite Hanuman Chalisa daily and offer jaggery/red lentils in charity."},
        "Rahu": {"H": "Guard against sudden fatigue or irregular sleep cycles; practice breathwork.", "C": "Unconventional expansion, digital breakthrough, and global opportunities.", "F": "Fluctuating high-yield gains; maintain strict audit control.", "M": "Ambitious, visionary, but guard against overthinking.", "R": "Practice clear communication to prevent sudden miscommunications.", "Remedy": "🪐 Rahu Remedy: Keep workspace clean and chant 'Om Raam Rahave Namah' in the evening."},
        "Jupiter": {"H": "Robust health and optimism; avoid overindulgent heavy meals.", "C": "Expansion, wisdom counsel, teaching success, and institutional respect.", "F": "Substantial financial expansion, wisdom-backed investments, and long-term security.", "M": "Optimistic, noble, philosophical, and spiritually uplifted.", "R": "Noble family bonding, mentor support, and social respect.", "Remedy": "💛 Jupiter Remedy: Apply yellow sandalwood tilak on forehead and respect gurus/teachers."},
        "Saturn": {"H": "Saturnian resilience; care for joint flexibility and physical posture.", "C": "Authoritative responsibility, structured operations, and long-term achievement.", "F": "Solid debt management, disciplined savings, and stable capital foundation.", "M": "Pragmatic, cautious, highly disciplined, and resilient.", "R": "Fulfill commitments faithfully; practice patient listening.", "Remedy": "⚖️ Saturn Remedy: Light a sesame oil lamp on Saturdays and serve aged workers/laborers."},
        "Mercury": {"H": "Active nervous system; take short walking breaks to release mental strain.", "C": "Fast networking, analytical audits, sales pitch triumph, and commercial success.", "F": "Fluid wealth gains through quick strategic transactions.", "M": "Quick-witted, versatile, curious, and sharp.", "R": "Lively communication, joyful outings, and mutual intellectual understanding.", "Remedy": "💚 Mercury Remedy: Feed green fodder to cows and chant 'Om Budhaya Namah'."}
    },
    "hi": {
        "Ketu": {"H": "तंत्रिका थकान या त्वचा संवेदनशीलता की संभावना; आध्यात्मिक शांति बनाए रखें।", "C": "गहन विश्लेषणात्मक ध्यान; शोध और तकनीकी कार्यों में सफलता।", "F": "शांत वित्तीय पुनर्गठन; सट्टेबाजी से बचें।", "M": "सहज, अनासक्त और चिंतनशील।", "R": "शांत गुणवत्तापूर्ण समय बिताएं; बहस से बचें।", "Remedy": "🕉️ केतु उपाय: आवारा कुत्तों को रोटी खिलाएं और 'ॐ कें केतवे नमः' का जाप करें।"},
        "Venus": {"H": "जीवंत शारीरिक जीवन शक्ति और आराम; संतुलित आहार लें।", "C": "रचनात्मक सफलता, डिजाइन में प्रगति और सुचारू बातचीत।", "F": "समृद्ध काल; संपत्ति विस्तार और सुख-सुविधाओं के लिए अनुकूल।", "M": "सौहार्दपूर्ण, आकर्षक और शांतिपूर्ण।", "R": "रोमांटिक निकटता और पारिवारिक खुशी।", "Remedy": "🌸 शुक्र उपाय: देवी लक्ष्मी को सफेद फूल अर्पित करें और शुक्रवार को घी/चावल दान करें।"},
        "Sun": {"H": "उच्च सूर्य सहनशक्ति और आत्मविश्वास; हृदय स्वास्थ्य का ध्यान रखें।", "C": "उच्च नेतृत्व अधिकार, सरकारी मान्यता और पदोन्नति।", "F": "मजबूत पूंजी वृद्धि और वरिष्ठों का समर्थन।", "M": "गरिमापूर्ण, साहसी और निर्णायक।", "R": "सहानुभूति के साथ संबंध संभालें; अहंकार से बचें।", "Remedy": "☀️ सूर्य उपाय: सूर्यदेव को तांबे के पात्र से जल अर्पित करें।"},
        "Moon": {"H": "तरल जीवन शक्ति; पर्याप्त जलयोजन और मानसिक शांति बनाए रखें।", "C": "सार्वजनिक नेटवर्किंग और विपणन में सफलता।", "F": "स्थिर वित्तीय तरलता और लाभदायक सौदे।", "M": "सहानुभूतिपूर्ण, संवेदनशील और कल्पनाशील।", "R": "गहरी भावनात्मक निकटता और पारिवारिक माहौल।", "Remedy": "🌙 चंद्र उपाय: चांदी के बर्तन से पानी पीएं और माता का सम्मान करें।"},
        "Mars": {"H": "उच्च शारीरिक सहनशक्ति; जल्दबाजी से बचें।", "C": "साहसी निष्पादन, प्रतिस्पर्धी जीत और लक्ष्य पूर्ति।", "F": "रियल एस्टेट और पूंजी संचय से लाभ।", "M": "जुनूनी, साहसी और सक्रिय।", "R": "अपनी भावनाएं स्पष्ट रखें; धैर्य रखें।", "Remedy": "🔥 मंगल उपाय: प्रतिदिन हनुमान चालीसा का पाठ करें और गुड़ दान करें।"},
        "Rahu": {"H": "अचानक थकान या अनियमित नींद से बचें; प्राणायाम करें।", "C": "डिजिटल सफलता और वैश्विक अवसर।", "F": "उच्च आय के अवसर; सख्त बजट बनाए रखें।", "M": "महत्वाकांक्षी, दूरदर्शी लेकिन तनाव से बचें।", "R": "स्पष्ट बातचीत बनाए रखें।", "Remedy": "🪐 राहु उपाय: कार्यस्थल साफ रखें और 'ॐ रां राहवे नमः' का जाप करें।"},
        "Jupiter": {"H": "मजबूत स्वास्थ्य और आशावाद; भारी भोजन से बचें।", "C": "विस्तार, ज्ञान, सलाह और संस्थागत सम्मान।", "F": "बड़ा वित्तीय विस्तार और दीर्घकालिक सुरक्षा।", "M": "आशावादी, दार्शनिक और आध्यात्मिक।", "R": "पारिवारिक सामंजस्य और वरिष्ठों का सहयोग।", "Remedy": "💛 गुरु उपाय: मस्तक पर केसर/हल्दी का तिलक लगाएं और गुरुओं का सम्मान करें।"},
        "Saturn": {"H": "शनि का अनुशासन; जोड़ों के स्वास्थ्य का ध्यान रखें।", "C": "संरचित कार्यभार और दीर्घकालिक सफलता।", "F": "ऋण प्रबंधन और ठोस बचत नींव।", "M": "व्यावहारिक, सतर्क और अनुशासित।", "R": "प्रतिबद्धताओं का ईमानदारी से पालन करें।", "Remedy": "⚖️ शनि उपाय: शनिवार को तिल के तेल का दीपक जलाएं और बुजुर्गों की सेवा करें।"},
        "Mercury": {"H": "सक्रिय तंत्रिका तंत्र; मानसिक तनाव कम करने के लिए टहलें।", "C": "त्वरित नेटवर्किंग, ऑडिट और व्यापारिक सफलता।", "F": "रणनीतिक सौदों से त्वरित धन लाभ।", "M": "चतुर, बहुमुखी और तीक्ष्ण।", "R": "जीवंत संचार और आपसी समझ।", "Remedy": "💚 बुध उपाय: गायों को हरा चारा खिलाएं और 'ॐ बुधाय नमः' का जाप करें।"}
    }
}
dasha_predictions["mr"] = dasha_predictions["hi"]
dasha_predictions["gu"] = dasha_predictions["hi"]

num_lords_map = {
    "en": {1: "Sun (Surya)", 2: "Moon (Chandra)", 3: "Jupiter (Guru)", 4: "Rahu", 5: "Mercury (Budh)", 6: "Venus (Shukra)", 7: "Ketu", 8: "Saturn (Shani)", 9: "Mars (Mangal)"},
    "hi": {1: "सूर्य", 2: "चंद्र", 3: "गुरु", 4: "राहु", 5: "बुध", 6: "शुक्र", 7: "केतु", 8: "शनि", 9: "मंगल"}
}
num_lords_map["mr"] = num_lords_map["hi"]
num_lords_map["gu"] = num_lords_map["hi"]

nakshatra_traits_map = {
    "Ashwini": "Swift action, pioneering spirit, natural healing energy, courageous initiative, and enthusiasm.",
    "Bharani": "Strong willpower, transformative power, creative intensity, passion, and deep responsibility.",
    "Krittika": "Sharp intellect, ambitious nature, protective instincts, purifier energy, and determination.",
    "Rohini": "Charming personality, artistic elegance, growth, magnetic attraction, and steady stability.",
    "Mrigashira": "Inquisitive mind, seeker of truth, gentle nature, versatile adaptability, and perceptiveness.",
    "Ardra": "Analytical depth, emotional intensity, capacity for breakthroughs, research drive, and resilience.",
    "Punarvasu": "Optimistic outlook, restorative wisdom, generosity, spiritual purity, and good fortune.",
    "Pushya": "Nurturing demeanor, high moral values, protective caretaker, prosperous wisdom, and patience.",
    "Ashlesha": "Deep intuition, strategic intelligence, persuasive speech, protective focus, and sharp focus.",
    "Magha": "Royal dignity, leadership authority, respect for lineage, magnanimous presence, and self-respect.",
    "Purva Phalguni": "Creative flair, desire for comfort, social charm, relationship focus, and warm hospitality.",
    "Uttara Phalguni": "Helpful nature, commitment, leadership in service, integrity, patronage, and reliability.",
    "Hasta": "Skilled craftsmanship, practical intelligence, agility, resourceful problem-solving, and dexterity.",
    "Chitra": "Aesthetic vision, architectural skill, charismatic appeal, perfectionist eye, and creativity.",
    "Swati": "Independent spirit, diplomatic skill, flexible mind, lover of freedom, and balanced communication.",
    "Vishakha": "Unwavering focus, goal-oriented drive, competitive ambition, purposeful energy, and victory.",
    "Anuradha": "Devoted friendship, organizational mastery, resilience under pressure, harmony, and loyalty.",
    "Jyeshtha": "Protective leadership, senior authority, sharp courage, guardian energy, and executive power.",
    "Moola": "Root investigator, truth seeker, transformative insight, bold honesty, and deep research.",
    "Purva Ashadha": "Invincible confidence, persuasive speech, philosophical strength, pride, and enthusiasm.",
    "Uttara Ashadha": "Enduring success, ethical victory, steadfast leadership, duty-bound nature, and nobility.",
    "Shravana": "Active listener, seeker of knowledge, methodical wisdom, respectful presence, and learning.",
    "Dhanishta": "Musical and rhythmic talent, adaptability, wealth manifestation, group leadership, and optimism.",
    "Shatabhisha": "Mystical healer, visionary thinker, independent solver, deep research focus, and privacy.",
    "Purva Bhadrapada": "Passion for ideals, transformative vision, spiritual depth, intensity, and conviction.",
    "Uttara Bhadrapada": "Calming wisdom, emotional maturity, spiritual stability, patience, and altruism.",
    "Revati": "Compassionate guardian, nourishing guidance, artistic sensitivity, peaceful journey, and empathy."
}

moolank_traits_map = {
    "en": {
        1: "Solar vitality & original leadership — drives you to take bold independent initiatives.",
        2: "Lunar sensitivity & diplomatic harmony — excels in teamwork, empathy, and intuitive decisions.",
        3: "Jupiterian wisdom & expressive growth — fuels creative ideas, optimism, and effective counsel.",
        4: "Rahu's unconventional vision & practical discipline — excels in structured audits and systematic work.",
        5: "Mercurial agility & fast networking — thrives in dynamic environments and quick problem-solving.",
        6: "Venusian harmony & aesthetic balance — focuses on family wellness, design, and relationship bonding.",
        7: "Ketu's contemplative research & deep intuition — thrives in analytical study and quiet observation.",
        8: "Saturnian resilience & financial execution — commands authoritative responsibility and solid planning.",
        9: "Martial stamina & courageous completion — drives completion of pending goals and passionate action."
    },
    "hi": {
        1: "सूर्य की ऊर्जा व मौलिक नेतृत्व — आपको स्वतंत्र और साहसी पहल करने की प्रेरणा देता है।",
        2: "चंद्रमा की संवेदनशीलता व कूटनीतिक सौहार्द — टीम वर्क, सहानुभूति और अंतर्ज्ञान में श्रेष्ठ।",
        3: "गुरु का ज्ञान व अभिव्यक्ति — रचनात्मक विचारों, आशावाद और सही सलाह को बढ़ावा देता है।",
        4: "राहु की व्यावहारिक अनुशासन व अनूठी दृष्टि — संरचित ऑडिट और व्यवस्थित कार्यों में निपुण।",
        5: "बुध की चपलता व त्वरित नेटवर्किंग — गतिशील वातावरण और त्वरित समस्या समाधान में सफल।",
        6: "शुक्र का सौंदर्य व सामंजस्य — पारिवारिक कल्याण, डिजाइन और संबंधों के निर्माण पर केंद्रित।",
        7: "केतु का गहन शोध व अंतर्ज्ञान — विश्लेषणात्मक अध्ययन और शांत अवलोकन में सर्वोत्तम।",
        8: "शनि का धैर्य व वित्तीय निष्पादन — जिम्मेदारियों और ठोस वित्तीय नियोजन को संभालता है।",
        9: "मंगल का साहस व लक्ष्य पूर्ति — रुके हुए कार्यों को पूरा करने और साहसी कदमों के लिए प्रेरित करता है।"
    }
}
moolank_traits_map["mr"] = moolank_traits_map["hi"]
moolank_traits_map["gu"] = moolank_traits_map["hi"]

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
    }
}
personal_day_meanings["mr"] = personal_day_meanings["hi"]
personal_day_meanings["gu"] = personal_day_meanings["hi"]

paya_map = {
    "en": {
        2: {"name": "Rajat Paya (Silver Feet) 🥈", "grade": "Most Auspicious & Protective", "desc": "Acts as a divine protective shield, cushioning transit friction, bringing financial expansion, debt clearance, and steady career growth."},
        5: {"name": "Rajat Paya (Silver Feet) 🥈", "grade": "Most Auspicious & Protective", "desc": "Acts as a divine protective shield, cushioning transit friction, bringing financial expansion, debt clearance, and steady career growth."},
        9: {"name": "Rajat Paya (Silver Feet) 🥈", "grade": "Most Auspicious & Protective", "desc": "Acts as a divine protective shield, cushioning transit friction, bringing financial expansion, debt clearance, and steady career growth."},
        3: {"name": "Tamra Paya (Copper Feet) 🥉", "grade": "Favorable & Productive", "desc": "Brings rewards for honest hard work, steady business growth, positive support from elders/mentors, and strong physical stamina."},
        7: {"name": "Tamra Paya (Copper Feet) 🥉", "grade": "Favorable & Productive", "desc": "Brings rewards for honest hard work, steady business growth, positive support from elders/mentors, and strong physical stamina."},
        10: {"name": "Tamra Paya (Copper Feet) 🥉", "grade": "Favorable & Productive", "desc": "Brings rewards for honest hard work, steady business growth, positive support from elders/mentors, and strong physical stamina."},
        1: {"name": "Swarna Paya (Gold Feet) 🥇", "grade": "Testing / Mixed Results", "desc": "Brings prestige alongside high personal/family expenses and workload. Requires strict budget discipline, humility, and avoiding ego clashes."},
        6: {"name": "Swarna Paya (Gold Feet) 🥇", "grade": "Testing / Mixed Results", "desc": "Brings prestige alongside high personal/family expenses and workload. Requires strict budget discipline, humility, and avoiding ego clashes."},
        11: {"name": "Swarna Paya (Gold Feet) 🥇", "grade": "Testing / Mixed Results", "desc": "Brings prestige alongside high personal/family expenses and workload. Requires strict budget discipline, humility, and avoiding ego clashes."},
        4: {"name": "Loha Paya (Iron Feet) 🪙", "grade": "Requires Discipline & Caution", "desc": "Brings delays in key projects, physical fatigue or joint strain. Best managed through routine hard work, avoiding speculative bets, and reciting Hanuman Chalisa daily."},
        8: {"name": "Loha Paya (Iron Feet) 🪙", "grade": "Requires Discipline & Caution", "desc": "Brings delays in key projects, physical fatigue or joint strain. Best managed through routine hard work, avoiding speculative bets, and reciting Hanuman Chalisa daily."},
        12: {"name": "Loha Paya (Iron Feet) 🪙", "grade": "Requires Discipline & Caution", "desc": "Brings delays in key projects, physical fatigue or joint strain. Best managed through routine hard work, avoiding speculative bets, and reciting Hanuman Chalisa daily."}
    },
    "hi": {
        2: {"name": "चांदी का पाया (Rajat Paya) 🥈", "grade": "अति शुभ एवं सुरक्षात्मक", "desc": "दिव्य सुरक्षा कवच के रूप में कार्य करता है; वित्तीय विस्तार, ऋण मुक्ति और स्थिर व्यावसायिक प्रगति प्रदान करता है।"},
        5: {"name": "चांदी का पाया (Rajat Paya) 🥈", "grade": "अति शुभ एवं सुरक्षात्मक", "desc": "दिव्य सुरक्षा कवच के रूप में कार्य करता है; वित्तीय विस्तार, ऋण मुक्ति और स्थिर व्यावसायिक प्रगति प्रदान करता है।"},
        9: {"name": "चांदी का पाया (Rajat Paya) 🥈", "grade": "अति शुभ एवं सुरक्षात्मक", "desc": "दिव्य सुरक्षा कवच के रूप में कार्य करता है; वित्तीय विस्तार, ऋण मुक्ति और स्थिर व्यावसायिक प्रगति प्रदान करता है।"},
        3: {"name": "तांबे का पाया (Tamra Paya) 🥉", "grade": "शुभ एवं फलदायी", "desc": "ईमानदार कड़ी मेहनत का प्रतिफल, व्यापार में वृद्धि, वरिष्ठों का समर्थन और मजबूत शारीरिक क्षमता प्रदान करता है।"},
        7: {"name": "तांबे का पाया (Tamra Paya) 🥉", "grade": "शुभ एवं फलदायी", "desc": "ईमानदार कड़ी मेहनत का प्रतिफल, व्यापार में वृद्धि, वरिष्ठों का समर्थन और मजबूत शारीरिक क्षमता प्रदान करता है।"},
        10: {"name": "तांबे का पाया (Tamra Paya) 🥉", "grade": "शुभ एवं फलदायी", "desc": "ईमानदार कड़ी मेहनत का प्रतिफल, व्यापार में वृद्धि, वरिष्ठों का समर्थन और मजबूत शारीरिक क्षमता प्रदान करता है।"},
        1: {"name": "सोने का पाया (Swarna Paya) 🥇", "grade": "मध्यम एवं सचेत", "desc": "प्रतिष्ठा के साथ उच्च व्यक्तिगत व पारिवारिक खर्च लाता है। बजट अनुशासन, विनम्रता और अहंकार से बचने की आवश्यकता है।"},
        6: {"name": "सोने का पाया (Swarna Paya) 🥇", "grade": "मध्यम एवं सचेत", "desc": "प्रतिष्ठा के साथ उच्च व्यक्तिगत व पारिवारिक खर्च लाता है। बजट अनुशासन, विनम्रता और अहंकार से बचने की आवश्यकता है।"},
        11: {"name": "सोने का पाया (Swarna Paya) 🥇", "grade": "मध्यम एवं सचेत", "desc": "प्रतिष्ठा के साथ उच्च व्यक्तिगत व पारिवारिक खर्च लाता है। बजट अनुशासन, विनम्रता और अहंकार से बचने की आवश्यकता है।"},
        4: {"name": "लोहे का पाया (Loha Paya) 🪙", "grade": "कठिन एवं धैर्यपूर्वक", "desc": "कार्यों में विलंब, शारीरिक थकान या जोड़ों में खिंचाव संभव है। दिनचर्या की मेहनत और हनुमान चालीसा के पाठ से श्रेष्ठ परिणाम मिलते हैं।"},
        8: {"name": "लोहे का पाया (Loha Paya) 🪙", "grade": "कठिन एवं धैर्यपूर्वक", "desc": "कार्यों में विलंब, शारीरिक थकान या जोड़ों में खिंचाव संभव है। दिनचर्या की मेहनत और हनुमान चालीसा के पाठ से श्रेष्ठ परिणाम मिलते हैं।"},
        12: {"name": "लोहे का पाया (Loha Paya) 🪙", "grade": "कठिन एवं धैर्यपूर्वक", "desc": "कार्यों में विलंब, शारीरिक थकान या जोड़ों में खिंचाव संभव है। दिनचर्या की मेहनत और हनुमान चालीसा के पाठ से श्रेष्ठ परिणाम मिलते हैं।"}
    }
}
paya_map["mr"] = paya_map["hi"]
paya_map["gu"] = paya_map["hi"]

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
    },
    "hi": {
        1: {"name": "घोड़ा (Horse) 🐴", "symbolism": "गति और तीव्र प्रगति", "H": "उच्च शारीरिक सहनशक्ति; अत्यधिक परिश्रम से बचें।", "C": "तेजी से करियर विस्तार और प्रतिस्पर्धियों पर विजय।", "F": "तेज वित्तीय प्रवाह और लाभदायक सौदों की गति।", "M": "ऊर्जावान, साहसी और सक्रिय मानसिकता।", "R": "गतिशील संचार; साझेदार के निर्णयों में जल्दबाजी से बचें।", "Remedy": "🏇 शनि वाहन उपाय: शनिवार को घोड़ों या श्रमिकों को भिगोए हुए काले चने खिलाएं।"},
        2: {"name": "गधा (Donkey) 🫏", "symbolism": "कड़ा परिश्रम और धैर्य", "H": "शारीरिक थकान या जोड़ों में खिंचाव; पर्याप्त आराम सुनिश्चित करें।", "C": "धैर्य की आवश्यकता वाला भारी कार्यभार; निरंतर प्रयास से परिणाम मिलते हैं।", "F": "सख्त बजट की आवश्यकता; नियमित आय पर ध्यान दें।", "M": "तनाव के खिलाफ लचिलापन।", "R": "घरेलू विवादों से बचने के लिए सुनने का अभ्यास करें।", "Remedy": "🫏 शनि वाहन उपाय: बुजुर्ग श्रमिकों की सेवा करें या जरूरतमंदों को जूते-चप्पल दान करें।"},
        3: {"name": "सियार (Jackal) 🦊", "symbolism": "सावधानी और सतर्कता", "H": "तंत्रिका थकान; हाइड्रेटेड और शांत रहें।", "C": "गुमराह करने वाली सलाह से बचें; सभी दस्तावेजों की दो बार जांच करें।", "F": "वित्तीय धोखाधड़ी का जोखिम; असत्यापित योजनाओं से बचें।", "M": "सतर्क, सूक्ष्मदर्शी लेकिन अधिक सोचने से बचें।", "R": "बातचीत में प्रत्यक्ष और पारदर्शी रहें।", "Remedy": "🦊 शनि वाहन उपाय: शनिवार की शाम आवारा पशुओं या पक्षियों को रोटी/ब्रेड खिलाएं।"},
        4: {"name": "हाथी (Elephant) 🐘", "symbolism": "राजसी प्रतिष्ठा और वित्तीय लाभ", "H": "मजबूत स्वास्थ्य, गरिमापूर्ण ऊर्जा और स्थिरता।", "C": "अधिकारियों से मान्यता, पदोन्नति और उच्च प्रतिष्ठा।", "F": "वित्तीय लाभ, लग्जरी संपत्ति और स्थिरता।", "M": "गरिमापूर्ण, उदार, आत्मविश्वासी और शांत।", "R": "परिवार और सामाजिक संबंधों में उदार उपस्थिति।", "Remedy": "🐘 शनि वाहन उपाय: गुरुओं का सम्मान करें और सरसों का तेल या तिल दान करें।"},
        5: {"name": "बैल (Bull) 🐂", "symbolism": "निरंतर दृढ़ता और वृद्धि", "H": "ठोस सहनशक्ति; गर्दन और जोड़ों की लचक बनाए रखें।", "C": "मूल कार्यों में व्यवस्थित प्रगति; जमीनी कार्य के लिए आदर्श।", "F": "रियल एस्टेट या संपत्ति के माध्यम से स्थिर संचय।", "M": "व्यावहारिक, निरंतर, धैर्यवान और केंद्रित।", "R": "भरोसेमंद, प्रतिबद्ध और स्थिर संबंध।", "Remedy": "🐂 शनि वाहन उपाय: शनिवार को काले बैलों या गायों को हरा चारा या गुड़ खिलाएं।"},
        6: {"name": "शेर (Lion) 🦁", "symbolism": "शक्ति और नेतृत्व का साहस", "H": "मजबूत आत्मविश्वास; हृदय के तनाव को कम रखें।", "C": "कमांडिंग नेतृत्व अधिकार; चुनौतियों पर विजय।", "F": "मजबूत पूंजी सुरक्षा और बातचीत में बढ़त।", "M": "साहसी, निडर, आधिकारिक और निर्णायक।", "R": "अपनों की सुरक्षा करें; दबदबा बनाने से बचें।", "Remedy": "🦁 शनि वाहन उपाय: हनुमान चालीसा का पाठ करें या भगवान हनुमान या शिव को लाल फूल अर्पित करें।"},
        7: {"name": "कौवा (Crow) 🐦‍⬛", "symbolism": "बेचैनी और बिखरा हुआ ध्यान", "H": "बेचैन नसें या हल्की नींद; प्राणायाम का अभ्यास करें।", "C": "बार-बार यात्रा, बिखरा हुआ ध्यान या अप्रत्याशित देरी।", "F": "छोटे-मोटे खर्च; ऑनलाइन आवेगपूर्ण खरीदारी से बचें।", "M": "चिंताजनक मानसिकता; मौन और ध्यान का अभ्यास करें।", "R": "निकटतम परिवार के साथ बहस से बचें।", "Remedy": "🐦‍⬛ शनि वाहन उपाय: हर सुबह कौवों या पक्षियों को अनाज या रोटी खिलाएं।"},
        8: {"name": "मयूर (Peacock) 🦚", "symbolism": "आनंद और रचनात्मक सफलता", "H": "जीवंत जीवन शक्ति, सौंदर्य और भावात्मक चमक।", "C": "रचनात्मक सफलता, सामाजिक प्रशंसा और टीम में सामंजस्य।", "F": "सुखद वित्तीय लाभ और सुखद आश्चर्य।", "M": "आनंदमय, आशावादी, रचनात्मक और प्रसन्न।", "R": "रोमांटिक गर्माहट, सुखद पारिवारिक समाचार और सामाजिक खुशी।", "Remedy": "🦚 शनि वाहन उपाय: अपने डेस्क पर मोर पंख रखें या 'ॐ शं शनैश्चराय नमः' का जाप करें।"},
        9: {"name": "हंस (Swan) 🦢", "symbolism": "सर्वोच्च ज्ञान और शांति", "H": "शांतिपूर्ण जीवन शक्ति, मानसिक शांति और समग्र स्वास्थ्य।", "C": "बुद्धिमत्तापूर्ण निर्णय, उत्कृष्ट निर्णय क्षमता और सम्मान।", "F": "मजबूत वित्तीय सुरक्षा, ऋण मुक्ति और बुद्धिमान निवेश।", "M": "गहरी आध्यात्मिक स्पष्टता, शांत और सहज।", "R": "शुद्ध, आत्मा को पोषण देने वाला सामंजस्य और आपसी सम्मान।", "Remedy": "🦢 शनि वाहन उपाय: शांत ध्यान का अभ्यास करें; पक्षियों या भगवान शिव को दूध या ताजा पानी अर्पित करें।"}
    }
}
vahan_map["mr"] = vahan_map["hi"]
vahan_map["gu"] = vahan_map["hi"]

tara_details_en = {
    0: {"status": "Janma ⚪", "H": "Focus on self-care and light diet.", "C": "Maintain daily routine tasks.", "F": "Keep finances stable.", "M": "Self-reflective mindset.", "Rel": "Maintain emotional balance in relationships.", "R": ""},
    1: {"status": "Sampat 🟢", "H": "High physical energy and vitality.", "C": "Excellent day for professional growth.", "F": "Favorable for wealth accumulation.", "M": "Positive and confident mindset.", "Rel": "Great day for bonding and mutual trust.", "R": ""},
    2: {"status": "Vipat 🔴", "H": "Physically vulnerable; avoid strain.", "C": "Unexpected hurdles or project delays.", "F": "Strictly avoid speculative investments.", "M": "Prone to sudden stress.", "Rel": "Practice patient listening to prevent friction.", "R": "🛡️ Vedic Remedy: Recite Hanuman Chalisa or offer fresh water to green plants/birds."},
    3: {"status": "Kshema 🟢", "H": "Good health and physical comfort.", "C": "Smooth operations and steady progress.", "F": "Financial security is favored.", "M": "Peaceful and emotionally balanced.", "Rel": "Warm family moments and comfort.", "R": ""},
    4: {"status": "Pratyari 🔴", "H": "Ensure adequate sleep and hydration.", "C": "Possible friction with authority figures.", "F": "Unexpected small expenses.", "M": "Easily irritated; practice mindfulness.", "Rel": "Practice silence during arguments.", "R": "🛡️ Vedic Remedy: Practice Mouna (silence) during arguments or chant 'Om Sham Shanayscharaya Namah'."},
    5: {"status": "Sadhaka 🟢", "H": "Strong physical vitality.", "C": "Breakthroughs and goal achievements.", "F": "Profitable long-term investments.", "M": "Determined and highly focused.", "Rel": "Resolve past issues and deepen bonds.", "R": ""},
    6: {"status": "Vadha 🔴", "H": "Higher fatigue or vulnerability; caution.", "C": "Major blockages; avoid confrontations.", "F": "Protect capital; avoid risky deals.", "M": "Overwhelmed or defensive.", "Rel": "Avoid bringing up past grievances.", "R": "🛡️ Vedic Remedy: Chant Mahamrityunjaya Mantra or offer water/milk to Lord Shiva."},
    7: {"status": "Mitra 🟢", "H": "Improving physical energy.", "C": "Good team cooperation and support.", "F": "Collaborative financial gains.", "M": "Happy and socially supported.", "Rel": "Supportive and friendly vibration.", "R": ""},
    8: {"status": "Ati-Mitra 🟢🟢", "H": "Vibrant energy and health.", "C": "High growth and public recognition.", "F": "Financial windfalls or good news.", "M": "Joyous and spiritually uplifted.", "Rel": "Deep emotional joy and family harmony.", "R": ""}
}

translations = {
    "en": {
        "intro_title": "Unlocking the Wisdom of Vedic Astrology",
        "intro_desc": "In Vedic astrology and numerology, the Moon's transit through the 27 Nakshatras and daily numerical vibrations create a unique energy pattern relative to your birth profile. This app provides accurate, astronomical, and numerological insights into your health, career, finance, mindset, and relationships.",
        "profile_title": "👤 Birth Profile",
        "horoscope_title": "7-Day Horoscope Prediction & Life Guidance",
        "dasha_title": "🔮 Vimshottari Dasha Analysis & Life Guidance",
        "search_prompt": "🌍 Birth Place Name or 6-Digit Pincode",
        "generate_btn": "Save Profile & Generate Predictions",
        "expander_title": "✨ Click here to see the Prediction & Life Guidance ✨",
        "dasha_expander_title": "✨ Click here for Active Dasha Impact & Predictions ✨",
        "name_label": "Name", "dob_label": "Date of Birth", "tob_label": "Time of Birth (24-Hour)",
        "birth_place_label": "Birth Place",
        "mobile_banner_title": "📱 Save & Install for 1-Click Mobile Access",
        "mobile_banner_desc": "Your birth profile details have been saved to this custom URL. To open this horoscope anytime without re-entering details:",
        "mobile_banner_ios": "iPhone (Safari): Tap the Share icon ➔ select 'Add to Home Screen'.",
        "mobile_banner_android": "Android (Chrome): Tap the three dots (⋮) ➔ select 'Add to Home screen' or 'Install App'.",
        "navtara_head": "🌙 Navtara Transit:", "num_head": "🔢 Numerology Vibration:", "vahan_head": "🪐 Shani Vahan:",
        "health_head": "🩺 Health:", "career_head": "💼 Career:", "finance_head": "💰 Finance:", "mindset_head": "🧘 Mindset:", "rel_head": "❤️ Relationships:",
        "share_title": "🔗 Share Navtara Pulse",
        "active_now": "⚡ Active Now",
        "warning_name": "⚠️ Name is required", "warning_dob": "⚠️ Date of Birth is required",
        "warning_hh": "⚠️ Hour (HH) is required", "warning_mm": "⚠️ Minute (MM) is required",
        "warning_place": "⚠️ Birth Place or 6-digit Pincode is required",
        "tara": tara_details_en,
        "vahan_details": vahan_map["en"],
        "paya_details": paya_map["en"],
        "moolank_details": moolank_traits_map["en"],
        "nak_details": nakshatra_traits_map
    },
    "hi": {
        "intro_title": "वैदिक ज्योतिष और अंकशास्त्र का ज्ञान",
        "intro_desc": "वैदिक ज्योतिष और अंकशास्त्र में, 27 नक्षत्रों में चंद्रमा का गोचर और दैनिक अंक कंपन आपके जन्म विवरण के सापेक्ष एक अनूठा ऊर्जा पैटर्न बनाते हैं। यह ऐप स्वास्थ्य, करियर, वित्त, मानसिकता और संबंधों में सटीक अंतर्दृष्टि प्रदान करता है।",
        "profile_title": "👤 जन्म विवरण",
        "horoscope_title": "7-दिवसीय राशिफल भविष्यवाणी और जीवन मार्गदर्शन",
        "dasha_title": "🔮 विंशोत्तरी दशा विश्लेषण एवं जीवन मार्गदर्शन",
        "search_prompt": "🌍 जन्म स्थान का नाम या 6-अंकीय पिनकोड",
        "generate_btn": "प्रोफाइल सहेजें और भविष्यवाणियां उत्पन्न करें",
        "expander_title": "✨ दैनिक भविष्यवाणी और जीवन मार्गदर्शन देखने के लिए यहां क्लिक करें ✨",
        "dasha_expander_title": "✨ सक्रिय दशा प्रभाव एवं भविष्यवाणियां देखने के लिए यहां क्लिक करें ✨",
        "name_label": "नाम", "dob_label": "जन्म तिथि", "tob_label": "जन्म समय (24-घंटे)",
        "birth_place_label": "जन्म स्थान",
        "mobile_banner_title": "📱 1-क्लिक मोबाइल एक्सेस के लिए सहेजें और इंस्टॉल करें",
        "mobile_banner_desc": "आपके जन्म विवरण इस URL में सहेजे गए हैं। बिना दोबारा विवरण भरे कभी भी देखने के लिए:",
        "mobile_banner_ios": "iPhone (Safari): शेयर (Share) आइकन ➔ 'Add to Home Screen' चुनें।",
        "mobile_banner_android": "Android (Chrome): तीन बिंदु (⋮) ➔ 'Add to Home screen' या 'Install App' चुनें।",
        "navtara_head": "🌙 नवतारा गोचर:", "num_head": "🔢 अंकशास्त्र कंपन:", "vahan_head": "🪐 शनि वाहन:",
        "health_head": "🩺 स्वास्थ्य:", "career_head": "💼 करियर:", "finance_head": "💰 वित्त:", "mindset_head": "🧘 मानसिकता:", "rel_head": "❤️ संबंध:",
        "share_title": "🔗 नवतारा पल्स शेयर करें",
        "active_now": "⚡ अभी सक्रिय",
        "warning_name": "⚠️ नाम आवश्यक है", "warning_dob": "⚠️ जन्म तिथि आवश्यक है",
        "warning_hh": "⚠️ घंटा (HH) आवश्यक है", "warning_mm": "⚠️ मिनट (MM) आवश्यक है",
        "warning_place": "⚠️ जन्म स्थान या 6-अंकीय पिनकोड आवश्यक है",
        "tara": tara_details_en,
        "vahan_details": vahan_map["hi"],
        "paya_details": paya_map["hi"],
        "moolank_details": moolank_traits_map["hi"],
        "nak_details": nakshatra_traits_map
    }
}
translations["mr"] = translations["hi"]
translations["gu"] = translations["hi"]

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
    """Calculates exact Sidereal Moon Lon, Nakshatra, Rashi, and Lagna indices using PyEphem + Lahiri Ayanamsa."""
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
        
    return nakshatra_index, rashi_index, lagna_index, sidereal_moon_lon

def calculate_7_day_transits(now_utc, utc_offset_hours, days=7):
    """Computes current and future transits anchored strictly to UTC time."""
    now_local = now_utc + datetime.timedelta(hours=utc_offset_hours)
    current_nak, _, _, _ = get_moon_and_kundli_indices(now_utc)
    
    start_search_utc = now_utc
    for i in range(1, 200):
        test_utc = now_utc - datetime.timedelta(minutes=15 * i)
        test_nak, _, _, _ = get_moon_and_kundli_indices(test_utc)
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
        test_nak, _, _, _ = get_moon_and_kundli_indices(test_utc)
        
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

def calculate_vimshottari_dasha(birth_utc_dt, moon_lon_deg, target_utc_dt):
    """Calculates 5-level Vimshottari Dasha hierarchy for a target date."""
    nak_span = 13.333333333333334
    nak_idx = int(moon_lon_deg / nak_span) % 27
    lord_idx = nak_idx % 9
    
    traversed = (moon_lon_deg % nak_span) / nak_span
    remaining = 1.0 - traversed
    
    first_md_years = dasha_years[lord_idx] * remaining
    consumed_first_md_years = dasha_years[lord_idx] - first_md_years
    
    first_md_start = birth_utc_dt - datetime.timedelta(days=consumed_first_md_years * 365.25)
    
    curr_start = first_md_start
    active_md_idx = lord_idx
    
    # 1. Mahadasha Loop
    for step in range(30):
        dur_years = dasha_years[active_md_idx]
        curr_end = curr_start + datetime.timedelta(days=dur_years * 365.25)
        if curr_start <= target_utc_dt < curr_end:
            break
        curr_start = curr_end
        active_md_idx = (active_md_idx + 1) % 9
        
    md_start, md_end, md_lord = curr_start, curr_end, dasha_order[active_md_idx]
    
    # 2. Antardasha Loop
    ad_curr_start = md_start
    active_ad_idx = active_md_idx
    for step in range(9):
        ad_dur_days = (dasha_years[active_md_idx] * dasha_years[active_ad_idx] / 120.0) * 365.25
        ad_curr_end = ad_curr_start + datetime.timedelta(days=ad_dur_days)
        if ad_curr_start <= target_utc_dt < ad_curr_end:
            break
        ad_curr_start = ad_curr_end
        active_ad_idx = (active_ad_idx + 1) % 9
        
    ad_start, ad_end, ad_lord = ad_curr_start, ad_curr_end, dasha_order[active_ad_idx]
    
    # 3. Pratyantardasha Loop
    pd_curr_start = ad_start
    active_pd_idx = active_ad_idx
    ad_total_days = (dasha_years[active_md_idx] * dasha_years[active_ad_idx] / 120.0) * 365.25
    for step in range(9):
        pd_dur_days = (ad_total_days * dasha_years[active_pd_idx] / 120.0)
        pd_curr_end = pd_curr_start + datetime.timedelta(days=pd_dur_days)
        if pd_curr_start <= target_utc_dt < pd_curr_end:
            break
        pd_curr_start = pd_curr_end
        active_pd_idx = (active_pd_idx + 1) % 9
        
    pd_start, pd_end, pd_lord = pd_curr_start, pd_curr_end, dasha_order[active_pd_idx]
    
    # 4. Sookshmadasha Loop
    sd_curr_start = pd_start
    active_sd_idx = active_pd_idx
    pd_total_days = (ad_total_days * dasha_years[active_pd_idx] / 120.0)
    for step in range(9):
        sd_dur_days = (pd_total_days * dasha_years[active_sd_idx] / 120.0)
        sd_curr_end = sd_curr_start + datetime.timedelta(days=sd_dur_days)
        if sd_curr_start <= target_utc_dt < sd_curr_end:
            break
        sd_curr_start = sd_curr_end
        active_sd_idx = (active_sd_idx + 1) % 9
        
    sd_start, sd_end, sd_lord = sd_curr_start, sd_curr_end, dasha_order[active_sd_idx]
    
    # 5. Pranadasha Loop
    prd_curr_start = sd_start
    active_prd_idx = active_sd_idx
    sd_total_days = (pd_total_days * dasha_years[active_sd_idx] / 120.0)
    for step in range(9):
        prd_dur_days = (sd_total_days * dasha_years[active_prd_idx] / 120.0)
        prd_curr_end = prd_curr_start + datetime.timedelta(days=prd_dur_days)
        if prd_curr_start <= target_utc_dt < prd_curr_end:
            break
        prd_curr_start = prd_curr_end
        active_prd_idx = (active_prd_idx + 1) % 9
        
    prd_start, prd_end, prd_lord = prd_curr_start, prd_curr_end, dasha_order[active_prd_idx]
    
    return {
        "MD": {"lord": md_lord, "start": md_start, "end": md_end},
        "AD": {"lord": ad_lord, "start": ad_start, "end": ad_end},
        "PD": {"lord": pd_lord, "start": pd_start, "end": pd_end},
        "SD": {"lord": sd_lord, "start": sd_start, "end": sd_end},
        "PRD": {"lord": prd_lord, "start": prd_start, "end": prd_end}
    }

# ==========================================
# 4. MAIN APP LAYOUT & URL PARAMETERS
# ==========================================
query_params = st.query_params

if 'profile_generated' not in st.session_state:
    st.session_state['profile_generated'] = (query_params.get('saved') == 'true')

st.title("🌙 Navtara Pulse")

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

dob_day_idx = 0
dob_month_idx = 0
dob_year_idx = 0

year_options_list = [str(y) for y in range(2026, 1899, -1)]

if default_date_str:
    try:
        parsed_d = datetime.datetime.strptime(default_date_str, '%Y-%m-%d').date()
        dob_day_idx = parsed_d.day
        dob_month_idx = parsed_d.month
        if str(parsed_d.year) in year_options_list:
            dob_year_idx = year_options_list.index(str(parsed_d.year)) + 1
    except:
        pass

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

    st.write(t['dob_label'])
    dob_c1, dob_c2, dob_c3 = st.columns(3)
    
    day_options = ["--"] + [f"{i:02d}" for i in range(1, 32)]
    month_options = ["--", "Jan (01)", "Feb (02)", "Mar (03)", "Apr (04)", "May (05)", "Jun (06)", "Jul (07)", "Aug (08)", "Sep (09)", "Oct (10)", "Nov (11)", "Dec (12)"]
    year_options = ["--"] + year_options_list

    with dob_c1:
        selected_day = st.selectbox("DD", day_options, index=dob_day_idx)
    with dob_c2:
        selected_month = st.selectbox("MM", month_options, index=dob_month_idx)
    with dob_c3:
        selected_year = st.selectbox("YYYY", year_options, index=dob_year_idx)

    is_dob_valid = False
    birth_date = None

    if selected_day != "--" and selected_month != "--" and selected_year != "--":
        try:
            m_num = month_options.index(selected_month)
            birth_date = datetime.date(int(selected_year), m_num, int(selected_day))
            is_dob_valid = True
        except ValueError:
            st.markdown(f'<span class="missing-field-warning">{t["warning_dob"]} (Invalid Date)</span>', unsafe_allow_html=True)
    else:
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

utc_offset_val = get_utc_offset_hours(place_obj_data, place_query)

if is_dob_valid and is_hh_valid and is_mm_valid:
    birth_local_dt = datetime.datetime.combine(birth_date, datetime.time(int(birth_hour), int(birth_minute)))
    birth_utc_dt = birth_local_dt - datetime.timedelta(hours=utc_offset_val)
    auto_janma_idx, auto_rashi_idx, auto_lagna_idx, birth_moon_lon = get_moon_and_kundli_indices(birth_utc_dt, place_obj_data)
else:
    auto_janma_idx, auto_rashi_idx, auto_lagna_idx, birth_moon_lon = 0, 0, 0, 0.0

if selected_place_display and is_place_valid:
    st.markdown(f"<div class='verified-badge'>📍 Birth Place: {selected_place_display}</div>", unsafe_allow_html=True)

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
    
    janma_nakshatra_name = nakshatra_list[auto_janma_idx]
    janma_lord = nakshatra_lords[auto_janma_idx]
    janma_rashi_name = rashi_list[auto_rashi_idx]
    janma_lagna_name = lagna_list[auto_lagna_idx]
    janma_traits = nakshatra_traits_map.get(janma_nakshatra_name, "Balanced vitality, strong intuition, and steady growth.")
    
    moolank = reduce_to_single_digit(birth_date.day)
    bhagyank = reduce_to_single_digit(birth_date.day + birth_date.month + birth_date.year)
    moolank_lord = num_lords_map[lang_code].get(moolank, "")
    bhagyank_lord = num_lords_map[lang_code].get(bhagyank, "")
    moolank_trait = moolank_traits_map[lang_code].get(moolank, "Leadership and steady focus.")
    bhagyank_trait = moolank_traits_map[lang_code].get(bhagyank, "Long-term purpose and natural path.")
    lucky_nums = lucky_numbers_map.get(moolank, "1, 3, 5, 6")
    
    saturn_transit_rashi_idx = 11  # Pisces (Meena)
    house_from_saturn = (auto_rashi_idx - saturn_transit_rashi_idx) % 12 + 1
    active_paya = t["paya_details"].get(house_from_saturn, t["paya_details"][2])
    
    clean_name = user_name.strip()
    profile_display_name = f"{clean_name}'s Profile" if lang_code == "en" else f"{clean_name} की प्रोफाइल"

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
    
    # 7-DAY TRANSIT CARDS
    st.header(t['horoscope_title'])
    
    now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    transits = calculate_7_day_transits(now_utc, utc_offset_val)
    
    for transit in transits:
        nak_difference = (transit["nak_index"] - auto_janma_idx) % 27
        tara_index = nak_difference % 9
        
        tara_data = t["tara"][tara_index]
        tara_badge_name = navtara_names[tara_index]
        transit_nak_name = nakshatra_list[transit["nak_index"]]
        transit_nak_lord = nakshatra_lords[transit["nak_index"]]
        
        start_str = transit["start"].strftime('%a, %d %b %I:%M %p')
        end_str = transit["end"].strftime('%a, %d %b %I:%M %p')
        
        current_pill = f"<span class='current-badge'>{t['active_now']}</span>" if transit.get("is_current") else ""
        
        t_date = transit["start"].date()
        p_day = reduce_to_single_digit(birth_date.day + birth_date.month + t_date.day + t_date.month + t_date.year)
        p_lord = num_lords_map[lang_code].get(p_day, "")
        p_desc = personal_day_meanings[lang_code].get(p_day, "")
        
        janma_nak_num = auto_janma_idx + 1
        transit_nak_num = transit["nak_index"] + 1
        vahan_rem = ((janma_nak_num * 4) + transit_nak_num) % 9
        if vahan_rem == 0: vahan_rem = 9
        vahan_info = t["vahan_details"].get(vahan_rem, t["vahan_details"][9])
        
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
        
        with st.expander(t["expander_title"]):
            st.write(f"{t['health_head']} {tara_data['H']} *(Shani Vahan: {vahan_info['H']})*")
            st.write(f"{t['career_head']} {tara_data['C']} *(Shani Vahan: {vahan_info['C']})*")
            st.write(f"{t['finance_head']} {tara_data['F']} *(Shani Vahan: {vahan_info['F']})*")
            st.write(f"{t['mindset_head']} {tara_data['M']} *(Shani Vahan: {vahan_info['M']})*")
            st.write(f"{t['rel_head']} {tara_data.get('Rel', '')} *(Shani Vahan: {vahan_info['R']})*")
            
            if tara_data['R']:
                st.error(tara_data['R'])
            if vahan_info.get("Remedy", ""):
                st.warning(vahan_info["Remedy"])

    # ==========================================
    # 7. VIMSHOTTARI DASHA ANALYSIS SECTION
    # ==========================================
    st.divider()
    st.header(t['dasha_title'])
    
    dasha_hierarchy = calculate_vimshottari_dasha(birth_utc_dt, birth_moon_lon, now_utc)
    
    md_lord_key = dasha_hierarchy["MD"]["lord"]
    ad_lord_key = dasha_hierarchy["AD"]["lord"]
    
    md_disp = dasha_names_map[lang_code].get(md_lord_key, md_lord_key)
    ad_disp = dasha_names_map[lang_code].get(ad_lord_key, ad_lord_key)
    pd_disp = dasha_names_map[lang_code].get(dasha_hierarchy["PD"]["lord"], dasha_hierarchy["PD"]["lord"])
    sd_disp = dasha_names_map[lang_code].get(dasha_hierarchy["SD"]["lord"], dasha_hierarchy["SD"]["lord"])
    prd_disp = dasha_names_map[lang_code].get(dasha_hierarchy["PRD"]["lord"], dasha_hierarchy["PRD"]["lord"])
    
    md_s = (dasha_hierarchy["MD"]["start"] + datetime.timedelta(hours=utc_offset_val)).strftime('%d %b %Y')
    md_e = (dasha_hierarchy["MD"]["end"] + datetime.timedelta(hours=utc_offset_val)).strftime('%d %b %Y')
    
    ad_s = (dasha_hierarchy["AD"]["start"] + datetime.timedelta(hours=utc_offset_val)).strftime('%d %b %Y')
    ad_e = (dasha_hierarchy["AD"]["end"] + datetime.timedelta(hours=utc_offset_val)).strftime('%d %b %Y')
    
    pd_s = (dasha_hierarchy["PD"]["start"] + datetime.timedelta(hours=utc_offset_val)).strftime('%d %b %Y')
    pd_e = (dasha_hierarchy["PD"]["end"] + datetime.timedelta(hours=utc_offset_val)).strftime('%d %b %Y')
    
    sd_s = (dasha_hierarchy["SD"]["start"] + datetime.timedelta(hours=utc_offset_val)).strftime('%d %b %Y')
    sd_e = (dasha_hierarchy["SD"]["end"] + datetime.timedelta(hours=utc_offset_val)).strftime('%d %b %Y')
    
    prd_s = (dasha_hierarchy["PRD"]["start"] + datetime.timedelta(hours=utc_offset_val)).strftime('%d %b %Y %I:%M %p')
    prd_e = (dasha_hierarchy["PRD"]["end"] + datetime.timedelta(hours=utc_offset_val)).strftime('%d %b %Y %I:%M %p')

    # Dasha Hierarchy Visual Top Card
    st.markdown(f"""
    <div class="dasha-card">
        <h4>✨ Active Vimshottari Dasha Periods</h4>
        <p style="margin-bottom: 8px; font-size: 0.92rem; color: #451a03;">
            <b>Active Combined Period:</b> <span style="background-color: #fef08a; padding: 3px 10px; border-radius: 6px; font-weight: 800; color: #78350f;">{md_disp} Mahadasha ➔ {ad_disp} Antardasha</span>
        </p>
        <div class="dasha-grid">
            <div class="dasha-item">
                <div class="title">Mahadasha</div>
                <div class="planet">{md_disp}</div>
                <div class="dates">{md_s}<br>to {md_e}</div>
            </div>
            <div class="dasha-item">
                <div class="title">Antardasha</div>
                <div class="planet">{ad_disp}</div>
                <div class="dates">{ad_s}<br>to {ad_e}</div>
            </div>
            <div class="dasha-item">
                <div class="title">Pratyantar</div>
                <div class="planet">{pd_disp}</div>
                <div class="dates">{pd_s}<br>to {pd_e}</div>
            </div>
            <div class="dasha-item">
                <div class="title">Sookshma</div>
                <div class="planet">{sd_disp}</div>
                <div class="dates">{sd_s}<br>to {sd_e}</div>
            </div>
            <div class="dasha-item">
                <div class="title">Prana Dasha</div>
                <div class="planet">{prd_disp}</div>
                <div class="dates">{prd_s}<br>to {prd_e}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Active Dasha Impact Expander
    md_pred = dasha_predictions[lang_code].get(md_lord_key, dasha_predictions["en"]["Ketu"])
    ad_pred = dasha_predictions[lang_code].get(ad_lord_key, dasha_predictions["en"]["Venus"])

    with st.expander(t["dasha_expander_title"]):
        st.write(f"{t['health_head']} {md_pred['H']} *(Antardasha Focus: {ad_pred['H']})*")
        st.write(f"{t['career_head']} {md_pred['C']} *(Antardasha Focus: {ad_pred['C']})*")
        st.write(f"{t['finance_head']} {md_pred['F']} *(Antardasha Focus: {ad_pred['F']})*")
        st.write(f"{t['mindset_head']} {md_pred['M']} *(Antardasha Focus: {ad_pred['M']})*")
        st.write(f"{t['rel_head']} {md_pred['R']} *(Antardasha Focus: {ad_pred['R']})*")
        
        st.info(md_pred["Remedy"])
        st.warning(ad_pred["Remedy"])

# ==========================================
# 8. SHARE APP (Direct Link Payload)
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
