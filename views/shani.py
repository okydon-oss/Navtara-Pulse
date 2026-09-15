# views/shani.py - Dedicated Shani, Paya & Sade Sati View with Full Hindi & English Support
import streamlit as st

def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

# Hindi Translation Dictionaries for Shani and Sade Sati Data
SHANI_HI_MAP = {
    "Swarna Paya": "स्वर्ण पाया (Gold Paya)",
    "Roupya Paya": "रौप्य पाया (Silver Paya)",
    "Loha Paya": "लोह पाया (Iron Paya)",
    "Tamra Paya": "ताम्र पाया (Copper Paya)",
    "Very Challenging": "अति संवेदनशील / संघर्षपूर्ण",
    "Favorable / Balanced": "अनुकूल एवं संतुलित",
    "Demanding & Strategic": "परिश्रम एवं रणनीति प्रधान",
    "Saturn in Pisces (Meena)": "मीन राशि में शनि गोचर",
    "Active Transit Paya for Your": "आपकी चन्द्र राशि हेतु वर्तमान गोचर पाया:",
    "Active Window": "सक्रिय समयावधि",
    "Core Focus": "मुख्य कर्मक्षेत्र",
    "Complete 7.5-Year Sade Sati Evolutionary Blueprint for": "चन्द्र राशि हेतु 7.5-वर्षीय शनि साढ़े साती का संपूर्ण चक्र:",
    "Phase 1: Rising Phase": "प्रथम चरण: उदय काल (द्वादश भाव गोचर)",
    "Phase 2: Peak Janma Shani": "द्वितीय चरण: शिखर काल (जन्मांग चन्द्र पर शनि)",
    "Phase 3: Setting Phase": "तृतीय चरण: अस्त काल (द्वितीय भाव गोचर)",
    "Core Dynamic": "मूल प्रभाव",
    "Financial & Career": "आर्थिक एवं कार्यक्षेत्र",
    "Karmic Mastery": "कर्मिक संतुलन एवं सीख",
    "Prescribed Remedies for Planetary Neutralization": "🪐 ग्रह शांति एवं शमन हेतु निर्धारित वैदिक उपाय:",
    "Open Dedicated Digital Japa Counter": "📿 डिजिटल जप माला काउंटर खोलें"
}

