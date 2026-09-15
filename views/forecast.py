# views/forecast.py - Dedicated 7-Day Moon Transit Forecast View with Complete Bilingual Support
import streamlit as st
import datetime
from databanks import (
    NAKSHATRAS,
    NAVTARA_NAMES,
    get_7_day_moon_transits,
    calculate_shani_vahan,
    get_personal_day_vibe,
    get_detailed_day_insights,
    calculate_daily_muhurtas
)

def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

NAKSHATRA_NAMES_HI = {
    "Ashwini": "अश्विनी", "Bharani": "भरणी", "Krittika": "कृत्तिका",
    "Rohini": "रोहिणी", "Mrigashira": "मृगशिरा", "Ardra": "आर्द्रा",
    "Punarvasu": "पुनर्वसु", "Pushya": "पुष्य", "Ashlesha": "आश्लेषा",
    "Magha": "मघा", "Purva Phalguni": "पूर्वा फाल्गुनी", "Uttara Phalguni": "उत्तरा फाल्गुनी",
    "Hasta": "हस्त", "Chitra": "चित्रा", "Swati": "स्वाति",
    "Vishakha": "विशाखा", "Anuradha": "अनुराधा", "Jyeshtha": "ज्येष्ठा",
    "Mula": "मूल", "Purva Ashadha": "पूर्वाषाढ़ा", "Uttara Ashadha": "उत्तराषाढ़ा",
    "Shravana": "श्रवण", "Dhanishta": "धनिष्ठा", "Shatabhisha": "शतभिषा",
    "Purva Bhadrapada": "पूर्वाभाद्रपद", "Uttara Bhadrapada": "उत्तराभाद्रपद", "Revati": "रेवती"
}

NAVTARA_NAMES_HI = {
    "Janma": "जन्म तारा", "Sampat": "सम्पत तारा", "Vipat": "विपत तारा",
    "Kshema": "क्षेम तारा", "Pratyak": "प्रत्यक तारा", "Sadhana": "साधना तारा",
    "Naidhana": "निधन तारा", "Mitra": "मित्र तारा", "Ati-Mitra": "अति-मित्र तारा"
}

# Complete Bilingual Insight Dictionaries for Forecast Transits
FORECAST_INSIGHTS_HI = {
    "Strategic Mastery & Manifestation (Sadhana)": {
        "title": "रणनीतिक निपुणता एवं सिद्धि (साधना तारा)",
        "desc": "उच्च-स्तरीय सफलताओं के लिए स्वर्ण काल। जटिल इंजीनियरिंग, रणनीति और कार्य निष्पादन के लिए मानसिक क्षमताएं अत्यंत तीव्र हैं।",
        "opp": "महत्वपूर्ण अभियानों का शुभारंभ करें, जटिल तकनीकी परियोजनाओं को हाथ में लें, पदोन्नति के लिए बातचीत करें और उच्च अध्ययन करें।",
        "hazaz": "इस उच्च-आवृत्ति वाली ऊर्जा विंडो को सतही या साधारण कार्यों में व्यर्थ न जाने दें।",
        "mantra": "ॐ नमो भगवते वासुदेवाय (प्रातःकाल पूर्व दिशा की ओर मुख करके 11 बार जप करें)",
        "charity": "वैश्विक समृद्धि सुनिश्चित करने के लिए वरिष्ठों, गुरुजनों या मंदिर में मीठे पीले फल अथवा दूध की मिठाई अर्पित करें।",
        "action": "शीर्षक ऊर्जा के साथ प्रतिध्वनि प्रसारित करने के लिए हल्के और जीवंत रंग (मूंगा लाल, अंबर स्वर्ण, या इलेक्ट्रिक व्हाइट) पहनें।"
    },
    "Abundant Expansion & Material Growth (Sampat)": {
        "title": "प्रचुर विस्तार एवं भौतिक वृद्धि (सम्पत तारा)",
        "desc": "आर्थिक प्रगति, व्यावसायिक विस्तार और दीर्घकालिक निवेश के लिए अत्यंत अनुकूल समय।",
        "opp": "नए वित्तीय अनुबंधों पर हस्ताक्षर करें, पूंजी निवेश करें और वाणिज्यिक साझेदारियों को आगे बढ़ाएं।",
        "hazaz": "अति-आशावादिता में आकर बिना सोचे-समझे बड़े वित्तीय जोखिम न लें।",
        "mantra": "ॐ श्री महालक्ष्म्यै नमः (11 बार संध्या समय)",
        "charity": "जरूरतमंदों को अन्न या वस्त्र का दान करें।",
        "action": "सकारात्मक वित्तीय ऊर्जा के लिए हरे या सुनहरे रंग के वस्त्रों का प्रयोग करें।"
    },
    "Protective Prudence & Friction Defense (Vipat)": {
        "title": "सुरक्षात्मक विवेक एवं संघर्ष बचाव (विपत तारा)",
        "desc": "अवरोधों और वैचारिक मतभेदों की संभावना। यह दिन आक्रामक कदमों के बजाय रक्षात्मक और धैर्यवान समीक्षा की मांग करता है।",
        "opp": "पुराने कार्यों की समीक्षा करें, आंतरिक ऑडिट करें और दस्तावेजों की सूक्ष्म जांच करें।",
        "hazaz": "नए ऋण लेने, वाद-विवाद शुरू करने या महत्वपूर्ण दस्तावेजों पर बिना पढ़े हस्ताक्षर करने से बचें।",
        "mantra": "ॐ गं गणपतये नमः (21 बार संकट निवारण हेतु)",
        "charity": "पक्षियों को दाना डालें या काले तिल का दान करें।",
        "action": "धीरज बनाए रखें; गहरे नीले या शांत श्वेत रंगों का चयन करें।"
    }
}

