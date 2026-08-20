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
    st.info("To fix this, please open your terminal/command prompt and run:")
    st.code("pip install requests ephem", language="bash")
    st.stop()

# ==========================================
# 1. PAGE CONFIGURATION & CSS
# ==========================================
st.set_page_config(page_title="Navtara Pulse", page_icon="🌙", layout="centered")

st.markdown("""
    <style>
    div[data-baseweb="select"] > div { background-color: #6a0dad !important; color: white !important; border-radius: 8px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .transit-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #6a0dad; }
    .verified-badge { background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; margin-bottom: 15px; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. COMPLETE LOCALIZATION & PREDICTIONS
# ==========================================
translations = {
    "en": {
        "intro_title": "Unlocking the Wisdom of Vedic Astrology",
        "intro_desc": "In our fast-paced world, many people may not be familiar with ancient concepts like Navtara and accurate predictions rooted in Vedic astrology. This app serves as a guide, helping you explore the profound insights that astrology can offer. By understanding the Nakshatras, or lunar mansions, you can gain valuable knowledge about your personality, life path, and potential challenges. To access your personalized horoscope, simply enter your name, date of birth, time of birth, and place of birth. Let us help you uncover the wisdom of the stars!",
        "horoscope_title": "7-Day Horoscope Prediction & Life Guidance",
        "tara_details": {
            0: {"name": "Janma", "status": "Janma (Self)", "H": "Focus on self-care. Body may feel sensitive.", "C": "Maintain routine work; avoid major new launches.", "F": "Keep finances stable. No impulsive buying.", "M": "Self-reflective and calm.", "R": ""},
            1: {"name": "Sampat", "status": "Sampat (Wealth) 🟢", "H": "Energy levels are high and healing is favored.", "C": "Excellent for professional growth and opportunities.", "F": "Favorable day for investments and financial gains.", "M": "Highly positive and confident.", "R": ""},
            2: {"name": "Vipat", "status": "Vipat (Obstacles) 🔴", "H": "Vulnerable day. Avoid physical strain or risky activities.", "C": "Sudden hurdles or delays in projects may occur.", "F": "Strictly avoid speculative investments or lending.", "M": "Prone to anxiety or stress.", "R": "🛡️ Remedy: Recite Hanuman Chalisa. Offer water to plants or birds. Postpone major risky financial commitments."},
            3: {"name": "Kshema", "status": "Kshema (Wellbeing)", "H": "Good day for recovery and general wellbeing.", "C": "Smooth operations and steady progress.", "F": "Financial security and safe transactions.", "M": "Peaceful and content.", "R": ""},
            4: {"name": "Pratyari", "status": "Pratyari (Opposition) 🔴", "H": "Stress may manifest physically. Rest well.", "C": "Friction with colleagues or authority is possible.", "F": "Unexpected expenses or delayed payments.", "M": "Irritated or frustrated.", "R": "🛡️ Remedy: Practice silence during tense conversations. Chant 'Om Sham Shanayscharaya Namah' or donate sesame seeds/oil."},
            5: {"name": "Sadhaka", "status": "Sadhaka (Success) 🟢", "H": "Strong vitality and overcoming of ailments.", "C": "Great achievements and successful task completion.", "F": "Profitable ventures and realization of goals.", "M": "Determined and highly focused.", "R": ""},
            6: {"name": "Vadha", "status": "Vadha (Danger) 🔴", "H": "High risk of injury or illness. Be extremely cautious.", "C": "Major blockages. Not a day for important meetings.", "F": "Protect your assets. High chance of loss.", "M": "Fearful or overwhelmed.", "R": "🛡️ Remedy: Chant Mahamrityunjaya mantra or 'Om Namah Shivaya'. Offer water/milk to Lord Shiva. Avoid travel if possible."},
            7: {"name": "Mitra", "status": "Mitra (Friend)", "H": "Improving health and supportive energy.", "C": "Help from peers and cooperative success.", "F": "Collaborative gains and stable wealth.", "M": "Happy and sociable.", "R": ""},
            8: {"name": "Ati-Mitra", "status": "Ati-Mitra (Best Friend) 🟢🟢", "H": "Excellent physical vitality.", "C": "High growth, ultimate success, and recognition.", "F": "Windfalls or highly favorable financial news.", "M": "Joyous and spiritually uplifted.", "R": ""}
        }
    },
    "hi": {
        "intro_title": "वैदिक ज्योतिष के ज्ञान को अनलॉक करें",
        "intro_desc": "आज की तेज-तर्रार दुनिया में, बहुत से लोग नवतारा जैसी प्राचीन अवधारणाओं और वैदिक ज्योतिष में निहित सटीक भविष्यवाणियों से परिचित नहीं होंगे। यह ऐप एक मार्गदर्शक के रूप में कार्य करता है, जो आपको ज्योतिष के गहन ज्ञान का पता लगाने में मदद करता है। नक्षत्रों को समझकर, आप अपने व्यक्तित्व और जीवन पथ के बारे में मूल्यवान ज्ञान प्राप्त कर सकते हैं। अपनी व्यक्तिगत कुंडली तक पहुंचने के लिए, बस अपना नाम, जन्म तिथि, समय और स्थान दर्ज करें!",
        "horoscope_title": "7-दिवसीय राशिफल भविष्यवाणी और जीवन मार्गदर्शन",
        "tara_details": {
            0: {"name": "जन्म", "status": "जन्म (स्वयं)", "H": "आत्म-देखभाल पर ध्यान दें। शरीर संवेदनशील हो सकता है।", "C": "नियमित कार्य बनाए रखें; नई शुरुआत से बचें।", "F": "वित्त स्थिर रखें। आवेगपूर्ण खरीदारी न करें।", "M": "आत्म-चिंतनशील और शांत।", "R": ""},
            1: {"name": "सम्पत", "status": "सम्पत (धन) 🟢", "H": "ऊर्जा का स्तर उच्च है और स्वास्थ्य में सुधार होगा।", "C": "व्यावसायिक विकास और अवसरों के लिए उत्कृष्ट।", "F": "निवेश और वित्तीय लाभ के लिए अनुकूल दिन।", "M": "अत्यधिक सकारात्मक और आश्वस्त।", "R": ""},
            2: {"name": "विपत", "status": "विपत (बाधाएं) 🔴", "H": "संवेदनशील दिन। शारीरिक तनाव या जोखिम से बचें।", "C": "परियोजनाओं में अचानक बाधाएं या देरी हो सकती है।", "F": "सट्टा निवेश या उधार देने से सख्ती से बचें।", "M": "चिंता या तनाव से ग्रस्त।", "R": "🛡️ उपाय: हनुमान चालीसा का पाठ करें। पौधों/पक्षियों को जल दें। जोखिम भरे वित्तीय निर्णय टालें।"},
            3: {"name": "क्षेम", "status": "क्षेम (कल्याण)", "H": "पुनर्प्राप्ति और सामान्य भलाई के लिए अच्छा दिन।", "C": "सुचारू संचालन और स्थिर प्रगति।", "F": "वित्तीय सुरक्षा और सुरक्षित लेनदेन।", "M": "शांतिपूर्ण और संतुष्ट।", "R": ""},
            4: {"name": "प्रत्यारी", "status": "प्रत्यारी (विरोध) 🔴", "H": "तनाव शारीरिक रूप से प्रकट हो सकता है। आराम करें।", "C": "सहकर्मियों या अधिकारियों के साथ टकराव संभव है।", "F": "अप्रत्याशित खर्च या भुगतान में देरी।", "M": "चिड़चिड़ा या निराश।", "R": "🛡️ उपाय: तनावपूर्ण बातचीत के दौरान मौन रहें। 'ॐ शं शनैश्चराय नमः' का जाप करें या तिल/तेल का दान करें।"},
            5: {"name": "साधक", "status": "साधक (सफलता) 🟢", "H": "मजबूत जीवन शक्ति और बीमारियों पर विजय।", "C": "महान उपलब्धियां और कार्यों का सफल समापन।", "F": "लाभदायक उद्यम और लक्ष्यों की प्राप्ति।", "M": "दृढ़ संकल्पी और अत्यधिक केंद्रित।", "R": ""},
            6: {"name": "वध", "status": "वध (खतरा) 🔴", "H": "चोट या बीमारी का उच्च जोखिम। बेहद सतर्क रहें।", "C": "बड़ी रुकावटें। महत्वपूर्ण बैठकों के लिए दिन नहीं है।", "F": "अपनी संपत्ति की रक्षा करें। नुकसान की उच्च संभावना।", "M": "भयभीत या अभिभूत।", "R": "🛡️ उपाय: महामृत्युंजय मंत्र या 'ॐ नमः शिवाय' का जाप करें। भगवान शिव को जल/दूध अर्पित करें। यात्रा से बचें।"},
            7: {"name": "मित्र", "status": "मित्र (दोस्त)", "H": "स्वास्थ्य में सुधार और सहायक ऊर्जा।", "C": "साथियों से मदद और सहयोगात्मक सफलता।", "F": "सहयोगात्मक लाभ और स्थिर धन।", "M": "खुश और मिलनसार।", "R": ""},
            8: {"name": "अति-मित्र", "status": "अति-मित्र (परम मित्र) 🟢🟢", "H": "उत्कृष्ट शारीरिक जीवन शक्ति।", "C": "उच्च विकास, अंतिम सफलता और मान्यता।", "F": "अचानक धन लाभ या अत्यधिक अनुकूल वित्तीय समाचार।", "M": "आनंदित और आध्यात्मिक रूप से उन्नत।", "R": ""}
        }
    }
}
# Fallbacks for MR and GU
translations["mr"] = translations["hi"]
translations["gu"] = translations["hi"]

nakshatra_list = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# ==========================================
# 3. ASTRONOMY & HELPER FUNCTIONS
# ==========================================
@st.cache_data(show_spinner=False)
def search_places_online(query):
    if len(query) < 3: return []
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=5"
    try:
        res = requests.get(url, headers={'User-Agent': 'NavtaraPulse/1.0'}, timeout=5)
        if res.status_code == 200:
            return [r['display_name'] for r in res.json()]
    except: pass
    return []

def get_moon_nakshatra_index(dt_obj):
    observer = ephem.Observer()
    observer.date = ephem.date(dt_obj)
    moon = ephem.Moon(observer)
    sidereal_lon = (math.degrees(moon.hlon) - 24.1) % 360
    return int(sidereal_lon / 13.3333) % 27

def calculate_7_day_transits(start_dt):
    """Calculates exact moon transit windows for the next 7 days"""
    transits = []
    current_dt = start_dt
    current_nak = get_moon_nakshatra_index(current_dt)
    window_start = current_dt
    
    # Scan forward in 30-minute intervals to find Nakshatra changes
    for i in range(1, 7 * 48): 
        test_dt = start_dt + datetime.timedelta(minutes=30 * i)
        test_nak = get_moon_nakshatra_index(test_dt)
        if test_nak != current_nak:
            transits.append({"start": window_start, "end": test_dt, "nak_index": current_nak})
            current_nak = test_nak
            window_start = test_dt
            
    transits.append({"start": window_start, "end": start_dt + datetime.timedelta(days=7), "nak_index": current_nak})
    return transits

# ==========================================
# 4. MAIN APP LAYOUT
# ==========================================
if 'profile_saved' not in st.session_state:
    st.session_state['profile_saved'] = False

st.title("🌙 Navtara Pulse")

# Language Selector
lang_options = {"en": "English", "hi": "हिन्दी (Hindi)", "mr": "मराठी (Marathi)", "gu": "ગુજરાતી (Gujarati)"}
selected_lang_name = st.selectbox("🌐 Select Language", list(lang_options.values()), index=0)
lang_code = [k for k, v in lang_options.items() if v == selected_lang_name][0]
t = translations[lang_code]

st.markdown(f"### {t['intro_title']}")
st.write(t['intro_desc'])
st.divider()

# ==========================================
# 5. USER PROFILE
# ==========================================
st.header("👤 Your Birth Profile")
col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("Name", value=st.session_state.get('name', ''))
    birth_date = st.date_input("Date of Birth", min_value=datetime.date(1925, 1, 1), max_value=datetime.date.today(), value=datetime.date(1995, 1, 1))
with col2:
    st.write("Time of Birth (24-Hour)")
    tc1, tc2 = st.columns(2)
    with tc1: birth_hour = st.selectbox("HH", [f"{i:02d}" for i in range(24)], index=0)
    with tc2: birth_minute = st.selectbox("MM", [f"{i:02d}" for i in range(60)], index=0)

st.write("🌍 Birth Place Name or 6-Digit Pincode")
place_query = st.text_input("Type at least 3 letters or a pincode to search...", value=st.session_state.get('place_query', ''))
selected_place = ""
if len(place_query) >= 3:
    with st.spinner("Searching online..."):
        places = search_places_online(place_query)
        if places:
            selected_place = st.selectbox("Select matching location:", places)
        else:
            st.warning("No matches found. Try modifying your search.")

if selected_place:
    st.markdown(f"<div class='verified-badge'>📍 Verified Birth Place: {selected_place}</div>", unsafe_allow_html=True)

if st.button("💾 Save Profile Changes", use_container_width=True):
    if not selected_place:
        st.error("Please select a verified birthplace from the dropdown first.")
    else:
        st.session_state['name'] = user_name
        st.session_state['bdate'] = birth_date
        st.session_state['bhour'] = birth_hour
        st.session_state['bminute'] = birth_minute
        st.session_state['bplace'] = selected_place
        st.session_state['profile_saved'] = True
        st.success("Profile Saved Successfully!")

# ==========================================
# 6. RESULTS & 7-DAY TRANSIT SCHEDULE
# ==========================================
if st.session_state.get('profile_saved'):
    st.divider()
    
    # Calculate Janma Nakshatra
    birth_dt = datetime.datetime.combine(birth_date, datetime.time(int(birth_hour), int(birth_minute)))
    janma_index = get_moon_nakshatra_index(birth_dt)
    janma_nakshatra = nakshatra_list[janma_index]
    
    st.success(f"🌟 **{st.session_state['name']}'s Janma Nakshatra:** {janma_nakshatra}")
    st.header(t['horoscope_title'])
    
    # Generate exactly calculated Transits
    now = datetime.datetime.now()
    transits = calculate_7_day_transits(now)
    
    for transit in transits:
        tara_index = (transit["nak_index"] - janma_index) % 9
        if tara_index < 0: tara_index += 9
        
        tara_data = t["tara_details"][tara_index]
        moon_nakshatra = nakshatra_list[transit["nak_index"]]
        
        start_str = transit["start"].strftime('%a, %d %b %I:%M %p')
        end_str = transit["end"].strftime('%a, %d %b %I:%M %p')
        
        st.markdown(f"""
        <div class="transit-card">
            <h5 style='margin-top:0;'>{start_str} ➔ {end_str}</h5>
            <p style='margin-bottom:0;'><b>Status:</b> {tara_data['status']} | <b>Moon Nakshatra:</b> {moon_nakshatra}</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔮 Daily Prediction & Life Guidance"):
            st.write(f"**Health:** {tara_data['H']}")
            st.write(f"**Career:** {tara_data['C']}")
            st.write(f"**Finance:** {tara_data['F']}")
            st.write(f"**Mindset:** {tara_data['M']}")
            if tara_data['R']:
                st.error(tara_data['R'])

# ==========================================
# 7. SHARE APP
# ==========================================
st.divider()
st.subheader("🔗 Share Navtara Pulse")
app_url = "https://navtara-pulse.streamlit.app"
share_text = urllib.parse.quote(f"Check out Navtara Pulse - Precision Moon Transit: {app_url}")

sc1, sc2, sc3 = st.columns(3)
with sc1: st.link_button("💬 WhatsApp", f"https://api.whatsapp.com/send?text={share_text}", use_container_width=True)
with sc2: st.link_button("✉️ Email", f"mailto:?subject=Navtara Pulse&body={share_text}", use_container_width=True)
with sc3: st.link_button("✈️ Telegram", f"https://t.me/share/url?url={app_url}&text=Check out Navtara Pulse", use_container_width=True)