def render_page_shani():
    if not st.session_state.get("has_valid_profile", False):
        is_hi = st.session_state.get("user_profile", {}).get("lang", "en") == "hi"
        prompt_title = "अपनी जन्म पत्रिका प्रोफाइल सेट करें" if is_hi else "Set Up Your Vedic Birth Profile"
        prompt_desc = "शनि पाया और साढ़े साती की सटीक गणना के लिए यूज़र प्रोफाइल टैब में अपना जन्म विवरण भरें।" if is_hi else "To calculate your Shani Paya and Sade Sati status, please enter your birth details in the User Profile tab."
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

    current_lang = st.session_state.get("user_profile", {}).get("lang", "en")
    is_hi = (current_lang == "hi")

    chart_info = st.session_state.get("chart_info", {})
    shani_paya_data = st.session_state.get("shani_paya_data", {})
    shani_sadesati_data = st.session_state.get("shani_sadesati_data", {})

    m_name = chart_info.get('moon_rashi_name', 'Mesha').split()[0]
    
    p1_active_tag = '<span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW</span>' if shani_sadesati_data.get('phase_1_active') else ''
    p2_active_tag = '<span style="font-size:0.82rem; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW (PEAK)</span>' if shani_sadesati_data.get('phase_2_active') else ''
    p3_active_tag = '<span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW</span>' if shani_sadesati_data.get('phase_3_active') else ''

    # Localized text translations
    paya_name = shani_paya_data.get('paya', '')
    if is_hi:
        if "Swarna" in paya_name or "Gold" in paya_name: paya_display = "स्वर्ण पाया (Gold Paya — अत्यधिक संघर्ष व परिश्रम)"
        elif "Roupya" in paya_name or "Silver" in paya_name: paya_display = "रौप्य पाया (Silver Paya — मध्यम फलदायक व शुभ)"
        elif "Tamra" in paya_name or "Copper" in paya_name: paya_display = "ताम्र पाया (Copper Paya — प्रगति एवं आर्थिक लाभ)"
        else: paya_display = "लोह पाया (Iron Paya — कड़ा संघर्ष व अनुशासन)"
    else:
        paya_display = paya_name

    main_title = "🪐 शनि पाया एवं साढ़े साती संपूर्ण जीवन-क्षेत्र मैट्रिक्स" if is_hi else "🪐 Shani Paya & Sade Sati Exhaustive Life-Domain Matrix"
    saturn_transit = "मीन राशि में शनि गोचर" if is_hi else "Saturn in Pisces (Meena)"
    active_paya_lbl = f"आपकी {m_name.upper()} चन्द्र राशि हेतु वर्तमान गोचर पाया:" if is_hi else f"ACTIVE TRANSIT PAYA FOR YOUR {m_name.upper()} MOON"
    
    status_grade = shani_paya_data.get('status', '')
    if is_hi:
        status_grade_disp = "संघर्षपूर्ण एवं संवेदनशील" if "Challenging" in status_grade else "संतुलित एवं रणनीतिक"
    else:
        status_grade_disp = status_grade

    tone_disp = shani_paya_data.get('tone', '')
    timeline_disp = shani_paya_data.get('timeline', '')
    desc_disp = shani_paya_data.get('desc', '')
    houses_disp = shani_paya_data.get('houses', '')

    sadesati_title = f"⚖️ {m_name} चन्द्र राशि हेतु सक्रिय साढ़े साती / ढैय्या जीवन-क्षेत्र विश्लेषण" if is_hi else f"⚖️ Active Sade Sati / Dhaiya Life-Domain Breakdown for {m_name} Moon"
    
    render_html(f"""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.35rem; color:#5b21b6; margin-bottom:1rem; border-bottom:2px solid #ddd6fe; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{main_title}</span>
            <span style="font-size:0.85rem; background:#ede9fe; color:#5b21b6; padding:4px 10px; border-radius:20px; font-weight:800;">{saturn_transit}</span>
        </div>
        
        <!-- SHANI PAYA IN-DEPTH MATRIX -->
        <div style="background:#f5f3ff; border-radius:14px; padding:16px; border:1.5px solid #e9d5ff; margin-bottom:1.25rem;">
            <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">{active_paya_lbl}</div>
            <div style="font-size:1.45rem; font-weight:900; color:#5b21b6; margin:4px 0;">{paya_display}</div>
            <div style="font-size:0.98rem; color:#7c3aed; font-weight:800;">{"स्तर" if is_hi else "Grade"}: {status_grade_disp} | {"ऊर्जा" if is_hi else "Dynamic"}: {tone_disp}</div>
            <div style="font-size:0.92rem; color:#475569; margin-top:3px;"><b>{"सक्रिय समयावधि" if is_hi else "Active Timeline"}:</b> {timeline_disp}</div>
            
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1px solid #ddd6fe; margin-top:12px; font-size:0.93rem; color:#3b0764; line-height:1.7;">
                <b>🏛️ {"शास्त्रीय आधार" if is_hi else "Classical Foundation"}:</b> {desc_disp}<br>
                <b>🧭 {"सक्रिय भाव धुरी" if is_hi else "Operating Houses"}:</b> शनि आपकी जन्मकालीन चन्द्र राशि से {houses_disp} भावों को सक्रिय कर रहे हैं।
            </div>

            <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-top:12px;">
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #f97316; font-size:0.91rem; color:#7c2d12; line-height:1.6;">
                    <b>🌿 1. {"स्वास्थ्य एवं प्राण ऊर्जा प्रभाव" if is_hi else "Health & Vitality Impact"}:</b><br>{shani_paya_data.get('health', '')}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #10b981; font-size:0.91rem; color:#14532d; line-height:1.6;">
                    <b>💰 2. {"धन संचय एवं नकदी प्रवाह" if is_hi else "Wealth & Cash Flow Dynamics"}:</b><br>{shani_paya_data.get('wealth', '')}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #8b5cf6; font-size:0.91rem; color:#3b0764; line-height:1.6;">
                    <b>👨‍👩‍👧‍👦 3. {"पारिवारिक एवं घरेलू सामंजस्य" if is_hi else "Family & Domestic Harmony"}:</b><br>{shani_paya_data.get('family', '')}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #e11d48; font-size:0.91rem; color:#881337; line-height:1.6;">
                    <b>📉 4. {"ऋण एवं देनदारियों का प्रबंधन" if is_hi else "Loans & Liabilities Management"}:</b><br>{shani_paya_data.get('loan', '')}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #065f46; font-size:0.91rem; color:#065f46; line-height:1.6;">
                    <b>🤝 5. {"व्यापारिक साझेदारियाँ व अनुबंध" if is_hi else "Partnerships & Business Alliances"}:</b><br>{shani_paya_data.get('partner', '')}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #d97706; font-size:0.91rem; color:#78350f; line-height:1.6;">
                    <b>🍀 6. {"भाग्य एवं अवसर संरेखण" if is_hi else "Luck & Destiny Alignment"}:</b><br>{shani_paya_data.get('luck', '')}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #0284c7; font-size:0.91rem; color:#0369a1; line-height:1.6;">
                    <b>💼 7. {"कर्मक्षेत्र, अधिकार एवं प्रतिष्ठा" if is_hi else "Career, Authority & Executive Standing"}:</b><br>{shani_paya_data.get('career', '')}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #475569; font-size:0.91rem; color:#0f172a; line-height:1.6;">
                    <b>🪔 8. {"लक्षित तत्वीय उपाय एवं सावधानियाँ" if is_hi else "Targeted Elemental Countermeasures"}:</b><br>{shani_paya_data.get('protocol', '')}
                </div>
            </div>
        </div>

        <!-- SADE SATI / DHAIYA EXHAUSTIVE MATRIX -->
        <div style="background:#ffffff; border-radius:14px; padding:16px; border:1.5px solid #ddd6fe; margin-bottom:1.25rem;">
            <div style="font-weight:900; font-size:1.2rem; color:#5b21b6; margin-bottom:10px; border-bottom:1px solid #e9d5ff; padding-bottom:5px; display:flex; justify-content:space-between; align-items:center;">
                <span>{sadesati_title}</span>
                <span style="font-size:0.82rem; background:#ede9fe; color:#5b21b6; padding:3px 8px; border-radius:10px; font-weight:800;">{shani_sadesati_data.get('status_title', '').split(':')[0]}</span>
            </div>
            
            <div style="background:{'#fef2f2' if shani_sadesati_data.get('phase_2_active') else '#f5f3ff'}; border-radius:12px; padding:14px; border-left:5px solid {'#ef4444' if shani_sadesati_data.get('phase_2_active') else '#9333ea'}; margin-bottom:14px;">
                <b style="color:{'#991b1b' if shani_sadesati_data.get('phase_2_active') else '#5b21b6'}; font-size:1.1rem;">{shani_sadesati_data.get('status_title', '')}</b>
                <div style="font-size:0.92rem; color:#64748b; margin:3px 0 8px 0;"><b>{"सक्रिय समयावधि" if is_hi else "Active Window"}:</b> {shani_sadesati_data.get('dates', '')} | <b>{"मुख्य फोकस" if is_hi else "Core Focus"}:</b> {shani_sadesati_data.get('focus', '')}</div>
                <div style="font-size:0.95rem; line-height:1.7; color:#334155;">{shani_sadesati_data.get('impact', '')}</div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:14px;">
                <div style="background:#fff7ed; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#7c2d12; border-left:4px solid #f97316;">
                    <b>🌿 1. {"स्वास्थ्य प्रभाव" if is_hi else "Health & Vitality Impact"}:</b><br>{shani_sadesati_data.get('health', '')}
                </div>
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#14532d; border-left:4px solid #10b981;">
                    <b>💰 2. {"धन एवं नकदी प्रवाह" if is_hi else "Wealth Dynamics"}:</b><br>{shani_sadesati_data.get('wealth', '')}
                </div>
                <div style="background:#faf5ff; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#3b0764; border-left:4px solid #8b5cf6;">
                    <b>👨‍👩‍👧‍👦 3. {"परिवार व गृहस्थी" if is_hi else "Family Harmony"}:</b><br>{shani_sadesati_data.get('family', '')}
                </div>
                <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#881337; border-left:4px solid #e11d48;">
                    <b>📉 4. {"ऋण व देयताएं" if is_hi else "Loans & Liabilities"}:</b><br>{shani_sadesati_data.get('loan', '')}
                </div>
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#065f46;">
                    <b>🤝 5. {"साझेदारियाँ" if is_hi else "Partnerships"}:</b><br>{shani_sadesati_data.get('partner', '')}
                </div>
                <div style="background:#fffbeb; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#78350f;">
                    <b>🍀 6. {"भाग्य संरेखण" if is_hi else "Destiny Alignment"}:</b><br>{shani_sadesati_data.get('luck', '')}
                </div>
                <div style="background:#f0f9ff; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#0369a1;">
                    <b>💼 7. {"करियर व प्रतिष्ठा" if is_hi else "Career Standing"}:</b><br>{shani_sadesati_data.get('career', '')}
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#0f172a;">
                    <b>🪔 8. {"उपाय प्रोटोकॉल" if is_hi else "Remedial Protocol"}:</b><br>{shani_sadesati_data.get('remedy', '')}
                </div>
            </div>

            <div style="font-weight:900; font-size:1.05rem; color:#475569; margin:16px 0 8px 0; border-top:1px solid #e9d5ff; padding-top:10px;">
                {"चन्द्र राशि हेतु 7.5-वर्षीय शनि साढ़े साती के तीनों चरण:" if is_hi else f"Complete 7.5-Year Sade Sati Evolutionary Blueprint for {m_name} Moon:"}
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #a855f7; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#5b21b6; font-size:0.96rem;">{"प्रथम चरण: उदय काल (द्वादश भाव गोचर)" if is_hi else f"Phase 1: Rising Phase (Saturn in {shani_sadesati_data.get('rashi_12th', '')} / 12th from Moon)"}</b>
                    {p1_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>{"मूल प्रभाव" if is_hi else "Core Dynamic"}:</b> {"मानसिक पुनर्गठन, अंतर्मुखता, और व्यय नियंत्रण का काल।" if is_hi else "Subconscious restructuring, elimination of toxic habits, and mental detachment."}<br>
                    • <b>{"आर्थिक एवं करियर" if is_hi else "Financial & Career"}:</b> {"यात्राओं, निवेश या स्वास्थ्य संबंधी खर्चों में वृद्धि; कार्य पर्दे के पीछे से होते हैं।" if is_hi else "Spikes in expenses related to travel, relocation, or healthcare; work happens behind the scenes."}<br>
                    • <b>{"कर्मिक सीख" if is_hi else "Karmic Mastery"}:</b> {"पुरानी मानसिक बाधाओं को छोड़कर भविष्य के लिए मानसिक रूप से तैयार होना।" if is_hi else "Shedding psychological baggage and preparing for the core transit."}
                </div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #ef4444; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#991b1b; font-size:0.96rem;">{"द्वितीय चरण: शिखर काल (जन्मांग चन्द्र पर शनि)" if is_hi else f"Phase 2: Peak Janma Shani (Saturn in {shani_sadesati_data.get('rashi_1st', '')} / Over Natal Moon)"}</b>
                    {p2_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>{"मूल प्रभाव" if is_hi else "Core Dynamic"}:</b> {"चरित्र एवं सहनशक्ति की कड़ी परीक्षा। अहंकार का शमन एवं आत्म-सत्य की खोज।" if is_hi else "Crucible of character and endurance. Dissolves false pride and tests emotional truth."}<br>
                    • <b>{"आर्थिक एवं करियर" if is_hi else "Financial & Career"}:</b> {"कार्यभार की अधिकता, महत्वपूर्ण निर्णयों का दबाव और नेतृत्व संबंधी एकाग्रता।" if is_hi else "Maximum administrative burden, heavy decision-making stress, and executive solitude."}<br>
                    • <b>{"कर्मिक सीख" if is_hi else "Karmic Mastery"}:</b> {"भावनात्मक दृढ़ता, शारीरिक अनुशासन और परिपक्वता का विकास।" if is_hi else "Cultivating emotional resilience, physical discipline, and enduring maturity."}
                </div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #10b981; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#065f46; font-size:0.96rem;">{"तृतीय चरण: अस्त काल (द्वितीय भाव गोचर)" if is_hi else f"Phase 3: Setting Phase (Saturn in {shani_sadesati_data.get('rashi_2nd', '')} / 2nd from Moon)"}</b>
                    {p3_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>{"मूल प्रभाव" if is_hi else "Core Dynamic"}:</b> {"मानसिक दबाव में कमी, अर्जित ज्ञान का स्थिरीकरण और पारिवारिक सौहार्द की बहाली।" if is_hi else "Lifting of psychological pressure, consolidation of hard-won wisdom, and stabilizing family harmony."}<br>
                    • <b>{"आर्थिक एवं करियर" if is_hi else "Financial & Career"}:</b> {"धन लाभ, संपत्ति की प्राप्ति, वाणी में संयम और delayed recognition की प्राप्ति।" if is_hi else "Wealth recovery, acquisition of durable assets, disciplined speech, and delayed recognition."}<br>
                    • <b>{"कर्मिक सीख" if is_hi else "Karmic Mastery"}:</b> {"पूर्व संघर्षों के अनुभवों को ठोस सफलता और दीर्घकालिक सुरक्षा में बदलना।" if is_hi else "Transforming lessons into lasting institutional stability and financial security."}
                </div>
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe;">
            <div style="font-weight:900; font-size:1.05rem; color:#5b21b6; margin-bottom:6px;">{"🪔 शनि ग्रह शांति एवं शमन हेतु वैदिक उपाय:" if is_hi else "🪔 Prescribed Remedies for Planetary Neutralization:"}</div>
            <div style="font-size:0.93rem; line-height:1.7; color:#3b0764;">
                • <b>{"मंत्र जप" if is_hi else "Mantra Japa"}:</b> {"शनिवार की संध्या को पश्चिम दिशा की ओर मुख करके 'ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः' मंत्र का 108 बार जप करें।" if is_hi else "Recite the Shani Beej Mantra (ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः) 108 times at twilight on Saturdays facing West."}<br>
                • <b>{"हनुमान साधना" if is_hi else "Vitality Shield"}:</b> {"मानसिक शांति और प्राण ऊर्जा बढ़ाने के लिए प्रतिदिन हनुमान चालीसा का पाठ करें।" if is_hi else "Recite the Hanuman Chalisa daily to boost pranic fire, disperse lethargy, and protect mental peace."}<br>
                • <b>{"दान एवं सेवा" if is_hi else "Charity & Service"}:</b> {"शनिवार के दिन सरसों का तेल, काले तिल अथवा काले वस्त्र असहाय श्रमिकों को दान करें।" if is_hi else "Donate mustard oil, black sesame seeds, or dark blankets to laborers, sweepers, or elderly persons on Saturdays."}<br>
                • <b>{"व्यवहारिक अनुशासन" if is_hi else "Behavioral Grounding"}:</b> {"समय की पाबंदी रखें, विनम्र रहें और अनुबंधों में शॉर्टकट से बचें।" if is_hi else "Practice absolute punctuality, avoid harsh speech, and avoid shortcuts in contractual agreements."}
            </div>
        </div>
    </div>
    """)

    st.write("")
    if st.button("📿 डिजिटल जप माला काउंटर खोलें" if is_hi else "📿 Open Dedicated Digital Japa Counter", type="primary", use_container_width=True):
        st.session_state.current_page = "mantra"
        st.rerun()
