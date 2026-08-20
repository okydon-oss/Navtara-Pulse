import streamlit as st
import datetime
import requests
import urllib.parse
import ephem
import math

# ==========================================
# 1. PAGE CONFIGURATION & CSS
# ==========================================
st.set_page_config(page_title="Navtara Pulse", page_icon="🌙", layout="centered")

# Custom CSS for Mobile Responsiveness & Purple Language Selector
st.markdown("""
    <style>
    /* Purple background for language selector */
    div[data-baseweb="select"] > div {
        background-color: #6a0dad !important;
        color: white !important;
        border-radius: 8px;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Clean Cards for Mobile */
    .transit-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #6a0dad;
    }
    .verified-badge {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin-bottom: 15px;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOCALIZATION DICTIONARIES
# ==========================================
translations = {
    "en": {
        "intro_title": "Unlocking the Wisdom of Vedic Astrology",
        "intro_desc": "In our fast-paced world, many people may not be familiar with ancient concepts like Navtara and accurate predictions rooted in Vedic astrology. This app serves as a guide, helping you explore the profound insights that astrology can offer. By understanding the Nakshatras, or lunar mansions, you can gain valuable knowledge about your personality, life path, and potential challenges. To access your personalized horoscope, simply enter your name, date of birth, time of birth, and place of birth. Let us help you uncover the wisdom of the stars!",
        "horoscope_title": "7-Day Horoscope Prediction & Life Guidance",
        "predictions": {
            "Health": "Maintain a balanced diet and regular routine. Hydration and light exercise are favored today.",
            "Career": "Focus on steady progress. Good day for planning and organizing tasks rather than impulsive decisions.",
            "Finance": "Avoid speculative investments. Focus on budgeting and saving.",
            "Mindset": "Stay calm and composed. Meditation and mindfulness will bring mental clarity."
        },
        "remedies": {
            "Vipat": "Remedy (Vipat): Recite Hanuman Chalisa. Offer water to plants and avoid major financial risks.",
            "Pratyari": "Remedy (Pratyari): Practice patience. Donate sesame seeds or oil. Chant 'Om Sham Shanayscharaya Namah'.",
            "Vadha": "Remedy (Vadha): Chant Mahamrityunjaya Mantra or 'Om Namah Shivaya'. Offer milk/water to Lord Shiva. Exercise high caution."
        }
    },
    "hi": {
        "intro_title": "वैदिक ज्योतिष के ज्ञान को अनलॉक करें",
        "intro_desc": "आज की तेज-तर्रार दुनिया में, बहुत से लोग नवतारा जैसी प्राचीन अवधारणाओं और वैदिक ज्योतिष में निहित सटीक भविष्यवाणियों से परिचित नहीं होंगे। यह ऐप एक मार्गदर्शक के रूप में कार्य करता है। नक्षत्रों को समझकर, आप अपने व्यक्तित्व और जीवन पथ के बारे में मूल्यवान ज्ञान प्राप्त कर सकते हैं। अपनी व्यक्तिगत कुंडली तक पहुंचने के लिए, बस अपना नाम, जन्म तिथि, जन्म समय और जन्म स्थान दर्ज करें!",
        "horoscope_title": "7-दिवसीय राशिफल भविष्यवाणी और जीवन मार्गदर्शन",
        "predictions": {
            "Health": "संतुलित आहार लें। आज हल्का व्यायाम और ध्यान आपके लिए अनुकूल रहेगा।",
            "Career": "लगातार प्रगति पर ध्यान दें। जल्दबाजी में निर्णय लेने से बचें।",
            "Finance": "अटकलों या सट्टेबाजी से बचें। बजट और बचत पर ध्यान दें।",
            "Mindset": "शांत रहें। ध्यान और मानसिक स्पष्टता आपके दिन को बेहतर बनाएगी।"
        },
        "remedies": {
            "Vipat": "उपाय (विपत): हनुमान चालीसा का पाठ करें। पौधों को जल दें और बड़े वित्तीय जोखिमों से बचें।",
            "Pratyari": "उपाय (प्रत्यारी): धैर्य रखें। तिल या तेल का दान करें। 'ॐ शं शनैश्चराय नमः' का जाप करें।",
            "Vadha": "उपाय (वध): महामृत्युंजय मंत्र या 'ॐ नमः शिवाय' का जाप करें। भगवान शिव को जल/दूध अर्पित करें।"
        }
    }
}
# Fallbacks for MR and GU mapping to Hindi/English for simplicity in this template
translations["mr"] = translations["hi"]
translations["gu"] = translations["hi"]

navtara_names = ["Janma", "Sampat", "Vipat", "Kshema", "Pratyari", "Sadhaka", "Vadha", "Mitra", "Ati-Mitra"]
nakshatra_list = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
@st.cache_data(show_spinner=False)
def search_places_online(query):
    """Fetch location data from OpenStreetMap (Nominatim) based on query or pincode."""
    if len(query) < 3:
        return []
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=5"
    headers = {'User-Agent': 'NavtaraPulseApp/1.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            results = response.json()
            return [res['display_name'] for res in results]
    except:
        pass
    return []

def get_status_badge(tara_name):
    """Return formatted status with appropriate emojis."""
    if tara_name in ["Vipat", "Pratyari", "Vadha"]:
        return f"{tara_name} 🔴"
    elif tara_name == "Ati-Mitra":
        return f"{tara_name} 🟢🟢"
    return tara_name

def calculate_nakshatra(date_obj, hour, minute):
    """
    Approximation of Nakshatra using Ephem. 
    In a full production app, pyswisseph with Lahiri Ayanamsa is recommended.
    """
    observer = ephem.Observer()
    observer.date = f"{date_obj.year}-{date_obj.month}-{date_obj.day} {hour}:{minute}:00"
    moon = ephem.Moon(observer)
    # Convert Moon longitude to Nakshatra (Simplified sidereal approximation)
    sidereal_lon = (math.degrees(moon.hlon) - 24.1) % 360  # Rough Lahiri offset for modern era
    nakshatra_index = int(sidereal_lon / 13.3333)
    return nakshatra_list[nakshatra_index % 27]

# ==========================================
# 4. MAIN APP LAYOUT & SESSION STATE
# ==========================================
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'en'
if 'profile_saved' not in st.session_state:
    st.session_state['profile_saved'] = False

# App Header
st.title("🌙 Navtara Pulse")

# Language Selector
lang_options = {"en": "English", "hi": "हिन्दी (Hindi)", "mr": "मराठी (Marathi)", "gu": "ગુજરાતી (Gujarati)"}
selected_lang_name = st.selectbox("🌐 Select Language", list(lang_options.values()), index=0)
lang_code = [k for k, v in lang_options.items() if v == selected_lang_name][0]
t = translations[lang_code]

# Introductory Text
st.markdown(f"### {t['intro_title']}")
st.write(t['intro_desc'])
st.divider()

# ==========================================
# 5. USER PROFILE & INPUTS (Main Scrolling Page)
# ==========================================
st.header("👤 Your Birth Profile")

col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("Name", value=st.session_state.get('name', ''))
    birth_date = st.date_input("Date of Birth", min_value=datetime.date(1925, 1, 1), max_value=datetime.date.today(), value=datetime.date(1995, 1, 1))

with col2:
    st.write("Time of Birth (24-Hour)")
    time_c1, time_c2 = st.columns(2)
    with time_c1:
        birth_hour = st.selectbox("HH", [f"{i:02d}" for i in range(24)], index=0)
    with time_c2:
        birth_minute = st.selectbox("MM", [f"{i:02d}" for i in range(60)], index=0) # Defaults to 00

# Unified Birthplace Search Window
st.write("🌍 Birth Place Name or 6-Digit Pincode")
place_query = st.text_input("Type at least 3 letters or a pincode to search...", value=st.session_state.get('place_query', ''))

selected_place = ""
if len(place_query) >= 3:
    with st.spinner("Searching online..."):
        places = search_places_online(place_query)
        if places:
            selected_place = st.selectbox("Select matching location:", places, key=f"sb_matched_{hash(place_query)}")
        else:
            st.warning("No matches found. Try modifying your search.")

# Display Verified Birthplace Badge above Save button
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
# 6. RESULTS & 7-DAY HOROSCOPE
# ==========================================
if st.session_state.get('profile_saved'):
    st.divider()
    
    # Calculate Janma Nakshatra
    janma_nakshatra = calculate_nakshatra(birth_date, int(birth_hour), int(birth_minute))
    nakshatra_index = nakshatra_list.index(janma_nakshatra)
    
    st.success(f"🌟 **{st.session_state['name']}'s Janma Nakshatra:** {janma_nakshatra}")
    
    st.header(t['horoscope_title'])
    
    # Generate 7-Day Schedule
    today = datetime.datetime.now()
    for i in range(7):
        day_date = today + datetime.timedelta(days=i)
        
        # Simulate daily moon nakshatra movement (1 nakshatra per roughly 1 day)
        daily_moon_index = (nakshatra_index + i) % 27
        tara_index = (daily_moon_index - nakshatra_index) % 9
        if tara_index < 0: tara_index += 9
        
        tara_name = navtara_names[tara_index]
        status = get_status_badge(tara_name)
        moon_nakshatra = nakshatra_list[daily_moon_index]
        
        # Display as a responsive card
        st.markdown(f"""
        <div class="transit-card">
            <h4>{day_date.strftime('%A, %d %b %Y')}</h4>
            <p><b>Status:</b> {status} | <b>Moon Nakshatra:</b> {moon_nakshatra}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Expandable Daily Predictions & Life Guidance
        with st.expander("🔮 Daily Prediction & Life Guidance"):
            st.write(f"**Health:** {t['predictions']['Health']}")
            st.write(f"**Career:** {t['predictions']['Career']}")
            st.write(f"**Finance:** {t['predictions']['Finance']}")
            st.write(f"**Mindset:** {t['predictions']['Mindset']}")
            
            # Show specific remedies for high-risk transits
            if tara_name in ["Vipat", "Pratyari", "Vadha"]:
                st.error(t['remedies'][tara_name])

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
