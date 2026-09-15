# app.py - Main Streamlit Application Entry Point
import streamlit as st
import datetime
import urllib.parse

# Import data banks and calculation routines from databanks.py
import databanks as db
from databanks import *

# Configure Streamlit page settings
st.set_page_config(
    page_title="Navtara Pulse",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Helper function to inject clean HTML safely
def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

# Mobile-optimized CSS styling
render_html("""
<style>
    html { font-size: 16px; }
    @media (max-width: 640px) {
        html { font-size: 15.5px; }
        .block-container {
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
            padding-top: 1rem !important;
            padding-bottom: 5.5rem !important;
        }
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 5.5rem;
        padding-left: 0.9rem;
        padding-right: 0.9rem;
        max-width: 780px;
    }
    div[data-baseweb="select"] {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }
    .auth-hero-box {
        background: linear-gradient(135deg, #fdfbf7 0%, #fffbeb 100%);
        border: 1.5px solid #fde68a;
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 2px 10px rgba(245, 158, 11, 0.08);
    }
    .light-card-profile {
        background: #ffffff;
        border: 1.5px solid #fed7aa;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 3px 12px rgba(249, 115, 22, 0.06);
    }
    .light-card-num {
        background: #ffffff;
        border: 1.5px solid #bbf7d0;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 3px 12px rgba(16, 185, 129, 0.06);
    }
    .light-card-shani {
        background: #ffffff;
        border: 1.5px solid #ddd6fe;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 3px 12px rgba(139, 92, 246, 0.06);
    }
    .light-card-live {
        background: #ffffff;
        border: 1.5px solid #bae6fd;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 3px 12px rgba(14, 165, 233, 0.06);
    }
    .stButton button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        padding: 8px 6px !important;
        transition: all 0.2s ease-in-out;
    }
</style>
""")

TRANSLATIONS = {
    "en": {
        "app_title": "✨ Navtara Pulse",
        "app_subtitle": "Vedic Nakshatra Rhythm & Cosmic Precision",
        "btn_about": "✨ About App",
        "btn_user_profile": "👤 User Profile",
        "btn_numerology": "🔢 Numerology",
        "btn_shani": "🪐 Shani & Sade Sati",
        "btn_live": "⚡ Daily Horoscope",
        "btn_forecast": "🗓️ Weekly Horoscope",
        "btn_monthly": "📅 Monthly Horoscope",
        "btn_dasha": "⏳ Dasha Timeline",
        "btn_mantra": "📿 Mantra Sadhana",
        "edit_details": "✏️ Edit Details",
        "save_details": "💾 Save Profile",
        "cancel": "Cancel",
        "name_label": "Full Name",
        "dob_label": "Birth Date",
        "tob_label": "Birth Time",
        "city_label": "Birth Location / City Name",
        "nakshatra_label": "Janma Nakshatra",
        "pada_label": "Pada (Quarter)",
        "moon_rashi_label": "Moon Sign (Rashi)",
        "lagna_label": "Ascendant (Lagna)",
        "mulank_label": "Mulank (Driver)",
        "bhagyank_label": "Bhagyank (Destiny)",
        "namank_label": "Namank (Name Vibration)",
        "shani_paya_title": "🪐 Shani Paya & Active 2.5-Year Transit",
        "sadesati_title": "⚖️ Shani Sade Sati & Dhaiya Status",
        "live_pulse_title": "⚡ Today's Live Cosmic Pulse",
        "forecast_title": "🗓️ 7-Day Moon Transit Matrix & Daily Forecasts",
        "share_title": "📲 Share Navtara Pulse With Friends & Family",
        "dasha_page_title": "⏳ Vimshottari Dasha: The Cosmic Timeline",
        "dasha_page_subtitle": "Your active planetary periods mathematically calculated down to the exact minute. This represents the overarching 'season' of your life."
    },
    "hi": {
        "app_title": "✨ नवतारा पल्स (Navtara Pulse)",
        "app_subtitle": "वैदिक नक्षत्र गोचर एवं खगोलीय ऊर्जा चक्र",
        "btn_about": "✨ ऐप परिचय",
        "btn_user_profile": "👤 यूज़र प्रोफाइल",
        "btn_numerology": "🔢 अंकशास्त्र",
        "btn_shani": "🪐 शनि एवं साढ़े साती",
        "btn_live": "⚡ आज का फल",
        "btn_forecast": "🗓️ 7 दिवसीय फल",
        "btn_monthly": "📅 मासिक राशिफल",
        "btn_dasha": "⏳ दशा समयरेखा",
        "btn_mantra": "📿 मंत्र साधना",
        "edit_details": "✏️ विवरण बदलें",
        "save_details": "💾 सुरक्षित करें",
        "cancel": "रद्द करें",
        "name_label": "पूरा नाम",
        "dob_label": "जन्म तिथि",
        "tob_label": "जन्म समय",
        "city_label": "जन्म स्थान का नाम",
        "nakshatra_label": "जन्म नक्षत्र",
        "pada_label": "चरण",
        "moon_rashi_label": "चन्द्र राशि",
        "lagna_label": "लग्न राशि",
        "mulank_label": "मूलांक (Driver)",
        "bhagyank_label": "भाग्यांक (Conductor)",
        "namank_label": "नामांक (Name Vibration)",
        "shani_paya_title": "🪐 वर्तमान शनि पाया एवं 2.5 वर्षीय गोचर",
        "sadesati_title": "⚖️ शनि साढ़े साती एवं ढैय्या स्थिति",
        "live_pulse_title": "⚡ आज का दैनिक खगोलीय प्रवाह",
        "forecast_title": "🗓️ आगामी 7 दिनों का नक्षत्र गोचर एवं दैनिक फल",
        "share_title": "📲 नवतारा पल्स को परिवार व मित्रों के साथ साझा करें",
        "dasha_page_title": "⏳ विंशोत्तरी दशा: खगोलीय समयरेखा",
        "dasha_page_subtitle": "आपकी वर्तमान सक्रिय ग्रहों की महादशा और अंतरदशा सटीक समय के साथ।"
    }
}

def t(key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))

# ==============================================================================
# CLIENT-SIDE BROWSER MEMORY (URL QUERY PARAMS + SESSION STATE)
# ==============================================================================
client_params = st.query_params

if "user_profile" not in st.session_state:
    if client_params.get("name") and client_params.get("dob") and client_params.get("tob"):
        st.session_state.user_profile = {
            "name": client_params.get("name", ""),
            "dob": client_params.get("dob", ""),
            "tob": client_params.get("tob", ""),
            "city": client_params.get("city", ""),
            "lat": float(client_params.get("lat", 28.6139)),
            "lon": float(client_params.get("lon", 77.2090)),
            "lang": client_params.get("lang", "en")
        }
    else:
        st.session_state.user_profile = {
            "name": "",
            "dob": "",
            "tob": "",
            "city": "",
            "lat": 28.6139,
            "lon": 77.2090,
            "lang": "en"
        }

if "current_page" not in st.session_state:
    st.session_state.current_page = "about"

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "selected_transit_idx" not in st.session_state:
    st.session_state.selected_transit_idx = 0

if "japa_count" not in st.session_state:
    st.session_state.japa_count = 0

if "mala_rounds" not in st.session_state:
    st.session_state.mala_rounds = 0

prof = st.session_state.user_profile
current_lang = prof.get("lang", "en")

# Universal Centered Header on ALL tabs
render_html(f"""
    <div style='text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; margin-top:0.2rem; margin-bottom:0.75rem;'>
        <div style='background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); width:76px; height:76px; border-radius:26px; display:flex; align-items:center; justify-content:center; font-size:2.45rem; box-shadow:0 8px 28px rgba(245,158,11,0.38); margin-bottom:10px;'>
            ✨
        </div>
        <h1 style='margin:0; font-size:2.15rem; color:#0f172a; font-weight:900; line-height:1.2; text-align:center;'>{t('app_title', current_lang)}</h1>
        <div style='font-size:1rem; color:#64748b; font-weight:600; margin-top:6px; text-align:center;'>{t('app_subtitle', current_lang)}</div>
    </div>
""")

# Top Navigation Dock (3x3 Grid)
nav_r1_c1, nav_r1_c2, nav_r1_c3 = st.columns(3)
with nav_r1_c1:
    p_type = "primary" if st.session_state.current_page == "about" else "secondary"
    if st.button("✨ About App", type=p_type, use_container_width=True):
        st.session_state.current_page = "about"
        st.rerun()
with nav_r1_c2:
    p_type = "primary" if st.session_state.current_page == "profile" else "secondary"
    if st.button("👤 User Profile", type=p_type, use_container_width=True):
        st.session_state.current_page = "profile"
        st.rerun()
with nav_r1_c3:
    p_type = "primary" if st.session_state.current_page == "numerology" else "secondary"
    if st.button("🔢 Numerology", type=p_type, use_container_width=True):
        st.session_state.current_page = "numerology"
        st.rerun()

nav_r2_c1, nav_r2_c2, nav_r2_c3 = st.columns(3)
with nav_r2_c1:
    p_type = "primary" if st.session_state.current_page == "shani" else "secondary"
    if st.button("🪐 Shani", type=p_type, use_container_width=True):
        st.session_state.current_page = "shani"
        st.rerun()
with nav_r2_c2:
    p_type = "primary" if st.session_state.current_page == "live" else "secondary"
    if st.button("⚡ Daily Horoscope", type=p_type, use_container_width=True):
        st.session_state.current_page = "live"
        st.rerun()
with nav_r2_c3:
    p_type = "primary" if st.session_state.current_page == "forecast" else "secondary"
    if st.button("🗓️ Weekly Horoscope", type=p_type, use_container_width=True):
        st.session_state.current_page = "forecast"
        st.rerun()

nav_r3_c1, nav_r3_c2, nav_r3_c3 = st.columns(3)
with nav_r3_c1:
    p_type = "primary" if st.session_state.current_page == "monthly" else "secondary"
    if st.button("📅 Monthly Horoscope", type=p_type, use_container_width=True):
        st.session_state.current_page = "monthly"
        st.rerun()
