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
# 2. CONSTANTS & LOCALIZATION (UPDATED DASHA NARRATIVES)
# ==========================================
dasha_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
dasha_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]

dasha_names_map = {
    "en": {"Ketu": "Ketu", "Venus": "Venus (Shukra)", "Sun": "Sun (Surya)", "Moon": "Moon (Chandra)", "Mars": "Mars (Mangal)", "Rahu": "Rahu", "Jupiter": "Jupiter (Guru)", "Saturn": "Saturn (Shani)", "Mercury": "Mercury (Budh)"},
    "hi": {"Ketu": "केतु", "Venus": "शुक्र", "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Rahu": "राहु", "Jupiter": "गुरु", "Saturn": "शनि", "Mercury": "बुध"},
    "mr": {"Ketu": "केतू", "Venus": "शुक्र", "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगळ", "Rahu": "राहु", "Jupiter": "गुरु", "Saturn": "शनि", "Mercury": "बुध"},
    "gu": {"Ketu": "કેતુ", "Venus": "શુક્ર", "Sun": "સૂર્ય", "Moon": "ચંદ્ર", "Mars": "મંગળ", "Rahu": "રાહુ", "Jupiter": "ગુરુ", "Saturn": "શનિ", "Mercury": "બુધ"}
}

dasha_narratives = {
    "en": {
        "Ketu": {
            "text": "The energy of Ketu brings deep introspection, technical research drive, and spiritual detachment. During this period, quiet concentration and analytical focus yield significant breakthroughs. External distractions recede, allowing you to master complex technical tasks, investigate underlying truths, and restructure your priorities. It requires maintaining calm, avoiding speculative financial gambles, and cultivating inner peace.",
            "remedy": "🕉️ Ketu Remedy: Feed stray dogs with bread/roti daily and recite 'Om Kem Ketave Namah'."
        },
        "Venus": {
            "text": "The influence of Venus unfolds a period of creative vitality, harmony, and material comfort. It enhances your diplomatic influence, design vision, and client negotiations, opening avenues for financial expansion, luxury comfort, and asset growth. This phase fosters heartwarming romantic closeness, social appreciation, and deep personal fulfillment.",
            "remedy": "🌸 Venus Remedy: Offer white flowers to Goddess Lakshmi and donate ghee or rice on Fridays."
        },
        "Sun": {
            "text": "The solar period elevates leadership authority, self-dignity, and career prominence. Recognition from senior officials and institutional bodies highlights this phase, driving bold initiative and administrative breakthroughs. It inspires courageous decision-making and strong capital growth while encouraging humility and steady physical stamina.",
            "remedy": "☀️ Sun Remedy: Offer fresh water (Arghya) to the rising Sun daily and recite Aditya Hrudayam."
        },
        "Moon": {
            "text": "The Moon brings fluid vitality, heightened intuition, and effective public networking. It supports prosperous deal flow, empathetic communication, and marketing success. This phase nurtures domestic peace, deep emotional bonding, and financial liquidity, encouraging a balanced, observant, and creative approach to life.",
            "remedy": "🌙 Moon Remedy: Drink water from a silver cup and respect mother or elder matriarchs."
        },
        "Mars": {
            "text": "The martial influence ignites courageous execution, muscular stamina, and competitive victories. It provides the determination needed to complete long-pending goals, master real estate or technical projects, and overcome obstacles. Success comes through active drive, strategic discipline, and patient persistence.",
            "remedy": "🔥 Mars Remedy: Recite Hanuman Chalisa daily and offer jaggery or red lentils in charity."
        },
        "Rahu": {
            "text": "The period of Rahu opens doors to unconventional expansion, digital innovation, and global opportunities. It inspires ambitious vision, creative problem-solving, and high yields. Navigating this energy effectively requires disciplined financial audits, clear transparent communication, and maintaining emotional grounding.",
            "remedy": "🪐 Rahu Remedy: Keep your workspace clean and chant 'Om Raam Rahave Namah' in the evening."
        },
        "Jupiter": {
            "text": "Jupiter brings wisdom, optimism, institutional respect, and substantial expansion. It favors long-term wealth security, high-level counsel, spiritual growth, and generous support from mentors and family. This phase creates strong social goodwill, educational achievements, and noble guidance.",
            "remedy": "💛 Jupiter Remedy: Apply yellow sandalwood tilak on forehead and respect gurus or teachers."
        },
        "Saturn": {
            "text": "Saturn instills pragmatic resilience, structured operational discipline, and enduring achievement. It establishes solid capital foundations, debt management, and authoritative responsibility. Honest, patient, and dedicated effort yields long-lasting progress and high organizational respect.",
            "remedy": "⚖️ Saturn Remedy: Light a sesame oil lamp on Saturdays and serve aged workers or laborers."
        },
        "Mercury": {
            "text": "Mercury sharpens commercial agility, analytical precision, and fast networking. It accelerates sales pitches, intellectual tasks, and transaction gains, creating versatile opportunities and lively social harmony. Communication flows smoothly, making it ideal for strategic deals and learning.",
            "remedy": "💚 Mercury Remedy: Feed green fodder to cows and chant 'Om Budhaya Namah'."
        }
    },
    "hi": {
        "Ketu": {
            "text": "केतु की दशा गहन आत्मनिरीक्षण, तकनीकी शोध और आध्यात्मिक शांति लाती है। इस अवधि में शांत ध्यान और विश्लेषणात्मक अध्ययन से बड़ी सफलताएं मिलती हैं। बाहरी भटकाव कम होते हैं, जिससे आप जटिल कार्यों और अनुसंधान में निपुणता प्राप्त करते हैं। यह समय शांत रहने, वित्तीय सट्टेबाजी से बचने और आंतरिक शांति बनाए रखने का है।",
            "remedy": "🕉️ केतु उपाय: आवारा कुत्तों को रोटी खिलाएं और 'ॐ कें केतवे नमः' का जाप करें।"
        },
        "Venus": {
            "text": "शुक्र का प्रभाव जीवन में रचनात्मक ऊर्जा, सौहार्द और सुख-सुविधाओं का विस्तार करता है। यह आपके सौंदर्यबोध, कूटनीतिक प्रभाव और व्यापारिक बातचीत को बढ़ावा देता है, जिससे वित्तीय समृद्धि, संपत्ति वृद्धि और पारिवारिक प्रसन्नता प्राप्त होती है।",
            "remedy": "🌸 शुक्र उपाय: देवी लक्ष्मी को सफेद फूल अर्पित करें और शुक्रवार को घी या चावल दान करें।"
        },
        "Sun": {
            "text": "सूर्य की महादशा नेतृत्व अधिकार, प्रतिष्ठा और करियर में पदोन्नति प्रदान करती है। वरिष्ठ अधिकारियों और संस्थागत कार्यों से मान्यता मिलती है। यह समय साहसी फैसलों, पूंजी वृद्धि और आत्मविश्वास के साथ आगे बढ़ने की प्रेरणा देता है।",
            "remedy": "☀️ सूर्य उपाय: सूर्यदेव को तांबे के पात्र से जल अर्पित करें और नित्य आदित्य हृदय स्तोत्र का पाठ करें।"
        },
        "Moon": {
            "text": "चंद्रमा की स्थिति सहज बोध, जनसंपर्क और भावनात्मक संतुलन को मजबूत करती है। यह व्यापारिक नेटवर्किंग, वित्तीय तरलता और पारिवारिक शांति को बढ़ावा देती है। निर्णय क्षमता में स्पष्टता और रचनात्मकता बनी रहती है।",
            "remedy": "🌙 चंद्र उपाय: चांदी के बर्तन से पानी पीएं और माता का सम्मान करें।"
        },
        "Mars": {
            "text": "मंगल का प्रभाव अदम्य साहस, शारीरिक क्षमता और प्रतिस्पर्धी जीत प्रदान करता है। यह रुके हुए कार्यों को पूरा करने, रियल एस्टेट सौदों और साहसी निर्णय लेने के लिए सर्वोत्तम समय है। धैर्य और निरंतर प्रयास से बड़ी सफलता मिलती है।",
            "remedy": "🔥 मंगल उपाय: प्रतिदिन हनुमान चालीसा का पाठ करें और गुड़ या लाल मसूर दान करें।"
        },
        "Rahu": {
            "text": "राहु की अवधि डिजिटल उन्नति, नए अवसरों और वैश्विक विस्तार का मार्ग प्रशस्त करती है। यह महत्वाकांक्षी दूरदृष्टि देती है। इस ऊर्जा का सर्वोत्तम लाभ उठाने के लिए अनुशासित वित्तीय प्रबंधन और स्पष्ट बातचीत बनाए रखना आवश्यक है।",
            "remedy": "🪐 राहु उपाय: कार्यस्थल साफ रखें और शाम को 'ॐ रां राहवे नमः' का जाप करें।"
        },
        "Jupiter": {
            "text": "गुरु की दशा ज्ञान, आशावाद और संस्थागत सम्मान लाती है। यह दीर्घकालिक वित्तीय सुरक्षा, सही मार्गदर्शन और आध्यात्मिक उन्नति के लिए अत्यंत शुभ फलदायी है। वरिष्ठों और परिवार का पूर्ण सहयोग प्राप्त होता है।",
            "remedy": "💛 गुरु उपाय: मस्तक पर केसर या हल्दी का तिलक लगाएं और गुरुओं का सम्मान करें।"
        },
        "Saturn": {
            "text": "शनि का प्रभाव व्यावहारिक अनुशासन, ठोस वित्तीय प्रबंधन और दीर्घकालिक सफलता प्रदान करता है। यह कड़ी मेहनत, धैर्य और जिम्मेदारियों के निष्पादन से स्थायी प्रगति देता है। ऋण प्रबंधन और बचत मजबूत होती है।",
            "remedy": "⚖️ शनि उपाय: शनिवार को तिल के तेल का दीपक जलाएं और बुजुर्गों या श्रमिकों की सेवा करें।"
        },
        "Mercury": {
            "text": "बुध की अवधि बौद्धिक तीक्ष्णता, व्यापारिक सफलता और त्वरित नेटवर्किंग प्रदान करती है। यह विश्लेषणात्मक कार्यों, बिक्री सौदों और प्रभावी संचार में तेजी से लाभ देती है। बहुमुखी अवसरों का मार्ग प्रशस्त होता है।",
            "remedy": "💚 बुध उपाय: गायों को हरा चारा खिलाएं और 'ॐ बुधाय नमः' का जाप करें।"
        }
    }
}
dasha_narratives["mr"] = dasha_narratives["hi"]
dasha_narratives["gu"] = dasha_narratives["hi"]


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
# 3. HELPER & ASTRONOMY FUNCTIONS (GEOCENTRIC MOON FIX)
# ==========================================
def get_moon_and_kundli_indices(dt_utc, place_obj=None):
    """Calculates exact Sidereal Geocentric Moon Lon, Nakshatra, Rashi, and Lagna indices using PyEphem + Lahiri Ayanamsa."""
    # Geocentric Moon for accurate Nakshatra Lon & Dasha calculations (removes topocentric parallax shift)
    moon_geo = ephem.Moon(dt_utc)
    ecl = ephem.Ecliptic(moon_geo)
    
    year = dt_utc.year + (dt_utc.month - 1) / 12.0
    ayanamsa = 23.85306 + (year - 2000.0) * 0.01397
    
    sidereal_moon_lon = (math.degrees(ecl.lon) - ayanamsa) % 360
    nakshatra_index = int(sidereal_moon_lon / 13.333333333333334) % 27
    rashi_index = int(sidereal_moon_lon / 30.0) % 12
    
    # Topocentric Observer for Ascendant (Lagna) calculation only
    observer = ephem.Observer()
    observer.date = ephem.date(dt_utc)
    
    if isinstance(place_obj, dict):
        lat = float(place_obj.get('lat', 0))
        lon = float(place_obj.get('lon', 0))
        if lat != 0 or lon != 0:
            observer.lat = str(lat)
            observer.lon = str(lon)
            
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