def get_localized_forecast_insights(theme_title, raw_insights, is_hi):
    if is_hi:
        if theme_title in FORECAST_INSIGHTS_HI:
            m = FORECAST_INSIGHTS_HI[theme_title]
            return {
                "theme_title": m["title"],
                "theme_desc": m["desc"],
                "opportunities": m["opp"],
                "hazards": m["hazaz"],
                "remedy_mantra": m["mantra"],
                "remedy_charity": m["charity"],
                "remedy_action": m["action"]
            }
        else:
            return {
                "theme_title": "संतुलित खगोलीय प्रवाह एवं आत्म-समीक्षा",
                "desc": "आज का दिन व्यावहारिक समीक्षा, आंतरिक स्थिरता और व्यक्तिगत प्राथमिकताओं को व्यवस्थित करने के लिए अनुकूल है।",
                "opportunities": "लंबित प्रशासनिक कार्यों को पूरा करें, टीम के सदस्यों के साथ संवाद सुधारें और स्वास्थ्य पर ध्यान दें।",
                "hazards": "भावनात्मक अतिरेक या जल्दबाजी में लिए गए वित्तीय निर्णयों से बचें।",
                "remedy_mantra": "ॐ नमः शिवाय (11 बार)",
                "remedy_charity": "गौमाता को हरा चारा या गुड़ खिलाएं।",
                "action": "शांत और संतुलित आचरण बनाए रखें।"
            }
    return raw_insights

