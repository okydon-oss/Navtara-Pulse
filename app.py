# app.py - Main Streamlit Application Entry Point
import streamlit as st
import datetime

# Import data banks and calculation routines from databanks.py
import databanks as db
from databanks import *

# Import modular views (Pattern B)
from views.about import render_page_about
from views.profile import render_page_profile
from views.dasha import render_page_dasha

# ==============================================================================
# EARLY LANGUAGE DETECTION & PAGE CONFIG
# ==============================================================================
init_lang = st.query_params.get("lang", "en")
app_page_title = "✨ नवतारा पल्स" if init_lang == "hi" else "✨ Navtara Pulse"

st.set_page_config(
    page_title=app_page_title,
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

# ==============================================================================
# TRANSLATION DICTIONARY
# ==============================================================================
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
        "mulank_label": "Mulank (Driver)",
        "bhagyank_label": "Bhagyank (Destiny)",
        "namank_label": "Namank (Name Vibration)",
        "forecast_title": "🗓️ 7-Day Moon Transit Matrix & Daily Forecasts",
        "live_pulse_title": "⚡ Today's Live Cosmic Pulse"
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
        "mulank_label": "मूलांक (Driver)",
        "bhagyank_label": "भाग्यांक (Conductor)",
        "namank_label": "नामांक (Name Vibration)",
        "forecast_title": "🗓️ आगामी 7 दिनों का नक्षत्र गोचर एवं दैनिक फल",
        "live_pulse_title": "⚡ आज का दैनिक खगोलीय प्रवाह"
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

# Universal Centered Header
render_html(f"""
    <div style='text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; margin-top:0.2rem; margin-bottom:0.75rem;'>
        <div style='background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); width:76px; height:76px; border-radius:26px; display:flex; align-items:center; justify-content:center; font-size:2.45rem; box-shadow:0 8px 28px rgba(245,158,11,0.38); margin-bottom:10px;'>
            ✨
        </div>
        <h1 style='margin:0; font-size:2.15rem; color:#0f172a; font-weight:900; line-height:1.2; text-align:center;'>{t('app_title', current_lang)}</h1>
        <div style='font-size:1rem; color:#64748b; font-weight:600; margin-top:6px; text-align:center;'>{t('app_subtitle', current_lang)}</div>
    </div>
""")

# Top Navigation Dock (3x3 Grid) - Fully Localized Dynamic Titles
nav_r1_c1, nav_r1_c2, nav_r1_c3 = st.columns(3)
with nav_r1_c1:
    p_type = "primary" if st.session_state.current_page == "about" else "secondary"
    if st.button(t("btn_about", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "about"
        st.rerun()
with nav_r1_c2:
    p_type = "primary" if st.session_state.current_page == "profile" else "secondary"
    if st.button(t("btn_user_profile", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "profile"
        st.rerun()
with nav_r1_c3:
    p_type = "primary" if st.session_state.current_page == "numerology" else "secondary"
    if st.button(t("btn_numerology", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "numerology"
        st.rerun()

nav_r2_c1, nav_r2_c2, nav_r2_c3 = st.columns(3)
with nav_r2_c1:
    p_type = "primary" if st.session_state.current_page == "shani" else "secondary"
    if st.button(t("btn_shani", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "shani"
        st.rerun()
with nav_r2_c2:
    p_type = "primary" if st.session_state.current_page == "live" else "secondary"
    if st.button(t("btn_live", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "live"
        st.rerun()
with nav_r2_c3:
    p_type = "primary" if st.session_state.current_page == "forecast" else "secondary"
    if st.button(t("btn_forecast", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "forecast"
        st.rerun()

nav_r3_c1, nav_r3_c2, nav_r3_c3 = st.columns(3)
with nav_r3_c1:
    p_type = "primary" if st.session_state.current_page == "monthly" else "secondary"
    if st.button(t("btn_monthly", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "monthly"
        st.rerun()
with nav_r3_c2:
    p_type = "primary" if st.session_state.current_page == "dasha" else "secondary"
    if st.button(t("btn_dasha", current_lang), type=p_type, use_container_width=True):
        st.session_state.current_page = "dasha"
        st.rerun()
with nav_r3_c3:
    p_type = "primary" if st.session_state.current_page == "mantra" else "secondary"
    if st.button(t("btn_mantra", current_lang), type=p_type, use_container_width=True):
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

    # Save to session_state for Pattern B modular views
    st.session_state["has_valid_profile"] = True
    st.session_state["chart_info"] = chart_info
    st.session_state["dob_parsed"] = dob_parsed
    st.session_state["tob_parsed"] = tob_parsed
else:
    dob_parsed, tob_parsed, chart_info = None, None, None
    mulank, bhagyank, namank = None, None, None
    shani_paya_data, shani_sadesati_data = None, None
    u_lat, u_lon = 28.6139, 77.2090
    st.session_state["has_valid_profile"] = False

def render_profile_setup_prompt():
    is_hi = (current_lang == "hi")
    prompt_title = "अपनी जन्म पत्रिका प्रोफाइल सेट करें" if is_hi else "Set Up Your Vedic Birth Profile"
    prompt_desc = "अपना प्रामाणिक <b>जन्म नक्षत्र</b>, <b>लग्न</b>, <b>नवतारा चक्र</b> एवं <b>शनि साढ़े साती</b> की गणना करने के लिए यूज़र प्रोफाइल टैब में अपना जन्म विवरण भरें।" if is_hi else "To calculate your authentic <b>Janma Nakshatra</b>, <b>Ascendant (Lagna)</b>, <b>Navtara cycle</b>, and <b>Shani Sade Sati phase</b>, please enter your birth details in the User Profile tab."
    btn_lbl = "👉 प्रोफाइल अभी भरें" if is_hi else "👉 Configure Profile Now"

    render_html(f"""
    <div style="background:#fffbeb; border:2px dashed #f59e0b; border-radius:16px; padding:1.5rem; text-align:center; margin:1.5rem 0;">
        <div style="font-size:2.2rem; margin-bottom:8px;">👤</div>
        <div style="font-weight:900; font-size:1.25rem; color:#92400e; margin-bottom:6px;">
            {prompt_title}
        </div>
        <div style="font-size:0.95rem; color:#78350f; max-width:480px; margin:0 auto 1.2rem auto; line-height:1.6;">
            {prompt_desc}
        </div>
    </div>
    """)
    _, c_mid, _ = st.columns([1, 2, 1])
    with c_mid:
        if st.button(btn_lbl, type="primary", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()

# ==============================================================================
# POST-SUBMISSION ONBOARDING: ADD TO HOME SCREEN
# ==============================================================================
def render_page_install_guide():
    is_hi = (current_lang == "hi")
    ig_title = "मोबाइल होम स्क्रीन पर ऐप जोड़ें" if is_hi else "Save to Home Screen on Your Device"
    ig_desc = "आपकी ज्योतिषीय प्रोफाइल और निर्देशांक ब्राउज़र में सुरक्षित कर लिए गए हैं। <b>नवतारा पल्स को होम स्क्रीन पर सेव करें</b> ताकि हर दिन बिना दोबारा डेटा भरे ऐप खुल सके!" if is_hi else "Your astrological profile & coordinates are now securely loaded in your device's browser bar. <b>Add Navtara Pulse to your Home Screen now</b> so your profile opens automatically every day without typing anything again!"
    
    btn_p1 = "⚡ आज का फल देखें" if is_hi else "⚡ Proceed to Today's Prediction"
    btn_p2 = "👤 जन्म कुंडली प्रोफाइल देखें" if is_hi else "👤 View Astrological Profile"

    render_html(f"""
    <div class="auth-hero-box" style="text-align:center; border:2px solid #f59e0b; background:#fffbeb;">
        <div style="font-size:2.6rem; margin-bottom:8px;">📱</div>
        <div style="font-weight:900; font-size:1.45rem; color:#92400e; margin-bottom:6px;">
            {ig_title}
        </div>
        <div style="font-size:0.98rem; color:#78350f; line-height:1.6; margin-bottom:12px;">
            {ig_desc}
        </div>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.18rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:1.5px solid #fed7aa; padding-bottom:0.3rem;">
            🤖 Android (Google Chrome)
        </div>
        <ol style="margin-top:5px; margin-bottom:6px; padding-left:1.3rem; font-size:0.95rem; color:#431407; line-height:1.75;">
            <li>क्रोम के ऊपरी दाएं कोने में <b>तीन बिंदुओं (⋮)</b> पर टैप करें।</li>
            <li><b>'ऐप इंस्टॉल करें' (Install app)</b> या <b>'होम स्क्रीन में जोड़ें' (Add to Home screen)</b> चुनें।</li>
            <li><b>'Install'</b> पर क्लिक करें। ऐप आपके फोन में सुरक्षित रूप से इंस्टॉल हो जाएगा।</li>
        </ol>
    </div>

    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.18rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:1.5px solid #fed7aa; padding-bottom:0.3rem;">
            🍏 iPhone / iOS (Safari)
        </div>
        <ol style="margin-top:5px; margin-bottom:6px; padding-left:1.3rem; font-size:0.95rem; color:#431407; line-height:1.75;">
            <li>सफारी के नीचे <b>शेयर आइकन (Share)</b> पर टैप करें।</li>
            <li>नीचे स्क्रॉल करें और <b>'होम स्क्रीन में जोड़ें' (Add to Home Screen)</b> पर क्लिक करें।</li>
            <li>ऊपरी दाएं कोने में <b>'Add'</b> पर टैप करें।</li>
        </ol>
    </div>
    """)

    st.write("")
    c_btn1, c_btn2 = st.columns([1, 1])
    with c_btn1:
        if st.button(btn_p1, type="primary", use_container_width=True):
            st.session_state.current_page = "live"
            st.rerun()
    with c_btn2:
        if st.button(btn_p2, use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()

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
# TAB 4: SHANI & SADE SATI
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
                <div style="background:#f0f9ff; border-radius:10px; padding:10px 12px; border-left:4px solid #0284c7;">
                    <b>💼 7. Career, Authority & Executive Standing:</b><br>{shani_sadesati_data['career']}
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px 12px; border-left:4px solid #475569;">
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
# TAB 9: DEDICATED MANTRA SADHANA & DIGITAL JAPA MALA COUNTER
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
        default_idx = (chart_info["star_idx"] - 1) if chart_info else 0
        selected_star_idx = st.selectbox(
            "Choose Nakshatra Beej Mantra:",
            options=list(nak_options.keys()),
            format_func=lambda x: nak_options[x],
            index=default_idx
        )
        m_info = NAKSHATRA_BEEJ_MANTRAS[selected_star_idx]

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
