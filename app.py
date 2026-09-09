import os
import json
import datetime
import streamlit as st

# Swiss Ephemeris astronomical calculation library
try:
    import swisseph as swe
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False
    st.error("🚨 Missing Library: `pyswisseph` is not installed. Please add `pyswisseph` to `requirements.txt`.")
    st.stop()

st.set_page_config(
    page_title="Navtara Pulse",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Clean, app-like header & footer hiding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1.0rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 0.9rem !important;
        padding-right: 0.9rem !important;
        max-width: 720px !important;
        margin: 0 auto !important;
    }
    
    /* Mobile-optimized typography */
    h1 {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        text-align: center !important;
        margin-bottom: 0.2rem !important;
        letter-spacing: -0.5px;
    }
    h2 { font-size: 1.35rem !important; font-weight: 700 !important; }
    h3 { font-size: 1.15rem !important; font-weight: 700 !important; }
    p, span, div { font-size: 15px; }
    
    label { font-size: 14.5px !important; font-weight: 600 !important; }
    input, select { min-height: 46px !important; font-size: 15px !important; }
    
    /* Touch button styling */
    .stButton > button {
        min-height: 48px !important;
        font-size: 15.5px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
    }

    /* Cards */
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13.5px;
    }
    .badge-favorable { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
    .badge-caution { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
    .badge-neutral { background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; }

    .card-box {
        background: #ffffff;
        border: 1.2px solid #e2e8f0;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .remedy-card {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1.5px solid #fde68a;
        border-radius: 14px;
        padding: 14px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

NAVTARA_NAMES = [
    "Janma", "Sampat", "Vipat", "Kshema", "Pratyari",
    "Sadhana", "Vadha", "Mitra", "Ati-Mitra"
]

NAVTARA_DESCRIPTIONS = {
    "Janma": "Self / Physical Vitality / Grounding & New Cycles",
    "Sampat": "Wealth / Financial Expansion / Material Acquisitions",
    "Vipat": "Obstacles / High Risk / Unforeseen Volatility",
    "Kshema": "Well-being / Comfort / Protection & Recovery",
    "Pratyari": "Resistance / Confrontation / Strategic Restraint",
    "Sadhana": "Achievement / Focused Effort / Peak Productivity",
    "Vadha": "Destruction / High Vulnerability / Complete Caution",
    "Mitra": "Friendship / Collaborative Harmony / Goodwill",
    "Ati-Mitra": "Supreme Support / Peak Auspicious Opportunity"
}

SHANI_VAHANS = {
    1: {"name": "Ghoda (Horse) 🐴", "nature": "Speed & Quick Victory", "desc": "Swift movement, high stamina, victory over competitors, rapid task completion."},
    2: {"name": "Gadha (Donkey) 🫏", "nature": "Heavy Labor & Delays", "desc": "High physical workload with delayed recognition. Demands continuous patience."},
    3: {"name": "Siyar (Jackal) 🦊", "nature": "Alertness & Caution", "desc": "Warning against deceptive advice, unverified schemes, or hidden friction."},
    4: {"name": "Hathi (Elephant) 🐘", "nature": "Royalty & Prosperity", "desc": "Sudden prestige, luxury gains, recognition from seniors, and material comfort."},
    5: {"name": "Bail (Bull) 🐂", "nature": "Steady Persistence", "desc": "Gradual, rock-solid gains through steady discipline. Excellent for foundational building."},
    6: {"name": "Sher (Lion) 🦁", "nature": "Power & Authority", "desc": "Commanding respect, high confidence, decisive success in legal or competitive arenas."},
    7: {"name": "Kowwa (Crow) 🐦‍⬛", "nature": "Restlessness & Distraction", "desc": "Scattered mental energy, minor arguments, frequent movement. Practice silence."},
    8: {"name": "Mayur (Peacock) 🦚", "nature": "Joy & Aesthetic Warmth", "desc": "Heartwarming social news, creative flow, domestic warmth, and delightful meetings."},
    9: {"name": "Hans (Swan) 🦢", "nature": "Wisdom & Spiritual Peace", "desc": "Highest mental clarity, serene intuition, spiritual grace, and sound financial judgment."}
}

CHALDEAN_MAP = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

PROFILE_FILE = "user_profile.json"

def load_user_profile() -> dict:
    defaults = {
        "name": "Okesh",
        "dob": datetime.date(1984, 1, 13),
        "tob": datetime.time(14, 0),
        "place": "Chhatrapati Sambhajinagar, India",
        "lat": 19.8762,
        "lon": 75.3433,
        "tz_offset": 5.5,
        "nakshatra_idx": 1  # Bharani (#2)
    }
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                saved = json.load(f)
                if "dob" in saved and isinstance(saved["dob"], str):
                    saved["dob"] = datetime.date.fromisoformat(saved["dob"])
                if "tob" in saved and isinstance(saved["tob"], str):
                    saved["tob"] = datetime.time.fromisoformat(saved["tob"])
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_user_profile(profile_data: dict) -> bool:
    try:
        to_store = profile_data.copy()
        if isinstance(to_store.get("dob"), (datetime.date, datetime.datetime)):
            to_store["dob"] = to_store["dob"].isoformat()
        if isinstance(to_store.get("tob"), datetime.time):
            to_store["tob"] = to_store["tob"].isoformat()
        with open(PROFILE_FILE, "w") as f:
            json.dump(to_store, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return False

def dt_to_jd(utc_dt: datetime.datetime) -> float:
    hour_dec = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0 + (utc_dt.microsecond / 1e6) / 3600.0
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)

def get_sidereal_lon(jd_ut: float, planet_id: int) -> float:
    res, _ = swe.calc_ut(jd_ut, planet_id, swe.FLG_MOSEPH)
    trop_lon = res[0]
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    return (trop_lon - ayanamsa) % 360.0

def lon_to_nakshatra(lon: float):
    nak_span = 360.0 / 27.0
    idx = int(lon / nak_span) % 27
    pada = int((lon % nak_span) / (nak_span / 4.0)) + 1
    return idx, pada

def lon_to_rashi(lon: float):
    return int(lon / 30.0) % 12, lon % 30.0

def calculate_navtara(birth_idx: int, transit_idx: int):
    offset = (transit_idx - birth_idx) % 27
    return NAVTARA_NAMES[offset % 9], (offset // 9) + 1

def calculate_shani_paya(moon_rashi_idx: int, saturn_rashi_idx: int):
    """
    Calculates Shani Paya (Saturn's Feet) based on relative distance from Saturn to Moon sign.
    1-indexed house count: (Moon - Saturn) mod 12 + 1
    """
    house_pos = ((moon_rashi_idx - saturn_rashi_idx) % 12) + 1
    if house_pos in [2, 5, 9]:
        return "Rajat Paya (Silver Feet) 🥈", "Most Auspicious & Protective", "Brings wealth expansion, protective cushioning, domestic comfort, and clear resolutions."
    elif house_pos in [3, 7, 10]:
        return "Tamra Paya (Copper Feet) 🥉", "Favorable & Progressive", "Brings steady rewards through hard work, continuous career growth, and strong vitality."
    elif house_pos in [1, 6, 11]:
        return "Swarna Paya (Gold Feet) 🥇", "Testing & High Expenditure", "Tests humility and character. Financial turnover is high; caution against ego conflicts."
    else:  # 4, 8, 12
        return "Loha Paya (Iron Feet) 🪙", "Heavy Labor & High Caution", "Indicates karmic testing, project friction, joint fatigue. Requires routine discipline."

def calculate_shani_vahan(birth_nak_1based: int, transit_moon_nak_1based: int):
    """
    Formula: ((Birth Nakshatra * 4) + Transit Moon Nakshatra) % 9
    Remainder 0 is treated as 9.
    """
    rem = ((birth_nak_1based * 4) + transit_moon_nak_1based) % 9
    rem = 9 if rem == 0 else rem
    return rem, SHANI_VAHANS[rem]

def reduce_single_digit(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

def calculate_numerology(dob: datetime.date, name: str):
    # Mulank (Driver Number): Day of birth
    mulank = reduce_single_digit(dob.day)
    
    # Bhagyank (Conductor / Destiny Number): Full Date Sum
    total_dob = dob.day + dob.month + dob.year
    bhagyank = reduce_single_digit(total_dob)
    
    # Namank (Name Number via Chaldean mapping)
    clean_name = "".join(ch for ch in name.upper() if ch.isalpha())
    name_sum = sum(CHALDEAN_MAP.get(ch, 0) for ch in clean_name)
    namank = reduce_single_digit(name_sum) if name_sum > 0 else 1
    
    return mulank, bhagyank, namank

def get_personal_day_vibe(mulank: int, target_date: datetime.date):
    day_sum = target_date.day + target_date.month + target_date.year
    universal_day = reduce_single_digit(day_sum)
    personal_day = reduce_single_digit(mulank + universal_day)
    
    vibe_map = {
        1: ("Leadership & Initiative", "Ideal for launching plans, asserting self-confidence, and signing off on direct decisions."),
        2: ("Diplomacy & Harmony", "Favor teamwork, quiet negotiations, emotional balance, and attentive listening."),
        3: ("Creative Expression", "Excellent for brainstorming, persuasive communication, writing, and social meetings."),
        4: ("Discipline & Foundation", "Focus on structured execution, organizing paperwork, maintenance, and detailed follow-through."),
        5: ("Flexibility & Quick Change", "Expect quick changes in pace. Good for networking, sales, and agile problem solving."),
        6: ("Responsibility & Family", "Nurture domestic relationships, assist colleagues, and focus on health harmony."),
        7: ("Deep Introspection & Study", "Avoid noisy debates. Ideal for research, spiritual contemplation, and analytical audits."),
        8: ("Authority & Financial Prudence", "Handle monetary decisions, contracts, and long-range business planning with discipline."),
        9: ("Completion & Detachment", "Wrap up pending items, release past friction, forgive misunderstandings, and prepare for new cycles.")
    }
    return universal_day, personal_day, vibe_map.get(personal_day, ("Balanced Focus", "Proceed with standard awareness."))

def find_7day_transitions(start_utc_dt: datetime.datetime):
    nak_span = 360.0 / 27.0
    transitions = []
    current_time = start_utc_dt
    end_time = start_utc_dt + datetime.timedelta(days=7)

    cur_lon = get_sidereal_lon(dt_to_jd(current_time), swe.MOON)
    active_nak = int(cur_lon / nak_span) % 27
    interval_start = current_time

    step = datetime.timedelta(minutes=30)
    eval_time = current_time

    while eval_time <= end_time:
        eval_time += step
        lon = get_sidereal_lon(dt_to_jd(eval_time), swe.MOON)
        nak = int(lon / nak_span) % 27

        if nak != active_nak:
            low, high = eval_time - step, eval_time
            for _ in range(7):
                mid = low + (high - low) / 2
                mid_lon = get_sidereal_lon(dt_to_jd(mid), swe.MOON)
                if int(mid_lon / nak_span) % 27 == active_nak:
                    low = mid
                else:
                    high = mid
            boundary = high
            transitions.append({
                "nak_idx": active_nak,
                "start": interval_start,
                "end": boundary
            })
            interval_start = boundary
            active_nak = nak

    transitions.append({
        "nak_idx": active_nak,
        "start": interval_start,
        "end": end_time
    })
    return transitions

def get_daily_remedy(navtara_cat: str, vahan_name: str, day_name: str):
    remedies = []
    
    # Day-based foundational remedy
    if "Sat" in day_name:
        remedies.append("Offer mustard oil diya near a Peepal tree or donate black sesame to cultivate Saturn's grounding peace.")
    elif "Tue" in day_name:
        remedies.append("Recite the Hanuman Chalisa twice to dissolve friction and bolster internal stamina.")
    elif "Sun" in day_name:
        remedies.append("Offer Arghya (clean water in copper vessel) to the rising Sun to nourish vitality and clarity.")
    elif "Mon" in day_name:
        remedies.append("Keep your mind calm with deep hydration; avoid impulsive emotional reactions.")
    else:
        remedies.append("Begin your day with 5 minutes of focused conscious breathing or Japa before taking phone calls.")
        
    # Navtara category guidance
    if navtara_cat in ["Vadha", "Vipat"]:
        remedies.append("Feed stray birds or cattle with whole grains. Avoid signing high-risk financial commitments.")
    elif navtara_cat == "Pratyari":
        remedies.append("Practice diplomatic silence (Mouna). Avoid entering into avoidable debates or counter-arguments.")
    elif navtara_cat in ["Sampat", "Ati-Mitra"]:
        remedies.append("Share sweets or fresh fruit with someone in need; express gratitude to teachers and parents to expand positive merit.")
    else:
        remedies.append("Focus diligently on completing one pending task with full attention to harness steady Saturnian momentum.")

    # Vahan-specific addition
    if "Crow" in vahan_name:
        remedies.append("Feed crows or birds some soaked grains or bread on your terrace/balcony to settle mental restlessness.")
    elif "Jackal" in vahan_name:
        remedies.append("Double check transaction details and avoid speculation or unverified claims.")
    elif "Donkey" in vahan_name:
        remedies.append("Take regular short breaks during heavy physical or mental labor to prevent burnout.")

    return remedies

if "profile" not in st.session_state:
    st.session_state.profile = load_user_profile()

prof = st.session_state.profile

with st.sidebar:
    st.header("👤 Your Birth Profile")
    st.caption("Saved automatically to `user_profile.json`.")

    name_in = st.text_input("Full Name", value=prof.get("name", "Okesh"))
    dob_in = st.date_input("Date of Birth", value=prof.get("dob", datetime.date(1984, 1, 13)))
    tob_in = st.time_input("Time of Birth", value=prof.get("tob", datetime.time(14, 0)))
    place_in = st.text_input("Birth Place / City", value=prof.get("place", "Chhatrapati Sambhajinagar, India"))

    selected_nak = st.selectbox(
        "Janma Nakshatra",
        NAKSHATRAS,
        index=prof.get("nakshatra_idx", 1)  # Default: Bharani
    )
    selected_nak_idx = NAKSHATRAS.index(selected_nak)

    if st.button("💾 Save Profile", use_container_width=True, type="primary"):
        updated_prof = {
            "name": name_in,
            "dob": dob_in,
            "tob": tob_in,
            "place": place_in,
            "lat": prof.get("lat", 19.8762),
            "lon": prof.get("lon", 75.3433),
            "tz_offset": 5.5,
            "nakshatra_idx": selected_nak_idx
        }
        st.session_state.profile = updated_prof
        if save_user_profile(updated_prof):
            st.success("✅ Profile saved!")

janma_idx = prof.get("nakshatra_idx", 1)
janma_name = NAKSHATRAS[janma_idx]
user_dob = prof.get("dob", datetime.date(1984, 1, 13))
user_name = prof.get("name", "Okesh")

# Numerology metrics
mulank, bhagyank, namank = calculate_numerology(user_dob, user_name)

# Current time and planetary positions
now_utc = datetime.datetime.now(datetime.timezone.utc)
ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
now_ist = now_utc.astimezone(ist_tz)
jd_now = dt_to_jd(now_utc)

# Saturn & Moon current positions
saturn_lon = get_sidereal_lon(jd_now, swe.SATURN)
saturn_rashi_idx, _ = lon_to_rashi(saturn_lon)
moon_lon = get_sidereal_lon(jd_now, swe.MOON)
cur_moon_rashi_idx, _ = lon_to_rashi(moon_lon)
cur_moon_nak_idx, _ = lon_to_nakshatra(moon_lon)

# Natal Moon estimation based on Janma Nakshatra (approx sign)
# Bharani is in Mesha (Aries, index 0)
natal_moon_rashi_idx = int((janma_idx * (360.0 / 27.0)) / 30.0) % 12

# Shani Paya & Vahan
paya_name, paya_status, paya_desc = calculate_shani_paya(natal_moon_rashi_idx, saturn_rashi_idx)
today_vahan_num, today_vahan = calculate_shani_vahan(janma_idx + 1, cur_moon_nak_idx + 1)

# Current Navtara status
cur_nav_cat, cur_nav_series = calculate_navtara(janma_idx, cur_moon_nak_idx)

st.markdown(f"""
<div style="text-align: center; margin-bottom: 12px;">
    <h1>✨ Navtara Pulse</h1>
    <div style="color: #4f46e5; font-weight: 700; font-size: 15px;">Cosmic Timing • Shani Paya & Vahan • Numerology Engine</div>
    <div style="margin-top: 6px; font-size: 14.5px; color: #475569;">
        Native: <b>{user_name}</b> | Janma Star: <b>{janma_name}</b> (<code>#{janma_idx+1}</code>) | Moon Sign: <b>{RASHIS[natal_moon_rashi_idx].split(' ')[0]}</b>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗓️ 7-Day Matrix",
    "🔮 Today's Oracle & Remedy",
    "🪐 Shani Charan & Vahan",
    "🔢 Numerology",
    "🌌 Planets"
])

with tab1:
    st.subheader("Daily Moon Transition Table (Next 7 Days)")
    st.caption("Calculated with Swiss Ephemeris Chitrapaksha Lahiri Ayanamsa.")

    transitions = find_7day_transitions(now_utc)
    table_rows = []

    for t in transitions:
        nak_name = NAKSHATRAS[t["nak_idx"]]
        cat, series = calculate_navtara(janma_idx, t["nak_idx"])

        if cat in ["Vipat", "Pratyari", "Vadha"]:
            status_str = f"🔴 {cat}"
        elif cat == "Ati-Mitra":
            status_str = "🟢🟢 Ati-Mitra"
        elif cat in ["Mitra", "Sampat"]:
            status_str = f"🟢 {cat}"
        else:
            status_str = cat

        start_ist = t["start"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M)")
        end_ist = t["end"].astimezone(ist_tz).strftime("%a, %d %b (%H:%M IST)")

        # Daily Vahan for this transit
        _, vahan_info = calculate_shani_vahan(janma_idx + 1, t["nak_idx"] + 1)

        table_rows.append({
            "Status": status_str,
            "Day, Date & Time (IST)": f"{start_ist} – {end_ist}",
            "Nakshatra": nak_name,
            "Series": f"{cat} ({series})",
            "Shani Vahan": vahan_info["name"].split(" ")[0]
        })

    st.dataframe(table_rows, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("🔮 Today's Integrated Synthesis & Remedy")
    st.caption(f"Synthesized for {user_name} on {now_ist.strftime('%A, %d %B %Y')}")

    u_day, p_day, (p_title, p_desc) = get_personal_day_vibe(mulank, now_ist.date())

    # Quick summary badges
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Current Navtara:** `{cur_nav_cat} (Series {cur_nav_series})`")
        st.markdown(f"**Active Moon Star:** `{NAKSHATRAS[cur_moon_nak_idx]}`")
        st.markdown(f"**Personal Day Number:** `{p_day}` ({p_title})")
    with c2:
        st.markdown(f"**Shani Paya:** `{paya_name.split(' ')[0]} {paya_name.split(' ')[1]}`")
        st.markdown(f"**Today's Shani Vahan:** `{today_vahan['name']}`")
        st.markdown(f"**Universal Day Energy:** `{u_day}`")

    st.markdown("---")

    # Synthesized Forecast
    st.markdown("### 🎯 Daily Strategic Directives")
    st.write(f"**1. Cosmic Rhythm ({cur_nav_cat}):** {NAVTARA_DESCRIPTIONS.get(cur_nav_cat)}")
    st.write(f"**2. Saturn's Daily Mount ({today_vahan['name']}):** {today_vahan['desc']}")
    st.write(f"**3. Numerological Tone (Day {p_day}):** {p_desc}")

    # Prescribed Daily Remedy Card
    st.markdown("""<div class="remedy-card">
        <h4 style="margin-top: 0; color: #92400e;">🪔 Prescribed Astro-Remedy for Today</h4>
    """, unsafe_allow_html=True)
    
    daily_remedies = get_daily_remedy(cur_nav_cat, today_vahan["name"], now_ist.strftime("%a"))
    for idx, rem in enumerate(daily_remedies, 1):
        st.markdown(f"• **Step {idx}:** {rem}")
        
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.subheader("🪐 Shani Charan (Paya) & Vahan Analysis")
    st.caption("Understanding Saturn's material foundation and psychological behavioral speed.")

    sat_rashi_name = RASHIS[saturn_rashi_idx].split(" ")[0]
    moon_rashi_name = RASHIS[natal_moon_rashi_idx].split(" ")[0]

    st.markdown(f"""
    <div class="card-box">
        <h3 style="margin-top:0; color:#1e1b4b;">🥈 Shani Ka Paya: {paya_name}</h3>
        <p><b>Transit Position:</b> Saturn in <b>{sat_rashi_name}</b>, your Janma Rashi is <b>{moon_rashi_name}</b>.</p>
        <p><b>Status:</b> <span class="status-badge badge-favorable">{paya_status}</span></p>
        <p>{paya_desc}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card-box">
        <h3 style="margin-top:0; color:#1e1b4b;">🦚 Today's Shani Vahan: {today_vahan['name']}</h3>
        <p><b>Behavioral Theme:</b> <i>{today_vahan['nature']}</i></p>
        <p>{today_vahan['desc']}</p>
        <p><b>Formula:</b> <code>((Birth Star #{janma_idx+1} × 4) + Today's Moon Star #{cur_moon_nak_idx+1}) mod 9 = Remainder {today_vahan_num}</code></p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📖 View All 9 Vehicles of Saturn & Meanings"):
        v_rows = []
        for num, vdata in SHANI_VAHANS.items():
            v_rows.append({
                "Index": num,
                "Vehicle": vdata["name"],
                "Key Energy": vdata["nature"],
                "Impact": vdata["desc"]
            })
        st.dataframe(v_rows, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("🔢 Personal Numerology Engine")
    st.caption("Derived via Vedic and Chaldean reduction methodology.")

    num_col1, num_col2, num_col3 = st.columns(3)
    with num_col1:
        st.metric(label="Mulank (Driver)", value=mulank, help="Calculated from your birth day.")
    with num_col2:
        st.metric(label="Bhagyank (Conductor)", value=bhagyank, help="Calculated from your full date of birth.")
    with num_col3:
        st.metric(label="Namank (Name)", value=namank, help="Calculated via Chaldean letter values.")

    st.markdown("---")
    st.markdown(f"**Day Number Vibration for {now_ist.strftime('%d %b %Y')}:**")
    st.info(f"**Universal Day:** {u_day} | **Your Personal Day:** {p_day} — **{p_title}**\n\n{p_desc}")

    with st.expander("ℹ️ Understanding Your Core Numbers"):
        st.markdown(f"""
        - **Mulank {mulank} (Root Number):** Represents your core behavioral nature, innate desires, and spontaneous reactions.
        - **Bhagyank {bhagyank} (Destiny Number):** Dictates life path, career direction, karmic trajectory, and maturity cycles after age 32.
        - **Namank {namank} (Name Vibration):** Represents your public identity, social attraction, and professional resonance.
        """)

with tab5:
    st.subheader("Sidereal Planetary Positions (Lahiri)")
    planets = [
        ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
        ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
        ("Venus", swe.VENUS), ("Saturn", swe.SATURN), ("Rahu", swe.MEAN_NODE)
    ]
    coords = []
    for name, pid in planets:
        lon = get_sidereal_lon(jd_now, pid)
        r_idx, r_deg = lon_to_rashi(lon)
        n_idx, pada = lon_to_nakshatra(lon)
        coords.append({
            "Planet": name,
            "Sign": RASHIS[r_idx].split(" ")[0],
            "Degrees": f"{r_deg:.2f}°",
            "Nakshatra": f"{NAKSHATRAS[n_idx]} (Pada {pada})"
        })

    rahu_lon = get_sidereal_lon(jd_now, swe.MEAN_NODE)
    ketu_lon = (rahu_lon + 180.0) % 360.0
    kr_idx, kr_deg = lon_to_rashi(ketu_lon)
    kn_idx, k_pada = lon_to_nakshatra(ketu_lon)
    coords.append({
        "Planet": "Ketu",
        "Sign": RASHIS[kr_idx].split(" ")[0],
        "Degrees": f"{kr_deg:.2f}°",
        "Nakshatra": f"{NAKSHATRAS[kn_idx]} (Pada {k_pada})"
    })

    st.dataframe(coords, use_container_width=True, hide_index=True)

st.divider()
st.caption("Navtara Pulse Engine • Swiss Ephemeris Chitrapaksha Lahiri Framework • All rights reserved.")