def render_page_forecast():
    if not st.session_state.get("has_valid_profile", False):
        is_hi = st.session_state.get("user_profile", {}).get("lang", "en") == "hi"
        prompt_title = "अपनी जन्म पत्रिका प्रोफाइल सेट करें" if is_hi else "Set Up Your Vedic Birth Profile"
        prompt_desc = "साप्ताहिक गोचर और दैनिक फल की गणना के लिए यूज़र प्रोफाइल टैब में अपना जन्म विवरण भरें।" if is_hi else "To calculate your 7-day moon transit matrix and forecasts, please enter your birth details in the User Profile tab."
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
        return

    prof = st.session_state.get("user_profile", {})
    current_lang = prof.get("lang", "en")
    is_hi = (current_lang == "hi")

    chart_info = st.session_state.get("chart_info", {})
    dob_parsed = st.session_state.get("dob_parsed")
    u_lat = prof.get("lat", 28.6139)
    u_lon = prof.get("lon", 77.2090)

    now_ist = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
    now_ist = now_ist.replace(tzinfo=None)

    transits = get_7_day_moon_transits(now_ist, chart_info["star_idx"])

    forecast_title_text = "🗓️ आगामी 7 दिनों का नक्षत्र गोचर एवं दैनिक फल" if is_hi else "🗓️ 7-Day Moon Transit Matrix & Daily Forecasts"
    render_html(f"""
    <div style="font-weight:900; font-size:1.25rem; color:#1e293b; margin-bottom:0.8rem;">
        {forecast_title_text}
    </div>
    """)

    pill_elements = []
    for tr in transits:
        off = tr["nav_offset"]
        if off in [1, 8]:
            bg, fg, label = "#dcfce7", "#15803d", ("शिखर 🟢🟢" if is_hi else "Peak 🟢🟢")
        elif off in [3, 5, 7]:
            bg, fg, label = "#f0fdf4", "#166534", ("उत्तम 🟢" if is_hi else "Good 🟢")
        elif off == 0:
            bg, fg, label = "#fef9c3", "#854d0e", ("फोकस 🟡" if is_hi else "Focus 🟡")
        else:
            bg, fg, label = "#fee2e2", "#b91c1c", ("सतर्क 🔴" if is_hi else "Guard 🔴")
        
        raw_s_name = tr['star_name']
        disp_s_name = NAKSHATRA_NAMES_HI.get(raw_s_name, raw_s_name) if is_hi else raw_s_name
        
        pill_elements.append(f"""
        <div style="background:{bg}; color:{fg}; padding:8px 6px; border-radius:10px; text-align:center; font-size:0.8rem; font-weight:800; border:1px solid rgba(0,0,0,0.06);">
            <div>{tr['date_str'].split(',')[0]}</div>
            <div style="font-size:0.86rem; margin:2px 0;">{label.split()[0]}</div>
            <div style="font-size:0.75rem;">{disp_s_name[:4]}</div>
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
                raw_s_name = tr['star_name']
                disp_s_name = NAKSHATRA_NAMES_HI.get(raw_s_name, raw_s_name) if is_hi else raw_s_name
                render_html(f"<b>{tr['date_str']}</b><br><span style='font-size:0.92rem; color:#475569; font-weight:700;'>{disp_s_name}</span>")
            with col_t2:
                vahan_name = tr['vahan'].split()[1] if len(tr['vahan'].split()) > 1 else tr['vahan']
                raw_nav = tr['nav_name'].split('(')[0].strip()
                disp_nav = NAVTARA_NAMES_HI.get(raw_nav, raw_nav) if is_hi else raw_nav
                mount_lbl = "वाहन (Mount)" if is_hi else "Mount"
                render_html(f"<span style='font-size:1.1rem;'>{tr['icon']}</span> <b>{disp_nav}</b><br><span style='font-size:0.88rem; color:#64748b;'>{mount_lbl}: {vahan_name}</span>")
            with col_t3:
                btn_lbl = "🔮 देखें" if is_hi else "🔮 View"
                if st.button(btn_lbl, key=f"btn_tr_{idx}", use_container_width=True):
                    st.session_state.selected_transit_idx = idx
                    st.rerun()

    safe_idx = min(len(transits) - 1, max(0, st.session_state.selected_transit_idx))
    sel_tr = transits[safe_idx]
    
    sel_p_day = get_personal_day_vibe(dob_parsed, sel_tr['date'], current_lang)
    v_info = calculate_shani_vahan(chart_info["star_idx"], sel_tr["star_idx"])
    raw_sel_insights = get_detailed_day_insights(sel_tr["nav_offset"], v_info, sel_tr['star_name'], sel_p_day)
    sel_insights = get_localized_forecast_insights(raw_sel_insights.get('theme_title'), raw_sel_insights, is_hi)
    sel_muh = calculate_daily_muhurtas(sel_tr['date'], u_lat, u_lon)

    raw_sel_star = sel_tr['star_name']
    disp_sel_star = NAKSHATRA_NAMES_HI.get(raw_sel_star, raw_sel_star) if is_hi else raw_sel_star
    raw_sel_nav = sel_tr['nav_name']
    for en_k, hi_v in NAVTARA_NAMES_HI.items():
        raw_sel_nav = raw_sel_nav.replace(en_k, hi_v) if is_hi else raw_sel_nav

    det_title = f"🔮 विस्तृत गोचर फलादेश: {sel_tr['date_str']} ({disp_sel_star})" if is_hi else f"🔮 Detailed Transit Forecast: {sel_tr['date_str']} ({sel_tr['star_name']})"
    transit_win_lbl = "⏰ गोचर विंडो (Transit Window):" if is_hi else "⏰ Transit Window:"
    nav_class_lbl = "🧭 नवतारा वर्गीकरण:" if is_hi else "🧭 Navtara Classification:"
    sat_mount_lbl = "🪐 शनि वाहन (Vahan):" if is_hi else "🪐 Saturn Mount (Vahan):"
    timing_win_lbl = f"⏱️ {sel_tr['date_str']} हेतु महत्वपूर्ण समय:" if is_hi else f"⏱️ Key Timing Windows for {sel_tr['date_str']}:"
    abhijit_lbl = "अभिजीत मुहूर्त" if is_hi else "Abhijit Muhurta"
    rahu_lbl = "राहु काल" if is_hi else "Rahu Kaal"
    avoid_sign_lbl = "अनुबंधों से बचें" if is_hi else "Avoid Signings"
    golden_per_lbl = "स्वर्ण काल" if is_hi else "Golden Period"
    archetype_lbl = "🎯 खगोलीय आर्कीटाइप" if is_hi else "🎯 Cosmic Archetype"
    favorable_lbl = "🟢 अनुकूल पहल एवं ग्रीन लाइट्स:" if is_hi else "🟢 Favorable Initiatives & Green Lights:"
    hazards_lbl = "🔴 संभावित जोखिम एवं सतर्कता:" if is_hi else "🔴 Hazards, Caution & Red Lights:"
    remedies_lbl = "🪔 इस गोचर हेतु निर्धारित वैदिक उपाय:" if is_hi else "🪔 Prescribed Daily Remedies for this Window:"

    render_html(f"""
    <div class="light-card-live" style="margin-top:1.1rem;">
        <div style="font-weight:900; font-size:1.25rem; color:#0369a1; margin-bottom:8px; border-bottom:1.5px solid #bae6fd; padding-bottom:5px;">
            {det_title}
        </div>
        
        <div style="font-size:0.94rem; color:#334155; margin-bottom:10px; line-height:1.5;">
            {transit_win_lbl} {sel_tr['start_str']} → {sel_tr['end_str']}<br>
            {nav_class_lbl} {raw_sel_nav} ({sel_tr['quality']})<br>
            {sat_mount_lbl} {v_info['name']} — <i>{v_info['speed']} ({v_info['type']})</i>
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bae6fd; margin-bottom:10px; font-size:0.91rem;">
            <b>{timing_win_lbl}</b><br>
            • 🌟 <b>{abhijit_lbl}:</b> {sel_muh['abhijit'][0].strftime('%I:%M %p')} – {sel_muh['abhijit'][1].strftime('%I:%M %p IST')} ({golden_per_lbl})<br>
            • ⚠️ <b>{rahu_lbl}:</b> {sel_muh['rahu'][0].strftime('%I:%M %p')} – {sel_muh['rahu'][1].strftime('%I:%M %p IST')} ({avoid_sign_lbl})
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #bae6fd; margin-bottom:12px;">
            <b style="color:#0369a1; font-size:1rem;">{archetype_lbl}: {sel_insights['theme_title']}</b>
            <div style="font-size:0.94rem; line-height:1.65; color:#1e293b; margin-top:4px;">
                {sel_insights['theme_desc']}
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr; gap:8px; margin-bottom:12px;">
            <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; border-left:4px solid #16a34a;">
                <b style="color:#15803d; font-size:0.92rem;">{favorable_lbl}</b>
                <div style="font-size:0.91rem; line-height:1.6; color:#166534; margin-top:2px;">{sel_insights['opportunities']}</div>
            </div>
            <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; border-left:4px solid #e11d48;">
                <b style="color:#be123c; font-size:0.92rem;">{hazards_lbl}</b>
                <div style="font-size:0.91rem; line-height:1.6; color:#9f1239; margin-top:2px;">{sel_insights['hazards']}</div>
            </div>
        </div>

        <div style="background:#f0f9ff; border-radius:10px; padding:12px; border:1px solid #bae6fd;">
            <b style="color:#0369a1; font-size:0.98rem;">{remedies_lbl}</b>
            <div style="font-size:0.92rem; line-height:1.65; color:#0c4a6e; margin-top:4px;">
                • <b>{"मंत्र जप" if is_hi else "Mantra Japa"}:</b> {sel_insights.get('remedy_mantra', '')}<br>
                • <b>{"दान एवं सामंजस्य" if is_hi else "Elemental Donation"}:</b> {sel_insights.get('remedy_charity', '')}<br>
                • <b>{"व्यक्तिगत प्रोटोकॉल" if is_hi else "Personal Protocol"}:</b> {sel_insights.get('remedy_action', '')}
            </div>
        </div>
    </div>
    """)
