# views/profile.py - Dedicated User Profile View with Full Hindi & English Support
import streamlit as st
import datetime
from databanks import (
    NAKSHATRAS,
    NAKSHATRA_BIO_DATA,
    get_nakshatra_rich_data,
    get_rashi_rich_data,
    get_lagna_rich_data,
    get_tara_bala_info,
    resolve_location_name
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

RASHI_NAMES_HI = {
    "Mesha": "मेष", "Vrishabha": "वृषभ", "Mithuna": "मिथुन",
    "Karka": "कर्क", "Simha": "सिंह", "Kanya": "कन्या",
    "Tula": "तुला", "Vrishchika": "वृश्चिक", "Dhanu": "धनु",
    "Makara": "मकर", "Kumbha": "कुंभ", "Meena": "मीन",
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन",
    "Cancer": "कर्क", "Leo": "सिंह", "Virgo": "कन्या",
    "Libra": "तुला", "Scorpio": "वृश्चिक", "Sagittarius": "धनु",
    "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
}

TARA_NAMES_HI = {
    "Janma": "जन्म तारा", "Sampat": "सम्पत तारा", "Vipat": "विपत तारा",
    "Kshema": "क्षेम तारा", "Pratyak": "प्रत्यक तारा", "Sadhana": "साधना तारा",
    "Naidhana": "निधन तारा", "Mitra": "मित्र तारा", "Ati-Mitra": "अति-मित्र तारा"
}

def render_page_profile():
    prof = st.session_state.get("user_profile", {})
    current_lang = prof.get("lang", "en")
    is_hi = (current_lang == "hi")
    
    has_valid_profile = st.session_state.get("has_valid_profile", False)
    dob_parsed = st.session_state.get("dob_parsed")
    tob_parsed = st.session_state.get("tob_parsed")
    chart_info = st.session_state.get("chart_info")
    u_lat = float(prof.get("lat", 28.6139))
    u_lon = float(prof.get("lon", 77.2090))

    if not has_valid_profile or st.session_state.get("edit_mode", False):
        form_title = "👤 वैदिक जन्म विवरण दर्ज करें" if is_hi else "👤 Configure Vedic Birth Profile"
        form_sub = "प्रामाणिक जन्म पत्रिका, लग्न, जन्म नक्षत्र एवं साढ़े साती की गणना हेतु अपना विवरण भरें:" if is_hi else "Please enter your birth details to generate your authentic Vedic chart, Lagna, Janma Nakshatra, and Sade Sati status."
        name_label = "पूरा नाम" if is_hi else "Full Name"
        dob_label = "जन्म तिथि" if is_hi else "Birth Date"
        time_label = "**जन्म समय (घंटा, मिनट एवं AM/PM):**" if is_hi else "**Birth Time (Hour, Minute & AM/PM):**"
        hr_lbl = "घंटा" if is_hi else "Hour"
        min_lbl = "मिनट" if is_hi else "Minute"
        city_label = "जन्म स्थान का नाम" if is_hi else "Birth Location / City Name"
        save_btn_lbl = "✨ सुरक्षित करें एवं गणना करें" if is_hi else "✨ Save & Calculate Profile"
        cancel_btn_lbl = "रद्द करें" if is_hi else "Cancel"
        err_name = "कृपया अपना पूरा नाम दर्ज करें।" if is_hi else "Please provide your full name."
        err_city = "कृपया जन्म स्थान का नाम दर्ज करें।" if is_hi else "Please provide a birth location name."
        spinner_txt = "स्थान के भौगोलिक निर्देशांक खोजे जा रहे हैं..." if is_hi else "Searching coordinates for your location..."

        render_html(f"""
        <div class="light-card-profile">
            <div style="font-weight:900; font-size:1.3rem; color:#9a3412; margin-bottom:0.5rem;">
                {form_title}
            </div>
            <div style="font-size:0.94rem; color:#475569; margin-bottom:1rem;">
                {form_sub}
            </div>
        </div>
        """)
        with st.form("create_profile_form"):
            new_name = st.text_input(name_label, value=prof.get("name", ""), placeholder="e.g. Rahul Sharma")
            d_init = dob_parsed if dob_parsed else datetime.date(1990, 1, 1)
            new_dob = st.date_input(dob_label, value=d_init)
            
            st.markdown(time_label)
            t_col1, t_col2, t_col3 = st.columns([1.5, 1.5, 1.5])
            with t_col1:
                init_hr = (tob_parsed.hour % 12) if tob_parsed else 12
                init_hr = 12 if init_hr == 0 else init_hr
                in_hour = st.selectbox(hr_lbl, options=list(range(1, 13)), index=init_hr - 1)
            with t_col2:
                init_min = tob_parsed.minute if tob_parsed else 0
                in_minute = st.selectbox(min_lbl, options=list(range(0, 60)), index=init_min)
            with t_col3:
                init_ampm = "PM" if (tob_parsed and tob_parsed.hour >= 12) else "AM"
                in_ampm = st.selectbox("AM / PM", options=["AM", "PM"], index=1 if init_ampm == "PM" else 0)

            new_city_query = st.text_input(city_label, value=prof.get("city", ""), placeholder="e.g. Panvel, Aurangabad, Mumbai, London, New York")

            c_save, c_canc = st.columns([2, 1])
            with c_save:
                submitted = st.form_submit_button(save_btn_lbl, type="primary", use_container_width=True)
            with c_canc:
                canceled = st.form_submit_button(cancel_btn_lbl, use_container_width=True)

            if submitted:
                if not new_name.strip():
                    st.error(err_name)
                elif not new_city_query.strip():
                    st.error(err_city)
                else:
                    hr_24 = in_hour % 12
                    if in_ampm == "PM":
                        hr_24 += 12
                    final_tob_str = f"{hr_24:02d}:{in_minute:02d}"

                    with st.spinner(spinner_txt):
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

    # Top User Details Banner
    lbl_profile_tag = "की प्रोफाइल" if is_hi else "'s Profile"
    lbl_dob_tag = "जन्म तिथि" if is_hi else "DOB"
    lbl_time_tag = "समय" if is_hi else "Time"
    lbl_place_tag = "स्थान" if is_hi else "Place"
    lbl_edit_btn = "✏️ विवरण बदलें" if is_hi else "✏️ Edit Details"

    with st.container(border=True):
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            render_html(f"""
            <div style="font-weight:900; font-size:1.2rem; color:#0f172a;">👤 {prof['name']} {lbl_profile_tag}</div>
            <div style="font-size:0.95rem; color:#334155; margin-top:5px; line-height:1.6;">
                📅 <b>{lbl_dob_tag}:</b> {dob_parsed.strftime('%d %B %Y')} &nbsp;|&nbsp; ⏰ <b>{lbl_time_tag}:</b> {tob_parsed.strftime('%I:%M %p')}<br>
                📍 <b>{lbl_place_tag}:</b> {prof['city']} ({u_lat:.4f}° N, {u_lon:.4f}° E)
            </div>
            """)
        with col_p2:
            if st.button(lbl_edit_btn, use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()

    bio_nak = NAKSHATRA_BIO_DATA.get(chart_info["star_idx"], NAKSHATRA_BIO_DATA[2])
    n_data = get_nakshatra_rich_data(chart_info["star_idx"])
    m_data = get_rashi_rich_data(chart_info["moon_rashi_idx"])
    l_data = get_lagna_rich_data(chart_info["lagna_idx"])
    
    # Sign component parsing
    moon_parts = chart_info['moon_rashi_name'].split()
    moon_p1 = moon_parts[0] if moon_parts else chart_info['moon_rashi_name']
    moon_p2 = moon_parts[-1] if len(moon_parts) > 1 else ""

    lagna_parts = chart_info['lagna_name'].split()
    lagna_p1 = lagna_parts[0] if lagna_parts else chart_info['lagna_name']

    raw_nak = chart_info.get('star_name', 'Ashwini')
    disp_nak = NAKSHATRA_NAMES_HI.get(raw_nak, raw_nak) if is_hi else raw_nak
    disp_rashi = RASHI_NAMES_HI.get(moon_p1, moon_p1) if is_hi else moon_p1
    disp_lagna = RASHI_NAMES_HI.get(lagna_p1, lagna_p1) if is_hi else lagna_p1
    disp_pada = f"चरण {chart_info['pada']}" if is_hi else f"Pada {chart_info['pada']}"

    lbl_verified_header = "🌌 प्रमाणित वैदिक कुंडली संरेखण" if is_hi else "🌌 Verified Vedic Kundali Alignment"
    lbl_ayanamsa = "चित्रापक्षीय लाहिड़ी अयनांश" if is_hi else "Chitrapaksha Lahiri Ayanamsa"
    lbl_lagna = "लग्न राशि" if is_hi else "Ascendant (Lagna)"
    lbl_nak = "जन्म नक्षत्र" if is_hi else "Janma Nakshatra"
    lbl_rashi = "चन्द्र राशि" if is_hi else "Moon Sign (Rashi)"

    lbl_nak_section = f"⭐ जन्म नक्षत्र: {disp_nak} ({disp_pada})" if is_hi else f"⭐ Janma Nakshatra: {chart_info['star_name']} (Pada {chart_info['pada']})"
    lbl_rashi_section = f"🌙 चन्द्र राशि (Moon Sign): {disp_rashi}" if is_hi else f"🌙 Moon Sign (Chandra Rashi): {chart_info['moon_rashi_name']}"
    lbl_lagna_section = f"🌅 लग्न राशि (Ascendant): {disp_lagna} ({chart_info['lagna_deg']})" if is_hi else f"🌅 Ascendant (Lagna): {chart_info['lagna_name']} at {chart_info['lagna_deg']}"

    attr_deity = "🏛️ अधिष्ठाता देवता:" if is_hi else "🏛️ Deity:"
    attr_symbol = "🔱 प्रतीक:" if is_hi else "🔱 Symbol:"
    attr_tree = "🌳 पूज्य वृक्ष:" if is_hi else "🌳 Sacred Tree:"
    attr_bird = "🦅 पक्षी:" if is_hi else "🦅 Sacred Bird:"
    attr_animal = "🦁 योनि प्राणी:" if is_hi else "🦁 Yoni Animal:"
    attr_lord = "🪐 नक्षत्र स्वामी:" if is_hi else "🪐 Planetary Lord:"

    attr_rashi_lord = "🪐 राशि स्वामी:" if is_hi else "🪐 Rashi Sovereign:"
    attr_element = "🔥 तत्व:" if is_hi else "🔥 Element:"
    attr_lagna_lord = "👑 लग्नेश:" if is_hi else "👑 Ascendant Lord:"
    attr_lagna_tattva = "🌍 लग्न तत्व:" if is_hi else "🌍 Lagna Tattva:"

    lbl_core_arch = "🧠 मूल संज्ञानात्मक एवं व्यवहारिक स्वभाव:" if is_hi else "🧠 Core Cognitive & Behavioral Archetype:"
    lbl_superpowers = "✨ विशिष्ट क्षमताएं व जन्मजात शक्तियां:" if is_hi else "✨ Superpowers & Natural Assets:"
    lbl_shadows = "⚠️ कर्मिक चुनौतियां व कमजोर पहलू:" if is_hi else "⚠️ Karmic Shadows & Blind Spots:"
    lbl_vocational = "💼 अनुकूल आजीविका एवं कार्यक्षेत्र:" if is_hi else "💼 Peak Vocational & Executive Fields:"
    lbl_life_path = "🔮 जीवन पथ एवं विकास यात्रा:" if is_hi else "🔮 Evolutionary Life Path Trajectory:"
    lbl_nak_remedies = "🪔 निर्धारित नक्षत्र वैदिक उपाय:" if is_hi else "🪔 Prescribed Vedic Nakshatra Remedies:"

    lbl_psychology = "🧠 भावनात्मक दृष्टिकोण एवं अवचेतन विचार:" if is_hi else "🧠 Emotional Mindset & Subconscious Processing:"
    lbl_instincts = "⚡ तनाव में स्वाभाविक प्रतिक्रियाएं:" if is_hi else "⚡ Stress Reflexes & Primal Coping Instincts:"
    lbl_relations = "❤️ पारस्परिक संबंध एवं साझेदारी शैली:" if is_hi else "❤️ Interpersonal Blueprint & Relationship Style:"
    lbl_health = "🌿 शारीरिक प्रकृति एवं स्वास्थ्य संतुलन:" if is_hi else "🌿 Bio-Rhythms & Physiological Vitality:"
    lbl_lunar_rem = "🪔 निर्धारित चन्द्र उपाय:" if is_hi else "🪔 Prescribed Lunar Remedies:"

    lbl_constitution = "🛡️ शारीरिक बनावट, ओज एवं प्रकृति (Prakriti):" if is_hi else "🛡️ Physical Constitution, Vitality & Posture (Prakriti):"
    lbl_persona = "👔 सामाजिक छवि एवं नेतृत्व क्षमता:" if is_hi else "👔 Outward Persona & Negotiating Presence:"
    lbl_life_arc = "🚀 जीवन की दिशा एवं संपत्ति निर्माण:" if is_hi else "🚀 Evolutionary Life Arc & Asset Compounding:"
    lbl_lagna_rem = "🪔 निर्धारित लग्न उपाय:" if is_hi else "🪔 Prescribed Ascendant Remedies:"

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.35rem; color:#9a3412; margin-bottom:1rem; border-bottom:2px solid #fed7aa; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{lbl_verified_header}</span>
            <span style="font-size:0.85rem; background:#ffedd5; color:#c2410c; padding:4px 10px; border-radius:20px; font-weight:800;">{lbl_ayanamsa}</span>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:10px; text-align:center; margin-bottom:1.25rem;">
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{lbl_lagna}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{disp_lagna}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{chart_info['lagna_deg']}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{lbl_nak}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{disp_nak}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{disp_pada}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{lbl_rashi}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{disp_rashi}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{moon_p2}</div>
            </div>
        </div>

        <!-- JANMA NAKSHATRA CARD -->
        <div style="background:#fffaf0; border-radius:14px; padding:14px; border:1.5px solid #fed7aa; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#9a3412; margin-bottom:8px;">
                {lbl_nak_section}
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:8px; margin-bottom:12px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_deity}</b> {bio_nak['deity']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_symbol}</b> {bio_nak['symbol']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_tree}</b> {bio_nak['tree']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_bird}</b> {bio_nak['bird']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_animal}</b> {bio_nak['animal']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_lord}</b> {bio_nak['lord']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #fed7aa; margin-bottom:8px;">
                <b style="color:#9a3412; font-size:0.96rem;">{lbl_core_arch}</b>
                <div style="font-size:0.92rem; line-height:1.65; color:#431407; margin-top:2px;">{n_data['core']}</div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:8px;">
                <div style="background:#f0fdf4; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                    <b style="color:#15803d; font-size:0.92rem;">{lbl_superpowers}</b>
                    <div style="font-size:0.89rem; line-height:1.55; color:#14532d; margin-top:2px;">{n_data['strengths']}</div>
                </div>
                <div style="background:#fff1f2; border-radius:10px; padding:10px; border:1px solid #fecdd3;">
                    <b style="color:#be123c; font-size:0.92rem;">{lbl_shadows}</b>
                    <div style="font-size:0.89rem; line-height:1.55; color:#881337; margin-top:2px;">{n_data['shadows']}</div>
                </div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #fed7aa; margin-bottom:8px; font-size:0.91rem; color:#431407;">
                <b>{lbl_vocational}</b><br>{n_data['careers']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #fed7aa; margin-bottom:8px; font-size:0.91rem; color:#431407;">
                <b>{lbl_life_path}</b><br>{n_data['prediction']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #f97316; font-size:0.91rem; color:#431407;">
                <b>{lbl_nak_remedies}</b><br>{n_data['remedies']}
            </div>
        </div>

        <!-- MOON RASHI CARD -->
        <div style="background:#f0fdf4; border-radius:14px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#065f46; margin-bottom:8px;">
                {lbl_rashi_section}
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:10px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>{attr_element}</b> {m_data['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>{attr_rashi_lord}</b> {m_data['ruler']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>{lbl_psychology}</b><br>{m_data['psychology']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>{lbl_instincts}</b><br>{m_data['instincts']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>{lbl_relations}</b><br>{m_data['relations']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>{lbl_health}</b><br>{m_data['health']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #10b981; font-size:0.91rem; color:#14532d;">
                <b>{lbl_lunar_rem}</b><br>{m_data['remedies']}
            </div>
        </div>

        <!-- ASCENDANT (LAGNA) CARD -->
        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:8px;">
                {lbl_lagna_section}
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:10px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>{attr_lagna_tattva}</b> {l_data['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>{attr_lagna_lord}</b> {l_data['lord']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>{lbl_constitution}</b><br>{l_data['constitution']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>{lbl_persona}</b><br>{l_data['persona']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>{lbl_life_arc}</b><br>{l_data['life_arc']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #8b5cf6; font-size:0.91rem; color:#3b0764;">
                <b>{lbl_lagna_rem}</b><br>{l_data['remedies']}
            </div>
        </div>
    </div>
    """)

    # Tara Bala Widget (Fully Localized)
    lbl_tara_title = "**🤝 नक्षत्र अनुकूलता एवं ऊर्जा संबंध (तारा बल - Tara Bala)**" if is_hi else "**🤝 Nakshatra Synergy & Compatibility Evaluator (Tara Bala)**"
    lbl_select_star = "अन्य व्यक्ति का जन्म नक्षत्र चुनें:" if is_hi else "Select Counterpart's Birth Star:"
    lbl_dynamic = "ऊर्जा तालमेल (Dynamic):" if is_hi else "Dynamic:"

    with st.container(border=True):
        st.markdown(lbl_tara_title)
        
        if is_hi:
            star_display_options = [f"{NAKSHATRA_NAMES_HI.get(s, s)} ({s})" for s in NAKSHATRAS]
            partner_star_sel = st.selectbox(lbl_select_star, options=star_display_options, index=0)
            p_star_idx = star_display_options.index(partner_star_sel) + 1
        else:
            partner_star_choice = st.selectbox(lbl_select_star, options=NAKSHATRAS, index=0)
            p_star_idx = NAKSHATRAS.index(partner_star_choice) + 1

        tara_res = get_tara_bala_info(chart_info['star_idx'], p_star_idx)
        
        box_bg = '#f0fdf4' if tara_res['is_allied'] else ('#fff1f2' if tara_res['is_friction'] else '#f8fafc')
        box_border = '#86efac' if tara_res['is_allied'] else ('#fecdd3' if tara_res['is_friction'] else '#e2e8f0')
        box_color = '#15803d' if tara_res['is_allied'] else ('#be123c' if tara_res['is_friction'] else '#0f172a')
        
        disp_tara_name = TARA_NAMES_HI.get(tara_res['tara_name'], tara_res['tara_name']) if is_hi else tara_res['tara_name']

        render_html(f"""
        <div style="background:{box_bg}; border:1.5px solid {box_border}; border-radius:12px; padding:12px; margin-top:8px;">
            <div style="font-size:1.05rem; font-weight:800; color:{box_color};">
                {tara_res['icon']} {disp_tara_name} — {tara_res['quality']}
            </div>
            <div style="font-size:0.92rem; font-weight:700; color:#334155; margin-top:4px;">
                {lbl_dynamic} {tara_res['relationship_tone']}
            </div>
            <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.5;">
                {tara_res['advice']}
            </div>
        </div>
        """)
