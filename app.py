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

    /* Yellow Glittering Buttons (Both Save & Generate) */
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

lagna_list = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

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

cycles = {
    0: "1st Cycle (Janma Group)",
    1: "2nd Cycle (Anujanma Group)",
    2: "3rd Cycle (Trijanma Group)"
}

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

num_lords = {
    1: "Sun (Surya)",
    2: "Moon (Chandra)",
    3: "Jupiter (Guru)",
    4: "Rahu",
    5: "Mercury (Budh)",
    6: "Venus (Shukra)",
    7: "Ketu",
    8: "Saturn (Shani)",
    9: "Mars (Mangal)"
}

moolank_traits_map = {
    1: "Solar vitality & original leadership — drives you to take bold independent initiatives.",
    2: "Lunar sensitivity & diplomatic harmony — excels in teamwork, empathy, and intuitive decisions.",
    3: "Jupiterian wisdom & expressive growth — fuels creative ideas, optimism, and effective counsel.",
    4: "Rahu's unconventional vision & practical discipline — excels in structured audits and systematic work.",
    5: "Mercurial agility & fast networking — thrives in dynamic environments and quick problem-solving.",
    6: "Venusian harmony & aesthetic balance — focuses on family wellness, design, and relationship bonding.",
    7: "Ketu's contemplative research & deep intuition — thrives in analytical study and quiet observation.",
    8: "Saturnian resilience & financial execution — commands authoritative responsibility and solid planning.",
    9: "Martial stamina & courageous completion — drives completion of pending goals and passionate action."
}

lucky_numbers_map = {
    1: "1, 2, 3, 9",
    2: "1, 2, 5",
    3: "1, 2, 3, 9",
    4: "1, 4, 5, 6, 7",
    5: "1, 5, 6",
    6: "1, 5, 6, 7",
    7: "1, 4, 7",
    8: "3, 5, 6, 8",
    9: "1, 2, 3, 9"
}

personal_day_meanings_en = {
    1: "Good day to launch new goals, lead projects, and pitch ideas. Avoid hesitating or relying on others.",
    2: "Good day for teamwork, smooth negotiations, and active listening. Avoid emotional impulse buying or arguments.",
    3: "Good day for meetings, creative tasks, and social networking. Avoid overpromising or heavy overindulgence.",
    4: "Good day to organize, complete routine audits, and clean your workspace. Avoid taking shortcuts or making speculative bets.",
    5: "Good day for fast networking, sales pitches, and quick decisions. Avoid being rigid or losing focus.",
    6: "Good day for family discussions, relationship bonding, and self-care. Avoid unnecessary arguments or neglecting home ties.",
    7: "Good day for quiet study, deep research, and mental rest. Avoid launching major public changes or making hasty big decisions.",
    8: "Good day for financial planning, debt management, and structured work. Avoid being overly stern or rushing big tasks.",
    9: "Good day to finish pending backlogs, clear clutter, and forgive old grievances. Avoid launching brand-new long-term commitments."
}