with nav_r3_c2:
    p_type = "primary" if st.session_state.current_page == "dasha" else "secondary"
    if st.button(t("btn_dasha", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "dasha"
        st.rerun()
with nav_r3_c3:
    p_type = "primary" if st.session_state.current_page == "mantra" else "secondary"
    if st.button("📿 Mantra", type=p_type, use_container_width=True):
        st.session_state.current_page = "mantra"
        st.rerun()
        
render_html("<hr style='margin:10px 0 16px 0; border:none; border-top:1.5px solid #e2e8f0;'>")

has_valid_profile = bool(prof.get("name") and prof.get("dob") and prof.get("tob"))

if has_valid_profile:
    try:
        dob_parsed = datetime.datetime.strptime(prof["dob"], "%Y-%m-%d").date()
    except Exception:
        dob_parsed = datetime.date(1990, 1, 1)

    try:
        tob_parsed = datetime.datetime.strptime(prof["tob"], "%H:%M").time()
    except Exception:
        tob_parsed = datetime.time(12, 0)

    u_lat = float(prof.get("lat", 28.6139))
    u_lon = float(prof.get("lon", 77.2090))
    chart_info = calculate_birth_chart(dob_parsed, tob_parsed, u_lat, u_lon)
    mulank, bhagyank, namank = calculate_numerology(dob_parsed, prof.get("name", "User"))

    SATURN_TRANSIT_RASHI_IDX = 11  # Saturn in Pisces (Meena)
    shani_paya_data = calculate_shani_paya(chart_info["moon_rashi_idx"], SATURN_TRANSIT_RASHI_IDX)
    shani_sadesati_data = calculate_shani_sadesati_dhaiya(chart_info["moon_rashi_idx"], SATURN_TRANSIT_RASHI_IDX)
else:
    dob_parsed, tob_parsed, chart_info = None, None, None
    mulank, bhagyank, namank = None, None, None
    shani_paya_data, shani_sadesati_data = None, None
    u_lat, u_lon = 28.6139, 77.2090

def render_profile_setup_prompt():
    render_html("""
    <div style="background:#fffbeb; border:2px dashed #f59e0b; border-radius:16px; padding:1.5rem; text-align:center; margin:1.5rem 0;">
        <div style="font-size:2.2rem; margin-bottom:8px;">👤</div>
        <div style="font-weight:900; font-size:1.25rem; color:#92400e; margin-bottom:6px;">
            Set Up Your Vedic Birth Profile
        </div>
        <div style="font-size:0.95rem; color:#78350f; max-width:480px; margin:0 auto 1.2rem auto; line-height:1.6;">
            To calculate your authentic <b>Janma Nakshatra</b>, <b>Ascendant (Lagna)</b>, <b>Navtara cycle</b>, and <b>Shani Sade Sati phase</b>, please enter your birth details in the User Profile tab.
        </div>
    </div>
    """)
    _, c_mid, _ = st.columns([1, 2, 1])
    with c_mid:
        if st.button("👉 Configure Profile Now", type="primary", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()

# ==============================================================================
# POST-SUBMISSION ONBOARDING SCREEN: ADD TO HOME SCREEN
# ==============================================================================
def render_page_install_guide():
    render_html("""
    <div class="auth-hero-box" style="text-align:center; border:2px solid #f59e0b; background:#fffbeb;">
        <div style="font-size:2.6rem; margin-bottom:8px;">📱</div>
        <div style="font-weight:900; font-size:1.45rem; color:#92400e; margin-bottom:6px;">
            Save to Home Screen on Your Device
        </div>
        <div style="font-size:0.98rem; color:#78350f; line-height:1.6; margin-bottom:12px;">
            Your astrological profile & coordinates are now securely loaded in your device's browser bar. 
            <b>Add Navtara Pulse to your Home Screen now</b> so your profile opens automatically every day without typing anything again!
        </div>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.18rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:1.5px solid #fed7aa; padding-bottom:0.3rem;">
            🤖 For Android (Google Chrome)
        </div>
        <ol style="margin-top:5px; margin-bottom:6px; padding-left:1.3rem; font-size:0.95rem; color:#431407; line-height:1.75;">
            <li>Tap the <b>three vertical dots menu (⋮)</b> in the top-right corner of Chrome.</li>
            <li>Select <b>"Install app"</b> or <b>"Add to Home screen"</b>.</li>
            <li>Tap <b>"Install"</b>. The app icon is saved to your phone with your profile intact!</li>
        </ol>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.18rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:1.5px solid #fed7aa; padding-bottom:0.3rem;">
            🍏 For iPhone / iOS (Safari Browser)
        </div>
        <ol style="margin-top:5px; margin-bottom:6px; padding-left:1.3rem; font-size:0.95rem; color:#431407; line-height:1.75;">
            <li>Tap the <b>Share icon</b> (square with an upward arrow) at the bottom of Safari.</li>
            <li>Scroll down and tap <b>"Add to Home Screen"</b>.</li>
            <li>Tap <b>"Add"</b> in the top right. Launch directly anytime as a native full-screen app!</li>
        </ol>
    </div>
    """)

    st.write("")
    c_btn1, c_btn2 = st.columns([1, 1])
    with c_btn1:
        if st.button("⚡ Proceed to Today's Prediction", type="primary", use_container_width=True):
            st.session_state.current_page = "live"
            st.rerun()
    with c_btn2:
        if st.button("👤 View Astrological Profile", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()

# ==============================================================================
# TAB 1: ABOUT APP
# ==============================================================================
def render_page_about():
    with st.container(border=True):
        st.markdown("**🌐 Select Language / भाषा चुनें:**")
        lang_col1, _ = st.columns([2, 1])
        with lang_col1:
            lang_options = {"en": "English", "hi": "हिन्दी (Hindi)"}
            selected_lang_code = st.selectbox(
                "App Language",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
                index=list(lang_options.keys()).index(current_lang if current_lang in lang_options else "en"),
                label_visibility="collapsed"
            )
            if selected_lang_code != current_lang:
                st.session_state.user_profile["lang"] = selected_lang_code
                st.query_params["lang"] = selected_lang_code
                st.rerun()

    render_html("""
    <div class="auth-hero-box">
        <div style="font-weight:900; font-size:1.35rem; color:#92400e; margin-bottom:0.75rem; border-bottom:1.5px solid #fde68a; padding-bottom:0.4rem;">
            🧬 Navtara Pulse: Precision Chronobiology & Vedic Timing Engine
        </div>
        <div style="font-size:0.98rem; line-height:1.8; color:#451a03; margin-bottom:0.8rem;">
            <b>Navtara Pulse</b> bridges ancient Sidereal Jyotish with modern chronobiology. It is an algorithmic decision-support compass designed to answer one crucial question: <b>"Is today mathematically aligned for aggressive action, or does it demand strategic defense?"</b><br>
            By mapping the Moon's real-time transit through the 27 lunar mansions (Nakshatras) against your natal birth frequency, the app calculates your personalized 9-fold bio-rhythm, pinpointing exact windows of peak influence, effortless execution, and friction avoidance.
        </div>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            🔬 The Scientific Logic: Gravitational Hydrodynamics & Bio-Rhythms
        </div>
        
        <div style="font-size:0.96rem; line-height:1.75; color:#334155; margin-bottom:1rem;">
            <b>1. Lunar Tidal Hydrodynamics & Neuro-Endocrine Flow:</b><br>
            The adult human brain and body are composed of approximately <b>70% water and electrolytic fluids</b>. Chronobiology confirms that lunar periodicity modulates circadian gene expression, sleep architecture (REM cycles), cerebrospinal fluid pressure, and neuro-transmitter output. In classical Vedic science, the Moon governs the mind (<i>"Chandro Manaso Jatah"</i>). When the celestial Moon aligns harmoniously with your natal Moon's electro-magnetic horizon, neural processing operates at peak cognitive clarity.
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#334155; margin-bottom:1rem;">
            <b>2. The 9-Fold Mathematical Resonance Grid (27 = 9 × 3):</b><br>
            The zodiac is divided into 27 Nakshatras of 13° 20' each. The Vedic <b>Navtara Chakra</b> is an infradian mathematical model that groups these 27 stars into 3 repeating cycles of 9 qualitative energetic frequencies (Taras). Every single day, the Moon activates one of these 9 energetic chambers for your unique neural wiring:
            <ul style="margin-top:6px; padding-left:1.3rem;">
                <li><b>Expansion Windows (Sampat, Sadhana, Mitra, Ati-Mitra):</b> Characterized by high environmental receptivity and synaptic coherence. Ideal for high-stakes business negotiations, signing contracts, strategic investing, and key launches.</li>
                <li><b>Friction Shields (Vipat, Pratyari, Vadha):</b> Characterized by elevated resistance, biochemical fatigue, and communication misfires. On these days, defensive prudence and patient review prevent costly missteps.</li>
                <li><b>Foundational & Consolidation Days (Janma, Kshema):</b> Optimal for internal diagnostics, physical recuperation, and team alignment.</li>
            </ul>
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#334155;">
            <b>3. Sub-Arcsecond Planetary Ephemeris (Swiss Ephemeris):</b><br>
            Unlike conventional astrology apps that rely on generic sun signs or flat 24-hour sunrise assumptions, <b>Navtara Pulse</b> incorporates the <b>Moshier Swiss Ephemeris</b> (pyswisseph) with true topocentric Chitrapaksha Lahiri Ayanamsa. Ingress and egress timestamps are calculated down to the exact second for your geographical horizon.
        </div>
    </div>
    """)

    app_url = "https://navtara-pulse.streamlit.app"
    share_msg = "Track your real-time Vedic Moon transit rhythm, Shani Paya, and personalized timing blueprint with Navtara Pulse!"
    encoded_url = urllib.parse.quote(app_url)
    encoded_msg = urllib.parse.quote(f"{share_msg}\n\nCheck your cosmic alignment here: {app_url}")

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            {t('share_title', current_lang)}
        </div>
        <div style="font-size:0.95rem; color:#475569; margin-bottom:0.85rem;">
            Share this authentic Vedic chronobiology tool with your family, friends, and colleagues:
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:1rem;">
            <a href="https://api.whatsapp.com/send?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#25D366; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(37,211,102,0.2);">
                    🟢 WhatsApp
                </div>
            </a>
            <a href="https://t.me/share/url?url={encoded_url}&text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0088cc; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(0,136,204,0.2);">
                    ✈️ Telegram
                </div>
            </a>
            <a href="mailto:?subject=Navtara Pulse - Vedic Timing&body={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#ea4335; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(234,67,53,0.2);">
                    ✉️ Email
                </div>
            </a>
            <a href="https://twitter.com/intent/tweet?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0f172a; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(15,23,42,0.2);">
                    🐦 X (Twitter)
                </div>
            </a>
        </div>
    </div>
    """)

# ==============================================================================
# TAB 2: USER PROFILE
# ==============================================================================
def render_page_profile():
    global u_lat, u_lon
    if not has_valid_profile or st.session_state.edit_mode:
        render_html("""
        <div class="light-card-profile">
            <div style="font-weight:900; font-size:1.3rem; color:#9a3412; margin-bottom:0.5rem;">
                👤 Configure Vedic Birth Profile
            </div>
            <div style="font-size:0.94rem; color:#475569; margin-bottom:1rem;">
                Please enter your birth details to generate your authentic Vedic chart, Lagna, Janma Nakshatra, and Sade Sati status.
            </div>
        </div>
        """)
        with st.form("create_profile_form"):
            new_name = st.text_input(t("name_label", current_lang), value=prof.get("name", ""), placeholder="e.g. Rahul Sharma")
            d_init = dob_parsed if dob_parsed else datetime.date(1990, 1, 1)
            new_dob = st.date_input(t("dob_label", current_lang), value=d_init)
            
            st.markdown("**Birth Time (Hour, Minute & AM/PM):**")
            t_col1, t_col2, t_col3 = st.columns([1.5, 1.5, 1.5])
            with t_col1:
                init_hr = (tob_parsed.hour % 12) if tob_parsed else 12
                init_hr = 12 if init_hr == 0 else init_hr
                in_hour = st.selectbox("Hour", options=list(range(1, 13)), index=init_hr - 1)
            with t_col2:
                init_min = tob_parsed.minute if tob_parsed else 0
                in_minute = st.selectbox("Minute", options=list(range(0, 60)), index=init_min)
            with t_col3:
                init_ampm = "PM" if (tob_parsed and tob_parsed.hour >= 12) else "AM"
                in_ampm = st.selectbox("AM / PM", options=["AM", "PM"], index=1 if init_ampm == "PM" else 0)

            new_city_query = st.text_input(t("city_label", current_lang), value=prof.get("city", ""), placeholder="e.g. Panvel, Aurangabad, Mumbai, London, New York")

            c_save, c_canc = st.columns([2, 1])
            with c_save:
                submitted = st.form_submit_button("✨ Save & Calculate Profile", type="primary", use_container_width=True)
            with c_canc:
                canceled = st.form_submit_button("Cancel", use_container_width=True)

            if submitted:
                if not new_name.strip():
                    st.error("Please provide your full name.")
                elif not new_city_query.strip():
                    st.error("Please provide a birth location name.")
                else:
                    hr_24 = in_hour % 12
                    if in_ampm == "PM":
                        hr_24 += 12
                    final_tob_str = f"{hr_24:02d}:{in_minute:02d}"

                    # Note: Using the updated 2-return value correctly referencing databanks.py
                    with st.spinner("Searching coordinates for your location..."):
                        resolved_lat, resolved_lon = resolve_location_name(new_city_query)

                    st.session_state.user_profile.update({
                        "name": new_name.strip(),
                        "dob": new_dob.strftime("%Y-%m-%d"),
                        "tob": final_tob_str,
                        "city": new_city_query.strip(),
                        "lat": resolved_lat,
                        "lon": resolved_lon
                    })
                    
                    st.query_params.update({
                        "name": new_name.strip(),
                        "dob": new_dob.strftime("%Y-%m-%d"),
                        "tob": final_tob_str,
                        "city": new_city_query.strip(),
                        "lat": f"{resolved_lat:.4f}",
                        "lon": f"{resolved_lon:.4f}"
                    })

                    st.session_state.edit_mode = False
                    st.session_state.current_page = "install_guide"
                    st.rerun()
            
            if canceled:
                st.session_state.edit_mode = False
                st.rerun()
        return

    with st.container(border=True):
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            render_html(f"""
            <div style="font-weight:900; font-size:1.2rem; color:#0f172a;">👤 {prof['name']}'s Profile</div>
            <div style="font-size:0.95rem; color:#334155; margin-top:5px; line-height:1.6;">
                📅 <b>DOB:</b> {dob_parsed.strftime('%d %B %Y')} &nbsp;|&nbsp; ⏰ <b>Time:</b> {tob_parsed.strftime('%I:%M %p')}<br>
                📍 <b>Place:</b> {prof['city']} ({u_lat:.4f}° N, {u_lon:.4f}° E)
            </div>
            """)
        with col_p2:
            if st.button(t("edit_details", current_lang), use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()

    bio_nak = NAKSHATRA_BIO_DATA.get(chart_info["star_idx"], NAKSHATRA_BIO_DATA[2])
    n_data = get_nakshatra_rich_data(chart_info["star_idx"])
    m_data = get_rashi_rich_data(chart_info["moon_rashi_idx"])
    l_data = get_lagna_rich_data(chart_info["lagna_idx"])
    
    moon_parts = chart_info['moon_rashi_name'].split()
    moon_p1 = moon_parts[0] if moon_parts else chart_info['moon_rashi_name']
    moon_p2 = moon_parts[-1] if len(moon_parts) > 1 else ""

    lagna_parts = chart_info['lagna_name'].split()
    lagna_p1 = lagna_parts[0] if lagna_parts else chart_info['lagna_name']
    lagna_p2 = lagna_parts[-1] if len(lagna_parts) > 1 else ""

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.35rem; color:#9a3412; margin-bottom:1rem; border-bottom:2px solid #fed7aa; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>🌌 Verified Vedic Kundali Alignment</span>
            <span style="font-size:0.85rem; background:#ffedd5; color:#c2410c; padding:4px 10px; border-radius:20px; font-weight:800;">Chitrapaksha Lahiri Ayanamsa</span>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:10px; text-align:center; margin-bottom:1.25rem;">
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('lagna_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{lagna_p1}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{chart_info['lagna_deg']}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('nakshatra_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{chart_info['star_name']}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{t('pada_label', current_lang)} {chart_info['pada']}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{t('moon_rashi_label', current_lang)}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{moon_p1}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{moon_p2}</div>
            </div>
        </div>

        <div style="background:#fffaf0; border-radius:14px; padding:14px; border:1.5px solid #fed7aa; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#9a3412; margin-bottom:8px;">
                ⭐ Janma Nakshatra: {chart_info['star_name']} (Pada {chart_info['pada']})
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:8px; margin-bottom:12px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🏛️ Deity:</b> {bio_nak['deity']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🔱 Symbol:</b> {bio_nak['symbol']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🌳 Sacred Tree:</b> {bio_nak['tree']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🦅 Sacred Bird:</b> {bio_nak['bird']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🦁 Yoni Animal:</b> {bio_nak['animal']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>🪐 Planetary Lord:</b> {bio_nak['lord']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #fed7aa; margin-bottom:8px;">
                <b style="color:#9a3412; font-size:0.96rem;">🧠 Core Cognitive & Behavioral Archetype:</b>
                <div style="font-size:0.92rem; line-height:1.65; color:#431407; margin-top:2px;">{n_data['core']}</div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:8px;">
                <div style="background:#f0fdf4; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                    <b style="color:#15803d; font-size:0.92rem;">✨ Superpowers & Natural Assets:</b>
                    <div style="font-size:0.89rem; line-height:1.55; color:#14532d; margin-top:2px;">{n_data['strengths']}</div>
                </div>
                <div style="background:#fff1f2; border-radius:10px; padding:10px; border:1px solid #fecdd3;">
                    <b style="color:#be123c; font-size:0.92rem;">⚠️ Karmic Shadows & Blind Spots:</b>
                    <div style="font-size:0.89rem; line-height:1.55; color:#881337; margin-top:2px;">{n_data['shadows']}</div>
                </div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #fed7aa; margin-bottom:8px; font-size:0.91rem; color:#431407;">
                <b>💼 Peak Vocational & Executive Fields:</b><br>{n_data['careers']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #fed7aa; margin-bottom:8px; font-size:0.91rem; color:#431407;">
                <b>🔮 Evolutionary Life Path Trajectory:</b><br>{n_data['prediction']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #f97316; font-size:0.91rem; color:#431407;">
                <b>🪔 Prescribed Vedic Nakshatra Remedies:</b><br>{n_data['remedies']}
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:14px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#065f46; margin-bottom:8px;">
                🌙 Moon Sign (Chandra Rashi): {chart_info['moon_rashi_name']}
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:10px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>🔥 Element:</b> {m_data['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>🪐 Rashi Sovereign:</b> {m_data['ruler']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>🧠 Emotional Mindset & Subconscious Processing:</b><br>{m_data['psychology']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>⚡ Stress Reflexes & Primal Coping Instincts:</b><br>{m_data['instincts']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>❤️ Interpersonal Blueprint & Relationship Style:</b><br>{m_data['relations']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>🌿 Bio-Rhythms & Physiological Vitality:</b><br>{m_data['health']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #10b981; font-size:0.91rem; color:#14532d;">
                <b>🪔 Prescribed Lunar Remedies:</b><br>{m_data['remedies']}
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:8px;">
                🌅 Ascendant (Lagna): {chart_info['lagna_name']} at {chart_info['lagna_deg']}
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:10px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>🌍 Lagna Tattva:</b> {l_data['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>👑 Ascendant Lord:</b> {l_data['lord']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>🛡️ Physical Constitution, Vitality & Posture (Prakriti):</b><br>{l_data['constitution']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>👔 Outward Persona & Negotiating Presence:</b><br>{l_data['persona']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>🚀 Evolutionary Life Arc & Asset Compounding:</b><br>{l_data['life_arc']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #8b5cf6; font-size:0.91rem; color:#3b0764;">
                <b>🪔 Prescribed Ascendant Remedies:</b><br>{l_data['remedies']}
            </div>
        </div>
    </div>
    """)

    # Tara Bala Widget
    with st.container(border=True):
        st.markdown("**🤝 Nakshatra Synergy & Compatibility Evaluator (Tara Bala)**")
        partner_star_choice = st.selectbox("Select Counterpart's Birth Star:", options=NAKSHATRAS, index=0)
        p_star_idx = NAKSHATRAS.index(partner_star_choice) + 1
        tara_res = get_tara_bala_info(chart_info['star_idx'], p_star_idx)
        
        box_bg = '#f0fdf4' if tara_res['is_allied'] else ('#fff1f2' if tara_res['is_friction'] else '#f8fafc')
        box_border = '#86efac' if tara_res['is_allied'] else ('#fecdd3' if tara_res['is_friction'] else '#e2e8f0')
        box_color = '#15803d' if tara_res['is_allied'] else ('#be123c' if tara_res['is_friction'] else '#0f172a')
        
        render_html(f"""
        <div style="background:{box_bg}; border:1.5px solid {box_border}; border-radius:12px; padding:12px; margin-top:8px;">
            <div style="font-size:1.05rem; font-weight:800; color:{box_color};">
                {tara_res['icon']} {tara_res['tara_name']} — {tara_res['quality']}
            </div>
            <div style="font-size:0.92rem; font-weight:700; color:#334155; margin-top:4px;">
                Dynamic: {tara_res['relationship_tone']}
            </div>
            <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.5;">
                {tara_res['advice']}
            </div>
        </div>
        """)

# ==============================================================================
# TAB 3: NUMEROLOGY
# ==============================================================================
def render_page_numerology():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    num_domains = get_numerology_life_domains(mulank, bhagyank, namank, current_lang)
    avoid_data = get_numerology_avoidance(mulank, bhagyank, current_lang)
    p_m_label = NUM_PLANET_NAMES.get(mulank, {}).get(current_lang, f"Planet {mulank}")
    p_b_label = NUM_PLANET_NAMES.get(bhagyank, {}).get(current_lang, f"Planet {bhagyank}")
    p_n_label = NUM_PLANET_NAMES.get(namank, {}).get(current_lang, f"Planet {namank}")

    cautions_html = "".join(f"<li style='margin-bottom:5px;'>{c}</li>" for c in avoid_data['cautions'])

    render_html(f"""
    <div class="light-card-num">
        <div style="font-weight:900; font-size:1.25rem; color:#065f46; margin-bottom:1rem; border-bottom:2px solid #bbf7d0; padding-bottom:0.5rem;">
            <span>🔢 Core Numerology Blueprint</span>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:10px; text-align:center; margin-bottom:1.15rem;">
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900;">{t('mulank_label', current_lang)}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46;">{mulank}</div>
                <div style="font-size:0.88rem; color:#059669; font-weight:800;">{p_m_label}</div>
            </div>
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900;">{t('bhagyank_label', current_lang)}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46;">{bhagyank}</div>
                <div style="font-size:0.88rem; color:#059669; font-weight:800;">{p_b_label}</div>
            </div>
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900;">{t('namank_label', current_lang)}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46;">{namank}</div>
                <div style="font-size:0.88rem; color:#059669; font-weight:800;">{p_n_label}</div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr; gap:12px; margin-bottom:1.15rem;">
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #059669;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['career_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['career_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #10b981;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['wealth_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['wealth_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #14b8a6;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['rel_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['rel_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #0d9488;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['health_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['health_desc']}</div>
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:12px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:8px;">{num_domains['luck_title']}</div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.95rem; line-height:1.6;">
                <div><b>✨ Lucky Numbers:</b> {num_domains['lucky_num']}</div>
                <div><b>⚠️ Caution Numbers:</b> {num_domains['avoid_num']}</div>
                <div><b>📅 Auspicious Days:</b> {num_domains['lucky_days']}</div>
                <div><b>🧭 Favorable Direction:</b> {num_domains['lucky_dir']}</div>
                <div style="grid-column: 1 / -1;"><b>🎨 Energizing Colors:</b> {num_domains['lucky_colors']}</div>
            </div>
        </div>

        <div style="background:#fff1f2; border-radius:12px; padding:14px; border:1.5px solid #fecdd3; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.08rem; color:#9f1239; margin-bottom:8px;">{avoid_data['avoid_title']}</div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.93rem; line-height:1.6; margin-bottom:10px;">
                <div><b>🚫 Numbers to Avoid:</b> {avoid_data['avoid_numbers']}</div>
                <div><b>🎨 Colors to Avoid:</b> {avoid_data['avoid_colors']}</div>
                <div><b>📅 Unfavorable Days:</b> {avoid_data['avoid_days']}</div>
                <div><b>🧭 Direction to Avoid:</b> {avoid_data['avoid_directions']}</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border-left:4px solid #e11d48;">
                <b style="color:#9f1239; font-size:0.95rem;">⚠️ Critical Behavioral & Strategic Don'ts:</b>
                <ul style="margin:4px 0 0 0; padding-left:1.2rem; font-size:0.92rem; color:#881337; line-height:1.6;">
                    {cautions_html}
                </ul>
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:12px; padding:14px; border:1.5px solid #bbf7d0;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:6px;">🪔 Numerology Harmony & Grounding Remedies:</div>
            <div style="font-size:0.94rem; line-height:1.65; color:#14532d;">
                • <b>Metal Vessel Grounding:</b> Drink water from a pure silver or copper vessel to pacify nervous restlessness and enhance bio-electrical harmony.<br>
                • <b>Digital & Workspace Bio-Shield:</b> Remove tangled charging cables, broken electronic gadgets, and inactive clocks from your workspace.<br>
                • <b>Name Resonance (Namank):</b> Use green or blue ink when writing or endorsing important planning documents to harmonize your {namank} name vibration.
            </div>
        </div>
    </div>
    """)

# ==============================================================================
# TAB 4: SHANI & SADE SATI (EXHAUSTIVE 7-DOMAIN MATRIX)
# ==============================================================================
def render_page_shani():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    m_name = chart_info['moon_rashi_name'].split()[0]
    p1_active_tag = '<span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW</span>' if shani_sadesati_data['phase_1_active'] else ''
    p2_active_tag = '<span style="font-size:0.82rem; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW (PEAK)</span>' if shani_sadesati_data['phase_2_active'] else ''
    p3_active_tag = '<span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW</span>' if shani_sadesati_data['phase_3_active'] else ''

    render_html(f"""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.35rem; color:#5b21b6; margin-bottom:1rem; border-bottom:2px solid #ddd6fe; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>🪐 Shani Paya & Sade Sati Exhaustive Life-Domain Matrix</span>
            <span style="font-size:0.85rem; background:#ede9fe; color:#5b21b6; padding:4px 10px; border-radius:20px; font-weight:800;">Saturn in Pisces (Meena)</span>
        </div>
        
        <!-- SHANI PAYA IN-DEPTH MATRIX -->
        <div style="background:#f5f3ff; border-radius:14px; padding:16px; border:1.5px solid #e9d5ff; margin-bottom:1.25rem;">
            <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">ACTIVE TRANSIT PAYA FOR YOUR {m_name.upper()} MOON</div>
            <div style="font-size:1.45rem; font-weight:900; color:#5b21b6; margin:4px 0;">{shani_paya_data['paya']}</div>
            <div style="font-size:0.98rem; color:#7c3aed; font-weight:800;">Grade: {shani_paya_data['status']} | Dynamic: {shani_paya_data['tone']}</div>
            <div style="font-size:0.92rem; color:#475569; margin-top:3px;"><b>Active Timeline:</b> {shani_paya_data['timeline']}</div>
            
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1px solid #ddd6fe; margin-top:12px; font-size:0.93rem; color:#3b0764; line-height:1.7;">
                <b>🏛️ Classical Foundation:</b> {shani_paya_data['desc']}<br>
                <b>🧭 Operating Houses:</b> Saturn activates the {shani_paya_data['houses']} house axis relative to your natal Moon.
            </div>

            <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-top:12px;">
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #f97316; font-size:0.91rem; color:#7c2d12; line-height:1.6;">
                    <b>🌿 1. Health & Vitality Impact:</b><br>{shani_paya_data['health']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #10b981; font-size:0.91rem; color:#14532d; line-height:1.6;">
                    <b>💰 2. Wealth & Cash Flow Dynamics:</b><br>{shani_paya_data['wealth']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #8b5cf6; font-size:0.91rem; color:#3b0764; line-height:1.6;">
                    <b>👨‍👩‍👧‍👦 3. Family & Domestic Harmony:</b><br>{shani_paya_data['family']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #e11d48; font-size:0.91rem; color:#881337; line-height:1.6;">
                    <b>📉 4. Loans & Liabilities Management:</b><br>{shani_paya_data['loan']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #065f46; font-size:0.91rem; color:#065f46; line-height:1.6;">
                    <b>🤝 5. Partnerships & Business Alliances:</b><br>{shani_paya_data['partner']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #d97706; font-size:0.91rem; color:#78350f; line-height:1.6;">
                    <b>🍀 6. Luck & Destiny Alignment:</b><br>{shani_paya_data['luck']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #0284c7; font-size:0.91rem; color:#0369a1; line-height:1.6;">
                    <b>💼 7. Career, Authority & Executive Standing:</b><br>{shani_paya_data['career']}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #475569; font-size:0.91rem; color:#0f172a; line-height:1.6;">
                    <b>🪔 8. Targeted Elemental Countermeasures:</b><br>{shani_paya_data['protocol']}
                </div>
            </div>
        </div>

        <!-- SADE SATI / DHAIYA EXHAUSTIVE MATRIX -->
        <div style="background:#ffffff; border-radius:14px; padding:16px; border:1.5px solid #ddd6fe; margin-bottom:1.25rem;">
            <div style="font-weight:900; font-size:1.2rem; color:#5b21b6; margin-bottom:10px; border-bottom:1px solid #e9d5ff; padding-bottom:5px; display:flex; justify-content:space-between; align-items:center;">
                <span>⚖️ Active Sade Sati / Dhaiya Life-Domain Breakdown for {m_name} Moon</span>
                <span style="font-size:0.82rem; background:#ede9fe; color:#5b21b6; padding:3px 8px; border-radius:10px; font-weight:800;">{shani_sadesati_data['status_title'].split(':')[0]}</span>
            </div>
            
            <div style="background:{'#fef2f2' if shani_sadesati_data['phase_2_active'] else '#f5f3ff'}; border-radius:12px; padding:14px; border-left:5px solid {'#ef4444' if shani_sadesati_data['phase_2_active'] else '#9333ea'}; margin-bottom:14px;">
                <b style="color:{'#991b1b' if shani_sadesati_data['phase_2_active'] else '#5b21b6'}; font-size:1.1rem;">{shani_sadesati_data['status_title']}</b>
                <div style="font-size:0.92rem; color:#64748b; margin:3px 0 8px 0;"><b>Active Window:</b> {shani_sadesati_data['dates']} | <b>Core Focus:</b> {shani_sadesati_data['focus']}</div>
                <div style="font-size:0.95rem; line-height:1.7; color:#334155;">{shani_sadesati_data['impact']}</div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:14px;">
                <div style="background:#fff7ed; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#7c2d12; border-left:4px solid #f97316;">
                    <b>🌿 1. Health & Vitality Impact:</b><br>{shani_sadesati_data['health']}
                </div>
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#14532d; border-left:4px solid #10b981;">
                    <b>💰 2. Wealth & Cash Flow Dynamics:</b><br>{shani_sadesati_data['wealth']}
                </div>
                <div style="background:#faf5ff; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#3b0764; border-left:4px solid #8b5cf6;">
                    <b>👨‍👩‍👧‍👦 3. Family & Domestic Harmony:</b><br>{shani_sadesati_data['family']}
                </div>
                <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#881337; border-left:4px solid #e11d48;">
                    <b>📉 4. Loans & Liabilities Management:</b><br>{shani_sadesati_data['loan']}
                </div>
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#065f46; border-left:4px solid #065f46;">
                    <b>🤝 5. Partnerships & Business Alliances:</b><br>{shani_sadesati_data['partner']}
                </div>
                <div style="background:#fffbeb; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#78350f; border-left:4px solid #d97706;">
                    <b>🍀 6. Luck & Destiny Alignment:</b><br>{shani_sadesati_data['luck']}
                </div>
                <div style="background:#f0f9ff; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#0369a1; border-left:4px solid #0284c7;">
                    <b>💼 7. Career, Authority & Executive Standing:</b><br>{shani_sadesati_data['career']}
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#0f172a; border-left:4px solid #475569;">
                    <b>🪔 8. Prescribed Remedial Protocol:</b><br>{shani_sadesati_data['remedy']}
                </div>
            </div>

            <div style="font-weight:900; font-size:1.05rem; color:#475569; margin:16px 0 8px 0; border-top:1px solid #e9d5ff; padding-top:10px;">
                Complete 7.5-Year Sade Sati Evolutionary Blueprint for {m_name} Moon:
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #a855f7; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#5b21b6; font-size:0.96rem;">Phase 1: Rising Phase (Saturn in {shani_sadesati_data['rashi_12th']} / 12th from Moon)</b>
                    {p1_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>Core Dynamic:</b> Subconscious restructuring, elimination of toxic habits, and mental detachment.<br>
                    • <b>Financial & Career:</b> Spikes in expenses related to travel, relocation, or healthcare; work happens behind the scenes.<br>
                    • <b>Karmic Mastery:</b> Shedding psychological baggage and preparing for the core transit.
                </div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #ef4444; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#991b1b; font-size:0.96rem;">Phase 2: Peak Janma Shani (Saturn in {shani_sadesati_data['rashi_1st']} / Over Natal Moon)</b>
                    {p2_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>Core Dynamic:</b> Crucible of character and endurance. Dissolves false pride and tests emotional truth.<br>
                    • <b>Financial & Career:</b> Maximum administrative burden, heavy decision-making stress, and executive solitude.<br>
                    • <b>Karmic Mastery:</b> Cultivating emotional resilience, physical discipline, and enduring maturity.
                </div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #10b981; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#065f46; font-size:0.96rem;">Phase 3: Setting Phase (Saturn in {shani_sadesati_data['rashi_2nd']} / 2nd from Moon)</b>
                    {p3_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>Core Dynamic:</b> Lifting of psychological pressure, consolidation of hard-won wisdom, and stabilizing family harmony.<br>
                    • <b>Financial & Career:</b> Wealth recovery, acquisition of durable assets, disciplined speech, and delayed recognition.<br>
                    • <b>Karmic Mastery:</b> Transforming lessons into lasting institutional stability and financial security.
                </div>
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe;">
            <div style="font-weight:900; font-size:1.05rem; color:#5b21b6; margin-bottom:6px;">🪔 Prescribed Remedies for Planetary Neutralization:</div>
            <div style="font-size:0.93rem; line-height:1.7; color:#3b0764;">
                • <b>Mantra Japa:</b> Recite the <b>Shani Beej Mantra</b> (ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः) 108 times at twilight on Saturdays facing West.<br>
                • <b>Vitality Shield:</b> Recite the <b>Hanuman Chalisa</b> daily to boost pranic fire, disperse lethargy, and protect mental peace.<br>
                • <b>Charity & Service:</b> Donate mustard oil, black sesame seeds, or dark blankets to laborers, sweepers, or elderly persons on Saturdays.<br>
                • <b>Behavioral Grounding:</b> Practice absolute punctuality, avoid harsh speech, and avoid shortcuts in contractual agreements.
            </div>
        </div>
    </div>
    """)

    st.write("")
    if st.button("📿 Open Dedicated Digital Japa Counter", type="primary", use_container_width=True):
        st.session_state.current_page = "mantra"
        st.rerun()

# ==============================================================================
# TAB 5: LIVE PREDICTION
# ==============================================================================
def render_page_live():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    now_ist = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
    now_ist = now_ist.replace(tzinfo=None)

    cur_star_idx, s_dt, e_dt = get_current_nakshatra_window(now_ist)
    offset = (cur_star_idx - chart_info["star_idx"]) % 9
    nav_name, icon, quality = NAVTARA_NAMES[offset]
    vahan_info = calculate_shani_vahan(chart_info["star_idx"], cur_star_idx)
    p_day = get_personal_day_vibe(dob_parsed, now_ist.date(), current_lang)

    insights = get_detailed_day_insights(offset, vahan_info, NAKSHATRAS[cur_star_idx - 1], p_day)

    muhurtas = calculate_daily_muhurtas(now_ist.date(), u_lat, u_lon)
    abhijit_s, abhijit_e = muhurtas["abhijit"]
    rahu_s, rahu_e = muhurtas["rahu"]
    yama_s, yama_e = muhurtas["yamaganda"]

    is_abhijit = abhijit_s <= now_ist <= abhijit_e
    is_rahu = rahu_s <= now_ist <= rahu_e
    is_yama = yama_s <= now_ist <= yama_e

    now_time_str = now_ist.strftime('%I:%M %p')

    if is_rahu:
        status_banner = f"""
        <div style="background:#fee2e2; border:2px solid #ef4444; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#b91c1c; font-size:1.02rem;">🔴 CAUTION WINDOW ACTIVE: Rahu Kaal in Operation ({now_time_str} IST)</b>
                <div style="font-size:0.88rem; color:#7f1d1d; margin-top:2px;">Pause new contract signing, travel departures, and major capital moves until {rahu_e.strftime('%I:%M %p')}.</div>
            </div>
            <span style="font-size:1.8rem;">🛑</span>
        </div>
        """
    elif is_yama:
        status_banner = f"""
        <div style="background:#fee2e2; border:2px solid #ef4444; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#b91c1c; font-size:1.02rem;">🔴 CAUTION WINDOW ACTIVE: Yamaganda in Operation ({now_time_str} IST)</b>
                <div style="font-size:0.88rem; color:#7f1d1d; margin-top:2px;">Avoid launching crucial ventures or final legal settlements until {yama_e.strftime('%I:%M %p')}.</div>
            </div>
            <span style="font-size:1.8rem;">⚠️</span>
        </div>
        """
    elif is_abhijit:
        status_banner = f"""
        <div style="background:#dcfce7; border:2px solid #22c55e; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#15803d; font-size:1.02rem;">🟢 GOLDEN ACTION WINDOW ACTIVE: Abhijit Muhurta ({now_time_str} IST)</b>
                <div style="font-size:0.88rem; color:#14532d; margin-top:2px;">Supreme cosmic victory window. Highly auspicious for approvals, launches, and decisions until {abhijit_e.strftime('%I:%M %p')}.</div>
            </div>
            <span style="font-size:1.8rem;">🌟</span>
        </div>
        """
    else:
        status_banner = f"""
        <div style="background:#f0fdf4; border:1.5px solid #86efac; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#166534; font-size:0.98rem;">🟢 SAFE TO ACT: Standard Favorable Orbit ({now_time_str} IST)</b>
                <div style="font-size:0.86rem; color:#15803d; margin-top:2px;">No planetary friction windows currently active. Next Abhijit: {abhijit_s.strftime('%I:%M %p')} | Rahu Kaal: {rahu_s.strftime('%I:%M %p')}</div>
            </div>
            <span style="font-size:1.6rem;">⏱️</span>
        </div>
        """

    render_html(f"""
    <div class="light-card-live">
        <div style="font-weight:900; font-size:1.25rem; color:#0369a1; margin-bottom:1rem; border-bottom:2px solid #bae6fd; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{t('live_pulse_title', current_lang)}</span>
            <span style="font-size:0.85rem; background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:20px; font-weight:900;">LIVE IST</span>
        </div>

        {status_banner}

        <div style="background:#f0f9ff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:0.85rem; color:#0284c7; font-weight:800; text-transform:uppercase;">CURRENT MOON NAKSHATRA</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#0369a1;">{NAKSHATRAS[cur_star_idx - 1]}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.8rem;">{icon}</div>
                    <div style="font-size:0.88rem; font-weight:900; color:#0369a1;">{quality}</div>
                </div>
            </div>
            <div style="font-size:1.05rem; font-weight:900; color:#0284c7; margin-top:8px;">Navtara: {nav_name}</div>
            <div style="font-size:0.92rem; color:#334155; margin-top:6px; line-height:1.5;">
                ⏳ <b>Active Moon Transit Window:</b><br>
                {s_dt.strftime('%a, %d %b %I:%M %p')} → {e_dt.strftime('%a, %d %b %I:%M %p IST')}
            </div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <b>⏱️ Timing Windows for Today ({prof['city']}):</b><br>
            • 🌟 <b>Abhijit Muhurta:</b> {abhijit_s.strftime('%I:%M %p')} – {abhijit_e.strftime('%I:%M %p IST')} (Golden Window)<br>
            • ⚠️ <b>Rahu Kaal:</b> {rahu_s.strftime('%I:%M %p')} – {rahu_e.strftime('%I:%M %p IST')} (Avoid Signings)
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#0369a1; margin-bottom:10px; border-bottom:1px solid #e0f2fe; padding-bottom:5px;">
                📋 Practical Action Green Light Checklist
            </div>
            
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.92rem;">
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>💼 Career & Execution:</b><br>
                    <span style="color:#0f172a;">{'🟢 Green Light: Take bold action in Abhijit window' if offset in [1,3,5,7,8] else '🔴 Hold Back: Avoid starting disputes or high-stakes requests'}</span>
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>💰 Wealth & Financials:</b><br>
                    <span style="color:#0f172a;">{'🟢 Favorable: Execute capital transfers & investments' if offset in [1,3,5,7,8] else '🔴 Cautious: Strictly avoid speculative leverage & loans'}</span>
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>🏠 Domestic & Relations:</b><br>
                    <span style="color:#0f172a;">{'🟢 Harmonious: Excellent for family discussions' if offset in [1,3,5,7,8] else '🟡 Sensitive: Practice calm listening; avoid debates'}</span>
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>🌿 Health & Energy:</b><br>
                    <span style="color:#0f172a;">{'🟢 High Vitality: Great for workouts & physical tasks' if offset in [1,3,5,7,8] else '🔴 Prone to Fatigue: Rest well and hydrate deeply'}</span>
                </div>
            </div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#0369a1; margin-bottom:8px; border-bottom:1px solid #e0f2fe; padding-bottom:5px;">
                🧠 Cognitive & Strategic Archetype: {insights['theme_title']}
            </div>
            <div style="font-size:0.95rem; line-height:1.7; color:#1e293b; margin-bottom:12px;">
                {insights['theme_desc']}
            </div>

            <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; border-left:4px solid #16a34a; margin-bottom:10px;">
                <b style="color:#15803d; font-size:0.95rem;">🚀 Prime Opportunities & Protocols:</b>
                <div style="font-size:0.92rem; line-height:1.6; color:#166534; margin-top:2px;">{insights['opportunities']}</div>
            </div>

            <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; border-left:4px solid #e11d48;">
                <b style="color:#be123c; font-size:0.95rem;">⚠️ Potential Hazards & Red Flags:</b>
                <div style="font-size:0.92rem; line-height:1.6; color:#9f1239; margin-top:2px;">{insights['hazards']}</div>
            </div>
        </div>

        <div style="background:#f0f9ff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd;">
            <div style="font-weight:900; font-size:1.1rem; color:#0369a1; margin-bottom:8px; border-bottom:1px solid #bae6fd; padding-bottom:5px;">
                🪔 Targeted Daily Cosmic Remedies:
            </div>
            <div style="font-size:0.94rem; line-height:1.7; color:#0c4a6e;">
                • <b>Aura Protection Mantra:</b> {insights['remedy_mantra']}<br>
                • <b>Elemental Harmony & Donation:</b> {insights['remedy_charity']}<br>
                • <b>Behavioral & Color Calibration:</b> {insights['remedy_action']}
            </div>
        </div>
    </div>
    """)

# ==============================================================================
# TAB 6: 7 DAYS PREDICTION
# ==============================================================================
def render_page_forecast():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    now_ist = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
    now_ist = now_ist.replace(tzinfo=None)

    transits = get_7_day_moon_transits(now_ist, chart_info["star_idx"])

    render_html(f"""
    <div style="font-weight:900; font-size:1.25rem; color:#1e293b; margin-bottom:0.8rem;">
        {t('forecast_title', current_lang)}
    </div>
    """)

    pill_elements = []
    for tr in transits:
        off = tr["nav_offset"]
        if off in [1, 8]:
            bg, fg, label = "#dcfce7", "#15803d", "Peak 🟢🟢"
        elif off in [3, 5, 7]:
            bg, fg, label = "#f0fdf4", "#166534", "Good 🟢"
        elif off == 0:
            bg, fg, label = "#fef9c3", "#854d0e", "Focus 🟡"
        else:
            bg, fg, label = "#fee2e2", "#b91c1c", "Guard 🔴"
        pill_elements.append(f"""
        <div style="background:{bg}; color:{fg}; padding:8px 6px; border-radius:10px; text-align:center; font-size:0.8rem; font-weight:800; border:1px solid rgba(0,0,0,0.06);">
            <div>{tr['date_str'].split(',')[0]}</div>
            <div style="font-size:0.86rem; margin:2px 0;">{label.split()[1]}</div>
            <div style="font-size:0.75rem;">{tr['star_name'][:4]}</div>
        </div>
        """)
    pills_html = "".join(pill_elements)

    render_html(f"""
    <div style="display:grid; grid-template-columns: repeat(7, 1fr); gap:6px; margin-bottom:1rem;">
        {pills_html}
    </div>
    """)

    for idx, tr in enumerate(transits):
        with st.container(border=True):
            col_t1, col_t2, col_t3 = st.columns([1.6, 2.8, 1.6])
            with col_t1:
                render_html(f"<b>{tr['date_str']}</b><br><span style='font-size:0.92rem; color:#475569; font-weight:700;'>{tr['star_name']}</span>")
            with col_t2:
                vahan_name = tr['vahan'].split()[1] if len(tr['vahan'].split()) > 1 else tr['vahan']
                render_html(f"<span style='font-size:1.1rem;'>{tr['icon']}</span> <b>{tr['nav_name'].split('(')[0]}</b><br><span style='font-size:0.88rem; color:#64748b;'>Mount: {vahan_name}</span>")
            with col_t3:
                if st.button("🔮 View", key=f"btn_tr_{idx}", use_container_width=True):
                    st.session_state.selected_transit_idx = idx
                    st.rerun()

    safe_idx = min(len(transits) - 1, max(0, st.session_state.selected_transit_idx))
    sel_tr = transits[safe_idx]
    
    sel_p_day = get_personal_day_vibe(dob_parsed, sel_tr['date'], current_lang)
    v_info = calculate_shani_vahan(chart_info["star_idx"], sel_tr["star_idx"])
    sel_insights = get_detailed_day_insights(sel_tr["nav_offset"], v_info, sel_tr['star_name'], sel_p_day)
    sel_muh = calculate_daily_muhurtas(sel_tr['date'], u_lat, u_lon)

    render_html(f"""
    <div class="light-card-live" style="margin-top:1.1rem;">
        <div style="font-weight:900; font-size:1.25rem; color:#0369a1; margin-bottom:8px; border-bottom:1.5px solid #bae6fd; padding-bottom:5px;">
            🔮 Detailed Transit Forecast: {sel_tr['date_str']} ({sel_tr['star_name']})
        </div>
        
        <div style="font-size:0.94rem; color:#334155; margin-bottom:10px; line-height:1.5;">
            ⏰ <b>Transit Window:</b> {sel_tr['start_str']} → {sel_tr['end_str']}<br>
            🧭 <b>Navtara Classification:</b> {sel_tr['nav_name']} ({sel_tr['quality']})<br>
            🪐 <b>Saturn Mount (Vahan):</b> {v_info['name']} — <i>{v_info['speed']} ({v_info['type']})</i>
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bae6fd; margin-bottom:10px; font-size:0.91rem;">
            <b>⏱️ Key Timing Windows for {sel_tr['date_str']}:</b><br>
            • 🌟 <b>Abhijit Muhurta:</b> {sel_muh['abhijit'][0].strftime('%I:%M %p')} – {sel_muh['abhijit'][1].strftime('%I:%M %p IST')} (Golden Period)<br>
            • ⚠️ <b>Rahu Kaal:</b> {sel_muh['rahu'][0].strftime('%I:%M %p')} – {sel_muh['rahu'][1].strftime('%I:%M %p IST')} (Avoid Signings)
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #bae6fd; margin-bottom:12px;">
            <b style="color:#0369a1; font-size:1rem;">🎯 Cosmic Archetype: {sel_insights['theme_title']}</b>
            <div style="font-size:0.94rem; line-height:1.65; color:#1e293b; margin-top:4px;">
                {sel_insights['theme_desc']}
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr; gap:8px; margin-bottom:12px;">
            <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; border-left:4px solid #16a34a;">
                <b style="color:#15803d; font-size:0.92rem;">🟢 Favorable Initiatives & Green Lights:</b>
                <div style="font-size:0.91rem; line-height:1.6; color:#166534; margin-top:2px;">{sel_insights['opportunities']}</div>
            </div>
            <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; border-left:4px solid #e11d48;">
                <b style="color:#be123c; font-size:0.92rem;">🔴 Hazards, Caution & Red Lights:</b>
                <div style="font-size:0.91rem; line-height:1.6; color:#9f1239; margin-top:2px;">{sel_insights['hazards']}</div>
            </div>
        </div>

        <div style="background:#f0f9ff; border-radius:10px; padding:12px; border:1px solid #bae6fd;">
            <b style="color:#0369a1; font-size:0.98rem;">🪔 Prescribed Daily Remedies for this Window:</b>
            <div style="font-size:0.92rem; line-height:1.65; color:#0c4a6e; margin-top:4px;">
                • <b>Mantra Japa:</b> {sel_insights['remedy_mantra']}<br>
                • <b>Elemental Donation:</b> {sel_insights['remedy_charity']}<br>
                • <b>Personal Protocol:</b> {sel_insights['remedy_action']}
            </div>
        </div>
    </div>
    """)


# ==============================================================================
# TAB 7: MONTHLY HOROSCOPE (DYNAMIC GOCHAR ENGINE)
# ==============================================================================
def render_page_monthly():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    lagna_name = chart_info["lagna_name"]
    lagna_idx = chart_info["lagna_idx"]

    render_html(f"""
    <div class="light-card-profile" style="margin-bottom:1rem;">
        <div style="font-weight:900; font-size:1.3rem; color:#9a3412; margin-bottom:0.3rem;">
            📅 Lagna-Based Monthly Horoscope & Life Matrix
        </div>
        <div style="font-size:0.94rem; color:#475569;">
            Precision 12-Bhava predictive analysis for <b>{lagna_name}</b> ({chart_info['lagna_deg']}).
        </div>
    </div>
    """)

    # --- DYNAMIC CALENDAR LOGIC (Mid-Month Ephemeris Sampling) ---
    now = datetime.datetime.now()
    curr_mid = now.replace(day=15, hour=12, minute=0, second=0)
    curr_month_str = now.strftime("%B %Y")
    
    if now.month == 12:
        next_mid = now.replace(year=now.year + 1, month=1, day=15, hour=12, minute=0, second=0)
    else:
        next_mid = now.replace(month=now.month + 1, day=15, hour=12, minute=0, second=0)
    next_month_str = next_mid.strftime("%B %Y")

    month_choice = st.radio(
        "**Select Forecast Month:**",
        options=[f"Current Month ({curr_month_str})", f"Next Month ({next_month_str})"],
        horizontal=True
    )
    
    target_date = next_mid if "Next Month" in month_choice else curr_mid
    pred = db.get_dynamic_monthly_prediction(lagna_idx, target_date)

    render_html(f"""
    <div class="auth-hero-box" style="margin-bottom:1.2rem;">
        <div style="font-size:0.85rem; color:#b45309; font-weight:800; text-transform:uppercase;">ASTROLOGICAL CLIMATE • {pred['month_name'].upper()}</div>
        <div style="font-size:1.05rem; font-weight:900; color:#92400e; margin-top:4px;">
            {pred['highlight']}
        </div>
    </div>

    <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:1.2rem;">
        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fed7aa; border-left:5px solid #f97316;">
            <b style="color:#9a3412; font-size:0.98rem;">🧘 1. Self & Vitality (Body, Physique, Energy):</b>
            <div style="font-size:0.92rem; color:#431407; margin-top:3px; line-height:1.6;">{pred['self']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bbf7d0; border-left:5px solid #10b981;">
            <b style="color:#065f46; font-size:0.98rem;">👨‍👩‍👦 2. Family & Accumulated Wealth (Liquid Assets & Speech):</b>
            <div style="font-size:0.92rem; color:#14532d; margin-top:3px; line-height:1.6;">{pred['family']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd; border-left:5px solid #0284c7;">
            <b style="color:#0369a1; font-size:0.98rem;">✈️ 3. Travels & Enterprise (Short Journeys, Siblings & Courage):</b>
            <div style="font-size:0.92rem; color:#0c4a6e; margin-top:3px; line-height:1.6;">{pred['travels']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fed7aa; border-left:5px solid #ea580c;">
            <b style="color:#9a3412; font-size:0.98rem;">🏡 4. Property, Vehicles & Domestic Peace (Land & Home):</b>
            <div style="font-size:0.92rem; color:#431407; margin-top:3px; line-height:1.6;">{pred['property']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fde68a; border-left:5px solid #f59e0b;">
            <b style="color:#b45309; font-size:0.98rem;">📚 5. Children & Higher Study (Intellect & Creative Strategy):</b>
            <div style="font-size:0.92rem; color:#78350f; margin-top:3px; line-height:1.6;">{pred['study']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fecdd3; border-left:5px solid #e11d48;">
            <b style="color:#9f1239; font-size:0.98rem;">📉 6. Loans, Debts & Health Defense (Immunity & Competitors):</b>
            <div style="font-size:0.92rem; color:#881337; margin-top:3px; line-height:1.6;">{pred['loan']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #ddd6fe; border-left:5px solid #8b5cf6;">
            <b style="color:#5b21b6; font-size:0.98rem;">💍 7. Spouse & Business Partnerships (Alliances & Contracts):</b>
            <div style="font-size:0.92rem; color:#3b0764; margin-top:3px; line-height:1.6;">{pred['spouse']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fecdd3; border-left:5px solid #be123c;">
            <b style="color:#9f1239; font-size:0.98rem;">🔬 8. Sudden Shifts, Research & Accidents Caution:</b>
            <div style="font-size:0.92rem; color:#881337; margin-top:3px; line-height:1.6;">{pred['research']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fde68a; border-left:5px solid #d97706;">
            <b style="color:#92400e; font-size:0.98rem;">🍀 9. Luck, Dharma & Mentorship (Higher Journeys & Fortune):</b>
            <div style="font-size:0.92rem; color:#78350f; margin-top:3px; line-height:1.6;">{pred['luck']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd; border-left:5px solid #0284c7;">
            <b style="color:#0369a1; font-size:0.98rem;">💼 10. Career, Job & Executive Stature (Authority & Standing):</b>
            <div style="font-size:0.92rem; color:#0c4a6e; margin-top:3px; line-height:1.6;">{pred['career']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bbf7d0; border-left:5px solid #059669;">
            <b style="color:#065f46; font-size:0.98rem;">💰 11. Gains, Inflows & Network Circles (Profits & Aspirations):</b>
            <div style="font-size:0.92rem; color:#14532d; margin-top:3px; line-height:1.6;">{pred['gains']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #ddd6fe; border-left:5px solid #6d28d9;">
            <b style="color:#5b21b6; font-size:0.98rem;">🌐 12. Expenditure, Foreign Linkages & Overseas Settlements:</b>
            <div style="font-size:0.92rem; color:#3b0764; margin-top:3px; line-height:1.6;">{pred['foreign']}</div>
        </div>
    </div>
    """)


# ==============================================================================
# TAB 8: VIMSHOTTARI DASHA (OPTION 3: NATIVE HYBRID TOKEN TEMPLATE ENGINE)
# ==============================================================================
DASHA_SEQ = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YRS = {
    "Ketu": 7.0, "Venus": 20.0, "Sun": 6.0, "Moon": 10.0, "Mars": 7.0, 
    "Rahu": 18.0, "Jupiter": 16.0, "Saturn": 19.0, "Mercury": 17.0
}

PLANET_NAMES_HI = {
    "Sun": "सूर्य (Surya)", "Moon": "चन्द्र (Chandra)", "Mars": "मंगल (Mangal)",
    "Rahu": "राहु (Rahu)", "Jupiter": "गुरु / बृहस्पति (Guru)", "Saturn": "शनि (Shani)",
    "Mercury": "बुध (Budha)", "Ketu": "केतु (Ketu)", "Venus": "शुक्र (Shukra)"
}

LAGNA_NAMES_HI = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क",
    "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
}

LAGNA_LORDS = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
    4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
    8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter"
}

NATURAL_FRIENDSHIPS = {
    "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "neutrals": ["Mercury"], "enemies": ["Venus", "Saturn", "Rahu", "Ketu"]},
    "Moon": {"friends": ["Sun", "Mercury"], "neutrals": ["Mars", "Jupiter", "Venus", "Saturn"], "enemies": ["Rahu", "Ketu"]},
    "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "neutrals": ["Venus", "Saturn"], "enemies": ["Mercury", "Rahu", "Ketu"]},
    "Mercury": {"friends": ["Sun", "Venus"], "neutrals": ["Mars", "Jupiter", "Saturn"], "enemies": ["Moon", "Rahu", "Ketu"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "neutrals": ["Saturn"], "enemies": ["Mercury", "Venus", "Rahu", "Ketu"]},
    "Venus": {"friends": ["Mercury", "Saturn", "Rahu", "Ketu"], "neutrals": ["Mars", "Jupiter"], "enemies": ["Sun", "Moon"]},
    "Saturn": {"friends": ["Mercury", "Venus", "Rahu"], "neutrals": ["Jupiter"], "enemies": ["Sun", "Moon", "Mars", "Ketu"]},
    "Rahu": {"friends": ["Venus", "Saturn", "Mercury"], "neutrals": ["Jupiter"], "enemies": ["Sun", "Moon", "Mars", "Ketu"]},
    "Ketu": {"friends": ["Mars", "Venus", "Jupiter"], "neutrals": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon", "Rahu"]}
}

# Lagna-specific functional roles and gemstone safety profiles
LAGNA_AFFILIATION_MAP = {
    0: {
        "Sun": {"role_en": "5th Lord (Trine)", "role_hi": "पंचमेश (त्रिकोण भाव अधिपति)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "4th Lord (Kendra)", "role_hi": "चतुर्थेश (केंद्र भाव अधिपति)", "gem_safe": True, "gem_en": "Natural Pearl (Moti)", "gem_hi": "सच्चा मोती (Pearl)"},
        "Mars": {"role_en": "Lagna & 8th Lord", "role_hi": "लग्नेश एवं अष्टमेश", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "3rd & 6th Lord", "role_hi": "तृतीयेश एवं षष्ठेश (त्रिक भाव)", "gem_safe": False},
        "Jupiter": {"role_en": "9th & 12th Lord", "role_hi": "नवमेश एवं द्वादशेश (भाग्येश)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Yellow Sapphire)"},
        "Venus": {"role_en": "2nd & 7th Lord", "role_hi": "द्वितीयेश एवं सप्तमेश (मारक भाव)", "gem_safe": False},
        "Saturn": {"role_en": "10th & 11th Lord", "role_hi": "दशमेश एवं एकादशेश", "gem_safe": False},
        "Rahu": {"role_en": "Upachaya Catalyst", "role_hi": "उपचय भाव विस्तारक", "gem_safe": False},
        "Ketu": {"role_en": "Moksha Catalyst", "role_hi": "मोक्ष एवं वैराग्य कारक", "gem_safe": False}
    },
    1: {
        "Sun": {"role_en": "4th Lord (Kendra)", "role_hi": "चतुर्थेश (सुख व भूमि भाव)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "3rd Lord", "role_hi": "तृतीयेश (पराक्रम भाव)", "gem_safe": False},
        "Mars": {"role_en": "7th & 12th Lord", "role_hi": "सप्तमेश एवं द्वादशेश (मारक व व्यय)", "gem_safe": False},
        "Mercury": {"role_en": "2nd & 5th Lord", "role_hi": "द्वितीयेश एवं पंचमेश (परम धन व बुद्धि कारक)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "8th & 11th Lord", "role_hi": "अष्टमेश एवं एकादशेश (त्रिक भाव)", "gem_safe": False},
        "Venus": {"role_en": "Lagna & 6th Lord", "role_hi": "लग्नेश एवं षष्ठेश", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / ओपल / सफेद जरकन"},
        "Saturn": {"role_en": "9th & 10th Lord", "role_hi": "नवमेश व दशमेश (परम राजयोगकारक)", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम / जामुनिया (Blue Sapphire)"},
        "Rahu": {"role_en": "Material Catalyst", "role_hi": "भौतिक उन्नति कारक", "gem_safe": False},
        "Ketu": {"role_en": "Introspective Catalyst", "role_hi": "आंतरिक अनुसंधान कारक", "gem_safe": False}
    },
    2: {
        "Sun": {"role_en": "3rd Lord", "role_hi": "तृतीयेश (उद्यम भाव)", "gem_safe": False},
        "Moon": {"role_en": "2nd Lord", "role_hi": "द्वितीयेश (धन व वाणी)", "gem_safe": False},
        "Mars": {"role_en": "6th & 11th Lord", "role_hi": "षष्ठेश एवं एकादशेश", "gem_safe": False},
        "Mercury": {"role_en": "Lagna & 4th Lord", "role_hi": "लग्नेश एवं चतुर्थेश", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "7th & 10th Lord", "role_hi": "सप्तमेश एवं दशमेश", "gem_safe": False},
        "Venus": {"role_en": "5th & 12th Lord", "role_hi": "पंचमेश एवं द्वादशेश (त्रिकोण कारक)", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / जरकन"},
        "Saturn": {"role_en": "8th & 9th Lord", "role_hi": "अष्टमेश एवं नवमेश (भाग्येश)", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम (Neelam)"},
        "Rahu": {"role_en": "Career Catalyst", "role_hi": "कर्म विस्तारक कारक", "gem_safe": False},
        "Ketu": {"role_en": "Analytical Catalyst", "role_hi": "विश्लेषणात्मक वैराग्य कारक", "gem_safe": False}
    },
    3: {
        "Sun": {"role_en": "2nd Lord", "role_hi": "द्वितीयेश (धन संचय)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "Lagna Lord", "role_hi": "लग्नेश (शरीर व आत्मबल)", "gem_safe": True, "gem_en": "Natural Pearl (Moti)", "gem_hi": "सच्चा मोती (Pearl)"},
        "Mars": {"role_en": "5th & 10th Lord", "role_hi": "पंचमेश व दशमेश (परम योगकारक)", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "3rd & 12th Lord", "role_hi": "तृतीयेश एवं द्वादशेश", "gem_safe": False},
        "Jupiter": {"role_en": "6th & 9th Lord", "role_hi": "षष्ठेश एवं नवमेश (भाग्य वृद्धि)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "4th & 11th Lord", "role_hi": "चतुर्थेश एवं एकादशेश (बाधक भाव)", "gem_safe": False},
        "Saturn": {"role_en": "7th & 8th Lord", "role_hi": "सप्तमेश एवं अष्टमेश (मारक व त्रिक)", "gem_safe": False},
        "Rahu": {"role_en": "Expansion Catalyst", "role_hi": "अप्रत्यक्ष विस्तारक", "gem_safe": False},
        "Ketu": {"role_en": "Intuition Catalyst", "role_hi": "आध्यात्मिक ज्ञान कारक", "gem_safe": False}
    },
    4: {
        "Sun": {"role_en": "Lagna Lord", "role_hi": "लग्नेश (ओज व आत्म संप्रभुता)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "12th Lord", "role_hi": "द्वादशेश (व्यय भाव)", "gem_safe": False},
        "Mars": {"role_en": "4th & 9th Lord", "role_hi": "चतुर्थेश व नवमेश (परम योगकारक)", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "2nd & 11th Lord", "role_hi": "द्वितीयेश एवं एकादशेश (परम धन कारक)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "5th & 8th Lord", "role_hi": "पंचमेश एवं अष्टमेश (ज्ञान व मंत्र सिद्धि)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "3rd & 10th Lord", "role_hi": "तृतीयेश एवं दशमेश", "gem_safe": False},
        "Saturn": {"role_en": "6th & 7th Lord", "role_hi": "षष्ठेश एवं सप्तमेश (मारक)", "gem_safe": False},
        "Rahu": {"role_en": "Scale Catalyst", "role_hi": "महत्वाकांक्षा विस्तारक", "gem_safe": False},
        "Ketu": {"role_en": "Detachment Catalyst", "role_hi": "अहंकार निवारक", "gem_safe": False}
    },
    5: {
        "Sun": {"role_en": "12th Lord", "role_hi": "द्वादशेश (व्यय व दूरस्थ संबंध)", "gem_safe": False},
        "Moon": {"role_en": "11th Lord", "role_hi": "एकादशेश (आय व लाभ भाव)", "gem_safe": False},
        "Mars": {"role_en": "3rd & 8th Lord", "role_hi": "तृतीयेश एवं अष्टमेश (अति पापी)", "gem_safe": False},
        "Mercury": {"role_en": "Lagna & 10th Lord", "role_hi": "लग्नेश एवं दशमेश (कुलदीपक योगकारक)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "4th & 7th Lord", "role_hi": "चतुर्थेश एवं सप्तमेश (केंद्राधिपति दोष)", "gem_safe": False},
        "Venus": {"role_en": "2nd & 9th Lord", "role_hi": "द्वितीयेश एवं नवमेश (परम भाग्य व धन कारक)", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / जरकन"},
        "Saturn": {"role_en": "5th & 6th Lord", "role_hi": "पंचमेश एवं षष्ठेश (त्रिकोण अधिपति)", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम (Neelam)"},
        "Rahu": {"role_en": "Tech Catalyst", "role_hi": "तकनीकी नवाचार कारक", "gem_safe": False},
        "Ketu": {"role_en": "Audit Catalyst", "role_hi": "गहन विश्लेषण कारक", "gem_safe": False}
    },
    6: {
        "Sun": {"role_en": "11th Lord", "role_hi": "एकादशेश (बाधक भाव)", "gem_safe": False},
        "Moon": {"role_en": "10th Lord", "role_hi": "दशमेश (कर्म व यश)", "gem_safe": True, "gem_en": "Natural Pearl (Moti)", "gem_hi": "सच्चा मोती (Pearl)"},
        "Mars": {"role_en": "2nd & 7th Lord", "role_hi": "द्वितीयेश एवं सप्तमेश (प्रबल मारक)", "gem_safe": False},
        "Mercury": {"role_en": "9th & 12th Lord", "role_hi": "नवमेश एवं द्वादशेश (भाग्य कारक)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "3rd & 6th Lord", "role_hi": "तृतीयेश एवं षष्ठेश (रोग व संघर्ष)", "gem_safe": False},
        "Venus": {"role_en": "Lagna & 8th Lord", "role_hi": "लग्नेश एवं अष्टमेश (शरीर व प्रतिष्ठा)", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / ओपल"},
        "Saturn": {"role_en": "4th & 5th Lord", "role_hi": "चतुर्थेश व पंचमेश (परम योगकारक)", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम (Neelam)"},
        "Rahu": {"role_en": "Visibility Catalyst", "role_hi": "वैश्विक प्रभाव कारक", "gem_safe": False},
        "Ketu": {"role_en": "Esoteric Catalyst", "role_hi": "गूढ़ साधना कारक", "gem_safe": False}
    },
    7: {
        "Sun": {"role_en": "10th Lord", "role_hi": "दशमेश (राजसत्ता व कीर्ति)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "9th Lord", "role_hi": "नवमेश (धर्म व भाग्य कारक)", "gem_safe": True, "gem_en": "Natural Pearl (Moti)", "gem_hi": "सच्चा मोती (Pearl)"},
        "Mars": {"role_en": "Lagna & 6th Lord", "role_hi": "लग्नेश एवं षष्ठेश (शत्रुहंता)", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "8th & 11th Lord", "role_hi": "अष्टमेश एवं एकादशेश", "gem_safe": False},
        "Jupiter": {"role_en": "2nd & 5th Lord", "role_hi": "द्वितीयेश एवं पंचमेश (महा धन कारक)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "7th & 12th Lord", "role_hi": "सप्तमेश एवं द्वादशेश (मारक व व्यय)", "gem_safe": False},
        "Saturn": {"role_en": "3rd & 4th Lord", "role_hi": "तृतीयेश एवं चतुर्थेश", "gem_safe": False},
        "Rahu": {"role_en": "Breakthrough Catalyst", "role_hi": "अकस्मात उन्नति कारक", "gem_safe": False},
        "Ketu": {"role_en": "Psychological Catalyst", "role_hi": "मानसिक शोधक कारक", "gem_safe": False}
    },
    8: {
        "Sun": {"role_en": "9th Lord", "role_hi": "नवमेश (परम भाग्य व धर्म कारक)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "8th Lord", "role_hi": "अष्टमेश (आयु व संकट)", "gem_safe": False},
        "Mars": {"role_en": "5th & 12th Lord", "role_hi": "पंचमेश एवं द्वादशेश (त्रिकोण कारक)", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "7th & 10th Lord", "role_hi": "सप्तमेश एवं दशमेश", "gem_safe": False},
        "Jupiter": {"role_en": "Lagna & 4th Lord", "role_hi": "लग्नेश एवं चतुर्थेश (परम शुभ)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "6th & 11th Lord", "role_hi": "षष्ठेश एवं एकादशेश (अति पापी)", "gem_safe": False},
        "Saturn": {"role_en": "2nd & 3rd Lord", "role_hi": "द्वितीयेश एवं तृतीयेश (मारक)", "gem_safe": False},
        "Rahu": {"role_en": "Expansion Catalyst", "role_hi": "ज्ञान व भौतिक विस्तारक", "gem_safe": False},
        "Ketu": {"role_en": "Liberation Catalyst", "role_hi": "आध्यात्मिक मुक्ति कारक", "gem_safe": False}
    },
    9: {
        "Sun": {"role_en": "8th Lord", "role_hi": "अष्टमेश (गूढ़ संकट व परिवर्तन)", "gem_safe": False},
        "Moon": {"role_en": "7th Lord", "role_hi": "सप्तमेश (मारक भाव)", "gem_safe": False},
        "Mars": {"role_en": "4th & 11th Lord", "role_hi": "चतुर्थेश एवं एकादशेश (बाधक)", "gem_safe": False},
        "Mercury": {"role_en": "6th & 9th Lord", "role_hi": "षष्ठेश एवं नवमेश (भाग्य वृद्धि)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "3rd & 12th Lord", "role_hi": "तृतीयेश एवं द्वादशेश", "gem_safe": False},
        "Venus": {"role_en": "5th & 10th Lord", "role_hi": "पंचमेश व दशमेश (परम राजयोगकारक)", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / ओपल"},
        "Saturn": {"role_en": "Lagna & 2nd Lord", "role_hi": "लग्नेश एवं द्वितीयेश (धन व सत्ता)", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम (Neelam)"},
        "Rahu": {"role_en": "Elevation Catalyst", "role_hi": "अभूतपूर्व उत्थान कारक", "gem_safe": False},
        "Ketu": {"role_en": "Mastery Catalyst", "role_hi": "आत्म-नियंत्रण कारक", "gem_safe": False}
    },
    10: {
        "Sun": {"role_en": "7th Lord", "role_hi": "सप्तमेश (मारक भाव)", "gem_safe": False},
        "Moon": {"role_en": "6th Lord", "role_hi": "षष्ठेश (रोग व ऋण भाव)", "gem_safe": False},
        "Mars": {"role_en": "3rd & 10th Lord", "role_hi": "तृतीयेश एवं दशमेश", "gem_safe": False},
        "Mercury": {"role_en": "5th & 8th Lord", "role_hi": "पंचमेश एवं अष्टमेश (बुद्धि व शोध)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "2nd & 11th Lord", "role_hi": "द्वितीयेश एवं एकादशेश (प्रबल धनेश)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "4th & 9th Lord", "role_hi": "चतुर्थेश व नवमेश (परम योगकारक)", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / ओपल"},
        "Saturn": {"role_en": "Lagna & 12th Lord", "role_hi": "लग्नेश एवं द्वादशेश", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम (Neelam)"},
        "Rahu": {"role_en": "Innovation Catalyst", "role_hi": "युगांतरकारी परिवर्तन कारक", "gem_safe": False},
        "Ketu": {"role_en": "Reformation Catalyst", "role_hi": "आध्यात्मिक शोधक", "gem_safe": False}
    },
    11: {
        "Sun": {"role_en": "6th Lord", "role_hi": "षष्ठेश (शत्रु व रोग भाव)", "gem_safe": False},
        "Moon": {"role_en": "5th Lord", "role_hi": "पंचमेश (त्रिकोण व विद्या कारक)", "gem_safe": True, "gem_en": "Natural Pearl (Moti)", "gem_hi": "सच्चा मोती (Pearl)"},
        "Mars": {"role_en": "2nd & 9th Lord", "role_hi": "द्वितीयेश एवं नवमेश (परम धन व भाग्य कारक)", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "4th & 7th Lord", "role_hi": "चतुर्थेश एवं सप्तमेश (केंद्राधिपति)", "gem_safe": False},
        "Jupiter": {"role_en": "Lagna & 10th Lord", "role_hi": "लग्नेश एवं दशमेश (कुलदीपक राजयोग)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "3rd & 8th Lord", "role_hi": "तृतीयेश एवं अष्टमेश (अति पापी)", "gem_safe": False},
        "Saturn": {"role_en": "11th & 12th Lord", "role_hi": "एकादशेश एवं द्वादशेश", "gem_safe": False},
        "Rahu": {"role_en": "Unconventional Catalyst", "role_hi": "अप्रत्यक्ष लाभ कारक", "gem_safe": False},
        "Ketu": {"role_en": "Moksha Catalyst", "role_hi": "मोक्ष व वैराग्य कारक", "gem_safe": False}
    }
}

REMEDIAL_PROTOCOLS = {
    "Sun": {
        "mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः (11 या 108 बार प्रातःकाल)",
        "deity": "भगवान सूर्य नारायण — प्रातःकाल तांबे के लोटे में रोली, अक्षत और लाल पुष्प डालकर सूर्य देव को अर्घ्य दें।",
        "fasting": "रविवार के दिन नमक रहित व्रत का पालन करें।",
        "charity": "गेहूं, गुड़, तांबे के पात्र अथवा लाल वस्त्र किसी योग्य ब्राह्मण या जरूरतमंद को दान करें।"
    },
    "Moon": {
        "mantra": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः (11 या 108 बार संध्या समय)",
        "deity": "भगवान शिव — प्रत्येक सोमवार को शिवलिंग पर कच्चा दूध, जल अथवा पंचामृत से रुद्राभिषेक करें।",
        "fasting": "सोमवार अथवा पूर्णिमा के दिन उपवास रखें।",
        "charity": "सफेद चावल, दूध, चांदी, मिश्री अथवा पीने के जल का दान करें।"
    },
    "Mars": {
        "mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः (11 या 108 बार एकाग्रचित्त होकर)",
        "deity": "श्री हनुमान जी अथवा कार्तिकेय जी — प्रतिदिन हनुमान चालीसा का पाठ करें और चमेली के तेल का दीपक जलाएं।",
        "fasting": "मंगलवार को नमक रहित व्रत रखें और तामसिक भोजन से पूर्णतः दूर रहें।",
        "charity": "लाल मसूर की दाल, तांबा अथवा रक्तदान कर जीवन रक्षा में सहयोग करें।"
    },
    "Rahu": {
        "mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः (11 या 108 बार सूर्यास्त के बाद)",
        "deity": "माँ दुर्गा अथवा काल भैरव — सायंकाल दुर्गा सप्तशती अथवा भैरव चालीसा का पाठ करें।",
        "fasting": "शनिवार को सात्विक आहार लें और संयम बरतें।",
        "charity": "काले कुत्ते को मीठी रोटी खिलाएं, सूखा नारियल बहते जल में प्रवाहित करें या काले कंबल का दान करें।"
    },
    "Jupiter": {
        "mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः (19 या 108 बार प्रातःकाल)",
        "deity": "भगवान श्री हरि विष्णु — विष्णु सहस्रनाम का पाठ करें और गुरुवार को केले अथवा पीपल के वृक्ष की सेवा करें।",
        "fasting": "गुरुवार को व्रत रखें और भोजन में चने की दाल या बेसन की पीली वस्तुओं का प्रयोग करें।",
        "charity": "चने की दाल, हल्दी, धार्मिक पुस्तकें अथवा पीले वस्त्र सुपात्र गुरुजन या मंदिर में अर्पित करें।"
    },
    "Saturn": {
        "mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः (11 या 108 बार सायंकाल)",
        "deity": "शनि देव अथवा महाकाल — शनिवार की शाम पीपल वृक्ष के नीचे सरसों के तेल का दीपक प्रज्वलित करें।",
        "fasting": "शनिवार को व्रत रखें और उड़द दाल की खिचड़ी का सेवन करें।",
        "charity": "काले तिल, सरसों का तेल, लोहे के बर्तन या जूते-चप्पल असहाय श्रमिकों को दान करें।"
    },
    "Mercury": {
        "mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः (11 या 108 बार प्रातःकाल)",
        "deity": "माँ सरस्वती अथवा भगवान विष्णु — ॐ नमो भगवते वासुदेवाय का जप करें और तुलसी दल अर्पित करें।",
        "fasting": "बुधवार को मूंग दाल युक्त सात्विक भोजन ग्रहण करें।",
        "charity": "बुधवार को गौमाता को हरा चारा, पालक अथवा हरी घास खिलाएं।"
    },
    "Ketu": {
        "mantra": "ॐ स्रां स्रीं स्रौं सः केतवे नमः (11 या 108 बार प्रातः अथवा रात्रि)",
        "deity": "विघ्नहर्ता भगवान श्री गणेश — गणेश जी को दूर्वा अर्पित करें और संकटनाशन गणेश स्तोत्र का पाठ करें।",
        "fasting": "मंगलवार या शनिवार को हल्का फलाहार रखें।",
        "charity": "स्ट्रीट डॉग्स को भोजन कराएं, दो-रंगी (चितकबरे) कंबल या काले-सफेद तिल का दान करें।"
    },
    "Venus": {
        "mantra": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः (16 या 108 बार संध्या समय)",
        "deity": "माँ महालक्ष्मी — शुक्रवार को श्री सूक्त या कनकधारा स्तोत्र का पाठ कर देशी घी का दीपक जलाएं।",
        "fasting": "शुक्रवार को नमक व खटाई रहित खीर का सेवन करें।",
        "charity": "शुद्ध देशी घी, कपूर, दही, मिश्री अथवा सफेद रेशमी वस्त्र किसी वृद्ध स्त्री को दान करें।"
    }
}

# Universal Archetypal Forecasts (English & Authentic Classical Hindi)
DASHA_DETAILED_FORECASTS = {
    "Sun": {
        "md_en": "The Mahadasha of the Sun establishes a monumental multi-year epoch focused on sovereign authority, organizational leadership, and executive consolidation. Under this solar cycle, passive execution gives way to direct administrative accountability. You are compelled to step into roles demanding executive decision-making, visibility before key authorities, and clear ethical alignment. In career domains, this era rewards institutional compliance, transparent capital management, and decisive leadership. Financial growth stems from steady, structured advancement rather than hasty speculation. On a psychological level, it develops resolute confidence but cautions against egoic friction with peers or superiors. Health requires monitoring bodily heat, cardiovascular stamina, and eye wellness through balanced discipline.",
        "md_hi": "सूर्य की यह महादशा आपके जीवन में स्वावलंबन, प्रशासनिक प्रतिष्ठा, आत्मविश्वास और कार्यक्षेत्र में संप्रभु नेतृत्व का एक विशाल युग स्थापित करती है। इस सौर चक्र के प्रभाव से आपके भीतर निर्णय लेने की क्षमता और कार्यपालिका शक्ति का अभूतपूर्व विकास होता है। यदि यह ग्रह आपकी कुंडली में शुभ भावों का स्वामी है, तो उच्चाधिकारियों, शासन-प्रशासन और समाज के प्रबुद्ध वर्ग से पूर्ण सहयोग प्राप्त होता है। वित्तीय दृष्टिकोण से यह समय दीर्घकालिक पूंजी निर्माण, पैतृक संपत्ति के संरक्षण और प्रतिष्ठा से जुड़े कार्यों में स्थिरता प्रदान करता है। आपको अपने व्यक्तिगत अहंकार, उच्चाधिकारियों से वैचारिक टकराव और पित्त प्रकृति के रोगों (रक्तचाप, नेत्र विकार) से सजग रहने की आवश्यकता है। सूर्योपासना से मान-सम्मान में निरंतर वृद्धि होगी।",
        "ad_en": "During this Sun sub-period, tactical responsibilities accelerate rapidly. Decisions regarding managerial promotions, legal documentation, and organizational visibility come to the forefront. It demands transparent communication and disciplined execution.",
        "ad_hi": "सूर्य की इस अंतर्दशा के दौरान दैनिक कार्यक्षेत्र में आपकी भूमिका और दृश्यता तीव्र हो जाती है। पदोन्नति, प्रशासनिक निर्णय और उत्तरदायित्वों में त्वरित परिवर्तन देखने को मिलते हैं। अहंकार से बचते हुए स्पष्ट एवं पारदर्शी कार्यशैली अपनाना ही सफलता की कुंजी है।"
    },
    "Moon": {
        "md_en": "The Mahadasha of the Moon inaugurates an intensely foundational decade governing emotional intelligence, public trust, domestic assets, and intuitive strategy. The lunar archetype operates through cyclical momentum; hence, this era demands emotional resilience and adaptive versatility. Professional advancement is heavily linked to public relations, organizational branding, human capital management, and real estate stabilization. Capital reserves compound best when protected against emotional or impulsive spending. Psychologically, your intuition, maternal bonding, and protective impulses are heightened, but boundary management is necessary to avoid mental fatigue. Health maintenance focuses on lymphatic hydration, restful sleep cycles, and grounding routines.",
        "md_hi": "चन्द्रमा की यह 10-वर्षीय महादशा मानसिक शांति, जनसंपर्क, गृह-संपत्ति, मातृसुख और बौद्धिक संवेदनशीलता का एक अत्यंत महत्वपूर्ण आधारभूत कालखंड है। चन्द्रमा का प्रभाव जीवन में उतार-चढ़ाव और निरंतर गतिशीलता लाता है, अतः इस युग में धैर्य और मानसिक संतुलन अत्यंत आवश्यक है। कार्यक्षेत्र में जनता, ग्राहकों, टीम प्रबंधन और संस्थागत साख से जुड़े क्षेत्रों में उल्लेखनीय प्रगति होती है। भूमि, भवन और वाहन से संबंधित निवेश अनुकूल परिणाम देते हैं। अत्यधिक भावुकता, अनिद्रा, जल जनित रोग और कफ विकारों से सावधान रहना चाहिए। शिव साधना और ध्यान से इस महादशा में अपार मानसिक शांति और स्थिरता प्राप्त होती है।",
        "ad_en": "This Moon sub-period centers immediate tactical focus on domestic stabilization, workplace empathy, and flexible planning. Favorable for building supportive team relationships and managing liquid capital.",
        "ad_hi": "चन्द्रमा की इस अंतर्दशा में तात्कालिक प्राथमिकताएं गृह-परिवार के सामंजस्य, मानसिक प्रसन्नता और कार्यस्थल पर सहयोगियों के साथ विश्वास सुदृढ़ करने पर केंद्रित रहती हैं। वित्तीय लेन-देन में भावुक निर्णयों से बचें।"
    },
    "Mars": {
        "md_en": "The Mahadasha of Mars commands a fast-paced, high-stakes 7-year chapter characterized by decisive action, courage, competitive triumph, and technical enterprise. Under this martian vibration, hesitation is replaced by intense operational drive. Career progress is fueled by conquering market rivals, spearheading ambitious infrastructure or real estate initiatives, and resolving overdue liabilities. Wealth compounding thrives when channelled into tangible assets and calculated, vetted industrial investments. Strategic caution is vital against impulsive aggression, volatile confrontations, and contractual haste. Physical endurance is high, but safeguard against inflammation, muscular strain, and accident risks through mindful scheduling.",
        "md_hi": "मंगल की यह 7-वर्षीय महादशा पराक्रम, अदम्य साहस, प्रतिस्पर्धी विजय, भूमि-संपत्ति और तकनीकी पुरुषार्थ का एक अत्यंत ऊर्जावान कालखंड है। इस युग में आपके निर्णय लेने की गति तीव्र होती है और आप कठिन चुनौतियों व शत्रुओं पर विजय प्राप्त करने में सक्षम होते हैं। रियल एस्टेट, निर्माण, प्रबंधन, विधि और तकनीकी उद्यमों में अप्रत्याशित सफलता मिलती है। वित्तीय दृष्टिकोण से यह समय साहसिक किंतु संयमित निवेश द्वारा संपत्ति अर्जन का है। उग्र वाणी, जल्दबाजी, पारिवारिक विवादों और रक्त/अग्नि संबंधित दुर्घटनाओं से विशेष सावधानी बरतनी चाहिए। हनुमान जी की नियमित उपासना आपको अजेय सुरक्षा प्रदान करेगी।",
        "ad_en": "The active Mars sub-period acts as a high-octane catalyst, accelerating urgent deliverables and competitive benchmarks. Focus squarely on decisive resolution without entering unnecessary friction.",
        "ad_hi": "मंगल की इस अंतर्दशा में दैनिक गतिशीलता और कार्य का दबाव बढ़ जाता है। रुके हुए कार्यों को पूरा करने और प्रतिस्पर्धियों को पीछे छोड़ने के लिए यह उत्कृष्ट समय है, बशर्ते आप क्रोध और जल्दबाजी पर अंकुश रखें।"
    },
    "Rahu": {
        "md_en": "The Mahadasha of Rahu initiates a transformative 18-year epoch of boundary-breaking material ambition, foreign linkages, unorthodox scaling, and technological disruption. Rahu refuses conventional limitations, propelling you into unfamiliar ecosystems, innovative ventures, and cross-border commercial networks. Professional expansion often occurs in dramatic, exponential surges rather than linear increments. However, this illusionary catalyst commands strict risk governance: beware of unvetted speculative schemes, toxic sycophants, and sudden psychological restlessness. Channeling Rahu's obsessive drive into structured, ethical enterprise yields massive material elevation while preserving peace of mind.",
        "md_hi": "राहु की यह 18-वर्षीय महादशा अप्रत्याशित विस्तार, वैश्विक संपर्कों, तकनीकी नवाचार, महत्वाकांक्षा और जीवन में अभूतपूर्व मोड़ों का एक चमत्कारी कालखंड है। राहु परंपरागत सीमाओं को तोड़कर आपको नए अवसरों, विदेशी संपर्कों और आधुनिक प्रणालियों की ओर अग्रसर करता है। कार्यक्षेत्र में अचानक बड़ी उपलब्धियां और पद-प्रतिष्ठा में वृद्धि संभव है। किंतु यह छाया ग्रह भ्रम और लालच का कारक भी है; अतः रातों-रात अमीर बनने की योजनाओं, अनैतिक प्रलोभनों और गोपनीय शत्रुओं से अत्यधिक सतर्क रहना अनिवार्य है। दुर्गा सप्तशती और सात्विक दिनचर्या राहु के नकारात्मक प्रभावों को निर्मल कर देती है।",
        "ad_en": "During this Rahu sub-period, expect sudden tactical pivots, unconventional ideas, and digital or foreign possibilities. Meticulously verify all fine print before committing capital.",
        "ad_hi": "राहु की इस अंतर्दशा में अप्रत्याशित सूचनाएं और अचानक यात्राएं या योजनाएं बन सकती हैं। किसी भी नए अनुबंध पर हस्ताक्षर करने से पूर्व कानूनी और वित्तीय पहलुओं की गहन जांच अवश्य करें।"
    },
    "Jupiter": {
        "md_en": "The Mahadasha of Jupiter ushers in a golden 16-year era of philosophical expansion, institutional prestige, wealth compounding, and righteous counsel. Governed by the supreme benefic Guru, this chapter anchors long-term prosperity through ethical governance, higher learning, and institutional mentorship. Professional ventures gain gravitas; your advice is sought after, and financial structures achieve permanent compound stability. Children, legacy projects, and spiritual pilgrimages flourish. Cautions involve guarding against blind optimism, over-leveraging capital on optimistic forecasts, and liver or metabolic lethargy. Maintaining strict intellectual and dietary discipline guarantees sustained grace.",
        "md_hi": "बृहस्पति (गुरु) की यह 16-वर्षीय महादशा ज्ञान, विवेक, आर्थिक सुदृढ़ता, आध्यात्मिक उन्नति और संतान सुख का एक अत्यंत शुभ व गरिमामय युग है। देवगुरु की कृपा से समाज और कार्यक्षेत्र में आपका सम्मान बढ़ता है, वरिष्ठों व मार्गदर्शकों का आशीर्वाद प्राप्त होता है, और स्थायी संपत्ति का संचय होता है। शिक्षा, परामर्श, वित्त, न्याय और लोक-कल्याणकारी कार्यों में असाधारण प्रगति होती है। यह कालखंड संचित पुण्यों के उदय का है। अति-आशावादिता, अनुचित वित्तीय जोखिम और स्वास्थ्य में यकृत (लिवर) या मोटापे से संबंधित विकारों से सचेत रहना चाहिए। विष्णु आराधना से जीवन में निरंतर शुभता प्रवाहित होती है।",
        "ad_en": "The active Jupiter sub-period brings protective tactical grace, ethical clarity, and favorable financial arrangements. Excellent for launching educational, legal, or advisory milestones.",
        "ad_hi": "गुरु की इस अंतर्दशा में तात्कालिक समस्याओं का समाधान विवेकपूर्ण संवाद से होता है। यह समय नई योजनाओं के शुभारंभ, वित्तीय निवेश और पारिवारिक मांगलिक कार्यों के लिए अत्यंत अनुकूल है।"
    },
    "Saturn": {
        "md_en": "The Mahadasha of Saturn commands a profound 19-year masterclass in karmic accountability, structural discipline, organizational grit, and permanent legacy building. Saturn strips away superficial shortcuts, demanding meticulous labor, procedural integrity, and unyielding patience. While early phases often impose heavy operational burdens and delayed gratification, the structures forged during this era become indestructible anchors of permanent success. Capital must be allocated with extreme conservatism and zero speculative leverage. Health discipline requires attention to joint mobility, posture, and neurological stress through consistent restorative habits.",
        "md_hi": "शनिदेव की यह 19-वर्षीय महादशा कर्म शुद्धि, कठोर परिश्रम, अनुशासन, धैर्य और जीवन में स्थायी नींव रखने का एक गहरा आध्यात्मिक व व्यावहारिक कालखंड है। शनिदेव न्याय के अधिष्ठाता हैं; अतः यह युग किसी भी प्रकार के शॉर्टकट या अनैतिक आचरण को स्वीकार नहीं करता। प्रारंभिक रूप से कार्यभार और जिम्मेदारियां बढ़ सकती हैं, किंतु आपकी निष्ठा और संयम आपको दीर्घकालिक स्थायी सफलता, सत्ता और सम्मान प्रदान करते हैं। वित्तीय प्रबंधन में अत्यधिक मितव्ययिता बरतें। जोड़ों के दर्द, वात रोग, अवसाद और मानसिक तनाव से बचने के लिए नियमित योग व शनि साधना अनिवार्य है।",
        "ad_en": "The active Saturn sub-period demands rigorous attention to detail, operational audits, and patient stamina. Eliminate workflow redundancies and respect structural timelines.",
        "ad_hi": "शनि की इस अंतर्दशा में कार्यस्थल पर अनुशासन और दायित्वों की समीक्षा आवश्यक हो जाती है। परिणाम आने में भले ही थोड़ा विलंब हो, किंतु आपकी निरंतर मेहनत अंततः ठोस और स्थायी परिणाम देगी।"
    },
    "Mercury": {
        "md_en": "The Mahadasha of Mercury unfolds a versatile, intellectually stimulating 17-year chapter focused on commercial expansion, data synthesis, negotiation mastery, and communications. Under Mercury’s analytical stewardship, your mind operates at maximum agility. Professional gains materialize through digital media, cross-functional trade, legal contracts, and intellectual networking. Wealth thrives through diversified liquid asset allocations and calculated trading strategies. The primary hazards are cognitive burnout, nervous anxiety, and scattered priorities caused by over-multitasking. Grounding mental chatter through meditation and nature resets restores peak clarity.",
        "md_hi": "बुध की यह 17-वर्षीय महादशा व्यापारिक विस्तार, बौद्धिक चातुर्य, संचार कौशल, लेखन और विश्लेषणात्मक दक्षता का एक अत्यंत गतिशील युग है। बुध की कृपा से निर्णय क्षमता में तीव्रता आती है, व्यापार और साझेदारी के नए मार्ग प्रशस्त होते हैं, और बौद्धिक संपदा का विकास होता है। वाणिज्य, वित्त, मीडिया, सूचना प्रौद्योगिकी और जनसंचार से जुड़े लोगों के लिए यह कालखंड स्वर्णिम सिद्ध होता है। अत्यधिक मानसिक कार्य से स्नायु दुर्बलता (नर्वस सिस्टम) और त्वचा संबंधी विकारों से सावधान रहें। गौसेवा और गणेश जी की आराधना से व्यापार व बुद्धि में तीव्र प्रगति होती है।",
        "ad_en": "During this Mercury sub-period, correspondence, documentation, and verbal diplomacy take center stage. Execute contracts cleanly and maintain precise data hygiene.",
        "ad_hi": "बुध की इस अंतर्दशा में दैनिक कार्यों में संवाद, व्यापारिक यात्राएं और लिखा-पढ़ी के कार्य बढ़ जाते हैं। किसी भी दस्तावेज़ पर विचार-विमर्श के उपरांत ही सहमति दें।"
    },
    "Ketu": {
        "md_en": "The Mahadasha of Ketu represents a profound 7-year spiritual crucible dedicated to root-cause investigation, metaphysical research, psychological purification, and detachment from obsolete constructs. Ketu dissolves superficial attachments, compelling you to seek higher self-mastery. In professional domains, routine bureaucratic vanity loses appeal, shifting focus toward deep specialist research, technical troubleshooting, or autonomous advisory roles. Financial preservation demands conservative security rather than expansionist enterprise. Guard against sudden escapism, erratic decisions, and contractual ambiguity through grounded self-discipline.",
        "md_hi": "केतु की यह 7-वर्षीय महादशा आत्म-निरीक्षण, गूढ़ विद्याओं, आध्यात्मिक अनुसंधान, वैराग्य और भौतिक बंधनों के शोधन का एक पवित्र कालखंड है। केतु पुरानी और निरर्थक व्यवस्थाओं को समाप्त कर जीवन में एक नई चेतना का संचार करता है। कार्यक्षेत्र में नियमित चमक-दमक के स्थान पर गहन तकनीकी शोध, एकांत चिंतन और स्वतंत्र परामर्श में अभूतपूर्व सफलता मिलती है। भौतिक योजनाओं में अचानक बदलाव आ सकते हैं; अतः अनुबंधों में पूर्ण स्पष्टता रखें। मानसिक भटकाव और अज्ञात भय से बचने के लिए गणेश उपासना और ध्यान का आश्रय लेना सर्वश्रेष्ठ रहता है।",
        "ad_en": "This Ketu sub-period brings moments of introspection and subtle course-corrections. Rely on gut intuition while ensuring practical safeguards remain anchored.",
        "ad_hi": "केतु की इस अंतर्दशा में आपका मन आत्म-मंथन और एकांत की ओर प्रवृत्त हो सकता है। तात्कालिक योजनाओं को शांत भाव से परखें और जल्दबाजी में कोई संबंध या कार्य न छोड़ें।"
    },
    "Venus": {
        "md_en": "The Mahadasha of Venus commands an expansive 20-year cycle dedicated to material comforts, harmonious alliances, creative mastery, and refined aesthetic wealth. Governed by Daityaguru Shukra, this epoch unlocks access to luxury conveyances, domestic beautification, artistic fulfillment, and mutually enriching partnerships. Executive authority is achieved through soft power, diplomacy, and persuasive negotiation rather than brute force. Financial capital compounds through strategic alliances, high-value consumer assets, and creative design. Strategic caution centers on financial over-indulgence, vanity, and interpersonal dependency. Living with elegant restraint preserves peak harmony.",
        "md_hi": "शुक्र की यह 20-वर्षीय महादशा भौतिक ऐश्वर्य, कलात्मक सुरुचि, वाहन-सुख, मधुर संबंधों और जीवन में सुख-समृद्धि का एक अत्यंत वैभवशाली युग है। शुक्राचार्य की कृपा से जीवनशैली में गुणात्मक सुधार आता है, व्यापारिक साझेदारियों और दांपत्य जीवन में प्रगाढ़ता आती है, और नए संपत्तियों का अर्जन होता है। कूटनीति, सौंदर्य, विलासिता और रचनात्मक क्षेत्रों में भारी लाभ मिलता है। वित्तीय मामलों में अत्यधिक विलासिता, फिजूलखर्ची और आत्म-मुग्धता से बचना आवश्यक है। माँ महालक्ष्मी की नित्य आराधना इस महादशा में निरंतर सुख और अखंड लक्ष्मी की प्राप्ति कराती है।",
        "ad_en": "The active Venus sub-period refines immediate negotiations, social engagements, and domestic upgrades. Excellent for formalizing collaborations and resolving interpersonal friction.",
        "ad_hi": "शुक्र की इस अंतर्दशा में सामाजिक दायरे का विस्तार, कलात्मक कार्यों में रुचि और पारिवारिक सुख में वृद्धि होती है। वित्तीय सौदों में संयम बनाए रखें।"
    }
}

def generate_relationship_statements(lagna_idx: int, md_lord: str, ad_lord: str, is_hi: bool):
    lagna_lord = LAGNA_LORDS.get(lagna_idx, "Mars")
    lagna_aff = LAGNA_AFFILIATION_MAP.get(lagna_idx, {})
    
    md_aff = lagna_aff.get(md_lord, {"role_en": "Influence", "role_hi": "प्रभाव", "gem_safe": False})
    ad_aff = lagna_aff.get(ad_lord, {"role_en": "Influence", "role_hi": "प्रभाव", "gem_safe": False})
    
    md_name = PLANET_NAMES_HI[md_lord] if is_hi else md_lord
    ad_name = PLANET_NAMES_HI[ad_lord] if is_hi else ad_lord
    l_lord_name = PLANET_NAMES_HI[lagna_lord] if is_hi else lagna_lord
    
    md_role = md_aff['role_hi'] if is_hi else md_aff['role_en']
    ad_role = ad_aff['role_hi'] if is_hi else ad_aff['role_en']

    # 1. MD to Lagna
    md_friends = NATURAL_FRIENDSHIPS.get(md_lord, {}).get("friends", [])
    md_enemies = NATURAL_FRIENDSHIPS.get(md_lord, {}).get("enemies", [])
    if md_lord == lagna_lord:
        md_lagna_rel = f"महादशा स्वामी **{md_name}** स्वयं आपके **लग्नेश** हैं ({md_role})। यह कालखंड आत्मबल, शारीरिक आरोग्यता और व्यक्तिगत संप्रभुता के लिए अत्यंत फलदायी है।" if is_hi else f"The Mahadasha lord **{md_lord}** is your **Lagna Lord** ({md_role}). This establishes an era of personal empowerment and autonomy."
    elif lagna_lord in md_friends:
        md_lagna_rel = f"महादशा स्वामी **{md_name}** आपके लग्नेश {l_lord_name} के **प्राकृतिक मित्र** हैं तथा आपकी कुंडली में **{md_role}** का दायित्व संभालते हैं। यह संबंध करियर और जीवन में स्वाभाविक प्रगति और अनुकूल वातावरण प्रदान करता है।" if is_hi else f"The Mahadasha lord **{md_lord}** is a **natural ally** to your Lagna lord {l_lord_name} ({md_role}), supporting career stability and steady growth."
    elif lagna_lord in md_enemies:
        md_lagna_rel = f"महादशा स्वामी **{md_name}** आपके लग्नेश {l_lord_name} के **शत्रु ग्रह** हैं और कुंडली में **{md_role}** के रूप में स्थित हैं। यह कालखंड संयम, निरंतर सतर्कता और अनुशासित योजना की मांग करता है।" if is_hi else f"The Mahadasha lord **{md_lord}** is a **functional adversary** to your Lagna lord {l_lord_name} ({md_role}), demanding patient resilience and risk management."
    else:
        md_lagna_rel = f"महादशा स्वामी **{md_name}** आपके लग्नेश {l_lord_name} के प्रति **सम (तटस्थ)** भाव रखते हैं तथा **{md_role}** का कार्य करते हैं। परिणाम आपके निजी प्रयासों और कर्म पर निर्भर करेंगे।" if is_hi else f"The Mahadasha lord **{md_lord}** is **neutral** toward your Lagna lord {l_lord_name} ({md_role}). Outcomes depend directly on personal effort."

    # 2. AD to Lagna
    ad_friends = NATURAL_FRIENDSHIPS.get(ad_lord, {}).get("friends", [])
    ad_enemies = NATURAL_FRIENDSHIPS.get(ad_lord, {}).get("enemies", [])
    if ad_lord == lagna_lord:
        ad_lagna_rel = f"अंतर्दशा स्वामी **{ad_name}** आपके **लग्नेश** हैं ({ad_role})। यह समय आपके स्वास्थ्य, व्यक्तिगत निर्णयों और मान-सम्मान को प्रत्यक्ष रूप से सशक्त करता है।" if is_hi else f"The Antardasha lord **{ad_lord}** is your **Lagna Lord** ({ad_role}), revitalizing self-identity and physical energy."
    elif lagna_lord in ad_friends:
        ad_lagna_rel = f"अंतर्दशा स्वामी **{ad_name}** आपके लग्नेश के **मित्र** हैं ({ad_role})। यह दैनिक कार्यों को सुगम बनाता है और कार्यक्षेत्र में सहयोग प्राप्त कराता है।" if is_hi else f"The Antardasha lord **{ad_lord}** is an **ally to your Lagna lord** ({ad_role}), smoothing daily initiatives."
    elif lagna_lord in ad_enemies:
        ad_lagna_rel = f"अंतर्दशा स्वामी **{ad_name}** आपके लग्नेश के **शत्रु** हैं ({ad_role})। तात्कालिक परिस्थितियों में थोड़ा मानसिक तनाव अथवा अवरोध संभव है।" if is_hi else f"The Antardasha lord **{ad_lord}** is an **adversary to your Lagna lord** ({ad_role}), introducing short-term operational hurdles."
    else:
        ad_lagna_rel = f"अंतर्दशा स्वामी **{ad_name}** आपके लग्नेश के प्रति **सम** हैं ({ad_role})। दिनचर्या सामान्य और संतुलित रहेगी।" if is_hi else f"The Antardasha lord **{ad_lord}** is **neutral** to your Lagna lord ({ad_role}), maintaining steady daily rhythm."

    # 3. AD to MD Relationship
    ad_rel_friends = NATURAL_FRIENDSHIPS.get(ad_lord, {}).get("friends", [])
    ad_rel_enemies = NATURAL_FRIENDSHIPS.get(ad_lord, {}).get("enemies", [])
    if ad_lord == md_lord:
        ad_md_rel = f"अंतर्दशा स्वामी **{ad_name}** स्वयं महादशा स्वामी हैं (स्व-भुक्ति)। इस ग्रह का मूल प्रभाव बिना किसी रुकावट के पूर्ण क्षमता से कार्य करेगा।" if is_hi else f"The Antardasha lord **{ad_lord}** is identical to the Mahadasha lord (Sva-Bhukti), operating at full archetypal strength."
    elif md_lord in ad_rel_friends:
        ad_md_rel = f"अंतर्दशा स्वामी **{ad_name}** एवं महादशा स्वामी **{md_name}** के मध्य **परस्पर मित्रता** है। दोनों ग्रह सामंजस्य से कार्य करेंगे जिससे योजनाओं में त्वरित गति आएगी।" if is_hi else f"The Antardasha lord **{ad_lord}** is a **friend** to Mahadasha lord **{md_lord}**, allowing long-term projects to advance smoothly."
    elif md_lord in ad_rel_enemies:
        ad_md_rel = f"अंतर्दशा स्वामी **{ad_name}** एवं महादशा स्वामी **{md_name}** के मध्य **परस्पर शत्रुता** है। दीर्घकालिक लक्ष्यों और तात्कालिक प्राथमिकताओं में थोड़ा द्वंद्व रह सकता है।" if is_hi else f"The Antardasha lord **{ad_lord}** is an **adversary** to Mahadasha lord **{md_lord}**, requiring balance between macro and immediate priorities."
    else:
        ad_md_rel = f"अंतर्दशा स्वामी **{ad_name}** एवं महादशा स्वामी **{md_name}** के मध्य **तटस्थ संबंध** है। कार्य सुचारू रूप से आगे बढ़ेंगे।" if is_hi else f"The Antardasha lord **{ad_lord}** holds a **neutral** relationship with Mahadasha lord **{md_lord}**, maintaining steady progress."

    return md_lagna_rel, ad_lagna_rel, ad_md_rel, md_aff, ad_aff

def format_remedial_protocol(planet_name: str, aff_dict: dict, is_hi: bool) -> str:
    rem = REMEDIAL_PROTOCOLS.get(planet_name, {})
    lines = []
    
    if is_hi:
        if aff_dict.get("gem_safe", False):
            lines.append(f"<b>💎 अनुशंसित रत्न:</b> {aff_dict.get('gem_hi')} (शुभ मुहूर्त में विधिपूर्वक धारण करें)")
        else:
            lines.append(f"<b>⚠️ रत्न परामर्श:</b> आपकी कुंडली अनुसार {PLANET_NAMES_HI[planet_name]} त्रिक अथवा मारक भाव के स्वामी हैं; अतः <b>रत्न धारण वर्जित है</b>। अनिष्ट ग्रहों का रत्न धारण करने से रुकावटें बढ़ सकती हैं। केवल सात्विक पूजा व मंत्र जप करें:")
        
        lines.append(f"<b>📿 बीज मंत्र:</b> {rem.get('mantra')}")
        lines.append(f"<b>🪔 शास्त्रीय देव आराधना:</b> {rem.get('deity')}")
        lines.append(f"<b>🍲 उपवास व आहार नियम:</b> {rem.get('fasting')}")
        lines.append(f"<b>🤝 निर्धारित दान:</b> {rem.get('charity')}")
    else:
        p_name_en = planet_name
        if aff_dict.get("gem_safe", False):
            lines.append(f"<b>💎 Prescribed Vedic Gemstone:</b> {aff_dict.get('gem_en')} worn on recommended finger after expert trial.")
        else:
            lines.append(f"<b>⚠️ Gemstone Advisory:</b> Because {p_name_en} governs functional dusthana or maraka houses for your Ascendant, <b>gemstones are strictly not recommended</b>. Use the following non-invasive, sattvic protocols instead:")
        
        lines.append(f"<b>📿 Authentic Beej Mantra:</b> {rem.get('mantra')}")
        lines.append(f"<b>🪔 Classical Deity Sadhana:</b> {rem.get('deity')}")
        lines.append(f"<b>🍲 Dietary & Fasting Discipline:</b> {rem.get('fasting')}")
        lines.append(f"<b>🤝 Prescribed Charitable Action (Daan):</b> {rem.get('charity')}")
        
    return "<br><br>".join(lines)

def local_add_years(dt: datetime.datetime, years: float) -> datetime.datetime:
    return dt + datetime.timedelta(days=years * 365.2425)

def local_calculate_live_dasha(birth_dt: datetime.datetime, moon_lon: float, target_dt: datetime.datetime):
    star_span = 360.0 / 27.0
    star_idx = int(moon_lon / star_span)
    start_lord_idx = star_idx % 9
    
    elapsed_deg = moon_lon - (star_idx * star_span)
    fraction_left = max(0.0, min(1.0, 1.0 - (elapsed_deg / star_span)))
    
    start_lord = DASHA_SEQ[start_lord_idx]
    balance_years = DASHA_YRS[start_lord] * fraction_left
    
    md_idx = start_lord_idx
    md_start = birth_dt
    md_years = balance_years
    md_end = local_add_years(md_start, md_years)
    
    while target_dt > md_end:
        md_start = md_end
        md_idx = (md_idx + 1) % 9
        current_lord = DASHA_SEQ[md_idx]
        md_years = DASHA_YRS[current_lord]
        md_end = local_add_years(md_start, md_years)
        
    current_md_lord = DASHA_SEQ[md_idx]
    
    # Sub-periods (Antardasha)
    curr_ad_st = md_start
    active_ad = ("Ketu", md_years, md_start, md_end)
    for i in range(9):
        sub_lord = DASHA_SEQ[(md_idx + i) % 9]
        sub_yrs = (md_years * DASHA_YRS[sub_lord]) / 120.0
        sub_ed = local_add_years(curr_ad_st, sub_yrs)
        if curr_ad_st <= target_dt <= sub_ed:
            active_ad = (sub_lord, sub_yrs, curr_ad_st, sub_ed)
            break
        curr_ad_st = sub_ed
    else:
        active_ad = (sub_lord, sub_yrs, curr_ad_st, sub_ed)
        
    return [
        {"level": "Mahadasha", "lord": current_md_lord, "start": md_start, "end": md_end},
        {"level": "Antardasha", "lord": active_ad[0], "start": active_ad[2], "end": active_ad[3]}
    ]

def render_page_dasha():
    if not has_valid_profile:
        render_profile_setup_prompt()
        return

    is_hi = (current_lang == "hi")
    birth_ist = datetime.datetime.combine(dob_parsed, tob_parsed)
    now_ist = datetime.datetime.now()
    
    # Calculate live dasha levels
    dasha_levels = local_calculate_live_dasha(birth_ist, chart_info['moon_lon'], now_ist)
    md_item = dasha_levels[0]
    ad_item = dasha_levels[1]
    
    # Next Transitions
    next_ad_target = ad_item['end'] + datetime.timedelta(days=2)
    next_ad_levels = local_calculate_live_dasha(birth_ist, chart_info['moon_lon'], next_ad_target)
    next_ad_item = next_ad_levels[1]

    next_md_target = md_item['end'] + datetime.timedelta(days=2)
    next_md_levels = local_calculate_live_dasha(birth_ist, chart_info['moon_lon'], next_md_target)
    next_md_item = next_md_levels[0]

    lagna_idx = chart_info['lagna_idx']
    raw_lagna_name = chart_info['lagna_name']
    display_lagna = f"{LAGNA_NAMES_HI.get(raw_lagna_name, raw_lagna_name)} लग्न" if is_hi else f"{raw_lagna_name} Ascendant"

    md_lagna_rel, ad_lagna_rel, ad_md_rel, md_aff, ad_aff = generate_relationship_statements(
        lagna_idx, md_item['lord'], ad_item['lord'], is_hi
    )

    # Pull Detailed Forecasts
    md_forecast_obj = DASHA_DETAILED_FORECASTS.get(md_item['lord'], DASHA_DETAILED_FORECASTS["Jupiter"])
    ad_forecast_obj = DASHA_DETAILED_FORECASTS.get(ad_item['lord'], DASHA_DETAILED_FORECASTS["Saturn"])
    
    md_pred_text = md_forecast_obj['md_hi'] if is_hi else md_forecast_obj['md_en']
    ad_pred_text = ad_forecast_obj['ad_hi'] if is_hi else ad_forecast_obj['ad_en']

    md_rem_text = format_remedial_protocol(md_item['lord'], md_aff, is_hi)
    ad_rem_text = format_remedial_protocol(ad_item['lord'], ad_aff, is_hi)

    # Planetary Names localized
    md_disp_name = PLANET_NAMES_HI[md_item['lord']] if is_hi else md_item['lord'].upper()
    ad_disp_name = PLANET_NAMES_HI[ad_item['lord']] if is_hi else ad_item['lord'].upper()
    next_md_disp = PLANET_NAMES_HI[next_md_item['lord']] if is_hi else next_md_item['lord'].upper()
    next_ad_disp = PLANET_NAMES_HI[next_ad_item['lord']] if is_hi else next_ad_item['lord'].upper()

    # Labels
    lbl_md_card = "🟩 वर्तमान महादशा" if is_hi else "🟩 Active Mahadasha"
    lbl_ad_card = "🟦 वर्तमान अंतर्दशा" if is_hi else "🟦 Active Antardasha"
    lbl_rel_header = "🪐 लग्न के साथ संबंध:" if is_hi else "🪐 Planetary Relationship with Your Lagna:"
    lbl_ad_rel_header = "🪐 अंतर्दशा ग्रहीय संबंध:" if is_hi else "🪐 Sub-Period Planetary Relationships:"
    lbl_md_fc_header = "📋 विस्तृत रणनीतिक फलादेश (महादशा कालखंड):" if is_hi else "📋 Detailed Strategic Forecast (Mahadasha Era):"
    lbl_ad_fc_header = "🎯 सामयिक फलादेश (अंतर्दशा उप-काल):" if is_hi else "🎯 Tactical Forecast (Antardasha Sub-Period):"
    lbl_rem_header = "🪔 निर्धारित वैदिक उपाय एवं अनुष्ठान:" if is_hi else "🪔 Prescribed Remedial Protocol:"
    lbl_ad_rem_header = "🪔 अंतर्दशा उप-काल उपाय:" if is_hi else "🪔 Sub-Period Remedial Protocol:"
    lbl_upcoming_header = "⏳ आगामी ग्रहीय परिवर्तन (Upcoming Transitions)" if is_hi else "⏳ Upcoming Planetary Transitions"
    lbl_next_md = "अगली महादशा:" if is_hi else "Next Mahadasha:"
    lbl_next_ad = "अगली अंतर्दशा:" if is_hi else "Next Antardasha:"
    lbl_starts = "प्रारंभ" if is_hi else "Starts"

    render_html(f"""
    <div style="margin-bottom:1.5rem;">
        <div style="font-weight:900; font-size:1.35rem; color:#1e293b;">{t('dasha_page_title', current_lang)}</div>
        <div style="font-size:0.95rem; color:#475569; margin-top:4px;">
            {t('dasha_page_subtitle', current_lang)} ({display_lagna})
        </div>
    </div>

    <!-- ACTIVE TIMELINE CARDS WITH EMBEDDED IN-DEPTH BRIEFINGS -->
    <div style="display:grid; grid-template-columns: 1fr; gap:16px; margin-bottom:1.5rem;">
        
        <!-- MAHADASHA CARD -->
        <div style="background:#f0fdf4; border-radius:14px; padding:18px; border:1px solid #bbf7d0; border-left:6px solid #16a34a; box-shadow:0 3px 10px rgba(0,0,0,0.02);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <b style="color:#14532d; font-size:1.18rem;">{lbl_md_card}: {md_disp_name}</b>
                <span style="font-size:0.8rem; background:#ffffff; color:#15803d; padding:3px 8px; border-radius:12px; font-weight:800; border:1px solid #86efac;">Live 🟢</span>
            </div>
            <div style="font-size:0.88rem; color:#166534; font-weight:700; margin-bottom:12px;">
                ⏱️ {md_item['start'].strftime('%b %d, %Y')} — {md_item['end'].strftime('%b %d, %Y')}
            </div>

            <!-- Lagna Relationship Highlight -->
            <div style="background:#dcfce7; border-radius:10px; padding:12px 14px; border:1px solid #bbf7d0; margin-bottom:12px; font-size:0.93rem; color:#14532d; line-height:1.6;">
                <b>{lbl_rel_header}</b><br>{md_lagna_rel}
            </div>

            <!-- In-Depth Comprehensive Prediction -->
            <div style="font-size:0.95rem; color:#1e293b; line-height:1.75; background:#ffffff; padding:16px 18px; border-radius:10px; border:1px solid #dcfce7; margin-bottom:12px;">
                <b style="color:#15803d; font-size:1.02rem;">{lbl_md_fc_header}</b><br><br>
                {md_pred_text}
            </div>

            <!-- Filtered Remedial Protocol -->
            <div style="font-size:0.92rem; color:#14532d; line-height:1.65; background:#ffffff; padding:14px 16px; border-radius:10px; border:1px solid #86efac;">
                <b style="color:#166534; font-size:0.98rem;">{lbl_rem_header}</b><br><br>
                {md_rem_text}
            </div>
        </div>

        <!-- ANTARDASHA CARD -->
        <div style="background:#eff6ff; border-radius:14px; padding:18px; border:1px solid #bfdbfe; border-left:6px solid #2563eb; box-shadow:0 3px 10px rgba(0,0,0,0.02);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <b style="color:#1e3a8a; font-size:1.18rem;">{lbl_ad_card}: {ad_disp_name}</b>
                <span style="font-size:0.8rem; background:#ffffff; color:#1d4ed8; padding:3px 8px; border-radius:12px; font-weight:800; border:1px solid #93c5fd;">Live 🟢</span>
            </div>
            <div style="font-size:0.88rem; color:#1e40af; font-weight:700; margin-bottom:12px;">
                ⏱️ {ad_item['start'].strftime('%b %d, %Y')} — {ad_item['end'].strftime('%b %d, %Y')}
            </div>

            <!-- Interlocking Relationship Statements -->
            <div style="background:#dbeafe; border-radius:10px; padding:12px 14px; border:1px solid #bfdbfe; margin-bottom:12px; font-size:0.93rem; color:#1e3a8a; line-height:1.6;">
                <b>{lbl_ad_rel_header}</b><br>
                • {ad_lagna_rel}<br>
                • {ad_md_rel}
            </div>

            <!-- In-Depth Focused Prediction -->
            <div style="font-size:0.95rem; color:#1e293b; line-height:1.75; background:#ffffff; padding:16px 18px; border-radius:10px; border:1px solid #dbeafe; margin-bottom:12px;">
                <b style="color:#1d4ed8; font-size:1.02rem;">{lbl_ad_fc_header}</b><br><br>
                {ad_pred_text}
            </div>

            <!-- Filtered Sub-Period Remedial Protocol -->
            <div style="font-size:0.92rem; color:#1e3a8a; line-height:1.65; background:#ffffff; padding:14px 16px; border-radius:10px; border:1px solid #93c5fd;">
                <b style="color:#1e40af; font-size:0.98rem;">{lbl_ad_rem_header}</b><br><br>
                {ad_rem_text}
            </div>
        </div>
    </div>

    <!-- UPCOMING TRANSITIONS CARD -->
    <div style="background:#ffffff; border-radius:14px; padding:16px; border:1.5px solid #cbd5e1; box-shadow:0 3px 10px rgba(0,0,0,0.02);">
        <div style="font-weight:900; font-size:1.1rem; color:#0f172a; margin-bottom:10px; border-bottom:1.5px solid #f1f5f9; padding-bottom:6px;">
            {lbl_upcoming_header}
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; font-size:0.9rem;">
            <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                <b style="color:#0369a1;">{lbl_next_md}</b><br>
                <div style="font-weight:900; color:#0f172a; font-size:1rem; margin:2px 0;">{next_md_disp}</div>
                <span style="font-size:0.82rem; color:#64748b;">{lbl_starts} {next_md_item['start'].strftime('%b %d, %Y')}</span>
            </div>
            <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                <b style="color:#0369a1;">{lbl_next_ad}</b><br>
                <div style="font-weight:900; color:#0f172a; font-size:1rem; margin:2px 0;">{next_ad_disp}</div>
                <span style="font-size:0.82rem; color:#64748b;">{lbl_starts} {next_ad_item['start'].strftime('%b %d, %Y')}</span>
            </div>
        </div>
    </div>
    """)
    
# ==============================================================================
# TAB 7: DEDICATED MANTRA SADHANA & DIGITAL JAPA MALA COUNTER
# ==============================================================================
def render_page_mantra():
    render_html("""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.35rem; color:#5b21b6; margin-bottom:0.4rem;">
            📿 Japa Sadhana & Vedic Mantra Sanctuary
        </div>
        <div style="font-size:0.95rem; color:#475569; line-height:1.6;">
            Select from Supreme Classical Mantras, the 9 Navagraha Planetary Beej Mantras, 
            or your personalized Birth Nakshatra Beej Mantra to chant with the 108-bead digital Mala counter.
        </div>
    </div>
    """)

    # 1. Base Classical Protection Mantras
    classical_mantras = {
        "Maha Mrityunjaya Mantra (Supreme Protection)": {
            "sanskrit": "ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्।\nउर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय मामृतात्॥",
            "translit": "Om Tryambakam Yajamahe Sugandhim Pushti-Vardhanam |\nUrvarukamiva Bandhanan-Mrityor-Mukshiya Maamritat ||",
            "meaning": "We meditate on the Three-Eyed Lord Shiva, who permeates and nourishes all beings. May He liberate us from the bonds of fear and death into immortality.",
            "rules": "• Best chanted at dawn or dusk facing East or North.\n• Use a Rudraksha Mala.\n• Pacifies severe transit friction (Vipat, Vadha) and shields cellular vitality."
        },
        "Gayatri Mantra (Solar Illumination)": {
            "sanskrit": "ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात्॥",
            "translit": "Om Bhur Bhuvah Swah Tat Savitur Varenyam Bhargo Devasya Dheemahi Dhiyo Yo Nah Prachodayat ||",
            "meaning": "We meditate upon the supreme divine brilliance of the Sun who illuminates the inner cosmos. May that divine light awaken and inspire our intellect.",
            "rules": "• Best chanted during Brahma Muhurta or at sunrise facing East.\n• Use a Tulsi or Sandalwood Mala.\n• Enhances mental clarity, vitality, and cellular healing."
        },
        "Vishnu Sahasranama Shloka (Aura Shield)": {
            "sanskrit": "ॐ नमो भगवते वासुदेवाय॥",
            "translit": "Om Namo Bhagavate Vasudevaya ||",
            "meaning": "Salutations to the Supreme Preserver of the Cosmos who dwells within all living hearts.",
            "rules": "• Chant in the morning facing East.\n• Harmonizes favorable transits (Sampat, Sadhana, Ati-Mitra).\n• Brings peace to the home and liquid capital stability."
        }
    }

    category = st.radio(
        "**Select Mantra Category:**",
        options=["Classical & Protection", "9 Navagraha Beej Mantras", "27 Nakshatra Beej Mantras"],
        horizontal=True
    )

    if category == "Classical & Protection":
        mantra_choice = st.selectbox("Choose Classical Mantra:", list(classical_mantras.keys()))
        m_info = classical_mantras[mantra_choice]
    elif category == "9 Navagraha Beej Mantras":
        mantra_choice = st.selectbox("Choose Planetary Beej Mantra:", list(NAVAGRAHA_BEEJ_MANTRAS.keys()))
        m_info = NAVAGRAHA_BEEJ_MANTRAS[mantra_choice]
    else:
        nak_options = {idx: data["name"] for idx, data in NAKSHATRA_BEEJ_MANTRAS.items()}
        
        # Pre-select user's Janma Nakshatra if chart is loaded
        default_idx = (chart_info["star_idx"] - 1) if chart_info else 0
        selected_star_idx = st.selectbox(
            "Choose Nakshatra Beej Mantra:",
            options=list(nak_options.keys()),
            format_func=lambda x: nak_options[x],
            index=default_idx
        )
        m_info = NAKSHATRA_BEEJ_MANTRAS[selected_star_idx]

    # Render Card
    render_html(f"""
    <div style="background:#ffffff; border:1.5px solid #ddd6fe; border-radius:14px; padding:18px; margin:14px 0; box-shadow:0 3px 12px rgba(139,92,246,0.06);">
        <div style="font-size:1.4rem; font-weight:900; color:#1e1b4b; text-align:center; font-family:serif; line-height:1.6; white-space:pre-line;">
            {m_info['sanskrit']}
        </div>
        <div style="font-size:0.95rem; color:#6d28d9; text-align:center; font-style:italic; margin-top:8px; line-height:1.5; white-space:pre-line;">
            {m_info['translit']}
        </div>
        <hr style="margin:14px 0; border:none; border-top:1px solid #ede9fe;">
        <div style="font-size:0.93rem; color:#334155; line-height:1.7;">
            <b>📜 Meaning:</b> {m_info['meaning']}<br><br>
            <b>🧘 Sadhana Guidelines:</b><br>{m_info['rules'].replace(chr(10), '<br>')}
        </div>
    </div>
    """)

    # Interactive 108-Bead Mala Counter
    with st.container(border=True):
        st.markdown(f"### 📿 Digital Mala: **{st.session_state.japa_count} / 108** Beads")
        progress_val = min(1.0, st.session_state.japa_count / 108.0)
        st.progress(progress_val, text=f"Mala Progress: {int(progress_val * 100)}% | Completed Malas: {st.session_state.mala_rounds}")

        col_tap, col_reset = st.columns([2, 1])
        with col_tap:
            if st.button("📿 Tap Bead (+1)", type="primary", use_container_width=True):
                st.session_state.japa_count += 1
                if st.session_state.japa_count >= 108:
                    st.session_state.japa_count = 0
                    st.session_state.mala_rounds += 1
                    st.balloons()
                    st.success("🎉 Om Shanti! You completed 1 full Mala (108 Chants). May the vibration bring peace and protection!")
                st.rerun()
        with col_reset:
            if st.button("🔄 Reset Counter", use_container_width=True):
                st.session_state.japa_count = 0
                st.session_state.mala_rounds = 0
                st.rerun()

# ==============================================================================
# ROUTER DISPATCHER: RENDER THE SELECTED PAGE
# ==============================================================================
PAGES = {
    "about": render_page_about,
    "profile": render_page_profile,
    "numerology": render_page_numerology,
    "shani": render_page_shani,
    "live": render_page_live,
    "forecast": render_page_forecast,
    "monthly": render_page_monthly,
    "dasha": render_page_dasha,
    "mantra": render_page_mantra,
    "install_guide": render_page_install_guide,
}

active_page_func = PAGES.get(st.session_state.current_page, render_page_about)
active_page_func()
