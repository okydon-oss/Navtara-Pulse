# views/live.py - Dedicated Today's Live Horoscope View with Complete Bilingual Support
import streamlit as st
import datetime
from databanks import (
    NAKSHATRAS,
    NAVTARA_NAMES,
    get_current_nakshatra_window,
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

def render_page_live():
    if not st.session_state.get("has_valid_profile", False):
        is_hi = st.session_state.get("user_profile", {}).get("lang", "en") == "hi"
        prompt_title = "अपनी जन्म पत्रिका प्रोफाइल सेट करें" if is_hi else "Set Up Your Vedic Birth Profile"
        prompt_desc = "दैनिक खगोलीय प्रवाह और राशिफल की गणना के लिए यूज़र प्रोफाइल टैब में अपना जन्म विवरण भरें।" if is_hi else "To calculate your live daily cosmic pulse and horoscope, please enter your birth details in the User Profile tab."
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

    cur_star_idx, s_dt, e_dt = get_current_nakshatra_window(now_ist)
    offset = (cur_star_idx - chart_info["star_idx"]) % 9
    nav_name, icon, quality = NAVTARA_NAMES[offset]
    
    disp_nav_name = NAVTARA_NAMES_HI.get(nav_name.split()[0], nav_name) if is_hi else nav_name
    raw_cur_star = NAKSHATRAS[cur_star_idx - 1]
    disp_cur_star = NAKSHATRA_NAMES_HI.get(raw_cur_star, raw_cur_star) if is_hi else raw_cur_star

    vahan_info = calculate_shani_vahan(chart_info["star_idx"], cur_star_idx)
    p_day = get_personal_day_vibe(dob_parsed, now_ist.date(), current_lang)

    insights = get_detailed_day_insights(offset, vahan_info, raw_cur_star, p_day)

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
                <b style="color:#b91c1c; font-size:1.02rem;">{"🔴 सतर्कता काल सक्रिय: राहु काल जारी" if is_hi else "🔴 CAUTION WINDOW ACTIVE: Rahu Kaal in Operation"} ({now_time_str} IST)</b>
                <div style="font-size:0.88rem; color:#7f1d1d; margin-top:2px;">{"नवीन अनुबंधों, यात्रा प्रस्थान और बड़े पूंजी निवेश को" if is_hi else "Pause new contract signing, travel departures, and major capital moves until"} {rahu_e.strftime('%I:%M %p')} {"तक रोकें।" if is_hi else "."}</div>
            </div>
            <span style="font-size:1.8rem;">🛑</span>
        </div>
        """
    elif is_yama:
        status_banner = f"""
        <div style="background:#fee2e2; border:2px solid #ef4444; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#b91c1c; font-size:1.02rem;">{"🔴 सतर्कता काल सक्रिय: यमघंट काल जारी" if is_hi else "🔴 CAUTION WINDOW ACTIVE: Yamaganda in Operation"} ({now_time_str} IST)</b>
                <div style="font-size:0.88rem; color:#7f1d1d; margin-top:2px;">{"महत्वपूर्ण उपक्रमों या अंतिम कानूनी समझौतों के आरंभ से बचें।" if is_hi else f"Avoid launching crucial ventures or final legal settlements until {yama_e.strftime('%I:%M %p')}."}</div>
            </div>
            <span style="font-size:1.8rem;">⚠️</span>
        </div>
        """
    elif is_abhijit:
        status_banner = f"""
        <div style="background:#dcfce7; border:2px solid #22c55e; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#15803d; font-size:1.02rem;">{"🟢 स्वर्ण विजय काल सक्रिय: अभिजीत मुहूर्त" if is_hi else "🟢 GOLDEN ACTION WINDOW ACTIVE: Abhijit Muhurta"} ({now_time_str} IST)</b>
                <div style="font-size:0.88rem; color:#14532d; margin-top:2px;">{"सर्वश्रेष्ठ खगोलीय विजय काल। अनुमोदन, लॉन्च और महत्वपूर्ण निर्णयों हेतु अत्यंत शुभ।" if is_hi else f"Supreme cosmic victory window. Highly auspicious for approvals, launches, and decisions until {abhijit_e.strftime('%I:%M %p')}."}</div>
            </div>
            <span style="font-size:1.8rem;">🌟</span>
        </div>
        """
    else:
        status_banner = f"""
        <div style="background:#f0fdf4; border:1.5px solid #86efac; border-radius:12px; padding:12px 14px; display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <b style="color:#166534; font-size:0.98rem;">{"🟢 कार्य हेतु सुरक्षित समय: मानक अनुकूल कक्षा" if is_hi else "🟢 SAFE TO ACT: Standard Favorable Orbit"} ({now_time_str} IST)</b>
                <div style="font-size:0.86rem; color:#15803d; margin-top:2px;">{"वर्तमान में कोई ग्रह अवरोध सक्रिय नहीं है।" if is_hi else "No planetary friction windows currently active."} {"अगला अभिजीत" if is_hi else "Next Abhijit"}: {abhijit_s.strftime('%I:%M %p')} | {"राहु काल" if is_hi else "Rahu Kaal"}: {rahu_s.strftime('%I:%M %p')}</div>
            </div>
            <span style="font-size:1.6rem;">⏱️</span>
        </div>
        """

    page_title = "⚡ आज का दैनिक खगोलीय प्रवाह" if is_hi else "⚡ Today's Live Cosmic Pulse"
    moon_nak_lbl = "वर्तमान चन्द्र नक्षत्र" if is_hi else "CURRENT MOON NAKSHATRA"
    timing_lbl = f"आज के लिए महत्वपूर्ण समय-विंडो ({prof.get('city', 'Location')}):" if is_hi else f"Timing Windows for Today ({prof.get('city', 'Location')}):"
    checklist_title = "📋 व्यावहारिक कार्य निष्पादन चेकलिस्ट" if is_hi else "Practical Action Green Light Checklist"
    
    career_lbl = "💼 करियर एवं निष्पादन:" if is_hi else "Career & Execution:"
    wealth_lbl = "💰 धन एवं वित्तीय स्थिति:" if is_hi else "Wealth & Financials:"
    family_lbl = "🏠 पारिवारिक एवं संबंध:" if is_hi else "Domestic & Relations:"
    health_lbl = "🌿 स्वास्थ्य एवं ऊर्जा:" if is_hi else "Health & Energy:"

    render_html(f"""
    <div class="light-card-live">
        <div style="font-weight:900; font-size:1.25rem; color:#0369a1; margin-bottom:1rem; border-bottom:2px solid #bae6fd; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{page_title}</span>
            <span style="font-size:0.85rem; background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:20px; font-weight:900;">LIVE IST</span>
        </div>

        {status_banner}

        <div style="background:#f0f9ff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:0.85rem; color:#0284c7; font-weight:800; text-transform:uppercase;">{moon_nak_lbl}</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#0369a1;">{disp_cur_star}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.8rem;">{icon}</div>
                    <div style="font-size:0.88rem; font-weight:900; color:#0369a1;">{quality}</div>
                </div>
            </div>
            <div style="font-size:1.05rem; font-weight:900; color:#0284c7; margin-top:8px;">नवतारा (Navtara): {disp_nav_name}</div>
            <div style="font-size:0.92rem; color:#334155; margin-top:6px; line-height:1.5;">
                ⏳ <b>{"सक्रिय चन्द्र गोचर विंडो" if is_hi else "Active Moon Transit Window"}:</b><br>
                {s_dt.strftime('%a, %d %b %I:%M %p')} → {e_dt.strftime('%a, %d %b %I:%M %p IST')}
            </div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <b>⏱️ {timing_lbl}</b><br>
            • 🌟 <b>अभिजीत मुहूर्त (Abhijit):</b> {abhijit_s.strftime('%I:%M %p')} – {abhijit_e.strftime('%I:%M %p IST')} ({"स्वर्ण काल" if is_hi else "Golden Period"})<br>
            • ⚠️ <b>राहु काल (Rahu Kaal):</b> {rahu_s.strftime('%I:%M %p')} – {rahu_e.strftime('%I:%M %p IST')} ({"अनुबंध से बचें" if is_hi else "Avoid Signings"})
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#0369a1; margin-bottom:10px; border-bottom:1px solid #e0f2fe; padding-bottom:5px;">
                {checklist_title}
            </div>
            
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.92rem;">
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>{career_lbl}</b><br>
                    <span style="color:#0f172a;">{'🟢 अनुकूल: अभिजीत मुहूर्त में साहसिक कदम उठाएं' if is_hi and offset in [1,3,5,7,8] else ('🟢 Green Light: Take bold action in Abhijit window' if offset in [1,3,5,7,8] else ('🔴 संयम रखें: उच्च-जोखिम वाले अनुरोधों से बचें' if is_hi else '🔴 Hold Back: Avoid starting disputes or high-stakes requests'))}</span>
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>{wealth_lbl}</b><br>
                    <span style="color:#0f172a;">{'🟢 शुभ: पूंजी अंतरण एवं निवेश हेतु उपयुक्त' if is_hi and offset in [1,3,5,7,8] else ('🟢 Favorable: Execute capital transfers & investments' if offset in [1,3,5,7,8] else ('🔴 सतर्कता: सट्टेबाजी व कर्ज से दूर रहें' if is_hi else '🔴 Cautious: Strictly avoid speculative leverage & loans'))}</span>
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>{family_lbl}</b><br>
                    <span style="color:#0f172a;">{'🟢 सौहार्दपूर्ण: पारिवारिक चर्चा हेतु उत्तम' if is_hi and offset in [1,3,5,7,8] else ('🟢 Harmonious: Excellent for family discussions' if offset in [1,3,5,7,8] else ('🟡 संवेदनशील: शांत रहें; वाद-विवाद टालें' if is_hi else '🟡 Sensitive: Practice calm listening; avoid debates'))}</span>
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                    <b>{health_lbl}</b><br>
                    <span style="color:#0f172a;">{'🟢 उच्च ऊर्जा: व्यायाम और शारीरिक श्रम हेतु बढ़िया' if is_hi and offset in [1,3,5,7,8] else ('🟢 High Vitality: Great for workouts & physical tasks' if offset in [1,3,5,7,8] else ('🔴 थकान की संभावना: पूर्ण विश्राम और जलयोजन रखें' if is_hi else '🔴 Prone to Fatigue: Rest well and hydrate deeply'))}</span>
                </div>
            </div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd; margin-bottom:1.1rem;">
            <div style="font-weight:900; font-size:1.1rem; color:#0369a1; margin-bottom:8px; border-bottom:1px solid #e0f2fe; padding-bottom:5px;">
                🧠 {"संज्ञानात्मक एवं रणनीतिक थीम" if is_hi else "Cognitive & Strategic Archetype"}: {insights.get('theme_title', '')}
            </div>
            <div style="font-size:0.95rem; line-height:1.7; color:#1e293b; margin-bottom:12px;">
                {insights.get('theme_desc', '')}
            </div>

            <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; border-left:4px solid #16a34a; margin-bottom:10px;">
                <b style="color:#15803d; font-size:0.95rem;">{"🚀 प्रमुख अवसर एवं प्रोटोकॉल" if is_hi else "🚀 Prime Opportunities & Protocols"}:</b>
                <div style="font-size:0.92rem; line-height:1.6; color:#166534; margin-top:2px;">{insights.get('opportunities', '')}</div>
            </div>

            <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; border-left:4px solid #e11d48;">
                <b style="color:#be123c; font-size:0.95rem;">{"⚠️ संभावित जोखिम एवं लाल झंडे" if is_hi else "⚠️ Potential Hazards & Red Flags"}:</b>
                <div style="font-size:0.92rem; line-height:1.6; color:#9f1239; margin-top:2px;">{insights.get('hazards', '')}</div>
            </div>
        </div>

        <div style="background:#f0f9ff; border-radius:12px; padding:14px; border:1.5px solid #bae6fd;">
            <div style="font-weight:900; font-size:1.1rem; color:#0369a1; margin-bottom:8px; border-bottom:1px solid #bae6fd; padding-bottom:5px;">
                🪔 {"लक्षित दैनिक खगोलीय उपाय" if is_hi else "Targeted Daily Cosmic Remedies"}:
            </div>
            <div style="font-size:0.94rem; line-height:1.7; color:#0c4a6e;">
                • <b>{"रक्षक मंत्र" if is_hi else "Aura Protection Mantra"}:</b> {insights.get('remedy_mantra', '')}<br>
                • <b>{"तत्वीय दान एवं सामंजस्य" if is_hi else "Elemental Harmony & Donation"}:</b> {insights.get('remedy_charity', '')}<br>
                • <b>{"व्यवहारिक कैलिब्रेशन" if is_hi else "Behavioral & Color Calibration"}:</b> {insights.get('remedy_action', '')}
            </div>
        </div>
    </div>
    """)