personal_day_meanings_hi = {
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

personal_day_aspects_en = {
    1: {"H": "Solar vitality is active; boost cardiovascular health and physical posture.", "C": "Leadership initiative; drive pending pitches.", "F": "Favorable for launching new revenue ideas.", "M": "Focused, independent, and decisive.", "R": "Lead relationships with warmth; avoid ego clashes.", "Remedy": ""},
    2: {"H": "Lunar influence; maintain fluid intake and emotional peace.", "C": "Collaborative diplomatic negotiations succeed.", "F": "Avoid emotional impulse purchases.", "M": "Empathetic, sensitive, and observant.", "R": "Deepen romantic bonding through sincere listening.", "Remedy": "✨ Numerology Tip: Drink water from a silver cup or practice quiet breathing for calm focus."},
    3: {"H": "Expansive energy; avoid overindulgent heavy meals.", "C": "Excellent for presentations, pitching, and teaching.", "F": "Good day for long-term growth investments.", "M": "Optimistic, joyful, and expressive.", "R": "Warm social gatherings and joyful family exchanges.", "Remedy": ""},
    4: {"H": "Rahu frequency; guard against sudden nervous fatigue.", "C": "Focus on routine audits; strictly avoid shortcut risks.", "F": "Maintain strict budgeting; avoid speculative trading.", "M": "Analytical, grounded, but prone to restlessness.", "R": "Be direct yet polite to prevent sudden miscommunications.", "Remedy": "✨ Numerology Remedy (Day 4): Keep your workspace tidy and chant 'Om Raam Rahave Namah' to calm mental flutter."},
    5: {"H": "Mercurial pace; take short walking breaks to release tension.", "C": "Fast progress in sales, digital work, and networking.", "F": "Opportunities for quick fluid transactions.", "M": "Quick-witted, versatile, and curious.", "R": "Fun, lively outings and spontaneous communication.", "Remedy": ""},
    6: {"H": "Venusian alignment; focus on skin, hydration, and relaxation.", "C": "Ideal for design, client relations, and aesthetic projects.", "F": "Favorable for family assets and aesthetic comforts.", "M": "Harmonious, peaceful, and balanced.", "R": "Heartwarming romantic closeness and family peace.", "Remedy": ""},
    7: {"H": "Ketu vibration; prioritize quiet rest and digestive ease.", "C": "Best for research, auditing, and deep technical study.", "F": "Review finances silently; do not execute hasty transfers.", "M": "Contemplative, highly intuitive, and quiet.", "R": "Seek intimate, meaningful talks over noisy crowds.", "Remedy": "✨ Numerology Remedy (Day 7): Spend 10 minutes in quiet meditation or chant 'Om Kem Ketave Namah'."},
    8: {"H": "Saturnian discipline; care for joint health and posture.", "C": "Command authoritative tasks and structured workloads.", "F": "Focus on debt management and solid long-term assets.", "M": "Pragmatic, cautious, and resilient.", "R": "Honor commitments faithfully; avoid being overly stern.", "Remedy": "✨ Numerology Remedy (Day 8): Light a sesame oil lamp or chant 'Om Sham Shanayscharaya Namah' for smooth progress."},
    9: {"H": "Martial energy; high stamina—avoid hasty movements.", "C": "Clear backlogs and finalize closing contracts.", "F": "Settle pending bills and clear outstanding dues.", "M": "Passionate, courageous, and ready for completion.", "R": "Practice patience, forgiveness, and let go of past grievances.", "Remedy": "✨ Numerology Remedy (Day 9): Channel high drive into physical exercise or chant 'Om Bhaumaya Namah'."}
}

tara_details_en = {
    0: {
        "status": "Janma (1st Tara - Self) ⚪",
        "H": "Focus on self-care and balanced light diet. Body and digestion may feel sensitive today.",
        "C": "Maintain daily routine tasks. Avoid launching major new impulsive projects.",
        "F": "Keep finances stable. Avoid hasty or emotional buying.",
        "M": "Self-reflective, quiet, and calm mindset.",
        "Rel": "Maintain emotional balance in personal relationships; avoid demanding too much from loved ones.",
        "R": ""
    },
    1: {
        "status": "Sampat (2nd Tara - Wealth) 🟢",
        "H": "Energy levels are high. Great day for physical recovery and fitness.",
        "C": "Excellent day for professional growth, key business meetings, and new opportunities.",
        "F": "Highly favorable day for wealth accumulation, investments, and financial gains.",
        "M": "Positive, confident, and optimistic mindset.",
        "Rel": "Wonderful day for bonding, expressing appreciation, and deepening mutual trust in relationships.",
        "R": ""
    },
    2: {
        "status": "Vipat (3rd Tara - Obstacles) 🔴",
        "H": "Vulnerable day physically. Avoid excessive physical strain or high-risk activities.",
        "C": "Sudden hurdles or unexpected delays in projects may arise. Exercise patience.",
        "F": "Strictly avoid speculative investments, trading, or lending money today.",
        "M": "Prone to sudden anxiety, restlessness, or stress.",
        "Rel": "Potential for minor friction or misunderstandings; practice patience and gentle listening.",
        "R": "🛡️ Vedic Remedy (Vipat): Recite or listen to Hanuman Chalisa. Offer fresh water to green plants or birds. Postpone major risky commitments."
    },
    3: {
        "status": "Kshema (4th Tara - Wellbeing) 🟢",
        "H": "Good day for general wellbeing, healing, and physical comfort.",
        "C": "Smooth operations, effective teamwork, and steady ongoing progress.",
        "F": "Financial security and safe transactions are favored.",
        "M": "Peaceful, content, and emotionally balanced.",
        "Rel": "Warm, comforting interactions; excellent time for quality family moments and social harmony.",
        "R": ""
    },
    4: {
        "status": "Pratyari (5th Tara - Opposition) 🔴",
        "H": "Mental friction may manifest as fatigue. Ensure adequate sleep and hydration.",
        "C": "Friction or misunderstandings with colleagues or authority figures are possible.",
        "F": "Unexpected expenses or delayed payments can disrupt your budget.",
        "M": "Easily irritated or defensive. Practice mindfulness.",
        "Rel": "High chance of defensive reactions; practice silence (*Mouna*) during heated moments and give space.",
        "R": "🛡️ Vedic Remedy (Pratyari): Practice silence (Mouna) during arguments. Chant 'Om Sham Shanayscharaya Namah' or donate black sesame/oil."
    },
    5: {
        "status": "Sadhaka (6th Tara - Success) 🟢",
        "H": "Strong vitality and quick overcoming of minor health complaints.",
        "C": "Great achievements, breakthroughs, and successful completion of difficult goals.",
        "F": "Profitable ventures and realization of long-term financial plans.",
        "M": "Determined, highly focused, and intellectually sharp.",
        "Rel": "Achieve strong mutual understanding, resolve past issues, and build meaningful connections.",
        "R": ""
    },
    6: {
        "status": "Vadha (7th Tara - Danger) 🔴",
        "H": "Higher risk of fatigue, minor injury, or illness. Exercise caution while commuting.",
        "C": "Major blockages or opposition. Do not schedule crucial confrontations today.",
        "F": "Protect your assets. Avoid high-stakes financial commitments.",
        "M": "Overwhelmed, fearful, or defensive.",
        "Rel": "Sensitive day for personal ties; avoid major confrontations or bringing up past grievances.",
        "R": "🛡️ Vedic Remedy (Vadha): Chant Mahamrityunjaya Mantra or 'Om Namah Shivaya'. Offer water or milk to Lord Shiva."
    },
    7: {
        "status": "Mitra (8th Tara - Friend) 🟢",
        "H": "Improving health and supportive physical energy.",
        "C": "Expect cooperation from peers and joint success in group tasks.",
        "F": "Collaborative financial gains and steady wealth.",
        "M": "Happy, sociable, and emotionally supported.",
        "Rel": "Very supportive and friendly vibration; great day for social gatherings and romantic warmth.",
        "R": ""
    },
    8: {
        "status": "Ati-Mitra (9th Tara - Best Friend) 🟢🟢",
        "H": "Excellent physical vitality and vibrant energy.",
        "C": "High growth, ultimate success, and public recognition for your efforts.",
        "F": "Windfalls, bonuses, or highly favorable financial news.",
        "M": "Joyous, spiritually uplifted, and deeply fulfilled.",
        "Rel": "Deep emotional joy, heartwarming harmony, and full support from family and partners.",
        "R": ""
    }
}

translations = {
    "en": {
        "intro_title": "Unlocking the Wisdom of Vedic Astrology",
        "intro_desc": "In Vedic astrology and numerology, the Moon's transit through the 27 Nakshatras and daily numerical vibrations create a unique energy pattern relative to your birth profile. This app provides accurate, astronomical, and numerological insights into your health, career, finance, mindset, and relationships.",
        "profile_title": "👤 Birth Profile",
        "horoscope_title": "7-Day Horoscope Prediction & Life Guidance",
        "search_prompt": "🌍 Birth Place Name or 6-Digit Pincode",
        "generate_btn": "Generate Horoscope & Predictions",
        "save_btn": "Save Profile",
        "expander_title": "✨ Click here to see the Prediction & Life Guidance ✨",
        "tara": tara_details_en
    },
    "hi": {
        "intro_title": "वैदिक ज्योतिष और अंकशास्त्र का ज्ञान",
        "intro_desc": "वैदिक ज्योतिष और अंकशास्त्र में, 27 नक्षत्रों में चंद्रमा का गोचर और दैनिक अंक कंपन आपके जन्म विवरण के सापेक्ष एक अनूठा ऊर्जा पैटर्न बनाते हैं। यह ऐप स्वास्थ्य, करियर, वित्त, मानसिकता और संबंधों में सटीक अंतर्दृष्टि प्रदान करता है।",
        "profile_title": "👤 जन्म विवरण",
        "horoscope_title": "7-दिवसीय राशिफल भविष्यवाणी और जीवन मार्गदर्शन",
        "search_prompt": "🌍 जन्म स्थान का नाम या 6-अंकीय पिनकोड",
        "generate_btn": "राशिफल और भविष्यवाणियां उत्पन्न करें",
        "save_btn": "प्रोफाइल सहेजें",
        "expander_title": "✨ दैनिक भविष्यवाणी और जीवन मार्गदर्शन देखने के लिए यहां क्लिक करें ✨",
        "tara": tara_details_en 
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
if 'profile_saved' not in st.session_state:
    st.session_state['profile_saved'] = 'saved' in query_params

st.title("🌙 Navtara Pulse")

# Purple Highlighted Language Selector
lang_options = {"en": "English", "hi": "हिन्दी (Hindi)", "mr": "मराठी (Marathi)", "gu": "ગુજરાती (Gujarati)"}
selected_lang_name = st.selectbox("🌐 Select Language", list(lang_options.values()), index=0)
lang_code = [k for k, v in lang_options.items() if v == selected_lang_name][0]
t = translations[lang_code]

st.markdown(f"### {t['intro_title']}")
st.write(t['intro_desc'])
st.divider()

# ==========================================
# 5. UNIFIED USER PROFILE WINDOW
# ==========================================
st.header(t['profile_title'])

default_name = query_params.get('n', '')
default_date = datetime.datetime.strptime(query_params.get('d', '1995-01-01'), '%Y-%m-%d').date()
default_h = int(query_params.get('h', '0'))
default_m = int(query_params.get('m', '0'))
default_place = query_params.get('p', '')

col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("Name", value=default_name, placeholder="e.g. Rahul Sharma")
    birth_date = st.date_input("Date of Birth", min_value=datetime.date(1925, 1, 1), max_value=datetime.date.today(), value=default_date)

with col2:
    st.write("Time of Birth (24-Hour)")
    tc1, tc2 = st.columns(2)
    with tc1: 
        birth_hour = st.selectbox("HH", [f"{i:02d}" for i in range(24)], index=default_h)
    with tc2: 
        birth_minute = st.selectbox("MM", [f"{i:02d}" for i in range(60)], index=default_m)

# Unified Single Birth Place Search Box
st.write(t['search_prompt'])
place_query = st.text_input(
    "Search Location", 
    value=default_place, 
    placeholder="e.g. Ujjain, Mumbai, London, or 456001",
    label_visibility="collapsed"
)

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
birth_local_dt = datetime.datetime.combine(birth_date, datetime.time(int(birth_hour), int(birth_minute)))
birth_utc_dt = birth_local_dt - datetime.timedelta(hours=utc_offset_val)
auto_janma_idx, auto_rashi_idx, auto_lagna_idx = get_moon_and_kundli_indices(birth_utc_dt, place_obj_data)

# Plain Birth Place Badge
if selected_place_display:
    st.markdown(f"<div class='verified-badge'>📍 Birth Place: {selected_place_display}</div>", unsafe_allow_html=True)

# Both Save Profile & Generate Horoscope Buttons styled with primary glittering yellow
btn_col1, btn_col2 = st.columns([1, 1])
with btn_col1:
    save_clicked = st.button("💾 Save Profile", type="primary", use_container_width=True)

with btn_col2:
    generate_clicked = st.button(f"🔮 {t['generate_btn']}", type="primary", use_container_width=True)

if save_clicked or generate_clicked:
    if len(place_query) < 3:
        st.error("⚠️ Please enter a valid Birth Place or Pincode to save your profile.")
    else:
        st.query_params['n'] = user_name
        st.query_params['d'] = str(birth_date)
        st.query_params['h'] = str(int(birth_hour))
        st.query_params['m'] = str(int(birth_minute))
        st.query_params['p'] = selected_place_display
        st.query_params['saved'] = 'true'
        st.session_state['profile_saved'] = True
        st.toast("✅ Profile saved successfully!", icon="🎉")

# ==========================================
# 6. CONSOLIDATED PROFILE & HOROSCOPE
# ==========================================
if st.session_state.get('profile_saved'):
    st.divider()
    
    # 1. Fixed Astrological Kundli Parameters
    janma_nakshatra_name = nakshatra_list[auto_janma_idx]
    janma_lord = nakshatra_lords[auto_janma_idx]
    janma_rashi_name = rashi_list[auto_rashi_idx]
    janma_lagna_name = lagna_list[auto_lagna_idx]
    janma_traits = nakshatra_traits_map.get(janma_nakshatra_name, "Balanced vitality, strong intuition, and steady growth.")
    
    # 2. Vedic Numerology Profile Calculation
    moolank = reduce_to_single_digit(birth_date.day)
    bhagyank = reduce_to_single_digit(birth_date.day + birth_date.month + birth_date.year)
    moolank_lord = num_lords.get(moolank, "")
    bhagyank_lord = num_lords.get(bhagyank, "")
    moolank_trait = moolank_traits_map.get(moolank, "Leadership and steady focus.")
    bhagyank_trait = moolank_traits_map.get(bhagyank, "Long-term purpose and natural path.")
    lucky_nums = lucky_numbers_map.get(moolank, "1, 3, 5, 6")
    
    profile_display_name = user_name.strip() if user_name.strip() else "User"
    
    # Single Consolidated Light Green Profile Box
    st.markdown(f"""
    <div style="background-color: #f0fdf4; color: #166534; padding: 18px 20px; border-radius: 12px; border: 1.5px solid #86efac; margin-top: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
        <h4 style="color: #15803d; margin-top: 0; margin-bottom: 12px; font-weight: 800; font-size: 1.18rem; display: flex; align-items: center; gap: 8px;">
            🌿 {profile_display_name}'s Profile
        </h4>
        <div style="font-size: 0.94rem; color: #14532d; line-height: 1.6;">
            <p style="margin-bottom: 6px;">
                ⭐ <b>Janma Nakshatra:</b> {janma_nakshatra_name} &nbsp;|&nbsp; 
                <b>Nakshatra Lord:</b> {janma_lord} &nbsp;|&nbsp; 
                <b>Rashi:</b> {janma_rashi_name} &nbsp;|&nbsp; 
                <b>Lagna:</b> {janma_lagna_name}
            </p>
            <p style="margin-bottom: 12px; padding-left: 10px; border-left: 3.5px solid #22c55e; color: #166534; font-size: 0.91rem;">
                ✨ <b>Nakshatra Traits:</b> {janma_traits}
            </p>
            <hr style="border: 0; border-top: 1px dashed #a7f3d0; margin: 10px 0;">
            <p style="margin-bottom: 6px; margin-top: 10px;">
                🔢 <b>Numerology Profile:</b> Moolank (Driver): <b>{moolank} ({moolank_lord})</b> &nbsp;|&nbsp; Bhagyank (Conductor): <b>{bhagyank} ({bhagyank_lord})</b> &nbsp;|&nbsp; Lucky Numbers: <b>{lucky_nums}</b>
            </p>
            <p style="margin-bottom: 4px; padding-left: 10px; border-left: 3.5px solid #22c55e; color: #166534; font-size: 0.91rem;">
                💡 <b>Numerology Traits:</b> Moolank {moolank} brings {moolank_trait} Bhagyank {bhagyank} emphasizes {bhagyank_trait}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Save & Install Mobile Instructions Banner
    st.markdown("""
    <div style="background-color: #1e1b4b; color: #ffffff; padding: 16px; border-radius: 12px; margin-top: 10px; margin-bottom: 20px;">
        <h5 style="color: #fbbf24; margin-top: 0; font-size: 1.05rem; font-weight: bold;">📱 Save & Install for 1-Click Mobile Access</h5>
        <p style="font-size: 0.9rem; color: #e2e8f0; margin-bottom: 8px;">
            Your birth profile details have been saved to this custom URL. To open this horoscope anytime without re-entering details:
        </p>
        <ul style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 0; padding-left: 20px;">
            <li><b>iPhone (Safari):</b> Tap the <b>Share</b> icon at the bottom ➔ select <b>"Add to Home Screen"</b>.</li>
            <li><b>Android (Chrome):</b> Tap the <b>three dots (⋮)</b> at top-right ➔ select <b>"Add to Home screen"</b> or <b>"Install App"</b>.</li>
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
        tara_badge_name = navtara_names[tara_index]
        transit_nak_name = nakshatra_list[transit["nak_index"]]
        transit_nak_lord = nakshatra_lords[transit["nak_index"]]
        
        start_str = transit["start"].strftime('%a, %d %b %I:%M %p')
        end_str = transit["end"].strftime('%a, %d %b %I:%M %p')
        
        current_pill = "<span class='current-badge'>⚡ Active Now</span>" if transit.get("is_current") else ""
        
        # Calculate Daily Personal Day Number for the transit date
        t_date = transit["start"].date()
        p_day = reduce_to_single_digit(birth_date.day + birth_date.month + t_date.day + t_date.month + t_date.year)
        p_lord = num_lords.get(p_day, "")
        p_desc = (personal_day_meanings_hi if lang_code in ["hi", "mr", "gu"] else personal_day_meanings_en).get(p_day, "")
        num_aspects = personal_day_aspects_en.get(p_day, {})
        
        # Upper Portion: Day Card with Navtara Transit & Numerology Vibration
        st.markdown(f"""
        <div class="transit-card">
            <h5><span>🕒 {start_str} ➔ {end_str}</span> {current_pill}</h5>
            <p><b>🌙 Navtara Transit:</b> Status: <span class='status-badge'>{tara_badge_name}</span> | <b>Moon Nakshatra:</b> {transit_nak_name} (<b>Lord:</b> {transit_nak_lord})</p>
            <p style="margin-top: 6px; padding-top: 6px; border-top: 1px dashed #bae6fd;">
                🔢 <b>Numerology Vibration:</b> Personal Day <b>{p_day} ({p_lord})</b> — {p_desc}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Attached Lower Portion: Eye-Catching Yellow Glittering Expander Bar
        with st.expander(t["expander_title"]):
            st.write(f"🩺 **Health:** {tara_data['H']} *(Numerology Focus: {num_aspects.get('H', '')})*")
            st.write(f"💼 **Career:** {tara_data['C']} *(Numerology Focus: {num_aspects.get('C', '')})*")
            st.write(f"💰 **Finance:** {tara_data['F']} *(Numerology Focus: {num_aspects.get('F', '')})*")
            st.write(f"🧘 **Mindset:** {tara_data['M']} *(Numerology Focus: {num_aspects.get('M', '')})*")
            st.write(f"❤️ **Relationships:** {tara_data.get('Rel', '')} *(Numerology Focus: {num_aspects.get('R', '')})*")
            
            # Show Navtara and/or Numerology Remedies if applicable
            if tara_data['R']:
                st.error(tara_data['R'])
            if num_aspects.get("Remedy", ""):
                st.info(num_aspects["Remedy"])

# ==========================================
# 7. SHARE APP (Direct Link Payload)
# ==========================================
st.divider()
st.subheader("🔗 Share Navtara Pulse")
app_url = "https://navtara-pulse.streamlit.app"
share_text = urllib.parse.quote(f"Check out Navtara Pulse - Precision Moon Transit: {app_url}")

sc1, sc2, sc3 = st.columns(3)
with sc1: 
    st.link_button("💬 WhatsApp", f"https://api.whatsapp.com/send?text={share_text}", use_container_width=True)
with sc2: 
    st.link_button("✉️ Email", f"mailto:?subject=Navtara Pulse&body={share_text}", use_container_width=True)
with sc3: 
    st.link_button("✈️ Telegram", f"https://t.me/share/url?url={app_url}&text=Check out Navtara Pulse", use_container_width=True)