def calculate_vimshottari_dasha(birth_utc_dt, moon_lon_deg, target_utc_dt):
    """Calculates exact 5-level Vimshottari Dasha hierarchy for a target date."""
    nak_span = 13.333333333333334
    nak_idx = int(moon_lon_deg / nak_span) % 27
    lord_idx = nak_idx % 9
    
    traversed = (moon_lon_deg % nak_span) / nak_span
    
    YEAR_DAYS = 365.242189
    
    # Balance of first Mahadasha at birth
    consumed_first_md_days = dasha_years[lord_idx] * traversed * YEAR_DAYS
    first_md_start = birth_utc_dt - datetime.timedelta(days=consumed_first_md_days)
    
    curr_start = first_md_start
    active_md_idx = lord_idx
    
    # 1. Mahadasha Loop
    for _ in range(30):
        dur_days = dasha_years[active_md_idx] * YEAR_DAYS
        curr_end = curr_start + datetime.timedelta(days=dur_days)
        if curr_start <= target_utc_dt < curr_end:
            break
        curr_start = curr_end
        active_md_idx = (active_md_idx + 1) % 9
        
    md_start, md_end, md_lord = curr_start, curr_end, dasha_order[active_md_idx]
    
    # 2. Antardasha Loop
    ad_curr_start = md_start
    active_ad_idx = active_md_idx
    for _ in range(9):
        ad_dur_days = (dasha_years[active_md_idx] * dasha_years[active_ad_idx] / 120.0) * YEAR_DAYS
        ad_curr_end = ad_curr_start + datetime.timedelta(days=ad_dur_days)
        if ad_curr_start <= target_utc_dt < ad_curr_end:
            break
        ad_curr_start = ad_curr_end
        active_ad_idx = (active_ad_idx + 1) % 9
        
    ad_start, ad_end, ad_lord = ad_curr_start, ad_curr_end, dasha_order[active_ad_idx]
    
    # 3. Pratyantardasha Loop
    pd_curr_start = ad_start
    active_pd_idx = active_ad_idx
    ad_total_days = (dasha_years[active_md_idx] * dasha_years[active_ad_idx] / 120.0) * YEAR_DAYS
    for _ in range(9):
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
    for _ in range(9):
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
    for _ in range(9):
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
    # 7. VIMSHOTTARI DASHA ANALYSIS SECTION (PARAGRAPH PREDICTIONS)
    # ==========================================
    st.divider()
    st.header(t.get('dasha_title', '🔮 Vimshottari Dasha Analysis & Life Guidance'))
    
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
        <h4>✨ Active Vimshottari Dasha Hierarchy</h4>
        <p style="margin-bottom: 8px; font-size: 0.92rem; color: #451a03;">
            <b>Active Period:</b> <span style="background-color: #fef08a; padding: 3px 10px; border-radius: 6px; font-weight: 800; color: #78350f;">{md_disp} Mahadasha ➔ {ad_disp} Antardasha</span>
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

    # Active Dasha Impact Expander (Narrative Paragraph Predictions without headings)
    md_narrative = dasha_narratives[lang_code].get(md_lord_key, dasha_narratives["en"]["Ketu"])
    ad_narrative = dasha_narratives[lang_code].get(ad_lord_key, dasha_narratives["en"]["Venus"])

    expander_title_dasha = t.get("dasha_expander_title", "✨ Click here for Active Dasha Predictions & Guidance ✨")
    with st.expander(expander_title_dasha):
        st.markdown(f"### 🪐 Active Mahadasha Narrative ({md_disp})")
        st.write(md_narrative["text"])
        
        st.markdown(f"### 🌙 Active Antardasha Narrative ({ad_disp})")
        st.write(ad_narrative["text"])
        
        st.markdown(f"### 🔮 Dasha Synthesis & Operational Focus")
        st.write(f"Operating under {md_disp} Mahadasha and {ad_disp} Antardasha creates a unique planetary synergy. The broader long-term trajectory is shaped by {md_disp}, while immediate events, opportunities, and daily focus are directed by {ad_disp}. Aligning your actions with the strengths of both planets provides clarity and steady momentum.")
        
        st.divider()
        st.info(md_narrative["remedy"])
        st.warning(ad_narrative["remedy"])

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
